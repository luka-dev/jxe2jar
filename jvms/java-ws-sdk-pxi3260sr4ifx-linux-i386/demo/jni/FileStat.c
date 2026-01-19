/*
 * @(#)src/demo/jni/FileStat.c, dadev, dxdev 1.7
 * ===========================================================================
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 *
 * IBM SDK, Java(tm) 2 Technology Edition, v1.4.2
 * (C) Copyright IBM Corp. 2002, 2004. All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 * ===========================================================================
 */

static char oco_header[] = "Licensed Materials - Property of IBM\n"
        "IBM SDK, Java(tm) 2 Technology Edition, v1.4.2\n"
        "(C) Copyright IBM Corp. 2004. All Rights Reserved\n"
        "US Government Users Restricted Rights - Use, duplicate or disclosure\n"
        "restricted by GSA ADP Schedule Contract with IBM Corp.";


#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include "FileStat.h"

char* GetStringLocalChars(JNIEnv *, jstring);
void ReleaseStringLocalChars(JNIEnv *, char *);

/*
 * Class:     FileStat
 * Method:    nativeFileStat
 * Signature: (Ljava/lang/String;)V
 */
extern int errno;

JNIEXPORT void JNICALL Java_FileStat_nativeFileStat
  (JNIEnv *env, jobject obj, jstring jname)
{
	jfieldID fid;
	struct stat * buf=NULL;
	jclass cls;
	jlong val;
	char * name;

	name = GetStringLocalChars(env, jname);

	buf = (struct stat *) malloc(sizeof(*buf));
		
	if( (! buf) || (stat(name, buf)== -1) )
	{
		const char * cause = strerror(errno);
		(*env)->ThrowNew(env, (*env)->FindClass(env,"FileStatException"), cause);
		return;
	}

	cls = (*env)->GetObjectClass(env, obj);

	fid = (*env)->GetFieldID(env, cls, "inode", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_ino);

	fid = (*env)->GetFieldID(env, cls, "mode", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_mode);

	fid = (*env)->GetFieldID(env, cls, "nlink", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_nlink);

	fid = (*env)->GetFieldID(env, cls, "uid", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_uid);

	fid = (*env)->GetFieldID(env, cls, "gid", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_gid);

	fid = (*env)->GetFieldID(env, cls, "size", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_size);

	fid = (*env)->GetFieldID(env, cls, "atime", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_atime*1000);

	fid = (*env)->GetFieldID(env, cls, "mtime", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_mtime*1000);

	fid = (*env)->GetFieldID(env, cls, "ctime", "J");
	(*env)->SetLongField(env, obj, fid, (jlong)buf->st_ctime*1000);
	
	ReleaseStringLocalChars(env, name);
	free(buf);
}

char* GetStringLocalChars(JNIEnv *env, jstring str)
{
	jclass system;
	jmethodID getProperty;
	jstring fileEncoding;
	jstring enc;
	jclass cls;
    jmethodID getBytes;
    jbyteArray bytes;
    jsize len;
    char *s;
    jbyte *bs;

	system = (*env)->FindClass(env, "java/lang/System");
	getProperty = (*env)->GetStaticMethodID(env, system, "getProperty", "(Ljava/lang/String;)Ljava/lang/String;");
	fileEncoding = (*env)->NewStringUTF(env, "file.encoding");
	enc = (*env)->CallStaticObjectMethod(env, system, getProperty, fileEncoding);
	cls = (*env)->FindClass(env, "java/lang/String");
	getBytes = (*env)->GetMethodID(env, cls, "getBytes", "(Ljava/lang/String;)[B");
	bytes = (jbyteArray)(*env)->CallObjectMethod(env, str, getBytes, enc);
	len = (*env)->GetArrayLength(env, bytes);
	s = (char*)malloc(len+1);
	bs = (*env)->GetByteArrayElements(env, bytes, NULL);
	memcpy(s, bs, len);
	(*env)->ReleaseByteArrayElements(env, bytes, bs, 0);
	s[len] = '\0';
	return s;
}

void ReleaseStringLocalChars(JNIEnv *env, char* str){
	free(str);
}
