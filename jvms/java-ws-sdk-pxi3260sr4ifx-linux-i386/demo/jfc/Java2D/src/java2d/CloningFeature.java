/*
 * @(#)src/demo/jfc/Java2D/src/java2d/CloningFeature.java, dsdev, dsdev 1.8
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
 * @(#)CloningFeature.java	1.19 02/06/13
 */


package java2d;

import java.awt.Component;
import java.awt.Color;
import java.awt.Font;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.event.MouseEvent;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.border.EmptyBorder;
import javax.swing.border.SoftBevelBorder;
import javax.swing.border.CompoundBorder;

/**
 * Illustration of how to use the clone feature of the demo.
 */
public class CloningFeature extends JPanel implements Runnable {

    private Thread thread;
    private JTextArea ta;


    public CloningFeature() {

        setLayout(new BorderLayout());
        EmptyBorder eb = new EmptyBorder(5,5,5,5);
        SoftBevelBorder sbb = new SoftBevelBorder(SoftBevelBorder.RAISED);
        setBorder(new CompoundBorder(eb, sbb));

        ta = new JTextArea("Cloning Demonstrated\n\nClicking once on a demo\n");
        ta.setMinimumSize(new Dimension(300,500));
        JScrollPane scroller = new JScrollPane();
        scroller.getViewport().add(ta);
        ta.setFont(new Font("Dialog", Font.PLAIN, 14));
        ta.setForeground(Color.black);
        ta.setBackground(Color.lightGray);
        ta.setEditable(false);

        add("Center", scroller);

        start();
    }

    public void start() {
        thread = new Thread(this);
        thread.setPriority(Thread.MAX_PRIORITY);
        thread.setName("CloningFeature");
        thread.start();
    }

    public void stop() {
        if (thread != null && thread.isAlive()) { /*ibm@63240*/
            thread.interrupt();
        }
        thread = null;
    }


    public void run() {


        int index = Java2Demo.tabbedPane.getSelectedIndex();
        if (index == 0) {
           Java2Demo.tabbedPane.setSelectedIndex(1);
           try { thread.sleep(3333); } catch (Exception e) { return; }
        }

        if (!Java2Demo.controls.toolBarCB.isSelected()) {
            Java2Demo.controls.toolBarCB.setSelected(true);
            try { thread.sleep(2222); } catch (Exception e) { return; }
        }

        index = Java2Demo.tabbedPane.getSelectedIndex()-1;
        DemoGroup dg = Java2Demo.group[index];
        DemoPanel dp = (DemoPanel) dg.getPanel().getComponent(0);
        if (dp.surface == null) {
            ta.append("Sorry your zeroth component is not a Surface.");
            return;
        } 

        dg.mouseClicked(new MouseEvent(dp.surface, MouseEvent.MOUSE_CLICKED, 0, 0, 10, 10, 1, false));

        try { thread.sleep(3333); } catch (Exception e) { return; }

        ta.append("Clicking the ToolBar double document button\n");
        try { thread.sleep(3333); } catch (Exception e) { return; }

        dp = (DemoPanel) dg.clonePanels[0].getComponent(0);

        if (dp.tools != null) {
            for (int i = 0; i < 3 && thread != null; i++) {
                ta.append("   Cloning\n");
                Java2Demo.doClickOnDispatchThread(dp.tools.cloneB);
                try { thread.sleep(3333); } catch (Exception e) { return; }
            }
        }

        ta.append("Changing attributes \n");

        try { thread.sleep(3333); } catch (Exception e) { return; }

        Component cmps[] = dg.clonePanels[0].getComponents();
        for (int i = 0; i < cmps.length && thread != null; i++) {
            if ((dp = (DemoPanel) cmps[i]).tools == null) {
                continue;
            }
            switch (i) {
                case 0 : ta.append("   Changing AntiAliasing\n");
                    Java2Demo.doClickOnDispatchThread(dp.tools.aliasB);
                    break;
                case 1 : ta.append("   Changing Composite & Texture\n");
                    Java2Demo.doClickOnDispatchThread(dp.tools.compositeB);
                    Java2Demo.doClickOnDispatchThread(dp.tools.textureB);
                    break;
                case 2 : ta.append("   Changing Screen\n");
                    dp.tools.screenCombo.setSelectedIndex(4);
                    break;
                case 3 : ta.append("   Removing a clone\n");
                    Java2Demo.doClickOnDispatchThread(dp.tools.cloneB);
            }
            try { thread.sleep(3333); } catch (Exception e) { return; }
        }

        ta.append("\nAll Done!");
    }
}
