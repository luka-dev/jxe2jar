#!/usr/bin/env python3
"""Restore Java 1.4 wrapper conversions at javac's exact expression positions.

Vineflower can render original boxing or unboxing calls as Java 5 implicit
conversions, which fail under -source 1.4. Work on temporary copies and
promote only sources that pass isolated compilation.
"""

import argparse
import collections
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

from rtdiff import parse


HERE = Path(__file__).resolve().parent
UNBOX = {
    "Integer": ("int", "intValue"),
    "Boolean": ("boolean", "booleanValue"),
    "Long": ("long", "longValue"),
    "Double": ("double", "doubleValue"),
    "Float": ("float", "floatValue"),
    "Byte": ("byte", "byteValue"),
    "Short": ("short", "shortValue"),
    "Character": ("char", "charValue"),
}
PRIMITIVES = {value[0]: (name, value[1]) for name, value in UNBOX.items()}
WIDENING = {"byte": "short int long float double", "short": "int long float double",
            "char": "int long float double", "int": "long float double", "long": "float double",
            "float": "double"}
DESCRIPTOR = {"I": "int", "Z": "boolean", "J": "long", "D": "double", "F": "float", "B": "byte",
              "S": "short", "C": "char"}
DIAGNOSTIC = re.compile(r"^(\d+):(\d+):(\d+):(\d+): (.*)", re.S)
CONVERSION = re.compile(r"incompatible types: (?:java\.lang\.)?(\w+) cannot be converted to (?:java\.lang\.)?(\w+)")
UNARY = re.compile(r"bad operand type (?:java\.lang\.)?Boolean for unary operator '!'")
BINARY = re.compile(r"bad operand types for binary operator '([^']+)'\s+first type:\s+(?:java\.lang\.)?(\w+)"
                    r"\s+second type:\s+(?:java\.lang\.)?(\w+)")
TERNARY = re.compile(r"incompatible types for \?: neither is a subtype of the other\s+second operand:\s+"
                     r"(?:java\.lang\.)?(\w+)\s+third operand :\s+(?:java\.lang\.)?(\w+)")
CALL = re.compile(r"no suitable (method|constructor) found for (\w+)\(([^)]*)\)(.*)", re.S)
CANDIDATE = re.compile(r"(?:method|constructor) [\w.$]+\(([^)]*)\) is not applicable")
SHAPES = (CONVERSION, UNARY, BINARY, TERNARY, CALL)


def short(name):
    return name[10:] if name.startswith("java.lang.") else name


def converted(expression, wrapper, primitive):
    """The explicit 1.4 spelling of a rejected implicit conversion, or None."""
    if wrapper in UNBOX and UNBOX[wrapper][0] == primitive:
        return "(" + expression + ")." + UNBOX[wrapper][1] + "()"
    if wrapper == "Object" and primitive in PRIMITIVES:
        cast, method = PRIMITIVES[primitive]
        return "((" + cast + ")" + expression + ")." + method + "()"
    if wrapper in PRIMITIVES and primitive in ("Object", PRIMITIVES[wrapper][0]):
        return PRIMITIVES[wrapper][0] + ".valueOf(" + expression + ")"
    return None


def unboxed(expression, wrapper):
    """`(expression).intValue()` with the operand's surrounding whitespace kept."""
    head = expression[:len(expression) - len(expression.lstrip())]
    tail = expression[len(expression.rstrip()):]
    return head + "(" + expression.strip() + ")." + UNBOX[wrapper][1] + "()" + tail


def boxed(expression, primitive):
    """`Integer.valueOf(expression)` - what Vineflower hid - with the whitespace kept."""
    head = expression[:len(expression) - len(expression.lstrip())]
    tail = expression[len(expression.rstrip()):]
    return head + PRIMITIVES[primitive][0] + ".valueOf(" + expression.strip() + ")" + tail


def ahead(source, base, units):
    """String index `units` UTF-16 code units after string index `base` - javac offsets
    count code units, Python string indices do not."""
    return base + len(source[base:].encode("utf-16-le")[:units * 2].decode("utf-16-le", "surrogatepass"))


def column(source, line, col):
    """String index of javac's line:col - the operator of a binary, unary or ?: expression.
    Vineflower writes no tabs, so a column is a plain code-unit count."""
    start = 0
    for _ in range(line - 1):
        start = source.index("\n", start) + 1
    return ahead(source, start, col - 1)


def toplevel(text, start):
    """(index, char) of every bracket-depth-0 character from `start` on, outside string and char
    literals (opening brackets excluded); the bracket closing the enclosing one comes last."""
    depth, quote, i = 0, None, start
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                yield i, c
                return
            depth -= 1
        elif depth == 0:
            yield i, c
        i += 1


def ternary_colon(text):
    """Index in `text` (what follows a `?`) of the `:` belonging to that `?`, or None."""
    nested = 0
    for i, c in toplevel(text, 0):
        if c == "?":
            nested += 1
        elif c == ":":
            if not nested:
                return i
            nested -= 1
    return None


