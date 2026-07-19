#!/usr/bin/env python3
"""
decompile_fallback.py - Re-decompile Vineflower stubs with CFR.

Vineflower occasionally emits a `// $VF: Couldn't be decompiled` stub for a
method whose control flow its DomHelper can't structure (a genuine VF bug, e.g.
com.ibm.oti.util.DefaultPolicy.loadKeystore). CFR usually handles those. This
tool scans a decompiled tree for such stubs and, for each affected class,
re-decompiles it from the JAR with CFR and replaces the .java file.

Usage:
  python3 tools/decompile_fallback.py <decompiled-dir> <jar> [--cfr path.jar]
                                                        [--java path] [--dry-run]
"""

import argparse
import os
import subprocess
import sys
import tempfile
import zipfile

STUB_MARKER = "Couldn't be decompiled"
DEFAULT_CFR = os.path.join(os.path.dirname(__file__), "cfr-0.152.jar")


def find_stubs(root):
    for dirpath, _, files in os.walk(root):
        for name in files:
            if not name.endswith(".java"):
                continue
            path = os.path.join(dirpath, name)
            try:
                if STUB_MARKER in open(path, encoding="utf-8", errors="replace").read():
                    yield path
            except OSError:
                pass


def main():
    ap = argparse.ArgumentParser(description="CFR fallback for Vineflower stubs.")
    ap.add_argument("dir")
    ap.add_argument("jar")
    ap.add_argument("--cfr", default=DEFAULT_CFR)
    ap.add_argument("--java", default="java")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    stubs = list(find_stubs(args.dir))
    print(f"found {len(stubs)} Vineflower stub file(s)")
    if not stubs:
        return

    zf = zipfile.ZipFile(args.jar)
    entries = set(zf.namelist())
    fixed = failed = 0
    for java_path in stubs:
        rel = os.path.relpath(java_path, args.dir)
        internal = rel[:-5].replace(os.sep, "/") + ".class"
        if internal not in entries:
            print(f"  SKIP {rel} (no {internal} in jar)")
            failed += 1
            continue
        if args.dry_run:
            print(f"  would re-decompile {rel} with CFR")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            cls = os.path.join(tmp, "T.class")
            open(cls, "wb").write(zf.read(internal))
            out = subprocess.run(
                [args.java, "-jar", args.cfr, cls, "--comments", "false"],
                capture_output=True, text=True,
            ).stdout
            if not out.strip() or STUB_MARKER in out:
                print(f"  FAIL {rel} (CFR also could not decompile)")
                failed += 1
                continue
            open(java_path, "w", encoding="utf-8").write(out)
            print(f"  FIXED {rel}")
            fixed += 1

    print(f"\n{fixed} fixed, {failed} unresolved"
          + ("  (dry-run)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
