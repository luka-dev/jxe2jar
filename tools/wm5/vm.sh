#!/bin/sh
# vm.sh - run the Windows XP VM headless with plain QEMU (same disk as the UTM bundle), so
# keyboard/screen are scriptable over QMP (qmp.py) and nothing needs the UTM GUI.
# Never run this while UTM has the VM started: both would write the same qcow2.
#
#   tools/wm5/vm.sh start     # boots in the background; QMP at vms/xp/qmp.sock
#   tools/wm5/vm.sh stop      # ACPI power-off (XP shuts down cleanly)
#   tools/wm5/vm.sh status
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
XP="$ROOT/vms/xp"
DISK="$XP/Windows XP.utm/Data/disk-0.qcow2"
ISO="$XP/Windows XP.utm/Data/bootstrap.iso"
PID="$XP/qemu.pid"
SOCK="$XP/qmp.sock"

case "$1" in
  start)
    if [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null; then echo "already running"; exit 0; fi
    rm -f "$SOCK"
    # Same guest-visible hardware as the UTM config (IDE disk, rtl8139 NIC, PS/2), so XP does
    # not re-detect anything. Slirp user networking: the host is 10.0.2.2 for the agent.
    qemu-system-x86_64 -M pc -m 512 -rtc base=localtime \
      -drive "file=$DISK,if=ide,format=qcow2" \
      -drive "file=$ISO,if=ide,index=2,media=cdrom,readonly=on" \
      -device rtl8139,netdev=n0 -netdev user,id=n0 \
      -vga std -display none -daemonize -pidfile "$PID" \
      -qmp "unix:$SOCK,server,nowait"
    echo "started pid $(cat "$PID")"
    ;;
  stop)
    python3 "$ROOT/tools/wm5/qmp.py" cmd system_powerdown
    ;;
  status)
    if [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null; then echo running; else echo stopped; fi
    ;;
  *) echo "usage: $0 start|stop|status"; exit 2 ;;
esac
