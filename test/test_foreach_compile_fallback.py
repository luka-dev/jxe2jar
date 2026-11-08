#!/usr/bin/env python3
"""Only compiler-passing enhanced-for rewrites may enter the source tree."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
JDK8 = ROOT / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin"


def test_foreach_compiler_gate():
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        tree = work / "source"
        tree.mkdir()
        good = tree / "Good.java"
        bad = tree / "Bad.java"
        good.write_text("public class Good { int sum(int[] a) { int s = 0; "
                        "for (int n : a) s += n; return s; } }\n")
        bad.write_text("public class Bad { int sum(int[] a) { int s = 0; "
                       "for (int n : a) s += n; return s; } }\n")
        subprocess.run([str(JDK8 / "javac"), "-source", "1.5", "-target", "1.5",
                        str(good), str(bad)], check=True, capture_output=True, text=True)
        jar = work / "classes.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            for name in ("Good", "Bad"):
                archive.write(tree / (name + ".class"), name + ".class")
        bad.write_text(bad.read_text().replace("return s", "return missing"))
        diagnostics = work / "diagnostics.json"
        diagnostics.write_text(json.dumps({"reported_failures": {
            str(path): {"first_error": str(path) + ":1: error: enhanced for loops are not supported in -source 1.4"}
            for path in (good, bad)
        }}))
        command = [sys.executable, str(ROOT / "tools/foreach_compile_fallback.py"),
                   str(tree), str(jar), str(diagnostics), "--osgi", str(work)]
        dry = subprocess.run(command, check=True, capture_output=True, text=True)
        assert "foreach compilable: 1/2" in dry.stdout
        assert "for (int n : a)" in good.read_text()
        incomplete = work / "incomplete-diagnostics.json"
        incomplete.write_text(json.dumps({"reported_failures": {
            str(good): {"first_error": str(good) + ":1: error: enhanced for loops are not supported in -source 1.4"}
        }}))
        blocked = subprocess.run(command[:4] + [str(incomplete)] + command[5:] + ["--apply"],
                                 check=True, capture_output=True, text=True)
        assert "foreach compilable: 0/1" in blocked.stdout
        assert "for (int n : a)" in good.read_text()
        applied = subprocess.run(command + ["--apply"], check=True, capture_output=True, text=True)
        assert "foreach compilable: 1/2" in applied.stdout
        assert "for (int n : a)" not in good.read_text()
        assert "return missing" in bad.read_text()
        assert subprocess.run([str(JDK8 / "javac"), "-source", "1.4", "-target", "1.4",
                               "-cp", str(jar), str(good)], capture_output=True).returncode == 0


def test_foreach_compiler_gate_isolated_report():
    """isolated_compile_check reports carry an `errors` list instead of `first_error`; the gate
    then runs isolated_compile_check on the candidates and needs no whole-tree pass."""
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        tree = work / "source"
        tree.mkdir()
        good, bad = tree / "Good.java", tree / "Bad.java"
        good.write_text("public class Good { int sum(int[] a) { int s = 0; for (int n : a) s += n; return s; } }\n")
        bad.write_text("public class Bad { int sum(int[] a) { int s = 0; for (int n : a) s += n; return s; } }\n")
        subprocess.run([str(JDK8 / "javac"), "-source", "1.5", "-target", "1.5", str(good), str(bad)],
                       check=True, capture_output=True, text=True)
        jar = work / "classes.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            for name in ("Good", "Bad"):
                archive.write(tree / (name + ".class"), name + ".class")
        bad.write_text(bad.read_text().replace("return s", "return missing"))
        diagnostics = work / "isolated.json"
        diagnostics.write_text(json.dumps({"files": 2, "passed": 0, "filtered_classpaths": 0, "reported_failures": {
            str(path.resolve()): {"source": "1.4", "target": "1.4", "filtered_classes": [], "passed": False,
                                  "errors": ["1:40:0:0: enhanced for loops are not supported in -source 1.4"]}
            for path in (good, bad)
        }}))
        command = [sys.executable, str(ROOT / "tools/foreach_compile_fallback.py"),
                   str(tree), str(jar), str(diagnostics), "--osgi", str(work)]
        dry = subprocess.run(command, check=True, capture_output=True, text=True)
        assert "foreach compilable: 1/2" in dry.stdout, dry.stdout + dry.stderr
        assert "for (int n : a)" in good.read_text()
        applied = subprocess.run(command + ["--apply", "--result", str(work / "r.json")], check=True, capture_output=True, text=True)
        assert "foreach compilable: 1/2" in applied.stdout
        assert "for (int n : a)" not in good.read_text() and "return missing" in bad.read_text()
        results = json.loads((work / "r.json").read_text())["results"]
        assert results["Good.java"]["status"] == "applied" and results["Bad.java"]["status"] == "skipped"
        assert "missing" in results["Bad.java"]["reason"]


if __name__ == "__main__":
    test_foreach_compiler_gate()
    test_foreach_compiler_gate_isolated_report()
