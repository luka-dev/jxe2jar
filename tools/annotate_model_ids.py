#!/usr/bin/env python3
"""
annotate_model_ids.py - Resolve model-ID integer literals back to their names.

javac inlines `static final int` constants at the call site, so decompiled code
shows `getChoiceModel(402127)` instead of the symbolic
`getChoiceModel(NAV_MAP_SERVICELIST_GOOGLE_EARTH_CHOICE)`. The *names* survive in
the model-ID registry interfaces (`de/audi/atip/model/I*ModelBank.java`), so the
value -> name mapping is fully recoverable.

This tool scans a decompiled tree, builds that map, and annotates every
`get<Kind>Model(<int>)` call in place:

    getChoiceModel(402127)  ->  getChoiceModel(/* NAV_MAP_SERVICELIST_GOOGLE_EARTH_CHOICE */ 402127)

Resolution is context-aware to beat two kinds of ambiguity:
  * enum collisions - a small value like 1 matches hundreds of enum constants;
    model IDs live only in *ModelBank* interfaces, so names defined there win.
  * bank aliases - the same ID may be named in a Core and an Evo bank; the
    caller's package domain (navi/car/tuner/media/...) picks the right one, and
    for getChoiceModel a `*_CHOICE` name is preferred.

Usage:
  python3 tools/annotate_model_ids.py <dir>                 # dry-run (report only)
  python3 tools/annotate_model_ids.py <dir> --apply         # rewrite files in place
  python3 tools/annotate_model_ids.py <dir> --table map.md  # write value->name table
"""

import argparse
import os
import re
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONST_RE = re.compile(r"\bint\s+([A-Z][A-Za-z0-9_]+)\s*=\s*(-?\d+)\s*;")
# get<Kind>Model( <int> )  - not already annotated (no /* */ before the number)
CALL_RE = re.compile(r"(get([A-Z][A-Za-z]*)Model\(\s*)(\d+)(\s*\))")
BANK_HINT = "modelbank"  # files whose name contains this hold the ID registry

# caller-package domain -> token that should appear in the winning bank's filename
DOMAINS = [
    "navi", "car", "tuner", "media", "tv", "messaging", "online", "phone",
    "tone", "connectivity", "earlyapps", "earlyfunc", "sds", "bluetooth",
]


def _iter_java(root):
    for dirpath, _, files in os.walk(root):
        for name in files:
            if name.endswith(".java"):
                yield os.path.join(dirpath, name)


def build_index(root):
    """Return (val2names, name2bank) where name2bank[name] is the defining file's
    relpath, and val2names[value] is the set of constant names with that value."""
    val2names = defaultdict(set)
    name2file = {}
    for path in _iter_java(root):
        rel = os.path.relpath(path, root)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for match in CONST_RE.finditer(text):
            name, value = match.group(1), int(match.group(2))
            val2names[value].add(name)
            name2file.setdefault(name, rel)
    return val2names, name2file


def _domain_of(rel_path):
    low = rel_path.lower()
    for dom in DOMAINS:
        if "/" + dom in low or dom + "/" in low:
            return dom
    return None


def resolve(value, kind, caller_rel, val2names, name2file):
    """Pick the best constant name for `value` used in a get<kind>Model call.
    Returns (name, ambiguous_bool) or (None, False) if unresolvable."""
    names = val2names.get(value)
    if not names:
        return None, False

    # 1. Model IDs are declared in *ModelBank* interfaces - that filter alone
    #    removes the enum-value collisions.
    bank = [n for n in names if BANK_HINT in name2file.get(n, "").lower()]
    pool = bank or list(names)

    # 2. For getChoiceModel, a *_CHOICE name is the real one.
    if kind.lower() == "choice":
        choice = [n for n in pool if n.endswith("_CHOICE")]
        if choice:
            pool = choice

    if len(pool) == 1:
        return pool[0], False

    # 3. Disambiguate bank aliases (Core vs Evo, etc.) by the caller's domain.
    dom = _domain_of(caller_rel)
    if dom:
        domain_hit = [n for n in pool if dom in name2file.get(n, "").lower()]
        if len(domain_hit) == 1:
            return domain_hit[0], False
        if domain_hit:
            pool = domain_hit

    # Still ambiguous: prefer a Core bank over Evo/other, else shortest name.
    pool.sort(key=lambda n: ("core" not in name2file.get(n, "").lower(), len(n), n))
    return pool[0], True


def annotate_text(text, caller_rel, val2names, name2file, stats):
    def repl(match):
        head, kind, num, tail = match.groups()
        name, ambiguous = resolve(
            int(num), kind, caller_rel, val2names, name2file
        )
        if not name:
            stats["unresolved"] += 1
            return match.group(0)
        stats["resolved"] += 1
        if ambiguous:
            stats["ambiguous"] += 1
        return f"{head}/* {name} */ {num}{tail}"

    return CALL_RE.sub(repl, text)


def main():
    ap = argparse.ArgumentParser(description="Annotate model-ID literals with names.")
    ap.add_argument("dir", help="decompiled source tree")
    ap.add_argument("--apply", action="store_true", help="rewrite files in place")
    ap.add_argument("--table", metavar="FILE", help="write a value->name markdown table")
    args = ap.parse_args()

    val2names, name2file = build_index(args.dir)
    print(f"indexed {sum(len(v) for v in val2names.values())} int constants "
          f"({len(val2names)} distinct values)")

    stats = defaultdict(int)
    files_changed = 0
    used = {}  # value -> (name, ambiguous) actually chosen (for the table)
    for path in _iter_java(args.dir):
        rel = os.path.relpath(path, args.dir)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "Model(" not in text:
            continue
        # record chosen names for the table
        for m in CALL_RE.finditer(text):
            name, amb = resolve(int(m.group(3)), m.group(2), rel, val2names, name2file)
            if name:
                used.setdefault(int(m.group(3)), (name, amb))
        new = annotate_text(text, rel, val2names, name2file, stats)
        if new != text:
            files_changed += 1
            if args.apply:
                open(path, "w", encoding="utf-8").write(new)

    action = "annotated" if args.apply else "would annotate"
    print(f"{action} {stats['resolved']} model-ID call sites in {files_changed} files "
          f"({stats['ambiguous']} ambiguous, {stats['unresolved']} unresolved)")
    if not args.apply:
        print("dry-run - pass --apply to rewrite files")

    if args.table:
        with open(args.table, "w", encoding="utf-8") as fh:
            fh.write("| value | name | ambiguous |\n|---|---|---|\n")
            for value in sorted(used):
                name, amb = used[value]
                fh.write(f"| {value} | `{name}` | {'yes' if amb else ''} |\n")
        print(f"wrote table: {args.table} ({len(used)} entries)")


if __name__ == "__main__":
    main()
