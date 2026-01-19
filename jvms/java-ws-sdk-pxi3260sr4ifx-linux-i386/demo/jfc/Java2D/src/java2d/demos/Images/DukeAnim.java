/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Images/DukeAnim.java, dsdev, dsdev 1.6
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
 * @(#)DukeAnim.java	1.16 02/06/13
 */

package java2d.demos.Images;

import java.awt.*;
import javax.swing.JButton;
import java.awt.image.ImageObserver;
import java2d.AnimatingSurface;
import java2d.DemoPanel;


/**
 * Animated gif with a transparent background.
 */
public class DukeAnim extends AnimatingSurface implements ImageObserver {

    private static Image agif, clouds;
    private static int aw, ah, cw;
    private int x;
    private JButton b;


    public DukeAnim() {
        setBackground(Color.white);
        clouds = getImage("clouds.jpg");
        agif = getImage("duke.running.gif");
        aw = agif.getWidth(this) / 2;
        ah = agif.getHeight(this) / 2;
        cw = clouds.getWidth(this);
        dontThread = true;
    }


    public void reset(int w, int h) { 
        b = ((DemoPanel) getParent()).tools.startStopB;
    }


    public void step(int w, int h) { }


    public void render(int w, int h, Graphics2D g2) {
        if ((x -= 3) <= -cw) {
            x = w;
        }
        g2.drawImage(clouds, x, 10, cw, h-20, this);
        g2.drawImage(agif, w/2-aw, h/2-ah, this);
    }


    public boolean imageUpdate(Image img, int infoflags,
                int x, int y, int width, int height)
    {
        if (b.isSelected() && (infoflags & ALLBITS) != 0)
            repaint();
        if (b.isSelected() && (infoflags & FRAMEBITS) != 0)
            repaint();
        return isShowing();
    }



    public static void main(String s[]) {
        createDemoFrame(new DukeAnim());
    }
}
