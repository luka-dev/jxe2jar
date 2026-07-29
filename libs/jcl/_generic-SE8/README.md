# _generic-SE8 - full Java SE 8 rt.jar (fallback / non-firmware)

`rt.jar` -> symlink to the bundled Zulu JDK 8 (`jvms/zulu8.../jre/lib/rt.jar`), 19991 classes.

This is the GENERIC SE8 class library, NOT a firmware JCL. It is what `vineflower.sh` already
uses by default via `--include-runtime`. Use it as `VF_JCL` only when you have no firmware
context (a standalone jxe, or non-firmware Java):

    VF_JCL=libs/jcl/_generic-SE8/rt.jar bash tools/vineflower.sh out/final.jar out/final-vf

For real head-unit firmware prefer the per-firmware CDC JCL (../<FW>/jcl.jar) - SE8 is
over-permissive (has AWT/Swing/java.util.concurrent that the CDC firmware does NOT ship).
