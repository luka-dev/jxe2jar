/*
 * @(#)src/demo/applets/ImageMap/RoundHrefButtonArea.java, ui, dsdev 1.11
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
 * @(#)RoundHrefButtonArea.java	1.10 02/06/13
 */

/**
 * An improved, round, "Fetch a URL" ImageArea class.
 * This class extends the HrefButtonArea Class to make the 3D button
 * a rounded ellipse.  All of the same feedback and operational
 * charactistics as the HrefButtonArea apply.
 *
 * @author 	Jim Graham
 * @version 	1.10, 06/13/02
 */
class RoundHrefButtonArea extends HrefButtonArea {
    /**
     * The filter used to create the 3D look for the button when it is up.
     */
    RoundButtonFilter roundfilter;

    /**
     * Test if the coordinate is inside the round region.  Use the test
     * provided by the filter that creates the 3D look for consistency.
     */
    public boolean inside(int x, int y) {
	return roundfilter.inside(x - X, y - Y);
    }

    /**
     * Construct the 3D look images that this area uses to draw the button.
     */
    public void makeImages() {
	roundfilter = new RoundButtonFilter(false, parent.hlpercent,
					    border, W, H);
	upImage = parent.getHighlight(X, Y, W, H, roundfilter);
	downImage = parent.getHighlight(X, Y, W, H,
					new RoundButtonFilter(true,
							      parent.hlpercent,
							      border, W, H));
    }
}
