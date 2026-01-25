"""Java bytecode."""
import struct
from enum import Enum
from bitstring import BitArray
from constpool import CONST


class JBOpcode(int, Enum):
    """Opcode mapping."""

    JBnop = 0x00
    JBaconstnull = 0x01
    JBiconstm1 = 0x02
    JBiconst0 = 0x03
    JBiconst1 = 0x04
    JBiconst2 = 0x05
    JBiconst3 = 0x06
    JBiconst4 = 0x07
    JBiconst5 = 0x08
    JBlconst0 = 0x09
    JBlconst1 = 0x0A
    JBfconst0 = 0x0B
    JBfconst1 = 0x0C
    JBfconst2 = 0x0D
    JBdconst0 = 0x0E
    JBdconst1 = 0x0F
    JBbipush = 0x10
    JBsipush = 0x11
    JBldc = 0x12
    JBldcw = 0x13
    JBldc2lw = 0x14
    JBiload = 0x15
    JBlload = 0x16
    JBfload = 0x17
    JBdload = 0x18
    JBaload = 0x19
    JBiload0 = 0x1A
    JBiload1 = 0x1B
    JBiload2 = 0x1C
    JBiload3 = 0x1D
    JBlload0 = 0x1E
    JBlload1 = 0x1F
    JBlload2 = 0x20
    JBlload3 = 0x21
    JBfload0 = 0x22
    JBfload1 = 0x23
    JBfload2 = 0x24
    JBfload3 = 0x25
    JBdload0 = 0x26
    JBdload1 = 0x27
    JBdload2 = 0x28
    JBdload3 = 0x29
    JBaload0 = 0x2A
    JBaload1 = 0x2B
    JBaload2 = 0x2C
    JBaload3 = 0x2D
    JBiaload = 0x2E
    JBlaload = 0x2F
    JBfaload = 0x30
    JBdaload = 0x31
    JBaaload = 0x32
    JBbaload = 0x33
    JBcaload = 0x34
    JBsaload = 0x35
    JBistore = 0x36
    JBlstore = 0x37
    JBfstore = 0x38
    JBdstore = 0x39
    JBastore = 0x3A
    JBistore0 = 0x3B
    JBistore1 = 0x3C
    JBistore2 = 0x3D
    JBistore3 = 0x3E
    JBlstore0 = 0x3F
    JBlstore1 = 0x40
    JBlstore2 = 0x41
    JBlstore3 = 0x42
    JBfstore0 = 0x43
    JBfstore1 = 0x44
    JBfstore2 = 0x45
    JBfstore3 = 0x46
    JBdstore0 = 0x47
    JBdstore1 = 0x48
    JBdstore2 = 0x49
    JBdstore3 = 0x4A
    JBastore0 = 0x4B
    JBastore1 = 0x4C
    JBastore2 = 0x4D
    JBastore3 = 0x4E
    JBiastore = 0x4F
    JBlastore = 0x50
    JBfastore = 0x51
    JBdastore = 0x52
    JBaastore = 0x53
    JBbastore = 0x54
    JBcastore = 0x55
    JBsastore = 0x56
    JBpop = 0x57
    JBpop2 = 0x58
    JBdup = 0x59
    JBdupx1 = 0x5A
    JBdupx2 = 0x5B
    JBdup2 = 0x5C
    JBdup2x1 = 0x5D
    JBdup2x2 = 0x5E
    JBswap = 0x5F
    JBiadd = 0x60
    JBladd = 0x61
    JBfadd = 0x62
    JBdadd = 0x63
    JBisub = 0x64
    JBlsub = 0x65
    JBfsub = 0x66
    JBdsub = 0x67
    JBimul = 0x68
    JBlmul = 0x69
    JBfmul = 0x6A
    JBdmul = 0x6B
    JBidiv = 0x6C
    JBldiv = 0x6D
    JBfdiv = 0x6E
    JBddiv = 0x6F
    JBirem = 0x70
    JBlrem = 0x71
    JBfrem = 0x72
    JBdrem = 0x73
    JBineg = 0x74
    JBlneg = 0x75
    JBfneg = 0x76
    JBdneg = 0x77
    JBishl = 0x78
    JBlshl = 0x79
    JBishr = 0x7A
    JBlshr = 0x7B
    JBiushr = 0x7C
    JBlushr = 0x7D
    JBiand = 0x7E
    JBland = 0x7F
    JBior = 0x80
    JBlor = 0x81
    JBixor = 0x82
    JBlxor = 0x83
    JBiinc = 0x84
    JBi2l = 0x85
    JBi2f = 0x86
    JBi2d = 0x87
    JBl2i = 0x88
    JBl2f = 0x89
    JBl2d = 0x8A
    JBf2i = 0x8B
    JBf2l = 0x8C
    JBf2d = 0x8D
    JBd2i = 0x8E
    JBd2l = 0x8F
    JBd2f = 0x90
    JBi2b = 0x91
    JBi2c = 0x92
    JBi2s = 0x93
    JBlcmp = 0x94
    JBfcmpl = 0x95
    JBfcmpg = 0x96
    JBdcmpl = 0x97
    JBdcmpg = 0x98
    JBifeq = 0x99
    JBifne = 0x9A
    JBiflt = 0x9B
    JBifge = 0x9C
    JBifgt = 0x9D
    JBifle = 0x9E
    JBificmpeq = 0x9F
    JBificmpne = 0xA0
    JBificmplt = 0xA1
    JBificmpge = 0xA2
    JBificmpgt = 0xA3
    JBificmple = 0xA4
    JBifacmpeq = 0xA5
    JBifacmpne = 0xA6
    JBgoto = 0xA7
    JBjsr = 0xA8
    JBret = 0xA9
    JBtableswitch = 0xAA
    JBlookupswitch = 0xAB
    JBreturn0 = 0xAC
    JBreturn1 = 0xAD
    JBreturn2 = 0xAE
    JBsyncReturn0 = 0xAF
    JBsyncReturn1 = 0xB0
    JBsyncReturn2 = 0xB1
    JBgetstatic = 0xB2
    JBputstatic = 0xB3
    JBgetfield = 0xB4
    JBputfield = 0xB5
    JBinvokevirtual = 0xB6
    JBinvokespecial = 0xB7
    JBinvokestatic = 0xB8
    JBinvokeinterface = 0xB9
    JBnew = 0xBB
    JBnewarray = 0xBC
    JBanewarray = 0xBD
    JBarraylength = 0xBE
    JBathrow = 0xBF
    JBcheckcast = 0xC0
    JBinstanceof = 0xC1
    JBmonitorenter = 0xC2
    JBmonitorexit = 0xC3
    JBmultianewarray = 0xC5
    JBifnull = 0xC6
    JBifnonnull = 0xC7
    JBgotow = 0xC8
    JBbreakpoint = 0xCA
    JBiloadw = 0xCB
    JBlloadw = 0xCC
    JBfloadw = 0xCD
    JBdloadw = 0xCE
    JBaloadw = 0xCF
    JBistorew = 0xD0
    JBlstorew = 0xD1
    JBfstorew = 0xD2
    JBdstorew = 0xD3
    JBastorew = 0xD4
    JBiincw = 0xD5
    JBaload0getfield = 0xD7
    JBreturnFromConstructor = 0xE4
    JBgenericReturn = 0xE5
    JBinvokeinterface2 = 0xE7
    JBreturnToMicroJIT = 0xF3
    JBretFromNative0 = 0xF4
    JBretFromNative1 = 0xF5
    JBretFromNativeF = 0xF6
    JBretFromNativeD = 0xF7
    JBretFromNativeJ = 0xF8
    JBldc2dw = 0xF9
    JBasyncCheck = 0xFA
    JBimpdep1 = 0xFE
    JBimpdep2 = 0xFF


