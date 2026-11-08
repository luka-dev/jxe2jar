"""rtdiff.py ORIG.jar RT.jar [-v N]: structural + bytecode comparison of a jar against its
jar2jxe -> jxe2jar round trip. Reports attribute losses, flag/version/member mismatches and
per-method bytecode identity (CP indices resolved to symbols, ldc/ldc_w merged, nops dropped)."""
import sys, zipfile, struct, collections, json

OPS = ("nop aconst_null iconst_m1 iconst_0 iconst_1 iconst_2 iconst_3 iconst_4 iconst_5 lconst_0 lconst_1 "
       "fconst_0 fconst_1 fconst_2 dconst_0 dconst_1 bipush sipush ldc ldc_w ldc2_w iload lload fload dload aload "
       "iload_0 iload_1 iload_2 iload_3 lload_0 lload_1 lload_2 lload_3 fload_0 fload_1 fload_2 fload_3 "
       "dload_0 dload_1 dload_2 dload_3 aload_0 aload_1 aload_2 aload_3 iaload laload faload daload aaload baload "
       "caload saload istore lstore fstore dstore astore istore_0 istore_1 istore_2 istore_3 lstore_0 lstore_1 "
       "lstore_2 lstore_3 fstore_0 fstore_1 fstore_2 fstore_3 dstore_0 dstore_1 dstore_2 dstore_3 astore_0 "
       "astore_1 astore_2 astore_3 iastore lastore fastore dastore aastore bastore castore sastore pop pop2 dup "
       "dup_x1 dup_x2 dup2 dup2_x1 dup2_x2 swap iadd ladd fadd dadd isub lsub fsub dsub imul lmul fmul dmul idiv "
       "ldiv fdiv ddiv irem lrem frem drem ineg lneg fneg dneg ishl lshl ishr lshr iushr lushr iand land ior lor "
       "ixor lxor iinc i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s lcmp fcmpl fcmpg dcmpl dcmpg "
       "ifeq ifne iflt ifge ifgt ifle if_icmpeq if_icmpne if_icmplt if_icmpge if_icmpgt if_icmple if_acmpeq "
       "if_acmpne goto jsr ret tableswitch lookupswitch ireturn lreturn freturn dreturn areturn return getstatic "
       "putstatic getfield putfield invokevirtual invokespecial invokestatic invokeinterface invokedynamic new "
       "newarray anewarray arraylength athrow checkcast instanceof monitorenter monitorexit wide multianewarray "
       "ifnull ifnonnull goto_w jsr_w").split()
assert len(OPS) == 202
CPOPS = {18, 19, 20, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 189, 192, 193, 197}
LEN = {16: 2, 18: 2, 21: 2, 22: 2, 23: 2, 24: 2, 25: 2, 54: 2, 55: 2, 56: 2, 57: 2, 58: 2, 169: 2, 188: 2,
       17: 3, 19: 3, 20: 3, 132: 3, 178: 3, 179: 3, 180: 3, 181: 3, 182: 3, 183: 3, 184: 3, 187: 3, 189: 3,
       192: 3, 193: 3, 198: 3, 199: 3, 197: 4, 185: 5, 186: 5, 200: 5, 201: 5}
for o in range(153, 169): LEN[o] = 3


class R:
    def __init__(self, b, p=0): self.b, self.p = b, p
    def u1(self): v = self.b[self.p]; self.p += 1; return v
    def u2(self): v = struct.unpack_from('>H', self.b, self.p)[0]; self.p += 2; return v
    def u4(self): v = struct.unpack_from('>I', self.b, self.p)[0]; self.p += 4; return v
    def s4(self): v = struct.unpack_from('>i', self.b, self.p)[0]; self.p += 4; return v
    def u8(self): v = struct.unpack_from('>Q', self.b, self.p)[0]; self.p += 8; return v
    def utf(self): n = self.u2(); s = self.b[self.p:self.p + n]; self.p += n; return s.decode('latin1')


