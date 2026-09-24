# Independent one-frame-glitch screen: decode to small grayscale, look for frames unlike both neighbours
# while the neighbours are alike (own definition; not the session's s51_vidglitch.py).
import subprocess, numpy as np, sys
path = sys.argv[1]; W, H = 160, 90
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                     stdout=subprocess.PIPE)
buf = p.stdout.read(); p.wait()
fr = np.frombuffer(buf, np.uint8).reshape(-1, H, W).astype(np.float32)
n = len(fr)
d1 = np.abs(fr[1:] - fr[:-1]).mean(axis=(1, 2))          # d(i, i+1)
d2 = np.abs(fr[2:] - fr[:-2]).mean(axis=(1, 2))          # d(i-1, i+1)
a = d1[:-1]; b = d1[1:]                                   # d(i-1,i), d(i,i+1) for i = 1..n-2
score = np.minimum(a, b) - d2
print('frames decoded', n)
print('d1 median %.2f p99 %.2f max %.2f' % (np.median(d1), np.percentile(d1, 99), d1.max()))
for T in (4, 6, 10, 20):
    idx = np.where((np.minimum(a, b) > T) & (d2 < np.minimum(a, b) / 3))[0] + 1
    print('T', T, 'one-frame candidates', len(idx), list(idx[:10]))
top = np.argsort(score)[-5:][::-1] + 1
print('top isolation scores', [(int(i), round(float(score[i - 1]), 2), round(float(d2[i - 1]), 2)) for i in top])
