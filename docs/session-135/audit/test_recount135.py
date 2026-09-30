# test_recount135.py - fixtures of the auditor's recount135.py: window edge 9/10/88/89 (p.55(b)), row n = F of the next
# GateArm is position 89 of the outgoing block, arm by GateArm text, form (a) running residual edges K = 64 / 65.
import sys, os, hashlib, tempfile
import recount135 as R

me = os.path.abspath(__file__); tgt = os.path.abspath(R.__file__)
print('suite test_recount135.py sha256 %s target recount135.py sha256 %s' % (hashlib.sha256(open(me, 'rb').read()).hexdigest(),
                                                                          hashlib.sha256(open(tgt, 'rb').read()).hexdigest()))
ok = True
checks = 0


def check(name, cond):
    global ok, checks
    checks += 1
    if not cond:
        ok = False
        print('FAIL', name)


def xline(n, **kw):
    v = {k: 0 for k in R.X_F}
    v.update(dict(rb_cal_ns=100, rb_cal_n=10, rb_slow_n=8, rs_sync_noop_n=8, rs_ro_n=8, rs_bf_n=4))
    v.update(kw)
    return 'FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % (k, v[k]) for k in R.X_F)


def build(blocks, mark_pos=None, mark_val=1000):
    L = []
    last = 1800 + 90 * len(blocks)
    arm_of = {}
    for b, a in enumerate(blocks):
        arm_of[b] = a
    for n in range(1790, last + 1):
        b = (n - 1801) // 90 if n > 1800 else -1
        a = arm_of.get(b, 0)
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < len(blocks):
            bb = (n - 1800) // 90
            L.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=b2reuse=%d' % (blocks[bb], bb, n, blocks[bb]))
        p = (n - 1800 - 1) - 90 * b if b >= 0 else -1
        dt = mark_val if (mark_pos is not None and p == mark_pos) else 100
        L.append('FrameTrace: n=%d dt_us=%d draws=5 arm=%d blk=%d' % (n, dt, a, max(b, 0)))
        L.append('FrameTrace-draw: n=%d bda_scan=10' % n)
        L.append(xline(n))
    return '\n'.join(L) + '\n'


def run(text):
    fd, p = tempfile.mkstemp(suffix='.txt'); os.close(fd)
    open(p, 'w').write(text)
    P = R.parse(p)
    os.remove(p)
    return P, R.run_abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})


# block frame F; row n = F + 1 + p; positions 9 and 89 outside, 10 and 88 inside (mark only in block 0, arm 0; 20 blocks, 10 pairs)
ABBA20 = [(0, 1, 1, 0)[i % 4] for i in range(20)]
for pos, inside in ((9, False), (10, True), (88, True), (89, False)):
    txt = build(ABBA20, mark_pos=None)
    n_mark = 1800 + 1 + pos
    txt = txt.replace('FrameTrace: n=%d dt_us=100 ' % n_mark, 'FrameTrace: n=%d dt_us=1000 ' % n_mark)
    P, A = run(txt)
    M = A['modes']['NEW']
    mu = M['arm0']['dt_us'][0]
    want = 100 + (900 / 79) / 10 if inside else 100.0
    check('edge %d %s (arm0 dt %.4f)' % (pos, inside, mu), abs(mu - want) < 1e-9)
# n = F of block 1 belongs to block 0 position 89: its blk field is 0 in the builder and it is outside the window
P, A = run(build([0, 1, 1, 0]))
check('rowF next block has blk of outgoing', P['rows']['m'][1890]['blk'] == 0)
check('complete 4', A['complete'] == 4 and A['seq_ok'])
check('pairs 2 -> DEBT', A['modes']['NEW']['pairs'] == 2 and A['modes']['NEW'].get('reading') == 'DEBT')
# arm by text: wrong ABBA order breaks seq_ok
P, A = run(build([0, 0, 1, 1]))
check('abba order', not A['seq_ok'])
# form (a): identity I1 residual 64 passes, 65 fails
def xs_with(res):
    base = {k: 0 for k in R.X_F}
    r1 = dict(base); r1.update(rb_slow_n=100, rs_sync_n=0, rs_sync_noop_n=100 + res, rs_ro_n=100, rb_slow_ns=10, rs_head_ns=10)
    r2 = dict(base); r2.update(rb_slow_n=100, rs_sync_noop_n=100 - res, rs_ro_n=100, rb_slow_ns=10, rs_head_ns=10)
    return [r1, r2]
check('I1 64 ok', R.form_a(xs_with(64))['I1']['ok'])
check('I1 65 fail', not R.form_a(xs_with(65))['I1']['ok'])
check('I1 -65 fail', not R.form_a(xs_with(-65))['I1']['ok'])
# inequality N7: xchk - xdiff >= -64 per line and in sum
base = {k: 0 for k in R.X_F}; base.update(rb_slow_ns=1, rs_head_ns=1)
a = dict(base); a.update(rs_bf_xdiff=64); b = dict(base); b.update(rs_bf_xchk=64)
check('N7 -64 ok', R.form_a([a, b])['N7']['ok'])
a2 = dict(base); a2.update(rs_bf_xdiff=65)
check('N7 -65 fail', not R.form_a([a2, b])['N7']['ok'])
print('checks:', checks)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
