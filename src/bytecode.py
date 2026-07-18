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


def _return_opcode_for_signature(signature: str) -> int:
    """Infer the standard JVM return opcode from a method descriptor."""
    if not signature or ")" not in signature:
        return 0xB1  # void fallback
    ret = signature[signature.rindex(")") + 1:]
    if not ret or ret[0] == "V":
        return 0xB1  # return
    if ret[0] in "IBZSC":
        return 0xAC  # ireturn
    if ret[0] == "J":
        return 0xAD  # lreturn
    if ret[0] == "F":
        return 0xAE  # freturn
    if ret[0] == "D":
        return 0xAF  # dreturn
    return 0xB0  # areturn (L...; or [...;)


def _j9_instr_size(bytecode, i):
    """Return byte size of the J9 instruction at position *i*."""
    if i >= len(bytecode):
        return 1
    op = bytecode[i]

    # --- 2-byte opcodes (opcode + 1-byte operand) ---
    if op in (
        0x10,  # bipush
        0x12,  # ldc
        0x15, 0x16, 0x17, 0x18, 0x19,  # iload..aload
        0x36, 0x37, 0x38, 0x39, 0x3A,  # istore..astore
        0xA9,  # ret
        0xBC,  # newarray
    ):
        return 2

    # --- 3-byte opcodes (opcode + 2-byte operand, usually LE) ---
    if op in (
        0x11,  # sipush
        0x13,  # ldc_w
        0x14,  # ldc2_lw
        0x84,  # iinc
        0xB2, 0xB3, 0xB4, 0xB5,  # getstatic..putfield
        0xB6, 0xB7, 0xB8, 0xB9,  # invokevirtual..invokeinterface
        0xBB, 0xBD,  # new, anewarray
        0xC0, 0xC1,  # checkcast, instanceof
        0x99, 0x9A, 0x9B, 0x9C, 0x9D, 0x9E,  # ifeq..ifle
        0x9F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4,  # if_icmpeq..if_icmple
        0xA5, 0xA6,  # if_acmpeq, if_acmpne
        0xA7, 0xA8,  # goto, jsr
        0xC6, 0xC7,  # ifnull, ifnonnull
        0xF9,  # ldc2dw (J9)
        0xCB, 0xCC, 0xCD, 0xCE, 0xCF,  # J9 wide loads
        0xD0, 0xD1, 0xD2, 0xD3, 0xD4,  # J9 wide stores
    ):
        return 3

    # --- 4-byte opcodes ---
    if op == 0xC5:  # multianewarray
        return 4

    # --- 5-byte opcodes ---
    if op in (
        0xC8,  # goto_w
        0xD5,  # iincw (J9)
        0xE7,  # invokeinterface2 (J9): 1 + 2 nop/pad + 2 cp index
    ):
        return 5

    # --- variable-length: tableswitch ---
    if op == 0xAA:
        pad = (i + 1) % 4
        pad = pad if pad == 0 else (4 - pad)
        base = i + 1 + pad
        if base + 12 > len(bytecode):
            return len(bytecode) - i
        low = struct.unpack("<i", bytecode[base + 4 : base + 8])[0]
        high = struct.unpack("<i", bytecode[base + 8 : base + 12])[0]
        return 1 + pad + 12 + (high - low + 1) * 4

    # --- variable-length: lookupswitch ---
    if op == 0xAB:
        pad = (i + 1) % 4
        pad = pad if pad == 0 else (4 - pad)
        base = i + 1 + pad
        if base + 8 > len(bytecode):
            return len(bytecode) - i
        n = struct.unpack("<i", bytecode[base + 4 : base + 8])[0]
        return 1 + pad + 8 + n * 8

    # Everything else is 1-byte (simple opcodes, J9 1-byte specials).
    return 1


