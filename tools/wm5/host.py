#!/usr/bin/env python3
"""Run commands inside the Windows XP UTM VM (and, through it, the WM5 emulator) from the Mac.

The VM side is `agent.vbs` (installed once by the bootstrap CD, see make_iso.sh); it polls
this script's HTTP job server on the QEMU slirp host address 10.0.2.2:8790, so nothing
about the Mac's network matters. A job is a directory under vms/xp/jobs/<id>/ holding
`job.txt` (command, input list, output list) plus the inputs; the agent runs the command
with cmd.exe in C:\\\\EMU\\\\jobs\\\\<id>\\\\ and PUTs the outputs, stdout.txt and `done` back.

  python3 tools/wm5/host.py run "ver"                       # any cmd.exe command line
  python3 tools/wm5/host.py run "dir" --in a.jar --out b.txt
  python3 tools/wm5/host.py setup                           # once: weme + autorun.exe -> C:\\WM5
  python3 tools/wm5/host.py emu                             # start the WM5 emulator (idempotent)
  python3 tools/wm5/host.py jar2jxe in.jar out.jxe [--startup pkg.Main]
  python3 tools/wm5/host.py start | stop | status           # utmctl wrappers

WM5 side: the emulator's shared folder is C:\\WM5 (= \\Storage Card). autorun.exe there
(\\Storage Card\\2577\\autorun.exe, started by the OS at boot) runs every jobs\\*.cmd it finds:
line 1 = exe, line 2 = arguments, and writes <name>.done with the exit code.
"""
import argparse
import http.server
import pathlib
import shutil
import subprocess
import sys
import threading
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
JOBS = ROOT / "vms/xp/jobs"
WEME = ROOT / "vms/xp/mount-fs/weme"
UTMCTL = "/Applications/UTM.app/Contents/MacOS/utmctl"
VM = "Windows XP"
PORT = 8790
# Device Emulator install inside XP (Visual Studio 2005 + WM5 SDK R2); confirmed by `run dir`.
EMU_EXE = r"C:\Program Files\Microsoft Device Emulator\1.0\DeviceEmulator.exe"
EMU_SDK = r"C:\Program Files\Windows CE Tools\wce500\Windows Mobile 5.0 Pocket PC SDK\Deviceemulation"
EMU_IMAGE = EMU_SDK + r"\0409\PPC_USA.bin"
EMU_SKIN = EMU_SDK + r"\Pocket_pc\Pocket_PC.xml"
SHARE = r"C:\WM5"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_):  # quiet
        pass

    def _send(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/jobs/next":
            for job in sorted(JOBS.glob("*/job.txt")):
                claimed = job.parent / "claimed"
                if not claimed.exists():
                    claimed.touch()
                    return self._send(200, job.parent.name.encode())
            return self._send(200, b"")
        target = JOBS / path.removeprefix("/jobs/")
        if path.startswith("/jobs/") and target.is_file():
            return self._send(200, target.read_bytes())
        self._send(404)

    def do_PUT(self):
        path = self.path.split("?", 1)[0]
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        target = JOBS / path.removeprefix("/jobs/")
        if path.startswith("/jobs/") and target.parent.is_dir():
            target.write_bytes(body)
            return self._send(200)
        self._send(404)


def serve():
    """Start the job server in a thread; None if one already listens (then it is shared)."""
    try:
        server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    except OSError:
        return None
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def run(command, inputs=(), outputs=(), timeout=1800, keep=False):
    """Submit one job and wait. Returns (rc, stdout, job_dir)."""
    JOBS.mkdir(parents=True, exist_ok=True)
    job = JOBS / (time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6])
    job.mkdir()
    names = []
    for src in inputs:
        src = pathlib.Path(src)
        shutil.copy(src, job / src.name)
        names.append(src.name)
    (job / "job.txt").write_text(f"{command}\n{','.join(names)}\n{','.join(outputs)}\n")
    server = serve()
    try:
        deadline = time.time() + timeout
        while not (job / "done").exists():
            if time.time() > deadline:
                raise TimeoutError(f"job {job.name} not finished in {timeout}s (agent alive? VM running?)")
            time.sleep(1)
    finally:
        if server:
            server.shutdown()
    rc = (job / "done").read_text().strip()
    out = (job / "stdout.txt").read_text(errors="replace") if (job / "stdout.txt").exists() else ""
    return rc, out, job


def setup():
    """Push the WEME runtime (jar2jxe.exe + dlls) and autorun.exe into C:\\WM5 once."""
    files = sorted(WEME.iterdir()) + [ROOT / "tools/wm5/autorun.exe"]
    cmd = (f"mkdir {SHARE}\\weme {SHARE}\\2577 {SHARE}\\jobs 2>nul & "
           f"copy /y *.dll {SHARE}\\weme\\ & copy /y *.exe {SHARE}\\weme\\ & copy /y java.properties {SHARE}\\weme\\ & "
           f"copy /y autorun.exe {SHARE}\\2577\\ & dir /s /b {SHARE}")
    return run(cmd, files)


