import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.Enumeration;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

/** Loads + links (verifies) every class in a jar; prints failures, exit 1 if any. */
public class VerifyAll {
    public static void main(String[] args) throws Exception {
        JarFile jar = new JarFile(args[0]);
        URLClassLoader cl = new URLClassLoader(new URL[]{new File(args[0]).toURI().toURL()}, VerifyAll.class.getClassLoader());
        int ok = 0, bad = 0;
        for (Enumeration<JarEntry> e = jar.entries(); e.hasMoreElements();) {
            String n = e.nextElement().getName();
            if (!n.endsWith(".class")) continue;
            String name = n.substring(0, n.length() - 6).replace('/', '.');
            try {
                Class<?> c = Class.forName(name, false, cl);
                c.getDeclaredMethods();  // forces linking => verification
                c.getDeclaredFields();
                ok++;
            } catch (Throwable t) {
                bad++;
                System.out.println("FAIL " + name + ": " + t);
            }
        }
        System.out.println("verified ok=" + ok + " bad=" + bad);
        System.exit(bad == 0 ? 0 : 1);
    }
}
