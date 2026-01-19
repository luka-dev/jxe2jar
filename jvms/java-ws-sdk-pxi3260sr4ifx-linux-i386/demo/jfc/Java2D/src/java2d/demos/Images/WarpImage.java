/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Images/WarpImage.java, dsdev, dsdev 1.6
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
 * @(#)WarpImage.java	1.22 02/06/13
 */

package java2d.demos.Images;

import java.awt.*;
import java.awt.geom.CubicCurve2D;
import java.awt.geom.Point2D;
import java.awt.geom.FlatteningPathIterator;
import java.awt.geom.PathIterator;
import java2d.AnimatingSurface;


/**
 * Warps a image on a CubicCurve2D flattened path.
 */
public class WarpImage extends AnimatingSurface {

    private static int iw, ih, iw2, ih2;
    private static Image img;
    private static final int FORWARD = 0;
    private static final int BACK = 1;
    private Point2D pts[];
    private int direction = FORWARD;
    private int pNum;
    private int x, y;


    public WarpImage() {
        setBackground(Color.white);
        img = getImage("surfing.gif");
        iw = img.getWidth(this);
        ih = img.getHeight(this);
        iw2 = iw/2;
        ih2 = ih/2;
    }


    public void reset(int w, int h) {
        pNum = 0;
        direction = FORWARD;
        CubicCurve2D cc = new CubicCurve2D.Float(
                        w*.2f, h*.5f, w*.4f,0, w*.6f,h,w*.8f,h*.5f);
        PathIterator pi = cc.getPathIterator(null, 0.1);
        Point2D tmp[] = new Point2D[200];
        int i = 0;
        while ( !pi.isDone() ) {
            float[] coords = new float[6];
            switch ( pi.currentSegment(coords) ) {
                case PathIterator.SEG_MOVETO:
                case PathIterator.SEG_LINETO:
                        tmp[i] = new Point2D.Float(coords[0], coords[1]);
            }
            i++;
            pi.next();
        }
        pts = new Point2D[i];
        System.arraycopy(tmp,0,pts,0,i);
    }


    public void step(int w, int h) {
        if (pts == null) {
            return;
        }
        x = (int) pts[pNum].getX();
        y = (int) pts[pNum].getY();
        if (direction == FORWARD)
            if (++pNum == pts.length)
                direction = BACK;
        if (direction == BACK)
            if (--pNum == 0)
                direction = FORWARD;
    }


    public void render(int w, int h, Graphics2D g2) {
        g2.drawImage(img,
                        0,              0,              x,              y,
                        0,              0,              iw2,            ih2,
                        this);
        g2.drawImage(img,
                        x,              0,              w,              y,
                        iw2,            0,              iw,             ih2,
                        this);
        g2.drawImage(img,
                        0,              y,              x,              h,
                        0,              ih2,            iw2,            ih,
                        this);
        g2.drawImage(img,
                        x,              y,              w,              h,
                        iw2,            ih2,            iw,             ih,
                        this);
    }


    public static void main(String argv[]) {
        createDemoFrame(new WarpImage());
    }
}
