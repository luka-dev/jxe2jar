/*
 * @(#)src/demo/applets/JumpingBox/JumpingBox.java, awt, dsdev 1.7
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
 * @(#)JumpingBox.java	1.12 02/06/13
 */

import java.awt.event.*;
import java.awt.*;

public class JumpingBox extends java.applet.Applet 
    implements MouseListener, MouseMotionListener, ComponentListener {

    private int mx, my;
    private Dimension size;
    private int onaroll;

    public void init() {
        onaroll = 0;
        setSize(500, 500);
        size = getSize();
        addMouseListener(this);
        addMouseMotionListener(this);
        addComponentListener(this);
    }

    public void update(Graphics g) {
        Dimension newSize = getSize();
        if (size.equals(newSize)) {
            // Erase old box
            g.setColor(getBackground());
            g.drawRect(mx, my, (size.width / 10) - 1, 
                       (size.height / 10) - 1);
        } else {
            size = newSize;
            g.clearRect(0, 0, size.width, size.height);
        }
        // Calculate new position
        mx = (int) (Math.random() * 1000) % 
            (size.width - (size.width / 10));
        my = (int) (Math.random() * 1000) % 
            (size.height - (size.height / 10));
        paint(g);
    }
  
    public void paint(Graphics g) {
        g.setColor(Color.black);
        g.drawRect(0, 0, size.width - 1, size.height - 1);
        g.drawRect(mx, my, (size.width / 10) - 1, 
                   (size.height / 10) - 1);
    }

    /*
     * Mouse methods
     */
    public void mouseDragged(MouseEvent e) {}

    public void mouseMoved(MouseEvent e) {
        e.consume();
        if ((e.getX() % 3 == 0) && (e.getY() % 3 == 0)) {
            repaint();
        }
    }

    public void mousePressed(MouseEvent e) {
        int x = e.getX();
        int y = e.getY();
        e.consume();
        requestFocus();
        if (mx < x && x < mx + getSize().width / 10 - 1 && 
            my < y && y < my + getSize().height / 10 - 1) {  //determine if hit
            if (onaroll > 0) {   //not first hit
                switch (onaroll%4) {   //play a sound
                case 0:
                    play(getCodeBase(), 
                         "sounds/tiptoe.thru.the.tulips.au");
                    break;
                case 1:
                    play(getCodeBase(), "sounds/danger.au");
                    break;
                case 2:
                    play(getCodeBase(), "sounds/adapt-or-die.au");
                    break;
                case 3:
                    play(getCodeBase(), "sounds/cannot.be.completed.au");
                    break;
                }
                onaroll++;
                if (onaroll > 5) {
                    getAppletContext()
                        .showStatus("You're on your way to THE HALL OF FAME:"
                                    + onaroll + "Hits!");
                } else {
                    getAppletContext().showStatus("YOU'RE ON A ROLL:" 
                                                  + onaroll + "Hits!");
                }
            } else {   //first hit
                getAppletContext().showStatus("HIT IT AGAIN! AGAIN!");
                play(getCodeBase(), "sounds/that.hurts.au");
                onaroll = 1;
            }
        } else {   //miss
            getAppletContext().showStatus("You hit nothing at (" + x + ", " 
                                          + y + "), exactly");
            play(getCodeBase(), "sounds/thin.bell.au");
            onaroll = 0;
        }
        repaint();
    }

    public void mouseReleased(MouseEvent e) {}

    public void mouseEntered(MouseEvent e) {
        repaint();
    }

    public void mouseExited(MouseEvent e) {
        repaint();
    }

    public void mouseClicked(MouseEvent e) {}

    public void componentHidden(ComponentEvent e) {}
 
    public void componentMoved(ComponentEvent e) {}
 
    public void componentResized(ComponentEvent e) {
        repaint();
    }
 
    public void componentShown(ComponentEvent e) {
        repaint();
    }
  
    public void destroy() {
        removeMouseListener(this);
        removeMouseMotionListener(this);
    }

    public String getAppletInfo() {
        return "Title: JumpingBox\n"
            + "Author: Anonymous";
    }
}
