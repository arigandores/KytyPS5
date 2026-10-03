"""ana_f7b.py - F7b (HPP-398): offline analysis of the RenderDoc replay outputs of rd_f7b.py (phases hist, vsout).
No GPU, no game.  Input: C:/kyty/f287/f7b/rd/*.  Output: C:/kyty/f287/f7b/ana_f7b.txt and rd/uv_floor_on_12274.png.
Members:
  (1) pixel history of the floor points on the G-buffer targets (draws 950/960 floor, 1028 rim, 1197 Astro, 1321 saucer);
  (2) albedo texel of the plain atlas region (tex 12274, BC7_SRGB) vs the RT0 value of the floor;
  (3) floor material constants searched for the RT0 colour (linear, sRGB);
  (4) floor UV (VS out_param_1.xy = PS in_param_1.xy, the coordinate of image_3[5] = tex 12274) statistics;
  (5) BC7 blocks of tex 12274 under the floor triangles (barycentric grid 12 per triangle);
  (6) wireframe of the floor UV over the atlas.
Ends with ALL OK when every member produced its line.
"""
import collections
import glob
import math
import os
import re
import struct
import sys

from PIL import Image, ImageDraw

RD = 'C:/kyty/f287/f7b/rd'
OUT = 'C:/kyty/f287/f7b/ana_f7b.txt'
lines = []


def P(*a):
    lines.append(' '.join(str(x) for x in a))


