package cases;

public class InnerClasses {
    private int base;

    public InnerClasses(int base) {
        this.base = base;
    }

    public class Adder {
        public int add(int value) {
            return base + value;
        }
    }

    public static class Multiplier {
        private int factor;

        public Multiplier(int factor) {
            this.factor = factor;
        }

        public int mul(int value) {
            return value * factor;
        }
    }

    public int run(int value) {
        Adder adder = new Adder();
        Multiplier mul = new Multiplier(3);
        return mul.mul(adder.add(value));
    }
}