def _method_arg_slots(descriptor: str) -> int:
    """Return number of local slots for method args (not including receiver)."""
    if not descriptor:
        return 0
    if descriptor[0] != "(":
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


def transform_bytecode(bytecode, signature, cp, owner=None, method_name=None):
    """Transforms bytecode"""
    i = 0
    new_cp_transform = {}
    new_bytecode = bytearray()

    while i < len(bytecode):
        opcode = bytecode[i]
        if opcode in (
            JBOpcode.JBgetstatic,
            JBOpcode.JBputstatic,
            JBOpcode.JBgetfield,
            JBOpcode.JBputfield,
            JBOpcode.JBinvokevirtual,
            JBOpcode.JBinvokespecial,
            JBOpcode.JBinvokestatic,
            JBOpcode.JBnew,
            JBOpcode.JBanewarray,
            JBOpcode.JBcheckcast,
            JBOpcode.JBinstanceof,
        ):
            new_bytecode.append(opcode)
            if i + 3 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"]
            tmp = struct.pack(">H", new_index + 1)
            new_bytecode += tmp
            i += 3
        elif opcode in (JBOpcode.JBldcw,):
            new_bytecode.append(opcode)
            if i + 3 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"]
            tmp = struct.pack(">H", new_index + 1)
            new_bytecode += tmp
            i += 3
        elif opcode in (JBOpcode.JBldc2lw,):
            if i + 3 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            new_bytecode.append(JBOpcode.JBldc2lw)
            if cp.check_transform(index, b"\x06"):
                transform = cp.get_transform(index)
                new_index = transform["new_index"]
                tmp = struct.pack(">H", new_index + 1)
                new_cp_transform[new_index] = b"\x05"
                new_bytecode += tmp
            else:
                if cp.check_transform(index, b"\x03"):
                    transform = cp.get_transform(index)
                    new_index = transform["new_index"]
                    new_index = cp.add(CONST.LONG, (0, cp.get_int(new_index))) - 1
                else:
                    where = ""
                    if owner and method_name:
                        where = f" in {owner}.{method_name}{signature}"
                    print(f"WARNING: ldc2_w fallback{where} (cp={index})")
                    # TODO: very dirty hack, because we incorrectly
                    # parse constant pool used in 1 case
                    new_index = 0
                tmp = struct.pack(">H", new_index + 1)
                new_bytecode += tmp
            i += 3
        elif opcode in (JBOpcode.JBldc2dw,):
            new_bytecode.append(JBOpcode.JBldc2lw)
            if i + 3 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"]
            tmp = struct.pack(">H", new_index + 1)
            new_cp_transform[new_index] = b"\x06"
            new_bytecode += tmp
            i += 3
        elif opcode in (JBOpcode.JBiincw,):
            # Convert J9 wide iinc to standard wide form.
            new_bytecode.append(0xC4)  # wide
            new_bytecode.append(JBOpcode.JBiinc)
            o1 = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            o2 = struct.unpack("<H", bytecode[i + 3 : i + 5])[0]
            t1 = struct.pack(">H", o1)
            t2 = struct.pack(">H", o2)
            new_bytecode += t1 + t2
            i += 5
        elif opcode in (
            JBOpcode.JBiloadw,
            JBOpcode.JBlloadw,
            JBOpcode.JBfloadw,
            JBOpcode.JBdloadw,
            JBOpcode.JBaloadw,
            JBOpcode.JBistorew,
            JBOpcode.JBlstorew,
            JBOpcode.JBfstorew,
            JBOpcode.JBdstorew,
            JBOpcode.JBastorew,
        ):
            # Convert J9 wide load/store to standard wide form.
            opcode_map = {
                JBOpcode.JBiloadw: JBOpcode.JBiload,
                JBOpcode.JBlloadw: JBOpcode.JBlload,
                JBOpcode.JBfloadw: JBOpcode.JBfload,
                JBOpcode.JBdloadw: JBOpcode.JBdload,
                JBOpcode.JBaloadw: JBOpcode.JBaload,
                JBOpcode.JBistorew: JBOpcode.JBistore,
                JBOpcode.JBlstorew: JBOpcode.JBlstore,
                JBOpcode.JBfstorew: JBOpcode.JBfstore,
                JBOpcode.JBdstorew: JBOpcode.JBdstore,
                JBOpcode.JBastorew: JBOpcode.JBastore,
            }
            new_bytecode.append(0xC4)  # wide
            new_bytecode.append(opcode_map[opcode])
            value = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            tmp = struct.pack(">H", value)
            new_bytecode += tmp
            i += 3
        elif opcode in (
            JBOpcode.JBsipush,
            JBOpcode.JBifeq,
            JBOpcode.JBifne,
            JBOpcode.JBiflt,
            JBOpcode.JBifge,
            JBOpcode.JBifgt,
            JBOpcode.JBifle,
            JBOpcode.JBificmpeq,
            JBOpcode.JBificmpne,
            JBOpcode.JBificmplt,
            JBOpcode.JBificmpge,
            JBOpcode.JBificmpgt,
            JBOpcode.JBificmple,
            JBOpcode.JBifacmpeq,
            JBOpcode.JBifacmpne,
            JBOpcode.JBgoto,
            JBOpcode.JBjsr,
            JBOpcode.JBifnull,
            JBOpcode.JBifnonnull,
        ):
            new_bytecode.append(opcode)
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            tmp = struct.pack(">H", index)
            new_bytecode += tmp
            i += 3
        elif opcode in (JBOpcode.JBaload0getfield,):
            new_bytecode.append(JBOpcode.JBaload0)
            i += 1
        elif opcode in (JBOpcode.JBreturn0, JBOpcode.JBsyncReturn0, JBOpcode.JBreturnFromConstructor):
            # JBreturn0 -> return (0xb1)
            # Used only if function return void
            new_bytecode.append(0xB1)
            i += 1
        elif opcode in (JBOpcode.JBreturn1, JBOpcode.JBsyncReturn1):
            # JBreturn1 -> areturn/ireturn/freturn (0xb0)
            # Used only after push on stack
            if signature.endswith(")B") or signature.endswith(")Z") or signature.endswith(")S") or \
                signature.endswith(")C") or signature.endswith(")I"):
                new_bytecode.append(0xAC)
            elif signature.endswith(")F"):
                new_bytecode.append(0xAE)
            else:
                new_bytecode.append(0xB0)
            i += 1
        elif opcode in (JBOpcode.JBreturn2, JBOpcode.JBsyncReturn2):
            # JBreturn2 -> lreturn/dreturn
            # Used only after push on stack
            if signature.endswith(")J"):
                new_bytecode.append(0xAD)
            elif signature.endswith(")D"):
                new_bytecode.append(0xAF)
            else:
                new_bytecode.append(0xAD)
            i += 1
        elif opcode in (JBOpcode.JBinvokeinterface2,):
            # JBinvokeinterface2 -> invokeinterface
            # Usually placed as JBinvokeinterface2 JBnop JBinvokeinterface
            # invokeinterface in Oracle get 4 bytes but j9 get 2
            # JBinvokeinterface2 JBnop correlate with this to fix this misalign
            new_bytecode.append(JBOpcode.JBinvokeinterface)
            if i + 5 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 3 : i + 5])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"]
            tmp = struct.pack(">H", new_index + 1)
            new_cp_transform[new_index] = b"\x0b"
            new_bytecode += tmp
            count = _method_arg_slots(transform.get("descriptor")) + 1
            new_bytecode.append(count & 0xFF)
            new_bytecode.append(0)
            i += 5
        elif opcode in (JBOpcode.JBinvokeinterface,):
            new_bytecode.append(JBOpcode.JBinvokeinterface)
            if i + 3 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"]
            tmp = struct.pack(">H", new_index + 1)
            new_cp_transform[new_index] = b"\x0b"
            new_bytecode += tmp
            count = _method_arg_slots(transform.get("descriptor")) + 1
            new_bytecode.append(count & 0xFF)
            new_bytecode.append(0)
            # If J9 encoded trailing count/zero bytes, consume them.
            if i + 4 < len(bytecode) and bytecode[i + 3] == 0 and bytecode[i + 4] == 0:
                i += 5
            else:
                i += 3
        elif opcode in (JBOpcode.JBldc,):
            index = bytecode[i + 1]
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"] + 1
            if new_index > 0xFF:
                new_bytecode.append(JBOpcode.JBldcw)
                new_bytecode += struct.pack(">H", new_index)
            else:
                new_bytecode.append(opcode)
                new_bytecode.append(new_index)
            i += 2
        elif opcode in (
            JBOpcode.JBbipush,
            JBOpcode.JBnewarray,
            JBOpcode.JBiload,
            JBOpcode.JBlload,
            JBOpcode.JBfload,
            JBOpcode.JBdload,
            JBOpcode.JBaload,
            JBOpcode.JBistore,
            JBOpcode.JBlstore,
            JBOpcode.JBfstore,
            JBOpcode.JBdstore,
            JBOpcode.JBastore,
            JBOpcode.JBret,
        ):
            new_bytecode.append(opcode)
            new_bytecode.append(bytecode[i + 1])
            i += 2
        elif opcode in (JBOpcode.JBiinc,):
            new_bytecode.append(opcode)
            new_bytecode.append(bytecode[i + 1])
            new_bytecode.append(bytecode[i + 2])
            i += 3
        elif opcode in (JBOpcode.JBtableswitch,):
            new_bytecode.append(opcode)
            in_padding = (i + 1) % 4
            in_padding = in_padding if in_padding == 0 else (4 - in_padding)
            out_padding = len(new_bytecode) % 4
            out_padding = out_padding if out_padding == 0 else (4 - out_padding)
            for _ in range(out_padding):
                new_bytecode.append(0x0)
            i += 1 + in_padding
            if i + 12 > len(bytecode):
                break
            default = struct.unpack("<I", bytecode[i : i + 4])[0]
            new_bytecode += struct.pack(">I", default)
            i += 4
            low = struct.unpack("<i", bytecode[i : i + 4])[0]
            new_bytecode += struct.pack(">i", low)
            i += 4
            high = struct.unpack("<i", bytecode[i : i + 4])[0]
            new_bytecode += struct.pack(">i", high)
            i += 4
            for _ in range(high - low + 1):
                if i + 4 > len(bytecode):
                    break
                jump = struct.unpack("<I", bytecode[i : i + 4])[0]
                new_bytecode += struct.pack(">I", jump)
                i += 4
        elif opcode in (JBOpcode.JBlookupswitch,):
            new_bytecode.append(opcode)
            in_padding = (i + 1) % 4
            in_padding = in_padding if in_padding == 0 else (4 - in_padding)
            out_padding = len(new_bytecode) % 4
            out_padding = out_padding if out_padding == 0 else (4 - out_padding)
            for _ in range(out_padding):
                new_bytecode.append(0x0)
            i += 1 + in_padding
            if i + 8 > len(bytecode):
                break
            default = struct.unpack("<I", bytecode[i : i + 4])[0]
            new_bytecode += struct.pack(">I", default)
            i += 4
            n = struct.unpack("<I", bytecode[i : i + 4])[0]
            new_bytecode += struct.pack(">I", n)
            i += 4
            for _ in range(n):
                if i + 8 > len(bytecode):
                    break
                match = struct.unpack("<I", bytecode[i : i + 4])[0]
                new_bytecode += struct.pack(">I", match)
                i += 4
                jump = struct.unpack("<I", bytecode[i : i + 4])[0]
                new_bytecode += struct.pack(">I", jump)
                i += 4
        elif opcode in (JBOpcode.JBmultianewarray,):
            new_bytecode.append(opcode)
            if i + 4 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            new_index = transform["new_index"]
            tmp = struct.pack(">H", new_index + 1)
            new_bytecode += tmp
            new_bytecode.append(bytecode[i + 3])
            i += 4
        elif opcode in (JBOpcode.JBgotow,):
            new_bytecode.append(opcode)
            if i + 5 > len(bytecode):
                break
            value = struct.unpack("<I", bytecode[i + 1 : i + 5])[0]
            tmp = struct.pack(">I", value)
            new_bytecode += tmp
            i += 5
        else:
            new_bytecode.append(opcode)
            i += 1

    for index, value in new_cp_transform.items():
        cp.apply_transform(index, value)

    return new_bytecode
