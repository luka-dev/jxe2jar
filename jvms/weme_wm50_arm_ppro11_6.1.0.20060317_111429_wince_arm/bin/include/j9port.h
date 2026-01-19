/*
 (c) Copyright IBM Corp. 1991, 2006 All Rights Reserved
 File generated in stream: 'GA 2.3'
*/

/**
 * @file
 * @ingroup Port
 * @brief Port Library Header
 */

#ifndef portlibrarydefines_h
#define portlibrarydefines_h


/* fix for linux s390 32bit stdint vs unistd.h definition of intptr_t (see CMVC 73850) */
#if defined(LINUX) && defined(S390)
#include <stdint.h>
#endif

#include <stdarg.h>	/* for va_list */
#if defined(J9OSE) 
#include <unistd.h>
#endif
#include "j9comp.h"
#include "j9cfg.h"
#include "j9thread.h"
#include "j9socket.h"
#include "gp.h"	/* for typedefs of function arguments to gp functions */

#if defined(J9VM_INTERP_SIG_QUIT_THREAD) && (defined(LINUX) || defined(RS6000) || defined(SOLARIS) || defined(DECUNIX) || defined(OSX) || defined(IRIX))
#include <unistd.h>
#endif

/**
 * @name Port library access
 * @anchor PortAccess
 * Macros for accessing port library.
 * @{
 */
#ifdef USING_VMI
#define PORT_ACCESS_FROM_ENV(jniEnv) \
VMInterface *portPrivateVMI = VMI_GetVMIFromJNIEnv(jniEnv); \
J9PortLibrary *privatePortLibrary = (*portPrivateVMI)->GetPortLibrary(portPrivateVMI)
#define PORT_ACCESS_FROM_JAVAVM(javaVM) \
VMInterface *portPrivateVMI = VMI_GetVMIFromJavaVM(javaVM); \
J9PortLibrary *privatePortLibrary = (*portPrivateVMI)->GetPortLibrary(portPrivateVMI)
#else
#define PORT_ACCESS_FROM_ENV(jniEnv) J9PortLibrary *privatePortLibrary = ((J9VMThread *) (jniEnv))->javaVM->portLibrary
#define PORT_ACCESS_FROM_JAVAVM(javaVM) J9PortLibrary *privatePortLibrary = (javaVM)->portLibrary
#define PORT_ACCESS_FROM_VMC(vmContext) J9PortLibrary *privatePortLibrary = (vmContext)->javaVM->portLibrary
#define PORT_ACCESS_FROM_GINFO(javaVM) J9PortLibrary *privatePortLibrary = (javaVM)->portLibrary
#define PORT_ACCESS_FROM_JITCONFIG(jitConfig) J9PortLibrary *privatePortLibrary = (jitConfig)->javaVM->portLibrary
#define PORT_ACCESS_FROM_WALKSTATE(walkState) J9PortLibrary *privatePortLibrary = (walkState)->walkThread->javaVM->portLibrary
#endif
#define PORT_ACCESS_FROM_VMI(vmi) J9PortLibrary *privatePortLibrary = (*vmi)->GetPortLibrary(vmi)
#define PORT_ACCESS_FROM_PORT(portLibrary) J9PortLibrary *privatePortLibrary = (portLibrary)
/** @} */

#define J9_STR_(x) #x
#define J9_STR(x) J9_STR_(x)
#define J9_GET_CALLSITE() __FILE__ ":" J9_STR(__LINE__)

#define PORTLIB privatePortLibrary

/**
 * @name File Operations
 * @anchor PortFileOperations
 * File operation modifiers.
 * @{
 */
#ifdef BREW
#include "AEEFile.h"
#define	EsSeekSet	_SEEK_START
#define	EsSeekCur	_SEEK_CURRENT
#define	EsSeekEnd	_SEEK_END
#else
#ifdef		SEEK_SET
#define	EsSeekSet	SEEK_SET	/* Values for EsFileSeek */
#else
#define	EsSeekSet	0
#endif
#ifdef 		SEEK_CUR
#define	EsSeekCur	SEEK_CUR
#else
#define	EsSeekCur	1
#endif
#ifdef		SEEK_END
#define	EsSeekEnd	SEEK_END
#else
#define	EsSeekEnd	2
#endif
#endif

#define	EsOpenRead		1	/* Values for EsFileOpen */
#define	EsOpenWrite		2
#define	EsOpenCreate	4
#define	EsOpenTruncate	8
#define	EsOpenAppend	16
#define	EsOpenText		32
#define	EsOpenCreateNew 64		/* Use this flag with EsOpenCreate, if this flag is specified then trying to create an existing file will fail */
#define	EsOpenSync	128

#define EsIsDir 	0	/* Return values for EsFileAttr */
#define EsIsFile 	1
/** EsMaxPath was chosen from unix MAXPATHLEN.  Override in platform
  * specific j9file implementations if needed.
  */
#define EsMaxPath 	1024
/** @} */

/**
 * @name Shared Semaphore Success flags
 * @anchor PortSharedSemaphoreSuccessFlags
 * Success codes related to shared semaphore  operations.
 * @{
 * @internal J9PORT_INFO_SHSEM* range from at 100 to 109 to avoid overlap 
 */
#define J9PORT_INFO_SHSEM_BASE 100
#define J9PORT_INFO_SHSEM_CREATED (J9PORT_INFO_SHSEM_BASE)
#define J9PORT_INFO_SHSEM_OPENED (J9PORT_INFO_SHSEM_BASE+1)
#define J9PORT_INFO_SHSEM_SEMID_DIFF (J9PORT_INFO_SHSEM_BASE+2)
/** @} */

/**
 * @name Shared Memory Success flags
 * @anchor PortSharedMemorySuccessFlags
 * Success codes related to shared memory semaphore operations.
 * @{
 * @internal J9PORT_INFO_SHMEM* range from at 110 to 119 to avoid overlap
 */
#define J9PORT_INFO_SHMEM_BASE 110
#define J9PORT_INFO_SHMEM_CREATED (J9PORT_INFO_SHMEM_BASE)
#define J9PORT_INFO_SHMEM_OPENED (J9PORT_INFO_SHMEM_BASE+1)
#define J9PORT_INFO_SHMEM_SHMID_DIFF (J9PORT_INFO_SHMEM_BASE+2)
/** @} */

/**
 * @name Shared Memory Eyecatcher
 * @anchor PortSharedMemoryEyecatcher
 * Eyecatcher written to start of a shared classes cache to identify the shared memory segment as such a cache
 * @{
 */
#define J9PORT_SHMEM_EYECATCHER "J9SC"
#define J9PORT_SHMEM_EYECATCHER_LENGTH 4
/** @} */

/**
 * @name Sysinfo get limit success flags
 * @anchor PortSharedMemorySuccessFlags
 * Return codes related to sysinfo get limit operations.
 * @{
 * @internal J9PORT_LIMIT* range from at 120 to 129 to avoid overlap
 */
#define J9PORT_LIMIT_BASE 120
#define J9PORT_LIMIT_UNLIMITED (J9PORT_LIMIT_BASE)
#define J9PORT_LIMIT_UNKNOWN (J9PORT_LIMIT_BASE+1)
#define J9PORT_LIMIT_LIMITED (J9PORT_LIMIT_BASE+2)
/** @} */

/**
 * @name Sysinfo Limits 
 * Flags used to indicate type of operation for j9sysinfo_get_limit
 * @{
 */
#define J9PORT_LIMIT_SOFT ((UDATA) 0x0)
#define J9PORT_LIMIT_HARD ((UDATA) 0x1)
#define J9PORT_RESOURCE_SHARED_MEMORY ((UDATA) 0x2)
/** @} */

/**
 * @name Sysinfo Limits - return values 
 * These values are returned by j9sysinfo_get_limit in the limit parameter for the corresponding return codes.
 * If a value has been determined for a limit, it is the value reurned in the limit parameter.
 * @{
 */
#define J9PORT_LIMIT_UNLIMITED_VALUE (J9CONST64(0xffffffffffffffff))
#define J9PORT_LIMIT_UNKNOWN_VALUE (J9CONST64(0xffffffffffffffff))
/** @} */

/**
 * @name JSIG support (optional)
 * JSIG
 * @{ 
 */
#ifdef J9VM_PORT_JSIG_SUPPORT
#define J9JSIG_SIGNAL(signum, handler)	jsig_primary_signal(signum, handler)
#define J9JSIG_SIGACTION(signum, act, oldact)	jsig_primary_sigaction(signum, act, oldact)
#else
#define J9JSIG_SIGNAL(signum, handler)	signal(signum, handler)
#define J9JSIG_SIGACTION(signum, act, oldact)	sigaction(signum, act, oldact)
#endif
/** @} */

/**
 * @name OS Exception Handling
 * OS Exceptions
 * @{
 */
#define MAX_SIZE_TOTAL_GPINFO 2048
#define J9GP_VALUE_UNDEFINED 0
#define J9GP_VALUE_32 1 
#define J9GP_VALUE_64 2
#define J9GP_VALUE_STRING 3
#define J9GP_VALUE_ADDRESS 4
#define J9GP_VALUE_FLOAT_64 5

#define J9GP_SIGNAL 0 	/* information about the signal */
#define J9GP_GPR 1 /* general purpose registers */
#define J9GP_OTHER 2  /* other information */
#define J9GP_CONTROL 3 	/* control registers */
#define J9GP_FPR 4 		/* floating point registers */
#define J9GP_MODULE 5 	/* module information */	
#define J9GP_NUM_CATEGORIES 6

#define J9GP_CONTROL_PC (-1)
#define J9GP_MODULE_NAME (-1)
/** @} */

/**
 * @name Native Language Support 
 * Native Language Support
 * @{
 * @internal standards require that all VM messages be prefixed with JVM. 
 */
#define J9NLS_COMMON_PREFIX "JVM"
#define J9NLS_ERROR_PREFIX ""
#define J9NLS_WARNING_PREFIX ""
#define J9NLS_INFO_PREFIX ""
#define J9NLS_ERROR_SUFFIX "E"
#define J9NLS_WARNING_SUFFIX "W"
#define J9NLS_INFO_SUFFIX "I"

/** @internal these macros construct in string literals from message ids. */
#define J9NLS_MESSAGE(id, message) ("" J9NLS_COMMON_PREFIX "" id##__PREFIX " " message)
#define J9NLS_ERROR_MESSAGE(id, message) ("" J9NLS_ERROR_PREFIX "" J9NLS_COMMON_PREFIX "" id##__PREFIX "" J9NLS_ERROR_SUFFIX " " message)
#define J9NLS_INFO_MESSAGE(id, message) ("" J9NLS_INFO_PREFIX "" J9NLS_COMMON_PREFIX "" id##__PREFIX "" J9NLS_INFO_SUFFIX " " message)
#define J9NLS_WARNING_MESSAGE(id, message) ("" J9NLS_WARNING_PREFIX "" J9NLS_COMMON_PREFIX "" id##__PREFIX "" J9NLS_WARNING_SUFFIX " " message)
/** @} */

/**
 * @name Virtual Memory Access
 * Flags used to create bitmap indicating memory access
 * @{
 */
#define J9PORT_VMEM_MEMORY_MODE_READ 0x00000001
#define J9PORT_VMEM_MEMORY_MODE_WRITE 0x00000002
#define J9PORT_VMEM_MEMORY_MODE_EXECUTE 0x00000004
#define J9PORT_VMEM_MEMORY_MODE_COMMIT 0x00000008
/** @} */

/**
 * @name Virtual Memory Page Size
 * Shortcut for requesting default page size when large pages are not required
 * @ref j9vmem::j9vmem_supported_page_sizes "j9vmem_supported_page_sizes" 
 * and @ref j9vmem::j9vmem_reserve_memory "j9vmem_reserve_memory"
 * @{
 */
#define J9PORT_VMEM_PAGE_SIZE_DEFAULT 0x00000001
/** @} */

/**
 * @name Timer Resolution
 * @anchor timerResolution
 * Define resolution requested in @ref j9time::j9time_hires_delta
 * @{
 */
#define J9PORT_TIME_DELTA_IN_SECONDS ((UDATA) 1)
#define J9PORT_TIME_DELTA_IN_MILLISECONDS ((UDATA) 1000)
#define J9PORT_TIME_DELTA_IN_MICROSECONDS ((UDATA) 1000000)
#define J9PORT_TIME_DELTA_IN_NANOSECONDS ((UDATA) 1000000000)
/** @} */

