/*
*	(c) Copyright IBM Corp. 1991, 2006 All Rights Reserved
*/

#include <windows.h>
#include <ctype.h>
#include "jni.h"
#include "j9port.h"
#include "libhlp.h"
#include "j9thread.h"

#if (_WIN32_WCE < 300)
#define isspace(c) (((c) == 0x20) || (((c) >= 0x9) && ((c) <= 0xd)))
#endif

/* external prototypes */
UDATA gpProtectedMain(void* arg);

static IDATA  (VMCALL *old_file_write) (struct J9PortLibrary *portLibrary, IDATA fd, const char * buf, IDATA nbytes) ;

typedef struct {
	LPWSTR lpCmdLine;
	J9PortLibrary *portLibrary;	
} threadOptions;

void freeUnicodeToASCII PROTOTYPE((J9PortLibrary *portLibrary, LPSTR path));
static I_32 VMCALL stub_tty_startup PROTOTYPE((struct J9PortLibrary *portLibrary));
void freeArgvCmdLine PROTOTYPE((J9PortLibrary *portLibrary, char **argv));
static int WINAPI j9vmThreadProc PROTOTYPE((threadOptions * opts));
char ** getArgvCmdLine PROTOTYPE((J9PortLibrary *portLibrary, LPWSTR buffer, int *finalArgc));
static void VMCALL stub_tty_shutdown PROTOTYPE((struct J9PortLibrary *portLibrary));
static IDATA VMCALL stub_tty_get_chars PROTOTYPE((struct J9PortLibrary *portLibrary, char * s, UDATA length));
static IDATA VMCALL stub_file_write PROTOTYPE((struct J9PortLibrary *portLibrary, IDATA fd, const char * buf, IDATA nbytes));
LPSTR makeUnicodeToASCII PROTOTYPE((J9PortLibrary *portLibrary, LPWSTR path));


#define QUOTE_CHAR '"'

static I_32 VMCALL
stub_tty_startup(struct J9PortLibrary *portLibrary)
{
	return 0;
}
static void VMCALL 
stub_tty_shutdown(struct J9PortLibrary *portLibrary)
{
}
static IDATA VMCALL stub_tty_get_chars(struct J9PortLibrary *portLibrary, char * s, UDATA length)
{
	return -1;
}
static IDATA VMCALL 
stub_file_write(struct J9PortLibrary *portLibrary, IDATA fd, const char * buf, IDATA nbytes)
{
	if (fd == J9PORT_TTY_OUT || fd == J9PORT_TTY_ERR) {
		/* throw it away */
		return nbytes;
	} else {
		return old_file_write(portLibrary, fd, buf, nbytes);
	}
}

/*
 *	Takes the command line (1 string) and breaks it into an
 *	argc, argv[] style list.
 *	Understands LFNs and strips quotes off the exe name.
 *	also converts the string to ASCII.
 */
void freeArgvCmdLine(J9PortLibrary *portLibrary, char **argv)
{
	PORT_ACCESS_FROM_PORT(portLibrary);

	j9mem_free_memory(argv[0]);
	j9mem_free_memory(argv);
}
/* This function converts a unicode string into a char array */
void freeUnicodeToASCII(J9PortLibrary *portLibrary, LPSTR path)
{
	PORT_ACCESS_FROM_PORT(portLibrary);

	j9mem_free_memory(path);
}
/*
 *	Takes the command line (1 string) and breaks it into an
 *	argc, argv[] style list.
 *	Understands LFNs and strips quotes off the exe name.
 *	also converts the string to ASCII.
 */
char **
getArgvCmdLine(J9PortLibrary *portLibrary, LPWSTR buffer, int *finalArgc)
{
	int argc = 0, currentArg = 1, i, asciiLen;
	char *asciiCmdLine;
	char **argv;
	PORT_ACCESS_FROM_PORT(portLibrary);

	asciiCmdLine = makeUnicodeToASCII(portLibrary, buffer);
	if (!asciiCmdLine) {
		return NULL;
	}

	/* determine an upper bound on the # of args by counting spaces and tabs */
	argc = 2; /* count the exe name (not found in arg array passed in)
							 and the NULL terminator */
	asciiLen = strlen(asciiCmdLine);
	for (i = 0; i <= asciiLen; i++) {
		if (isspace(asciiCmdLine[i]) || (asciiCmdLine[i] == '\0')) {
			argc += 1;
		}
	}

	/* allocate the buffer for the args */
	argv = j9mem_allocate_memory(argc * sizeof(char *));
	if (!argv) {
		freeUnicodeToASCII(portLibrary, asciiCmdLine);
		return NULL;
	}

	/* now fill in the argv array */
	if (0 != portLibrary->sysinfo_get_executable_name(portLibrary, "j9", &argv[0])) {
		freeUnicodeToASCII(portLibrary, asciiCmdLine);
		j9mem_free_memory(argv);
		return NULL;
	}

	if(QUOTE_CHAR == *asciiCmdLine) {	/* we have a quoted name. */
		argv[currentArg++] = ++asciiCmdLine;	/* move past the quote */
		while(QUOTE_CHAR != *asciiCmdLine) {
			asciiCmdLine++;
		}
		if (*asciiCmdLine) {
			*asciiCmdLine++ = '\0';	/* past close quote, slam the close quote and advance */
		}
	}

	/* Skip whitespace */
	while ((*asciiCmdLine != '\0') && isspace(*asciiCmdLine)) {
		asciiCmdLine++;
	}

	/* Split up args */
	while (*asciiCmdLine) {
		if(QUOTE_CHAR == *asciiCmdLine) {
			/* Parse a quoted arg */
			argv[currentArg++] = ++asciiCmdLine;
			while (*asciiCmdLine && *asciiCmdLine != QUOTE_CHAR) {
				asciiCmdLine++;
			}
		} else {
			/* Whitespace separated arg */
			argv[currentArg++] = asciiCmdLine;
			while ((*asciiCmdLine != '\0') && (!isspace(*asciiCmdLine))) {
				asciiCmdLine++;
			}
		}

		/* Null terminate */
		if (*asciiCmdLine) {
			*asciiCmdLine++ = '\0';
		}

		/* Skip whitespace */
		while ((*asciiCmdLine != '\0') && isspace(*asciiCmdLine)) {
			asciiCmdLine++;
		}
	}
	*finalArgc = currentArg;
	argv[currentArg] = NULL;
	return argv;
}
/* Helper function to run the vm gpProtectedMain on its own thread. */

