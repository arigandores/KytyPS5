# F3a (HPP-308): stream scan of the two s142 census logs with BvhLoopCapTrip lines.
# Read-only, binary mode, one pass per log. Output: scan_f3a.out.txt
import sys, os, re, hashlib

LOCK = "C:/kyty/SEALED_RUN.lock"
if os.path.exists(LOCK):
    sys.exit(3)

LOGS = [("c142_02", "C:/kyty/s142/log_c142_02.txt"), ("c142_09", "C:/kyty/s142/log_c142_09.txt")]
KEYS = [b"BvhLoopCap", b"Accessed non-GPU cached memory", b"PriorityStall:", b"Level has started",
        b"GpuWaitSlow", b"GpuHangAbort", b"AsyncPipelines: skipped draw", b"380bb9d636390bae",
        b"bvh", b"Bvh", b"BVH"]
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


for tag, path in LOGS:
    h = hashlib.sha256()
    size = os.path.getsize(path)
    counts = {k: 0 for k in KEYS}
    first = {}
    trips = []
    faults = []
    stalls = []
    frames = []  # (lineno, text) of FrameTrace lines
    level = []
    capcfg = []
    ft_x_trip = []
    n = 0
    with open(path, "rb") as f:
        for raw in f:
            n += 1
            h.update(raw)
            for k in KEYS:
                if k in raw:
                    counts[k] += 1
                    first.setdefault(k, n)
            if b"BvhLoopCapTrip:" in raw:
                trips.append((n, raw.rstrip().decode("utf-8", "replace")))
            elif b"BvhLoopCap:" in raw:
                capcfg.append((n, raw.rstrip().decode("utf-8", "replace")))
            if b"Accessed non-GPU cached memory" in raw:
                faults.append((n, raw.rstrip().decode("utf-8", "replace")))
            if b"PriorityStall:" in raw:
                stalls.append((n, raw.rstrip().decode("utf-8", "replace")))
            if b"Level has started" in raw:
                level.append((n, raw.rstrip().decode("utf-8", "replace")))
            if raw.startswith(b"FrameTrace") or b"] FrameTrace" in raw or b"FrameTrace:" in raw[:80]:
                if b"FrameTrace-" in raw:
                    if b"bl_trip=" in raw:
                        m = re.search(rb"bl_trip=(\d+)", raw)
                        m2 = re.search(rb"bl_near=(\d+)", raw)
                        if m and (int(m.group(1)) or (m2 and int(m2.group(1)))):
                            ft_x_trip.append((n, raw[:60].decode("utf-8", "replace"), int(m.group(1)), int(m2.group(1)) if m2 else -1))
                else:
                    frames.append((n, raw.rstrip().decode("utf-8", "replace")))
    p("=====", tag, path, "bytes", size, "lines", n, "sha256", h.hexdigest()[:16])
    for k in KEYS:
        p("  count", k.decode(), counts[k], "first line", first.get(k))
    p("  -- BvhLoopCap config lines:", len(capcfg))
    for x in capcfg[:40]:
        p("   ", x[0], x[1][:300])
    p("  -- Level has started:")
    for x in level:
        p("   ", x[0], x[1][:200])
    p("  -- BvhLoopCapTrip lines:", len(trips))
    for x in trips:
        p("   ", x[0], x[1][:300])
    p("  -- FrameTrace-x rows with bl_trip/bl_near != 0:", len(ft_x_trip))
    for x in ft_x_trip:
        p("   ", x)
    p("  -- fault lines total:", len(faults))
    if trips:
        lo, hi = trips[0][0] - 20000, trips[-1][0] + 20000
        near = [x for x in faults if lo <= x[0] <= hi]
        p("  -- fault lines within +-20000 lines of trips:", len(near))
        for x in near[:200]:
            p("   ", x[0], x[1][:200])
        p("  -- PriorityStall within the same range:")
        for x in stalls:
            if lo <= x[0] <= hi:
                p("   ", x[0], x[1][:300])
        p("  -- FrameTrace lines within the same range:")
        for x in frames:
            if lo <= x[0] <= hi:
                p("   ", x[0], x[1][:420])
    p("  -- frames total", len(frames))
    if frames:
        p("  -- first FrameTrace sample:", frames[0][1][:600])

open("C:/kyty/f287/f3a/scan_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("lines out", len(out))
