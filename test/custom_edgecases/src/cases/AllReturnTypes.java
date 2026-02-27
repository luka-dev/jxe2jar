package cases;

/**
 * Exercise every JVM return type so that all JBreturn0/1/2 paths
 * (and JBgenericReturn / JBretFromNative* in VM-generated ROM)
 * produce valid output.
 *
 * javac maps:
 *   void     -> return   (0xB1)  — J9 JBreturn0
 *   boolean  -> ireturn  (0xAC)  — J9 JBreturn1
 *   byte     -> ireturn  (0xAC)  — J9 JBreturn1
 *   char     -> ireturn  (0xAC)  — J9 JBreturn1
 *   short    -> ireturn  (0xAC)  — J9 JBreturn1
 *   int      -> ireturn  (0xAC)  — J9 JBreturn1
 *   float    -> freturn  (0xAE)  — J9 JBreturn1
 *   long     -> lreturn  (0xAD)  — J9 JBreturn2
 *   double   -> dreturn  (0xAF)  — J9 JBreturn2
 *   Object   -> areturn  (0xB0)  — J9 JBreturn1
 *   array    -> areturn  (0xB0)  — J9 JBreturn1
 */
public class AllReturnTypes {

    /* --- void -------------------------------------------------------- */

    public static void retVoid() {
        /* nothing */
    }

    public void retVoidInstance() {
        /* nothing */
    }

    /* --- boolean ----------------------------------------------------- */

    public static boolean retBoolean(int x) {
        return x > 0;
    }

    /* --- byte -------------------------------------------------------- */

    public static byte retByte(int x) {
        return (byte)(x & 0xFF);
    }

    /* --- char -------------------------------------------------------- */

    public static char retChar(int x) {
        return (char)(x + 65);
    }

    /* --- short ------------------------------------------------------- */

    public static short retShort(int x) {
        return (short)(x * 2);
    }

    /* --- int --------------------------------------------------------- */

    public static int retInt(int x) {
        return x + 1;
    }

    /* --- float ------------------------------------------------------- */

    public static float retFloat(float x) {
        return x * 2.0f;
    }

    public static float retFloatFromInt(int x) {
        return (float)x;
    }

    public static float retFloatConst() {
        return 3.14f;
    }

    /* --- long -------------------------------------------------------- */

    public static long retLong(long x) {
        return x + 1L;
    }

    public static long retLongFromInt(int x) {
        return (long)x;
    }

    /* --- double ------------------------------------------------------ */

    public static double retDouble(double x) {
        return x + 1.0;
    }

    public static double retDoubleConst() {
        return 2.718281828;
    }

    /* --- Object reference -------------------------------------------- */

    public static Object retObject(Object o) {
        return o;
    }

    public static String retString() {
        return "hello";
    }

    /* --- Array reference --------------------------------------------- */

    public static int[] retIntArray(int n) {
        return new int[n];
    }

    public static Object[] retObjectArray(int n) {
        return new Object[n];
    }

    public static byte[] retByteArray() {
        return new byte[] { 1, 2, 3 };
    }

    /* --- Synchronized returns (exercises JBsyncReturn0/1/2) ---------- */

    private static int counter;

    public static synchronized void syncRetVoid() {
        counter++;
    }

    public static synchronized int syncRetInt() {
        return ++counter;
    }

    public static synchronized float syncRetFloat() {
        return (float)counter;
    }

    public static synchronized long syncRetLong() {
        return (long)counter;
    }

    public static synchronized double syncRetDouble() {
        return (double)counter;
    }

    public static synchronized Object syncRetObject() {
        return new Object();
    }

    /* --- Use everything so nothing is optimized away ----------------- */

    public static void exercise() {
        retVoid();
        new AllReturnTypes().retVoidInstance();
        boolean z = retBoolean(1);
        byte b = retByte(42);
        char c = retChar(0);
        short s = retShort(10);
        int i = retInt(100);
        float f = retFloat(1.5f);
        float f2 = retFloatFromInt(7);
        float f3 = retFloatConst();
        long l = retLong(999L);
        long l2 = retLongFromInt(5);
        double d = retDouble(1.0);
        double d2 = retDoubleConst();
        Object o = retObject("test");
        String str = retString();
        int[] ia = retIntArray(3);
        Object[] oa = retObjectArray(2);
        byte[] ba = retByteArray();
        syncRetVoid();
        int si = syncRetInt();
        float sf = syncRetFloat();
        long sl = syncRetLong();
        double sd = syncRetDouble();
        Object so = syncRetObject();
    }
}