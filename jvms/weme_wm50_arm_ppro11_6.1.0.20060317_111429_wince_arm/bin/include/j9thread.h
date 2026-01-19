/*
 (c) Copyright IBM Corp. 1991, 2006 All Rights Reserved
 File generated in stream: 'GA 2.3'
*/

#ifndef J9THREAD_H
#define J9THREAD_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include "j9comp.h"

typedef UDATA j9thread_tls_key_t;

#define J9THREAD_PROC VMCALL

typedef int(J9THREAD_PROC* j9thread_entrypoint_t)(void*);
typedef void(J9THREAD_PROC* j9thread_tls_finalizer_t)(void*);

typedef struct J9Thread *j9thread_t;
typedef struct J9ThreadMonitor *j9thread_monitor_t;
typedef struct J9Semaphore *j9sem_t;

struct J9PortLibrary;

#define J9THREAD_PRIORITY_MIN  0
#define J9THREAD_PRIORITY_USER_MIN  1
#define J9THREAD_PRIORITY_NORMAL  5
#define J9THREAD_PRIORITY_USER_MAX  10
#if defined(J9VM_OPT_REAL_TIME_EXTENSIONS) && !defined(WIN32)
#define J9THREAD_PRIORITY_MAX 40
#else
#define J9THREAD_PRIORITY_MAX  11
#endif

#if defined(J9VM_OPT_REAL_TIME_LOCKING_SUPPORT) 
#define J9THREAD_LOCKING_PRIO_NONE	1	/* no policy  */
#define J9THREAD_LOCKING_PRIO_INHERIT	2	/* priority inheritance policy */
#define J9THREAD_LOCKING_PRIO_PROTECT	3	/* priority protection aka ceiling policy */
#define J9THREAD_LOCKING_DEFAULT	J9THREAD_LOCKING_PRIO_INHERIT	/* default locking policy for platform */ 
#else
#define J9THREAD_LOCKING_DEFAULT	0 /* default locking policy for platform */ 
#endif
#define J9THREAD_LOCKING_NO_DATA	(-1)	/* if no policy data is provided */

#define J9THREAD_FLAG_BLOCKED  1
#define J9THREAD_ALREADY_INITIALIZED  4
#define J9THREAD_TIMED_OUT  3
#define J9THREAD_FLAG_STARTED  0x800
#define J9THREAD_FLAG_JLM_HAS_BEEN_ENABLED  0x20000
#define J9THREAD_ILLEGAL_MONITOR_STATE  1
#define J9THREAD_FLAG_PRIORITY_INTERRUPTED  0x100
#define J9THREAD_FLAG_JLMHST_ENABLED  0x10000
#define J9THREAD_FLAG_JLM_ENABLED  0x4000
#define J9THREAD_FLAG_INTERRUPTED  4
#define J9THREAD_INVALID_ARGUMENT  7
#define J9THREAD_FLAG_DETACHED  0x80
#define J9THREAD_PRIORITY_INTERRUPTED  5
#define J9THREAD_FLAG_CANCELED  0x400
#define J9THREAD_FLAG_NOTIFIED  16
#define J9THREAD_FLAG_ATTACHED  0x200
#define J9THREAD_WOULD_BLOCK  8
#define J9THREAD_FLAG_DEAD  32
#define J9THREAD_FLAG_WAITING  2
#define J9THREAD_FLAG_PARKED  0x40000
#define J9THREAD_FLAG_UNPARKED  0x80000
#define J9THREAD_FLAG_INTERRUPTABLE  0x2000
#define J9THREAD_FLAG_TIMER_SET  0x100000
#define J9THREAD_FLAG_JLM_ENABLED_ALL  0x1C000
#define J9THREAD_INTERRUPTED  2
#define J9THREAD_FLAG_JLM_TIME_STAMPS_ENABLED  0x8000
#define J9THREAD_FLAG_BLOCKED_AFTER_WAIT  0x1000
#define J9THREAD_ALREADY_ATTACHED  6
#define J9THREAD_FLAG_SUSPENDED  8
#define J9THREAD_FLAG_SLEEPING  64

