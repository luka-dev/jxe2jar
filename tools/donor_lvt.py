"""donor_lvt.py - carry LocalVariableTable / LineNumberTable / SourceFile from non-romized
sibling-firmware jars (the MH2p `lsd.jar`s are compiled with -g) into a converted JXE jar.

  build:  python3 tools/donor_lvt.py build DONOR.jar [MORE.jar ...] -o libs/donor/mh2p-lvt.json.gz
  apply:  python3 tools/donor_lvt.py apply IN.jar libs/donor/mh2p-lvt.json.gz -o OUT.jar

A method is matched by class name + name + descriptor. When its bytecode is identical to the
donor's (constant-pool symbols resolved, so pool layout and ldc/ldc_w do not matter) the whole
LVT and LNT are copied, pcs remapped through instruction indices; otherwise only the parameter
names (LVT entries at pc 0 in argument slots) are copied, which depend on the signature alone.
The database keeps one record per distinct bytecode per method, so several firmware versions
can be merged into it.
"""
import argparse
import collections
import gzip
import hashlib
import json
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtdiff import R, code, cp_bytes, norm, parse, walk  # noqa: E402


def _fingerprint(bc, cp):
    """(sha1 of the symbolic instruction list, instruction start pcs + code length)."""
    ins = norm(bc, cp)[0]
    pcs = [pc for pc, _, _ in walk(bc)] + [len(bc)]
    return hashlib.sha1("\n".join(ins).encode("latin1", "replace")).hexdigest()[:16], pcs


# Names that must not be grafted: `this` (slot 0 of the donor's instance method can be a real
# parameter of ours when only the signature matches), javac's synthetic captures (`this$0`,
# `val$x`), and keywords. With them Vineflower stops recognising its own synthetic patterns and
# prints `this.this$0 = this$0` or `(int) this` (36 MU1316 files regressed on exactly this).
_KEYWORDS = frozenset("abstract assert boolean break byte case catch char class const continue default do double else enum "
                      "extends final finally float for goto if implements import instanceof int interface long native new package "
                      "private protected public return short static strictfp super switch synchronized this throw throws transient "
                      "try void volatile while true false null".split())


def _graftable(name):
    return name not in _KEYWORDS and "$" not in name and name.isidentifier()


def _arg_slots(desc, static):
    i, n = 1, 0 if static else 1
    while desc[i] != ")":
        if desc[i] in "JD": n += 2
        else: n += 1
        if desc[i] == "L": i = desc.index(";", i)
        elif desc[i] == "[":
            while desc[i] == "[": i += 1
            if desc[i] == "L": i = desc.index(";", i)
        i += 1
    return n


def build(jars, out, lines=True):
    db = {"sources": [os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(j)))))) or j for j in jars], "classes": {}}
    st = collections.Counter()
    for jar in jars:
        with zipfile.ZipFile(jar) as z:
            for info in z.infolist():
                if not info.filename.endswith(".class"): continue
                try: c = parse(z.read(info))
                except Exception: st["unparsable"] += 1; continue
                methods = {}
                for (mn, md), m in c["methods"].items():
                    attrs = dict(m["attrs"])
                    if "Code" not in attrs: continue
                    _, _, bc, _, cattrs = code(attrs["Code"], c["cp"])
                    ca = dict(cattrs)
                    if "LocalVariableTable" not in ca and "LineNumberTable" not in ca: continue
                    fp, pcs = _fingerprint(bc, c["cp"]); pos = {pc: i for i, pc in enumerate(pcs)}
                    rec = {"fp": fp, "n": len(pcs) - 1}
                    if "LocalVariableTable" in ca:
                        r = R(ca["LocalVariableTable"]); lvt = []
                        for _ in range(r.u2()):
                            s, ln, ni, di, slot = r.u2(), r.u2(), r.u2(), r.u2(), r.u2()
                            if s in pos and s + ln in pos: lvt.append([pos[s], pos[s + ln], slot, c["cp"].utf(ni), c["cp"].utf(di)])
                        rec["lvt"] = lvt
                    if lines and "LineNumberTable" in ca:
                        r = R(ca["LineNumberTable"])
                        rec["lnt"] = [[pos[s], line] for s, line in (struct.unpack_from(">HH", r.b, 2 + 4 * k) for k in range(r.u2())) if s in pos]
                    methods[mn + md] = rec
                if not any("lvt" in rec for rec in methods.values()):
                    st["classes without LVT"] += 1; continue  # compiled without -g:vars, line numbers alone are not worth the bytes
                entry = db["classes"].setdefault(info.filename[:-6], {"methods": {}})
                sf = dict(c["attrs"]).get("SourceFile")
                if sf is not None: entry.setdefault("sf", c["cp"].utf(R(sf).u2()))
                for key, rec in methods.items():
                    variants = entry["methods"].setdefault(key, [])
                    if not any(v["fp"] == rec["fp"] for v in variants):
                        variants.append(rec); st["method records"] += 1
                st["classes"] += 1
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with gzip.open(out, "wt", compresslevel=9) as f:
        json.dump(db, f, separators=(",", ":"))
    print(f"{out}: {len(db['classes'])} classes, {st['method records']} method records, {os.path.getsize(out) // 1024} KB; {dict(st)}")


