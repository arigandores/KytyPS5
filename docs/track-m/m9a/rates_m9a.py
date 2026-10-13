# M9a (HPP-863, track M): event rates of T188 from the M6c table and the cost table of fix form A / form B.
# Input: docs/track-m/m6c/table.txt (KytyPS5 44e1a421). Output: rates_m9a.out.txt next to this script.
# Offline only; exits if the lock exists.
import os, sys, hashlib

LOCK = "C:/kyty/SEALED_RUN.lock"
if os.path.exists(LOCK):
    sys.exit(3)

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "..", "m6c", "table.txt")
OUT = os.path.join(HERE, "rates_m9a.out.txt")

raw = open(TABLE, "rb").read()
lines = raw.decode("utf-8").replace("\r", "").split("\n")
hdr = None
rows = {}
for ln in lines:
    if ln.startswith("| tag |"):
        hdr = [c.strip() for c in ln.strip("|").split("|")]
        continue
    if hdr and ln.startswith("| m6_"):
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows[cells[0]] = dict(zip(hdr, cells))

out = []
out.append("table %s sha256 %s" % ("docs/track-m/m6c/table.txt", hashlib.sha256(raw).hexdigest()))
out.append("tag inv_calls inv_gpu inv_part inv_part_src inv_off hold_s video_frames part_per_s part_per_frame off_share full_gpu")
tot = {"inv_part": 0, "inv_off": 0}
rates = {}
for tag in ("m6_sg", "m6_hb", "m6_mg"):
    r = rows[tag]
    calls, gpu, part, src, off = (int(r[k]) for k in ("inv_calls", "inv_gpu", "inv_part", "inv_part_src", "inv_off"))
    hold = float(r["hold_s"])
    frames = int(r["video"])
    pps = part / hold
    ppf = part / frames
    rates[tag] = (pps, ppf)
    tot["inv_part"] += part
    tot["inv_off"] += off
    out.append("%s %d %d %d %d %d %.1f %d %.1f %.3f %.3f %d" % (
        tag, calls, gpu, part, src, off, hold, frames, pps, ppf, off / part, gpu - part))
    assert part == src, tag
out.append("SUM inv_part %d inv_off %d off_share %.3f" % (tot["inv_part"], tot["inv_off"], tot["inv_off"] / tot["inv_part"]))
out.append("note: counts are whole-run totals (entry + hold); per-second and per-frame rates divide by hold_s and video frames [I]")
out.append("")
out.append("cost of form A per frame = part_per_frame x S (one image->buffer download of the image source range per event)")
out.append("S_MiB " + " ".join("%s_MiB_per_frame" % t for t in ("m6_sg", "m6_hb", "m6_mg")))
for s in (0.25, 1, 4, 8, 16, 32):
    out.append("%.2f " % s + " ".join("%.2f" % (rates[t][1] * s) for t in ("m6_sg", "m6_hb", "m6_mg")))
out.append("")
out.append("ms per frame at an assumed effective download bandwidth B (read+write, tiler included) [I]:")
for bw in (50, 100, 200):
    for s in (1, 8, 32):
        vals = []
        for t in ("m6_sg", "m6_hb", "m6_mg"):
            bytes_pf = rates[t][1] * s * 1024 * 1024
            vals.append("%.3f" % (bytes_pf / (bw * 1e9) * 1e3))
        out.append("B=%d GB/s S=%d MiB ms/frame sg hb mg: %s" % (bw, s, " ".join(vals)))
out.append("")
out.append("render pass breaks of form A per frame (upper bound = part_per_frame, if every event is inside a pass):")
for t in ("m6_sg", "m6_hb", "m6_mg"):
    out.append("%s %.3f" % (t, rates[t][1]))
out.append("ALL OK")
open(OUT, "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
