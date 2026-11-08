#!/usr/bin/env python3
"""Minimal QMP client for the headless XP VM (see vm.sh): type keys, take screenshots.

  python3 tools/wm5/qmp.py keys "meta_l-r"            # chord: keys joined by '-'
  python3 tools/wm5/qmp.py text 'D:\\bootstrap.vbs'    # ASCII text + optional Enter via "\n"
  python3 tools/wm5/qmp.py shot /tmp/x.png             # screendump (PPM -> PNG via sips)
  python3 tools/wm5/qmp.py cmd system_powerdown        # any argument-less QMP command
"""
import json
import pathlib
import socket
import subprocess
import sys
import time

SOCK = pathlib.Path(__file__).resolve().parents[2] / "vms/xp/qmp.sock"

QCODE = {c: c for c in "abcdefghijklmnopqrstuvwxyz0123456789"}
QCODE.update({
    " ": "spc", "\n": "ret", "\t": "tab", "-": "minus", "=": "equal", "[": "bracket_left",
    "]": "bracket_right", ";": "semicolon", "'": "apostrophe", "`": "grave_accent",
    "\\": "backslash", ",": "comma", ".": "dot", "/": "slash",
})
SHIFTED = {
    "A": "a", "B": "b", "C": "c", "D": "d", "E": "e", "F": "f", "G": "g", "H": "h", "I": "i",
    "J": "j", "K": "k", "L": "l", "M": "m", "N": "n", "O": "o", "P": "p", "Q": "q", "R": "r",
    "S": "s", "T": "t", "U": "u", "V": "v", "W": "w", "X": "x", "Y": "y", "Z": "z",
    "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9",
    ")": "0", "_": "minus", "+": "equal", "{": "bracket_left", "}": "bracket_right",
    ":": "semicolon", '"': "apostrophe", "~": "grave_accent", "|": "backslash", "<": "comma",
    ">": "dot", "?": "slash",
}


class QMP:
    def __init__(self, path=SOCK):
        self.s = socket.socket(socket.AF_UNIX)
        self.s.connect(str(path))
        self.f = self.s.makefile("rwb", buffering=0)
        self._recv()  # greeting
        self.cmd("qmp_capabilities")

    def _recv(self):
        while True:
            line = self.f.readline()
            if not line:
                raise ConnectionError("qmp closed")
            msg = json.loads(line)
            if "event" in msg:
                continue
            return msg

    def cmd(self, name, **args):
        self.f.write((json.dumps({"execute": name, "arguments": args}) + "\n").encode())
        msg = self._recv()
        if "error" in msg:
            raise RuntimeError(msg["error"])
        return msg.get("return")

    def keys(self, chord, hold_ms=60):
        self.cmd("send-key", keys=[{"type": "qcode", "data": k} for k in chord.split("-")],
                 **{"hold-time": hold_ms})
        time.sleep(0.12)

    def text(self, s):
        for ch in s:
            if ch in SHIFTED:
                self.keys("shift-" + SHIFTED[ch])
            else:
                self.keys(QCODE[ch])

    def shot(self, png):
        ppm = str(png) + ".ppm"
        self.cmd("screendump", filename=ppm)
        subprocess.run(["sips", "-s", "format", "png", ppm, "--out", str(png)],
                       check=True, capture_output=True)
        pathlib.Path(ppm).unlink()


def _main():
    q = QMP()
    what, arg = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
    if what == "keys":
        q.keys(arg)
    elif what == "text":
        q.text(arg.replace("\\n", "\n"))
    elif what == "shot":
        q.shot(arg)
    elif what == "cmd":
        print(q.cmd(arg))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    _main()
