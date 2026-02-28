#!/usr/bin/env python3
"""
int2hex.py — Heuristic integer-to-hex converter for decompiled Java sources.

Scans .java files and replaces decimal integer literals with hex where the
hex representation is more readable/meaningful. Uses heuristic rules:

  1. Bitmask patterns  — single bit set (powers of 2), or few bits set
  2. All-ones masks    — 0xFF, 0xFFFF, 0xFFFFFFFF, etc.
  3. Byte-aligned      — values whose hex is "round" (trailing 00s)
  4. Nibble-clean      — values where most hex nibbles are 0 or F
  5. Color-like        — 0xAARRGGBB patterns (large values with alpha byte)
  6. Shift results     — values exactly 2^N or 2^N - 1
  7. Context hints     — variable/field names containing mask, flag, color, etc.

Does NOT convert:
  - Small numbers (-128..255) unless context strongly suggests hex
  - Numbers inside string literals or comments
  - Numbers that are clearly "human" values (100, 1000, 1024, etc.)
  - float/double/long literals (with f/d/L suffix)

Usage:
  python3 tools/int2hex.py <dir>                 # dry-run (report only)
  python3 tools/int2hex.py <dir> --apply          # rewrite files in-place
  python3 tools/int2hex.py <dir> --report out.csv # save CSV report
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Heuristic scoring
# ---------------------------------------------------------------------------

def popcount(n):
    """Count set bits."""
    return bin(n).count("1")

def is_power_of_2(n):
    return n > 0 and (n & (n - 1)) == 0

def trailing_zero_nibbles(n):
    """Count trailing 0-nibbles in hex (i.e. trailing zero bytes/halves)."""
    if n == 0:
        return 0
    count = 0
    while (n & 0xF) == 0:
        n >>= 4
        count += 1
    return count

def hex_display(n, neg=False):
    """Format n as a Java hex literal."""
    prefix = "-" if neg else ""
    return f"{prefix}0x{n:X}"

# Common "human" decimal numbers that should stay decimal
HUMAN_NUMBERS = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    20, 24, 25, 30, 32, 40, 48, 50, 60, 64, 72, 80, 90, 96,
    100, 120, 128, 150, 180, 200, 250, 255, 256,
    300, 360, 365, 400, 500, 512, 600, 700, 768, 800, 900,
    1000, 1024, 1080, 1200, 1500, 1920, 2000, 2048,
    3000, 3600, 4000, 4096, 5000, 6000, 7200, 8000, 8192,
    10000, 16384, 20000, 32768, 50000, 65535, 65536,
    100000, 1000000, 10000000, 100000000, 1000000000,
    # Common time/size
    86400, 3600000, 86400000,
}

# Context keywords in surrounding code that suggest hex usage
HEX_CONTEXT_KEYWORDS = re.compile(
    r'(?:mask|flag|[^.]bit[^m]|shift|hex|rgba?|argb|color|colour|alpha|opaque|'
    r'transparent|permission|modifier|type_mask|paint|'
    r'\b0x[0-9a-fA-F]|&\s+\d|~\s*\d|\|\s*\d)',  # nearby hex literal or bitwise ops
    re.IGNORECASE,
)


def score_as_hex(value, context_line=""):
    """
    Score how likely a decimal integer should be hex.
    Returns (score, reason) where score >= 1.0 means "convert".
    """
    if value in HUMAN_NUMBERS:
        return (0.0, "common_decimal")

    abs_val = abs(value)

    # Very small values — almost never hex
    if abs_val < 256:
        # Exception: exact bit patterns like 0x80 = 128 (already in HUMAN)
        if abs_val in (0x55, 0xAA, 0x7E, 0x7C):
            return (1.0, "known_byte_pattern")
        return (0.0, "too_small")

    score = 0.0
    reasons = []

    # --- Hard rules (high confidence) ---

    # Single bit set (power of 2, > 256)
    if is_power_of_2(abs_val) and abs_val > 256:
        score += 2.0
        reasons.append("power_of_2")

    # 2^N - 1 (all-ones mask)
    if is_power_of_2(abs_val + 1) and abs_val > 255:
        score += 2.0
        reasons.append("all_ones_mask")

    # Nibble-aligned: all hex nibbles are 0 or F
    hex_str = f"{abs_val:X}"
    if all(c in "0F" for c in hex_str) and len(hex_str) >= 3:
        score += 2.0
        reasons.append("nibble_mask")

    # Byte-aligned with trailing zero nibbles (e.g. 0xFF00, 0x10000)
    tz = trailing_zero_nibbles(abs_val)
    if tz >= 2 and abs_val >= 0x100:
        score += 1.0 + tz * 0.3
        reasons.append(f"trailing_{tz}_zero_nibbles")

    # --- Medium rules ---

    # Low popcount relative to magnitude (sparse bit pattern)
    bits_needed = abs_val.bit_length()
    pc = popcount(abs_val)
    if bits_needed >= 12 and pc <= 4:
        score += 1.5
        reasons.append(f"sparse_bits({pc}/{bits_needed})")
    elif bits_needed >= 16 and pc <= 6:
        score += 0.8
        reasons.append(f"somewhat_sparse({pc}/{bits_needed})")

    # High popcount relative to magnitude (dense mask like 0x3FFFFF)
    if bits_needed >= 12 and pc >= bits_needed - 2:
        score += 1.2
        reasons.append(f"dense_mask({pc}/{bits_needed})")

    # Large 32-bit values that look like ARGB colors (top byte non-zero)
    if 0x01000000 <= abs_val <= 0xFFFFFFFF:
        # Check if looks like color: top byte is 0xFF (opaque) or similar
        top_byte = (abs_val >> 24) & 0xFF
        if top_byte == 0xFF or top_byte == 0x80 or top_byte == 0x00:
            score += 0.5
            reasons.append("possible_color")

    # Hex representation is notably shorter or cleaner
    dec_len = len(str(abs_val))
    hex_len = len(hex_str) + 2  # "0x" prefix
    if dec_len - hex_len >= 3:
        score += 0.3
        reasons.append("hex_shorter")

    # Repeating nibble patterns (e.g. 0xAAAAAAAA, 0x55555555)
    # Only count for larger values (>= 5 nibbles) to avoid false positives
    # like 8224=0x2020 which could just be a normal number
    if len(hex_str) >= 5:
        nibble_set = set(hex_str)
        if len(nibble_set) <= 2:
            score += 1.0
            reasons.append("repeating_nibbles")

    # --- Context boost ---
    if HEX_CONTEXT_KEYWORDS.search(context_line):
        score += 0.8
        reasons.append("context_hint")

    # Values > 2^20 that aren't round decimal — probably hex
    if abs_val > (1 << 20) and abs_val not in HUMAN_NUMBERS:
        dec_str = str(abs_val)
        # Not a round decimal (doesn't end in multiple zeros)
        if not dec_str.endswith("000"):
            score += 0.5
            reasons.append("large_non_round_decimal")

    reason = "+".join(reasons) if reasons else "no_signal"
    return (score, reason)


# ---------------------------------------------------------------------------
# Java source scanning
# ---------------------------------------------------------------------------

# Match integer literals in Java source (decimal, not already hex/octal/binary)
# Negative sign is handled by looking for preceding minus.
# This carefully avoids:
#   - Hex literals (0x...)
#   - Octal (0[0-7]+)
#   - Binary (0b...)
#   - Float/double (contains . or ends with f/d/F/D)
#   - Long (ends with L/l)
#   - Inside strings or comments
INT_LITERAL_RE = re.compile(
    r'(?<![.\w])(-?)(\d{4,10})(?![.\w\dLlFfDd])'
)

def is_inside_string_or_comment(line, match_start):
    """Quick check if position is inside a string literal or comment."""
    # Check for line comment
    dslash = line.find("//")
    if dslash != -1 and match_start > dslash:
        return True

    # Simple string check: count unescaped quotes before position
    in_string = False
    in_char = False
    i = 0
    while i < match_start:
        c = line[i]
        if c == '\\' and (in_string or in_char):
            i += 2
            continue
        if c == '"' and not in_char:
            in_string = not in_string
        elif c == "'" and not in_string:
            in_char = not in_char
        i += 1
    return in_string or in_char


def scan_file(filepath, threshold=1.0):
    """
    Scan a .java file for integer literals that should be hex.
    Returns list of (line_no, col, old_text, new_text, score, reason).
    """
    results = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (IOError, OSError):
        return results

    for line_no, line in enumerate(lines, 1):
        # Skip import/package lines, Javadoc/block comments, HTML entities
        stripped = line.lstrip()
        if stripped.startswith("import ") or stripped.startswith("package "):
            continue
        if stripped.startswith("*") or stripped.startswith("/*"):
            continue
        if "&#" in line:
            continue

        for m in INT_LITERAL_RE.finditer(line):
            neg_sign = m.group(1)
            digits = m.group(2)

            # Skip if inside string or comment
            if is_inside_string_or_comment(line, m.start()):
                continue

            # Skip numbers with leading zeros (octal-like) unless just "0"
            if digits.startswith("0") and len(digits) > 1:
                continue

            try:
                val = int(digits)
            except ValueError:
                continue

            if neg_sign:
                val = -val

            score, reason = score_as_hex(val, line)

            if score >= threshold:
                abs_val = abs(val)
                hex_lit = hex_display(abs_val, neg=bool(neg_sign))
                old_text = f"{neg_sign}{digits}"
                results.append((line_no, m.start(), old_text, hex_lit, score, reason))

    return results


def apply_replacements(filepath, replacements):
    """Apply replacements to file. Replacements must be sorted by (line, col) desc."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Sort by line desc, then col desc so offsets don't shift
    for (line_no, col, old_text, new_text, _score, _reason) in sorted(
        replacements, key=lambda r: (r[0], r[1]), reverse=True
    ):
        idx = line_no - 1
        line = lines[idx]
        # Verify the old text is still there
        if line[col:col + len(old_text)] == old_text:
            lines[idx] = line[:col] + new_text + line[col + len(old_text):]

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Heuristic int→hex converter for decompiled Java sources"
    )
    parser.add_argument("dir", help="Directory of .java files to scan")
    parser.add_argument("--apply", action="store_true",
                        help="Rewrite files in-place (default: dry-run)")
    parser.add_argument("--threshold", type=float, default=2.0,
                        help="Minimum score to convert (default: 2.0)")
    parser.add_argument("--report", type=str, default=None,
                        help="Write CSV report to this path")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print every replacement")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    java_files = sorted(root.rglob("*.java"))
    print(f"Scanning {len(java_files)} .java files (threshold={args.threshold})...")

    total_replacements = 0
    files_modified = 0
    all_results = []

    for filepath in java_files:
        results = scan_file(str(filepath), threshold=args.threshold)
        if not results:
            continue

        files_modified += 1
        total_replacements += len(results)
        rel = filepath.relative_to(root)

        for (line_no, col, old, new, score, reason) in results:
            all_results.append((str(rel), line_no, col, old, new, score, reason))
            if args.verbose:
                print(f"  {rel}:{line_no}  {old} → {new}  ({score:.1f} {reason})")

        if args.apply:
            apply_replacements(str(filepath), results)

    # Summary
    print(f"\n{'Applied' if args.apply else 'Would apply'} "
          f"{total_replacements} replacements across {files_modified} files")

    # Show top reasons breakdown
    reason_counts = {}
    for (_, _, _, _, _, score, reason) in all_results:
        for r in reason.split("+"):
            reason_counts[r] = reason_counts.get(r, 0) + 1
    if reason_counts:
        print("\nReason breakdown:")
        for r, c in sorted(reason_counts.items(), key=lambda x: -x[1])[:15]:
            print(f"  {r:40s} {c}")

    # Show some examples
    if all_results and not args.verbose:
        print(f"\nSample conversions (showing first 20):")
        for (rel, line_no, col, old, new, score, reason) in all_results[:20]:
            print(f"  {rel}:{line_no}  {old:>15s} → {new:<15s}  ({score:.1f} {reason})")

    # CSV report
    if args.report:
        with open(args.report, "w", newline="") as csvf:
            w = csv.writer(csvf)
            w.writerow(["file", "line", "col", "decimal", "hex", "score", "reason"])
            for row in all_results:
                w.writerow(row)
        print(f"\nCSV report written to {args.report}")


if __name__ == "__main__":
    main()