/*
 * @(#)src/demo/applets/ImageMap/LinkArea.java, ui, dsdev 1.11
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
 * @(#)LinkArea.java	1.11 02/06/13
 */

import java.awt.Graphics;
import java.net.URL;
import java.net.MalformedURLException;

/**
 * The classic "Fetch a URL" ImageArea class.
 * This class extends the basic ImageArea Class to fetch a URL when
 * the user clicks in the area.
 *
 * @author 	Jim Graham
 * @version 	1.11, 06/13/02
 */
class LinkArea extends ImageMapArea {
    /** The URL to be fetched when the user clicks on this area. */
    URL anchor;

    /**
     * The argument string is the URL to be fetched.
     */
    public void handleArg(String arg) {
	try {
	    anchor = new URL(parent.getDocumentBase(), arg);
	} catch (MalformedURLException e) {
	    anchor = null;
	}
    }

    /**
     * The isTerminal method indicates whether events should propagate
     * to the areas underlying this one.
     */
    public boolean isTerminal() {
	return true;
    }

    /**
     * The status message area is updated to show the destination URL.
     */
    public void enter() {
	showStatus((anchor != null)
		   ? "Go To " + anchor.toExternalForm()
		   : null);
    }

    /**
     * The status message area is updated to show the destination URL.
     */
    public void exit() {
	showStatus(null);
    }

    /**
     * The new URL is fetched when the user releases the mouse button
     * only if they are still in the area.
     */
    public boolean lift(int x, int y) {
	if (inside(x, y) && anchor != null) {
	    showDocument(anchor);
	}
	return true;
    }
}
