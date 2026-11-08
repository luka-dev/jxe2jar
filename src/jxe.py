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
    FLOAT = 5
    DOUBLE = 6


# Word 19 of the class header: the "CP kind-run" stream the romizer writes for every scalar
# and ref slot (bcutil sub_10015E20). runs of {kindByte, count:u8, index[count]} ending in
# 0xFF; odd kindByte => kind = byte+1 with u8 indices, even => u16 LE indices.
KIND_INT, KIND_FLOAT, KIND_LONG, KIND_DOUBLE = 14, 16, 18, 6
KIND_STATIC_METHOD, KIND_VIRTUAL_METHOD, KIND_SPECIAL_METHOD, KIND_INTERFACE_METHOD = 2, 8, 10, 12
KIND_INSTANCE_FIELD, KIND_STATIC_FIELD = 20, 22


def read_kind_runs(stream) -> dict:
    """Decode the kind-run stream at the current position: {rom cp index: kind}."""
    kinds = {}
    while True:
        kind_byte = stream.read_u8()
        if kind_byte == 0xFF:
            return kinds
        count = stream.read_u8()
        if kind_byte & 1:
            kind, indices = kind_byte + 1, [stream.read_u8() for _ in range(count)]
        else:
            kind, indices = kind_byte, [stream.read_u16() for _ in range(count)]
        for index in indices:
            kinds[index] = kind


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
        generic_signature=None,
    ):
        self.name = name
        self.signature = signature
        self.access_flag = access_flag
        self.const_value = const_value
        self.const_value2 = const_value2
        self.generic_signature = generic_signature  # field-level Signature (0x40000000), or None

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Field from stream."""
        name = stream.read_string_ref()
        signature = stream.read_string_ref()
        # print(name + signature)
        access_flags = stream.read_u32()

        const_value = const_value2 = None
        generic_signature = None
        if access_flags & 0x400000:
            const_value = stream.read_u32()
            if access_flags & 0x40000:
                const_value2 = stream.read_u32()

        if access_flags & 0x40000000:
            # J9FieldFlagHasGenericSignature: self-relative SRP to the field's generic
            # Signature UTF8 (JVMS 4.7.9). Confirmed: all such fields resolve to valid
            # field signatures (e.g. GMap<Class,GList<EventSubscriber>>). The old code
            # read this same 4-byte word as an unused "const_value3" - alignment intact.
            generic_signature = stream.read_string_ref() or None

        return J9ROMField(
            name,
            signature,
            access_flags,
            const_value=const_value,
            const_value2=const_value2,
            generic_signature=generic_signature,
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
        generic_signature=None,
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
        self.generic_signature = generic_signature  # method-level Signature (0x02000000), or None

    @staticmethod
    def read(stream: BitArray):
        """Returns J9 Method."""
        name = stream.read_string_ref()
        signature = stream.read_string_ref()
        modifier = stream.read_u32()
        has_exception_info = modifier & 0x00020000
        max_stack = stream.read_u16()
        generic_signature = None  # resolved from the 0x02000000 SRP below
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
            caught_exceptions = []
            thrown_exceptions = []
            if modifier & 0x20000:
                # same exception-info block as bytecode methods: a native has no catch
                # entries but keeps its declared `throws` (was skipped as opaque bytes)
                caught_exception_count = stream.read_u16()
                thrown_exception_count = stream.read_u16()
                caught_exceptions = [
                    J9ROMCatchException.read(stream) for _ in range(caught_exception_count)
                ]
                thrown_exceptions = [
                    J9ROMThrowException.read(stream) for _ in range(thrown_exception_count)
                ]
            bytecode = stream.read_bytes(0)
            

        else:
            bytecode_size = stream.read_u16() * 4  # in u32 units
            stream.read_u8()  # byte 16: never written by the romizer (stale buffer), ignore
            arg_count = stream.read_u8()
            temp_count = stream.read_u16()
            bytecode = stream.read_bytes(bytecode_size)
            if modifier & 0x02000000:
                # J9AccMethodHasGenericSignature: the u32 after bytecode is a self-
                # relative SRP to the method's generic Signature UTF8 (JVMS 4.7.9).
                # read_string_ref consumes exactly that 4-byte SRP (alignment intact,
                # same as the old read_bytes(4)) and follows it to the string.
                generic_signature = stream.read_string_ref() or None
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
            if modifier & 0x00400000:
                # reserved trailer word of the precompile/AOT configuration (jar2jxe's own
                # ROM-method walker skips it; never set by the interpreter-only builder)
                stream.read_u32()

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
            generic_signature=generic_signature,
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
        if cons_type == ConstType.REF:
            self._class = _class
            self.name = name
            self.descriptor = descriptor
        else:
            self.value = value

    @staticmethod
    def read(stream: BitArray, base, class_name, index, ram_count, shapes, kinds):
        """Returns one J9 ROM constant-pool slot (8 bytes: two u32 words).

        Slot typing is deterministic, from two facts the ROM records (verified on
        3047 classes / 150k slots: zero contradictions with the referencing opcodes):
          * index >= ramConstantPoolCount: the ROM-only tail, which holds every
            long/double (8 raw bytes, stored {low, high}); ldc2_lw / ldc2_dw at the
            use site decide long vs double. Nothing else ever lives there.
          * else the cpShapeDescription nibble: 1 = string, 2 = class (first word is
            an SRP to the J9UTF8), 3 = static field ref, 0 = either a single-slot
            scalar (int/float, second word 0) or a method / instance field ref
            {U32 classRefCPIndex; SRP nameAndSignature} (second word is the SRP,
            never 0). The shape table only covers the RAM part of the pool.
          * the header's kind-run stream (`kinds`, see read_kind_runs) says int vs float
            and long vs double for every scalar slot; a slot missing from it (older or
            foreign builders) falls back to int / long and is retyped by its ldc2 use.
        """
        pos = stream.get()
        value = stream.read_u32()
        value_type = stream.read_u32()
        common = dict(raw_value=value, raw_type=value_type, rom_pos=pos)

        kind = kinds.get(index)
        if index >= ram_count:
            return J9ROMConstant(
                ConstType.DOUBLE if kind == KIND_DOUBLE else ConstType.LONG,
                value=struct.pack("<II", value, value_type), **common,
            )
        shape = shapes[index]
        if shape in (1, 2):
            srp = struct.unpack("<i", struct.pack("<I", value))[0]
            with StreamCursor(stream, pos + srp):
                text = stream.read_string()
            return J9ROMConstant(
                ConstType.STRING if shape == 1 else ConstType.CLASS, value=text, **common
            )
        if shape == 0 and value_type == 0:
            return J9ROMConstant(
                ConstType.FLOAT if kind == KIND_FLOAT else ConstType.INT,
                value=struct.pack("<I", value), **common,
            )

        # field / method ref: first word indexes the owner's CLASS slot, second word
        # is an SRP (relative to its own position) to {SRP name; SRP descriptor}.
        try:
            if not (value < ram_count and shapes[value] == 2):
                raise ValueError("ref class index is not a class slot")
            with StreamCursor(stream, base + 8 * value):
                _class = stream.read_string_ref() or class_name
            nas = pos + 4 + struct.unpack("<i", struct.pack("<I", value_type))[0]
            if not 0 <= nas <= int(stream.len) - 8:
                raise ValueError("invalid ref pointer")
            with StreamCursor(stream, nas):
                name = stream.read_string_ref()
                descriptor = stream.read_string_ref()
            if not name:
                raise ValueError("invalid ref name")
            descriptor = descriptor.rstrip("\x00")
            if not _is_descriptor(descriptor):
                cleaned = descriptor.split("\x00", 1)[0]
                if _is_descriptor(cleaned):
                    descriptor = cleaned
                elif not descriptor:
                    raise ValueError("invalid ref descriptor")
            return J9ROMConstant(
                ConstType.REF, _class=_class, name=name, descriptor=descriptor, **common
            )
        except Exception as exc:  # pylint: disable=W0718
            # Never expected (the typing above is exact); keep the slot so later
            # indices stay aligned, and say so - a used placeholder fails verification.
            print(
                f"WARNING: {class_name} cp[{index}] shape={shape} words="
                f"({value:#x},{value_type:#x}) unreadable ref ({exc}); INT 0 placeholder"
            )
            return J9ROMConstant(ConstType.INT, value=b"\x00\x00\x00\x00", **common)


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
        ram_constant_pool_count=None,
        rom_constant_pool_count=None,
        outer_class_name=None,
        member_access_flags=0,
        inner_class_names=None,
        simple_name=None,
        has_enclosing_method=False,
        enclosing_class=None,
        enclosing_method_name=None,
        enclosing_method_sig=None,
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
        self.ram_constant_pool_count = ram_constant_pool_count
        self.rom_constant_pool_count = rom_constant_pool_count
        # Real J9 ROM inner-class metadata (JVMS InnerClasses/EnclosingMethod source).
        # J9 preserves these (unlike StackMapTable), so nesting is read, not guessed.
        self.outer_class_name = outer_class_name  # enclosing class, or None if top-level
        self.member_access_flags = member_access_flags  # original inner modifiers
        self.inner_class_names = inner_class_names or []  # direct member inner classes
        self.simple_name = simple_name  # inner simple name; None => anonymous
        self.has_enclosing_method = has_enclosing_method  # true => anonymous/local
        # EnclosingMethod attribute source: enclosing class + optional method NameAndType.
        self.enclosing_class = enclosing_class
        self.enclosing_method_name = enclosing_method_name
        self.enclosing_method_sig = enclosing_method_sig

    @staticmethod
    def read_at(stream: BitArray, class_name: str, class_pointer: int):
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
            stream.read_u32()  # word 15: reserved, always 0
            instance_size = stream.read_u32()  # noqa: F841
            stream.read_u32()  # word 17: constant 14 in every image seen
            # cpShapeDescription: 4 bits per RAM constant-pool slot, LSB-first within
            # each little-endian u32 (see J9ROMConstant.read for the nibble values).
            cp_shape_description_pointer = stream.read_relative()
            with StreamCursor(stream, cp_shape_description_pointer):
                shape_words = [
                    stream.read_u32() for _ in range((ram_constant_pool_count + 7) // 8)
                ]
            cp_shapes = [
                (shape_words[k // 8] >> (4 * (k % 8))) & 0xF
                for k in range(ram_constant_pool_count)
            ]

            # --- words 19..25 (per u32 word after cpShapeDescription):
            #   [+0] kind-run stream SRP          [+1] outerClassName SRP
            #   [+2] memberAccessFlags            [+3] innerClassCount
            #   [+4] innerClasses SRP             [+5] optionalFlags   [+6] optionalInfo SRP
            # (An SRP whose stored i32 is 0 is NULL. The ROM keeps no classfile version;
            # the converter infers it, so major/minor are placeholders.)
            kinds = {}
            kr_base = stream.get()
            kr_raw = stream.read_i32()
            if kr_raw != 0:
                with StreamCursor(stream, kr_base + kr_raw):
                    kinds = read_kind_runs(stream)
            else:
                print(f"WARNING: {class_name} has no CP kind stream; int/float typing is a guess")

            occ_base = stream.get()
            occ_raw = stream.read_i32()
            outer_class_name = None
            if occ_raw != 0:
                with StreamCursor(stream, occ_base + occ_raw):
                    outer_class_name = stream.read_string() or None

            member_access_flags = stream.read_u32()
            inner_class_count = stream.read_u32()
            ic_base = stream.get()
            ic_raw = stream.read_i32()
            inner_class_names = []
            if inner_class_count and ic_raw != 0:
                with StreamCursor(stream, ic_base + ic_raw):
                    for _ in range(inner_class_count):
                        name = stream.read_string_ref()
                        if name:
                            inner_class_names.append(name)

            optional_flags = stream.read_u32()
            opt_base = stream.get()
            opt_raw = stream.read_i32()
            major, minor = 50, 0  # placeholders; real version recomputed downstream
            # optional flag 0x40 => an EnclosingMethod record exists (true anonymous
            # or local class); its absence on a nested class marks a synthetic one.
            has_enclosing_method = bool(optional_flags & 0x40)

            # simpleName (optional flag 0x80): its SRP sits at index = popcount of the
            # optional flags below bit 0x80. Absent => the class is anonymous.
            simple_name = None
            if not (optional_flags & 0x2000) and (optional_flags & 0x80) and opt_raw != 0:
                idx = bin(optional_flags & 0x7F).count("1")
                with StreamCursor(stream, opt_base + opt_raw + 4 * idx):
                    simple_name = stream.read_string_ref() or None

            # optional flag 0x02 => class-level generic Signature (JVMS 4.7.9). CONFIRMED
            # empirically: on classes carrying it the SRP record decodes to a valid
            # signature (e.g. GPair -> "<F:...;S:...>L...;"). The J9 romizer KEEPS these
            # (contrary to the old "generics fully erased" note) - jxe2jar had been
            # dropping them. SRP index = popcount of the flags below 0x02 (i.e. 0x01,
            # SourceFile, which is always absent here -> index 0).
            class_generic_signature = None
            if (optional_flags & 0x02) and opt_raw != 0:
                gi = bin(optional_flags & 0x01).count("1")
                with StreamCursor(stream, opt_base + opt_raw + 4 * gi):
                    class_generic_signature = stream.read_string_ref() or None

            # EnclosingMethod (optional flag 0x40): its SRP sits at index = popcount of
            # the optional flags below bit 0x40 and points at a J9EnclosingObject:
            #   { U32 classRefCPIndex; SRP nameAndSignature }
            # nameAndSignature (or NULL) -> J9ROMNameAndSignature { SRP name; SRP sig }.
            # The class is resolved from the ROM constant pool once it is parsed below.
            enclosing_class_cp_index = None
            enclosing_method_name = None
            enclosing_method_sig = None
            if (optional_flags & 0x40) and opt_raw != 0:
                em_i = bin(optional_flags & 0x3F).count("1")
                with StreamCursor(stream, opt_base + opt_raw + 4 * em_i):
                    eo_base = stream.get()
                    eo_srp = stream.read_i32()
                    if eo_srp != 0:
                        with StreamCursor(stream, eo_base + eo_srp):
                            enclosing_class_cp_index = stream.read_u32()
                            nas_base = stream.get()
                            nas_srp = stream.read_i32()
                            if nas_srp != 0:
                                with StreamCursor(stream, nas_base + nas_srp):
                                    enclosing_method_name = stream.read_string_ref() or None
                                    enclosing_method_sig = stream.read_string_ref() or None

            base = stream.get()
            constant_pool_count = rom_constant_pool_count
            constant_pool = []
            print(
                f"     >> cp={constant_pool_count}, methods={rom_method_count}, fields={rom_field_count}"
            )

            for i in range(constant_pool_count):
                slot = stream.get()
                try:
                    constant_pool.append(
                        J9ROMConstant.read(
                            stream, base, class_name, i, ram_constant_pool_count, cp_shapes, kinds
                        )
                    )
                except Exception as exc:  # pylint: disable=W0718
                    # Keep the slot: dropping it shifts every later CP index by one and
                    # silently rewires all references after it. A zero INTEGER is inert.
                    print(f"WARNING: {class_name} cp[{i}] unreadable ({exc}); INT 0 placeholder")
                    stream.set(slot + 8)
                    constant_pool.append(
                        J9ROMConstant(ConstType.INT, value=b"\x00\x00\x00\x00")
                    )

            # Resolve the enclosing class from the parsed ROM constant pool. Fall back
            # to outerClassName, then to the JVM-mandated Outer$N naming (the enclosing
            # class of an anonymous class is unambiguously the part before the last '$').
            enclosing_class = None
            if enclosing_class_cp_index is not None and (
                0 <= enclosing_class_cp_index < len(constant_pool)
            ):
                ec = constant_pool[enclosing_class_cp_index]
                if ec.type == ConstType.CLASS and ec.value:
                    enclosing_class = ec.value
            if enclosing_class is None and (optional_flags & 0x40):
                enclosing_class = outer_class_name or (
                    class_name.rsplit("$", 1)[0] if "$" in class_name else None
                )

        romclass = J9ROMClass(
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
            ram_constant_pool_count=ram_constant_pool_count,
            rom_constant_pool_count=rom_constant_pool_count,
            outer_class_name=outer_class_name,
            member_access_flags=member_access_flags,
            inner_class_names=inner_class_names,
            simple_name=simple_name,
            has_enclosing_method=has_enclosing_method,
            enclosing_class=enclosing_class,
            enclosing_method_name=enclosing_method_name,
            enclosing_method_sig=enclosing_method_sig,
        )
        romclass.optional_flags = optional_flags  # raw class-level optinfo bitfield (census/debug)
        romclass.class_generic_signature = class_generic_signature  # JVMS Signature (0x02), or None
        return romclass


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
            classes.append(J9ROMClass.read_at(stream, name, ptr))
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
