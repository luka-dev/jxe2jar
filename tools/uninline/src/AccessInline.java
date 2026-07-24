/*
 * #4 Synthetic accessor inlining (RELIABLE - reads the real body, no guessing).
 *
 * Java 1.2/1.4 nested classes reach a sibling's private members through synthetic
 * `access$NNN` bridge methods. The J9-converted classes KEEP these methods (they are
 * ACC_SYNTHETIC), but Vineflower leaves ~6k calls un-inlined. Since the accessor body
 * IS present, we inline deterministically: an accessor is a single field or method op
 * wrapped in loads/return, so at every `invokestatic Owner.access$N(...)` we splice in
 * that exact op. A re-decompile then shows `x.field` / `x.method()`.
 *
 * Handled (stack-preserving 1:1 rewrites): field getter (GETFIELD/GETSTATIC), void
 * field setter (PUTFIELD/PUTSTATIC), method bridge (INVOKEVIRTUAL/SPECIAL/INTERFACE/
 * STATIC). Refused (left as-is): value-returning setters and multi-op bodies - never
 * guess, never change stack shape.
 *
 * Usage: java -cp asm-9.7.jar:asm-tree-9.7.jar:. AccessInline <in.jar> <out.jar>
 */
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.io.*; import java.util.*; import java.util.regex.*; import java.util.zip.*;

public class AccessInline {
    static final Pattern A = Pattern.compile("access\\$\\d+");
    // owner\0name\0desc -> the single member op to splice in (a fresh node factory)
    static final Map<String, AbstractInsnNode> body = new HashMap<>();
    static final Map<String, Boolean> valueReturningSetter = new HashMap<>();
    static long inlined=0, classes=0, refused=0;

    public static void main(String[] a) throws Exception {
        List<byte[]> all=new ArrayList<>();
        try (ZipFile zf=new ZipFile(a[0])) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();) {
                ZipEntry ze=e.nextElement(); if(!ze.getName().endsWith(".class")) continue;
                all.add(readAll(zf.getInputStream(ze)));
            }
        }
        for (byte[] d: all) try { decode(d); } catch(Exception ig){}
        System.out.println("decoded " + body.size() + " inlinable accessors");

        try (ZipFile zf=new ZipFile(a[0]);
             ZipOutputStream zos=new ZipOutputStream(new BufferedOutputStream(new FileOutputStream(a[1])))) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();) {
                ZipEntry ze=e.nextElement(); byte[] d=readAll(zf.getInputStream(ze));
                if (ze.getName().endsWith(".class")) try { d=rewrite(d); } catch(Exception ig){}
                zos.putNextEntry(new ZipEntry(ze.getName())); zos.write(d); zos.closeEntry();
            }
        }
        System.out.printf("inlined %d accessor calls across %d classes (refused %d ambiguous bodies)%n",
                inlined, classes, refused);
    }

    static void decode(byte[] data){
        ClassNode n=new ClassNode(); new ClassReader(data).accept(n,0);
        for(MethodNode m: n.methods){
            if((m.access&Opcodes.ACC_STATIC)==0 || !A.matcher(m.name).matches() || m.instructions==null) continue;
            AbstractInsnNode member=null; int members=0; boolean bad=false;
            for(AbstractInsnNode in=m.instructions.getFirst(); in!=null; in=in.getNext()){
                if(in instanceof LabelNode||in instanceof LineNumberNode||in instanceof FrameNode) continue;
                int op=in.getOpcode();
                if(op>=Opcodes.GETSTATIC && op<=Opcodes.INVOKEINTERFACE){ member=in; members++; }  // field/invoke ops 178..185
                else if(in instanceof VarInsnNode || (op>=Opcodes.IRETURN&&op<=Opcodes.RETURN) || op==Opcodes.NOP
                        || op==Opcodes.INVOKEDYNAMIC || op==Opcodes.DUP || op==Opcodes.DUP_X1) { /* loads/returns/dup ok */ }
                else { bad=true; break; }
            }
            if(bad || members!=1 || member==null){ if(member==null&&members!=1) refused++; continue; }
            // STACK-SAFETY (Codex): the member op must pop exactly as many values as the
            // accessor takes, and push iff the accessor returns a value. Otherwise splicing
            // it in corrupts the caller's stack. Refuse any mismatch - never guess.
            boolean nonVoid = !Type.getReturnType(m.desc).getDescriptor().equals("V");
            int accArgs = Type.getArgumentTypes(m.desc).length;
            int mop=member.getOpcode(); int pops; boolean pushes;
            switch(mop){
                case Opcodes.GETFIELD:  pops=1; pushes=true;  break;
                case Opcodes.GETSTATIC: pops=0; pushes=true;  break;
                case Opcodes.PUTFIELD:  pops=2; pushes=false; break;
                case Opcodes.PUTSTATIC: pops=1; pushes=false; break;
                case Opcodes.INVOKESTATIC: pops=Type.getArgumentTypes(((MethodInsnNode)member).desc).length; pushes=!Type.getReturnType(((MethodInsnNode)member).desc).getDescriptor().equals("V"); break;
                case Opcodes.INVOKEVIRTUAL: case Opcodes.INVOKESPECIAL: case Opcodes.INVOKEINTERFACE:
                    pops=1+Type.getArgumentTypes(((MethodInsnNode)member).desc).length; pushes=!Type.getReturnType(((MethodInsnNode)member).desc).getDescriptor().equals("V"); break;
                default: refused++; continue;
            }
            if(pops!=accArgs || pushes!=nonVoid){ refused++; continue; }   // stack shape must match exactly
            body.put(n.name+"\0"+m.name+"\0"+m.desc, member);
        }
    }

    static AbstractInsnNode fresh(AbstractInsnNode t){
        if(t instanceof FieldInsnNode){ FieldInsnNode f=(FieldInsnNode)t; return new FieldInsnNode(f.getOpcode(),f.owner,f.name,f.desc); }
        MethodInsnNode m=(MethodInsnNode)t; return new MethodInsnNode(m.getOpcode(),m.owner,m.name,m.desc,m.itf);
    }

    static byte[] rewrite(byte[] data){
        ClassNode n=new ClassNode(); new ClassReader(data).accept(n,0); boolean t=false;
        for(MethodNode m: n.methods){ if(m.instructions==null) continue;
            for(AbstractInsnNode in=m.instructions.getFirst(); in!=null;){
                AbstractInsnNode next=in.getNext();
                if(in.getOpcode()==Opcodes.INVOKESTATIC){ MethodInsnNode c=(MethodInsnNode)in;
                    if(A.matcher(c.name).matches()){
                        AbstractInsnNode tgt=body.get(c.owner+"\0"+c.name+"\0"+c.desc);
                        if(tgt!=null){ m.instructions.set(in, fresh(tgt)); inlined++; t=true; }
                    }
                }
                in=next;
            }
        }
        if(!t) return data; classes++;
        ClassWriter cw=new ClassWriter(0); n.accept(cw); return cw.toByteArray();
    }
    static byte[] readAll(InputStream in) throws IOException { ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] u=new byte[8192]; for(int r;(r=in.read(u))!=-1;) b.write(u,0,r); return b.toByteArray(); }
}
