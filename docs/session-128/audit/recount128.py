# Session 128 audit (HPP-125, Session Auditor): independent recount of the sealed pd128 (ABBA protceil=0|2)
# from the RAW log. No code shared with pd128.py, step8/recount8.py or lead/recount6c_lead.py (none of them read).
# Blocks ONLY by 'GateArm:' lines; row of position p of block b: FrameTrace n = frame_b + 1 + p (seal s.5);
# window 10..88 inclusive (item 55(b)); level = mean of window rows; SE over pairs (n-1).
# Constants from pred/01_pd128.md s.1, s.5, s.6, s.9 and ROADMAP item 93(g)(3)-(4): bar +500 us (min(D-2SE) over
# both estimators >= +500 -> OPEN; max(D+2SE) < +500 -> CLOSED), BDA bands <=300 NEW / >=600 OLD (FrameTrace-draw
# bda_scan), >=10 pairs, DRS 1 %, dose delivery [0.95; 1.10].
import json, math, os, re, sys
from fractions import Fraction

ROOT = 'C:/kyty/s128/'
WLO = int(os.environ.get('RC_WLO', '10'))
WHI = int(os.environ.get('RC_WHI', '88'))
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
GA = re.compile(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(\S*)')
DEATH = (b'--- std::terminate ---', b'--- abort() ---', b'--- Error ---', b'--- Fatal Error ---', b'GpuHangAbort:',
         b'ErrorDeviceLost', b'VK_ERROR_DEVICE_LOST', b'Unhandled exception')


def kv(line):
    d = {}
    for k, v in KV.findall(line):
        d[k.decode()] = int(v)
    return d


def read_log(path):
    main, drw, x = {}, {}, {}
    dup = {'main': 0, 'draw': 0, 'x': 0}
    arms = []
    L = {'protceil': [], 'protceil_refused': 0, 'rtskip': [], 'rtskip_refused': 0, 'skipped_draw': 0,
         'death': 0, 'gpuwaitslow': 0, 'bvhtrip': 0, 'clockpin': 0, 'gate': []}
    last_main = 0
    slow_at = []
    with open(path, 'rb') as f:
        for raw in f:
            s = raw.lstrip()
            if s.startswith(b'FrameTrace: '):
                d = kv(s[12:]); n = d['n']
                if n in main: dup['main'] += 1
                main[n] = d; last_main = n
            elif s.startswith(b'FrameTrace-draw: '):
                d = kv(s[17:]); n = d['n']
                if n in drw: dup['draw'] += 1
                drw[n] = d
            elif s.startswith(b'FrameTrace-x: '):
                d = kv(s[14:]); n = d['n']
                if n in x: dup['x'] += 1
                x[n] = d
            elif s.startswith(b'GateArm: '):
                m = GA.match(s)
                if not m: raise SystemExit('unparsed GateArm line: %r' % s[:200])
                arms.append(tuple(int(m.group(i)) for i in range(1, 7)) + (m.group(7).decode(),))
            else:
                if b'ProtCeil: mode' in s: L['protceil'].append(s.strip().decode(errors='replace'))
                if b'ProtCeil: refused' in s: L['protceil_refused'] += 1
                if b'RtSkip: mode' in s: L['rtskip'].append(s.strip().decode(errors='replace')[:40])
                if b'RtSkip: refused' in s: L['rtskip_refused'] += 1
                if b'AsyncPipelines: skipped draw' in s: L['skipped_draw'] += 1
                if any(t in s for t in DEATH): L['death'] += 1
                if b'GpuWaitSlow' in s: L['gpuwaitslow'] += 1; slow_at.append(last_main)
                if b'BvhLoopCapTrip' in s: L['bvhtrip'] += 1
                if s.startswith(b'GpuClockPin: mode 1'): L['clockpin'] += 1
                if s.startswith(b'Gate: '): L['gate'].append(s.strip().decode(errors='replace'))
    return main, drw, x, arms, dup, L


def mean(v):
    return sum(v) / len(v)


def se(v):
    m = mean(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1)) / math.sqrt(len(v))


def mode_of(avg):
    return 'NEW' if avg <= 300 else ('OLD' if avg >= 600 else 'BETWEEN')


