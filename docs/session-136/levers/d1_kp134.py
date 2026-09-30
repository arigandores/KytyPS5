# d1_kp134.py - Lever Researcher, s.135 step 9a (HPP-231): audit debt D1 (ROADMAP p.175(e)(1)).
# Per-arm c-hat and RAW rows (without the c-hat subtraction) of kp134 beside the same rows of rs135, one formula for both.
# Parsing: recount134.parse (sha256 b0473c0b...) for kp134, recount135.parse (sha256 16ed3028...) for rs135 - imported,
# not copied. Blocks by GateArm: lines only; arm by the TEXT of the GateArm line; row n of block b at p = n - F_b - 1;
# the row n = F of the next GateArm is p = 89 of the OUTGOING block (excluded); window p 10..88 inclusive (p.55(b)).
# Pairs (2k, 2k+1) of complete blocks with different arms, same BDA mode (mean bda_scan <= 300 NEW, >= 600 OLD).
# Rows are [I] (constancy of the lap-segment cost between arms); not a win, not a ceiling, not speed.
import sys, math, hashlib

sys.dont_write_bytecode = True  # no __pycache__ beside the audit scripts

sys.path.insert(0, 'C:/kyty/KytyPS5/docs/session-134/audit')
sys.path.insert(0, 'C:/kyty/KytyPS5/docs/session-135/audit')
import recount134 as R4
import recount135 as R5

W_LO, W_HI = 10, 88
CLS = ('stream', 'cbank', 'epoch', 'slow')
NEED_X = tuple('rb_%s_%s' % (k, s) for k in CLS for s in ('ns', 'n')) + ('rb_cal_ns', 'rb_cal_n', 'mh_bind_us', 'bl_buf_us')
NEED_M = ('dt_us', 'draws', 'arm', 'blk')
ARM_TEXT = {'b2reuse=0': 0, 'b2reuse=1': 1}


def blocks(P):
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    out = []
    for b, a in enumerate(P['arms']):
        F = int(a.get('frame', -1))
        arm = ARM_TEXT.get(a.get('text'))
        win, ok = [], arm is not None
        for p in range(W_LO, W_HI + 1):
            n = F + 1 + p
            if not ok or n not in m or n not in d or n not in x:
                ok = False; break
            mr, dr, xr = m[n], d[n], x[n]
            if any(k not in mr for k in NEED_M) or 'bda_scan' not in dr or any(k not in xr for k in NEED_X):
                ok = False; break
            if mr['arm'] != arm or mr['blk'] != b:
                ok = False; break
            r = dict(mr); r.update(dr); r.update(xr); r['n'] = n; r['p'] = p
            win.append(r)
        out.append(dict(b=b, arm=arm, F=F, ok=ok, rows=win if ok else []))
    return out


def level(rows):
    N = len(rows)
    S = lambda k: sum(r[k] for r in rows)
    c = S('rb_cal_ns') / S('rb_cal_n') if S('rb_cal_n') else None
    L = dict(N=N, c=c, dt_us=S('dt_us') / N, draws=S('draws') / N, bda_scan=S('bda_scan') / N,
             bl_buf_us=S('bl_buf_us') / N, mh_bind_us=S('mh_bind_us') / N)
    for K in CLS:
        ns, n = S('rb_%s_ns' % K), S('rb_%s_n' % K)
        L['raw_' + K] = 8 * ns / (1000.0 * N)
        L['lv_' + K] = None if c is None else (8 * ns - n * c) / (1000.0 * N)
        L['n_' + K] = n / N
        L['itraw_' + K] = 8 * ns / n if n else None
    L['raw_L'] = L['raw_stream'] + L['raw_cbank']
    L['raw_net'] = L['raw_L'] + L['raw_epoch'] + L['raw_slow']
    if c is not None:
        L['lv_L'] = L['lv_stream'] + L['lv_cbank']
        L['lv_net'] = L['lv_L'] + L['lv_epoch'] + L['lv_slow']
    return L


