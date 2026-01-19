package cases;

public class Thrower {
    public static int blow(int x) {
        if (x == 0) {
            throw new IllegalArgumentException("zero");
        }
        return x;
    }

    public static int catchIt(int x) {
        try {
            return blow(x);
        } catch (IllegalArgumentException e) {
            return -1;
        }
    }
}
