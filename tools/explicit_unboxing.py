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
DIAGNOSTIC = re.compile(
    r"^(\d+):(\d+):(\d+):(\d+): incompatible types: "
    r"(?:java\.lang\.)?(\w+) cannot be converted to (?:java\.lang\.)?(\w+)"
)


def repair(source, message):
    match = DIAGNOSTIC.match(message)
    if not match:
        return None
    start, end = int(match.group(3)), int(match.group(4))
    wrapper, primitive = match.group(5), match.group(6)
    if start >= end:
        return None
    # javac offsets count UTF-16 code units; Python string indices do not.
    encoded = source.encode("utf-16-le")
    first, last = start * 2, end * 2
    if last > len(encoded):
        return None
    expression = encoded[first:last].decode("utf-16-le")
    if wrapper in UNBOX and UNBOX[wrapper][0] == primitive:
        replacement = "(" + expression + ")." + UNBOX[wrapper][1] + "()"
    elif wrapper == "Object":
        inverse = {value[0]: (name, value[1]) for name, value in UNBOX.items()}
        if primitive not in inverse:
            return None
        cast, method = inverse[primitive]
        replacement = "((" + cast + ")" + expression + ")." + method + "()"
    elif wrapper in {value[0] for value in UNBOX.values()} and primitive in ("Object",):
        cast = next(name for name, value in UNBOX.items() if value[0] == wrapper)
        replacement = cast + ".valueOf(" + expression + ")"
    else:
        return None
    if source.encode("utf-16-le")[:first].decode("utf-16-le").rstrip().endswith("switch"):
        # javac reports the entire parenthesized switch selector. Keep those
        # parentheses around the new int expression, not around its operand.
        replacement = "(" + replacement + ")"
    return (encoded[:first] + replacement.encode("utf-16-le") + encoded[last:]).decode("utf-16-le")


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
            if "cannot be converted to" in value["errors"][0]:
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