def emu(restart=False):
    """Start the WM5 emulator with C:\\WM5 as its storage card, unless it is already up.
    `restart` kills a running (or wedged) DeviceEmulator.exe first."""
    # `start` with its own nul redirections: a plain `start` would hand the emulator the
    # job's stdout.txt handle and keep that file locked for as long as the emulator runs
    # (wmic process call create mangles the quoted paths: "incorrect startup parameters").
    cmd = (f'tasklist /fi "imagename eq DeviceEmulator.exe" | find /i "DeviceEmulator.exe" && echo already running || '
           f'(start "" "{EMU_EXE}" "{EMU_IMAGE}" /skin "{EMU_SKIN}" /sharedfolder "{SHARE}" /memsize 128 '
           f'<nul >nul 2>&1 && echo started)')
    if restart:
        cmd = "taskkill /F /IM DeviceEmulator.exe & ping -n 3 127.0.0.1 >nul & " + cmd
    return run(cmd)


def jar2jxe(jar, out, startup=None, timeout=1800):
    """Romize one jar through the real jar2jxe.exe inside the WM5 emulator."""
    jar = pathlib.Path(jar)
    name = time.strftime("%H%M%S") + uuid.uuid4().hex[:4]
    # the option set from mount-fs/run.lnk (the one that produced cases.jxe); this DLL rejects
    # -noPrecompile/-noCompileAheadOfTime/-noStripBytecode ("not supported in this configuration")
    args = "-le -noverify -vmOption -jcl:foun11"
    if startup:
        args += f" -startupClass {startup}"
    args += f' -o "\\Storage Card\\jobs\\{name}.jxe" "\\Storage Card\\jobs\\{name}.jar"'
    # XP side (a .bat: labels/goto do not work on a cmd /c line): drop jar + .cmd into the
    # share, wait for autorun.exe's .done (bounded), bring the results back.
    bat = f"""@echo off
copy /y {jar.name} {SHARE}\\jobs\\{name}.jar >nul
(echo \\Storage Card\\weme\\jar2jxe.exe
echo {args}) > {SHARE}\\jobs\\{name}.cmd
set /a n=0
:w
if exist {SHARE}\\jobs\\{name}.done goto done
set /a n+=1
if %n% geq {max(60, timeout // 2)} (echo TIMEOUT waiting for autorun.exe & exit /b 2)
ping -n 3 127.0.0.1 >nul
goto w
:done
echo jar2jxe exit code: & type {SHARE}\\jobs\\{name}.done & echo.
copy /y {SHARE}\\jobs\\{name}.jxe out.jxe
copy /y {SHARE}\\jobs\\{name}.sym out.sym
del /q {SHARE}\\jobs\\{name}.*
"""
    JOBS.mkdir(parents=True, exist_ok=True)
    batfile = JOBS / f"wm5job-{name}.bat"
    batfile.write_text(bat.replace("\n", "\r\n"))
    try:
        rc, text, job = run(f"call {batfile.name}", [jar, batfile], ["out.jxe", "out.sym"], timeout)
    finally:
        batfile.unlink(missing_ok=True)
    if (job / "out.jxe").exists():
        shutil.copy(job / "out.jxe", out)
        if (job / "out.sym").exists():
            shutil.copy(job / "out.sym", str(out) + ".sym")
    return rc, text, job


def _main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a cmd.exe command line in the VM")
    r.add_argument("command")
    r.add_argument("--in", dest="inputs", nargs="*", default=[], help="files to copy into the job dir")
    r.add_argument("--out", dest="outputs", nargs="*", default=[], help="files to bring back")
    r.add_argument("--timeout", type=int, default=1800)
    sub.add_parser("serve", help="run the job server in the foreground (lets `run` calls share it)")
    sub.add_parser("setup")
    e = sub.add_parser("emu")
    e.add_argument("--restart", action="store_true", help="kill a running/wedged emulator first")
    j = sub.add_parser("jar2jxe")
    j.add_argument("jar")
    j.add_argument("out")
    j.add_argument("--startup", help="-startupClass for jar2jxe (e.g. cases.Hello)")
    j.add_argument("--timeout", type=int, default=1800)
    for name in ("start", "stop", "status", "suspend"):
        sub.add_parser(name)
    args = ap.parse_args()
    if args.cmd in ("start", "stop", "status", "suspend"):
        sys.exit(subprocess.call([UTMCTL, args.cmd, VM]))
    if args.cmd == "serve":
        JOBS.mkdir(parents=True, exist_ok=True)
        if serve() is None:
            sys.exit("port busy: a server is already running")
        print(f"serving {JOBS} on :{PORT}")
        while True:
            time.sleep(3600)
    if args.cmd == "run":
        rc, out, job = run(args.command, args.inputs, args.outputs, args.timeout)
    elif args.cmd == "setup":
        rc, out, job = setup()
    elif args.cmd == "emu":
        rc, out, job = emu(args.restart)
    else:
        rc, out, job = jar2jxe(args.jar, args.out, args.startup, args.timeout)
        if not pathlib.Path(args.out).exists():
            print("no jxe produced")
    sys.stdout.write(out)
    print(f"[rc={rc}] job {job}")
    for name in getattr(args, "outputs", []):
        if not (job / name).exists():
            print(f"  missing: {name}")


if __name__ == "__main__":
    _main()