def graft(data, donor, st):
    """Return the classfile `data` with donor LVT/LNT/SourceFile added, or `data` unchanged."""
    c = parse(data); cp = c["cp"]; entries = cp.e
    utf = {e[1]: i for i, e in enumerate(entries) if e and e[0] == "utf8"}

    def utf_idx(s):
        if s not in utf: entries.append(("utf8", s)); utf[s] = len(entries) - 1
        return utf[s]

    changed = False
    methods_out = []
    for (mn, md), m in c["methods"].items():
        attrs = list(m["attrs"]); ai = next((k for k, (n, _) in enumerate(attrs) if n == "Code"), None)
        variants = donor["methods"].get(mn + md)
        if ai is not None and variants:
            cd = attrs[ai][1]; ms, ml, bc, ex, cattrs = code(cd, cp)
            if not any(n == "LocalVariableTable" for n, _ in cattrs):
                fp, pcs = _fingerprint(bc, cp)
                exact = next((v for v in variants if v["fp"] == fp and v["n"] == len(pcs) - 1), None)
                new = []
                if exact is not None:
                    lvt = [(pcs[si], pcs[ei] - pcs[si], utf_idx(nm), utf_idx(ds), slot) for si, ei, slot, nm, ds in exact.get("lvt", []) if slot < ml and _graftable(nm)]
                    if lvt: new.append(("LocalVariableTable", lvt)); st["methods: full LVT"] += 1
                    lnt = [(pcs[si], line) for si, line in exact.get("lnt", []) if si < len(pcs)]
                    if lnt: new.append(("LineNumberTable", lnt)); st["methods: line numbers"] += 1
                else:
                    src = next((v for v in variants if v.get("lvt")), None)
                    if src is not None:
                        nargs = _arg_slots(md, m["acc"] & 0x0008)
                        lvt = [(0, len(bc), utf_idx(nm), utf_idx(ds), slot) for si, ei, slot, nm, ds in src["lvt"] if si == 0 and slot < nargs and slot < ml and _graftable(nm)]
                        if lvt: new.append(("LocalVariableTable", lvt)); st["methods: parameter names only"] += 1
                if new:
                    head_len = 8 + len(bc) + 2 + 8 * len(ex)
                    extra = b""
                    for name, rows in new:
                        if name == "LocalVariableTable":
                            body = struct.pack(">H", len(rows)) + b"".join(struct.pack(">HHHHH", *row) for row in rows)
                        else:
                            body = struct.pack(">H", len(rows)) + b"".join(struct.pack(">HH", *row) for row in rows)
                        extra += struct.pack(">HI", utf_idx(name), len(body)) + body
                    attrs[ai] = ("Code", cd[:head_len] + struct.pack(">H", len(cattrs) + len(new)) + cd[head_len + 2:] + extra)
                    changed = True
        methods_out.append((m, attrs))
    class_attrs = list(c["attrs"])
    if "sf" in donor and not any(n == "SourceFile" for n, _ in class_attrs):
        class_attrs.append(("SourceFile", struct.pack(">H", utf_idx(donor["sf"])))); changed = True; st["classes: SourceFile"] += 1
    if not changed: return data

    def attr_bytes(lst):
        return struct.pack(">H", len(lst)) + b"".join(struct.pack(">HI", utf_idx(n), len(d)) + d for n, d in lst)

    # body first: attr_bytes may still intern attribute names; the pool is written last
    body = bytearray(struct.pack(">HHHH", c["acc"], c["this_idx"], c["super_idx"], len(c["iface_idx"])) + b"".join(struct.pack(">H", i) for i in c["iface_idx"]))
    body += struct.pack(">H", len(c["fields"])) + b"".join(struct.pack(">HHH", f["acc"], f["ni"], f["di"]) + attr_bytes(f["attrs"]) for f in c["fields"].values())
    body += struct.pack(">H", len(methods_out)) + b"".join(struct.pack(">HHH", m["acc"], m["ni"], m["di"]) + attr_bytes(a) for m, a in methods_out)
    body += attr_bytes(class_attrs)
    st["classes changed"] += 1
    return struct.pack(">IHHH", 0xCAFEBABE, c["minor"], c["major"], len(entries)) + cp_bytes(entries) + bytes(body)


def apply(in_jar, db_path, out_jar):
    with gzip.open(db_path, "rt") as f: db = json.load(f)["classes"]
    st = collections.Counter()
    with zipfile.ZipFile(in_jar) as zin, zipfile.ZipFile(out_jar, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info)
            if info.filename.endswith(".class"):
                st["classes"] += 1
                donor = db.get(info.filename[:-6])
                if donor:
                    try: data = graft(data, donor, st)
                    except Exception as exc: st["graft errors"] += 1; print(f"WARNING {info.filename}: {exc!r}")
            zout.writestr(info.filename, data)
    print(f"{out_jar}: " + ", ".join(f"{k}={v}" for k, v in sorted(st.items())))
    return st


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("jars", nargs="+"); b.add_argument("-o", required=True)
    b.add_argument("--no-lines", action="store_true", help="skip LineNumberTable (names and types only, much smaller)")
    a = sub.add_parser("apply"); a.add_argument("jar"); a.add_argument("db"); a.add_argument("-o", required=True)
    args = ap.parse_args()
    if args.cmd == "build": build(args.jars, args.o, lines=not args.no_lines)
    else: apply(args.jar, args.db, args.o)


if __name__ == "__main__":
    main()
