#!/usr/bin/env python3
"""JAR -> JXE -> JAR round trip on the edge-case suite, judged by the JVM itself.

`test/custom_edgecases/out/cases.jxe` is the real WinCE `jar2jxe.exe` output of
`cases.jar` (javac -target 1.2). Converting it back must give classes that
  * pass the JDK 8 verifier (-Xverify:all) - catches constant-pool mistyping,
    invokespecial on a non-`this` receiver, int/float mix-ups;
  * carry the original classfile version (46 for every 1.2 class);
  * match the original javac bytecode opcode for opcode (ldc/ldc_w masked: the
    pool layout differs, the instruction does not).
"""
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
JDK = ROOT / "jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home/bin"
JXE = ROOT / "test/custom_edgecases/out/cases.jxe"
ORIGINAL = ROOT / "test/custom_edgecases/out/cases.jar"


def opcodes(jar):
    """{(class, method header): [opcode mnemonics]} from javap -c."""
    names = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class"))
    out = subprocess.run([str(JDK / "javap"), "-c", "-p", "-cp", str(jar)] + names,
                         capture_output=True, text=True, check=True).stdout
    res, cls, cur = {}, None, None
    for line in out.splitlines():
        m = re.match(r"(?:\w+ )*(?:class|interface) ([\w.$]+)", line)
        if m:
            cls = m.group(1)
            continue
        m = re.match(r"  \S.*?[\w$<>]+\(.*\)(?: throws .*)?;$", line)
        if m:
            cur = (cls, line.strip())
            res[cur] = []
            continue
        m = re.match(r"\s+\d+: (\w+)", line)
        if m and cur and m.group(1) != "nop":
            res[cur].append("ldc" if m.group(1) in ("ldc", "ldc_w") else m.group(1))
    return res


def test_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        jar = pathlib.Path(tmp) / "cases.from_jxe.jar"
        subprocess.run([sys.executable, str(ROOT / "src/jxe2jar.py"), str(JXE), str(jar)],
                       check=True, capture_output=True)
        subprocess.run([str(JDK / "javac"), "-d", tmp, str(ROOT / "test/VerifyAll.java")], check=True)
        verify = subprocess.run([str(JDK / "java"), "-Xverify:all", "-cp", tmp, "VerifyAll", str(jar)],
                                capture_output=True, text=True)
        assert verify.returncode == 0, verify.stdout + verify.stderr

        with zipfile.ZipFile(jar) as z:
            majors = {n: z.read(n)[7] for n in z.namelist() if n.endswith(".class")}
        assert set(majors.values()) == {46}, {n: v for n, v in majors.items() if v != 46}

        want, got = opcodes(ORIGINAL), opcodes(jar)
        assert set(want) == set(got), set(want) ^ set(got)
        assert [k for k in want if want[k] != got[k]] == []


if __name__ == "__main__":
    test_roundtrip()
    print("ok")
