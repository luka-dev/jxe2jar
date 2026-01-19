package cases;

public class Casts {
    public static boolean run(Object o) {
        if (o instanceof String) {
            String s = (String) o;
            return s.length() > 0;
        }
        return false;
    }
}
