"""Inline-annotate the DOUBTFUL constant resolutions in the decompiled source.

Instead of dumping a TSV nobody reads, we put the uncertainty right where it lives:
for each low-confidence resolution (RefineResolve reverted it to an honest literal),
add `/* ?? maybe Owner.FIELD */` next to that number in the .java. Confident
resolutions stay clean symbolic references with no noise. Only ~dozens of sites.

Input: doubtful.tsv  (class \t method \t value \t owner \t field \t action \t reason)
       - a machine intermediate, not a human file.

Usage: python3 tools/annotate_doubtful.py <src_dir> <doubtful.tsv> [--apply]
"""
import sys, os, re, csv
from collections import defaultdict

src_dir, tsv = sys.argv[1], sys.argv[2]
apply = "--apply" in sys.argv

byfile = defaultdict(list)                 # outer .java -> [(method, value, owner, field)]
with open(tsv) as f:
    r = csv.reader(f, delimiter="\t"); next(r, None)
    for row in r:
        if len(row) < 5: continue
        cls, method, value, owner, field = row[0], row[1], int(row[2]), row[3], row[4]
        byfile[cls.split("$")[0]].append((method, value, owner.split("/")[-1], field))

def forms(v):
    out = [str(v)]
    if v > 0: out += ["0x%X" % v, "0x%x" % v]
    elif v < 0: out += ["-0x%X" % -v, "-0x%x" % -v]
    return out

annotated = missed = 0
miss_list = []
for outer, items in byfile.items():
    path = os.path.join(src_dir, outer + ".java")
    if not os.path.exists(path):
        missed += len(items); miss_list += [f"{outer} (no file)"] * 0; continue
    text = open(path, encoding="utf-8", errors="replace").read()
    orig = text
    for method, value, owner, field in items:
        mi = re.search(r"\b" + re.escape(method) + r"\s*\(", text)
        start = mi.end() if mi else 0
        hit = False
        for form in forms(value):
            m = re.search(r"(?<![\w.$])" + re.escape(form) + r"(?![\w.xX])", text[start:])
            if not m: continue
            end = start + m.end()
            if text[end:end + 6].lstrip().startswith("/*"):     # already annotated
                hit = True; break
            text = text[:end] + f" /* ?? maybe {owner}.{field} */" + text[end:]
            annotated += 1; hit = True; break
        if not hit:
            missed += 1; miss_list.append(f"{outer}.{method} {value} -> {field}")
    if apply and text != orig:
        open(path, "w", encoding="utf-8").write(text)

print(f"{'annotated' if apply else 'would annotate'} {annotated} doubtful sites; missed {missed}")
for m in miss_list[:15]:
    print("  MISS", m)
