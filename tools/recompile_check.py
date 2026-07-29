#!/usr/bin/env python3
"""
recompile_check.py - round-trip QA: does the decompiled VF source recompile?

Closes the jxe2jar loop: .jxe -> jar -> un-inline -> decompile (VF) -> [fixers] ->
  >>> recompile_check <<<  -> report/gate.

Compiles the given VF source file(s) against the authentic jar (combined-final.jar)
so every dependency resolves as binary, reports which files DON'T recompile
(classified by artifact type), AND scans the compiled output for runtime classes
the target J9 lacks.

RUNTIME TARGET (verified from a live core dump, `-Dcom.ibm.oti...`, jclfoun11):
  IBM J9, CDC 1.1 + Foundation Profile 1.1  (~= J2SE 1.4 API), started -noverify.
  The runtime has NO java.lang.StringBuilder / Enum / Iterable (all absent from the
  core; stock uses StringBuffer 28305x, StringBuilder 0x).  So:

    * COMPILE-clean is NOT enough.  `-target 1.5+` compiles `"a"+b` into a
      StringBuilder call; -noverify loads it fine, then NoClassDefFoundError fires
      at the first concat.  Use -target 1.4 (StringBuffer) to match the runtime.
    * -source 1.4 rejects @Override / generics / enums, so VF output that carries
      them must be produced 1.4-style (vineflower --override-annotation=false
      --decompile-generics=false --decompile-enums=false) OR patched.

This tool defaults to -source/-target 1.4 (the real runtime level) and additionally
FAILS any class whose bytecode references a --forbid class (StringBuilder etc.).

METHOD-LEVEL 1.5 API (--jcl):  the --forbid bytecode scan only catches forbidden *classes*
(StringBuilder/Enum/Iterable).  It does NOT catch 1.5+ *methods* on classes that DO exist in
the firmware (e.g. Class.getSimpleName, which stock IBM CDC 1.1 lacks) -- because by default
`java.lang.*` resolves from the JDK8 bootclasspath, where getSimpleName exists, so it compiles
clean (false pass).  Pass `--jcl libs/jcl/<FW>/jcl.jar` to put the firmware JCL on the
-bootclasspath: then java.lang.Class is the *firmware* one (no getSimpleName) and the call
fails to compile -- a real method-level catch.  This is complete-by-construction for a jar
decompiled from that same firmware (every API it uses is in that firmware's reachable JCL).

javap TRAP (why to trust --jcl, not javap):  `javap -classpath jcl.jar java.lang.Class` still
prints the JDK8 class (getSimpleName present, StringBuilder-based body) because java.lang.*
loads from bootclasspath, not -classpath.  To inspect the real firmware class, extract the
.class from the jar and run `javap` on the FILE (`javap Class.class`) -- the authentic one is
StringBuffer-based with IBM *Impl native methods and no getSimpleName.

Usage:
  recompile_check.py <file_or_dir> [more...] [options]
    --jar PATH        stock classpath jar (default: out/MU1316-combined-final.jar)
    --jcl PATH        firmware JCL jar for -bootclasspath (catches method-level 1.5 API);
                      alias --bootclasspath. Default: none (uses javac's JDK8 boot -> misses methods)
    --osgi DIR        dir with org.osgi.*.jar (default: libs)
    --javac PATH      javac (default: bundled Zulu 8)
    --source LVL      -source (default: 1.4)
    --target LVL      -target (default: 1.4)
    --batch N         files per javac invocation (default: 300)
    --limit N         cap number of files (for sampling a huge tree)
    --show K          print up to K example files per artifact category (default: 5)
"""
import argparse, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # jxe2jar/

DEF_JAR   = os.path.join(ROOT, "out", "MU1316-combined-final.jar")
DEF_OSGI  = os.path.join(ROOT, "libs")
DEF_JAVAC = os.path.join(ROOT, "jvms",
    "zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64", "zulu-8.jdk", "Contents", "Home", "bin", "javac")

# Artifact classifiers, checked in order against a file's FIRST error text.
# Each: (category, regex, one-line hint for the fixer).
CLASSIFIERS = [
    ("class$-idiom",     re.compile(r"method class\$|cannot find symbol\b.*\bclass\$", re.S),
                         "decompiler class$ idiom -> Foo.class  (tools/fix_class_literals.py)"),
    ("synthetic-$N-ref", re.compile(r"cannot find symbol\b.*symbol:\s*class\s+\w+\$\d+", re.S),
                         "source refs a synthetic anon class Outer$N (stale 2-arg ctor) -> drop it"),
    ("override-anno",    re.compile(r"annotations are not supported in -source|method does not override"),
                         "decompiler @Override -> strip (or raise -source)"),
    ("javac-crash",      re.compile(r"An exception has occurred in the compiler|java\.lang\.\w*Exception\b.*javac", re.S),
                         "javac internal bug on this source shape -> whole-class / rewrite"),
    ("missing-method-api", re.compile(r"cannot find symbol\b.*symbol:\s*method", re.S),
                         "method absent from firmware JCL (1.5+ API on a class that exists at 1.4) -> avoid it"),
    ("missing-type",     re.compile(r"package [\w.]+ does not exist|cannot find symbol\b.*symbol:\s*class"),
                         "unresolved dependency (native-only / not in jar)"),
    ("generics-raw",     re.compile(r"incompatible types|inconvertible types|unchecked"),
                         "erased-generics raw-type mismatch -> (T[]) cast (fix_vf_artifacts)"),
]