def _parse_param_types(descriptor):
    """Parse a method descriptor and return a list of single-char type indicators.

    E.g. '(FILjava/lang/String;[BD)V' -> ['F', 'I', 'L', 'L', 'B', 'D']
    Arrays and objects both return 'L'.
    """
    if not descriptor or descriptor[0] != "(":
        return []
    result = []
    i = 1
    while i < len(descriptor) and descriptor[i] != ")":
        ch = descriptor[i]
        if ch == "[":
            # Array - skip all '[' then the component type
            while i < len(descriptor) and descriptor[i] == "[":
                i += 1
            if i < len(descriptor) and descriptor[i] == "L":
                i = descriptor.find(";", i)
                if i == -1:
                    return result
            result.append("L")
        elif ch == "L":
            i = descriptor.find(";", i)
            if i == -1:
                return result
            result.append("L")
        elif ch in "BCDFIJSZ":
            result.append(ch)
        else:
            break
        i += 1
    return result


def _find_float_constants(bytecode, cp, signature):
    """Identify J9 CP indices that should be FLOAT instead of INTEGER.

    Walks bytecode with a simplified stack simulation.  Stack entries are
    either a J9 CP index (int, from ldc/ldc_w) or None.  When a
    float-consuming opcode pops a tracked index, it gets added to the
    returned set.
    """
    float_indices = set()
    stack = []

    def _mark(entry):
        if entry is not None:
            float_indices.add(entry)

    def _pop():
        return stack.pop() if stack else None

    def _push(v):
        stack.append(v)

    # Float-consuming opcodes that pop 1 float value
    FLOAT_POP1 = {
        0x38,  # fstore
        0x43, 0x44, 0x45, 0x46,  # fstore_0..fstore_3
        0x76,  # fneg
        0x8B, 0x8C, 0x8D,  # f2i, f2l, f2d
    }
    # Float-consuming opcodes that pop 2 float values
    FLOAT_POP2 = {
        0x62,  # fadd
        0x66,  # fsub
        0x6A,  # fmul
        0x6E,  # fdiv
        0x72,  # frem
        0x95, 0x96,  # fcmpl, fcmpg
    }
    # J9 wide fstore
    FLOAT_WIDE_STORE = {0xD2}  # fstorew

    # Branch opcodes (clear stack conservatively)
    BRANCH_OPS = {
        0x99, 0x9A, 0x9B, 0x9C, 0x9D, 0x9E,  # ifeq..ifle
        0x9F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4,  # if_icmpeq..if_icmple
        0xA5, 0xA6,  # if_acmpeq, if_acmpne
        0xA7, 0xA8,  # goto, jsr
        0xC6, 0xC7,  # ifnull, ifnonnull
        0xC8,  # goto_w
        0xAA, 0xAB,  # tableswitch, lookupswitch
    }

    # Opcodes that push exactly 1 non-CP value (no pops)
    PUSH1_OPS = {
        0x01,  # aconst_null
        0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,  # iconst_m1..iconst_5
        0x09, 0x0A,  # lconst_0, lconst_1  (2 slots but we track None)
        0x0B, 0x0C, 0x0D,  # fconst_0..fconst_2
        0x0E, 0x0F,  # dconst_0, dconst_1
        0x10,  # bipush
        0x11,  # sipush
        0x15, 0x16, 0x17, 0x18, 0x19,  # iload..aload
        0x1A, 0x1B, 0x1C, 0x1D,  # iload_0..iload_3
        0x1E, 0x1F, 0x20, 0x21,  # lload_0..lload_3
        0x22, 0x23, 0x24, 0x25,  # fload_0..fload_3
        0x26, 0x27, 0x28, 0x29,  # dload_0..dload_3
        0x2A, 0x2B, 0x2C, 0x2D,  # aload_0..aload_3
        0xBB,  # new
        0xB2,  # getstatic (no pop, just push)
        0xCB, 0xCC, 0xCD, 0xCE, 0xCF,  # J9 wide loads
    }

    # Opcodes that pop 1, push 1 (net zero, but must pop to keep stack aligned)
    POP1_PUSH1_OPS = {
        0xB4,  # getfield (pop objectref, push field value)
        0xBE,  # arraylength (pop arrayref, push length)
        0xC0,  # checkcast (pop ref, push ref - type unchanged)
        0xC1,  # instanceof (pop ref, push int)
    }

    # Array load ops: pop 2 (index, arrayref), push 1 (value)
    ARRAY_LOAD_OPS = {
        0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35,  # iaload..saload
    }

    # Return-1 opcodes (J9) - pop 1 value, mark as float if sig says F
    RETURN1_OPS = {0xAD, 0xB0, 0xF5}  # JBreturn1, JBsyncReturn1, JBretFromNative1

    i = 0
    while i < len(bytecode):
        op = bytecode[i]
        size = _j9_instr_size(bytecode, i)

        # --- ldc: push tracked CP index ---
        if op == 0x12:  # ldc (1-byte index)
            idx = bytecode[i + 1] if i + 1 < len(bytecode) else None
            _push(idx)

        elif op == 0x13:  # ldc_w (2-byte LE index)
            if i + 3 <= len(bytecode):
                idx = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
                _push(idx)
            else:
                _push(None)

        # --- float-consuming: pop 1 ---
        elif op in FLOAT_POP1:
            _mark(_pop())
            if op == 0x76:  # fneg: push result back
                _push(None)
            elif op in (0x8B, 0x8C, 0x8D):  # f2i, f2l, f2d: push converted
                _push(None)

        # --- float-consuming: pop 2 ---
        elif op in FLOAT_POP2:
            _mark(_pop())
            _mark(_pop())
            _push(None)  # result (None since it's a computed value)

        # --- fastore: pop value(float), index, arrayref ---
        elif op == 0x51:  # fastore
            _mark(_pop())  # value
            _pop()  # index
            _pop()  # arrayref

        # --- J9 wide fstore ---
        elif op in FLOAT_WIDE_STORE:
            _mark(_pop())

        # --- putfield / putstatic: check descriptor for F ---
        elif op in (0xB3, 0xB5):  # putstatic, putfield
            if i + 3 <= len(bytecode):
                cp_idx = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
                t = cp.transform.get(cp_idx)
                desc = t.get("descriptor", "") if t else ""
                if desc and desc[0] == "F":
                    _mark(_pop())
                else:
                    _pop()
                if op == 0xB5:  # putfield also pops objectref
                    _pop()
            else:
                stack.clear()

        # --- invoke*: check descriptor params for F ---
        elif op in (0xB6, 0xB7, 0xB8, 0xB9, 0xE7):
            if op == 0xE7:  # invokeinterface2: CP index at i+3
                cp_offset = 3
            else:
                cp_offset = 1
            if i + cp_offset + 2 <= len(bytecode):
                cp_idx = struct.unpack("<H", bytecode[i + cp_offset : i + cp_offset + 2])[0]
                t = cp.transform.get(cp_idx)
                desc = t.get("descriptor", "") if t else ""
                param_types = _parse_param_types(desc)
                # Total argument slots (including wide types)
                total_slots = 0
                for pt in param_types:
                    total_slots += 2 if pt in ("J", "D") else 1
                # Has receiver? (instance methods)
                has_receiver = op in (0xB6, 0xB7, 0xB9, 0xE7)
                total_pop = total_slots + (1 if has_receiver else 0)
                # Pop arguments from stack and check float params
                # Arguments are pushed left-to-right, so last param is TOS.
                # We pop in reverse param order.
                args = []
                for _ in range(total_slots):
                    args.append(_pop())
                if has_receiver:
                    _pop()  # objectref
                # Now args[0] = TOS = last param slot
                # Walk param_types in reverse to match stack positions
                slot = 0
                for pt in reversed(param_types):
                    if pt in ("J", "D"):
                        slot += 2
                    else:
                        if pt == "F" and slot < len(args):
                            _mark(args[slot])
                        slot += 1
                # Push return value if not void
                if desc and ")" in desc:
                    ret = desc[desc.rindex(")") + 1:]
                    if ret and ret[0] != "V":
                        _push(None)
            else:
                stack.clear()

        # --- J9 return1: mark as float if method returns F ---
        elif op in RETURN1_OPS:
            if signature and signature.endswith(")F"):
                _mark(_pop())
            else:
                _pop()

        # --- JBretFromNativeF (0xF6): always float return ---
        elif op == 0xF6:
            _mark(_pop())

        # --- dup: duplicate TOS ---
        elif op == 0x59:  # dup
            v = _pop()
            _push(v)
            _push(v)

        # --- swap: swap top two ---
        elif op == 0x5F:  # swap
            a = _pop()
            b = _pop()
            _push(a)
            _push(b)

        # --- pop ---
        elif op == 0x57:  # pop
            _pop()
        elif op == 0x58:  # pop2
            _pop()
            _pop()

        # --- dup_x1: ..., b, a -> ..., a, b, a ---
        elif op == 0x5A:
            a = _pop()
            b = _pop()
            _push(a)
            _push(b)
            _push(a)

        # --- dup_x2: ..., c, b, a -> ..., a, c, b, a ---
        elif op == 0x5B:
            a = _pop()
            b = _pop()
            c = _pop()
            _push(a)
            _push(c)
            _push(b)
            _push(a)

        # --- dup2: ..., b, a -> ..., b, a, b, a ---
        elif op == 0x5C:
            a = _pop()
            b = _pop()
            _push(b)
            _push(a)
            _push(b)
            _push(a)

        # --- push 1 None for various opcodes ---
        elif op in PUSH1_OPS:
            _push(None)

        # --- pop 1, push 1 (getfield, arraylength, checkcast, instanceof) ---
        elif op in POP1_PUSH1_OPS:
            _pop()
            _push(None)

        # --- array loads: pop 2 (index, arrayref), push 1 (value) ---
        elif op in ARRAY_LOAD_OPS:
            _pop()  # index
            _pop()  # arrayref
            _push(None)

        # --- aload0getfield (J9): pushes 1 value ---
        elif op == 0xD7:
            _push(None)

        # --- ldc2_lw / ldc2dw: push 1 wide value ---
        elif op in (0x14, 0xF9):
            _push(None)

        # --- store ops (pop 1) ---
        elif op in (
            0x36, 0x37, 0x39, 0x3A,  # istore, lstore, dstore, astore
            0x3B, 0x3C, 0x3D, 0x3E,  # istore_0..istore_3
            0x3F, 0x40, 0x41, 0x42,  # lstore_0..lstore_3
            0x47, 0x48, 0x49, 0x4A,  # dstore_0..dstore_3
            0x4B, 0x4C, 0x4D, 0x4E,  # astore_0..astore_3
            0xD0, 0xD1, 0xD3, 0xD4,  # J9 wide stores (not fstorew)
        ):
            _pop()

        # --- array stores (pop 3: value, index, arrayref) ---
        elif op in (0x4F, 0x50, 0x52, 0x53, 0x54, 0x55, 0x56):
            # iastore, lastore, dastore, aastore, bastore, castore, sastore
            _pop()
            _pop()
            _pop()

        # --- binary int/long ops (pop 2, push 1) ---
        elif op in (
            0x60, 0x61, 0x63,  # iadd, ladd, dadd
            0x64, 0x65, 0x67,  # isub, lsub, dsub
            0x68, 0x69, 0x6B,  # imul, lmul, dmul
            0x6C, 0x6D, 0x6F,  # idiv, ldiv, ddiv
            0x70, 0x71, 0x73,  # irem, lrem, drem
            0x78, 0x79,  # ishl, lshl
            0x7A, 0x7B,  # ishr, lshr
            0x7C, 0x7D,  # iushr, lushr
            0x7E, 0x7F,  # iand, land
            0x80, 0x81,  # ior, lor
            0x82, 0x83,  # ixor, lxor
            0x94,  # lcmp
            0x97, 0x98,  # dcmpl, dcmpg
        ):
            _pop()
            _pop()
            _push(None)

        # --- unary ops (pop 1, push 1) ---
        elif op in (
            0x74, 0x75, 0x77,  # ineg, lneg, dneg
            0x85, 0x86, 0x87,  # i2l, i2f, i2d
            0x88, 0x89, 0x8A,  # l2i, l2f, l2d
            0x8E, 0x8F, 0x90,  # d2i, d2l, d2f
            0x91, 0x92, 0x93,  # i2b, i2c, i2s
        ):
            _pop()
            _push(None)

        # --- branches: clear stack ---
        elif op in BRANCH_OPS:
            stack.clear()

        # --- return / athrow: clear stack ---
        elif op in (
            0xAC, 0xAE, 0xAF, 0xB1,  # JBreturn0, JBreturn2, JBsyncReturn0..2
            0xBF,  # athrow
            0xE4, 0xE5,  # returnFromConstructor, genericReturn
            0xF3, 0xF4, 0xF7, 0xF8,  # J9 retFromNative variants
        ):
            stack.clear()

        # --- monitorenter/monitorexit: pop 1 ---
        elif op in (0xC2, 0xC3):
            _pop()

        # --- iinc / iincw / nop-like: no stack effect ---
        elif op in (0x84, 0xD5, 0x00, 0xCA, 0xFA, 0xFE, 0xFF):
            pass

        # --- anything else: clear stack (conservative) ---
        else:
            stack.clear()

        i += size

    return float_indices


