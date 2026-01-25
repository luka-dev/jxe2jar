"""JXE class."""
# pylint: disable=W0612
import struct
from enum import Enum
from io import IOBase
from zipfile import ZipFile

from bitstring import BitArray
from common import ReaderStream, StreamCursor, WriterStream  # noqa: F401
# from bytecode import estimate_bc_size


class ConstType(int, Enum):
    """Constant types"""

    INT = 0
    STRING = 1
    CLASS = 2
    LONG = 3
    REF = 4


def _consume_field_descriptor(desc: str, idx: int) -> int:
    """Return next index after a field descriptor starting at idx, or -1."""
    if idx >= len(desc):
        return -1
    ch = desc[idx]
    if ch == "[":
        while idx < len(desc) and desc[idx] == "[":
            idx += 1
        return _consume_field_descriptor(desc, idx)
    if ch in "BCDFIJSZ":
        return idx + 1
    if ch == "L":
        end = desc.find(";", idx + 1)
        if end == -1:
            return -1
        return end + 1
    return -1


def _is_field_descriptor(desc: str) -> bool:
    if not desc:
        return False
    end = _consume_field_descriptor(desc, 0)
    return end == len(desc)


def _is_method_descriptor(desc: str) -> bool:
    if not desc or desc[0] != "(":
        return False
    idx = 1
    while idx < len(desc) and desc[idx] != ")":
        nxt = _consume_field_descriptor(desc, idx)
        if nxt == -1:
            return False
        idx = nxt
    if idx >= len(desc) or desc[idx] != ")":
        return False
    idx += 1
    if idx >= len(desc):
        return False
    if desc[idx] == "V":
        return idx + 1 == len(desc)
    nxt = _consume_field_descriptor(desc, idx)
    return nxt == len(desc)


def _is_descriptor(desc: str) -> bool:
    return _is_field_descriptor(desc) or _is_method_descriptor(desc)


class J9ROMField:
    """J9 Field."""

    def __init__(
        self,
        name,
        signature,
        access_flag,
        const_value=None,
        const_value2=None,
        const_value3=None,
    ):
        self.name = name
        self.signature = signature
        self.access_flag = access_flag
        self.const_value = const_value
        self.const_value2 = const_value2
        self.const_value3 = const_value3

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Field from stream."""
        name = stream.read_string_ref()
        signature = stream.read_string_ref()
        # print(name + signature)
        access_flags = stream.read_u32()

        const_value = const_value2 = const_value3 = None
        if access_flags & 0x400000:
            const_value = stream.read_u32()
            if access_flags & 0x40000:
                const_value2 = stream.read_u32()

        if access_flags & 0x40000000:
            const_value3 = stream.read_u32()

        return J9ROMField(
            name,
            signature,
            access_flags,
            const_value=const_value,
            const_value2=const_value2,
            const_value3=const_value3,
        )


class J9ROMCatchException:
    """J9 Catch Exception."""

    def __init__(self, start, end, handler, catch_type):
        self.start = start
        self.end = end
        self.handler = handler
        self.catch_type = catch_type

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Catch Exception from stream."""
        start = stream.read_u32()
        end = stream.read_u32()
        handler = stream.read_u32()
        catch_type = stream.read_u32()
        return J9ROMCatchException(start, end, handler, catch_type)