#define J9THREAD_MONITOR_INFLATED  0x10000
#define J9THREAD_MONITOR_INTERRUPTABLE  0x20000
#define J9THREAD_MONITOR_PRIORITY_INTERRUPTABLE  0x40000
#define J9THREAD_MONITOR_SYSTEM  0
#define J9THREAD_MONITOR_OBJECT  0x60000
#define J9THREAD_MONITOR_MUTEX_UNINITIALIZED  0x80000
#define J9THREAD_MONITOR_SUPPRESS_CONTENDED_EXIT  0x100000
#define J9THREAD_MONITOR_MUTEX_IN_USE  0x200000
#define J9THREAD_MONITOR_JLM_TIME_STAMP_INVALIDATOR  0x400000
#define J9THREAD_MONITOR_SPINLOCK_UNOWNED  0
#define J9THREAD_MONITOR_SPINLOCK_OWNED  1
#define J9THREAD_MONITOR_SPINLOCK_EXCEEDED  2

#define J9THREAD_LIB_FLAG_JLM_TIME_STAMPS_ENABLED  0x8000
#define J9THREAD_LIB_FLAG_JLMHST_ENABLED  0x10000
#define J9THREAD_LIB_FLAG_JLM_ENABLED  0x4000
#define J9THREAD_LIB_FLAG_JLM_ENABLED_ALL  0x1C000
#define J9THREAD_LIB_FLAG_JLM_HAS_BEEN_ENABLED  0x20000




typedef struct J9ThreadMonitorTracing {
    char* monitor_name;
    UDATA enter_count;
    UDATA slow_count;
    UDATA recursive_count;
    UDATA spin2_count;
    UDATA yield_count;
} J9ThreadMonitorTracing;

#define J9SIZEOF_J9ThreadMonitorTracing 24
extern J9_CFUNC void VMCALL
j9thread_detach PROTOTYPE((j9thread_t thread));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_notify PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_exit_using_threadId PROTOTYPE((j9thread_monitor_t monitor, j9thread_t threadId));
#if (defined(J9VM_THR_JLM)) /* priv. proto (autogen) */
extern J9_CFUNC UDATA VMCALL
j9thread_lib_set_flags PROTOTYPE((UDATA flags));
#endif /* J9VM_THR_JLM (autogen) */

extern J9_CFUNC IDATA VMCALL 
j9thread_tls_alloc PROTOTYPE((j9thread_tls_key_t* handle));
extern J9_CFUNC IDATA VMCALL 
j9thread_sleep_interruptable PROTOTYPE((I_64 millis, IDATA nanos));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_enter_using_threadId PROTOTYPE((j9thread_monitor_t monitor, j9thread_t threadId));
extern J9_CFUNC void  VMCALL 
j9thread_cancel PROTOTYPE((j9thread_t thread));
extern J9_CFUNC UDATA VMCALL
j9thread_clear_interrupted PROTOTYPE((void));
extern J9_CFUNC void VMCALL 
j9thread_lib_unlock PROTOTYPE((j9thread_t self));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_enter PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL
j9thread_monitor_notify_all PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL 
j9thread_attach PROTOTYPE((j9thread_t* handle));
#if (defined(J9VM_THR_JLM)) /* priv. proto (autogen) */
extern J9_CFUNC J9ThreadMonitorTracing* VMCALL 
j9thread_jlm_get_gc_lock_tracing PROTOTYPE(());
#endif /* J9VM_THR_JLM (autogen) */

extern J9_CFUNC UDATA VMCALL 
j9thread_priority_interrupted PROTOTYPE((j9thread_t thread));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_destroy PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL 
j9sem_post PROTOTYPE((j9sem_t s));
extern J9_CFUNC UDATA VMCALL 
j9thread_monitor_num_waiting PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC UDATA VMCALL
j9thread_interrupted PROTOTYPE((j9thread_t thread));
#if (defined(J9VM_THR_TRACING)) /* priv. proto (autogen) */
extern J9_CFUNC void VMCALL 
j9thread_reset_tracing PROTOTYPE((void));
#endif /* J9VM_THR_TRACING (autogen) */

