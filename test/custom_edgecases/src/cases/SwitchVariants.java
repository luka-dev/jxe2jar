package cases;

public class SwitchVariants {
    public static int dense(int x) {
        switch (x) {
            case 0: return 10;
            case 1: return 11;
            case 2: return 12;
            case 3: return 13;
            case 4: return 14;
            case 5: return 15;
            case 6: return 16;
            case 7: return 17;
            case 8: return 18;
            case 9: return 19;
            case 10: return 20;
            default: return -1;
        }
    }

    public static int sparse(int x) {
        switch (x) {
            case -1000: return -1;
            case -1: return 1;
            case 5: return 5;
            case 100: return 100;
            case 1000: return 1000;
            case 10000: return 10000;
            default: return 0;
        }
    }
}
