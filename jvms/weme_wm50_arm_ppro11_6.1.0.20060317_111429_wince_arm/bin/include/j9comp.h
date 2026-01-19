/*
*	(c) Copyright IBM Corp. 1991, 2006 All Rights Reserved
*/

#ifndef j9comp_h
#define j9comp_h

#include "j9cfg.h"

/*
USE_PROTOTYPES:			Use full ANSI prototypes.

CLOCK_PRIMS:					We want the timer/clock prims to be used

LITTLE_ENDIAN:				This is for the intel machines or other
											little endian processors. Defaults to big endian.

NO_LVALUE_CASTING:	This is for compilers that don't like the left side
											of assigns to be cast.  It hacks around to do the
											right thing.

ATOMIC_FLOAT_ACCESS:	For the hp720 so that float operations will work.

LINKED_USER_PRIMITIVES:	Indicates that user primitives are statically linked
													with the VM executeable.

OLD_SPACE_SIZE_DIFF:	The 68k uses a different amount of old space.
											This "legitimizes" the change.

SIMPLE_SIGNAL:		For machines that don't use real signals in C.
									(eg: PC, 68k)

OS_NAME_LOOKUP:		Use nlist to lookup user primitive addresses.

VMCALL:			Tag for all functions called by the VM.

VMAPICALL:		Tag for all functions called via the PlatformFunction
							callWith: mechanism.
			
SYS_FLOAT:	For the MPW C compiler on MACintosh. Most of the math functions 
						there return extended type which has 80 or 96 bits depending on 68881 option.
						On All other platforms it is double

FLOAT_EXTENDED: If defined, the type name for extended precision floats.

PLATFORM_IS_ASCII: Must be defined if the platform is ASCII

EXE_EXTENSION_CHAR: the executable has a delimiter that we want to stop at as part of argv[0].

*/

/* By default order doubles in the native (i.e. big/little endian) ordering. */
#define J9_PLATFORM_DOUBLE_ORDER

/* ARM_EMULATED */

#if defined(ARM_EMULATED) 
typedef long long	I_64 ;
typedef unsigned long long	U_64 ;

#define NO_LVALUE_CASTING
#define SYS_FLOAT	double
#define PLATFORM_LINE_DELIMITER	"\015"
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"

#ifdef VA_PTR
#undef VA_PTR
#endif
#define VA_PTR(valist) (&valist[0])

#endif
/* ARMGNU */

#if defined(ARMGNU) && !defined(NEUTRINO) && !defined(ARMGNUEABI)
#undef J9_PLATFORM_DOUBLE_ORDER
#endif

/* AS400 */

#ifdef AS400

#define DATA_TYPES_DEFINED
typedef unsigned int				UDATA ;		/* 64bits */
typedef unsigned int				U_64;
typedef unsigned __int32		U_32;
typedef unsigned short			U_16;
typedef unsigned char			U_8;
typedef signed int				IDATA;		/* 64bits */
typedef signed int				I_64;		
typedef __int32					I_32;
typedef signed short				I_16;
typedef signed char				I_8;			
typedef U_32						BOOLEAN;

typedef double					SYS_FLOAT;

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#endif

/* CHORUS */

#ifdef CHORUS

typedef long long I_64;
typedef unsigned long long U_64;

#define DATA_TYPES_DEFINED
typedef unsigned int                    UDATA;
typedef unsigned int                    U_32;
typedef unsigned short          U_16;
typedef unsigned char           U_8;
typedef int                                             IDATA;
typedef int                                             I_32;
typedef short                                   I_16;
typedef signed char                     I_8;
typedef UDATA                           BOOLEAN;
typedef double                          SYS_FLOAT;

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER "\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#define h_errno errno

#define J9_DEFAULT_SCHED SCHED_RR
#define J9_PRIORITY_MAP {5,6,7,8,9,10,11,12,13,14,15, 16}

#endif

/* DOS TTY, with Watcom C */

#ifdef DOS
#define NO_LVALUE_CASTING

#define SYS_FLOAT double
#define EXE_EXTENSION_CHAR	'.'
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"
#endif

/* HP720 ANSI compiler */

#ifdef HP720

typedef signed long long 		I_64;
typedef unsigned long long 	U_64;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define ATOMIC_FLOAT_ACCESS
#define SYS_FLOAT double
#define FLOAT_EXTENDED	long double
#define PLATFORM_IS_ASCII
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#endif

/* ITRON */
#ifdef ITRON
#ifdef ITRONGNU
typedef long long I_64;
typedef unsigned long long U_64;
#define J9CONST64(x) x##LL
#else
typedef long I_64;									/* BOGUS -- Compiler does not provide an int64 type! */
typedef unsigned long U_64;						/* BOGUS -- Compiler does not provide an int64 type! */
#endif

