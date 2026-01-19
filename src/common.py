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

    def _read_utf8_bytes(self, start_pos: int, expect_padding: bool = True):
        """Helper to read pad+len data."""
        padding = self.read_u16()
        length = self.read_u16()
        data_start = self.get()
        available = max(0, self.len - data_start)
        # Add sanity check: reject suspiciously large lengths
        max_reasonable_length = min(available, 65535)
        if (not expect_padding or padding == 0) and 0 <= length <= max_reasonable_length:
            # Additional validation: length should be reasonable for a string
            if length > 10000 and padding != 0:
                raise ValueError("invalid ROM string header - length too large")
            data = self.read_bytes(length)
            return data
        raise ValueError("invalid ROM string header")

    def _read_rom_string_at(self, pos: int, visited: set, debug=False):
        if pos in visited:
            raise ValueError("cycle in ROM string")
        visited.add(pos)
        try:
            with StreamCursor(self, pos):
                try:
                    data = self._read_utf8_bytes(pos)
                    try:
                        result = decode_modified_utf8(data)
                        if _is_valid_string(result):
                            if debug:
                                print(f"DEBUG _read_rom_string_at: pad+length path succeeded, len={len(result)}")
                            return result
                    except UnicodeDecodeError:
                        pass
                    # Don't use latin-1 fallback - it creates garbage in constant pool
                except Exception as e:
                    if debug:
                        print(f"DEBUG _read_rom_string_at: pad+length failed: {e}")
                    pass

                # Try legacy u16 length BEFORE SRP table (SRP is too permissive and finds false matches)
                self.set(pos)
                length = self.read_u16()
                available = max(0, self.len - self.get())
                if debug:
                    peek_bytes = b""
                    saved = self.get()
                    self.set(pos)
                    peek_bytes = self.read_bytes(min(20, self.len - pos))
                    self.set(saved)
                    print(f"DEBUG legacy: pos={hex(pos)}, length={length} (0x{length:04x}), available={available}, peek={peek_bytes[:8].hex()}...")
                # Add better validation: reject clearly invalid lengths
                # Allow length=0 for empty strings
                if 0 <= length <= min(available, 10000):
                    data = self.read_bytes(length)
                    # Empty string is valid
                    if length == 0:
                        return ""
                    # Validate that the data looks like text
                    try:
                        result = decode_modified_utf8(data)
                        # Validate result doesn't contain too many null bytes or control chars
                        if _is_valid_string(result):
                            if debug:
                                print(f"DEBUG legacy SUCCESS: decoded {len(result)} chars: {result[:30]!r}")
                            return result
                    except UnicodeDecodeError:
                        pass
                    # Don't use latin-1 fallback for constant pool strings - it creates garbage

                # Try SRP table (only if legacy format failed)
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
                        with StreamCursor(self, target):
                            data = self._read_utf8_bytes(target)
                            try:
                                result = decode_modified_utf8(data)
                                if _is_valid_string(result):
                                    if debug:
                                        print(f"DEBUG _read_rom_string_at: SRP path succeeded at {hex(target)}, len={len(result)}")
                                    return result
                            except UnicodeDecodeError:
                                pass
                            # Don't use latin-1 fallback - creates garbage
                    except Exception:
                        try:
                            result = self._read_rom_string_at(target, visited)
                            if debug:
                                print(f"DEBUG _read_rom_string_at: SRP recursive succeeded at {hex(target)}, len={len(result)}")
                            return result
                        except Exception:
                            continue

                # All formats failed - return empty string as last resort
                # This prevents crashes when encountering unknown string formats
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
