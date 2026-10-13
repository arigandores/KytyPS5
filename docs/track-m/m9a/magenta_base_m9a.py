# M9a (HPP-863): natural "tint-like" magenta pixels in the M6c videos (no tint) - an offline estimate of the detector
# baseline M_b before the series (the series recomputes it on every frame). Decodes 1 frame per second at full size,
# ffmpeg at IDLE priority. Pixel is magenta if R >= 200, G <= 60, B >= 200 (8-bit RGB after decode).
# Usage: python magenta_base_m9a.py <video>... ; writes magenta_base_m9a.out.txt next to the script. Exits if the lock exists.
import os, sys, subprocess, hashlib
import numpy as np

LOCK = "C:/kyty/SEALED_RUN.lock"
if os.path.exists(LOCK):
    sys.exit(3)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "magenta_base_m9a.out.txt")
W, H = 960, 540
IDLE = 0x00000040

def count(video):
    cmd = ["ffmpeg", "-v", "error", "-i", video, "-vf", "fps=1,scale=%d:%d" % (W, H), "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, creationflags=IDLE)
    n = W * H * 3
    res = []
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        a = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3)
        m = (a[:, :, 0] >= 200) & (a[:, :, 1] <= 60) & (a[:, :, 2] >= 200)
        res.append(int(m.sum()))
    p.wait()
    return res

out = ["rule: R>=200 G<=60 B>=200, 1 frame per second, %dx%d" % (W, H)]
for v in sys.argv[1:]:
    if os.path.exists(LOCK):
        sys.exit(3)
    h = hashlib.sha256(open(v, "rb").read()).hexdigest()
    c = count(v)
    s = sorted(c)
    p999 = s[min(len(s) - 1, int(0.999 * len(s)))] if s else -1
    out.append("%s sha256 %s frames %d max %d p99.9 %d mean %.2f frames_gt0 %d frames_gt200 %d" % (
        os.path.basename(v), h, len(c), max(c) if c else -1, p999, (sum(c) / len(c)) if c else -1,
        sum(1 for x in c if x > 0), sum(1 for x in c if x > 200)))
out.append("ALL OK")
open(OUT, "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
