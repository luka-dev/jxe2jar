package cases;

/**
 * Exercise sipush-range values (128..32767 / -129..-32768) passed as
 * method arguments - the exact pattern that was zeroed out by the
 * sipush-as-branch bug.
 *
 * javac emits:
 *   iconst   for -1..5
 *   bipush   for -128..127 (excl. iconst range)
 *   sipush   for -32768..32767 (excl. bipush range)
 *   ldc      for anything outside sipush range
 */
public class SipushArgs {

    /* Sink methods - prevent javac from folding constants away. */

    public static int sink(int v) { return v; }
    public static int sink2(int a, int b) { return a + b; }
    public static int sink3(int a, int b, int c) { return a + b + c; }

    /* --- sipush positive values (>= 128) ----------------------------- */

    public static int positiveSmall() {
        return sink(128) + sink(200) + sink(255) + sink(256);
    }

    public static int positiveMedium() {
        return sink(2210) + sink(2220) + sink(2230);
    }

    public static int positiveLarge() {
        return sink(10000) + sink(30000) + sink(32767);
    }

    public static int positiveMultiArg() {
        return sink3(222, 223, 224);
    }

    /* --- sipush negative values (<= -129) ---------------------------- */

    public static int negativeSmall() {
        return sink(-129) + sink(-200) + sink(-256);
    }

    public static int negativeLarge() {
        return sink(-10000) + sink(-30000) + sink(-32768);
    }

    /* --- mixed with bipush/iconst to ensure boundaries are clean ----- */

    public static int boundaries() {
        int x = 0;
        x += sink(-1);      // iconst_m1
        x += sink(0);       // iconst_0
        x += sink(5);       // iconst_5
        x += sink(6);       // bipush
        x += sink(127);     // bipush
        x += sink(128);     // sipush boundary
        x += sink(-128);    // bipush
        x += sink(-129);    // sipush boundary
        return x;
    }

    /* --- sipush as field-like pass (mimics the Audi menu ID pattern) - */

    private int id;

    public void registerEntry(int entryId, short prio) {
        this.id = entryId + prio;
    }

    public void deregisterEntry(int entryId) {
        this.id = this.id - entryId;
    }

    public void menuPattern() {
        registerEntry(2210, (short)9);
        registerEntry(2220, (short)9);
        registerEntry(2230, (short)9);
        registerEntry(600054, (short)9);   // ldc (outside sipush range)
        registerEntry(222, (short)9);
        registerEntry(223, (short)9);
        registerEntry(224, (short)9);
        deregisterEntry(2210);
        deregisterEntry(2220);
        deregisterEntry(2230);
        deregisterEntry(222);
        deregisterEntry(223);
        deregisterEntry(224);
    }

    public int getId() { return id; }

    /* --- sipush in array indexing ------------------------------------- */

    public static int arrayIndex() {
        int[] arr = new int[500];
        arr[128] = 1;
        arr[256] = 2;
        arr[499] = 3;
        return arr[128] + arr[256] + arr[499];
    }

    /* --- sipush in switch cases -------------------------------------- */

    public static int switchSipush(int x) {
        switch (x) {
            case 128:  return 1;
            case 256:  return 2;
            case 2210: return 3;
            case 2220: return 4;
            default:   return 0;
        }
    }
}
