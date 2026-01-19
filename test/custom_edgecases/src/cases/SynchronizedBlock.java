package cases;

public class SynchronizedBlock {
    private static final Object LOCK = new Object();

    public static int inc(int x) {
        synchronized (LOCK) {
            return x + 1;
        }
    }

    public static int incLocal(int x) {
        Object local = new Object();
        synchronized (local) {
            return x + 2;
        }
    }
}
