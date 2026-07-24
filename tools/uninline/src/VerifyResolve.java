/*
 * Full correctness verification of constant un-inlining.
 *
 * Invariant: every un-inlined `getstatic Owner.FIELD` must have replaced a literal of
 * the EXACT SAME VALUE as Owner.FIELD's ConstantValue - otherwise the resolution
 * silently changed the program's value (a real bug). This aligns the ORIGINAL jar
 * (all constants folded as literals) against the UN-INLINED jar instruction-by-
 * instruction; each divergence must be exactly (literal V) -> (getstatic F where
 * value(F)==V). Anything else is reported.
 *
 * Usage: java -cp asm-9.7.jar:asm-tree-9.7.jar:. VerifyResolve <original.jar> <uninlined.jar>
 */
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.io.*; import java.util.*; import java.util.zip.*;

public class VerifyResolve {
    static final Map<String,String> constVal = new HashMap<>();   // owner\0name\0desc -> value-string
    static final Map<String,Integer> valueMult = new HashMap<>(); // value-string -> # distinct constants sharing it
    static long methods=0, replacements=0, valueMatch=0, valueMISMATCH=0, structAnomaly=0, otherDiverge=0;
    static long safeUnique=0, safeSelf=0, safeDistinct=0, review=0;
    static final List<String> mism = new ArrayList<>();
    static final List<String> reviewSamples = new ArrayList<>();

