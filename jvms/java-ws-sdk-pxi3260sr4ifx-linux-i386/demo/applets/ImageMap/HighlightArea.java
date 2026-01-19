/*
 * @(#)src/demo/applets/ImageMap/HighlightArea.java, ui, dsdev 1.11
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
 * @(#)HighlightArea.java	1.10 02/06/13
 */

import java.awt.Graphics;
import java.net.URL;
import java.net.MalformedURLException;

/**
 * An area highlighting ImageArea class.
 * This class extends the basic ImageArea Class to highlight an area of
 * the base image when the mouse enters the area.
 *
 * @author 	Jim Graham
 * @version 	1.10, 06/13/02
 */
class HighlightArea extends ImageMapArea {
    int hlmode;
    int hlpercent;

    /**
     * The argument string is the highlight mode to be used.
     */
    public void handleArg(String arg) {
	if (arg == null) {
	    hlmode = parent.hlmode;
	    hlpercent = parent.hlpercent;
	} else {
	    if (arg.startsWith("darker")) {
		hlmode = parent.DARKER;
		arg = arg.substring("darker".length());
	    } else {
		hlmode = parent.BRIGHTER;
		if (arg.startsWith("brighter")) {
		    arg = arg.substring("brighter".length());
		}
	    }
	    hlpercent = Integer.parseInt(arg);
	}
    }

    public void makeImages() {
	setHighlight(parent.getHighlight(X, Y, W, H, hlmode, hlpercent));
    }

    public void highlight(Graphics g) {
	if (entered) {
	    g.drawImage(hlImage, X, Y, this);
	}
    }

    /**
     * The area is repainted when the mouse enters.
     */
    public void enter() {
	repaint();
    }

    /**
     * The area is repainted when the mouse leaves.
     */
    public void exit() {
	repaint();
    }
}
