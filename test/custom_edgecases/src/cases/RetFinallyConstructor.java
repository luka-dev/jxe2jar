package cases;

public class RetFinallyConstructor {
    private int x;

    public RetFinallyConstructor(int v) {
        try {
            this.x = v;
        } finally {
            this.x = this.x + 1;
        }
    }

    public static int test(int v) {
        try {
            return v + 1;
        } finally {
            v = v + 2;
        }
    }
}
