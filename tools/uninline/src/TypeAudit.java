/*
 * Correctness audit for J9 ROM -> classfile type ambiguities (the silent-bug class).
 *
 * J9 stores int/float in one CP slot (handled via stack-sim) - and ALSO long/double in
 * one 8-byte slot. The converter defaults every non-ref 8-byte constant to DOUBLE, so a
 * genuine `long` constant can be emitted as a `double` (wrong value/type). This audits
 * for that and neighbours:
 *   [A] field ConstantValue type vs field descriptor  (J/D, I/F, ...) - decisive
 *   [B] ldc2_w of a Double constant consumed by a LONG opcode (or vice versa)
 *   [C] jsr/jsr_w/ret presence (old finally subroutines -> decompiler-quality risk)
 *   [D] Modified-UTF-8 edge strings (embedded NUL / lone surrogate / non-BMP)
 *
 * Usage: java -cp asm-9.7.jar:asm-tree-9.7.jar:asm-analysis-9.7.jar:. TypeAudit <jar>
 */
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import org.objectweb.asm.tree.analysis.*;
import java.io.*; import java.util.*; import java.util.zip.*;

public class TypeAudit {
    static long fieldMismatch=0, ldc2Mismatch=0, jsrMethods=0, utf8Edge=0, classes=0, methods=0;
    static final List<String> fm=new ArrayList<>(), lm=new ArrayList<>(), um=new ArrayList<>();

    public static void main(String[] a) throws Exception {
        try (ZipFile zf=new ZipFile(a[0])) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();){ ZipEntry ze=e.nextElement();
                if(ze.getName().endsWith(".class")) try{ audit(readAll(zf.getInputStream(ze))); }catch(Exception ig){} }
        }
        System.out.println("classes="+classes+" methods="+methods);
        System.out.println("[A] field ConstantValue type != descriptor: "+fieldMismatch+"   <-- silent wrong constant");
        for(String s: fm.subList(0,Math.min(fm.size(),20))) System.out.println("     "+s);
        System.out.println("[B] ldc2_w double-constant consumed as long (or vice versa): "+ldc2Mismatch);
        for(String s: lm.subList(0,Math.min(lm.size(),20))) System.out.println("     "+s);
        System.out.println("[C] methods with jsr/jsr_w/ret (finally-subroutine): "+jsrMethods);
        System.out.println("[D] strings with modified-UTF-8 edge (NUL/surrogate/non-BMP): "+utf8Edge);
        for(String s: um.subList(0,Math.min(um.size(),10))) System.out.println("     "+s);
    }

    static void audit(byte[] data){
        ClassNode n=new ClassNode(); new ClassReader(data).accept(n,0); classes++;
        // [A] field ConstantValue vs descriptor
        for(FieldNode f: n.fields){ if(f.value==null) continue; String exp=null;
            switch(f.desc){ case "J": exp="Long"; break; case "D": exp="Double"; break;
                case "F": exp="Float"; break; case "I": case "S": case "B": case "C": case "Z": exp="Integer"; break; default: continue; }
            String got=f.value.getClass().getSimpleName();
            if(!got.equals(exp)){ fieldMismatch++;
                if(fm.size()<200) fm.add(n.name+"."+f.name+":"+f.desc+"  ConstantValue="+got+"("+f.value+")  expected "+exp); }
        }
        for(MethodNode m: n.methods){ if(m.instructions==null) continue; methods++;
            boolean jsr=false;
            for(AbstractInsnNode in=m.instructions.getFirst(); in!=null; in=in.getNext()){
                int op=in.getOpcode();
                if(op==Opcodes.JSR||op==Opcodes.RET) jsr=true;
                // [D] modified-UTF-8 edge chars in String ldc constants
                if(op==Opcodes.LDC && ((LdcInsnNode)in).cst instanceof String){ String s=(String)((LdcInsnNode)in).cst;
                    for(int k=0;k<s.length();k++){ char ch=s.charAt(k);
                        if(ch=='\0' || Character.isSurrogate(ch)){ utf8Edge++;
                            if(um.size()<50) um.add(n.name+"."+m.name+": string edge U+"+Integer.toHexString(ch)); break; } }
                }
            }
            if(jsr) jsrMethods++;
            checkLdc2(n.name, m);   // [B]
        }
    }

    // consumer check: for each LDC of a Double, is the value popped by a long-typed op?
    static void checkLdc2(String cn, MethodNode m){
        Frame<SourceValue>[] fr; try{ fr=new Analyzer<>(new SourceInterpreter()).analyze(cn,m);}catch(Throwable t){return;}
        AbstractInsnNode[] arr=m.instructions.toArray();
        for(int i=0;i<arr.length;i++){ AbstractInsnNode in=arr[i];
            // find ops that consume a category-2 value and are LONG-typed
            int op=in.getOpcode(); if(op<0) continue;
            boolean longOp = op==Opcodes.LSTORE||op==Opcodes.LADD||op==Opcodes.LSUB||op==Opcodes.LMUL||op==Opcodes.LDIV
                ||op==Opcodes.LREM||op==Opcodes.LAND||op==Opcodes.LOR||op==Opcodes.LXOR||op==Opcodes.LCMP||op==Opcodes.LRETURN
                ||op==Opcodes.L2I||op==Opcodes.L2F||op==Opcodes.L2D||op==Opcodes.LSHL||op==Opcodes.LSHR||op==Opcodes.LUSHR;
            if(!longOp) continue;
            Frame<SourceValue> f=fr[i]; if(f==null||f.getStackSize()<1) continue;
            // the (a) long op's top operand producers
            SourceValue top; try{ top=f.getStack(f.getStackSize()-1);}catch(Exception e){continue;}
            for(AbstractInsnNode p: top.insns){
                if(p.getOpcode()==Opcodes.LDC && ((LdcInsnNode)p).cst instanceof Double){ ldc2Mismatch++;
                    if(lm.size()<200) lm.add(cn+"."+m.name+"  double-const "+((LdcInsnNode)p).cst+" used by long op "+op); break; }
            }
        }
    }

    static byte[] readAll(InputStream in) throws IOException { ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] u=new byte[8192]; for(int r;(r=in.read(u))!=-1;) b.write(u,0,r); return b.toByteArray(); }
}