def run(tag='pd128'):
    main, drw, x, arms, dup, L = read_log(ROOT + 'log_%s.txt' % tag)
    out = {'tag': tag, 'window': [WLO, WHI], 'dup': dup, 'gatearm_lines': len(arms),
           'lines': {k: (len(v) if isinstance(v, list) else v) for k, v in L.items()},
           'protceil_lines': L['protceil'], 'rtskip_lines': L['rtskip']}
    ABBA = (0, 1, 1, 0)
    TXT = {0: 'protceil=0', 1: 'protceil=2'}
    bad = []
    for i, (arm, narms, blk, fr, per, abba, text) in enumerate(arms):
        e = ABBA[i % 4]
        if blk != i or fr != 1800 + 90 * i or narms != 2 or per != 90 or abba != 1 or arm != e or text != TXT[e]:
            bad.append(i)
    out['gatearm_bad'] = bad
    blocks = []
    for i, a in enumerate(arms):
        arm, fr = a[0], a[3]
        rows, ok = [], True
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
    out['complete_by_arm'] = {a: sum(1 for b in comp if b['arm'] == a) for a in (0, 1)}
    out['incomplete'] = [b['b'] for b in blocks if not b['complete']]
    for b in comp:
        R = b['rows']
        b['dt'] = mean([r[0]['dt_us'] for r in R])
        b['draws'] = mean([r[0]['draws'] for r in R])
        b['cpu'] = mean([r[0]['cpu_gpu_us'] for r in R])
        b['gpu'] = mean([r[0]['gpu_busy_us'] for r in R])
        b['bda'] = mean([r[1]['bda_scan'] for r in R])
        b['mode'] = mode_of(b['bda'])
        b['dose_n'] = sum(r[2]['pc_dose_n'] for r in R)
        b['dose_ns'] = sum(r[2]['pc_dose_ns'] for r in R)
        b['elig_ns'] = sum(r[2]['pc_elig_ns'] for r in R)
    out['block_modes'] = {m: sum(1 for b in comp if b['mode'] == m) for m in ('NEW', 'OLD', 'BETWEEN')}
    out['bda_range'] = [min(b['bda'] for b in comp), max(b['bda'] for b in comp)]
    # dose guards (window rows of complete blocks; every block of the log is complete here except the last)
    a2 = [b for b in comp if b['arm'] == 1]; a0 = [b for b in comp if b['arm'] == 0]
    dn = sum(b['dose_ns'] for b in a2); en = sum(b['elig_ns'] for b in a2)
    out['dose'] = {'arm2_rows': sum(len(b['rows']) for b in a2), 'dose_ns': dn, 'elig_ns': en,
                   'delivery': dn / en, 'delivery_in_band': 100 * dn >= 95 * en and 100 * dn <= 110 * en,
                   'arm2_blocks_zero_dose': [b['b'] for b in a2 if b['dose_n'] == 0],
                   'arm2_block_delivery_range': [min(b['dose_ns'] / b['elig_ns'] for b in a2),
                                                 max(b['dose_ns'] / b['elig_ns'] for b in a2)],
                   'arm0_window_dose_n': sum(b['dose_n'] for b in a0),
                   'arm0_rows': sum(len(b['rows']) for b in a0)}
    # incomplete block window rows (read what exists) - dose fields and dose_n
    inc_rows_missing_fields = 0
    for b in blocks:
        if b['complete']: continue
        fr = arms[b['b']][3]
        for p in range(WLO, WHI + 1):
            n = fr + 1 + p
            if n in x and ('pc_dose_n' not in x[n] or 'pc_dose_ns' not in x[n]): inc_rows_missing_fields += 1
    out['dose']['incomplete_rows_missing_fields'] = inc_rows_missing_fields
    whole = {k: sum(v.get(k, 0) for v in x.values()) for k in ('pc_u_set', 'pc_skip_n', 'pc_refuse', 'pc_u_clr',
                                                               'pc_rearm_pages', 'pc_rearm_n', 'pc_op1', 'pc_offthr')}
    whole['last_pc_u_live'] = x[max(x)].get('pc_u_live')
    out['whole_log'] = whole
    out['rts_guard_window_rows'] = sum(1 for b in comp for r in b['rows']
                                       if r[2].get('rts_xthr', 0) or r[2].get('rts_acqw', 0) or r[2].get('rts_refuse', 0))
    # beta: pooled within-block OLS dt_us on draws, window rows of complete arm-0 blocks
    sxy = sxx = 0.0
    for b in a0:
        xs = [r[0]['draws'] for r in b['rows']]; ys = [r[0]['dt_us'] for r in b['rows']]
        mx, my = mean(xs), mean(ys)
        sxy += sum((u - mx) * (w - my) for u, w in zip(xs, ys)); sxx += sum((u - mx) ** 2 for u in xs)
    beta = sxy / sxx if sxx else 0.0
    out['beta'] = beta
    byb = {b['b']: b for b in comp}
    pairs = []
    for k in range(len(blocks) // 2):
        b0, b1 = byb.get(2 * k), byb.get(2 * k + 1)
        if b0 is None or b1 is None: continue
        if b0['arm'] == b1['arm']: raise SystemExit('pair with the same arm')
        z, t = (b0, b1) if b0['arm'] == 0 else (b1, b0)
        md = z['mode'] if z['mode'] == t['mode'] and z['mode'] != 'BETWEEN' else None
        pairs.append({'k': k, 'mode': md, 'ddt': t['dt'] - z['dt'], 'ddraws': t['draws'] - z['draws'],
                      'dcpu': t['cpu'] - z['cpu'], 'dgpu': t['gpu'] - z['gpu'], 'dose_us': t['dose_ns'] / len(t['rows']) / 1000})
    out['pairs_total'] = len(pairs)
    out['pairs_outside_mode'] = sum(1 for p in pairs if p['mode'] is None)
    res, read = {}, {}
    for md in ('NEW', 'OLD'):
        P = [p for p in pairs if p['mode'] == md]
        r = {'pairs': len(P)}
        if len(P) >= 2:
            d = [p['ddt'] for p in P]; da = [p['ddt'] - beta * p['ddraws'] for p in P]
            r.update({'d': mean(d), 'd_2se': 2 * se(d), 'd_adj': mean(da), 'd_adj_2se': 2 * se(da),
                      'ddraws': mean([p['ddraws'] for p in P]), 'ddraws_2se': 2 * se([p['ddraws'] for p in P]),
                      'dcpu': mean([p['dcpu'] for p in P]), 'dcpu_2se': 2 * se([p['dcpu'] for p in P]),
                      'dgpu': mean([p['dgpu'] for p in P]), 'dgpu_2se': 2 * se([p['dgpu'] for p in P]),
                      'pair_min': min(d), 'pair_max': max(d), 'pairs_below_500': sum(1 for v in d if v < 500),
                      'dose_us_arm2': mean([p['dose_us'] for p in P])})
            r['ratio_d_over_dose'] = r['d'] / r['dose_us_arm2']
        if len(P) >= 10:
            lo = min(r['d'] - r['d_2se'], r['d_adj'] - r['d_adj_2se'])
            hi = max(r['d'] + r['d_2se'], r['d_adj'] + r['d_adj_2se'])
            r['lower'] = lo; r['upper'] = hi
            r['verdict'] = 'K14_OPEN' if lo >= 500 else ('K14_CLOSED' if hi < 500 else 'NOT_RESOLVED')
            read[md] = r['verdict']
        else:
            r['verdict'] = 'DEBT' if P else 'no pair'
        res[md] = r
    out['modes'] = res
    if not pairs:
        T = 'NOT_EVALUABLE'
    elif any(v == 'K14_OPEN' for v in read.values()):
        T = 'K14_OPEN'
    elif read and all(v == 'K14_CLOSED' for v in read.values()):
        T = 'K14_CLOSED'
    else:
        T = 'NOT_RESOLVED'
    kpx = {0: 0, 1: 0}; att = {0: 0, 1: 0}; att0 = {0: 0, 1: 0}
    for b in comp:
        for r in b['rows']:
            if r[2]['rt_att'] == 0: att0[b['arm']] += 1; continue
            kpx[b['arm']] += r[2]['rt_kpx']; att[b['arm']] += r[2]['rt_att']
    m0 = Fraction(kpx[0], att[0]); m2 = Fraction(kpx[1], att[1])
    mixed = 100 * abs(m2 - m0) > m0
    out['drs'] = {'m0': float(m0), 'm2': float(m2), 'rt_att0_rows': att0, 'mixed': mixed}
    if mixed: T = 'NOT_RESOLVED'
    out['T'] = T
    base = {}
    for md in ('ALL', 'NEW', 'OLD', 'BETWEEN'):
        v = [r[0]['dt_us'] for b in a0 if (md == 'ALL' or b['mode'] == md) for r in b['rows']]
        if v: base[md] = {'rows': len(v), 'blocks': sum(1 for b in a0 if md == 'ALL' or b['mode'] == md),
                          'mean_dt_us': mean(v), 'speed_pct': 100 * 16667 / mean(v)}
    v2 = [r[0]['dt_us'] for b in a2 for r in b['rows']]
    base['arm2_mean_dt_us'] = mean(v2)
    out['base'] = base
    # rows (levels), not guards
    def lvl(arm, key, where):
        vals = []
        for b in comp:
            if b['arm'] != arm: continue
            for r in b['rows']:
                d = r[where]
                if key in d: vals.append(d[key])
        return mean(vals) if vals else None
    rowkeys = [('dt_us', 0), ('draws', 0), ('cpu_gpu_us', 0), ('gpu_busy_us', 0), ('faults_gpu', 0), ('fault_gpu_us', 0),
               ('faults_main', None), ('fault_main_us', None), ('prot_gpu_us', None), ('pb_wait_gpu_us', None),
               ('sync_up_kb', None), ('fw_n', None), ('tex_inval', None), ('img_up_kb', None), ('img_pend_kb', None),
               ('bda_scan', 1), ('pc_elig_ns', 2), ('pc_elig_n', 2), ('pc_dose_ns', 2), ('pc_dose_n', 2),
               ('prot_gpu_ro_ns', 2), ('prot_gpu_na_ns', 2), ('prot_gpu_rw_ns', 2), ('bl_trip', None)]
    lev = {}
    for k, w in rowkeys:
        for arm in (0, 1):
            val = None
            for where in ((w,) if w is not None else (0, 1, 2)):
                val = lvl(arm, k, where)
                if val is not None: break
            lev.setdefault(k, {})['arm%d' % (0 if arm == 0 else 2)] = val
    out['levels'] = lev
    out['skipped_draw_window'] = sum(1 for b in comp for r in b['rows'] if r[1].get('d_skip', 0))
    return out


def attempt(tag='pd128'):
    j = json.load(open(ROOT + '%s.json' % tag, encoding='utf-8'))
    return j


if __name__ == '__main__':
    R = run()
    print(json.dumps(R, ensure_ascii=True, indent=1, default=str))
