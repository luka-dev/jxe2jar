package cases;

public class FloatDoubleBits {
    public static final float F_NAN = Float.NaN;
    public static final float F_POS_INF = Float.POSITIVE_INFINITY;
    public static final float F_NEG_INF = Float.NEGATIVE_INFINITY;
    public static final float F_POS_ZERO = 0.0f;
    public static final float F_NEG_ZERO = -0.0f;

    public static final double D_NAN = Double.NaN;
    public static final double D_POS_INF = Double.POSITIVE_INFINITY;
    public static final double D_NEG_INF = Double.NEGATIVE_INFINITY;
    public static final double D_POS_ZERO = 0.0d;
    public static final double D_NEG_ZERO = -0.0d;

    public static final float F_BITS = Float.intBitsToFloat(0x7fc12345);
    public static final double D_BITS = Double.longBitsToDouble(0x7ff8000000000001L);

    public static int fBits() {
        return Float.floatToIntBits(F_BITS);
    }

    public static long dBits() {
        return Double.doubleToLongBits(D_BITS);
    }
}
