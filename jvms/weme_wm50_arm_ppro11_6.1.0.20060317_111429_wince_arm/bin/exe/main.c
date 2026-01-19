/*
*	(c) Copyright IBM Corp. 1991, 2006 All Rights Reserved
*/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "jni.h"
#include "j9port.h"
#include "j9lib.h"

#include "libhlp.h"

#ifdef NEUTRINO
#include <sys/mman.h>
#include <ctype.h>
#endif

#include "j9exenls.h"

#define CDEV_CURRENT_FUNCTION _prototypes_private
static void dumpHelpText PROTOTYPE(( J9PortLibrary *portLib, int argc, char **argv, int *copyrightWritten));
U_32 parseStringToLong PROTOTYPE((char* strarg));
static I_32 initDefaultDefines PROTOTYPE(( J9PortLibrary *portLib, void **vmOptionsTable, int argc, char **argv, int jxeBpArg, int jxeCpArg, int jarArg, J9StringBuffer **classPathInd, J9StringBuffer **javaHomeInd, J9StringBuffer **bootLibraryPathInd, J9StringBuffer **javaLibraryPathInd));
#if (defined(J9VM_OPT_JXE_LOAD_SUPPORT)) /* priv. proto (autogen) */

static int handleNeutrinoJxeSpaceArg PROTOTYPE((J9PortLibrary * portLib, int jxeSpaceArg, char **argv));
#endif /* J9VM_OPT_JXE_LOAD_SUPPORT (autogen) */



UDATA VMCALL gpProtectedMain PROTOTYPE((void *arg));

#undef CDEV_CURRENT_FUNCTION


#ifdef NEUTRINO
#define CDEV_CURRENT_FUNCTION parseStringToLong
/*  Added due to jxespace option.  Used to parse string values into hex long equivalents from the command line 
	Assumes a hex string of 8 characters or less and terminate on a space, comma, or end of string.
	Returns a long hex value.  
*/   
U_32 parseStringToLong(char* strarg)
{ 
	char value[16];		/* hopefully 16 bytes is enough on all platforms */

	if (isxdigit(strarg[0])) {
		int i;
		for (i = 0; i < 8; i++) {
			if (isxdigit(strarg[i])) {
				value[i] = strarg[i];

				if (strarg[i+1] == ',' || 	strarg[i+1] == 0x20 || strarg[i+1] == 0x0) {
					value[i+1] = 0x0;
					return atoh(&value[0]);
				}
			} else {
				return 0;
			}
		}
	} 
	return 0;
}

#undef CDEV_CURRENT_FUNCTION

#define CDEV_CURRENT_FUNCTION handleNeutrinoJxeSpaceArg
#if (defined(J9VM_OPT_JXE_LOAD_SUPPORT)) /* priv. proto (autogen) */

static int 
handleNeutrinoJxeSpaceArg(J9PortLibrary * portLib, int jxeSpaceArg, char **argv)
{
	PORT_ACCESS_FROM_PORT(portLib);
	char *tmpargv      = &argv[jxeSpaceArg][10];
	char *partitionStr = NULL;
	char *virtStr      = NULL;
	int correctParms   = 0;
	U_32 physicalAddr  = 0;
	U_32 jxeSpaceSize  = 0;
	void *logicalAddr  = NULL;
	void *mappedAddr   = NULL;

	/* parse out the jxespace options, all parameters are expected to be hex */
	physicalAddr = parseStringToLong(tmpargv);
	partitionStr = strchr(tmpargv, ',');
	if (partitionStr) {
		jxeSpaceSize = parseStringToLong(partitionStr + 1);
		correctParms = 1;
		virtStr = strchr(partitionStr + 1, ',');
		if (virtStr) {
			logicalAddr = (void *) parseStringToLong(virtStr + 1);
		}
	}

	/* Don't continue if parsing failed or requested size is 0 */
	if (!correctParms || !jxeSpaceSize) {
		j9nls_printf(PORTLIB, J9NLS_ERROR, J9NLS_EXE_INVALID_JXESPACE ); /* \nInvalid jxespace parameters.\n */
		return 8;
	}

	/* Get the logical mapped addr. */
	mappedAddr = mmap_device_memory(logicalAddr, jxeSpaceSize, PROT_READ | PROT_NOCACHE, 0, physicalAddr);
	if (mappedAddr == MAP_FAILED) {
		j9nls_printf( PORTLIB, J9NLS_ERROR, J9NLS_EXE_ERROR_MAPPING_JXE_IN_FLASH ); /* \nError mapping jxe in flash\n */
		return 7;
	}

	return 0;
}

