/*
 * @(#)src/demo/applets/ImageMap/AniArea.java, ui, dsdev 1.11
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
 * @(#)AniArea.java	1.13 02/06/13
 */

import java.awt.Graphics;
import java.util.StringTokenizer;
import java.awt.Image;
import java.net.URL;
import java.net.MalformedURLException;

/**
 * This ImageArea provides for a button that animates when the mouse is
 * over it. The animation is specifed as a base image that contains all
 * of the animation frames and then a series of X,Y coordinate pairs that
 * define the top left corner of each new frame.
 *
 * @author	Chuck McManis
 * @version	1.13, 06/13/02
 */
class AniArea extends ImageMapArea {

    Image sourceImage;
    int	 nFrames;
    int  coords[];
    int	 currentFrame = 0;

    public void handleArg(String s) {
	StringTokenizer st = new StringTokenizer(s, ", ");
	int	i;
        String imgName;

	imgName = st.nextToken();
	try {
	    sourceImage = parent.getImage(new URL(parent.getDocumentBase(),
						  imgName));
	    parent.addImage(sourceImage);
	} catch (MalformedURLException e) {}

	nFrames = 0;
	coords = new int[40];

	while (st.hasMoreTokens()) {
	    coords[nFrames*2]     = Integer.parseInt(st.nextToken());
	    coords[(nFrames*2)+1] = Integer.parseInt(st.nextToken());
	    nFrames++;
	    if (nFrames > 19)
		break;
	}
    }

    public boolean animate() {
	if (entered) {
	    repaint();
	}
	return entered;
    }

    public void enter() {
	currentFrame = 0;
	parent.startAnimation();
    }

    public void highlight(Graphics g) {
	if (entered) {
	    drawImage(g, sourceImage, 
		      X-coords[currentFrame*2], Y-coords[(currentFrame*2)+1],
		      X, Y, W, H);
	    currentFrame++;
	    if (currentFrame >= nFrames)
		currentFrame = 0;
	}
    }
  public String getAppletInfo() {
    return "Title: AniArea \nAuthor: Chuck McManis \nThis ImageMapArea subclass provides for a button that animates when the mouse is over it. The animation is specifed as a base image that contains all of the animation frames and then a series of X,Y coordinate pairs that define the top left corner of each new frame.";
  }
}

