package cases;

public class MathOps {
    public static int sum(int[] values) {
        int acc = 0;
        if (values == null) {
            return 0;
        }
        for (int i = 0; i < values.length; i++) {
            acc += values[i];
        }
        return acc;
    }

    public static int max(int[] values) {
        if (values == null || values.length == 0) {
            return Integer.MIN_VALUE;
        }
        int best = values[0];
        for (int i = 1; i < values.length; i++) {
            if (values[i] > best) {
                best = values[i];
            }
        }
        return best;
    }

    public static int fib(int n) {
        if (n <= 0) {
            return 0;
        }
        if (n == 1) {
            return 1;
        }
        int a = 0;
        int b = 1;
        for (int i = 2; i <= n; i++) {
            int next = a + b;
            a = b;
            b = next;
        }
        return b;
    }

    public static long mix(long a, long b) {
        long x = a ^ (b << 13);
        x = x + (a * 31L);
        return x;
    }
}
