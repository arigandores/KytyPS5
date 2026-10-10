# F33a (HPP-736): references <commit>:<path>:<line> of docs/track-f/f33a.md (rule 24(1)).
#   python refs_f33a.py freeze  - writes refs_f33a.tsv: commit, path, line, anchor (line), anchor+1 (next line), stripped
#   python refs_f33a.py         - checks: every line equals its anchor and the next line its +1 anchor; negative control -
#                                 every reference shifted by +1 must FAIL (per reference). Last line ALL OK / NOT OK.
import csv
import os
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "refs_f33a.tsv")
C = "ee9632be"
S = "5f48cc3e"
REFS = [
    (C, "src/graphics/presentation/window/window.cpp", 217),
    (C, "src/graphics/presentation/window/window.cpp", 219),
    (C, "src/emulator.cpp", 145),
    (C, "src/emulator.cpp", 147),
    (C, "src/emulator.cpp", 158),
    (C, "src/emulator.cpp", 159),
    (C, "src/emulator.cpp", 160),
    (C, "src/emulator.cpp", 161),
    (C, "src/emulator.cpp", 162),
    (C, "src/emulator.cpp", 163),
    (C, "src/emulator.cpp", 164),
    (C, "src/emulator.cpp", 165),
    (C, "src/emulator.cpp", 166),
    (C, "src/emulator.cpp", 167),
    (C, "src/emulator.cpp", 192),
    (C, "src/emulator.cpp", 198),
    (C, "src/emulator.cpp", 199),
    (C, "src/emulator.cpp", 228),
    (C, "src/emulator.cpp", 239),
    (C, "src/emulator.cpp", 243),
    (C, "src/common/subsystems.cpp", 5),
    (C, "src/common/subsystems.cpp", 7),
    (C, "src/common/subsystems.cpp", 8),
    (C, "src/common/subsystems.cpp", 28),
    (C, "src/common/subsystems.cpp", 29),
    (C, "src/common/subsystems.cpp", 34),
    (C, "src/common/subsystems.cpp", 37),
    (C, "src/common/subsystems.cpp", 39),
    (C, "src/common/subsystems.h", 56),
    (C, "src/common/assert.cpp", 22),
    (C, "src/common/assert.cpp", 24),
    (C, "src/common/assert.cpp", 25),
    (C, "src/common/assert.cpp", 38),
    (C, "src/common/assert.cpp", 116),
    (C, "src/common/assert.cpp", 118),
    (C, "src/common/assert.cpp", 120),
    (C, "src/common/assert.h", 50),
    (C, "src/common/assert.h", 54),
    (C, "src/common/logging/log.h", 19),
    (C, "src/common/logging/log.cpp", 114),
    (C, "src/common/logging/log.cpp", 698),
    (C, "src/common/logging/log.cpp", 707),
    (C, "src/common/logging/log.cpp", 775),
    (C, "src/common/logging/log.cpp", 786),
    (C, "src/common/profiler.cpp", 68),
    (C, "src/kernel/fileSystem.cpp", 409),
    (C, "src/kernel/fileSystem.cpp", 413),
    (C, "src/kernel/fileSystem.cpp", 264),
    (C, "src/kernel/fileSystem.cpp", 280),
    (C, "src/libs/libSaveData.cpp", 433),
    (C, "src/libs/libSaveData.cpp", 455),
    (C, "src/libs/libSaveData.cpp", 456),
    (C, "src/libs/controller.cpp", 228),
    (C, "src/libs/controller.cpp", 863),
    (C, "src/libs/controller.cpp", 865),
    (C, "src/libs/controller.cpp", 869),
    (C, "src/libs/controller.cpp", 1152),
    (S, "src/common/subsystems.cpp", 28),
    (S, "src/common/subsystems.h", 17),
    (S, "src/emulator.cpp", 41),
    (S, "src/emulator.cpp", 122),
    (S, "src/emulator.cpp", 183),
    (S, "src/emulator.cpp", 212),
    (S, "src/emulator.cpp", 347),
    (S, "src/emulator.cpp", 409),
    (S, "src/emulator.cpp", 434),
    (S, "src/emulator.cpp", 194),
]


def lines(c, p):
    out = subprocess.run([G, "-C", REPO, "show", "%s:%s" % (c, p)], capture_output=True, check=True).stdout
    return out.decode("utf-8").replace("\r\n", "\n").split("\n")


if len(sys.argv) > 1 and sys.argv[1] == "freeze":
    with open(TSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        for c, p, n in REFS:
            ls = lines(c, p)
            w.writerow([c, p, n, ls[n - 1].strip(), ls[n].strip()])
    print("frozen", len(REFS))
    sys.exit(0)

rows = list(csv.reader(open(TSV, encoding="utf-8"), delimiter="\t"))
ok = True
neg_failed = 0
cache = {}
for c, p, n, a0, a1 in rows:
    n = int(n)
    ls = cache.setdefault((c, p), lines(c, p))
    good = n < len(ls) and ls[n - 1].strip() == a0 and ls[n].strip() == a1
    shifted = n + 1 < len(ls) and ls[n].strip() == a0 and ls[n + 1].strip() == a1
    neg_failed += 0 if shifted else 1
    print("%s %s:%s:%d | %s" % ("ok  " if good else "BAD ", c, p, n, a0[:90]))
    ok &= good
print("REFS %d, anchor %d of %d, +1 control NOT OK %d of %d" % (len(rows), sum(1 for _ in rows) if ok else -1, len(rows),
                                                                 neg_failed, len(rows)))
print("ALL OK" if ok and neg_failed == len(rows) else "NOT OK")
sys.exit(0 if ok and neg_failed == len(rows) else 1)
