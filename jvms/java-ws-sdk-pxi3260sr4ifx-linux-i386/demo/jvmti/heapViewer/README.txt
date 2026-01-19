/*
 * @(#)src/demo/jvmti/heapViewer/README.txt, dsdev, dsdev, 20060202 1.2
 * ===========================================================================
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 *
 * IBM SDK, Java(tm) 2 Technology Edition, v1.4.2
 * (C) Copyright IBM Corp. 2004. All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 * ===========================================================================
 */
 heapViewer: @(#)README.txt	1.6 04/06/23

This agent library demonstrates how to get an easy view of the
heap in terms of total object count and space used.
It uses GetLoadedClasses(), SetTag(), and IterateOverHeap()
to count up all the objects of all the current loaded classes.
The heap dump will happen at the event JVMTI_EVENT_VM_DEATH, or the
event JVMTI_EVENT_DATA_DUMP_REQUEST.

It also demonstrates some more robust agent error handling using 
GetErrorName(),

You can use this agent library as follows:

    java -agentlib:heapViewer ...

Using the heap iterate functions, lots of statistics can be generated
without resorting to using Byte Code Instrumentation (BCI).

If the Virtual Machine complains that it can't find the library, 
you may need to add the directory containing the library into the 
LD_LIBRARY_PATH environment variable (Unix), or the PATH environment 
variable (Windows).

