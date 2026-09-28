# Session 129 audit (HPP-138, Session Auditor): independent recount of the sealed ac129 (ABBA armcopy=0|1), the
# self-check ack129 (armcopy=2), the videos acv129/acw129 and the correctness smokes of step 5, from the RAW logs.
# No code shared with ac129.py, smk129.py, chk_ac129.py (none of them read or imported); port of my own
# audit128/recount128.py (blocks and estimators), extended for the armcopy counters.
# Blocks ONLY by 'GateArm:' lines; row of position p of block b: FrameTrace n = frame_b + 1 + p (pred s.5);
# window 10..88 inclusive (item 55(b)); level = mean of window rows; SE over pairs (n-1).
# Constants: pred/01_ac129.md s.1, s.5, s.8, s.10; ROADMAP item 97(e)(4)-(6), 102(b), 104(a).
import json, math, os, re, sys
from fractions import Fraction

ROOT = 'C:/kyty/s129/'
WLO = int(os.environ.get('RC_WLO', '10'))
WHI = int(os.environ.get('RC_WHI', '88'))
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
GA = re.compile(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(\S*)')
DEATH = (b'--- std::terminate ---', b'--- abort() ---', b'--- Error ---', b'--- Fatal Error ---', b'GpuHangAbort:',
         b'ErrorDeviceLost', b'VK_ERROR_DEVICE_LOST', b'Unhandled exception', b'ReportVulkanFatal')
ACK = ('ac_n', 'ac_chk', 'ac_bad', 'ac_gchk', 'ac_gbad', 'ac_jleft', 'ac_jremark', 'ac_gjleft', 'ac_orphan',
       'ac_cmp_pages', 'ac_cdiff', 'ac_cbad', 'ac_refuse', 'ac_offthr', 'ac_moved_n', 'ac_kept_n', 'pb_stuck',
       'pb_inflight_bad', 'pc_u_set', 'pc_skip_n', 'pc_refuse', 'pc_dose_n')


def kv(line):
    return {k.decode(): int(v) for k, v in KV.findall(line)}


def read_log(path):
    main, drw, x = {}, {}, {}
    dup = {'main': 0, 'draw': 0, 'x': 0}
    arms = []
    L = {'armcopy_mode': [], 'armcopy_refused': 0, 'protceil': [], 'rtskip': [], 'rtskip_refused': 0,
         'skipped_draw': 0, 'death': 0, 'gpuwaitslow': 0, 'bvhtrip': 0, 'clockpin': 0,
         'verify_mismatch': [], 'verify_left': [], 'verify_content': 0, 'verify_other': 0}
    with open(path, 'rb') as f:
        for raw in f:
            s = raw.lstrip()
            if s.startswith(b'FrameTrace: '):
                d = kv(s[12:]); n = d['n']
                if n in main: dup['main'] += 1
                main[n] = d
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
                t = s.strip().decode(errors='replace')
                if b'ArmCopy: mode' in s: L['armcopy_mode'].append(t[:40])
                if b'ArmCopy: refused' in s: L['armcopy_refused'] += 1
                if b'ProtCeil:' in s: L['protceil'].append(t[:40])
                if b'RtSkip: mode' in s: L['rtskip'].append(t[:40])
                if b'RtSkip: refused' in s: L['rtskip_refused'] += 1
                if b'AsyncPipelines: skipped draw' in s: L['skipped_draw'] += 1
                if any(k in s for k in DEATH): L['death'] += 1
                if b'GpuWaitSlow' in s: L['gpuwaitslow'] += 1
                if b'BvhLoopCapTrip' in s: L['bvhtrip'] += 1
                if s.startswith(b'GpuClockPin: mode 1'): L['clockpin'] += 1
                if b'ArmCopyVerify:' in s:
                    if b'MISMATCH' in s: L['verify_mismatch'].append(t)
                    elif b'LEFT' in s: L['verify_left'].append(t)
                    elif b'CONTENT' in s: L['verify_content'] += 1
                    else: L['verify_other'] += 1
    return main, drw, x, arms, dup, L


def mean(v):
    return sum(v) / len(v)


def se(v):
    m = mean(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1)) / math.sqrt(len(v))


def mode_of(avg):
    return 'NEW' if avg <= 300 else ('OLD' if avg >= 600 else 'BETWEEN')


def field(r, k):
    for d in r:
        if k in d: return d[k]
    return None


def whole(x, keys):
    return {k: sum(v.get(k, 0) for v in x.values()) for k in keys}


