#!/usr/bin/env python3
"""
fix_class_literals.py - Collapse Java 1.2 class$ patterns back to Foo.class

Replaces the pre-Java 5 class literal pattern:
  (class$foo$bar == null ? (class$foo$bar = class$("foo.bar")) : class$foo$bar)
with:
  Foo.class

Also removes the synthetic field declarations and class$() method.

Handles variants from both CFR and Vineflower output:
  - CFR:  ClassName.class$("pkg.Name")
  - VF:   class$("pkg.Name")
  - Both: multi-line and single-line ternaries
  - Array class refs: array$Ljava$lang$Object  ->  Object[].class

Usage:
  python3 tools/fix_class_literals.py <dir>            # dry-run (report only)
  python3 tools/fix_class_literals.py <dir> --apply     # rewrite files in-place
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Match the full ternary with class$ or array$ fields.
# Variants (with or without outer parens, with or without ClassName. prefix on fields):
#   (class$pkg$Name == null ? (class$pkg$Name = class$("pkg.Name")) : class$pkg$Name)
#   (Foo.class$pkg$Name == null ? (Foo.class$pkg$Name = Foo.class$("pkg.Name")) : Foo.class$pkg$Name)
#   (array$Ljava$lang$Object == null ? (array$Ljava$lang$Object = class$("[Ljava.lang.Object;")) : array$Ljava$lang$Object)
#   Without outer parens in field initializers:
#     Foo.class$pkg$Name == null ? (Foo.class$pkg$Name = class$("pkg.Name")) : Foo.class$pkg$Name
# The core conditional (no surrounding parens). "%s" is where the FQN capture goes.
#   class$X == null ? (class$X = class$("fqn")) : class$X
_CORE = (
    r'(?:[\w$]+\s*\.\s*)?'              # optional ClassName. prefix on field ref
    r'(?:class|array)\$[\w$]+\s*==\s*null\s*'
    r'\?\s*\(\s*'
    r'(?:[\w$]+\s*\.\s*)?'              # optional ClassName. prefix on assignment
    r'(?:class|array)\$[\w$]+\s*=\s*'
    r'(?:[\w$]+\s*\.\s*)?'              # optional ClassName. prefix on class$() call
    r'class\$\(\s*"%s"\s*\)'            # class$("fqn") - FQN capture goes here
    r'\s*\)\s*'
    r':\s*(?:[\w$]+\s*\.\s*)?'          # optional ClassName. prefix on else branch
    r'(?:class|array)\$[\w$]+'
)
# Match ONLY the bare conditional, never any surrounding parentheses. Consuming a
# wrapping `(` ... `)` is unsafe: a lone ternary and one wrapping a call/keyword operand
# (`foo(TERNARY)`, `synchronized (TERNARY)`) are locally identical, so eating "its" parens
# eats the call's / statement's. Leaving a redundant `(Foo.class)` behind is valid Java;
# eating a required paren is not. group(1) = the FQN.
TERNARY_PATTERN = re.compile(_CORE % r'([^"]+)', re.DOTALL)

# Match synthetic fields: static Class class$pkg$Name; or static Class array$Ljava$...;
# Also matches with visibility modifiers or final
FIELD_PATTERN = re.compile(
    r'^\s+(?:(?:private|protected|public|static|final)\s+)*Class\s+(?:class|array)\$[\w$]+\s*;\s*\n',
    re.MULTILINE
)

# Match the synthetic class$() method - CFR style with /* synthetic */ comment
METHOD_PATTERN_CFR = re.compile(
    r'^\s+static\s+/\*\s*synthetic\s*\*/\s+Class\s+class\$\(String[^)]*\)\s*\{[^}]*?\}\s*\n',
    re.MULTILINE | re.DOTALL
)

# Match the synthetic class$() method - plain style (VF or CFR without synthetic comment)
# Uses a non-greedy match on the body, anchored by Class.forName or NoClassDefFoundError
METHOD_PATTERN_PLAIN = re.compile(
    r'^\s+static\s+Class\s+class\$\(String[^)]*\)\s*\{[^}]*?NoClassDefFoundError[^}]*?\}\s*\n',
    re.MULTILINE | re.DOTALL
)


def fqn_to_class_literal(fqn):
    """
    Convert a Class.forName argument to a .class literal.
      "de.audi.app.Foo"       -> "de.audi.app.Foo.class"
      "[Ljava.lang.Object;"   -> "Object[].class"
      "[[I"                   -> "int[][].class"
    """
    # Array types
    if fqn.startswith("["):
        dims = 0
        i = 0
        while i < len(fqn) and fqn[i] == '[':
            dims += 1
            i += 1
        suffix = "[]" * dims
        rest = fqn[i:]
        if rest.startswith("L") and rest.endswith(";"):
            # Object array: [Ljava.lang.Object;
            base = rest[1:-1]
            # Use simple name for java.lang types
            if "." in base:
                base = base.rsplit(".", 1)[1]
            return base + suffix + ".class"
        else:
            # Primitive array: [I, [D, etc.
            prim_map = {"I": "int", "J": "long", "D": "double", "F": "float",
                        "Z": "boolean", "B": "byte", "C": "char", "S": "short"}
            base = prim_map.get(rest, rest)
            return base + suffix + ".class"

    # Regular class
    return fqn + ".class"


def fix_file(filepath):
    """
    Fix class literal patterns in a single file.
    Returns (new_content, num_replacements) or (None, 0) if no changes.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (IOError, OSError):
        return None, 0

    if "class$" not in content:
        return None, 0

    count = 0

    # 1. Replace ternary patterns with Foo.class
    def replace_ternary(m):
        nonlocal count
        count += 1
        fqn = m.group(1)
        return fqn_to_class_literal(fqn)

    new_content = TERNARY_PATTERN.sub(replace_ternary, content)

    # 2. Remove synthetic class$/array$ fields
    if count > 0:
        new_content = FIELD_PATTERN.sub("", new_content)

        # 3. Remove synthetic class$() method
        new_content = METHOD_PATTERN_CFR.sub("", new_content)
        new_content = METHOD_PATTERN_PLAIN.sub("", new_content)

        # 4. Clean up resulting blank lines (collapse 3+ newlines to 2)
        new_content = re.sub(r'\n{3,}', '\n\n', new_content)

    if new_content == content:
        return None, 0

    return new_content, count


def main():
    parser = argparse.ArgumentParser(
        description="Collapse Java 1.2 class$ patterns to Foo.class"
    )
    parser.add_argument("dir", help="Directory of .java files to process")
    parser.add_argument("--apply", action="store_true",
                        help="Rewrite files in-place (default: dry-run)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print every replacement")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    java_files = sorted(root.rglob("*.java"))
    print(f"Scanning {len(java_files)} .java files...")

    total_replacements = 0
    files_modified = 0

    for filepath in java_files:
        new_content, count = fix_file(str(filepath))
        if new_content is None:
            continue

        files_modified += 1
        total_replacements += count
        rel = filepath.relative_to(root)

        if args.verbose:
            print(f"  {rel}: {count} class literal(s)")

        if args.apply:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

    action = "Fixed" if args.apply else "Would fix"
    print(f"\n{action} {total_replacements} class literal(s) across {files_modified} files")


if __name__ == "__main__":
    main()
