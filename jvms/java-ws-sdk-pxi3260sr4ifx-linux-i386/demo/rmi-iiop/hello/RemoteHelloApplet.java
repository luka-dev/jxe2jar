/*
 * @(#)src/demo/rmi-iiop/hello/RemoteHelloApplet.java, orb, dsdev 1.9
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

import java.applet.Applet;
import java.awt.Graphics;
import java.rmi.RemoteException;
import java.util.Properties;
import javax.naming.InitialContext;
import javax.rmi.PortableRemoteObject;

public class RemoteHelloApplet extends Applet
{
    private String message = "UNDEFINED";

    public RemoteHelloApplet ()
    {
    }

    public void init ()
    {
	try
	    {
		String hostName = getCodeBase().getHost();

		// Pass system properties with -D option of java command, e.g.
		// for jrmp ...
		// -Djava.naming.factory.initial=com.sun.jndi.registry.RegistryContextFactory
		// for iiop ...
		// -Djava.naming.factory.initial=com.sun.jndi.cosnaming.CNCtxFactory

		String factory = getParameter ("factory");

		Properties env = new Properties ();
		env.put ("java.naming.applet", this);
		env.put ("java.naming.factory.initial", factory);

		// Shouldn't have to do this, but for now you must

		if ( factory.equals ("com.sun.jndi.cosnaming.CNCtxFactory") ) {
		    env.put ("java.naming.provider.url", "iiop://" + hostName);
		} else {
		    env.put ("java.naming.provider.url", "rmi://" + hostName);
		}

		InitialContext context = new InitialContext (env);
		Object o = context.lookup ("RemoteHelloServer");
		RemoteHello hello = (RemoteHello)PortableRemoteObject.narrow (o,RemoteHello.class);

		message = hello.message ();

	    }
	catch (Exception e)
	    {
		System.out.println ("HelloApplet exception: " + e.getMessage ());
		e.printStackTrace ();
	    }
    }

    public void paint (Graphics g)
    {
	g.drawString (message, 10, 40);
    }

}
