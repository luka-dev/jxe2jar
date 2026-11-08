"""fix_javac_casts: raw for-each loops and dropped casts are repaired from javac's own
diagnostics; files that compile are left alone."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import fix_javac_casts  # noqa: E402

SRC = """package p;
import java.util.*;
public class Loops {
    int total(List names, final List nums, Map m) {
        int n = 0;
        for (String name : names) {
            n += name.length();
        }
        for (final int v : nums) {
            n += v;
        }
        for (Object o : m.keySet()) {
            n += o.hashCode();
        }
        String s = java.security.AccessController.doPrivileged(new java.security.PrivilegedAction() {
            public Object run() { return "x"; }
        });
        boolean flag = names.get(0);
        return n + s.length() + (flag ? 1 : 0) + first(names).length;
    }
    String[] first(List names) {
        return names.isEmpty() ? null : names
            .toArray(new String[0]);
    }
}
"""


def test_rewrite_and_compile():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "p" / "Loops.java"; f.parent.mkdir(); f.write_text(SRC)
        r = subprocess.run([sys.executable, str(ROOT / "tools/fix_javac_casts.py"), tmp, "--cp", tmp, "--apply"], capture_output=True, text=True)
        assert "rewrote 5 cast(s) in 1 of 1 file(s); 1 file(s) compile afterwards" in r.stdout, r.stdout + r.stderr
        text = f.read_text()
        assert "for (Object name_ : names) {\n            String name = (String) name_;" in text
        assert "for (Object v_ : nums) {\n            final int v = (Integer) v_;" in text
        assert "for (Object o : m.keySet()) {" in text  # untouched: it compiled
        assert "String s = (String) java.security.AccessController.doPrivileged(" in text
        assert "boolean flag = (Boolean) names.get(0);" in text
        assert "return names.isEmpty() ? null : (String[]) names\n" in text  # cast placed at the statement, not the wrapped line
        assert subprocess.run([fix_javac_casts.DEF_JAVAC, "-source", "1.5", "-target", "1.5", "-nowarn", "-d", tmp, str(f)], capture_output=True).returncode == 0
        r2 = subprocess.run([sys.executable, str(ROOT / "tools/fix_javac_casts.py"), tmp, "--cp", tmp], capture_output=True, text=True)
        assert "would rewrite 0 cast(s)" in r2.stdout


if __name__ == "__main__":
    test_rewrite_and_compile(); print("ok")
