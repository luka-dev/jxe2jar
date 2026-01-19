package cases;

public class MultiArray {
    public static int sum(int n) {
        int[][][] a = new int[2][3][4];
        a[1][2][3] = n;
        return a[1][2][3];
    }

    public static Object makeObj(int n) {
        String[][] s = new String[2][n];
        s[0][0] = "x";
        return s;
    }
}
