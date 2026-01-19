package cases;

public class TryCatch {
    public static class Boom extends Exception {
        public Boom(String message) {
            super(message);
        }
    }

    public static int riskyDivide(int a, int b) throws Boom {
        if (b == 0) {
            throw new Boom("divide by zero");
        }
        return a / b;
    }

    public static int run(int a, int b) {
        int result = 0;
        try {
            result = riskyDivide(a, b);
            result = result + 10;
        } catch (Boom ex) {
            result = -1;
        } finally {
            result = result + 1;
        }
        return result;
    }
}
