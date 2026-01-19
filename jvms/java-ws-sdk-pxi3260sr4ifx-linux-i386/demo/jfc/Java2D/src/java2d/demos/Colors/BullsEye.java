/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Colors/BullsEye.java, dsdev, dsdev 1.6
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
 * @(#)BullsEye.java	1.15 02/06/13
 */

package java2d.demos.Colors;

import java.awt.*;
import java.awt.geom.Ellipse2D;
import java2d.Surface;


/**
 * Creating colors with an alpha value.
 */
public class BullsEye extends Surface {


    public BullsEye() {
        setBackground(Color.white);
    }


    public void render(int w, int h, Graphics2D g2) {

        Color reds[] = { Color.red.darker(), Color.red };
        for (int N = 0; N < 18; N++) {
            float i = (N + 2) / 2.0f;
            float x = (float) (5+i*(w/2/10));
            float y = (float) (5+i*(h/2/10));
            float ew = (w-10)-(i*w/10);
            float eh = (h-10)-(i*h/10);
            float alpha = (N == 0) ? 0.1f : 1.0f / (19.0f - N);
            if ( N >= 16 )
                g2.setColor(reds[N-16]);
            else
                g2.setColor(new Color(0f, 0f, 0f, alpha));
            g2.fill(new Ellipse2D.Float(x,y,ew,eh));
        }
    }


    public static void main(String s[]) {
        createDemoFrame(new BullsEye());
    }
}
