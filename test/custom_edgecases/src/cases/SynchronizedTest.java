package cases;

public class SynchronizedTest {
    private final Object lock = new Object();
    private int count;

    public synchronized void inc() {
        count++;
    }

    public int withBlock(int delta) {
        synchronized (lock) {
            count += delta;
            return count;
        }
    }

    public int get() {
        return count;
    }
}
