package cases;

public class Inheritance {
    public interface Greeter {
        String greet(String name);
    }

    public static abstract class Base implements Greeter {
        protected String prefix;

        public Base(String prefix) {
            this.prefix = prefix;
        }

        public String greet(String name) {
            return prefix + ":" + name;
        }

        public abstract int score(int value);
    }

    public static class Child extends Base {
        public Child(String prefix) {
            super(prefix);
        }

        public int score(int value) {
            return value * 2 + 1;
        }
    }

    public static String run(String name, int value) {
        Base child = new Child("hi");
        return child.greet(name) + "=" + child.score(value);
    }
}
