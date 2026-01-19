/*
 * @(#)src/demo/rmi-iiop/idl/RemoteHelloServer.java, orb, dsdev 1.9
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

// RemoteHelloServer will use the naming service.
import org.omg.CosNaming.*;

// The package containing special exceptions thrown by the name service.
import org.omg.CosNaming.NamingContextPackage.*;

// All CORBA applications need these classes.
import org.omg.CORBA.*;

// All CORBA server applications need the PortableServer classes.
import org.omg.PortableServer.*;

public class RemoteHelloServer
{
    public static void main(String args[])
    {
	try{

	    // Create and initialize the ORB
	    ORB orb = ORB.init(args, null);

	    // Obtain and activate a POA.  The basic RootPOA is adequate for
	    // this example.
	    org.omg.CORBA.Object objRef = orb.resolve_initial_references("RootPOA");
	    POA poa = POAHelper.narrow(objRef);
	    poa.the_POAManager().activate();

	    // Create the servant and obtain its object reference from the POA.
	    HelloServant helloServant = new HelloServant();
	    org.omg.CORBA.Object helloRef = poa.servant_to_reference(helloServant);

	    // Get the root naming context
	    objRef = orb.resolve_initial_references("NameService");
	    NamingContext ncRef = NamingContextHelper.narrow(objRef);

	    // Bind the object reference in naming
	    NameComponent nc = new NameComponent("RemoteHelloServer", "");
	    NameComponent path[] = {nc};
	    ncRef.rebind(path, helloRef);

	    // Wait for invocations from clients
	    System.out.println("IDL Hello Server waiting for client invocations");
	    orb.run();

	} catch(Exception e) {
	    System.err.println("ERROR: " + e);
	    e.printStackTrace(System.out);
	}
    }
}

class HelloServant extends RemoteHelloPOA
{
    public String message()
    {
	System.out.println("returning Hello World from IDL server");
	return "Hello world from IDL Server!!";
    }
}
