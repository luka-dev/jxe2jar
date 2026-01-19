/*
 * @(#)src/demo/rmi-iiop/idl/RemoteHelloApplet.java, orb, dsdev 1.9
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





package hello;

// RemoteHelloClient will use the naming service.
import org.omg.CosNaming.*;

// The package containing special exceptions thrown by the name service.
import org.omg.CosNaming.NamingContextPackage.*;

// All CORBA applications need these classes.
import org.omg.CORBA.*;

// Needed for the applet.
import java.awt.Graphics;

public class RemoteHelloApplet extends java.applet.Applet
{
    public void init()
    {
	try{

	    // Create and initialize the ORB
	    // The applet 'this' is passed to make parameters from the <APPLET...> tag
	    // available to initialize the ORB
	    ORB orb = ORB.init(this, null);

	    // Get the root naming context
	    org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
	    NamingContext ncRef = NamingContextHelper.narrow(objRef);

	    // Resolve the object reference in naming
	    NameComponent nc = new NameComponent("RemoteHelloServer", "");
	    NameComponent path[] = {nc};
	    RemoteHello helloRef = RemoteHelloHelper.narrow(ncRef.resolve(path));

	    // Call the RemoteHello server object and print the results
	    message = helloRef.message();

	} catch(Exception e) {
	    System.out.println("RemoteHelloApplet exception: " + e);
	    e.printStackTrace(System.out);
	}
    }

    String message = "";

    public void paint(Graphics g)
    {
	g.drawString(message, 25, 50);
    }

}
