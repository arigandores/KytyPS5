# Auditor's own one-frame glitch detector (independent of s20/s51_vidglitch.py).
# Frame t is a one-frame glitch candidate when it differs from BOTH neighbours much more than the
# neighbours differ from each other: min(d(t-1,t), d(t,t+1)) > K * d(t-1,t+1) + floor.
import subprocess, numpy as np, sys
V = 'C:/kyty/s103/rec_vid103.mp4'
W, H = 240, 135
cmd = ['ffmpeg', '-v', 'error', '-i', V, '-vf', 'scale=%d:%d' % (W, H), '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
fs = W * H * 3
frames = []
while True:
    b = p.stdout.read(fs)
    if len(b) < fs: break
    frames.append(np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.int16))
p.wait()
n = len(frames)
def d(a, b):
    return float(np.mean(np.abs(frames[a] - frames[b])))
adj = [d(i, i + 1) for i in range(n - 1)]
out = ['frames decoded %d' % n, 'mean adjacent MAD %.3f, p99 %.3f, max %.3f at %d' % (
    np.mean(adj), np.percentile(adj, 99), max(adj), int(np.argmax(adj)))]
cands = []
for t in range(1, n - 1):
    a, b = adj[t - 1], adj[t]
    skip = d(t - 1, t + 1)
    score = min(a, b) / (skip + 1.0)
    cands.append((score, t, a, b, skip))
cands.sort(reverse=True)
out.append('top 10 one-frame candidates (score=min(d_prev,d_next)/(d_skip+1), t, d_prev, d_next, d_skip):')
for c in cands[:10]:
    out.append('  %.3f t=%d %.3f %.3f %.3f' % c)
flag = [c for c in cands if c[0] > 4.0 and min(c[2], c[3]) > 4.0]
out.append('flagged (score>4 and both diffs>4 levels): %d %s' % (len(flag), [c[1] for c in flag[:20]]))
# black / blank frames
dark = [i for i, f in enumerate(frames) if f.mean() < 3]
out.append('near-black frames: %d %s' % (len(dark), dark[:20]))
print('\n'.join(out))
open('C:/kyty/s103/audit103/recount/vid_glitch_own.out.txt', 'w').write('\n'.join(out) + '\n')