/**
 * @name Shared Semaphore
 * Flags used to indicate type of operation for j9shsem_post/j9shsem_wait
 * @{
 */
#define J9PORT_SHSEM_MODE_DEFAULT ((UDATA) 0)
#define J9PORT_SHSEM_MODE_UNDO ((UDATA) 1)
#define J9PORT_SHSEM_MODE_NOWAIT ((UDATA) 2)
/** @} */


/* Constants from J9NLSConstants */
#define J9NLS_BEGIN_MULTI_LINE 0x100
#define J9NLS_DO_NOT_APPEND_NEWLINE 0x10
#define J9NLS_DO_NOT_PRINT_MESSAGE_TAG 0x1
#define J9NLS_END_MULTI_LINE 0x400
#define J9NLS_ERROR 0x2
#define J9NLS_INFO 0x8
#define J9NLS_MULTI_LINE 0x200
#define J9NLS_STDERR 0x40
#define J9NLS_STDOUT 0x20
#define J9NLS_WARNING 0x4

typedef struct J9PortLibraryVersion {
    U_16 majorVersionNumber;
    U_16 minorVersionNumber;
    U_32 padding;
    U_64 capabilities;
} J9PortLibraryVersion;

#define J9SIZEOF_J9PortLibraryVersion 16

typedef struct J9PortVmemIdentifier {
    void* address;
    void* handle;
    UDATA size;
    UDATA pageSize;
    UDATA mode;
} J9PortVmemIdentifier;

#define J9SIZEOF_J9PortVmemIdentifier 20

typedef struct J9PortShmemStatistic {
    UDATA shmid;
    UDATA nattach;
    UDATA key;
    UDATA perm;
    char* file;
    UDATA pad;
    I_64 atime;
    I_64 dtime;
    I_64 chtime;
} J9PortShmemStatistic;

#define J9SIZEOF_J9PortShmemStatistic 48

/** 
 * @struct J9PortLibrary 
 * The port library function table
 */
