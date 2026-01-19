package cases;

public class TryFinallyReturn {
    private static int sideEffect;

    public static int test(int x) {
        try {
            if (x < 0) {
                return -1;
            }
            return x + 1;
        } finally {
            sideEffect += 1;
        }
    }

    public static int test2(int x) {
        int y = x;
        try {
            y = y + 10;
            return y;
        } finally {
            y = y + 1;
            sideEffect += y;
        }
    }

    public static int sideEffect() {
        return sideEffect;
    }
}
