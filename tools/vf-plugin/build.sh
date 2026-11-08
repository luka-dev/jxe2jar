#!/bin/sh
# Builds tools/vf-lvt-first-renamer.jar (Vineflower plugin, needs a JDK 17+ javac).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
VF_JAR="$(ls -1 "$ROOT"/tools/vineflower-*.jar | grep -vE 'slim|sources|javadoc' | sort -V | tail -1)"
JAVAC="${JAVAC:-$(/usr/libexec/java_home -v 17+ 2>/dev/null)/bin/javac}"; JAR="$(dirname "$JAVAC")/jar"
rm -rf "$HERE/build" && mkdir -p "$HERE/build"
"$JAVAC" --release 17 -cp "$VF_JAR" -d "$HERE/build" $(find "$HERE/src" -name '*.java')
"$JAR" cf "$ROOT/tools/vf-lvt-first-renamer.jar" -C "$HERE/build" . -C "$HERE/src" META-INF
echo "built $ROOT/tools/vf-lvt-first-renamer.jar"
