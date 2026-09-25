"""Independent recount of session 119 seal 01 (g2_119) - audit119, lens "independent recount".

Written from the session-104 pre-registration C:/kyty/s104/pred/02_a_stage1.md sections 3-6 and the session-119
pre-registration C:/kyty/s119/pred/01_g2_119.md only; nothing is imported or copied from g2_119.py or a104.py.

Population: blocks of 90 from frame 1800 (block b = the main-line blk= field, frame of row n = n - 1, so the row's index
in its block is n - 1 - 1800 - 90 b); kept rows idx 60..88; a block is usable only if all 29 kept rows exist and its first
kept frame >= 2100; pairs (4q, 4q+1) and (4q+2, 4q+3) inside complete ABBA quartets (arms 0,1,1,0); per block the mean of
its kept rows; an arm's level = the median of its selected block means; d X = mean over pairs of (arm1 - arm0); SE =
sample sd / sqrt(n).

usage: python recount119.py            (reads C:/kyty/s119/log_sh119.txt and log_mut119.txt)
"""
import math
import re
import statistics
import sys

START, PERIOD, KEEP_LO, KEEP_HI, FIRST_KEPT_MIN = 1800, 90, 60, 88, 2100
ABBA = (0, 1, 1, 0)

MAIN = ['dt_us', 'draws', 'dispatches', 'cpu_gpu_us', 'gpu_busy_us', 'arm', 'blk']
DRAW = ['spin_gpu_us', 'rec_n', 'bda_n', 'da_walk_us', 'da_queue_us', 'da_take_us']
XLIN = ['a_mut_us', 'a_mut_n', 'a_hold_us', 'a_hold_n', 'mw_n', 'mh_n', 'mh_disp_n', 'mh_draws', 'mh_prog_us',
        'mh_emit_us', 'pl_prog_hold_us', 'pl_prog_n', 'pl_pipe_n', 'pl_cs_n', 'pl_em_n', 'pl_em_vtx_ns', 'pl_em_rt_ns',
        'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns', 'pl_em_rest_ns', 'pl_pref_ns', 'pl_pref_n', 'pl_proc_n',
        'sh_jobs', 'sh_us', 'sh_push_us', 'sh_drop', 'rt_att', 'rt_kpx', 'da_wjobs', 'gm_ops']
KINDS = {b'FrameTrace:': MAIN, b'FrameTrace-draw:': DRAW, b'FrameTrace-x:': XLIN}
TOK = re.compile(rb'([A-Za-z0-9_]+)=(-?\d+)')


def parse(path):
    rows = {}           # n -> dict
    dup_names = 0
    lines = {k: 0 for k in KINDS}
    other = {'gateArm': [], 'pin': 0, 'rec_started': 0, 'ckpt': 0, 'hang': 0, 'fatal': 0, 'worker': []}
    fatal = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---', b'ErrorDeviceLost',
             b'Unhandled exception:', b'GpuWaitSlow:', b'AsyncPipelines: skipped draw')
    with open(path, 'rb') as f:
        for line in f:
            head = line.split(b' ', 1)[0]
            if head in KINDS:
                lines[head] += 1
                want = KINDS[head]
                d = {}
                names = []
                for m in TOK.finditer(line):
                    k = m.group(1).decode()
                    names.append(k)
                    d[k] = int(m.group(2))
                if len(names) != len(set(names)):
                    dup_names += 1
                n = d['n']
                r = rows.setdefault(n, {})
                for k in want:
                    if k not in d:
                        raise SystemExit('%s: field %s missing on %s n=%d' % (path, k, head, n))
                    if k in r:
                        raise SystemExit('%s: field %s twice for n=%d' % (path, k, n))
                    r[k] = d[k]
                continue
            if line.startswith(b'GateArm:'):
                other['gateArm'].append(line.rstrip(b'\r\n').decode('utf-8', 'replace'))
            elif line.startswith(b'GpuClockPin: mode'):
                other['pin'] += 1
            elif line.startswith(b'RecordThread: started'):
                other['rec_started'] += 1
            elif b'GPU checkpoints' in line:
                other['ckpt'] += 1
            elif b'GpuHangAbort' in line:
                other['hang'] += 1
            elif line.startswith(b'ShadowResolve: worker'):
                other['worker'].append(line.rstrip(b'\r\n').decode())
            if any(x in line for x in fatal):
                other['fatal'] += 1
    return rows, lines, dup_names, other