def classify(err_text):
    for cat, rx, hint in CLASSIFIERS:
        if rx.search(err_text):
            return cat, hint
    return "other", err_text.strip().splitlines()[0] if err_text.strip() else "?"

def collect(paths, limit):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for dp, _, fns in os.walk(p):
                for fn in fns:
                    if fn.endswith(".java"):
                        files.append(os.path.join(dp, fn))
        elif p.endswith(".java"):
            files.append(p)
    files.sort()
    if limit:
        files = files[:limit]
    return files

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--jar", default=DEF_JAR)
    ap.add_argument("--jcl", "--bootclasspath", dest="jcl", default=None,
                    help="firmware JCL jar on -bootclasspath (catches method-level 1.5 API "
                         "like Class.getSimpleName that -cp cannot)")
    ap.add_argument("--osgi", default=DEF_OSGI)
    ap.add_argument("--javac", default=DEF_JAVAC)
    ap.add_argument("--source", default="1.4")
    ap.add_argument("--target", default="1.4")
    ap.add_argument("--forbid", default="java/lang/StringBuilder,java/lang/Enum,java/lang/Iterable",
                    help="comma-list of binary class names the runtime lacks; any output class "
                         "referencing one FAILS (jclfoun11 = Foundation 1.1, no 1.5 classes)")
    ap.add_argument("--batch", type=int, default=300)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--show", type=int, default=5)
    a = ap.parse_args()

    cp = a.jar
    if os.path.isdir(a.osgi):
        for j in os.listdir(a.osgi):
            if j.startswith("org.osgi") and j.endswith(".jar") and "sources" not in j and "javadoc" not in j:
                cp += ":" + os.path.join(a.osgi, j)

    files = collect(a.paths, a.limit)
    if not files:
        print("no .java files found"); return 2
    boot = []
    if a.jcl:
        if not os.path.exists(a.jcl):
            print("--jcl not found: %s" % a.jcl); return 2
        boot = ["-bootclasspath", a.jcl]
    print("recompile_check: %d files, -source %s -target %s" % (len(files), a.source, a.target))
    print("classpath: %s (+osgi)%s\n" % (os.path.basename(a.jar),
          "  bootclasspath: %s (method-level API enforced)" % os.path.basename(a.jcl) if a.jcl else
          "  (no --jcl: java.lang.* from JDK8 boot -> method-level 1.5 API NOT caught)"))

    fail = {}  # file -> (category, first_error_line, hint)
    outdir = tempfile.mkdtemp(prefix="recompile_qa_")
    for i in range(0, len(files), a.batch):
        batch = files[i:i+a.batch]
        cmd = [a.javac, "-nowarn", "-proc:none", "-source", a.source, "-target", a.target] + boot + \
              ["-cp", cp, "-d", outdir] + batch
        r = subprocess.run(cmd, capture_output=True, text=True)
        err = r.stderr
        # attribute errors to files by "path.java:line: error:"
        per = {}
        for m in re.finditer(r"^(.+?\.java):(\d+): (error|warning): (.*)$", err, re.M):
            f = m.group(1)
            if m.group(3) == "error":
                per.setdefault(f, []).append(m.group(0))
        # javac-crash has no per-file line; attribute to whole batch if present
        if "An exception has occurred in the compiler" in err and not per:
            for f in batch:
                per.setdefault(f, []).append("javac internal exception (whole batch)")
        for f, errs in per.items():
            cat, hint = classify("\n".join(errs))
            fail[f] = (cat, errs[0], hint)
        sys.stdout.write("\r  compiled %d/%d ..." % (min(i+a.batch, len(files)), len(files)))
        sys.stdout.flush()
    print()

    # --- runtime-safety scan: forbidden classes in the compiled output ---
    forbid = [f.strip() for f in a.forbid.split(",") if f.strip()]
    forbidden_hits = {}  # forbidden_class -> [output .class names]
    if forbid:
        for dp, _, fns in os.walk(outdir):
            for fn in fns:
                if not fn.endswith(".class"):
                    continue
                try:
                    blob = open(os.path.join(dp, fn), "rb").read()
                except OSError:
                    continue
                for fc in forbid:
                    if fc.encode() in blob:
                        forbidden_hits.setdefault(fc, []).append(fn)

    ok = len(files) - len(fail)
    print("\n=== RESULT: %d/%d recompile OK (%.1f%%), %d fail ===" %
          (ok, len(files), 100.0*ok/len(files), len(fail)))
    if forbidden_hits:
        print("\n!!! RUNTIME-UNSAFE: output references classes jclfoun11 LACKS "
              "(loads under -noverify, then NoClassDefFoundError):")
        for fc in sorted(forbidden_hits):
            cs = forbidden_hits[fc]
            print("    %s  in %d classes: %s%s" % (fc, len(cs), ", ".join(cs[:a.show]),
                                                   " ..." if len(cs) > a.show else ""))
        print("    -> lower -target (StringBuilder concat needs -target 1.4) / avoid the API.")
    by_cat = {}
    for f, (cat, line, hint) in fail.items():
        by_cat.setdefault(cat, []).append((f, line, hint))
    for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
        items = by_cat[cat]
        print("\n[%s] %d files  -- %s" % (cat, len(items), items[0][2]))
        for f, line, _ in items[:a.show]:
            rel = f.split("MU1316-combined-vf/")[-1]
            print("    %s" % rel)
            print("      %s" % line.split(": error: ")[-1][:120])
        if len(items) > a.show:
            print("    ... +%d more" % (len(items) - a.show))
    return 0 if (not fail and not forbidden_hits) else 1

if __name__ == "__main__":
    sys.exit(main())
