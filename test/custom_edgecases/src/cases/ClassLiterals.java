package cases;

public class ClassLiterals {
    public static Class getHello() {
        return Hello.class;
    }

    public static Class getSelf() {
        return ClassLiterals.class;
    }
}
