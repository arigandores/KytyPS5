# F44a (HPP-791, ROADMAP s122 item 698(d)(1)): driver and reader of the F29 stand f29_fault_stand.
# run:  python run_stand_f44a.py run <exe> <seed> <R> <out dir>   - runs KYTY_FIX_F29=0 then =1 (separate processes),
#       then reads; output <out dir>/f29_<k>.tsv, .tsv.log, .out
# read: python run_stand_f44a.py read <seed> <R> <out dir>         - reads existing outputs only
# Members (F43a section 3, ROADMAP s122 item 698(d)(1)): zero invariants, identities, G1, G2, P0 (=0), P1 (=1), H, lines.
# Prints one line per member with PASS/FAIL and counts; last line ALL OK / FAIL. A dead P0 or G1 prints STAND DEFECT
# (edition 2 of the stand, not a failure of the fix - item 698(d)(1)).
import os, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
ARMS = ['S0', 'S1', 'S2', 'E1', 'O1', 'O7', 'D1', 'L']
ONE_BIT = {'S1', 'S2', 'E1', 'O1', 'O7', 'L'}
BITS = {'S0': 0, 'S1': 1000, 'S2': 1023, 'E1': 1024, 'O1': 1100, 'O7': 1100, 'D1': 1120, 'L': 1100}
AREA = {'S0': 0, 'S1': 0, 'S2': 3, 'E1': 0, 'O1': 0, 'O7': 7, 'D1': 0, 'L': 0}
OVER = {'E1', 'O1', 'O7', 'D1', 'L'}
LAST = 1023
LINES_CAP = 32
INT_COLS = ['seed', 'fix', 'rep', 'seq', 'area', 'bits', 'words', 'raw', 'raw_hi', 'stored', 'read', 'read_vis',
            'out_area', 'out_buf', 'cls_zero', 'cls_low', 'cls_page', 'cls_exit', 'extra', 'dup', 'map_left',
            'nb_touched', 'h_inproc']


def load(path):
    lines = open(path, encoding='utf-8').read().split(chr(10))
    head = lines[0].split(chr(9))
    rows = []
    for l in lines[1:]:
        if not l:
            continue
        r = dict(zip(head, l.split(chr(9))))
        for c in INT_COLS:
            r[c] = int(r[c])
        rows.append(r)
    return rows


def log_lines(path):
    out = []
    for l in open(path, 'rb').read().decode('utf-8', 'replace').split(chr(10)):
        i = l.find('FixF29:')
        if i >= 0:
            out.append(l[i:].strip())
    return out


class Book:
    def __init__(self):
        self.ok = True
        self.defect = False

    def member(self, name, bad, total, note=''):
        st = 'PASS' if bad == 0 and total > 0 else 'FAIL'
        if st == 'FAIL':
            self.ok = False
        print('%-34s %s bad=%d of %d %s' % (name, st, bad, total, note))
        return st == 'PASS'


