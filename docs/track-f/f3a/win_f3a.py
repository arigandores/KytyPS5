# F3a (HPP-308): the 24 logs with BvhLoopCapTrip - is every trip readback inside the window
# [frame of the first X1>>8 page fault + 1 .. frame of the 0x4024000 (X2>>8) page fault + 1]?
# Also: fault lines printed in the same deferred operation as a trip line (the next lines).
import sys, os, re, json

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
D = "C:/kyty/f287/f3a/"
rows = json.load(open(D + "sky_f3a.json", encoding="utf-8"))
paths = [r["path"] for r in rows if r["trips"]] + ["C:/kyty/s142/log_c142_02.txt", "C:/kyty/s142/log_c142_09.txt"]
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


inside = total = 0
extra_logs = 0
all_logs = 0
whole = 0
nlines = 0
for path in paths:
    faults, trips = [], []
    frame = None
    with open(path, "rb") as f:
        for raw in f:
            c = raw[:1]
            if c == b"F" and raw.startswith(b"FrameTrace: n="):
                frame = int(raw[14:raw.index(b" ", 14)])
            elif c == b"A" and raw.startswith(b"Accessed non-GPU cached memory at "):
                faults.append((frame, int(raw.split()[-1], 16)))
            elif c == b"B" and raw.startswith(b"BvhLoopCapTrip:"):
                m = re.search(rb"trips=\+(\d+) total=(\d+) near=\+(\d+) near_total=(\d+) max_spent=(\d+)", raw)
                trips.append((frame,) + tuple(int(x) for x in m.groups()))
    low = [(fr, a) for fr, a in faults if a < 0x100000000]
    f1 = low[0][0] if low else None
    p1 = low[0][1] if low else None
    f2 = next((fr for fr, a in low if a == 0x4024000), None)
    tf = [t[0] for t in trips]
    ok = f1 is not None and f2 is not None and all(f1 + 1 <= t <= f2 + 1 for t in tf)
    extra = sorted(set(a for fr, a in low if a not in (p1, 0x4024000) and f1 is not None and f2 is not None and f1 < (fr or 0) <= f2 + 1))
    all_logs += 1
    inside += 1 if ok else 0
    extra_logs += 1 if extra else 0
    nlines += len(trips)
    whole += sum(1 for t in trips if t[1] == 131072)
    p(path.replace("C:/kyty/", ""), "P1", hex(p1) if p1 else None, "f1", f1, "f2", f2, "trip frames", tf, "inside" if ok else "OUTSIDE",
      "trips", [t[1] for t in trips], "near", sum(t[3] for t in trips), "max_spent", sorted(set(t[5] for t in trips)),
      "garbage low pages in window", [hex(a) for a in extra])
p("logs", all_logs, "with every trip readback inside [f1+1, f2+1]:", inside, "; logs with other low fault pages inside the window:", extra_logs)
p("trip lines", nlines, "of them a whole dispatch (131072 = 2048 x 64):", whole)
open(D + "win_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
