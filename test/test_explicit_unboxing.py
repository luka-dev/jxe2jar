#!/usr/bin/env python3
"""Repair javac-located implicit unboxing without changing unrelated source."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from explicit_unboxing import choose, javac_types, repair, repair_all, spell


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


def test_repair_call_shapes():
    """`no suitable method` names the actual argument types; the target overload comes from the
    class's own constant pool (invoked) or, failing that, from javac's candidate list."""
    assert javac_types("(ILjava/lang/String;[Ljava/util/Map$Entry;[[I)V") == \
        ["int", "java.lang.String", "java.util.Map.Entry[]", "int[][]"]
    assert choose(["int", "boolean"], [["int", "java.lang.Object"], ["java.lang.String", "boolean"]]) == ["", "box"]
    assert choose(["java.lang.Integer", "boolean"], [["long", "boolean"], ["java.lang.Object", "java.lang.Object"]]) is None

    source = 'void f(boolean flag) { this.channel\n    .log(1, "s(,)", flag, this.n); }'
    candidates = ("method de.L.log(int,java.lang.String,java.lang.Object,java.lang.Object) is not applicable"
                  "   (argument mismatch; boolean cannot be converted to java.lang.Object)"
                  "   method de.L.log(int,java.lang.String,boolean,boolean) is not applicable"
                  "   (argument mismatch; java.lang.Integer cannot be converted to boolean)")
    message = "2:5:23:44: no suitable method found for log(int,java.lang.String,boolean,java.lang.Integer)   " + candidates
    assert repair(source, message) == 'void f(boolean flag) { this.channel\n    .log(1, "s(,)", Boolean.valueOf(flag), this.n); }'
    # a Boolean last argument fits both overloads with one conversion each: only the class's own
    # constant pool, which holds the (boolean,boolean) descriptor, breaks the tie
    message = message.replace("boolean,java.lang.Integer)", "boolean,java.lang.Boolean)")
    assert repair(source, message) is None
    invoked = {"log": [["int", "java.lang.String", "boolean", "boolean"]]}
    assert repair(source, message, invoked) == 'void f(boolean flag) { this.channel\n    .log(1, "s(,)", flag, (this.n).booleanValue()); }'

    source = "x = new Param(flag);"
    message = ("1:5:4:19: no suitable constructor found for Param(boolean)   constructor de.Param.Param(java.lang.Boolean)"
               " is not applicable   (argument mismatch; boolean cannot be converted to java.lang.Boolean)")
    assert repair(source, message) == "x = new Param(Boolean.valueOf(flag));"


def test_explicit_boxing_against_class_descriptors():
    """Vineflower hides Boolean.valueOf(flag) in a call; javac 1.4 then finds no overload. The
    constant pool of the original class says which overload was called."""
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        tree = work / "source"
        tree.mkdir()
        (tree / "Channel.java").write_text(
            "public class Channel {\n"
            "  public void log(int level, String text, Object a, Object b) {}\n"
            "  public void log(int level, String text, boolean a, boolean b) {}\n}\n")
        caller = tree / "Caller.java"
        original = ("public class Caller {\n  Channel channel = new Channel();\n"
                    "  void run(String s, boolean flag) { this.channel.log(1, \"x\", s, Boolean.valueOf(flag)); }\n}\n")
        caller.write_text(original)
        subprocess.run([str(JDK8 / "javac"), "-source", "1.4", "-target", "1.4", str(tree / "Channel.java"), str(caller)],
                       check=True, capture_output=True)
        jar = work / "classes.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            for name in ("Channel", "Caller"):
                archive.write(tree / (name + ".class"), name + ".class")
        caller.write_text(original.replace("Boolean.valueOf(flag)", "flag"))
        report = work / "compile.json"
        check = [sys.executable, str(ROOT / "tools/isolated_compile_check.py"),
                 str(tree), "--jar", str(jar), "--json-report", str(report)]
        assert subprocess.run(check, capture_output=True).returncode == 1
        assert "no suitable method found for log" in json.loads(report.read_text())["reported_failures"][str(caller.resolve())]["errors"][0]
        fix = [sys.executable, str(ROOT / "tools/explicit_unboxing.py"),
               str(tree), str(jar), str(report), "--libs", str(work), "--apply"]
        applied = subprocess.run(fix, check=True, capture_output=True, text=True)
        assert "explicit wrapper conversions: 1/1" in applied.stdout, applied.stdout + applied.stderr
        assert caller.read_text() == original
        assert subprocess.run(check, capture_output=True).returncode == 0


def test_repair_throws_shape():
    src = (
        "package p;\n\nimport java.io.IOException;\n\npublic class A {\n"
        "    static final String BRACE = \"{\";\n\n"
        "    public void a() {\n        if (this.d == null) {\n            throw new IOException(\"x\");\n        }\n    }\n\n"
        "    void b(int n) throws Exception {\n        if (n > 0) {\n        } else if (n < 0) {\n            c();\n        }\n    }\n\n"
        "    void d() {\n        new Thread() {\n            public void run() {\n                e();\n            }\n        }.start();\n    }\n\n"
        "    static {\n        f();\n    }\n}\n")
    lines = src.split("\n")
    offset = lambda line: sum(len(l) + 1 for l in lines[:line - 1])
    def message(line, exception):
        start = offset(line) + len(lines[line - 1]) - len(lines[line - 1].lstrip())
        return "%d:1:%d:%d: unreported exception %s; must be caught or declared to be thrown" % (
            line, start, start + 3, exception)
    out = repair(src, message(10, "java.io.IOException"))
    assert "    public void a() throws IOException {\n" in out, out
    assert out.replace(" throws IOException", "") == src
    out = repair(src, message(17, "java.net.MalformedURLException"))
    assert "    void b(int n) throws Exception, java.net.MalformedURLException {\n" in out, out
    out = repair(src, message(24, "p.Oops"))
    assert "            public void run() throws Oops {\n" in out, out
    assert repair(src, message(31, "java.io.IOException")) is None


def test_boxing_spelling():
    assert repair("Object o = n;", "1:12:11:12: incompatible types: int cannot be converted to java.lang.Object") == "Object o = new Integer(n);"
    assert repair("Long l = n;", "1:10:9:10: incompatible types: long cannot be converted to java.lang.Long") == "Long l = new Long(n);"
    assert repair("f( n );", "1:1:0:1: no suitable method found for f(int)\n    method A.f(java.lang.Object) is not applicable") == "f( new Integer(n) );"


def test_casts_generics_and_rounds():
    src = ("package p.q;\n\nimport java.util.Map;\nimport de.x.Outer;\nimport de.y.Deep.Inner;\n\n"
           "public class A {\n    Map<String, Stack<State[]>> m;\n    void f() {\n        IContext c = Preconditions.checkNotNull(x);\n"
           "        String[] a = list.toArray();\n        long l = n;\n        Object o = flag ? a : b;\n    }\n}\n")
    assert spell(src, "p.q.IContext") == "IContext" and spell(src, "de.x.Outer.Nested[]") == "Outer.Nested[]"
    assert spell(src, "de.y.Deep.Inner") == "Inner" and spell(src, "de.z.Far") == "de.z.Far"
    def message(needle, text):
        a = src.index(needle)
        return "%d:1:%d:%d: %s" % (src[:a].count("\n") + 1, a, a + len(needle), text)
    out = repair(src, message("Preconditions.checkNotNull(x)", "incompatible types: java.lang.Object cannot be converted to p.q.IContext"))
    assert "IContext c = (IContext) Preconditions.checkNotNull(x);" in out, out
    out = repair(src, message("list.toArray()", "incompatible types: java.lang.Object[] cannot be converted to java.lang.String[]"))
    assert "String[] a = (String[]) list.toArray();" in out, out
    assert repair(src, message("flag ? a : b", "incompatible types: boolean cannot be converted to int")) is None
    a = src.index("l = n;") + 4
    out = repair(src, "%d:1:%d:%d: incompatible types: java.lang.Integer cannot be converted to long" % (src[:a].count("\n") + 1, a, a + 1))
    assert "long l = (n).intValue();" in out, out
    out = repair(src, "8:8:%d:%d: generics are not supported in -source 1.4" % ((src.index("<"),) * 2))
    assert "    Map m;\n" in out and "<" not in out, out
    # one round applies both spans, later one first; the generics error alone rewrites the file
    both = repair_all(src, [message("list.toArray()", "incompatible types: java.lang.Object[] cannot be converted to java.lang.String[]"),
                            message("Preconditions.checkNotNull(x)", "incompatible types: java.lang.Object cannot be converted to p.q.IContext")])
    assert "(IContext) Preconditions" in both and "(String[]) list.toArray()" in both, both


def test_ternary_targets_and_anonymous_overrides():
    src = ("package p;\n\npublic class A {\n    private Handler handler;\n\n"
           "    Reader open(boolean internal) {\n        return internal ? new CharArrayReader(this.value) : this.reader;\n    }\n\n"
           "    void pick(int i) {\n        Ops ops;\n        ops = i == 0 ? this.left : this.right;\n"
           "        this.handler = i > 0 ? this.handlers[i] : this.fallback;\n        Object o = new Consumer2() {\n"
           "            public void accept(State a, final Device b) {\n                use(a, b);\n            }\n        };\n    }\n}\n")
    def ternary(needle, second, third):
        a = src.index(needle)
        q = src.index("?", a)
        text = "incompatible types for ?: neither is a subtype of the other\n  second operand: %s\n  third operand : %s" % (second, third)
        return "%d:%d:%d:%d: %s" % (src[:a].count("\n") + 1, q - src.rfind("\n", 0, q), a, a + len(needle), text)
    out = repair(src, ternary("internal ? new CharArrayReader(this.value) : this.reader", "java.io.CharArrayReader", "p.XMLInputReader"))
    assert "return internal ? (Reader) new CharArrayReader(this.value) : this.reader;" in out, out
    out = repair(src, ternary("i == 0 ? this.left : this.right", "p.LeftOps", "p.RightOps"))
    assert "ops = i == 0 ? (Ops) this.left : this.right;" in out, out
    out = repair(src, ternary("i > 0 ? this.handlers[i] : this.fallback", "p.ButtonHandler", "p.DefaultHandler"))
    assert "this.handler = i > 0 ? (Handler) this.handlers[i] : this.fallback;" in out, out
    line = src[:src.index("new Consumer2()")].count("\n") + 1
    out = repair(src, "%d:20:0:1: <anonymous p.A$1> is not abstract and does not override abstract method accept(java.lang.Object,java.lang.Object) in p.Consumer2" % line)
    assert ("            public void accept(Object a_, Object b_) {\n                State a = (State) a_;\n"
            "                Device b = (Device) b_;\n                use(a, b);\n") in out, out


if __name__ == "__main__":
    test_explicit_unboxing()
    test_repair_expression_shapes()
    test_repair_operator_shapes()
    test_repair_call_shapes()
    test_explicit_boxing_against_class_descriptors()
    test_repair_throws_shape()
    test_boxing_spelling()
    test_casts_generics_and_rounds()
    test_ternary_targets_and_anonymous_overrides()
