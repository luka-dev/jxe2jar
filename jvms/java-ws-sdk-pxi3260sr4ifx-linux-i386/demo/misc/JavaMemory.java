/*
 * @(#)src/demo/misc/JavaMemory.java, core, dsdev 1.8
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
 * Title: JavaMemory
 *
 * Description: Displays free and total memory usage
 *
 * Usage: java JavaMemory
 *
 */

public class JavaMemory {

	public static void main(String[] args) {
		Runtime runtime = Runtime.getRuntime();
		long freeKMem = runtime.freeMemory()/1024;
		long totalKMem = runtime.totalMemory()/1024;
		long freeMMem = runtime.freeMemory()/1024/1024;
		long totalMMem = runtime.totalMemory()/1024/1024;
		System.out.println("Free Mem:"+freeKMem+"KB ("+freeMMem+"MB), Total Mem:"+totalKMem+"KB ("+totalMMem+"MB)");
	}
}

