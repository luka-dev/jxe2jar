/*
 * @(#)src/demo/applets/GraphicsTest/AppletFrame.java, ui, dsdev 1.16
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
 * @(#)AppletFrame.java	1.11 02/06/13
 */

import java.awt.Frame;
import java.awt.Event;
import java.awt.Dimension;
import java.applet.Applet;
import java.awt.AWTEvent;

// Applet to Application Frame window
class AppletFrame extends Frame
{

    public static void startApplet(String className, 
                                   String title, 
                                   String args[])
    {
       // local variables
       Applet a;
       Dimension appletSize;

       try 
       {
          // create an instance of your applet class
          a = (Applet) Class.forName(className).newInstance();
       }
       catch (ClassNotFoundException e) { return; }
       catch (InstantiationException e) { return; }
       catch (IllegalAccessException e) { return; }

       // initialize the applet
       a.init();
       a.start();
  
       // create new application frame window
       AppletFrame f = new AppletFrame(title);
  
       // add applet to frame window
       f.add("Center", a);
  
       // resize frame window to fit applet
       // assumes that the applet sets its own size
       // otherwise, you should set a specific size here.
       appletSize =  a.getSize();
       f.pack();
       f.setSize(appletSize);  

       // show the window
       f.show();
  
    }  // end startApplet()
  
  
    // constructor needed to pass window title to class Frame
    public AppletFrame(String name)
    {
       // call java.awt.Frame(String) constructor
       super(name);
    }

    // needed to allow window close
    public void processEvent(AWTEvent e)
    {
       // Window Destroy event
       if (e.getID() == Event.WINDOW_DESTROY)
       {
          // exit the program
          System.exit(0);
       }    
   }  // end handleEvent()

}   // end class AppletFrame






