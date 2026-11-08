package cases;

/**
 * Every call shape the J9 romizer may or may not devirtualise (invokevirtual -> invokespecial):
 * own final / inherited final / private / super / Outer.super (javac access$N01 accessor) /
 * final class / Object's final methods on receivers of every static type.
 */
public class FinalCalls {
    public static class Base {
        public final int fin(int x) {
            return x + 1;
        }

        public int virt() {
            return 1;
        }

        public final String tag() {
            return "base";
        }
    }

    public static class Derived extends Base {
        public final int ownFin(int x) {
            return x * 2;
        }

        private int priv(int x) {
            return x - 1;
        }

        public int virt() {
            return 2;
        }

        // own final via this, inherited final via this, private via this
        public int viaThis() {
            return ownFin(1) + fin(2) + priv(3);
        }

        // own final / inherited final / private on another instance, inherited final via Base
        public int viaOther(Derived d, Base b) {
            return d.ownFin(1) + d.fin(2) + d.priv(3) + b.fin(4);
        }

        // super call of a non-final and of a final method
        public int viaSuper() {
            return super.virt() + super.fin(5);
        }

        public String tags() {
            return tag() + super.tag();
        }

        // Outer.super.m() from an inner class: javac emits a static access$N01 accessor that
        // does invokespecial Base.m on its parameter - a genuine javac invokespecial with a
        // non-this receiver, which must survive conversion untouched.
        class Inner {
            int f() {
                return Derived.super.virt() + Derived.super.fin(6);
            }
        }

        public int inner() {
            return new Inner().f();
        }
    }

    public static final class Sealed {
        public int m(int x) {
            return x + 7;
        }

        public int self() {
            return m(1);
        }
    }

    public static int objectFinals(Object o, String s, Runnable r, int[] a, Base b)
            throws InterruptedException {
        int h = o.getClass().hashCode() + s.getClass().hashCode() + r.getClass().hashCode()
                + a.getClass().hashCode() + b.getClass().hashCode();
        synchronized (o) {
            o.notify();
            o.notifyAll();
            o.wait(1L);
            o.wait(1L, 1);
        }
        synchronized (s) {
            s.notify();
            s.wait(1L);
        }
        synchronized (b) {
            b.notifyAll();
            b.wait(2L, 2);
        }
        return h;
    }

    public int thisGetClass() {
        return getClass().hashCode() + this.getClass().getName().length();
    }

    public static int run() {
        Derived d = new Derived();
        return d.viaThis() + d.viaOther(d, d) + d.viaSuper() + d.tags().length() + d.inner()
                + new Sealed().self() + new FinalCalls().thisGetClass();
    }
}