def arguments(text, open_):
    """(from, to) of each top-level argument of the list opening at text[open_] == '(', or None."""
    found, last = [], open_ + 1
    for i, c in toplevel(text, open_ + 1):
        if c == ",":
            found.append((last, i))
            last = i + 1
        elif c == ")":
            return found + [(last, i)] if found or text[last:i].strip() else found
    return None


def conversion(actual, param):
    """'' when javac 1.4 takes the argument as is, 'box'/'unbox' when a wrapper call makes it
    acceptable, None when nothing does. Reference-to-reference is left to javac."""
    actual, param = short(actual), short(param)
    if actual == param:
        return ""
    if actual in PRIMITIVES:
        if param in WIDENING.get(actual, "").split():
            return ""
        return "box" if param in ("Object", PRIMITIVES[actual][0]) else None
    if actual in UNBOX:
        primitive = UNBOX[actual][0]
        if param == primitive or param in WIDENING.get(primitive, "").split():
            return "unbox"
        return "" if param == "Object" else None
    return None if param in PRIMITIVES else ""


def choose(actual, signatures):
    """Per-argument conversions for the one signature that needs the fewest, or None."""
    ranked = {}
    for params in signatures:
        if len(params) == len(actual):
            plan = tuple(conversion(a, p) for a, p in zip(actual, params))
            if None not in plan:
                ranked.setdefault(sum(map(bool, plan)), set()).add(plan)
    best = ranked[min(ranked)] if ranked else ()
    return list(best.pop()) if len(best) == 1 else None


def javac_types(descriptor):
    """Parameter types of a method descriptor as javac spells them (`int[]`, `java.lang.String`)."""
    out, dims, i = [], 0, 1
    while descriptor[i] != ")":
        if descriptor[i] == "[":
            dims, i = dims + 1, i + 1
            continue
        if descriptor[i] == "L":
            j = descriptor.index(";", i)
            name, i = descriptor[i + 1:j].replace("/", ".").replace("$", "."), j + 1
        else:
            name, i = DESCRIPTOR[descriptor[i]], i + 1
        out.append(name + "[]" * dims)
        dims = 0
    return out


def invocations(jar, rel):
    """{method name (or simple class name for constructors): [parameter type lists]} of every
    method the classes of source `rel` call - a constant pool only holds references in use."""
    out = collections.defaultdict(list)
    prefix = rel.with_suffix("").as_posix()
    with zipfile.ZipFile(jar) as archive:
        for name in archive.namelist():
            if name == prefix + ".class" or name.startswith(prefix + "$") and name.endswith(".class"):
                cp = parse(archive.read(name))["cp"]
                for entry in cp.e:
                    if entry and entry[0] in ("method", "imethod"):
                        nat = cp.e[entry[2]]
                        method = cp.utf(nat[1])
                        if method == "<init>":
                            method = cp.cls(entry[1]).rsplit("/", 1)[-1].rsplit("$", 1)[-1]
                        out[method].append(javac_types(cp.utf(nat[2])))
    return out


def repair(source, message, invoked=None):
    """`source` with javac's one diagnostic repaired, or None. `invoked` (see invocations) picks
    the overload a `no suitable method` call really targets; javac's candidate list is the fallback."""
    match = DIAGNOSTIC.match(message)
    if not match:
        return None
    line, col, start, end = (int(g) for g in match.groups()[:4])
    text = match.group(5)
    if start >= end or end * 2 > len(source.encode("utf-16-le")):
        return None
    start, end = ahead(source, 0, start), ahead(source, 0, end)
    span = source[start:end]
    pieces = []  # (from, to, replacement), ascending and disjoint
    conv, unary, binary, ternary, call = (p.match(text) for p in SHAPES)
    if conv:
        replacement = converted(span, *conv.groups())
        if replacement is None:
            return None
        if source[:start].rstrip().endswith("switch"):
            # javac reports the entire parenthesized switch selector. Keep those
            # parentheses around the new int expression, not around its operand.
            replacement = "(" + replacement + ")"
        pieces.append((start, end, replacement))
    elif unary and span.startswith("!"):
        pieces.append((start + 1, end, unboxed(span[1:], "Boolean")))
    elif binary:
        op, left, right = binary.groups()
        pos = column(source, line, col)
        if source[pos:pos + len(op)] != op:
            return None
        if left in UNBOX:
            pieces.append((start, pos, unboxed(source[start:pos], left)))
        if right in UNBOX:
            pieces.append((pos + len(op), end, unboxed(source[pos + len(op):end], right)))
    elif ternary:
        second, third = ternary.groups()
        pos = column(source, line, col)
        colon = ternary_colon(source[pos + 1:end]) if source[pos] == "?" else None
        if colon is None:
            return None
        colon += pos + 1
        if second in UNBOX and UNBOX[second][0] == third:
            pieces.append((pos + 1, colon, unboxed(source[pos + 1:colon], second)))
        elif third in UNBOX and UNBOX[third][0] == second:
            pieces.append((colon + 1, end, unboxed(source[colon + 1:end], third)))
    elif call:
        kind, name, actual, rest = call.groups()
        actual = [t for t in actual.split(",") if t]
        plan = choose(actual, (invoked or {}).get(name, ())) or choose(
            actual, [[t for t in p.split(",") if t] for p in CANDIDATE.findall(rest) if "..." not in p])
        # the span is `new X(args)` for a constructor, the method select (`a.b.log`) for a method
        open_ = source.find("(", start) if kind == "constructor" else end + len(source[end:]) - len(source[end:].lstrip())
        found = arguments(source, open_) if source[open_:open_ + 1] == "(" else None
        if not plan or found is None or len(found) != len(actual):
            return None
        for (a, b), what, actual_type in zip(found, plan, actual):
            if what == "box":
                pieces.append((a, b, boxed(source[a:b], actual_type)))
            elif what == "unbox":
                pieces.append((a, b, unboxed(source[a:b], short(actual_type))))
    if not pieces:
        return None
    out, cursor = [], 0
    for a, b, replacement in pieces:
        out += source[cursor:a], replacement
        cursor = b
    return "".join(out) + source[cursor:]