class CP:
    def __init__(self, r):
        n = r.u2(); self.e = [None] * n; i = 1
        while i < n:
            t = r.u1()
            if t == 1: self.e[i] = ('utf8', r.utf())
            elif t == 3: self.e[i] = ('int', r.u4())
            elif t == 4: self.e[i] = ('float', r.u4())
            elif t == 5: self.e[i] = ('long', r.u8()); i += 1
            elif t == 6: self.e[i] = ('double', r.u8()); i += 1
            elif t in (7, 8, 16, 19, 20): self.e[i] = ({7: 'class', 8: 'string', 16: 'mtype', 19: 'module', 20: 'package'}[t], r.u2())
            elif t in (9, 10, 11, 12): self.e[i] = ({9: 'field', 10: 'method', 11: 'imethod', 12: 'nat'}[t], r.u2(), r.u2())
            elif t == 15: self.e[i] = ('mhandle', r.u1(), r.u2())
            elif t in (17, 18): self.e[i] = ('dyn', r.u2(), r.u2())
            else: raise ValueError(f'cp tag {t}')
            i += 1
    def utf(self, i): return self.e[i][1]
    def cls(self, i): return self.utf(self.e[i][1]) if i else None
    def text(self, i):
        e = self.e[i]
        if e is None: return '<?>'
        t = e[0]
        if t == 'utf8': return e[1]
        if t in ('int', 'float', 'long', 'double'): return f'{t}:{e[1]:x}'
        if t in ('class', 'string', 'mtype', 'module', 'package'): return f'{t}:{self.utf(e[1])}'
        if t == 'nat': return f'{self.utf(e[1])}:{self.utf(e[2])}'
        if t in ('field', 'method', 'imethod'): return f'{t}:{self.cls(e[1])}.{self.text(e[2])}'
        return f'{t}:{e[1:]}'


def attrs(r, cp):
    out = []
    for _ in range(r.u2()):
        name = cp.utf(r.u2()); ln = r.u4(); out.append((name, r.b[r.p:r.p + ln])); r.p += ln
    return out


def cp_bytes(entries):
    """Serialize a CP entry list as parsed by CP (None = second half of long/double)."""
    out = bytearray()
    for e in entries[1:]:
        if e is None: continue
        t = e[0]
        if t == 'utf8': b = e[1].encode('latin1'); out += struct.pack('>BH', 1, len(b)) + b
        elif t in ('int', 'float'): out += struct.pack('>BI', 3 if t == 'int' else 4, e[1])
        elif t in ('long', 'double'): out += struct.pack('>BQ', 5 if t == 'long' else 6, e[1])
        elif t in ('class', 'string', 'mtype', 'module', 'package'):
            out += struct.pack('>BH', {'class': 7, 'string': 8, 'mtype': 16, 'module': 19, 'package': 20}[t], e[1])
        elif t in ('field', 'method', 'imethod', 'nat'):
            out += struct.pack('>BHH', {'field': 9, 'method': 10, 'imethod': 11, 'nat': 12}[t], e[1], e[2])
        elif t == 'mhandle': out += struct.pack('>BBH', 15, e[1], e[2])
        else: raise ValueError(f'cannot re-serialize CP entry {t}')
    return bytes(out)


def parse(b):
    r = R(b)
    assert r.u4() == 0xCAFEBABE
    minor = r.u2(); major = r.u2(); cp = CP(r)
    acc, this, sup = r.u2(), r.u2(), r.u2()
    iface_idx = [r.u2() for _ in range(r.u2())]
    # indices are kept next to the resolved names so a classfile can be re-serialized (donor_lvt.py)
    c = dict(minor=minor, major=major, acc=acc, name=cp.cls(this), super=cp.cls(sup), ifaces=[cp.cls(i) for i in iface_idx],
             cp=cp, this_idx=this, super_idx=sup, iface_idx=iface_idx)
    for kind in ('fields', 'methods'):
        items = {}
        for _ in range(r.u2()):
            f = r.u2(); ni = r.u2(); di = r.u2()
            items[(cp.utf(ni), cp.utf(di))] = dict(acc=f, ni=ni, di=di, attrs=attrs(r, cp))
        c[kind] = items
    c['attrs'] = attrs(r, cp)
    return c


def code(data, cp):
    r = R(data); ms, ml, cl = r.u2(), r.u2(), r.u4(); bc = data[8:8 + cl]; r.p = 8 + cl
    ex = []
    for _ in range(r.u2()):
        s, e, h, t = r.u2(), r.u2(), r.u2(), r.u2()
        ex.append((s, e, h, cp.cls(t) or 'any'))
    return ms, ml, bc, ex, attrs(r, cp)


