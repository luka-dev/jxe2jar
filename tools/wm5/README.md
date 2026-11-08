# tools/wm5 - run the real `jar2jxe.exe` from the Mac, unattended

`jar2jxe.exe` is a **Windows CE ARM** binary (`j9jar2jxe23.dll` -> `j9bcutil_createRomClass`),
so it only runs inside the Windows Mobile 5 Device Emulator, which only runs on 32-bit Windows.
This directory turns the existing XP VM (`vms/xp/`) into a headless job runner:

```
Mac                       XP VM (QEMU, headless)             WM5 emulator (inside XP)
host.py  --HTTP 8790-->   agent.vbs (polls 10.0.2.2)  --C:\WM5 = \Storage Card-->  autorun.exe
  jobs/<id>/job.txt         cmd.exe runs the command         runs jobs\*.cmd, writes .done
  <- outputs, stdout.txt    PUTs results back
```

Three layers, each tiny and stateless:

| piece | runs where | what it is |
|---|---|---|
| `host.py` | Mac | job server + CLI (`run`, `setup`, `emu`, `jar2jxe`, `serve`) |
| `vm.sh`, `qmp.py` | Mac | boot the XP disk with plain QEMU (`-display none`, QMP socket), send keys, screenshots |
| `agent.vbs` | XP, at logon | polls the job server, runs `cmd.exe` jobs, uploads outputs. WSH + MSXML + ADO only |
| `bootstrap.vbs`, `autorun.inf`, `make_iso.sh` | CD | one-shot installer for the agent (XP AutoPlay or `Run -> D:\bootstrap.vbs`) |
| `autorun.c` -> `autorun.exe` | WM5 | `\Storage Card\2577\autorun.exe`: the OS starts it at boot; it loops over `jobs\*.cmd` (line 1 exe, line 2 args), runs them, writes `<name>.done` |

## Daily use

```sh
tools/wm5/vm.sh start                      # XP boots in ~4 min (TCG); agent starts at logon
python3 tools/wm5/host.py serve &          # job server (or let each `run` start its own)
python3 tools/wm5/host.py emu              # start the WM5 emulator (cold boot, several minutes)
python3 tools/wm5/host.py jar2jxe test/custom_edgecases/out/cases.jar out/cases.jxe --startup cases.Hello
python3 tools/wm5/host.py run 'dir C:\WM5\jobs'    # any cmd.exe line, --in/--out to move files
tools/wm5/vm.sh stop                       # ACPI shutdown
```

`jar2jxe` passes `-le -noverify -vmOption -jcl:foun11` (the `run.lnk` set that produced the
checked-in `cases.jxe`; this jar2jxe build rejects the `-noPrecompile`/`-noStripBytecode`
options recorded in `run.txt`) and brings back `out.jxe` + `.sym`. Nothing in the emulator needs to be saved: every boot re-runs
`autorun.exe` from the shared folder.

## One-time setup (already done on this VM)

1. `make_iso.sh` builds `bootstrap.iso` next to the disk image; `vm.sh` attaches it as XP's `D:`.
2. First boot: XP AutoPlay runs `bootstrap.vbs` (if it does not, `qmp.py keys meta_l-r`,
   `qmp.py text 'D:\bootstrap.vbs\n'`). It installs `C:\EMU\agent.vbs` and a Startup shortcut.
3. `host.py setup` copies `vms/xp/mount-fs/weme/*` and `autorun.exe` into `C:\WM5`.

To change the agent later: `host.py run "call update_agent.bat" --in tools/wm5/agent.vbs tools/wm5/update_agent.bat`
(installs the file and restarts the agent from a detached helper; the job itself reports -1
because the helper inherits its stdout handle - expected).

`autorun.exe` is built with CeGCC (no WinCE toolchain on macOS):

```sh
docker run --rm --platform linux/amd64 -v "$PWD/tools/wm5":/src paliantech/cegcc \
  sh -c 'cd /src && arm-mingw32ce-gcc -Os -Wall -o autorun.exe autorun.c -lcoredll'
```

## Why not UTM / Wine / QEMU-for-WM5

- Wine: no WinCE, no ARM. QEMU: no bootable WM5 image; the Device Emulator *is* the ARM
  emulator and is x86-Windows-only.
- UTM runs the same disk, but has no keyboard/screen API; `utmctl exec` needs the QEMU guest
  agent, which is not installed on XP. Plain QEMU + QMP gives both. Never run `vm.sh start`
  while UTM has the VM started (same qcow2).
- Inside XP, `start` would hand the emulator the job's redirected stdout handle and lock
  `stdout.txt`; `emu` launches it via `wmic process call create` instead.
