"""Own one-frame-glitch screen: frame i is an outlier if it differs from both neighbours by far more
than the neighbours differ from each other. Downscaled grey 160x90."""
import subprocess, sys
import numpy as np
W, H = 160, 90
for v in sys.argv[1:]:
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', 'scale=%d:%d' % (W, H), '-pix_fmt', 'gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    n = len(f)
    a = np.abs(f[1:-1] - f[:-2]).mean(axis=(1, 2))      # i vs i-1
    b = np.abs(f[1:-1] - f[2:]).mean(axis=(1, 2))       # i vs i+1
    c = np.abs(f[2:] - f[:-2]).mean(axis=(1, 2))        # i-1 vs i+1
    score = np.minimum(a, b) / (c + 1.0)
    idx = np.argsort(-score)[:8]
    print(v, 'frames', n, 'median_step', round(float(np.median(a)), 3))
    for i in idx:
        print('   frame %d min(d_prev,d_next)=%.2f d_skip=%.2f score=%.2f' % (i + 1, min(a[i], b[i]), c[i], score[i]))
    print('   candidates score>4 and min>6:', int(((score > 4) & (np.minimum(a, b) > 6)).sum()))
