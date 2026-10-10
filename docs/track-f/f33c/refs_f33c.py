# F33c (HPP-744): references <commit>:<path>:<line> of docs/track-f/f33c.md and f33c/f33c_s0.md (rule 24(1)); form of
# F33a refs_f33a.py, the list is taken from the two texts by a regex (a range ':a'-':b' is checked at its first line).
#   python refs_f33c.py freeze  - writes refs_f33c.tsv: commit, path, line, anchor (line), anchor+1 (next line)
#   python refs_f33c.py         - checks: every line equals its anchor and the next line its +1 anchor; negative control -
#                                 every reference shifted by +1 must FAIL (per reference). Last line ALL OK / NOT OK.
import csv
import os
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "refs_f33c.tsv")
TEXTS = [os.path.join(HERE, "..", "f33c.md"), os.path.join(HERE, "f33c_s0.md")]
RX = re.compile(r"\b([0-9a-f]{8}):((?:src|tests|docs)/[A-Za-z0-9_./-]+):(\d+)")


def refs():
    seen = []
    for t in TEXTS:
        for m in RX.finditer(open(t, encoding="utf-8").read()):
            k = (m.group(1), m.group(2), int(m.group(3)))
            if k not in seen:
                seen.append(k)
    return seen


def lines(c, p):
    out = subprocess.run([G, "-C", REPO, "show", "%s:%s" % (c, p)], capture_output=True, check=True).stdout
    return out.decode("utf-8").replace("\r\n", "\n").split("\n")


if len(sys.argv) > 1 and sys.argv[1] == "freeze":
    with open(TSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        for c, p, n in refs():
            ls = lines(c, p)
            w.writerow([c, p, n, ls[n - 1].strip(), ls[n].strip()])
    print("frozen", len(refs()))
    sys.exit(0)

rows = list(csv.reader(open(TSV, encoding="utf-8"), delimiter="\t"))
ok = sorted((c, p, int(n)) for c, p, n, _, _ in rows) == sorted(refs())
if not ok:
    print("TSV does not match the references of the texts")
neg_failed = 0
good_n = 0
cache = {}
for c, p, n, a0, a1 in rows:
    n = int(n)
    ls = cache.setdefault((c, p), lines(c, p))
    good = n < len(ls) and ls[n - 1].strip() == a0 and ls[n].strip() == a1
    shifted = n + 1 < len(ls) and ls[n].strip() == a0 and ls[n + 1].strip() == a1
    neg_failed += 0 if shifted else 1
    good_n += 1 if good else 0
    print("%s %s:%s:%d | %s" % ("ok  " if good else "BAD ", c, p, n, a0[:90]))
    ok &= good
print("REFS %d, anchor %d of %d, +1 control NOT OK %d of %d" % (len(rows), good_n, len(rows), neg_failed, len(rows)))
print("ALL OK" if ok and neg_failed == len(rows) else "NOT OK")
sys.exit(0 if ok and neg_failed == len(rows) else 1)
