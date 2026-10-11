"""Track F link F47d (HPP-809; ROADMAP s122 item 708 (b)(7), (g)(1); F47a section 3.1-3.2, F47a2 section 7.1): the detector G on the
thumbnails of the captures of one f47_rd* tag - a SELECTION of the F47d link, not the member G' (G' is F47e, replay, outside the lock).
Rule (F47a section 1.3 / 3.2, constants named before the data): every runs/<tag>/kNN.png (renderdoccmd thumb) is decoded by ffmpeg and
scaled to 480x270 RGB24; in the band y < 81 (top 30 %) K = pixels with max(R, G, B) <= 16, Wt = pixels with min(R, G, B) >= 240;
class 'black' when K >= 150, 'white' when Wt >= 1000 (both may hold - printed 'black+white'), else '-'.  The capture kNN is matched to
the grid value g_N of runs/<tag>/grid.txt in ascending order (k01 = the smallest) - the frame of the capture is level+g_N by the
'RenderDoc: auto capture at frame F (level+X)' lines; the reader checks the X list against the grid.
Prints one row per capture and the line 'G black <n> white <m> of <c> thumbs <t>'.  ASCII only.
usage: python thumb_f47d.py <runs/<tag> dir>        python thumb_f47d.py --png <file>   (one picture, fixtures)"""
import glob
import os
import subprocess
import sys

import numpy as np

W, H, BAND_H = 480, 270, 81
TK, TW = 150, 1000


def counts(png):
    proc = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', png, '-vf', 'scale=%d:%d' % (W, H), '-frames:v', '1', '-f', 'rawvideo',
                           '-pix_fmt', 'rgb24', '-'], capture_output=True)
    if proc.returncode != 0 or len(proc.stdout) < W * H * 3:
        return None
    arr = np.frombuffer(proc.stdout[:W * H * 3], dtype=np.uint8).reshape(H, W, 3)[:BAND_H]
    k = int((arr.max(axis=2) <= 16).sum())
    w = int((arr.min(axis=2) >= 240).sum())
    return k, w


def cls(k, w):
    c = []
    if k >= TK:
        c.append('black')
    if w >= TW:
        c.append('white')
    return '+'.join(c) or '-'


def main(argv):
    if argv[:1] == ['--png']:
        r = counts(argv[1])
        print('png %s K %s Wt %s class %s' % (argv[1], None if r is None else r[0], None if r is None else r[1],
                                               'NO_DECODE' if r is None else cls(*r)))
        return 0 if r is not None else 1
    d = argv[0]
    grid = []
    gp = os.path.join(d, 'grid.txt')
    if os.path.exists(gp):
        grid = sorted(int(x) for x in open(gp, encoding='ascii').read().strip().split(',') if x.strip())
    pngs = sorted(glob.glob(os.path.join(d, 'k[0-9][0-9].png')))
    nb = nw = 0
    print('thumb_f47d band y<%d of %dx%d TK %d TW %d grid %s' % (BAND_H, W, H, TK, TW, ','.join(str(g) for g in grid)))
    for p in pngs:
        kk = os.path.basename(p)[1:3]
        i = int(kk) - 1
        g = grid[i] if 0 <= i < len(grid) else None
        r = counts(p)
        if r is None:
            print('k%s level+%s K - Wt - class NO_DECODE' % (kk, g))
            continue
        c = cls(*r)
        nb += 'black' in c
        nw += 'white' in c
        print('k%s level+%s K %d Wt %d class %s' % (kk, g, r[0], r[1], c))
    print('G black %d white %d of %d thumbs %d' % (nb, nw, len(grid), len(pngs)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
