#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Vineflower 1.12.0 is compiled for Java 17 (class 61); it must RUN on a JDK 17+.
# (rt.jar for --include-runtime stays JDK8 below, for decompiling the old target classes.)
if [ -n "$VINEFLOWER_JAVA" ]; then
  JAVA_BIN="$VINEFLOWER_JAVA"
elif [ -x /usr/libexec/java_home ] && J17="$(/usr/libexec/java_home -v 17+ 2>/dev/null)"; then
  JAVA_BIN="$J17/bin/java"
else
  JAVA_BIN="java"   # assume a 17+ java is on PATH
fi
# Pick newest available vineflower jar in tools/
VF_JAR="$(ls -1 "$ROOT"/tools/vineflower-*.jar 2>/dev/null | grep -vE 'slim|sources|javadoc' | sort -V | tail -1)"
VF_JAR="${VF_JAR:-$ROOT/tools/vineflower-1.12.0.jar}"
case "$(uname -s)" in
  Darwin)  JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home" ;;
  Linux)   JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-linux_x64" ;;
  MINGW*|MSYS*|CYGWIN*) JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-win_x64" ;;
  *) JDK8_HOME="${JDK8_HOME:?Unknown OS; set JDK8_HOME manually}" ;;
esac
RTJAR="$JDK8_HOME/jre/lib/rt.jar"

INPUT="${1:?Usage: vineflower.sh <input.jar> [output_dir]}"
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
OUTDIR="${2:-${INPUT%.jar}-vf}"

if [ ! -f "$RTJAR" ]; then
  echo "rt.jar not found: $RTJAR" >&2
  exit 1
fi

# All --flag=value options first
args=(
  "$JAVA_BIN" -Xmx30g -jar "$VF_JAR"
  --decompile-generics=true
  --decompile-enums=true
  --decompile-assert=true
  --decompile-finally=true
  --decompile-inner=true
  --decompile-java4=true
  --decompile-switch-expressions=true
  --remove-bridge=true
  --remove-synthetic=true
  --remove-empty-try-catch=true
  --remove-getclass=true
  --hide-default-constructor=true
  --hide-empty-super=true
  --override-annotation=true
  --inline-simple-lambdas=true
  --use-lvt-names=true
  --use-method-parameters=true
  --boolean-as-int=true
  --simplify-stack=true
  --incorporate-returns=true
  --pattern-matching=true
  --ternary-in-if=true
  --ensure-synchronized-monitors=true
  --ignore-invalid-bytecode=true
  --decompiler-comments=true
  --dump-bytecode-on-error=true
  --variable-renaming=jad
  --rename-parameters=true
  "--banner="
  "--indent-string=    "
  --preferred-line-length=120
  --thread-count=14
  --old-try-dedup
  --warn-inconsistent-inner-attributes=false
  "--include-runtime=$JDK8_HOME"
  "--add-external=$RTJAR"
)

# External libs
if [ -d "$ROOT/libs" ]; then
  for jar in "$ROOT"/libs/*.jar; do
    case "$jar" in *-javadoc.jar|*-sources.jar) continue;; esac
    [ -f "$jar" ] && args+=("--add-external=$jar")
  done
fi

# Input and output last
args+=("$INPUT" "$OUTDIR")

echo "Input:  $INPUT"
echo "Output: $OUTDIR"
"${args[@]}" 2>&1 | tee "$OUTDIR.log"
