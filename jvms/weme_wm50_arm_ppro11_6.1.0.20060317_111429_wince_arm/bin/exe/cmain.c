/*
*	(c) Copyright IBM Corp. 1991, 2006 All Rights Reserved
*/

#include "j9comp.h"
#include "j9port.h"
#include "libhlp.h"

#if defined(J9ZOS390)
#include <stdlib.h> /* for malloc for atoe */
#include "atoe.h"
#endif

extern UDATA VMCALL gpProtectedMain(void *arg);

#ifdef J9VM_PORT_SIGNAL_SUPPORT
static UDATA VMCALL 
genericSignalHandler(struct J9PortLibrary* portLibrary, U_32 gpType, void* gpInfo, void* userData)
{
	PORT_ACCESS_FROM_PORT(portLibrary);
	U_32 category;

	j9tty_printf(PORTLIB, "\nAn unhandled error (%d) has occurred.\n", gpType);

	for (category=0 ; category<J9PORT_SIG_NUM_CATEGORIES ; category++) {
		U_32 infoCount = j9sig_info_count(gpInfo, category) ;
		U_32 infoKind, index;
		void *value;
		const char* name;

		for (index=0 ; index < infoCount ; index++) {
			infoKind = j9sig_info(gpInfo, category, index, &name, &value);

			switch (infoKind) {
				case J9PORT_SIG_VALUE_32:
					j9tty_printf(PORTLIB, "%s=%08.8x\n", name, *(U_32 *)value);
					break;
				case J9PORT_SIG_VALUE_64:
				case J9PORT_SIG_VALUE_FLOAT_64:
					j9tty_printf(PORTLIB, "%s=%016.16llx\n", name, *(U_64 *)value);
					break;
				case J9PORT_SIG_VALUE_STRING:
					j9tty_printf(PORTLIB, "%s=%s\n", name, (const char *)value);
					break;
				case J9PORT_SIG_VALUE_ADDRESS:
					j9tty_printf(PORTLIB, "%s=%p\n", name, *(void**)value);
					break;
			}
		}
	}

	abort();

	/* UNREACHABLE */
	return 0;
}

static UDATA VMCALL
signalProtectedMain(J9PortLibrary* portLibrary, void* arg)
{
	return gpProtectedMain(arg);
}
#endif

int 
main(int argc, char ** argv, char ** envp)
{
	J9PortLibrary j9portLibrary;
	J9PortLibraryVersion portLibraryVersion;
	struct j9cmdlineOptions options;
	int rc = 257;
#ifdef J9VM_PORT_SIGNAL_SUPPORT
	UDATA result;
#endif

#if defined(J9ZOS390)
	iconv_init();
	{  /* translate argv strings to ascii */
		int i;
		for (i = 0; i < argc; i++) {
			argv[i] = e2a_string(argv[i]);
		}
	}
#endif

	/* Use portlibrary version which we compiled against, and have allocated space
	 * for on the stack.  This version may be different from the one in the linked DLL.
	 */
	J9PORT_SET_VERSION(&portLibraryVersion, J9PORT_CAPABILITY_MASK);
	if (0 == j9port_init_library(&j9portLibrary, &portLibraryVersion, sizeof(J9PortLibrary))) {
		options.argc = argc;
		options.argv = argv;
		options.envp = envp;
		options.portLibrary = &j9portLibrary;

#ifdef J9VM_PORT_SIGNAL_SUPPORT
		if (j9portLibrary.sig_protect(&j9portLibrary, 
			signalProtectedMain, &options,
			genericSignalHandler, NULL,
			J9PORT_SIG_FLAG_SIGALLSYNC, 
			&result) == 0
		) {
			rc = result;
		}
#else
		rc = j9portLibrary.gp_protect(&j9portLibrary, gpProtectedMain, &options);
#endif

		j9portLibrary.port_shutdown_library(&j9portLibrary);
	}

	return rc;
}
