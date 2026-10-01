# F3a (HPP-308): all 12 s142 logs - fault addresses (pairs X and X>>8), cap lines, and every
# translated program that contains IMAGE_BVH (asm saved per hash). Read-only stream scan.
import sys, os, re, glob, hashlib

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
D = "C:/kyty/f287/f3a/"
PAGE = 0x4000
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


logs = sorted(glob.glob("C:/kyty/s142/log_*.txt"))
p("logs", len(logs))
saved = {}
for path in logs:
    tag = os.path.basename(path)[4:-4]
    faults, trips, level = [], [], []
    cur_hash, cur_asm, in_asm, has_bvh = None, [], False, False
    n = 0
    frame = None
    with open(path, "rb") as f:
        for raw in f:
            n += 1
            if raw.startswith(b"FrameTrace: n="):
                frame = int(raw[14:raw.index(b" ", 14)])
            elif raw.startswith(b"Accessed non-GPU cached memory at "):
                faults.append((n, frame, int(raw.split()[-1], 16)))
            elif raw.startswith(b"BvhLoopCapTrip:"):
                trips.append((n, frame))
            elif b"Level has started: " in raw:
                level.append(raw.rstrip().split(b": ")[-1].decode())
            elif b" decoded RDNA2" in raw:
                in_asm, cur_asm, has_bvh = True, [], False
            elif in_asm:
                if raw.startswith(b"0x"):
                    cur_asm.append(raw.rstrip(b"\r\n"))
                    if b"IMAGE_BVH" in raw:
                        has_bvh = True
                elif b"phase begin" in raw and b"CFG BuildGraph" in raw:
                    m = re.search(rb"hash=0x([0-9a-f]{16})", raw)
                    h = m.group(1).decode() if m else "unknown"
                    kind = raw.split(b" ")[0].decode()
                    if has_bvh and h not in saved:
                        saved[h] = (tag, kind, len(cur_asm))
                        open(D + "asm_bvh_%s.txt" % h, "wb").write(b"\n".join(cur_asm) + b"\n")
                    in_asm = False
                # other interleaved lines (other threads) are ignored
    pages = set(a for _, _, a in faults)
    pairs = [(a, (a >> 8) & ~(PAGE - 1)) for a in sorted(pages) if ((a >> 8) & ~(PAGE - 1)) in pages and a > 0x100000000]
    lows = sorted(a for a in pages if a < 0x100000000)
    p("==", tag, level[-1] if level else "?", "lines", n, "faults", len(faults), "distinct", len(pages),
      "trips", len(trips), "trip frames", sorted(set(t[1] for t in trips)))
    p("   low (<4 GiB) fault pages:", [hex(a) for a in lows])
    p("   pairs (X, X>>8 page) both faulted:", [(hex(a), hex(b)) for a, b in pairs])
    for ln, fr, a in faults:
        p("   fault line", ln, "after frame", fr, hex(a), "<- X>>8 of a faulted page" if any(b == a for _, b in pairs) else "")
p("== programs with IMAGE_BVH whose translation dump is in the logs:", len(saved))
for h, v in sorted(saved.items()):
    p("  ", h, v)
open(D + "scan12_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
