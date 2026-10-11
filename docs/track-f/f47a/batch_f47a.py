# F47a (HPP-802): for each recording of the list - level, named start n (n_start), d_tail = last present - last FrameTrace
# n (tail_f47a.py; checked against the DiagF5Ev pairs of four logs: |d_tail - d_early| <= 3), and the block runs of the title
# band (det_f47a.py rule, numpy): black K >= TK (max channel <= 16), white Wt >= TW (min channel >= 240), in the video window
# [n_start + d + LO, n_start + d + HI]. For every run: video frames, presents and dn = present - d - n_start (the phase in
# FrameTrace n from the named start line). No judgement - data for the report and the sheet.
# Usage: python batch_f47a.py <map.tsv rows: tag mp4 log> <out.tsv> [--lo 600] [--hi 950] [--tk 150] [--tw 1000]
import re, subprocess, sys
import numpy as np

RXN = re.compile(rb'^FrameTrace: n=(\d+) ')
args = sys.argv
lst, outp = args[1], args[2]
LO = int(args[args.index('--lo') + 1]) if '--lo' in args else 600
HI = int(args[args.index('--hi') + 1]) if '--hi' in args else 950
TK = int(args[args.index('--tk') + 1]) if '--tk' in args else 150
TW = int(args[args.index('--tw') + 1]) if '--tw' in args else 1000
W, H, BAND_H = 480, 270, 81


def scan_log(logp):
    n = None
    start, pend, lvl = None, False, ''
    with open(logp, 'rb') as f:
        for line in f:
            m = RXN.match(line)
            if m:
                n = int(m.group(1))
                if pend:
                    start, pend = n, False
                continue
            if start is None and not pend and b'Level has started:' in line:
                t = line.split(b'started:', 1)[1].strip()
                if t:
                    lvl, pend = t.decode('utf-8', 'replace'), True
    return lvl, start, n


def runs(v):
    out = []
    for x in v:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def detect(mp4, a, b):
    sel = "select='between(n%s%d%s%d)',scale=%d:%d" % (chr(92) + ',', a, chr(92) + ',', b, W, H)
    proc = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp4, '-vf', sel, '-vsync', '0', '-f', 'rawvideo',
                           '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
    arr = np.frombuffer(proc.stdout, dtype=np.uint8)
    nfr = arr.size // (W * H * 3)
    arr = arr[:nfr * W * H * 3].reshape(nfr, H, W, 3)[:, :BAND_H]
    k = (arr.max(axis=3) <= 16).sum(axis=(1, 2))
    w = (arr.min(axis=3) >= 240).sum(axis=(1, 2))
    return nfr, k, w


rows = [l.rstrip('\n').split('\t') for l in open(lst, encoding='utf-8') if l.strip() and not l.startswith('#')]
with open(outp, 'w', encoding='utf-8', newline='\n') as out:
    out.write('# batch_f47a.py LO %d HI %d TK %d TW %d band y<%d of %dx%d\n' % (LO, HI, TK, TW, BAND_H, W, H))
    out.write('tag\tlevel\tn_start\tlast_n\tlast_present\td\twin_vf\tdecoded\tblack_runs(vf;present;dn)\twhite_runs(vf;present;dn)\tmaxK\tmaxW\n')
    for tag, mp4, logp in rows:
        lvl, start, last_n = scan_log(logp)
        pres = {}
        last_p = None
        for ln in open(mp4 + '.idx', encoding='ascii'):
            p = ln.split()
            if len(p) >= 2:
                pres[int(p[0])] = int(p[1])
                last_p = int(p[1])
        if start is None or last_n is None or last_p is None:
            out.write('%s\t%s\t%s\t%s\t%s\t-\t-\t0\tNO_START\t\t\t\n' % (tag, lvl, start, last_n, last_p))
            out.flush()
            continue
        d = last_p - last_n
        a, b = max(0, start + d + LO - 1), start + d + HI - 1
        nfr, k, w = detect(mp4, a, b)

        def fmt(hits):
            s = []
            for x, y in runs(hits):
                px, py = pres.get(x), pres.get(y)
                s.append('%d-%d;%s-%s;%s-%s' % (x, y, px, py, (px - d - start) if px else '?', (py - d - start) if py else '?'))
            return ' '.join(s) or '-'

        hk = [a + i for i in range(nfr) if k[i] >= TK]
        hw = [a + i for i in range(nfr) if w[i] >= TW]
        out.write('%s\t%s\t%d\t%d\t%d\t%d\t%d-%d\t%d\t%s\t%s\t%d\t%d\n' % (
            tag, lvl, start, last_n, last_p, d, a, b, nfr, fmt(hk), fmt(hw), int(k.max()) if nfr else 0,
            int(w.max()) if nfr else 0))
        out.flush()
        print(tag, 'done', flush=True)
