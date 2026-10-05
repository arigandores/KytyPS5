"""rc602.py - S15r (HPP-602), Red Team: own recount, independent of sc_s / sc_s15 code.
(i) T-1 / T-2 / T-6 of k_01, k_02 (S13b logs) by the row and by frame=; (ii) Sky Garden first 120 s after the first scene frame.
Streaming, binary. ASCII output."""
import hashlib
import re
import sys

RXN = re.compile(rb'^FrameTrace: n=(\d+) ')
RXF = re.compile(rb' (dt_us|draws)=(\d+)')
RXX = re.compile(rb'^FrameTrace-x: n=(\d+) ')
RXSK = re.compile(rb' skc_ap_skip=(\d+)')
RXHI = re.compile(rb' skc_held_inc=(\d+)')
RXFR = re.compile(rb'frame=(\d+)')
RXHF = re.compile(rb'^AsyncPipelines: flip (\d+) held')
ST = b'GuestOut: Level has started:'


def scan(path):
    h = hashlib.sha256()
    rows, x, skips, held, starts = [], {}, [], [], []
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            m = RXN.match(line)
            if m:
                d = dict((k, int(v)) for k, v in RXF.findall(line))
                if b'dt_us' in d:
                    rows.append((int(m.group(1)), d[b'dt_us'], d.get(b'draws', -1)))
                continue
            m = RXX.match(line)
            if m:
                a = RXSK.search(line)
                b = RXHI.search(line)
                x[int(m.group(1))] = (int(a.group(1)) if a else 0, int(b.group(1)) if b else 0)
                continue
            if line.startswith(b'AsyncPipelines: skipped draw'):
                fr = RXFR.search(line)
                skips.append((len(rows), int(fr.group(1)) if fr else None))
                continue
            m = RXHF.match(line)
            if m:
                held.append((len(rows), int(m.group(1))))
                continue
            if line.startswith(ST):
                starts.append((len(rows), line[len(ST):].strip().decode('latin1')))
    return dict(rows=rows, x=x, skips=skips, held=held, starts=starts, sha=h.hexdigest())


def locate(s, level):
    idx = [j for j, t in enumerate(s['starts']) if t[1] == level]
    if not idx:
        return None, None, None
    eg = s['starts'][idx[0]][0]
    end = s['starts'][idx[0] + 1][0] if idx[0] + 1 < len(s['starts']) else len(s['rows'])
    fi = next((i for i in range(eg, end) if s['rows'][i][2] >= 100), None)
    return eg, end, fi


def ident(path, level):
    s = scan(path)
    eg, end, fi = locate(s, level)
    rows = s['rows']
    lo = max(fi if fi is not None else (eg or 0), 1)
    nlo = rows[lo][0]
    sk = sum(s['x'].get(rows[i][0], (0, 0))[0] for i in range(lo, len(rows)))
    hi = sum(s['x'].get(rows[i][0], (0, 0))[1] for i in range(lo, len(rows)))
    by_row = [e for e in s['skips'] if e[0] >= lo]
    by_fr = [e for e in s['skips'] if e[1] is not None and e[1] >= nlo]
    hin = sum(1 for g, n in s['held'] if n >= nlo)
    hbef = sum(1 for g, n in s['held'] if n < nlo)
    print('%s %s sha256 %s rows %d eg %s fi %s lo %d n_lo %d' % (path.split('/')[-1], level, s['sha'], len(rows), eg, fi, lo, nlo))
    print('  T-1 by row: sum skc_ap_skip(rows>=lo) %d vs lines g>=lo %d; by frame>=n_lo: lines %d' % (sk, len(by_row), len(by_fr)))
    print('  T-6 by row: distinct frame= %d vs sum held_inc %d' % (len(set(e[1] for e in by_row if e[1] is not None)), hi))
    print('  T-2: held lines N>=n_lo %d, before %d, total %d; sum held_inc(rows>=lo) %d; min(64-before, hi) %d' % (
        hin, hbef, len(s['held']), hi, min(max(0, 64 - hbef), hi)))
    # the S13b form: rows from fi (index) and lines by frame= >= n of fi
    if fi is not None:
        nfi = rows[fi][0]
        sk2 = sum(s['x'].get(rows[i][0], (0, 0))[0] for i in range(fi, len(rows)))
        l2 = sum(1 for e in s['skips'] if e[1] is not None and e[1] >= nfi)
        h2 = sum(1 for g, n in s['held'] if n >= nfi)
        hi2 = sum(s['x'].get(rows[i][0], (0, 0))[1] for i in range(fi, len(rows)))
        print('  S13b form (frame>=n_fi %d): T-1 %d / %d; T-2 lines %d / held_inc %d' % (nfi, l2, sk2, h2, hi2))
        # the boundary lines
        for e in s['skips']:
            if (e[0] < fi) != (e[1] is not None and e[1] < nfi):
                print('  boundary skip line: group %d (row n %s) frame=%s' % (e[0], rows[e[0]][0] if e[0] < len(rows) else '-', e[1]))
    for g, n in s['held']:
        if g == 0:
            print('  held line before the first FrameTrace row: flip %d' % n)


def sky(path, level):
    s = scan(path)
    eg, end, fi = locate(s, level)
    rows = s['rows']
    acc, j = 0, fi + 1
    while j < len(rows) and acc < 120000000:
        acc += rows[j][1]
        j += 1
    n = j - fi - 1
    long = sum(1 for i in range(fi + 1, j) if rows[i][1] >= 100000)
    print('%s sha256 %s fi %d: first 120 s rows %d presented %.1f s frames/s %.2f >=100ms %d' % (
        path, s['sha'][:16], fi, n, acc / 1e6, n / (acc / 1e6), long))


if __name__ == '__main__':
    if sys.argv[1] == 'ident':
        ident(sys.argv[2], sys.argv[3])
    else:
        sky(sys.argv[2], sys.argv[3])
