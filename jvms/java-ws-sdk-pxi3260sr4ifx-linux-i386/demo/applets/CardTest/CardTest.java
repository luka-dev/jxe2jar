/*
 * @(#)src/demo/applets/CardTest/CardTest.java, ui, dsdev 1.14
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
 * @(#)CardTest.java	1.9 02/06/13
 */

import java.awt.*;
import java.awt.event.*;
import java.applet.Applet;

class CardPanel extends Panel {
    ActionListener listener;

    Panel create(LayoutManager layout) {
	Button b = null;
	Panel p = new Panel();

	p.setLayout(layout);

	b = new Button("one");
	b.addActionListener(listener);
	p.add("North", b);

	b = new Button("two");
	b.addActionListener(listener);
	p.add("West", b);

	b = new Button("three");
	b.addActionListener(listener);
	p.add("South", b);

	b = new Button("four");
	b.addActionListener(listener);
	p.add("East", b);

	b = new Button("five");
	b.addActionListener(listener);
	p.add("Center", b);

	b = new Button("six");
	b.addActionListener(listener);
	p.add("Center", b);

	return p;
    }

    CardPanel(ActionListener actionListener) {
	listener = actionListener;
	setLayout(new CardLayout());
	add("one", create(new FlowLayout()));
	add("two", create(new BorderLayout()));
	add("three", create(new GridLayout(2, 2)));
	add("four", create(new BorderLayout(10, 10)));
	add("five", create(new FlowLayout(FlowLayout.LEFT, 10, 10)));
	add("six", create(new GridLayout(2, 2, 10, 10)));
    }

    public Dimension getPreferredSize() {
	return new Dimension(200, 100);
    }
}

public class CardTest extends Applet
		      implements ActionListener,
				 ItemListener {
    CardPanel cards;

    public CardTest() {
	setLayout(new BorderLayout());
	add("Center", cards = new CardPanel(this));
	Panel p = new Panel();
	p.setLayout(new FlowLayout());
	add("South", p);

	Button b = new Button("first");
	b.addActionListener(this);
	p.add(b);

	b = new Button("next");
	b.addActionListener(this);
	p.add(b);

	b = new Button("previous");
	b.addActionListener(this);
	p.add(b);

	b = new Button("last");
	b.addActionListener(this);
	p.add(b);

	Choice c = new Choice();
	c.addItem("one");
	c.addItem("two");
	c.addItem("three");
	c.addItem("four");
	c.addItem("five");
	c.addItem("six");
	c.addItemListener(this);
	p.add(c);
    }

    public void itemStateChanged(ItemEvent e) {
	((CardLayout)cards.getLayout()).show(cards,
	                                     (String)(e.getItem()));
    }

    public void actionPerformed(ActionEvent e) {
	String arg = e.getActionCommand();

	if ("first".equals(arg)) {
	    ((CardLayout)cards.getLayout()).first(cards);
	} else if ("next".equals(arg)) {
	    ((CardLayout)cards.getLayout()).next(cards);
	} else if ("previous".equals(arg)) {
	    ((CardLayout)cards.getLayout()).previous(cards);
	} else if ("last".equals(arg)) {
	    ((CardLayout)cards.getLayout()).last(cards);
	} else {
	    ((CardLayout)cards.getLayout()).show(cards,(String)arg);
	}
    }

    public static void main(String args[]) {
	Frame f = new Frame("CardTest");
	CardTest cardTest = new CardTest();
	cardTest.init();
	cardTest.start();

	f.add("Center", cardTest);
	f.setSize(300, 300);
	f.show();
    }
    
    public String getAppletInfo() {
        return "Demonstrates the different types of layout managers.";
    }
}
