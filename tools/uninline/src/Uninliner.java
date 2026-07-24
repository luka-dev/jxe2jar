/*
 * ASM constant un-inliner (Layers 1-3) - all constant types, tiered resolution.
 *
 * javac inlines `static final` constants at the use site (drops NAME, keeps VALUE).
 * We recover the name and rewrite the literal-load into `getstatic Owner.FIELD:desc`,
 * so a re-decompile shows the real symbolic reference (no regex/text matching).
 *
 * Resolution is tiered; first tier that yields exactly ONE candidate wins, and the
 * reason is auditable (never a fuzzy score):
 *   T1 closure-unique   - value unique among accessible constants in the use-site
 *                         class's inheritance closure (matches Java simple-name res).
 *   T3 owner co-ref     - the class already references some Owner.X via a surviving
 *                         getstatic, and the value uniquely matches an Owner constant.
 *   T2 global distinct  - value is owned by exactly one PUBLIC constant in the whole
 *                         jar AND passes a strict distinctiveness gate (catches FQN /
 *                         static-import refs the closure misses).
 *
 * Types: int/short/byte/char/boolean (I/S/B/C/Z, all int-category on stack), long(J),
 * float(F), double(D), String. Match is category-exact so the getstatic has identical
 * stack behaviour. T2/T3 only target PUBLIC fields in PUBLIC classes (legal getstatic
 * from anywhere). Value-preserving for READING; decompile aid, not runnable bytecode.
 *
 * Usage: java -cp asm-9.7.jar:asm-tree-9.7.jar:. Uninliner <in.jar> <out.jar> [floor]
 */
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;

public class Uninliner {

    static final class FConst { final String name, desc; final Object val; final boolean pub;
        FConst(String n, String d, Object v, boolean p){name=n;desc=d;val=v;pub=p;} }
    static final class CInfo { String sup; String[] ifaces = new String[0]; boolean pub;
        final List<FConst> consts = new ArrayList<>(); }
    static final class Ref { final String owner, name, desc; Ref(String o,String n,String d){owner=o;name=n;desc=d;} }

    static final Map<String, CInfo> index = new HashMap<>();
    // constant-key -> Ref, for PUBLIC constants in PUBLIC classes:
    static final Map<String, List<Ref>> globalPub = new HashMap<>();          // T2
    static final Map<String, Map<String, List<Ref>>> ownerPub = new HashMap<>(); // T3: owner -> key -> refs
    static final Set<String> constFieldSig = new HashSet<>();                 // "owner\0name\0desc"
    static int floor = 100;
    static final long[] stats = new long[4];   // T1, T3, T2, classes

    public static void main(String[] args) throws Exception {
        String inJar = args[0], outJar = args[1];
        if (args.length > 2) floor = Integer.parseInt(args[2]);

        try (ZipFile zf = new ZipFile(inJar)) {
            for (Enumeration<? extends ZipEntry> e = zf.entries(); e.hasMoreElements(); ) {
                ZipEntry ze = e.nextElement();
                if (ze.getName().endsWith(".class"))
                    try { scan(readAll(zf.getInputStream(ze))); } catch (Exception ig) {}
            }
        }
        buildGlobal();
        System.out.println("indexed " + index.size() + " classes; "
                + globalPub.size() + " public constant-keys");

        try (ZipFile zf = new ZipFile(inJar);
             ZipOutputStream zos = new ZipOutputStream(new BufferedOutputStream(new FileOutputStream(outJar)))) {
            for (Enumeration<? extends ZipEntry> e = zf.entries(); e.hasMoreElements(); ) {
                ZipEntry ze = e.nextElement();
                byte[] data = readAll(zf.getInputStream(ze));
                if (ze.getName().endsWith(".class"))
                    try { data = rewrite(data); } catch (Exception ig) {}
                zos.putNextEntry(new ZipEntry(ze.getName())); zos.write(data); zos.closeEntry();
            }
        }
        System.out.printf("uninlined: T1(closure)=%d  T3(co-ref)=%d  T2(global)=%d  across %d classes (floor %d)%n",
                stats[0], stats[1], stats[2], stats[3], floor);
    }

