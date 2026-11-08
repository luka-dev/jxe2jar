#!/usr/bin/env python3
"""Repair the remaining non-compilable Vineflower source artifacts.

Synthetic anonymous-class captures are handled by jxe2jar.py preserving the ROM
field's ACC_SYNTHETIC flag. This script only handles independent decompiler
rendering errors that cannot be corrected by that classfile metadata.

Usage:
  python3 tools/fix_vf_artifacts.py <dir>            # dry-run (report only)
  python3 tools/fix_vf_artifacts.py <dir> --apply     # rewrite files in place
"""

import argparse
import os
import re


TOKEN = "<unrepresentable>"

# The `jad` variable renamer can turn a type into a reserved-word variable name,
# for example `Void void`. Restrict this to declaration/parameter positions.
_JAVA_KEYWORDS = (
    "abstract|assert|boolean|break|byte|case|catch|char|class|const|continue|default|do|"
    "double|else|enum|extends|final|finally|float|for|goto|if|implements|import|instanceof|"
    "int|interface|long|native|new|package|private|protected|public|return|short|static|"
    "strictfp|super|switch|synchronized|this|throw|throws|transient|try|void|volatile|while|"
    "true|false|null"
)
KEYWORD_PARAM = re.compile(
    r"\b([A-Z][A-Za-z0-9_$]*)\s+(" + _JAVA_KEYWORDS + r")\b(?=\s*[=;,)])"
)

DUP_INTERSECTION = re.compile(r"\(\s*([A-Za-z_$][\w$.]*)\s*&\s*\1\s*\)")

# A raw List.toArray(T[]) is typed Object[] even though its result has runtime
# type T[]. The explicit cast restores the assignability of the decompiled code.
# Any receiver (field chain, this.x, no-arg call chain) in any expression position, unless a cast
# already precedes it: `cond ? null : list.toArray(new T[0])`, `map.values().toArray(new T[0])`.
TOARRAY_CAST = re.compile(
    r"(?<![\w.$\]])(?<!\]\) )((?:[A-Za-z_$][\w$]*(?:\(\))?\.)*[A-Za-z_$][\w$]*(?:\(\))?)\.toArray\(\s*new\s+([\w.$]+)\["
)

# Vineflower writes `new ArrayList<>()` whenever it can see the element type (via the JDK
# runtime it resolves against), also in classfile-version 46-49 code; the diamond is Java 7
# syntax and fails every -source 1.5 check (126 occurrences in 19 MU1316 files). The raw
# constructor call compiles on 1.5 with at most an unchecked warning.
DIAMOND = re.compile(r"\bnew(\s+[A-Za-z_$][\w$.]*)<>\(")

# Old compiler class-literal helper calls can survive when Vineflower omits the
# helper definition. Accept only quoted Java binary names.
CLASS_DOLLAR_CALL = re.compile(
    r'(?<![\w.$])(?:[A-Za-z_$][\w$]*\.)?class\$\(\s*"([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)"\s*\)'
)
CLASS_DOLLAR_CACHE = re.compile(
    r"(?P<field>(?:[A-Za-z_$][\w$]*\.)?class\$[\w$]+)\s*==\s*null\s*"
    r"\?\s*\(\s*(?P=field)\s*=\s*(?P<literal>[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+\.class)\s*\)\s*"
    r":\s*(?P=field)"
)
# The same cache with the branches the other way round, as javac 1.1/1.2 (InstallShield, dom4j)
# compiled it: `f != null ? f : (f = X.class)`; Vineflower spreads it over several lines.
CLASS_DOLLAR_CACHE_NE = re.compile(
    r"(?P<field>(?:[A-Za-z_$][\w$]*\.)?class\$[\w$]+)\s*!=\s*null\s*\?\s*(?P=field)\s*:\s*"
    r"\(\s*(?P=field)\s*=\s*(?P<literal>[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+\.class)\s*\)"
)


def fix_dangling_outer_field(text):
    """Standalone Outer$N classes can lack a declared constructor-assigned this$0."""
    if not re.search(r"this\.this\$0\s*=", text) or re.search(r"\bthis\$0\s*;", text):
        return text, 0
    match = re.search(
        r"(class\s+[\w$]+\$\d+[^\{]*\{)\s*(?:\r?\n)(\s*[\w$]+\$\d+\(([\w.$]+)\s+[\w$]+\)\s*\{)",
        text,
    )
    if not match:
        return text, 0
    indent = re.match(r"\s*", match.group(2)).group()
    insert = f"\n{indent}private final {match.group(3)} this$0;\n"
    return text[:match.start(2)] + insert + text[match.start(2):], 1


def fix_navigation_param_alias(text):
    # Two RRD constructors refer to `navigationx` although the actual parameter
    # is named `navigation` in the same declaration.
    if "Navigation navigation" not in text or "Navigation navigationx" in text:
        return text, 0
    return re.subn(r"(this\.navigation\s*=\s*)navigationx;", r"\1navigation;", text)


def fix_class_dollar_literals(text):
    if re.search(r"\bClass\s+class\$\s*\(", text):
        return text, 0
    text, calls = CLASS_DOLLAR_CALL.subn(
        lambda match: match.group(1).replace("$", ".") + ".class", text
    )
    text, caches = CLASS_DOLLAR_CACHE.subn(lambda match: match.group("literal"), text)
    text, caches_ne = CLASS_DOLLAR_CACHE_NE.subn(lambda match: match.group("literal"), text)
    return text, calls + caches + caches_ne


def fix_text(text):
    n = text.count(TOKEN)
    text = text.replace(TOKEN, "Object")
    text, keywords = KEYWORD_PARAM.subn(lambda m: f"{m.group(1)} {m.group(2)}_", text)
    text, intersections = DUP_INTERSECTION.subn(r"(\1)", text)
    text, arrays = TOARRAY_CAST.subn(r"(\2[]) \1.toArray(new \2[", text)
    text, diamonds = DIAMOND.subn(r"new\1(", text)
    text, outers = fix_dangling_outer_field(text)
    text, params = fix_navigation_param_alias(text)
    text, literals = fix_class_dollar_literals(text)
    return text, n + keywords + intersections + arrays + diamonds + outers + params + literals


def main():
    parser = argparse.ArgumentParser(description="Fix Vineflower rendering artifacts.")
    parser.add_argument("dir")
    parser.add_argument("--apply", action="store_true", help="rewrite files in place")
    args = parser.parse_args()

    changed = hits = 0
    for directory, _, files in os.walk(args.dir):
        for name in files:
            if not name.endswith(".java"):
                continue
            path = os.path.join(directory, name)
            try:
                with open(path, encoding="utf-8", errors="replace") as source:
                    original = source.read()
            except OSError:
                continue
            repaired, count = fix_text(original)
            if repaired == original:
                continue
            hits += count
            changed += 1
            if args.apply:
                with open(path, "w", encoding="utf-8") as target:
                    target.write(repaired)

    action = "fixed" if args.apply else "would fix"
    print(f"{action} {hits} artifact(s) in {changed} file(s)")
    if not args.apply:
        print("dry-run - pass --apply to rewrite files")


if __name__ == "__main__":
    main()
