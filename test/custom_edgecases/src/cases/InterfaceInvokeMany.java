package cases;

public class InterfaceInvokeMany {
    interface Many {
        int m(int a, long b, float c, double d, Object e, String f);
    }

    static class Impl implements Many {
        public int m(int a, long b, float c, double d, Object e, String f) {
            return a + (int)b + (int)c + (int)d + f.length();
        }
    }

    public static int call() {
        Many m = new Impl();
        return m.m(1, 2L, 3.0f, 4.0d, new Object(), "hi");
    }
}