    static void scan(byte[] data) {
        ClassReader cr = new ClassReader(data);
        final CInfo ci = new CInfo();
        cr.accept(new ClassVisitor(Opcodes.ASM9) {
            public void visit(int v,int a,String n,String s,String sup,String[] ifs){
                ci.sup=sup; if(ifs!=null) ci.ifaces=ifs; ci.pub=(a & Opcodes.ACC_PUBLIC)!=0; }
            public FieldVisitor visitField(int acc,String fn,String d,String sig,Object val){
                if((acc&Opcodes.ACC_STATIC)!=0 && (acc&Opcodes.ACC_FINAL)!=0 && val!=null)
                    ci.consts.add(new FConst(fn,d,val,(acc&Opcodes.ACC_PUBLIC)!=0));
                return null; }
        }, ClassReader.SKIP_CODE|ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);
        index.put(cr.getClassName(), ci);
    }

    static void buildGlobal() {
        for (Map.Entry<String,CInfo> e : index.entrySet()) {
            String owner = e.getKey(); CInfo ci = e.getValue();
            for (FConst f : ci.consts) {
                constFieldSig.add(owner + "\0" + f.name + "\0" + f.desc);
                if (!ci.pub || !f.pub) continue;               // T2/T3 need legal getstatic from anywhere
                String key = constKey(f.desc, f.val);
                if (key == null) continue;
                Ref r = new Ref(owner, f.name, f.desc);
                globalPub.computeIfAbsent(key, k -> new ArrayList<>()).add(r);
                ownerPub.computeIfAbsent(owner, k -> new HashMap<>())
                        .computeIfAbsent(key, k -> new ArrayList<>()).add(r);
            }
        }
    }

    // ---- key encoding: identical for a constant field and for a literal-load instruction ----
    static String constKey(String desc, Object val) {
        switch (desc) {
            case "I": case "S": case "B": case "C": case "Z": return "i:" + ((Integer) val).intValue();
            case "J": return "j:" + ((Long) val).longValue();
            case "F": return "f:" + Float.floatToRawIntBits((Float) val);
            case "D": return "d:" + Double.doubleToRawLongBits((Double) val);
            case "Ljava/lang/String;": return "s:" + val;
            default: return null;
        }
    }

    static final class Lit { String key; char cat; long num; String str; }
    static Lit litOf(AbstractInsnNode in) {
        int op = in.getOpcode(); Lit L = new Lit();
        if (op >= Opcodes.ICONST_M1 && op <= Opcodes.ICONST_5) { L.cat='i'; L.num=op-Opcodes.ICONST_0; }
        else if (op==Opcodes.BIPUSH||op==Opcodes.SIPUSH) { L.cat='i'; L.num=((IntInsnNode)in).operand; }
        else if (op==Opcodes.LCONST_0||op==Opcodes.LCONST_1) { L.cat='j'; L.num=op-Opcodes.LCONST_0; }
        else if (op==Opcodes.FCONST_0||op==Opcodes.FCONST_1||op==Opcodes.FCONST_2) {
            L.cat='f'; L.num=Float.floatToRawIntBits((float)(op-Opcodes.FCONST_0)); }
        else if (op==Opcodes.DCONST_0||op==Opcodes.DCONST_1) {
            L.cat='d'; L.num=Double.doubleToRawLongBits((double)(op-Opcodes.DCONST_0)); }
        else if (op==Opcodes.LDC) {
            Object c=((LdcInsnNode)in).cst;
            if (c instanceof Integer){L.cat='i';L.num=(Integer)c;}
            else if (c instanceof Long){L.cat='j';L.num=(Long)c;}
            else if (c instanceof Float){L.cat='f';L.num=Float.floatToRawIntBits((Float)c);}
            else if (c instanceof Double){L.cat='d';L.num=Double.doubleToRawLongBits((Double)c);}
            else if (c instanceof String){L.cat='s';L.str=(String)c;}
            else return null;
        } else return null;
        L.key = L.cat==':' ? null : (L.cat=='s' ? "s:"+L.str : L.cat+":"+L.num);
        return L.key==null?null:L;
    }

