"""Common class."""
import errno
import os
import os.path
from io import IOBase

import bitstring


class StreamCursor:
    """StreamCursor object."""

    def __init__(self, stream, pos):
        self._stream_ = stream
        self._new_pos_ = pos
        self._old_pos_ = None

    def __enter__(self):
        self._old_pos_ = self._stream_.get()
        if self._new_pos_ < 0 or self._new_pos_ > self._stream_.len:
            raise EOFError
        self._stream_.set(self._new_pos_)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream_.set(self._old_pos_)


class ReaderStream:
    """ReaderStream class."""

    def __init__(self, obj):
        if isinstance(obj, IOBase):
            self._file_object_ = obj
            self._bit_stream_ = bitstring.BitStream(self._file_object_)
        elif isinstance(obj, bitstring.BitArray):
            self._bit_stream_ = bitstring.BitStream()
            self._bit_stream_._append(obj)
        else:
            raise TypeError("Invalid ReaderStream instance type")

    def get(self) -> int:
        """Returns current file stream cursor position."""
        return self._bit_stream_.bytepos

    def set(self, pos: int) -> None:
        """Sets current file stream cursor position."""
        self._bit_stream_.bytepos = pos

    def read_bytes(self, length: int):
        """Reads n bytes from file stream."""
        return self._bit_stream_.read(f"bytes:{length}")

    def read_u8(self) -> int:
        """Reads uint8 le from file stream."""
        return self._bit_stream_.read("uintle:8")

    def read_u16(self) -> int:
        """Reads uint16 le from file stream."""
        return self._bit_stream_.read("uintle:16")

    def read_u32(self) -> int:
        """Reads uint32 le from file stream."""
        return self._bit_stream_.read("uintle:32")

    def read_i8(self) -> int:
        """Reads int8 le from file stream."""
        return self._bit_stream_.read("intle:8")

    def read_i16(self) -> int:
        """Reads int16 le from file stream."""
        return self._bit_stream_.read("intle:16")

    def read_i32(self) -> int:
        """Reads int32 le from file stream."""
        return self._bit_stream_.read("intle:32")

    def _read_j9utf8_at(self, pos: int) -> str:
        """Reads one J9UTF8 record: LE u16 length, then `length` bytes of modified UTF-8.

        A zero length word is a genuine empty string, never a padding field. Reading it
        as padding made the reader swallow the *next* record in the ROM UTF8 pool, so
        every "" came out as whatever name happened to follow it in the pool.
        """
        self.set(pos)
        length = self.read_u16()
        available = max(0, self.len - self.get())
        if length > min(available, 10000):
            raise ValueError("invalid ROM string header")
        if length == 0:
            return ""
        # decode_modified_utf8 raises UnicodeDecodeError, a ValueError subclass.
        result = decode_modified_utf8(self.read_bytes(length))
        if not _is_valid_string(result):
            raise ValueError("ROM string does not look like text")
        return result

    def _read_rom_string_at(self, pos: int, visited: set, debug=False):
        if pos in visited:
            raise ValueError("cycle in ROM string")
        visited.add(pos)
        try:
            with StreamCursor(self, pos):
                try:
                    return self._read_j9utf8_at(pos)
                except ValueError as exc:
                    if debug:
                        print(f"DEBUG _read_rom_string_at: J9UTF8 at {hex(pos)} failed: {exc}")

                # Not a J9UTF8 record - try an SRP table pointing at the real ones.
                self.set(pos)
                targets = []
                for _ in range(64):  # safety limit
                    srp = self.read_i32()
                    anchor = self.get()
                    _ = self.read_i32()
                    if srp == 0:
                        break
                    target = srp + anchor
                    if 0 <= target < self.len:
                        targets.append(target)
                if debug and targets:
                    print(f"DEBUG _read_rom_string_at: Found {len(targets)} SRP targets: {[hex(t) for t in targets[:5]]}")
                for target in targets:
                    if target in visited:
                        continue
                    try:
                        return self._read_j9utf8_at(target)
                    except ValueError:
                        pass
                    try:
                        return self._read_rom_string_at(target, visited)
                    except Exception:
                        continue

                # All formats failed - "" keeps broken pointers out of the constant pool.
                return ""
        finally:
            visited.remove(pos)

    def read_string(self, _visited=None) -> str:
        """Reads ROM string, following SRP tables if present."""
        if _visited is None:
            _visited = set()
        pos = self.get()
        return self._read_rom_string_at(pos, _visited, debug=False)

    def read_relative(self):
        """Reads int32 from file stream using relative position."""
        base = self.get()
        ptr = self.read_i32()
        return base + ptr

    def read_string_ref(self) -> str:
        """Reads string ref from file stream."""
        ptr = self.read_relative()
        pos = self.get()
        try:
            self.set(ptr)
            value = self.read_string()
            self.set(pos)
            return value
        except Exception:
            # If string reading completely fails, return empty string
            # This prevents broken binary data from being used as strings
            self.set(pos)
            return ""

    @property
    def bytes(self) -> bytes:
        """Returns bytes from BitArray stream."""
        return self._bit_stream_.bytes

    @property
    def len(self) -> int:
        """Returns BitArray length"""
        return int(self._bit_stream_.length // 8)

    @property
    def file_object(self) -> IOBase:
        """Retursn file object."""
        return self._file_object_

    @staticmethod
    def bytes_to_stream(value: bytes):
        """Returns ReaderStream from bytes."""
        return ReaderStream(bitstring.BitArray(bytes=value))


class WriterStream:
    """WriteStream class using bitstring."""

    def __init__(self, file_object):
        self._file_object_ = file_object
        self._bit_stream_ = bitstring.BitStream()

    def write(self) -> None:
        """Writes BitStream to file object."""
        self._bit_stream_.tofile(self._file_object_)

    def write_raw_bytes(self, data: bytes) -> None:
        """Writes raw bytes to BitArray stream."""
        self._bit_stream_.append(bitstring.BitArray(bytes=data))

    def write_u8(self, value: int) -> None:
        """Writes uint8 be to BitArray stream."""
        self._bit_stream_.append(bitstring.pack("uintbe:8", value))

    def write_u16(self, value: int) -> None:
        """Writes uint16 be to BitArray stream."""
        self._bit_stream_.append(bitstring.pack("uintbe:16", value))

    def write_u32(self, value: int) -> None:
        """Writes uint32 be to BitArray stream."""
        self._bit_stream_.append(bitstring.pack("uintbe:32", value))

    def write_i8(self, value: int) -> None:
        """Writes int8 be to BitArray stream."""
        self._bit_stream_.append(bitstring.pack("intbe:8", value))

    def write_i16(self, value: int) -> None:
        """Writes int16 be to BitArray stream."""
        self._bit_stream_.append(bitstring.pack("intbe:16", value))

    def write_i32(self, value: int) -> None:
        """Writes int32 be to BitArray stream."""
        self._bit_stream_.append(bitstring.pack("intbe:32", value))


def create_file_path(filepath: str) -> None:
    """Creates file path directories."""
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def _is_valid_string(s: str) -> bool:
    """Check if a string is valid for use in constant pool (no excessive control chars)."""
    if not s:
        return True  # Empty string is valid

    # Count null bytes and control characters
    null_count = s.count('\x00')
    control_count = sum(1 for c in s if ord(c) < 32 and c not in '\n\r\t')

    # Reject if more than 10% null bytes or control chars
    if null_count > len(s) * 0.1 or control_count > len(s) * 0.1:
        return False

    # Reject if string starts with null or control chars (common in corrupted data)
    if s[0] in '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f':
        return False

    return True


def decode_modified_utf8(data: bytes) -> str:
    """Decodes modified UTF-8 as used in Java class files."""
    result = []
    idx = 0
    length = len(data)
    while idx < length:
        byte = data[idx]
        if byte >> 7 == 0:
            result.append(chr(byte))
            idx += 1
        elif (byte & 0xE0) == 0xC0:
            if idx + 1 >= length:
                raise UnicodeDecodeError("mutf8", data, idx, idx + 1, "truncated sequence")
            byte2 = data[idx + 1]
            char = ((byte & 0x1F) << 6) | (byte2 & 0x3F)
            result.append(chr(char))
            idx += 2
        elif (byte & 0xF0) == 0xE0:
            if idx + 2 >= length:
                raise UnicodeDecodeError("mutf8", data, idx, idx + 2, "truncated sequence")
            byte2 = data[idx + 1]
            byte3 = data[idx + 2]
            char = ((byte & 0x0F) << 12) | ((byte2 & 0x3F) << 6) | (byte3 & 0x3F)
            result.append(chr(char))
            idx += 3
        else:
            raise UnicodeDecodeError("mutf8", data, idx, idx + 1, "invalid modified utf-8 byte")
    return "".join(result)
