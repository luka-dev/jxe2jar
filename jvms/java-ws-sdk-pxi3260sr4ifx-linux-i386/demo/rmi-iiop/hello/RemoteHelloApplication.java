/*
 * @(#)src/demo/rmi-iiop/hello/RemoteHelloApplication.java, orb, dsdev 1.9
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

import java.rmi.RemoteException;
import java.util.Properties;
import javax.naming.InitialContext;
import javax.rmi.PortableRemoteObject;
import java.rmi.RMISecurityManager;

public class RemoteHelloApplication
{
    public void run (String[] args)
    {
	// Must pass the server's host address as a command line parameter

	String host = args[0];

	// Pass system properties with -D option of java command, e.g.
	// for jrmp ...
	// -Djava.naming.factory.initial=com.sun.jndi.registry.RegistryContextFactory
	// for iiop ...
	// -Djava.naming.factory.initial=com.sun.jndi.cosnaming.CNCtxFactory

	String factory = System.getProperty ("java.naming.factory.initial");

	try
	    {
		String hostName = args[0];

		if ( System.getSecurityManager() == null ) {
		    System.setSecurityManager (new RMISecurityManager());
		}

		Properties env = new Properties ();

		// Shouldn't have to do this, but for now you must

		if ( factory.equals ("com.sun.jndi.cosnaming.CNCtxFactory") ) {
		    env.put ("java.naming.provider.url", "iiop://" + host);
		} else {
		    env.put ("java.naming.provider.url", "rmi://" + host);
		}

		InitialContext context = new InitialContext (env);
		Object o = context.lookup ("RemoteHelloServer");
		RemoteHello hello = (RemoteHello)PortableRemoteObject.narrow (o,RemoteHello.class);

		System.out.println (hello.message());
	    }
	catch (Exception e)
	    {
		System.out.println ("exception: " + e.getMessage ());
		e.printStackTrace ();
	    }

    }

    public static void main (String[] args)
    {
	RemoteHelloApplication app = new RemoteHelloApplication ();
	app.run (args);
    }
}
