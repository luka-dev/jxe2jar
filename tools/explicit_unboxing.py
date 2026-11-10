#!/usr/bin/env python3
"""Restore Java 1.4 wrapper conversions at javac's exact expression positions.

Vineflower can render original boxing or unboxing calls as Java 5 implicit
conversions, which fail under -source 1.4. Work on temporary copies and
promote only sources that pass isolated compilation.
"""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


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
DIAGNOSTIC = re.compile(r"^(\d+):(\d+):(\d+):(\d+): (.*)", re.S)
CONVERSION = re.compile(r"incompatible types: (?:java\.lang\.)?(\w+) cannot be converted to (?:java\.lang\.)?(\w+)")
UNARY = re.compile(r"bad operand type (?:java\.lang\.)?Boolean for unary operator '!'")
BINARY = re.compile(r"bad operand types for binary operator '([^']+)'\s+first type:\s+(?:java\.lang\.)?(\w+)"
                    r"\s+second type:\s+(?:java\.lang\.)?(\w+)")
TERNARY = re.compile(r"incompatible types for \?: neither is a subtype of the other\s+second operand:\s+"
                     r"(?:java\.lang\.)?(\w+)\s+third operand :\s+(?:java\.lang\.)?(\w+)")
PRIMITIVES = {value[0]: (name, value[1]) for name, value in UNBOX.items()}


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


def column_offset(source, line, col):
    """UTF-16 offset of javac's line:col - the operator of a binary, unary or ?: expression.
    Vineflower writes no tabs, so a column is a plain character count."""
    start = 0
    for _ in range(line - 1):
        start = source.index("\n", start) + 1
    return len(source[:start].encode("utf-16-le")) // 2 + col - 1


def ternary_colon(text):
    """Index in `text` (what follows a `?`) of the `:` belonging to that `?`, or None."""
    depth = nested = 0
    quote = None
    i = 0
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
            depth -= 1
        elif depth == 0 and c == "?":
            nested += 1
        elif depth == 0 and c == ":":
            if not nested:
                return i
            nested -= 1
        i += 1
    return None


def repair(source, message):
    match = DIAGNOSTIC.match(message)
    if not match:
        return None
    line, col, start, end = (int(g) for g in match.groups()[:4])
    text = match.group(5)
    # javac offsets count UTF-16 code units; Python string indices do not.
    encoded = source.encode("utf-16-le")
    if start >= end or end * 2 > len(encoded):
        return None

    def unit(a, b):
        return encoded[a * 2:b * 2].decode("utf-16-le")

    pieces = []  # (from, to, replacement) in UTF-16 units, ascending, disjoint
    conv, unary, binary, ternary = (p.match(text) for p in (CONVERSION, UNARY, BINARY, TERNARY))
    if conv:
        replacement = converted(unit(start, end), *conv.groups())
        if replacement is None:
            return None
        if unit(0, start).rstrip().endswith("switch"):
            # javac reports the entire parenthesized switch selector. Keep those
            # parentheses around the new int expression, not around its operand.
            replacement = "(" + replacement + ")"
        pieces.append((start, end, replacement))
    elif unary and unit(start, start + 1) == "!":
        pieces.append((start + 1, end, unboxed(unit(start + 1, end), "Boolean")))
    elif binary:
        op, left, right = binary.groups()
        pos = column_offset(source, line, col)
        if unit(pos, pos + len(op)) != op:
            return None
        if left in UNBOX:
            pieces.append((start, pos, unboxed(unit(start, pos), left)))
        if right in UNBOX:
            pieces.append((pos + len(op), end, unboxed(unit(pos + len(op), end), right)))
    elif ternary:
        second, third = ternary.groups()
        pos = column_offset(source, line, col)
        colon = ternary_colon(unit(pos + 1, end)) if unit(pos, pos + 1) == "?" else None
        if colon is None:
            return None
        colon += pos + 1
        if second in UNBOX and UNBOX[second][0] == third:
            pieces.append((pos + 1, colon, unboxed(unit(pos + 1, colon), second)))
        elif third in UNBOX and UNBOX[third][0] == second:
            pieces.append((colon + 1, end, unboxed(unit(colon + 1, end), third)))
    if not pieces:
        return None
    out, cursor = b"", 0
    for a, b, replacement in pieces:
        out += encoded[cursor * 2:a * 2] + replacement.encode("utf-16-le")
        cursor = b
    return (out + encoded[cursor * 2:]).decode("utf-16-le")


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
    patches = dict.fromkeys(candidates, 0)
    for _ in range(max_rounds):
        failures = compile_all(work, jar, libs, jcl, source)
        changed = 0
        for candidate in candidates:
            errors = failures.get(str(candidate), {}).get("errors")
            if not errors:
                continue
            before = candidate.read_text()
            after = repair(before, errors[0])
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
            if any(p.search(value["errors"][0]) for p in (CONVERSION, UNARY, BINARY, TERNARY)):
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
