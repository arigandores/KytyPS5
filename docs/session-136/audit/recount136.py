# recount136.py - Session Auditor, s.136 step 8 (HPP-240): independent recount of kp136 (sealed ABBA bindlean=0|1),
# of the kill row of s1s136, and of the smoke/registered-tag sums s2..s6, s4b, s4c, kk136, kv136, kw136.
# Own code: no import from kp136.py, smk136.py, smk5c*.py, chk_kp136.py, lead/*, step*/*. Logs read in binary.
# Formulas from the TEXT of the seal pred/01_kp136.md s.1, s.5, s.8 and ROADMAP p.176(g), (e)(3)-(5), 181, 187-189 - not from
# the scorer. Blocks by GateArm lines only (never by blk); arm by the TEXT of the GateArm line; block b row at position
# p = n - F_b - 1, F_b = 1800 + 90 b; the row n = F of the next GateArm is position 89 of the OUTGOING block; window p 10..88
# inclusive (ROADMAP p.55(b)). Pairs (2k, 2k+1) of complete blocks of different arms; a pair is in a mode only if both of its
# blocks are of that mode (p.83(g)); block mode by the mean bda_scan of the window: <= 300 NEW, >= 600 OLD (p.40(e)(1)).
import sys, math, json, hashlib, os

W_LO, W_HI = 10, 88
K_RUN = 32
MAIN_F = ('dt_us', 'draws', 'arm', 'blk', 'cpu_gpu_us', 'gpu_busy_us')
DRAW_F = ('bda_scan',)
BLN = ('bln_n', 'bln_hit', 'bln_miss_new', 'bln_miss_gen', 'bln_miss_evict', 'bln_miss_kind', 'bln_chk', 'bln_bad', 'bln_path',
       'bln_nomap', 'bln_pchk', 'bln_pbad', 'bln_skip', 'bln_skip_a', 'bln_skip_b', 'bln_sbad', 'bln_srace', 'bln_sctl',
       'bln_refuse', 'bln_rst_cpu', 'bln_rst_cpuw', 'bln_srace_a')
CLS = ('stream', 'cbank', 'epoch', 'slow')
RB = tuple('rb_%s_%s' % (k, s) for k in CLS for s in ('ns', 'n')) + ('rb_cal_ns', 'rb_cal_n', 'rb_cls_bad', 'rb_refuse')
X_F = BLN + RB + ('mh_bind_us', 'bl_buf_us', 'rt_att', 'rt_kpx', 'gclk_pin', 'ob_stream', 'rts_xthr', 'rts_acqw', 'rts_refuse')
KINDS = {b'FrameTrace:': ('m', MAIN_F), b'FrameTrace-draw:': ('d', DRAW_F), b'FrameTrace-x:': ('x', X_F)}
MARKERS = (b'--- std::terminate ---', b'--- abort() ---', b'--- Fatal Error ---', b'--- Error', b'GpuHangAbort:', b'ErrorDeviceLost',
           b'VK_ERROR_DEVICE_LOST', b'Unhandled exception')
COUNT_TAGS = (b'GpuWaitSlow:', b'BvhLoopCapTrip:', b'AsyncPipelines: skipped draw', b'[Vulkan][E]', b'BindLean: refused',
              b'B2Reuse:', b'RbCen: refused', b'RtSkip: refused')
HEADS = (b'BindLean: mode', b'RbCen: mode', b'RtSkip: mode', b'GpuClockPin: mode')


