"""Convert IBM J9/CDC JXE (rom.classes) to a standard Java JAR.

This script parses a JXE image and reconstructs .class files that are
compatible with common JVM tooling. It performs a small set of fixups:
 - Infers a minimal classfile version from flags (min 46, effectively capped at
   49 so the romizer-stripped StackMapTable is never required by the verifier).
 - Rewrites J9-specific bytecode patterns to standard JVM bytecode.
 - Rebuilds constant pool entries (including ConstantValue where possible).

Usage:
  python3 src/jxe2jar.py input.jxe output.jar
  python3 src/jxe2jar.py input.jxe output.jar --skip-libs libs/
  python3 src/jxe2jar.py input.jxe output.jar --skip-jdk /path/to/rt.jar
  python3 src/jxe2jar.py input.jxe output.jar --strip-synthetic

Notes:
 - JDK/JRE classes are skipped by default using src/rt.classes.
 - --skip-jdk can point to a custom JAR/JMOD/list file (e.g. rt.jar).
 - --skip-classes can add additional classes to skip.
 - --skip-libs skips classes already present in a libs/ JAR directory.
 - --strip-synthetic clears ACC_SYNTHETIC flags for stricter javap output.
 - Some JXE images embed non-standard metadata; output is best-effort.
"""
import argparse
import io
import os
import zipfile

from bytecode import transform_bytecode
from constpool import CONST, ConstPool
from jxe import JXE, ConstType, ReaderStream, WriterStream


CLASS_FLAG_MASK = (
    0x0001  # public
    | 0x0010  # final
    | 0x0020  # super
    | 0x0200  # interface
    | 0x0400  # abstract
    | 0x1000  # synthetic
    | 0x2000  # annotation
    | 0x4000  # enum
    | 0x8000  # module
)

FIELD_FLAG_MASK = (
    0x0001  # public
    | 0x0002  # private
    | 0x0004  # protected
    | 0x0008  # static
    | 0x0010  # final
    | 0x0040  # volatile / bridge
    | 0x0080  # transient / varargs
    | 0x0100  # synthetic / native
    | 0x4000  # enum
)

METHOD_FLAG_MASK = (
    0x0001  # public
    | 0x0002  # private
    | 0x0004  # protected
    | 0x0008  # static
    | 0x0010  # final
    | 0x0020  # synchronized
    | 0x0040  # bridge
    | 0x0080  # varargs
    | 0x0100  # native
    | 0x0400  # abstract
    | 0x0800  # strict
    | 0x1000  # synthetic
)


def _method_arg_slots(descriptor: str) -> int:
    """Return number of local slots for method args (not including receiver)."""
    if not descriptor or not descriptor.startswith("("):
        return 0
    i = 1
    slots = 0
    while i < len(descriptor) and descriptor[i] != ")":
        ch = descriptor[i]
        if ch == "[":
            while i < len(descriptor) and descriptor[i] == "[":
                i += 1
            if i < len(descriptor) and descriptor[i] == "L":
                i = descriptor.find(";", i)
                if i == -1:
                    return slots
            slots += 1
        elif ch == "L":
            i = descriptor.find(";", i)
            if i == -1:
                return slots
            slots += 1
        elif ch in ("J", "D"):
            slots += 2
        else:
            slots += 1
        i += 1
    return slots


