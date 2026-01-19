IBM SDK for Linux, Java Technology Edition, Version 6
=====================================================

This READMEFIRST file applies to Version 6, and to all subsequent
releases, modifications, and service refreshes, until otherwise indicated
in a new READMEFIRST file.

This READMEFIRST file provides release notes that were not incorporated
into the User Guides.  This file must be read in conjunction with any User
Guides.

The SDK provided in this release is functionally equivalent to the Sun FCS
version of Java 6 Update 7 Build 02 codebase.

IBM provides additional content with the SDK.


Known problems:
---------------

 - There is no ECC provider.
 - In the XL TXE-J XSLT compiler:
   - A low split limit might cause compilation errors
   - It is not recommended to call Java extension functions that have side
     effects. The order of execution is not guaranteed.
   - Versions of Ant prior to 1.7.0 will not work with the XL TXE-J compiler.
     Use the XSLT4J interpreter instead:
     -Djavax.xml.transform.TransformerFactory=
       org.apache.xalan.processor.TransformerFactoryImpl.