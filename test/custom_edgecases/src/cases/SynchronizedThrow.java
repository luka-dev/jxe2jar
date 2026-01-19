package cases;

public class SynchronizedThrow {
    private static final Object LOCK = new Object();

    public static void boom() {
        synchronized (LOCK) {
            throw new RuntimeException("boom");
        }
    }
}
