#!/usr/bin/env python3
"""Replace enhanced-for artifacts only when compilation does not regress.

Candidates come from recompile_check.py or isolated_compile_check.py --json-report.
RewriteForeach operates on temporary copies. With a recompile_check report (one javac
over the whole tree) --apply also re-checks the complete tree and aborts promotion if
any previously passing file starts failing; with an isolated report every file is
compiled alone, so a rewrite cannot affect other files and the per-candidate check is
the gate.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from recompile_check import DEF_JAVAC, DEF_OSGI


HERE = Path(__file__).resolve().parent


def message(diagnosis):
    """recompile_check reports `first_error`, isolated_compile_check an `errors` list."""
    return diagnosis.get("first_error") or "\n".join(diagnosis.get("errors") or [])


def candidates(tree, report):
    """(sorted [(path, rel)], isolated) - isolated = the report is isolated_compile_check's."""
    data = json.loads(Path(report).read_text())
    isolated = any("errors" in diagnosis for diagnosis in data["reported_failures"].values())
    selected = []
    for raw, diagnosis in data["reported_failures"].items():
        if "enhanced for loops are not supported" not in message(diagnosis):
            continue
        path = Path(raw).resolve()
        try:
            rel = path.relative_to(tree)
        except ValueError:
            continue
        if path.is_file() and rel.suffix == ".java":
            selected.append((path, rel))
    return sorted(selected, key=lambda pair: str(pair[1])), isolated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tree", type=Path)
    parser.add_argument("jar", type=Path)
    parser.add_argument("diagnostics", type=Path)
    parser.add_argument("--jcl", type=Path)
    parser.add_argument("--osgi", type=Path, default=Path(DEF_OSGI))
    parser.add_argument("--javac", default=DEF_JAVAC)
    parser.add_argument("--java", default="java")
    parser.add_argument("--source", default="1.4")
    parser.add_argument("--target", default=None)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    tree, jar = args.tree.resolve(), args.jar.resolve()
    selected, isolated = candidates(tree, args.diagnostics)
    results = {}
    if selected:
        with tempfile.TemporaryDirectory(prefix="foreach_compile_fallback_") as directory:
            work = Path(directory).resolve()  # the isolated report keys are resolved paths
            paths = []
            for original, rel in selected:
                candidate = work / rel
                candidate.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, candidate)
                paths.append(candidate)
            classpath = os.pathsep.join((str(HERE / "foreach1_4" / "*"), str(HERE / "foreach1_4")))
            rewrite = subprocess.run(
                [args.java, "-cp", classpath, "RewriteForeach", str(jar), str(args.osgi.resolve()), "-"],
                input="\n".join(map(str, paths)) + "\n", capture_output=True, text=True)
            if rewrite.returncode:
                raise RuntimeError("RewriteForeach failed: " + rewrite.stderr[-1000:])

            report = work / "compile.json"
            if isolated:
                command = [sys.executable, str(HERE / "isolated_compile_check.py"), str(work),
                           "--jar", str(jar), "--libs", str(args.osgi.resolve()),
                           "--javac", str(args.javac), "--source", args.source,
                           "--target", args.target or args.source,
                           "--filter-clashing-classes", "--json-report", str(report)]
            else:
                command = [sys.executable, str(HERE / "recompile_check.py"), str(work),
                           "--jar", str(jar), "--osgi", str(args.osgi.resolve()),
                           "--javac", str(args.javac), "--source", args.source,
                           "--target", args.target or args.source,
                           "--json-report", str(report), "--show", "0"]
            if args.jcl:
                command += ["--jcl", str(args.jcl.resolve())]
            check = subprocess.run(command, capture_output=True, text=True)
            if check.returncode not in (0, 1) or not report.is_file():
                raise RuntimeError(command[1].rsplit("/", 1)[-1] + " failed: " + check.stderr[-1000:])
            failures = json.loads(report.read_text())["reported_failures"]
            for (original, rel), candidate in zip(selected, paths):
                key = rel.as_posix()
                if candidate.read_bytes() == original.read_bytes():
                    results[key] = {"status": "skipped", "reason": "no rewrite"}
                elif str(candidate) in failures:
                    results[key] = {"status": "skipped", "reason": message(failures[str(candidate)])}
                else:
                    results[key] = {"status": "would_apply"}

            accepted = [(original, rel, candidate) for (original, rel), candidate in zip(selected, paths)
                        if results[rel.as_posix()]["status"] == "would_apply"]
            if args.apply and accepted and isolated:
                # files compile independently: a rewrite cannot change another file's result
                for original, rel, candidate in accepted:
                    shutil.copy2(candidate, original)
                    results[rel.as_posix()] = {"status": "applied"}
            elif args.apply and accepted:
                staged = (work / "full_tree").resolve()
                shutil.copytree(tree, staged)
                for _, rel, candidate in accepted:
                    shutil.copy2(candidate, staged / rel)
                full_report = work / "full_compile.json"
                full_command = command[:]
                full_command[2] = str(staged)
                full_command[full_command.index(str(report))] = str(full_report)
                full_check = subprocess.run(full_command, capture_output=True, text=True)
                if full_check.returncode not in (0, 1) or not full_report.is_file():
                    raise RuntimeError("full-tree recompile_check failed: " + full_check.stderr[-1000:])
                after = json.loads(full_report.read_text())
                before_fail = {Path(raw).resolve().relative_to(tree).as_posix()
                               for raw in json.loads(args.diagnostics.read_text())["reported_failures"]
                               if Path(raw).resolve().is_relative_to(tree)}
                after_fail = {Path(raw).resolve().relative_to(staged).as_posix()
                              for raw in after["reported_failures"]}
                new_fail = after_fail - before_fail
                if new_fail or after["forbidden_runtime_classes"]:
                    reason = "full-tree regression: %d new failing file(s)" % len(new_fail)
                    if after["forbidden_runtime_classes"]:
                        reason += "; forbidden runtime class references"
                    for _, rel, _ in accepted:
                        results[rel.as_posix()] = {"status": "skipped", "reason": reason}
                else:
                    for original, rel, candidate in accepted:
                        shutil.copy2(candidate, original)
                        results[rel.as_posix()] = {"status": "applied"}

    accepted = sum(value["status"] != "skipped" for value in results.values())
    print("foreach compilable: %d/%d candidate(s); %s" %
          (accepted, len(results), "applied" if args.apply else "dry-run"))
    if args.result:
        args.result.write_text(json.dumps({"tree": str(tree), "jar": str(jar),
                                          "source": args.source, "target": args.target or args.source,
                                          "results": results}, indent=2) + "\n")


if __name__ == "__main__":
    main()
