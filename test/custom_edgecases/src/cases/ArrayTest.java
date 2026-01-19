package cases;

public class ArrayTest {
    public static int sum2d(int[][] values) {
        int total = 0;
        if (values == null) {
            return 0;
        }
        for (int i = 0; i < values.length; i++) {
            int[] row = values[i];
            if (row == null) {
                continue;
            }
            for (int j = 0; j < row.length; j++) {
                total += row[j];
            }
        }
        return total;
    }

    public static String[][] makeGrid(int w, int h) {
        String[][] grid = new String[h][w];
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                grid[y][x] = "" + x + "," + y;
            }
        }
        return grid;
    }
}