def _infer_classfile_major(romclass) -> int:
    """Infer the minimal classfile major version required by class features."""
    # CDC/J9 targets old classfiles; start from Java 1.2 baseline (46).
    required = 46

    # Class-level flags that require Java 5+.
    if romclass.access_flags & (0x2000 | 0x4000):  # annotation/enum
        required = max(required, 49)
    if romclass.access_flags & 0x1000:  # synthetic
        required = max(required, 49)

    # Module flag would require Java 9+, but we clamp to 52 below.
    if romclass.access_flags & 0x8000:
        required = max(required, 53)

    for field in romclass.fields:
        if field.access_flag & 0x4000:  # enum
            required = max(required, 49)
        if field.access_flag & 0x1000:  # synthetic
            required = max(required, 49)

    for method in romclass.methods:
        # strictfp exists since Java 1.2
        if method.modifier & 0x0800:
            required = max(required, 46)
        # bridge/varargs require Java 5+
        if method.modifier & (0x0040 | 0x0080):
            required = max(required, 49)
        if method.modifier & 0x1000:
            required = max(required, 49)
        # NOTE: no invokedynamic (0xBA) bump. A raw `0xBA in bytecode` byte-scan
        # false-positives on 0xBA operands (it flagged 1559 firmware classes that
        # have zero real invokedynamic). And the converter emits no BootstrapMethods,
        # so a genuine invokedynamic couldn't be produced anyway. Capping at 49 keeps
        # every class on the old inference verifier (no StackMapTable required), which
        # the romizer strips - otherwise v50+ classes fail -Xverify:all.

    # J9/CDC firmware is javac-7 max with no invokedynamic; 49 covers every used
    # feature (annotations, enums, bridge/varargs, synthetic) and stays verifiable
    # without stack maps.
    return max(required, 46)


def build_inner_meta(classes):
    """Global map className -> (outer_class_name, simple_name, member_access_flags)
    for every nested class, built from the *real* J9 ROM inner-class fields (no
    name guessing). Members carry a real outer/name; anonymous, local and synthetic
    (`Outer$1`) classes have outer=None and are recorded so the outer class can list
    them (their InnerClasses entry gets outer=0, name=0 as javac emits)."""
    meta = {}
    children = {}
    for rc in classes:
        nested = rc.outer_class_name is not None or "$" in rc.class_name
        if not nested:
            continue
        flags = rc.member_access_flags
        # J9 leaves member flags at 0 for synthetic $N classes. javac records the
        # *static* ones (e.g. Formatter$1) as ACC_STATIC in InnerClasses; those are
        # ACC_FINAL in their own header, whereas a non-static synthetic/anonymous $N
        # (e.g. JobQueue$1, own flags 0x20) is not - so ACC_FINAL is the tell.
        if (
            flags == 0
            and rc.outer_class_name is None
            and rc.simple_name is None
            and rc.access_flags & 0x0010  # ACC_FINAL
        ):
            flags = 0x0008
        meta[rc.class_name] = (rc.outer_class_name, rc.simple_name, flags)
        # Name-based nest tree: `Outer$Inner` => Inner is a child of Outer. javac lists
        # every nest member in the outer's InnerClasses, so we need this even when the
        # ROM outerClassName is null (anonymous/synthetic).
        if "$" in rc.class_name:
            outer_name = rc.class_name.rsplit("$", 1)[0]
            children.setdefault(outer_name, []).append(rc.class_name)
    return meta, children


def _classes_in_descriptor(descriptor):
    """Yield every `Lpkg/Name;` internal class name inside a field/method descriptor."""
    if not descriptor:
        return
    i = 0
    while i < len(descriptor):
        if descriptor[i] == "L":
            end = descriptor.find(";", i)
            if end == -1:
                return
            yield descriptor[i + 1 : end]
            i = end + 1
        else:
            i += 1