#if (defined(J9VM_THR_TRACING)) /* priv. proto (autogen) */
extern J9_CFUNC void VMCALL 
j9thread_monitor_dump_trace PROTOTYPE((j9thread_monitor_t monitor));
#endif /* J9VM_THR_TRACING (autogen) */

extern J9_CFUNC void VMCALL 
j9thread_monitor_lock PROTOTYPE((j9thread_t self, j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL 
j9thread_park PROTOTYPE((I_64 millis, IDATA nanos));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_init_with_name PROTOTYPE((j9thread_monitor_t* handle, UDATA flags, char* name));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_try_enter PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC j9thread_t VMCALL j9thread_self PROTOTYPE((void));
extern J9_CFUNC IDATA VMCALL 
j9thread_tls_free PROTOTYPE((j9thread_tls_key_t key));
extern J9_CFUNC UDATA VMCALL
j9thread_clear_priority_interrupted PROTOTYPE((void));
extern J9_CFUNC void VMCALL 
j9thread_monitor_unlock PROTOTYPE((j9thread_t self, j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL 
j9sem_wait PROTOTYPE((j9sem_t s));
extern J9_CFUNC void VMCALL 
j9thread_yield PROTOTYPE((void));
extern J9_CFUNC void VMCALL 
j9thread_suspend PROTOTYPE((void));
extern J9_CFUNC void VMCALL 
j9thread_interrupt PROTOTYPE((j9thread_t thread));
extern J9_CFUNC IDATA VMCALL 
j9thread_tls_set PROTOTYPE((j9thread_t thread, j9thread_tls_key_t key, void* value));
extern J9_CFUNC IDATA VMCALL 
j9thread_create PROTOTYPE((j9thread_t* handle, UDATA stacksize, UDATA priority, UDATA suspend, j9thread_entrypoint_t entrypoint, void* entryarg));
extern J9_CFUNC IDATA VMCALL
j9sem_init PROTOTYPE((j9sem_t* sp, I_32 initValue));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_init_policy PROTOTYPE((j9thread_monitor_t* handle, UDATA flags, IDATA policy, IDATA policyData));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_wait PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL
j9sem_destroy PROTOTYPE((j9sem_t s));
extern J9_CFUNC UDATA VMCALL
j9thread_current_stack_free PROTOTYPE((void));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_wait_interruptable PROTOTYPE((j9thread_monitor_t monitor, I_64 millis, IDATA nanos));
#if (defined(J9VM_THR_TRACING)) /* priv. proto (autogen) */
extern J9_CFUNC void VMCALL 
j9thread_dump_trace PROTOTYPE((j9thread_t thread));
#endif /* J9VM_THR_TRACING (autogen) */

extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_try_enter_using_threadId PROTOTYPE((j9thread_monitor_t monitor, j9thread_t threadId));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_exit PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC IDATA VMCALL 
j9thread_set_priority PROTOTYPE((j9thread_t thread, UDATA priority));
extern J9_CFUNC void VMCALL 
j9thread_unpark PROTOTYPE((j9thread_t thread));
extern J9_CFUNC void VMCALL 
j9thread_lib_lock PROTOTYPE((j9thread_t self));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_init PROTOTYPE((j9thread_monitor_t* handle, UDATA flags));
extern J9_CFUNC IDATA VMCALL 
j9thread_sleep PROTOTYPE((I_64 millis));
#if (defined(J9VM_THR_TRACING)) /* priv. proto (autogen) */
extern J9_CFUNC void VMCALL 
j9thread_monitor_dump_all PROTOTYPE((void));
#endif /* J9VM_THR_TRACING (autogen) */

extern J9_CFUNC UDATA* VMCALL 
j9thread_global PROTOTYPE((char* name));
extern J9_CFUNC IDATA VMCALL 
j9thread_tls_alloc_with_finalizer PROTOTYPE((j9thread_tls_key_t* handle, j9thread_tls_finalizer_t finalizer));
extern J9_CFUNC IDATA VMCALL 
j9thread_monitor_wait_timed PROTOTYPE((j9thread_monitor_t monitor, I_64 millis, IDATA nanos));
#if (defined(J9VM_THR_JLM)) /* priv. proto (autogen) */
extern J9_CFUNC IDATA VMCALL 
j9thread_jlm_init PROTOTYPE((UDATA flags));
#endif /* J9VM_THR_JLM (autogen) */

extern J9_CFUNC void VMCALL
j9thread_resume PROTOTYPE((j9thread_t thread));
#if (defined(J9VM_THR_JLM)) /* priv. proto (autogen) */
extern J9_CFUNC UDATA VMCALL 
j9thread_lib_clear_flags PROTOTYPE((UDATA flags));
#endif /* J9VM_THR_JLM (autogen) */

extern J9_CFUNC void VMCALL 
j9thread_priority_interrupt PROTOTYPE((j9thread_t thread));
extern J9_CFUNC void VMCALL NORETURN 
j9thread_exit PROTOTYPE((j9thread_monitor_t monitor));
#if (defined(J9VM_THR_JLM)) /* priv. proto (autogen) */
extern J9_CFUNC UDATA VMCALL 
j9thread_lib_get_flags PROTOTYPE(());
#endif /* J9VM_THR_JLM (autogen) */

#if (defined(J9VM_THR_STACK_PROBES)) /* priv. proto (autogen) */
extern J9_CFUNC IDATA VMCALL
j9thread_probe PROTOTYPE((void));
#endif /* J9VM_THR_STACK_PROBES (autogen) */

#if (defined(J9VM_INTERP_VERBOSE))  || (defined(J9VM_PROF_PROFILING)) /* priv. proto (autogen) */
extern J9_CFUNC void VMCALL 
j9thread_enable_stack_usage PROTOTYPE((UDATA enable));
#endif /* J9VM_('INTERP_VERBOSE' 'PROF_PROFILING') (autogen) */

#if (defined(J9VM_PROF_PROFILING)) /* priv. proto (autogen) */
extern J9_CFUNC UDATA VMCALL 
j9thread_get_handle PROTOTYPE((j9thread_t thread));
#endif /* J9VM_PROF_PROFILING (autogen) */

#if (defined(J9VM_INTERP_VERBOSE))  || (defined(J9VM_PROF_PROFILING)) /* priv. proto (autogen) */
extern J9_CFUNC UDATA VMCALL 
j9thread_get_stack_usage PROTOTYPE((j9thread_t thread));
#endif /* J9VM_('INTERP_VERBOSE' 'PROF_PROFILING') (autogen) */

#if (defined(J9VM_PROF_PROFILING))  || (defined(J9VM_PROF_JVMPI)) /* priv. proto (autogen) */
extern J9_CFUNC I_64 VMCALL 
j9thread_get_cpu_time PROTOTYPE((j9thread_t thread));
#endif /* J9VM_('PROF_PROFILING' 'PROF_JVMPI') (autogen) */

#if (defined(J9VM_PROF_PROFILING)) /* priv. proto (autogen) */
extern J9_CFUNC UDATA VMCALL 
j9thread_get_stack_size PROTOTYPE((j9thread_t thread));
#endif /* J9VM_PROF_PROFILING (autogen) */

extern J9_CFUNC I_64 VMCALL 
j9thread_get_user_time PROTOTYPE((j9thread_t thread));
#if (defined(J9VM_PROF_PROFILING)) /* priv. proto (autogen) */
extern J9_CFUNC IDATA VMCALL j9thread_get_os_priority PROTOTYPE((j9thread_t thread, IDATA* policy, IDATA *priority));
#endif /* J9VM_PROF_PROFILING (autogen) */

extern J9_CFUNC UDATA VMCALL 
j9thread_get_flags PROTOTYPE((j9thread_t thread, j9thread_monitor_t* blocker));
extern J9_CFUNC j9thread_monitor_t VMCALL 
j9thread_monitor_walk_no_locking PROTOTYPE((j9thread_monitor_t monitor));
#if (defined(J9VM_THR_JLM)) /* priv. proto (autogen) */
extern J9_CFUNC J9ThreadMonitorTracing* VMCALL 
j9thread_monitor_get_tracing PROTOTYPE((j9thread_monitor_t monitor));
#endif /* J9VM_THR_JLM (autogen) */

extern J9_CFUNC UDATA VMCALL 
j9thread_get_priority PROTOTYPE((j9thread_t thread));
extern J9_CFUNC void* VMCALL
j9thread_tls_get PROTOTYPE((j9thread_t thread, j9thread_tls_key_t key));
extern J9_CFUNC char* VMCALL 
j9thread_monitor_get_name PROTOTYPE((j9thread_monitor_t monitor));
extern J9_CFUNC j9thread_monitor_t VMCALL 
j9thread_monitor_walk PROTOTYPE((j9thread_monitor_t monitor));

struct RWMutex;
typedef struct RWMutex* j9thread_rwmutex_t;
extern J9_CFUNC IDATA VMCALL
j9thread_rwmutex_enter_read PROTOTYPE((j9thread_rwmutex_t mutex));
extern J9_CFUNC IDATA VMCALL
j9thread_rwmutex_destroy PROTOTYPE((j9thread_rwmutex_t mutex));
extern J9_CFUNC IDATA VMCALL
j9thread_rwmutex_exit_read PROTOTYPE((j9thread_rwmutex_t mutex));
extern J9_CFUNC IDATA VMCALL
j9thread_rwmutex_exit_write PROTOTYPE((j9thread_rwmutex_t mutex));
extern J9_CFUNC IDATA VMCALL
j9thread_rwmutex_init PROTOTYPE((j9thread_rwmutex_t* handle, UDATA flags, const char* name));
extern J9_CFUNC IDATA VMCALL
j9thread_rwmutex_enter_write PROTOTYPE((j9thread_rwmutex_t mutex));

/* J9VMThreadHelpers*/
#ifndef _J9VMTHREADHELPERS_
#define _J9VMTHREADHELPERS_
extern J9_CFUNC UDATA  VMCALL current_stack_depth ();
extern J9_CFUNC void  VMCALL j9thread_monitor_unpin ( j9thread_monitor_t monitor, j9thread_t osThread);
extern J9_CFUNC void  VMCALL j9thread_monitor_pin ( j9thread_monitor_t monitor, j9thread_t osThread);
#endif /* _J9VMTHREADHELPERS_ */

/* J9VMThreadSpinlocks*/
#ifndef _J9VMTHREADSPINLOCKS_
#define _J9VMTHREADSPINLOCKS_
extern J9_CFUNC IDATA  VMCALL j9thread_spinlock_acquire (j9thread_t self, j9thread_monitor_t monitor);
extern J9_CFUNC UDATA  VMCALL j9thread_spinlock_swapState (j9thread_monitor_t monitor, UDATA newState);
#endif /* _J9VMTHREADSPINLOCKS_ */

#define j9thread_global_monitor() (*(j9thread_monitor_t*)j9thread_global("global_monitor"))

#ifdef J9VM_THR_SYSTEM_MONITOR_NAMES
#define j9thread_monitor_init(pMon,flags)  j9thread_monitor_init_with_name(pMon,flags, #pMon)
#else
#define j9thread_monitor_init_with_name(pMon,flags,pName)  j9thread_monitor_init(pMon,flags)
#endif

#define j9thread_monitor_set_name(pMon,pName) /* fn on death row */ 


#ifdef __cplusplus
}
#endif

#endif /* J9THREAD_H */