def population(rows):
    blocks = {}
    bad_idx = 0
    bad_arm = 0
    for n, r in rows.items():
        if len(r) != len(MAIN) + len(DRAW) + len(XLIN):
            continue
        b = r['blk']
        idx = n - 1 - START - PERIOD * b
        if not (0 <= idx < PERIOD):
            if n - 1 >= START:
                bad_idx += 1
            continue
        if n - 1 >= START and r['arm'] != ABBA[b % 4]:
            bad_arm += 1
        if KEEP_LO <= idx <= KEEP_HI:
            blocks.setdefault(b, {})[idx] = r
    usable = {}
    for b, kept in blocks.items():
        if len(kept) == KEEP_HI - KEEP_LO + 1 and START + PERIOD * b + KEEP_LO >= FIRST_KEPT_MIN:
            usable[b] = [kept[i] for i in range(KEEP_LO, KEEP_HI + 1)]
    quartets = sorted({b // 4 for b in usable})
    complete = [q for q in quartets if all((4 * q + j) in usable for j in range(4))]
    selected = {b: usable[b] for q in complete for b in range(4 * q, 4 * q + 4)}
    excluded = sorted(set(usable) - set(selected))
    pairs = []
    for q in complete:
        pairs.append((4 * q, 4 * q + 1))       # arm 0, arm 1  (A B)
        pairs.append((4 * q + 3, 4 * q + 2))   # arm 0, arm 1  (B A: block 4q+2 is arm 1, 4q+3 is arm 0)
    return selected, pairs, excluded, bad_idx, bad_arm, sorted(blocks)


def bmean(block, fn):
    return sum(fn(r) for r in block) / len(block)


def level(selected, arm, fn):
    return statistics.median(bmean(v, fn) for b, v in selected.items() if ABBA[b % 4] == arm)


def delta(selected, pairs, fn):
    d = [bmean(selected[b1], fn) - bmean(selected[b0], fn) for b0, b1 in pairs]
    m = sum(d) / len(d)
    se = statistics.stdev(d) / math.sqrt(len(d))
    return m, se, len(d)


def total(selected, arm, fn):
    return sum(fn(r) for b, v in selected.items() if (arm is None or ABBA[b % 4] == arm) for r in v)


def cpu_net(r):
    return r['cpu_gpu_us'] - r['spin_gpu_us']


def main():
    runs = {}
    for tag in ('sh119', 'mut119'):
        rows, lines, dups, other = parse('C:/kyty/s119/log_%s.txt' % tag)
        sel, pairs, excl, bad_idx, bad_arm, allb = population(rows)
        runs[tag] = (rows, sel, pairs)
        orient = [sum(1 for b0, b1 in pairs if b0 % 4 == 0), sum(1 for b0, b1 in pairs if b0 % 4 == 3)]
        print('== %s rows %d  lines %s  dup-name lines %d  blocks seen %d..%d  selected %d  pairs %d (AB %d, BA %d)'
              '  excluded usable %s  bad idx %d  arm/ABBA mismatches %d'
              % (tag, len(rows), {k.decode(): v for k, v in lines.items()}, dups, allb[0], allb[-1], len(sel),
                 len(pairs), orient[0], orient[1], excl, bad_idx, bad_arm))
        ga = other['gateArm']
        ga_bad = 0
        for g in ga:
            m = re.match(r'GateArm: arm=(\d+) arms=2 block=(\d+) frame=(\d+) period=90 abba=1 text=(.*)$', g)
            if not m:
                ga_bad += 1
                continue
            a, b, fr = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a != ABBA[b % 4] or fr != START + PERIOD * b:
                ga_bad += 1
        print('   GateArm lines %d (bad %d); texts %s' % (len(ga), ga_bad, sorted({g.split('text=', 1)[1] + ' @arm' + g.split()[1][4:] for g in ga})))
        print('   pin lines %d  RecordThread started %d  checkpoint lines %d  GpuHangAbort %d  fatal %d  workers %s'
              % (other['pin'], other['rec_started'], other['ckpt'], other['hang'], other['fatal'], other['worker']))
        for name, fn in (('dt_us', lambda r: r['dt_us']), ('cpu_net', cpu_net), ('draws', lambda r: r['draws']),
                         ('gpu_busy_us', lambda r: r['gpu_busy_us']), ('rec_n', lambda r: r['rec_n']),
                         ('a_mut_us', lambda r: r['a_mut_us']), ('a_hold_us', lambda r: r['a_hold_us']),
                         ('mw_n', lambda r: r['mw_n']), ('mh_prog_us', lambda r: r['mh_prog_us']),
                         ('mh_emit_us', lambda r: r['mh_emit_us']), ('pl_prog_hold_us', lambda r: r['pl_prog_hold_us']),
                         ('pl_em_rec_us', lambda r: r['pl_em_rec_ns'] / 1000), ('pl_em_com_us', lambda r: r['pl_em_com_ns'] / 1000),
                         ('walk-queue', lambda r: r['da_walk_us'] - r['da_queue_us']), ('da_take_us', lambda r: r['da_take_us']),
                         ('sh_jobs', lambda r: r['sh_jobs']), ('sh_us', lambda r: r['sh_us']), ('sh_push_us', lambda r: r['sh_push_us'])):
            print('   %-16s arm0 %10.1f  arm1 %10.1f' % (name, level(sel, 0, fn), level(sel, 1, fn)))
        for name, fn in (('cpu_net', cpu_net), ('dt_us', lambda r: r['dt_us']), ('draws', lambda r: r['draws'])):
            m, se, n = delta(sel, pairs, fn)
            print('   d %-8s mean %9.2f  2SE %8.2f  t %6.2f  n %d' % (name, m, 2 * se, m / se, n))
    return runs


# ---------------------------------------------------------------------------------------------------------------------
# G2 terms, arming checks and controls (sections 4-6 of the session-104 pre-registration, section "THE RULE" of 119)

F2, F2_SENS, BAR, C_TS, W_E, SPINE_FLOOR = 0.555, 0.564, 3000.0, 3.96, 1115.575, 959.0


def g_terms(runs):
    rows_s, sel_s, pairs_s = runs['sh119']
    rows_m, sel_m, pairs_m = runs['mut119']
    L = level
    out = {}
    out['cpu_net'] = cpu_net_ = L(sel_s, 0, cpu_net)
    T2, T2se, T2n = delta(sel_s, pairs_s, cpu_net)
    dT_dt, dT_dt_se, _ = delta(sel_s, pairs_s, lambda r: r['dt_us'])
    out['T2'], out['T2_2SE'] = T2, 2 * T2se
    out['T2_dt'], out['T2_dt_2SE'] = dT_dt, 2 * dT_dt_se
    out['sh_push'] = sh_push = L(sel_s, 1, lambda r: r['sh_push_us'])
    out['S_lo'] = L(sel_m, 0, lambda r: r['a_mut_us'])
    out['S_raw'] = S_raw = L(sel_m, 1, lambda r: r['a_mut_us'])
    P, Pse, _ = delta(sel_m, pairs_m, cpu_net)
    out['P_mw'], out['P_mw_2SE'] = P, 2 * Pse
    tin_expr = lambda r: 5 * r['pl_em_n'] + 3 * (r['pl_prog_n'] + r['pl_pipe_n'] + r['pl_cs_n']) + r['a_mut_n']
    out['T_in'] = T_in = L(sel_m, 1, tin_expr)
    out['T_in_alt_sum_of_levels'] = (5 * L(sel_m, 1, lambda r: r['pl_em_n']) + 3 * (L(sel_m, 1, lambda r: r['pl_prog_n'])
                                     + L(sel_m, 1, lambda r: r['pl_pipe_n']) + L(sel_m, 1, lambda r: r['pl_cs_n']))
                                     + L(sel_m, 1, lambda r: r['a_mut_n']))
    out['dI'] = dI = C_TS * T_in / 1000
    out['E_rec'] = E_rec = L(sel_m, 1, lambda r: r['pl_em_rec_ns'] / 1000)
    out['E_com'] = E_com = L(sel_m, 1, lambda r: r['pl_em_com_ns'] / 1000)
    out['S_now'] = S_now = S_raw - max(P, 0) - dI
    out['E_move'] = E_move = E_rec + W_E
    out['S_ctx'] = S_ctx = S_now - E_move
    out['spine_proxy_mut0'] = sp = L(sel_m, 0, lambda r: r['da_walk_us'] - r['da_queue_us'])
    out['spine_proxy_sh0'] = L(sel_s, 0, lambda r: r['da_walk_us'] - r['da_queue_us'])
    out['spine'] = spine = max(sp, SPINE_FLOOR)

    def G(f, sctx, t2):
        return cpu_net_ - (sctx + f * (cpu_net_ - sctx)) - spine - t2
    out['G2'] = G(F2, S_ctx, T2)
    out['G2_f0564'] = G(F2_SENS, S_ctx, T2)
    out['G2_wall'] = out['G2'] - max(0.0, dT_dt - T2)
    out['S_now^'] = S_now_c = S_raw - max(P + 2 * Pse, 0) - 2 * dI
    out['E_move^'] = E_move_c = E_rec + E_com
    out['S_ctx^'] = S_ctx_c = S_now_c - E_move_c
    out['T2^'] = T2_c = max(0.0, T2 - 2 * T2se - sh_push)
    out['G2^'] = G(F2, S_ctx_c, T2_c)
    out['G2^_f0564'] = G(F2_SENS, S_ctx_c, T2_c)
    out['T2_to_bar'] = out['G2'] + T2 - BAR
    pref_spine = L(sel_m, 0, lambda r: r['pl_pref_ns'] / 1000 - r['da_queue_us'])
    out['spine_pref_based'] = pref_spine
    out['G2_pref_spine'] = cpu_net_ - (S_ctx + F2 * (cpu_net_ - S_ctx)) - pref_spine - T2
    out['H/M_levels_arm1'] = L(sel_m, 1, lambda r: r['pl_prog_hold_us']) / L(sel_m, 1, lambda r: r['mh_prog_us'])
    out['H/M_levels_arm0'] = L(sel_m, 0, lambda r: r['pl_prog_hold_us']) / L(sel_m, 0, lambda r: r['mh_prog_us'])
    out['xrun_price'] = L(sel_m, 0, cpu_net) - cpu_net_

    def area(sel, arm):
        return total(sel, arm, lambda r: r['rt_kpx']) / total(sel, arm, lambda r: r['rt_att'])
    out['area_sh0'], out['area_mut0'] = area(sel_s, 0), area(sel_m, 0)
    out['area_xrun_pct'] = 100 * (out['area_mut0'] / out['area_sh0'] - 1)
    for tag, sel, pairs in (('sh', sel_s, pairs_s), ('mut', sel_m, pairs_m)):
        n1 = sum(len(v) for b, v in sel.items() if ABBA[b % 4] == 1)
        n0 = sum(len(v) for b, v in sel.items() if ABBA[b % 4] == 0)
        d1 = total(sel, 1, lambda r: r['draws']) / n1
        d0 = total(sel, 0, lambda r: r['draws']) / n0
        out['work_pct_' + tag] = 100 * (d1 / d0 - 1)
        out['area_split_pct_' + tag] = 100 * (area(sel, 1) / area(sel, 0) - 1)

        def barea(b, sel=sel):
            return sum(r['rt_kpx'] for r in sel[b]) / sum(r['rt_att'] for r in sel[b])
        out['area_pair_match_pct_' + tag] = 100 * sum(1 for b0, b1 in pairs if abs(barea(b1) / barea(b0) - 1) < 0.005) / len(pairs)
    return out


def ratio_check(sel, arm, num, den):
    return level(sel, arm, num) / level(sel, arm, den) - 1


def arming(runs):
    res = []
    rows_s, sel_s, pairs_s = runs['sh119']
    rows_m, sel_m, pairs_m = runs['mut119']

    def f(k):
        return lambda r: r[k]
    # mut
    t0, t1 = total(sel_m, 0, f('mw_n')), total(sel_m, 1, f('mw_n'))
    res.append(('MW_DARK_ARM0', level(sel_m, 0, f('mw_n')) == 0 and t0 <= 0.001 * t1,
                'level0 %.1f tot0 %d tot1 %d' % (level(sel_m, 0, f('mw_n')), t0, t1)))
    v = ratio_check(sel_m, 1, f('mw_n'), lambda r: 2 * r['mh_n'] + r['mh_disp_n'] + r['bda_n'])
    res.append(('MW_IDENTITY_ARM1', abs(v) <= 0.02, '%.4f' % v))
    ok = all(level(sel_m, a, f('a_mut_us')) > 0 and level(sel_m, a, f('a_mut_n')) > 0 for a in (0, 1))
    res.append(('AMUT_ARMED', ok, ''))
    vv = [ratio_check(sel_m, a, f('a_hold_n'), lambda r: r['mh_n'] + r['mh_disp_n']) for a in (0, 1)]
    res.append(('MUTSITE_HOLD_IDENTITY', all(abs(x) <= 0.02 for x in vv) and all(level(sel_m, a, f('mh_n')) > 0 for a in (0, 1)),
                '%s' % ['%.4f' % x for x in vv]))
    v1 = [ratio_check(sel_m, a, f('pl_prog_n'), f('mh_n')) for a in (0, 1)]
    v2 = [ratio_check(sel_m, a, f('pl_cs_n'), f('dispatches')) for a in (0, 1)]
    ok = all(abs(x) <= 0.02 for x in v1 + v2) and all(level(sel_m, a, f('pl_prog_hold_us')) > 0 for a in (0, 1))
    res.append(('PLKSTAT_IDENTITIES', ok, 'prog %s cs %s' % (['%.4f' % x for x in v1], ['%.4f' % x for x in v2])))

    def emsum(r):
        return (r['pl_em_vtx_ns'] + r['pl_em_rt_ns'] + r['pl_em_pipe_ns'] + r['pl_em_com_ns'] + r['pl_em_rec_ns']
                + r['pl_em_rest_ns']) / 1000
    v1 = [ratio_check(sel_m, a, f('pl_em_n'), f('mh_draws')) for a in (0, 1)]
    ch = [level(sel_m, a, emsum) / level(sel_m, a, f('mh_emit_us')) for a in (0, 1)]
    pref = [level(sel_m, a, f('pl_pref_n')) for a in (0, 1)]
    ok = all(abs(x) <= 0.02 for x in v1) and all(0.95 <= c <= 1.01 for c in ch) and all(p >= 1 for p in pref)
    res.append(('PATHLAP_ARMED', ok, 'em_n %s chain %s pref_n %s' % (['%.4f' % x for x in v1], ['%.4f' % x for x in ch], pref)))
    res.append(('OTHER_INSTRUMENTS_DARK(mut)', total(sel_m, None, f('sh_jobs')) == 0,
                'sh_jobs %d da_wjobs(info) %d' % (total(sel_m, None, f('sh_jobs')), total(sel_m, None, f('da_wjobs')))))
    # sh
    t0, t1 = total(sel_s, 0, f('sh_jobs')), total(sel_s, 1, f('sh_jobs'))
    res.append(('SH_DARK_ARM0', level(sel_s, 0, f('sh_jobs')) == 0 and t0 <= 0.001 * t1, 'tot0 %d tot1 %d' % (t0, t1)))
    v = level(sel_s, 1, f('sh_jobs')) / level(sel_s, 1, f('draws'))
    res.append(('SH_JOBS_PER_DRAW', 0.90 <= v <= 1.02, '%.4f' % v))
    v = total(sel_s, 1, f('sh_drop')) / t1
    res.append(('SH_NO_DROP', v <= 0.01, '%.5f' % v))
    dark = {k: total(sel_s, None, f(k)) for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n')}
    res.append(('INSTRUMENTS_DARK(sh)', all(x == 0 for x in dark.values()),
                '%s da_wjobs(info) %d' % (dark, total(sel_s, None, f('da_wjobs')))))
    for tag, sel in (('sh', sel_s), ('mut', sel_m)):
        b = []
        for a in (0, 1):
            b.append(28000 <= level(sel, a, f('dt_us')) <= 40000)
            b.append(9000 <= level(sel, a, f('rec_n')) <= 13000)
            b.append(10000 <= level(sel, a, f('gpu_busy_us')) <= 16000)
        res.append(('BANDS(%s)' % tag, all(b), ''))
        res.append(('MARKERS_OFF(%s)' % tag, total(sel, None, f('gm_ops')) == 0, 'gm_ops %d' % total(sel, None, f('gm_ops'))))
    return res


if __name__ == '__main__':
    R = main()
    print()
    for k, v in g_terms(R).items():
        print('%-28s %12.3f' % (k, v))
    print()
    for name, ok, info in arming(R):
        print('%-28s %s  %s' % (name, 'PASS' if ok else 'FAIL', info))
