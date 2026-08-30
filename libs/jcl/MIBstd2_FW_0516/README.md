# MIBstd2_FW_0516 - VW MIB std2 firmware JCL (COMPLETE core)

Unlike the Audi MHI2 folders (whose core-lsd is a reachable subset from lsd.jxe), this core is
the **complete** J9 2.3 CDC Foundation Profile 1.1 class library, taken as a plain jar from the
firmware build tree (build-v8/build/libs/jclFoundation11.jar, 973 classes, classfile v46 = 1.2).

- `core-jcl.jar` - complete jclFoundation11 (java.lang/util/io/net/..., com.ibm.oti.*). NOT a subset.
- `ext/j9jce.jar` - JCE crypto extension.
- `jcl.jar`       - merged. Point VF_JCL here for FW_0516 / MIBHMI / tsd.mibstd2.

Verified authentic (not JDK8): java.lang.Class has getName()+native getNameImpl() and NO
getSimpleName (a 1.5 API). Inspect with `javap -bootclasspath core-jcl.jar java.lang.Class`
(NOT `javap java.lang.Class`, which shows the JDK8 class from the bootclasspath).
