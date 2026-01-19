package cases;

public class NullChecks {
    public static int len(String s) {
        if (s == null) return -1;
        return s.length();
    }

    public static boolean isNotNull(Object o) {
        return o != null;
    }
}
