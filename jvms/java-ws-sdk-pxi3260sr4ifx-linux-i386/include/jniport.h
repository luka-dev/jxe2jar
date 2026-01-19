/*
*	(c) Copyright IBM Corp. 1991, 2007 All Rights Reserved
*/
#ifndef jniport_h
#define jniport_h

#if defined(WIN32) || (defined(_WIN32) && !defined(J9EPOC32)) || defined(J9WINCE) || defined(RIM386) || (defined(BREW) && defined(AEE_SIMULATOR)) || (defined(J9EPOC32) && defined(J9X86) && !defined(__WINSCW__))

/* PalmOS6 Simulator */
#if defined(PALMOS6)
#include "j9comp.h"
#endif

#define JNIEXPORT __declspec(dllexport)
#define JNICALL __stdcall
typedef signed char jbyte;
typedef int jint;
typedef __int64 jlong;

#if defined(PALMOS5) || (defined(J9WINCE) && defined(J9X86))
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

#if defined (PILOT) || defined (__palmos__)
#include <stddef.h>	/* <stdio.h> doesn't define NULL on PalmOS, so pull in stddef to make users happier */
#ifdef __GNUC__
#define FILE void
#endif
typedef long jint;
#else
typedef int jint;
#endif

#ifdef PALMARM
#undef EOF
#endif

#endif /* WIN32 */

#ifndef JNICALL
#define JNICALL
#endif

#ifndef JNIEXPORT
#define JNIEXPORT
#endif

#endif     /* jniport_h */

