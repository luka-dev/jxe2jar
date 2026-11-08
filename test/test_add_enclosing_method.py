#!/usr/bin/env python3
"""add_enclosing_method: javac -target 1.4 writes no EnclosingMethod; the pass recovers the
enclosing class from the single `new Outer$N` site, the method too unless the site is a
constructor/static initializer (field initializer -> method_index 0, as javac writes it)."""
import os
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JDK8 = ROOT / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin"
sys.path.insert(0, str(ROOT / "tools"))
from add_enclosing_method import fix  # noqa: E402
from rtdiff import parse  # noqa: E402

SRC = """
public class Owner {
    Runnable field = new Runnable() { public void run() {} };                 // Owner$1: field init -> class only
    Runnable method() { return new Runnable() { public void run() {} }; }     // Owner$2: Owner.method
    static Runnable stat() { return new Runnable() { public void run() {} }; } // Owner$3: Owner.stat
    class Inner { Runnable run() { return new Runnable() { public void run() {} }; } } // Owner$Inner$1
    public static void main(String[] a) { new Owner().method().run(); stat().run(); new Owner().new Inner().run().run(); }
}
"""


def _em(data):
    c = parse(data)
    raw = next((d for n, d in c["attrs"] if n == "EnclosingMethod"), None)
    if raw is None:
        return None
    ci, mi = struct.unpack(">HH", raw)
    cp = c["cp"]
    return (cp.cls(ci), cp.text(mi) if mi else None)


def test_add_enclosing_method():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d); (tmp / "Owner.java").write_text(SRC)
        subprocess.run([str(JDK8 / "javac"), "-nowarn", "-source", "1.4", "-target", "1.4", "-d", d, str(tmp / "Owner.java")], check=True, capture_output=True)
        with zipfile.ZipFile(tmp / "in.jar", "w") as z:
            for p in tmp.glob("*.class"): z.write(p, p.name)
        with zipfile.ZipFile(tmp / "in.jar") as z:
            assert all(_em(z.read(n)) is None for n in z.namelist())  # -target 1.4 wrote none
        st = fix(tmp / "in.jar", tmp / "out.jar")
        assert st["anonymous without EnclosingMethod"] == 4 and st["added: class+method"] == 3 and st["added: class only"] == 1
        with zipfile.ZipFile(tmp / "out.jar") as z:
            assert _em(z.read("Owner$1.class")) == ("Owner", None)
            assert _em(z.read("Owner$2.class")) == ("Owner", "method:()Ljava/lang/Runnable;")
            assert _em(z.read("Owner$3.class")) == ("Owner", "stat:()Ljava/lang/Runnable;")
            assert _em(z.read("Owner$Inner$1.class")) == ("Owner$Inner", "run:()Ljava/lang/Runnable;")
            assert _em(z.read("Owner.class")) is None and _em(z.read("Owner$Inner.class")) is None
        # the rewritten classfiles load and verify; the pass is idempotent
        subprocess.run([str(JDK8 / "java"), "-Xverify:all", "-cp", str(tmp / "out.jar"), "Owner"], check=True, capture_output=True)
        st2 = fix(tmp / "out.jar", tmp / "again.jar")
        assert st2["anonymous without EnclosingMethod"] == 0
        with zipfile.ZipFile(tmp / "out.jar") as a, zipfile.ZipFile(tmp / "again.jar") as b:
            assert all(a.read(n) == b.read(n) for n in a.namelist())


if __name__ == "__main__":
    test_add_enclosing_method(); print("ok")
