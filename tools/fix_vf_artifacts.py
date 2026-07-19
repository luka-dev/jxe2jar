#!/usr/bin/env python3
"""
fix_vf_artifacts.py - Repair non-compilable Vineflower rendering artifacts.

When anonymous classes are inlined (which the EnclosingMethod attribute now
enables), Vineflower occasionally cannot name the type of a nested anonymous
class's synthetic outer-`this` field and emits the placeholder token
`<unrepresentable>`, which is not valid Java. The field is a synthetic
enclosing-instance reference, so widening it to `Object` restores a
compilable/parseable file without changing behaviour.

Usage:
  python3 tools/fix_vf_artifacts.py <dir>            # dry-run (report only)
  python3 tools/fix_vf_artifacts.py <dir> --apply     # rewrite files in place
"""

import argparse
import os
import re
import sys

TOKEN = "<unrepresentable>"

# Vineflower's `jad` renamer derives a variable name by lower-casing its type, which
# collides with a reserved word for a few types (e.g. `Void` -> `void`), producing an
# illegal identifier like `accept(Void void)`. These are unused synthetic parameters, so
# suffixing the identifier with `_` in the declaration makes the file legal Java.
KEYWORD_PARAM = re.compile(r"\b(Void|Class|Enum)\s+(void|class|enum)\b")

# Vineflower sometimes emits a cast as a self-duplicated intersection type,
# `(Map & Map)x`, which is a valid but pointless intersection of a type with itself.
# Collapse `(X & X)` -> `(X)` (backref keeps it to identical types; a real `(A & B)`
# intersection cast is left untouched). This also drops the Java-8-only intersection
# syntax that some downstream parsers reject.
DUP_INTERSECTION = re.compile(r"\(\s*([A-Za-z_$][\w$.]*)\s*&\s*\1\s*\)")


def fix_text(text):
    n = text.count(TOKEN)
    text = text.replace(TOKEN, "Object")
    text, k = KEYWORD_PARAM.subn(lambda m: f"{m.group(1)} {m.group(2)}_", text)
    text, d = DUP_INTERSECTION.subn(r"(\1)", text)
    return text, n + k + d


def main():
    ap = argparse.ArgumentParser(description="Fix Vineflower rendering artifacts.")
    ap.add_argument("dir")
    ap.add_argument("--apply", action="store_true", help="rewrite files in place")
    args = ap.parse_args()

    changed = hits = 0
    for dp, _, files in os.walk(args.dir):
        for name in files:
            if not name.endswith(".java"):
                continue
            path = os.path.join(dp, name)
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            new, n = fix_text(text)
            if new == text:
                continue
            hits += n
            changed += 1
            if args.apply:
                open(path, "w", encoding="utf-8").write(new)

    action = "fixed" if args.apply else "would fix"
    print(f"{action} {hits} artifact(s) in {changed} file(s)")
    if not args.apply:
        print("dry-run - pass --apply to rewrite files")


if __name__ == "__main__":
    main()