def ms(v):
    n = len(v)
    mu = sum(v) / n
    sd = math.sqrt(sum((a - mu) ** 2 for a in v) / (n - 1)) if n > 1 else float('nan')
    return mu, 2 * sd / math.sqrt(n), n


KEYS = ('c', 'raw_L', 'raw_stream', 'raw_cbank', 'raw_epoch', 'raw_slow', 'raw_net', 'lv_L', 'lv_epoch', 'lv_slow', 'lv_net',
        'n_stream', 'n_cbank', 'n_epoch', 'n_slow', 'itraw_stream', 'itraw_cbank', 'itraw_epoch', 'itraw_slow',
        'bl_buf_us', 'mh_bind_us', 'dt_us', 'draws')


def rows_of(P, mode='NEW'):
    bl = blocks(P)
    for x in bl:
        if x['ok']:
            x['lv'] = level(x['rows'])
            bs = x['lv']['bda_scan']
            x['mode'] = 'NEW' if bs <= 300 else ('OLD' if bs >= 600 else 'MID')
    byb = {x['b']: x for x in bl if x['ok']}
    pairs = []
    for k in range(0, len(bl), 2):
        if k in byb and k + 1 in byb and byb[k]['arm'] != byb[k + 1]['arm']:
            p0, p1 = (byb[k], byb[k + 1]) if byb[k]['arm'] == 0 else (byb[k + 1], byb[k])
            if p0['mode'] == p1['mode'] == mode and p0['lv']['c'] is not None and p1['lv']['c'] is not None:
                pairs.append((p0['lv'], p1['lv']))
    res = dict(gatearm=len(bl), complete=len(byb), pairs=len(pairs), a0={}, a1={}, d={})
    for k in KEYS:
        res['a0'][k] = ms([p[0][k] for p in pairs])
        res['a1'][k] = ms([p[1][k] for p in pairs])
        res['d'][k] = ms([p[1][k] - p[0][k] for p in pairs])
    return res


def suite():
    # synthetic ABBA: two blocks F0 = 1800, F1 = 1890; the row n = 1890 (= F1) is p = 89 of block 0 and must stay out.
    chk = []
    arms = [dict(frame='1800', text='b2reuse=0'), dict(frame='1890', text='b2reuse=1')]
    m, d, x = {}, {}, {}
    for n in range(1800, 1992):
        b = 0 if n < 1891 else 1
        p = n - (1800 if b == 0 else 1890) - 1
        good = W_LO <= p <= W_HI
        val = 1000 if good else 10 ** 9
        m[n] = dict(dt_us=val, draws=1, arm=b, blk=b)
        d[n] = dict(bda_scan=10)
        x[n] = {k: 8 for k in NEED_X}
        x[n]['bl_buf_us'] = val
    P = dict(rows=dict(m=m, d=d, x=x), arms=arms)
    bl = blocks(P)
    b0, b1 = bl
    ns0 = [r['n'] for r in b0['rows']]
    chk.append(('b0 ok', b0['ok']))
    chk.append(('b0 first n = F+11 (p 10)', ns0[0] == 1811))
    chk.append(('b0 last n = F+89 (p 88)', ns0[-1] == 1889))
    chk.append(('b0 p9 excluded (n 1810)', 1810 not in ns0))
    chk.append(('b0 p89 = row n = F1 excluded (n 1890)', 1890 not in ns0))
    chk.append(('b0 79 rows', len(ns0) == 79))
    chk.append(('b0 dt mean 1000 (no poison)', level(b0['rows'])['dt_us'] == 1000))
    ns1 = [r['n'] for r in b1['rows']]
    chk.append(('b1 first n 1901 (p 10)', ns1[0] == 1901))
    chk.append(('b1 last n 1979 (p 88)', ns1[-1] == 1979))
    chk.append(('b1 p9 n 1900 excluded', 1900 not in ns1))
    # c-hat and raw algebra: raw - lv = n * c / 1000N ; c = 1 here
    lv = level(b0['rows'])
    chk.append(('c = cal_ns / cal_n', lv['c'] == 1.0))
    chk.append(('raw_slow = 8*ns/1000N', abs(lv['raw_slow'] - 0.064) < 1e-12))
    chk.append(('lv_slow = raw - n*c/1000N', abs(lv['lv_slow'] - (0.064 - 0.008)) < 1e-12))
    # an incomplete block (missing p 50 row) must drop
    del m[1851]
    chk.append(('missing row -> block incomplete', not blocks(P)[0]['ok']))
    bad = [n for n, ok in chk if not ok]
    return len(chk), bad


