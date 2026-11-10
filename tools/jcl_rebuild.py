#!/usr/bin/env python3
"""Rebuild a firmware JCL folder (libs/jcl/<FW>/) from a freshly converted combined jar.

core-lsd.jar keeps its class list (the use-subset the apps reference) but takes every class
from the combined jar, so converter fixes reach the compile classpath; jcl.jar is ext/*.jar
(device bytes, win on collision) + core-lsd.jar. The July 2026 jars were converted before
native methods kept their Exceptions attribute: Object.clone() without `throws` made javac
reject every clone catch and clone override.
"""

import glob
import sys
import zipfile


def main(combined, folder):
    core = folder + "/core-lsd.jar"
    names = [n for n in zipfile.ZipFile(core).namelist() if n.endswith(".class")]
    with zipfile.ZipFile(combined) as src, zipfile.ZipFile(core, "w", zipfile.ZIP_DEFLATED) as out:
        for name in names:
            out.writestr(name, src.read(name))
    seen = set()
    with zipfile.ZipFile(folder + "/jcl.jar", "w", zipfile.ZIP_DEFLATED) as out:
        for jar in sorted(glob.glob(folder + "/ext/*.jar")) + [core]:
            with zipfile.ZipFile(jar) as src:
                for name in src.namelist():
                    if name.endswith(".class") and name not in seen:
                        out.writestr(name, src.read(name))
                        seen.add(name)
    print("%s: core-lsd %d classes, jcl %d" % (folder, len(names), len(seen)))


if __name__ == "__main__":
    main(*sys.argv[1:3])
