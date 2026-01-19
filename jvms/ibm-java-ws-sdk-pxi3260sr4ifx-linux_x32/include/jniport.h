/*******************************************************************************
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 * 
 * (c) Copyright IBM Corp. 1991, 2008 All Rights Reserved
 * 
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 *******************************************************************************/

#ifndef jniport_h
#define jniport_h

#if defined(WIN32) || (defined(_WIN32) && !defined(J9EPOC32)) || defined(J9WINCE) || defined(RIM386) || (defined(BREW) && defined(AEE_SIMULATOR)) || (defined(J9EPOC32) && defined(J9X86) && !defined(__WINSCW__))

#define JNIEXPORT __declspec(dllexport)
#define JNICALL __stdcall
typedef signed char jbyte;
typedef int jint;
typedef __int64 jlong;

#if defined(J9WINCE) && defined(_X86_)
#undef JNICALL
#define JNICALL __cdecl
#endif

#else

#define JNIEXPORT 

#if defined(J9EPOC32) && defined(__WINSCW__)
#define JNICALL __stdcall
#endif

typedef signed char jbyte;
typedef long long jlong;

#ifdef BREW
#include "AEEFile.h"
#define FILE IFile
#endif

typedef int jint;

#endif /* WIN32 */

#ifndef JNICALL
#define JNICALL
#endif

#ifndef JNIEXPORT
#define JNIEXPORT
#endif

#endif     /* jniport_h */
