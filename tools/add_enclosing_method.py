#!/usr/bin/env python3
"""Add EnclosingMethod to anonymous classes that lack it.

javac < 1.5 (the firmware's OSGi bundle jars, classfile major 45-48) never wrote the
EnclosingMethod attribute, so Vineflower cannot tie `Outer$N` to its declaration site and
emits it as a standalone Outer$N.java with a dangling `this$0` and failing private access
(MU1316: 631 such files, 507 of them not compiling - 45% of all compile failures). The
converter already synthesizes the attribute for ROM classes (jxe2jar.build_anon_enclosing);
this pass does the same for the classes combine.sh merges in, with the same rule: the
enclosing class and method are the single `new Outer$N` that constructs the anonymous class
(searched within its top-level class family, which is where javac declares it), a site in
`<init>`/`<clinit>` gives the class only (javac writes method_index 0 for field and instance
initializers), and with no site at all the name prefix is used. Classes that already have
the attribute are left alone, so the pass is idempotent.

    python3 tools/add_enclosing_method.py IN.jar -o OUT.jar
"""
import argparse
import collections
import os
import re
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtdiff import code, parse, serialize, walk  # noqa: E402

ANON = re.compile(r"\$\d+$")


def _top(name):
    return name.split("$", 1)[0]


def sites(classes, wanted):
    """anon -> (owner, method name, method desc) for every anon with exactly one `new` site."""
    found = collections.defaultdict(set)
    for name, c in classes.items():
        cp = c["cp"]
        targets = {i: cp.utf(e[1]) for i, e in enumerate(cp.e) if e and e[0] == "class" and cp.utf(e[1]) in wanted}
        if not targets:
            continue
        for (mn, md), m in c["methods"].items():
            cd = next((d for n, d in m["attrs"] if n == "Code"), None)
            if cd is None:
                continue
            bc = code(cd, cp)[2]
            for pc, op, _ in walk(bc):
                if op == 0xBB:  # new
                    t = targets.get(struct.unpack_from(">H", bc, pc + 1)[0])
                    if t and t != name:
                        found[t].add((name, None, None) if mn in ("<init>", "<clinit>") else (name, mn, md))
    return {t: next(iter(s)) for t, s in found.items() if len(s) == 1}


def fix(in_jar, out_jar):
    st = collections.Counter()
    with zipfile.ZipFile(in_jar) as zin, zipfile.ZipFile(out_jar, "w", zipfile.ZIP_DEFLATED) as zout:
        names = [i.filename for i in zin.infolist()]
        cls = [n[:-6] for n in names if n.endswith(".class")]
        st["classes"] = len(cls)
        anon = {n: parse(zin.read(n + ".class")) for n in cls if ANON.search(n)}
        wanted = {n for n, c in anon.items() if not any(a == "EnclosingMethod" for a, _ in c["attrs"])}
        st["anonymous without EnclosingMethod"] = len(wanted)
        families = {_top(n) for n in wanted}
        classes = {n: anon.get(n) or parse(zin.read(n + ".class")) for n in cls if _top(n) in families}
        site = sites(classes, wanted) if wanted else {}
        for fn in names:
            data = zin.read(fn)
            n = fn[:-6]
            if fn.endswith(".class") and n in wanted:
                c = classes[n]
                e = c["cp"].e
                owner, mn, md = site.get(n) or (n.rpartition("$")[0], None, None)
                e.append(("utf8", owner)); e.append(("class", len(e) - 1)); cls_idx = len(e) - 1
                nat = 0
                if mn:
                    e.append(("utf8", mn)); e.append(("utf8", md)); e.append(("nat", len(e) - 2, len(e) - 1)); nat = len(e) - 1
                attrs = list(c["attrs"]) + [("EnclosingMethod", struct.pack(">HH", cls_idx, nat))]
                data = serialize(c, [(m, m["attrs"]) for m in c["methods"].values()], attrs)
                st["added: class+method" if mn else "added: class only"] += 1
            zout.writestr(fn, data)
    print(f"{out_jar}: " + ", ".join(f"{k}={v}" for k, v in sorted(st.items())))
    return st


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jar")
    ap.add_argument("-o", required=True)
    args = ap.parse_args()
    fix(args.jar, args.o)


if __name__ == "__main__":
    main()