#endif /* J9VM_OPT_JXE_LOAD_SUPPORT (autogen) */


#undef CDEV_CURRENT_FUNCTION

#endif

#if defined(J9ZOS390)
#include "atoe.h"
#endif

#define CDEV_CURRENT_FUNCTION dumpHelpText
static void dumpHelpText( J9PortLibrary *portLib, int argc, char **argv, int *copyrightWritten)
{
	PORT_ACCESS_FROM_PORT(portLib);

	if( *copyrightWritten == 0 ) {
		dumpCopyrights(portLib);
		*copyrightWritten = 1;
	}

#ifdef J9VM_OPT_DYNAMIC_LOAD_SUPPORT
	j9file_printf(PORTLIB, 
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_1, "Usage:\t%s [options] classname [args...]\n" ),
		argv[0]
	);
#endif
#ifdef J9VM_OPT_JXE_LOAD_SUPPORT
	j9file_printf(PORTLIB, 
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_2, "Usage:\t%s [options] -jxe:<jxeFile> [args...]\n" ),
		argv[0]
	);
	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT,
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_2_1, "Usage:\t%s [-jxe] [options] <jxeFile> [args...]\n" ),
		argv[0]
	);
#endif
	j9file_printf(PORTLIB, 
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_3, "\n[options]\n"
		"  -classpath <path>\n"
		"  -cp <path>       set classpath to <path>.\n" ) 
	);

#ifdef J9VM_OPT_JXE_LOAD_SUPPORT
	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT,
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_4, "  -jxe:<jxeFile>   run the named jxe file.\n" ) 
	);
	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_4_1, "  -jxe <jxeFile>   places jxeFile on the classpath and executes the startup\n"
		"                    class found in jxeFile.\n" ) 
	);
#ifdef NEUTRINO
	j9file_printf(PORTLIB, 
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_5, "  -jxespace:<physicalAddr>,<size>,<logicalAddr>\n"
		"                   map memory region for jxes, (values are in hex).\n"
		"  -jxeaddr:<logicalAddr>\n"
		"                   run a jxe directly from memory, (address is in hex).\n" ) 
	);
#endif /* NEUTRINO */
#endif /* J9VM_OPT_JXE_LOAD_SUPPORT */

	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_6, "  -D<prop>=<val>   set the value of a system property.\n" )
	); /* PGG */
#if defined(J9VM_INTERP_DEBUG_SUPPORT)
	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_7, "  -debug:<options> enable debug, JDWP standard <options>.\n" )
	); 
#endif
#if !defined(J9VM_OPT_LINKED_CLASSES_ZIP)
	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT, 	
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_8, "  -jcl:<config>[:options]\n"
		"                   specify which JCL DLL to use (e.g. cdc, cldc, ...).\n" )
	); 
#endif
#if defined(J9VM_INTERP_VERBOSE)
	j9file_printf(PORTLIB,
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_9, "  -verbose[:class,gc,stack,sizes]\n"
		"                   enable verbose output (default=class).\n" )
	);
#endif
	j9file_printf(PORTLIB, 
		J9PORT_TTY_OUT, 
		portLib->nls_lookup_message( PORTLIB, J9NLS_DO_NOT_PRINT_MESSAGE_TAG, J9NLS_EXE_HELPTEXT_10, "  -verify          enable class file verification.\n"
		"  -X               print help on non-standard options.\n" )
	);

	return;
}
#undef CDEV_CURRENT_FUNCTION
  