class J9ROMThrowException:
    """J9 Throw Exception."""

    def __init__(self, throw_type):
        self.throw_type = throw_type

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Throw Exception"""
        return J9ROMThrowException(stream.read_string_ref())


class J9ROMMethod:
    """J9 MMethod."""

    def __init__(
        self,
        name,
        signature,
        modifier,
        max_stack,
        arg_count,
        temp_count,
        bytecode,
        catch_exceptions,
        throw_exceptions,
    ):
        self.name = name
        self.signature = signature
        self.modifier = modifier
        self.max_stack = max_stack
        self.arg_count = arg_count
        self.temp_count = temp_count
        self.bytecode = bytecode
        self.catch_exceptions = catch_exceptions
        self.throw_exceptions = throw_exceptions

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Method."""
        name = stream.read_string_ref()
        signature = stream.read_string_ref()
        modifier = stream.read_u32()
        use_bytecodesize_high = modifier & 0x00008000
        has_exception_info = modifier & 0x00020000
        add_four1 = modifier & 0x00010000  # pylint: disable=unused-variable
        max_stack = stream.read_u16()
        if modifier & 0x100:
            base = stream.get()  # noqa: F841
            native_arg_count = stream.read_u8()  # noqa: F841
            temp_count = stream.read_u8()
            stream.read_u8()  # noqa: F841
            arg_count2 = stream.read_u8()
            stream.read_u8()
            stream.read_u8()
            arg_count = stream.read_u8()
            return_type = stream.read_u8()  # noqa: F841
            args = []
            for i in range(arg_count):
                args.append(stream.read_u8())
                
            # align
            stream.set((stream.get() + 3) & ~3)
            # stream.read_u32()
            if modifier & 0x2000000:
                stream.read_u32()
            if modifier & 0x20000:
                extra_pos = stream.get()
                table_a = stream.read_u16()
                table_b = stream.read_u16()
                extra_len = table_a * 16 + table_b * 4
                stream_len = int(stream.len)
                if (
                    extra_len <= 0
                    or extra_len > 0x100000
                    or extra_pos + extra_len > stream_len
                ):
                    stream.set(extra_pos)
                else:
                    stream.read_bytes(extra_len)
            caught_exceptions = []
            thrown_exceptions = []
            bytecode = stream.read_bytes(0)
            

        else:
            bytecode_size_low = stream.read_u16()
            bytecode_size_high = stream.read_u8()
            arg_count = stream.read_u8()
            temp_count = stream.read_u16()
            bytecode_size = bytecode_size_low
            if use_bytecodesize_high:
                bytecode_size += bytecode_size_high << 16
            bytecode_size *= 4
            bytecode = stream.read_bytes(bytecode_size)
            if modifier & 0x02000000:
                # J9 stores an extra u32 after bytecode for some methods.
                stream.read_bytes(4)
            stream.set((stream.get() + 3) & ~3)
            if has_exception_info:
                caught_exception_count = stream.read_u16()
                thrown_exception_count = stream.read_u16()
                caught_exceptions = [
                    J9ROMCatchException.read(stream)
                    for i in range(caught_exception_count)
                ]
                thrown_exceptions = [
                    J9ROMThrowException.read(stream)
                    for i in range(thrown_exception_count)
                ]
            else:
                caught_exceptions = []
                thrown_exceptions = []

            # if add_four2:
            # stream.read_u32()

        return J9ROMMethod(
            name,
            signature,
            modifier,
            max_stack,
            arg_count,
            temp_count,
            bytecode,
            caught_exceptions,
            thrown_exceptions,
        )


class J9ROMInterface:
    """J9 Interface."""

    def __init__(self, name):
        self.name = name

    @staticmethod
    def read(stream: BitArray):
        """ "Returns J9 Interface from stream."""
        name = stream.read_string_ref()
        return J9ROMInterface(name)


