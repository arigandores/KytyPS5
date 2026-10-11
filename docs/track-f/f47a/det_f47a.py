# F47a (HPP-802): per-frame counts of "block" pixels in the title band of a recording (no judgement, data for the sheet).
# Frames a..b (0-based video frames, the first column of <mp4>.idx) are decoded by ffmpeg to 480x270 RGB24; in the band
# y < BAND_H (top 30 %) it counts K = pixels with max(R,G,B) <= 16 (black) and Wt = pixels with min(R,G,B) >= 240
# (white). Prints one row per frame: vf, present (from .idx), K, Wt; then the runs of frames with K >= TK.
# Usage: python det_f47a.py <mp4> <a> <b> [--tk 150] [--tw 150]
import subprocess, sys

mp4, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
TK = int(sys.argv[sys.argv.index('--tk') + 1]) if '--tk' in sys.argv else 150
TW = int(sys.argv[sys.argv.index('--tw') + 1]) if '--tw' in sys.argv else 150
W, H = 480, 270
BAND_H = 81
present = {}
for ln in open(mp4 + '.idx', encoding='ascii'):
    p = ln.split()
    if len(p) >= 2:
        present[int(p[0])] = int(p[1])
sel = "select='between(n%s%d%s%d)',scale=%d:%d" % (chr(92) + ',', a, chr(92) + ',', b, W, H)
proc = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp4, '-vf', sel, '-vsync', '0', '-f', 'rawvideo',
                       '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
data = proc.stdout
fs = W * H * 3
nfr = len(data) // fs
print('mp4 %s frames %d..%d decoded %d band y<%d of %dx%d TK %d TW %d' % (mp4, a, b, nfr, BAND_H, W, H, TK, TW))
print('vf\tpresent\tK_black\tW_white')
hitk, hitw = [], []
for i in range(nfr):
    fr = data[i * fs:(i + 1) * fs]
    band = fr[:BAND_H * W * 3]
    k = w = 0
    for j in range(0, len(band), 3):
        r, g, bl = band[j], band[j + 1], band[j + 2]
        if r <= 16 and g <= 16 and bl <= 16:
            k += 1
        elif r >= 240 and g >= 240 and bl >= 240:
            w += 1
    vf = a + i
    print('%d\t%s\t%d\t%d' % (vf, present.get(vf, '?'), k, w))
    if k >= TK:
        hitk.append(vf)
    if w >= TW:
        hitw.append(vf)


def runs(v):
    out = []
    for x in v:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


print('black runs (K >= %d): %s' % (TK, runs(hitk)))
print('white runs (W >= %d): %s' % (TW, runs(hitw)))
