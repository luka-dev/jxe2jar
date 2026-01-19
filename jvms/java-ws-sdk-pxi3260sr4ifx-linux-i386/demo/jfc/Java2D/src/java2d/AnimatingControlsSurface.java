/*
 * @(#)src/demo/jfc/Java2D/src/java2d/AnimatingControlsSurface.java, dsdev, dsdev 1.6
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
 * @(#)AnimatingControlsSurface.java	1.5 02/06/13
 */

package java2d;

import java.awt.Component;


/**
 * Demos that animate and have custom controls extend this class.
 */
public abstract class AnimatingControlsSurface extends AnimatingSurface implements CustomControlsContext {


    public void setControls(Component[] controls) {
        this.controls = controls;
    }
  
    public void setConstraints(String[] constraints) {
        this.constraints = constraints;
    }
    
    public String[] getConstraints() {
        return constraints;
    }

    public Component[] getControls() { 
        return controls;
    }

    public void handleThread(int state) {
        for (int i = 0; i < controls.length; i++) {
            if (state == CustomControlsContext.START) {
                if (controls[i] instanceof CustomControls) {
                    ((CustomControls) controls[i]).start();
                }
            } else if (state == CustomControlsContext.STOP) {
                if (controls[i] instanceof CustomControls) {
                    ((CustomControls) controls[i]).stop();
                }
            }
        }
    }


    private Component[] controls;
    private String[] constraints = { java.awt.BorderLayout.NORTH };
}
