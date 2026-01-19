/*
 * @(#)src/demo/jfc/Metalworks/src/GreenMetalTheme.java, swing, dsdev 1.11
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
 * @(#)GreenMetalTheme.java	1.7 02/06/13
 */
 

import javax.swing.plaf.*;
import javax.swing.plaf.metal.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;

/**
 * This class describes a theme using "green" colors.
 *
 * @version 1.7 06/13/02
 * @author Steve Wilson
 */
public class GreenMetalTheme extends DefaultMetalTheme {

    public String getName() { return "Emerald"; }

  // greenish colors
    private final ColorUIResource primary1 = new ColorUIResource(51, 102, 51);
    private final ColorUIResource primary2 = new ColorUIResource(102, 153, 102);
    private final ColorUIResource primary3 = new ColorUIResource(153, 204, 153); 

    protected ColorUIResource getPrimary1() { return primary1; }  
    protected ColorUIResource getPrimary2() { return primary2; } 
    protected ColorUIResource getPrimary3() { return primary3; } 

}
