/*
*	(c) Copyright IBM Corp. 1998, 2006 All Rights Reserved
*/

/**
 * @file
 * @ingroup Port
 * @brief Port Library Error Codes
 *
 * When an error is reported by the operating system the port library must translate this OS specific error code to a 
 * portable error code.  All portable error codes are negative numbers.  Not every module of the port library will have
 * error codes dedicated to it's own use, some will use the generic portable error code values.
 *
 * Errors reported by the OS may be recorded by calling the port library functions @ref j9error.c::j9error_set_last_error "j9error_set_last_error()"
 * or @ref j9error.c::j9error_set_last_error_with_message "j9error_set_last_error_with_message()".  The mapping of the OS specific error
 * code to a portable error code is the responsibility of the calling module.
 */
#ifndef j9porterror_h
#define j9porterror_h

/**
 * @name Generic Errors
 * Generic error codes for modules that do not have their own specific errors.  Where possible it is recommended that all
 * modules that return error codes have their own set
 *
 * @internal J9PORT_ERROR* range from -1 to -99 avoid overlap
 * @{
 */
#define J9PORT_ERROR_BASE -1
#define J9PORT_ERROR_OPFAILED J9PORT_ERROR_BASE
#define J9PORT_ERROR_EOF J9PORT_ERROR_BASE-1
#define J9PORT_ERROR_NOPERMISSION J9PORT_ERROR_BASE-2
#define J9PORT_ERROR_NOTFOUND J9PORT_ERROR_BASE-3
#define J9PORT_ERROR_NAMETOOLONG J9PORT_ERROR_BASE-4
#define J9PORT_ERROR_DISKFULL J9PORT_ERROR_BASE-5
#define J9PORT_ERROR_EXIST J9PORT_ERROR_BASE-6
#define J9PORT_ERROR_NOTEXIST J9PORT_ERROR_BASE-7
#define J9PORT_ERROR_SYSTEMFULL J9PORT_ERROR_BASE-8
#define J9PORT_ERROR_NOENT J9PORT_ERROR_BASE-9
#define J9PORT_ERROR_DIRECTORY J9PORT_ERROR_BASE-10
#define J9PORT_ERROR_NOTDIRECTORY J9PORT_ERROR_BASE-11
#define J9PORT_ERROR_LOOP J9PORT_ERROR_BASE-12
#define J9PORT_ERROR_BADF J9PORT_ERROR_BASE-13
#define J9PORT_ERROR_WOULDBLOCK J9PORT_ERROR_BASE-14
#define J9PORT_ERROR_INVALID J9PORT_ERROR_BASE-15
/** @} */

/** 
 * @name Port Library startup failure code
 * Failures related to the initialization and startup of the port library.
 *
 * @internal J9PORT_ERROR_STARTUP* range from -100 to -149 to avoid overlap
 * @{
 */
