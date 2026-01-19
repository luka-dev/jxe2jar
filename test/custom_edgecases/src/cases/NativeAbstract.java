package cases;

public abstract class NativeAbstract {
    public abstract int compute(int a, int b);

    public native int nativeAdd(int a, int b);

    public static class Impl extends NativeAbstract {
        public int compute(int a, int b) {
            return a * b;
        }
    }
}