    static boolean meaningful(String s){ if(s.length()<3) return false;
        for(int i=0;i<s.length();i++) if(Character.isUpperCase(s.charAt(i))) return true; return false; }

    /** True value carried by a literal, for gating (int/long as long; float/double via bits ignored here). */
    static Long numVal(Lit L){
        if(L.cat=='i'||L.cat=='j') return L.num;
        return null;   // float/double/string gated separately
    }

    // strict distinctiveness for T2 numeric (avoid genuine-literal false positives)
    static boolean distinctiveNum(long v){
        long a=Math.abs(v);
        if(a<4096) return false;
        if((a&(a-1))==0) return false;                 // power of two
        if(((a+1)&a)==0) return false;                 // 2^n - 1
        if(Long.bitCount(a)<=2) return false;          // sparse flag
        if(a%10==0) return false;                      // decimal-round
        if((a&0xFF)==0) return false;                  // byte-aligned
        int tz=Long.numberOfTrailingZeros(a); long m=a>>>tz;
        if(((m+1)&m)==0) return false;                 // shifted 2^n-1 mask
        return true;
    }
    static boolean distinctiveStr(String s){ String t=s.trim();
        if(t.length()<8) return false;
        boolean letter=false; for(int i=0;i<t.length();i++) if(Character.isLetter(t.charAt(i))){letter=true;break;}
        return letter; }

    static byte[] rewrite(byte[] data) {
        ClassReader cr = new ClassReader(data);
        String cn = cr.getClassName();
        ClassNode node = new ClassNode(); cr.accept(node, 0);

        // T1 closure map (accessible + meaningful + floor + closure-unique).
        Map<String, Ref> closure = closureMap(cn);

        // T3 evidence: public constant-bearing owners this class REFERENCES in any way
        // (supertype, field/method target, or a `new`/cast/instanceof type). "This class
        // talks to Owner X" makes X's constants a plausible family for X's literals here.
        Set<String> corefOwners = new HashSet<>();
        addOwner(corefOwners, node.superName, cn);
        for (String it : node.interfaces) addOwner(corefOwners, it, cn);
        for (MethodNode mn : node.methods) if (mn.instructions!=null)
            for (AbstractInsnNode in=mn.instructions.getFirst(); in!=null; in=in.getNext()) {
                if (in instanceof FieldInsnNode) addOwner(corefOwners, ((FieldInsnNode)in).owner, cn);
                else if (in instanceof MethodInsnNode) addOwner(corefOwners, ((MethodInsnNode)in).owner, cn);
                else if (in instanceof TypeInsnNode) addOwner(corefOwners, ((TypeInsnNode)in).desc, cn);
            }

        boolean touched=false;
        for (MethodNode mn : node.methods) {
            if (mn.instructions==null) continue;
            for (AbstractInsnNode in=mn.instructions.getFirst(); in!=null; ) {
                AbstractInsnNode next=in.getNext();
                Lit L=litOf(in);
                if (L!=null) {
                    Ref r=null; int tier=-1;
                    // T1 closure-unique (strongest: actual simple-name scope)
                    r=closure.get(L.key); if(r!=null) tier=0;
                    // T2 global-unique + distinctive (high-confidence cross-scope)
                    if(r==null){
                        List<Ref> g=globalPub.get(L.key);
                        if(g!=null && g.size()==1){
                            boolean ok = L.cat=='s' ? distinctiveStr(L.str)
                                       : (L.cat=='i'||L.cat=='j') ? distinctiveNum(L.num) : false;
                            Ref x=g.get(0);
                            if(ok && meaningful(x.name)){ r=x; tier=2; }
                        }
                    }
                    // T3a owner co-reference: value unique within a single referenced
                    // owner AND DISTINCTIVE. The distinctiveness gate is load-bearing:
                    // without it, non-distinctive values (1024=screen width, shared by
                    // 71 constants) get mislabeled just because the owner is referenced.
                    // Recovering non-distinctive cross-scope constants needs sink-domain
                    // dataflow (T3b, not done here) - co-reference alone is insufficient.
                    if(r==null && !corefOwners.isEmpty()){
                        boolean dist = L.cat=='s' ? distinctiveStr(L.str)
                                     : (L.cat=='i'||L.cat=='j') ? distinctiveNum(L.num) : false;
                        if(dist){
                            Ref cand=null; boolean amb=false;
                            for(String o: corefOwners){
                                Map<String,List<Ref>> m=ownerPub.get(o); if(m==null) continue;
                                List<Ref> ls=m.get(L.key); if(ls==null) continue;
                                for(Ref x: ls){
                                    if(!meaningful(x.name)) continue;
                                    if(cand==null) cand=x;
                                    else if(!(cand.owner.equals(x.owner)&&cand.name.equals(x.name))) amb=true;
                                }
                            }
                            if(cand!=null && !amb){ r=cand; tier=1; }
                        }
                    }
                    if(r!=null){
                        mn.instructions.set(in, new FieldInsnNode(Opcodes.GETSTATIC, r.owner, r.name, r.desc));
                        stats[tier]++; touched=true;
                    }
                }
                in=next;
            }
        }
        if(!touched) return data;
        stats[3]++;
        ClassWriter cw=new ClassWriter(0); node.accept(cw); return cw.toByteArray();
    }

