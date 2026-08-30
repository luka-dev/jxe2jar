#!/usr/bin/env python3
"""J9UTF8 reader check: an empty ROM string must not swallow the next pool record."""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from common import ReaderStream  # noqa: E402


def _rec(text):
    """One J9UTF8: LE u16 length + modified-UTF8 data, padded to 2-byte alignment."""
    data = text.encode()
    return struct.pack("<H", len(data)) + data + (b"\x00" if len(data) % 2 else b"")


def main():
    # Layout lifted from MU1326-lsd.jxe around offset 0x393B18F.
    pool = _rec("") + _rec("isNativeLittleEndian") + _rec("java/lang/OutOfMemoryError")
    stream = ReaderStream.bytes_to_stream(pool)

    stream.set(0)
    assert stream.read_string() == "", "empty string leaked the next pool record"
    stream.set(2)
    assert stream.read_string() == "isNativeLittleEndian"
    stream.set(24)
    assert stream.read_string() == "java/lang/OutOfMemoryError"

    # Odd-length record: the pad byte must not bleed into the string.
    padded = _rec("freePointer") + _rec("isNativeLittleEndian")
    stream = ReaderStream.bytes_to_stream(padded)
    stream.set(0)
    assert stream.read_string() == "freePointer"
    stream.set(14)
    assert stream.read_string() == "isNativeLittleEndian"

    print("ok")


if __name__ == "__main__":
    main()