def _build_inner_classes_attr(romclass, const_pool, inner_meta, children):
    """Reconstruct the InnerClasses attribute for one class from ROM metadata.

    Like javac, a class lists an entry for: itself when nested, every nest member it
    encloses, and every nested class it references in its constant pool. Each entry's
    outer/name/flags come from that nested class's own ROM record, so modifiers are
    exact (a nested interface keeps interface+abstract, etc.)."""
    if not inner_meta:
        return None
    names = []
    seen = set()

    def consider(class_name):
        if class_name in inner_meta and class_name not in seen:
            seen.add(class_name)
            names.append(class_name)

    consider(romclass.class_name)
    # Enclosing nest chain: Outer$Mid$Inner also lists Outer$Mid (and up).
    chain = romclass.class_name
    while "$" in chain:
        chain = chain.rsplit("$", 1)[0]
        consider(chain)
    consider(romclass.superclass_name)  # a nested class may extend a sibling/member
    for iface in romclass.interfaces:  # ...or implement one (stored outside the CP)
        consider(getattr(iface, "name", None))
    for member in children.get(romclass.class_name, ()):  # nest members we enclose
        consider(member)
    # A nested class is often mentioned only inside a descriptor (e.g. a synthetic
    # `Ctor(Outer$1)` accessor parameter) rather than as a standalone CONSTANT_Class;
    # javac still lists it, so scan every method/field signature for `L...;` types.
    for method in romclass.methods:
        for class_name in _classes_in_descriptor(getattr(method, "signature", None)):
            consider(class_name)
    for field in romclass.fields:
        for class_name in _classes_in_descriptor(getattr(field, "signature", None)):
            consider(class_name)
    for const in romclass.constant_pool:
        const_type = getattr(const, "type", None)
        if const_type == ConstType.CLASS:
            consider(getattr(const, "value", None))
        elif const_type == ConstType.REF:
            # field/method refs carry their owning class name; a nested class is
            # often referenced only through these, not a standalone CLASS entry.
            consider(getattr(const, "_class", None))
            for class_name in _classes_in_descriptor(getattr(const, "descriptor", None)):
                consider(class_name)

    # Some refs are reconstructed during conversion (e.g. a call to a sibling's
    # `<init>(Outer$1)`) and exist only in the *output* pool, not the J9 ROM one.
    # Scan its UTF8 entries - every class name and descriptor javac would see is here.
    for entry in const_pool.pool:
        if not entry or entry[0] != CONST.UTF8:
            continue
        raw = entry[1]
        if not isinstance(raw, (bytes, bytearray)) or len(raw) <= 2:
            continue
        try:
            text = raw[2:].decode("utf-8", "surrogatepass")
        except (UnicodeDecodeError, ValueError):
            continue
        consider(text)  # a bare class-name UTF8 (from a CONSTANT_Class)
        for class_name in _classes_in_descriptor(text):  # or embedded in a descriptor
            consider(class_name)
    if not names:
        return None

    entries = []
    for class_name in names:
        outer, simple, flags = inner_meta[class_name]
        inner_idx = const_pool.add(CONST.CLASS, class_name)
        outer_idx = const_pool.add(CONST.CLASS, outer) if outer else 0
        name_idx = const_pool.add(CONST.UTF8, simple) if simple else 0
        entries.append((inner_idx, outer_idx, name_idx, flags & 0xFFFF))
    attr_name_idx = const_pool.add(CONST.UTF8, "InnerClasses")
    return {"attribute_name_index": attr_name_idx, "classes": entries}


