package cases;

/**
 * Constant-pool slot typing: int vs float and long vs double share the same ROM slot shapes,
 * so the same bit pattern appears as both kinds in one class, floats flow through ternaries
 * and sit behind wide (long/double) arguments, and the ConstantValue of each kind is checked.
 */
public class FloatTyping {
    public static final float THREE = 3.0f;
    public static final int THREE_BITS = 0x40400000;          // bits of 3.0f, as an int
    public static final long PI_BITS = 0x400921FB54442D18L;   // bits of Math.PI, as a long
    public static final double PI = Math.PI;
    public static final int BIG_INT = 1234567;                // ldc int, not a float
    public static final float TINY = 1.0e-30f;

    static int sink(long l, float f, double d) {
        return (int) (l + f + d);
    }

    static int sinkI(int i) {
        return i;
    }

    static int sinkMany(int a, long b, float c, double d, float e, Object f, String g, float h) {
        return a + (int) b + (int) c + (int) d + (int) e + g.length() + (int) h + (f == null ? 0 : 1);
    }

    static float pickF(boolean c, float x) {
        return c ? 1.5f : x;
    }

    static float pickF2(boolean c, float x) {
        return c ? x : 2.5f;
    }

    static float pickF3(boolean c) {
        return c ? 4.5f : 5.5f;
    }

    static double pickD(boolean c) {
        return c ? 1.25 : 2.75;
    }

    static long pickL(boolean c) {
        return c ? 123456789012L : 2L;
    }

    static int pickI(boolean c) {
        return c ? 0x40400000 : 1234567;
    }

    public static int run(boolean c) {
        float[] fa = { 1.1f, 2.2f, 3.3f };
        double[] da = { 1.1, 2.2 };
        long[] la = { 123456789012L, 2L };
        int r = sink(123456789012L, 3.0f, 4.5) + sinkI(0x40400000) + sinkI(1234567);
        r += sinkMany(7, 123456789012L, 3.0f, 2.75, 6.5f, null, "str", 7.5f);
        r += (int) (fa[1] * THREE) + (int) pickF(c, 9.5f) + (int) pickF2(c, 8.5f) + (int) pickF3(c)
                + (int) pickD(c) + (int) pickL(c) + pickI(c) + (int) da[1] + (int) la[0];
        r += (THREE > 2.5f) ? 1 : 0;
        r += (PI_BITS == Double.doubleToLongBits(PI)) ? 1 : 0;
        r += (THREE_BITS == Float.floatToIntBits(THREE)) ? 1 : 0;
        float neg = -0.0f;
        double nd = -0.0;
        r += (neg == 0.0f && nd == 0.0) ? 1 : 0;
        float f = 1.0e10f;
        f /= 3.0e-5f;
        f += TINY;
        double d = 7.0e100 / 1.0e99;
        return r + (int) f + (int) d + BIG_INT;
    }
}