def abba(tag, TXT):
    main, drw, x, arms, dup, L = read_log(ROOT + 'log_%s.txt' % tag)
    out = {'tag': tag, 'window': [WLO, WHI], 'dup': dup, 'gatearm_lines': len(arms),
           'lines': {k: (len(v) if isinstance(v, list) else v) for k, v in L.items()},
           'armcopy_mode_lines': L['armcopy_mode'], 'protceil_lines': sorted(set(L['protceil'])),
           'rtskip_lines': L['rtskip']}
    AB = (0, 1, 1, 0)
    bad = []
    for i, (arm, narms, blk, fr, per, ab, text) in enumerate(arms):
        e = AB[i % 4]
        if blk != i or fr != 1800 + 90 * i or narms != 2 or per != 90 or ab != 1 or arm != e or text != TXT[e]:
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
        blocks.append({'b': i, 'arm': arm, 'fr': fr, 'complete': ok, 'rows': rows if ok else None})
    comp = [b for b in blocks if b['complete']]
    out['blocks'] = len(blocks); out['complete'] = len(comp)
    out['complete_by_arm'] = {a: sum(1 for b in comp if b['arm'] == a) for a in (0, 1)}
    out['incomplete'] = [b['b'] for b in blocks if not b['complete']]
    for b in comp:
        R = b['rows']
        for k, w in (('dt', 'dt_us'), ('draws', 'draws'), ('cpu', 'cpu_gpu_us'), ('gpu', 'gpu_busy_us')):
            b[k] = mean([r[0][w] for r in R])
        b['bda'] = mean([r[1]['bda_scan'] for r in R])
        b['mode'] = mode_of(b['bda'])
        for k in ('prot_gpu_ro_ns', 'pb_wait_gpu_us', 'acopy_wait_us', 'stg_pool_ns'):
            b[k] = mean([field(r, k) for r in R])
    out['block_modes'] = {m: sum(1 for b in comp if b['mode'] == m) for m in ('NEW', 'OLD', 'BETWEEN')}
    out['bda_range'] = [min(b['bda'] for b in comp), max(b['bda'] for b in comp)]
    a1 = [b for b in comp if b['arm'] == 1]; a0 = [b for b in comp if b['arm'] == 0]
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
        p = {'k': k, 'mode': md, 'ddt': t['dt'] - z['dt'], 'ddraws': t['draws'] - z['draws'],
             'dcpu': t['cpu'] - z['cpu'], 'dgpu': t['gpu'] - z['gpu']}
        for kk in ('prot_gpu_ro_ns', 'pb_wait_gpu_us', 'acopy_wait_us', 'stg_pool_ns'):
            p['d_' + kk] = t[kk] - z[kk]
        pairs.append(p)
    out['pairs_total'] = len(pairs)
    out['pairs_outside_mode'] = sum(1 for p in pairs if p['mode'] is None)
    res, read = {}, {}
    for md in ('NEW', 'OLD'):
        P = [p for p in pairs if p['mode'] == md]
        r = {'pairs': len(P)}
        if len(P) >= 2:
            d = [p['ddt'] for p in P]; da = [p['ddt'] - beta * p['ddraws'] for p in P]
            r.update({'d': mean(d), 'd_2se': 2 * se(d), 'd_adj': mean(da), 'd_adj_2se': 2 * se(da),
                      'pair_min': min(d), 'pair_max': max(d), 'pairs_above_m100': sum(1 for v in d if v > -100)})
            for key in ('ddraws', 'dcpu', 'dgpu', 'd_prot_gpu_ro_ns', 'd_pb_wait_gpu_us', 'd_acopy_wait_us',
                        'd_stg_pool_ns'):
                v = [p[key] for p in P]
                r[key] = mean(v); r[key + '_2se'] = 2 * se(v)
            r['ratio_d_over_pd128'] = r['d'] / 1016.8
        if len(P) >= 10:
            hi = max(r['d'] + r['d_2se'], r['d_adj'] + r['d_adj_2se'])
            lo = min(r['d'] - r['d_2se'], r['d_adj'] - r['d_adj_2se'])
            r['upper'] = hi; r['lower'] = lo
            r['verdict'] = 'ARMCOPY_GAIN' if hi <= -100 else ('ARMCOPY_NO_GAIN' if lo > -100 else 'NOT_RESOLVED')
            read[md] = r['verdict']
        else:
            r['verdict'] = 'DEBT'
        res[md] = r
    out['modes'] = res
    if any(v == 'ARMCOPY_GAIN' for v in read.values()):
        T = 'ARMCOPY_GAIN'
    elif read and all(v == 'ARMCOPY_NO_GAIN' for v in read.values()):
        T = 'ARMCOPY_NO_GAIN'
    else:
        T = 'NOT_RESOLVED'
    kpx = {0: 0, 1: 0}; att = {0: 0, 1: 0}; att0 = {0: 0, 1: 0}
    for b in comp:
        for r in b['rows']:
            if r[2]['rt_att'] == 0: att0[b['arm']] += 1; continue
            kpx[b['arm']] += r[2]['rt_kpx']; att[b['arm']] += r[2]['rt_att']
    m0 = Fraction(kpx[0], att[0]); m1 = Fraction(kpx[1], att[1])
    mixed = 100 * abs(m1 - m0) > m0
    out['drs'] = {'m0': float(m0), 'm1': float(m1), 'rt_att0_rows': att0, 'mixed': mixed}
    if mixed: T = 'NOT_RESOLVED'
    out['T'] = T
    base = {}
    for md in ('ALL', 'NEW', 'OLD', 'BETWEEN'):
        v = [r[0]['dt_us'] for b in a0 if (md == 'ALL' or b['mode'] == md) for r in b['rows']]
        if v: base[md] = {'rows': len(v), 'blocks': sum(1 for b in a0 if md == 'ALL' or b['mode'] == md),
                          'mean_dt_us': mean(v), 'speed_pct': 100 * 16667 / mean(v)}
    base['arm1_mean_dt_us'] = mean([r[0]['dt_us'] for b in a1 for r in b['rows']])
    base['arm0_bda'] = mean([r[1]['bda_scan'] for b in a0 for r in b['rows']])
    base['arm1_bda'] = mean([r[1]['bda_scan'] for b in a1 for r in b['rows']])
    out['base'] = base
    # share S and guard of item 102(b): window rows of complete arm-1 blocks
    S = {k: sum(r[2][k] for b in a1 for r in b['rows']) for k in
         ('ac_moved_ns', 'ac_kept_ns', 'ac_moved_n', 'ac_kept_n', 'ac_job_other_n', 'ac_kept_help_n', 'ac_kept_inl_ns',
          'ac_kept_gap_ns', 'ac_kept_full_ns', 'ac_kept_tmp_ns', 'ac_kept_wr_ns', 'ac_kept_help_ns', 'pc_elig_n',
          'ac_orphan', 'ac_n')}
    S['rows'] = sum(len(b['rows']) for b in a1)
    S['S'] = S['ac_moved_ns'] / (S['ac_moved_ns'] + S['ac_kept_ns'])
    S['other_over_moved'] = S['ac_job_other_n'] / S['ac_moved_n']
    S['guard_102b_pass'] = 100 * S['ac_job_other_n'] <= S['ac_moved_n']
    S['T3'] = S['pc_elig_n'] - (S['ac_kept_n'] - S['ac_kept_help_n'])
    out['share'] = S
    # arm 0 window (all arm-0 blocks, complete or not) must not run the mechanism
    off0 = {k: 0 for k in ('ac_n', 'ac_jobs', 'ac_chunks', 'ac_moved_n', 'ac_kept_n', 'ac_chk')}; rows0 = 0
    for b in blocks:
        if b['arm'] != 0: continue
        for p in range(WLO, WHI + 1):
            n = b['fr'] + 1 + p
            if n in x:
                rows0 += 1
                for k in off0: off0[k] += x[n].get(k, 0)
    off0['rows'] = rows0
    out['arm0_window_off'] = off0
    out['arm0_pos0_9_moved'] = sum(x.get(b['fr'] + 1 + p, {}).get('ac_moved_n', 0)
                                   for b in blocks if b['arm'] == 0 for p in range(0, 10))
    out['arm1_blocks_without_ac_n'] = [b['b'] for b in a1 if sum(r[2]['ac_n'] for r in b['rows']) == 0]
    out['whole_log'] = whole(x, ACK)
    out['rts_guard_window_rows'] = sum(1 for b in comp for r in b['rows']
                                       if r[2].get('rts_xthr', 0) or r[2].get('rts_acqw', 0) or r[2].get('rts_refuse', 0))
    out['gclk_pin_window'] = {a: sum(r[2].get('gclk_pin', 0) for b in comp if b['arm'] == a for r in b['rows'])
                              for a in (0, 1)}
    out['max_dt_after_1800'] = max(v['dt_us'] for n, v in main.items() if n > 1800)
    out['stg_res_ns_window'] = {a: sum(r[2].get('stg_res_ns', 0) for b in comp if b['arm'] == a for r in b['rows'])
                                for a in (0, 1)}
    # sensitivity rows (not the rule): other windows
    return out


