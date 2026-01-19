/*
 * @(#)src/demo/jdbcodbc/bridgetest.java, dsdev, dsdev 1.8
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
** bridgetest.java
*/

import java.sql.*;
import java.io.*;

public class bridgetest {
 
    private static final String copyr = 
        "Licensed Materials - Property of IBM\n" +
        "IBM SDK, Java(tm) 2 Technology Edition, v5.0\n" +
        "(C) Copyright IBM Corp. 1998, 2005. All Rights Reserved\n" +
        "\n" +
        "US Government Users Restricted Rights - Use, duplication or disclosure\n" +
        "restricted by GSA ADP Schedule Contract with IBM Corp.\n" ;
 


    public static void main(String args[]) throws Exception {


	// Check arguments

	if (args.length < 3) {
            System.out.println("Usage: java bridgetest <databasename> <userid> <password>");
            return;
        }

        // Prepare the connection URL

	// update your database name in url 
        // String url = "jdbc:odbc:databasename";
        String url = "jdbc:odbc:" + args[0];

        Connection con;
        int tran;

        try {

            // Register the driver

            System.out.println("Registering...");
            Class.forName("sun.jdbc.odbc.JdbcOdbcDriver");        

        } catch(Exception e) {

            System.out.println("Exception: " + e.getMessage());

        }

        try {

            DriverManager.setLogStream(System.out);

            System.out.println("Getting Connection...");

	    // update your user id and password to connect to database 
            // con = DriverManager.getConnection(url,"userid","password");
            con = DriverManager.getConnection(url,args[1],args[2]);
	
            System.out.println("Getting Transaction Isolation...");
            tran = con.getTransactionIsolation();
            System.out.println("Transaction Isolation " + tran);
   
            System.out.println("Closing a Connection");   
            con.close();

        } catch(SQLException ex) {

            System.out.println("SQLException: " + ex.getMessage());
            ex.printStackTrace();

        }

        System.out.println("End");

    } 

}

