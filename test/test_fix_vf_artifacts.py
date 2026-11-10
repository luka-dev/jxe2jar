"""Remaining source repairs must yield executable Java 1.4."""

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from fix_vf_artifacts import fix_text  # noqa: E402


def test_remaining_repairs_compile_and_run():
    outer = """import java.util.List;
interface Event { int value(); }
class Navigation {}
public class Outer {
    Navigation navigation;
    Outer(Navigation navigation) { this.navigation = navigationx; }
    void accept(Void void) {}
    String cast(Object value) { return (String & String)value; }
    String[] array(List list) { return list.toArray(new String[0]); }
    Class literal() { return class$("java.lang.String"); }
    Class cache() { return (class$java$lang$String == null
        ? (class$java$lang$String = class$("java.lang.String")) : class$java$lang$String); }
    static String classNameFromPackageName(Class type) { return type.getName(); }
    String nestedCache() { return classNameFromPackageName(
        class$java$lang$Integer == null
            ? (class$java$lang$Integer = class$("java.lang.Integer")) : class$java$lang$Integer
    ); }
    public static void main(String[] args) {
        Outer outer = new Outer(new Navigation());
        if (outer.navigation == null || outer.literal() != String.class || outer.cache() != String.class
                || !outer.nestedCache().equals("java.lang.Integer")
                || !outer.cast("ok").equals("ok") || outer.array(java.util.Arrays.asList(new String[]{"ok"})).length != 1
                || new Outer$1(outer).value() != 7)
            throw new AssertionError("source repair changed behavior");
    }
    final int number = 7;
}
"""
    orphan = """class Outer$1 implements Event {
    Outer$1(Outer outer) { this.this$0 = outer; }
    public int value() { return this.this$0.number; }
}
"""
    fixed_outer, outer_count = fix_text(outer)
    fixed_orphan, orphan_count = fix_text(orphan)
    assert outer_count == 9 and orphan_count == 1
    assert fix_text(fixed_outer)[0] == fixed_outer
    assert fix_text(fixed_orphan)[0] == fixed_orphan

    jdk = ROOT / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin"
    with tempfile.TemporaryDirectory() as directory:
        work = pathlib.Path(directory)
        (work / "Outer.java").write_text(fixed_outer)
        (work / "Outer$1.java").write_text(fixed_orphan)
        subprocess.run(
            [str(jdk / "javac"), "-source", "1.4", "-target", "1.4", "Outer.java", "Outer$1.java"],
            cwd=work, check=True, capture_output=True, text=True,
        )
        subprocess.run([str(jdk / "java"), "Outer"], cwd=work, check=True)


if __name__ == "__main__":
    test_remaining_repairs_compile_and_run()


def test_diamond_becomes_raw_constructor():
    src = "List a = new ArrayList<>(Arrays.asList(X));\nMap<String, List<Integer>> m = new java.util.HashMap<>();\nnew Foo<>();"
    fixed, n = fix_text(src)
    assert n == 3 and "<>" not in fixed
    assert "new ArrayList(Arrays.asList(X))" in fixed and "new java.util.HashMap()" in fixed and "new Foo()" in fixed
    assert fix_text(fixed)[0] == fixed


def test_inverted_class_dollar_cache():
    src = ("if (m != null\n    && (class$com$x$Y != null\n        ? class$com$x$Y\n        : (\n"
           "            class$com$x$Y = com.x.Y.class\n        ))\n    .isAssignableFrom(m.getClass())) {}")
    fixed, n = fix_text(src)
    assert n == 1 and "class$" not in fixed and "(com.x.Y.class)" in fixed, fixed


def test_toarray_cast_in_any_position():
    src = ("String[] a = list.toArray(new String[0]);\n"
           "return x.isEmpty() ? null : x.toArray(new String[x.size()]);\n"
           "return this.classes.values().toArray(new ClassStats[0]);\n"
           "return (String[]) done.toArray(new String[0]);\n")
    fixed, n = fix_text(src)
    assert "a = (String[]) list.toArray(new String[0])" in fixed
    assert ": (String[]) x.toArray(new String[x.size()])" in fixed
    assert "return (ClassStats[]) this.classes.values().toArray(new ClassStats[0])" in fixed
    assert fixed.count("(String[]) done.toArray") == 1 and n == 3, fixed
    assert fix_text(fixed)[0] == fixed


def test_dangling_outer_field_with_this0_parameter():
    src = "class Outer$1 implements Runnable {\n    Outer$1(Outer this$0) {\n        this.this$0 = this$0;\n    }\n}\n"
    fixed, n = fix_text(src)
    assert n == 1 and "private final Outer this$0;" in fixed, fixed
    assert fix_text(fixed)[0] == fixed


def test_literal_shapes():
    src = ("public final class Double {\n    public static final double MAX_VALUE = MAX_VALUE;\n"
           "    public static final double NaN = NaN;\n    public static final int MIN_VALUE = MIN_VALUE;\n"
           "    void f() {\n        int flag = false;\n        boolean b;\n        b = (boolean)0;\n"
           "        long big = MAX_VALUE;\n    }\n}\n")
    fixed, n = fix_text(src)
    assert "double MAX_VALUE = 1.7976931348623157E308;" in fixed, fixed
    assert "double NaN = 0.0 / 0.0;" in fixed and "int MIN_VALUE = -2147483648;" in fixed, fixed
    assert "int flag = 0;" in fixed and "b = false;" in fixed and "long big = MAX_VALUE;" in fixed, fixed
    assert n == 5 and fix_text(fixed)[0] == fixed, (n, fixed)