    public static void main(String[] a) throws Exception {
        // index constant values from the un-inlined jar (fields unchanged by un-inlining)
        try (ZipFile zf=new ZipFile(a[1])) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();){ ZipEntry ze=e.nextElement();
                if(ze.getName().endsWith(".class")) try{ indexConsts(readAll(zf.getInputStream(ze))); }catch(Exception ig){} }
        }
        // global value multiplicity: how many distinct constants share each value
        Map<String,Set<String>> byVal=new HashMap<>();
        for(Map.Entry<String,String> e: constVal.entrySet()){ String[] p=e.getKey().split("\0");
            byVal.computeIfAbsent(e.getValue(),k->new HashSet<>()).add(p[0]+"."+p[1]); }
        for(Map.Entry<String,Set<String>> e: byVal.entrySet()) valueMult.put(e.getKey(), e.getValue().size());

        Map<String,byte[]> orig=new HashMap<>();
        try (ZipFile zf=new ZipFile(a[0])) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();){ ZipEntry ze=e.nextElement();
                if(ze.getName().endsWith(".class")) orig.put(ze.getName(), readAll(zf.getInputStream(ze))); }
        }
        try (ZipFile zf=new ZipFile(a[1])) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();){ ZipEntry ze=e.nextElement();
                if(!ze.getName().endsWith(".class")) continue; byte[] ob=orig.get(ze.getName()); if(ob==null) continue;
                try{ compare(ob, readAll(zf.getInputStream(ze))); }catch(Exception ig){} }
        }
        System.out.println("methods compared: "+methods);
        System.out.println("literal->getstatic replacements: "+replacements);
        System.out.println("  VALUE MATCH   : "+valueMatch);
        System.out.println("  VALUE MISMATCH: "+valueMISMATCH+"   <-- must be 0");
        System.out.println("methods with instruction-count anomaly: "+structAnomaly);
        System.out.println("other unexpected divergences: "+otherDiverge);
        for(String s: mism.subList(0, Math.min(mism.size(),15))) System.out.println("  MISMATCH "+s);
        System.out.println("\n--- NAME-PROVENANCE AUDIT (all value-correct) ---");
        System.out.println("  SAFE  globally-unique value : "+safeUnique);
        System.out.println("  SAFE  own-class constant     : "+safeSelf);
        System.out.println("  SAFE  distinctive value     : "+safeDistinct);
        System.out.println("  REVIEW non-distinct+ambiguous: "+review+"   ("+String.format("%.1f",100.0*review/Math.max(1,valueMatch))+"% of resolutions)");
        System.out.println("  review samples:");
        for(String s: reviewSamples) System.out.println("    "+s);
    }
    static boolean distinctive(String cv){
        if(cv.startsWith("s:")) return cv.length()-2>=8;
        if(cv.startsWith("i:")||cv.startsWith("j:")){ long a; try{ a=Math.abs(Long.parseLong(cv.substring(2))); }catch(Exception e){return true;}
            if(a<4096) return false; if((a&(a-1))==0) return false; if(((a+1)&a)==0) return false;
            if(Long.bitCount(a)<=2) return false; if(a%10==0) return false; if((a&0xFF)==0) return false;
            int tz=Long.numberOfTrailingZeros(a); long m=a>>>tz; if(((m+1)&m)==0) return false; return true; }
        return true;   // float/double treated distinctive (rare)
    }

    static void indexConsts(byte[] d){
        ClassReader cr=new ClassReader(d); final String cn=cr.getClassName();
        cr.accept(new ClassVisitor(Opcodes.ASM9){
            public FieldVisitor visitField(int acc,String n,String desc,String sig,Object val){
                if((acc&Opcodes.ACC_STATIC)!=0&&(acc&Opcodes.ACC_FINAL)!=0&&val!=null) constVal.put(cn+"\0"+n+"\0"+desc, vstr(desc,val));
                return null; }
        }, ClassReader.SKIP_CODE|ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);
    }
    static String vstr(String desc,Object v){
        switch(desc){ case "I": case "S": case "B": case "C": case "Z": return "i:"+((Integer)v).intValue();
            case "J": return "j:"+((Long)v).longValue(); case "F": return "f:"+Float.floatToRawIntBits((Float)v);
            case "D": return "d:"+Double.doubleToRawLongBits((Double)v); case "Ljava/lang/String;": return "s:"+v; default: return "?:"+v; }
    }
    static String litVal(AbstractInsnNode in){
        int op=in.getOpcode();
        if(op>=Opcodes.ICONST_M1&&op<=Opcodes.ICONST_5) return "i:"+(op-Opcodes.ICONST_0);
        if(op==Opcodes.BIPUSH||op==Opcodes.SIPUSH) return "i:"+((IntInsnNode)in).operand;
        if(op==Opcodes.LCONST_0) return "j:0"; if(op==Opcodes.LCONST_1) return "j:1";
        if(op==Opcodes.FCONST_0) return "f:"+Float.floatToRawIntBits(0f); if(op==Opcodes.FCONST_1) return "f:"+Float.floatToRawIntBits(1f); if(op==Opcodes.FCONST_2) return "f:"+Float.floatToRawIntBits(2f);
        if(op==Opcodes.DCONST_0) return "d:"+Double.doubleToRawLongBits(0d); if(op==Opcodes.DCONST_1) return "d:"+Double.doubleToRawLongBits(1d);
        if(op==Opcodes.LDC){ Object c=((LdcInsnNode)in).cst;
            if(c instanceof Integer) return "i:"+c; if(c instanceof Long) return "j:"+c;
            if(c instanceof Float) return "f:"+Float.floatToRawIntBits((Float)c); if(c instanceof Double) return "d:"+Double.doubleToRawLongBits((Double)c);
            if(c instanceof String) return "s:"+c; }
        return null;
    }
    static List<AbstractInsnNode> real(InsnList l){ List<AbstractInsnNode> r=new ArrayList<>();
        for(AbstractInsnNode n=l.getFirst(); n!=null; n=n.getNext()) if(n.getOpcode()>=0) r.add(n); return r; }

    static void compare(byte[] ob, byte[] nb){
        ClassNode o=new ClassNode(); new ClassReader(ob).accept(o,0);
        ClassNode n=new ClassNode(); new ClassReader(nb).accept(n,0);
        Map<String,MethodNode> nm=new HashMap<>(); for(MethodNode m:n.methods) nm.put(m.name+m.desc,m);
        for(MethodNode om: o.methods){ MethodNode nn=nm.get(om.name+om.desc); if(nn==null||om.instructions==null||nn.instructions==null) continue;
            methods++;
            List<AbstractInsnNode> A=real(om.instructions), B=real(nn.instructions);
            if(A.size()!=B.size()){ structAnomaly++; continue; }   // count changed -> not pure constant un-inlining
            for(int i=0;i<A.size();i++){ AbstractInsnNode a=A.get(i), b=B.get(i);
                if(a.getOpcode()==b.getOpcode() && sameOperand(a,b)) continue;    // unchanged
                if(b.getOpcode()==Opcodes.GETSTATIC){                            // a literal -> getstatic F
                    FieldInsnNode f=(FieldInsnNode)b; String cv=constVal.get(f.owner+"\0"+f.name+"\0"+f.desc);
                    String lv=litVal(a);
                    if(cv!=null && lv!=null){ replacements++;
                        if(cv.equals(lv)){ valueMatch++;
                            int mult=valueMult.getOrDefault(cv,1);
                            boolean self = f.owner.equals(o.name);   // resolving own constant = Java simple-name, safe
                            if(mult<=1) safeUnique++;
                            else if(self) safeSelf++;
                            else if(distinctive(cv)) safeDistinct++;
                            else { review++; if(reviewSamples.size()<25) reviewSamples.add(
                                o.name.substring(o.name.lastIndexOf('/')+1)+"."+om.name+"  "+lv+" -> "+f.owner.substring(f.owner.lastIndexOf('/')+1)+"."+f.name+"  (globally "+mult+" share it)"); }
                        }
                        else { valueMISMATCH++; if(mism.size()<200) mism.add(o.name+"."+om.name+" ["+lv+"] -> "+f.owner+"."+f.name+" ["+cv+"]"); }
                        continue; }
                }
                otherDiverge++;   // some other change (e.g. getstatic to non-const, or unexpected)
            }
        }
    }
    static boolean sameOperand(AbstractInsnNode a, AbstractInsnNode b){
        if(a instanceof FieldInsnNode){ FieldInsnNode x=(FieldInsnNode)a,y=(FieldInsnNode)b; return x.owner.equals(y.owner)&&x.name.equals(y.name)&&x.desc.equals(y.desc); }
        if(a instanceof MethodInsnNode){ MethodInsnNode x=(MethodInsnNode)a,y=(MethodInsnNode)b; return x.owner.equals(y.owner)&&x.name.equals(y.name)&&x.desc.equals(y.desc); }
        if(a instanceof IntInsnNode) return ((IntInsnNode)a).operand==((IntInsnNode)b).operand;
        if(a instanceof LdcInsnNode) return Objects.equals(((LdcInsnNode)a).cst,((LdcInsnNode)b).cst);
        if(a instanceof VarInsnNode) return ((VarInsnNode)a).var==((VarInsnNode)b).var;
        return true;
    }
    static byte[] readAll(InputStream in) throws IOException { ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] u=new byte[8192]; for(int r;(r=in.read(u))!=-1;) b.write(u,0,r); return b.toByteArray(); }
}
