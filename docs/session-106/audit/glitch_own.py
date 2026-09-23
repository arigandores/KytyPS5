"""Auditor: independent one-frame-glitch heuristic. Decode to 64x36 gray; frame i is a candidate if it differs
from both neighbours much more than the neighbours differ from each other."""
import subprocess, sys
import numpy as np
W, H = 64, 36
p = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-vf', 'scale=%d:%d' % (W, H), '-pix_fmt', 'gray',
                    '-f', 'rawvideo', '-'], capture_output=True, check=True)
a = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W).astype(np.float32)
n = len(a)
d = lambda i, j: float(np.abs(a[i] - a[j]).mean())
cand = []
for i in range(1, n - 1):
    x, y, z = d(i - 1, i), d(i, i + 1), d(i - 1, i + 1)
    if min(x, y) > 6.0 and min(x, y) > 3.0 * z + 2.0:
        cand.append((i, round(x, 1), round(y, 1), round(z, 1)))
print(sys.argv[1], 'frames', n, 'one-frame candidates', len(cand), cand[:10])
