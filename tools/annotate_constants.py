#!/usr/bin/env python3
"""
annotate_constants.py - Recover inlined `static final int` names across a decompile.

javac inlines integer constants at the call site, so decompiled code shows raw
magic numbers (getChoiceModel(402127), getText(871), ...). The symbolic names
survive in registry interfaces/classes, so value->name is recoverable. This tool
annotates each recognised accessor call in place:

    getChoiceModel(402127)  ->  getChoiceModel(/* NAV_MAP_SERVICELIST_GOOGLE_EARTH_CHOICE */ 402127)
    getText(871)            ->  getText(/* TEXT_CONST_EVO_INPUTFIELD_DELETE_PROMPT */ 871)

Resolution is context-aware to beat the two ambiguities that plague raw lookups:
  * enum collisions - a small value (1) matches hundreds of enum constants, so a
    name defined in the accessor's registry (model IDs live in *ModelBank* files,
    text IDs in *Constants*/DSI files) is preferred, and small values below a
    per-accessor floor are left alone.
  * name aliases - a naming-convention hint (*_CHOICE for choices, TXT_/TEXT_ for
    text) and the caller's package domain pick the right one.

It supersedes annotate_model_ids.py (which only handled get*Model).

Usage:
  python3 tools/annotate_constants.py <dir>                 # dry-run (report only)
  python3 tools/annotate_constants.py <dir> --apply         # rewrite files in place
  python3 tools/annotate_constants.py <dir> --table map.md  # write value->name table
"""

import argparse
import os
import re
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONST_RE = re.compile(r"\bint\s+([A-Z][A-Za-z0-9_]+)\s*=\s*(-?\d+)\s*;")

# Each accessor rule: how to find calls, which registry files hold its names,
# a substring the "real" name tends to carry, and a value floor below which the
# argument is too collision-prone to annotate.
RULES = [
    {   # getChoiceModel / getButtonModel / getLabelModel / ... - model IDs
        "name": "model",
        "call": re.compile(r"(get([A-Z][A-Za-z]*)Model\(\s*)(\d+)(\s*\))"),
        "registry": "modelbank",
        "hint": lambda kind: "_CHOICE" if kind.lower() == "choice" else None,
        "floor": 0,
    },
    {   # getText / getString - HMI text-resource IDs
        "name": "text",
        "call": re.compile(r"(get(Text|String)\(\s*)(\d+)(\s*\))"),
        "registry": None,   # text consts are scattered; rely on name hint + floor
        "hint": lambda kind: ("TEXT_", "TXT_", "_TEXT", "STR_"),
        "floor": 100,       # below this a text arg is almost always an enum collision
    },
]

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
    val2names = defaultdict(set)
    name2file = {}
    for path in _iter_java(root):
        rel = os.path.relpath(path, root)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in CONST_RE.finditer(text):
            val2names[int(m.group(2))].add(m.group(1))
            name2file.setdefault(m.group(1), rel)
    return val2names, name2file


def _domain_of(rel_path):
    low = rel_path.lower()
    for dom in DOMAINS:
        if "/" + dom in low or dom + "/" in low:
            return dom
    return None


def resolve(value, kind, caller_rel, rule, val2names, name2file):
    if value < rule["floor"]:
        return None, False
    names = val2names.get(value)
    if not names:
        return None, False

    pool = list(names)
    if rule["registry"]:
        bank = [n for n in pool if rule["registry"] in name2file.get(n, "").lower()]
        if bank:
            pool = bank

    hint = rule["hint"](kind)
    if hint:
        hints = (hint,) if isinstance(hint, str) else hint
        hinted = [n for n in pool if any(h in n for h in hints)]
        if hinted:
            pool = hinted

    if len(pool) == 1:
        return pool[0], False

    dom = _domain_of(caller_rel)
    if dom:
        hit = [n for n in pool if dom in name2file.get(n, "").lower()]
        if len(hit) == 1:
            return hit[0], False
        if hit:
            pool = hit

    pool.sort(key=lambda n: ("core" not in name2file.get(n, "").lower(), len(n), n))
    return pool[0], True


def annotate_text(text, caller_rel, val2names, name2file, stats, used):
    def make_repl(rule):
        def repl(match):
            head, kind, num, tail = match.groups()
            name, amb = resolve(
                int(num), kind, caller_rel, rule, val2names, name2file
            )
            if not name:
                stats["skipped"] += 1
                return match.group(0)
            stats["resolved"] += 1
            if amb:
                stats["ambiguous"] += 1
            used.setdefault(int(num), (name, amb))
            return f"{head}/* {name} */ {num}{tail}"

        return repl

    for rule in RULES:
        text = rule["call"].sub(make_repl(rule), text)
    return text


def main():
    ap = argparse.ArgumentParser(description="Annotate inlined constant names.")
    ap.add_argument("dir")
    ap.add_argument("--apply", action="store_true", help="rewrite files in place")
    ap.add_argument("--table", metavar="FILE", help="write a value->name markdown table")
    args = ap.parse_args()

    val2names, name2file = build_index(args.dir)
    print(f"indexed {sum(len(v) for v in val2names.values())} int constants "
          f"({len(val2names)} distinct values)")

    stats = defaultdict(int)
    used = {}
    files_changed = 0
    quick = tuple({r["call"].pattern.split("(")[1].split("|")[0].strip("\\")
                   for r in RULES})  # cheap pre-filter substrings, best-effort
    for path in _iter_java(args.dir):
        rel = os.path.relpath(path, args.dir)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "Model(" not in text and "get" not in text:
            continue
        new = annotate_text(text, rel, val2names, name2file, stats, used)
        if new != text:
            files_changed += 1
            if args.apply:
                open(path, "w", encoding="utf-8").write(new)

    action = "annotated" if args.apply else "would annotate"
    print(f"{action} {stats['resolved']} call sites in {files_changed} files "
          f"({stats['ambiguous']} ambiguous, {stats['skipped']} below-floor/unresolved)")
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