#define DATA_TYPES_DEFINED
typedef unsigned int			UDATA;
typedef unsigned int			U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
typedef int						IDATA;
typedef int						I_32;
typedef short					I_16;
typedef signed char			I_8;
typedef UDATA				BOOLEAN;
typedef double				SYS_FLOAT;

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#define J9_DEFAULT_SCHED SCHED_RR
#define J9_PRIORITY_MAP {12,11,10,9,8,7,6,5,4,3,2,1}

#endif

/* J9EPOC32 */

#ifdef J9EPOC32
#ifdef ARM
typedef long long	I_64 ;
typedef unsigned long long	U_64 ;
#ifndef J9OS_EPOC_9
#undef J9_PLATFORM_DOUBLE_ORDER
#endif
#define J9CONST64(x) x##LL
#else
#ifdef __WINSCW__
typedef long long	I_64 ;
typedef unsigned long long	U_64 ;
#else
typedef __int64					I_64 ;
typedef unsigned __int64	U_64 ;
#endif
#endif

/* Neither Metrowerks nor RCVT like multiple consts */
#ifdef J9OS_EPOC_9
#define J9CONST_TABLE
#endif

#define NO_LVALUE_CASTING
#define SYS_FLOAT double
#define EXE_EXTENSION_CHAR	'.'
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"

#define J9_PRIORITY_MAP {	\
	EPriorityNull,						/* 0 */\
	EPriorityMuchLess,				/* 1 */\
	EPriorityMuchLess,				/* 2 */\
	EPriorityLess,						/* 3 */\
	EPriorityLess,						/* 4 */\
	EPriorityNormal,					/* 5 */\
	EPriorityNormal,					/* 6 */\
	EPriorityMore,						/* 7 */\
	EPriorityMore,						/* 8 */\
	EPriorityMuchMore,			/* 9 */\
	EPriorityMuchMore,			/*10 */\
	EPriorityMuchMore				/*11 */}

/* ANSI qsort crashes on the device */
extern void j9_sort(void* base, int nmemb, int size, int(*compare)(const void *, const void *));
#define J9_SORT(base, nmemb, size, compare) j9_sort((base), (nmemb), (size), (compare))

#endif
/* J9WINCE WinCE */

#ifdef J9WINCE

typedef __int64					I_64 ;
typedef unsigned __int64	U_64 ;
typedef double 					SYS_FLOAT;

/* TGD:  the following was added as WinCE #defines it in winnt.h.
	To not #define it by hand, one must do:
		#include <windows.h>
	but that isn't the right solution, so we do it by hand.
*/
#ifndef offsetof
#define offsetof(s,m) ((size_t)&(((s*)0)->m))
#endif

#define NO_LVALUE_CASTING

#define VMAPICALL _stdcall
#define VMCALL _cdecl
#define PLATFORM_IS_ASCII
#define EXE_EXTENSION_CHAR	'.'
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"

#ifdef SH4
#define J9_NO_DENORMAL_FLOAT_SUPPORT
#endif

#ifdef MIPS64
#define J9_NO_DENORMAL_FLOAT_SUPPORT
#endif

#endif

/* Linux ANSI compiler (gcc) */

#ifdef LINUX

/* NOTE: Linux supports different processors -- do not assume 386 */

#if defined(J9HAMMER) || defined(S39064) || defined(LINUXPPC64)
#define DATA_TYPES_DEFINED
typedef unsigned long int		UDATA;					/* 64bits */
typedef unsigned long int	U_64;
typedef unsigned int				U_32;
typedef unsigned short			U_16;
typedef unsigned char			U_8;
typedef signed long int			IDATA;					/* 64bits */
typedef long int					I_64;
typedef signed int				I_32;						
typedef signed short				I_16;			
typedef signed char				I_8;				
typedef U_32						BOOLEAN; 	

/* LinuxPPC64 is like AIX64 so we need direct function pointers */
#if defined(J9VM_ENV_DIRECT_FUNCTION_POINTERS) && defined(LINUXPPC64)
#define TOC_UNWRAP_ADDRESS(wrappedPointer) ((void *) (wrappedPointer)[0])
#define TOC_STORE_TOC(dest,wrappedPointer) (dest = ((UDATA*)wrappedPointer)[1])
#endif

#else
typedef long long I_64;
typedef unsigned long long U_64;
#endif

typedef double SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define FLOAT_EXTENDED	long double
#define PLATFORM_IS_ASCII
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#if defined(J9VM_OPT_REAL_TIME_EXTENSIONS)
#define J9_DEFAULT_SCHED realtime_sched_policy(0)
#else
/* no priorities on Linux */
#define J9_PRIORITY_MAP {0,0,0,0,0,0,0,0,0,0,0,0}
#endif


