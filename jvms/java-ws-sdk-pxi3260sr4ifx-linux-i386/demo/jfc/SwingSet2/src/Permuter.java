/*
 * @(#)src/demo/jfc/SwingSet2/src/Permuter.java, swing, dsdev 1.11
 * ===========================================================================
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 *
 * IBM SDK, Java(tm) 2 Technology Edition, v5.0
 * (C) Copyright IBM Corp. 1998, 2005. All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 * ===========================================================================
 */

/*
 * ===========================================================================
 (C) Copyright Sun Microsystems Inc, 1992, 2004. All rights reserved.
 * ===========================================================================
 */





/*
 * @(#)Permuter.java	1.5 02/06/13
 */



import java.util.Random;

/**
 * An object that implements a cheesy pseudorandom permutation of the integers
 * from zero to some user-specified value. (The permutation is a linear
 * function.) 
 *
 * @version 1.5 06/13/02
 * @author Josh Bloch
 */
class Permuter {
    /**
     * The size of the permutation.
     */
    private int modulus;

    /**
     * Nonnegative integer less than n that is relatively prime to m.
     */
    private int multiplier;

    /**
     * Pseudorandom nonnegative integer less than n.
     */
    private int addend = 22;

    public Permuter(int n) {
        if (n<0) {
            throw new IllegalArgumentException();
	}
        modulus = n;
        if (n==1) {
            return;
	}

        // Initialize the multiplier and offset
        multiplier = (int) Math.sqrt(n);
        while (gcd(multiplier, n) != 1) {
            if (++multiplier == n) {
                multiplier = 1;
	    }
	}
    }

    /**
     * Returns the integer to which this permuter maps the specified integer.
     * The specified integer must be between 0 and n-1, and the returned
     * integer will be as well.
     */
    public int map(int i) {
        return (multiplier * i + addend) % modulus;
    }

    /**
     * Calculate GCD of a and b, which are assumed to be non-negative.
     */
    private static int gcd(int a, int b) {
        while(b != 0) {
            int tmp = a % b;
            a = b;
            b = tmp;
        }
        return a;
    }

    /**
     * Simple test.  Takes modulus on command line and prints out permutation.
     */
    public static void main(String[] args) {
        int modulus = Integer.parseInt(args[0]);
        Permuter p = new Permuter(modulus);
        for (int i=0; i<modulus; i++) {
            System.out.print(p.map(i)+" ");
	}
        System.out.println();
    }
}

