/*
 * @(#)src/demo/applets/ImageMap/NameArea.java, ui, dsdev 1.11
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
 * @(#)NameArea.java	1.11 02/06/13
 */

import java.awt.Graphics;

/**
 * A message feedback ImageArea class.
 * This class extends the basic ImageArea Class to show the a given
 * message in the status message area when the user enters this area.
 *
 * @author 	Jim Graham
 * @version 	1.11, 06/13/02
 */
class NameArea extends ImageMapArea {
    /** The string to be shown in the status message area. */
    String name;

    /**
     * The argument is the string to be displayed in the status message
     * area.
     */
    public void handleArg(String arg) {
	name = arg;
    }

    /**
     * The enter method displays the message in the status bar.
     */
    public void enter() {
	showStatus(name);
    }

    /**
     * The exit method clears the status bar.
     */
    public void exit() {
	showStatus(null);
    }
}

