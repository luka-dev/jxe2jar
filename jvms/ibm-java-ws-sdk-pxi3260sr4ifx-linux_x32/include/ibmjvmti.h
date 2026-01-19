/*******************************************************************************
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 * 
 * (c) Copyright IBM Corp. 1991, 2008 All Rights Reserved
 * 
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 *******************************************************************************/

#ifndef ibmjvmti_h
#define ibmjvmti_h

/* 
 *-----------------------------------------------------------------------------
 * This file defines structures, constants, enums and other
 * definitions which can be used with IBM Corporation's
 * JVMTI extensions. These extensions are available through
 * the JVMTI extension mechanism.
 * See GetExtensionEvents(), GetExtensionFunctions() and
 * SetExtensionEventCallback()
 *-----------------------------------------------------------------------------
 */


#include "jvmti.h"

/* 
 *-----------------------------------------------------------------------------
 * Extended JVMTI constants
 *-----------------------------------------------------------------------------
 */

#define COM_IBM_GET_POTENTIAL_EXTENDED_CAPABILITIES "com.ibm.GetPotentialExtendedCapabilities"
#define COM_IBM_ADD_EXTENDED_CAPABILITIES "com.ibm.AddExtendedCapabilities"
#define COM_IBM_RELINQUISH_EXTENDED_CAPABILITIES "com.ibm.RelinquishExtendedCapabilities"
#define COM_IBM_GET_EXTENDED_CAPABILITIES "com.ibm.GetExtendedCapabilities"

#define COM_IBM_COMPILING_START "com.ibm.CompilingStart"
#define COM_IBM_COMPILING_END "com.ibm.CompilingEnd"

#define COM_IBM_METHOD_ENTRY_EXTENDED       "com.ibm.MethodEntryExtended"
#define COM_IBM_METHOD_EXIT_NO_RC           "com.ibm.MethodExitNoRc"
#define COM_IBM_INSTRUMENTABLE_OBJECT_ALLOC "com.ibm.InstrumentableObjectAlloc"

#define COM_IBM_SET_VM_TRACE "com.ibm.SetVmTrace"
#define COM_IBM_SET_VM_DUMP "com.ibm.SetVmDump"
#define COM_IBM_RESET_VM_DUMP "com.ibm.ResetVmDump"

#define COM_IBM_SET_VM_JLM "com.ibm.SetVmJlm"
#define COM_IBM_SET_VM_JLM_DUMP "com.ibm.SetVmJlmDump"

#define COM_IBM_ALLOW_INLINING_WITH_METHOD_ENTER_EXIT "com.ibm.AllowMethodInliningWithMethodEnterExit"
#define COM_IBM_ALLOW_DIRECT_JNI_WITH_METHOD_ENTER_EXIT "com.ibm.AllowDirectJNIWithMethodEnterExit"
#define COM_IBM_SET_VM_AND_COMPILING_CONTROL_OPTIONS "com.ibm.SetVmAndCompilingControlOptions"
#define COM_IBM_SET_METHOD_SELECTIVE_ENTRY_EXIT_NOTIFY "com.ibm.jvmtiSetMethodSelectiveEntryExitNotification"
#define COM_IBM_SET_EXTENDED_EVENT_NOTIFICATION_MODE "com.ibm.jvmtiSetExtendedEventNotificationMode"

#define COM_IBM_TRIGGER_VM_DUMP "com.ibm.TriggerVmDump"
#define COM_IBM_VM_DUMP_START "com.ibm.VmDumpStart"
#define COM_IBM_VM_DUMP_END "com.ibm.VmDumpEnd"

#define COM_IBM_GET_OS_THREAD_ID "com.ibm.GetOSThreadID"

#define COM_IBM_SIGNAL_ASYNC_EVENT "com.ibm.SignalAsyncEvent"
#define COM_IBM_CANCEL_ASYNC_EVENT "com.ibm.CancelAsyncEvent"
#define COM_IBM_ASYNC_EVENT "com.ibm.AsyncEvent"

