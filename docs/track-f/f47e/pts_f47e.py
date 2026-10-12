"""F47e (HPP-810): G' (3) detector on the saved presented guest image and the points of edition 2 section 2 (F47a section 4.1).

    python pts_f47e.py det  <png> [<thumb png>]          K / Wt of the band y < 81 at 480x270 (form F47a section 1.3), class
    python pts_f47e.py pts  <png> <W> <H> <tex id> <snap> <out.json>   points: per block (connected component of the class mask in the
                                                         band) 4 inner points + 1 outer point, chosen before any analysis

Detector (F47a section 1.3, edition 2 section 7.1(3)): image scaled to 480x270 (ffmpeg, bilinear as ffmpeg default), band y < 81;
K = pixels with max(R,G,B) <= 16, Wt = pixels with min(R,G,B) >= 240; class black if K >= 150, white if Wt >= 1000 (both -> black+white).
Points (edition 2 section 2): mask = K pixels (black block) / Wt pixels (white block) of the band; a block = 8-connected component with
>= 150 (black) / >= 1000 (white) pixels... components smaller than 20 pixels are dropped as noise; for each block the 4 inner points are
the corners of its bounding box moved 2 pixels inwards, each replaced by the nearest mask pixel of the component (Chebyshev, then
scan order) when the moved corner is not in the mask; the outer point is the first pixel left of the bounding box (x0 - 3, then
x1 + 3) at the middle row that is not in any mask; map x = floor((x_m + 0.5) * W / 480), y = floor((y_m + 0.5) * H / 270).
"""
import json
import subprocess
import sys

import numpy as np


def load480(png):
    cmd = ['ffmpeg', '-v', 'error', '-i', png, '-vf', 'scale=480:270', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw[:480 * 270 * 3], dtype=np.uint8).reshape(270, 480, 3)


def kw(a):
    b = a[:81]
    km = b.max(axis=2) <= 16
    wm = b.min(axis=2) >= 240
    return km, wm


def cls(k, w):
    c = []
    if k >= 150:
        c.append('black')
    if w >= 1000:
        c.append('white')
    return '+'.join(c) if c else '-'


def components(mask):
    h, w = mask.shape
    lab = np.zeros(mask.shape, dtype=np.int32)
    comps = []
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not lab[y, x]:
                n += 1
                st = [(y, x)]
                lab[y, x] = n
                pix = []
                while st:
                    cy, cx = st.pop()
                    pix.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n
                                st.append((ny, nx))
                comps.append((n, pix))
    return lab, comps


def main():
    mode = sys.argv[1]
    a = load480(sys.argv[2])
    km, wm = kw(a)
    K, W = int(km.sum()), int(wm.sum())
    if mode == 'det':
        line = 'det %s K %d Wt %d class %s' % (sys.argv[2], K, W, cls(K, W))
        if len(sys.argv) > 3:
            t = load480(sys.argv[3])
            tk, tw = kw(t)
            line += ' | thumb %s K %d Wt %d class %s' % (sys.argv[3], int(tk.sum()), int(tw.sum()), cls(int(tk.sum()), int(tw.sum())))
        print(line)
        return 0
    Wd, Hd, tex, snap, outp = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6], sys.argv[7]
    pts = []
    anym = km | wm
    for kind, mask, thr in (('black', km, 150), ('white', wm, 1000)):
        if (K if kind == 'black' else W) < thr:
            continue
        lab, comps = components(mask)
        comps = [c for c in comps if len(c[1]) >= 20]
        comps.sort(key=lambda c: -len(c[1]))
        for bi, (n, pix) in enumerate(comps):
            ys = [p[0] for p in pix]
            xs = [p[1] for p in pix]
            y0, y1, x0, x1 = min(ys), max(ys), min(xs), max(xs)
            pset = set(pix)
            corners = [('c00', x0 + 2, y0 + 2), ('c10', x1 - 2, y0 + 2), ('c01', x0 + 2, y1 - 2), ('c11', x1 - 2, y1 - 2)]
            for cname, cx, cy in corners:
                if (cy, cx) in pset:
                    px, py, how = cx, cy, 'corner'
                else:
                    best = min(pix, key=lambda p: (max(abs(p[0] - cy), abs(p[1] - cx)), p[0], p[1]))
                    py, px, how = best[0], best[1], 'nearest'
                pts.append(dict(snap=snap, block='%s%d' % (kind, bi + 1), name='%s%d_%s' % (kind, bi + 1, cname), tex=int(tex),
                                xm=px, ym=py, x=int((px + 0.5) * Wd / 480), y=int((py + 0.5) * Hd / 270), inner=True, how=how,
                                npix=len(pix), bbox=[x0, y0, x1, y1]))
            ym = (y0 + y1) // 2
            for ox in (x0 - 3, x1 + 3):
                if 0 <= ox < 480 and not anym[ym, ox]:
                    pts.append(dict(snap=snap, block='%s%d' % (kind, bi + 1), name='%s%d_out' % (kind, bi + 1), tex=int(tex), xm=ox, ym=ym,
                                    x=int((ox + 0.5) * Wd / 480), y=int((ym + 0.5) * Hd / 270), inner=False, how='outside',
                                    npix=len(pix), bbox=[x0, y0, x1, y1]))
                    break
    for p in pts:
        print('point %s %s block %s m(%d,%d) -> (%d,%d) %s npix %d bbox %s' % (p['snap'], p['name'], p['block'], p['xm'], p['ym'], p['x'],
                                                                          p['y'], p['how'], p['npix'], p['bbox']))
    json.dump(pts, open(outp, 'w'), indent=1)
    print('points %d -> %s' % (len(pts), outp))
    return 0


sys.exit(main())
