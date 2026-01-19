package cases;

public class TryFinally {
    public static int run(int value) {
        int out = 0;
        try {
            out = 10 / value;
            return out;
        } finally {
            out = out + 1;
        }
    }
}
