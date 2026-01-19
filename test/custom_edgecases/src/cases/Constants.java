package cases;

public class Constants {
    public static final int INT_CONST = 123456789;
    public static final long LONG_CONST = 0x1122334455667788L;
    public static final float FLOAT_CONST = 3.14159f;
    public static final double DOUBLE_CONST = 2.718281828;
    public static final String STR_CONST = "constant-string";

    public static int useInts() {
        int x = INT_CONST;
        x = x + 7;
        return x;
    }

    public static long useLongs() {
        long v = LONG_CONST;
        v = v ^ 0xA5A5A5A5A5A5A5A5L;
        return v;
    }

    public static double useDoubles() {
        return DOUBLE_CONST + FLOAT_CONST;
    }

    public static String useStrings() {
        return STR_CONST + ":" + INT_CONST;
    }
}