#define COM_IBM_GET_STACK_TRACE_EXTENDED "com.ibm.GetStackTraceExtended"
#define COM_IBM_GET_ALL_STACK_TRACES_EXTENDED "com.ibm.GetAllStackTracesExtended"
#define COM_IBM_GET_THREAD_LIST_STACK_TRACES_EXTENDED "com.ibm.GetThreadListStackTracesExtended"

/*
 *-----------------------------------------------------------------------------
 * Extended JVMTI enumerations
 *-----------------------------------------------------------------------------
 */
enum {
	COM_IBM_METHOD_ENTRY_EXTENDED_INTERPRETED = 0,
	COM_IBM_METHOD_ENTRY_EXTENDED_COMPILED = 1,
	COM_IBM_METHOD_ENTRY_EXTENDED_NATIVE = 2,
	COM_IBM_METHOD_ENTRY_EXTENDED_PARTIAL_IN_LINE = 3,
	COM_IBM_METHOD_ENTRY_EXTENDED_IN_LINE = 4
};

enum {
	COM_IBM_JLM_START = 0,
	COM_IBM_JLM_START_TIME_STAMP = 1,
	COM_IBM_JLM_STOP = 2,
	COM_IBM_JLM_STOP_TIME_STAMP = 3
};

enum {
	COM_IBM_ENABLE_SELECTIVE_METHOD_ENTRY_EXIT_NOTIFICATION = 0
};

enum {
	COM_IBM_STACK_FRAME_EXTENDED_NOT_JITTED = 0,
	COM_IBM_STACK_FRAME_EXTENDED_JITTED     = 1
};

/**
 * Bits used to select the type of data to be returned by the extended stack trace calls 
 */
enum {
	COM_IBM_GET_STACK_TRACE_PRUNE_UNREPORTED_METHODS	= 1,	/** Prunes methods for which method enter was not reported */
	COM_IBM_GET_STACK_TRACE_ENTRY_LOCAL_STORAGE			= 2,	/** Returns ELS pointers */
	COM_IBM_GET_STACK_TRACE_EXTRA_FRAME_INFO			= 4		/** Returns jitted vs non-jitted data */
};

/*
 *-----------------------------------------------------------------------------
 * Extended JVMTI function types
 *-----------------------------------------------------------------------------
 */

/*
 *-----------------------------------------------------------------------------
 * Extended JVMTI structure types
 *-----------------------------------------------------------------------------
 */

typedef struct jlm_dump {
	char * begin;
	char * end;
} jlm_dump;

/*  JLM dump format
 *
 *  All entries are in  packed big endian format
 *	u1	monitor type
 *
 *   	1	Java monitor
 *   		jobjectID	object
 *   		JNIEnv *	owner thread
 *  		u4    		entry count
 *  		u4    		# of threads waiting to enter
 *  		[JNIEnv *]*	threads waiting to enter
 *  		u4   		# of threads waiting to be notified
 *  		[JNIEnv *]*	threads waiting to be notified
 *
 *  	2	raw monitor
 *  		char *    	name
 *  		RawMonitor	raw monitor
 *  		JNIEnv * 	owner thread
 *  		u4    		entry count
 *  		u4   		# of threads waiting to enter
 *  		[JNIEnv *]*	threads waiting to enter
 *  		u4  		# of threads waiting to be notified
 *  		[JNIEnv *]*	threads waiting to be notified
 */

/**
 * struct jvmtiFrameInfoExtended
 * Has two additional fields, compared to struct jvmtiFrameInfo:
 * machinepc and type
 */  
typedef struct jvmtiFrameInfoExtended {
	jmethodID method;
	jlocation location;
	jlocation machinepc;
	jint      type;                 /*!< frame type can be not jitted or jitted */
	void    * nativeFrameAddress;   /*!< address of the native frame */
} jvmtiFrameInfoExtended;

/**
 * struct jvmtiStackInfoExtended
 * frame buffer is a pointer to jvmtiFrameInfoExtended,
 * whereas frame buffer is pointer to jvmtiFrameInfo 
 * in struct jvmtiStackInfo
 */  
typedef struct jvmtiStackInfoExtended {
	jthread thread;
	jint state;
	jvmtiFrameInfoExtended* frame_buffer;
	jint frame_count;
} jvmtiStackInfoExtended;

#endif     /* ibmjvmti_h */
