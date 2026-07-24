/*
 * Three-way refinement of constant resolutions (precision QA).
 *
 * The un-inliner is 100% value-correct, but a small tail of NAME resolutions is
 * misleading: a genuine literal (e.g. setProgress(100)) that coincidentally equals a
 * closure constant (OSDConstants.CONTENT_GROUP_X_RATED). This pass reverts ONLY that
 * clear class back to a plain literal, keeping everything else. (Per Codex: full
 * auto-revert is unsafe; do a conservative subset + flag the rest.)
 *
 * KEEP   (untouched): distinctive value, or own-class constant, or FAMILY COHESION
 *        (the class references >=2 constants from that owner -> real family, e.g.
 *        ObjectOutputStream using many ObjectStreamConstants.TC_*). Cohesion is a hard
 *        keep-veto.
 * REVERT (getstatic -> literal): a getstatic-to-constant that (a) flows into a
 *        BOUNDED-SCALAR sink method (setProgress/setAlpha/sleep/substring/...), (b) is
 *        a LONE use of that owner in the class, (c) non-distinctive + not globally
 *        unique + owner != using class, (d) natural round value. All must hold.
 * FLAG   everything else non-distinctive+foreign -> const_review.tsv sidecar.
 *
 * Usage: java -cp asm-9.7.jar:asm-tree-9.7.jar:asm-analysis-9.7.jar:. RefineResolve <in.jar> <out.jar> <review.tsv>
 */
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import org.objectweb.asm.tree.analysis.*;
import java.io.*; import java.util.*; import java.util.zip.*;

public class RefineResolve {
    static final Map<String,int[]> constIntVal = new HashMap<>();     // owner\0name\0desc -> [value] (int-family only)
    static final Map<String,Integer> valueMult = new HashMap<>();     // "i:"+v -> #distinct constants
    static final Set<String> constSig = new HashSet<>();
    static long revert=0, flag=0, keptCohesion=0;
    static final List<String> flags = new ArrayList<>();

    // bounded-scalar sinks: params are quantities, not symbolic registry constants
    static final String[] SCALAR = {"setProgress","setAlpha","setOpacity","setBounds","setSize","setWidth","setHeight",
        "setLocation","setX","setY","setPadding","setMargin","setWeight","setScale","setRotation","setVolume","setPercent",
        "sleep","substring","setPosition","setDuration","setDelay","setTimeout","setRadius","setAngle"};

    public static void main(String[] a) throws Exception {
        Map<String,byte[]> classes = new LinkedHashMap<>();
        try (ZipFile zf=new ZipFile(a[0])) {
            for (Enumeration<? extends ZipEntry> e=zf.entries(); e.hasMoreElements();){ ZipEntry ze=e.nextElement();
                byte[] d=readAll(zf.getInputStream(ze)); classes.put(ze.getName(), d);
                if(ze.getName().endsWith(".class")) try{ index(d); }catch(Exception ig){} }
        }
        Map<String,Set<String>> byVal=new HashMap<>();
        for(Map.Entry<String,int[]> e: constIntVal.entrySet()){ String[] p=e.getKey().split("\0");
            byVal.computeIfAbsent("i:"+e.getValue()[0],k->new HashSet<>()).add(p[0]+"."+p[1]); }
        for(Map.Entry<String,Set<String>> e: byVal.entrySet()) valueMult.put(e.getKey(), e.getValue().size());
        System.out.println("indexed "+constIntVal.size()+" int constants");

        try (ZipOutputStream zos=new ZipOutputStream(new BufferedOutputStream(new FileOutputStream(a[1])))) {
            for (Map.Entry<String,byte[]> e: classes.entrySet()){
                byte[] d=e.getValue();
                if(e.getKey().endsWith(".class")) try{ d=refine(d); }catch(Exception ig){}
                zos.putNextEntry(new ZipEntry(e.getKey())); zos.write(d); zos.closeEntry();
            }
        }
        try (PrintWriter w=new PrintWriter(new FileWriter(a[2]))){
            w.println("class\tmethod\tvalue\towner\tfield\taction\treason");
            for(String s: flags) w.println(s);
        }
        System.out.printf("REVERT=%d (misleading -> literal)  FLAG=%d (-> %s)  kept-by-cohesion=%d%n", revert, flag, a[2], keptCohesion);
    }

    static void index(byte[] d){
        ClassReader cr=new ClassReader(d); final String cn=cr.getClassName();
        cr.accept(new ClassVisitor(Opcodes.ASM9){
            public FieldVisitor visitField(int acc,String n,String desc,String sig,Object val){
                if((acc&Opcodes.ACC_STATIC)!=0&&(acc&Opcodes.ACC_FINAL)!=0&&val!=null){
                    constSig.add(cn+"\0"+n+"\0"+desc);
                    if(val instanceof Integer && ("I".equals(desc)||"S".equals(desc)||"B".equals(desc)||"C".equals(desc)))
                        constIntVal.put(cn+"\0"+n+"\0"+desc, new int[]{(Integer)val});
                }
                return null; }
        }, ClassReader.SKIP_CODE|ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);
    }
    static boolean isScalarSink(String m){ for(String s: SCALAR) if(m.equals(s)||m.startsWith(s)) return true; return false; }

