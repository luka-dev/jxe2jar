<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!--
 - @(#)src/demo/rmi-iiop/hello/hello.tm, orb, dudev, 20050711 1.1
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
   <title>RMI-IIOP: Hello Sample</title>
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
<h1>Hello Sample</h1>
<p><font size=-2>Copyright &copy; 1999 Sun Microsystems, Inc.&nbsp;</font>
<br><font size=-2>Copyright &copy; 1999,2003 International Business Machines
Corporation. All Rights Reserved.</font></td>
</tr>
</table>
<hr size="3" noshade>

<h2>The RMI-IIOP Hello Sample</h2>
<p>This is the classic "Hello World!" application adapted to RMI-IIOP.
While similar to the Hello World sample presented in the
<a href="../../../docs/rmi-iiop/rmi_iiop_pg.html">RMI-IIOP Programmer's Guide</a>
this sample illustrates developing an RMI program that can be built and
run for either the JRMP or IIOP protocols with the "flip of a switch".
The "switch" we refer to is an -iiop switch used with the <tt>rmic</tt>
compiler.
You also need to pass a different system/applet environment setting to
the java command using the -D option, but the code itself need not be
changed.
This sample illustrates both application and applet client.

<h3>The Files</h3>
<p>The sample code is found in the <tt>$JAVA_HOME/demo/rmi-iiop/hello</tt>
directory.
There you will find the following files:
<ul>
<li><tt>RemoteHello.java</tt> - the remote interface</li>
<li><tt>RemoteHelloServer.java</tt> - the remote server</li>
<li><tt>RemoteHelloApplet.java</tt> - a client applet</li>
<li><tt>RemoteHelloApplication.java</tt> - a client application</li>
<li><tt>jrmp.html</tt> - HTML for applet with JRMP settings</li>
<li><tt>iiop.html</tt> - HTML for applet with IIOP settings</li>
</ul>
<p>To provide a complete explanation in the steps that follow, we make the
following assumptions:
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
<p>Set your CLASSPATH environment variable so that the current directory
(".") is at the beginning.
<p>Check that your PATH environment variable includes
<tt>$JAVA_HOME/bin:$JAVA_HOME/jre/bin</tt>, where <tt>$JAVA_HOME</tt>
is the directory where the Java SDK is installed.
<p><b>Note:</b>
Don't forget to set up a security policy file.
See the following section for instructions.

<h3>A Note About Security Policy Files</h3>
The JDK 1.2 security model is more sophisticated than the JDK 1.1 model.
JDK 1.2 contains enhancements for finer-grained security and requires
code to be granted specific permissions to be allowed to perform certain
operations.
In JDK 1.1 code in the class path is trusted and can perform any
operation; downloaded code is governed by the rules of the installed
security manager.
If you run this example in JDK 1.2, you need to specify a <i>policy file</i>
when you run your server and client.
In this example, for simplicity, we will use a policy file that gives
global permission to anyone from anywhere.
<b><i>Do not use this policy file in a production environment</i></b>.
For more information on how to properly open up permissions using a
<tt>java.security.policy</tt> file, please refer to the following
documents:
<ul>
<li><a href="http://java.sun.com/products/jdk/1.4.1/docs/guide/security/PolicyFiles.html">
http://java.sun.com/products/jdk/1.4.1/docs/guide/security/PolicyFiles.html</a></li>
<li><a href="http://java.sun.com/products/jdk/1.4.1/docs/guide/security/permissions.html">
http://java.sun.com/products/jdk/1.4.1/docs/guide/security/permissions.html</a></li>
</ul>
<p>Create a policy file called <tt>$DEMO_HOME/policy</tt>
containing the following code:
<pre>
   grant {
      permission java.security.AllPermission;
   };
</pre>
<p>The <a href="http://java.sun.com/docs/books/tutorial/rmi/running.html">
RMI section</a> in the <i>Java Tutorial</i> contains a discussion of policy
files.

<h3>Building the Hello Sample</h3>
<p>After configuring your environment, as explained above, change
directory to <tt>$DEMO_HOME/hello</tt>.
<ol>
<li>Copy the demo files to your demo build directory.
<pre>
   cp $JAVA_HOME/demo/rmi-iiop/hello/*.java .
</pre>
<li>Compile all java files.</li>
<pre>
   javac *.java
</pre>
<li>Change directory to <tt>$DEMO_HOME</tt>.</li>
<pre>
   cd ..
</pre>
<li>Compile the stubs with <tt>rmic</tt>.</li>
<ul>
<li>For JRMP:</li>
<br><pre>rmic hello.RemoteHelloServer</pre>
<li>For IIOP:</li>
<br><pre>rmic -iiop hello.RemoteHelloServer</pre>
</ul>
<li>Copy the following files to <tt>$SERVER_ROOT</tt> (the HTTP server root):</li>
<ul>
<li><tt>iiop.html</tt></li>
<li><tt>jrmp.html</tt></li>
<br>&nbsp;
</ul>
<li>Copy the following files to <tt>$SERVER_ROOT/java/hello</tt>:</li>
<ul>
<li><tt>RemoteHello.class</tt></li>
<li><tt>RemoteHelloApplet.class</tt></li>
<li><tt>RemoteHelloServer_Stub.class</tt> (for JRMP)</li>
<li><tt>_RemoteHello_Stub.class</tt> (for IIOP)</li>
</ul>
<p>Remember that <tt>$SERVER_ROOT/java</tt> is your <tt>codebase</tt>,
and that <tt>hello</tt> is the package name.
</ol>

<h3>Running the Hello Sample</h3>
<p>The following assumes that the server is run on a host named
<tt>aslan.narnia.com</tt>, that an http server is running, and that the
code base is a <tt>java</tt> directory under the server's root and that the
class files are in a <tt>hello</tt> directory under <tt>java</tt>.
<ol>
<li>Start an HTTP server.</li>
<li>Run the name server that will be used to resolve the name
<i>RemoteHelloServer</i> to an RMI server.</li>
<br>The name server you run depends on whether you will be using JRMP or
IIOP.
The name server must be started in a separate process, so it is easiest
to start it in its own window.
<br><b>Note:</b> Run your naming service from an environment (shell) where
your CLASSPATH does <i>not</i> include the samples directory.
See the <a href="http://java.sun.com/products/jdk/1.4.1/docs/guide/rmi/getstart.doc.html#5522">RMI</a>
documentation for an explanation.
<br>&nbsp;
<ul>
<li>For JRMP:</li>
<br><pre>rmiregistry</pre>
<li>For IIOP:</li>
<br><pre>tnameserv</pre>
</ul>
<li>From <tt>$DEMO_HOME</tt> run the server, passing
parameters to the system with the <tt>-D</tt> option.</li>
<br>There are several details to pay attention to here.
First, these commands are all one line, even though the formatting in
this document may make them appear to have carriage returns.
Second, there must be no space between the <tt>-D</tt> and the property
text that follows it.
Finally, the codebase property must end with a "/".
<br>&nbsp;
<ul>
<li>For JRMP:</li>
<pre>
java -Djava.rmi.server.codebase=http://aslan.narnia.com/java/
     -Djava.security.policy=policy
     -Djava.naming.factory.initial=com.sun.jndi.rmi.registry.RegistryContextFactory
      hello.RemoteHelloServer
</pre>
<li>For IIOP:</li>
<pre>
java -Djava.rmi.server.codebase=http://aslan.narnia.com/java/
     -Djava.security.policy=policy
     -Djava.naming.factory.initial=com.sun.jndi.cosnaming.CNCtxFactory
      hello.RemoteHelloServer
</pre>
</ul>
<li>From <tt>$DEMO_HOME</tt> run the application.</li>
<br>Pass the host address of the server to the application as a command
line parameter.
Pay attention to the same details described in the last step.
<br>&nbsp;
<ul>
<li>For JRMP:</li>
<pre>
java -Djava.rmi.server.codebase=http://aslan.narnia.com/java/
     -Djava.security.policy=policy
     -Djava.naming.factory.initial=com.sun.jndi.rmi.registry.RegistryContextFactory
      hello.RemoteHelloApplication aslan.narnia.com
</pre>
<li>For IIOP:</li>
<pre>
java -Djava.rmi.server.codebase=http://aslan.narnia.com/java/
     -Djava.security.policy=policy
     -Djava.naming.factory.initial=com.sun.jndi.cosnaming.CNCtxFactory
      hello.RemoteHelloApplication aslan.narnia.com
</pre>
</ul>
<li>Run the applet.</li>
<br>This is easiest to do using the <tt>appletviewer</tt>.
To use a browser such as Internet Explorer or Netscape Navigator you
will need to modify <tt>jrmp.html</tt> or <tt>iiop.html</tt> to enable
the browser to use the Java plug-in.
Details of the Java plug-in can be found on the following website:
<a href="http://java.sun.com/products/plugin">http://java.sun.com/products/plugin</a>.
<br>&nbsp;
<ul>
<li>For JRMP:</li>
<pre>appletviewer http://aslan.narnia.com/jrmp.html</pre>
<li>For IIOP:</li>
<pre>appletviewer http://aslan.narnia.com/iiop.html</pre>
</ul>
</ol>

<h3>Errors</h3>
<p>There are several steps involved and it is easy to make a mistake.
You may build for one protocol and run for another, run the wrong name
server for the protocol, or forget to copy class files, for example.
Here are a couple of errors (exceptions) you may encounter and what they
mean.
<p>
<table BORDER NOSAVE >
<tr ALIGN=LEFT NOSAVE>
<th NOSAVE>Exception&nbsp;</th>
<th>Probable Cause&nbsp;</th>
</tr>
<tr>
<td><tt>java.lang.ClassCastException</tt></td>
<td>The stub class file cannot be found in the client class path&nbsp;</td>
</tr>
<tr>
<td><tt>java.lang.NoClassDefFound</tt></td>
<td>The interface class file cannot be found in the client class path&nbsp;</td>
</tr>
<tr>
<td><tt>java.rmi.ConnectException</tt></td>
<td>Either the server has not been started or you are running a client
for the wrong protocol&nbsp;</td>
</tr>
</table>

<h2>The Hello IDL Sample</h2>
Next, you might want to look at the <a href="../idl/helloidl.html">
Hello IDL</a> sample.
Hello IDL shows how an RMI-IIOP program interoperates with a
conventional IDL program.

</body>
</html>
