/*
 * @(#)src/demo/applets/SortDemo/BubbleSortAlgorithm.java, ui, dsdev 1.11
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
 * @(#)BubbleSortAlgorithm.java	1.8 02/06/13
 */

/**
 * A bubble sort demonstration algorithm
 * SortAlgorithm.java, Thu Oct 27 10:32:35 1994
 *
 * @author James Gosling
 * @version 	1.6f, 31 Jan 1995
 */
class BubbleSortAlgorithm extends SortAlgorithm {
    void sort(int a[]) throws Exception {
	for (int i = a.length; --i>=0; ) {
	    boolean swapped = false;
	    for (int j = 0; j<i; j++) {
		if (stopRequested) {
		    return;
		}
		if (a[j] > a[j+1]) {
		    int T = a[j];
		    a[j] = a[j+1];
		    a[j+1] = T;
		    swapped = true;
		}
		pause(i,j);
	    }
	    if (!swapped)
		return;
	}
    }
}