def dump_romclass(
    stream, romclass, strip_synthetic: bool = False, inner_meta=None, children=None
) -> tuple[ConstPool, list]:  # pylint: disable=R0914, R0915
    """Dumps romclass."""
    stream.write_raw_bytes(b"\xca\xfe\xba\xbe")
    # Infer the minimal classfile version required by flags/opcodes.
    target_minor = 0
    target_major = _infer_classfile_major(romclass)
    stream.write_u16(target_minor)
    stream.write_u16(target_major)
    const_pool = ConstPool(romclass)
    class_name_id = const_pool.add(CONST.CLASS, romclass.class_name)
    superclass_name_id = const_pool.add(CONST.CLASS, romclass.superclass_name)
    interface_id_list = []
    method_info_list = []

    for interface in romclass.interfaces:
        interface_id_list.append(const_pool.add(CONST.CLASS, interface.name))

    field_info_list = []
    const_value_attr_name_index = const_pool.add(CONST.UTF8, "ConstantValue")

    field_names = {field.name for field in romclass.fields}
    has_empty_string = any(
        getattr(c, "value", None) == ""
        for c in romclass.constant_pool
        if getattr(c, "type", None) == 1
    )

    for field in romclass.fields:
        access_flags = field.access_flag & FIELD_FLAG_MASK
        if strip_synthetic:
            access_flags &= ~0x1000
        attributes = []
        const_index = None

        if (
            field.const_value is not None
            and (access_flags & 0x0008)
            and (access_flags & 0x0010)
        ):
            sig = field.signature
            if sig in ("I", "S", "B", "C", "Z"):
                const_index = const_pool.add(CONST.INTEGER, field.const_value)
            elif sig == "F":
                const_index = const_pool.add(CONST.FLOAT, field.const_value)
            elif sig == "J":
                if field.const_value2 is not None:
                    const_index = const_pool.add(
                        CONST.LONG, (field.const_value2, field.const_value)
                    )
            elif sig == "D":
                if field.const_value2 is not None:
                    const_index = const_pool.add(
                        CONST.DOUBLE, (field.const_value2, field.const_value)
                    )
            elif sig == "Ljava/lang/String;":
                if field.const_value < len(romclass.constant_pool):
                    rom_const = romclass.constant_pool[field.const_value]
                    if hasattr(rom_const, "value"):
                        value = rom_const.value
                        if (
                            value in field_names
                            and value != field.name
                            and not has_empty_string
                        ):
                            value = ""
                        const_index = const_pool.add(CONST.STRING, value)

        if const_index is not None:
            attributes.append(
                {
                    "attribute_name_index": const_value_attr_name_index,
                    "attribute_length": 2,
                    "constantvalue_index": const_index,
                }
            )

        field_info_list.append(
            {
                "access_flags": access_flags,
                "name_index": const_pool.add(CONST.UTF8, field.name),
                "descriptor_index": const_pool.add(CONST.UTF8, field.signature),
                "attributes_count": len(attributes),
                "attributes": attributes,
            }
        )

    code_attr_name_index = const_pool.add(CONST.UTF8, "Code")

    for method in romclass.methods:
        method_flags = method.modifier & METHOD_FLAG_MASK
        if strip_synthetic:
            method_flags &= ~0x1000
        has_code = not (method_flags & (0x0100 | 0x0400))  # native or abstract
        if has_code:
            bytecode, offset_map = transform_bytecode(
                bytearray(method.bytecode),
                method.signature,
                const_pool,
                owner=romclass.class_name,
                method_name=method.name,
            )
        else:
            bytecode = b""
            offset_map = {}
        attributes = []
        if has_code:
            arg_slots = _method_arg_slots(method.signature)
            if not (method_flags & 0x0008):  # not static
                arg_slots += 1
            max_locals = arg_slots + method.temp_count
            def _map_offset(value: int) -> int:
                if value in offset_map:
                    return offset_map[value]
                if value >= len(method.bytecode):
                    return len(bytecode)
                # Fallback: find the nearest prior offset
                for back in range(value - 1, -1, -1):
                    if back in offset_map:
                        return offset_map[back]
                return 0

            attributes.append(
                {
                    "attribute_name_index": code_attr_name_index,
                    "attribute_length": len(bytecode)
                    + len(method.catch_exceptions) * 8
                    + 0xC,
                    "max_stack": method.max_stack,
                    "max_locals": max_locals,
                    "code_length": len(bytecode),
                    "code": bytecode,
                    "exception_table_length": len(method.catch_exceptions),
                    "exception_table": [
                        (
                            _map_offset(exception.start),
                            _map_offset(exception.end),
                            _map_offset(exception.handler),
                            exception.catch_type + 1
                            if exception.catch_type > 0
                            else 0,
                        )
                        for exception in method.catch_exceptions
                    ],
                    "attributes_count": 0,
                    "attributes": [],
                }
            )
        method_info_list.append(
            {
                "access_flags": method_flags,
                "name_index": const_pool.add(CONST.UTF8, method.name),
                "descriptor_index": const_pool.add(CONST.UTF8, method.signature),
                "attributes_count": len(attributes),
                "attributes": attributes,
            }
        )

    # Build InnerClasses (adds CP entries) BEFORE the pool is serialized.
    inner_attr = _build_inner_classes_attr(romclass, const_pool, inner_meta, children or {})

    const_pool.write(stream)

    class_access_flags = romclass.access_flags & CLASS_FLAG_MASK
    if strip_synthetic:
        class_access_flags &= ~0x1000
    if not (class_access_flags & 0x0200):  # ensure ACC_SUPER for normal classes
        class_access_flags |= 0x0020

    stream.write_u16(class_access_flags)
    stream.write_u16(class_name_id)
    stream.write_u16(superclass_name_id)
    stream.write_u16(len(interface_id_list))

    for elem in interface_id_list:
        stream.write_u16(elem)

    stream.write_u16(len(field_info_list))

    for field_info in field_info_list:
        stream.write_u16(field_info["access_flags"] & 0xFFFF)
        stream.write_u16(field_info["name_index"])
        stream.write_u16(field_info["descriptor_index"])
        stream.write_u16(field_info["attributes_count"])
        for attr in field_info["attributes"]:
            stream.write_u16(attr["attribute_name_index"])
            stream.write_u32(attr["attribute_length"])
            stream.write_u16(attr["constantvalue_index"])

    stream.write_u16(len(method_info_list))

    for method_info in method_info_list:
        stream.write_u16(method_info["access_flags"] & 0xFFFF)
        stream.write_u16(method_info["name_index"])
        stream.write_u16(method_info["descriptor_index"])
        stream.write_u16(method_info["attributes_count"])
        if method_info["attributes_count"]:
            attribute = method_info["attributes"][0]
            stream.write_u16(attribute["attribute_name_index"])
            stream.write_u32(attribute["attribute_length"])
            stream.write_u16(attribute["max_stack"])
            stream.write_u16(attribute["max_locals"])
            stream.write_u32(attribute["code_length"])
            stream.write_raw_bytes(attribute["code"])
            stream.write_u16(attribute["exception_table_length"])
            for exception in attribute["exception_table"]:
                stream.write_u16(exception[0])
                stream.write_u16(exception[1])
                stream.write_u16(exception[2])
                stream.write_u16(exception[3])
            stream.write_u16(attribute["attributes_count"])
            if attribute["attributes_count"]:
                raise NotImplementedError()

    if inner_attr:
        stream.write_u16(1)  # one class-level attribute: InnerClasses
        stream.write_u16(inner_attr["attribute_name_index"])
        stream.write_u32(2 + 8 * len(inner_attr["classes"]))
        stream.write_u16(len(inner_attr["classes"]))
        for inner_idx, outer_idx, name_idx, flags in inner_attr["classes"]:
            stream.write_u16(inner_idx)
            stream.write_u16(outer_idx)
            stream.write_u16(name_idx)
            stream.write_u16(flags)
    else:
        stream.write_u16(0)

    return method_info_list, const_pool