#define J9PORT_ERROR_STARTUP_BASE -100
#define J9PORT_ERROR_STARTUP_THREAD (J9PORT_ERROR_STARTUP_BASE)
#define J9PORT_ERROR_STARTUP_MEM (J9PORT_ERROR_STARTUP_BASE -1)
#define J9PORT_ERROR_STARTUP_TLS (J9PORT_ERROR_STARTUP_BASE -2)
#define J9PORT_ERROR_STARTUP_TLS_ALLOC (J9PORT_ERROR_STARTUP_BASE -3)
#define J9PORT_ERROR_STARTUP_TLS_MUTEX (J9PORT_ERROR_STARTUP_BASE -4)
#define J9PORT_ERROR_STARTUP_CPU (J9PORT_ERROR_STARTUP_BASE -5)
#define J9PORT_ERROR_STARTUP_VMEM (J9PORT_ERROR_STARTUP_BASE -6)
#define J9PORT_ERROR_STARTUP_FILE (J9PORT_ERROR_STARTUP_BASE -7)
#define J9PORT_ERROR_STARTUP_TTY (J9PORT_ERROR_STARTUP_BASE -8)
#define J9PORT_ERROR_STARTUP_TTY_HANDLE (J9PORT_ERROR_STARTUP_BASE -9)
#define J9PORT_ERROR_STARTUP_TTY_CONSOLE (J9PORT_ERROR_STARTUP_BASE -10)
#define J9PORT_ERROR_STARTUP_MMAP (J9PORT_ERROR_STARTUP_BASE -11)
#define J9PORT_ERROR_STARTUP_IPCMUTEX (J9PORT_ERROR_STARTUP_BASE -12)
#define J9PORT_ERROR_STARTUP_NLS (J9PORT_ERROR_STARTUP_BASE -13)
#define J9PORT_ERROR_STARTUP_SOCK (J9PORT_ERROR_STARTUP_BASE -14)
#define J9PORT_ERROR_STARTUP_TIME (J9PORT_ERROR_STARTUP_BASE -15)
#define J9PORT_ERROR_STARTUP_GP (J9PORT_ERROR_STARTUP_BASE -16)
#define J9PORT_ERROR_STARTUP_EXIT (J9PORT_ERROR_STARTUP_BASE -17)
#define J9PORT_ERROR_STARTUP_SYSINFO (J9PORT_ERROR_STARTUP_BASE -18)
#define J9PORT_ERROR_STARTUP_SL (J9PORT_ERROR_STARTUP_BASE -19)
#define J9PORT_ERROR_STARTUP_STR (J9PORT_ERROR_STARTUP_BASE -20)
#define J9PORT_ERROR_STARTUP_SHSEM (J9PORT_ERROR_STARTUP_BASE -21)
#define J9PORT_ERROR_STARTUP_SHMEM (J9PORT_ERROR_STARTUP_BASE -22)
#define J9PORT_ERROR_STARTUP_ERROR (J9PORT_ERROR_STARTUP_BASE -23)
#define J9PORT_ERROR_STARTUP_SIGNAL (J9PORT_ERROR_STARTUP_BASE -24)
/** @} */

/**
 * @name Shared Semaphore Errors
 * Error codes for shared semaphore operations.
 *
 * @internal J9PORT_ERROR_SHSEM* range from at -150 to 159 to avoid overlap 
 * @{
 */
#define J9PORT_ERROR_SHSEM_BASE -150
#define J9PORT_ERROR_SHSEM_OPFAILED (J9PORT_ERROR_SHSEM_BASE)
#define J9PORT_ERROR_SHSEM_HANDLE_INVALID (J9PORT_ERROR_SHSEM_BASE-1)
#define J9PORT_ERROR_SHSEM_SEMSET_INVALID (J9PORT_ERROR_SHSEM_BASE-2)
#define J9PORT_ERROR_SHSEM_NOT_EXIST (J9PORT_ERROR_SHSEM_BASE-3)
#define J9PORT_ERROR_SHSEM_NOPERMISSION (J9PORT_ERROR_SHSEM_BASE-4)
#define J9PORT_ERROR_SHSEM_INVALID_INPUT	(J9PORT_ERROR_SHSEM_BASE-5)
#define J9PORT_ERROR_SHSEM_NOSPACE (J9PORT_ERROR_SHSEM_BASE-6)
#define J9PORT_ERROR_SHSEM_ALREADY_EXIST (J9PORT_ERROR_SHSEM_BASE-7)
#define J9PORT_ERROR_SHSEM_DATA_DIRECTORY_FAILED (J9PORT_ERROR_SHSEM_BASE-8)
#define J9PORT_ERROR_SHSEM_WAIT_FOR_CREATION_MUTEX_TIMEDOUT (J9PORT_ERROR_SHSEM_BASE-9)
/** @} */

/**
 * @name Shared Memory Errors
 * Error codes for shared memory semaphore operations.
 *
 * @internal J9PORT_ERROR_SHMEM* range from at -160 to -170 to avoid overlap 
 * @{
 */
