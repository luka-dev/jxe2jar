/*
 * @(#)src/demo/jfc/Font2DTest/src/Font2DTestApplet.java, font, dsdev 1.7
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
 * @(#)Font2DTestApplet.java	1.8 02/06/13
 */

import java.awt.AWTPermission;
import java.awt.Frame;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.*;

/**
 * Font2DTestApplet.java
 *
 * @version @(#)Font2DTestApplet.java	1.1 00/08/22
 * @author Shinsuke Fukuda
 * @author Ankit Patel [Conversion to Swing - 01/07/30]  
 */

/// Applet version of Font2DTest that wraps the actual demo

public final class Font2DTestApplet extends JApplet {
    public void init() {
        /// Check if necessary permission is given...
        SecurityManager security = System.getSecurityManager();
        if ( security != null ) {
            try {
                security.checkPermission( new AWTPermission( "showWindowWithoutWarningBanner" ));
            }
            catch ( SecurityException e ) {
                System.out.println( "NOTE: showWindowWithoutWarningBanner AWTPermission not given.\n" +
                                    "Zoom window will contain warning banner at bottom when shown\n" );
            }
            try {
                security.checkPrintJobAccess();
            }
            catch ( SecurityException e ) {
                System.out.println( "NOTE: queuePrintJob RuntimePermission not given.\n" +
                                    "Printing feature will not be available\n" );
            }
        }
        
        final JFrame f = new JFrame( "Font2DTest" );
        final Font2DTest f2dt = new Font2DTest( f, true );
        f.addWindowListener( new WindowAdapter() {
            public void windowClosing( WindowEvent e ) { f.dispose(); }
        });

        f.getContentPane().add( f2dt );
        f.pack();
        f.show();
    }
}