def _find_ternary_float_constants(bytecode, cp, known_float_indices=None):
    """Reclassify ldc INTEGER constants that are really floats but live inside a
    ternary branch.

    J9/JVM store `int` and `float` ldc constants in the same INTEGER pool slot, and
    the linear flow in `_find_float_constants` clears its stack at every branch, so a
    constant sitting in one arm of a `cond ? A : B` expression is never seen flowing
    into the float consumer. The result is one arm typed `int` and the other `float`,
    which decompilers cannot unify ("No common supertype for ternary expression").

    We match the ternary shape directly:  `ifXX L1 ; <arm A> ; goto L2 ; L1: <arm B> ; L2:`
    If one arm's terminal push is an int-ldc and the other arm's is unambiguously a
    float, Java type unification proves the int-ldc must be a float - so we return its
    J9 CP index for reclassification. (int-vs-float is the only case we touch, so a
    genuine int constant is never mis-typed.)
    """
    known_float_indices = known_float_indices or set()

    FLOAT_TERMINAL = {
        0x0B, 0x0C, 0x0D,              # fconst_0..2
        0x17, 0x22, 0x23, 0x24, 0x25,  # fload, fload_0..3
        0x30,                          # faload
        0x76,                          # fneg
        0x86, 0x89, 0x90,              # i2f, l2f, d2f
        0x62, 0x66, 0x6A, 0x6E, 0x72,  # fadd, fsub, fmul, fdiv, frem
        0xCD,                          # J9 wide fload
    }

    def _ldc_index(op, at):
        if op == 0x12 and at + 2 <= len(bytecode):          # ldc
            return bytecode[at + 1]
        if op == 0x13 and at + 3 <= len(bytecode):          # ldc_w
            return struct.unpack("<H", bytecode[at + 1 : at + 3])[0]
        return None

    def _int_ldc_index(op, at):
        k = _ldc_index(op, at)
        if k is None:
            return None
        t = cp.transform.get(k)
        return k if (t and t.get("type") == CONST.INTEGER) else None

    def _classify_arm(start, end):
        """Return ('intconst', cp_idx) | ('float', None) | ('other', None) from the
        arm's terminal value-producing instruction."""
        kind, idx = "other", None
        j = start
        while j < end:
            op = bytecode[j]
            sz = _j9_instr_size(bytecode, j)
            k = _ldc_index(op, j)
            if k in known_float_indices:
                kind, idx = "float", None
            elif k is not None and _int_ldc_index(op, j) is not None:
                kind, idx = "intconst", k
            elif op in FLOAT_TERMINAL:
                kind, idx = "float", None
            elif op in (0xB6, 0xB7, 0xB8, 0xB9, 0xE7):      # invoke* -> float if returns F
                co = 3 if op == 0xE7 else 1
                if j + co + 2 <= len(bytecode):
                    ci = struct.unpack("<H", bytecode[j + co : j + co + 2])[0]
                    t = cp.transform.get(ci)
                    d = t.get("descriptor", "") if t else ""
                    r = d[d.rindex(")") + 1 :] if ")" in d else ""
                    kind, idx = ("float", None) if (r and r[0] == "F") else ("other", None)
                else:
                    kind, idx = "other", None
            elif op == 0xA7:                                # goto: not a push, keep prior
                pass
            else:
                kind, idx = "other", None
            j += sz if sz > 0 else 1
        return kind, idx

    result = set()
    n = len(bytecode)
    i = 0
    while i < n:
        op = bytecode[i]
        sz = _j9_instr_size(bytecode, i)
        if ((0x99 <= op <= 0xA6) or op in (0xC6, 0xC7)) and i + 3 <= n:
            rel = struct.unpack("<h", bytecode[i + 1 : i + 3])[0]
            T = i + rel                                     # L1 (ifXX target = arm B start)
            a_start = i + 3
            if a_start < T <= n:
                g = l2 = None
                if (
                    T - 3 >= a_start
                    and T <= n
                    and bytecode[T - 3] == 0xA7
                ):                                          # goto (3B) ends arm A
                    g = T - 3
                    if g + 3 <= n:
                        l2 = g + struct.unpack("<h", bytecode[g + 1 : g + 3])[0]
                elif (
                    T - 5 >= a_start
                    and T <= n
                    and bytecode[T - 5] == 0xC8
                ):                                          # goto_w (5B)
                    g = T - 5
                    if g + 5 <= n:
                        l2 = g + struct.unpack("<i", bytecode[g + 1 : g + 5])[0]
                if g is not None and l2 is not None and T < l2 <= n:
                    ka, ia = _classify_arm(a_start, g)
                    kb, ib = _classify_arm(T, l2)
                    if ka == "intconst" and kb == "float":
                        result.add(ia)
                    elif kb == "intconst" and ka == "float":
                        result.add(ib)
        i += sz if sz > 0 else 1
    return result