def s2l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def l2s(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


ok = True

# (1) pixel history on G-buffer targets
P('== (1) pixel history (rd_f7b_hist.txt), targets 6683 RT0 R8G8B8A8_SRGB, 6657 RT1, 6647 RT2 RGBA16F, 6685 RT3, 13050 RT4')
cur = None
n1 = 0
for l in open(os.path.join(RD, 'rd_f7b_hist.txt'), encoding='utf-8'):
    l = l.rstrip('\r\n')
    if l.startswith('-- HIST'):
        m = re.match(r'-- HIST (\S+) \((\d+),(\d+)\) on tex (\d+)', l)
        cur = m.groups()
        continue
    if cur and cur[3] in ('6683', '6657', '6647', '6685', '13050', '5685') and l.startswith('   eid'):
        m = re.match(r'\s+eid (\d+).*passed=(\w+).*out=(\([^)]*\)) post=(\([^)]*\))', l)
        if m and m.group(2) == 'True' and m.group(1) in ('302', '950', '960', '1028', '1197', '1321'):
            P('  %s (%s,%s) tex %s eid %s out=%s post=%s' % (cur[0], cur[1], cur[2], cur[3], m.group(1), m.group(3), m.group(4)))
            n1 += 1
ok &= n1 > 0

# (2) plain atlas texel
im = Image.open(os.path.join(RD, 'tex_12274_e950_m0.png')).convert('RGB')
W, H = im.size
px = im.load()
P('== (2) tex 12274 mip0 %dx%d sampled texels (sRGB 8 bit) and linear' % (W, H))
for (x, y) in [(0, 0), (10, 10), (100, 300), (300, 1000), (50, 1900), (150, 1500), (380, 600)]:
    c = px[x, y]
    P('  (%d,%d) %s linear %s' % (x, y, c, [round(s2l(v), 4) for v in c]))
ok &= px[100, 300] == (204, 205, 215)

# (3) constants
P('== (3) material constants of draw 950 searched for RT0 colour (tolerance 0.004)')
tgt = [0.6055, 0.6094, 0.6797]
cands = {'linear': tgt, 'srgb': [l2s(c) for c in tgt], 'lin_of': [s2l(c * 255) for c in tgt]}
found = 0
for f in sorted(glob.glob(os.path.join(RD, 'buf_e950_*.bin'))):
    d = open(f, 'rb').read()
    n = len(d) // 4
    fl = struct.unpack('<%df' % n, d[:n * 4])
    for i in range(n - 2):
        for k, c in cands.items():
            if all(abs(fl[i + j] - c[j]) < 0.004 for j in range(3)):
                P('  match %s off %d %s' % (os.path.basename(f), i * 4, k))
                found += 1
P('  files %d, matches %d' % (len(glob.glob(os.path.join(RD, 'buf_e950_*.bin'))), found))

# (4) floor UV
P('== (4) floor UV = VS out_param_1.xy (post-VS byte offset 48 of stride 160)')
tris = {}
for e in (950, 960):
    vb = open(os.path.join(RD, 'vsout_e%d.bin' % e), 'rb').read()
    ib = open(os.path.join(RD, 'vsidx_e%d.bin' % e), 'rb').read()
    idx = struct.unpack('<%dH' % (len(ib) // 2), ib)
    nv = len(vb) // 160
    uv = [struct.unpack_from('<4f', vb, v * 160 + 48) for v in range(nv)]
    used = sorted(set(idx))
    us = [uv[v] for v in used]
    mn = [min(x[c] for x in us) for c in range(4)]
    mx = [max(x[c] for x in us) for c in range(4)]
    nd = len(set((round(x[0], 5), round(x[1], 5)) for x in us))
    same_zw = sum(1 for x in us if x[0] == x[2] and x[1] == x[3])
    plain = 0
    for x in us:
        tx = int((x[0] - math.floor(x[0])) * W) % W
        ty = int((x[1] - math.floor(x[1])) * H) % H
        plain += px[tx, ty] == (204, 205, 215)
    P('  eid %d indices %d vertices %d uv min %s max %s distinct xy %d; zw==xy %d; vertices on plain texel %d (%.1f%%)' % (
        e, len(idx), len(used), ['%.4g' % v for v in mn], ['%.4g' % v for v in mx], nd, same_zw, plain, 100.0 * plain / len(us)))
    tris[e] = (idx, uv)
ok &= len(tris) == 2

# (5) BC7 blocks under floor triangles
raw = open(os.path.join(RD, 'tex_12274_e950_m0.raw'), 'rb').read()
P('== (5) tex 12274 raw bytes %d (BC7 2048x2048 = %d)' % (len(raw), 2048 * 2048))
BW = 512
cnt = collections.Counter()
for e, (idx, uv) in tris.items():
    for t in range(0, len(idx) - 2, 3):
        pts = [uv[i] for i in idx[t:t + 3]]
        N = 12
        for a in range(N + 1):
            for b in range(N + 1 - a):
                c = N - a - b
                u = (pts[0][0] * a + pts[1][0] * b + pts[2][0] * c) / N
                v = (pts[0][1] * a + pts[1][1] * b + pts[2][1] * c) / N
                bx = min(BW - 1, int((u - math.floor(u)) * 2048) // 4)
                by = min(BW - 1, int((v - math.floor(v)) * 2048) // 4)
                cnt[(bx, by)] += 1
tot = sum(cnt.values())
kinds = collections.Counter()
for k, w in cnt.items():
    o = (k[1] * BW + k[0]) * 16
    kinds[raw[o:o + 16]] += w
P('  blocks touched %d, distinct BC7 blocks %d, samples %d' % (len(cnt), len(kinds), tot))
for blk, w in kinds.most_common(5):
    P('  block %s weight %.2f%%' % (blk.hex(), 100.0 * w / tot))
ok &= len(kinds) > 0

# (6) wireframe
im2 = im.resize((1024, 1024))
d = ImageDraw.Draw(im2)
col = {950: (255, 0, 0), 960: (0, 200, 0)}
for e, (idx, uv) in tris.items():
    for t in range(0, len(idx) - 2, 3):
        p = [(uv[i][0] * 1024, uv[i][1] * 1024) for i in idx[t:t + 3]]
        d.line(p + [p[0]], fill=col[e], width=1)
fn = os.path.join(RD, 'uv_floor_on_12274.png')
im2.save(fn)
P('== (6) wireframe %s (red 950, green 960)' % fn)

P('ALL OK' if ok else 'FAIL')
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('\n'.join(lines[-12:]))
sys.exit(0 if ok else 1)