#if (defined(LINUXPPC) && !defined(LINUXPPC64)) || defined(S390) || defined(J9HAMMER)
#define VA_PTR(valist) (&valist[0])
#endif

#if (defined(HARDHAT) && defined(ARMGNU))
#define ATOMIC_LONG_ACCESS
#endif

#endif

/* MIPS processors */

#ifdef MIPS
#define ATOMIC_FLOAT_ACCESS

#ifdef MIPS64
#define ATOMIC_LONG_ACCESS
#endif

#endif

/* IRIX ANSI compiler (gcc) */

#ifdef IRIX

/* NOTE: UDATA needs to be a long (not just an int) on IRIX, for some of
 * the C++ code in the JIT to compile. sizeof(long int) == sizeof(int), but
 * C++ is picky about types
 */
typedef unsigned long int			UDATA;
typedef unsigned long int			U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
typedef long int			IDATA;
typedef long int			I_32;
typedef short				I_16;
typedef char				I_8;
typedef long long					I_64;
typedef unsigned long long	U_64;
typedef double					SYS_FLOAT;

#define J9CONST64(x) x##LL

#define DATA_TYPES_DEFINED
#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#define J9_DEFAULT_SCHED SCHED_RR

/* no generic U_64 or I_64 */



/* temp hack -- don't typedef BOOLEAN since it's already def'ed on Win32 */
#define BOOLEAN UDATA

#endif

/* MVS compiler */

#ifdef MVS

#define DATA_TYPES_DEFINED
typedef unsigned int				UDATA;
typedef unsigned long long	U_64;
typedef unsigned int				U_32;
typedef unsigned short			U_16;
typedef unsigned char			U_8;
typedef signed int				IDATA;
typedef signed long long		I_64;
typedef signed int				I_32;
typedef signed short				I_16;
typedef signed char				I_8;
typedef I_32						BOOLEAN;
typedef double 					SYS_FLOAT;
typedef long double				FLOAT_EXTENDED;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\025"
#define DIR_SEPARATOR '.'
#define DIR_SEPARATOR_STR "."

#include "esmap.h"

#endif

/* NEUTRINO */

#ifdef NEUTRINO

typedef long long I_64;
typedef unsigned long long U_64;

#define DATA_TYPES_DEFINED
typedef unsigned int			UDATA;
typedef unsigned int			U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
typedef int						IDATA;
typedef int						I_32;
typedef short					I_16;
typedef signed char			I_8;
typedef UDATA				BOOLEAN;
typedef double				SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#define J9_DEFAULT_SCHED SCHED_RR
#define J9_PRIORITY_MAP {5,6,7,8,9,10,11,12,13,14,15, 16}

#ifdef MIPS
#define J9_NO_DENORMAL_FLOAT_SUPPORT
#endif

#ifdef PPC
#define VA_PTR(valist) (&valist[0])
#endif

#endif

/* NeXT Ansi Gnu compiler */

#ifdef NeXT

#define DATA_TYPES_DEFINED
typedef unsigned long int		UDATA;					/* 32bits */
typedef unsigned long long int	U_64;					/* 64bits */
typedef unsigned long int		U_32;
typedef unsigned short			U_16;
typedef unsigned char			U_8;
typedef signed long int			IDATA;					/* 32bits */
typedef signed long long int	I_64;					/* 64bits */
typedef signed long int			I_32;						
typedef signed short			I_16;			
typedef signed char				I_8;				
typedef U_32					BOOLEAN; 	
typedef double					SYS_FLOAT; 

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\015"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#define FLOAT_EXTENDED	long double

#endif

/* OS2 */

#ifdef OS2
#define NO_LVALUE_CASTING
#define EXE_EXTENSION_CHAR	'.'
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"

#define OS2PM
#include "headers.h"
#define	VMCALL _Optlink
#define VMAPICALL _System

#define J9CONST64(x) x##LL

typedef double	 		SYS_FLOAT;
typedef long double		FLOAT_EXTENDED;
typedef unsigned long long			U_64;
typedef long long			I_64;

#endif

/* OSX (mac) compiler (gcc) */

#ifdef OSX

#define DATA_TYPES_DEFINED
typedef unsigned long int		UDATA;					/* 32bits */
typedef unsigned long long int	U_64;					/* 64bits */
typedef unsigned int 		U_32;
typedef unsigned short			U_16;
typedef unsigned char			U_8;
typedef signed long int			IDATA;					/* 32bits */
typedef signed long long int	I_64;					/* 64bits */
typedef signed int			I_32;						
typedef signed short			I_16;			
typedef signed char				I_8;				
typedef U_32					BOOLEAN; 	
typedef double					SYS_FLOAT; 