def transform_bytecode(bytecode, signature, cp, owner=None, method_name=None):
    """Transforms bytecode and returns (new_bytecode, offset_map)."""
    i = 0
    new_cp_transform = {}

    # Pre-pass: identify float constants via stack simulation
    float_cp_indices = _find_float_constants(bytecode, cp, signature)
    # Pre-pass: float constants hidden inside ternary branches (int/float merge)
    float_cp_indices |= _find_ternary_float_constants(bytecode, cp, float_cp_indices)
    for j9_idx in float_cp_indices:
        t = cp.transform.get(j9_idx)
        if t and t.get("type") == CONST.INTEGER:
            new_cp_transform[t["new_index"]] = b"\x04"  # FLOAT

    new_bytecode = bytearray()
    offset_map = {}
    fixups = []

    def _pack_s16(value):
        return struct.pack(">h", value)

    def _pack_s32(value):
        return struct.pack(">i", value)

    while i < len(bytecode):
        offset_map[i] = len(new_bytecode)
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
            op_pos = len(new_bytecode)
            new_bytecode.append(opcode)
            if i + 3 > len(bytecode):
                break
            index = struct.unpack("<H", bytecode[i + 1 : i + 3])[0]
            if index == 0xFFFF:
                break
            transform = cp.transform.get(index)
            if not transform:
                break
            # J9 devirtualizes `invokevirtual` of a final method into `invokespecial`
            # (final => statically bindable). Standard bytecode forbids invokespecial
            # to a superclass method on a non-`this` receiver, so the HotSpot verifier
            # rejects it ("Incompatible object argument for invokespecial"). Object's
            # getClass/wait/notify/notifyAll are final - virtual and non-virtual dispatch
            # are identical and no super-call is possible - so restoring invokevirtual is
            # always safe. (The common trigger is the `x.getClass()` NPE/equals idiom.)
            if (
                opcode == JBOpcode.JBinvokespecial
                and transform.get("ref_class") == "java/lang/Object"
                and transform.get("ref_name")
                in ("getClass", "wait", "notify", "notifyAll")
            ):
                new_bytecode[op_pos] = JBOpcode.JBinvokevirtual
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
            cp_len = None
            if getattr(cp, "romclass", None) is not None:
                cp_len = len(cp.romclass.constant_pool)
            if cp_len is not None and index == cp_len and index > 0:
                index -= 1
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
                    raw_long = cp.get_raw_long(index)
                    if raw_long is not None:
                        new_index = cp.add(CONST.LONG, raw_long) - 1
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
            cp_len = None
            if getattr(cp, "romclass", None) is not None:
                cp_len = len(cp.romclass.constant_pool)
            if cp_len is not None and index == cp_len and index > 0:
                index -= 1
            if cp.check_transform(index, b"\x06"):
                # Already DOUBLE (8 bytes + phantom) - just keep it.
                transform = cp.get_transform(index)
                new_index = transform["new_index"]
                tmp = struct.pack(">H", new_index + 1)
                new_bytecode += tmp
            elif cp.check_transform(index, b"\x03"):
                # INTEGER (4 bytes, no phantom) - create proper DOUBLE entry.
                transform = cp.get_transform(index)
                old_index = transform["new_index"]
                raw = cp.get_int(old_index)
                new_index = cp.add(CONST.DOUBLE, (raw, 0)) - 1
                tmp = struct.pack(">H", new_index + 1)
                new_bytecode += tmp
            else:
                raw_long = cp.get_raw_long(index)
                if raw_long is not None:
                    new_index = cp.add(CONST.DOUBLE, raw_long) - 1
                else:
                    transform = cp.transform.get(index)
                    if transform:
                        new_index = transform["new_index"]
                        new_cp_transform[new_index] = b"\x06"
                    else:
                        where = ""
                        if owner and method_name:
                            where = f" in {owner}.{method_name}{signature}"
                        print(f"WARNING: ldc2_dw fallback{where} (cp={index})")
                        new_index = 0
                tmp = struct.pack(">H", new_index + 1)
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
        elif opcode in (JBOpcode.JBsipush,):
            # sipush: push a 16-bit signed immediate onto the stack.
            new_bytecode.append(opcode)
            if i + 3 > len(bytecode):
                break
            value = struct.unpack("<h", bytecode[i + 1 : i + 3])[0]
            new_bytecode += struct.pack(">h", value)
            i += 3
        elif opcode in (
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
            if i + 3 > len(bytecode):
                break
            rel = struct.unpack("<h", bytecode[i + 1 : i + 3])[0]
            target = i + rel
            fixups.append((len(new_bytecode), target, 2, i))
            new_bytecode += b"\x00\x00"
            i += 3
        elif opcode in (JBOpcode.JBaload0getfield,):
            # J9 prefix for implicit aload_0 before a field access.
            new_bytecode.append(JBOpcode.JBaload0)
            i += 1
        elif opcode in (JBOpcode.JBreturn0, JBOpcode.JBsyncReturn0, JBOpcode.JBreturnFromConstructor, JBOpcode.JBretFromNative0):
            # JBreturn0 -> return (0xb1)
            # Used only if function return void
            new_bytecode.append(0xB1)
            i += 1
        elif opcode in (JBOpcode.JBreturn1, JBOpcode.JBsyncReturn1, JBOpcode.JBretFromNative1):
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
        elif opcode == JBOpcode.JBretFromNativeF:
            new_bytecode.append(0xAE)  # freturn
            i += 1
        elif opcode == JBOpcode.JBretFromNativeD:
            new_bytecode.append(0xAF)  # dreturn
            i += 1
        elif opcode == JBOpcode.JBretFromNativeJ:
            new_bytecode.append(0xAD)  # lreturn
            i += 1
        elif opcode in (JBOpcode.JBgenericReturn, JBOpcode.JBreturnToMicroJIT):
            # Generic return - infer from full method signature.
            new_bytecode.append(_return_opcode_for_signature(signature))
            i += 1
        elif opcode in (JBOpcode.JBasyncCheck, JBOpcode.JBbreakpoint, JBOpcode.JBimpdep1, JBOpcode.JBimpdep2):
            new_bytecode.append(0x00)  # nop
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
            origin = i
            new_bytecode.append(opcode)
            in_padding = (i + 1) % 4
            in_padding = in_padding if in_padding == 0 else (4 - in_padding)
            out_padding = len(new_bytecode) % 4
            out_padding = out_padding if out_padding == 0 else (4 - out_padding)
            new_bytecode.extend(b"\x00" * out_padding)
            i += 1 + in_padding
            if i + 12 > len(bytecode):
                break
            default = struct.unpack("<i", bytecode[i : i + 4])[0]
            fixups.append((len(new_bytecode), origin + default, 4, origin))
            new_bytecode += b"\x00\x00\x00\x00"
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
                jump = struct.unpack("<i", bytecode[i : i + 4])[0]
                fixups.append((len(new_bytecode), origin + jump, 4, origin))
                new_bytecode += b"\x00\x00\x00\x00"
                i += 4
        elif opcode in (JBOpcode.JBlookupswitch,):
            origin = i
            new_bytecode.append(opcode)
            in_padding = (i + 1) % 4
            in_padding = in_padding if in_padding == 0 else (4 - in_padding)
            out_padding = len(new_bytecode) % 4
            out_padding = out_padding if out_padding == 0 else (4 - out_padding)
            new_bytecode.extend(b"\x00" * out_padding)
            i += 1 + in_padding
            if i + 8 > len(bytecode):
                break
            default = struct.unpack("<i", bytecode[i : i + 4])[0]
            fixups.append((len(new_bytecode), origin + default, 4, origin))
            new_bytecode += b"\x00\x00\x00\x00"
            i += 4
            n = struct.unpack("<i", bytecode[i : i + 4])[0]
            new_bytecode += struct.pack(">i", n)
            i += 4
            for _ in range(n):
                if i + 8 > len(bytecode):
                    break
                match = struct.unpack("<i", bytecode[i : i + 4])[0]
                new_bytecode += struct.pack(">i", match)
                i += 4
                jump = struct.unpack("<i", bytecode[i : i + 4])[0]
                fixups.append((len(new_bytecode), origin + jump, 4, origin))
                new_bytecode += b"\x00\x00\x00\x00"
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
            rel = struct.unpack("<i", bytecode[i + 1 : i + 5])[0]
            target = i + rel
            fixups.append((len(new_bytecode), target, 4, i))
            new_bytecode += b"\x00\x00\x00\x00"
            i += 5
        else:
            new_bytecode.append(opcode)
            i += 1

    offset_map[len(bytecode)] = len(new_bytecode)

    for pos, target, size, origin in fixups:
        if target not in offset_map:
            continue
        new_rel = offset_map[target] - offset_map[origin]
        if size == 2:
            new_bytecode[pos : pos + 2] = _pack_s16(new_rel)
        else:
            new_bytecode[pos : pos + 4] = _pack_s32(new_rel)

    for index, value in new_cp_transform.items():
        cp.apply_transform(index, value)

    return new_bytecode, offset_map
