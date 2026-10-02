# glitch145.py - Session Auditor, s145 step 3 (HPP-353), debt D-4 of s144: own detector of one-frame glitches.
# No code of C:/kyty/scripts/s51_vidglitch.py (the sealed detector) - only its RULE, read from the file:
#   frame i is a one-frame glitch when d1 = mean|f[i]-f[i-1]| > T and d2 = mean|f[i+1]-f[i]| > T and
#   back = mean|f[i+1]-f[i-1]| < 0.35 * min(d1, d2); T = 4 gray levels (the sealed call "s51_vidglitch.py <mp4> 4 6").
# Own implementation: integer absolute differences, sums per tile of a 4x4 grid (240x135 px), the whole-frame means are
# derived from the tile sums. Beyond the letter (data, not a verdict):
#   - the same rule at T = 2 and at ratio 0.6 (near misses);
#   - the same rule per tile (T = 4 and T = 12 on the tile means): local one-frame changes that the whole-frame mean hides;
#   - the distribution of "back" (two-frame motion) - the smallest whole-frame change the rule can see is max(T, back / 0.35).
# READ ONLY for the videos. Usage: python glitch145.py <out.json> <video> [<video> ...] [--workers N]
import sys, os, json, subprocess, hashlib, statistics
from multiprocessing import Pool

import numpy as np

W, H, GX, GY = 960, 540, 4, 4
T, RATIO = 4.0, 0.35
NPIX = W * H
TPIX = (W // GX) * (H // GY)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def tiles(a, b):
    d = np.abs(a - b)
    return d.reshape(GY, H // GY, GX, W // GX).sum(axis=(1, 3), dtype=np.int64)


def scan(path):
    R = {'path': path, 'sha256': sha(path)}
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path],
                        capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip().split(',')
    if [int(x) for x in pr[:2]] != [W, H]:
        R['error'] = 'size %r' % (pr,)
        return R
    rd = subprocess.Popen(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', path, '-vf', 'format=gray', '-f', 'rawvideo', '-'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    f0 = f1 = None            # frames i-1 and i (int16)
    s01 = None                # tile sums |f[i]-f[i-1]|
    n = 0
    ev, ev_t2, ev_r6 = [], [], []
    tev4 = tev12 = 0
    ttop = []
    backs = []
    d1s = []
    best_q = (0.0, None)      # largest min(d1,d2) among frames with back < 0.35*min (any T)
    while True:
        buf = rd.stdout.read(NPIX)
        if len(buf) < NPIX:
            break
        f2 = np.frombuffer(buf, np.uint8).reshape(H, W).astype(np.int16)
        if f1 is not None:
            s12 = tiles(f2, f1)
            if f0 is not None:
                s02 = tiles(f2, f0)
                i = n - 1                               # index of the middle frame f1
                d1, d2, back = float(s01.sum()) / NPIX, float(s12.sum()) / NPIX, float(s02.sum()) / NPIX
                backs.append(back)
                d1s.append(d1)
                m = min(d1, d2)
                if back < RATIO * m:
                    if m > best_q[0]:
                        best_q = (m, i)
                    if d1 > T and d2 > T:
                        ev.append([i, round(d1, 2), round(d2, 2), round(back, 2)])
                    if d1 > 2.0 and d2 > 2.0:
                        ev_t2.append([i, round(d1, 2), round(d2, 2), round(back, 2)])
                if d1 > T and d2 > T and back < 0.6 * m:
                    ev_r6.append([i, round(d1, 2), round(d2, 2), round(back, 2)])
                t1, t2, tb = s01 / TPIX, s12 / TPIX, s02 / TPIX
                tm = np.minimum(t1, t2)
                hit = (t1 > T) & (t2 > T) & (tb < RATIO * tm)
                if hit.any():
                    tev4 += 1
                    k = int(np.argmax(np.where(hit, tm, 0)))
                    v = float(tm.flat[k])
                    if v > 12.0:
                        tev12 += 1
                    ttop.append([i, k // GX, k % GX, round(float(t1.flat[k]), 1), round(float(t2.flat[k]), 1), round(float(tb.flat[k]), 1), int(hit.sum())])
            s01 = s12
        f0, f1 = f1, f2
        n += 1
    err = rd.stderr.read().decode('utf-8', 'replace')
    rd.wait()
    ttop.sort(key=lambda x: -min(x[3], x[4]))
    backs.sort()
    R.update({'frames': n, 'rc': rd.returncode, 'decoder_error_lines': len([x for x in err.splitlines() if x.strip()]),
              'glitches': ev, 'glitches_T2': len(ev_t2), 'glitches_T2_first': ev_t2[:5], 'glitches_ratio06': len(ev_r6), 'glitches_ratio06_first': ev_r6[:5],
              'largest_returning_change': [round(best_q[0], 3), best_q[1]],
              'tile_events_T4': tev4, 'tile_events_T12': tev12, 'tile_top': ttop[:8],
              'back_median': round(statistics.median(backs), 3) if backs else None,
              'back_p90': round(backs[int(len(backs) * 0.9)], 3) if backs else None,
              'd1_median': round(statistics.median(d1s), 3) if d1s else None,
              'still_frames_d1_lt_0.05': sum(1 for x in d1s if x < 0.05)})
    return R


def main():
    outp = sys.argv[1]
    args = sys.argv[2:]
    workers = 4
    if '--workers' in args:
        k = args.index('--workers')
        workers = int(args[k + 1])
        args = args[:k] + args[k + 2:]
    with Pool(workers) as pool:
        res = pool.map(scan, args, chunksize=1)
    json.dump(res, open(outp, 'w', encoding='ascii'), ensure_ascii=True, indent=1)
    for R in res:
        if 'error' in R:
            print('GLITCH %s: %s' % (os.path.basename(R['path']), R['error']))
            continue
        bm = R['back_median'] or 0
        print('GLITCH %s sha %s: frames %d (ffmpeg rc %s, decoder error lines %d); ONE-FRAME GLITCHES by the rule of the seal (T 4, ratio 0.35): %d %s; '
              'near misses: T 2 -> %d %s, ratio 0.6 -> %d %s; largest change that returned (min(d1,d2) with back < 0.35 min): %s gray levels at frame %s; '
              'two-frame motion "back": median %s, p90 %s (smallest visible whole-frame change max(4, back/0.35): median %.1f, p90 %.1f gray levels); '
              'frames with d1 < 0.05 (still picture) %d; per-tile rule (4x4 grid): frames with a tile event T 4: %d, T 12: %d; top tile events (frame, row, col, d1, d2, back, tiles) %s' % (
                  os.path.basename(R['path']), R['sha256'][:16], R['frames'], R['rc'], R['decoder_error_lines'], len(R['glitches']), R['glitches'][:6],
                  R['glitches_T2'], R['glitches_T2_first'][:3], R['glitches_ratio06'], R['glitches_ratio06_first'][:3],
                  R['largest_returning_change'][0], R['largest_returning_change'][1], R['back_median'], R['back_p90'],
                  max(4.0, bm / 0.35), max(4.0, (R['back_p90'] or 0) / 0.35), R['still_frames_d1_lt_0.05'],
                  R['tile_events_T4'], R['tile_events_T12'], R['tile_top'][:5]))
    print('VIDEOS %d' % len(res))
    print('ALL DONE')


if __name__ == '__main__':
    main()