#define NO_LVALUE_CASTING
#define FLOAT_EXTENDED	long double
#define PLATFORM_IS_ASCII
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#endif

/* J9OSE */

#ifdef J9OSE

typedef long long  I_64;
typedef unsigned long long U_64;

#define DATA_TYPES_DEFINED
typedef unsigned int			UDATA;
typedef unsigned int			U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
typedef int						IDATA;
typedef int						I_32;
typedef short					I_16;
typedef signed char			I_8;
typedef UDATA				BOOLEAN;
typedef double				SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#define J9_DEFAULT_SCHED SCHED_FIFO
#define J9_PRIORITY_MAP {20,19,18,17,16,15,14,13,12,11,10,9}

#ifdef J9VM_ENV_LITTLE_ENDIAN
#ifndef LITTLE_ENDIAN
#define LITTLE_ENDIAN
#endif
#else
#define BIG_ENDIAN
#endif

#ifdef PPC
#define VA_PTR(valist) (&valist[0])
#endif

#ifdef ARM
#define VA_PTR(valist) (&valist[0])
#endif

#endif

/* BREW */

#ifdef BREW
/* resolve any issues about TRUE/FALSE definition */
#define TRUE   1   /* Boolean true value. */
#define FALSE  0   /* Boolean false value. */

#ifdef AEE_SIMULATOR
typedef __int64 I_64;
typedef  unsigned __int64 U_64;
#else
typedef long long I_64;
typedef unsigned long long U_64;
#endif

#define DATA_TYPES_DEFINED
typedef unsigned int			UDATA;
typedef unsigned int			U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
typedef int						IDATA;
typedef int						I_32;
typedef short					I_16;
typedef signed char			I_8;
typedef UDATA				BOOLEAN;
typedef double				SYS_FLOAT;

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"

#ifdef AEE_SIMULATOR
#define DIR_SEPARATOR  '\\'
#define DIR_SEPARATOR_STR   "\\"
#else
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#endif

#define LITTLE_ENDIAN

#ifdef ARM
#define VA_PTR(valist) (&valist[0])
#endif

#endif

/* PILOT Ansi Gnu compiler */

#ifdef PILOT

#define DATA_TYPES_DEFINED
typedef unsigned long int UDATA;	/* 32bits */
typedef unsigned long long int U_64;	/* 64bits */
typedef unsigned long int U_32;
typedef unsigned short U_16;
typedef unsigned char U_8;
typedef signed long int IDATA;	/* 32bits */
typedef signed long long int I_64;	/* 64bits */
typedef signed long int I_32;
typedef signed short I_16;
typedef signed char I_8;
typedef U_32 BOOLEAN;
typedef double SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\015"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#define FLOAT_EXTENDED	long double

#define J9_SORT(base, nmemb, size, compare) SysQSort( (base), (Int16)(nmemb), (Int16)(size), (CmpFuncPtr)(compare), (Int32)0 )

extern void* getDataPtrFromOffset();
#define GLOBAL_DATA(symbol) \
({	void *__res; \
	asm("pea " #symbol ".w\n" \
		"bsr.w getDataPtrFromOffset\n" \
		"addq.w #4, %%sp\n" \
		"move.l %%a0, %0\n" \
		: "=a" (__res) : : \
		"a0", "a1", "d0", "d1", "d2"); \
	__res; })
#define GLOBAL_TABLE(symbol) GLOBAL_DATA(symbol)

#else

#define GLOBAL_DATA(symbol) ((void*)&(symbol))
#define GLOBAL_TABLE(symbol) GLOBAL_DATA(symbol)

#endif

/* RIM386 */

#ifdef RIM386

typedef __int64					I_64 ;
typedef unsigned __int64	U_64 ;

typedef double 					SYS_FLOAT;

#define NO_LVALUE_CASTING
#define VMAPICALL _stdcall
#define VMCALL _cdecl
#define EXE_EXTENSION_CHAR	'.'
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"

/* (on WinCE, there's another priority: THREAD_PRIORITY_ABOVE_IDLE) */
#define J9_PRIORITY_MAP {	\
	THREAD_PRIORITY_IDLE,							/* 0 */\
	THREAD_PRIORITY_LOWEST,					/* 1 */\
	THREAD_PRIORITY_BELOW_NORMAL,	/* 2 */\
	THREAD_PRIORITY_BELOW_NORMAL,	/* 3 */\
	THREAD_PRIORITY_BELOW_NORMAL,	/* 4 */\
	THREAD_PRIORITY_NORMAL,						/* 5 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 6 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 7 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 8 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 9 */\
	THREAD_PRIORITY_HIGHEST,					/*10 */\
	THREAD_PRIORITY_TIME_CRITICAL			/*11 */}

#endif

