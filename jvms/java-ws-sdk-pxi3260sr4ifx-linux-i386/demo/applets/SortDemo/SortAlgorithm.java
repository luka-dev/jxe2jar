/*
 * @(#)src/demo/applets/SortDemo/SortAlgorithm.java, ui, dsdev 1.11
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
 * @(#)SortAlgorithm.java	1.8 02/06/13
 */

/**
 * A generic sort demonstration algorithm
 * SortAlgorithm.java, Thu Oct 27 10:32:35 1994
 *
 * @author James Gosling
 * @version 	1.6f, 31 Jan 1995
 */

class SortAlgorithm {
    /**
     * The sort item.
     */
    private SortItem parent;

    /**
     * When true stop sorting.
     */
    protected boolean stopRequested = false;

    /**
     * Set the parent.
     */
    public void setParent(SortItem p) {
	parent = p;
    }

    /**
     * Pause for a while.
     */
    protected void pause() throws Exception {
	if (stopRequested) {
	    throw new Exception("Sort Algorithm");
	}
	parent.pause(parent.h1, parent.h2);
    }

    /**
     * Pause for a while and mark item 1.
     */
    protected void pause(int H1) throws Exception {
	if (stopRequested) {
	    throw new Exception("Sort Algorithm");
	}
	parent.pause(H1, parent.h2);
    }

    /**
     * Pause for a while and mark item 1 & 2.
     */
    protected void pause(int H1, int H2) throws Exception {
	if (stopRequested) {
	    throw new Exception("Sort Algorithm");
	}
	parent.pause(H1, H2);
    }

    /**
     * Stop sorting.
     */
    public void stop() {
	stopRequested = true;
    }

    /**
     * Initialize
     */
    public void init() {
	stopRequested = false;
    }

    /**
     * This method will be called to
     * sort an array of integers.
     */
    void sort(int a[]) throws Exception {
    }
}
