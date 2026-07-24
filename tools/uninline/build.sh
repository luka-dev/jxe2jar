#!/bin/bash
# Build uninline.jar - a fat jar: our ASM recovery tools + the asm dependency.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
JH="$(/usr/libexec/java_home -v 17+ 2>/dev/null || true)"
JAVAC="${JH:+$JH/bin/}javac"; JAR="${JH:+$JH/bin/}jar"
CP="$DIR/lib/asm-9.7.jar:$DIR/lib/asm-tree-9.7.jar:$DIR/lib/asm-analysis-9.7.jar"
B="$DIR/.build"; rm -rf "$B"; mkdir -p "$B"
"$JAVAC" -cp "$CP" -d "$B" "$DIR"/src/*.java
for j in "$DIR"/lib/*.jar; do (cd "$B" && "$JAR" xf "$j"); done
rm -rf "$B"/META-INF
"$JAR" cf "$DIR/uninline.jar" -C "$B" .
rm -rf "$B"
echo "built $DIR/uninline.jar"