/* RS6000 */

/* The AIX platform has the define AIXPPC and RS6000,
	this means AIXPPC inherits from the RS6000.*/

#if defined(RS6000) || defined(OSOPEN)

#define DATA_TYPES_DEFINED

/* long is 32 bits on AIX32, and 64 bits on AIX64 */
typedef unsigned long UDATA;
typedef signed long IDATA;

#if defined(PPC64)
typedef unsigned long U_64;
typedef long I_64;
#else
typedef unsigned long long U_64;
typedef long long I_64;
#endif

typedef unsigned int U_32;
typedef unsigned short U_16;
typedef unsigned char U_8;
typedef signed int I_32;
typedef signed short I_16;
typedef signed char I_8;
typedef U_32 BOOLEAN;
typedef double SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#ifdef J9VM_ENV_DIRECT_FUNCTION_POINTERS
#define TOC_UNWRAP_ADDRESS(wrappedPointer) ((void *) (wrappedPointer)[0])
#define TOC_STORE_TOC(dest,wrappedPointer) (dest = ((UDATA*)wrappedPointer)[1])
#endif

/*
 * Have to have priorities between 40 and 60 inclusive for AIX >=5.3 
 * AIX 5.2 ignores them 
 */
#define J9_PRIORITY_MAP  { 40,41,43,45,47,49,51,53,55,57,59,60 }

#endif
/* Solaris ANSI compiler */

#ifdef SOLARIS
#ifndef J9OSE
typedef long long					I_64;
typedef unsigned long long	U_64;
typedef double					SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#endif /* J9OSE */
#endif

/* Win32 - Windows 3.1 & NT using Win32 */

#ifdef WIN32
#ifndef BREW

#ifdef J9HAMMER
/* NOTE: Windows now supports different processors -- do not assume 386 only */

#define DATA_TYPES_DEFINED 
typedef unsigned __int64	UDATA;					/* 64bits */
typedef unsigned __int64	U_64;
typedef unsigned __int32	U_32;
typedef unsigned __int16	U_16;
typedef unsigned __int8		U_8;
typedef signed __int64		IDATA;					/* 64bits */
typedef signed __int64		I_64;
typedef signed __int32		I_32;						
typedef signed __int16		I_16;			
typedef signed __int8			I_8;				

/* temp hack -- don't typedef BOOLEAN since it's already def'ed on Win32 */
#define BOOLEAN UDATA

#else

#ifdef WIN32_IBMC
typedef long long I_64;
typedef unsigned long long	 U_64;
#define J9CONST64(x) x##LL
#else
#ifndef PALMOS6	/* Do not typedef for PalmOS6 simulator compiles */
typedef __int64					I_64 ;
typedef unsigned __int64	U_64 ;
#endif
#endif
#endif

typedef double 					SYS_FLOAT;

#define NO_LVALUE_CASTING
#define VMAPICALL _stdcall
#define VMCALL _cdecl
#define EXE_EXTENSION_CHAR	'.'

#ifdef PALMOS5
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#else
#define DIR_SEPARATOR '\\'
#define DIR_SEPARATOR_STR "\\"
#endif

/* Modifications for the Alpha running WIN-NT */
#ifdef _ALPHA_
#undef small  /* defined as char in rpcndr.h */
typedef double	FLOAT_EXTENDED;
#endif

/* (on WinCE, there's another priority: THREAD_PRIORITY_ABOVE_IDLE) */
#define J9_PRIORITY_MAP {	\
	THREAD_PRIORITY_IDLE,							/* 0 */\
	THREAD_PRIORITY_LOWEST,					/* 1 */\
	THREAD_PRIORITY_BELOW_NORMAL,	/* 2 */\
	THREAD_PRIORITY_BELOW_NORMAL,	/* 3 */\
	THREAD_PRIORITY_BELOW_NORMAL,	/* 4 */\
	THREAD_PRIORITY_NORMAL,						/* 5 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 6 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 7 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 8 */\
	THREAD_PRIORITY_ABOVE_NORMAL,		/* 9 */\
	THREAD_PRIORITY_HIGHEST,					/*10 */\
	THREAD_PRIORITY_TIME_CRITICAL			/*11 */}

#endif
#endif

/* ZOS390 */

#if defined(J9ZOS390)

#define DATA_TYPES_DEFINED
typedef unsigned long			UDATA;
typedef unsigned int   		U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
typedef signed long			IDATA;
typedef signed int			I_32;
typedef signed short			I_16;
typedef signed char			I_8;			
typedef unsigned int			BOOLEAN;
#if defined (J9VM_ENV_DATA64)
typedef unsigned long U_64;
typedef long I_64;
#else
typedef signed long long	I_64;
typedef unsigned long long	U_64;
#endif

