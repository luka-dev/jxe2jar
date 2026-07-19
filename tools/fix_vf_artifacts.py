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
import sys

TOKEN = "<unrepresentable>"


def main():
    ap = argparse.ArgumentParser(description="Fix Vineflower <unrepresentable> tokens.")
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
            if TOKEN not in text:
                continue
            n = text.count(TOKEN)
            hits += n
            changed += 1
            if args.apply:
                open(path, "w", encoding="utf-8").write(text.replace(TOKEN, "Object"))

    action = "replaced" if args.apply else "would replace"
    print(f"{action} {hits} `{TOKEN}` token(s) in {changed} file(s)")
    if not args.apply:
        print("dry-run - pass --apply to rewrite files")


if __name__ == "__main__":
    main()
