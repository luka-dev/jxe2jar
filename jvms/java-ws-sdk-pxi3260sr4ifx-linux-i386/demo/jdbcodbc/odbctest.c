/*
 * @(#)src/demo/jdbcodbc/odbctest.c, dsdev, dsdev, 20060202 1.6
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
 * IBM Developer Kit, Java(TM) Tech Edition
 *
 * US Government Users Restricted Rights - Use,
 * duplication or disclosure restricted by GSA
 * ADP Schedule Contract with IBM Corp.
 */
 
#ifndef COPY_DECLARED
#define COPY_DECLARED 1
               "IBM Developer Kit, Java(TM) Tech Edition\n"
               "\n"
               "US Government Users Restricted Rights - Use,\n"
               "duplication or disclosure restricted by GSA\n"
               "ADP Schedule Contract with IBM Corp.\n" ;
#endif
 
/*
** example/jdbcodbc_example/odbctest.c, a116, a118
*/

#define FAR
#define EXPORT
#define CALLBACK

typedef      int HWND;

#include <stdio.h>
#include "sqlext.h"

void main(int argc, char *argv[]) {

    HENV      hEnv = SQL_NULL_HENV;
    HDBC      hDbc = SQL_NULL_HDBC;
    RETCODE   rc;
    char      c;
    UCHAR     szConnStrOut[256];
    SWORD     cbConnStrOut = 0;
    UCHAR     ConnectString[256];   
    char      dbms_name[30];
    char      dbms_ver[30];
    char      driver_name[30];
    char      driver_ver[30];
    char      driver_odbc_ver[30];
    char      odbc_ver[30];
    short     odbc_sql_con;
    char      sql_multiple_active_txn[30];
    char      sql_mult_result_sets[30];
    short     sql_active_connections;
    short     sql_active_statements;
    short     sql_odbc_api_con;
    short     sql_async_mode;
    short     sql_quoted_identifier_case;
    short     sql_identifier_case;
    short     size;

#ifdef INITCON
/*      Alternatively you can initialize your database, user id and password
        here without passing through command line.  Set up your database
        name, user id and password in the ConnectString and recompile
        with -DINITCON flag
 */
	strcpy (ConnectString, "DSN=database;UID=myid;PWD=mypassword");
#else

    if (argc < 4) {
        printf ("Usage: odbctest <databasename> <userid> <password>\n");
        exit (0);
    }
    strcpy (ConnectString, "DSN=");
    strcat (ConnectString, argv[1]);
    strcat (ConnectString, ";UID=");
    strcat (ConnectString, argv[2]);
    strcat (ConnectString, ";PWD=");
    strcat (ConnectString, argv[3]);
        
#endif

/* Allocate a new environment handle */

    rc = SQLAllocEnv (
        &hEnv);                 /* Pointer to environment handle */
    if ( rc == 0 )
        printf ("Allocated environment handle %d\n", hEnv);
    else {
        printf ("Unable to allocate environment handle. Return Code is %d\n", rc);
        exit(0); 
    }

/* Allocate a new connection handle */

    rc = SQLAllocConnect (
        (HENV) hEnv,            /* Environment handle */
        &hDbc);                 /* Pointer to connection handle */
    if ( rc == 0 )
        printf ("Allocated connection handle %d for Environment %d\n", hDbc, hEnv);
    else {
        printf ("Unable to allocate connection handle for Environment %d. Return Code is %d\n", hEnv, rc);
        printf ("Freeing Environment....");
        rc = SQLFreeEnv (hEnv);
        printf ("\n");
        exit(0); 
    }

/* Get a Connection */

        printf ("connecting to database .....");
        rc = SQLDriverConnect (
                (HDBC) hDbc,            /* Connection handle */
                NULL,                   /* Window handle */
                ConnectString,          /* Full connection string */
                SQL_NTS,                /* Length of connection string */
                szConnStrOut,           /* Pointer to completed connection */
                                        /*  string */
                sizeof (szConnStrOut),  /* Maximum length of completed */
                                        /*  connection string */
                &cbConnStrOut,          /* Pointer to completed connection */
                                        /*  string length */
                SQL_DRIVER_NOPROMPT);   /* Prompt flag */

    if (rc == 0) 
        printf ("\n\nConnected to database via ODBC!!!\n\n");
    else {
        printf ("\nUnable to Connect to database. Return Code is %d\n", rc);
        printf ("Freeing Connection and Environment ....");
        rc = SQLFreeConnect (hDbc);
        rc = SQLFreeEnv (hEnv);
        printf ("\n\nYou did not establish ODBC connection to database!!!\n\n");
        exit(0); 
    }

/* Get DBMS Name */

    rc = SQLGetInfo (hDbc, SQL_DBMS_NAME, &dbms_name, sizeof(dbms_name), &size);

    if (rc == 0) 
        printf ("DBMS Name:     %s\n", dbms_name);
    else 
        printf ("\nUnable to retrieve DBMS Name. Return Code is %d\n", rc);

/* Get DBMS Version */

    rc = SQLGetInfo (hDbc, SQL_DBMS_VER, &dbms_ver, sizeof(dbms_ver), &size);

    if (rc == 0) 
        printf ("DBMS Version:  %s\n", dbms_ver);
    else 
        printf ("\nUnable to retrieve DBMS Version. Return Code is %d\n", rc);

/* Get Driver Name */

    rc = SQLGetInfo (hDbc, SQL_DRIVER_NAME, &driver_name, sizeof(driver_name), &size);

    if (rc == 0) 
        printf ("Driver Name:     %s\n", driver_name);
    else 
        printf ("\nUnable to retrieve Driver Name. Return Code is %d\n", rc);

/* Get Driver Version */

    rc = SQLGetInfo (hDbc, SQL_DRIVER_VER, &driver_ver, sizeof(driver_ver), &size);

    if (rc == 0) 
        printf ("Driver Version:  %s\n", driver_ver);
    else 
        printf ("\nUnable to retrieve Driver Version. Return Code is %d\n", rc);

/* Get Driver ODBC Version */

    rc = SQLGetInfo (hDbc, SQL_DRIVER_ODBC_VER, &driver_odbc_ver, sizeof(driver_odbc_ver), &size);

    if (rc == 0) 
        printf ("Driver ODBC version:   %s\n", driver_odbc_ver);
    else 
        printf ("\nUnable to retrieve Driver ODBC version. Return Code is %d\n", rc);

/* Get ODBC Version */

    rc = SQLGetInfo (hDbc, SQL_ODBC_VER, &odbc_ver, sizeof(odbc_ver), &size);

    if (rc == 0) 
        printf ("ODBC version:   %s\n", odbc_ver);
    else 
        printf ("\nUnable to retrieve ODBC version. Return Code is %d\n", rc);

/* Get ODBC SQL Conformance */

    rc = SQLGetInfo (hDbc, SQL_ODBC_SQL_CONFORMANCE, &odbc_sql_con, sizeof(odbc_sql_con), &size);

    if (rc == 0) 
        printf ("ODBC SQL Conformance:   %d\n", odbc_sql_con);
    else 
        printf ("\nUnable to retrieve ODBC SQL Conformance. Return Code is %d\n", rc);

/* Get SQL Multiple Active Transactions */

    rc = SQLGetInfo (hDbc, SQL_MULTIPLE_ACTIVE_TXN, &sql_multiple_active_txn, sizeof(sql_multiple_active_txn), &size);

    if (rc == 0) 
        printf ("SQL Multiple Active Transactions:   %s\n", sql_multiple_active_txn);
    else 
        printf ("\nUnable to retrieve SQL Multiple Active Transactions Info. Return Code is %d\n", rc);

/* Get SQL Multiple Result Sets */

    rc = SQLGetInfo (hDbc, SQL_MULT_RESULT_SETS, &sql_mult_result_sets, sizeof(sql_mult_result_sets), &size);

    if (rc == 0) 
        printf ("SQL Multiple Result Sets:   %s\n", sql_mult_result_sets);
    else 
        printf ("\nUnable to retrieve SQL Multi Result Set info. Return Code is %d\n", rc);

/* Get SQL Active Connections */

    rc = SQLGetInfo (hDbc, SQL_ACTIVE_CONNECTIONS, &sql_active_connections, sizeof(sql_active_connections), &size);

    if (rc == 0) 
        printf ("SQL Active Connections:   %d\n", sql_active_connections);
    else 
        printf ("\nUnable to retrieve No. of SQL Active Connections. Return Code is %d\n", rc);

/* Get SQL Active Statements */

    rc = SQLGetInfo (hDbc, SQL_ACTIVE_STATEMENTS, &sql_active_statements, sizeof(sql_active_statements), &size);

    if (rc == 0) 
        printf ("SQL Active Statements:   %d\n", sql_active_statements);
    else 
        printf ("\nUnable to retrieve No. of SQL Active Statements. Return Code is %d\n", rc);

/* Get ODBC API Conformance */

    rc = SQLGetInfo (hDbc, SQL_ODBC_API_CONFORMANCE, &sql_odbc_api_con, sizeof(sql_odbc_api_con), &size);

    if (rc == 0) 
        printf ("SQL ODBC API Conformance:   %d\n", sql_odbc_api_con);
    else 
        printf ("\nUnable to retrieve status of ODBC API Conformance. Return Code is %d\n", rc);

/* Get SQL Quoted Identifier Case */

    rc = SQLGetInfo (hDbc, SQL_QUOTED_IDENTIFIER_CASE, &sql_quoted_identifier_case, sizeof(sql_quoted_identifier_case), &size);

    if (rc == 0) 
        printf ("SQL Quoted Identifier Case:   %d\n", sql_quoted_identifier_case);
    else 
        printf ("\nUnable to retrieve status of SQL Quoted Identifier Case. Return Code is %d\n", rc);

/* Get SQL Identifier Case */

    rc = SQLGetInfo (hDbc, SQL_IDENTIFIER_CASE, &sql_identifier_case, sizeof(sql_identifier_case), &size);

    if (rc == 0) 
        printf ("SQL Identifier Case:   %d\n", sql_identifier_case);
    else 
        printf ("\nUnable to retrieve status of SQL Quoted Identifier Case. Return Code is %d\n", rc);

/* Disconnect */
 
    /*printf ("Hit any key to start disconnecting from database\n");
    read(0, &c, 1);
    */
    printf ("Disconnecting.....");
        rc = SQLDisconnect (
                (HDBC) hDbc);           /* Connection handle */
    if ( rc == 0 )
        printf ("Disconnected from database\n");
    else
        printf ("\n Error in disconnection from database.  Return code is %d\n", rc);

/* Free Connection Handle */

    printf ("Freeing connection resources......\n");
    rc = SQLFreeConnect (
             (HDBC) hDbc);           /* Connection handle */
    if ( rc == 0 )
        printf ("Connection Resources Freed\n");
    else
        printf ("\nError in freeing connection resources.  Return code is %d\n", rc);

/* Free Environment handle */

    printf ("Freeing environment resources......\n");
    rc = SQLFreeEnv (
             (HENV) hEnv);            /* Environment handle */

    if ( rc == 0 )
        printf ("Environment resources freed\n");
    else
        printf ("\nError in freeing environment resources.  Return code is %d\n", rc);

}