def walk(bc):
    """(pc, opcode, length) for every instruction, including nops and switch padding."""
    i, n = 0, len(bc)
    while i < n:
        op = bc[i]
        if op == 196: ln = 6 if bc[i + 1] == 132 else 4
        elif op in (170, 171):
            p = (i + 4) & ~3
            if op == 170:
                lo, hi = struct.unpack_from('>ii', bc, p + 4); ln = p + 12 + 4 * (hi - lo + 1) - i
            else:
                ln = p + 8 + 8 * struct.unpack_from('>i', bc, p + 4)[0] - i
        else: ln = LEN.get(op, 1)
        yield i, op, ln
        i += ln


def norm(bc, cp):
    """Symbolic instruction list with branch targets as instruction indices (layout-independent);
    returns (instrs, nops, pc->index map)."""
    ins = list(walk(bc)); idx = {pc: k for k, (pc, _, _) in enumerate(ins)}; idx[len(bc)] = len(ins)
    tgt = lambda pc: f'#{idx[pc]}' if pc in idx else f'pc?{pc}'
    out, nops = [], 0
    for i, op, ln in ins:
        if op == 0: nops += 1; continue
        name = OPS[op] if op < 202 else f'op{op}'
        if op in (18, 19, 20):
            k = bc[i + 1] if op == 18 else struct.unpack_from('>H', bc, i + 1)[0]
            out.append(f'ldc {cp.text(k)}'); continue
        if op in CPOPS:
            k = struct.unpack_from('>H', bc, i + 1)[0]
            extra = '' if op not in (185, 197) else f' {bc[i + 3]}'
            out.append(f'{name} {cp.text(k)}{extra}'); continue
        if op == 196:
            out.append(f'wide {OPS[bc[i + 1]]} ' + bc[i + 2:i + ln].hex()); continue
        if op in (170, 171):
            p = (i + 4) & ~3; r = R(bc, p); d = r.s4()
            if op == 170:
                lo, hi = r.s4(), r.s4(); offs = [r.s4() for _ in range(hi - lo + 1)]
                out.append(f'tableswitch {tgt(i + d)} {lo} {hi} ' + ' '.join(tgt(i + o) for o in offs))
            else:
                cnt = r.s4(); pairs = [(r.s4(), r.s4()) for _ in range(cnt)]
                out.append(f'lookupswitch {tgt(i + d)} ' + ' '.join(f'{k}:{tgt(i + o)}' for k, o in pairs))
            continue
        if op in range(153, 169) or op in (198, 199):
            out.append(f'{name} {tgt(i + struct.unpack_from(">h", bc, i + 1)[0])}')
        elif op in (200, 201):
            out.append(f'{name} {tgt(i + struct.unpack_from(">i", bc, i + 1)[0])}')
        else:
            out.append(name + (' ' + bc[i + 1:i + ln].hex() if ln > 1 else ''))
    return out, nops, idx


def load(jar):
    out = {}
    with zipfile.ZipFile(jar) as z:
        for i in z.infolist():
            if i.filename.endswith('.class'):
                try: out[i.filename[:-6]] = parse(z.read(i))
                except Exception as e: out[i.filename[:-6]] = e
    return out


