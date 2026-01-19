package cases;

public class StaticFinalNonConst {
    public static final Integer BOXED = new Integer(5);
    public static final String STR = new String("hi");
    public static final int[] ARR = new int[] {1, 2, 3};

    public static int sum() {
        return BOXED.intValue() + ARR.length + STR.length();
    }
}
