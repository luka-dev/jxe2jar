#!/bin/sh
set -e

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
JAVA_BIN="${VINEFLOWER_JAVA:-java}"
JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home"
RTJAR="$JDK8_HOME/jre/lib/rt.jar"

INPUT="${1:?Usage: vineflower.sh <input.jar> [output_dir]}"
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
OUTDIR="${2:-${INPUT%.jar}-vf}"

if [ ! -f "$RTJAR" ]; then
  echo "rt.jar not found: $RTJAR" >&2
  exit 1
fi

LIBS=""
if [ -d "$ROOT/libs" ]; then
  for jar in "$ROOT"/libs/*.jar; do
    [ -f "$jar" ] && LIBS="$LIBS -e $jar"
  done
fi

echo "Input:  $INPUT"
echo "Output: $OUTDIR"

exec "$JAVA_BIN" -Xmx30g -jar "$ROOT/tools/vineflower-1.11.2.jar" \
  --include-runtime "$JDK8_HOME" \
  -e "$RTJAR" \
  --ignore-invalid-bytecode \
  --old-try-dedup \
  --verify-merges \
  --warn-inconsistent-inner-attributes false \
  --variable-renaming tiny \
  --rename-parameters \
  $LIBS \
  "$INPUT" "$OUTDIR" \
  2>&1 | tee "$OUTDIR.log"
