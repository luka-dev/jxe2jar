package cases;

public class CompareOps {
    public static int cmp(long a, long b) {
        if (a == b) return 0;
        if (a < b) return -1;
        return 1;
    }

    public static int cmpf(float a, float b) {
        if (a < b) return -1;
        if (a > b) return 1;
        return 0;
    }

    public static int cmpd(double a, double b) {
        if (a < b) return -1;
        if (a > b) return 1;
        return 0;
    }

    public static boolean acmp(Object a, Object b) {
        return a == b;
    }

    public static int shift(int x, int s) {
        return (x << s) ^ (x >>> s) ^ (x >> s);
    }

    public static int bit(int x, int y) {
        return (x & y) | (x ^ y);
    }

    public static int conv(double d) {
        return (int)d + (int)((long)d) + (int)((float)d);
    }
}
