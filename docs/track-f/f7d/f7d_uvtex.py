"""f7d_uvtex.py - F7d (HPP-443, Red Team): offline check of PS 508 inputs other than the albedo atlas under the floor UV.

Reads only files already produced by F7b (C:/kyty/f287/f7b/rd): post-VS outputs of draws 950/960 (stride 160,
out_param_1 at byte 48 = UV), indices, and mip0 readbacks of image_3[0] (12226 BC4), image_3[3] (12222 BC5),
image_3[5] (12274 BC7, block identity only). No Vulkan device, no RenderDoc.
PS 508 (rd/ps_508.dis.txt): image_3[0] sampled at (u, v) lines 818-824; image_3[3] at (u, v) lines 1151-1159
(same %376/%380 as the atlas at 1961-1966); image_3[1]/[4] at a scaled detail UV (lines 840-857, 1198-1206).
Prints per image: share of floor samples within +-2/255 of the mode, percentiles, and writes crops of the
floor UV region (u 0..0.6667, v 0..0.5) as PNG for the sheet.
"""
import os, struct, sys, hashlib
import numpy as np

RD = 'C:/kyty/f287/f7b/rd'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f7d'
W = 2048
NB = W // 4


def P(*a):
    print(*a)


def bc4_blocks(raw, nblk, stride, off):
    """Decode nblk BC4 blocks (8 bytes each, at off within each stride) -> (nblk, 16) float32 0..1."""
    b = np.frombuffer(raw, dtype=np.uint8).reshape(nblk, stride)[:, off:off + 8]
    r0 = b[:, 0].astype(np.float32)
    r1 = b[:, 1].astype(np.float32)
    bits = np.zeros(nblk, dtype=np.uint64)
    for i in range(6):
        bits |= b[:, 2 + i].astype(np.uint64) << np.uint64(8 * i)
    idx = np.stack([((bits >> np.uint64(3 * k)) & np.uint64(7)).astype(np.int64) for k in range(16)], axis=1)
    pal = np.zeros((nblk, 8), dtype=np.float32)
    pal[:, 0] = r0
    pal[:, 1] = r1
    gt = r0 > r1
    for k in range(1, 7):
        pal[:, 1 + k] = np.where(gt, ((7 - k) * r0 + k * r1) / 7.0, pal[:, 1 + k])
    for k in range(1, 5):
        pal[:, 1 + k] = np.where(~gt, ((5 - k) * r0 + k * r1) / 5.0, pal[:, 1 + k])
    pal[:, 6] = np.where(~gt, 0.0, pal[:, 6])
    pal[:, 7] = np.where(~gt, 255.0, pal[:, 7])
    return np.take_along_axis(pal, idx, axis=1) / 255.0


def to_image(vals):
    """(NB*NB, 16) block texels -> (W, W) image, row-major blocks, texel k = (k % 4, k // 4)."""
    v = vals.reshape(NB, NB, 4, 4)
    return v.transpose(0, 2, 1, 3).reshape(W, W)


def load_bc4(name):
    raw = open(os.path.join(RD, name), 'rb').read()
    assert len(raw) == NB * NB * 8, (name, len(raw))
    return to_image(bc4_blocks(raw, NB * NB, 8, 0)), hashlib.sha256(raw).hexdigest()


def load_bc5(name):
    raw = open(os.path.join(RD, name), 'rb').read()
    assert len(raw) == NB * NB * 16, (name, len(raw))
    r = to_image(bc4_blocks(raw, NB * NB, 16, 0))
    g = to_image(bc4_blocks(raw, NB * NB, 16, 8))
    return r, g, hashlib.sha256(raw).hexdigest()


