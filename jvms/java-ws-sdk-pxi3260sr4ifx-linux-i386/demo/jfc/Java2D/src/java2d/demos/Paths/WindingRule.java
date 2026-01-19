/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Paths/WindingRule.java, dsdev, dsdev 1.6
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
 * @(#)WindingRule.java	1.21 02/06/13
 */

package java2d.demos.Paths;

import java.awt.*;
import java.awt.geom.GeneralPath;
import java2d.Surface;


/**
 * Rectangles filled to illustrate the GenerPath winding rule, determining
 * the interior of a path.
 */
public class WindingRule extends Surface {

    public WindingRule() {
        setBackground(Color.white);
    }


    public void render(int w, int h, Graphics2D g2) {

        g2.translate(w*.2, h*.2);

        GeneralPath p = new GeneralPath(GeneralPath.WIND_NON_ZERO);
        p.moveTo(0.0f, 0.0f);
        p.lineTo(w*.5f, 0.0f);
        p.lineTo(w*.5f, h*.2f);
        p.lineTo(0.0f, h*.2f);
        p.closePath();

        p.moveTo(w*.05f, h*.05f);
        p.lineTo(w*.55f, h*.05f);
        p.lineTo(w*.55f, h*.25f);
        p.lineTo(w*.05f, h*.25f);
        p.closePath();

        g2.setColor(Color.lightGray);
        g2.fill(p);
        g2.setColor(Color.black);
        g2.draw(p);
        g2.drawString("NON_ZERO rule", 0, -5);

        g2.translate(0.0f, h*.45);

        p.setWindingRule(GeneralPath.WIND_EVEN_ODD);
        g2.setColor(Color.lightGray);
        g2.fill(p);
        g2.setColor(Color.black);
        g2.draw(p);
        g2.drawString("EVEN_ODD rule", 0, -5);
    }

    public static void main(String s[]) {
        createDemoFrame(new WindingRule());
    }
}