    // T1: value unique among accessible (self|public) meaningful constants in cn's closure, past floor.
    static Map<String, Ref> closureMap(String cn) {
        Map<String, Set<Ref>> buck = new HashMap<>();
        Set<String> seen=new HashSet<>(); Deque<String> st=new ArrayDeque<>(); st.push(cn);
        while(!st.isEmpty()){
            String c=st.pop(); if(c==null||!seen.add(c)) continue;
            CInfo ci=index.get(c); if(ci==null) continue; boolean self=c.equals(cn);
            for(FConst f: ci.consts){
                if(!(self||f.pub)||!meaningful(f.name)) continue;
                String key=constKey(f.desc,f.val); if(key==null) continue;
                if((key.startsWith("i:")||key.startsWith("j:"))){
                    long v=Long.parseLong(key.substring(2)); if(Math.abs(v)<floor) continue;
                }else if(key.startsWith("f:")){ float v=Float.intBitsToFloat((int)Long.parseLong(key.substring(2)));
                    if(v==0f||v==1f||v==-1f||v==2f) continue;
                }else if(key.startsWith("d:")){ double v=Double.longBitsToDouble(Long.parseLong(key.substring(2)));
                    if(v==0d||v==1d||v==-1d) continue;
                }else if(key.startsWith("s:")){ if(key.length()-2<2) continue; }
                buck.computeIfAbsent(key,k->new HashSet<>()).add(new Ref(c,f.name,f.desc));
            }
            if(ci.sup!=null) st.push(ci.sup); for(String it: ci.ifaces) st.push(it);
        }
        Map<String,Ref> out=new HashMap<>();
        for(Map.Entry<String,Set<Ref>> e: buck.entrySet()) if(e.getValue().size()==1) out.put(e.getKey(), e.getValue().iterator().next());
        return out;
    }

    /** Record a referenced type as a co-ref family owner if it's an indexed PUBLIC class. */
    static void addOwner(Set<String> set, String o, String self) {
        if (o == null || o.equals(self) || o.startsWith("[")) return;
        CInfo ci = index.get(o);
        if (ci != null && ci.pub) set.add(o);
    }

    static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] buf=new byte[8192];
        for(int n; (n=in.read(buf))!=-1; ) b.write(buf,0,n); return b.toByteArray();
    }
}
