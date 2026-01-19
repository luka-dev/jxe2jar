/*
 * @(#)src/demo/jfc/SwingSet2/src/ProgressBarDemo.java, swing, dsdev 1.13
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
 * @(#)ProgressBarDemo.java	1.6 02/06/13
 */


import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;
import javax.swing.border.*;
import javax.swing.colorchooser.*;
import javax.swing.filechooser.*;
import javax.accessibility.*;

import java.awt.*;
import java.awt.event.*;
import java.beans.*;
import java.util.*;
import java.io.*;
import java.applet.*;
import java.net.*;

/**
 * JProgressBar Demo
 *
 * @version 1.6 06/13/02
 * @author Jeff Dinkins
 # @author Peter Korn (accessibility support)
 */
public class ProgressBarDemo extends DemoModule {

    /**
     * main method allows us to run as a standalone demo.
     */
    public static void main(String[] args) {
	ProgressBarDemo demo = new ProgressBarDemo(null);
	demo.mainImpl();
    }

    /**
     * ProgressBarDemo Constructor
     */
    public ProgressBarDemo(SwingSet2 swingset) {
	// Set the title for this demo, and an icon used to represent this
	// demo inside the SwingSet2 app.
	super(swingset, "ProgressBarDemo", "toolbar/JProgressBar.gif");

	createProgressPanel();
    }

    javax.swing.Timer timer;
    Action loadAction;
    Action stopAction;
    JProgressBar progressBar;
    JTextArea progressTextArea;
    void updateDragEnabled(boolean dragEnabled) {
        progressTextArea.setDragEnabled(dragEnabled);
    }
    
    public void createProgressPanel() {
	getDemoPanel().setLayout(new BorderLayout());

	JPanel textWrapper = new JPanel(new BorderLayout());
	textWrapper.setBorder(new SoftBevelBorder(BevelBorder.LOWERED));
	textWrapper.setAlignmentX(LEFT_ALIGNMENT);
	progressTextArea = new MyTextArea();
	progressTextArea.getAccessibleContext().setAccessibleName(getString("ProgressBarDemo.accessible_text_area_name"));
	progressTextArea.getAccessibleContext().setAccessibleName(getString("ProgressBarDemo.accessible_text_area_description"));
	textWrapper.add(new JScrollPane(progressTextArea), BorderLayout.CENTER);

	getDemoPanel().add(textWrapper, BorderLayout.CENTER);

	JPanel progressPanel = new JPanel();
	getDemoPanel().add(progressPanel, BorderLayout.SOUTH);

	progressBar = new JProgressBar(JProgressBar.HORIZONTAL, 0, text.length()) {
	    public Dimension getPreferredSize() {
		return new Dimension(300, super.getPreferredSize().height);
	    }
	};
	progressBar.getAccessibleContext().setAccessibleName(getString("ProgressBarDemo.accessible_text_loading_progress"));

	progressPanel.add(progressBar);
	progressPanel.add(createLoadButton());
	progressPanel.add(createStopButton());
    }

    public JButton createLoadButton() {
	loadAction = new AbstractAction(getString("ProgressBarDemo.start_button")) {
	    public void actionPerformed(ActionEvent e) {
		if(timer == null) {
		    loadAction.setEnabled(false);
		    stopAction.setEnabled(true);
                    if(progressBar.getValue() == progressBar.getMaximum()) {
                        // start again from the beginning
                        progressBar.setValue(0);
                        progressTextArea.setText("");
                        textLocation = 0;
                    }
		    timer = new javax.swing.Timer(18, createTextLoadAction());
		    timer.start();
		}
	    }
	};
	return createButton(loadAction);
    }

    public JButton createStopButton() {
	stopAction = new AbstractAction(getString("ProgressBarDemo.stop_button")) {
	    public void actionPerformed(ActionEvent e) {
		if(timer != null) {
		    timer.stop();
		    timer = null;
		}
		loadAction.setEnabled(true);
		stopAction.setEnabled(false);
	    }
	};
	return createButton(stopAction);
    }

    public JButton createButton(Action a) {
	JButton b = new JButton();
	// setting the following client property informs the button to show
	// the action text as it's name. The default is to not show the
	// action text.
	b.putClientProperty("displayActionText", Boolean.TRUE);
	b.setAction(a);
	return b;
    }


    int textLocation = 0;

    String text = getString("ProgressBarDemo.text");

    public Action createTextLoadAction() {
	return new AbstractAction("text load action") {
	    public void actionPerformed (ActionEvent e) {
		if(progressBar.getValue() < progressBar.getMaximum()) {
		    progressBar.setValue(progressBar.getValue() + 1);
		    progressTextArea.append(text.substring(textLocation, textLocation+1));
		    textLocation++;
		} else {
		    if(timer != null) {
			timer.stop();
			timer = null;
			loadAction.setEnabled(true);
			stopAction.setEnabled(false);
		    }
		}
	    }
	};
    }


    class MyTextArea extends JTextArea {
        public MyTextArea() {
            super(null, 0, 0);
	    setEditable(false);
	    setText("");
        }

        public float getAlignmentX () {
            return LEFT_ALIGNMENT;
        }
 
        public float getAlignmentY () {
            return TOP_ALIGNMENT;
        }
    }
}


