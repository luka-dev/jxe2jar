/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Paths/Append.java, dsdev, dsdev 1.6
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
 * @(#)Append.java	1.21 02/06/13
 */


package java2d.demos.Paths;

import java.awt.*;
import java.awt.geom.GeneralPath;
import java.awt.geom.Rectangle2D;
import java2d.Surface;


/**
 * Simple append of rectangle to path with & without the connect.
 */
public class Append extends Surface {

    public Append() { 
        setBackground(Color.white);
    }


    public void render(int w, int h, Graphics2D g2) {
        GeneralPath p = new GeneralPath(GeneralPath.WIND_NON_ZERO);
        p.moveTo(w*0.25f, h*0.2f);
        p.lineTo(w*0.75f, h*0.2f);
        p.closePath();
        p.append(new Rectangle2D.Double(w*.4, h*.3, w*.2, h*.1), false);
        g2.setColor(Color.gray);
        g2.fill(p);
        g2.setColor(Color.black);
        g2.draw(p);
        g2.drawString("Append rect to path", (int)(w*.25), (int)(h*.2)-5);

        p.reset();
        p.moveTo(w*0.25f, h*0.6f);
        p.lineTo(w*0.75f, h*0.6f);
        p.closePath();
        p.append(new Rectangle2D.Double(w*.4, h*.7, w*.2, h*.1), true);
        g2.setColor(Color.gray);
        g2.fill(p);
        g2.setColor(Color.black);
        g2.draw(p);
        g2.drawString("Append, connect", (int) (w*.25), (int) (h*.6)-5);
    }


    public static void main(String s[]) {
        createDemoFrame(new Append());
    }
}