typedef double				SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\012"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"

#define VA_PTR(valist) (&valist[0])

#ifdef __cplusplus
#else
#include "zvarmaps.h"
#endif

typedef struct {
#if !defined(J9VM_ENV_DATA64)
    char stuff[16];
#endif
    char *ada;
    void (*rawFnAddress)();
} J9FunctionDescriptor_T;

#define TOC_UNWRAP_ADDRESS(wrappedPointer) (((J9FunctionDescriptor_T *) (wrappedPointer))->rawFnAddress)

#endif

/* PALMARM PalmOS5 ADS tools */

#ifdef PALMARM

#define DATA_TYPES_DEFINED
typedef unsigned int UDATA;	/* 32bits */
typedef unsigned long long int U_64;	/* 64bits */
typedef unsigned int U_32;
typedef unsigned short U_16;
typedef unsigned char U_8;
typedef signed int IDATA;	/* 32bits */
typedef signed long long int I_64;	/* 64bits */
typedef signed int I_32;
typedef signed short I_16;
typedef signed char I_8;
typedef U_32 BOOLEAN;
typedef double SYS_FLOAT;

#define J9CONST64(x) x##LL

#define NO_LVALUE_CASTING
#define PLATFORM_LINE_DELIMITER	"\015"
#define DIR_SEPARATOR '/'
#define DIR_SEPARATOR_STR "/"
#define FLOAT_EXTENDED	long double

#ifdef VA_PTR
#undef VA_PTR
#endif
#ifndef PALMOS6
#define VA_PTR(valist) (&valist[0])
#endif

/* ADS 1.2 places ALL const data in the position-independent constantdata section.
 * This means that const tables can't be relocated. Workaround is to not use const
 * tables on this platform.
 */
#define J9CONST_TABLE

#endif

/* PALMOS6 generic */

#ifdef PALMOS6
#include <stdlib.h>
#include <PalmOS.h>
#include <DataMgrCompatibility.h>
#include <MemoryMgrCompatibility.h>

#define MemCardInfo MemCardInfoV40
#define MemSemaphoreRelease(a)
#define MemSemaphoreReserve(a)

#ifdef WIN32	/* Compiling for a simulator target? */

typedef int64_t     I_64 ;
typedef uint64_t    U_64 ;

typedef int64_t	__int64;
typedef uint64_t	__uint64;

#undef VMCALL
#define VMCALL

#endif

#endif


/* PALMOS5 generic */

#ifdef PALMOS5 

#include <SysUtils.h>
#define J9_SORT(base, nmemb, size, compare) SysQSort( (base), (Int16)(nmemb), (Int16)(size), (CmpFuncPtr)(compare), (Int32)0 )

#ifdef WIN32
#define J9PACE_FN_PTR 0x80000000
#else
#define J9PACE_FN_PTR 0x00000001
#endif

#if 0
#if defined(PALMOS5) && !defined(PALMOS6)
#define LocalID MemHandle
#define SysCurAppDatabase(a,b) SysCurAppDatabase(b)
#define SysAppLaunch(a,b,c,d,e,f) SysAppLaunch(b,c,d,e,f)
#define DmFindDatabase(a,b) DmFindDatabase(b)
#define DmDeleteDatabase(a,b) DmDeleteDatabase(b)
#define DmOpenDatabase(a,b,c) DmOpenDatabase(b,c)
#define DmDatabaseSize(a,b,c,d,e) DmDatabaseSize(b,c,d,e)
#define DmCreateDatabase(a,b,c,d,e) DmCreateDatabase(b,c,d,e)
#define DmDatabaseInfo(a,b,c,d,e,f,g,h,i,j,k,l,m) DmDatabaseInfo(b,c,d,e,f,g,h,i,j,k,l,m)
#define DmSetDatabaseInfo(a,b,c,d,e,f,g,h,i,j,k,l,m) DmSetDatabaseInfo(b,c,d,e,f,g,h,i,j,k,l,m)
#define DmGetNextDatabaseByTypeCreator(a,b,c,d,e,f,g) DmGetNextDatabaseByTypeCreator(a,b,c,d,e,g)
#define MemCardInfo(a,b,c,d,e,f,g,h) MemInfo(b,c,d,e,f,g,h)
#define DmGetAppInfoID(a) DmGetAppInfoH(a)
#define MemLocalIDToLockedPtr(a,b) MemHandleLock(a)
#define MemHandleToLocalID(a) a
#define MemSemaphoreRelease(a)
#define MemSemaphoreReserve(a)
#endif
#endif

#endif


/* SPARC processors */

#ifdef SPARC
#define ATOMIC_LONG_ACCESS
#define ATOMIC_FLOAT_ACCESS
#endif


