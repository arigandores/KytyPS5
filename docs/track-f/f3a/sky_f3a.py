# F3a (HPP-308): Sky Garden comparison. For the 22 logs with BvhLoopCapTrip (s103-126), the whole
# ent103 series (67 entries, 7 with trips) and the Sky Garden logs of s127+ from the F0 sweep list:
# fault pages (X and X>>8), trip frames. Read-only stream scan; waits nothing, exits on lock/STOP.
import sys, os, re, json, glob, time

LOCK, STOP = "C:/kyty/SEALED_RUN.lock", "C:/kyty/f287/STOP"
if os.path.exists(LOCK):
    sys.exit(3)
if os.path.exists(STOP):
    sys.exit(4)
D = "C:/kyty/f287/f3a/"
PAGE = 0x4000
agg = json.load(open("C:/kyty/f287/f0/agg_f0.json", encoding="utf-8"))
sel = {}
for e in agg:
    if e.get("dup_of"):
        continue
    path = e["path"]
    ses = e.get("session")
    lv = e.get("levels") or []
    met = e.get("met") or {}
    if "underwater_aerial_garden" not in json.dumps(lv):
        continue
    if ses is None or ses < 103:
        continue
    trip = met.get("trip_n", 0) > 0
    base = os.path.basename(path)
    grp = None
    if trip:
        grp = "trip"
    elif "/s103/log_ent103_" in path:
        grp = "ent103"
    elif ses >= 127:
        grp = "s127+"
    else:
        grp = "s103-126"
    if grp:
        sel[path] = (grp, ses, int(e["size"]))
total = sum(v[2] for v in sel.values())
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))
    print(out[-1][:300], flush=True)


p("selected", len(sel), "bytes", total, {g: sum(1 for v in sel.values() if v[0] == g) for g in ("trip", "ent103", "s103-126", "s127+")})
rows = []
t0 = time.time()
done = 0
for path in sorted(sel, key=lambda x: (sel[x][1], x)):
    if os.path.exists(LOCK):
        p("LOCK appeared - stop at", path)
        break
    if os.path.exists(STOP):
        p("STOP appeared - stop at", path)
        break
    grp, ses, size = sel[path]
    faults, trips = [], []
    frame = None
    cap = None
    rtskip = None
    try:
        with open(path, "rb") as f:
            for raw in f:
                c = raw[:1]
                if c == b"F":
                    if raw.startswith(b"FrameTrace: n="):
                        frame = int(raw[14:raw.index(b" ", 14)])
                elif c == b"A":
                    if raw.startswith(b"Accessed non-GPU cached memory at "):
                        faults.append((frame, int(raw.split()[-1], 16)))
                elif c == b"B":
                    if raw.startswith(b"BvhLoopCapTrip:"):
                        m = re.search(rb"trips=\+(\d+)", raw)
                        trips.append((frame, int(m.group(1))))
                    elif raw.startswith(b"BvhLoopCap: cap="):
                        cap = raw.rstrip().decode()[12:40]
    except OSError as ex:
        p("skip", path, ex)
        continue
    done += size
    pages = [a for _, a in faults]
    pset = set(pages)
    pairs = sorted((a, (a >> 8) & ~(PAGE - 1)) for a in pset if a > 0x100000000 and ((a >> 8) & ~(PAGE - 1)) in pset)
    lows = sorted(a for a in pset if a < 0x100000000)
    first_pair_frame = min([fr for fr, a in faults if a < 0x100000000 and fr is not None], default=None)
    rows.append(dict(path=path, grp=grp, ses=ses, faults=len(faults), lows=[hex(a) for a in lows],
                     pairs=[(hex(a), hex(b)) for a, b in pairs], trips=len(trips),
                     trip_sum=sum(t for _, t in trips), trip_frames=sorted(set(fr for fr, _ in trips if fr is not None)),
                     low_first_frame=first_pair_frame, cap=cap,
                     fault_seq=[(fr, hex(a)) for fr, a in faults][:12]))
    r = rows[-1]
    p(grp, ses, path.replace("C:/kyty/", ""), "trips", r["trips"], r["trip_sum"], "frames", r["trip_frames"][:8],
      "low", r["lows"], "pairs", r["pairs"], "seq", r["fault_seq"][:6])
json.dump(rows, open(D + "sky_f3a.json", "w", encoding="utf-8"), indent=0)
p("scanned", len(rows), "of", len(sel), "bytes", done, "sec", int(time.time() - t0))
open(D + "sky_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
