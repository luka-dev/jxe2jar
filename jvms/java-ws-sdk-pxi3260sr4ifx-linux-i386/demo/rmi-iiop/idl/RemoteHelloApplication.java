/*
 * @(#)src/demo/rmi-iiop/idl/RemoteHelloApplication.java, orb, dsdev 1.9
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
import org.omg.CosNaming.*;  // HelloClient will use the naming service.
import org.omg.CORBA.*;      // All CORBA applications need these classes.

public class RemoteHelloApplication
{
    public static void main(String args[])
    {
	try{

	    // Create and initialize the ORB
	    ORB orb = ORB.init(args, null);

	    // Get the root naming context
	    org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
	    NamingContext ncRef = NamingContextHelper.narrow(objRef);

	    // Resolve the object reference in naming
	    NameComponent nc = new NameComponent("RemoteHelloServer", "");
	    NameComponent path[] = {nc};
	    RemoteHello helloRef = RemoteHelloHelper.narrow(ncRef.resolve(path));

	    // Call the RemoteHello server object and print results
	    String Hello = helloRef.message();
	    System.out.println(Hello);

	} catch(Exception e) {
	    System.out.println("RemoteHelloApplication ERROR : " + e);
	    e.printStackTrace(System.out);
	}
    }
}
