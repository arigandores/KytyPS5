# recount134.py - Session Auditor, s.134 step 9 (HPP-211): independent recount of kp134 and s1s134 (ABBA),
# and the correctness smokes s2s134..s6s134 (constant value). Own code: no import from kp134.py, smk134.py,
# lead/*, step6/*. Reads logs in binary.
# ABBA: blocks by GateArm: lines only (never by blk); arm by the TEXT of the GateArm line; row n of block b at
# position p = n - F_b - 1; the row n = F of the next GateArm is position 89 of the OUTGOING block;
# window p 10..88 inclusive (ROADMAP p.55(b)). Pairs (2k, 2k+1) of complete blocks with different arms.
# BDA mode of a block: mean bda_scan (FrameTrace-draw) over the window, <= 300 NEW, >= 600 OLD (p.40(e)(1)).
import sys, math, json, hashlib, os

W_LO, W_HI = 10, 88
MAIN_F = ('dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'arm', 'blk')
DRAW_F = ('bda_scan',)
B2R = ('b2r_n', 'b2r_hit', 'b2r_chk', 'b2r_bad', 'b2r_path', 'b2r_hit_draw', 'b2r_hit_x', 'b2r_miss_new', 'b2r_miss_gen',
       'b2r_miss_evict', 'b2r_miss_kind', 'b2r_refuse', 'b2r_rst_cpu', 'b2r_rst_cpuw', 'b2r_wrapcur', 'b2r_nomap')
RB2 = ('rb_b2_n', 'rb_b2_would', 'rb_b2_kb', 'rb_b2_chk', 'rb_b2_diff', 'rb_b2_xchk', 'rb_b2_xdiff', 'rb_b2_evict', 'rb_b2_shovf',
       'rb_b2_rst_sub', 'rb_b2_rst_host', 'rb_b2_rst_wait', 'rb_b2_rst_rel', 'rb_b2_rst_wr', 'rb_b2_rst_cond', 'rb_b2_rst_emu',
       'rb_b2_rst_gpuw', 'rb_b2_rst_imgw', 'rb_b2_rst_ring')
CLS = ('stream', 'cbank', 'epoch', 'slow')
X_F = tuple(['rb_%s_%s' % (k, s) for k in CLS for s in ('ns', 'n')]) + ('rb_cal_ns', 'rb_cal_n', 'mh_bind_us', 'bl_buf_us', 'rt_att',
      'rt_kpx', 'rts_xthr', 'rts_acqw', 'rts_refuse', 'gclk_pin', 'ob_stream', 'rb_cls_bad', 'rb_refuse', 'pb_wait_gpu_us') + B2R + RB2
KINDS = {b'FrameTrace:': ('m', MAIN_F), b'FrameTrace-draw:': ('d', DRAW_F), b'FrameTrace-x:': ('x', X_F)}
MARKERS = (b'--- std::terminate ---', b'--- abort() ---', b'--- Error', b'--- Fatal Error ---', b'GpuHangAbort:', b'ErrorDeviceLost',
           b'VK_ERROR_DEVICE_LOST', b'Unhandled exception')
COUNT_TAGS = (b'GpuWaitSlow:', b'BvhLoopCapTrip:', b'B2ReuseVerify:', b'AsyncPipelines: skipped draw', b'BufferGc:', b'[Vulkan][E]',
              b'[Vulkan][W]', b'RbCen: refused', b'B2Reuse: refused', b'RtSkip: refused')


def parse(path):
    rows = {'m': {}, 'd': {}, 'x': {}}
    dups = {'m': 0, 'd': 0, 'x': 0}
    arms, heads, cnt = [], {}, {t.decode(): 0 for t in COUNT_TAGS}
    markers, quit_line, verify, bufgc, vkw = [], None, [], [], {}
    h = hashlib.sha256()
    lno = 0
    with open(path, 'rb') as f:
        for ln in f:
            lno += 1
            h.update(ln)
            j = ln.find(b'FrameTrace')
            if j >= 0:
                sp = ln.find(b' ', j)
                key = ln[j:sp]
                if key in KINDS:
                    kind, names = KINDS[key]
                    toks = ln[sp + 1:].split()
                    if not toks or not toks[0].startswith(b'n='):
                        continue
                    n = int(toks[0][2:])
                    want = set(names)
                    d = {}
                    for t in toks[1:]:
                        k, _, v = t.partition(b'=')
                        ks = k.decode('ascii', 'replace')
                        if ks in want:
                            try:
                                d[ks] = int(v)
                            except ValueError:
                                pass
                    if n in rows[kind]:
                        dups[kind] += 1
                    rows[kind][n] = d
                    continue
            if b'GateArm:' in ln:
                a = {}
                for t in ln[ln.find(b'GateArm:') + 8:].split():
                    k, _, v = t.partition(b'=')
                    a[k.decode()] = v.decode()
                arms.append(a)
                continue
            s = ln.strip()
            for hd in (b'B2Reuse: mode', b'RbCen: mode', b'RtSkip: mode', b'GpuClockPin: mode'):
                if hd in ln:
                    heads.setdefault(hd.decode(), []).append(s[s.find(hd):].decode('utf-8', 'replace')[:80])
            for t in COUNT_TAGS:
                if t in ln:
                    cnt[t.decode()] += 1
            if b'B2ReuseVerify:' in ln and len(verify) < 60:
                verify.append(s.decode('utf-8', 'replace')[:200])
            if b'BufferGc:' in ln and len(bufgc) < 4:
                bufgc.append(s.decode('utf-8', 'replace')[:240])
            if b'[Vulkan][W]' in ln:
                q = s[s.find(b'[Vulkan][W]'):]
                key = q[:110].decode('utf-8', 'replace')
                vkw[key] = vkw.get(key, 0) + 1
            if quit_line is None and s == b'Event: quit':
                quit_line = lno
            for mk in MARKERS:
                if mk in ln:
                    markers.append((lno, mk.decode(), s.decode('utf-8', 'replace')[:160]))
                    break
    return dict(rows=rows, dups=dups, arms=arms, heads=heads, cnt=cnt, markers=markers, quit_line=quit_line, verify=verify,
                bufgc=bufgc, vkw=vkw, sha=h.hexdigest(), lines=lno)


def full_rows(P):
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    out = []
    for n in sorted(m):
        if n in d and n in x and all(k in m[n] for k in MAIN_F) and all(k in d[n] for k in DRAW_F) and all(k in x[n] for k in X_F):
            r = dict(m[n]); r.update(d[n]); r.update(x[n]); r['n'] = n
            out.append(r)
    return out


def ms(v):
    n = len(v)
    if n == 0:
        return (float('nan'), float('nan'), 0)
    mu = sum(v) / n
    if n < 2:
        return (mu, float('nan'), n)
    sd = math.sqrt(sum((a - mu) ** 2 for a in v) / (n - 1))
    return (mu, sd / math.sqrt(n), n)


def runsum(rows, f):
    s, mx, nz = 0, 0, 0
    for r in rows:
        dv = f(r)
        if dv:
            nz += 1
        s += dv
        mx = max(mx, abs(s))
    return dict(max_abs=mx, last=s, rows_nz=nz)


def level(rows):
    N = len(rows)
    S = lambda k: sum(r[k] for r in rows)
    cn = S('rb_cal_n')
    c = S('rb_cal_ns') / cn if cn else None
    lv = {}
    for K in CLS:
        lv[K] = None if c is None else (8 * S('rb_%s_ns' % K) - S('rb_%s_n' % K) * c) / (1000.0 * N)
    out = {k: S(k) / N for k in ('dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'bda_scan', 'mh_bind_us', 'bl_buf_us', 'ob_stream',
                                 'pb_wait_gpu_us', 'b2r_n', 'b2r_hit', 'rb_stream_n', 'rb_cbank_n')}
    out['c_ns'] = c
    out['L'] = None if c is None else lv['stream'] + lv['cbank']
    out['E'] = None if c is None else lv['epoch'] + lv['slow']
    out['LE'] = None if c is None else out['L'] + out['E']
    return out


def abba(P, arm_text, ABBA=(0, 1, 1, 0)):
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    blocks, seq_ok = [], True
    for b, a in enumerate(P['arms']):
        txt = a.get('text')
        arm = arm_text.get(txt)
        F = int(a.get('frame', -1))
        if not (int(a.get('block', -1)) == b and F == 1800 + 90 * b and a.get('arms') == '2' and a.get('period') == '90'
                and a.get('abba') == '1' and arm == ABBA[b % 4] and int(a.get('arm', -1)) == arm):
            seq_ok = False
        win, complete = [], True
        for p in range(W_LO, W_HI + 1):
            n = F + 1 + p
            if n not in m or n not in d or n not in x:
                complete = False; break
            mr, dr, xr = m[n], d[n], x[n]
            if any(k not in mr for k in MAIN_F) or any(k not in dr for k in DRAW_F) or any(k not in xr for k in X_F):
                complete = False; break
            if mr['arm'] != arm or mr['blk'] != b:
                complete = False; break
            r = dict(mr); r.update(dr); r.update(xr); r['n'] = n; r['p'] = p
            win.append(r)
        blocks.append(dict(b=b, arm=arm, F=F, complete=complete, rows=win if complete else []))
    for bl in blocks:
        if bl['complete']:
            bl['lv'] = level(bl['rows'])
            bs = bl['lv']['bda_scan']
            bl['mode'] = 'NEW' if bs <= 300 else ('OLD' if bs >= 600 else 'MID')
    comp = [bl for bl in blocks if bl['complete']]
    a0 = [bl for bl in comp if bl['arm'] == 0]
    a1 = [bl for bl in comp if bl['arm'] == 1]
    # beta: OLS dt_us on draws over window rows of all complete arm-0 blocks, centred within block
    sxy = sxx = 0.0
    for bl in a0:
        mdt = sum(r['dt_us'] for r in bl['rows']) / len(bl['rows'])
        mdr = sum(r['draws'] for r in bl['rows']) / len(bl['rows'])
        for r in bl['rows']:
            sxy += (r['dt_us'] - mdt) * (r['draws'] - mdr)
            sxx += (r['draws'] - mdr) ** 2
    beta = sxy / sxx if sxx else 0.0
    byb = {bl['b']: bl for bl in comp}
    pairs = []
    for k in range(0, len(blocks), 2):
        if k in byb and k + 1 in byb and byb[k]['arm'] != byb[k + 1]['arm']:
            p0, p1 = (byb[k], byb[k + 1]) if byb[k]['arm'] == 0 else (byb[k + 1], byb[k])
            mode = p0['mode'] if p0['mode'] == p1['mode'] else 'MIXED(%s/%s)' % (p0['mode'], p1['mode'])
            pairs.append(dict(k=k, mode=mode, l0=p0['lv'], l1=p1['lv']))
    res = dict(blocks=len(blocks), complete=len(comp), complete_arm0=len(a0), complete_arm1=len(a1), seq_ok=seq_ok,
               incomplete=[bl['b'] for bl in blocks if not bl['complete']], beta=beta,
               block_modes={'arm0': [bl['mode'] for bl in a0], 'arm1': [bl['mode'] for bl in a1]}, modes={})
    for mode in sorted(set(p['mode'] for p in pairs)):
        ps = [p for p in pairs if p['mode'] == mode]
        dd = [p['l1']['dt_us'] - p['l0']['dt_us'] for p in ps]
        ddr = [p['l1']['draws'] - p['l0']['draws'] for p in ps]
        dadj = [a - beta * b for a, b in zip(dd, ddr)]
        R = dict(pairs=len(ps))
        for nm, v in (('d_dt', dd), ('d_dt_adj', dadj), ('d_draws', ddr)):
            mu, se, n = ms(v)
            R[nm] = (mu, 2 * se)
        for nm, key, sign in (('L_red', 'L', -1), ('d_E', 'E', 1), ('d_LE', 'LE', 1), ('d_cpu_gpu', 'cpu_gpu_us', 1),
                              ('d_gpu_busy', 'gpu_busy_us', 1), ('d_mh_bind', 'mh_bind_us', 1), ('d_bl_buf', 'bl_buf_us', 1)):
            v = [sign * (p['l1'][key] - p['l0'][key]) for p in ps if p['l1'][key] is not None and p['l0'][key] is not None]
            mu, se, n = ms(v)
            R[nm] = (mu, 2 * se, se, n)
        R['L_arm0'] = ms([p['l0']['L'] for p in ps])[0]
        if len(ps) >= 10:
            hi = max(R['d_dt'][0] + R['d_dt'][1], R['d_dt_adj'][0] + R['d_dt_adj'][1])
            lo = min(R['d_dt'][0] - R['d_dt'][1], R['d_dt_adj'][0] - R['d_dt_adj'][1])
            R['max_plus'] = hi; R['min_minus'] = lo
            R['verdict'] = 'GAIN' if hi <= -100 else ('NO_GAIN' if lo > -100 else 'NOT_RESOLVED')
        else:
            R['verdict'] = 'DEBT'
        res['modes'][mode] = R
    # DRS p.78(e)
    drs = {}
    for arm, bls in ((0, a0), (1, a1)):
        rs = [r for bl in bls for r in bl['rows'] if r['rt_att'] > 0]
        drs[arm] = (sum(r['rt_kpx'] for r in rs), sum(r['rt_att'] for r in rs),
                    sum(1 for bl in bls for r in bl['rows'] if r['rt_att'] == 0))
    m0 = drs[0][0] / drs[0][1] if drs[0][1] else None
    m1 = drs[1][0] / drs[1][1] if drs[1][1] else None
    res['drs'] = dict(m0=m0, m1=m1, rows_att0=(drs[0][2], drs[1][2]),
                      mixed=(m0 is None or m1 is None or 100 * abs(m1 - m0) > m0))
    # base p.151(d)(6): mean dt_us of window rows of complete arm-0 blocks
    r0 = [r for bl in a0 for r in bl['rows']]
    res['base_dt_arm0'] = sum(r['dt_us'] for r in r0) / len(r0) if r0 else None
    res['base_speed_pct'] = 100 * 16667 / res['base_dt_arm0'] if r0 else None
    r1 = [r for bl in a1 for r in bl['rows']]
    res['arm1_dt'] = sum(r['dt_us'] for r in r1) / len(r1) if r1 else None
    # guards / rows over windows
    res['arm0_window_rows'] = len(r0)
    res['arm0_b2r_nonzero_fields'] = sum(1 for r in r0 for k in B2R if r[k] != 0)
    res['arm1_blocks_hit0'] = sum(1 for bl in a1 if sum(r['b2r_hit'] for r in bl['rows']) == 0)
    S1 = lambda k: sum(r[k] for r in r1)
    res['arm1_sums'] = {k: S1(k) for k in B2R}
    res['arm1_hit_share'] = S1('b2r_hit') / S1('b2r_n') if S1('b2r_n') else None
    res['arm1_B1'] = S1('b2r_miss_evict') / (S1('b2r_n') - S1('b2r_hit')) if S1('b2r_n') - S1('b2r_hit') else None
    res['arm1_IF5_E1'] = runsum(r1, lambda r: r['b2r_n'] - r['b2r_hit'] - r['b2r_miss_new'] - r['b2r_miss_gen'] - r['b2r_miss_evict'] - r['b2r_miss_kind'])
    res['arm1_IF5_E2'] = runsum(r1, lambda r: r['b2r_hit'] - r['b2r_hit_draw'] - r['b2r_hit_x'])
    res['arm1_IF6_rows'] = sum(1 for r in r1 if r['b2r_hit'] > r['rb_stream_n'] + r['rb_cbank_n'] + 32)
    res['arm1_IF6_rows_noslack'] = sum(1 for r in r1 if r['b2r_hit'] > r['rb_stream_n'] + r['rb_cbank_n'])
    res['rts_guard_rows'] = sum(1 for r in r0 + r1 if r['rts_xthr'] or r['rts_acqw'] or r['rts_refuse'])
    res['gclk_pin_sum'] = (sum(r['gclk_pin'] for r in r0), sum(r['gclk_pin'] for r in r1))
    res['levels_arm'] = {str(a): {k: ms([bl['lv'][k] for bl in bls])[0] for k in ('dt_us', 'draws', 'ob_stream', 'pb_wait_gpu_us', 'bda_scan', 'L', 'E')}
                         for a, bls in ((0, a0), (1, a1))}
    return res


def smoke(P, rows):
    S = lambda k: sum(r[k] for r in rows)
    res = dict(full_rows=len(rows), sums={k: S(k) for k in B2R + RB2 + ('rb_cls_bad', 'rb_refuse')})
    res['rows_bad_nz'] = sum(1 for r in rows if r['b2r_bad'])
    res['rows_path_nz'] = sum(1 for r in rows if r['b2r_path'])
    res['rows_nomap_nz'] = sum(1 for r in rows if r['b2r_nomap'])
    res['IF5_E1'] = runsum(rows, lambda r: r['b2r_n'] - r['b2r_hit'] - r['b2r_miss_new'] - r['b2r_miss_gen'] - r['b2r_miss_evict'] - r['b2r_miss_kind'])
    res['IF5_E2'] = runsum(rows, lambda r: r['b2r_hit'] - r['b2r_hit_draw'] - r['b2r_hit_x'])
    res['A3_chk_hit'] = runsum(rows, lambda r: r['b2r_chk'] - r['b2r_hit'])
    res['IF6_rows_v1'] = sum(1 for r in rows if r['b2r_hit'] > r['rb_stream_n'] + r['rb_cbank_n'] + 32)
    res['IF6_rows_v23'] = sum(1 for r in rows if r['b2r_hit'] - r['b2r_path'] - r['b2r_nomap'] > r['rb_stream_n'] + r['rb_cbank_n'] + 32)
    res['hit_share'] = S('b2r_hit') / S('b2r_n') if S('b2r_n') else None
    bs = [r['bda_scan'] for r in rows]
    res['bda_scan_mean_all'] = sum(bs) / len(bs) if bs else None
    tail = rows[300:]
    res['bda_scan_mean_after300'] = sum(r['bda_scan'] for r in tail) / len(tail) if tail else None
    return res


def death(P, stdout_path):
    ql = P['quit_line']
    guard = []
    for lno, mk, s in P['markers']:
        exit_race = ql is not None and lno > ql and (mk in ('--- Fatal Error ---', '--- Error')) and 'fileSystem.cpp' in s
        guard.append(dict(line=lno, marker=mk, text=s, exit_race_candidate=exit_race))
    so = []
    if stdout_path and os.path.exists(stdout_path):
        with open(stdout_path, 'rb') as f:
            for i, ln in enumerate(f, 1):
                for mk in MARKERS:
                    if mk in ln:
                        so.append((i, mk.decode(), ln.strip().decode('utf-8', 'replace')[:160])); break
    return dict(log_markers=guard, stdout_markers=so, quit_line=ql)


def main():
    out = {}
    base = 'C:/kyty/s134/'
    for tag in sys.argv[1:]:
        P = parse(base + 'log_%s.txt' % tag)
        R = dict(log_sha256=P['sha'], lines=P['lines'], dups=P['dups'], heads=P['heads'], cnt=P['cnt'], verify_sample=P['verify'][:6],
                 bufgc=P['bufgc'], vk_w_classes=len(P['vkw']), death=death(P, base + 'stdout_%s.txt' % tag),
                 gatearm_lines=len(P['arms']))
        rows = full_rows(P)
        R['smoke'] = smoke(P, rows)
        if P['arms']:
            R['abba'] = abba(P, {'b2reuse=0': 0, 'b2reuse=1': 1})
        out[tag] = R
        print('==', tag, 'sha', P['sha'][:16], 'lines', P['lines'], 'GateArm', len(P['arms']), 'full rows', len(rows), flush=True)
    with open(base + 'audit134/recount134.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=str)
    for tag, R in out.items():
        print('\n########', tag, R['log_sha256'])
        print('heads', R['heads']); print('cnt', R['cnt']); print('dups', R['dups'])
        print('death', json.dumps(R['death'], ensure_ascii=False)[:600])
        sm = R['smoke']
        print('smoke rows', sm['full_rows'], 'bad rows', sm['rows_bad_nz'], 'path rows', sm['rows_path_nz'], 'nomap rows', sm['rows_nomap_nz'])
        print('sums', {k: v for k, v in sm['sums'].items()})
        print('IF5 E1', sm['IF5_E1'], 'E2', sm['IF5_E2'], 'A3', sm['A3_chk_hit'], 'IF6 v1', sm['IF6_rows_v1'], 'IF6 v23', sm['IF6_rows_v23'])
        print('hit share %.4f' % sm['hit_share'] if sm['hit_share'] is not None else 'hit share -', 'bda all %.1f after300 %.1f' % (sm['bda_scan_mean_all'], sm['bda_scan_mean_after300']))
        if R['bufgc']:
            print('bufgc', R['bufgc'])
        print('vk W classes', R['vk_w_classes'], 'verify sample', R['verify_sample'][:3])
        if 'abba' in R:
            A = R['abba']
            print('ABBA blocks', A['blocks'], 'complete', A['complete'], A['complete_arm0'], A['complete_arm1'], 'seq_ok', A['seq_ok'],
                  'incomplete', A['incomplete'], 'beta %.4f' % A['beta'])
            for mode, M in A['modes'].items():
                print(' mode', mode, 'pairs', M['pairs'], 'verdict', M['verdict'])
                for k in ('d_dt', 'd_dt_adj', 'd_draws'):
                    print('   %-10s %+10.2f +- %8.2f' % (k, M[k][0], M[k][1]))
                for k in ('L_red', 'd_E', 'd_LE', 'd_cpu_gpu', 'd_gpu_busy', 'd_mh_bind', 'd_bl_buf'):
                    print('   %-10s %+10.2f +- %8.2f (SE %.2f, n %d)' % (k, M[k][0], M[k][1], M[k][2], M[k][3]))
                print('   L_arm0 %.2f' % M['L_arm0'], 'max(D+2SE) %s min(D-2SE) %s' % (M.get('max_plus'), M.get('min_minus')))
                if M['L_red'][0]:
                    print('   D/Lred %.3f' % (M['d_dt'][0] / M['L_red'][0]))
            print(' DRS', A['drs']); print(' base arm0 dt %.2f speed %.2f %%, arm1 dt %.2f' % (A['base_dt_arm0'], A['base_speed_pct'], A['arm1_dt']))
            print(' arm0 window rows', A['arm0_window_rows'], 'arm0 b2r nonzero fields', A['arm0_b2r_nonzero_fields'], 'arm1 blocks hit0', A['arm1_blocks_hit0'])
            print(' arm1 sums', A['arm1_sums']); print(' arm1 hit share', A['arm1_hit_share'], 'B1', A['arm1_B1'])
            print(' arm1 IF5', A['arm1_IF5_E1'], A['arm1_IF5_E2'], 'IF6', A['arm1_IF6_rows'], 'IF6 noslack', A['arm1_IF6_rows_noslack'])
            print(' rts guard rows', A['rts_guard_rows'], 'gclk', A['gclk_pin_sum'], 'levels', A['levels_arm'])
            print(' block modes', {k: {m: v.count(m) for m in set(v)} for k, v in A['block_modes'].items()})


if __name__ == '__main__':
    main()
