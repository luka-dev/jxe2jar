package cases;

public class CastInstanceof {
    interface I {
        int v();
    }

    static class A implements I {
        public int v() { return 1; }
    }

    static class B extends A {
        public int v() { return 2; }
    }

    public static I cast(Object o) {
        return (I) o;
    }

    public static boolean test(Object o) {
        return o instanceof I;
    }

    public static boolean testArray(Object o) {
        return o instanceof String[];
    }

    public static Object down(Object o) {
        return (B) o;
    }
}
