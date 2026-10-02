# inset145.py - Session Auditor, s145 step 3 (HPP-353): the one-frame rule of glitch145.py restricted to one rectangle
# (the HUD inset of final_stage in the upper left corner). Data for the lead, not a verdict.
# Usage: python inset145.py <video> <x> <y> <w> <h> [T]
import sys, subprocess
import numpy as np

path, x, y, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
T = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
W, H = 960, 540
rd = subprocess.Popen(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', path, '-vf', 'format=gray,crop=%d:%d:%d:%d' % (w, h, x, y),
                       '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
f0 = f1 = None
d01 = None
n = 0
ev = []
while True:
    buf = rd.stdout.read(w * h)
    if len(buf) < w * h:
        break
    f2 = np.frombuffer(buf, np.uint8).astype(np.int16)
    if f1 is not None:
        d12 = float(np.abs(f2 - f1).mean())
        if f0 is not None:
            back = float(np.abs(f2 - f0).mean())
            m = min(d01, d12)
            if d01 > T and d12 > T and back < 0.35 * m:
                ev.append((n - 1, round(d01, 1), round(d12, 1), round(back, 1)))
        d01 = d12
    f0, f1 = f1, f2
    n += 1
rd.wait()
gaps = [b[0] - a[0] for a, b in zip(ev, ev[1:])]
print('INSET %s rect x %d y %d %dx%d T %.1f: frames %d; one-frame events %d; first 40: %s; frame distance between consecutive events: min %s max %s' % (
    path[-16:], x, y, w, h, T, n, len(ev), ev[:40], min(gaps) if gaps else None, max(gaps) if gaps else None))