#define J9PORT_ERROR_SHMEM_BASE -160
#define J9PORT_ERROR_SHMEM_OPFAILED (J9PORT_ERROR_SHMEM_BASE)
#define J9PORT_ERROR_SHMEM_HANDLE_INVALID (J9PORT_ERROR_SHMEM_BASE-1)
#define J9PORT_ERROR_SHMEM_NOT_EXIST (J9PORT_ERROR_SHMEM_BASE-2)
#define J9PORT_ERROR_SHMEM_NOPERMISSION (J9PORT_ERROR_SHMEM_BASE-3)
#define J9PORT_ERROR_SHMEM_INVALID_INPUT	(J9PORT_ERROR_SHMEM_BASE-4)
#define J9PORT_ERROR_SHMEM_NOSPACE (J9PORT_ERROR_SHMEM_BASE-5)
#define J9PORT_ERROR_SHMEM_ALREADY_EXIST (J9PORT_ERROR_SHMEM_BASE-6)
#define J9PORT_ERROR_SHMEM_TOOBIG (J9PORT_ERROR_SHMEM_BASE-7)
#define J9PORT_ERROR_SHMEM_ATTACH_FAILED (J9PORT_ERROR_SHMEM_BASE-8)
#define J9PORT_ERROR_SHMEM_DATA_DIRECTORY_FAILED (J9PORT_ERROR_SHMEM_BASE-9)
#define J9PORT_ERROR_SHMEM_WAIT_FOR_CREATION_MUTEX_TIMEDOUT (J9PORT_ERROR_SHMEM_BASE-10)

/** @} */

/* -171 to -199 available for use */

/**
 * @name Socket Errors
 * Error codes for socket operations
 *
 * @internal J9PORT_ERROR_SOCKET* range from -200 to -299 avoid overlap
 * @{
 */
