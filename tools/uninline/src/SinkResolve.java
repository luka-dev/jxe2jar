/*
 * T3b - sink-domain constant recovery, with fixpoint + field & switch domains.
 *
 * Non-distinctive cross-scope constants (e.g. DSIBAP.RT_GETBAPSTATE = 1000) are
 * recovered by WHERE the literal flows, using shallow intra-procedural dataflow
 * (ASM Analyzer<SourceValue>). Domains are LEARNED from surviving getstatic
 * references that the earlier un-inliner tiers (T1/T2/T3a) placed, so this runs on
 * an already-un-inlined jar and self-seeds.
 *
 * Sinks whose domain is learned:
 *   - call-arg slot   (callee owner, method, desc, argIndex)  <- getstatic passed as arg
 *   - field slot      (owner, name, desc)                     <- getstatic stored to field
 *   - switch-on-param  a switch whose keys match owner O's constant set, over a value
 *                      loaded directly from method parameter p -> that (method,p) slot = O
 *
 * A slot is trusted when >=2 distinct constants from a SINGLE owner back it. Then a
 * NON-distinctive literal (past floor) flowing into that slot is rewritten to
 * getstatic of the owner's uniquely-matching constant.
 *
 * FIXPOINT: each resolve pass adds getstatic refs, which seed more slots; iterate
 * learn+resolve until no new rewrites (monotonic - only facts added). Return-value
 * domains are intentionally NOT used (utility methods returning status/ID/bool-as-int
 * over-generalize).
 *
 * Usage: java -cp asm-9.7.jar:asm-tree-9.7.jar:asm-analysis-9.7.jar:. SinkResolve <in.jar> <out.jar> [floor]
 */
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import org.objectweb.asm.tree.analysis.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;

public class SinkResolve {

    static final class Ref { final String owner,name,desc; Ref(String o,String n,String d){owner=o;name=n;desc=d;} }
    static final Map<String,byte[]> classes = new LinkedHashMap<>();
    static final Map<String, Map<String, List<Ref>>> ownerPub = new HashMap<>();  // owner -> key -> refs (public consts)
    static final Set<String> constSig = new HashSet<>();                          // owner\0name\0desc
    // learned domains (rebuilt each iteration, monotonic):
    static final Map<String, String> sinkOwner = new HashMap<>();                 // call-arg / switch-param slot -> owner
    static final Map<String, String> fieldOwner = new HashMap<>();                // field slot -> owner
    static int floor = 100;