static int WINAPI j9vmThreadProc(threadOptions * opts)
{
	int argc=0, rc;
	J9PortLibrary *j9portLibrary = opts->portLibrary;
	struct j9cmdlineOptions options;
	char **argv;

	argv = getArgvCmdLine(j9portLibrary, opts->lpCmdLine, &argc);
	if(!argv) {
		return -1;
	}

	options.argc = argc;
	options.argv = argv;
	options.envp = NULL;
	options.portLibrary = j9portLibrary;

	rc = j9portLibrary->gp_protect(j9portLibrary, gpProtectedMain, &options);

	freeArgvCmdLine(j9portLibrary, argv);

	j9portLibrary->exit_shutdown_and_exit(j9portLibrary, rc);

	return rc;
}

/* This function converts a unicode string into a char array */
LPSTR makeUnicodeToASCII(J9PortLibrary *portLibrary, LPWSTR path)
{
	PORT_ACCESS_FROM_PORT(portLibrary);
	int convSize;
	LPSTR asciiBuffer;

	convSize = WideCharToMultiByte(CP_ACP, WC_COMPOSITECHECK | WC_DISCARDNS, path, -1, NULL, 0, NULL, NULL);
	convSize += 1;
	asciiBuffer = j9mem_allocate_memory(convSize);
	if(!asciiBuffer)
		return NULL;
	WideCharToMultiByte(CP_ACP, WC_COMPOSITECHECK | WC_DISCARDNS, path, -1, asciiBuffer, convSize, NULL, NULL);
	return asciiBuffer;
}
int WINAPI WinMain(HINSTANCE hInstance, 	HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nShowCmd)
{
	j9thread_t javaThread;
	DWORD tempRc;
	threadOptions options;
	J9PortLibrary j9portLibrary;
	J9PortLibraryVersion portLibraryVersion;

	options.lpCmdLine = lpCmdLine;

	/* Create the port library and initialize the functions, but don't start up.
	 * Use portlibrary version which we compiled against, and have allocated space
	 * for on the stack.  This version may be different from the one in the linked DLL.
	 */
	J9PORT_SET_VERSION(&portLibraryVersion, J9PORT_CAPABILITY_MASK);
	tempRc = j9port_create_library(&j9portLibrary, &portLibraryVersion, sizeof(J9PortLibrary));
	if (0 != tempRc) {
		return -1;
	}
	
	/* Replace the console-based functions with stubs */
	old_file_write = j9portLibrary.file_write;
	j9portLibrary.tty_startup = stub_tty_startup;
	j9portLibrary.tty_shutdown = stub_tty_shutdown;
	j9portLibrary.file_write = stub_file_write;
	j9portLibrary.tty_get_chars = stub_tty_get_chars;

	/* Continue with the port library startup */
	tempRc = j9port_startup_library(&j9portLibrary);
	if (0 != tempRc) {
		return -1;
	}

	options.portLibrary = &j9portLibrary;

	j9thread_create(&javaThread, 
		0, 
		J9THREAD_PRIORITY_NORMAL,
		FALSE,
		j9vmThreadProc,
		&options
	);

	if (!javaThread)  {
		MessageBox(NULL, _T("j9thread_create failed"), NULL, MB_OK);
		return -1;
	}

	tempRc = j9portLibrary.exit_get_exit_code(&j9portLibrary);

	j9portLibrary.port_shutdown_library(&j9portLibrary);

	/*	Simply returning terminates the process, but doesn't seem to clean up windows properly. */
	ExitThread(tempRc);

	/* Unreachable code */
	return (int)tempRc; 
}
