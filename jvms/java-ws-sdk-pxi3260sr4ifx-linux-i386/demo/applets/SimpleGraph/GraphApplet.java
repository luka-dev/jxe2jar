/*
 * @(#)src/demo/applets/SimpleGraph/GraphApplet.java, ui, dsdev 1.11
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
 * @(#)GraphApplet.java	1.6 02/06/13
 */

import java.awt.Graphics;

public class GraphApplet extends java.applet.Applet {
    double f(double x) {
	return (Math.cos(x/5) + Math.sin(x/7) + 2) * getSize().height / 4;
    }

    public void paint(Graphics g) {
        for (int x = 0 ; x < getSize().width ; x++) {
	    g.drawLine(x, (int)f(x), x + 1, (int)f(x + 1));
        }
    }
  public String getAppletInfo() {
    return "Draws a sin graph.";
  }
}