#define CDEV_CURRENT_FUNCTION gpProtectedMain
/* note - this cannot be static, since it's called externally by WinMain, for instance */
UDATA VMCALL gpProtectedMain(void *arg)
{
	struct j9cmdlineOptions *startupOptions = (struct j9cmdlineOptions *) arg;
	int argc = startupOptions->argc;
	char **argv = startupOptions->argv;
	J9StringBuffer *javaHome = NULL, *classPath = NULL, *bootLibraryPath = NULL, *javaLibraryPath = NULL;
	J9PortLibrary *j9portLibrary = startupOptions->portLibrary;
	JavaVM *jvm = NULL;
	JNIEnv *env = NULL;
	JavaVMInitArgs vm_args;
	int rc = 1, i, javaRc = 0;
	UDATA classArg = argc;
	char *mainClass = NULL;
	void *vmOptionsTable = NULL;
	int isStandaloneJar = 0;
	int isStandaloneJxe = 0;
	int jxeArg = 0;
	int copyrightWritten = 0;
	int writeVersion = 0;
	int isNameUTF = 0;

#if defined(J9VM_OPT_JXE_LOAD_SUPPORT) 
	void *jxeUtil = NULL;
	void *jxeName = NULL;
#if defined(NEUTRINO)
	int jxeSpaceArg = 0;
#endif /* NEUTRINO */
#endif /* J9VM_OPT_JXE_LOAD_SUPPORT */

#ifdef J9VM_STATIC_LINKAGE
	J9StringBuffer *jclArg = NULL;
	extern const char jclOption[];
	extern const char *jclExtraLibs;
#endif
	extern const char *jclProfile;

	main_setNLSCatalog(j9portLibrary, argv);

	/* 
	   we start by scanning the command line, looking for the first arg that does not have a - in front of it.  This is 
	   taken to be the class we are trying to load. NB: skip argv[0], the exe name. 
	   Include some lightweight integrity checking.  */

	for (i = 1; i < argc; i++) {
		if ('-' != argv[i][0]) {
			classArg = i;
			mainClass = argv[i];
			break;
		} else if ((strcmp("-cp", argv[i]) == 0) || (strcmp("-classpath", argv[i]) == 0)) {
			if ((i + 1) >= argc) {
				/* "\n%s requires a parameter\n" */
				j9portLibrary->nls_printf(j9portLibrary, J9NLS_ERROR, J9NLS_EXE_REQUIRES_PARM, argv[i]);
				dumpHelpText(j9portLibrary, argc, argv, &copyrightWritten);
				return 0;
			}
 			i++;			/* Skip the next arg */
		}

		if (0 == strcmp("-version", argv[i])) {
			writeVersion = 2;
		}

		if (0 == strcmp("-showversion", argv[i])) {
			if(!writeVersion) {
					writeVersion = 1;
			}
		}

		if ((0 == strcmp("-help", argv[i]))||(0 == strcmp("-?", argv[i]))) {
			dumpHelpText(j9portLibrary, argc, argv, &copyrightWritten);
			return 0;
		}

		if (0 == strcmp("-X", argv[i])) {
			describeInternalOptions(j9portLibrary);
			return 0;
		}

		if (strcmp("-jar", argv[i]) == 0) {
			isStandaloneJar = 1;
		}

#if defined(J9VM_OPT_JXE_LOAD_SUPPORT) 
		if (strcmp("-jxe", argv[i]) == 0) {
			isStandaloneJxe = 1;
		}

		if (!strncmp("-jxe:", argv[i], 5)) {
			classArg = i;
			jxeArg = i;
			break;
		}
#if defined(NEUTRINO)
		if (!strncmp("-jxespace:", argv[i], 10)) {
			jxeSpaceArg = i;
		}
#endif /* NEUTRINO */
#endif /* J9VM_OPT_JXE_LOAD_SUPPORT */
	}

#ifdef J9VM_OPT_REMOTE_CONSOLE_SUPPORT
	remoteConsole_parseCmdLine(j9portLibrary, classArg - 1, argv);
#endif

#ifdef J9VM_OPT_MEMORY_CHECK_SUPPORT
	/* This should happen before anybody allocates memory!  Otherwise, shutdown will not work properly. */
	memoryCheck_parseCmdLine(j9portLibrary, classArg - 1, argv);
#endif /* J9VM_OPT_MEMORY_CHECK_SUPPORT */

#if defined(J9VM_OPT_JXE_LOAD_SUPPORT)
#if defined(NEUTRINO)
	if (jxeSpaceArg) {
		rc = handleNeutrinoJxeSpaceArg(j9portLibrary, jxeSpaceArg, argv);
		if (rc)
			goto cleanup;
	}
#endif /* NEUTRINO */
#endif /* J9VM_OPT_JXE_LOAD_SUPPORT */

	vmOptionsTable = NULL;

	vmOptionsTableInit(j9portLibrary, &vmOptionsTable, 15);
	if (NULL == vmOptionsTable)
		goto cleanup;

#if defined(J9VM_OPT_JXE_LOAD_SUPPORT)
	if ( jxeArg ) {
		if ( vmOptionsTableAddOption(&vmOptionsTable, "_jxe", (void *) (argv[jxeArg]+5)) != J9CMDLINE_OK ) {
			goto cleanup;
		}
		jxeUtil = main_createJxeUtilities( j9portLibrary );
		if ( !jxeUtil ) {
			rc = 10;
			goto cleanup;
		}
		jxeName = argv[jxeArg]+5;
		main_findMainClassAndUpdateVMOptionsTableFromJXE( j9portLibrary, &mainClass, NULL, &vmOptionsTable, jxeUtil, jxeName );
		if ( !mainClass ) {
			rc = 11;
			goto cleanup;
		}
	}
	if ( isStandaloneJxe ) {
		if ( !jxeUtil ) {
			jxeUtil = main_createJxeUtilities( j9portLibrary );
			if ( !jxeUtil ) {
				rc = 10;
				goto cleanup;
			}
			if ( classArg == argc ) {
				/* a jxe was not supplied with -jxe */
				dumpHelpText(j9portLibrary, argc, argv, &copyrightWritten);
				rc = 4;
				goto cleanup;
			}
			jxeName = argv[classArg];
			main_findMainClassAndUpdateVMOptionsTableFromJXE( j9portLibrary, &mainClass, NULL, &vmOptionsTable, jxeUtil, jxeName );
			if ( !mainClass ) {
				rc = 11;
				goto cleanup;
			}
		}
	}
#endif  /* J9VM_OPT_JXE_LOAD_SUPPORT */

#ifdef J9VM_STATIC_LINKAGE
	/* on static platforms add a default -Xjcl option for the library which we're linked against */
	if (NULL == (jclArg = strBufferCat(j9portLibrary, NULL, "-Xjcl:"))) {
		goto cleanup;
	}
	if (NULL == (jclArg = strBufferCat(j9portLibrary, jclArg, jclOption))) {
		goto cleanup;
	}
	if ( jclExtraLibs ) {
		if (NULL == (jclArg = strBufferCat(j9portLibrary, jclArg, ":"))) {
			goto cleanup;
		}
		if (NULL == (jclArg = strBufferCat(j9portLibrary, jclArg, jclExtraLibs))) {
			goto cleanup;
		}
	}
	if (vmOptionsTableAddOption(&vmOptionsTable, strBufferData(jclArg), (void *) NULL) != J9CMDLINE_OK) {
		goto cleanup;
	}
#else
	if ( jclProfile ) {
		/* when a default profile is specified add a -jcl:<profile> option */
		if (vmOptionsTableParseArgs(j9portLibrary, &vmOptionsTable, 1, (char**)&jclProfile) != J9CMDLINE_OK) {
			goto cleanup;
		}
	}
#endif

	if (vmOptionsTableAddExeName(&vmOptionsTable, argv[0]) != J9CMDLINE_OK)
		goto cleanup;
	if (vmOptionsTableAddOption(&vmOptionsTable, "_port_library", (void *) j9portLibrary) != J9CMDLINE_OK)
		goto cleanup;

	/* do not substract 1 from classArg  (i.e., 'classArg-1') when jxeArg is present since the 'classArg' is the -jxe: option */
	if (vmOptionsTableParseArgs(j9portLibrary, &vmOptionsTable, classArg - (jxeArg?0:1), &(argv[1])) != J9CMDLINE_OK)
		goto cleanup;

	/* Check that the minimum required -D options have been included.  If not, calculate and add the defaults */
	initDefaultDefines(j9portLibrary, &vmOptionsTable, argc, argv, jxeArg, isStandaloneJxe?classArg:0, isStandaloneJar?classArg:0, &classPath, &javaHome, &bootLibraryPath, &javaLibraryPath);

	vm_args.version = JNI_VERSION_1_2;
	vm_args.nOptions = vmOptionsTableGetCount(&vmOptionsTable);
	vm_args.options = vmOptionsTableGetOptions(&vmOptionsTable);
	vm_args.ignoreUnrecognized = JNI_FALSE;

	if (JNI_CreateJavaVM(&jvm, (void**)&env, &vm_args)) {
		/* "Internal VM error: Failed to create Java VM\n" */
		j9portLibrary->nls_printf(j9portLibrary, J9NLS_ERROR, J9NLS_EXE_INTERNAL_VM_ERROR_CREATE_FAILED);
		/* "Run %s -help for usage\n" */
		j9portLibrary->nls_printf(j9portLibrary, J9NLS_INFO, J9NLS_EXE_RUN_HELP, argv[0] );
		rc = 2;
		if ( writeVersion ) {
			dumpVersionInfo( j9portLibrary, NULL, &copyrightWritten );
		}
		goto cleanup;
	}

	rc = 0;

	if ( writeVersion ) {
		dumpVersionInfo( j9portLibrary, env, &copyrightWritten );
		if ( writeVersion > 1 ) {
			/* -version was on the command line, so display and exit */
			goto destroy_jvm;
		}
	}

	if (mainClass) {
		if (isStandaloneJar) {
			jclass jarRunner;
			jclass clazz;
			jmethodID mID;
			jstring jStrObject; 
			
			/* using Class.forName as J2ME JCLs do not return a catchable exception from FindClass*/
			mainClass = "com.ibm.oti.vm.JarRunner";
			jStrObject = (*env)->NewStringUTF(env, mainClass);
			if (!jStrObject) {
				(*env)->ExceptionDescribe(env);
				rc = 3;
				goto destroy_jvm;
			}			

			clazz = (*env)->FindClass(env, "java/lang/Class");
			if (!clazz) {
				(*env)->ExceptionDescribe(env);	
				rc = 3;
				goto destroy_jvm;
			}	

			mID = (*env)->GetStaticMethodID(env, clazz, "forName", "(Ljava/lang/String;)Ljava/lang/Class;");
			if (!mID) {
				(*env)->ExceptionDescribe(env);
				rc = 3;
				goto destroy_jvm;
			}	

			/* should not spawn an exception if using JCL greater than J2ME */
			jarRunner = (*env)->CallStaticObjectMethod(env, clazz, mID, jStrObject);

			if (jarRunner) {
				(*env)->DeleteLocalRef(env, jarRunner);
				classArg -= 1; /* make sure that the JAR is the first argument */
			} else {
				(*env)->ExceptionClear(env);
				/* "-jar option is not available for this class library\n" */
				j9portLibrary->nls_printf(j9portLibrary, J9NLS_ERROR, J9NLS_EXE_JAR_OPTION_NOT_AVAIL );
				rc = 3;
				goto destroy_jvm;
			}
		}
		javaRc = main_runJavaMain(env, mainClass, isNameUTF, (argc - (classArg + 1)), &argv[classArg + 1], j9portLibrary);
	} else {
		dumpHelpText(j9portLibrary, argc, argv, &copyrightWritten);
		rc = 4;
	}

	destroy_jvm:
	(*jvm)->DestroyJavaVM(jvm);

  cleanup:
	switch (rc) {
	case 1:
		/* "VM startup error: Out of memory\n" */
		j9portLibrary->nls_printf(j9portLibrary, J9NLS_ERROR, J9NLS_EXE_OUT_OF_MEMORY );
		break;
	/* case 4: help text was displayed */
	/* case 3,7,8,9: various jxe msgs already printed */
#if defined(J9VM_OPT_JXE_LOAD_SUPPORT) 
	case 10:
		/* could not create JXE Util */
		j9portLibrary->nls_printf(j9portLibrary, J9NLS_ERROR, J9NLS_EXE_COULD_NOT_INITIALIZE_JXE_UTILITIES );
		break;
	case 11:
		/* JXE did not contain a mainClass */
		j9portLibrary->nls_printf(j9portLibrary, J9NLS_ERROR, J9NLS_EXE_JXE_DID_NOT_CONTAIN_STARTUP_CLASS, jxeName );
		break;
#endif
	}
#if defined(J9VM_OPT_JXE_LOAD_SUPPORT) 
	if (jxeUtil) {
		main_destroyJxeUtilities(j9portLibrary, jxeUtil);
	}
#endif
#ifdef J9VM_STATIC_LINKAGE
	if (jclArg) {
		j9portLibrary->mem_free_memory(j9portLibrary, jclArg);
	}
#endif
	if (classPath) {
		j9portLibrary->mem_free_memory(j9portLibrary, classPath);
	}
	if (javaHome) {
		j9portLibrary->mem_free_memory(j9portLibrary, javaHome);
	}
	if (bootLibraryPath) {
		j9portLibrary->mem_free_memory(j9portLibrary, bootLibraryPath);
	}
	if (javaLibraryPath) {
		j9portLibrary->mem_free_memory(j9portLibrary, javaLibraryPath);
	}
	if (vmOptionsTable) {
		vmOptionsTableDestroy(&vmOptionsTable);
	}

#ifdef J9VM_OPT_MEMORY_CHECK_SUPPORT
	memoryCheck_shutdown(j9portLibrary);
#endif
	return (rc ? rc : javaRc);
}

