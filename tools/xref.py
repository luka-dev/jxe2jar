#!/usr/bin/env python3
"""
xref.py - Cross-reference index for a JAR, built from bytecode (not text).

Reads every class file's constant pool and records which classes reference which
classes/methods/fields via CONSTANT_Class / Methodref / Fieldref / InterfaceMethodref.
That is precise (unlike grepping decompiled source) and answers the question that
matters during reverse engineering: *who uses this?*

Usage:
  python3 tools/xref.py <jar> --callers <owner>[.<member>]   # who references it
  python3 tools/xref.py <jar> --uses <ClassName>             # what a class references
  python3 tools/xref.py <jar> --dump <out.txt>               # full reverse index

  # <owner> is an internal name, e.g. de/audi/tghu/navi/app/map/MapInterface
  # <member> is a method or field name, e.g. validateGELicenseState
"""

import argparse
import struct
import sys
import zipfile
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# constant-pool tag -> fixed byte width after the tag (5/6 = long/double also take
# two pool slots, handled separately)
_FIXED = {3: 4, 4: 4, 5: 8, 6: 8, 9: 4, 10: 4, 11: 4, 12: 4, 18: 4, 17: 4, 8: 2, 7: 2, 16: 2, 15: 3}


def parse_refs(data):
    """Return (this_class, set_of_referenced_symbols). A referenced symbol is
    'owner' for a class ref and 'owner.member' for a method/field ref."""
    if data[:4] != b"\xca\xfe\xba\xbe":
        return None, set()
    count = struct.unpack(">H", data[8:10])[0]
    i = 10
    utf, cls, nat, refs = {}, {}, {}, []
    idx = 1
    while idx < count:
        tag = data[i]
        i += 1
        if tag == 1:
            ln = struct.unpack(">H", data[i:i + 2])[0]
            i += 2
            utf[idx] = data[i:i + ln].decode("utf-8", "replace")
            i += ln
        elif tag == 7:
            cls[idx] = struct.unpack(">H", data[i:i + 2])[0]
            i += 2
        elif tag == 12:
            nat[idx] = struct.unpack(">HH", data[i:i + 4])
            i += 4
        elif tag in (9, 10, 11):
            refs.append((idx, struct.unpack(">HH", data[i:i + 4])))
            i += 4
        elif tag in _FIXED:
            i += _FIXED[tag]
        else:
            return None, set()
        if tag in (5, 6):  # long/double take two slots
            idx += 1
        idx += 1

    def cname(ci):
        return utf.get(cls.get(ci))

    # after the constant pool: access_flags(u2), this_class(u2), super_class(u2)
    this_class = None
    if i + 4 <= len(data):
        this_class = cname(struct.unpack(">H", data[i + 2:i + 4])[0])

    out = set()
    for _, (class_i, nat_i) in refs:
        owner = cname(class_i)
        if not owner:
            continue
        name_i = nat.get(nat_i, (0, 0))[0]
        member = utf.get(name_i)
        out.add(f"{owner}.{member}" if member else owner)
    # plain class refs too
    for ci in cls:
        n = utf.get(cls[ci])
        if n and not n.startswith("["):
            out.add(n)
    return this_class, out


def build(jar_path):
    uses = {}                    # class -> set(referenced symbols)
    referenced_by = defaultdict(set)
    with zipfile.ZipFile(jar_path) as z:
        for name in z.namelist():
            if not name.endswith(".class"):
                continue
            this_class, symbols = parse_refs(z.read(name))
            key = this_class or name[:-6]
            uses[key] = symbols
            for sym in symbols:
                referenced_by[sym].add(key)
    return uses, referenced_by


def main():
    ap = argparse.ArgumentParser(description="Bytecode cross-reference index.")
    ap.add_argument("jar")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--callers", metavar="OWNER[.MEMBER]", help="who references it")
    g.add_argument("--uses", metavar="CLASS", help="what a class references")
    g.add_argument("--dump", metavar="FILE", help="write the full reverse index")
    args = ap.parse_args()

    uses, referenced_by = build(args.jar)

    if args.callers:
        target = args.callers.replace(".", "/") if "/" not in args.callers and "." in args.callers else args.callers
        # member form uses a dot; keep it. Re-derive: internal names use '/', member after last '.'
        target = args.callers
        hits = set()
        for sym, callers in referenced_by.items():
            if sym == target or sym.startswith(target + "."):
                hits |= callers
        for c in sorted(hits):
            print(c)
        print(f"\n{len(hits)} classes reference {target}", file=sys.stderr)
    elif args.uses:
        for sym in sorted(uses.get(args.uses, ())):
            print(sym)
    elif args.dump:
        with open(args.dump, "w", encoding="utf-8") as fh:
            for sym in sorted(referenced_by):
                fh.write(f"{sym}\t{len(referenced_by[sym])}\t"
                         f"{','.join(sorted(referenced_by[sym]))}\n")
        print(f"wrote {args.dump} ({len(referenced_by)} symbols)")


if __name__ == "__main__":
    main()
