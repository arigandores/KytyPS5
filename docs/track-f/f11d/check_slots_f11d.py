# F11d (HPP-466): the slot table DiagBvhPrograms of the diagnostics commit against the BVH program lists of
# F3b (bvhmap_f3b.out.txt) and F11a (t1scan_f11a.out.txt: the T1 subset), and the word layout of the tail
# (no overlap with LoopTrip*). Read-only; prints ALL OK.
import re
import subprocess
import sys

GIT = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
DIAG = "c01451b0"


def show(path, rev=DIAG):
    return subprocess.run([GIT, "-C", REPO, "show", "%s:%s" % (rev, path)], capture_output=True,
                          check=True).stdout.decode("utf-8")


ok = True
src = show("src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp")
m = re.search(r"DiagBvhPrograms \{(.*?)\};", src, re.S)
table = re.findall(r"0x([0-9a-f]{16})ull", m.group(1))
print("table entries", len(table), "sorted", table == sorted(table), "unique", len(set(table)) == len(table))
ok &= len(table) == 20 and table == sorted(table) and len(set(table)) == 20

f3b = open(REPO + "/docs/track-f/f3b/bvhmap_f3b.out.txt", encoding="utf-8", errors="replace").read()
f3b_set = set(re.findall(r"\b([0-9a-f]{16})\b", f3b))
bvh_f3b = sorted(h for h in f3b_set if h in set(table))
print("F3b bvhmap: table hashes found", len(bvh_f3b), "of 20")
ok &= len(bvh_f3b) == 20

md = show("docs/track-f/f3b.md", "HEAD")
sec = md[md.index("Программы (хэш как в логах)"):md.index("Таблица по каждой инструкции")]
f3b_md = sorted(set(re.findall(r"`([0-9a-f]{16})`", sec)))
print("F3b report list", len(f3b_md), "equal to table", f3b_md == table)
ok &= f3b_md == table

t1 = open(REPO + "/docs/track-f/f11a/t1scan_f11a.out.txt", encoding="utf-8").read()
line = [l for l in t1.splitlines() if l.startswith("T1 hashes among the BVH programs of all ELFs:")][0]
t1_set = re.findall(r"'([0-9a-f]{16})'", line)
print("F11a T1 BVH subset", len(t1_set), "all in table", set(t1_set) <= set(table))
ok &= len(t1_set) == 14 and set(t1_set) <= set(table)
print("slot of 380bb9d636390bae", table.index("380bb9d636390bae"))
ok &= table.index("380bb9d636390bae") == 4

hdr = show("src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h")
num = lambda name: int(re.search(r"inline constexpr uint32_t %s\s*=\s*(\d+)" % name, hdr).group(1))
loop_words = num("LoopTripWords")
base = 1 << 21
diag_words = num("DiagWords")
enum = dict((k, int(v)) for k, v in re.findall(r"\t(Diag\w+)\s*=\s*(\d+),", hdr))
print("enum", enum)
print("| words | bytes from the bitmap end | what |")
print("| %d..%d | %d..%d | LoopTrip* (0-2 counters, 8-15 slots) |" % (base, base + loop_words - 1, 0, 4 * loop_words - 1))
print("| %d..%d | %d..%d | diagnostic words 0..%d |" % (base + loop_words, base + loop_words + diag_words - 1,
                                                       4 * loop_words, 4 * (loop_words + diag_words) - 1, diag_words - 1))
used = set()
for name, first in enum.items():
    width = {"DiagT0": 8, "DiagBuckets": 12, "DiagLanes": 21}.get(name, 1)
    words = set(range(first, first + width))
    if used & words:
        print("OVERLAP", name)
        ok = False
    used |= words
print("diagnostic words used", len(used), "max", max(used), "< DiagWords", max(used) < diag_words)
ok &= max(used) < diag_words and min(used) >= 0
print("no overlap with LoopTrip*: diag word 0 = tail word", loop_words, "> LoopTrip last", loop_words - 1)
print("ALL OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