def fmt(t):
    mu, s2, n = t
    return '%+10.3f +- %8.3f' % (mu, s2)


def main():
    n, bad = suite()
    print('suite d1_window: %d checks %s' % (n, 'ALL OK' if not bad else 'FAIL ' + ', '.join(bad)), flush=True)
    if bad:
        sys.exit(1)
    for nm, mod in (('recount134.py', 'C:/kyty/KytyPS5/docs/session-134/audit/recount134.py'),
                    ('recount135.py', 'C:/kyty/KytyPS5/docs/session-135/audit/recount135.py'),
                    ('d1_kp134.py', __file__)):
        print('sha256 %s %s' % (nm, hashlib.sha256(open(mod, 'rb').read()).hexdigest()))
    out = {}
    for tag, mod, path in (('kp134', R4, 'C:/kyty/s134/log_kp134.txt'), ('rs135', R5, 'C:/kyty/s135/log_rs135.txt')):
        P = mod.parse(path)
        r = rows_of(P)
        out[tag] = r
        print('== %s log sha256 %s lines %d GateArm %d complete %d NEW pairs %d' % (tag, P['sha'], P['lines'], r['gatearm'],
                                                                                   r['complete'], r['pairs']), flush=True)
    print()
    print('%-14s | %-22s | %-22s | %-22s | %-22s' % ('row (NEW)', 'kp134 arm0', 'kp134 d(1-0) +-2SE', 'rs135 arm0', 'rs135 d(1-0) +-2SE'))
    for k in KEYS:
        print('%-14s | %s | %s | %s | %s' % (k, fmt(out['kp134']['a0'][k]), fmt(out['kp134']['d'][k]), fmt(out['rs135']['a0'][k]),
                                             fmt(out['rs135']['d'][k])))
    print()
    print('arm1 c-hat: kp134 %.3f, rs135 %.3f' % (out['kp134']['a1']['c'][0], out['rs135']['a1']['c'][0]))
    for tag in ('kp134', 'rs135'):
        D = out[tag]['d']
        print('%s: dc %+.3f +- %.3f ns; raw net %+.1f +- %.1f; lv net %+.1f +- %.1f; bl_buf %+.1f +- %.1f; raw net - bl_buf %+.1f' % (
            tag, D['c'][0], D['c'][1], D['raw_net'][0], D['raw_net'][1], D['lv_net'][0], D['lv_net'][1], D['bl_buf_us'][0],
            D['bl_buf_us'][1], D['raw_net'][0] - D['bl_buf_us'][0]))
    # between-session difference of the raw rows (Welch-like, independent runs)
    for k in ('c', 'raw_L', 'raw_epoch', 'raw_slow', 'raw_net', 'bl_buf_us', 'itraw_epoch', 'itraw_slow'):
        a, b = out['kp134']['d'][k], out['rs135']['d'][k]
        print('between sessions d(%s): rs135 - kp134 %+.3f +- %.3f (2SE combined)' % (k, b[0] - a[0], math.sqrt(a[1] ** 2 + b[1] ** 2)))


if __name__ == '__main__':
    main()
