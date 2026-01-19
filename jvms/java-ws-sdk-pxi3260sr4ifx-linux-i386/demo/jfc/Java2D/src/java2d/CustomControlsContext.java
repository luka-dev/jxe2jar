/*
 * @(#)src/demo/jfc/Java2D/src/java2d/CustomControlsContext.java, dsdev, dsdev 1.6
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
 * @(#)CustomControlsContext.java	1.10 02/06/13
 */

package java2d;

import java.awt.Component;

/**
 * ControlsSurface or AnimatingControlsSurface classes implement 
 * this interface.
 */
public interface CustomControlsContext {

    public static final int START = 0;
    public static final int STOP = 1;

    public String[] getConstraints();
    public Component[] getControls();
    public void setControls(Component[] controls);
    public void setConstraints(String[] constraints);
    public void handleThread(int state);
}
