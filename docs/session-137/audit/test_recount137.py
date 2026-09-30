# test_recount137.py - fixtures of the auditor's own recount137.py on the edges: window 9/10/88/89 (p.55(b)), the IF5 tear form
# 32/33 on one row, two adjacent rows 33, S_last 32/33, (iii) 3/4 distinct n (one n in two identities = 1), pair 0 not read,
# order (0,1)/(1,0), beta centred per block, Cochran p edge.  Ends with ALL OK.
import sys, hashlib, math
sys.path.insert(0, 'C:/kyty/s137/audit137')
import recount137 as R

tgt = 'C:/kyty/s137/audit137/recount137.py'
print('suite test_recount137.py sha256 %s target recount137.py sha256 %s' % (
    hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), hashlib.sha256(open(tgt, 'rb').read()).hexdigest()))
ok = True
n_checks = 0


def chk(name, cond):
    global ok, n_checks
    n_checks += 1
    if not cond:
        print('FAIL', name)
    ok &= bool(cond)


def row(n, **kw):
    r = {k: 0 for k in R.BLN}
    r.update(kw)
    r['_n'] = n
    return (n, r)


def seq_with(ds, key='bln_n'):
    return [row(i + 1, **{key: d}) for i, d in enumerate(ds)]


f_a = R.ident(1, False)[0][1]
# one row 32 / 33 then back
e = R.tear(seq_with([0, 32, -32, 0]), f_a); chk('t32 not over', e['singles'] == [] and not e['fail'])
e = R.tear(seq_with([0, 33, -33, 0]), f_a); chk('t33 single', len(e['singles']) == 1 and not e['fail'] and e['singles'][0][:3] == (2, 33, 33))
e = R.tear(seq_with([0, 33, 0, -33, 0]), f_a); chk('two adjacent 33 fail', e['fail'] and e['two'] == 1)
e = R.tear(seq_with([0, 0, 32]), f_a); chk('S_last 32 pass', not e['fail'])
e = R.tear(seq_with([0, 0, 33]), f_a); chk('S_last 33 fail', e['fail'])
e = R.tear([], f_a); chk('empty fail', e['fail'])
# (iii) distinct n over identities
def mk(tears_a, tears_b):
    rows = []
    for i in range(1, 30):
        kw = {}
        if i in tears_a:
            kw['bln_n'] = 40
        if i - 1 in tears_a:
            kw['bln_n'] = kw.get('bln_n', 0) - 40
        if i in tears_b:
            kw['bln_skip'] = 40
        if i - 1 in tears_b:
            kw['bln_skip'] = kw.get('bln_skip', 0) - 40
        rows.append(row(i, **kw))
    return rows
chk('iii one n in two identities = 1', R.tag_if5(mk({5}, {5}), 1, False)['iii_distinct_n'] == 1)
chk('iii 3 distinct pass', not R.tag_if5(mk({5, 10}, {15}), 1, False)['FAIL'])
chk('iii 4 distinct fail', R.tag_if5(mk({5, 10}, {15, 20}), 1, False)['FAIL'])
chk('IF5c only at 2/3 not abba', len(R.ident(2, False)) == 3 and len(R.ident(2, True)) == 2 and len(R.ident(1, False)) == 2)


# window 9/10/88/89 and pairs
def fake_call(nblk=6, poison=None):
    m, d, x = {}, {}, {}
    arms = []
    for b in range(nblk):
        arm = R.ABBA_PAT[b % 4]
        F = 1800 + 90 * b
        arms.append({'arm': str(arm), 'arms': '2', 'block': str(b), 'frame': str(F), 'period': '90', 'abba': '1',
                     'text': 'bindlean=%d' % arm})
        for p in range(0, 90):
            n = F + 1 + p
            dt_us = 30000 + 100 * arm + (5000 if poison == p else 0)
            m[n] = dict(dt_us=dt_us, draws=5000 + (p % 3), arm=arm, blk=b, cpu_gpu_us=0, gpu_busy_us=0)
            d[n] = dict(bda_scan=50)
            xr = {k: 0 for k in R.X_F}
            xr['rt_att'] = 1
            xr['rt_kpx'] = 2000
            x[n] = xr
    return dict(rows={'m': m, 'd': d, 'x': x}, arms=arms)
for p, inwin in ((9, False), (10, True), (88, True), (89, False)):
    cb = R.call_blocks(fake_call(poison=p), {'bindlean=0': 0, 'bindlean=1': 1})
    lv = cb['blocks'][0]['lv']
    chk('window pos %d' % p, (abs(lv['dt_us'] - 30000) > 1) == inwin)
cb = R.call_blocks(fake_call(), {'bindlean=0': 0, 'bindlean=1': 1})
chk('seq ok', cb['seq_ok'] and all(b['complete'] for b in cb['blocks']) and cb['blocks'][0]['lv']['rows'] == 79)
ps = R.pairs_of(dict(tag='x', abba=cb))
chk('pairs 3', len(ps) == 3 and [p['k'] for p in ps] == [0, 2, 4])
chk('order', [p['order'] for p in ps] == ['(0,1)', '(1,0)', '(0,1)'])
chk('arm1-arm0 = 100', all(abs(p['b1']['dt_us'] - p['b0']['dt_us'] - 100) < 1e-9 for p in ps))
# beta centred per block: two blocks with different levels, same slope 2
rows1 = [dict({k: 0 for k in R.X_F + R.MAIN_F + R.DRAW_F}, draws=dr, dt_us=1000 + 2 * dr) for dr in range(10)]
rows2 = [dict({k: 0 for k in R.X_F + R.MAIN_F + R.DRAW_F}, draws=dr + 100, dt_us=90000 + 2 * dr) for dr in range(10)]
L1, L2 = R.block_level(rows1), R.block_level(rows2)
chk('beta centred', abs((L1['sxy'] + L2['sxy']) / (L1['sxx'] + L2['sxx']) - 2.0) < 1e-12)
chk('gammq chi2 df1 Q2 = 0.157299', abs(R.gammq(0.5, 1.0) - 0.157299) < 1e-5)
chk('gammq chi2 df7 Q5.830 ~ 0.5598', abs(R.gammq(3.5, 5.830 / 2) - 0.5598) < 5e-4)
print('checks %d' % n_checks)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
