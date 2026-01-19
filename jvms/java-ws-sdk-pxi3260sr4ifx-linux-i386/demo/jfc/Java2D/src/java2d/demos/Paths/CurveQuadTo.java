/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Paths/CurveQuadTo.java, dsdev, dsdev 1.6
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
 * @(#)CurveQuadTo.java	1.21 02/06/13
 */

package java2d.demos.Paths;

import java.awt.*;
import java.awt.geom.GeneralPath;
import java2d.Surface;


/**
 * Cubic & Quad curves implemented through GeneralPath.
 */
public class CurveQuadTo extends Surface {

    public CurveQuadTo() {
        setBackground(Color.white);
    }


    public void render(int w, int h, Graphics2D g2) {
        GeneralPath p = new GeneralPath(GeneralPath.WIND_EVEN_ODD);
        p.moveTo(w*.2f, h*.25f);
        p.curveTo(w*.4f, h*.5f, w*.6f, 0.0f, w*.8f, h*.25f);
        p.moveTo(w*.2f, h*.6f);
        p.quadTo(w*.5f, h*1.0f, w*.8f, h*.6f);
        g2.setColor(Color.lightGray);
        g2.fill(p);
        g2.setColor(Color.black);
        g2.draw(p);
        g2.drawString("curveTo", (int) (w*.2), (int) (h*.25f)-5);
        g2.drawString("quadTo", (int) (w*.2), (int) (h*.6f)-5);
    }

    public static void main(String s[]) {
        createDemoFrame(new CurveQuadTo());
    }
}
