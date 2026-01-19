IBM WebSphere Real Time version 1
===============================================================================


Introduction
===============================================================================

IBM WebSphere Real Time is an extension to the IBM Java Runtime Environment and
Software Development Kit with Metronome garbage collection, ahead-of-time
compilation and support of the Real-Time Specification for Java (RTSJ).

The benefits of the real-time environment are that Java applications run with
a greater degree of predictability than with the standard Java Virtual Machine
 (JVM) and provide a consistent timing behavior for your Java application.
Metronome garbage collection occurs at regular intervals and removes the
occurrence of any unexpected peaks of background activity during an
application's execution. In addition, Just-In-Time (JIT) compiliation can
be replaced with Ahead-Of-Time (AOT) compilation thus removing unpredictable
background activity when your application is run.

If you have previously precompiled code, you need to rebuild that code
for use with this version of WebSphere Real Time.

If you are running the TCK with WebSphere Real Time you should include
demo/realtime/TCKibm.jar  in the classpath in order for tests to be completed
successfully. TCKibm.jar includes the class VibmcorProcessorLock  which is
IBM's extension to the TCK.ProcessorLock class.  This class provides
uniprocessor behavior that is required in a small set of TCK tests. For more
information on the TCK.ProcessorLock class and vendor specific extensions to
this class, see the README file that is included with the TCK distribution.


Installation
===============================================================================

The SDK is supplied in a file called ibm-ws-rt-sdk-<version>-linux-i386.tgz.
The JRE is supplied in a file called ibm-ws-rt-jre-<version>-linux-i386.tgz.
The SDK can be installed into any directory by running the following command:

	tar xzf ibm-ws-rt-sdk-<version>-linux-i386.tgz -C <target directory>

Replace <target directory> with the directory where you want to unpack the JVM.
The following directory, and immediate files and directories will be
present in the target directory:
ibm-ws-rt-i386-<version>/
				   bin/
				   COPYRIGHT
				   demo/
				   docs/
				   include/
				   jre/
				   lib/
                                   realtime.src.jar
                                   src.jar

The command "java -version" displays the following if the install was
successful:

java version "1.5.0"
Java(TM) 2 Runtime Environment, Standard Edition (build pxi32rt23-20060809b)
IBM J9 VM (build 2.3, J2RE 1.5.0 IBM J9 2.3 Linux x86-32 j9vmxi3223ifx-20060719 (JIT enabled)
J9VM - 20060714_07194_lHdSMR
JIT  - 20060428_1800.ifix2_r8
GC   - 200607_07)
JCL  - 200608093

The command "java -Xrealtime -version" displays the following if the install
was successful:

java version "1.5.0"
Java(TM) 2 Runtime Environment, Standard Edition (build pxi32rt23-20060809b)
IBM J9 VM (build 2.3, J2RE 1.5.0 IBM J9 2.3 Linux x86-32 j9vmxi32rt23-20060809a (JIT enabled)
J9VM - 20060809_07538_lHdRRr
JIT  - 20060802_2345_r8.rt
GC   - 200608_02-Metronome
RT   - GA_2_3_RTJ--2006-07-24-AA-IMPORT)
JCL  - 20060809

The version information in both these examples is correct but the dates might
be different from those shown. The format of the date string is: yyyymmdd
followed possibly by additional information specific to the component.


Documentation
===============================================================================

In the docs directory, you will find readmeFirst.txt, rt_quick_start.pdf,
com.ibm.rt.doc.jar, com.ibm.rt.doc.zip, and rt_jre.pdf files.
 - readmeFirst.txt is this file.
 - rt_quick_start.pdf is the IBM WebSphere Quick Start Guide for use with the
 Adobe Acrobat Reader.
 - com.ibm.rt.doc.zip can be unpacked into the plugin directory of your Eclipse
 Help System, if the version is earlier than 3.1.1.
 - com.ibm.rt.doc.jar can be installed in the plugin directory of your Eclipse
 Help System version 3.1.1 or Eclipse SDK 3.1.2 or later.
 - The rt_jre.pdf is the WebSphere Real Time User Guide for use with the Adobe
 Acrobat Reader.

To access this information using a Web browser, enter

docs/startHere.htm

From this panel, you can view the PDF files and download com.ibm.rt.doc.jar or
com.ibm.rt.doc.zip to use with the Eclipse Help System that you can install
locally on your system or on your network.

