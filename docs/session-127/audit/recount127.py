# Session 127 audit (HPP-112, Session Auditor): independent recount of k3p127 (sealed ABBA rtskip=0|1),
# k3k127 (self-check rtskip=2), k3v127/k3w127 (video arms) from the RAW logs. No code shared with k3p127.py.
# Blocks ONLY by 'GateArm:' lines; row of position p of block b: n = frame_b + 1 + p; window 10..88 inclusive
# (item 55(b)); level = mean of window rows; SE over pairs (n-1). Constants from pred/01_k3p127.md s.5-6 and
# ROADMAP item 76(z)(5), 83(g): bar -100 us, BDA bands <=300 NEW / >=600 OLD, >=10 pairs, DRS 1 %, tol 256.
import json, math, os, re, sys
from fractions import Fraction

ROOT = 'C:/kyty/s127/'
WLO = int(os.environ.get('RC_WLO', '10'))
WHI = int(os.environ.get('RC_WHI', '88'))
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')


def kv(line):
    return {k.decode(): int(v) for k, v in KV.findall(line)}


def read_log(path):
    main, drw, x = {}, {}, {}
    arms, dup = [], 0
    lines = {'rtskip_mode': [], 'rtskip_refused': 0, 'verify': 0, 'skipped_draw': 0, 'death': 0,
             'gpuwaitslow': 0, 'gate': []}
    with open(path, 'rb') as f:
        for raw in f:
            s = raw.lstrip()
            if s.startswith(b'FrameTrace: '):
                d = kv(s[12:]); n = d['n']
                if n in main: dup += 1
                main[n] = d
            elif s.startswith(b'FrameTrace-draw: '):
                d = kv(s[17:]); drw[d['n']] = d
            elif s.startswith(b'FrameTrace-x: '):
                d = kv(s[14:]); x[d['n']] = d
            elif s.startswith(b'GateArm: '):
                m = re.match(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*?)\r?\n?$', s)
                arms.append(tuple(int(m.group(i)) for i in range(1, 7)) + (m.group(7).decode(),))
            else:
                if b'RtSkip: mode' in s: lines['rtskip_mode'].append(s.strip().decode(errors='replace'))
                if b'RtSkip: refused' in s: lines['rtskip_refused'] += 1
                if b'RtSkipVerify' in s: lines['verify'] += 1
                if b'AsyncPipelines: skipped draw' in s: lines['skipped_draw'] += 1
                if (b'--- Error ---' in s or b'--- Fatal Error ---' in s or b'--- std::terminate ---' in s
                        or b'--- abort() ---' in s): lines['death'] += 1
                if b'GpuWaitSlow' in s: lines['gpuwaitslow'] += 1
                if s.startswith(b'Gate: '): lines['gate'].append(s.strip().decode(errors='replace'))
    return main, drw, x, arms, dup, lines


def mean(v):
    return sum(v) / len(v)


def sd(v):
    m = mean(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1))


def se(v):
    return sd(v) / math.sqrt(len(v))


def mode_of(avg):
    return 'NEW' if avg <= 300 else ('OLD' if avg >= 600 else 'BETWEEN')


