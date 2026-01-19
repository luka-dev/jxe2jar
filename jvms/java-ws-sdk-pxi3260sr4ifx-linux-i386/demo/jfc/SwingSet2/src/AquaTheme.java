/*
 * @(#)src/demo/jfc/SwingSet2/src/AquaTheme.java, swing, dsdev 1.11
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
 * @(#)AquaTheme.java	1.6 02/06/13
 */


import javax.swing.plaf.*;
import javax.swing.plaf.metal.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;

/**
 * This class describes a theme using "blue-green" colors.
 *
 * 1.6 06/13/02
 * @author Steve Wilson
 */
public class AquaTheme extends DefaultMetalTheme {

    public String getName() { return "Aqua"; }

    private final ColorUIResource primary1 = new ColorUIResource(102, 153, 153);
    private final ColorUIResource primary2 = new ColorUIResource(128, 192, 192);
    private final ColorUIResource primary3 = new ColorUIResource(159, 235, 235);

    protected ColorUIResource getPrimary1() { return primary1; }
    protected ColorUIResource getPrimary2() { return primary2; }
    protected ColorUIResource getPrimary3() { return primary3; }

}