def parse(path):
    rows = {'m': {}, 'd': {}, 'x': {}}
    xorder, dups = [], {'m': 0, 'd': 0, 'x': 0}
    arms, heads, cnt = [], {}, {t.decode(): 0 for t in COUNT_TAGS}
    markers, quit_line, verify, nexts = [], None, {}, {}
    h = hashlib.sha256()
    lno = 0
    prev_marker = None
    with open(path, 'rb') as f:
        for ln in f:
            lno += 1
            h.update(ln)
            if prev_marker is not None:
                nexts[prev_marker] = ln.strip().decode('utf-8', 'replace')[:160]
                prev_marker = None
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
                    if kind == 'x' and all(k in d for k in BLN):
                        xorder.append((n, d))
                    continue
            if b'GateArm:' in ln:
                a = {}
                for t in ln[ln.find(b'GateArm:') + 8:].split():
                    k, _, v = t.partition(b'=')
                    a[k.decode()] = v.decode()
                # text may itself contain '=' (bindlean=0): rebuild from the raw tail
                tail = ln[ln.find(b'text=') + 5:].strip().decode() if b'text=' in ln else None
                a['text'] = tail
                arms.append(a)
                continue
            s = ln.strip()
            if b'BindLeanVerify:' in ln:
                q = s[s.find(b'BindLeanVerify:') + 15:].split()
                kind = q[0].decode() if q else '?'
                sub = ''
                for t in q[1:]:
                    if t.startswith(b'why=') or t.startswith(b'part=') or t.startswith(b'moved=') or t.startswith(b'path='):
                        sub += ' ' + t.decode()
                verify[kind + sub] = verify.get(kind + sub, 0) + 1
            for hd in HEADS:
                if hd in ln:
                    heads.setdefault(hd.decode(), []).append(s[s.find(hd):].decode('utf-8', 'replace')[:90])
            for t in COUNT_TAGS:
                if t in ln:
                    cnt[t.decode()] += 1
            if quit_line is None and s == b'Event: quit':
                quit_line = lno
            for mk in MARKERS:
                if mk in ln:
                    markers.append((lno, mk.decode(), s.decode('utf-8', 'replace')[:160]))
                    prev_marker = lno
                    break
    return dict(rows=rows, xorder=xorder, dups=dups, arms=arms, heads=heads, cnt=cnt, markers=markers, nexts=nexts,
                quit_line=quit_line, verify=verify, sha=h.hexdigest(), lines=lno)


def running(xs, f, K=K_RUN):
    """Running sum of the per-row residual f over the rows in log order (p.162(a)); returns max |S_n|, S_last, the rows over K."""
    S, mx, over, nz = 0, 0, [], 0
    for n, r in xs:
        d = f(r)
        if d:
            nz += 1
        S += d
        if abs(S) > mx:
            mx = abs(S)
        if abs(S) > K:
            over.append((n, S))
    return dict(max=mx, last=S, over_rows=len(over), first_over=over[0] if over else None, nz=nz, ok=bool(xs) and mx <= K)


def ifchecks(xs):
    return dict(
        IF5a=running(xs, lambda r: r['bln_n'] - r['bln_hit'] - r['bln_miss_new'] - r['bln_miss_gen'] - r['bln_miss_evict'] - r['bln_miss_kind']),
        IF5b=running(xs, lambda r: r['bln_skip'] - r['bln_skip_a'] - r['bln_skip_b']),
        IF5c=running(xs, lambda r: r['bln_chk'] - r['bln_hit']))


def ms(v):
    v = [a for a in v if a is not None]
    n = len(v)
    if n == 0:
        return (None, None, 0)
    mu = sum(v) / n
    if n < 2:
        return (mu, None, n)
    sd = math.sqrt(sum((a - mu) ** 2 for a in v) / (n - 1))
    return (mu, sd / math.sqrt(n), n)


def block_level(rows):
    N = len(rows)
    S = {k: sum(r[k] for r in rows) for k in X_F + MAIN_F + DRAW_F}
    L = dict(rows=N, sums=S)
    for k in ('dt_us', 'draws', 'bda_scan', 'mh_bind_us', 'bl_buf_us', 'cpu_gpu_us', 'gpu_busy_us'):
        L[k] = S[k] / N
    for K in CLS:
        L['raw_' + K] = 8.0 * S['rb_%s_ns' % K] / (1000.0 * N)
        L['pf_rb_%s_n' % K] = S['rb_%s_n' % K] / N
        L['it_' + K] = 8.0 * S['rb_%s_ns' % K] / S['rb_%s_n' % K] if S['rb_%s_n' % K] else None
    L['raw_net'] = sum(L['raw_' + K] for K in CLS)
    if S['rb_cal_n']:
        c = S['rb_cal_ns'] / S['rb_cal_n']
        L['c'] = c
        L['net_c'] = sum(8.0 * S['rb_%s_ns' % K] - S['rb_%s_n' % K] * c for K in CLS) / (1000.0 * N)
    else:
        L['c'] = None
        L['net_c'] = None
    return L


