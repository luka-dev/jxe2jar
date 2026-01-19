/*
 * @(#)src/demo/jfc/SampleTree/src/SampleData.java, swing, dsdev 1.11
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
 * @(#)SampleData.java	1.6 02/06/13
 */

import java.awt.Color;
import java.awt.Font;

/**
  * @version 1.6 06/13/02
  * @author Scott Violet
  */

public class SampleData extends Object
{
    /** Font used for drawing. */
    protected Font          font;

    /** Color used for text. */
    protected Color         color;

    /** Value to display. */
    protected String        string;


    /**
      * Constructs a new instance of SampleData with the passed in
      * arguments.
      */
    public SampleData(Font newFont, Color newColor, String newString) {
	font = newFont;
	color = newColor;
	string = newString;
    }

    /**
      * Sets the font that is used to represent this object.
      */
    public void setFont(Font newFont) {
	font = newFont;
    }

    /**
      * Returns the Font used to represent this object.
      */
    public Font getFont() {
	return font;
    }

    /**
      * Sets the color used to draw the text.
      */
    public void setColor(Color newColor) {
	color = newColor;
    }

    /**
      * Returns the color used to draw the text.
      */
    public Color getColor() {
	return color;
    }

    /**
      * Sets the string to display for this object.
      */
    public void setString(String newString) {
	string = newString;
    }

    /**
      * Returnes the string to display for this object.
      */
    public String string() {
	return string;
    }

    public String toString() {
	return string;
    }
}
