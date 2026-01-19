/*
 * @(#)src/demo/jfc/Java2D/src/java2d/demos/Clipping/Text.java, dsdev, dsdev 1.9
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
 * @(#)Text.java	1.27 02/06/13
 */

package java2d.demos.Clipping;

import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.awt.geom.Line2D;
import java.awt.geom.AffineTransform;
import java.awt.image.BufferedImage;
import java.awt.font.TextLayout;
import java.awt.font.FontRenderContext;
import javax.swing.*;
import java2d.ControlsSurface;
import java2d.CustomControls;


/**
 * Clipping an image, lines, text, texture and gradient with text.
 */
public class Text extends ControlsSurface {

    static Image img;
    static TexturePaint texture;
    static {
        BufferedImage bi = new BufferedImage(5, 5, BufferedImage.TYPE_INT_RGB);
        Graphics2D big = bi.createGraphics();
        big.setBackground(Color.yellow);
        big.clearRect(0,0,5,5);
        big.setColor(Color.red);
        big.fillRect(0,0,3,3);
        texture = new TexturePaint(bi,new Rectangle(0,0,5,5));
    }
    private String clipType = "Lines";
    private DemoControls controls;
    protected boolean doClip = true;


    public Text() {
        setBackground(Color.white);
        img = getImage("clouds.jpg");
        setControls(new Component[] { new DemoControls(this) });
    }


    public void render(int w, int h, Graphics2D g2) {

        FontRenderContext frc = g2.getFontRenderContext();
        Font f = new Font("sansserif",Font.BOLD,32);
        String s = new String("JAVA");
        TextLayout tl = new TextLayout(s, f, frc);
        double sw = tl.getBounds().getWidth();
        double sh = tl.getBounds().getHeight();
        double sx = (w-40)/sw;
        double sy = (h-40)/sh;
        AffineTransform Tx = AffineTransform.getScaleInstance(sx, sy);
        Shape shape = tl.getOutline(Tx);
        sw = shape.getBounds().getWidth();
        sh = shape.getBounds().getHeight();
        Tx = AffineTransform.getTranslateInstance(w/2-sw/2, h/2+sh/2);
        shape = Tx.createTransformedShape(shape);
        Rectangle r = shape.getBounds();

        if (doClip) {
            g2.clip(shape);
        }

        if (clipType.equals("Lines")) {
            g2.setColor(Color.black);
            g2.fill(r);
            g2.setColor(Color.yellow);
            g2.setStroke(new BasicStroke(1.5f));
            for (int j = r.y; j < r.y + r.height; j=j+3) {
                Line2D line = new Line2D.Float( (float) r.x, (float) j,
                                            (float) (r.x+r.width), (float) j);
                g2.draw(line);
            }
        } else if (clipType.equals("Image")) {
            g2.drawImage(img, r.x, r.y, r.width, r.height, null);
        } else if (clipType.equals("TP")) {
            g2.setPaint(texture);
            g2.fill(r);
        } else if (clipType.equals("GP")) {
            g2.setPaint(new GradientPaint(0,0,Color.blue,w,h,Color.yellow));
            g2.fill(r);
        } else if (clipType.equals("Text")) {
            g2.setColor(Color.black);
            g2.fill(shape.getBounds());
            g2.setColor(Color.cyan);
            f = new Font("serif",Font.BOLD,10);
            tl = new TextLayout("java", f, frc);
            sw = tl.getBounds().getWidth();
    
            int x = r.x;
            int y = (int) (r.y + tl.getAscent());
            sh = r.y + r.height;
            while ( y < sh ) {
                tl.draw(g2, x, y);
                if ((x += (int) sw) > (r.x+r.width)) {
                    x = r.x;
                    y += (int) tl.getAscent();
                }
            }
        }
        g2.setClip(new Rectangle(0, 0, w, h));

        g2.setColor(Color.gray);
        g2.draw(shape);
    }


    public static void main(String s[]) {
        createDemoFrame(new Text());
    }


    static class DemoControls extends CustomControls implements ActionListener {

        Text demo;
        JToolBar toolbar;

        public DemoControls(Text demo) {
            super(demo.name);
            this.demo = demo;
            add(toolbar = new JToolBar());
            toolbar.setFloatable(false);
            addTool("Clip", true);
            addTool("Lines", true);
            addTool("Image", false);
            addTool("TP", false);
            addTool("GP", false);
            addTool("Text", false);
        }

        public void addTool(String str, boolean state) {
            JToggleButton b = (JToggleButton) toolbar.add(new JToggleButton(str));
            b.setFocusPainted(false);
            b.setSelected(state);
            b.addActionListener(this);
            int width = b.getPreferredSize().width;
            Dimension prefSize = new Dimension(width, 21);
            b.setPreferredSize(prefSize);
            b.setMaximumSize(prefSize);
            b.setMinimumSize(prefSize);
        }

        public void actionPerformed(ActionEvent e) {
            if (e.getSource().equals(toolbar.getComponentAtIndex(0))) {
                JToggleButton b = (JToggleButton) e.getSource();
                demo.doClip = b.isSelected();
            } else {
                for (int i = 1; i < toolbar.getComponentCount(); i++) {
                    JToggleButton b = (JToggleButton) toolbar.getComponentAtIndex(i);
                    b.setSelected(false);
                }
                JToggleButton b = (JToggleButton) e.getSource();
                b.setSelected(true);
                demo.clipType = b.getText();
            }
            demo.repaint();
        }

        public Dimension getPreferredSize() {
            return new Dimension(200,40);
        }


        public void run() {
            try { thread.sleep(1111); } catch (Exception e) { return; }
            Thread me = Thread.currentThread();
            while (thread == me) {
                for (int i = 1; i < toolbar.getComponentCount()-1; i++) {
                    java2d.Java2Demo.doClickOnDispatchThread((AbstractButton) toolbar.getComponentAtIndex(i));
                    try {
                        thread.sleep(4444);
                    } catch (InterruptedException e) { return; }
                }
            }
            thread = null;
        }
    } // End DemoControls
} // End Text