def abba(P, arm_text, hold_blocks=None, ABBA=(0, 1, 1, 0)):
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    blocks, seq_ok = [], True
    for b, a in enumerate(P['arms']):
        arm = arm_text.get(a.get('text'))
        F = int(a.get('frame', -1))
        if not (int(a.get('block', -1)) == b and F == 1800 + 90 * b and a.get('arms') == '2' and a.get('period') == '90'
                and a.get('abba') == '1' and arm == ABBA[b % 4] and int(a.get('arm', -1)) == arm):
            seq_ok = False
        win, complete = [], True
        for p in range(W_LO, W_HI + 1):
            n = F + 1 + p
            if n not in m or n not in d or n not in x:
                complete = False
                break
            mr, dr, xr = m[n], d[n], x[n]
            if any(k not in mr for k in MAIN_F) or any(k not in dr for k in DRAW_F) or any(k not in xr for k in X_F):
                complete = False
                break
            if mr['arm'] != arm or mr['blk'] != b:
                complete = False
                break
            r = dict(mr)
            r.update(dr)
            r.update(xr)
            r['n'] = n
            r['p'] = p
            win.append(r)
        bl = dict(b=b, arm=arm, F=F, complete=complete, rows=win if complete else [])
        if complete:
            bl['lv'] = block_level(win)
            bs = bl['lv']['bda_scan']
            bl['mode'] = 'NEW' if bs <= 300 else ('OLD' if bs >= 600 else 'MID')
        blocks.append(bl)
    comp = [bl for bl in blocks if bl['complete']]
    res = dict(gatearm=len(blocks), complete=len(comp), seq_ok=seq_ok, incomplete=[bl['b'] for bl in blocks if not bl['complete']],
               arm_complete={a: sum(1 for bl in comp if bl['arm'] == a) for a in (0, 1)},
               modes_blocks={a: {mo: sum(1 for bl in comp if bl['arm'] == a and bl['mode'] == mo) for mo in ('NEW', 'OLD', 'MID')}
                             for a in (0, 1)}, modes={})
    # beta (p.77(b)): OLS dt_us on draws over the window rows of all complete arm-0 blocks, centred within each block
    sxy = sxx = 0.0
    for bl in comp:
        if bl['arm'] != 0:
            continue
        xm = sum(r['draws'] for r in bl['rows']) / len(bl['rows'])
        ym = sum(r['dt_us'] for r in bl['rows']) / len(bl['rows'])
        for r in bl['rows']:
            sxy += (r['draws'] - xm) * (r['dt_us'] - ym)
            sxx += (r['draws'] - xm) ** 2
    beta = sxy / sxx if sxx else 0.0
    res['beta'] = beta
    res['sxx'] = sxx
    byb = {bl['b']: bl for bl in comp}
    pairs, outside = [], []
    for k in range(0, len(blocks), 2):
        if k in byb and k + 1 in byb and byb[k]['arm'] != byb[k + 1]['arm']:
            p0, p1 = (byb[k], byb[k + 1]) if byb[k]['arm'] == 0 else (byb[k + 1], byb[k])
            if p0['mode'] == p1['mode'] and p0['mode'] in ('NEW', 'OLD'):
                pairs.append(dict(k=k, mode=p0['mode'], b0=p0, b1=p1))
            else:
                outside.append((k, p0['mode'], p1['mode']))
    res['pairs_outside'] = outside
    res['pairs_all'] = len(pairs)
    for mode in ('NEW', 'OLD'):
        ps = [p for p in pairs if p['mode'] == mode]
        R = dict(pairs=len(ps))
        if len(ps) < 10:
            R['reading'] = 'DEBT'
            res['modes'][mode] = R
            continue
        D = {}
        def row(name, f):
            v = [f(p) for p in ps]
            mu, se, n = ms(v)
            D[name] = (mu, 2 * se if se is not None else None, n)
        row('d_dt', lambda p: p['b1']['lv']['dt_us'] - p['b0']['lv']['dt_us'])
        row('d_draws', lambda p: p['b1']['lv']['draws'] - p['b0']['lv']['draws'])
        row('d_adj', lambda p: (p['b1']['lv']['dt_us'] - p['b0']['lv']['dt_us']) - beta * (p['b1']['lv']['draws'] - p['b0']['lv']['draws']))
        row('red_bl_buf', lambda p: p['b0']['lv']['bl_buf_us'] - p['b1']['lv']['bl_buf_us'])
        for k in ('bl_buf_us', 'mh_bind_us', 'cpu_gpu_us', 'gpu_busy_us', 'raw_net', 'raw_stream', 'raw_cbank', 'raw_epoch', 'raw_slow',
                  'pf_rb_epoch_n', 'pf_rb_slow_n'):
            row('d_' + k, lambda p, k=k: p['b1']['lv'][k] - p['b0']['lv'][k])
        pc = [p for p in ps if p['b0']['lv']['c'] is not None and p['b1']['lv']['c'] is not None]
        for k in ('c', 'net_c'):
            v = [p['b1']['lv'][k] - p['b0']['lv'][k] for p in pc]
            mu, se, n = ms(v)
            D['d_' + k] = (mu, 2 * se if se is not None else None, n)
        for k in ('it_epoch', 'it_slow'):
            v = [p['b1']['lv'][k] - p['b0']['lv'][k] for p in ps if p['b1']['lv'][k] is not None and p['b0']['lv'][k] is not None]
            mu, se, n = ms(v)
            D['d_' + k] = (mu, 2 * se if se is not None else None, n)
        R['rows'] = D
        hi = max(D['d_dt'][0] + D['d_dt'][1], D['d_adj'][0] + D['d_adj'][1])
        lo = min(D['d_dt'][0] - D['d_dt'][1], D['d_adj'][0] - D['d_adj'][1])
        R['max_plus'] = hi
        R['min_minus'] = lo
        R['reading'] = 'GAIN' if hi <= -100 else ('NO_GAIN' if lo > -100 else 'NOT_RESOLVED')
        R['kill'] = 'KILLED' if D['red_bl_buf'][0] < 200 else 'NOT_KILLED'
        a0 = [r for p in ps for r in p['b0']['rows']]
        R['base_arm0_rows_dt'] = sum(r['dt_us'] for r in a0) / len(a0)
        a0b = [bl for bl in comp if bl['arm'] == 0 and bl['mode'] == mode]
        a1b = [bl for bl in comp if bl['arm'] == 1 and bl['mode'] == mode]
        R['blocks'] = (len(a0b), len(a1b))
        R['level_arm0_dt_blocks'] = ms([bl['lv']['dt_us'] for bl in a0b])[0]
        R['level_arm1_dt_blocks'] = ms([bl['lv']['dt_us'] for bl in a1b])[0]
        R['level_arm0_blbuf'] = ms([bl['lv']['bl_buf_us'] for bl in a0b])[0]
        res['modes'][mode] = R
    # base (p.176(e)(6)): mean dt_us of the window rows of all complete arm-0 blocks
    rr = [r for bl in comp if bl['arm'] == 0 for r in bl['rows']]
    res['base_all_arm0_rows'] = sum(r['dt_us'] for r in rr) / len(rr) if rr else None
    res['base_rows'] = len(rr)
    # DRS (p.78(e))
    for a in (0, 1):
        ra = [r for bl in comp if bl['arm'] == a for r in bl['rows'] if r['rt_att'] > 0]
        res['drs_m%d' % a] = sum(r['rt_kpx'] for r in ra) / sum(r['rt_att'] for r in ra) if ra else None
    m0, m1 = res['drs_m0'], res['drs_m1']
    res['drs_mixed'] = (m0 is None or m1 is None) or (100 * abs(m1 - m0) > m0)
    # guards re-derived: IF1 (arm-0 window rows bln_* all 0), IF2 (self-check counters 0 on every row), live arm-1 blocks
    res['if1_nonzero'] = sum(1 for bl in comp if bl['arm'] == 0 for r in bl['rows'] for k in BLN if r[k])
    res['arm1_blocks_hit0'] = sum(1 for bl in comp if bl['arm'] == 1 and sum(r['bln_hit'] for r in bl['rows']) == 0)
    res['arm1_blocks_skip0'] = sum(1 for bl in comp if bl['arm'] == 1 and sum(r['bln_skip'] for r in bl['rows']) == 0)
    res['rts_rows'] = sum(1 for bl in comp for r in bl['rows'] if r['rts_xthr'] or r['rts_acqw'] or r['rts_refuse'])
    res['gclk'] = tuple(sum(r['gclk_pin'] for bl in comp if bl['arm'] == a for r in bl['rows']) for a in (0, 1))
    a1r = [r for bl in comp if bl['arm'] == 1 for r in bl['rows']]
    if a1r:
        sm = lambda k: sum(r[k] for r in a1r)
        it = sum(sm('rb_%s_n' % K) for K in CLS)
        res['pkg_arm1'] = dict(hit=sm('bln_hit'), n=sm('bln_n'), share=sm('bln_hit') / sm('bln_n') if sm('bln_n') else None,
                               skip=sm('bln_skip'), iters=it, skip_per_it=sm('bln_skip') / it if it else None,
                               skip_a=sm('bln_skip_a'), skip_b=sm('bln_skip_b'), miss_gen=sm('bln_miss_gen'))
    return res


