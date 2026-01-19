/*
 * @(#)src/demo/jfc/Metalworks/src/MetalworksDocumentFrame.java, swing, dsdev 1.11
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
 * @(#)MetalworksDocumentFrame.java	1.9 02/06/13
 */

import java.awt.*;
import java.awt.event.*;
import java.util.*;
import javax.swing.*;
import javax.swing.border.*;


/**
  * This is a subclass of JInternalFrame which displays documents.
  *
  * @version 1.9 06/13/02
  * @author Steve Wilson
  */
public class MetalworksDocumentFrame extends JInternalFrame {
  
    static int openFrameCount = 0;
    static final int offset = 30;

    public MetalworksDocumentFrame() {
	super("", true, true, true, true);
	openFrameCount++;
        setTitle("Untitled Message " + openFrameCount);

	JPanel top = new JPanel();
	top.setBorder(new EmptyBorder(10, 10, 10, 10));
	top.setLayout(new BorderLayout());
	top.add(buildAddressPanel(), BorderLayout.NORTH);

	JTextArea content = new JTextArea( 15, 30 );
	content.setBorder( new EmptyBorder(0,5 ,0, 5) );
	content.setLineWrap(true);



	JScrollPane textScroller = new JScrollPane(content, 
						   JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, 
						   JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED );
	top.add( textScroller, BorderLayout.CENTER);
	

	setContentPane(top);
	pack();
	setLocation( offset * openFrameCount, offset *openFrameCount);

    }

    private JPanel buildAddressPanel() {
        JPanel p = new JPanel();
	p.setLayout( new LabeledPairLayout() );
	

	JLabel toLabel = new JLabel("To: ", JLabel.RIGHT);
	JTextField toField = new JTextField(25);
	p.add(toLabel, "label");
	p.add(toField, "field");


	JLabel subLabel = new JLabel("Subj: ", JLabel.RIGHT);
	JTextField subField = new JTextField(25);
	p.add(subLabel, "label");
	p.add(subField, "field");


	JLabel ccLabel = new JLabel("cc: ", JLabel.RIGHT);
	JTextField ccField = new JTextField(25);
	p.add(ccLabel, "label");
	p.add(ccField, "field");

	return p;

    }

    class LabeledPairLayout implements LayoutManager {

      Vector labels = new Vector();
      Vector fields = new Vector();
      
      int yGap = 2;
      int xGap = 2;

      public void addLayoutComponent(String s, Component c) {
	  if (s.equals("label")) {
	      labels.addElement(c);
	  }  else {
	      fields.addElement(c);
	  }
      }

      public void layoutContainer(Container c) {
	  Insets insets = c.getInsets();
	  
	  int labelWidth = 0;
	  Enumeration labelIter = labels.elements();
	  while(labelIter.hasMoreElements()) {
	      JComponent comp = (JComponent)labelIter.nextElement();
	      labelWidth = Math.max( labelWidth, comp.getPreferredSize().width );
	  }

	  int yPos = insets.top;

	  Enumeration fieldIter = fields.elements();
	  labelIter = labels.elements();
	  while(labelIter.hasMoreElements() && fieldIter.hasMoreElements()) {
	      JComponent label = (JComponent)labelIter.nextElement();
	      JComponent field = (JComponent)fieldIter.nextElement();
	      int height = Math.max(label.getPreferredSize().height, field.getPreferredSize().height);
	      label.setBounds( insets.left, yPos, labelWidth, height ); 
	      field.setBounds( insets.left + labelWidth + xGap, 
				 yPos, 
				 c.getSize().width - (labelWidth +xGap + insets.left + insets.right), 
				 height ); 
	      yPos += (height + yGap);
	  }
	  
      }


      public Dimension minimumLayoutSize(Container c) {
	  Insets insets = c.getInsets();
	  
	  int labelWidth = 0;
	  Enumeration labelIter = labels.elements();
	  while(labelIter.hasMoreElements()) {
	      JComponent comp = (JComponent)labelIter.nextElement();
	      labelWidth = Math.max( labelWidth, comp.getPreferredSize().width );
	  }

	  int yPos = insets.top;

	  labelIter = labels.elements();
	  Enumeration fieldIter = fields.elements();
	  while(labelIter.hasMoreElements() && fieldIter.hasMoreElements()) {
	      JComponent label = (JComponent)labelIter.nextElement();
	      JComponent field = (JComponent)fieldIter.nextElement();
	      int height = Math.max(label.getPreferredSize().height, field.getPreferredSize().height);
	      yPos += (height + yGap);
	  }
	  return new Dimension( labelWidth * 3 , yPos );
      }
  
      public Dimension preferredLayoutSize(Container c) {
	  Dimension d = minimumLayoutSize(c);
	  d.width *= 2;
          return d;
      }
   
      public void removeLayoutComponent(Component c) {}

}


}


