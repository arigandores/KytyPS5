"""F47e (HPP-810): own reading of the tag f47_hi (ROADMAP s122 item 708(d), 734): knob-action members from the log and the splash-window
block detector on the video, written anew (not batch_f47a.py / f47d_read.py).

    python hi_f47e.py <log> <rec.mp4> <rec.mp4.idx> [--fs13 <log fs13_v>]

Log members (edition 2 section 9): (1) sum img_imp over FrameTrace-draw lines = 0; (2) sum stg_img_pool_b + stg_img_in_b over
FrameTrace-x lines > 0; (4) number of FrameTrace-draw lines with img_imp = number of 'FrameTrace: n=' lines; (3) control - sum img_imp > 0
in fs13_v. Video: d = last present of .idx - last n of FrameTrace; window [n_start + d + 600 - 1; n_start + d + 950 - 1] in records;
480x270, band y < 81: K = max(R,G,B) <= 16, Wt = min(R,G,B) >= 240; black series K >= 150, white Wt >= 1000; dn = present - d - n_start.
"""
import re
import subprocess
import sys

import numpy as np


def scan_log(path):
    n_lines = 0
    draw_imp = 0
    sum_imp = 0
    stg = 0
    stg_in = 0
    named = None
    n_start = None
    last_n = None
    pat_n = re.compile(rb'FrameTrace: n=(\d+)')
    pat_imp = re.compile(rb'\bimg_imp=(\d+)')
    pat_pool = re.compile(rb'\bstg_img_pool_b=(\d+)')
    pat_in = re.compile(rb'\bstg_img_in_b=(\d+)')
    with open(path, 'rb') as f:
        for line in f:
            if b'FrameTrace' in line:
                m = pat_n.search(line)
                if m:
                    n_lines += 1
                    last_n = int(m.group(1))
                    if named is not None and n_start is None:
                        n_start = last_n
                if b'FrameTrace-draw' in line:
                    m = pat_imp.search(line)
                    if m:
                        draw_imp += 1
                        sum_imp += int(m.group(1))
                if b'FrameTrace-x' in line:
                    m = pat_pool.search(line)
                    if m:
                        stg += int(m.group(1))
                    m = pat_in.search(line)
                    if m:
                        stg_in += int(m.group(1))
            elif named is None and b'Level has started: ' in line:
                rest = line.split(b'Level has started: ', 1)[1].strip()
                if rest:
                    named = rest.decode('latin-1')
    return dict(n_lines=n_lines, draw_imp=draw_imp, sum_imp=sum_imp, stg_pool=stg, stg_in=stg_in, named=named, n_start=n_start, last_n=last_n)


def read_idx(path):
    rows = []
    for line in open(path, encoding='latin-1'):
        p = line.split()
        if len(p) >= 2 and p[0].isdigit():
            rows.append((int(p[0]), int(p[1])))
    return rows


def detect(rec, first, count):
    cmd = ['ffmpeg', '-v', 'error', '-i', rec, '-vf', 'select=between(n\\,%d\\,%d),scale=480:270' % (first, first + count - 1),
           '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
    fr = 480 * 270 * 3
    out = []
    for i in range(len(raw) // fr):
        a = np.frombuffer(raw[i * fr:(i + 1) * fr], dtype=np.uint8).reshape(270, 480, 3)[:81]
        k = int((a.max(axis=2) <= 16).sum())
        w = int((a.min(axis=2) >= 240).sum())
        out.append((first + i, k, w))
    return out


def series(rows, idx_of, key):
    s = []
    cur = []
    for (rec, k, w) in rows:
        hit = (k >= 150) if key == 'K' else (w >= 1000)
        if hit:
            cur.append(rec)
        elif cur:
            s.append(cur)
            cur = []
    if cur:
        s.append(cur)
    return s


def main():
    log, rec, idx = sys.argv[1], sys.argv[2], sys.argv[3]
    L = scan_log(log)
    print('log %s: FrameTrace n lines %d; FrameTrace-draw with img_imp %d; sum img_imp %d; sum stg_img_pool_b %d stg_img_in_b %d; '
          'named start %r; n_start %s; last n %s' % (log, L['n_lines'], L['draw_imp'], L['sum_imp'], L['stg_pool'], L['stg_in'], L['named'],
                                                     L['n_start'], L['last_n']))
    m1 = L['sum_imp'] == 0
    m2 = (L['stg_pool'] + L['stg_in']) > 0
    m4 = L['draw_imp'] == L['n_lines']
    ok = m1 and m2 and m4
    if '--fs13' in sys.argv:
        C = scan_log(sys.argv[sys.argv.index('--fs13') + 1])
        m3 = C['sum_imp'] > 0
        print('control fs13_v: sum img_imp %d (> 0: %s); draw lines with img_imp %d = n lines %d' % (C['sum_imp'], m3, C['draw_imp'], C['n_lines']))
        ok = ok and m3
    print('knob members: (1) sum img_imp = 0: %s; (2) staging > 0: %s; (4) draw lines = n lines: %s' % (m1, m2, m4))
    rows = read_idx(idx)
    last_present = rows[-1][1]
    d = last_present - L['last_n']
    lo = L['n_start'] + d + 600 - 1
    hi = L['n_start'] + d + 950 - 1
    pres = {r: p for (r, p) in rows}
    print('idx records %d, last present %d, d = %d; window records [%d; %d]' % (len(rows), last_present, d, lo, hi))
    det = detect(rec, lo, hi - lo + 1)
    print('decoded %d frames; max K %d max Wt %d' % (len(det), max(x[1] for x in det), max(x[2] for x in det)))
    for key in ('K', 'Wt'):
        for s in series(det, pres, key):
            p0 = pres.get(s[0])
            dn = (p0 - d - L['n_start']) if p0 is not None else None
            print('series %s: records %d-%d (%d frames) dn %s' % ('black' if key == 'K' else 'white', s[0], s[-1], len(s), dn))
    print('ALL OK' if ok else 'MEMBER FAIL')


main()
