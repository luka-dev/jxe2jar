#!/bin/sh
set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
JAVAC="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-linux_x64/bin/javac"
JAR="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-linux_x64/bin/jar"
SRC="$ROOT/test/custom_edgecases/src"
OUT_CLASSES="$ROOT/test/custom_edgecases/build/classes"
OUT_DIR="$ROOT/test/custom_edgecases/out"
OUT_JAR="$OUT_DIR/cases.jar"

mkdir -p "$OUT_CLASSES" "$OUT_DIR"

"$JAVAC" -source 1.2 -target 1.2 -d "$OUT_CLASSES" $(find "$SRC" -name '*.java')
"$JAR" cf "$OUT_JAR" -C "$OUT_CLASSES" .

echo "Wrote $OUT_JAR"
