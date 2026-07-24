"""#3 Navigation / trust index for the recovered corpus.

After un-inlining, every recovered constant is a real `getstatic Owner.NAME` reference,
so a reverse-engineer can finally ask "who uses this constant?" and "what is value N?".
This builds a searchable index from the final jar (no code mutation):

  constants_by_owner.tsv : owner  NAME  value  #refs      (the catalog)
  constants_by_value.tsv : value  ->  owner.NAME[, ...]    (what is number N?)
  const_xref.tsv         : owner.NAME  ->  referencing classes
  recovery_report.md     : per-package + global recovery stats

References are read from each class's constant pool (Fieldref entries -> the constant
fields they name), which is exact and includes the un-inliner's new getstatic refs.

Usage: python3 tools/nav_index.py <jar> <out_dir>
"""
import sys, os, zipfile, struct
from collections import defaultdict


def parse(data):
    """-> (thisName, {constName:(value,desc)}, set(referenced 'owner\\0name\\0desc'), n_generic, n_methods)"""
    if data[:4] != b"\xca\xfe\xba\xbe":
        return None
    p = 8
    n = struct.unpack_from(">H", data, p)[0]; p += 2
    cp = [None] * n
    i = 1
    while i < n:
        t = data[p]; p += 1
        if t == 1:
            ln = struct.unpack_from(">H", data, p)[0]; cp[i] = data[p + 2:p + 2 + ln].decode("utf-8", "replace"); p += 2 + ln
        elif t == 3: cp[i] = ("I", struct.unpack_from(">i", data, p)[0]); p += 4
        elif t == 4: cp[i] = ("F", struct.unpack_from(">f", data, p)[0]); p += 4
        elif t == 5: cp[i] = ("J", struct.unpack_from(">q", data, p)[0]); p += 8; i += 1
        elif t == 6: cp[i] = ("D", struct.unpack_from(">d", data, p)[0]); p += 8; i += 1
        elif t == 7: cp[i] = ("class", struct.unpack_from(">H", data, p)[0]); p += 2
        elif t == 8: cp[i] = ("str", struct.unpack_from(">H", data, p)[0]); p += 2
        elif t in (9, 10, 11): cp[i] = ("ref", struct.unpack_from(">HH", data, p)); p += 4
        elif t == 12: cp[i] = ("nat", struct.unpack_from(">HH", data, p)); p += 4
        elif t in (16, 19, 20): p += 2
        elif t in (17, 18): p += 4
        elif t == 15: p += 3
        else: return None
        i += 1

    def U(x):
        v = cp[x]; return v if isinstance(v, str) else None
    def clsname(x):
        v = cp[x]; return U(v[1]) if isinstance(v, tuple) and v[0] == "class" else None

    p += 2                                            # access_flags
    this = clsname(struct.unpack_from(">H", data, p)[0]); p += 2
    p += 2                                            # super
    ic = struct.unpack_from(">H", data, p)[0]; p += 2 + 2 * ic

    consts = {}; n_generic = 0
    fc = struct.unpack_from(">H", data, p)[0]; p += 2
    for _ in range(fc):
        acc, ni, di = struct.unpack_from(">HHH", data, p); p += 6
        name, desc = U(ni), U(di); ac = struct.unpack_from(">H", data, p)[0]; p += 2
        cv = None
        for _a in range(ac):
            ani = struct.unpack_from(">H", data, p)[0]; aln = struct.unpack_from(">I", data, p + 2)[0]
            an = U(ani)
            if an == "ConstantValue": cv = struct.unpack_from(">H", data, p + 6)[0]
            elif an == "Signature": n_generic += 1
            p += 6 + aln
        if cv is not None and (acc & 0x0008) and (acc & 0x0010):
            e = cp[cv]
            if isinstance(e, tuple) and e[0] in ("I", "J", "F", "D"):
                consts[name] = (e[1], desc)
            elif isinstance(e, tuple) and e[0] == "str":
                consts[name] = (U(e[1]), desc)

    mc = struct.unpack_from(">H", data, p)[0]; p += 2
    for _ in range(mc):
        p += 6; ac = struct.unpack_from(">H", data, p)[0]; p += 2
        for _a in range(ac):
            aln = struct.unpack_from(">I", data, p + 2)[0]; nm = U(struct.unpack_from(">H", data, p)[0])
            if nm == "Signature": n_generic += 1
            p += 6 + aln

    # references: Fieldref entries -> owner\0name\0desc
    refs = set()
    for e in cp:
        if isinstance(e, tuple) and e[0] == "ref":
            ci, ni = e[1]
            c = cp[ci]; nat = cp[ni]
            if isinstance(c, tuple) and c[0] == "class" and isinstance(nat, tuple) and nat[0] == "nat":
                owner = U(c[1]); fn = U(nat[1][0]); fd = U(nat[1][1])
                if owner and fn and fd:
                    refs.add(owner + "\0" + fn + "\0" + fd)
    return this, consts, refs, n_generic, mc