def main():
    verbose = int(sys.argv[sys.argv.index('-v') + 1]) if '-v' in sys.argv else 12
    args = [a for a in sys.argv[1:] if a not in ('-v', str(verbose))]
    A, B = load(args[0]), load(args[1])
    st = collections.Counter(); att = {k: collections.Counter() for k in ('class', 'field', 'method', 'code')}
    attB = {k: collections.Counter() for k in att}; majors = collections.Counter(); flagdiff = collections.Counter()
    diffs, firstdiff = [], collections.Counter(); unparsable = []; ex_examples = []; examples = collections.defaultdict(list)
    common = sorted(set(A) & set(B))
    st['only_orig'], st['only_rt'], st['classes'] = len(set(A) - set(B)), len(set(B) - set(A)), len(common)
    for name in common:
        a, b = A[name], B[name]
        if isinstance(a, Exception) or isinstance(b, Exception):
            unparsable.append((name, a if isinstance(a, Exception) else b)); continue
        majors[(a['major'], b['major'])] += 1
        if a['acc'] != b['acc']: st['class_flags'] += 1; _bits(flagdiff, 'class', a['acc'], b['acc'])
        if a['super'] != b['super']: st['super'] += 1; examples['super'].append((name, a['super'], b['super']))
        if a['ifaces'] != b['ifaces']: st['ifaces'] += 1
        for n_, _ in a['attrs']: att['class'][n_] += 1
        for n_, _ in b['attrs']: attB['class'][n_] += 1
        ca, cb = dict(a['attrs']), dict(b['attrs'])
        for n_ in ('InnerClasses', 'EnclosingMethod', 'Signature'):
            if (n_ in ca) != (n_ in cb):
                if len(examples['class_' + n_ + '_presence']) < 5:
                    examples['class_' + n_ + '_presence'].append((name, 'orig' if n_ in ca else 'rt', _sym(n_, ca.get(n_) or cb.get(n_), (a if n_ in ca else b)['cp'])))
            elif n_ in ca:
                va, vb = _sym(n_, ca[n_], a['cp']), _sym(n_, cb[n_], b['cp'])
                st[f'class_{n_}_same' if va == vb else f'class_{n_}_DIFF'] += 1
                if va != vb and len(examples['class_' + n_]) < 5: examples['class_' + n_].append((name, va, vb))
        for kind, lvl in (('fields', 'field'), ('methods', 'method')):
            ka, kb = set(a[kind]), set(b[kind])
            st[f'{lvl}_only_orig'] += len(ka - kb); st[f'{lvl}_only_rt'] += len(kb - ka)
            for m in ka & kb:
                ma, mb = a[kind][m], b[kind][m]
                st[lvl] += 1
                if ma['acc'] != mb['acc']: st[f'{lvl}_flags'] += 1; _bits(flagdiff, lvl, ma['acc'], mb['acc'])
                da, db = dict(ma['attrs']), dict(mb['attrs'])
                for n_ in da: att[lvl][n_] += 1
                for n_ in db: attB[lvl][n_] += 1
                for n_ in ('Exceptions', 'ConstantValue', 'Signature'):
                    if n_ in da and n_ in db:
                        va = _sym(n_, da[n_], a['cp']); vb = _sym(n_, db[n_], b['cp'])
                        st[f'{n_}_same' if va == vb else f'{n_}_DIFF'] += 1
                        if va != vb and len(examples[n_]) < 5: examples[n_].append((name, m[0], va, vb))
                for n_ in ('Exceptions', 'Signature', 'ConstantValue', 'InnerClasses'):
                    if (n_ in da) != (n_ in db):
                        if n_ == 'ConstantValue' and n_ in da:
                            st['ConstantValue_lost_static' if ma['acc'] & 8 else 'ConstantValue_lost_instance'] += 1
                        if len(examples[n_ + '_presence']) < 5:
                            examples[n_ + '_presence'].append((name, m[0] + m[1], 'orig' if n_ in da else 'rt', _sym(n_, da.get(n_) or db.get(n_), (a if n_ in da else b)['cp'])))
                if lvl == 'method' and 'Code' in da and 'Code' in db:
                    sa, la, bca, exa, ata = code(da['Code'], a['cp']); sb, lb, bcb, exb, atb = code(db['Code'], b['cp'])
                    for n_, _ in ata: att['code'][n_] += 1
                    for n_, _ in atb: attB['code'][n_] += 1
                    st['code'] += 1
                    if sa != sb: st['max_stack_diff'] += 1
                    if la != lb: st['max_locals_diff'] += 1
                    ia, na, xa = norm(bca, a['cp']); ib, nb, xb = norm(bcb, b['cp'])
                    exa_ = [(xa.get(s, f'pc?{s}'), xa.get(e, f'pc?{e}'), xa.get(h, f'pc?{h}'), t) for s, e, h, t in exa]
                    exb_ = [(xb.get(s, f'pc?{s}'), xb.get(e, f'pc?{e}'), xb.get(h, f'pc?{h}'), t) for s, e, h, t in exb]
                    if exa_ != exb_:
                        st['exc_table_diff'] += 1
                        if len(ex_examples) < 4: ex_examples.append((name, m[0] + m[1], exa_, exb_))
                    st['nops_orig'] += na; st['nops_rt'] += nb
                    if ia == ib: st['bytecode_same'] += 1
                    else:
                        st['bytecode_DIFF'] += 1
                        k = next((j for j, (p, q) in enumerate(zip(ia, ib)) if p != q), min(len(ia), len(ib)))
                        pa = ia[k] if k < len(ia) else '<end>'; pb = ib[k] if k < len(ib) else '<end>'
                        firstdiff[(pa.split(' ')[0], pb.split(' ')[0])] += 1
                        diffs.append((name, m[0] + m[1], k, pa, pb, len(ia), len(ib)))
                elif lvl == 'method' and ('Code' in da) != ('Code' in db):
                    st['code_presence_diff'] += 1
    # ---- report
    print(f"classes common={st['classes']} only_orig={st['only_orig']} only_rt={st['only_rt']} unparsable={len(unparsable)}")
    for n_, e in unparsable[:5]: print(f'  unparsable {n_}: {e!r}')
    print('majors orig->rt:', ', '.join(f'{a}->{b}: {c}' for (a, b), c in sorted(majors.items())))
    print(f"class flags diff={st['class_flags']} super diff={st['super']} ifaces diff={st['ifaces']}")
    print(f"fields common={st['field']} only_orig={st['field_only_orig']} only_rt={st['field_only_rt']} flags diff={st['field_flags']}")
    print(f"methods common={st['method']} only_orig={st['method_only_orig']} only_rt={st['method_only_rt']} flags diff={st['method_flags']} code presence diff={st['code_presence_diff']}")
    for (lvl, x, side), c in sorted(flagdiff.items(), key=lambda kv: -kv[1])[:10]: print(f'  flag {lvl} 0x{x:04x} only in {side}: {c}')
    for k, v in examples.items():
        print(f'examples {k}:'); [print('   ', *map(str, e)) for e in v[:5]]
    for name, m, ea, eb in ex_examples: print(f'exc table {name}.{m}: {ea} vs {eb}')
    print(f"bytecode methods={st['code']} same={st['bytecode_same']} DIFF={st['bytecode_DIFF']} | max_stack diff={st['max_stack_diff']} max_locals diff={st['max_locals_diff']} exc_table diff={st['exc_table_diff']} | nops orig={st['nops_orig']} rt={st['nops_rt']}")
    if st['ConstantValue_lost_static'] or st['ConstantValue_lost_instance']:
        print(f"  ConstantValue lost: static={st['ConstantValue_lost_static']} instance={st['ConstantValue_lost_instance']}")
    for k in ('Exceptions', 'ConstantValue', 'Signature', 'class_InnerClasses', 'class_EnclosingMethod', 'class_Signature'):
        if st[f'{k}_same'] or st[f'{k}_DIFF']: print(f"  {k} content: same={st[f'{k}_same']} DIFF={st[f'{k}_DIFF']}")
    print('attributes orig -> rt:')
    for lvl in att:
        names = sorted(set(att[lvl]) | set(attB[lvl]))
        for n_ in names:
            print(f'  {lvl:6} {n_:28} {att[lvl][n_]:7} -> {attB[lvl][n_]:7}')
    if firstdiff:
        print('first-diff opcode pairs (orig vs rt):')
        for (p, q), c in firstdiff.most_common(10): print(f'  {p} vs {q}: {c}')
        print(f'sample diffs ({min(verbose, len(diffs))} of {len(diffs)}):')
        for name, m, k, pa, pb, la, lb in diffs[:verbose]: print(f'  {name}.{m} @{k}: {pa!r} vs {pb!r} (len {la}/{lb})')
    if '--json' in sys.argv:
        json.dump(dict(st), open(sys.argv[sys.argv.index('--json') + 1], 'w'))


def _bits(counter, lvl, x, y):
    for b in range(16):
        bit = 1 << b
        if (x ^ y) & bit: counter[(lvl, bit, 'orig' if x & bit else 'rt')] += 1


def _sym(kind, data, cp):
    r = R(data)
    if kind == 'Exceptions': return tuple(cp.cls(r.u2()) for _ in range(r.u2()))
    if kind == 'Signature': return cp.utf(r.u2())
    if kind == 'ConstantValue': return cp.text(r.u2())
    if kind == 'InnerClasses':
        out = []
        for _ in range(r.u2()):
            inner, outer, simple, flags = r.u2(), r.u2(), r.u2(), r.u2()
            out.append((cp.cls(inner), cp.cls(outer), cp.utf(simple) if simple else None, flags))
        return tuple(sorted(out, key=str))
    if kind == 'EnclosingMethod':
        c, m = r.u2(), r.u2()
        return (cp.cls(c), cp.text(m) if m else None)


if __name__ == '__main__':
    main()