Introduction to the Information Center
--------------------------------------
You can access the Information Center on your local machine or by visiting
http://publib.boulder.ibm.com/infocenter/realtime/v1r0/index.jsp

To use the information center on your local machine, you need to install
the Eclipse Help system.

A configured and installed copy of the Eclipse Help System version 3.1.1 is on the ISO
image under the /help_ibm directory. Although this copy of the help text
is not updateable and the CD medium makes it run rather slowly, it is
provided for convenience. See "Running the Eclipse Help System from the ISO
image" for more details.

Note: If you are already running Eclipse SDK, you can copy com.ibm.rt.doc.jar to
the plugin directory.  You have to stop and start Eclipse SDK to view the
Information Center.

The remainder of the information in this readme describes how to install  and run
the Eclipse Help system for WebSphere Real Time information center.

Installing the Eclipse Help System
----------------------------------
1. Download the latest version of the Eclipse Help System from
http://www.alphaworks.ibm.com/tech/iehs/download.
2. Select the zip or tgz file that is appropriate for your operating
system.
3. Create a new directory where you plan to install the Eclipse Help System.
This is referred to as <INSTALL_DIR> in the rest of this document.
4. Unpack the zip or tgz file into, for example, /opt/<INSTALL_DIR) or
C:\<INSTALL_DIR> directory depending on your operating system. This creates
a directory called /opt/<INSTALL_DIR)/ibm_help on Linux or
C:\<INSTALL_DIR>/IBM_Help_301_Win\ibm_help on Windows.

Starting and stopping the help system
-------------------------------------
You can start the IBM Eclipse Help System in two different modes, information center
mode and stand-alone mode.

Stand-alone mode. IBM Eclipse Help System acts as a private documentation server, and
automatically opens a Web browser to view the documentation on a randomly generated
port. Only browsers on the same system can access this server.

Information center mode. IBM Eclipse Help System acts as a public documentation
server and allows other Web browsers on your network to connect to the help system
on a defined port.


Adding the WebSphere Real Time information center to your Eclipse Help System
-----------------------------------------------------------------------------
For Eclipse Help System versions 3.0.1 and earlier
1. Extract the files from com.ibm.rt.doc.zip into either the
/opt/<INSTALL_DIR)/ibm_help/eclipse/plugins directory or
C:\<INSTALL_DIR>/IBM_Help_301_Win\ibm_help\eclipse\plugins depending on
your operating system.

1. Copy com.ibm.rt.doc.jar into either /opt/<INSTALL_DIR)/ibm_help/eclipse/plugins directory
or C:\<INSTALL_DIR>/IBM_Help_301_Win\ibm_help\eclipse\plugins depending on your operating system.


Starting and stopping the help system in stand-alone mode
---------------------------------------------------------
1. Navigate to the ibm_help directory.
2. To start and view the Eclipse Help System:
 Run /opt/<INSTALL_DIR)/ibm_help/help_start.sh file.
3. To stop the help system:
 Run /opt/<INSTALL_DIR)/ibm_help/help_end.sh file.

Starting and stopping the help system in information center mode
----------------------------------------------------------------
1. Navigate to the ibm_help directory.
2. To start and view the Eclipse Help System:
 Run /opt/<INSTALL_DIR)/ibm_help/IC_start.sh file.
3. Enter the URL for the information center using the following
syntax: http://<servername>:<portNumber>/help
4. To stop the help system:
 Run /opt/<INSTALL_DIR)/ibm_help/IC_end.sh file.


Running the Eclipse Help System from the ISO image
--------------------------------------------------

To access the WebSphere Real Time information center from the ISO image:
1. Mount the ISO image in your Linux system.
2. Change directory to ibm_help
3. To run the information center, enter: help_cd_start.sh
After a short time, your browser opens showing the home page of the WebSphere
Real Time information center.
An alternative way to start the Eclipse Help System is as follows:
1. Mount the ISO image in your Linux system.
2. Change directory to ibm_help
3. To run the information center, enter: IC_start.sh
4. Open your browser and enter the URL: http://machine_name:8888 where
machine_name is the name of your your machine. IC_start.sh does not start
your browser automatically.

Note: You must be running within the X Window system in order for a web browser
to open successfully.

To stop the Eclipse help system enter help_cd_end.sh or IC_end.sh depending
on the method that you chose to start the help system.

You can use the ISO image to burn a CD.

The PDF
-------
The information center is also provided as PDF (rt_jre.pdf). The information
has not been fully optimized for this format.



