"""Classfile major inference: 46 unless a Java 5 feature is present; `ldc CONSTANT_Class`
(javac >= 1.5 for `Foo.class`) counts, the verifier rejects it below 49."""
import sys
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jxe import ConstType  # noqa: E402
from jxe2jar import _infer_classfile_major  # noqa: E402


def _romclass(bytecode, pool_types):
    return NS(
        class_name="p/Foo", access_flags=0x21, class_generic_signature=None, fields=[],
        methods=[NS(modifier=0x0001, generic_signature=None, bytecode=bytes(bytecode))],
        constant_pool=[NS(type=t) for t in pool_types],
    )


def test_major_inference():
    pool = [ConstType.CLASS, ConstType.STRING, ConstType.INT]
    assert _infer_classfile_major(_romclass([0x12, 1, 0xB1], pool)) == 46          # ldc "string"
    assert _infer_classfile_major(_romclass([0x12, 2, 0x57, 0xB1], pool)) == 46    # ldc int
    assert _infer_classfile_major(_romclass([0x12, 0, 0xB1], pool)) == 49          # ldc Foo.class
    assert _infer_classfile_major(_romclass([0x13, 0, 0, 0xB1], pool)) == 49       # ldc_w Foo.class (LE index)
    assert _infer_classfile_major(_romclass([0xBB, 0, 0, 0xB1], pool)) == 46       # `new Foo` is fine in 46
    rc = _romclass([0xB1], pool); rc.methods[0].modifier |= 0x0040                 # bridge
    assert _infer_classfile_major(rc) == 49
    rc = _romclass([], pool); rc.class_name = "com/google/common/base/package-info"  # guava
    assert _infer_classfile_major(rc) == 49