def read(seed, reps, out):
    b = Book()
    data = {}
    for k in (0, 1):
        tsv = os.path.join(out, 'f29_%d.tsv' % k)
        rows = load(tsv)
        data[k] = rows
        txt = open(os.path.join(out, 'f29_%d.out' % k), encoding='utf-8', errors='replace').read()
        b.member('[%d] stdout FIXF29 on=%d, DONE rows=%d' % (k, k, reps * 8),
                 0 if ('FIXF29 env=%d on=%d' % (k, k)) in txt and ('DONE rows=%d' % (reps * 8)) in txt else 1, 1)
        shape = sum(1 for r in rows if r['seed'] != seed or r['fix'] != k)
        per = {}
        for r in rows:
            per.setdefault((r['rep'], r['arm']), 0)
            per[(r['rep'], r['arm'])] += 1
        shape += sum(1 for rep in range(reps) for a in ARMS if per.get((rep, a), 0) != 1)
        shape += sum(1 for r in rows if r['area'] != AREA[r['arm']] or r['bits'] != BITS[r['arm']])
        b.member('[%d] rows: seed, fix, R x 8 arms, area, bits' % k, shape, len(rows))
        # zero invariants
        z = sum(1 for r in rows for c in ('extra', 'dup', 'map_left', 'nb_touched', 'raw_hi') if r[c] != 0)
        b.member('[%d] zero extra/dup/map_left/nb/raw_hi' % k, z, len(rows) * 5)
        # identities
        idn = 0
        for r in rows:
            want_read = min(r['raw'], LAST) if k == 1 else r['raw']
            idn += r['read_vis'] != r['read']
            idn += r['read'] != want_read
            idn += r['out_area'] != max(0, r['read'] - LAST)
            idn += r['cls_zero'] + r['cls_low'] + r['cls_page'] + r['cls_exit'] != r['out_area']
            idn += r['arm'] in ONE_BIT and r['raw'] != r['bits']
            idn += r['stored'] != min(r['bits'], LAST)
        b.member('[%d] identities (6 per row)' % k, idn, len(rows) * 6)
        # G1
        g1 = 0
        n1 = 0
        for r in rows:
            if r['arm'] in OVER:
                n1 += 1
                g1 += r['raw'] <= LAST
                if r['arm'] == 'D1':
                    g1 += not (1024 <= r['raw'] <= 1058)
            if r['arm'] in ONE_BIT:
                n1 += 1
                g1 += r['raw'] != r['bits']
        if not b.member('[%d] G1 raw > 1023, one-bit raw = B, D1' % k, g1, n1):
            b.defect = True
        # G2
        g2 = sum(1 for r in rows if (r['bits'] >= 1024 and r['stored'] != LAST) or
                 (r['arm'] in ('S1', 'S2') and r['stored'] != r['bits']))
        b.member('[%d] G2 stored = 1023 / = B' % k, g2, sum(1 for r in rows if r['bits'] >= 1024 or r['arm'] in ('S1', 'S2')))
        ll = log_lines(os.path.join(out, 'f29_%d.tsv.log' % k))
        if k == 0:
            p0 = 0
            n0 = 0
            for r in rows:
                a = r['arm']
                if a == 'O1':
                    n0 += 1
                    p0 += not (r['out_area'] == 77 and r['cls_low'] == 1 and r['cls_page'] == 76 and r['out_buf'] == 0)
                elif a == 'O7':
                    n0 += 1
                    p0 += not (r['out_buf'] == 77 and r['cls_exit'] == 77)
                elif a == 'E1':
                    n0 += 1
                    p0 += r['out_area'] != 1
                elif a == 'L':
                    n0 += 1
                    p0 += r['cls_low'] < 1
            if not b.member('[0] P0 O1 77 (1+76), O7 buf 77 exit 77, E1 1, L low>=1', p0, n0):
                b.defect = True
            b.member('[0] lines FixF29: none', len(ll), 1, '(lines %d)' % len(ll))
        else:
            p1 = sum(1 for r in rows for c in ('out_area', 'out_buf', 'cls_low', 'cls_exit') if r[c] != 0)
            p1 += sum(1 for r in rows if r['raw'] > LAST and r['read'] != LAST)
            b.member('[1] P1 0 reads past area/buffer, read 1023', p1, len(rows) * 4)
            over = [r for r in sorted(rows, key=lambda r: r['seq']) if r['raw'] > LAST]
            want = []
            for i, r in enumerate(over[:LINES_CAP]):
                want.append('FixF29: overflow pass=%d area=%d count=%d read=%d total=%d' %
                            (r['seq'], r['area'], r['raw'], LAST, i + 1))
            bad = 0 if ll == want else 1 + abs(len(ll) - len(want))
            b.member('[1] lines overflow = min(32, %d), fields' % len(over), bad, 1, '(lines %d)' % len(ll))
    # H
    by = {k: {(r['rep'], r['arm']): r for r in data[k]} for k in (0, 1)}
    h = 0
    n = 0
    for rep in range(reps):
        for a in ('S0', 'S1', 'S2'):
            n += 1
            r0, r1 = by[0][(rep, a)], by[1][(rep, a)]
            h += not (r1['h_sha'] == r0['h_sha'] == r0['exp_sha'] == r1['exp_sha'])
        for a in ('E1', 'O1', 'D1'):
            n += 1
            h += by[1][(rep, a)]['h_inproc'] != 1
    b.member('H S0-S2 sorted =1 = =0 = expected; E1/O1/D1 h_inproc', h, n)
    hin = sum(1 for r in data[1] if r['h_inproc'] != 1) + sum(1 for r in data[0] if r['h_inproc'] != -1)
    b.member('h_inproc all =1 rows 1, =0 rows -1', hin, len(data[0]) + len(data[1]))
    if b.defect:
        print('STAND DEFECT (dead P0 or G1)')
    print('ALL OK' if b.ok else 'FAIL')
    return 0 if b.ok else 1


def run(exe, seed, reps, out):
    os.makedirs(out, exist_ok=True)
    for k in (0, 1):
        if os.path.exists(LOCK) or os.path.exists(STOP):
            print('LOCK or STOP')
            return 3
        env = dict(os.environ)
        env['KYTY_FIX_F29'] = str(k)
        tsv = os.path.join(out, 'f29_%d.tsv' % k)
        with open(os.path.join(out, 'f29_%d.out' % k), 'w', encoding='utf-8') as o:
            rc = subprocess.run([exe, str(seed), str(reps), tsv], env=env, stdout=o, stderr=subprocess.STDOUT).returncode
        print('process KYTY_FIX_F29=%d rc=%d' % (k, rc))
        if rc != 0:
            print('FAIL')
            return 1
    return read(seed, reps, out)


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    if sys.argv[1] == 'run':
        sys.exit(run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]))
    sys.exit(read(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]))


main()
