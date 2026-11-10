#!/usr/bin/env python3
"""Restore what Java 1.4 sources need at javac's exact diagnostic positions.

Vineflower can render original boxing or unboxing calls as Java 5 implicit
conversions, drop the reference cast next to a generic API, print type
arguments 1.4 classes never had, and the obfuscated classes lost their throws
clauses; all fail under -source 1.4. Work on temporary copies and promote
only sources that pass isolated compilation.
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
CONVERSION = re.compile(r"incompatible types: ([\w.$]+(?:\[\])*) cannot be converted to ([\w.$]+(?:\[\])*)")
UNARY = re.compile(r"bad operand type (?:java\.lang\.)?Boolean for unary operator '!'")
BINARY = re.compile(r"bad operand types for binary operator '([^']+)'\s+first type:\s+(?:java\.lang\.)?(\w+)"
                    r"\s+second type:\s+(?:java\.lang\.)?(\w+)")
TERNARY = re.compile(r"incompatible types for \?: neither is a subtype of the other\s+second operand:\s+"
                     r"([\w.$]+(?:\[\])*)\s+third operand :\s+([\w.$]+(?:\[\])*)")
CALL = re.compile(r"no suitable (method|constructor) found for (\w+)\(([^)]*)\)(.*)", re.S)
CANDIDATE = re.compile(r"(?:method|constructor) [\w.$]+\(([^)]*)\) is not applicable")
# the obfuscated de/eso classes lost their Exceptions attribute (0 of 581 methods keep one)
UNREPORTED = re.compile(r"unreported exception ([\w.$]+); must be caught or declared to be thrown")
# 1.4 classes carry no Signature attribute: the generics Vineflower prints come from the generic
# API they call (`Preconditions.checkNotNull`), javac 1.4 stops parsing at the first `<`
GENERICS = re.compile(r"generics are not supported in -source")
TYPE_ARGS = re.compile(r"(?<=[\w$])<([\w.$?]+(?:\[\])*(?:\s+(?:extends|super)\s+[\w.$]+(?:\[\])*)?"
                       r"(?:\s*,\s*[\w.$?]+(?:\[\])*(?:\s+(?:extends|super)\s+[\w.$]+(?:\[\])*)?)*)>")
SIMPLE = re.compile(r"[\w.$]+(?:\((?:[^()]|\([^()]*\))*\))?(?:\[[^\]]*\])*")
# after the erasure `accept(A a, B b)` no longer overrides the raw interface's accept(Object, Object)
OVERRIDE = re.compile(r"<anonymous [\w.$]+> is not abstract and does not override abstract method ([\w$]+)\(([^)]*)\) in")
KEYWORDS = {"return", "else", "case", "throw", "new", "instanceof", "void"}
SHAPES = (CONVERSION, UNARY, BINARY, TERNARY, CALL, UNREPORTED, GENERICS, OVERRIDE)
HEADER = re.compile(r"\)\s*(?:throws\s+[\w.$,\s]+)?\{\s*$")
BLOCK = re.compile(r"^\s*\}?\s*(?:(?:if|for|while|switch|catch|synchronized)\s*\(|else\b|do\b|try\b)|\bnew\b")
LITERALS = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//.*')


def short(name):
    return name[10:] if name.startswith("java.lang.") else name


def box_call(wrapper, expression):
    """What the firmware's 1.4 code spells: `Boolean.valueOf(x)` but `new Integer(x)`, since the
    CDC 1.1 JCL has no `Integer.valueOf(int)` (javap -cp shows the JDK's; extract the class)."""
    return ("Boolean.valueOf(" if wrapper == "Boolean" else "new " + wrapper + "(") + expression + ")"


def converted(expression, actual, target, spelled=None):
    """The explicit 1.4 spelling of a rejected implicit conversion, or None: unboxing (widened
    afterwards if needed), boxing, or the reference cast Vineflower dropped as redundant next to a
    generic API (`spelled` = how the source can name `target`)."""
    if actual in UNBOX and target in (UNBOX[actual][0],) + tuple(WIDENING.get(UNBOX[actual][0], "").split()):
        return "(" + expression + ")." + UNBOX[actual][1] + "()"
    if actual == "Object" and target in PRIMITIVES:
        cast, method = PRIMITIVES[target]
        return "((" + cast + ")" + expression + ")." + method + "()"
    if actual in PRIMITIVES and target in ("Object", PRIMITIVES[actual][0]):
        return box_call(PRIMITIVES[actual][0], expression)
    if actual not in PRIMITIVES and target not in PRIMITIVES and spelled:
        inner = expression.strip()
        return "(" + spelled + ") " + (inner if SIMPLE.fullmatch(inner) else "(" + inner + ")")
    return None


def erased(source):
    """`source` without type-argument lists, innermost first (`Map<String, List<X>>` -> `Map`)."""
    while True:
        source, n = TYPE_ARGS.subn("", source)
        if not n:
            return source


def unboxed(expression, wrapper):
    """`(expression).intValue()` with the operand's surrounding whitespace kept."""
    head = expression[:len(expression) - len(expression.lstrip())]
    tail = expression[len(expression.rstrip()):]
    return head + "(" + expression.strip() + ")." + UNBOX[wrapper][1] + "()" + tail


def boxed(expression, primitive):
    """`new Integer(expression)` - what Vineflower hid - with the whitespace kept."""
    head = expression[:len(expression) - len(expression.lstrip())]
    tail = expression[len(expression.rstrip()):]
    return head + box_call(PRIMITIVES[primitive][0], expression.strip()) + tail


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


def declaration(source, line):
    """str index of the `{` that opens the method or constructor enclosing 1-based `line`, or None
    (field initializer, static block). Walks up over block statements and anonymous class bodies."""
    lines = source.split("\n")
    depth = 0
    for i in range(line - 1, -1, -1):
        for c in reversed(LITERALS.sub("", lines[i])):
            if c == "}":
                depth += 1
            elif c == "{" and depth:
                depth -= 1
            elif c == "{":
                if HEADER.search(lines[i]) and not BLOCK.search(lines[i]):
                    return sum(len(l) + 1 for l in lines[:i]) + lines[i].rfind("{")
                if re.search(r"\b(class|interface|enum)\b", LITERALS.sub("", lines[i])):
                    return None
                break  # a block statement or anonymous class body: keep climbing
    return None


def spell(source, qualified):
    """`qualified` as the source can name it: simple when imported, same-package or java.lang,
    `Outer.Inner` when `Outer` is, else fully qualified. Array suffixes are kept."""
    name = qualified.rstrip("[]")
    suffix, parts = qualified[len(name):], name.split(".")
    own = re.match(r"\s*package\s+([\w.]+);", source)
    for k in range(len(parts) - 1, 0, -1):
        prefix = ".".join(parts[:k])
        if prefix in ("java.lang", own and own.group(1)) or re.search(
                r"^import\s+" + re.escape(".".join(parts[:k + 1])) + r";", source, re.M):
            return ".".join(parts[k:]) + suffix
    return qualified


def assigned_type(source, start, line):
    """The declared type the expression at `start` is assigned or returned into, as the source
    spells it, or None: `T x = e`, `x = e` (x's nearest declaration), `return e` (the method)."""
    head = source[:start]
    match = re.search(r"([\w.$]+(?:\[\])*)\s+([\w$]+)\s*=\s*$", head)
    if match and match.group(1) not in KEYWORDS:
        found = match.group(1)
    elif re.search(r"\breturn\s+$", head):
        brace = declaration(source, line)
        header = source[source.rfind("\n", 0, brace) + 1:brace] if brace is not None else ""
        match = re.search(r"(?:^|\s)([\w.$]+(?:\[\])*)\s+[\w$]+\s*\(", header)
        found = match.group(1) if match else None
    else:
        match = re.search(r"(?:this\.)?([\w$]+)\s*=\s*$", head)
        decls = re.findall(r"([\w.$]+(?:\[\])*)\s+" + re.escape(match.group(1)) + r"\b(?!\s*\()", head) if match else []
        found = next((t for t in reversed(decls) if t not in KEYWORDS), None)
    return found if found and found not in PRIMITIVES and found not in KEYWORDS else None


def overriding(source, line, name, arity):
    """`source` with the anonymous class method `name` of `arity` after `line` taking Object
    parameters and casting them on entry, the 1.4 spelling of a raw-interface implementation."""
    lines = source.split("\n")
    for i in range(line - 1, len(lines)):
        match = re.search(r"\b" + re.escape(name) + r"\s*\(", lines[i])
        if not match or not HEADER.search(lines[i]) or BLOCK.search(lines[i]):
            continue
        found = arguments(lines[i], match.end() - 1)
        if found is None or len(found) != arity:
            continue
        params, casts, indent = [], [], lines[i][:len(lines[i]) - len(lines[i].lstrip())] + "    "
        for a, b in found:
            param = re.fullmatch(r"(?:final\s+)?([\w.$]+(?:\[\])*)\s+([\w$]+)", lines[i][a:b].strip())
            if param is None:
                return None
            kind, var = param.groups()
            params.append(lines[i][a:b].strip() if kind == "Object" else "Object " + var + "_")
            if kind != "Object":
                casts.append(indent + kind + " " + var + " = (" + kind + ") " + var + "_;")
        if not casts:
            return None
        lines[i] = lines[i][:found[0][0]] + ", ".join(params) + lines[i][found[-1][1]:]
        lines[i + 1:i + 1] = casts
        return "\n".join(lines)
    return None


def repair(source, message, invoked=None):
    """`source` with javac's one diagnostic repaired, or None. `invoked` (see invocations) picks
    the overload a `no suitable method` call really targets; javac's candidate list is the fallback."""
    match = DIAGNOSTIC.match(message)
    if not match:
        return None
    line, col, start, end = (int(g) for g in match.groups()[:4])
    text = match.group(5)
    if GENERICS.match(text):
        out = erased(source)
        return out if out != source else None
    override = OVERRIDE.match(text)
    if override:
        return overriding(source, line, override.group(1), len([t for t in override.group(2).split(",") if t]))
    if start >= end or end * 2 > len(source.encode("utf-16-le")):
        return None
    start, end = ahead(source, 0, start), ahead(source, 0, end)
    span = source[start:end]
    pieces = []  # (from, to, replacement), ascending and disjoint
    conv, unary, binary, ternary, call, unreported = (p.match(text) for p in SHAPES[:6])
    if conv:
        actual, target = (short(t) for t in conv.groups())
        replacement = converted(span, actual, target, spell(source, target))
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
        second, third = (short(t) for t in ternary.groups())
        pos = column(source, line, col)
        colon = ternary_colon(source[pos + 1:end]) if source[pos] == "?" else None
        if colon is None:
            return None
        colon += pos + 1
        if second in UNBOX and UNBOX[second][0] == third:
            pieces.append((pos + 1, colon, unboxed(source[pos + 1:colon], second)))
        elif third in UNBOX and UNBOX[third][0] == second:
            pieces.append((colon + 1, end, unboxed(source[colon + 1:end], third)))
        elif second not in PRIMITIVES and third not in PRIMITIVES:
            # unrelated reference operands: javac 1.4 has no lub, the original cast one to the target
            target = assigned_type(source, start, line)
            if target:
                pieces.append((pos + 1, pos + 1, " (" + target + ")"))
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
    elif unreported:
        brace = declaration(source, line)
        if brace is None:
            return None
        head = source[:brace].rstrip()
        name = spell(source, unreported.group(1))
        clause = ", " + name if re.search(r"\bthrows\s+[\w.$,\s]+$", head) else " throws " + name
        pieces.append((len(head), brace, clause + " "))
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
               "--source", source, "--target", source, "--filter-clashing-classes",
               "--json-report", str(report)]
    if jcl:
        command += ["--jcl", str(jcl)]
    checked = subprocess.run(command, capture_output=True, text=True)
    if checked.returncode not in (0, 1) or not report.is_file():
        raise RuntimeError("isolated compiler failed: " + checked.stderr[-1000:])
    failures = json.loads(report.read_text())["reported_failures"]
    report.unlink()
    return failures


