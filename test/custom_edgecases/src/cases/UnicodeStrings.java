package cases;

public class UnicodeStrings {
    public static final String EMPTY = "";
    public static final String ASCII = "hello";
    public static final String OMEGA = "\u03A9";
    public static final String SHARP_S = "\u00DF";
    public static final String EMOJI = "\uD83D\uDE80";
    public static final String COMBINING = "A\u030A";
    public static final String LONG = "This is a long string used to test UTF-8 and constant pool handling."
        + " It should stay intact after round-trip conversion.";
}
