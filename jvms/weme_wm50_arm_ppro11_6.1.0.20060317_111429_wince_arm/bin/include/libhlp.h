/*
	(c) Copyright IBM Corp. 1998, 2006  All Rights Reserved
	Headers for exelib functions.

	File generated in stream: 'GA 2.3'
*/

#ifndef LIBHLP_H
#define LIBHLP_H

#ifdef __cplusplus
extern "C" {
#endif

#include "j9comp.h"
#include "j9port.h"
#include "jni.h"

#define J9CMDLINE_OK 0
#define J9CMDLINE_PARSE_ERROR 1
#define J9CMDLINE_OUT_OF_MEMORY 2
#define J9CMDLINE_GENERIC_ERROR 3


typedef struct J9StringBuffer {
    UDATA remaining;
    U_8 data[4];
} J9StringBuffer;

#define J9SIZEOF_J9StringBuffer 8

typedef struct J9IVERelocatorStruct {
    UDATA dllHandle;
    I_32  (PVMCALL iveLoadJxeFromFile)( J9PortLibrary *portLib, const char *fileName, void **jxePtr, void **allocPtr, UDATA *flags ) ;
    char*  (PVMCALL iveRelocateMessage)(int returnCode) ;
    I_32  (PVMCALL iveFindFileInJar)(
	void          *jarPtr,
	char          *fileName,
	I_32           fileNameLength,
	char         **fileContents,
	I_32          *fileContentsLength
	) ;
    void*  (PVMCALL iveGetJarInfoValues)(
	J9PortLibrary *portLib,
	void          *jarPtr,
	I_32           *_count,
	char        ***_keys,
	char        ***_vals
	) ;
    void  (PVMCALL iveFreeJarInfoValues)(
	J9PortLibrary *portLib,
	void          *jarInfoValues
	) ;
    void* romImage[2];
    struct J9JXEInfo* romImageInfo;
    void* jarPtr;
    void* jarAllocPtr;
    void* jarInfo;
    I_32 jarInfoCount;
    char** jarInfoKeys;
    char** jarInfoVals;
} J9IVERelocatorStruct;

#define J9SIZEOF_J9IVERelocatorStruct 60

typedef struct J9JXEInfo {
    struct J9ROMImageHeader* imageHeader;
    void* jxePointer;
    void* jxeAlloc;
    struct J9ClassLoader* classLoader;
    U_8* filename;
    UDATA flags;
    UDATA referenceCount;
} J9JXEInfo;

#define J9SIZEOF_J9JXEInfo 28

#define J9JXE_USER_CLASS_PATH  2
#define J9JXE_FLAGS_NAME_ALLOCATED  32
#define J9JXE_AOT_UNUSABLE  4
#define J9JXE_BOOT_CLASS_PATH  1
#define J9JXE_CLASS_PATH_MASK  3
#define J9JXE_UNUSABLE  8
#define J9JXE_FLAGS_ALLOCATED  16
#define J9JXE_FLAGS_IC_LOAD_REPORTED  64
#define J9JXE_FLAGS_MMAPED  0x80
#define J9JXE_FLAGS_VMEM_ALLOCATED  0x100

struct j9cmdlineOptions {
	int argc;
	char** argv;
	char** envp;
	J9PortLibrary* portLibrary;
};

struct J9PortLibrary ;
extern J9_CFUNC J9StringBuffer* strBufferCat PROTOTYPE((struct J9PortLibrary *portLibrary, J9StringBuffer* buffer, const char* string));
extern J9_CFUNC char* strBufferData PROTOTYPE((J9StringBuffer* buffer));
struct J9PortLibrary ;
extern J9_CFUNC J9StringBuffer* strBufferPrepend PROTOTYPE((struct J9PortLibrary *portLibrary, J9StringBuffer* buffer, char* string));
struct J9PortLibrary ;
extern J9_CFUNC J9StringBuffer* strBufferEnsure PROTOTYPE((struct J9PortLibrary *portLibrary, J9StringBuffer* buffer, UDATA len));
extern J9_CFUNC I_32 main_prependToClassPath PROTOTYPE(( J9PortLibrary *portLib, U_16 sep, J9StringBuffer **classPath, char *toPrepend));
extern J9_CFUNC void 
dumpVersionInfo PROTOTYPE((J9PortLibrary * portLib, JNIEnv *env, int *copyrightWritten));
extern J9_CFUNC int main_runJavaMain PROTOTYPE((JNIEnv * env, char *mainClassName, int nameIsUTF, int java_argc, char **java_argv, J9PortLibrary * j9portLibrary));
extern J9_CFUNC I_32 main_appendToClassPath PROTOTYPE(( J9PortLibrary *portLib, U_16 sep, J9StringBuffer **classPath, char *toAppend));
extern J9_CFUNC void dumpCopyrights PROTOTYPE(( J9PortLibrary *portLib ));
extern J9_CFUNC char * vmDetailString PROTOTYPE(( J9PortLibrary *portLib, char *detailString, int detailStringLength ));
extern J9_CFUNC char * main_vmVersionString PROTOTYPE((void));
extern J9_CFUNC IDATA main_initializeJavaLibraryPath PROTOTYPE((J9PortLibrary * portLib, J9StringBuffer **finalJavaLibraryPath, char *argv0));
extern J9_CFUNC IDATA main_initializeBootLibraryPath PROTOTYPE((J9PortLibrary * portLib, J9StringBuffer **finalBootLibraryPath, char *argv0));
extern J9_CFUNC void main_setNLSCatalog PROTOTYPE((J9PortLibrary * portLib, char **argv));
extern J9_CFUNC I_32 main_initializeClassPath PROTOTYPE(( J9PortLibrary *portLib, J9StringBuffer** classPath));
extern J9_CFUNC IDATA main_initializeJavaHome PROTOTYPE((J9PortLibrary * portLib, J9StringBuffer **finalJavaHome, int argc, char **argv));
extern J9_CFUNC void
main_findMainClassAndUpdateVMOptionsTableFromJXE PROTOTYPE(( J9PortLibrary *portLib, char **mainClass, BOOLEAN *requiresToolsExtDir, void **vmOptionsTable, void *jxeUtil, char *jxe ));
extern J9_CFUNC void *
main_createJxeUtilities PROTOTYPE(( J9PortLibrary *portLib ));
extern J9_CFUNC void
main_destroyJxeUtilities PROTOTYPE(( J9PortLibrary *portLib, void *jxeUtilities ));
extern J9_CFUNC I_32 vmOptionsTableAddExeName PROTOTYPE((
	void **vmOptionsTable, 
	char  *argv0
	));
extern J9_CFUNC void describeInternalOptions PROTOTYPE((J9PortLibrary *portLib));
extern J9_CFUNC int vmOptionsTableGetCount PROTOTYPE((
	void **vmOptionsTable
	));
extern J9_CFUNC I_32 vmOptionsTableAddOption PROTOTYPE((
	void **vmOptionsTable, 
	char  *optionString,
	void  *extraInfo
	));
extern J9_CFUNC I_32 vmOptionsTableParseArgs PROTOTYPE((
	J9PortLibrary *portLib,
	void **vmOptionsTable,
	int    argc, 
	char  *argv[]
	));
extern J9_CFUNC JavaVMOption *vmOptionsTableGetOptions PROTOTYPE((
	void **vmOptionsTable
	));
extern J9_CFUNC void vmOptionsTableDestroy PROTOTYPE((
	void **vmOptionsTable
	));
extern J9_CFUNC I_32 vmOptionsTableParseArgInternal PROTOTYPE((
	J9PortLibrary *portLib,
	void **vmOptionsTable,
	char  *argv
	));
extern J9_CFUNC I_32 vmOptionsTableParseArg PROTOTYPE((
	J9PortLibrary *portLib,
	void **vmOptionsTable,
	int *argc,
	char  *argv[]
	));
extern J9_CFUNC I_32 vmOptionsTableAddOptionWithCopy PROTOTYPE((
	void **vmOptionsTable, 
	char  *optionString,
	void  *extraInfo
	));
extern J9_CFUNC I_32 vmOptionsTableInit PROTOTYPE((
	J9PortLibrary    *portLib,
	void            **vmOptionsTable,
	int              initialCount
	));
extern J9_CFUNC IDATA VMCALL memoryCheck_initialize PROTOTYPE((J9PortLibrary * portLib, char const *modeStr));
extern J9_CFUNC UDATA VMCALL memoryCheck_parseCmdLine PROTOTYPE(( J9PortLibrary *portLibrary, UDATA lastLegalArg , char **argv ));
extern J9_CFUNC void VMCALL memoryCheck_shutdown PROTOTYPE((J9PortLibrary * portLib));
extern J9_CFUNC UDATA VMCALL
remoteConsole_parseCmdLine PROTOTYPE((J9PortLibrary *portLibrary, UDATA lastLegalArg, char **argv));

#ifdef __cplusplus
}
#endif

#endif /* LIBHLP_H */