def create_class(
    romclass, jarfile, strip_synthetic: bool = False, inner_meta=None, children=None
) -> None:
    """Creates class"""
    class_name = romclass.class_name
    class_file = f"{class_name}.class"
    f_stream = io.BytesIO()
    stream = WriterStream(f_stream)
    res = dump_romclass(
        stream, romclass, strip_synthetic=strip_synthetic, inner_meta=inner_meta, children=children
    )
    stream.write()
    jarfile.writestr(class_file, f_stream.getvalue())
    return res


def _collect_classes_from_jar(jar_path):
    classes = set()
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for name in jar.namelist():
                if name.endswith('.class') and not name.startswith('META-INF/'):
                    classes.add(name[:-6])
    except Exception as exc:
        print(f"Warning: Failed to read {jar_path}: {exc}")
    return classes


def _load_lib_classes(libs_path):
    """Load set of class names from JAR files in libs directory."""
    lib_classes = set()
    if not libs_path or not os.path.exists(libs_path):
        return lib_classes

    print(f"Loading library classes from {libs_path}...")
    for filename in os.listdir(libs_path):
        if not filename.endswith('.jar'):
            continue
        jar_path = os.path.join(libs_path, filename)
        lib_classes |= _collect_classes_from_jar(jar_path)

    print(f"Loaded {len(lib_classes)} classes from libraries")
    return lib_classes