def constant(tag):
    main, drw, x, arms, dup, L = read_log(ROOT + 'log_%s.txt' % tag)
    o = {'tag': tag, 'dup': dup, 'gatearm_lines': len(arms),
         'lines': {k: (len(v) if isinstance(v, list) else v) for k, v in L.items()},
         'armcopy_mode_lines': L['armcopy_mode'], 'protceil_lines': sorted(set(L['protceil'])),
         'rtskip_lines': L['rtskip'], 'whole_log': whole(x, ACK), 'x_rows': len(x), 'main_rows': len(main),
         'max_dt_after_1800': max((v['dt_us'] for n, v in main.items() if n > 1800), default=None)}
    left = []
    for t in L['verify_left']:
        d = dict(re.findall(r'(\w+)=(\S+)', t))
        left.append({'br': d.get('br'), 'pages': int(d.get('pages', '0')), 'perms': d.get('perms'), 'rm': d.get('rm'),
                     'mode': d.get('mode')})
    o['left'] = left
    o['left_pages_by_branch'] = {br: sum(e['pages'] for e in left if e['br'] == br) for br in ('job', 'gpu')}
    o['left_perms'] = sorted(set(e['perms'] for e in left))
    o['mismatch_branches'] = {}
    for t in L['verify_mismatch']:
        m = re.search(r'br=(\w+)', t)
        k = m.group(1) if m else '?'
        o['mismatch_branches'][k] = o['mismatch_branches'].get(k, 0) + 1
    w = o['whole_log']
    if w['ac_bad'] > 0 or w['ac_gbad'] > 0 or w['ac_jleft'] - w['ac_jremark'] > 0:
        o['selfcheck'] = 'ARMCOPY_INCORRECT'
    elif w['ac_chk'] == 0:
        o['selfcheck'] = 'NOT_RESOLVED'
    else:
        o['selfcheck'] = 'SELFCHECK_CLEAN'
    o['cbad_per_page'] = (w['ac_cbad'] / w['ac_cmp_pages']) if w['ac_cmp_pages'] else None
    return o


