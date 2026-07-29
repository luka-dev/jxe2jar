import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.type.*;
import com.github.javaparser.printer.lexicalpreservation.LexicalPreservingPrinter;
import com.github.javaparser.resolution.types.ResolvedType;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.*;

import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/*
 * Rewrite Java-5 enhanced-for loops into -source 1.4 equivalents, in place.
 *  - Iterable  -> Iterator + while (raw, cast element to erased type)
 *  - array     -> indexed for
 * Element type has its generics erased (illegal at -source 1.4).
 * Array-vs-Iterable decided by symbol resolution (classpath = combined-final.jar + libs);
 * on unresolved types, falls back to: primitive element => array, else Iterable.
 */
public class RewriteForeach {
    static int filesChanged = 0, loopsRewritten = 0, resolveFails = 0;

    public static void main(String[] args) throws Exception {
        String jar = args[0];            // classpath jar (combined-final.jar)
        String libsDir = args[1];        // libs dir (extra jars)
        // remaining args: .java files to process

        CombinedTypeSolver ts = new CombinedTypeSolver();
        ts.add(new ReflectionTypeSolver());
        ts.add(new JarTypeSolver(jar));
        Path libs = Paths.get(libsDir);
        if (Files.isDirectory(libs)) {
            for (Path p : (Iterable<Path>) Files.list(libs)::iterator) {
                String n = p.getFileName().toString();
                if (n.endsWith(".jar") && !n.contains("-sources") && !n.contains("-javadoc")) {
                    try { ts.add(new JarTypeSolver(p)); } catch (Exception ignore) {}
                }
            }
        }
        ParserConfiguration cfg = new ParserConfiguration().setSymbolResolver(new JavaSymbolSolver(ts));
        StaticJavaParser.setConfiguration(cfg);

        List<String> files = new ArrayList<>();
        if (args.length == 3 && args[2].equals("-")) {   // read paths from stdin
            Scanner sc = new Scanner(System.in);
            while (sc.hasNextLine()) { String l = sc.nextLine().trim(); if (!l.isEmpty()) files.add(l); }
        } else {
            for (int i = 2; i < args.length; i++) files.add(args[i]);
        }
        int done = 0;
        for (String s : files) {
            Path f = Paths.get(s);
            try {
                if (processFile(f)) filesChanged++;
            } catch (Exception e) {
                System.out.println("SKIP " + f + " : " + e.getClass().getSimpleName() + " " + e.getMessage());
            }
            if (++done % 2000 == 0) System.out.println("  ...scanned " + done + "/" + files.size());
        }
        System.out.println("\nfiles changed: " + filesChanged + "  loops rewritten: " + loopsRewritten
                + "  (resolve-fallbacks: " + resolveFails + ")");
    }

    static boolean processFile(Path f) throws Exception {
        CompilationUnit cu = StaticJavaParser.parse(f);
        List<ForEachStmt> loops = cu.findAll(ForEachStmt.class);
        if (loops.isEmpty()) return false;

        LexicalPreservingPrinter.setup(cu);
        AtomicInteger seq = new AtomicInteger();

        // deepest-last: replace inner loops before their enclosing ones
        Collections.reverse(loops);
        for (ForEachStmt fe : loops) {
            VariableDeclarationExpr ve = fe.getVariable();
            VariableDeclarator vd = ve.getVariable(0);
            String name = vd.getNameAsString();
            String rawType = erase(vd.getType());
            String iter = fe.getIterable().toString();
            String inner = bodyInner(fe.getBody());
            boolean fin = ve.isFinal();
            String mod = fin ? "final " : "";
            int id = seq.getAndIncrement();

            boolean isArray = decideArray(fe, vd.getType());
            String repl;
            if (isArray) {
                String a = "$arr" + id, j = "$i" + id;
                repl = "{\n" + rawType + "[] " + a + " = " + iter + ";\n"
                     + "for (int " + j + " = 0; " + j + " < " + a + ".length; " + j + "++) {\n"
                     + mod + rawType + " " + name + " = " + a + "[" + j + "];\n"
                     + inner + "\n}\n}";
            } else {
                String it = "$it" + id;
                repl = "{\n" + "java.util.Iterator " + it + " = (" + iter + ").iterator();\n"
                     + "while (" + it + ".hasNext()) {\n"
                     + mod + rawType + " " + name + " = (" + rawType + ") " + it + ".next();\n"
                     + inner + "\n}\n}";
            }
            BlockStmt newBlock = StaticJavaParser.parseBlock(repl);
            fe.replace(newBlock);
            loopsRewritten++;
        }

        Files.write(f, LexicalPreservingPrinter.print(cu).getBytes("UTF-8"));
        return true;
    }

    // erased raw source of a type (drop all generic arguments)
    static String erase(Type t) {
        Type c = t.clone();
        for (ClassOrInterfaceType coi : c.findAll(ClassOrInterfaceType.class)) {
            coi.setTypeArguments((com.github.javaparser.ast.NodeList<Type>) null);
        }
        if (c instanceof ClassOrInterfaceType) {
            ((ClassOrInterfaceType) c).setTypeArguments((com.github.javaparser.ast.NodeList<Type>) null);
        }
        return c.toString();
    }

    static String bodyInner(Statement body) {
        if (body.isBlockStmt()) {
            StringBuilder sb = new StringBuilder();
            for (Statement s : body.asBlockStmt().getStatements()) sb.append(s.toString()).append("\n");
            return sb.toString();
        }
        return body.toString();
    }

    @SuppressWarnings("unused")
    static boolean decideArray(ForEachStmt fe, Type elemType) {
        try {
            ResolvedType rt = fe.getIterable().calculateResolvedType();
            return rt.isArray();
        } catch (Throwable ex) {
            resolveFails++;
            // fallback: a primitive element type can only come from a primitive array
            return elemType instanceof PrimitiveType;
        }
    }
}
