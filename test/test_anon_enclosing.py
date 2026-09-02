#!/usr/bin/env python3
"""build_anon_enclosing: the `new Outer$N` site names an anonymous class's home.

The J9 romizer erases the EnclosingObject record for most anonymous classes, so the
enclosing class+method are recovered from the single `new` that constructs them.
"""
import os
import struct
import sys
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from jxe import ConstType  # noqa: E402
from jxe2jar import build_anon_enclosing  # noqa: E402


def _new(index):
    """J9 `new` (0xBB) with a little-endian ROM constant-pool index."""
    return b"\xbb" + struct.pack("<H", index)


def _cls(name, cp_names, methods):
    pool = [NS(type=ConstType.CLASS, value=n) for n in cp_names]
    return NS(class_name=name, constant_pool=pool, methods=methods)


def main():
    # Outer$1 is declared in Outer$Inner.run() - note the name prefix (Outer) is NOT
    # the enclosing class, which is exactly what the name-based guess gets wrong.
    classes = [
        _cls("Outer", ["Outer$Inner"], [NS(name="main", signature="()V", bytecode=_new(0))]),
        _cls("Outer$Inner", ["Outer$1"],
             [NS(name="run", signature="()V", bytecode=b"\x2a" + _new(0) + b"\xb1")]),
        _cls("Outer$1", [], [NS(name="<init>", signature="()V", bytecode=b"\xb1")]),
    ]
    assert build_anon_enclosing(classes)["Outer$1"] == ("Outer$Inner", "run", "()V")

    # A field/instance initializer compiles into <init>; javac emits method_index 0 for
    # those, so the constructor is reported as the class only, never as the method.
    classes = [
        _cls("Outer", ["Outer$1"], [NS(name="<init>", signature="()V", bytecode=_new(0))]),
        _cls("Outer$1", [], [NS(name="<init>", signature="()V", bytecode=b"\xb1")]),
    ]
    assert build_anon_enclosing(classes)["Outer$1"] == ("Outer", None, None)

    # Two disagreeing sites are ambiguous - dropped, not guessed.
    classes = [
        _cls("Outer", ["Outer$1"],
             [NS(name="a", signature="()V", bytecode=_new(0)),
              NS(name="b", signature="()V", bytecode=_new(0))]),
        _cls("Outer$1", [], [NS(name="<init>", signature="()V", bytecode=b"\xb1")]),
    ]
    assert "Outer$1" not in build_anon_enclosing(classes)

    # A class that only mentions itself yields nothing (no self-enclosure).
    classes = [_cls("Outer$1", ["Outer$1"], [NS(name="f", signature="()V", bytecode=_new(0))])]
    assert build_anon_enclosing(classes) == {}

    print("ok")


if __name__ == "__main__":
    main()