typedef UDATA (VMCALL *j9sig_protected_fn)(struct J9PortLibrary* portLib, void* handler_arg); /* Forward struct declaration */
typedef UDATA (VMCALL *j9sig_handler_fn)(struct J9PortLibrary* portLib, U_32 gpType, void* gpInfo, void* handler_arg); /* Forward struct declaration */
struct j9shsem_handle; /* Forward struct declaration */
struct j9shmem_handle ; /* Forward struct declaration */
struct J9PortShmemStatistic; /* Forward struct declaration */
struct J9PortLibrary ; /* Forward struct declaration */
struct J9PortLibrary; /* Forward struct declaration */
struct j9shmem_handle; /* Forward struct declaration */
struct j9NetworkInterfaceArray_struct; /* Forward struct declaration */
struct j9NetworkInterfaceArray_struct ; /* Forward struct declaration */
struct j9shsem_handle ; /* Forward struct declaration */
struct J9PortVmemIdentifier ; /* Forward struct declaration */
typedef struct J9PortLibrary {
	/** portVersion*/
    struct J9PortLibraryVersion portVersion;
	/** portGlobals*/
    struct J9PortLibraryGlobalData* portGlobals;
	/** see @ref j9port.c::j9port_shutdown_library "j9port_shutdown_library"*/
    I_32  (PVMCALL port_shutdown_library)(struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9port.c::j9port_isFunctionOverridden "j9port_isFunctionOverridden"*/
    I_32  (PVMCALL port_isFunctionOverridden)(struct J9PortLibrary *portLibrary, UDATA offset) ;
	/** see @ref j9port.c::j9port_tls_free "j9port_tls_free"*/
    void  (PVMCALL port_tls_free)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9error.c::j9error_startup "j9error_startup"*/
    I_32  (PVMCALL error_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9error.c::j9error_shutdown "j9error_shutdown"*/
    void  (PVMCALL error_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9error.c::j9error_last_error_number "j9error_last_error_number"*/
    I_32  (PVMCALL error_last_error_number)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9error.c::j9error_last_error_message "j9error_last_error_message"*/
    const char*  (PVMCALL error_last_error_message)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9error.c::j9error_set_last_error "j9error_set_last_error"*/
    I_32  (PVMCALL error_set_last_error)(struct J9PortLibrary *portLibrary,  I_32 platformCode, I_32 portableCode) ;
	/** see @ref j9error.c::j9error_set_last_error_with_message "j9error_set_last_error_with_message"*/
    I_32  (PVMCALL error_set_last_error_with_message)(struct J9PortLibrary *portLibrary, I_32 portableCode, const char *errorMessage) ;
	/** see @ref j9time.c::j9time_startup "j9time_startup"*/
    I_32  (PVMCALL time_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_shutdown "j9time_shutdown"*/
    void  (PVMCALL time_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_msec_clock "j9time_msec_clock"*/
    UDATA  (PVMCALL time_msec_clock)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_usec_clock "j9time_usec_clock"*/
    UDATA  (PVMCALL time_usec_clock)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_current_time_millis "j9time_current_time_millis"*/
    I_64  (PVMCALL time_current_time_millis)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_hires_clock "j9time_hires_clock"*/
    U_64  (PVMCALL time_hires_clock)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_hires_frequency "j9time_hires_frequency"*/
    U_64  (PVMCALL time_hires_frequency)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9time.c::j9time_hires_delta "j9time_hires_delta"*/
    U_64  (PVMCALL time_hires_delta)(struct J9PortLibrary *portLibrary, U_64 startTime, U_64 endTime, UDATA requiredResolution) ;
	/** see @ref j9sysinfo.c::j9sysinfo_startup "j9sysinfo_startup"*/
    I_32  (PVMCALL sysinfo_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_shutdown "j9sysinfo_shutdown"*/
    void  (PVMCALL sysinfo_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_pid "j9sysinfo_get_pid"*/
    UDATA  (PVMCALL sysinfo_get_pid)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_physical_memory "j9sysinfo_get_physical_memory"*/
    U_64  (PVMCALL sysinfo_get_physical_memory)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_OS_version "j9sysinfo_get_OS_version"*/
    const char*  (PVMCALL sysinfo_get_OS_version)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_env "j9sysinfo_get_env"*/
    IDATA  (PVMCALL sysinfo_get_env)(struct J9PortLibrary *portLibrary, char *envVar, char *infoString, UDATA bufSize) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_CPU_architecture "j9sysinfo_get_CPU_architecture"*/
    const char*  (PVMCALL sysinfo_get_CPU_architecture)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_OS_type "j9sysinfo_get_OS_type"*/
    const char*  (PVMCALL sysinfo_get_OS_type)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_classpathSeparator "j9sysinfo_get_classpathSeparator"*/
    U_16  (PVMCALL sysinfo_get_classpathSeparator)(struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_executable_name "j9sysinfo_get_executable_name"*/
    IDATA  (PVMCALL sysinfo_get_executable_name)(struct J9PortLibrary *portLibrary, char *argv0, char **result) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_number_CPUs "j9sysinfo_get_number_CPUs"*/
    UDATA  (PVMCALL sysinfo_get_number_CPUs)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_username "j9sysinfo_get_username"*/
    IDATA  (PVMCALL sysinfo_get_username)(struct J9PortLibrary* portLibrary, char* buffer, UDATA length) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_groupname "j9sysinfo_get_groupname"*/
    IDATA  (PVMCALL sysinfo_get_groupname)(struct J9PortLibrary* portLibrary, char* buffer, UDATA length) ;
	/** see @ref j9file.c::j9file_startup "j9file_startup"*/
    I_32  (PVMCALL file_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9file.c::j9file_shutdown "j9file_shutdown"*/
    void  (PVMCALL file_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9file.c::j9file_write "j9file_write"*/
    IDATA  (PVMCALL file_write)(struct J9PortLibrary *portLibrary, IDATA fd, const void *buf, IDATA nbytes) ;
	/** see @ref j9file.c::j9file_write_text "j9file_write_text"*/
    IDATA  (PVMCALL file_write_text)(struct J9PortLibrary *portLibrary, IDATA fd, const char *buf, IDATA nbytes) ;
	/** see @ref j9file.c::j9file_vprintf "j9file_vprintf"*/
    void  (PVMCALL file_vprintf)(struct J9PortLibrary *portLibrary, IDATA fd, const char *format, va_list args) ;
	/** see @ref j9file.c::j9file_printf "j9file_printf"*/
    void  (PVMCALL file_printf)(struct J9PortLibrary *portLibrary, IDATA fd, const char *format, ...) ;
	/** see @ref j9file.c::j9file_open "j9file_open"*/
    IDATA  (PVMCALL file_open)(struct J9PortLibrary *portLibrary, const char *path, I_32 flags, I_32 mode) ;
	/** see @ref j9file.c::j9file_close "j9file_close"*/
    I_32  (PVMCALL file_close)(struct J9PortLibrary *portLibrary, IDATA fd) ;
	/** see @ref j9file.c::j9file_seek "j9file_seek"*/
    I_64  (PVMCALL file_seek)(struct J9PortLibrary *portLibrary, IDATA fd, I_64 offset, I_32 whence) ;
	/** see @ref j9file.c::j9file_read "j9file_read"*/
    IDATA  (PVMCALL file_read)(struct J9PortLibrary *portLibrary, IDATA fd, void *buf, IDATA nbytes) ;
	/** see @ref j9file.c::j9file_unlink "j9file_unlink"*/
    I_32  (PVMCALL file_unlink)(struct J9PortLibrary *portLibrary, const char *path) ;
	/** see @ref j9file.c::j9file_attr "j9file_attr"*/
    I_32  (PVMCALL file_attr)(struct J9PortLibrary *portLibrary, const char *path) ;
	/** see @ref j9file.c::j9file_lastmod "j9file_lastmod"*/
    I_64  (PVMCALL file_lastmod)(struct J9PortLibrary *portLibrary, const char *path) ;
	/** see @ref j9file.c::j9file_length "j9file_length"*/
    I_64  (PVMCALL file_length)(struct J9PortLibrary *portLibrary, const char *path) ;
	/** see @ref j9file.c::j9file_set_length "j9file_set_length"*/
    I_32  (PVMCALL file_set_length)(struct J9PortLibrary *portLibrary, IDATA fd, I_64 newLength) ;
	/** see @ref j9file.c::j9file_sync "j9file_sync"*/
    I_32  (PVMCALL file_sync)(struct J9PortLibrary *portLibrary, IDATA fd) ;
	/** see @ref j9sl.c::j9sl_startup "j9sl_startup"*/
    I_32  (PVMCALL sl_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sl.c::j9sl_shutdown "j9sl_shutdown"*/
    void  (PVMCALL sl_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sl.c::j9sl_close_shared_library "j9sl_close_shared_library"*/
    UDATA  (PVMCALL sl_close_shared_library)(struct J9PortLibrary *portLibrary, UDATA descriptor) ;
	/** see @ref j9sl.c::j9sl_open_shared_library "j9sl_open_shared_library"*/
    UDATA  (PVMCALL sl_open_shared_library)(struct J9PortLibrary *portLibrary, char *name, UDATA *descriptor, BOOLEAN decorate) ;
	/** see @ref j9sl.c::j9sl_lookup_name "j9sl_lookup_name"*/
    UDATA  (PVMCALL sl_lookup_name)(struct J9PortLibrary *portLibrary, UDATA descriptor, char *name, UDATA *func, const char *argSignature) ;
	/** see @ref j9tty.c::j9tty_startup "j9tty_startup"*/
    I_32  (PVMCALL tty_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9tty.c::j9tty_shutdown "j9tty_shutdown"*/
    void  (PVMCALL tty_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9tty.c::j9tty_printf "j9tty_printf"*/
    void  (PVMCALL tty_printf)(struct J9PortLibrary *portLibrary, const char *format, ...) ;
	/** see @ref j9tty.c::j9tty_vprintf "j9tty_vprintf"*/
    void  (PVMCALL tty_vprintf)(struct J9PortLibrary *portLibrary, const char *format, va_list args) ;
	/** see @ref j9tty.c::j9tty_get_chars "j9tty_get_chars"*/
    IDATA  (PVMCALL tty_get_chars)(struct J9PortLibrary *portLibrary, char *s, UDATA length) ;
	/** see @ref j9tty.c::j9tty_err_printf "j9tty_err_printf"*/
    void  (PVMCALL tty_err_printf)(struct J9PortLibrary *portLibrary, const char *format, ...) ;
	/** see @ref j9tty.c::j9tty_err_vprintf "j9tty_err_vprintf"*/
    void  (PVMCALL tty_err_vprintf)(struct J9PortLibrary *portLibrary, const char *format, va_list args) ;
	/** see @ref j9tty.c::j9tty_available "j9tty_available"*/
    IDATA  (PVMCALL tty_available)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9mem.c::j9mem_startup "j9mem_startup"*/
    I_32  (PVMCALL mem_startup)(struct J9PortLibrary *portLibrary, UDATA portGlobalSize) ;
	/** see @ref j9mem.c::j9mem_shutdown "j9mem_shutdown"*/
    void  (PVMCALL mem_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9mem.c::j9mem_allocate_memory "j9mem_allocate_memory"*/
    void*  (PVMCALL mem_allocate_memory)(struct J9PortLibrary *portLibrary, UDATA byteAmount) ;
	/** see @ref j9mem.c::j9mem_allocate_memory_callSite "j9mem_allocate_memory_callSite"*/
    void*  (PVMCALL mem_allocate_memory_callSite)(struct J9PortLibrary *portLibrary, UDATA byteAmount, char *callSite) ;
	/** see @ref j9mem.c::j9mem_free_memory "j9mem_free_memory"*/
    void  (PVMCALL mem_free_memory)(struct J9PortLibrary *portLibrary, void *memoryPointer) ;
	/** see @ref j9mem.c::j9mem_reallocate_memory "j9mem_reallocate_memory"*/
    void*  (PVMCALL mem_reallocate_memory)(struct J9PortLibrary *portLibrary, void *memoryPointer, UDATA byteAmount) ;
	/** see @ref j9cpu.c::j9cpu_startup "j9cpu_startup"*/
    I_32  (PVMCALL cpu_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9cpu.c::j9cpu_shutdown "j9cpu_shutdown"*/
    void  (PVMCALL cpu_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9cpu.c::j9cpu_flush_icache "j9cpu_flush_icache"*/
    void  (PVMCALL cpu_flush_icache)(struct J9PortLibrary *portLibrary, void *memoryPointer, UDATA byteAmount) ;
	/** see @ref j9vmem.c::j9vmem_startup "j9vmem_startup"*/
    I_32  (PVMCALL vmem_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9vmem.c::j9vmem_shutdown "j9vmem_shutdown"*/
    void  (PVMCALL vmem_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9vmem.c::j9vmem_commit_memory "j9vmem_commit_memory"*/
    void*  (PVMCALL vmem_commit_memory)(struct J9PortLibrary *portLibrary, void *address, UDATA byteAmount, struct J9PortVmemIdentifier *identifier) ;
	/** see @ref j9vmem.c::j9vmem_decommit_memory "j9vmem_decommit_memory"*/
    IDATA  (PVMCALL vmem_decommit_memory)(struct J9PortLibrary *portLibrary, void *address, UDATA byteAmount, struct J9PortVmemIdentifier *identifier) ;
	/** see @ref j9vmem.c::j9vmem_free_memory "j9vmem_free_memory"*/
    I_32  (PVMCALL vmem_free_memory)(struct J9PortLibrary *portLibrary, void *userAddress, UDATA byteAmount, struct J9PortVmemIdentifier *identifier) ;
	/** see @ref j9vmem.c::j9vmem_reserve_memory "j9vmem_reserve_memory"*/
    void*  (PVMCALL vmem_reserve_memory)(struct J9PortLibrary *portLibrary, void *address, UDATA byteAmount, struct J9PortVmemIdentifier *identifier, UDATA mode, UDATA pageSize) ;
	/** see @ref j9vmem.c::j9vmem_supported_page_sizes "j9vmem_supported_page_sizes"*/
    UDATA*  (PVMCALL vmem_supported_page_sizes)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9vmem.c::j9vmem_default_large_page_size "j9vmem_default_large_page_size"*/
    UDATA  (PVMCALL vmem_default_large_page_size)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sock.c::j9sock_startup "j9sock_startup"*/
    I_32  (PVMCALL sock_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sock.c::j9sock_shutdown "j9sock_shutdown"*/
    I_32  (PVMCALL sock_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sock.c::j9sock_htons "j9sock_htons"*/
    U_16  (PVMCALL sock_htons)(struct J9PortLibrary *portLibrary, U_16 val) ;
	/** see @ref j9sock.c::j9sock_write "j9sock_write"*/
    I_32  (PVMCALL sock_write)(struct J9PortLibrary *portLibrary, j9socket_t sock, U_8 *buf, I_32 nbyte, I_32 flags) ;
	/** see @ref j9sock.c::j9sock_sockaddr "j9sock_sockaddr"*/
    I_32  (PVMCALL sock_sockaddr)(struct J9PortLibrary *portLibrary, j9sockaddr_t handle, char *addrStr, U_16 port) ;
	/** see @ref j9sock.c::j9sock_read "j9sock_read"*/
    I_32  (PVMCALL sock_read)(struct J9PortLibrary *portLibrary, j9socket_t sock, U_8 *buf, I_32 nbyte, I_32 flags) ;
	/** see @ref j9sock.c::j9sock_socket "j9sock_socket"*/
    I_32  (PVMCALL sock_socket)(struct J9PortLibrary *portLibrary, j9socket_t *handle, I_32 family, I_32 socktype,  I_32 protocol) ;
	/** see @ref j9sock.c::j9sock_close "j9sock_close"*/
    I_32  (PVMCALL sock_close)(struct J9PortLibrary *portLibrary, j9socket_t *sock) ;
	/** see @ref j9sock.c::j9sock_connect "j9sock_connect"*/
    I_32  (PVMCALL sock_connect)(struct J9PortLibrary *portLibrary, j9socket_t sock, j9sockaddr_t addr) ;
	/** see @ref j9sock.c::j9sock_inetaddr "j9sock_inetaddr"*/
    I_32  (PVMCALL sock_inetaddr)(struct J9PortLibrary *portLibrary, char *addrStr, U_32 *addr) ;
	/** see @ref j9sock.c::j9sock_gethostbyname "j9sock_gethostbyname"*/
    I_32  (PVMCALL sock_gethostbyname)(struct J9PortLibrary *portLibrary, char *name, j9hostent_t handle) ;
	/** see @ref j9sock.c::j9sock_hostent_addrlist "j9sock_hostent_addrlist"*/
    I_32  (PVMCALL sock_hostent_addrlist)(struct J9PortLibrary *portLibrary, j9hostent_t handle, U_32 index) ;
	/** see @ref j9sock.c::j9sock_sockaddr_init "j9sock_sockaddr_init"*/
    I_32  (PVMCALL sock_sockaddr_init)(struct J9PortLibrary *portLibrary, j9sockaddr_t handle, I_16 family, U_32 nipAddr, U_16 nPort) ;
	/** see @ref j9sock.c::j9sock_linger_init "j9sock_linger_init"*/
    I_32  (PVMCALL sock_linger_init)(struct J9PortLibrary *portLibrary, j9linger_t handle, I_32 enabled, U_16 timeout) ;
	/** see @ref j9sock.c::j9sock_setopt_linger "j9sock_setopt_linger"*/
    I_32  (PVMCALL sock_setopt_linger)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  j9linger_t optval) ;
	/** see @ref j9gp.c::j9gp_startup "j9gp_startup"*/
    I_32  (PVMCALL gp_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9gp.c::j9gp_shutdown "j9gp_shutdown"*/
    void  (PVMCALL gp_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9gp.c::j9gp_protect "j9gp_protect"*/
    UDATA  (PVMCALL gp_protect)(struct J9PortLibrary *portLibrary,  protected_fn fn, void* arg ) ;
	/** see @ref j9gp.c::j9gp_register_handler "j9gp_register_handler"*/
    void  (PVMCALL gp_register_handler)(struct J9PortLibrary *portLibrary, handler_fn fn, void *aUserData ) ;
	/** see @ref j9gp.c::j9gp_info "j9gp_info"*/
    U_32  (PVMCALL gp_info)(struct J9PortLibrary *portLibrary, void *info, U_32 category, I_32 index, const char **name, void **value) ;
	/** see @ref j9gp.c::j9gp_info_count "j9gp_info_count"*/
    U_32  (PVMCALL gp_info_count)(struct J9PortLibrary *portLibrary, void *info, U_32 category) ;
	/** see @ref j9gp.c::j9gp_handler_function "j9gp_handler_function"*/
    void  (PVMCALL gp_handler_function)(void *unknown) ;
	/** see @ref j9str.c::j9str_startup "j9str_startup"*/
    I_32  (PVMCALL str_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9str.c::j9str_shutdown "j9str_shutdown"*/
    void  (PVMCALL str_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9str.c::j9str_printf "j9str_printf"*/
    U_32  (PVMCALL str_printf)(struct J9PortLibrary *portLibrary, char *buf, U_32 bufLen, const char* format, ...) ;
	/** see @ref j9str.c::j9str_vprintf "j9str_vprintf"*/
    U_32  (PVMCALL str_vprintf)(struct J9PortLibrary *portLibrary, char *buf, U_32 bufLen, const char *format, va_list args) ;
	/** see @ref j9exit.c::j9exit_startup "j9exit_startup"*/
    I_32  (PVMCALL exit_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9exit.c::j9exit_shutdown "j9exit_shutdown"*/
    void  (PVMCALL exit_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9exit.c::j9exit_get_exit_code "j9exit_get_exit_code"*/
    I_32  (PVMCALL exit_get_exit_code)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9exit.c::j9exit_shutdown_and_exit "j9exit_shutdown_and_exit"*/
    void  (PVMCALL exit_shutdown_and_exit)(struct J9PortLibrary *portLibrary, I_32 exitCode) ;
	/** self_handle*/
    void* self_handle;
	/** see @ref j9dump.c::j9dump_create "j9dump_create"*/
    UDATA  (PVMCALL dump_create)(struct J9PortLibrary *portLibrary, char *filename, char *dumpType, void *userData) ;
	/** see @ref j9nls.c::j9nls_startup "j9nls_startup"*/
    I_32  (PVMCALL nls_startup)(struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9nls.c::j9nls_shutdown "j9nls_shutdown"*/
    void  (PVMCALL nls_shutdown)( struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9nls.c::j9nls_set_catalog "j9nls_set_catalog"*/
    void  (PVMCALL nls_set_catalog)( struct J9PortLibrary *portLibrary, const char **paths, const int nPaths, const char* baseName, const char* extension ) ;
	/** see @ref j9nls.c::j9nls_set_locale "j9nls_set_locale"*/
    void  (PVMCALL nls_set_locale)( struct J9PortLibrary *portLibrary, const char* lang, const char* region, const char* variant ) ;
	/** see @ref j9nls.c::j9nls_get_language "j9nls_get_language"*/
    const char*  (PVMCALL nls_get_language)( struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9nls.c::j9nls_get_region "j9nls_get_region"*/
    const char*  (PVMCALL nls_get_region)( struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9nls.c::j9nls_get_variant "j9nls_get_variant"*/
    const char*  (PVMCALL nls_get_variant)( struct J9PortLibrary *portLibrary ) ;
	/** see @ref j9nls.c::j9nls_printf "j9nls_printf"*/
    void  (PVMCALL nls_printf)( struct J9PortLibrary *portLibrary, UDATA flags, U_32 module_name, U_32 message_num, ... ) ;
	/** see @ref j9nls.c::j9nls_vprintf "j9nls_vprintf"*/
    void  (PVMCALL nls_vprintf)( struct J9PortLibrary *portLibrary, UDATA flags, U_32 module_name, U_32 message_num, va_list args ) ;
	/** see @ref j9nls.c::j9nls_lookup_message "j9nls_lookup_message"*/
    const char*  (PVMCALL nls_lookup_message)( struct J9PortLibrary *portLibrary, UDATA flags, U_32 module_name, U_32 message_num, const char *default_string ) ;
	/** see @ref j9ipcmutex.c::j9ipcmutex_startup "j9ipcmutex_startup"*/
    I_32  (PVMCALL ipcmutex_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9ipcmutex.c::j9ipcmutex_shutdown "j9ipcmutex_shutdown"*/
    void  (PVMCALL ipcmutex_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9ipcmutex.c::j9ipcmutex_acquire "j9ipcmutex_acquire"*/
    I_32  (PVMCALL ipcmutex_acquire)(struct J9PortLibrary *portLibrary, const char *name) ;
	/** see @ref j9ipcmutex.c::j9ipcmutex_release "j9ipcmutex_release"*/
    I_32  (PVMCALL ipcmutex_release)(struct J9PortLibrary *portLibrary, const char *name) ;
	/** see @ref j9j9portcontrol.c::j9port_control "j9port_control"*/
    I_32  (PVMCALL port_control)( struct J9PortLibrary *portLibrary, char *key, UDATA value) ;
	/** see @ref j9sig.c::j9sig_startup "j9sig_startup"*/
    I_32  (PVMCALL sig_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sig.c::j9sig_shutdown "j9sig_shutdown"*/
    void  (PVMCALL sig_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sig.c::j9sig_protect "j9sig_protect"*/
    I_32  (PVMCALL sig_protect)(struct J9PortLibrary *portLibrary,  j9sig_protected_fn fn, void* fn_arg, j9sig_handler_fn handler, void* handler_arg, U_32 flags, UDATA *result ) ;
	/** see @ref j9sig.c::j9sig_can_protect "j9sig_can_protect"*/
    I_32  (PVMCALL sig_can_protect)(struct J9PortLibrary *portLibrary,  U_32 flags) ;
	/** see @ref j9sig.c::j9sig_set_async_signal_handler "j9sig_set_async_signal_handler"*/
    U_32  (PVMCALL sig_set_async_signal_handler)(struct J9PortLibrary* portLibrary,  j9sig_handler_fn handler, void* handler_arg, U_32 flags) ;
	/** see @ref j9sig.c::j9sig_info "j9sig_info"*/
    U_32  (PVMCALL sig_info)(struct J9PortLibrary *portLibrary, void *info, U_32 category, I_32 index, const char **name, void **value) ;
	/** see @ref j9sig.c::j9sig_info_count "j9sig_info_count"*/
    U_32  (PVMCALL sig_info_count)(struct J9PortLibrary *portLibrary, void *info, U_32 category) ;
	/** see @ref j9sig.c::j9sig_set_options "j9sig_set_options"*/
    I_32  (PVMCALL sig_set_options)(struct J9PortLibrary *portLibrary, U_32 options) ;
	/** see @ref j9sig.c::j9sig_get_options "j9sig_get_options"*/
    U_32  (PVMCALL sig_get_options)(struct J9PortLibrary *portLibrary) ;
	/** attached_thread*/
    j9thread_t attached_thread;
	/** see @ref j9sysinfo.c::j9sysinfo_DLPAR_enabled "j9sysinfo_DLPAR_enabled"*/
    UDATA  (PVMCALL sysinfo_DLPAR_enabled)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_DLPAR_max_CPUs "j9sysinfo_DLPAR_max_CPUs"*/
    UDATA  (PVMCALL sysinfo_DLPAR_max_CPUs)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sysinfo.c::j9sysinfo_weak_memory_consistency "j9sysinfo_weak_memory_consistency"*/
    UDATA  (PVMCALL sysinfo_weak_memory_consistency)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9file.c::j9file_read_text "j9file_read_text"*/
    char*  (PVMCALL file_read_text)(struct J9PortLibrary *portLibrary, IDATA fd, char *buf, IDATA nbytes) ;
	/** see @ref j9file.c::j9file_mkdir "j9file_mkdir"*/
    I_32  (PVMCALL file_mkdir)(struct J9PortLibrary *portLibrary, const char *path) ;
	/** see @ref j9file.c::j9file_move "j9file_move"*/
    I_32  (PVMCALL file_move)(struct J9PortLibrary *portLibrary, const char *pathExist, const char *pathNew) ;
	/** see @ref j9file.c::j9file_unlinkdir "j9file_unlinkdir"*/
    I_32  (PVMCALL file_unlinkdir)(struct J9PortLibrary *portLibrary, const char *path) ;
	/** see @ref j9file.c::j9file_findfirst "j9file_findfirst"*/
    UDATA  (PVMCALL file_findfirst)(struct J9PortLibrary *portLibrary, const char *path, char *resultbuf) ;
	/** see @ref j9file.c::j9file_findnext "j9file_findnext"*/
    I_32  (PVMCALL file_findnext)(struct J9PortLibrary *portLibrary, UDATA findhandle, char *resultbuf) ;
	/** see @ref j9file.c::j9file_findclose "j9file_findclose"*/
    void  (PVMCALL file_findclose)(struct J9PortLibrary *portLibrary, UDATA findhandle) ;
	/** see @ref j9file.c::j9file_error_message "j9file_error_message"*/
    const char*  (PVMCALL file_error_message)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sock.c::j9sock_htonl "j9sock_htonl"*/
    I_32  (PVMCALL sock_htonl)(struct J9PortLibrary *portLibrary, I_32 val) ;
	/** see @ref j9sock.c::j9sock_bind "j9sock_bind"*/
    I_32  (PVMCALL sock_bind)(struct J9PortLibrary *portLibrary, j9socket_t sock, j9sockaddr_t addr) ;
	/** see @ref j9sock.c::j9sock_accept "j9sock_accept"*/
    I_32  (PVMCALL sock_accept)(struct J9PortLibrary *portLibrary, j9socket_t serverSock, j9sockaddr_t addrHandle, j9socket_t *sockHandle) ;
	/** see @ref j9sock.c::j9sock_shutdown_input "j9sock_shutdown_input"*/
    I_32  (PVMCALL sock_shutdown_input)(struct J9PortLibrary *portLibrary, j9socket_t sock) ;
	/** see @ref j9sock.c::j9sock_shutdown_output "j9sock_shutdown_output"*/
    I_32  (PVMCALL sock_shutdown_output)(struct J9PortLibrary *portLibrary, j9socket_t sock) ;
	/** see @ref j9sock.c::j9sock_listen "j9sock_listen"*/
    I_32  (PVMCALL sock_listen)(struct J9PortLibrary *portLibrary, j9socket_t sock, I_32 backlog ) ;
	/** see @ref j9sock.c::j9sock_ntohl "j9sock_ntohl"*/
    I_32  (PVMCALL sock_ntohl)(struct J9PortLibrary *portLibrary, I_32 val) ;
	/** see @ref j9sock.c::j9sock_ntohs "j9sock_ntohs"*/
    U_16  (PVMCALL sock_ntohs)(struct J9PortLibrary *portLibrary, U_16 val) ;
	/** see @ref j9sock.c::j9sock_getpeername "j9sock_getpeername"*/
    I_32  (PVMCALL sock_getpeername)(struct J9PortLibrary *portLibrary, j9socket_t handle, j9sockaddr_t addrHandle) ;
	/** see @ref j9sock.c::j9sock_getsockname "j9sock_getsockname"*/
    I_32  (PVMCALL sock_getsockname)(struct J9PortLibrary *portLibrary, j9socket_t handle, j9sockaddr_t addrHandle) ;
	/** see @ref j9sock.c::j9sock_readfrom "j9sock_readfrom"*/
    I_32  (PVMCALL sock_readfrom)(struct J9PortLibrary *portLibrary, j9socket_t sock, U_8 *buf, I_32 nbyte, I_32 flags, j9sockaddr_t addrHandle) ;
	/** see @ref j9sock.c::j9sock_select "j9sock_select"*/
    I_32  (PVMCALL sock_select)(struct J9PortLibrary *portLibrary, I_32 nfds, j9fdset_t readfds, j9fdset_t writefds, j9fdset_t exceptfds, j9timeval_t timeout) ;
	/** see @ref j9sock.c::j9sock_writeto "j9sock_writeto"*/
    I_32  (PVMCALL sock_writeto)(struct J9PortLibrary *portLibrary, j9socket_t sock, U_8 *buf, I_32 nbyte, I_32 flags, j9sockaddr_t addrHandle) ;
	/** see @ref j9sock.c::j9sock_inetntoa "j9sock_inetntoa"*/
    I_32  (PVMCALL sock_inetntoa)(struct J9PortLibrary *portLibrary, char **addrStr, U_32 nipAddr) ;
	/** see @ref j9sock.c::j9sock_gethostbyaddr "j9sock_gethostbyaddr"*/
    I_32  (PVMCALL sock_gethostbyaddr)(struct J9PortLibrary *portLibrary, char *addr, I_32 length, I_32 type, j9hostent_t handle) ;
	/** see @ref j9sock.c::j9sock_gethostname "j9sock_gethostname"*/
    I_32  (PVMCALL sock_gethostname)(struct J9PortLibrary *portLibrary, char *buffer, I_32 length) ;
	/** see @ref j9sock.c::j9sock_hostent_aliaslist "j9sock_hostent_aliaslist"*/
    I_32  (PVMCALL sock_hostent_aliaslist)(struct J9PortLibrary *portLibrary, j9hostent_t handle, char ***aliasList) ;
	/** see @ref j9sock.c::j9sock_hostent_hostname "j9sock_hostent_hostname"*/
    I_32  (PVMCALL sock_hostent_hostname)(struct J9PortLibrary *portLibrary, j9hostent_t handle, char** hostName) ;
	/** see @ref j9sock.c::j9sock_sockaddr_port "j9sock_sockaddr_port"*/
    U_16  (PVMCALL sock_sockaddr_port)(struct J9PortLibrary *portLibrary, j9sockaddr_t handle) ;
	/** see @ref j9sock.c::j9sock_sockaddr_address "j9sock_sockaddr_address"*/
    I_32  (PVMCALL sock_sockaddr_address)(struct J9PortLibrary *portLibrary, j9sockaddr_t handle) ;
	/** see @ref j9sock.c::j9sock_fdset_init "j9sock_fdset_init"*/
    I_32  (PVMCALL sock_fdset_init)(struct J9PortLibrary *portLibrary, j9socket_t socketP) ;
	/** see @ref j9sock.c::j9sock_fdset_size "j9sock_fdset_size"*/
    I_32  (PVMCALL sock_fdset_size)(struct J9PortLibrary *portLibrary, j9socket_t handle) ;
	/** see @ref j9sock.c::j9sock_timeval_init "j9sock_timeval_init"*/
    I_32  (PVMCALL sock_timeval_init)(struct J9PortLibrary *portLibrary, U_32 secTime, U_32 uSecTime, j9timeval_t timeP) ;
	/** see @ref j9sock.c::j9sock_getopt_int "j9sock_getopt_int"*/
    I_32  (PVMCALL sock_getopt_int)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  I_32 *optval) ;
	/** see @ref j9sock.c::j9sock_setopt_int "j9sock_setopt_int"*/
    I_32  (PVMCALL sock_setopt_int)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  I_32 *optval) ;
	/** see @ref j9sock.c::j9sock_getopt_bool "j9sock_getopt_bool"*/
    I_32  (PVMCALL sock_getopt_bool)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  BOOLEAN *optval) ;
	/** see @ref j9sock.c::j9sock_setopt_bool "j9sock_setopt_bool"*/
    I_32  (PVMCALL sock_setopt_bool)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  BOOLEAN *optval) ;
	/** see @ref j9sock.c::j9sock_getopt_byte "j9sock_getopt_byte"*/
    I_32  (PVMCALL sock_getopt_byte)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  U_8 *optval) ;
	/** see @ref j9sock.c::j9sock_setopt_byte "j9sock_setopt_byte"*/
    I_32  (PVMCALL sock_setopt_byte)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  U_8 *optval) ;
	/** see @ref j9sock.c::j9sock_getopt_linger "j9sock_getopt_linger"*/
    I_32  (PVMCALL sock_getopt_linger)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  j9linger_t optval) ;
	/** see @ref j9sock.c::j9sock_getopt_sockaddr "j9sock_getopt_sockaddr"*/
    I_32  (PVMCALL sock_getopt_sockaddr)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname, j9sockaddr_t optval) ;
	/** see @ref j9sock.c::j9sock_setopt_sockaddr "j9sock_setopt_sockaddr"*/
    I_32  (PVMCALL sock_setopt_sockaddr)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  j9sockaddr_t optval) ;
	/** see @ref j9sock.c::j9sock_setopt_ipmreq "j9sock_setopt_ipmreq"*/
    I_32  (PVMCALL sock_setopt_ipmreq)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  j9ipmreq_t optval) ;
	/** see @ref j9sock.c::j9sock_linger_enabled "j9sock_linger_enabled"*/
    I_32  (PVMCALL sock_linger_enabled)(struct J9PortLibrary *portLibrary, j9linger_t handle, BOOLEAN *enabled) ;
	/** see @ref j9sock.c::j9sock_linger_linger "j9sock_linger_linger"*/
    I_32  (PVMCALL sock_linger_linger)(struct J9PortLibrary *portLibrary, j9linger_t handle, U_16 *linger) ;
	/** see @ref j9sock.c::j9sock_ipmreq_init "j9sock_ipmreq_init"*/
    I_32  (PVMCALL sock_ipmreq_init)(struct J9PortLibrary *portLibrary, j9ipmreq_t handle, U_32 nipmcast, U_32 nipinterface) ;
	/** see @ref j9sock.c::j9sock_setflag "j9sock_setflag"*/
    I_32  (PVMCALL sock_setflag)(struct J9PortLibrary *portLibrary, I_32 flag, I_32 *arg) ;
	/** see @ref j9sock.c::j9sock_freeaddrinfo "j9sock_freeaddrinfo"*/
    I_32  (PVMCALL sock_freeaddrinfo)(struct J9PortLibrary *portLibrary, j9addrinfo_t handle) ;
	/** see @ref j9sock.c::j9sock_getaddrinfo "j9sock_getaddrinfo"*/
    I_32  (PVMCALL sock_getaddrinfo)(struct J9PortLibrary *portLibrary, char *name, j9addrinfo_t hints, j9addrinfo_t result) ;
	/** see @ref j9sock.c::j9sock_getaddrinfo_address "j9sock_getaddrinfo_address"*/
    I_32  (PVMCALL sock_getaddrinfo_address)(struct J9PortLibrary *portLibrary, j9addrinfo_t handle, U_8 *address, int index, U_32* scope_id) ;
	/** see @ref j9sock.c::j9sock_getaddrinfo_create_hints "j9sock_getaddrinfo_create_hints"*/
    I_32  (PVMCALL sock_getaddrinfo_create_hints)(struct J9PortLibrary *portLibrary, j9addrinfo_t *result, I_16 family, I_32 socktype, I_32 protocol, I_32 flags) ;
	/** see @ref j9sock.c::j9sock_getaddrinfo_family "j9sock_getaddrinfo_family"*/
    I_32  (PVMCALL sock_getaddrinfo_family)(struct J9PortLibrary *portLibrary, j9addrinfo_t handle, I_32 *family, int index) ;
	/** see @ref j9sock.c::j9sock_getaddrinfo_length "j9sock_getaddrinfo_length"*/
    I_32  (PVMCALL sock_getaddrinfo_length)(struct J9PortLibrary *portLibrary, j9addrinfo_t handle, I_32 *length) ;
	/** see @ref j9sock.c::j9sock_getaddrinfo_name "j9sock_getaddrinfo_name"*/
    I_32  (PVMCALL sock_getaddrinfo_name)(struct J9PortLibrary *portLibrary, j9addrinfo_t handle, char *name, int index) ;
	/** see @ref j9sock.c::j9sock_getnameinfo "j9sock_getnameinfo"*/
    I_32  (PVMCALL sock_getnameinfo)(struct J9PortLibrary *portLibrary, j9sockaddr_t in_addr, I_32 sockaddr_size, char *name, I_32 name_length, int flags) ;
	/** see @ref j9sock.c::j9sock_ipv6_mreq_init "j9sock_ipv6_mreq_init"*/
    I_32  (PVMCALL sock_ipv6_mreq_init)(struct J9PortLibrary *portLibrary, j9ipv6_mreq_t handle, U_8 *ipmcast_addr, U_32 ipv6mr_interface) ;
	/** see @ref j9sock.c::j9sock_setopt_ipv6_mreq "j9sock_setopt_ipv6_mreq"*/
    I_32  (PVMCALL sock_setopt_ipv6_mreq)(struct J9PortLibrary *portLibrary, j9socket_t socketP, I_32 optlevel, I_32 optname,  j9ipv6_mreq_t optval) ;
	/** see @ref j9sock.c::j9sock_sockaddr_address6 "j9sock_sockaddr_address6"*/
    I_32  (PVMCALL sock_sockaddr_address6)(struct J9PortLibrary *portLibrary, j9sockaddr_t handle, U_8 *address, U_32 *length, U_32* scope_id) ;
	/** see @ref j9sock.c::j9sock_sockaddr_family "j9sock_sockaddr_family"*/
    I_32  (PVMCALL sock_sockaddr_family)(struct J9PortLibrary *portLibrary, I_16 *family, j9sockaddr_t handle) ;
	/** see @ref j9sock.c::j9sock_sockaddr_init6 "j9sock_sockaddr_init6"*/
    I_32  (PVMCALL sock_sockaddr_init6)(struct J9PortLibrary *portLibrary, j9sockaddr_t handle, U_8 *addr, I_32 addrlength, I_16 family, U_16 nPort,U_32 flowinfo, U_32 scope_id, j9socket_t sock) ;
	/** see @ref j9sock.c::j9sock_socketIsValid "j9sock_socketIsValid"*/
    I_32  (PVMCALL sock_socketIsValid)(struct J9PortLibrary *portLibrary, j9socket_t handle) ;
	/** see @ref j9sock.c::j9sock_select_read "j9sock_select_read"*/
    I_32  (PVMCALL sock_select_read)(struct J9PortLibrary *portLibrary, j9socket_t j9socketP, I_32 secTime, I_32 uSecTime, BOOLEAN accept) ;
	/** see @ref j9sock.c::j9sock_set_nonblocking "j9sock_set_nonblocking"*/
    I_32  (PVMCALL sock_set_nonblocking)(struct J9PortLibrary *portLibrary, j9socket_t socketP, BOOLEAN nonblocking) ;
	/** see @ref j9sock.c::j9sock_error_message "j9sock_error_message"*/
    const char*  (PVMCALL sock_error_message)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9sock.c::j9sock_get_network_interfaces "j9sock_get_network_interfaces"*/
    I_32  (PVMCALL sock_get_network_interfaces)(struct J9PortLibrary *portLibrary, struct j9NetworkInterfaceArray_struct *array,BOOLEAN preferIPv4Stack) ;
	/** see @ref j9sock.c::j9sock_free_network_interface_struct "j9sock_free_network_interface_struct"*/
    I_32  (PVMCALL sock_free_network_interface_struct)(struct J9PortLibrary *portLibrary, struct j9NetworkInterfaceArray_struct* array) ;
	/** see @ref j9sock.c::j9sock_connect_with_timeout "j9sock_connect_with_timeout"*/
    I_32  (PVMCALL sock_connect_with_timeout)(struct J9PortLibrary *portLibrary, j9socket_t sock, j9sockaddr_t addr, U_32 timeout, U_32 step, U_8** context) ;
	/** see @ref j9str.c::j9str_ftime "j9str_ftime"*/
    U_32  (PVMCALL str_ftime)(struct J9PortLibrary *portLibrary, char *buf, U_32 bufLen, const char *format) ;
	/** see @ref j9mmap.c::j9mmap_startup "j9mmap_startup"*/
    I_32  (PVMCALL mmap_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9mmap.c::j9mmap_shutdown "j9mmap_shutdown"*/
    void  (PVMCALL mmap_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9mmap.c::j9mmap_capabilities "j9mmap_capabilities"*/
    I_32  (PVMCALL mmap_capabilities)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9mmap.c::j9mmap_map_file "j9mmap_map_file"*/
    void*  (PVMCALL mmap_map_file)(struct J9PortLibrary *portLibrary, const char *path, void **handle) ;
	/** see @ref j9mmap.c::j9mmap_unmap_file "j9mmap_unmap_file"*/
    void  (PVMCALL mmap_unmap_file)(struct J9PortLibrary *portLibrary, void *handle) ;
	/** see @ref j9shsem.c::j9shsem_startup "j9shsem_startup"*/
    I_32  (PVMCALL shsem_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9shsem.c::j9shsem_shutdown "j9shsem_shutdown"*/
    void  (PVMCALL shsem_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9shsem.c::j9shsem_open "j9shsem_open"*/
    IDATA  (PVMCALL shsem_open)(struct J9PortLibrary *portLibrary, struct j9shsem_handle** handle, const char* semname, int setSize, int permission) ;
	/** see @ref j9shsem.c::j9shsem_post "j9shsem_post"*/
    IDATA  (PVMCALL shsem_post)(struct J9PortLibrary *portLibrary, struct j9shsem_handle* handle, UDATA semset, UDATA flag) ;
	/** see @ref j9shsem.c::j9shsem_wait "j9shsem_wait"*/
    IDATA  (PVMCALL shsem_wait)(struct J9PortLibrary *portLibrary, struct j9shsem_handle* handle, UDATA semset, UDATA flag) ;
	/** see @ref j9shsem.c::j9shsem_getVal "j9shsem_getVal"*/
    IDATA  (PVMCALL shsem_getVal)(struct J9PortLibrary *portLibrary, struct j9shsem_handle* handle, UDATA semset) ;
	/** see @ref j9shsem.c::j9shsem_setVal "j9shsem_setVal"*/
    IDATA  (PVMCALL shsem_setVal)(struct J9PortLibrary *portLibrary, struct j9shsem_handle* handle, UDATA semset, IDATA value) ;
	/** see @ref j9shsem.c::j9shsem_close "j9shsem_close"*/
    void  (PVMCALL shsem_close)(struct J9PortLibrary *portLibrary, struct j9shsem_handle **handle) ;
	/** see @ref j9shsem.c::j9shsem_destroy "j9shsem_destroy"*/
    IDATA  (PVMCALL shsem_destroy)(struct J9PortLibrary *portLibrary, struct j9shsem_handle **handle) ;
	/** see @ref j9shmem.c::j9shmem_startup "j9shmem_startup"*/
    I_32  (PVMCALL shmem_startup)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9shmem.c::j9shmem_shutdown "j9shmem_shutdown"*/
    void  (PVMCALL shmem_shutdown)(struct J9PortLibrary *portLibrary) ;
	/** see @ref j9shmem.c::j9shmem_open "j9shmem_open"*/
    IDATA  (PVMCALL shmem_open)(struct J9PortLibrary *portLibrary, struct j9shmem_handle **handle, const char* rootname, I_32 size, I_32 perm) ;
	/** see @ref j9shmem.c::j9shmem_attach "j9shmem_attach"*/
    void*  (PVMCALL shmem_attach)(struct J9PortLibrary *portLibrary, struct j9shmem_handle* handle) ;
	/** see @ref j9shmem.c::j9shmem_detach "j9shmem_detach"*/
    IDATA  (PVMCALL shmem_detach)(struct J9PortLibrary *portLibrary, struct j9shmem_handle **handle) ;
	/** see @ref j9shmem.c::j9shmem_close "j9shmem_close"*/
    void  (PVMCALL shmem_close)(struct J9PortLibrary *portLibrary, struct j9shmem_handle **handle) ;
	/** see @ref j9shmem.c::j9shmem_destroy "j9shmem_destroy"*/
    IDATA  (PVMCALL shmem_destroy)(struct J9PortLibrary *portLibrary, struct j9shmem_handle **handle) ;
	/** see @ref j9shmem.c::j9shmem_findfirst "j9shmem_findfirst"*/
    UDATA  (PVMCALL shmem_findfirst)(struct J9PortLibrary *portLibrary, char *resultbuf) ;
	/** see @ref j9shmem.c::j9shmem_findnext "j9shmem_findnext"*/
    I_32  (PVMCALL shmem_findnext)(struct J9PortLibrary *portLibrary, UDATA findhandle, char *resultbuf) ;
	/** see @ref j9shmem.c::j9shmem_findclose "j9shmem_findclose"*/
    void  (PVMCALL shmem_findclose)(struct J9PortLibrary *portLibrary, UDATA findhandle) ;
	/** see @ref j9shmem.c::j9shmem_stat "j9shmem_stat"*/
    UDATA  (PVMCALL shmem_stat)(struct J9PortLibrary *portLibrary, const char* name, struct J9PortShmemStatistic* statbuf) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_limit "j9sysinfo_get_limit"*/
    U_32  (PVMCALL sysinfo_get_limit)(struct J9PortLibrary* portLibrary, U_32 resourceID, U_64* limit) ;
	/** see @ref j9sysinfo.c::j9sysinfo_get_processing_capacity "j9sysinfo_get_processing_capacity"*/
    UDATA  (PVMCALL sysinfo_get_processing_capacity)(struct J9PortLibrary *portLibrary) ;
} J9PortLibrary;


#define J9PORT_SL_FOUND  0
#define J9PORT_SL_NOT_FOUND  1
#define J9PORT_SL_INVALID  2
#define J9PORT_ARCH_X86  "x86"
#define J9PORT_ARCH_ARM  "arm"
#define J9PORT_ARCH_MIPS  "mips"
#define J9PORT_ARCH_ALPHA  "alpha"
#define J9PORT_ARCH_PPC  "ppc"
#define J9PORT_ARCH_PPC64  "ppc64"
#define J9PORT_ARCH_SH4  "sh4"
#define J9PORT_ARCH_SH3  "sh3"
#define J9PORT_ARCH_370  "370"
#define J9PORT_ARCH_68K  "M68000"
#define J9PORT_ARCH_SPARC  "sparc"
#define J9PORT_ARCH_S390  "s390"
#define J9PORT_ARCH_S390X  "s390x"
#define J9PORT_ARCH_PARISC  "PA-RISC"
#define J9PORT_ARCH_HAMMER  "amd64"
#define J9PORT_TTY_IN  0
#define J9PORT_TTY_OUT  1
#define J9PORT_TTY_ERR  2
#define J9PORT_CTLDATA_SIG_FLAGS  "SIG_FLAGS"
#define J9PORT_CTLDATA_TRACE_START  "TRACE_START"
#define J9PORT_CTLDATA_TRACE_STOP  "TRACE_STOP"
#define J9PORT_CTLDATA_SHMEM_GROUP_PERM  "SHMEM_GROUP_PERM"
#define J9PORT_CTLDATA_HTTP_PROXY_PARMS  "HTTP_PROXY_PARMS"
#define J9PORT_MAJOR_VERSION_NUMBER  6
#define J9PORT_MINOR_VERSION_NUMBER  1
#define J9PORT_CAPABILITY_BASE  0
#define J9PORT_CAPABILITY_STANDARD  1
#define J9PORT_CAPABILITY_FILESYSTEM  2
#define J9PORT_CAPABILITY_SOCKETS  4
#define J9PORT_CAPABILITY_LARGE_PAGE_SUPPORT  8
#define J9PORT_MMAP_CAPABILITY_COPYONWRITE  1
#define J9PORT_MMAP_FLAG_CREATE_FILE  1
#define J9PORT_MMAP_FLAG_READ  2
#define J9PORT_MMAP_FLAG_WRITE  4
#define J9PORT_MMAP_FLAG_COPYONWRITE  8
#define J9PORT_MMAP_FLAG_EXECUTABLE  16
#define J9PORT_SIG_FLAG_MAY_RETURN  1
#define J9PORT_SIG_FLAG_MAY_CONTINUE_EXECUTION  2
#define J9PORT_SIG_FLAG_SIGSEGV  4
#define J9PORT_SIG_FLAG_SIGBUS  8
#define J9PORT_SIG_FLAG_SIGILL  16
#define J9PORT_SIG_FLAG_SIGFPE  32
#define J9PORT_SIG_FLAG_SIGTRAP  64
#define J9PORT_SIG_FLAG_SIGRESERVED7  0x80
#define J9PORT_SIG_FLAG_SIGRESERVED8  0x100
#define J9PORT_SIG_FLAG_SIGRESERVED9  0x200
#define J9PORT_SIG_FLAG_SIGALLSYNC  124
#define J9PORT_SIG_FLAG_SIGQUIT  0x400
#define J9PORT_SIG_FLAG_SIGABRT  0x800
#define J9PORT_SIG_FLAG_SIGTERM  0x1000
#define J9PORT_SIG_FLAG_SIGRECONFIG  0x2000
#define J9PORT_SIG_FLAG_SIGRESERVED14  0x4000
#define J9PORT_SIG_FLAG_SIGRESERVED15  0x8000
#define J9PORT_SIG_FLAG_SIGRESERVED16  0x10000
#define J9PORT_SIG_FLAG_SIGRESERVED17  0x20000
#define J9PORT_SIG_FLAG_SIGALLASYNC  0x3C00
#define J9PORT_SIG_FLAG_SIGFPE_DIV_BY_ZERO  0x40020
#define J9PORT_SIG_FLAG_SIGFPE_INT_DIV_BY_ZERO  0x80020
#define J9PORT_SIG_FLAG_SIGFPE_INT_OVERFLOW  0x100020
#define J9PORT_SIG_EXCEPTION_CONTINUE_SEARCH  0
#define J9PORT_SIG_EXCEPTION_CONTINUE_EXECUTION  1
#define J9PORT_SIG_EXCEPTION_RETURN  2
#define J9PORT_SIG_EXCEPTION_OCCURRED  1
#define J9PORT_SIG_ERROR  -1
#define J9PORT_SIG_SIGNAL  0
#define J9PORT_SIG_GPR  1
#define J9PORT_SIG_OTHER  2
#define J9PORT_SIG_CONTROL  3
#define J9PORT_SIG_FPR  4
#define J9PORT_SIG_MODULE  5
#define J9PORT_SIG_NUM_CATEGORIES  6
#define J9PORT_SIG_SIGNAL_TYPE  -1
#define J9PORT_SIG_SIGNAL_CODE  -2
#define J9PORT_SIG_SIGNAL_ERROR_VALUE  -3
#define J9PORT_SIG_CONTROL_PC  -4
#define J9PORT_SIG_CONTROL_SP  -5
#define J9PORT_SIG_CONTROL_BP  -6
#define J9PORT_SIG_GPR_X86_EDI  -7
#define J9PORT_SIG_GPR_X86_ESI  -8
#define J9PORT_SIG_GPR_X86_EAX  -9
#define J9PORT_SIG_GPR_X86_EBX  -10
#define J9PORT_SIG_GPR_X86_ECX  -11
#define J9PORT_SIG_GPR_X86_EDX  -12
#define J9PORT_SIG_MODULE_NAME  -13
#define J9PORT_SIG_SIGNAL_ADDRESS  -14
#define J9PORT_SIG_SIGNAL_HANDLER  -15
#define J9PORT_SIG_SIGNAL_PLATFORM_SIGNAL_TYPE  -16
#define J9PORT_SIG_SIGNAL_INACCESSIBLE_ADDRESS  -17
#define J9PORT_SIG_GPR_AMD64_RDI  -18
#define J9PORT_SIG_GPR_AMD64_RSI  -19
#define J9PORT_SIG_GPR_AMD64_RAX  -20
#define J9PORT_SIG_GPR_AMD64_RBX  -21
#define J9PORT_SIG_GPR_AMD64_RCX  -22
#define J9PORT_SIG_GPR_AMD64_RDX  -23
#define J9PORT_SIG_GPR_AMD64_R8  -24
#define J9PORT_SIG_GPR_AMD64_R9  -25
#define J9PORT_SIG_GPR_AMD64_R10  -26
#define J9PORT_SIG_GPR_AMD64_R11  -27
#define J9PORT_SIG_GPR_AMD64_R12  -28
#define J9PORT_SIG_GPR_AMD64_R13  -29
#define J9PORT_SIG_GPR_AMD64_R14  -30
#define J9PORT_SIG_GPR_AMD64_R15  -31
#define J9PORT_SIG_VALUE_UNDEFINED  1
#define J9PORT_SIG_VALUE_STRING  2
#define J9PORT_SIG_VALUE_ADDRESS  3
#define J9PORT_SIG_VALUE_32  4
#define J9PORT_SIG_VALUE_64  5
#define J9PORT_SIG_VALUE_FLOAT_64  6
#define J9PORT_SIG_OPTIONS_JSIG_NO_CHAIN  1
#define J9PORT_SIG_OPTIONS_REDUCED_SIGNALS  2
#define J9SIZEOF_J9PortLibrary 936

#define J9PORT_CAPABILITY_MASK ((U_64)(J9PORT_CAPABILITY_STANDARD | J9PORT_CAPABILITY_FILESYSTEM | J9PORT_CAPABILITY_SOCKETS))


#define J9PORT_SET_VERSION(portLibraryVersion, capabilityMask) \
	(portLibraryVersion)->majorVersionNumber = J9PORT_MAJOR_VERSION_NUMBER; \
	(portLibraryVersion)->minorVersionNumber = J9PORT_MINOR_VERSION_NUMBER; \
	(portLibraryVersion)->capabilities = (capabilityMask)
#define J9PORT_SET_VERSION_DEFAULT(portLibraryVersion) \
	(portLibraryVersion)->majorVersionNumber = J9PORT_MAJOR_VERSION_NUMBER; \
	(portLibraryVersion)->minorVersionNumber = J9PORT_MINOR_VERSION_NUMBER; \
	(portLibraryVersion)->capabilities = J9PORT_CAPABILITY_MASK


/**
 * @name Port library startup and shutdown functions
 * @anchor PortStartup
 * Create, initialize, startup and shutdow the port library
 * @{
 */
/** Standard startup and shutdown (port library allocated on stack or by application)  */
extern J9_CFUNC I_32 VMCALL j9port_create_library(struct J9PortLibrary *portLibrary, struct J9PortLibraryVersion *version, UDATA size);
extern J9_CFUNC I_32 VMCALL j9port_init_library(struct J9PortLibrary*portLibrary, struct J9PortLibraryVersion *version, UDATA size);
extern J9_CFUNC I_32 VMCALL j9port_shutdown_library(struct J9PortLibrary *portLibrary);
extern J9_CFUNC I_32 VMCALL j9port_startup_library(struct J9PortLibrary *portLibrary);

/** Port library self allocation routines */
extern J9_CFUNC I_32 VMCALL j9port_allocate_library(struct J9PortLibraryVersion *expectedVersion, struct J9PortLibrary **portLibrary);
/** @} */

/**
 * @name Port library version and compatability queries
 * @anchor PortVersionControl
 * Determine port library compatability and version.
 * @{
 */
extern J9_CFUNC UDATA VMCALL j9port_getSize(struct J9PortLibraryVersion *version);
extern J9_CFUNC I_32 VMCALL j9port_getVersion(struct J9PortLibrary *portLibrary, struct J9PortLibraryVersion *version);
extern J9_CFUNC I_32 VMCALL j9port_isCompatible(struct J9PortLibraryVersion *expectedVersion);
/** @} */


/** 
 * @name PortLibrary Access functions
 * Convenience helpers for accessing port library functionality.  Users can 
 * either call functions directly via the table or by help macros.
 * @code 
 * memoryPointer = portLibrary->mem_allocate_memory(portLibrary, 1024); 
 * @endcode
 * @code
 * PORT_ACCESS_FROM_ENV(jniEnv);
 * memoryPointer = j9mem_allocate_memory(1024);
 * @endcode
 * @{
 */
#if !defined(J9PORT_LIBRARY_DEFINE)
#define j9port_shutdown_library() privatePortLibrary->port_shutdown_library(privatePortLibrary)
#define j9port_isFunctionOverridden(param1) privatePortLibrary->port_isFunctionOverridden(privatePortLibrary,param1)
#define j9port_tls_free() privatePortLibrary->port_tls_free(privatePortLibrary)
#define j9error_startup() privatePortLibrary->error_startup(privatePortLibrary)
#define j9error_shutdown() privatePortLibrary->error_shutdown(privatePortLibrary)
#define j9error_last_error_number() privatePortLibrary->error_last_error_number(privatePortLibrary)
#define j9error_last_error_message() privatePortLibrary->error_last_error_message(privatePortLibrary)
#define j9error_set_last_error(param1,param2) privatePortLibrary->error_set_last_error(privatePortLibrary,param1,param2)
#define j9error_set_last_error_with_message(param1,param2) privatePortLibrary->error_set_last_error_with_message(privatePortLibrary,param1,param2)
#define j9time_startup() privatePortLibrary->time_startup(privatePortLibrary)
#define j9time_shutdown() privatePortLibrary->time_shutdown(privatePortLibrary)
#define j9time_msec_clock() privatePortLibrary->time_msec_clock(privatePortLibrary)
#define j9time_usec_clock() privatePortLibrary->time_usec_clock(privatePortLibrary)
#define j9time_current_time_millis() privatePortLibrary->time_current_time_millis(privatePortLibrary)
#define j9time_hires_clock() privatePortLibrary->time_hires_clock(privatePortLibrary)
#define j9time_hires_frequency() privatePortLibrary->time_hires_frequency(privatePortLibrary)
#define j9time_hires_delta(param1,param2,param3) privatePortLibrary->time_hires_delta(privatePortLibrary,param1,param2,param3)
#define j9sysinfo_startup() privatePortLibrary->sysinfo_startup(privatePortLibrary)
#define j9sysinfo_shutdown() privatePortLibrary->sysinfo_shutdown(privatePortLibrary)
#define j9sysinfo_get_pid() privatePortLibrary->sysinfo_get_pid(privatePortLibrary)
#define j9sysinfo_get_physical_memory() privatePortLibrary->sysinfo_get_physical_memory(privatePortLibrary)
#define j9sysinfo_get_OS_version() privatePortLibrary->sysinfo_get_OS_version(privatePortLibrary)
#define j9sysinfo_get_env(param1,param2,param3) privatePortLibrary->sysinfo_get_env(privatePortLibrary,param1,param2,param3)
#define j9sysinfo_get_CPU_architecture() privatePortLibrary->sysinfo_get_CPU_architecture(privatePortLibrary)
#define j9sysinfo_get_OS_type() privatePortLibrary->sysinfo_get_OS_type(privatePortLibrary)
#define j9sysinfo_get_classpathSeparator() privatePortLibrary->sysinfo_get_classpathSeparator(privatePortLibrary)
#define j9sysinfo_get_executable_name(param1,param2) privatePortLibrary->sysinfo_get_executable_name(privatePortLibrary,param1,param2)
#define j9sysinfo_get_number_CPUs() privatePortLibrary->sysinfo_get_number_CPUs(privatePortLibrary)
#define j9sysinfo_get_username(param1,param2) privatePortLibrary->sysinfo_get_username(privatePortLibrary,param1,param2)
#define j9sysinfo_get_groupname(param1,param2) privatePortLibrary->sysinfo_get_groupname(privatePortLibrary,param1,param2)
#define j9file_startup() privatePortLibrary->file_startup(privatePortLibrary)
#define j9file_shutdown() privatePortLibrary->file_shutdown(privatePortLibrary)
#define j9file_write(param1,param2,param3) privatePortLibrary->file_write(privatePortLibrary,param1,param2,param3)
#define j9file_write_text(param1,param2,param3) privatePortLibrary->file_write_text(privatePortLibrary,param1,param2,param3)
#define j9file_vprintf(param1,param2,param3) privatePortLibrary->file_vprintf(privatePortLibrary,param1,param2,param3)
#define j9file_printf privatePortLibrary->file_printf
#define j9file_open(param1,param2,param3) privatePortLibrary->file_open(privatePortLibrary,param1,param2,param3)
#define j9file_close(param1) privatePortLibrary->file_close(privatePortLibrary,param1)
#define j9file_seek(param1,param2,param3) privatePortLibrary->file_seek(privatePortLibrary,param1,param2,param3)
#define j9file_read(param1,param2,param3) privatePortLibrary->file_read(privatePortLibrary,param1,param2,param3)
#define j9file_unlink(param1) privatePortLibrary->file_unlink(privatePortLibrary,param1)
#define j9file_attr(param1) privatePortLibrary->file_attr(privatePortLibrary,param1)
#define j9file_lastmod(param1) privatePortLibrary->file_lastmod(privatePortLibrary,param1)
#define j9file_length(param1) privatePortLibrary->file_length(privatePortLibrary,param1)
#define j9file_set_length(param1,param2) privatePortLibrary->file_set_length(privatePortLibrary,param1,param2)
#define j9file_sync(param1) privatePortLibrary->file_sync(privatePortLibrary,param1)
#define j9sl_startup() privatePortLibrary->sl_startup(privatePortLibrary)
#define j9sl_shutdown() privatePortLibrary->sl_shutdown(privatePortLibrary)
#define j9sl_close_shared_library(param1) privatePortLibrary->sl_close_shared_library(privatePortLibrary,param1)
#define j9sl_open_shared_library(param1,param2,param3) privatePortLibrary->sl_open_shared_library(privatePortLibrary,param1,param2,param3)
#define j9sl_lookup_name(param1,param2,param3,param4) privatePortLibrary->sl_lookup_name(privatePortLibrary,param1,param2,param3,param4)
#define j9tty_startup() privatePortLibrary->tty_startup(privatePortLibrary)
#define j9tty_shutdown() privatePortLibrary->tty_shutdown(privatePortLibrary)
#define j9tty_printf privatePortLibrary->tty_printf
#define j9tty_vprintf(param1,param2) privatePortLibrary->tty_vprintf(privatePortLibrary,param1,param2)
#define j9tty_get_chars(param1,param2) privatePortLibrary->tty_get_chars(privatePortLibrary,param1,param2)
#define j9tty_err_printf privatePortLibrary->tty_err_printf
#define j9tty_err_vprintf(param1,param2) privatePortLibrary->tty_err_vprintf(privatePortLibrary,param1,param2)
#define j9tty_available() privatePortLibrary->tty_available(privatePortLibrary)
#define j9mem_startup(param1) privatePortLibrary->mem_startup(privatePortLibrary,param1)
#define j9mem_shutdown() privatePortLibrary->mem_shutdown(privatePortLibrary)
#define j9mem_allocate_memory(param1) privatePortLibrary->mem_allocate_memory(privatePortLibrary,param1)
#define j9mem_allocate_memory_callSite(param1,param2) privatePortLibrary->mem_allocate_memory_callSite(privatePortLibrary,param1,param2)
#define j9mem_free_memory(param1) privatePortLibrary->mem_free_memory(privatePortLibrary,param1)
#define j9mem_reallocate_memory(param1,param2) privatePortLibrary->mem_reallocate_memory(privatePortLibrary,param1,param2)
#define j9cpu_startup() privatePortLibrary->cpu_startup(privatePortLibrary)
#define j9cpu_shutdown() privatePortLibrary->cpu_shutdown(privatePortLibrary)
#define j9cpu_flush_icache(param1,param2) privatePortLibrary->cpu_flush_icache(privatePortLibrary,param1,param2)
#define j9vmem_startup() privatePortLibrary->vmem_startup(privatePortLibrary)
#define j9vmem_shutdown() privatePortLibrary->vmem_shutdown(privatePortLibrary)
#define j9vmem_commit_memory(param1,param2,param3) privatePortLibrary->vmem_commit_memory(privatePortLibrary,param1,param2,param3)
#define j9vmem_decommit_memory(param1,param2,param3) privatePortLibrary->vmem_decommit_memory(privatePortLibrary,param1,param2,param3)
#define j9vmem_free_memory(param1,param2,param3) privatePortLibrary->vmem_free_memory(privatePortLibrary,param1,param2,param3)
#define j9vmem_reserve_memory(param1,param2,param3,param4,param5) privatePortLibrary->vmem_reserve_memory(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9vmem_supported_page_sizes() privatePortLibrary->vmem_supported_page_sizes(privatePortLibrary)
#define j9vmem_default_large_page_size() privatePortLibrary->vmem_default_large_page_size(privatePortLibrary)
#define j9sock_startup() privatePortLibrary->sock_startup(privatePortLibrary)
#define j9sock_shutdown() privatePortLibrary->sock_shutdown(privatePortLibrary)
#define j9sock_htons(param1) privatePortLibrary->sock_htons(privatePortLibrary,param1)
#define j9sock_write(param1,param2,param3,param4) privatePortLibrary->sock_write(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_sockaddr(param1,param2,param3) privatePortLibrary->sock_sockaddr(privatePortLibrary,param1,param2,param3)
#define j9sock_read(param1,param2,param3,param4) privatePortLibrary->sock_read(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_socket(param1,param2,param3,param4) privatePortLibrary->sock_socket(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_close(param1) privatePortLibrary->sock_close(privatePortLibrary,param1)
#define j9sock_connect(param1,param2) privatePortLibrary->sock_connect(privatePortLibrary,param1,param2)
#define j9sock_inetaddr(param1,param2) privatePortLibrary->sock_inetaddr(privatePortLibrary,param1,param2)
#define j9sock_gethostbyname(param1,param2) privatePortLibrary->sock_gethostbyname(privatePortLibrary,param1,param2)
#define j9sock_hostent_addrlist(param1,param2) privatePortLibrary->sock_hostent_addrlist(privatePortLibrary,param1,param2)
#define j9sock_sockaddr_init(param1,param2,param3,param4) privatePortLibrary->sock_sockaddr_init(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_linger_init(param1,param2,param3) privatePortLibrary->sock_linger_init(privatePortLibrary,param1,param2,param3)
#define j9sock_setopt_linger(param1,param2,param3,param4) privatePortLibrary->sock_setopt_linger(privatePortLibrary,param1,param2,param3,param4)
#define j9gp_startup() privatePortLibrary->gp_startup(privatePortLibrary)
#define j9gp_shutdown() privatePortLibrary->gp_shutdown(privatePortLibrary)
#define j9gp_protect(param1,param2) privatePortLibrary->gp_protect(privatePortLibrary,param1,param2)
#define j9gp_register_handler(param1,param2) privatePortLibrary->gp_register_handler(privatePortLibrary,param1,param2)
#define j9gp_info(param1,param2,param3,param4,param5) privatePortLibrary->gp_info(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9gp_info_count(param1,param2) privatePortLibrary->gp_info_count(privatePortLibrary,param1,param2)
#define j9gp_handler_function() privatePortLibrary->gp_handler_function(privatePortLibrary)
#define j9str_startup() privatePortLibrary->str_startup(privatePortLibrary)
#define j9str_shutdown() privatePortLibrary->str_shutdown(privatePortLibrary)
#define j9str_printf privatePortLibrary->str_printf
#define j9str_vprintf(param1,param2,param3,param4) privatePortLibrary->str_vprintf(privatePortLibrary,param1,param2,param3,param4)
#define j9exit_startup() privatePortLibrary->exit_startup(privatePortLibrary)
#define j9exit_shutdown() privatePortLibrary->exit_shutdown(privatePortLibrary)
#define j9exit_get_exit_code() privatePortLibrary->exit_get_exit_code(privatePortLibrary)
#define j9exit_shutdown_and_exit(param1) privatePortLibrary->exit_shutdown_and_exit(privatePortLibrary,param1)
#define j9dump_create(param1,param2,param3) privatePortLibrary->dump_create(privatePortLibrary,param1,param2,param3)
#define j9nls_startup() privatePortLibrary->nls_startup(privatePortLibrary)
#define j9nls_shutdown() privatePortLibrary->nls_shutdown(privatePortLibrary)
#define j9nls_set_catalog(param1,param2,param3,param4) privatePortLibrary->nls_set_catalog(privatePortLibrary,param1,param2,param3,param4)
#define j9nls_set_locale(param1,param2,param3) privatePortLibrary->nls_set_locale(privatePortLibrary,param1,param2,param3)
#define j9nls_get_language() privatePortLibrary->nls_get_language(privatePortLibrary)
#define j9nls_get_region() privatePortLibrary->nls_get_region(privatePortLibrary)
#define j9nls_get_variant() privatePortLibrary->nls_get_variant(privatePortLibrary)
#define j9nls_printf privatePortLibrary->nls_printf
#define j9nls_vprintf(param1,param2,param3,param4) privatePortLibrary->nls_vprintf(privatePortLibrary,param1,param2,param3,param4)
#define j9nls_lookup_message(param1,param2,param3,param4) privatePortLibrary->nls_lookup_message(privatePortLibrary,param1,param2,param3,param4)
#define j9ipcmutex_startup() privatePortLibrary->ipcmutex_startup(privatePortLibrary)
#define j9ipcmutex_shutdown() privatePortLibrary->ipcmutex_shutdown(privatePortLibrary)
#define j9ipcmutex_acquire(param1) privatePortLibrary->ipcmutex_acquire(privatePortLibrary,param1)
#define j9ipcmutex_release(param1) privatePortLibrary->ipcmutex_release(privatePortLibrary,param1)
#define j9port_control(param1,param2) privatePortLibrary->port_control(privatePortLibrary,param1,param2)
#define j9sig_startup() privatePortLibrary->sig_startup(privatePortLibrary)
#define j9sig_shutdown() privatePortLibrary->sig_shutdown(privatePortLibrary)
#define j9sig_protect(param1,param2,param3,param4,param5,param6) privatePortLibrary->sig_protect(privatePortLibrary,param1,param2,param3,param4,param5,param6)
#define j9sig_can_protect(param1) privatePortLibrary->sig_can_protect(privatePortLibrary,param1)
#define j9sig_set_async_signal_handler(param1,param2,param3) privatePortLibrary->sig_set_async_signal_handler(privatePortLibrary,param1,param2,param3)
#define j9sig_info(param1,param2,param3,param4,param5) privatePortLibrary->sig_info(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9sig_info_count(param1,param2) privatePortLibrary->sig_info_count(privatePortLibrary,param1,param2)
#define j9sig_set_options(param1) privatePortLibrary->sig_set_options(privatePortLibrary,param1)
#define j9sig_get_options() privatePortLibrary->sig_get_options(privatePortLibrary)
#define j9sysinfo_DLPAR_enabled() privatePortLibrary->sysinfo_DLPAR_enabled(privatePortLibrary)
#define j9sysinfo_DLPAR_max_CPUs() privatePortLibrary->sysinfo_DLPAR_max_CPUs(privatePortLibrary)
#define j9sysinfo_weak_memory_consistency() privatePortLibrary->sysinfo_weak_memory_consistency(privatePortLibrary)
#define j9file_read_text(param1,param2,param3) privatePortLibrary->file_read_text(privatePortLibrary,param1,param2,param3)
#define j9file_mkdir(param1) privatePortLibrary->file_mkdir(privatePortLibrary,param1)
#define j9file_move(param1,param2) privatePortLibrary->file_move(privatePortLibrary,param1,param2)
#define j9file_unlinkdir(param1) privatePortLibrary->file_unlinkdir(privatePortLibrary,param1)
#define j9file_findfirst(param1,param2) privatePortLibrary->file_findfirst(privatePortLibrary,param1,param2)
#define j9file_findnext(param1,param2) privatePortLibrary->file_findnext(privatePortLibrary,param1,param2)
#define j9file_findclose(param1) privatePortLibrary->file_findclose(privatePortLibrary,param1)
#define j9file_error_message() privatePortLibrary->file_error_message(privatePortLibrary)
#define j9sock_htonl(param1) privatePortLibrary->sock_htonl(privatePortLibrary,param1)
#define j9sock_bind(param1,param2) privatePortLibrary->sock_bind(privatePortLibrary,param1,param2)
#define j9sock_accept(param1,param2,param3) privatePortLibrary->sock_accept(privatePortLibrary,param1,param2,param3)
#define j9sock_shutdown_input(param1) privatePortLibrary->sock_shutdown_input(privatePortLibrary,param1)
#define j9sock_shutdown_output(param1) privatePortLibrary->sock_shutdown_output(privatePortLibrary,param1)
#define j9sock_listen(param1,param2) privatePortLibrary->sock_listen(privatePortLibrary,param1,param2)
#define j9sock_ntohl(param1) privatePortLibrary->sock_ntohl(privatePortLibrary,param1)
#define j9sock_ntohs(param1) privatePortLibrary->sock_ntohs(privatePortLibrary,param1)
#define j9sock_getpeername(param1,param2) privatePortLibrary->sock_getpeername(privatePortLibrary,param1,param2)
#define j9sock_getsockname(param1,param2) privatePortLibrary->sock_getsockname(privatePortLibrary,param1,param2)
#define j9sock_readfrom(param1,param2,param3,param4,param5) privatePortLibrary->sock_readfrom(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9sock_select(param1,param2,param3,param4,param5) privatePortLibrary->sock_select(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9sock_writeto(param1,param2,param3,param4,param5) privatePortLibrary->sock_writeto(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9sock_inetntoa(param1,param2) privatePortLibrary->sock_inetntoa(privatePortLibrary,param1,param2)
#define j9sock_gethostbyaddr(param1,param2,param3,param4) privatePortLibrary->sock_gethostbyaddr(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_gethostname(param1,param2) privatePortLibrary->sock_gethostname(privatePortLibrary,param1,param2)
#define j9sock_hostent_aliaslist(param1,param2) privatePortLibrary->sock_hostent_aliaslist(privatePortLibrary,param1,param2)
#define j9sock_hostent_hostname(param1,param2) privatePortLibrary->sock_hostent_hostname(privatePortLibrary,param1,param2)
#define j9sock_sockaddr_port(param1) privatePortLibrary->sock_sockaddr_port(privatePortLibrary,param1)
#define j9sock_sockaddr_address(param1) privatePortLibrary->sock_sockaddr_address(privatePortLibrary,param1)
#define j9sock_fdset_init(param1) privatePortLibrary->sock_fdset_init(privatePortLibrary,param1)
#define j9sock_fdset_size(param1) privatePortLibrary->sock_fdset_size(privatePortLibrary,param1)
#define j9sock_timeval_init(param1,param2,param3) privatePortLibrary->sock_timeval_init(privatePortLibrary,param1,param2,param3)
#define j9sock_getopt_int(param1,param2,param3,param4) privatePortLibrary->sock_getopt_int(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_setopt_int(param1,param2,param3,param4) privatePortLibrary->sock_setopt_int(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_getopt_bool(param1,param2,param3,param4) privatePortLibrary->sock_getopt_bool(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_setopt_bool(param1,param2,param3,param4) privatePortLibrary->sock_setopt_bool(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_getopt_byte(param1,param2,param3,param4) privatePortLibrary->sock_getopt_byte(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_setopt_byte(param1,param2,param3,param4) privatePortLibrary->sock_setopt_byte(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_getopt_linger(param1,param2,param3,param4) privatePortLibrary->sock_getopt_linger(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_getopt_sockaddr(param1,param2,param3,param4) privatePortLibrary->sock_getopt_sockaddr(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_setopt_sockaddr(param1,param2,param3,param4) privatePortLibrary->sock_setopt_sockaddr(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_setopt_ipmreq(param1,param2,param3,param4) privatePortLibrary->sock_setopt_ipmreq(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_linger_enabled(param1,param2) privatePortLibrary->sock_linger_enabled(privatePortLibrary,param1,param2)
#define j9sock_linger_linger(param1,param2) privatePortLibrary->sock_linger_linger(privatePortLibrary,param1,param2)
#define j9sock_ipmreq_init(param1,param2,param3) privatePortLibrary->sock_ipmreq_init(privatePortLibrary,param1,param2,param3)
#define j9sock_setflag(param1,param2) privatePortLibrary->sock_setflag(privatePortLibrary,param1,param2)
#define j9sock_freeaddrinfo(param1) privatePortLibrary->sock_freeaddrinfo(privatePortLibrary,param1)
#define j9sock_getaddrinfo(param1,param2,param3) privatePortLibrary->sock_getaddrinfo(privatePortLibrary,param1,param2,param3)
#define j9sock_getaddrinfo_address(param1,param2,param3,param4) privatePortLibrary->sock_getaddrinfo_address(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_getaddrinfo_create_hints(param1,param2,param3,param4,param5) privatePortLibrary->sock_getaddrinfo_create_hints(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9sock_getaddrinfo_family(param1,param2,param3) privatePortLibrary->sock_getaddrinfo_family(privatePortLibrary,param1,param2,param3)
#define j9sock_getaddrinfo_length(param1,param2) privatePortLibrary->sock_getaddrinfo_length(privatePortLibrary,param1,param2)
#define j9sock_getaddrinfo_name(param1,param2,param3) privatePortLibrary->sock_getaddrinfo_name(privatePortLibrary,param1,param2,param3)
#define j9sock_getnameinfo(param1,param2,param3,param4,param5) privatePortLibrary->sock_getnameinfo(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9sock_ipv6_mreq_init(param1,param2,param3) privatePortLibrary->sock_ipv6_mreq_init(privatePortLibrary,param1,param2,param3)
#define j9sock_setopt_ipv6_mreq(param1,param2,param3,param4) privatePortLibrary->sock_setopt_ipv6_mreq(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_sockaddr_address6(param1,param2,param3,param4) privatePortLibrary->sock_sockaddr_address6(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_sockaddr_family(param1,param2) privatePortLibrary->sock_sockaddr_family(privatePortLibrary,param1,param2)
#define j9sock_sockaddr_init6(param1,param2,param3,param4,param5,param6,param7,param8) privatePortLibrary->sock_sockaddr_init6(privatePortLibrary,param1,param2,param3,param4,param5,param6,param7,param8)
#define j9sock_socketIsValid(param1) privatePortLibrary->sock_socketIsValid(privatePortLibrary,param1)
#define j9sock_select_read(param1,param2,param3,param4) privatePortLibrary->sock_select_read(privatePortLibrary,param1,param2,param3,param4)
#define j9sock_set_nonblocking(param1,param2) privatePortLibrary->sock_set_nonblocking(privatePortLibrary,param1,param2)
#define j9sock_error_message() privatePortLibrary->sock_error_message(privatePortLibrary)
#define j9sock_get_network_interfaces(param1,param2) privatePortLibrary->sock_get_network_interfaces(privatePortLibrary,param1,param2)
#define j9sock_free_network_interface_struct(param1) privatePortLibrary->sock_free_network_interface_struct(privatePortLibrary,param1)
#define j9sock_connect_with_timeout(param1,param2,param3,param4,param5) privatePortLibrary->sock_connect_with_timeout(privatePortLibrary,param1,param2,param3,param4,param5)
#define j9str_ftime(param1,param2,param3) privatePortLibrary->str_ftime(privatePortLibrary,param1,param2,param3)
#define j9mmap_startup() privatePortLibrary->mmap_startup(privatePortLibrary)
#define j9mmap_shutdown() privatePortLibrary->mmap_shutdown(privatePortLibrary)
#define j9mmap_capabilities() privatePortLibrary->mmap_capabilities(privatePortLibrary)
#define j9mmap_map_file(param1,param2) privatePortLibrary->mmap_map_file(privatePortLibrary,param1,param2)
#define j9mmap_unmap_file(param1) privatePortLibrary->mmap_unmap_file(privatePortLibrary,param1)
#define j9shsem_startup() privatePortLibrary->shsem_startup(privatePortLibrary)
#define j9shsem_shutdown() privatePortLibrary->shsem_shutdown(privatePortLibrary)
#define j9shsem_open(param1,param2,param3,param4) privatePortLibrary->shsem_open(privatePortLibrary,param1,param2,param3,param4)
#define j9shsem_post(param1,param2,param3) privatePortLibrary->shsem_post(privatePortLibrary,param1,param2,param3)
#define j9shsem_wait(param1,param2,param3) privatePortLibrary->shsem_wait(privatePortLibrary,param1,param2,param3)
#define j9shsem_getVal(param1,param2) privatePortLibrary->shsem_getVal(privatePortLibrary,param1,param2)
#define j9shsem_setVal(param1,param2,param3) privatePortLibrary->shsem_setVal(privatePortLibrary,param1,param2,param3)
#define j9shsem_close(param1) privatePortLibrary->shsem_close(privatePortLibrary,param1)
#define j9shsem_destroy(param1) privatePortLibrary->shsem_destroy(privatePortLibrary,param1)
#define j9shmem_startup() privatePortLibrary->shmem_startup(privatePortLibrary)
#define j9shmem_shutdown() privatePortLibrary->shmem_shutdown(privatePortLibrary)
#define j9shmem_open(param1,param2,param3,param4) privatePortLibrary->shmem_open(privatePortLibrary,param1,param2,param3,param4)
#define j9shmem_attach(param1) privatePortLibrary->shmem_attach(privatePortLibrary,param1)
#define j9shmem_detach(param1) privatePortLibrary->shmem_detach(privatePortLibrary,param1)
#define j9shmem_close(param1) privatePortLibrary->shmem_close(privatePortLibrary,param1)
#define j9shmem_destroy(param1) privatePortLibrary->shmem_destroy(privatePortLibrary,param1)
#define j9shmem_findfirst(param1) privatePortLibrary->shmem_findfirst(privatePortLibrary,param1)
#define j9shmem_findnext(param1,param2) privatePortLibrary->shmem_findnext(privatePortLibrary,param1,param2)
#define j9shmem_findclose(param1) privatePortLibrary->shmem_findclose(privatePortLibrary,param1)
#define j9shmem_stat(param1,param2) privatePortLibrary->shmem_stat(privatePortLibrary,param1,param2)
#define j9sysinfo_get_limit(param1,param2) privatePortLibrary->sysinfo_get_limit(privatePortLibrary,param1,param2)
#define j9sysinfo_get_processing_capacity() privatePortLibrary->sysinfo_get_processing_capacity(privatePortLibrary)


#undef j9nls_lookup_message
#define j9nls_lookup_message(param1,param2,param3) privatePortLibrary->nls_lookup_message(privatePortLibrary,param1,param2,param3)

#undef j9nls_vprintf
#define j9nls_vprintf(param1,param2,param3) privatePortLibrary->j9nls_vprintf(privatePortLibrary,param1,param2,param3)

#undef j9mem_allocate_memory
#define j9mem_allocate_memory(param1) privatePortLibrary->mem_allocate_memory_callSite(privatePortLibrary,param1, J9_GET_CALLSITE())

#undef j9mem_allocate_code_memory
#define j9mem_allocate_code_memory(param1) privatePortLibrary->mem_allocate_code_memory_callSite(privatePortLibrary,param1, J9_GET_CALLSITE())

#endif /* !J9PORT_LIBRARY_DEFINE */

/** @} */

#endif
