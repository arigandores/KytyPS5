# test_recount136.py - fixtures of the auditor's recount136.py: window edge 9/10/88/89 (p.55(b)); the row n = F of the next
# GateArm is position 89 of the outgoing block; arm by the GateArm text; ABBA order; < 10 pairs -> DEBT; kill row threshold
# 200.0 not killed / below killed (p.176(g)); running sum K = 32 / 33 (p.162(a)); GAIN edge -100 inclusive, NO_GAIN strict.
import sys, os, hashlib, tempfile
import recount136 as R

me = os.path.abspath(__file__)
tgt = os.path.abspath(R.__file__)
print('suite test_recount136.py sha256 %s target recount136.py sha256 %s' % (hashlib.sha256(open(me, 'rb').read()).hexdigest(),
                                                                          hashlib.sha256(open(tgt, 'rb').read()).hexdigest()))
ok = True
checks = 0
NEG = os.environ.get('NEGCTL') == '1'   # negative control: shifts the window by one position in the builder's expectation


def check(name, cond):
    global ok, checks
    checks += 1
    if not cond:
        ok = False
        print('FAIL', name)


def xline(n, **kw):
    v = {k: 0 for k in R.X_F}
    v.update(dict(rb_cal_ns=100, rb_cal_n=10, rt_att=1, rt_kpx=2000, gclk_pin=1, bl_buf_us=5000))
    v.update(kw)
    return 'FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % (k, v[k]) for k in R.X_F)


def build(blocks, dt_of=None, blbuf_of=None):
    L = []
    last = 1800 + 90 * len(blocks)
    for n in range(1790, last + 1):
        b = (n - 1801) // 90 if n > 1800 else -1
        a = blocks[b] if 0 <= b < len(blocks) else 0
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < len(blocks):
            bb = (n - 1800) // 90
            L.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=bindlean=%d' % (blocks[bb], bb, n, blocks[bb]))
        p = (n - 1800 - 1) - 90 * b if b >= 0 else -1
        dt = dt_of(b, a, p) if dt_of else 100
        bl = blbuf_of(b, a, p) if blbuf_of else 5000
        L.append('FrameTrace: n=%d dt_us=%d draws=5 arm=%d blk=%d cpu_gpu_us=1 gpu_busy_us=1' % (n, dt, a, max(b, 0)))
        L.append('FrameTrace-draw: n=%d bda_scan=10' % n)
        L.append(xline(n, bl_buf_us=bl))
    return '\n'.join(L) + '\n'


def run(text):
    fd, p = tempfile.mkstemp(suffix='.txt')
    os.close(fd)
    open(p, 'w').write(text)
    P = R.parse(p)
    os.remove(p)
    return P, R.abba(P, {'bindlean=0': 0, 'bindlean=1': 1})


ABBA20 = [(0, 1, 1, 0)[i % 4] for i in range(20)]
# window edges: a spike at position pos of every arm-1 block; inside -> d dt = 900/79, outside -> 0
for pos, inside in ((9, False), (10, True), (88, True), (89, False)):
    shift = 1 if NEG else 0
    P, A = run(build(ABBA20, dt_of=lambda b, a, p, pos=pos: 1000 if (a == 1 and p == pos + shift) else 100))
    M = A['modes']['NEW']
    mu = M['rows']['d_dt'][0]
    want = 900.0 / 79 if inside else 0.0
    check('edge %d %s (d dt %.4f)' % (pos, inside, mu), abs(mu - want) < 1e-9)
P, A = run(build([0, 1, 1, 0]))
check('row n=F of block 1 carries blk of the outgoing block', P['rows']['m'][1890]['blk'] == 0)
check('complete 4, order ok', A['complete'] == 4 and A['seq_ok'])
check('2 pairs -> DEBT', A['modes']['NEW']['pairs'] == 2 and A['modes']['NEW'].get('reading') == 'DEBT')
P, A = run(build([0, 0, 1, 1]))
check('ABBA order broken', not A['seq_ok'])
# 18 blocks = 9 pairs -> DEBT; 20 blocks = 10 pairs -> read
P, A = run(build(ABBA20[:18]))
check('9 pairs DEBT', A['modes']['NEW'].get('reading') == 'DEBT')
P, A = run(build(ABBA20))
check('10 pairs read', A['modes']['NEW'].get('reading') in ('GAIN', 'NO_GAIN', 'NOT_RESOLVED'))
# kill row: reduction exactly 200 -> NOT_KILLED; 199 -> KILLED (constant per pair: SE 0)
for red, want in ((200, 'NOT_KILLED'), (199, 'KILLED')):
    P, A = run(build(ABBA20, blbuf_of=lambda b, a, p, red=red: 5000 - (red if a == 1 else 0)))
    check('kill %d -> %s' % (red, want), A['modes']['NEW']['kill'] == want)
# GAIN edge: d = -100 exactly with SE 0 -> GAIN (inclusive); d = -99 -> NOT GAIN; NO_GAIN strict (d = -100 is not NO_GAIN)
for d, want in ((-100, 'GAIN'), (-99, 'NO_GAIN')):
    P, A = run(build(ABBA20, dt_of=lambda b, a, p, d=d: 1000 + (d if a == 1 else 0)))
    check('reading d=%d -> %s' % (d, want), A['modes']['NEW']['reading'] == want)
# running sum K = 32: a one-row tear of 32 passes, 33 fails; a +33/-33 pair fails by max
def rows(ds):
    out = []
    for i, dd in enumerate(ds):
        r = {k: 0 for k in R.BLN}
        r['bln_skip'] = 1000 + dd
        r['bln_skip_a'] = 500
        r['bln_skip_b'] = 500
        out.append((i, r))
    return out
check('IF5b 32 ok', R.ifchecks(rows([0, 32, -32, 0]))['IF5b']['ok'])
check('IF5b 33 fail', not R.ifchecks(rows([0, 33, -33, 0]))['IF5b']['ok'])
check('IF5b -33 fail', not R.ifchecks(rows([-33, 33]))['IF5b']['ok'])
check('IF5b one row over', R.ifchecks(rows([0, 33, -33, 0]))['IF5b']['over_rows'] == 1)
print('checks:', checks)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
