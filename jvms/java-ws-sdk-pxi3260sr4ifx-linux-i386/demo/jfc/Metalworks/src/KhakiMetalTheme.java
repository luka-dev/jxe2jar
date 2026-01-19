/*
 * @(#)src/demo/jfc/Metalworks/src/KhakiMetalTheme.java, swing, dsdev 1.11
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
 * @(#)KhakiMetalTheme.java	1.7 02/06/13
 */


import javax.swing.plaf.*;
import javax.swing.plaf.metal.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;

/**
 * This class describes a theme using "khaki" colors.
 *
 * @version 1.7 06/13/02
 * @author Steve Wilson
 */
public class KhakiMetalTheme extends DefaultMetalTheme {

    public String getName() { return "Sandstone"; }

    private final ColorUIResource primary1 = new ColorUIResource( 87,  87,  47);
    private final ColorUIResource primary2 = new ColorUIResource(159, 151, 111);
    private final ColorUIResource primary3 = new ColorUIResource(199, 183, 143);

    private final ColorUIResource secondary1 = new ColorUIResource( 111,  111,  111);
    private final ColorUIResource secondary2 = new ColorUIResource(159, 159, 159);
    private final ColorUIResource secondary3 = new ColorUIResource(231, 215, 183);

    protected ColorUIResource getPrimary1() { return primary1; }
    protected ColorUIResource getPrimary2() { return primary2; }
    protected ColorUIResource getPrimary3() { return primary3; }

    protected ColorUIResource getSecondary1() { return secondary1; }
    protected ColorUIResource getSecondary2() { return secondary2; }
    protected ColorUIResource getSecondary3() { return secondary3; }

}