    public static void main(String[] args) throws Exception {
        if (args[0].equals("--domains")) { dumpDomains(args[1], args[2]); return; }
        String in = args[0], out = args[1];
        if (args.length > 2) floor = Integer.parseInt(args[2]);

        try (ZipFile zf = new ZipFile(in)) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();) {
                ZipEntry ze=e.nextElement(); byte[] d=readAll(zf.getInputStream(ze));
                classes.put(ze.getName(), d);
                if (ze.getName().endsWith(".class")) try { indexConsts(d); } catch(Exception ig){}
            }
        }
        System.out.println("loaded " + classes.size() + " entries; constants in " + ownerPub.size() + " owners");

        long grand = 0;
        for (int iter = 1; iter <= 6; iter++) {
            Map<String, Map<String,Set<String>>> callSeeds = new HashMap<>();
            Map<String, Map<String,Set<String>>> fieldSeeds = new HashMap<>();
            for (Map.Entry<String,byte[]> e : classes.entrySet())
                if (e.getKey().endsWith(".class"))
                    try { learn(e.getValue(), callSeeds, fieldSeeds); } catch(Exception ig){}
            sinkOwner.clear(); fieldOwner.clear();
            coherent(callSeeds, sinkOwner);
            coherent(fieldSeeds, fieldOwner);

            long r = 0;
            for (Map.Entry<String,byte[]> e : classes.entrySet()) {
                if (!e.getKey().endsWith(".class")) continue;
                try {
                    long[] c = {0};
                    byte[] nb = resolve(e.getValue(), c);
                    if (c[0] > 0) { e.setValue(nb); r += c[0]; }
                } catch(Exception ig){}
            }
            System.out.printf("  iter %d: slots(call=%d field=%d) rewrites=%d%n",
                    iter, sinkOwner.size(), fieldOwner.size(), r);
            grand += r;
            if (r == 0) break;
        }

        try (ZipOutputStream zos = new ZipOutputStream(new BufferedOutputStream(new FileOutputStream(out)))) {
            for (Map.Entry<String,byte[]> e : classes.entrySet()) {
                zos.putNextEntry(new ZipEntry(e.getKey())); zos.write(e.getValue()); zos.closeEntry();
            }
        }
        System.out.println("T3b total sink-resolved: " + grand);
    }

    /** #2-lite: learn sink-argument / field domains once and dump them (no rewrite). */
    static void dumpDomains(String in, String outMd) throws Exception {
        try (ZipFile zf = new ZipFile(in)) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();) {
                ZipEntry ze=e.nextElement(); byte[] d=readAll(zf.getInputStream(ze)); classes.put(ze.getName(), d);
                if (ze.getName().endsWith(".class")) try { indexConsts(d); } catch(Exception ig){}
            }
        }
        Map<String, Map<String,Set<String>>> callSeeds=new HashMap<>(), fieldSeeds=new HashMap<>();
        for (Map.Entry<String,byte[]> e: classes.entrySet())
            if (e.getKey().endsWith(".class")) try { learn(e.getValue(), callSeeds, fieldSeeds); } catch(Exception ig){}
        coherent(callSeeds, sinkOwner); coherent(fieldSeeds, fieldOwner);
        List<String> calls=new ArrayList<>(sinkOwner.keySet()); Collections.sort(calls);
        List<String> flds=new ArrayList<>(fieldOwner.keySet()); Collections.sort(flds);
        try (PrintWriter w=new PrintWriter(new FileWriter(outMd))) {
            w.println("# Sink-domain map (learned constant family per argument slot)\n");
            w.println("What constant registry each method-argument / field speaks - the reliable");
            w.println("form of enum-domain recovery (annotate, not retype). Learned from surviving");
            w.println("getstatic references via dataflow.\n");
            w.println("## Method-argument slots  (" + calls.size() + ")\n");
            w.println("| callee | arg | domain owner |\n|---|---|---|");
            for (String k: calls) { int h=k.lastIndexOf("#"); String slot=k.substring(0,h), arg=k.substring(h+1);
                w.println("| `"+slot+"` | "+arg+" | `"+sinkOwner.get(k)+"` |"); }
            w.println("\n## Field slots  (" + flds.size() + ")\n");
            w.println("| field | domain owner |\n|---|---|");
            for (String k: flds) { String[] p=k.split("\0"); w.println("| `"+p[0]+"."+p[1]+" "+p[2]+"` | `"+fieldOwner.get(k)+"` |"); }
        }
        System.out.println("wrote " + outMd + ": " + sinkOwner.size() + " arg-slot domains, " + fieldOwner.size() + " field domains");
    }

    static void coherent(Map<String, Map<String,Set<String>>> seeds, Map<String,String> out) {
        for (Map.Entry<String, Map<String,Set<String>>> e : seeds.entrySet()) {
            Map<String,Set<String>> byOwner = e.getValue();
            if (byOwner.size() != 1) continue;                       // ambiguous -> skip
            Map.Entry<String,Set<String>> only = byOwner.entrySet().iterator().next();
            if (only.getValue().size() >= 2) out.put(e.getKey(), only.getKey());
        }
    }

    // ---------- constant index ----------
    static void indexConsts(byte[] data) {
        ClassReader cr = new ClassReader(data);
        final boolean[] pub = { false }; final String cn = cr.getClassName();
        cr.accept(new ClassVisitor(Opcodes.ASM9) {
            public void visit(int v,int a,String n,String s,String sup,String[] i){ pub[0]=(a&Opcodes.ACC_PUBLIC)!=0; }
            public FieldVisitor visitField(int acc,String fn,String d,String sig,Object val){
                if((acc&Opcodes.ACC_STATIC)!=0 && (acc&Opcodes.ACC_FINAL)!=0 && val!=null){
                    constSig.add(cn+"\0"+fn+"\0"+d);
                    if(pub[0] && (acc&Opcodes.ACC_PUBLIC)!=0){ String key=constKey(d,val);
                        if(key!=null) ownerPub.computeIfAbsent(cn,k->new HashMap<>())
                                .computeIfAbsent(key,k->new ArrayList<>()).add(new Ref(cn,fn,d)); }
                }
                return null;
            }
        }, ClassReader.SKIP_CODE|ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);
    }
    static String constKey(String desc, Object val){
        switch(desc){
            case "I": case "S": case "B": case "C": case "Z": return "i:"+((Integer)val).intValue();
            case "J": return "j:"+((Long)val).longValue();
            case "F": return "f:"+Float.floatToRawIntBits((Float)val);
            case "D": return "d:"+Double.doubleToRawLongBits((Double)val);
            case "Ljava/lang/String;": return "s:"+val;
            default: return null;
        }
    }
    static boolean meaningful(String s){ if(s.length()<3) return false;
        for(int i=0;i<s.length();i++) if(Character.isUpperCase(s.charAt(i))) return true; return false; }
    static String litKey(AbstractInsnNode in){
        int op=in.getOpcode();
        if(op>=Opcodes.ICONST_M1&&op<=Opcodes.ICONST_5) return "i:"+(op-Opcodes.ICONST_0);
        if(op==Opcodes.BIPUSH||op==Opcodes.SIPUSH) return "i:"+((IntInsnNode)in).operand;
        if(op==Opcodes.LCONST_0) return "j:0"; if(op==Opcodes.LCONST_1) return "j:1";
        if(op==Opcodes.LDC){ Object c=((LdcInsnNode)in).cst;
            if(c instanceof Integer) return "i:"+c; if(c instanceof Long) return "j:"+c;
            if(c instanceof Float) return "f:"+Float.floatToRawIntBits((Float)c);
            if(c instanceof Double) return "d:"+Double.doubleToRawLongBits((Double)c);
            if(c instanceof String) return "s:"+c; }
        return null;
    }
    static Long numOfKey(String k){ if(k.startsWith("i:")||k.startsWith("j:")){ try{return Long.parseLong(k.substring(2));}catch(Exception e){return null;} } return null; }
    static boolean isConstGetStatic(AbstractInsnNode p){
        return p.getOpcode()==Opcodes.GETSTATIC &&
               constSig.contains(((FieldInsnNode)p).owner+"\0"+((FieldInsnNode)p).name+"\0"+((FieldInsnNode)p).desc);
    }
    static AbstractInsnNode sole(SourceValue sv){ return (sv!=null && sv.insns.size()==1) ? sv.insns.iterator().next() : null; }

    // local-var slot -> argument index for this method (-1 if not a parameter slot)
    static int[] paramMap(MethodNode mn){
        boolean stat=(mn.access & Opcodes.ACC_STATIC)!=0;
        Type[] at=Type.getArgumentTypes(mn.desc);
        int slot=stat?0:1, total=slot; for(Type t:at) total+=t.getSize();
        int[] map=new int[total+2]; Arrays.fill(map,-1);
        int s=stat?0:1; for(int i=0;i<at.length;i++){ if(s<map.length) map[s]=i; s+=at[i].getSize(); }
        return map;
    }

    // ---------- LEARN ----------
    static void learn(byte[] data, Map<String,Map<String,Set<String>>> callSeeds,
                      Map<String,Map<String,Set<String>>> fieldSeeds) {
        ClassNode node=new ClassNode(); new ClassReader(data).accept(node,0);
        for(MethodNode mn: node.methods){
            if(mn.instructions==null||mn.instructions.size()==0) continue;
            Frame<SourceValue>[] fr=analyze(node.name, mn); if(fr==null) continue;
            AbstractInsnNode[] arr=mn.instructions.toArray();
            int[] pmap=paramMap(mn);
            for(int i=0;i<arr.length;i++){
                AbstractInsnNode in=arr[i]; Frame<SourceValue> f=fr[i]; if(f==null) continue;
                if(in instanceof MethodInsnNode){
                    MethodInsnNode call=(MethodInsnNode)in; Type[] at=Type.getArgumentTypes(call.desc);
                    int base=f.getStackSize()-at.length;
                    for(int a=0;a<at.length;a++){
                        AbstractInsnNode p; try{ p=sole(f.getStack(base+a)); }catch(Exception e){continue;}
                        if(p!=null && isConstGetStatic(p)){ FieldInsnNode fi=(FieldInsnNode)p;
                            seed(callSeeds, call.owner+"."+call.name+call.desc+"#"+a, fi.owner, fi.name); }
                    }
                } else if(in.getOpcode()==Opcodes.PUTFIELD || in.getOpcode()==Opcodes.PUTSTATIC){
                    FieldInsnNode fi=(FieldInsnNode)in;
                    AbstractInsnNode p; try{ p=sole(f.getStack(f.getStackSize()-1)); }catch(Exception e){ p=null; }
                    if(p!=null && isConstGetStatic(p)){ FieldInsnNode g=(FieldInsnNode)p;
                        seed(fieldSeeds, fi.owner+"\0"+fi.name+"\0"+fi.desc, g.owner, g.name); }
                } else if(in instanceof LookupSwitchInsnNode || in instanceof TableSwitchInsnNode){
                    List<Integer> keys=switchKeys(in);
                    AbstractInsnNode subj; try{ subj=sole(f.getStack(f.getStackSize()-1)); }catch(Exception e){ subj=null; }
                    if(subj instanceof VarInsnNode && subj.getOpcode()==Opcodes.ILOAD){
                        int v=((VarInsnNode)subj).var; int arg=(v>=0&&v<pmap.length)?pmap[v]:-1;
                        if(arg>=0){ String o=switchOwner(keys);
                            if(o!=null){ String slot=node.name+"."+mn.name+mn.desc+"#"+arg;
                                Map<String,List<Ref>> m=ownerPub.get(o);
                                for(int k:keys){ List<Ref> ls=m.get("i:"+k); if(ls!=null&&ls.size()==1) seed(callSeeds, slot, o, ls.get(0).name); } } }
                    }
                }
            }
        }
    }
    static void seed(Map<String,Map<String,Set<String>>> m, String slot, String owner, String name){
        m.computeIfAbsent(slot,k->new HashMap<>()).computeIfAbsent(owner,k->new HashSet<>()).add(name);
    }
    static List<Integer> switchKeys(AbstractInsnNode in){
        List<Integer> ks=new ArrayList<>();
        if(in instanceof LookupSwitchInsnNode) ks.addAll(((LookupSwitchInsnNode)in).keys);
        else { TableSwitchInsnNode t=(TableSwitchInsnNode)in; for(int k=t.min;k<=t.max;k++) ks.add(k); }
        return ks;
    }
    /** owner whose public constants uniquely cover >=2 of the switch keys, and is the sole such owner. */
    static String switchOwner(List<Integer> keys){
        Map<String,Integer> hit=new HashMap<>();
        for(int k:keys){ for(Map.Entry<String,Map<String,List<Ref>>> e: ownerPub.entrySet()){
            List<Ref> ls=e.getValue().get("i:"+k); if(ls!=null&&ls.size()==1) hit.merge(e.getKey(),1,Integer::sum); } }
        String best=null; int bn=0, ties=0;
        for(Map.Entry<String,Integer> e: hit.entrySet()){ if(e.getValue()>bn){best=e.getKey();bn=e.getValue();ties=0;} else if(e.getValue()==bn) ties++; }
        return (bn>=2 && ties==0) ? best : null;
    }

    // ---------- RESOLVE ----------
    static byte[] resolve(byte[] data, long[] count) {
        ClassNode node=new ClassNode(); new ClassReader(data).accept(node,0);
        Map<AbstractInsnNode,Ref> plan=new IdentityHashMap<>();
        Set<AbstractInsnNode> conflict=Collections.newSetFromMap(new IdentityHashMap<>());
        for(MethodNode mn: node.methods){
            if(mn.instructions==null||mn.instructions.size()==0) continue;
            Frame<SourceValue>[] fr=analyze(node.name, mn); if(fr==null) continue;
            AbstractInsnNode[] arr=mn.instructions.toArray();
            for(int i=0;i<arr.length;i++){
                AbstractInsnNode in=arr[i]; Frame<SourceValue> f=fr[i]; if(f==null) continue;
                if(in instanceof MethodInsnNode){
                    MethodInsnNode call=(MethodInsnNode)in; Type[] at=Type.getArgumentTypes(call.desc);
                    int base=f.getStackSize()-at.length;
                    for(int a=0;a<at.length;a++){
                        String owner=sinkOwner.get(call.owner+"."+call.name+call.desc+"#"+a); if(owner==null) continue;
                        planLiteral(f, base+a, owner, plan, conflict);
                    }
                } else if(in.getOpcode()==Opcodes.PUTFIELD || in.getOpcode()==Opcodes.PUTSTATIC){
                    FieldInsnNode fi=(FieldInsnNode)in;
                    String owner=fieldOwner.get(fi.owner+"\0"+fi.name+"\0"+fi.desc); if(owner==null) continue;
                    planLiteral(f, f.getStackSize()-1, owner, plan, conflict);
                }
            }
        }
        for(AbstractInsnNode c: conflict) plan.remove(c);
        if(plan.isEmpty()) return data;
        for(MethodNode mn: node.methods){ if(mn.instructions==null) continue;
            for(AbstractInsnNode in=mn.instructions.getFirst(); in!=null;){
                AbstractInsnNode next=in.getNext(); Ref r=plan.get(in);
                if(r!=null){ mn.instructions.set(in,new FieldInsnNode(Opcodes.GETSTATIC,r.owner,r.name,r.desc)); count[0]++; }
                in=next; } }
        ClassWriter cw=new ClassWriter(0); node.accept(cw); return cw.toByteArray();
    }
    static void planLiteral(Frame<SourceValue> f, int stackIdx, String owner,
                            Map<AbstractInsnNode,Ref> plan, Set<AbstractInsnNode> conflict){
        AbstractInsnNode p; try{ p=sole(f.getStack(stackIdx)); }catch(Exception e){ return; }
        if(p==null) return; String key=litKey(p); if(key==null) return;
        Long nv=numOfKey(key); if(nv!=null && Math.abs(nv)<floor) return;
        Map<String,List<Ref>> m=ownerPub.get(owner); if(m==null) return;
        List<Ref> ls=m.get(key); if(ls==null||ls.size()!=1) return;
        Ref r=ls.get(0); if(!meaningful(r.name)) return;
        if(plan.containsKey(p) && !same(plan.get(p),r)) conflict.add(p); else plan.put(p,r);
    }
    static boolean same(Ref a, Ref b){ return a.owner.equals(b.owner)&&a.name.equals(b.name)&&a.desc.equals(b.desc); }

    static Frame<SourceValue>[] analyze(String owner, MethodNode mn){
        try { return new Analyzer<>(new SourceInterpreter()).analyze(owner, mn); }
        catch(Throwable t){ return null; }
    }
    static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] buf=new byte[8192];
        for(int n; (n=in.read(buf))!=-1;) b.write(buf,0,n); return b.toByteArray();
    }
}