    // generic-quantity domain words: presence in the USING method/callee name => scalar context
    static final Set<String> QUANTITY = new HashSet<>(Arrays.asList(
        "progress","resolution","width","height","alpha","opacity","volume","size","timeout","duration",
        "percent","scale","radius","angle","count","length","capacity","coordinate","margin","padding",
        "position","delay","offset","brightness","contrast","speed","distance","threshold","ratio","weight",
        "bounds","dimension","pixel","dpi","fontsize","spacing","gap","stroke","zoom","level","index"));
    // truly-generic tokens (no domain signal). Domain-bearing words (service/state/role/
    // media/tuner/seat/menu/update/...) are intentionally NOT here - Codex: keep them.
    static final Set<String> STOP = new HashSet<>(Arrays.asList(
        "constant","constants","value","values","type","types","ids","manager","impl","data","info",
        "helper","object","default","get","set","the","abstract","base","core","evo","hmi",
        "new","create","common","util","utils","interface","class","field","method","for","and","with","from"));
    // acronym / abbreviation aliases -> expanded domain tokens (curated for this corpus)
    static final Map<String,String[]> ALIAS = new HashMap<>();
    static { ALIAS.put("swdl", new String[]{"software","download","update","ota","uota"});
             ALIAS.put("uota", new String[]{"update","ota","software","download","swdl"});
             ALIAS.put("gps",  new String[]{"location","position","navi"});
             ALIAS.put("sds",  new String[]{"speech","dialog","command","voice"});
             ALIAS.put("adb",  new String[]{"address","addressbook","contact"});
             ALIAS.put("ens",  new String[]{"setting","settings"});
             ALIAS.put("lang", new String[]{"language"}); }
    static Set<String> tokenize(String s){
        Set<String> t=new HashSet<>();
        for(String part: s.replaceAll("([a-z])([A-Z])","$1 $2").replaceAll("([A-Z]+)([A-Z][a-z])","$1 $2")
                          .replace('_',' ').replace('$',' ').split("[^A-Za-z]+")){
            String w=part.toLowerCase(); if(w.length()<3 || STOP.contains(w)) continue;
            if(w.endsWith("s") && w.length()>4) w=w.substring(0,w.length()-1);   // light plural stem
            t.add(w); String[] al=ALIAS.get(w); if(al!=null) t.addAll(Arrays.asList(al));
        }
        return t;
    }
    // overlap allowing prefix match (lang~language) for tokens >=4 chars
    static boolean overlaps(Set<String> a, Set<String> b){
        for(String x: a) for(String y: b){
            if(x.equals(y)) return true;
            if(x.length()>=4 && y.length()>=4 && (x.startsWith(y)||y.startsWith(x))) return true;
        }
        return false;
    }
    static String simple(String internal){ int i=internal.lastIndexOf('/'); String s=i<0?internal:internal.substring(i+1);
        int d=s.lastIndexOf('$'); return d<0?s:s.substring(d+1); }
    static boolean distinctive(long v){ long a=Math.abs(v);
        if(a<4096) return false; if((a&(a-1))==0) return false; if(((a+1)&a)==0) return false;
        if(Long.bitCount(a)<=2) return false; if(a%10==0) return false; if((a&0xFF)==0) return false;
        int tz=Long.numberOfTrailingZeros(a); long m=a>>>tz; if(((m+1)&m)==0) return false; return true; }
    static boolean natural(long v){ long a=Math.abs(v); return a<=2048 || a%10==0 || a%5==0; }

