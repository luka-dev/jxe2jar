#!/bin/bash
# Bytecode constant/accessor recovery for J9-converted jars (see README.md).
DIR="$(cd "$(dirname "$0")" && pwd)"
JH="$(/usr/libexec/java_home -v 17+ 2>/dev/null || true)"; JAVA="${JH:+$JH/bin/}java"
JAR="$DIR/uninline.jar"; [ -f "$JAR" ] || { echo "build first: $DIR/build.sh"; exit 1; }
run(){ "$JAVA" -Xmx8g -cp "$JAR" "$@"; }
cmd="$1"; shift 2>/dev/null || true
case "$cmd" in
  uninline) run Uninliner    "$@" ;;   # <in.jar> <out.jar> [floor]  (T1/T2/T3a, all types)
  sink)     run SinkResolve  "$@" ;;   # <in.jar> <out.jar> [floor]  (T3b sink-domain, fixpoint)
  refine)   run RefineResolve "$@" ;;  # <in.jar> <out.jar> <doubtful.tsv>  (3-way QA)
  access)   run AccessInline "$@" ;;   # <in.jar> <out.jar>          (inline access$NNN)
  verify)   run VerifyResolve "$@" ;;  # <orig.jar> <uninlined.jar>  (0 value-mismatch)
  audit)    run TypeAudit    "$@" ;;   # <jar>                       (type-ambiguity audit)
  pipeline)                            # <base.jar> <out.jar> <doubtful.tsv> [floor]
    b="$1"; o="$2"; d="$3"; f="${4:-100}"; t="$(mktemp -d)"
    run Uninliner "$b" "$t/u.jar" "$f" && run SinkResolve "$t/u.jar" "$t/s.jar" "$f" \
      && run RefineResolve "$t/s.jar" "$t/r.jar" "$d" && run AccessInline "$t/r.jar" "$o"
    rc=$?; rm -rf "$t"; exit $rc ;;
  *) echo "usage: uninline.sh {uninline|sink|refine|access|verify|audit|pipeline} <args>"; exit 1 ;;
esac
