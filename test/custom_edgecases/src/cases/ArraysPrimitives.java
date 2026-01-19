package cases;

public class ArraysPrimitives {
    public static int work() {
        int[] ia = new int[3];
        long[] la = new long[2];
        float[] fa = new float[2];
        double[] da = new double[2];
        byte[] ba = new byte[2];
        char[] ca = new char[2];
        short[] sa = new short[2];
        boolean[] za = new boolean[2];

        ia[0] = 1;
        la[0] = 2L;
        fa[0] = 3.0f;
        da[0] = 4.0d;
        ba[0] = 5;
        ca[0] = 'A';
        sa[0] = 7;
        za[0] = true;

        return ia[0] + (int)la[0] + (int)fa[0] + (int)da[0] + ba[0] + ca[0] + sa[0] + (za[0] ? 1 : 0);
    }
}
