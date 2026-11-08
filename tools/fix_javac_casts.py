#!/usr/bin/env python3
"""Put back the casts Vineflower drops from 1.4-era code, where javac says so.

Decompiling pre-generics bytecode, Vineflower leaves out casts it believes redundant and javac
then reports "incompatible types: Object cannot be converted to T" (or Object[] -> T[]). Every
file is compiled alone (classpath = the jar it was decompiled from plus --cp) and only the
reported lines are rewritten, so files that compile are never touched:

  * `for (String name : names) {`  (raw collection)  ->  `for (Object name_ : names) {`
                                                          `    String name = (String) name_;`
  * `x = AccessController.doPrivileged(...)`, `return list.toArray(EMPTY)`, `flag = get(...)`
    ->  `x = (T) ...`, `return (T[]) ...`, `flag = (Boolean) ...` - the cast goes right after the
    `=` / `return` of the statement, found on the reported line or the lines just above it when
    javac points into a wrapped call chain.

Round-trip corpus: 119 + ~50 of 3500 files failed on these two shapes.

  python3 tools/fix_javac_casts.py TREE --cp orig.jar[:dep.jar] [--bootclasspath rt.jar]
                                   [--only-failing isolated-report.json] [--jobs 8] --apply
"""
import argparse
import concurrent.futures
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
DEF_JAVAC = str(HERE.parent / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin/javac")
ERROR = re.compile(r"^(.*?):(\d+): error: incompatible types: (Object(?:\[\])*) cannot be converted to ([\w.$<>\[\]]+)")
ASSIGN = re.compile(r"^(?P<head>\s*(?:return|[^=;]*?[^=!<>]=)\s+)(?P<rhs>(?!\(\s*[\w.$<>\[\]]+\s*\)\s)\S.*)$")
HEADER = re.compile(r"^(?P<indent>\s*)for \((?P<final>final\s+)?(?P<type>[\w.$]+(?:<[^>]*>)?(?:\[\])*)\s+(?P<var>[A-Za-z_$][\w$]*)\s*:\s*(?P<expr>.+)\)\s*\{\s*$")
WRAPPER = {"int": "Integer", "long": "Long", "short": "Short", "byte": "Byte", "char": "Character",
           "boolean": "Boolean", "float": "Float", "double": "Double"}


def javac_errors(javac, path, cp, bcp, source):
    with tempfile.TemporaryDirectory(prefix="fix_raw_foreach_") as out:
        cmd = [javac, "-nowarn", "-proc:none", "-encoding", "utf8", "-source", source, "-target", source, "-Xmaxerrs", "500",
               "-d", out, "-cp", cp]
        if bcp:
            cmd += ["-bootclasspath", bcp]
        r = subprocess.run(cmd + [str(path)], capture_output=True, text=True)
    lines = {}
    err = r.stderr.splitlines()
    for i, line in enumerate(err):
        m = ERROR.match(line)
        if m and pathlib.Path(m.group(1)).resolve() == path.resolve():
            # javac prints the source line, then a caret under the offending sub-expression
            col = err[i + 2].index("^") if i + 2 < len(err) and "^" in err[i + 2] else None
            lines[int(m.group(2))] = (m.group(4), col)
    return r.returncode == 0, lines


def _cast(target):
    return "(" + WRAPPER.get(target, target) + ") "


def _expr_start(body, col):
    """javac marks a call at its `(` and an operator at its symbol; walk back over the primary
    (identifiers, dots, balanced () and []) to where the cast has to go."""
    i = col
    while i > 0:
        ch = body[i - 1]
        if ch.isalnum() or ch in "_$.":
            i -= 1
        elif ch in ")]":
            open_, close = ("(", ")") if ch == ")" else ("[", "]")
            depth = 0
            while i > 0:
                i -= 1
                depth += (body[i] == close) - (body[i] == open_)
                if depth == 0:
                    break
        else:
            break
    return i


def _cast_position(body, col, target):
    """Column to insert the cast at, or None when the line is a wrapped continuation."""
    if col is None or col >= len(body):
        return None
    ch = body[col]
    if ch == "?":  # conditional: cast the non-null branch
        depth = 0
        for j in range(col + 1, len(body)):
            depth += body[j] in "([" ; depth -= body[j] in ")]"
            if depth == 0 and body[j] == ":":
                a, b = body[col + 1:j], body[j + 1:]
                if b.strip() and b.strip() != "null" and not b.strip().endswith(("?", "(")):
                    return j + 1 + (len(b) - len(b.lstrip()))
                return col + 1 + (len(a) - len(a.lstrip())) if a.strip() != "null" else None
        return None
    start = _expr_start(body, col) if ch in "([" or ch.isalnum() or ch in "_$\"'" else None
    if start is None or (start == col and ch in "([") or body[start:].lstrip().startswith(".") or body[:start].rstrip().endswith("."):
        return None
    return start if not body[start:].startswith(_cast(target).rstrip()) else None


def rewrite(text, bad_lines):
    """Return (new_text, rewritten_count)."""
    src = text.splitlines(keepends=True)
    out, n = list(src), 0
    for lineno, (target, col) in sorted(bad_lines.items(), reverse=True):
        body = src[lineno - 1].rstrip("\r\n"); eol = src[lineno - 1][len(body):]
        m = HEADER.match(body)
        if m:
            g = m.groupdict(); tmp = g["var"] + "_"
            out[lineno - 1] = (f"{g['indent']}for (Object {tmp} : {g['expr']}) {{{eol}"
                               f"{g['indent']}    {g['final'] or ''}{g['type']} {g['var']} = {_cast(g['type'])}{tmp};{eol}")
            n += 1
            continue
        # the caret marks the offending sub-expression (assignment RHS, ternary branch, argument):
        # cast exactly there, unless javac points at a `.call(` continuation of a wrapped chain
        pos = _cast_position(body, col, target)
        if pos is not None:
            out[lineno - 1] = body[:pos] + _cast(target) + body[pos:] + eol
            n += 1
            continue
        for k in range(lineno - 1, max(-1, lineno - 6), -1):
            cand = src[k].rstrip("\r\n")
            if k != lineno - 1 and (cand.rstrip().endswith((";", "{", "}")) or not cand.strip()):
                break
            a = ASSIGN.match(cand)
            if a and ("(" + WRAPPER.get(target, target) + ")") not in a.group("rhs")[:len(target) + 4]:
                out[k] = a.group("head") + _cast(target) + a.group("rhs") + src[k][len(cand):]
                n += 1
                break
    return "".join(out), n


def process(path, args):
    ok, bad = javac_errors(args.javac, path, args.cp, args.bootclasspath, args.source)
    if ok or not bad:
        return path, ok, 0, ok
    text = path.read_text(encoding="utf-8", errors="replace")
    new, n = rewrite(text, bad)
    if n == 0:
        return path, ok, 0, ok
    if args.apply:
        path.write_text(new, encoding="utf-8")
        ok_after = javac_errors(args.javac, path, args.cp, args.bootclasspath, args.source)[0]
    else:
        with tempfile.NamedTemporaryFile("w", suffix=".java", dir=path.parent, delete=False, encoding="utf-8") as tmp:
            tmp.write(new); tmp_path = pathlib.Path(tmp.name)
        try:
            ok_after = javac_errors(args.javac, tmp_path, args.cp, args.bootclasspath, args.source)[0]
        finally:
            tmp_path.unlink()
    return path, ok, n, ok_after


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tree", type=pathlib.Path)
    ap.add_argument("--cp", required=True, help="classpath for the per-file javac (the decompiled jar and its dependencies)")
    ap.add_argument("--bootclasspath", default=None, help="e.g. the firmware JCL; default = the javac's own runtime")
    ap.add_argument("--javac", default=DEF_JAVAC)
    ap.add_argument("--source", default="1.5")
    ap.add_argument("--only-failing", type=pathlib.Path, help="isolated_compile_check --json-report: restrict to its reported_failures")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    files = sorted(args.tree.rglob("*.java"))
    if args.only_failing:
        wanted = {pathlib.Path(p).resolve() for p in json.loads(args.only_failing.read_text())["reported_failures"]}
        files = [f for f in files if f.resolve() in wanted]
    rewritten = fixed = touched = 0
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
        for path, ok_before, n, ok_after in ex.map(lambda f: process(f, args), files):
            if n:
                touched += 1; rewritten += n; fixed += (not ok_before) and ok_after
    verb = "rewrote" if args.apply else "would rewrite"
    print(f"{verb} {rewritten} cast(s) in {touched} of {len(files)} file(s); {fixed} file(s) compile afterwards")
    if not args.apply:
        print("dry-run - pass --apply to rewrite files")


if __name__ == "__main__":
    main()
