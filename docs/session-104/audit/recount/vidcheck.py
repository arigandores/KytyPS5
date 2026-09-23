# Independent one-frame-glitch check (auditor). Decodes to 96x54 gray, counts frames, and flags
# frames that differ strongly from both neighbours while the neighbours agree with each other.
import subprocess, sys
import numpy as np

W, H = 96, 54
for path in sys.argv[1:]:
    p = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '2', '-i', path, '-vf', 'scale=%d:%d' % (W, H),
                        '-pix_fmt', 'gray', '-f', 'rawvideo', '-'], capture_output=True)
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = buf.size // (W * H)
    fr = buf[:n * W * H].reshape(n, H, W).astype(np.float32)
    d1 = np.abs(fr[1:] - fr[:-1]).mean(axis=(1, 2))          # d(i, i+1)
    d2 = np.abs(fr[2:] - fr[:-2]).mean(axis=(1, 2))          # d(i-1, i+1)
    prev, nxt = d1[:-1], d1[1:]                              # for frame i = 1..n-2
    res = {}
    for T in (4.0, 6.0, 10.0):
        m = (prev > T) & (nxt > T) & (d2 < 0.35 * np.minimum(prev, nxt))
        res[T] = [int(i) + 1 for i in np.nonzero(m)[0]]
    print(path, 'decoded frames', n, 'stderr bytes', len(p.stderr),
          'median d1 %.3f p99 d1 %.3f max d1 %.3f' % (np.median(d1), np.percentile(d1, 99), d1.max()),
          {k: (len(v), v[:10]) for k, v in res.items()})
