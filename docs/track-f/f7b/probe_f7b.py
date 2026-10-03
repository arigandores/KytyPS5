"""probe_f7b.py - F7b (HPP-398) rework after the lead review 2026-10-03T01:48:59Z: distinguishing probe.
Offline, no GPU, no game.  Finds screen pixels of the floor draws 950/960 where the perspective-correct interpolated UV
(VS out_param_1.xy = PS in_param_1.xy, the coordinate of image_3[5] = tex 12274) lands on NON-uniform atlas texels
(not the plain region (204,205,215) that equals texel (0,0)), so that the pixel history there distinguishes
  (a) correct UV interpolation -> RT0 = atlas texel at the interpolated UV (not the plain colour), from
  (b) UV collapsed to 0 / constant in the PS -> RT0 = plain colour.
Inputs: rd/vsout_e950.bin, rd/vsout_e960.bin (stride 160: gl_Position offset 0, out_param_1 offset 48),
        rd/vsidx_e950.bin, rd/vsidx_e960.bin (uint16), rd/tex_12274_e950_m0.png (mip0 sRGB), rd/rd_f7b_hist.txt.
Members:
  (c) calibration: the 6 floor points F1..F6 with their primitiveID from the pixel history must lie inside the
      projected triangle and the projected depth must equal the history depth (viewport convention check);
  (t) triangles of each draw whose UV triangle touches non-plain texels, and how many of them are on screen;
  (p) candidate pixels: front-most triangle of the same draw at that pixel, footprint <= MAXFP texels,
      neighbourhood of the UV (radius = max(2, footprint)) non-plain and uniform -> expected linear colour.
Output: probe_f7b.txt, rd/probe_pts.json (points for the replay phase 'probe'), rd/probe_pick.png.
Ends with ALL OK when every member produced its line.
"""
import json
import math
import os
import re
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

RD = 'C:/kyty/f287/f7b/rd'
OUT = 'C:/kyty/f287/f7b/probe_f7b.txt'
SW, SH = 3840, 2160
PLAIN = (204, 205, 215)
MAXFP = 64.0
lines = []


def P(*a):
    lines.append(' '.join(str(x) for x in a))


