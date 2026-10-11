# FS14b (HPP-813, Red Team, ROADMAP s122 item 712(g)(2)): own recount of the f29_fault_stand outputs (independent of the
# reader of run_stand_f44a.py / run_stand_fs14a.py). Usage: python recount_fs14b.py <tsv default> <out default> <tsv =0> <out =0> <seed> <R>
# Members: process without the variable - stdout 'FIXF29 env=(unset) on=1', fix = 1 in every row, P1 (item 698(d)(1)):
# out_area = out_buf = cls_low = cls_exit = 0 in all rows, read = 1023 at E1 O1 O7 D1 L, extra = dup = map_left = 0,
# 8 arms x R rows with the seed; control =0 - stdout 'FIXF29 env=0 on=0', P0: O1 out_area = 77 and O7 out_buf = 77 in R of R.
import sys

ARMS = ['S0', 'S1', 'S2', 'E1', 'O1', 'O7', 'D1', 'L']
OVER = {'E1', 'O1', 'O7', 'D1', 'L'}


def load(p):
    ls = [l for l in open(p, encoding='utf-8').read().split(chr(10)) if l]
    h = ls[0].split(chr(9))
    return [dict(zip(h, l.split(chr(9)))) for l in ls[1:]]


def main():
    t1, o1, t0, o0, seed, reps = sys.argv[1:7]
    seed, reps = int(seed), int(reps)
    ok = True

    def check(name, cond, info=''):
        nonlocal ok
        ok &= bool(cond)
        print('%-4s %s %s' % ('ok' if cond else 'FAIL', name, info))

    r1, r0 = load(t1), load(t0)
    s1 = open(o1, encoding='utf-8').read().split(chr(10))[0].strip()
    s0 = open(o0, encoding='utf-8').read().split(chr(10))[0].strip()
    check('default stdout', s1 == 'FIXF29 env=(unset) on=1', s1)
    check('control stdout', s0 == 'FIXF29 env=0 on=0', s0)
    for name, rows, fix in (('default', r1, '1'), ('control', r0, '0')):
        check('%s rows %d = 8 x R' % (name, len(rows)), len(rows) == 8 * reps)
        check('%s seed and fix columns' % name, all(int(r['seed']) == seed and r['fix'] == fix for r in rows))
        for a in ARMS:
            check('%s arm %s count R' % (name, a), sum(1 for r in rows if r['arm'] == a) == reps)
        check('%s extra = dup = map_left = 0' % name, all(r['extra'] == r['dup'] == r['map_left'] == '0' for r in rows))
    bad = [r for r in r1 if not (r['out_area'] == r['out_buf'] == r['cls_low'] == r['cls_exit'] == '0')]
    check('P1 out_area = out_buf = cls_low = cls_exit = 0 in all default rows', not bad, 'bad %d of %d' % (len(bad), len(r1)))
    rd = [r for r in r1 if r['arm'] in OVER]
    check('P1 read = 1023 at E1 O1 O7 D1 L', rd and all(r['read'] == '1023' for r in rd), '%d rows' % len(rd))
    p0a = sum(1 for r in r0 if r['arm'] == 'O1' and r['out_area'] == '77')
    p0b = sum(1 for r in r0 if r['arm'] == 'O7' and r['out_buf'] == '77')
    check('P0 control O1 out_area 77', p0a == reps, '%d of %d' % (p0a, reps))
    check('P0 control O7 out_buf 77', p0b == reps, '%d of %d' % (p0b, reps))
    print('RECOUNT ALL OK' if ok else 'RECOUNT NOT OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