#undef CDEV_CURRENT_FUNCTION

#define CDEV_CURRENT_FUNCTION initDefaultDefines
static I_32 initDefaultDefines(  J9PortLibrary *portLib, void **vmOptionsTable, int argc, char **argv, int jxeBpArg, int jxeCpArg, int jarArg, J9StringBuffer **classPathInd, J9StringBuffer **javaHomeInd, J9StringBuffer **bootLibraryPathInd, J9StringBuffer **javaLibraryPathInd)
{
	extern char* getDefineArgument(char*,char*);

	int optionCount, i;
	JavaVMOption *options;
	int hasJavaHome = 0;
	int hasBootLibraryPath = 0; 
	int hasJavaLibraryPath = 0;
	int hasClassPath = 0;
	J9StringBuffer *classPath = NULL;
	J9StringBuffer *javaHome = NULL;
	J9StringBuffer *bootLibraryPath = NULL;
	J9StringBuffer *javaLibraryPath = NULL;

	/* Cycle through the list of VM options and check that the minimum required defaults are there.
	 * Calculate and insert the missing ones
	 */

	optionCount = vmOptionsTableGetCount(vmOptionsTable);
	options = vmOptionsTableGetOptions(vmOptionsTable);

	for(i  = 0; i < optionCount; i++) {
		if(getDefineArgument(options[i].optionString, "java.home")) { hasJavaHome = 1; continue; }
		if(getDefineArgument(options[i].optionString, "com.ibm.oti.vm.bootstrap.library.path")) { hasBootLibraryPath = 1; continue; }
		if(getDefineArgument(options[i].optionString, "java.library.path")) { hasJavaLibraryPath = 1; continue; }
		if(getDefineArgument(options[i].optionString, "java.class.path")) { 
			/* Ignore classpath defines for -jar */
			if(!jarArg && !jxeBpArg && !jxeCpArg) {
				hasClassPath = 1; 
				continue; 
			}
		}
	}

	if (!hasJavaHome)  {
		if (0 != main_initializeJavaHome( portLib, &javaHome, argc, argv ))  {
			/* This might be a memory leak, but main() will fail anyway */
			return -1;
		}
		if(javaHome) {
			javaHome = strBufferPrepend(portLib, javaHome, "-Djava.home=");
			if(!javaHome) return -1;
			*javaHomeInd = javaHome;
			if(vmOptionsTableAddOption(vmOptionsTable, strBufferData(javaHome), NULL) != J9CMDLINE_OK) return -1;
		}
	}

	if (!hasBootLibraryPath) {
		if (0 != main_initializeBootLibraryPath( portLib, &bootLibraryPath, argv[0] ))  {
			/* This might be a memory leak, but main() will fail anyway */
			return -1;
		}
		if(bootLibraryPath) {
			bootLibraryPath = strBufferPrepend(portLib, bootLibraryPath , "-Dcom.ibm.oti.vm.bootstrap.library.path=");
			if(!bootLibraryPath) return -1;
			*bootLibraryPathInd = bootLibraryPath;
			if(vmOptionsTableAddOption(vmOptionsTable, strBufferData(bootLibraryPath), NULL) != J9CMDLINE_OK) return -1;
		}
	}

	if (!hasJavaLibraryPath) {
		if (0 != main_initializeJavaLibraryPath( portLib, &javaLibraryPath, argv[0] ))  {
			/* This might be a memory leak, but main() will fail anyway */
			return -1;
		}
		if(javaLibraryPath) {
			javaLibraryPath = strBufferPrepend(portLib, javaLibraryPath, "-Djava.library.path=");
			if(!javaLibraryPath) return -1;
			*javaLibraryPathInd = javaLibraryPath;
			if(vmOptionsTableAddOption(vmOptionsTable, strBufferData(javaLibraryPath), NULL) != J9CMDLINE_OK) return -1;
		}
	}
	
	if(!hasClassPath) {
		/* no free classpath if there is a JXE or -jar */
		if(jarArg) {
			if (jarArg < argc) {
				classPath = strBufferCat(portLib, classPath, argv[jarArg]);
				if (classPath == NULL) return -1;
			}
		} else if (jxeCpArg) {
			if (jxeCpArg < argc) {
				classPath = strBufferCat(portLib, classPath, argv[jxeCpArg]);
				if (classPath == NULL) return -1;
			}
		} else if (!jxeBpArg) {
			if (0 != main_initializeClassPath( portLib, &classPath)) {
				/* This might be a memory leak, but main() will fail anyway */
				return -1;
			}
			if (classPath == NULL || classPath->data[0] == 0) {
				classPath = strBufferCat(portLib, classPath, ".");
				if (classPath == NULL) return -1;
			}
		}

		classPath = strBufferPrepend(portLib, classPath, "-Djava.class.path=");
		if (classPath == NULL) return -1;
		*classPathInd = classPath;
		if(vmOptionsTableAddOption(vmOptionsTable, strBufferData(classPath), NULL) != J9CMDLINE_OK) return -1;
	}

	return 0;
}
#undef CDEV_CURRENT_FUNCTION

#define CDEV_CURRENT_FUNCTION 

#undef CDEV_CURRENT_FUNCTION

