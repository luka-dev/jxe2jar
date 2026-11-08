"""Donor LVT transplant: the edge cases compiled with -g act as the donor for their own
round trip (cases.jxe -> jar). Every method must get its LocalVariableTable / LineNumberTable
back, every class its SourceFile, and the result must still pass -Xverify:all."""
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import donor_lvt  # noqa: E402
from rtdiff import code, load  # noqa: E402

JDK8 = ROOT / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin"


def _census(jar):
    lvt = lnt = sf = methods = 0
    for c in load(jar).values():
        sf += any(n == "SourceFile" for n, _ in c["attrs"])
        for m in c["methods"].values():
            d = dict(m["attrs"])
            if "Code" not in d: continue
            methods += 1; names = {n for n, _ in code(d["Code"], c["cp"])[4]}
            lvt += "LocalVariableTable" in names; lnt += "LineNumberTable" in names
    return dict(methods=methods, lvt=lvt, lnt=lnt, sourcefile=sf)


def test_donor_lvt():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); classes = tmp / "classes"; classes.mkdir()
        srcs = [str(p) for p in (ROOT / "test/custom_edgecases/src").rglob("*.java")]
        subprocess.run([str(JDK8 / "javac"), "-g", "-nowarn", "-source", "1.2", "-target", "1.2", "-d", str(classes)] + srcs,
                       check=True, capture_output=True)
        subprocess.run([str(JDK8 / "jar"), "cf", str(tmp / "donor.jar"), "-C", str(classes), "."], check=True)
        subprocess.run([sys.executable, str(ROOT / "src/jxe2jar.py"), str(ROOT / "test/custom_edgecases/out/cases.jxe"), str(tmp / "rt.jar")],
                       check=True, capture_output=True)
        donor_lvt.build([str(tmp / "donor.jar")], str(tmp / "db.json.gz"))
        st = donor_lvt.apply(str(tmp / "rt.jar"), str(tmp / "db.json.gz"), str(tmp / "rt-lvt.jar"))
        want, got = _census(str(tmp / "donor.jar")), _census(str(tmp / "rt-lvt.jar"))
        assert got["methods"] == want["methods"]
        assert got["lvt"] == want["lvt"] == st["methods: full LVT"], (want, got, dict(st))
        assert got["lnt"] == want["lnt"], (want, got)
        assert st["methods: parameter names only"] == 0 and st["graft errors"] == 0, dict(st)
        subprocess.run([str(JDK8 / "javac"), "-d", str(tmp), str(ROOT / "test/VerifyAll.java")], check=True, capture_output=True)
        verify = subprocess.run([str(JDK8 / "java"), "-Xverify:all", "-cp", str(tmp), "VerifyAll", str(tmp / "rt-lvt.jar")], capture_output=True, text=True)
        assert verify.returncode == 0, verify.stdout + verify.stderr
        with zipfile.ZipFile(tmp / "rt-lvt.jar") as z:
            assert b"sinkMany" in z.read("cases/FloatTyping.class")  # sanity: a real name made it in


if __name__ == "__main__":
    test_donor_lvt(); print("ok")