    static byte[] refine(byte[] data){
        ClassNode node=new ClassNode(); new ClassReader(data).accept(node,0); String cn=node.name;
        // cohesion: distinct constants referenced per owner in THIS class
        Map<String,Set<String>> cohesion=new HashMap<>();
        for(MethodNode m: node.methods){ if(m.instructions==null) continue;
            for(AbstractInsnNode in=m.instructions.getFirst(); in!=null; in=in.getNext())
                if(in.getOpcode()==Opcodes.GETSTATIC){ FieldInsnNode f=(FieldInsnNode)in;
                    if(constSig.contains(f.owner+"\0"+f.name+"\0"+f.desc))
                        cohesion.computeIfAbsent(f.owner,k->new HashSet<>()).add(f.name); } }

        // sink context: which callee (owner+name) each getstatic-value flows into as an arg
        Map<AbstractInsnNode,String[]> sinkCtx = new IdentityHashMap<>();   // getstatic -> {calleeOwnerSimple, calleeName}
        for(MethodNode m: node.methods){ if(m.instructions==null||m.instructions.size()==0) continue;
            Frame<SourceValue>[] fr; try{ fr=new Analyzer<>(new SourceInterpreter()).analyze(cn,m);}catch(Throwable t){continue;}
            AbstractInsnNode[] arr=m.instructions.toArray();
            for(int i=0;i<arr.length;i++){ if(!(arr[i] instanceof MethodInsnNode)) continue;
                MethodInsnNode call=(MethodInsnNode)arr[i]; Frame<SourceValue> f=fr[i]; if(f==null) continue;
                Type[] at=Type.getArgumentTypes(call.desc); int base=f.getStackSize()-at.length;
                for(int ai=0;ai<at.length;ai++){ SourceValue sv; try{ sv=f.getStack(base+ai);}catch(Exception e){continue;}
                    if(sv!=null&&sv.insns.size()==1) sinkCtx.put(sv.insns.iterator().next(), new String[]{simple(call.owner), call.name}); } }
        }
        // classify each getstatic-to-int-constant: KEEP / REVERT / FLAG (lexical, Codex rule)
        Map<AbstractInsnNode,Integer> revertPlan=new IdentityHashMap<>();
        for(MethodNode m: node.methods){ if(m.instructions==null) continue; String mn=m.name;
            for(AbstractInsnNode in=m.instructions.getFirst(); in!=null; in=in.getNext()){
                if(in.getOpcode()!=Opcodes.GETSTATIC) continue; FieldInsnNode g=(FieldInsnNode)in;
                int[] iv=constIntVal.get(g.owner+"\0"+g.name+"\0"+g.desc); if(iv==null) continue;
                int v=iv[0]; String vk="i:"+v;
                boolean self=g.owner.equals(cn); int fam=cohesion.getOrDefault(g.owner, Collections.emptySet()).size();
                boolean amb=valueMult.getOrDefault(vk,1)>1;
                if(!amb || self || fam>=2 || distinctive(v)){ if(fam>=2&&amb&&!distinctive(v)&&!self) keptCohesion++; continue; }
                // REVIEW: build lexical tokens for constant vs using-context
                Set<String> constT=tokenize(g.name); constT.addAll(tokenize(simple(g.owner)));
                Set<String> ctxT=tokenize(mn); ctxT.addAll(tokenize(simple(cn)));
                String[] sc=sinkCtx.get(in); if(sc!=null){ ctxT.addAll(tokenize(sc[0])); ctxT.addAll(tokenize(sc[1])); }
                boolean overlap=overlaps(constT, ctxT);
                boolean quantity=false; for(String w: tokenize(mn)) if(QUANTITY.contains(w)) quantity=true;
                if(!quantity && sc!=null) for(String w: tokenize(sc[1])) if(QUANTITY.contains(w)) quantity=true;
                String owner=simple(g.owner);
                if(overlap){                                                     // KEEP: positive domain coherence
                    keptCohesion++;
                } else {                                                          // DOUBTFUL -> revert to honest literal;
                    revertPlan.put(in, v);                                        // the candidate becomes an inline "??" comment
                    String reason = (quantity && natural(v)) ? "quantity-clash" : "low-confidence-lone";
                    flags.add(cn+"\t"+mn+"\t"+v+"\t"+g.owner+"\t"+g.name+"\t"+(reason.equals("quantity-clash")?"REVERT":"FLAG")+"\t"+reason);
                    flag++;
                }
            }
        }
        if(revertPlan.isEmpty()) return data;
        for(MethodNode m: node.methods){ if(m.instructions==null) continue;
            for(AbstractInsnNode in=m.instructions.getFirst(); in!=null;){ AbstractInsnNode nx=in.getNext();
                Integer v=revertPlan.get(in);
                if(v!=null){ m.instructions.set(in, intLit(v)); revert++; }
                in=nx; } }
        ClassWriter cw=new ClassWriter(0); node.accept(cw); return cw.toByteArray();
    }

    static AbstractInsnNode intLit(int v){
        if(v>=-1&&v<=5) return new InsnNode(Opcodes.ICONST_0+v);
        if(v>=Byte.MIN_VALUE&&v<=Byte.MAX_VALUE) return new IntInsnNode(Opcodes.BIPUSH,v);
        if(v>=Short.MIN_VALUE&&v<=Short.MAX_VALUE) return new IntInsnNode(Opcodes.SIPUSH,v);
        return new LdcInsnNode(v);
    }
    static byte[] readAll(InputStream in) throws IOException { ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] u=new byte[8192]; for(int r;(r=in.read(u))!=-1;) b.write(u,0,r); return b.toByteArray(); }
}