#ifndef	VMCALL
#define	VMCALL
#define	VMAPICALL
#endif
#define PVMCALL VMCALL *

/* Provide some reasonable defaults for the VM "types":

	UDATA			unsigned data, can be used as an integer or pointer storage.
	IDATA			signed data, can be used as an integer or pointer storage.
	U_64 / I_64	unsigned/signed 64 bits.
	U_32 / I_32	unsigned/signed 32 bits.
	U_16 / I_16	unsigned/signed 16 bits.
	U_8 / I_8		unsigned/signed 8 bits (bytes -- not to be confused with char)
	BOOLEAN	something that can be zero or non-zero.

*/

#ifndef	DATA_TYPES_DEFINED

typedef unsigned int			UDATA;
typedef unsigned int			U_32;
typedef unsigned short		U_16;
typedef unsigned char		U_8;
/* no generic U_64 or I_64 */

typedef int					IDATA;
typedef int					I_32;
typedef short				I_16;
typedef char				I_8;


/* temp hack -- don't typedef BOOLEAN since it's already def'ed on Win32 */
#if defined(J9WINCE)
typedef U_8 BOOLEAN;
#else
#define BOOLEAN UDATA
#endif


#endif

#ifndef J9CONST64
#define J9CONST64(x) x##L
#endif

#ifndef J9_DEFAULT_SCHED
/* by default, pthreads platforms use the SCHED_OTHER thread scheduling policy */
#define J9_DEFAULT_SCHED SCHED_OTHER
#endif

#ifndef J9_PRIORITY_MAP
/* if no priority map if provided, priorities will be determined algorithmically */
#endif

#ifndef	FALSE
#define	FALSE		((BOOLEAN) 0)

#ifndef TRUE
#define	TRUE		((BOOLEAN) (!FALSE))
#endif
#endif

#ifndef NULL
#ifdef __cplusplus
#define NULL    (0)
#else
#define NULL    ((void *)0)
#endif
#endif

#define USE_PROTOTYPES
#ifdef	USE_PROTOTYPES
#define	PROTOTYPE(x)	x
#define	VARARGS		, ...
#else
#define	PROTOTYPE(x)	()
#define	VARARGS
#endif

/* Assign the default line delimiter if it was not set */
#ifndef PLATFORM_LINE_DELIMITER
#define PLATFORM_LINE_DELIMITER	"\015\012"
#endif

/* Set the max path length if it was not set */
#ifndef MAX_IMAGE_PATH_LENGTH
#define MAX_IMAGE_PATH_LENGTH	(2048)
#endif

typedef	double	ESDOUBLE;
typedef	float		ESSINGLE;

/* helpers for U_64s */
#define CLEAR_U64(u64)  (u64 = (U_64)0)

#ifdef	J9VM_ENV_LITTLE_ENDIAN
#define	LOW_LONG(l)	(*((U_32 *) &(l)))
#define	HIGH_LONG(l)	(*(((U_32 *) &(l)) + 1))
#else
#define	HIGH_LONG(l)	(*((U_32 *) &(l)))
#define	LOW_LONG(l)	(*(((U_32 *) &(l)) + 1))
#endif

#define	I8(x)			((I_8) (x))
#define	I8P(x)			((I_8 *) (x))
#ifndef ITRON									/* Was conflicting */
#define	U16(x)			((U_16) (x))
#define	I16(x)			((I_16) (x))
#endif
#define	I16P(x)			((I_16 *) (x))
#ifndef ITRON									/* Was conflicting */
#define	U32(x)			((U_32) (x))
#define	I32(x)			((I_32) (x))
#endif
#define	I32P(x)			((I_32 *) (x))
#define	U16P(x)			((U_16 *) (x))
#define	U32P(x)			((U_32 *) (x))
#define	OBJP(x)			((J9Object *) (x))
#define	OBJPP(x)		((J9Object **) (x))
#define	OBJPPP(x)		((J9Object ***) (x))
#define	CLASSP(x)		((Class *) (x))
#define	CLASSPP(x)		((Class **) (x))
#define	BYTEP(x)		((BYTE *) (x))

/* Test - was conflicting with OS2.h */
#define	ESCHAR(x)		((CHARACTER) (x))
#define	FLT(x)			((FLOAT) x)
#define	FLTP(x)			((FLOAT *) (x))