def sealed(tag='k3p127'):
    main, drw, x, arms, dup, lines = read_log(ROOT + 'log_%s.txt' % tag)
    out = {'tag': tag, 'window': [WLO, WHI], 'dup_n': dup, 'gatearm_lines': len(arms), 'lines': {
        k: (v if not isinstance(v, list) else len(v)) for k, v in lines.items()}, 'rtskip_mode': lines['rtskip_mode']}
    ABBA = (0, 1, 1, 0)
    bad_arm = []
    for i, (arm, narms, blk, fr, per, abba, text) in enumerate(arms):
        exp_arm = ABBA[i % 4]
        if (blk != i or fr != 1800 + 90 * i or narms != 2 or per != 90 or abba != 1 or arm != exp_arm
                or text != 'rtskip=%d' % exp_arm):
            bad_arm.append(i)
    out['gatearm_bad'] = bad_arm
    blocks = []
    for i, a in enumerate(arms):
        arm, fr = a[0], a[3]
        rows = []
        ok = True
        for p in range(WLO, WHI + 1):
            n = fr + 1 + p
            if n not in main or n not in drw or n not in x:
                ok = False; break
            m = main[n]
            if m.get('arm') != arm or m.get('blk') != i:
                ok = False; break
            rows.append((m, drw[n], x[n]))
        blocks.append({'b': i, 'arm': arm, 'complete': ok, 'rows': rows if ok else None})
    comp = [b for b in blocks if b['complete']]
    out['blocks'] = len(blocks)
    out['complete'] = len(comp)
    out['incomplete'] = [b['b'] for b in blocks if not b['complete']]
    for b in comp:
        b['dt'] = mean([r[0]['dt_us'] for r in b['rows']])
        b['draws'] = mean([r[0]['draws'] for r in b['rows']])
        b['cpu'] = mean([r[0]['cpu_gpu_us'] for r in b['rows']])
        b['gpu'] = mean([r[0]['gpu_busy_us'] for r in b['rows']])
        b['bda'] = mean([r[1]['bda_scan'] for r in b['rows']])
        b['mode'] = mode_of(b['bda'])
    out['block_modes'] = {m: sum(1 for b in comp if b['mode'] == m) for m in ('NEW', 'OLD', 'BETWEEN')}
    out['bda_range'] = [min(b['bda'] for b in comp), max(b['bda'] for b in comp)]
    # beta: pooled within-block OLS of dt_us on draws, arm-0 complete blocks window rows
    sxy = sxx = 0.0
    for b in comp:
        if b['arm'] != 0: continue
        xs = [r[0]['draws'] for r in b['rows']]; ys = [r[0]['dt_us'] for r in b['rows']]
        mx, my = mean(xs), mean(ys)
        sxy += sum((a - mx) * (c - my) for a, c in zip(xs, ys)); sxx += sum((a - mx) ** 2 for a in xs)
    beta = sxy / sxx if sxx else 0.0
    out['beta'] = beta
    # pairs (2k, 2k+1) of complete blocks
    byb = {b['b']: b for b in comp}
    pairs = []
    for k in range(len(blocks) // 2):
        b0, b1 = byb.get(2 * k), byb.get(2 * k + 1)
        if b0 is None or b1 is None: continue
        if b0['arm'] == b1['arm']: raise SystemExit('pair with same arm')
        a0, a1 = (b0, b1) if b0['arm'] == 0 else (b1, b0)
        md = a0['mode'] if a0['mode'] == a1['mode'] and a0['mode'] != 'BETWEEN' else None
        pairs.append({'k': k, 'mode': md, 'ddt': a1['dt'] - a0['dt'], 'ddraws': a1['draws'] - a0['draws'],
                      'dcpu': a1['cpu'] - a0['cpu'], 'dgpu': a1['gpu'] - a0['gpu']})
    out['pairs_total'] = len(pairs)
    out['pairs_outside_mode'] = sum(1 for p in pairs if p['mode'] is None)
    res = {}
    verdicts = {}
    for md in ('NEW', 'OLD'):
        P = [p for p in pairs if p['mode'] == md]
        r = {'pairs': len(P)}
        if len(P) >= 2:
            d = [p['ddt'] for p in P]; da = [p['ddt'] - beta * p['ddraws'] for p in P]
            r.update({'d': mean(d), 'd_2se': 2 * se(d), 'd_adj': mean(da), 'd_adj_2se': 2 * se(da),
                      'ddraws': mean([p['ddraws'] for p in P]), 'ddraws_2se': 2 * se([p['ddraws'] for p in P]),
                      'dcpu': mean([p['dcpu'] for p in P]), 'dcpu_2se': 2 * se([p['dcpu'] for p in P]),
                      'dgpu': mean([p['dgpu'] for p in P]), 'dgpu_2se': 2 * se([p['dgpu'] for p in P]),
                      'median_d': sorted(d)[len(d) // 2] if len(d) % 2 else (sorted(d)[len(d) // 2 - 1] + sorted(d)[len(d) // 2]) / 2})
        if len(P) >= 10:
            hi = max(r['d'] + r['d_2se'], r['d_adj'] + r['d_adj_2se'])
            lo = min(r['d'] - r['d_2se'], r['d_adj'] - r['d_adj_2se'])
            v = 'RTSKIP_GAIN' if hi <= -100 else ('RTSKIP_NO_GAIN' if lo > -100 else 'NOT_RESOLVED')
            r['upper'] = hi; r['lower'] = lo
            r['slowdown'] = (r['d'] - r['d_2se'] > 0) or (r['d_adj'] - r['d_adj_2se'] > 0)
            r['verdict'] = v
            verdicts[md] = r
        else:
            r['verdict'] = 'NOT_RESOLVED(<10 pairs)' if P else 'EMPTY'
        res[md] = r
    out['modes'] = res
    if not verdicts:
        T = 'NOT_EVALUABLE'
    elif any(v['verdict'] == 'RTSKIP_GAIN' for v in verdicts.values()) and not any(v['slowdown'] for v in verdicts.values()):
        T = 'RTSKIP_GAIN'
    elif all(v['verdict'] == 'RTSKIP_NO_GAIN' for v in verdicts.values()):
        T = 'RTSKIP_NO_GAIN'
    else:
        T = 'NOT_RESOLVED'
    # DRS
    kpx = {0: 0, 1: 0}; att = {0: 0, 1: 0}; att0 = {0: 0, 1: 0}
    for b in comp:
        for r in b['rows']:
            if r[2]['rt_att'] == 0: att0[b['arm']] += 1; continue
            kpx[b['arm']] += r[2]['rt_kpx']; att[b['arm']] += r[2]['rt_att']
    m0 = Fraction(kpx[0], att[0]); m1 = Fraction(kpx[1], att[1])
    drs_mixed = 100 * abs(m1 - m0) > m0
    out['drs'] = {'m0': float(m0), 'm1': float(m1), 'rt_att0_rows': att0, 'mixed': drs_mixed}
    if drs_mixed: T = 'NOT_RESOLVED'
    # census: zero control arm 0 window rows, T3 at arm 1, identities T2/T4/T5, positive control
    rts_names = sorted({k for b in comp for r in b['rows'] for k in r[2] if k.startswith('rts_')})
    out['rts_fields'] = rts_names
    zero_bad = 0
    for b in comp:
        if b['arm'] != 0: continue
        for r in b['rows']:
            if any(r[2].get(k, 0) for k in rts_names) or r[0].get('rts_chain_max', 0) or any(
                    v for k, v in r[1].items() if k.startswith('rts_')):
                zero_bad += 1
    t3 = ['rts_pb', 'rts_chk', 'rts_chk_b', 'rts_chain2', 'rts_bad', 'rts_bad_noreg', 'rts_race', 'rts_rec',
          'rts_wr', 'rts_wr_obj', 'rts_lost', 'rts_early']
    t3_bad = 0; t2_bad = t4_bad = t5_bad = pos_bad = 0; guard_rows = 0
    sums1 = {}
    xa = [k for k in rts_names if k.startswith('rts_xa_')]; xb = [k for k in rts_names if k.startswith('rts_xb_')]
    for b in comp:
        if b['arm'] != 1: continue
        S = {}
        for r in b['rows']:
            X = r[2]
            if any(X.get(k, 0) for k in t3) or r[0].get('rts_chain_max', 0): t3_bad += 1
            for k in rts_names: S[k] = S.get(k, 0) + X.get(k, 0)
            S['draws'] = S.get('draws', 0) + r[0]['draws']
        n = S['rts_n']; sk = S['rts_skip']
        pa = n - sum(S[k] for k in xa)
        if sk + sum(S[k] for k in xb) > pa + 256: t2_bad += 1
        if n > S['draws'] + 256: t4_bad += 1
        if S.get('rts_rec_x', 0) + S.get('rts_ovf', 0) > n - sk + 256: t5_bad += 1
        if not (n > 0 and sk > 0 and S.get('rts_xa_reg', 0) > 0): pos_bad += 1
        for k, v in S.items(): sums1[k] = sums1.get(k, 0) + v
    for n_, X in x.items():
        if X.get('rts_xthr', 0) or X.get('rts_acqw', 0) or X.get('rts_refuse', 0): guard_rows += 1
    out['census'] = {'zero_ctrl_bad_rows': zero_bad, 't3_bad_rows': t3_bad, 't2_bad': t2_bad, 't4_bad': t4_bad,
                     't5_bad': t5_bad, 'pos_ctrl_bad_blocks': pos_bad, 'guard_rows_all': guard_rows,
                     'arm1_window': {k: sums1.get(k, 0) for k in ('rts_n', 'rts_skip', 'rts_xa_reg', 'rts_lost', 'rts_early', 'draws')}}
    out['census']['arm1_skip_frac'] = sums1['rts_skip'] / sums1['rts_n']
    out['T'] = T
    # base item 76(z)(6): mean dt_us of window rows of complete arm-0 blocks (all and by mode)
    base = {}
    for md in ('ALL', 'NEW', 'OLD', 'BETWEEN'):
        v = [r[0]['dt_us'] for b in comp if b['arm'] == 0 and (md == 'ALL' or b['mode'] == md) for r in b['rows']]
        if v: base[md] = {'rows': len(v), 'mean_dt_us': mean(v), 'speed_pct': 100 * 16667 / mean(v)}
    v1 = [r[0]['dt_us'] for b in comp if b['arm'] == 1 for r in b['rows']]
    base['arm1_mean_dt_us'] = mean(v1)
    out['base'] = base
    out['skipped_draw_window'] = sum(1 for b in comp for r in b['rows'] if r[1].get('d_skip', 0))
    return out


def selfcheck(tag='k3k127'):
    main, drw, x, arms, dup, lines = read_log(ROOT + 'log_%s.txt' % tag)
    ns = sorted(x)
    first = next((n for n in ns if x[n].get('rts_n', 0) > 0), None)
    pop = [n for n in ns if first is not None and n >= first]
    S = {}
    badrows = 0
    for n in pop:
        X = x[n]
        if X.get('rts_bad', 0): badrows += 1
        for k in ('rts_n', 'rts_skip', 'rts_chk', 'rts_chk_b', 'rts_chain2', 'rts_bad', 'rts_bad_noreg', 'rts_race',
                  'rts_xthr', 'rts_acqw', 'rts_refuse'):
            S[k] = S.get(k, 0) + X.get(k, 0)
    return {'tag': tag, 'gatearm_lines': len(arms), 'dup_n': dup, 'first_row': first, 'rows': len(pop),
            'rts_bad_rows': badrows, 'sums': S, 'chain_frac': S['rts_chain2'] / S['rts_chk'] if S.get('rts_chk') else None,
            'rows_all_bad_total': sum(v.get('rts_bad', 0) for v in x.values()),
            'lines': {k: (v if not isinstance(v, list) else len(v)) for k, v in lines.items()},
            'rtskip_mode': lines['rtskip_mode'], 'gate_lines': lines['gate'][:6]}


def video_arm(tag):
    main, drw, x, arms, dup, lines = read_log(ROOT + 'log_%s.txt' % tag)
    return {'tag': tag, 'gatearm_lines': len(arms), 'rows': len(x),
            'rts_n': sum(v.get('rts_n', 0) for v in x.values()), 'rts_skip': sum(v.get('rts_skip', 0) for v in x.values()),
            'rts_bad': sum(v.get('rts_bad', 0) for v in x.values()), 'rts_chk': sum(v.get('rts_chk', 0) for v in x.values()),
            'lines': {k: (v if not isinstance(v, list) else len(v)) for k, v in lines.items()},
            'rtskip_mode': lines['rtskip_mode'], 'gate_lines': lines['gate'][:6]}


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    R = {}
    if what in ('all', 'sealed'): R['k3p127'] = sealed()
    if what in ('all', 'k'): R['k3k127'] = selfcheck()
    if what in ('all', 'video'):
        R['k3v127'] = video_arm('k3v127'); R['k3w127'] = video_arm('k3w127')
    for v in R.values():
        if 'blocks' in v and isinstance(v['blocks'], list): del v['blocks']
    print(json.dumps(R, ensure_ascii=False, indent=1))
