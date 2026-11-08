#!/usr/bin/env python3
"""Decompiler oracle: how much of a jar's source survives decompile -> recompile, with and without
the LocalVariableTable, and which javac errors remain.

  python3 tools/decompile_oracle.py --orig ORIG.jar --rt ROUNDTRIP.jar --out DIR [--fix] [--cp dep.jar:...]

ORIG is the javac output (with LVT), ROUNDTRIP the same classes after jar2jxe -> jxe2jar (no LVT).
Both are decompiled with tools/vineflower.sh; with --fix the post-passes tools/fix_vf_artifacts.py
and tools/fix_javac_casts.py run on both trees first. Every source file is then compiled alone
against ORIG (+ --cp) with JDK 8 javac at -source 1.5, and the recompiled classes are compared
method by method (tools/rtdiff.py normalisation, StringBuilder/StringBuffer folded):

  * compile ok on the LVT side but not on the round-trip side = cost of the missing LVT
  * compile failures on both sides = decompiler / pipeline defects (or missing dependencies)
  * recompiled round-trip == recompiled LVT-side bytecode = the decompiled text is equivalent
  * recompiled round-trip == ORIGINAL bytecode = exact semantic round trip (javac idioms aside)

Prints one summary line plus the top error categories; DIR keeps the trees, class files and
compile-*.json (per file: ok, first javac error) for a closer look.
"""
import argparse
import collections
import concurrent.futures
import json
import os
import pathlib
import re
import subprocess
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rtdiff import code, load, norm  # noqa: E402

JAVAC = HERE.parent / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin/javac"
ERR = re.compile(r"error: (.*)")


def decompile(jar, out):
    if not out.exists():
        subprocess.run([str(HERE / "vineflower.sh"), str(jar), str(out)], check=True, capture_output=True,
                       env={**os.environ, "VF_THREADS": os.environ.get("VF_THREADS", "8")})


def compile_one(src, root, cp, outdir):
    rel = src.relative_to(root)
    d = outdir / rel.as_posix().replace("/", "__")
    d.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(JAVAC), "-nowarn", "-proc:none", "-encoding", "utf8", "-source", "1.5", "-target", "1.5",
                        "-Xmaxerrs", "3", "-cp", cp, "-d", str(d), str(src)], capture_output=True, text=True)
    first = None
    lines = r.stderr.splitlines()
    for i, line in enumerate(lines):
        m = ERR.search(line)
        if m:
            first = m.group(1)
            sym = next((l.strip() for l in lines[i + 1:i + 5] if l.strip().startswith("symbol:")), None)
            if sym:
                first += " | " + sym
            break
    return rel.as_posix(), r.returncode == 0, first


def compile_tree(root, cp, outdir, jobs):
    files = sorted(root.rglob("*.java"))
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        return dict((rel, (ok, first)) for rel, ok, first in ex.map(lambda f: compile_one(f, root, cp, outdir), files))


def jar_dir(d, jar):
    with zipfile.ZipFile(jar, "w") as z:
        for p in sorted(d.rglob("*.class")):
            z.writestr(p.relative_to(d).as_posix().split("/", 1)[1], p.read_bytes())


def methods(jar):
    out = {}
    for name, c in load(jar).items():
        if isinstance(c, Exception):
            continue
        for (mn, md), m in c["methods"].items():
            a = dict(m["attrs"])
            if "Code" in a:
                ins = norm(code(a["Code"], c["cp"])[2], c["cp"])[0]
                out[(name, mn + md)] = [x.replace("java/lang/StringBuilder", "java/lang/StringBuffer") for x in ins]
    return out


def category(msg):
    if msg is None:
        return "ok"
    if re.search(r"package [\w.]+ does not exist|cannot access|symbol:\s+class |symbol:\s+package|as of release 5, 'enum'", msg):
        return "environmental (missing dependency / 'enum' identifier)"
    if "class$" in msg:
        return "class$ literal leftover"
    if msg.startswith("diamond"):
        return "diamond <> (Java 7 syntax)"
    if "Object cannot be converted" in msg:
        return "for-each over a raw collection"
    if "Object[] cannot be converted" in msg:
        return "raw toArray() without cast"
    return re.sub(r"\b[\w.$<>\[\]]+\b(?=\s*(\(|$))", "X", msg[:70])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--orig", type=pathlib.Path, required=True)
    ap.add_argument("--rt", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--cp", default="", help="extra classpath entries for the per-file javac")
    ap.add_argument("--fix", action="store_true", help="run fix_vf_artifacts + fix_javac_casts on both trees first")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    D = args.out; D.mkdir(parents=True, exist_ok=True)
    cp = str(args.orig) + (os.pathsep + args.cp if args.cp else "")
    res = {}
    for side, jar in (("orig", args.orig), ("rt", args.rt)):
        tree = D / f"src-{side}"
        decompile(jar, tree)
        if args.fix and not (D / f"fixed-{side}").exists():
            subprocess.run([sys.executable, str(HERE / "fix_vf_artifacts.py"), str(tree), "--apply"], check=True, capture_output=True)
            subprocess.run([sys.executable, str(HERE / "fix_javac_casts.py"), str(tree), "--cp", cp, "--apply"], check=True, capture_output=True)
            (D / f"fixed-{side}").touch()
        report = D / f"compile-{side}.json"
        if not report.exists():
            r = compile_tree(tree, cp, D / f"cls-{side}", args.jobs)
            report.write_text(json.dumps(r))
            jar_dir(D / f"cls-{side}", D / f"{side}-recompiled.jar")
        res[side] = json.loads(report.read_text())
    files = sorted(set(res["orig"]) | set(res["rt"]))
    ok = {s: sum(1 for v in res[s].values() if v[0]) for s in res}
    rt_only = [f for f in files if f in res["rt"] and res["orig"].get(f, (False,))[0] and not res["rt"][f][0]]
    mo, mr, morig = methods(D / "orig-recompiled.jar"), methods(D / "rt-recompiled.jar"), methods(args.orig)
    both = set(mo) & set(mr); same_rr = sum(1 for k in both if mo[k] == mr[k])
    vs = set(mr) & set(morig); same_ro = sum(1 for k in vs if mr[k] == morig[k])
    print(f"files: LVT side {len(res['orig'])} / round trip {len(res['rt'])} | compile ok: {ok['orig']} / {ok['rt']} | "
          f"fail only without LVT: {len(rt_only)} | recompiled rt == recompiled LVT side: {same_rr}/{len(both)} methods | "
          f"recompiled rt == original: {same_ro}/{len(vs)}")
    cats = collections.Counter(category(v[1]) for v in res["rt"].values() if not v[0])
    for k, v in cats.most_common(10):
        print(f"  {v:5}  {k}")
    for f in rt_only[:5]:
        print(f"  only without LVT: {f}: {res['rt'][f][1]}")


if __name__ == "__main__":
    main()