class J9ROMConstant:
    """J9 Constant."""

    def __init__(
        self,
        cons_type,
        value=None,
        _class=None,
        name=None,
        descriptor=None,
        raw_value=None,
        raw_type=None,
        rom_pos=None,
    ):
        self.type = cons_type
        self.raw_value = raw_value
        self.raw_type = raw_type
        self.rom_pos = rom_pos
        match cons_type:
            case ConstType.INT | ConstType.STRING | ConstType.LONG:
                self.value = value
            case ConstType.CLASS:
                self.value = value
            case ConstType.REF:
                self._class = _class
                self.name = name
                self.descriptor = descriptor

    @staticmethod
    def read(stream: BitArray, base, class_name, class_count=None):
        """Returns J9 constant from stream."""
        pos = stream.get()
        value = stream.read_u32()
        value_type = stream.read_u32()
        raw_value = value
        raw_type = value_type

        match value_type:
            case ConstType.STRING | ConstType.CLASS:
                value = struct.unpack("<i", struct.pack("<I", value))[0]
                ptr = pos + value
                with StreamCursor(stream, ptr):
                    value = stream.read_string()
            case ConstType.INT:
                value = struct.pack("<I", value)
            case _:
                stream_len = int(stream.len) // 8
                if class_count is not None and value >= class_count:
                    value = struct.pack("<II", value, value_type)
                    value_type = ConstType.LONG
                    return J9ROMConstant(
                        value_type,
                        value=value,
                        raw_value=raw_value,
                        raw_type=raw_type,
                        rom_pos=pos,
                    )

                class_ptr = base + 8 * value
                if class_ptr < 0 or class_ptr + 4 > stream_len:
                    value = struct.pack("<II", value, value_type)
                    value_type = ConstType.LONG
                    return J9ROMConstant(
                        value_type,
                        value=value,
                        raw_value=raw_value,
                        raw_type=raw_type,
                        rom_pos=pos,
                    )
                try:
                    with StreamCursor(stream, class_ptr):
                        _class = stream.read_string_ref()
                    if not _class:
                        _class = class_name
                    ptr = value_type + pos + 4
                    if ptr < 0 or ptr + 4 > stream_len:
                        raise ValueError("invalid ref pointer")
                    with StreamCursor(stream, ptr):
                        name = stream.read_string_ref()
                        descriptor = stream.read_string_ref()
                    if not name:
                        raise ValueError("invalid ref name")
                    if descriptor:
                        descriptor = descriptor.rstrip("\x00")
                    if not _is_descriptor(descriptor):
                        cleaned = descriptor.split("\x00", 1)[0] if descriptor else ""
                        if _is_descriptor(cleaned):
                            descriptor = cleaned
                        elif not descriptor:
                            raise ValueError("invalid ref descriptor")
                    return J9ROMConstant(
                        ConstType.REF,
                        _class=_class,
                        name=name,
                        descriptor=descriptor,
                        raw_value=raw_value,
                        raw_type=raw_type,
                        rom_pos=pos,
                    )
                except Exception:
                    value = struct.pack("<II", value, value_type)
                    value_type = 3

        return J9ROMConstant(
            value_type,
            value=value,
            raw_value=raw_value,
            raw_type=raw_type,
            rom_pos=pos,
        )


