/*
 * @(#)src/demo/jni/FileStat.java, dadev, dxdev, 20061221 1.6
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




import java.util.Date;
import java.text.DateFormat;

/**
 * This class is provided for access to the underlying stat(2)
 * subroutine. This may be needed for getting the information 
 * about the file named by the path parameter. Read, write, or
 * execute permission for the named file is not required, but 
 * all directories listed in the path leading to the file must
 * be searchable.
 *
 * Though it supports the same basic functionality as the C stat(2)
 * API, this class currently contains only the important fields
 * like inode, mode, nlink, uid, gid, size, atime, mtime & ctime.
 * See man pages of stat(2) for info on C API.
 *
 *
 * @author  Prakash S Rao
 * @see     attached README
 * @since   JDK1.4
 */

public class FileStat
{
	protected long inode;
	protected long mode;
	protected long nlink;
	protected long uid;
	protected long gid;
	protected long size;
	protected long atime; 
	protected long mtime;
	protected long ctime;
	protected String name;

	static
	{
		System.loadLibrary("FileStat");
	}

	/**
	* Constructs an instance of a <code>FileStat</code> object
	* and initializes all the required fields.
	*/
	public FileStat(String name) throws FileStatException
	{
		this.name = name;
		nativeFileStat(name);
	}

	private native void nativeFileStat(String name) throws FileStatException;

	/**
	* Returns the pathname of the file.
	*/
	public String getName()
	{
		return name;
	}

	/**
	* Returns the inode number of the file.
	*/
	public long getInode()
	{
		return inode;
	}

	/**
	* Returns the mode of the file.
	*/
	public long getMode()
	{
		return mode;
	}

	/**
	* Returns the nuber of hard links to the file.
	*/
	public long getNLink()
	{
		return nlink;
	}

	/**
	* Returns the file owner ID.
	*/
	public long getUid()
	{
		return uid;
	}

	/**
	* Returns the file group ID.
	*/
	public long getGid()
	{
		return gid;
	}

	/**
	* Returns the size of the file in bytes.
	*/
	public long getSize()
	{
		return size;
	}

	/**
	* Returns the Time when file data was last accessed, measured in milliseconds.
	*/
	public long getATime()
	{
		return atime;
	}

	/**
	* Returns the Time when file data was last modified, measured in milliseconds.
	*/
	public long getMTime()
	{
		return mtime;
	}

	/**
	* Returns the Time when the file status was last changed, measured in milliseconds.
	*/
	public long getCTime()
	{
		return ctime;
	}

	/**
	* Returns a string representation of this FileStat object.
	*/
	public String toString()
	{
		String data;
		data = "        File Name: "+name+"\n"
			 + "            Inode: "+inode+"\n"
			 + "             Mode: "+Long.toOctalString(mode)+"\n"
			 + "            Links: "+nlink+"\n"
			 + "              UID: "+uid+"\n"
			 + "              GID: "+gid+"\n"
			 + "             Size: "+size+"\n"
			 + " Last Access Time: "+new Date(atime)+"\n"
			 + "Modification Time: "+new Date(mtime)+"\n"
			 + "    Creation Time: "+new Date(ctime)+"\n";
		return data;
	}

	/**
	* Compares the specified Object with this FileStat for equality.
	* @param obj-object to be compared for equality with this FileStat.
	* @return true if the specified Object is equal to this FileStat.
	*/
	public boolean equals(Object obj)
	{
		if (obj instanceof FileStat){
			FileStat fs = (FileStat) obj;
			return fs.toString().equals(this.toString());
		}
		return false;
	}
}