def smoke_share(tag):
    # item 97(e)(2) share on the arm-1 window of a 0|1 smoke (row, not read per item 104(a))
    main, drw, x, arms, dup, L = read_log(ROOT + 'log_%s.txt' % tag)
    s = {k: 0 for k in ('ac_moved_ns', 'ac_kept_ns', 'ac_moved_n', 'ac_job_other_n', 'ac_kept_help_n')}; rows = 0
    for i, a in enumerate(arms):
        arm, fr = a[0], a[3]
        if arm != 1: continue
        ok = all((fr + 1 + p) in main and (fr + 1 + p) in x and main[fr + 1 + p].get('blk') == i for p in range(WLO, WHI + 1))
        if not ok: continue
        for p in range(WLO, WHI + 1):
            rows += 1
            for k in s: s[k] += x[fr + 1 + p][k]
    s['rows'] = rows
    s['S'] = s['ac_moved_ns'] / (s['ac_moved_ns'] + s['ac_kept_ns'])
    s['other_over_moved'] = s['ac_job_other_n'] / s['ac_moved_n']
    s['death'] = L['death']; s['gpuwaitslow'] = L['gpuwaitslow']
    return s


def smoke_sums(tag):
    main, drw, x, arms, dup, L = read_log(ROOT + 'log_%s.txt' % tag)
    w = whole(x, ACK)
    # per arm by the text of the GateArm line (the flip takes the counters of the leaving arm: rows by main arm=)
    per = {}
    for n, v in x.items():
        a = main.get(n, {}).get('arm')
        d = per.setdefault(str(a), {k: 0 for k in ('ac_chk', 'ac_bad', 'ac_gchk', 'ac_gbad')})
        for k in d: d[k] += v.get(k, 0)
    return {'tag': tag, 'whole': w, 'per_main_arm': per, 'arms_text': sorted(set(a[6] for a in arms)),
            'death': L['death'], 'gpuwaitslow': L['gpuwaitslow'], 'armcopy_mode_lines': L['armcopy_mode'],
            'left_lines': len(L['verify_left']), 'mismatch_lines': len(L['verify_mismatch'])}


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'ac129'
    if what == 'ac129':
        R = abba('ac129', {0: 'armcopy=0', 1: 'armcopy=1'})
    elif what in ('ack129', 'acv129', 'acw129'):
        R = constant(what)
    elif what == 'smokes':
        R = {'shares': {t: smoke_share(t) for t in ('s1s129', 's7s129')},
             'sums': {t: smoke_sums(t) for t in ('s2s129', 's3s129', 's4s129', 's8s129', 's9s129')}}
    else:
        raise SystemExit('usage: recount129.py ac129|ack129|acv129|acw129|smokes')
    print(json.dumps(R, ensure_ascii=True, indent=1, default=str))