#define J9PORT_ERROR_SOCKET_BASE -200
#define J9PORT_ERROR_SOCKET_BADSOCKET J9PORT_ERROR_SOCKET_BASE						/* generic error */
#define J9PORT_ERROR_SOCKET_NOTINITIALIZED J9PORT_ERROR_SOCKET_BASE-1					/* socket library uninitialized */
#define J9PORT_ERROR_SOCKET_BADAF J9PORT_ERROR_SOCKET_BASE-2								/* bad address family */
#define J9PORT_ERROR_SOCKET_BADPROTO J9PORT_ERROR_SOCKET_BASE-3						/* bad protocol */
#define J9PORT_ERROR_SOCKET_BADTYPE J9PORT_ERROR_SOCKET_BASE-4							/* bad type */
#define J9PORT_ERROR_SOCKET_SYSTEMBUSY J9PORT_ERROR_SOCKET_BASE-5					/* system busy handling requests */
#define J9PORT_ERROR_SOCKET_SYSTEMFULL J9PORT_ERROR_SOCKET_BASE-6					/* too many sockets */
#define J9PORT_ERROR_SOCKET_NOTCONNECTED J9PORT_ERROR_SOCKET_BASE-7				/* socket is not connected */
#define J9PORT_ERROR_SOCKET_INTERRUPTED	J9PORT_ERROR_SOCKET_BASE-8					/* the call was cancelled */
#define J9PORT_ERROR_SOCKET_TIMEOUT	J9PORT_ERROR_SOCKET_BASE-9							/* the operation timed out */
#define J9PORT_ERROR_SOCKET_CONNRESET J9PORT_ERROR_SOCKET_BASE-10					/* the connection was reset */
#define J9PORT_ERROR_SOCKET_WOULDBLOCK	 J9PORT_ERROR_SOCKET_BASE-11			/* the socket is marked as nonblocking operation would block */
#define J9PORT_ERROR_SOCKET_ADDRNOTAVAIL J9PORT_ERROR_SOCKET_BASE-12				/* address not available */
#define J9PORT_ERROR_SOCKET_ADDRINUSE J9PORT_ERROR_SOCKET_BASE-13					/* address already in use */
#define J9PORT_ERROR_SOCKET_NOTBOUND J9PORT_ERROR_SOCKET_BASE-14						/* the socket is not bound */
#define J9PORT_ERROR_SOCKET_UNKNOWNSOCKET J9PORT_ERROR_SOCKET_BASE-15		/* resolution of fileDescriptor to socket failed */
#define J9PORT_ERROR_SOCKET_INVALIDTIMEOUT J9PORT_ERROR_SOCKET_BASE-16			/* the specified timeout is invalid */
#define J9PORT_ERROR_SOCKET_FDSETFULL J9PORT_ERROR_SOCKET_BASE-17					/* Unable to create an FDSET */
#define J9PORT_ERROR_SOCKET_TIMEVALFULL J9PORT_ERROR_SOCKET_BASE-18					/* Unable to create a TIMEVAL */
#define J9PORT_ERROR_SOCKET_REMSOCKSHUTDOWN J9PORT_ERROR_SOCKET_BASE-19	/* The remote socket has shutdown gracefully */
#define J9PORT_ERROR_SOCKET_NOTLISTENING J9PORT_ERROR_SOCKET_BASE-20				/* listen() was not invoked prior to accept() */
#define J9PORT_ERROR_SOCKET_NOTSTREAMSOCK J9PORT_ERROR_SOCKET_BASE-21			/* The socket does not support connection-oriented service */
#define J9PORT_ERROR_SOCKET_ALREADYBOUND J9PORT_ERROR_SOCKET_BASE-22			/* The socket is already bound to an address */
#define J9PORT_ERROR_SOCKET_NBWITHLINGER J9PORT_ERROR_SOCKET_BASE-23				/* The socket is marked non-blocking & SO_LINGER is non-zero */
#define J9PORT_ERROR_SOCKET_ISCONNECTED J9PORT_ERROR_SOCKET_BASE-24				/* The socket is already connected */
#define J9PORT_ERROR_SOCKET_NOBUFFERS J9PORT_ERROR_SOCKET_BASE-25					/* No buffer space is available */
#define J9PORT_ERROR_SOCKET_HOSTNOTFOUND J9PORT_ERROR_SOCKET_BASE-26			/* Authoritative Answer Host not found */
#define J9PORT_ERROR_SOCKET_NODATA J9PORT_ERROR_SOCKET_BASE-27							/* Valid name, no data record of requested type */
#define J9PORT_ERROR_SOCKET_BOUNDORCONN J9PORT_ERROR_SOCKET_BASE-28				/* The socket has not been bound or is already connected */
#define J9PORT_ERROR_SOCKET_OPNOTSUPP J9PORT_ERROR_SOCKET_BASE-29					/* The socket does not support the operation */
#define J9PORT_ERROR_SOCKET_OPTUNSUPP J9PORT_ERROR_SOCKET_BASE-30					/* The socket option is not supported */
#define J9PORT_ERROR_SOCKET_OPTARGSINVALID J9PORT_ERROR_SOCKET_BASE-31			/* The socket option arguments are invalid */
#define J9PORT_ERROR_SOCKET_SOCKLEVELINVALID J9PORT_ERROR_SOCKET_BASE-32		/* The socket level is invalid */
#define J9PORT_ERROR_SOCKET_TIMEOUTFAILURE J9PORT_ERROR_SOCKET_BASE-33			
#define J9PORT_ERROR_SOCKET_SOCKADDRALLOCFAIL J9PORT_ERROR_SOCKET_BASE-34	/* Unable to allocate the sockaddr structure */
#define J9PORT_ERROR_SOCKET_FDSET_SIZEBAD J9PORT_ERROR_SOCKET_BASE-35				/* The calculated maximum size of the file descriptor set is bad */
#define J9PORT_ERROR_SOCKET_UNKNOWNFLAG J9PORT_ERROR_SOCKET_BASE-36				/* The flag is unknown */
#define J9PORT_ERROR_SOCKET_MSGSIZE J9PORT_ERROR_SOCKET_BASE-37						/* The datagram was too big to fit the specified buffer & was truncated. */
#define J9PORT_ERROR_SOCKET_NORECOVERY J9PORT_ERROR_SOCKET_BASE-38				/* The operation failed with no recovery possible */
#define J9PORT_ERROR_SOCKET_ARGSINVALID J9PORT_ERROR_SOCKET_BASE-39					/* The arguments are invalid */
#define J9PORT_ERROR_SOCKET_BADDESC J9PORT_ERROR_SOCKET_BASE-40						/* The socket argument is not a valid file descriptor */
#define J9PORT_ERROR_SOCKET_NOTSOCK J9PORT_ERROR_SOCKET_BASE-41						/* The socket argument is not a socket */
#define J9PORT_ERROR_SOCKET_HOSTENTALLOCFAIL J9PORT_ERROR_SOCKET_BASE-42		/* Unable to allocate the hostent structure */
#define J9PORT_ERROR_SOCKET_TIMEVALALLOCFAIL J9PORT_ERROR_SOCKET_BASE-43		/* Unable to allocate the timeval structure */
#define J9PORT_ERROR_SOCKET_LINGERALLOCFAIL J9PORT_ERROR_SOCKET_BASE-44			/* Unable to allocate the linger structure */
#define J9PORT_ERROR_SOCKET_IPMREQALLOCFAIL J9PORT_ERROR_SOCKET_BASE-45		 	/* Unable to allocate the ipmreq structure */
#define J9PORT_ERROR_SOCKET_FDSETALLOCFAIL J9PORT_ERROR_SOCKET_BASE-46 			/* Unable to allocate the fdset structure */
#define J9PORT_ERROR_SOCKET_OPFAILED J9PORT_ERROR_SOCKET_BASE-47
#define J9PORT_ERROR_SOCKET_VALUE_NULL J9PORT_ERROR_SOCKET_BASE-48 					/* The value indexed was NULL */
#define J9PORT_ERROR_SOCKET_CONNECTION_REFUSED	 J9PORT_ERROR_SOCKET_BASE-49	/* connection was refused */
#define J9PORT_ERROR_SOCKET_ENETUNREACH J9PORT_ERROR_SOCKET_BASE-50					/* network is not reachable */
#define J9PORT_ERROR_SOCKET_EACCES J9PORT_ERROR_SOCKET_BASE-51							/* permissions do not allow action on socket */


