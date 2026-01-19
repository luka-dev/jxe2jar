/*
 * @(#)src/demo/rmi-iiop/hello/RemoteHelloServer.java, orb, dsdev 1.9
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
import javax.rmi.PortableRemoteObject;
import java.util.Properties;
import javax.naming.InitialContext;
import java.rmi.RMISecurityManager;

public class RemoteHelloServer extends PortableRemoteObject
    implements RemoteHello
{
    public RemoteHelloServer () throws RemoteException
    {
    }

    public String message ()
    {
	System.out.println ("got request");
	return "Hello World!";
    }

    public static void main (String[] args)
    {
	try
	    {
		if ( System.getSecurityManager() == null ) {
		    System.setSecurityManager (new RMISecurityManager());
		}

		RemoteHelloServer obj = new RemoteHelloServer ();

		// Pass system properties with -D option of java command, e.g.
		// for jrmp ...
		// -Djava.naming.factory.initial=com.sun.jndi.registry.RegistryContextFactory
		// for iiop ...
		// -Djava.naming.factory.initial=com.sun.jndi.cosnaming.CNCtxFactory

		InitialContext context = new InitialContext ();
		context.rebind ("RemoteHelloServer", obj);
		System.out.println ("HelloServer bound in registry");
	    }
	catch (Exception e)
	    {
		System.out.println ("HelloServer Exception: " + e.getMessage());
		e.printStackTrace ();
	    }
    }
}
