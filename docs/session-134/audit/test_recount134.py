# test_recount134.py - window-edge fixtures for recount134.py (ROADMAP p.55(b): window 10..88 inclusive;
# row n = F of the next GateArm is position 89 of the OUTGOING block; blocks by GateArm, not by blk).
import sys, os, hashlib, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recount134 as R

here = os.path.abspath(__file__)
tgt = os.path.join(os.path.dirname(here), 'recount134.py')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
print('suite test_recount134.py sha256 %s target recount134.py sha256 %s' % (sha(here), sha(tgt)))

XZ = ' '.join('%s=0' % k for k in R.X_F if k not in ('rb_cal_ns', 'rb_cal_n', 'rt_att', 'rt_kpx', 'rb_stream_ns', 'rb_stream_n'))


def mklog(nblocks, dt_of, blk_of=None, bda=100):
    L = []
    last = 1800 + 90 * nblocks + 95
    for n in range(1, last):
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < nblocks:
            b = (n - 1800) // 90
            arm = (0, 1, 1, 0)[b % 4]
            L.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=b2reuse=%d' % (arm, b, n, arm))
        b = max(0, (n - 1801) // 90) if n > 1800 else 0
        arm = (0, 1, 1, 0)[b % 4]
        p = (n - 1800 - 1) % 90 if n > 1800 else -1
        blk = blk_of(b) if blk_of else b
        L.append('FrameTrace: n=%d dt_us=%d draws=5000 cpu_gpu_us=1 gpu_busy_us=1 arm=%d blk=%d' % (n, dt_of(b, arm, p), arm, blk))
        L.append('FrameTrace-draw: n=%d bda_scan=%d' % (n, bda))
        L.append('FrameTrace-x: n=%d rb_cal_ns=100 rb_cal_n=10 rt_att=1 rt_kpx=5 rb_stream_ns=1000 rb_stream_n=10 %s' % (n, XZ))
    fd, path = tempfile.mkstemp(suffix='.txt')
    os.write(fd, ('\n'.join(L) + '\n').encode())
    os.close(fd)
    return path


ok = True
n_chk = 0


def check(name, cond):
    global ok, n_chk
    n_chk += 1
    print(('PASS ' if cond else 'FAIL ') + name)
    ok &= bool(cond)


# e1: positions 9 and 89 carry +1e6 in arm 1 - excluded; window rows carry +100 in arm 1
def dt1(b, arm, p):
    if p in (9, 89) and arm == 1:
        return 1000000
    return 30000 + (100 if arm == 1 else 0)
P = R.parse(mklog(24, dt1))
A = R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})
M = A['modes']['NEW']
check('e1 complete 24', A['complete'] == 24 and A['seq_ok'])
check('e1 pairs 12', M['pairs'] == 12)
check('e1 delta exactly +100 (p 9 and 89 outside)', abs(M['d_dt'][0] - 100) < 1e-9)
# e2: position 10 and 88 inside
def dt2(b, arm, p):
    if p in (10, 88) and arm == 1:
        return 30000 + 7900
    return 30000
P = R.parse(mklog(24, dt2))
M = R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})['modes']['NEW']
check('e2 delta = 2*7900/79 = 200 (p 10, 88 inside)', abs(M['d_dt'][0] - 200) < 1e-9)
# e3: blk wrong on one window row -> block incomplete (blocks by GateArm, blk only a consistency check)
P = R.parse(mklog(24, lambda b, a, p: 30000, blk_of=lambda b: b))
for n, r in P['rows']['m'].items():
    if n == 1800 + 90 * 5 + 1 + 40:
        r['blk'] = 99
A = R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})
check('e3 block 5 incomplete', A['incomplete'] == [5] and A['modes']['NEW']['pairs'] == 11)
# e4: < 10 pairs -> DEBT
P = R.parse(mklog(18, lambda b, a, p: 30000))
check('e4 9 pairs DEBT', R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})['modes']['NEW']['verdict'] == 'DEBT')
# e5: L estimator: level = (8*1000 - 10*10)/1000 = 7.9 per block both arms -> reduction 0
P = R.parse(mklog(20, lambda b, a, p: 30000))
M = R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})['modes']['NEW']
check('e5 L_arm0 7.9, reduction 0', abs(M['L_arm0'] - 7.9) < 1e-9 and abs(M['L_red'][0]) < 1e-9)
# e6: OLD band 600 and MID 300 < x < 600
P = R.parse(mklog(20, lambda b, a, p: 30000, bda=600))
check('e6 bda 600 -> OLD', list(R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})['modes']) == ['OLD'])
P = R.parse(mklog(20, lambda b, a, p: 30000, bda=301))
check('e6 bda 301 -> MID', list(R.abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})['modes']) == ['MID'])
# e7: runsum
check('e7 runsum', R.runsum([{'v': 3}, {'v': -3}, {'v': 5}], lambda r: r['v']) == dict(max_abs=5, last=5, rows_nz=3))
print('%d checks' % n_chk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
