/*
 * @(#)src/demo/jfc/Java2D/src/java2d/AnimatingContext.java, dsdev, dsdev 1.6
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
 * @(#)AnimatingContext.java	1.7 02/06/13
 */

package java2d;


/**
 * The interface for a DemoSurface that animates.
 */
public interface AnimatingContext {
        public void step(int w, int h);
        public void reset(int newwidth, int newheight);
}
