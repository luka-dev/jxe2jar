#!/bin/sh
# Builds the one-shot bootstrap CD for the XP VM: XP AutoPlay runs bootstrap.vbs, which
# installs agent.vbs (see host.py). Output: vms/xp/Windows XP.utm/Data/bootstrap.iso
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../../vms/xp/Windows XP.utm/Data/bootstrap.iso"
TMP="$(mktemp -d)"
cp "$HERE/autorun.inf" "$HERE/bootstrap.vbs" "$HERE/agent.vbs" "$TMP/"
rm -f "$OUT"
hdiutil makehybrid -iso -joliet -default-volume-name WM5AGENT -o "$OUT" "$TMP" >/dev/null
rm -rf "$TMP"
echo "wrote $OUT"