def floor_samples(eid, n=12):
    vb = open(os.path.join(RD, 'vsout_e%d.bin' % eid), 'rb').read()
    ib = open(os.path.join(RD, 'vsidx_e%d.bin' % eid), 'rb').read()
    nv = len(vb) // 160
    uv = np.array([struct.unpack_from('<2f', vb, v * 160 + 48) for v in range(nv)], dtype=np.float64)
    idx = np.array(struct.unpack('<%dH' % (len(ib) // 2), ib), dtype=np.int64).reshape(-1, 3)
    bary = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            bary.append(((i + 1.0 / 3) / (n + 1), (j + 1.0 / 3) / (n + 1)))
    bary = np.array([(a, b, 1 - a - b) for a, b in bary if a + b <= 1])
    t = uv[idx]  # (ntri, 3, 2)
    s = np.einsum('kc,tcd->tkd', bary, t).reshape(-1, 2)
    x = np.floor(np.mod(s[:, 0], 1.0) * W).astype(np.int64)
    y = np.floor(np.mod(s[:, 1], 1.0) * W).astype(np.int64)
    return x, y, len(idx), len(s)


def stats(tag, img, x, y):
    v = img[y, x]
    q = np.round(v * 255).astype(np.int64)
    vals, cnt = np.unique(q, return_counts=True)
    mode = vals[np.argmax(cnt)]
    near = np.mean(np.abs(q - mode) <= 2)
    pc = np.percentile(v, [1, 5, 50, 95, 99])
    P('%-34s n=%d mode=%d/255 within+-2=%.4f distinct=%d p1/p5/p50/p95/p99=%s std=%.4f' % (
        tag, len(v), mode, near, len(vals), ' '.join('%.3f' % p for p in pc), float(np.std(v))))
    return near


def save_png(path, img):
    a = np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)
    try:
        from PIL import Image
        Image.fromarray(a).save(path)
    except ImportError:
        h, w = a.shape[:2]
        c = 3 if a.ndim == 3 else 1
        with open(path[:-4] + '.ppm' if c == 3 else path[:-4] + '.pgm', 'wb') as f:
            f.write(b'P6' if c == 3 else b'P5')
            f.write(b' %d %d 255 ' % (w, h))
            f.write(a.tobytes())
    return hashlib.sha256(open(path, 'rb').read()).hexdigest() if os.path.exists(path) else 'n/a'


def main():
    os.makedirs(OUT, exist_ok=True)
    i0, h0 = load_bc4('tex_12226_e950_m0.raw')
    n3r, n3g, h3 = load_bc5('tex_12222_e950_m0.raw')
    i1, h1 = load_bc4('tex_15244_e950_m0.raw')
    n4r, n4g, h4 = load_bc5('tex_15245_e950_m0.raw')
    P('inputs sha256: 12226 %s / 12222 %s / 15244 %s / 15245 %s' % (h0[:16], h3[:16], h1[:16], h4[:16]))
    P('image min/max: [0] %.3f..%.3f  [3].r %.3f..%.3f [3].g %.3f..%.3f  [1] %.3f..%.3f  [4].r %.3f..%.3f' % (
        i0.min(), i0.max(), n3r.min(), n3r.max(), n3g.min(), n3g.max(), i1.min(), i1.max(), n4r.min(), n4r.max()))
    res = {}
    for e in (950, 960):
        x, y, nt, ns = floor_samples(e)
        P('== draw %d: triangles %d, samples %d (UV of out_param_1, wrap, nearest texel of mip0)' % (e, nt, ns))
        res[(e, 0)] = stats('image_3[0] 12226 BC4 R', i0, x, y)
        res[(e, 3)] = stats('image_3[3] 12222 BC5 R', n3r, x, y)
        res[(e, 4)] = stats('image_3[3] 12222 BC5 G', n3g, x, y)
    # crops of the floor UV region: u 0..2/3, v 0..1/2 (rd/uv_floor_on_12274.png region), 2x downscale
    ys, xs = slice(0, W // 2), slice(0, (2 * W) // 3)
    crop_n = np.stack([n3r[ys, xs], n3g[ys, xs], np.full_like(n3r[ys, xs], 0.5)], axis=-1)[::2, ::2]
    crop_0 = i0[ys, xs][::2, ::2]
    # contrast-stretched normal map (x8 around 0.5) to make small slopes visible
    crop_ns = np.clip((crop_n - 0.5) * 8.0 + 0.5, 0, 1)
    crop_ns[..., 2] = 0.5
    for nm, im in (('n3_floor_region.png', crop_n), ('n3_floor_region_x8.png', crop_ns), ('i0_floor_region.png', crop_0)):
        P('wrote %s sha256 %s' % (nm, save_png(os.path.join(OUT, nm), im)[:16]))
    # fixtures: BC4 decoder on hand-made blocks
    ok = True
    blk = bytes([255, 0]) + bytes(6)  # r0>r1, all idx 0 -> 1.0
    ok &= abs(float(bc4_blocks(blk, 1, 8, 0)[0, 0]) - 1.0) < 1e-6
    blk = bytes([0, 255]) + bytes([0b11111111] * 6)  # r0<=r1, all idx 7 -> 255
    ok &= abs(float(bc4_blocks(blk, 1, 8, 0)[0, 5]) - 1.0) < 1e-6
    blk = bytes([0, 255]) + bytes([0b10110110, 0b01101101, 0b11011011] * 2)  # all idx 6 -> 0
    ok &= abs(float(bc4_blocks(blk, 1, 8, 0)[0, 3])) < 1e-6
    blk = bytes([70, 0]) + bytes([0b01001001, 0b10010010, 0b00100100] * 2)  # r0>r1 idx 1 -> r1 = 0
    ok &= abs(float(bc4_blocks(blk, 1, 8, 0)[0, 7])) < 1e-6
    blk = bytes([140, 0]) + bytes([0b10010010, 0b00100100, 0b01001001] * 2)  # idx 2 -> (6*140+0)/7 = 120
    ok &= abs(float(bc4_blocks(blk, 1, 8, 0)[0, 0]) * 255 - 120.0) < 1e-3
    P('fixtures bc4 %s' % ('ok' if ok else 'FAIL'))
    P('ALL OK' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