def compile_all(work, jar, libs, jcl, source="1.4"):
    """isolated_compile_check over the copies under `work`; returns its reported_failures."""
    report = work.parent / (work.name + "_compile.json")
    command = [sys.executable, str(HERE / "isolated_compile_check.py"), str(work),
               "--jar", str(jar), "--libs", str(libs),
               "--source", source, "--target", source, "--json-report", str(report)]
    if jcl:
        command += ["--jcl", str(jcl)]
    checked = subprocess.run(command, capture_output=True, text=True)
    if checked.returncode not in (0, 1) or not report.is_file():
        raise RuntimeError("isolated compiler failed: " + checked.stderr[-1000:])
    failures = json.loads(report.read_text())["reported_failures"]
    report.unlink()
    return failures


def unbox(work, candidates, jar, libs, jcl, source="1.4", max_rounds=30):
    """Repair the copies in place, one javac error per file per round, until nothing changes.
    Returns ({candidate: patches}, failures of the final state)."""
    patches, invoked = dict.fromkeys(candidates, 0), {}
    for _ in range(max_rounds):
        failures = compile_all(work, jar, libs, jcl, source)
        changed = 0
        for candidate in candidates:
            errors = failures.get(str(candidate), {}).get("errors")
            if not errors:
                continue
            before = candidate.read_text()
            if candidate not in invoked and "no suitable" in errors[0]:
                invoked[candidate] = invocations(jar, candidate.relative_to(work))
            after = repair(before, errors[0], invoked.get(candidate))
            if after is not None and after != before:
                candidate.write_text(after)
                patches[candidate] += 1
                changed += 1
        if not changed:
            return patches, failures
    return patches, compile_all(work, jar, libs, jcl, source)  # --max-rounds reached: re-check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tree", type=Path)
    parser.add_argument("jar", type=Path)
    parser.add_argument("diagnostics", type=Path, help="JSON from isolated_compile_check.py")
    parser.add_argument("--jcl", type=Path)
    parser.add_argument("--libs", type=Path, default=HERE.parent / "libs")
    parser.add_argument("--max-rounds", type=int, default=30)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    tree = args.tree.resolve()
    diagnosed = json.loads(args.diagnostics.read_text())["reported_failures"]
    selected = []
    for raw, value in diagnosed.items():
        path = Path(raw).resolve()
        try:
            rel = path.relative_to(tree)
        except ValueError:
            continue
        if path.is_file() and value.get("source") == "1.4" and value.get("errors"):
            if any(p.search(value["errors"][0]) for p in SHAPES):
                selected.append((path, rel))

    manifest = {}
    with tempfile.TemporaryDirectory(prefix="explicit_unboxing_") as directory:
        work = Path(directory).resolve()
        copies = []
        for original, rel in selected:
            candidate = work / rel
            candidate.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, candidate)
            copies.append(candidate)
        patches, failures = unbox(work, copies, args.jar.resolve(), args.libs.resolve(),
                                  args.jcl and args.jcl.resolve(), max_rounds=args.max_rounds)
        for (original, rel), candidate in zip(selected, copies):
            key = rel.as_posix()
            manifest[key] = {"patches": patches[candidate], "status": "skipped"}
            if patches[candidate] and str(candidate) not in failures:
                if args.apply:
                    shutil.copy2(candidate, original)
                manifest[key]["status"] = "applied" if args.apply else "would_apply"
            elif str(candidate) in failures:
                manifest[key]["reason"] = failures[str(candidate)]["errors"][:1]

    accepted = sum(value["status"] != "skipped" for value in manifest.values())
    print("explicit wrapper conversions: %d/%d candidate(s); %s" %
          (accepted, len(manifest), "applied" if args.apply else "dry-run"))
    if args.result:
        args.result.write_text(json.dumps({"tree": str(tree), "results": manifest}, indent=2) + "\n")


if __name__ == "__main__":
    main()
