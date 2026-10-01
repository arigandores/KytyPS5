# F3a (HPP-308): how many places in eboot.bin build a BVH descriptor base as BFE(addr, 8, 40)?
# S_BFE_U64 with the literal 0x00280008 (offset 8, width 40) = the word before the literal is a SOP2
# with src1 = 255 (literal). Counted next to the number of IMAGE_BVH_INTERSECT_RAY words (MIMG 0xe6).
import sys, os, re, collections, struct

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
P = "C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin"
data = open(P, "rb").read()
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


p("eboot.bin bytes", len(data))
lit = struct.pack("<I", 0x00280008)
pos = [m.start() for m in re.finditer(re.escape(lit), data)]
p("occurrences of the literal 0x00280008:", len(pos), "aligned to 4:", sum(1 for x in pos if x % 4 == 0))
prev = collections.Counter()
bfe = []
for x in pos:
    if x < 4:
        continue
    w = struct.unpack_from("<I", data, x - 4)[0]
    # SOP2: [31:30] = 0b10, [29:23] = op, [22:16] = sdst, [15:8] = src1, [7:0] = src0
    if (w >> 30) == 2:
        op = (w >> 23) & 0x7f
        src1 = (w >> 8) & 0xff
        src0 = w & 0xff
        prev[(op, src1 == 255, src0 == 255)] += 1
        if src1 == 255:
            bfe.append((x - 4, op, (w >> 16) & 0x7f, src0))
p("word before the literal, SOP2 (op, src1 is literal, src0 is literal) -> count:", dict(prev))
ops = collections.Counter(b[1] for b in bfe)
p("SOP2 opcodes with the literal as src1:", dict(ops))
# IMAGE_BVH_INTERSECT_RAY: MIMG, encoding bits [31:26] = 0b111100, op [25:18] = 0xe6 (and 0xe7 = BVH64)
bvh = collections.Counter()
bvh_pos = []
for off in range(0, len(data) - 4, 4):
    w = struct.unpack_from("<I", data, off)[0]
    if (w >> 26) == 0x3c:
        op = (w >> 18) & 0xff
        if op in (0xe6, 0xe7):
            bvh[op] += 1
            bvh_pos.append(off)
p("MIMG words with op 0xe6 / 0xe7 at 4-byte alignment (upper bound, data words may match):", dict((hex(k), v) for k, v in bvh.items()))
# pair them: a BFE literal within 0x1000 bytes before a BVH word
bset = sorted(b[0] for b in bfe)
import bisect
near = 0
for off in bvh_pos:
    i = bisect.bisect_left(bset, off - 0x1000)
    if i < len(bset) and bset[i] < off:
        near += 1
p("BVH words with such a BFE within 0x1000 bytes before:", near, "of", len(bvh_pos))
# the known program: its first words
open("C:/kyty/f287/f3a/bfe_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