/* Palm OS6 uses a hybrid error reporting mechanism.  Need to be able to distinguish socket
 * errors from all other errors (yuck this is really awful).
 */
#define J9PORT_ERROR_SOCKET_FIRST_ERROR_NUMBER J9PORT_ERROR_SOCKET_BASE
#define J9PORT_ERROR_SOCKET_LAST_ERROR_NUMBER J9PORT_ERROR_SOCKET_VALUE_NULL /* Equals last used error code */


/**
 * @name File Errors 
 * Error codes for file operations.
 *
 * @internal J9PORT_ERROR_FILE* range from -300 to -349 avoid overlap
 * @{
 */
#define J9PORT_ERROR_FILE_BASE -300
#define J9PORT_ERROR_FILE_OPFAILED (J9PORT_ERROR_FILE_BASE)
#define J9PORT_ERROR_FILE_EOF (J9PORT_ERROR_FILE_BASE-1)
#define J9PORT_ERROR_FILE_NOPERMISSION (J9PORT_ERROR_FILE_BASE-2)
#define J9PORT_ERROR_FILE_NOTFOUND (J9PORT_ERROR_FILE_BASE-3)
#define J9PORT_ERROR_FILE_NAMETOOLONG (J9PORT_ERROR_FILE_BASE-4)
#define J9PORT_ERROR_FILE_DISKFULL (J9PORT_ERROR_FILE_BASE-5)
#define J9PORT_ERROR_FILE_EXIST (J9PORT_ERROR_FILE_BASE-6)
#define J9PORT_ERROR_FILE_SYSTEMFULL (J9PORT_ERROR_FILE_BASE-7)
#define J9PORT_ERROR_FILE_NOENT (J9PORT_ERROR_FILE_BASE-8)
#define J9PORT_ERROR_FILE_NOTDIR (J9PORT_ERROR_FILE_BASE-9)
#define J9PORT_ERROR_FILE_LOOP (J9PORT_ERROR_FILE_BASE-10)
#define J9PORT_ERROR_FILE_BADF (J9PORT_ERROR_FILE_BASE-11)
#define J9PORT_ERROR_FILE_WOULDBLOCK (J9PORT_ERROR_FILE_BASE-12)
#define J9PORT_ERROR_FILE_INVAL (J9PORT_ERROR_FILE_BASE-13)
/** @} */

#endif     /* j9porterror_h */

