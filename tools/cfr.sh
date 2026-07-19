#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# CFR runs on any modern JVM. rt.jar / libs below are handed to CFR as extra
# classpath so it can resolve @Override and generics against the target's stdlib.
JAVA_BIN="${CFR_JAVA:-java}"

# Pick newest available cfr jar in tools/
CFR_JAR="$(ls -1 "$ROOT"/tools/cfr-*.jar 2>/dev/null | sort -V | tail -1)"
CFR_JAR="${CFR_JAR:-$ROOT/tools/cfr-0.152.jar}"
case "$(uname -s)" in
  Darwin)  JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-macosx_aarch64/zulu-8.jdk/Contents/Home" ;;
  Linux)   JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-linux_x64" ;;
  MINGW*|MSYS*|CYGWIN*) JDK8_HOME="$ROOT/jvms/zulu8.78.0.19-ca-jdk8.0.412-win_x64" ;;
  *) JDK8_HOME="${JDK8_HOME:-}" ;;
esac
RTJAR="$JDK8_HOME/jre/lib/rt.jar"

INPUT="${1:?Usage: cfr.sh <input.jar> [output_dir]}"
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
OUTDIR="${2:-${INPUT%.jar}-cfr}"

if [ ! -f "$CFR_JAR" ]; then
  echo "cfr jar not found: $CFR_JAR" >&2
  exit 1
fi

# Build --extraclasspath (rt.jar + libs/) so CFR can resolve external types.
CP=""
[ -f "$RTJAR" ] && CP="$RTJAR"
if [ -d "$ROOT/libs" ]; then
  for jar in "$ROOT"/libs/*.jar; do
    case "$jar" in *-javadoc.jar|*-sources.jar) continue;; esac
    [ -f "$jar" ] && CP="${CP:+$CP:}$jar"
  done
fi

args=(
  "$JAVA_BIN" -Xmx30g -jar "$CFR_JAR" "$INPUT"
  --outputdir "$OUTDIR"
  --silent true
  --comments true
  --showversion false
  --removeboilerplate true
  --removeinnerclasssynthetics true
  --decodelambdas true
  --decodefinally true
  --sugarasserts true
  --sugarenums true
  --sugarboxing true
  --decodeenumswitch true
  --decodestringswitch true
  --arrayiter true
  --collectioniter true
  --tryresources true
  --hidebridgemethods true
  --hidelangimports true
  --innerclasses true
  --removebadgenerics true
  --removedeadmethods true
  --relinkconst true
  --relinkconststring true
  --liftconstructorinit true
  --override true
  --renameillegalidents true
  --recover true
  --allowcorrecting true
  --tidymonitors true
  --labelledblocks true
  --usenametable true
  --eclipse true
)
[ -n "$CP" ] && args+=(--extraclasspath "$CP")

echo "Input:  $INPUT"
echo "Output: $OUTDIR"
"${args[@]}" 2>&1 | tee "$OUTDIR.log"
