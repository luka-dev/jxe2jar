/*
 * @(#)src/contract/awt/pfm/jawt_md.h, awt-peer-unix, audev, 20070112 1.14
 * ===========================================================================
 * Licensed Materials - Property of IBM
 * "Restricted Materials of IBM"
 *
 * IBM SDK, Java(tm) 2 Technology Edition, v5.0
 * (C) Copyright IBM Corp. 1998, 2005. All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or disclosure
 * restricted by GSA ADP Schedule Contract with IBM Corp.
 * ===========================================================================
 */

/*
 * ===========================================================================
 (C) Copyright Sun Microsystems Inc, 1992, 2004. All rights reserved.
 * ===========================================================================
 */

/* 
 *
 * Change activity:
 *
 * Reason  Date   Origin    Description
 * ------  ----   ------    -------------------------------------------------- 
 * 63757  050903 slattery  Add IBM module header; 
 * 83234  210305 rlee      Resolve _JNI_IMPORT_OR_EXPORT_ for Unix
 *
 * ===========================================================================
 * Module Information:
 * 
 * DESCRIPTION: IBM.WRITEME
 * ===========================================================================
 */

/*
 * @(#)jawt_md.h	1.10 03/01/23
 *
 */

#ifndef _JAVASOFT_JAWT_MD_H_
#define _JAVASOFT_JAWT_MD_H_

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Intrinsic.h>
#define _JNI_IMPORT_OR_EXPORT_
#include "jawt.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * X11-specific declarations for AWT native interface.
 * See notes in jawt.h for an example of use.
 */
typedef struct jawt_X11DrawingSurfaceInfo {
    Drawable drawable;
    Display* display;
    VisualID visualID;
    Colormap colormapID;
    int depth;
    /*
     * Since 1.4
     * Returns a pixel value from a set of RGB values.
     * This is useful for paletted color (256 color) modes.
     */
    int (JNICALL *GetAWTColor)(JAWT_DrawingSurface* ds,
        int r, int g, int b);
} JAWT_X11DrawingSurfaceInfo;

#ifdef __cplusplus
}
#endif

#endif /* !_JAVASOFT_JAWT_MD_H_ */