def _load_classes_from_list_file(list_path):
    classes = set()
    try:
        with open(list_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.endswith(".class"):
                    line = line[:-6]
                classes.add(line)
    except Exception as exc:
        print(f"Warning: Failed to read {list_path}: {exc}")
    return classes


def _load_classes_from_path(path):
    if not path:
        return set()
    if os.path.isdir(path):
        classes = set()
        for filename in os.listdir(path):
            if filename.endswith(".jar"):
                classes |= _collect_classes_from_jar(os.path.join(path, filename))
        return classes
    if path.endswith(".jmod"):
        classes = set()
        try:
            with zipfile.ZipFile(path, "r") as jmod:
                for name in jmod.namelist():
                    if name.startswith("classes/") and name.endswith(".class"):
                        classes.add(name[len("classes/"):-6])
        except Exception as exc:
            print(f"Warning: Failed to read {path}: {exc}")
        return classes
    if path.endswith(".jar"):
        return _collect_classes_from_jar(path)
    return _load_classes_from_list_file(path)


def _should_skip_class(class_name, skip_classes):
    """Check if a class should be skipped."""
    if skip_classes and class_name in skip_classes:
        return True

    return False


def _create_jar(
    jar_name,
    jxe,
    skip_classes=None,
    strip_synthetic=False,
):
    with zipfile.ZipFile(jar_name, "w") as jar_zipfile:
        total = len(jxe.image.classes)
        skipped = 0
        written = 0

        # Global nesting map from real ROM fields, used to reconstruct InnerClasses.
        inner_meta, children = build_inner_meta(jxe.image.classes)

        for idx, romclass in enumerate(jxe.image.classes, 1):
            if _should_skip_class(romclass.class_name, skip_classes):
                skipped += 1
                print(f"[{idx}/{total}] {romclass.class_name} (skipped)")
                continue

            print(f"[{idx}/{total}] {romclass.class_name}")
            try:
                create_class(
                    romclass,
                    jar_zipfile,
                    strip_synthetic=strip_synthetic,
                    inner_meta=inner_meta,
                    children=children,
                )
                written += 1
            except Exception as exc:  # pylint: disable=W0718
                print("bad class, skip", romclass.class_name, ": ", exc)

        print(f"\nSummary: {written} classes written, {skipped} classes skipped")


def _main():
    parser = argparse.ArgumentParser(
        description='Convert JXE (J9 ROM) files to JAR format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.jxe output.jar
  %(prog)s input.jxe output.jar --skip-libs libs/
  %(prog)s input.jxe output.jar --skip-jdk /path/to/rt.jar
  %(prog)s input.jxe output.jar --skip-classes path/to/rt.classes
  %(prog)s input.jxe output.jar --strip-synthetic
        """)

    parser.add_argument('jxe_file', help='Input JXE file')
    parser.add_argument('jar_file', help='Output JAR file')
    parser.add_argument('--skip-libs', metavar='DIR',
                        help='Skip classes found in JAR files in the specified directory')
    parser.add_argument('--skip-jdk', nargs='?', const='__DEFAULT__', metavar='PATH',
                        help='Skip JDK/JRE classes (default: src/rt.classes, or provide rt.jar)')
    parser.add_argument('--skip-classes', metavar='PATH',
                        help='Skip classes listed in a JAR/JMOD/list file or directory')
    parser.add_argument('--strip-synthetic', action='store_true',
                        help='Clear ACC_SYNTHETIC flags on classes/methods/fields')

    args = parser.parse_args()

    skip_classes = set()

    if args.skip_jdk and args.skip_jdk != "__DEFAULT__":
        skip_classes |= _load_classes_from_path(args.skip_jdk)
        print(f"Loaded {len(skip_classes)} classes from {args.skip_jdk}")
    else:
        local_rtclasses = os.path.join(os.path.dirname(__file__), "rt.classes")
        if os.path.isfile(local_rtclasses):
            skip_classes |= _load_classes_from_list_file(local_rtclasses)
            print(f"Loaded {len(skip_classes)} classes from {local_rtclasses}")
        else:
            print("Warning: src/rt.classes not found; not skipping JDK/JRE classes.")

    if args.skip_classes:
        skip_classes |= _load_classes_from_path(args.skip_classes)
        print(f"Loaded {len(skip_classes)} classes from {args.skip_classes}")

    if args.skip_libs:
        skip_classes |= _load_lib_classes(args.skip_libs)

    with open(args.jxe_file, "rb") as fp_jar:
        stream = ReaderStream(fp_jar)
        jxe = JXE.read(stream)
        _create_jar(
            args.jar_file,
            jxe,
            skip_classes=skip_classes if skip_classes else None,
            strip_synthetic=args.strip_synthetic,
        )


if __name__ == "__main__":
    _main()