def repair_all(source, errors, invoked=None):
    """`source` with every repairable error of one javac run applied, last span first so the
    earlier offsets stay valid. A throws clause or generics erasure moves text, so it ends the round."""
    taken = []
    for error in sorted(errors, key=lambda e: int(DIAGNOSTIC.match(e).group(3)), reverse=True):
        match = DIAGNOSTIC.match(error)
        a, b = int(match.group(3)), int(match.group(4))
        moving = UNREPORTED.match(match.group(5)) or GENERICS.match(match.group(5)) or OVERRIDE.match(match.group(5))
        if any(a < y and x < b for x, y in taken) or (moving and taken):
            continue
        fixed = repair(source, error, invoked)
        if fixed is None or fixed == source:
            continue
        source = fixed
        taken.append((a, b))
        if moving:
            break
    return source


def unbox(work, candidates, jar, libs, jcl, source="1.4", max_rounds=30):
    """Repair the copies in place, every repairable javac error per file per round, until
    nothing changes. Returns ({candidate: patches}, failures of the final state)."""
    patches, invoked, last = dict.fromkeys(candidates, 0), {}, {}
    for _ in range(max_rounds):
        failures = compile_all(work, jar, libs, jcl, source)
        changed = 0
        for candidate in candidates:
            errors = failures.get(str(candidate), {}).get("errors")
            if not errors or errors == last.get(candidate):  # same errors after a repair: not converging
                continue
            before = candidate.read_text()
            if candidate not in invoked and any("no suitable" in e for e in errors):
                invoked[candidate] = invocations(jar, candidate.relative_to(work))
            after = repair_all(before, errors, invoked.get(candidate))
            if after != before:
                candidate.write_text(after)
                patches[candidate] += 1
                last[candidate] = errors
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