def main():
    jar, outd = sys.argv[1], sys.argv[2]
    os.makedirs(outd, exist_ok=True)
    decl = {}                       # owner -> {name: (value, desc)}
    referrers = defaultdict(set)    # owner\0name -> set(referring class)
    gen_classes = 0; obf = 0; total_cls = 0
    all_ref_sigs = defaultdict(set) # owner\0name\0desc -> referrers (need declared descs to match name)

    with zipfile.ZipFile(jar) as z:
        parsed = []
        for info in z.infolist():
            if not info.filename.endswith(".class"): continue
            try: r = parse(z.read(info))
            except Exception: r = None
            if not r: continue
            this, consts, refs, ng, _ = r
            parsed.append((this, refs))
            total_cls += 1
            if consts: decl[this] = consts
            if ng: gen_classes += 1
            simple = this.split("/")[-1].split("$")[0]
            if len(simple) <= 2: obf += 1

    # known constant field sigs -> (owner,name)
    sig2cn = {}
    for owner, cs in decl.items():
        for name, (val, desc) in cs.items():
            sig2cn[owner + "\0" + name + "\0" + desc] = (owner, name)
    for this, refs in parsed:
        for s in refs:
            if s in sig2cn:
                o, nm = sig2cn[s]; referrers[o + "\0" + nm].add(this)

    # write catalog by owner
    n_const = sum(len(c) for c in decl.values())
    with open(os.path.join(outd, "constants_by_owner.tsv"), "w") as f:
        f.write("owner\tname\tvalue\trefs\n")
        for owner in sorted(decl):
            for name, (val, desc) in sorted(decl[owner].items()):
                nref = len(referrers.get(owner + "\0" + name, ()))
                f.write(f"{owner}\t{name}\t{val!r}\t{nref}\n")
    # by value (int only, the "what is number N" lookup)
    byval = defaultdict(list)
    for owner, cs in decl.items():
        for name, (val, desc) in cs.items():
            if desc == "I": byval[val].append(f"{owner.split('/')[-1]}.{name}")
    with open(os.path.join(outd, "constants_by_value.tsv"), "w") as f:
        f.write("value\tcandidates\n")
        for v in sorted(byval):
            f.write(f"{v}\t{', '.join(sorted(byval[v])[:12])}{' ...' if len(byval[v])>12 else ''}\n")
    # xref (only referenced constants)
    with open(os.path.join(outd, "const_xref.tsv"), "w") as f:
        f.write("constant\treferrers\n")
        for k in sorted(referrers, key=lambda x: -len(referrers[x])):
            o, nm = k.split("\0"); rs = sorted(referrers[k])
            f.write(f"{o.split('/')[-1]}.{nm}\t{len(rs)}\t{', '.join(r.split('/')[-1] for r in rs[:10])}{' ...' if len(rs)>10 else ''}\n")
    # report
    referenced = sum(1 for k in referrers if referrers[k])
    with open(os.path.join(outd, "recovery_report.md"), "w") as f:
        f.write(f"# Recovery / navigation report\n\n")
        f.write(f"- classes: **{total_cls}**\n")
        f.write(f"- static-final constants declared: **{n_const}** in {len(decl)} owners\n")
        f.write(f"- constants actually referenced (getstatic): **{referenced}**\n")
        f.write(f"- classes carrying generic Signatures: **{gen_classes}**\n")
        f.write(f"- obfuscated (<=2-char simple name) classes: **{obf}**\n\n")
        f.write("## Most-referenced constants (navigation hot-spots)\n\n")
        top = sorted(referrers, key=lambda x: -len(referrers[x]))[:25]
        for k in top:
            o, nm = k.split("\0")
            f.write(f"- `{o.split('/')[-1]}.{nm}` - {len(referrers[k])} refs\n")
    print(f"classes={total_cls} constants={n_const} referenced={referenced} generic-classes={gen_classes} obfuscated={obf}")
    print("wrote:", ", ".join(sorted(os.listdir(outd))))


if __name__ == "__main__":
    main()
