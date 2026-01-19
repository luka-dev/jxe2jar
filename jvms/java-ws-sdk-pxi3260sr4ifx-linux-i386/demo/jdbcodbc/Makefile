#
# @(#)src/demo/jdbcodbc/Makefile, dsdev, dsdev, 20060202 1.5
# ===========================================================================
# IBM Confidential
# OCO Source Materials
#
# IBM SDK, Java(tm) 2 Technology Edition, v5.0
# (C) Copyright IBM Corp. 2004, 2005.
#
# The source code for this program is not published or otherwise divested of
# its trade secrets, irrespective of what has been deposited with the U.S.
# Copyright office.
#
# ===========================================================================
#
# Makefile example - please modify for your environment

# ------------------------------------------------------------------------------

# Name of library linked: libc.a and libodbc.a
LIBRARY = -lc -lodbc

# Path of Library linked
LIBRARY_PATH = /usr/lib

all:	odbctest

.c:
	xlc_r -I. -o $* -blibpath:$(LIBRARY_PATH) $(LIBRARY) $<

