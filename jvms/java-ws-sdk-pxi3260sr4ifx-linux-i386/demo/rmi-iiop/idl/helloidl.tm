<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!--
 - @(#)src/demo/rmi-iiop/idl/helloidl.tm, orb, dudev, 20050711 1.1
 - ===========================================================================
 - Licensed Materials - Property of IBM
 - "Restricted Materials of IBM"
 -
 - IBM SDK, Java(tm) 2 Technology Edition, v5.0
 - (C) Copyright IBM Corp. 1998, 2005. All Rights Reserved
 - ===========================================================================
-->
<!--
 - ===========================================================================
 -(C) Copyright Sun Microsystems Inc, 1992, 2004. All rights reserved.
 - ===========================================================================
-->

   <meta name="GENERATOR" content="Mozilla/4.5 [en] (X11; I; AIX 4.3) [Netscape]">
   <title>RMI-IIOP: Hello IDL Sample</title>
</head>
<body text="#000000" bgcolor="#FFFFFF">
&nbsp;
<table WIDTH="100%" >
<tr>
<td VALIGN=CENTER WIDTH="30">
<h1>
<img SRC="../../../demo/rmi-iiop/javalogo52x88.gif" ALT="Java" height=88 width=52></h1>
</td>
<td ALIGN=CENTER></td>
<td ALIGN=CENTER>
<h1>RMI-IIOP</h1>
<h1>Hello IDL Sample</h1>
<p><font size=-2>Copyright &copy; 1999 Sun Microsystems, Inc.&nbsp;</font>
<br><font size=-2>Copyright &copy; 1999,2002 International Business Machines
Corporation. All Rights Reserved.</font></td>
</tr>
</table>
<hr size="3" noshade>

<h2>RMI-IIOP Inter-operating with IDL</h2>
<p>This sample illustrates how an RMI-IIOP program can inter-operate
with a conventional IDL program.
It assumes that you have already built and run the
<a href="../hello/hello.html">RMI-IIOP "Hello World"</a> sample
program.
This sample shows inter-operability with IDL programs built in Java but
of course any programming language which supports IDL could be used.
<p>When you have built the two sets of clients and servers you will be
able to run them in the following combinations:
<p><center><table BORDER=0 WIDTH="400" colspec="l200 c200" units="pixels" >
<tr ALIGN=CENTER>
<td><b>Client</b></td> <td><b>Server</b></td>
</tr>
<tr ALIGN=CENTER>
<td>RMI-IIOP</td> <td>RMI-IIOP</td>
</tr>
<tr ALIGN=CENTER>
<td>IDL</td> <td>IDL</td>
</tr>
<tr ALIGN=CENTER>
<td>RMI-IIOP</td> <td>IDL</td>
</tr>
<tr ALIGN=CENTER>
<td>IDL</td> <td>RMI-IIOP</td>
</tr>
</table></center>

<h3>The Files</h3>
<p>The sample IDL source code is found in the
<tt>$JAVA_HOME/demo/rmi-iiop/idl</tt> directory.
There you will find the following files:
<ul>
<li><tt>RemoteHelloServer.java</tt> - the server IDL application</li>
<li><tt>RemoteHelloApplet.java</tt> - a client IDL applet</li>
<li><tt>RemoteHelloApplication.java</tt> - a client IDL application</li>
<li><tt>idl.html</tt> - HTML for applet with IDL settings</li>
</ul>
<p>To provide a complete explanation in the steps that follow, we make
the following assumptions:
<ul>
<li>A server named <tt>aslan.narnia.com</tt>.</li>
<li>A writable build directory of <tt>$DEMO_HOME</tt> (for example
<tt>$HOME/rmi-iiop/demo</tt>).</li>
<li>A running HTTP server with root <tt>$SERVER_ROOT</tt>.</li>
<br>Class files resulting from a sample build go into a codebase of
<tt>$SERVER_ROOT/java</tt>.
Classes in this directory will be loaded remotely; files to be copied
into this directory will be listed in the instructions below.
</ul>

<h3>Setting Up the Environment</h3>
<p>Set your <tt>CLASSPATH</tt> environment variable so that the current
directory (".") is at the beginning.
<p>Check that your PATH environment variable includes
<tt>$JAVA_HOME/bin:$JAVA_HOME/jre/bin</tt>, where <tt>$JAVA_HOME</tt>
is the directory where the Java SDK is installed.

<h3>Building the IDL program</h3>
<p>After configuring your environment, as explained above, change
directory to <tt>$DEMO_HOME/idl</tt>.
<ol>
<li>Copy the demo files to your demo build directory.
<pre>
   cp $JAVA_HOME/demo/rmi-iiop/idl/*.java .
</pre>
<li>Create the IDL files.</li>
<pre>
   rmic -idl -d idl hello.RemoteHelloServer
</pre>
<li>Go to the IDL samples directory.</li>
<pre>
   cd idl
</pre>
<li>Run the IDL to java converter to create the client-side
<tt>.java</tt> files.</li>
<pre>
   idlj -Fclient hello/RemoteHello.idl
</pre>
<li>Compile the client IDL application and the client applet.</li>
<pre>
   javac -d . RemoteHelloApplication.java
   javac -d . RemoteHelloApplet.java
</pre>
<p><b>Note:</b>
The next two steps are not required if you only require an IDL client.
<br>&nbsp;
<li>Run the IDL to java converter to create the sever-side
<tt>.java</tt> files.
<pre>
   idlj -Fall hello/RemoteHello.idl
</pre>
<li>Compile the IDL server application</li>
<pre>
   javac -d . RemoteHelloServer.java
</pre>
</ol>

<h3>Distributing the files</h3>
<p>For the client IDL application you must copy the following files to a
<tt>hello</tt> sub-directory on your client system.
<ul>
<li><tt>RemoteHelloApplication.class</tt></li>
<li><tt>RemoteHello.class</tt></li>
<li><tt>RemoteHelloOperations.class</tt></li>
<li><tt>RemoteHelloHelper.class</tt></li>
<li><tt>_RemoteHelloStub.class</tt></li>
</ul>
<p>Copy the following <tt>.class</tt> files to your server directory (e.g.
<tt>$SERVER_ROOT/java/hello</tt>
using our sample naming conventions).
<ul>
<li><tt>RemoteHelloOperations.class</tt></li>
<li><tt>_RemoteHelloStub.class</tt></li>
<li><tt>RemoteHello.class</tt></li>
<li><tt>RemoteHelloApplet.class</tt></li>
<li><tt>RemoteHelloHelper.class</tt></li>
</ul>
<p>The <tt>idl.html</tt> file should be copied to <tt>$SERVER_ROOT</tt>.

<h3>Running the IDL Sample</h3>
<h4>Starting the name server</h4>
<p>Run the name server that will be used to resolve the name
<i>RemoteHelloServer</i> that will be used by your applicaton.
The name server you run is the same whether you are running an RMI-IIOP
program or an IDL one.
<pre>
   tnameserv
</pre>
<h4>Starting your server application</h4>
<p>Run the IDL server application, passing parameters to the system with the
<tt>-D</tt> option.
Note that there must be no space between the <tt>-D</tt> and the
property text that follows it.
<pre>
   java -Dorg.omg.CORBA.ORBInitialHost=aslan.narnia.com hello.RemoteHelloServer
</pre>
<h4>Running your application client</h4>
<p>Run the application, passing the host address and port number of the
server to the application as system properties.
<pre>
   java -Dorg.omg.CORBA.ORBInitialHost=aslan.narnia.com hello.RemoteHelloApplication
</pre>
<h4>Running your applet client</h4>
<p>Run the applet using <tt>appletviewer</tt>.
<pre>
   appletviewer http://aslan.narnia.com/idl.html
</pre>
<p>It is simplest to test the applet using the <tt>appletviewer</tt> in this way.
To use a browser such as Internet Explorer or Netscape Navigator you
will need to modify <tt>idl.html</tt> or <tt>iiop.html</tt> to enable
the browser to use the Java plug-in.
Details of the Java plug-in can be found on the following website:
<a href="http://java.sun.com/products/plugin">http://java.sun.com/products/ plugin</a>

<h3>Inter-operating</h3>
<p>You now have a running IDL client and (optionally) an IDL server
application.
If you have previously implemented the
<a href="../hello/hello.html">RMI-IIOP "Hello World"</a> sample you will
also have a running RMI-IIOP client and server.
You are now ready to inter-operate between heterogeneous clients and servers.
<h4>IDL client with RMI-IIOP server</h4>
<ol>
<li>Start the RMI-IIOP server application as described in the instructions
for the <a href="../hello/hello.html">RMI-IIOP "Hello World"</a> sample.</li>
<li>Run the IDL client (application or applet) as described above.</li>
</ol>
<h4>RMI-IIOP client with IDL server</h4>
<ol>
<li>Start the IDL server application as described above</li>
<li>Run the RMI-IIOP client (application or applet) as described in the
instructions for the
<a href="../hello/hello.html">RMI-IIOP "Hello World"</a> sample .</li>
</ol>
</body>
</html>
