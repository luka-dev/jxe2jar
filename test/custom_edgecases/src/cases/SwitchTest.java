package cases;

public class SwitchTest {
    public static int denseSwitch(int v) {
        int out;
        switch (v) {
            case 0:
                out = 10;
                break;
            case 1:
                out = 11;
                break;
            case 2:
                out = 12;
                break;
            case 3:
                out = 13;
                break;
            default:
                out = -1;
                break;
        }
        return out;
    }

    public static int sparseSwitch(int v) {
        int out;
        switch (v) {
            case -10:
                out = 1;
                break;
            case 7:
                out = 2;
                break;
            case 100:
                out = 3;
                break;
            case 1000:
                out = 4;
                break;
            default:
                out = 0;
                break;
        }
        return out;
    }
}
