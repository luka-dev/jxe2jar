package cases;

public class InterfaceInvoke {
    public interface Greeter {
        String greet(String name);
    }

    public static class SimpleGreeter implements Greeter {
        public String greet(String name) {
            return "hi " + name;
        }
    }

    public static String run(String name) {
        Greeter g = new SimpleGreeter();
        return g.greet(name);
    }
}
