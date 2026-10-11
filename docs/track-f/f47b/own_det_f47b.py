# F47b own detector (independent of det_f47a.py): full 960x540 frames, per frame: black pixels (all channels <= 8) and
# white pixels (all channels >= 247) in the top 30 % and in the whole frame, plus bbox of black pixels in the band.
import subprocess, sys
import numpy as np
mp4, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
W, H = 960, 540
sel = "select='between(n%s%d%s%d)'" % (chr(92) + ',', a, chr(92) + ',', b)
p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp4, '-vf', sel, '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                   capture_output=True, check=True)
arr = np.frombuffer(p.stdout, dtype=np.uint8)
n = arr.size // (W * H * 3)
arr = arr[:n * W * H * 3].reshape(n, H, W, 3)
bh = int(H * 0.3)
for i in range(n):
    f = arr[i]
    blk = f.max(axis=2) <= 8
    wht = f.min(axis=2) >= 247
    bb = blk[:bh]
    ys, xs = np.nonzero(bb)
    box = '%d-%d x %d-%d' % (xs.min(), xs.max(), ys.min(), ys.max()) if xs.size else '-'
    print('vf %d band_black %d band_white %d frame_black %d frame_white %d mean %.1f bbox %s' % (
        a + i, bb.sum(), wht[:bh].sum(), blk.sum(), wht.sum(), f.mean(), box))