class J9ROMClass:
    """J9 Class."""

    def __init__(
        self,
        minor,
        major,
        class_name,
        superclass_name,
        access_flags,
        interfaces,
        methods,
        fields,
        constant_pool,
        rom_base=None,
        rom_stream=None,
        class_count=None,
        ram_constant_pool_count=None,
        rom_constant_pool_count=None,
    ):
        self.minor = minor
        self.major = major
        self.class_name = class_name
        self.superclass_name = superclass_name
        self.access_flags = access_flags
        self.interfaces = interfaces
        self.methods = methods
        self.fields = fields
        self.constant_pool = constant_pool
        self.rom_base = rom_base
        self.rom_stream = rom_stream
        self.class_count = class_count
        self.ram_constant_pool_count = ram_constant_pool_count
        self.rom_constant_pool_count = rom_constant_pool_count

    @staticmethod
    def read_at(stream: BitArray, class_name: str, class_pointer: int, class_count=None):
        """Returns J9 Class from already resolved pointer."""
        print(f"  -> reading class {class_name!r}")
        with StreamCursor(stream, class_pointer):
            rom_size = stream.read_u32()  # noqa: F841
            single_scalar_static_count = stream.read_u32()  # noqa: F841
            class_name = stream.read_string_ref()
            superclass_name = stream.read_string_ref()
            access_flags = stream.read_u32()
            interface_count = stream.read_u32()
            interfaces_pointer = stream.read_relative()

            with StreamCursor(stream, interfaces_pointer):
                interfaces = [
                    J9ROMInterface.read(stream) for i in range(interface_count)
                ]

            rom_method_count = stream.read_u32()
            rom_methods_pointer = stream.read_relative()

            with StreamCursor(stream, rom_methods_pointer):
                methods = [J9ROMMethod.read(stream) for i in range(rom_method_count)]

            rom_field_count = stream.read_u32()
            rom_fields_pointer = stream.read_relative()

            with StreamCursor(stream, rom_fields_pointer):
                fields = [J9ROMField.read(stream) for i in range(rom_field_count)]

            object_static_count = stream.read_u32()  # noqa: F841
            double_scalar_static_count = stream.read_u32()  # noqa: F841
            ram_constant_pool_count = stream.read_u32()
            rom_constant_pool_count = stream.read_u32()
            crc = stream.read_u32()  # noqa: F841
            instance_size = stream.read_u32()  # noqa: F841
            instance_shape = stream.read_u32()  # noqa: F841
            cp_shape_description_pointer = stream.read_relative()  # noqa: F841
            outer_class_name = stream.read_relative()  # noqa: F841
            member_access_flags = stream.read_u32()  # noqa: F841
            inner_class_count = stream.read_u32()  # noqa: F841
            inner_classes_pointer = stream.read_relative()  # noqa: F841
            major = stream.read_u16()
            minor = stream.read_u16()
            optional_flags = stream.read_u32()
            optional_info_pointer = stream.read_relative()

            if not optional_flags & 0x2000:
                with StreamCursor(stream, optional_info_pointer):
                    pass
                    # source_filename = stream.read_sprr(optional_flags, 0x1)
                    # generic_signature = stream.read_sprr(optional_flags, 0x2)
                    # source_debug_ext = stream.read_sprr(optional_flags, 0x4)
                    # annotation_info = stream.read_sprr(optional_flags, 0x8)
                    # debug_info = stream.read_sprr(optional_flags, 0x10)
                    # enclosing_method = stream.read_sprr(optional_flags, 0x40)
                    # simple_name = stream.read_sprr(optional_flags, 0x80)

            base = stream.get()
            constant_pool_count = rom_constant_pool_count
            constant_pool = []
            print(
                f"     >> cp={constant_pool_count}, methods={rom_method_count}, fields={rom_field_count}"
            )

            for i in range(constant_pool_count):
                try:
                    constant_pool.append(
                        J9ROMConstant.read(stream, base, class_name, class_count)
                    )
                except EOFError:
                    # Usual between ram_constant_pool_count and rom_constant_pool_count
                    # liy double const but in some cases last element contain not valid
                    # string const, so we skip sthis case
                    pass

        return J9ROMClass(
            minor,
            major,
            class_name,
            superclass_name,
            access_flags,
            interfaces,
            methods,
            fields,
            constant_pool,
            rom_base=base,
            rom_stream=stream,
            class_count=class_count,
            ram_constant_pool_count=ram_constant_pool_count,
            rom_constant_pool_count=rom_constant_pool_count,
        )


class J9ROMImage:
    """J9 Image."""

    def __init__(self, signature, flags_and_version, rom_size, symbol_file_id, classes):
        self.signature = signature
        self.flags_and_version = flags_and_version
        self.rom_size = rom_size
        self.symbol_file_id = symbol_file_id
        self.classes = classes

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Image from stream."""
        signature = stream.read_u32()
        flags_and_version = stream.read_u32()
        rom_size = stream.read_u32()
        class_count = stream.read_u32()
        jxe_pointer = stream.read_relative()  # noqa: F841
        toc_pointer = stream.read_relative()
        first_class_pointer = stream.read_relative()  # noqa: F841
        aot_pointer = stream.read_relative()  # noqa: F841
        symbol_file_id = stream.read_bytes(0x10)
        pos = stream.get()
        stream.set(toc_pointer)
        print(f"ROM header OK (class_count={class_count}, rom_size={rom_size})")
        toc = []
        for _ in range(class_count):
            name = stream.read_string_ref()
            ptr = stream.read_relative()
            toc.append((name, ptr))
        classes = []
        for idx, (name, ptr) in enumerate(toc, 1):
            print(f"[TOC] {idx}/{class_count} {name!r}")
            classes.append(J9ROMClass.read_at(stream, name, ptr, class_count))
        stream.set(pos)

        return J9ROMImage(
            signature, flags_and_version, rom_size, symbol_file_id, classes
        )


class JXE:
    """JXE object."""

    def __init__(self, image):
        self.image = image

    @staticmethod
    def read(stream: IOBase):
        """Returns JXE class from file object reading."""
        with ZipFile(stream.file_object) as fp_zipfile:
            with fp_zipfile.open("rom.classes") as rom:
                rom_stream = ReaderStream.bytes_to_stream(rom.read())
                return JXE(J9ROMImage.read(rom_stream))
