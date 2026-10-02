"""tiles146.py - session 146 step 0 (HPP-386; ROADMAP s122 item 309 (i) debt D-4, (l)(4)): the data row "tile events" of one V video
and the triples for the lead's sheet.  The RULE is the auditor's tile rule of AUDIT145 s1.4 (C:/kyty/KytyPS5/docs/session-145/audit/
glitch145.py), re-implemented here (no code of glitch145.py and none of s51_vidglitch.py): the gray frames of the video (960x540),
a 4 x 4 grid of 240 x 135 px tiles, for the middle frame i of every three frames the tile means t1 = mean|f[i]-f[i-1]|,
t2 = mean|f[i+1]-f[i]|, tb = mean|f[i+1]-f[i-1]| (integer absolute differences summed per tile); a tile event at i when some
tile has t1 > T and t2 > T and tb < 0.35 * min(t1, t2), T = 4 (threshold 4 of item 309 (i) D-4); the frame's event names the
tile with the largest min(t1, t2) among its hit tiles (frame, row, col, t1, t2, tb, number of hit tiles).  The count at T 12
(the same frames with that largest min > 12) is printed beside, as the auditor printed it.  A data row, not a gate.
Output (ASCII), one line:
  TILES <video name> sha256 <64 hex>: frames <N>; tile events T4 <K>, T12 <K12>; events [[frame, row, col, t1, t2, tb, tiles], ...]
(all events, in frame order).  With --sheet <png>: the triples f[i-1], f[i], f[i+1] of at most MAX_TRIPLES events (the largest
min(t1, t2) first, then put in frame order), each frame 320 px wide, one triple per row, written with ffmpeg; no event - no sheet,
the line "SHEET none (0 events)".
    python tiles146.py <video.mp4> <out.txt> [--sheet <out.png>]
rc 0 written; rc 1 the video cannot be read (size other than 960x540, ffmpeg error); rc 2 usage.
"""
import hashlib
import os
import subprocess
import sys

import numpy as np

W, H, GX, GY = 960, 540, 4, 4
T, T12, RATIO = 4.0, 12.0, 0.35
NPIX = W * H
TPIX = (W // GX) * (H // GY)
MAX_TRIPLES = 12


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def tilesum(a, b):
    d = np.abs(a - b)
    return d.reshape(GY, H // GY, GX, W // GX).sum(axis=(1, 3), dtype=np.int64)


def frame_event(s01, s12, s02):
    """(row, col, t1, t2, tb, hit tiles) of the frame between the three, or None: the tile rule with threshold T."""
    t1, t2, tb = s01 / TPIX, s12 / TPIX, s02 / TPIX
    tm = np.minimum(t1, t2)
    hit = (t1 > T) & (t2 > T) & (tb < RATIO * tm)
    if not hit.any():
        return None
    k = int(np.argmax(np.where(hit, tm, 0)))
    return (k // GX, k % GX, round(float(t1.flat[k]), 1), round(float(t2.flat[k]), 1), round(float(tb.flat[k]), 1),
            int(hit.sum()))


def frames_gray(path):
    """Yield the gray frames (int16, H x W) of the video; raise ValueError on another size."""
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of',
                         'csv=p=0', path], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip().split(',')
    if [int(x) for x in pr[:2] if x.strip().isdigit()] != [W, H]:
        raise ValueError('size %r' % (pr,))
    rd = subprocess.Popen(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', path, '-vf', 'format=gray', '-f',
                           'rawvideo', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    try:
        while True:
            buf = rd.stdout.read(NPIX)
            if len(buf) < NPIX:
                break
            yield np.frombuffer(buf, np.uint8).reshape(H, W).astype(np.int16)
    finally:
        rd.stdout.close()
        rd.wait()


def scan(frames):
    """(number of frames, events) over an iterable of gray frames."""
    f0 = f1 = None
    s01 = None
    n = 0
    ev = []
    for f2 in frames:
        if f1 is not None:
            s12 = tilesum(f2, f1)
            if f0 is not None:
                x = frame_event(s01, s12, tilesum(f2, f0))
                if x is not None:
                    ev.append([n - 1] + list(x))
            s01 = s12
        f0, f1 = f1, f2
        n += 1
    return n, ev


def sheet(path, ev, out):
    """The triples of at most MAX_TRIPLES events into out.png (ffmpeg select + tile); returns the frames used."""
    top = sorted(ev, key=lambda e: -min(e[3], e[4]))[:MAX_TRIPLES]
    top.sort(key=lambda e: e[0])
    want = []
    for e in top:
        want.extend([e[0] - 1, e[0], e[0] + 1])
    sel = '+'.join('eq(n\\,%d)' % i for i in want)
    vf = "select='%s',scale=320:-1,tile=3x%d" % (sel, len(top))
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-i', path, '-vf', vf, '-frames:v', '1',
                        '-vsync', '0', out], capture_output=True, stdin=subprocess.DEVNULL)
    return r.returncode, [e[0] for e in top]


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    shp = None
    if '--sheet' in a:
        k = a.index('--sheet')
        if k + 1 >= len(a):
            print('usage: tiles146.py <video.mp4> <out.txt> [--sheet <out.png>]')
            return 2
        shp = a[k + 1]
        a = a[:k] + a[k + 2:]
    if len(a) != 2:
        print('usage: tiles146.py <video.mp4> <out.txt> [--sheet <out.png>]')
        return 2
    video, out = a
    try:
        n, ev = scan(frames_gray(video))
    except (ValueError, OSError) as e:
        line = 'TILES %s ERROR %s' % (os.path.basename(video), str(e)[:120])
        open(out, 'w', encoding='ascii').write(line + '\n')
        print(line)
        return 1
    t12 = sum(1 for e in ev if min(e[3], e[4]) > T12)
    line = 'TILES %s sha256 %s: frames %d; tile events T4 %d, T12 %d; events %s' % (
        os.path.basename(video), sha(video), n, len(ev), t12, ev)
    lines = [line]
    if shp is not None:
        if ev:
            rc, used = sheet(video, ev, shp)
            lines.append('SHEET %s rc %d triples of frames %s' % (os.path.basename(shp), rc, used))
        else:
            lines.append('SHEET none (0 events)')
    open(out, 'w', encoding='ascii').write('\n'.join(lines) + '\n')
    print('\n'.join(x[:300] for x in lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