def s2l(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


ok = True
im = Image.open(os.path.join(RD, 'tex_12274_e950_m0.png')).convert('RGB')
A = np.asarray(im).astype(np.int32)          # [y, x, 3]
TW = A.shape[1]
TH = A.shape[0]
nonplain = np.any(A != np.array(PLAIN), axis=2)
P('== atlas tex 12274 mip0 %dx%d, non-plain texels %d (%.2f%%), texel (0,0) %s' % (
    TW, TH, int(nonplain.sum()), 100.0 * nonplain.mean(), tuple(A[0, 0])))
Alin = s2l(A.astype(np.float64))


def load(e):
    vb = open(os.path.join(RD, 'vsout_e%d.bin' % e), 'rb').read()
    ib = open(os.path.join(RD, 'vsidx_e%d.bin' % e), 'rb').read()
    nv = len(vb) // 160
    arr = np.frombuffer(vb, dtype=np.float32).reshape(nv, 40)
    pos = arr[:, 0:4].astype(np.float64)
    uv = arr[:, 12:14].astype(np.float64)
    idx = np.frombuffer(ib, dtype=np.uint16).astype(np.int64).reshape(-1, 3)
    return pos, uv, idx


def project(pos):
    w = pos[:, 3]
    sx = (pos[:, 0] / w * 0.5 + 0.5) * SW
    sy = (-pos[:, 1] / w * 0.5 + 0.5) * SH          # negative-height viewport (y up in NDC), checked by member (c)
    z = pos[:, 2] / w
    return sx, sy, z, w


def bary(px, py, x, y):
    # x, y: (..., 3) screen vertices; returns l0, l1, l2 (screen-space barycentrics)
    d = (y[..., 1] - y[..., 2]) * (x[..., 0] - x[..., 2]) + (x[..., 2] - x[..., 1]) * (y[..., 0] - y[..., 2])
    l0 = ((y[..., 1] - y[..., 2]) * (px - x[..., 2]) + (x[..., 2] - x[..., 1]) * (py - y[..., 2])) / d
    l1 = ((y[..., 2] - y[..., 0]) * (px - x[..., 2]) + (x[..., 0] - x[..., 2]) * (py - y[..., 2])) / d
    return l0, l1, 1.0 - l0 - l1


def interp(l, w, att):
    # perspective-correct: att (..., 3, k), w (..., 3)
    q = l / w
    s = q.sum(axis=-1, keepdims=True)
    return (q[..., None] * att).sum(axis=-2) / s


def texel(u, v):
    tx = int((u - math.floor(u)) * TW) % TW
    ty = int((v - math.floor(v)) * TH) % TH
    return tx, ty


D = {e: load(e) for e in (950, 960)}

# (c) calibration with the history primitive IDs
P('== (c) calibration: floor points of the pixel history (RT0 6683) vs projected primitive (screen y = (-y/w*0.5+0.5)*H, depth z/w)')
hist = {}
cur = None
for l in open(os.path.join(RD, 'rd_f7b_hist.txt'), encoding='utf-8'):
    m = re.match(r'-- HIST (\S+) \((\d+),(\d+)\) on tex (\d+)', l)
    if m:
        cur = m.groups()
        continue
    if cur and cur[3] == '6683' and cur[0].startswith('F'):
        m = re.match(r'\s+eid (950|960) .*passed=True prim=(\d+) .*depth pre=([\d.]+) post=([\d.]+)', l)
        if m:
            hist[(cur[0], int(m.group(1)))] = (int(cur[1]), int(cur[2]), int(m.group(2)), float(m.group(4)))
ncal = 0
FRONT = set()
for (name, e), (X, Y, prim, dep) in sorted(hist.items()):
    pos, uv, idx = D[e]
    sx, sy, z, w = project(pos)
    t = idx[prim]
    l = np.array(bary(X + 0.5, Y + 0.5, sx[t], sy[t]))
    inside = bool(np.all(l >= -1e-6))
    zz = float((l * z[t]).sum())
    uvp = interp(l[None, :], w[t][None, :], uv[t][None, :, :])[0]
    tx, ty = texel(uvp[0], uvp[1])
    good = inside and abs(zz - dep) < 2e-5
    sgn = 0.5 * ((sx[t][1] - sx[t][0]) * (sy[t][2] - sy[t][0]) - (sx[t][2] - sx[t][0]) * (sy[t][1] - sy[t][0]))
    FRONT.add(int(np.sign(sgn)))
    ncal += good
    P('  %s eid %d px (%d,%d) prim %d inside %s depth proj %.6f hist %.6f uv (%.5f,%.5f) texel (%d,%d) %s plain %s' % (
        name, e, X, Y, prim, inside, zz, dep, uvp[0], uvp[1], tx, ty, tuple(A[ty, tx]), tuple(A[ty, tx]) == PLAIN))
P('  calibrated %d of %d; signed screen area of the passed (front-facing, cull Back) primitives: sign %s' % (ncal, len(hist), sorted(FRONT)))
ok &= ncal == len(hist) and ncal >= 12 and len(FRONT) == 1
FSIGN = list(FRONT)[0]

# (t) triangles touching non-plain texels
P('== (t) floor triangles whose UV triangle touches non-plain texels (barycentric grid 24)')
N = 24
gl = [(a / N, b / N, (N - a - b) / N) for a in range(N + 1) for b in range(N + 1 - a)]
G = np.array(gl)                               # [g, 3]
cands = {}
for e in (950, 960):
    pos, uv, idx = D[e]
    sx, sy, z, w = project(pos)
    tuv = uv[idx]                                  # [t, 3, 2]
    gu = np.einsum('gk,tkc->tgc', G, tuv)          # [t, g, 2]
    txs = (np.floor((gu[..., 0] - np.floor(gu[..., 0])) * TW).astype(np.int64)) % TW
    tys = (np.floor((gu[..., 1] - np.floor(gu[..., 1])) * TH).astype(np.int64)) % TH
    np_frac = nonplain[tys, txs].mean(axis=1)
    sel = np.nonzero(np_frac > 0)[0]
    tw = w[idx]
    tsx = sx[idx]
    tsy = sy[idx]
    front = np.all(tw > 0, axis=1)
    onscr = front & (tsx.max(axis=1) >= 0) & (tsx.min(axis=1) < SW) & (tsy.max(axis=1) >= 0) & (tsy.min(axis=1) < SH)
    area = 0.5 * ((tsx[:, 1] - tsx[:, 0]) * (tsy[:, 2] - tsy[:, 0]) - (tsx[:, 2] - tsx[:, 0]) * (tsy[:, 1] - tsy[:, 0]))
    P('  eid %d triangles %d; touching non-plain %d; of them in front of the camera %d, on screen %d; '
      'screen area of those on screen %.0f px (signed sum %.0f)' % (
          e, len(idx), len(sel), int(front[sel].sum()), int(onscr[sel].sum()),
          float(np.abs(area[sel][onscr[sel]]).sum()), float(area[sel][onscr[sel]].sum())))
    ff = np.sign(area) == FSIGN
    P('  eid %d of the on-screen ones front-facing (sign %d) %d, area %.0f px' % (e, FSIGN, int((onscr & ff)[sel].sum()), float(np.abs(area[sel][(onscr & ff)[sel]]).sum())))
    cands[e] = [int(t) for t in sel if onscr[t] and ff[t]]

# (p) candidate pixels
P('== (p) candidate pixels (every pixel centre of the front-facing candidate triangles): front-most triangle of the same draw, footprint <= %.0f texels, neighbourhood radius ceil(footprint)+2 all non-plain and uniform' % MAXFP)
picked = []
allpix = {}
for e in (950, 960):
    pos, uv, idx = D[e]
    sx, sy, z, w = project(pos)
    Tsx, Tsy, Tz, Tw, Tuv = sx[idx], sy[idx], z[idx], w[idx], uv[idx]
    found = []
    for t in cands[e]:
        x0 = max(0, int(math.floor(Tsx[t].min())))
        x1 = min(SW - 1, int(math.ceil(Tsx[t].max())))
        y0 = max(0, int(math.floor(Tsy[t].min())))
        y1 = min(SH - 1, int(math.ceil(Tsy[t].max())))
        if x1 < x0 or y1 < y0:
            continue
        step = 1
        ys, xs = np.mgrid[y0:y1 + 1:step, x0:x1 + 1:step]
        pxs = xs.ravel() + 0.5
        pys = ys.ravel() + 0.5
        l0, l1, l2 = bary(pxs, pys, Tsx[t][None, :], Tsy[t][None, :])
        L = np.stack([l0, l1, l2], axis=1)
        ins = np.all(L >= 0, axis=1)
        for k in np.nonzero(ins)[0]:
            X, Y = int(pxs[k]), int(pys[k])
            l = L[k]
            uvp = interp(l[None, :], Tw[t][None, :], Tuv[t][None, :, :])[0]
            # footprint by finite differences of the same triangle plane
            lx = np.array(bary(X + 1.5, Y + 0.5, Tsx[t], Tsy[t]))
            ly = np.array(bary(X + 0.5, Y + 1.5, Tsx[t], Tsy[t]))
            ux = interp(lx[None, :], Tw[t][None, :], Tuv[t][None, :, :])[0]
            uy = interp(ly[None, :], Tw[t][None, :], Tuv[t][None, :, :])[0]
            fx = math.hypot((ux[0] - uvp[0]) * TW, (ux[1] - uvp[1]) * TH)
            fy = math.hypot((uy[0] - uvp[0]) * TW, (uy[1] - uvp[1]) * TH)
            fp = max(fx, fy)
            if fp > MAXFP:
                continue
            tx, ty = texel(uvp[0], uvp[1])
            r = int(math.ceil(fp)) + 2
            if tx - r < 0 or ty - r < 0 or tx + r >= TW or ty + r >= TH:
                continue
            nb = A[ty - r:ty + r + 1, tx - r:tx + r + 1]
            if not np.all(nonplain[ty - r:ty + r + 1, tx - r:tx + r + 1]):
                continue
            nbl = Alin[ty - r:ty + r + 1, tx - r:tx + r + 1].reshape(-1, 3)
            spread = float((nbl.max(axis=0) - nbl.min(axis=0)).max())
            found.append((spread, fp, X, Y, t, uvp[0], uvp[1], tx, ty, [float(v) for v in nbl.mean(axis=0)],
                          [int(v) for v in A[ty, tx]], [float(v) for v in Alin[ty, tx]]))
    # front-most check against every triangle of the same draw
    keep = []
    for f in sorted(found):
        if f[0] > 0.06:
            continue
        X, Y, t = f[2], f[3], f[4]
        px, py = X + 0.5, Y + 0.5
        l0, l1, l2 = bary(px, py, Tsx, Tsy)
        L = np.stack([l0, l1, l2], axis=1)
        cov = np.all(L >= 0, axis=1) & np.all(Tw > 0, axis=1)
        zs = (L * Tz).sum(axis=1)
        cov_ids = np.nonzero(cov)[0]
        fm = int(cov_ids[np.argmin(zs[cov_ids])])
        ufm = interp(L[fm][None, :], Tw[fm][None, :], Tuv[fm][None, :, :])[0]
        ftx, fty = texel(ufm[0], ufm[1])
        keep.append(f + (int(len(cov_ids)), float(zs[t]), fm, float(zs[fm]), [int(v) for v in A[fty, ftx]]))
    allpix[e] = keep
    nfront = sum(1 for k in keep if k[14] == k[4])
    P('  eid %d candidate triangles on screen %d -> pixels passing footprint and uniform non-plain %d, spread <= 0.06: %d; '
      'of them the candidate is the front-most triangle of the draw: %d; front-most texel plain at %d' % (
          e, len(cands[e]), len(found), len(keep), nfront, sum(1 for k in keep if tuple(k[16]) == PLAIN)))

# choose points: per draw up to 8, spread on screen (>= 120 px apart) and over different atlas colours
for e in (950, 960):
    ch = []
    for f in sorted(allpix[e], key=lambda k: (k[14] != k[4], k[0])):
        X, Y = f[2], f[3]
        if any(abs(X - g[2]) < 12 and abs(Y - g[3]) < 12 for g in ch):
            continue
        ch.append(f)
        if len(ch) >= 8:
            break
    for i, f in enumerate(ch):
        spread, fp, X, Y, t, u, v, tx, ty, mean, c8, cl, ncov, zt, fm, zfm, fc8 = f
        name = 'Q%d_%d' % (e, i + 1)
        P('  %s eid %d px (%d,%d) prim %d uv (%.5f,%.5f) texel (%d,%d) sRGB %s footprint %.2f spread %.4f '
          'expected linear mean (%.4f %.4f %.4f) covering triangles of the draw %d depth %.6f; front-most prim %d depth %.6f texel sRGB %s' % (
              name, e, X, Y, t, u, v, tx, ty, tuple(c8), fp, spread, mean[0], mean[1], mean[2], ncov, zt, fm, zfm, tuple(fc8)))
        picked.append({'name': name, 'eid': e, 'x': X, 'y': Y, 'prim': t, 'u': u, 'v': v, 'tx': tx, 'ty': ty,
                       'srgb': c8, 'expected': mean, 'footprint': fp, 'spread': spread, 'depth': zt,
                       'front_prim': fm, 'front_depth': zfm, 'front_srgb': fc8})
ok &= len(picked) >= 3
json.dump(picked, open(os.path.join(RD, 'probe_pts.json'), 'w'), indent=1)
P('  points written: %d -> rd/probe_pts.json' % len(picked))

# picture: atlas with the picked texels
im2 = im.resize((1024, 1024))
d = ImageDraw.Draw(im2)
for p in picked:
    cx, cy = p['tx'] / TW * 1024, p['ty'] / TH * 1024
    col = (255, 0, 0) if p['eid'] == 950 else (0, 200, 0)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=col, width=2)
    d.text((cx + 8, cy - 6), p['name'], fill=col)
im2.save(os.path.join(RD, 'probe_pick.png'))
P('== picture rd/probe_pick.png (red 950, green 960)')
P('ALL OK' if ok else 'FAIL')
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(0 if ok else 1)
