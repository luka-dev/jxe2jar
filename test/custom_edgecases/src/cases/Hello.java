package cases;

public class Hello {
    public static final int MAGIC = 0x1A2B3C;
    private static String greeting;

    static {
        greeting = "hello";
    }

    public static String join(String a, String b) {
        StringBuffer buf = new StringBuffer();
        buf.append(a);
        buf.append(":");
        buf.append(b);
        return buf.toString();
    }

    public static void main(String[] args) {
        String out = join(greeting, "world");
        if (args != null && args.length > 0) {
            out = join(out, args[0]);
        }
        System.out.println(out);
    }
}
