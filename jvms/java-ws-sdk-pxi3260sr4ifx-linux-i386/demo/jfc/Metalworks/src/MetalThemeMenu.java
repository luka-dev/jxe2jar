/*
 * @(#)src/demo/jfc/Metalworks/src/MetalThemeMenu.java, swing, dsdev 1.11
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
 * @(#)MetalThemeMenu.java	1.8 02/06/13
 */
 

import javax.swing.plaf.metal.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;

/**
 * This class describes a theme using "green" colors.
 *
 * @version 1.8 06/13/02
 * @author Steve Wilson
 */
public class MetalThemeMenu extends JMenu implements ActionListener{

  MetalTheme[] themes;
  public MetalThemeMenu(String name, MetalTheme[] themeArray) {
    super(name);
    themes = themeArray;
    ButtonGroup group = new ButtonGroup();
    for (int i = 0; i < themes.length; i++) {
        JRadioButtonMenuItem item = new JRadioButtonMenuItem( themes[i].getName() );
	group.add(item);
        add( item );
	item.setActionCommand(i+"");
	item.addActionListener(this);
	if ( i == 0)
	    item.setSelected(true);
    }

  }

  public void actionPerformed(ActionEvent e) {
    String numStr = e.getActionCommand();
    MetalTheme selectedTheme = themes[ Integer.parseInt(numStr) ];
    MetalLookAndFeel.setCurrentTheme(selectedTheme);
    try {
	UIManager.setLookAndFeel("javax.swing.plaf.metal.MetalLookAndFeel");
    } catch (Exception ex) {
        System.out.println("Failed loading Metal");
	System.out.println(ex);
    }

  }

}
