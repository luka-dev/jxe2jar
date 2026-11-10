#!/usr/bin/env python3
"""Repair javac-located implicit unboxing without changing unrelated source."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from explicit_unboxing import repair


ROOT = Path(__file__).resolve().parents[1]
JDK8 = ROOT / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin"


def test_explicit_unboxing():
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        tree = work / "source"
        tree.mkdir()
        source = tree / "Example.java"
        original = ("public class Example { // 😀 UTF-16 offset\n"
                    "  int value() { return Integer.valueOf(7).intValue(); }\n}\n")
        source.write_text(original)
        subprocess.run([str(JDK8 / "javac"), "-source", "1.4", "-target", "1.4", str(source)],
                       check=True, capture_output=True)
        jar = work / "classes.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            archive.write(tree / "Example.class", "Example.class")
        source.write_text(original.replace(".intValue()", ""))
        report = work / "compile.json"
        check = [sys.executable, str(ROOT / "tools/isolated_compile_check.py"),
                 str(tree), "--jar", str(jar), "--json-report", str(report)]
        assert subprocess.run(check, capture_output=True).returncode == 1
        assert "Integer cannot be converted to int" in json.loads(report.read_text())["reported_failures"][str(source.resolve())]["errors"][0]
        fix = [sys.executable, str(ROOT / "tools/explicit_unboxing.py"),
               str(tree), str(jar), str(report), "--libs", str(work)]
        dry = subprocess.run(fix, check=True, capture_output=True, text=True)
        assert "explicit wrapper conversions: 1/1" in dry.stdout
        assert ".intValue()" not in source.read_text()
        applied = subprocess.run(fix + ["--apply"], check=True, capture_output=True, text=True)
        assert "explicit wrapper conversions: 1/1" in applied.stdout
        assert source.read_text() == original.replace("Integer.valueOf(7).intValue()",
                                                      "(Integer.valueOf(7)).intValue()")
        assert subprocess.run(check, capture_output=True).returncode == 0


def test_repair_expression_shapes():
    source = "switch(map.getKey()) { default: break; }"
    start = source.index("(")
    end = source.index("))", start) + 2
    message = "%d:%d:%d:%d: incompatible types: java.lang.Object cannot be converted to int" % (1, 7, start, end)
    assert repair(source, message) == "switch(((Integer)(map.getKey())).intValue()) { default: break; }"

    source = "consume(flag);"
    start, end = source.index("flag"), source.index("flag") + len("flag")
    message = "%d:%d:%d:%d: incompatible types: boolean cannot be converted to java.lang.Object" % (1, 1, start, end)
    assert repair(source, message) == "consume(Boolean.valueOf(flag));"


def test_repair_operator_shapes():
    """Binary, unary and ?: operands are located from javac's column, which points at the operator."""
    source = "if (!flag) {}"
    message = "1:5:4:9: bad operand type java.lang.Boolean for unary operator '!'"
    assert repair(source, message) == "if (!(flag).booleanValue()) {}"

    source = "while (this.length > read) {}"
    message = "1:20:7:25: bad operand types for binary operator '>'   first type:  java.lang.Integer   second type: int"
    assert repair(source, message) == "while ((this.length).intValue() > read) {}"
    message = "1:20:7:25: bad operand types for binary operator '>'   first type:  int   second type: java.lang.Integer"
    assert repair(source, message) == "while (this.length > (read).intValue()) {}"
    source = "x = a + b;"
    message = "1:7:4:9: bad operand types for binary operator '+'\n  first type:  java.lang.Long\n  second type: java.lang.Long"
    assert repair(source, message) == "x = (a).longValue() + (b).longValue();"

    source = "return c != null ? (c) : f(\"?:\", a ? 1 : 2);"
    message = "1:18:7:43: incompatible types for ?: neither is a subtype of the other   second operand: java.lang.Long   third operand : long"
    assert repair(source, message) == "return c != null ? ((c)).longValue() : f(\"?:\", a ? 1 : 2);"
    message = "1:18:7:43: incompatible types for ?: neither is a subtype of the other   second operand: int   third operand : java.lang.Integer"
    assert repair(source, message) == "return c != null ? (c) : (f(\"?:\", a ? 1 : 2)).intValue();"
    message = "1:18:7:43: incompatible types for ?: neither is a subtype of the other   second operand: java.io.Reader   third operand : java.io.Writer"
    assert repair(source, message) is None

    source = "this.active = active;"
    message = "1:15:14:20: incompatible types: boolean cannot be converted to java.lang.Boolean"
    assert repair(source, message) == "this.active = Boolean.valueOf(active);"


if __name__ == "__main__":
    test_explicit_unboxing()
    test_repair_expression_shapes()
    test_repair_operator_shapes()
