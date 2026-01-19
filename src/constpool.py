"""Constants Pool class."""
import struct
from enum import Enum


class CONST(bytes, Enum):
    CLASS = b"\x07"
    FIELDREF = b"\x09"
    METHODREF = b"\x0a"
    INTERFACEMETHODREF = b"\x0b"
    STRING = b"\x08"
    INTEGER = b"\x03"
    FLOAT = b"\x04"
    LONG = b"\x05"
    DOUBLE = b"\x06"
    NAMEANDTYPE = b"\x0c"
    UTF8 = b"\x01"


class J9CONST(int, Enum):
    INT = 0
    STRING = 1
    CLASS = 2
    LONG = 3
    REF = 4


def _encode_utf8(value: str) -> bytes:
    return value.encode("utf-8", "surrogatepass")


class ConstPool:
    def __init__(self, romclass):
        self.pool = []
        self.transform = {}
        stack = []
        # self.pool.append([-1, None])

        for i, constant in enumerate(romclass.constant_pool):
            if constant.type == J9CONST.INT:
                index = len(self.pool)
                self.pool.append([CONST.INTEGER, constant.value[::-1]])
                self.transform[i] = {"new_index": index, "type": CONST.INTEGER}
            elif constant.type == J9CONST.LONG:
                index = len(self.pool)
                self.pool.append([CONST.DOUBLE, constant.value[::-1]])
                self.pool.append([-1, None])
                self.transform[i] = {"new_index": index, "type": CONST.DOUBLE}
            elif constant.type == J9CONST.STRING:
                index = len(self.pool)
                self.pool.append([CONST.STRING, ""])
                value = _encode_utf8(constant.value)
                stack.append(
                    (
                        index,
                        CONST.UTF8,
                        struct.pack(">H", len(value)) + value,
                    )
                )
                self.transform[i] = {"new_index": index, "type": CONST.STRING}
            elif constant.type == J9CONST.CLASS:
                index = len(self.pool)
                self.pool.append([CONST.CLASS, ""])
                value = _encode_utf8(constant.value)
                stack.append(
                    (
                        index,
                        CONST.UTF8,
                        struct.pack(">H", len(value)) + value,
                    )
                )
                self.transform[i] = {"new_index": index, "type": CONST.CLASS}
            elif constant.type == J9CONST.REF:
                index = len(self.pool)
                const_type = (
                    CONST.METHODREF
                    if constant.descriptor.find("(") >= 0
                    else CONST.FIELDREF
                )
                self.pool.append([const_type, "", ""])
                value_class = _encode_utf8(constant._class)
                value_c_name = _encode_utf8(constant.name)
                value_c_desc = _encode_utf8(constant.descriptor)
                stack.append(
                    (
                        index,
                        CONST.CLASS,
                        struct.pack(">H", len(value_class)) + value_class,
                    )
                )
                stack.append(
                    (
                        index,
                        CONST.NAMEANDTYPE,
                        struct.pack(">H", len(value_c_name)) + value_c_name,
                        struct.pack(">H", len(value_c_desc)) + value_c_desc,
                    )
                )
                self.transform[i] = {
                    "new_index": index,
                    "type": const_type,
                    "descriptor": constant.descriptor,
                }

        for elem in stack:
            cp_id = len(self.pool)
            if elem[1] == CONST.UTF8:
                self.pool.append([elem[1], elem[2]])
                if self.pool[elem[0]][1]:
                    self.pool[elem[0]][2] = struct.pack(">H", cp_id + 1)
                else:
                    self.pool[elem[0]][1] = struct.pack(">H", cp_id + 1)
            elif elem[1] == CONST.CLASS:
                self.pool.append([elem[1], ""])
                stack.append((cp_id, CONST.UTF8, elem[2]))
                self.pool[elem[0]][1] = struct.pack(">H", cp_id + 1)
            elif elem[1] == CONST.NAMEANDTYPE:
                self.pool.append([elem[1], "", ""])
                stack.append((cp_id, CONST.UTF8, elem[2]))
                stack.append((cp_id, CONST.UTF8, elem[3]))
                self.pool[elem[0]][2] = struct.pack(">H", cp_id + 1)
        # Check for incomplete constants but only warn, don't fail
        incomplete_count = 0
        for idx, elem in enumerate(self.pool):
            if elem[0] != -1 and elem[1] in ("", None):
                incomplete_count += 1
        if incomplete_count > 0:
            print(f"Warning: {incomplete_count} incomplete constant(s) in pool")

    def add(self, value_type, value):
        if isinstance(value, str):
            value = _encode_utf8(value)

        if value_type == CONST.INTEGER:
            index = len(self.pool)
            self.pool.append([CONST.INTEGER, struct.pack(">I", value & 0xFFFFFFFF)])
            return index + 1

        if value_type == CONST.FLOAT:
            index = len(self.pool)
            self.pool.append([CONST.FLOAT, struct.pack(">I", value & 0xFFFFFFFF)])
            return index + 1

        if value_type == CONST.DOUBLE:
            index = len(self.pool)
            if isinstance(value, (tuple, list)):
                hi, lo = value
                payload = struct.pack(">II", hi & 0xFFFFFFFF, lo & 0xFFFFFFFF)
            else:
                payload = struct.pack(">Q", value & 0xFFFFFFFFFFFFFFFF)
            self.pool.append([CONST.DOUBLE, payload])
            self.pool.append([-1, None])
            return index + 1

        if value_type == CONST.STRING:
            index_utf8 = len(self.pool)
            self.pool.append([CONST.UTF8, struct.pack(">H", len(value)) + value])
            index_string = len(self.pool)
            self.pool.append([CONST.STRING, struct.pack(">H", index_utf8 + 1)])
            return index_string + 1

        if value_type == CONST.CLASS:
            index = len(self.pool)
            self.pool.append([CONST.UTF8, struct.pack(">H", len(value)) + value])
            self.pool.append([CONST.CLASS, struct.pack(">H", index + 1)])
            return index + 2

        if value_type == CONST.UTF8:
            index = len(self.pool)
            self.pool.append([CONST.UTF8, struct.pack(">H", len(value)) + value])
            return index + 1

        if value_type == CONST.LONG:
            index = len(self.pool)
            self.pool.append([CONST.LONG, struct.pack(">II", *value)])
            self.pool.append([-1, None])
            return index + 1

        raise ValueError(f"Unexpected value type: '{value_type}'")

    def apply_transform(self, index, transform_type):
        self.pool[index][0] = transform_type

    def get_int(self, index):
        return struct.unpack(">I", self.pool[index][1])[0]

    def check_transform(self, index, transform_type=None):
        # print(self.transform[index]["type"])
        return index in self.transform and (
            not transform_type or self.transform[index]["type"] == transform_type
        )

    def get_transform(self, index):
        return self.transform[index]

    def write(self, stream):
        stream.write_u16(len(self.pool) + 1)
        for idx, elem in enumerate(self.pool):
            if elem[0] == -1:
                continue
            if elem[1] is None:
                raise ValueError(
                    f"Constant pool element missing data at {idx}: {elem}"
                )
            stream.write_raw_bytes(elem[0])
            stream.write_raw_bytes(elem[1])
            if len(elem) > 2:
                stream.write_raw_bytes(elem[2])
