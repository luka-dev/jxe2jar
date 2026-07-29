#!/bin/bash
# combine.sh - merge a converted lsd base jar with the firmware's OSGi bundles and
# app jars into ONE base jar, so the un-inliner sees the whole closure (cross-corpus
# constant recovery) and Vineflower resolves everything intra-jar (no --add-external
# for app code). Run BETWEEN jxe2jar and the un-inliner:
#
#   jxe2jar -> combine -> uninline -> vineflower
#
# The lsd base wins on class-name collisions (its romized version is the running one).
#
# Usage: combine.sh <lsd-base.jar> <out-merged.jar> <src>...
#   <src> = a .jar, a dir searched (recursively) for *.jar/*.zip, OR
#           --appimg <APPIMG> where APPIMG is the firmware app image root, always of the form
#           /Users/.../Firmwares/HU/<FW>/advanced/<MODEL>-appimg  (unpack or backup, same layout).
#           It auto-adds the standard eso sources: eso/bundles, eso/bundles_prod, eso/hmi/lsd/jars.
# Examples (MU1316):
#   tools/combine.sh out/MU1316-base.jar out/MU1316-combined.jar --appimg \
#     /Users/luka/Desktop/AUDI_2/Firmwares/HU/MU1316-MHI2Q_..._1811930398/advanced/MU1316-appimg
#   tools/combine.sh out/base.jar out/combined.jar "$APPIMG/eso/bundles" "$APPIMG/eso/hmi/lsd/jars"
set -e
[ $# -ge 3 ] || { echo "usage: combine.sh <lsd-base.jar> <out.jar> (<src-jar-or-dir> | --appimg <APPIMG>)..."; exit 1; }
BASE="$1"; OUT="$2"; shift 2

# expand any --appimg <dir> into the standard eso sources under it
srcs=()
while [ $# -gt 0 ]; do
  if [ "$1" = "--appimg" ]; then
    APP="$2"; shift 2
    [ -d "$APP" ] || { echo "  appimg not found: $APP" >&2; exit 1; }
    srcs+=("$APP/eso/bundles" "$APP/eso/bundles_prod" "$APP/eso/hmi/lsd/jars")
  else
    srcs+=("$1"); shift
  fi
done
set -- "${srcs[@]}"
# resolve to absolute paths (we cd into the staging dir to repack)
case "$BASE" in /*) : ;; *) BASE="$PWD/$BASE" ;; esac
case "$OUT"  in /*) : ;; *) OUT="$PWD/$OUT" ;; esac
STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT

# 1) lsd base first (it wins collisions via unzip -n below)
unzip -oq "$BASE" -d "$STAGE"

# 2) fold in every source jar/zip, never clobbering the lsd base (-n)
add=0
for src in "$@"; do
  if [ -f "$src" ]; then jars="$src"
  elif [ -d "$src" ]; then jars="$(find "$src" \( -name '*.jar' -o -name '*.zip' \) 2>/dev/null)"
  else echo "  skip (not found): $src"; continue; fi
  for j in $jars; do
    unzip -nq "$j" '*.class' -d "$STAGE" 2>/dev/null || true   # -n: never clobber the lsd base
    add=$((add+1))
  done
done
rm -rf "$STAGE/META-INF"

# 3) repack (OUT is absolute)
cls=$(find "$STAGE" -name '*.class' | wc -l | tr -d ' ')
( cd "$STAGE" && jar cf "$OUT" . )

echo "combined: $cls classes from base + $add source jars -> $OUT"
