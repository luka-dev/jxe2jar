#!/usr/bin/env python3
"""Undo the romizer's invokevirtual -> invokespecial rewrite, exactly as bcutil applies it.

bcutil (sub_1001299C) devirtualises an invokevirtual iff the target is one of Object's six
final methods (any owner in the reference), or the reference names the class being
romized and that class itself declares the method final or private. Nothing else: not
inherited finals, not final classes, not super calls. So the converter restores exactly
those, and leaves javac's own invokespecials (<init>, private, super.m(), inner-class
`access$N01` super accessors) alone.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from bytecode import transform_bytecode  # noqa: E402
from constpool import CONST  # noqa: E402


class FakeCP:
    """Just enough of ConstPool for transform_bytecode: J9 index -> ref info."""

    def __init__(self, refs):
        self.transform = {
            i: {"new_index": i, "type": t, "ref_class": c, "ref_name": n, "descriptor": d}
            for i, (t, c, n, d) in refs.items()
        }
        self.retagged = {}

    def check_transform(self, index, t=None):
        return index in self.transform and (t is None or self.transform[index]["type"] == t)

    def get_transform(self, index):
        return self.transform[index]

    def apply_transform(self, index, t):
        self.retagged[index] = t


REFS = {
    1: (CONST.METHODREF, "pkg/Owner", "fin", "()V"),          # own final method
    2: (CONST.METHODREF, "pkg/Owner", "priv", "()V"),         # own private method
    3: (CONST.METHODREF, "pkg/Super", "fin", "()V"),          # inherited final / super call
    4: (CONST.METHODREF, "pkg/Super", "<init>", "()V"),
    5: (CONST.METHODREF, "pkg/Other", "getClass", "()Ljava/lang/Class;"),  # Object final, any owner
    6: (CONST.METHODREF, "pkg/Owner", "plain", "()V"),        # own, neither final nor private
    7: (CONST.METHODREF, "pkg/Owner", "take", "(JF)V"),
    8: (CONST.DOUBLE, None, None, None),
    9: (CONST.LONG, None, None, None),
}
ALOAD_0, ALOAD_1, DUP, NEW, RETURN0 = 0x2A, 0x2B, 0x59, 0xBB, 0xAC
INVOKESPECIAL, INVOKEVIRTUAL = 0xB7, 0xB6


def special(index):
    return bytes([INVOKESPECIAL]) + struct.pack("<H", index)


def run(code):
    cp = FakeCP(REFS)
    out, offsets = transform_bytecode(
        bytearray(code), "()V", cp, owner="pkg/Owner", method_name="m",
        final_methods={("fin", "()V"), ("priv", "()V")}, private_methods={("priv", "()V")},
    )
    return out, offsets, cp


def op_at(out, offsets, j9_offset):
    return out[offsets[j9_offset]]


def test_devirtualize():
    # own final method -> was invokevirtual (receiver does not matter)
    for recv in (ALOAD_0, ALOAD_1):
        out, off, _ = run(bytes([recv]) + special(1) + bytes([RETURN0]))
        assert op_at(out, off, 1) == INVOKEVIRTUAL
    # own private method: javac's own invokespecial
    out, off, _ = run(bytes([ALOAD_0]) + special(2) + bytes([RETURN0]))
    assert op_at(out, off, 1) == INVOKESPECIAL
    # own non-final method via invokespecial cannot come from the romizer: keep
    out, off, _ = run(bytes([ALOAD_0]) + special(6) + bytes([RETURN0]))
    assert op_at(out, off, 1) == INVOKESPECIAL
    # inherited final / super.fin() / access$N01 super accessor: never devirtualised -> keep
    for recv in (ALOAD_0, ALOAD_1):
        out, off, _ = run(bytes([recv]) + special(3) + bytes([RETURN0]))
        assert op_at(out, off, 1) == INVOKESPECIAL
    # <init> always stays
    out, off, _ = run(bytes([NEW]) + struct.pack("<H", 4) + bytes([DUP]) + special(4) + bytes([RETURN0]))
    assert op_at(out, off, 4) == INVOKESPECIAL
    # Object's finals, whatever class the reference names (javac uses the static type)
    out, off, _ = run(bytes([ALOAD_1]) + special(5) + bytes([RETURN0]))
    assert op_at(out, off, 1) == INVOKEVIRTUAL

    # ldc2: slot type comes from the ROM kind stream; the J9 opcode must agree, else retag
    code = bytes([ALOAD_0, 0x14]) + struct.pack("<H", 9) + bytes([0xF9]) + struct.pack("<H", 8) + special(7) + bytes([RETURN0])
    out, off, cp = run(code)
    assert cp.retagged == {}, cp.retagged
    code = bytes([0xF9]) + struct.pack("<H", 9) + bytes([RETURN0])  # ldc2_dw on a LONG-typed slot
    out, off, cp = run(code)
    assert cp.retagged == {9: CONST.DOUBLE}, cp.retagged

    # J9 wide forms are 4 / 6 bytes; the JVM `wide` forms are too, so offsets line up
    code = bytes([0xCB, 0x34, 0x12, 0x00, 0xD5, 0x34, 0x12, 0xFF, 0xFF, 0x00, RETURN0])
    out, off, _ = run(code)
    assert bytes(out) == bytes([0xC4, 0x15, 0x12, 0x34, 0xC4, 0x84, 0x12, 0x34, 0xFF, 0xFF, 0xB1]), out.hex()
    print("ok")


if __name__ == "__main__":
    test_devirtualize()