#ifdef	NO_LVALUE_CASTING
#define	LI8(x)			(*((I_8 *) &(x)))
#define	LI8P(x)			(*((I_8 **) &(x)))
#define	LU16(x)			(*((U_16 *) &(x)))
#define	LI16(x)			(*((I_16 *) &(x)))
#define	LU32(x)			(*((U_32 *) &(x)))
#define	LI32(x)			(*((I_32 *) &(x)))
#define	LI32P(x)		(*((I_32 **) &(x)))
#define	LU16P(x)		(*((U_16 **) &(x)))
#define	LU32P(x)		(*((U_32 **) &(x)))
#define	LOBJP(x)		(*((J9Object **) &(x)))
#define	LOBJPP(x)		(*((J9Object ***) &(x)))
#define	LOBJPPP(x)		(*((J9Object ****) &(x))
#define	LCLASSP(x)		(*((Class **) &(x)))
#define	LBYTEP(x)		(*((BYTE **) &(x)))
#define	LCHAR(x)		(*((CHARACTER) &(x)))
#define	LFLT(x)			(*((FLOAT) &x))
#define	LFLTP(x)		(*((FLOAT *) &(x)))
#else
#define	LI8(x)			I8((x))
#define	LI8P(x)			I8P((x))
#define	LU16(x)			U16((x))
#define	LI16(x)			I16((x))
#define	LU32(x)			U32((x))
#define	LI32(x)			I32((x))
#define	LI32P(x)		I32P((x))
#define	LU16P(x)		U16P((x))
#define	LU32P(x)		U32P((x))
#define	LOBJP(x)		OBJP((x))
#define	LOBJPP(x)		OBJPP((x))
#define	LOBJPPP(x)		OBJPPP((x))
#define	LIOBJP(x)		IOBJP((x))
#define	LCLASSP(x)		CLASSP((x))
#define	LBYTEP(x)		BYTEP((x))
#define	LCHAR(x)		CHAR((x))
#define	LFLT(x)			FLT((x))
#define	LFLTP(x)		FLTP((x))
#endif

/* Macros for converting between words and longs and accessing bits */

#define	HIGH_WORD(x)	U16(U32((x)) >> 16)
#define	LOW_WORD(x)		U16(U32((x)) & 0xFFFF)
#define	LOW_BIT(o)		(U32((o)) & 1)
#define	LOW_2_BITS(o)	(U32((o)) & 3)
#define	LOW_3_BITS(o)	(U32((o)) & 7)
#define	LOW_4_BITS(o)	(U32((o)) & 15)
#define	MAKE_32(h, l)	((U32((h)) << 16) | U32((l)))
#define	MAKE_64(h, l)	((((I_64)(h)) << 32) | (l))

#ifdef __cplusplus
#define J9_CFUNC "C"
#define J9_CDATA "C"
#else
#define J9_CFUNC 
#define J9_CDATA
#endif

/* Macros for tagging functions which read/write the vm thread */

#define READSVMTHREAD
#define WRITESVMTHREAD
#define REQUIRESSTACKFRAME

/* macro for tagging functions which never return */
#ifdef __GNUC__
/* on GCC, we can actually pass this information on to the compiler */
#define NORETURN __attribute__((noreturn))
#else
#define NORETURN
#endif

/* on some systems (e.g. LinuxPPC) va_list is an array type.  This is probably in
 * violation of the ANSI C spec, but it's not entirely clear.  Because of this, we end
 * up with an undesired extra level of indirection if we take the address of a
 * va_list argument. 
 *
 * To get it right ,always use the VA_PTR macro
 */
#ifndef VA_PTR
#define VA_PTR(valist) (&valist)
#endif

/* Macros used on RS6000 to manipulate wrapped function pointers */
#ifndef TOC_UNWRAP_ADDRESS
#define TOC_UNWRAP_ADDRESS(wrappedPointer) (wrappedPointer)
#endif
#ifndef TOC_STORE_TOC
#define TOC_STORE_TOC(dest,wrappedPointer)
#endif

/* Macros for accessing I_64 values */
#ifdef ATOMIC_LONG_ACCESS
#define PTR_LONG_STORE(dstPtr, aLongPtr) ((*U32P(dstPtr) = *U32P(aLongPtr)), (*(U32P(dstPtr)+1) = *(U32P(aLongPtr)+1)))
#define PTR_LONG_VALUE(dstPtr, aLongPtr) ((*U32P(aLongPtr) = *U32P(dstPtr)), (*(U32P(aLongPtr)+1) = *(U32P(dstPtr)+1)))
#else
#define PTR_LONG_STORE(dstPtr, aLongPtr) (*(dstPtr) = *(aLongPtr))
#define PTR_LONG_VALUE(dstPtr, aLongPtr) (*(aLongPtr) = *(dstPtr))
#endif

/* Macro used when declaring tables which require relocations.
 * See PALMARM for more details
 */
#ifndef J9CONST_TABLE
#define J9CONST_TABLE const
#endif

/* ANSI qsort is not always available */
#ifndef J9_SORT
#define J9_SORT(base, nmemb, size, compare) qsort((base), (nmemb), (size), (compare))
#endif

#endif /* escomp_h */