def death(P, stdout_path):
    ql = P['quit_line']
    g = []
    for l, mk, s in P['markers']:
        nx = P['nexts'].get(l, '')
        exc = (ql is not None and l > ql and (s == '--- Fatal Error ---' or s.startswith('--- Error'))
               and ('fileSystem.cpp' in s or 'fileSystem.cpp' in nx))
        g.append(dict(line=l, marker=mk, text=s, excluded_132g=exc))
    so = []
    if stdout_path and os.path.exists(stdout_path):
        with open(stdout_path, 'rb') as f:
            for i, ln in enumerate(f, 1):
                for mk in MARKERS:
                    if mk in ln:
                        so.append((i, mk.decode(), ln.strip().decode('utf-8', 'replace')[:160]))
                        break
    return dict(log=g, guard=sum(1 for e in g if not e['excluded_132g']), stdout=so, quit_line=ql)


def sums(P):
    xs = P['xorder']
    S = {k: sum(r[k] for _, r in xs) for k in BLN}
    for k in ('rb_cls_bad', 'rb_refuse', 'rb_stream_n', 'rb_cbank_n', 'rb_slow_n'):
        S[k] = sum(r.get(k, 0) for _, r in xs)
    # bda_scan over all full rows (x row + draw row)
    d = P['rows']['d']
    bs = [d[n]['bda_scan'] for n, _ in xs if n in d and 'bda_scan' in d[n]]
    S['bda_mean'] = sum(bs) / len(bs) if bs else None
    S['bda_rows_new'] = sum(1 for v in bs if v <= 300)
    S['bda_rows'] = len(bs)
    S['rows'] = len(xs)
    # per-row rows of p.178(v) (never conditions)
    S['row_hit_off'] = sum(1 for _, r in xs if r['bln_hit'] > r.get('rb_stream_n', 0) + r.get('rb_cbank_n', 0) + 32)
    return S


def main():
    base = 'C:/kyty/s136/'
    out = {}
    for tag in sys.argv[1:]:
        P = parse(base + 'log_%s.txt' % tag)
        R = dict(log_sha256=P['sha'], lines=P['lines'], dups=P['dups'], heads=P['heads'], cnt=P['cnt'], gatearm=len(P['arms']),
                 verify=P['verify'], death=death(P, base + 'stdout_%s.txt' % tag), sums=sums(P), ifs=ifchecks(P['xorder']))
        if P['arms']:
            R['abba'] = abba(P, {'bindlean=0': 0, 'bindlean=1': 1})
        out[tag] = R
        print('==', tag, 'sha', P['sha'][:16], 'lines', P['lines'], flush=True)
    with open(base + 'audit136/recount136_%s.json' % '_'.join(sys.argv[1:]), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=True, default=str)


if __name__ == '__main__':
    main()
