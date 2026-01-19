/*
*       (c) Copyright IBM Corp. 1991, 2004 All Rights Reserved
*/

/*
 * File included for compatibility - jvmras.h
 * is recommended include in documentation
 * to enable jvmri intreface 
 */

#include "jvmri.h"

/*
 * ======================================================================
 *    RAS structure header
 * ======================================================================
 */
typedef struct RasDataHeader {
    char eyecatcher[4];
    int length;
    int version;
    int modification;
} RasDataHeader;



