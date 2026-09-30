# recount137.py - Session Auditor, s.137 step 5 (HPP-255): independent recount of the pooled sealed kp137 (8 calls x 300 s,
# ABBA bindlean=0|1), of the correctness tags s4cs137 / kk137 / s6s137 in the IF5 "snapshot tear" form of ROADMAP p.190(e)(2),
# of the calibration print on the 12 logs of s.136 and of the positive control rt1_probe (p.194(e)).
# Own code: no import from kp137.py, smk137.py, chk_kp137.py, rt1_*.py, lead/*, step*/*. Ported from the auditor's own
# recount136.py (s.136 audit). Logs read in binary. Formulas from the TEXT of ROADMAP p.176(e)(5), 190(e)(2)-(7), 194(d)(1)-(5)
# and the seal pred/01_kp137.md - not from the scorer.
# Blocks by GateArm lines only (never by blk); arm by the TEXT of the GateArm line; block b row at position p = n - F_b - 1,
# F_b = 1800 + 90 b; the row n = F of the next GateArm is position 89 of the OUTGOING block; window p 10..88 inclusive
# (ROADMAP p.55(b)). Pairs (2k, 2k+1) of complete blocks of different arms; pair 0 of every call is not read (p.194(d)(1));
# a pair is in a mode only if both blocks are of that mode (p.83(g)); block mode by the mean bda_scan of the window:
# <= 300 NEW, >= 600 OLD (p.40(e)(1)).
# Usage: python recount137.py parse <tag>...   (writes json/<tag>.json)
#        python recount137.py report          (reads json/*.json, prints the recount)
import sys, math, json, hashlib, os

W_LO, W_HI = 10, 88
K_RUN = 32
ROOT137 = 'C:/kyty/s137/'
ROOT136 = 'C:/kyty/s136/'
OUT = 'C:/kyty/s137/audit137/json/'
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
COUNT_TAGS = (b'GpuWaitSlow:', b'BvhLoopCapTrip:', b'AsyncPipelines: skipped draw', b'[Vulkan][E]', b'[Vulkan][W]',
              b'BindLean: refused', b'B2Reuse:', b'RbCen: refused', b'RtSkip: refused', b'duplicate_message_limit')
HEADS = (b'BindLean: mode', b'RbCen: mode', b'RtSkip: mode', b'GpuClockPin: mode')
ABBA_PAT = (0, 1, 1, 0)
TAGS137 = {'s4cs137': 3, 'kk137': 2, 's6s137': 1}
CALLS = ['kp137' + c for c in 'abcdefgh']
CAL136 = [('s1s136', None), ('s2s136', 2), ('s3s136', 2), ('s4s136', 3), ('s4bs136', 3), ('s4cs136', 3), ('s5s136', 2),
          ('s6s136', 1), ('kp136', None), ('kk136', 2), ('kv136', 1), ('kw136', 0)]


def parse(path):
    rows = {'m': {}, 'd': {}, 'x': {}}
    dups = {'m': 0, 'd': 0, 'x': 0}
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
                    continue
            if b'GateArm:' in ln:
                a = {}
                for t in ln[ln.find(b'GateArm:') + 8:].split():
                    k, _, v = t.partition(b'=')
                    a[k.decode()] = v.decode()
                a['text'] = ln[ln.find(b'text=') + 5:].strip().decode() if b'text=' in ln else None
                arms.append(a)
                continue
            s = ln.strip()
            if b'BindLeanVerify:' in ln:
                q = s[s.find(b'BindLeanVerify:') + 15:].split()
                kind = q[0].decode() if q else '?'
                sub = ''
                for t in q[1:]:
                    if t.startswith(b'why=') or t.startswith(b'moved='):
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
    return dict(rows=rows, dups=dups, arms=arms, heads=heads, cnt=cnt, markers=markers, nexts=nexts,
                quit_line=quit_line, verify=verify, sha=h.hexdigest(), lines=lno)


def full_rows(P):
    """Rows carrying all three streams with every bln_* field (the rows of the running sum, p.162(a)), in n order."""
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    out = []
    for n in sorted(x):
        r = x[n]
        if n in m and n in d and all(k in r for k in BLN):
            out.append((n, r))
    partial = sum(1 for n in x if any(k in x[n] for k in BLN) and not (n in m and n in d and all(k in x[n] for k in BLN)))
    return out, partial


def ident(value, abba):
    ids = [('IF5a', lambda r: r['bln_n'] - r['bln_hit'] - r['bln_miss_new'] - r['bln_miss_gen'] - r['bln_miss_evict'] - r['bln_miss_kind']),
           ('IF5b', lambda r: r['bln_skip'] - r['bln_skip_a'] - r['bln_skip_b'])]
    if not abba and value in (2, 3):
        ids.append(('IF5c', lambda r: r['bln_chk'] - r['bln_hit']))
    return ids


def tear(seq, f):
    """Own implementation of the form of p.190(e)(2): running sum S over the full rows in n order; (i) |S| > K on two
    adjacent rows; (ii) |S_last| > K; single rows (over K with both neighbours <= K) returned for (iii)."""
    S, ns, ds, ss = 0, [], [], []
    for n, r in seq:
        v = f(r)
        S += v
        ns.append(n)
        ds.append(v)
        ss.append(S)
    L = len(ss)
    ov = [abs(v) > K_RUN for v in ss]
    two = sum(1 for i in range(L - 1) if ov[i] and ov[i + 1])
    singles = [(ns[i], ds[i], ss[i], ss[i + 1] if i + 1 < L else None) for i in range(L)
               if ov[i] and (i == 0 or not ov[i - 1]) and (i == L - 1 or not ov[i + 1])]
    imax = max(range(L), key=lambda i: abs(ds[i])) if L else None
    return dict(rows=L, two=two, last=ss[-1] if L else 0, singles=singles,
                maxd=abs(ds[imax]) if L else 0, maxd_n=ns[imax] if L else None,
                minpair=max((min(abs(ss[i]), abs(ss[i + 1])) for i in range(L - 1)), default=0),
                maxs=max((abs(v) for v in ss), default=0), fail=bool(L == 0 or two or abs(ss[-1]) > K_RUN))


def tag_if5(seq, value, abba):
    res = {}
    tn = set()
    for key, f in ident(value, abba):
        e = tear(seq, f)
        res[key] = e
        tn |= set(s[0] for s in e['singles'])
    res['iii_distinct_n'] = len(tn)
    res['FAIL'] = any(res[k]['fail'] for k, _ in ident(value, abba)) or len(tn) > 3
    return res


def probe(seq, value, abba):
    """Positive control of p.194(e) re-derived: a persistent defect E at the middle full row (step) or +1 on E rows from the
    middle (spread); the smallest E in 1..80 at which the tag form fails by (i)/(ii) of that identity."""
    out = {}
    mid = len(seq) // 2
    for key, f in ident(value, abba):
        es = esp = None
        n0 = seq[mid][0]
        for E in range(1, 81):
            if es is None:
                if tear(seq, lambda r, E=E, f=f: f(r) + (E if r['_n'] == n0 else 0))['fail']:
                    es = E
            if esp is None:
                nsx = set(n for n, _ in seq[mid:mid + E])
                if tear(seq, lambda r, nsx=nsx, f=f: f(r) + (1 if r['_n'] in nsx else 0))['fail']:
                    esp = E
            if es is not None and esp is not None:
                break
        out[key] = (es, esp)
    return out


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
    L = dict(rows=N)
    for k in ('dt_us', 'draws', 'bda_scan', 'mh_bind_us', 'bl_buf_us', 'cpu_gpu_us', 'gpu_busy_us'):
        L[k] = S[k] / N
    for K in CLS:
        L['raw_' + K] = 8.0 * S['rb_%s_ns' % K] / (1000.0 * N)
        L['pf_rb_%s_n' % K] = S['rb_%s_n' % K] / N
    L['raw_net'] = sum(L['raw_' + K] for K in CLS)
    if S['rb_cal_n']:
        c = S['rb_cal_ns'] / S['rb_cal_n']
        L['c'] = c
        L['net_c'] = sum(8.0 * S['rb_%s_ns' % K] - S['rb_%s_n' % K] * c for K in CLS) / (1000.0 * N)
    else:
        L['c'] = L['net_c'] = None
    L['rt_kpx'] = S['rt_kpx']
    L['rt_att'] = S['rt_att']
    L['rt_att0'] = sum(1 for r in rows if r['rt_att'] <= 0)
    L['bln_sum'] = sum(r[k] for r in rows for k in BLN)
    L['bln_hit'] = S['bln_hit']
    L['bln_skip'] = S['bln_skip']
    L['gclk'] = S['gclk_pin']
    L['rts'] = sum(1 for r in rows if r['rts_xthr'] or r['rts_acqw'] or r['rts_refuse'])
    xm = S['draws'] / N
    ym = S['dt_us'] / N
    L['sxy'] = sum((r['draws'] - xm) * (r['dt_us'] - ym) for r in rows)
    L['sxx'] = sum((r['draws'] - xm) ** 2 for r in rows)
    return L


def call_blocks(P, arm_text):
    m, d, x = P['rows']['m'], P['rows']['d'], P['rows']['x']
    blocks, seq_ok = [], True
    for b, a in enumerate(P['arms']):
        arm = arm_text.get(a.get('text'))
        F = int(a.get('frame', -1))
        if not (int(a.get('block', -1)) == b and F == 1800 + 90 * b and a.get('arms') == '2' and a.get('period') == '90'
                and a.get('abba') == '1' and arm == ABBA_PAT[b % 4] and int(a.get('arm', -1)) == arm):
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
            win.append(r)
        bl = dict(b=b, arm=arm, F=F, complete=complete)
        if complete:
            bl['lv'] = block_level(win)
            bs = bl['lv']['bda_scan']
            bl['mode'] = 'NEW' if bs <= 300 else ('OLD' if bs >= 600 else 'MID')
        blocks.append(bl)
    return dict(blocks=blocks, seq_ok=seq_ok)


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
    return dict(guard=sum(1 for e in g if not e['excluded_132g']), log=g, stdout=so, quit_line=ql)


def tag_sums(P, seq):
    x, d = P['rows']['x'], P['rows']['d']
    S = {k: sum(r.get(k, 0) for r in x.values()) for k in BLN}
    S['rows_x_bln'] = sum(1 for r in x.values() if 'bln_n' in r)
    S['full_rows'] = len(seq)
    bs = [d[n]['bda_scan'] for n, _ in seq if 'bda_scan' in d[n]]
    S['bda_mean'] = sum(bs) / len(bs) if bs else None
    S['full_rows_new'] = sum(1 for v in bs if v <= 300)
    # Debt D11' (p.196(v)): sum bln_chk on the NEW full rows (bda_scan <= 300) of the tag
    S['chk_new'] = sum(r['bln_chk'] for n, r in seq if d[n].get('bda_scan', 10 ** 9) <= 300)
    S['chk_full'] = sum(r['bln_chk'] for n, r in seq)
    S['bad_new'] = sum(r['bln_bad'] + r['bln_path'] + r['bln_pbad'] + r['bln_sbad'] for n, r in seq
                       if d[n].get('bda_scan', 10 ** 9) <= 300)
    # tenths of the log: mean bda_scan
    t = []
    if bs:
        k = len(bs)
        for i in range(10):
            part = bs[i * k // 10:(i + 1) * k // 10]
            t.append(round(sum(part) / len(part), 1) if part else None)
    S['bda_tenths'] = t
    return S


def do_parse(tag):
    if tag in CALLS or tag in TAGS137:
        root = ROOT137
    else:
        root = ROOT136
    P = parse(root + 'log_%s.txt' % tag)
    seq, partial = full_rows(P)
    for n, r in seq:
        r['_n'] = n
    value = TAGS137.get(tag, dict(CAL136).get(tag))
    abba = tag in CALLS or tag in ('s1s136', 'kp136')
    R = dict(tag=tag, log_sha256=P['sha'], lines=P['lines'], dups=P['dups'], heads=P['heads'], cnt=P['cnt'],
             gatearm=len(P['arms']), verify=P['verify'], death=death(P, root + 'stdout_%s.txt' % tag),
             partial_rows=partial, if5=tag_if5(seq, value, abba), sums=tag_sums(P, seq))
    if tag not in CALLS:
        R['probe'] = probe(seq, value, abba)
    if tag in CALLS:
        R['abba'] = call_blocks(P, {'bindlean=0': 0, 'bindlean=1': 1})
    os.makedirs(OUT, exist_ok=True)
    with open(OUT + tag + '.json', 'w', encoding='utf-8') as f:
        json.dump(R, f, ensure_ascii=True, default=str)
    print('parsed', tag, P['sha'][:16], P['lines'], flush=True)


# ---------------------------------------------------------------- pooled reading of kp137 -------------------------------
def gammq(a, x):
    """Upper regularized incomplete gamma Q(a, x) (series / continued fraction, own)."""
    if x <= 0:
        return 1.0
    gl = math.lgamma(a)
    if x < a + 1:
        ap, s, de = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1
            de *= x / ap
            s += de
            if abs(de) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gl)
    b = x + 1 - a
    c = 1e300
    dd = 1.0 / b
    hh = dd
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        dd = an * dd + b
        dd = 1e-300 if abs(dd) < 1e-300 else dd
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        dd = 1.0 / dd
        de = dd * c
        hh *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gl) * hh


def pairs_of(C):
    blocks = C['abba']['blocks']
    byb = {bl['b']: bl for bl in blocks if bl['complete']}
    out = []
    for k in range(0, len(blocks), 2):
        if k in byb and k + 1 in byb and byb[k]['arm'] != byb[k + 1]['arm']:
            p0, p1 = (byb[k], byb[k + 1]) if byb[k]['arm'] == 0 else (byb[k + 1], byb[k])
            mode = p0['mode'] if p0['mode'] == p1['mode'] else 'MIXED'
            out.append(dict(call=C['tag'], k=k, order='(0,1)' if byb[k]['arm'] == 0 else '(1,0)', mode=mode, b0=p0['lv'], b1=p1['lv'],
                            ib0=p0['b'], ib1=p1['b']))
    return out


def fmt(t, nd=1):
    mu, se, n = t
    if mu is None:
        return '- (0)'
    if se is None:
        return ('%.' + str(nd) + 'f (n %d)') % (mu, n)
    return ('%.' + str(nd) + 'f +- %.' + str(nd) + 'f (%d)') % (mu, 2 * se, n)


def report():
    P = print
    J = {}
    for fn in sorted(os.listdir(OUT)):
        if fn.endswith('.json'):
            with open(OUT + fn, encoding='utf-8') as f:
                J[fn[:-5]] = json.load(f)
    me = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
    P('recount137 sha256 %s (own parser; no import of kp137.py / smk137.py / chk_kp137.py / rt1_*.py)' % me)
    # ---- kp137 pooled
    calls = [J[c] for c in CALLS if c in J]
    P('== kp137 POOLED (p.190(e)(4)-(5), 194(d)); calls parsed %d of 8' % len(calls))
    allp, beta_blocks = [], []
    for C in calls:
        bl = C['abba']['blocks']
        comp = [b for b in bl if b['complete']]
        ps = pairs_of(C)
        dd = C['death']
        P('call %s log %s lines %d GateArm %d seq_ok %s complete %d/%d arm0/1 complete %d/%d pairs %d (NEW %d) death guard %d '
          'stdout %d dups %s IF5a %s IF5b %s partial %d heads %s' % (
              C['tag'], C['log_sha256'][:16], C['lines'], C['gatearm'], C['abba']['seq_ok'], len(comp), len(bl),
              sum(1 for b in comp if b['arm'] == 0), sum(1 for b in comp if b['arm'] == 1), len(ps),
              sum(1 for p in ps if p['mode'] == 'NEW'), dd['guard'], len(dd['stdout']), C['dups'],
              'FAIL' if C['if5']['IF5a']['fail'] else 'PASS', 'FAIL' if C['if5']['IF5b']['fail'] else 'PASS',
              C['partial_rows'], {k: sorted(set(v))[:2] for k, v in C['heads'].items()}))
        P('   IF1 arm-0 window bln_* nonzero blocks %d; arm-1 blocks with hit 0: %d, skip 0: %d; rts rows %d; gclk arm0/1 %d/%d; '
          'IF5 singles a/b %d/%d distinct %d; maxS a/b %d/%d; S_last a/b %d/%d' % (
              sum(1 for b in comp if b['arm'] == 0 and b['lv']['bln_sum']),
              sum(1 for b in comp if b['arm'] == 1 and b['lv']['bln_hit'] == 0),
              sum(1 for b in comp if b['arm'] == 1 and b['lv']['bln_skip'] == 0),
              sum(b['lv']['rts'] for b in comp), sum(b['lv']['gclk'] for b in comp if b['arm'] == 0),
              sum(b['lv']['gclk'] for b in comp if b['arm'] == 1),
              len(C['if5']['IF5a']['singles']), len(C['if5']['IF5b']['singles']), C['if5']['iii_distinct_n'],
              C['if5']['IF5a']['maxs'], C['if5']['IF5b']['maxs'], C['if5']['IF5a']['last'], C['if5']['IF5b']['last']))
        for p in ps:
            p['pair0'] = (p['k'] == 0)
        allp += ps
        for b in comp:
            if b['arm'] == 0:
                beta_blocks.append((C['tag'], b['b'], b['lv']['sxy'], b['lv']['sxx']))
    readp = [p for p in allp if not p['pair0']]
    modes = {mo: [p for p in readp if p['mode'] == mo] for mo in ('NEW', 'OLD', 'MID', 'MIXED')}
    P('pooled pairs (pair 0 of every call not read): ' + ', '.join('%s %d' % (k, len(v)) for k, v in modes.items()))

    def beta_from(sel):
        sxy = sum(t[2] for t in sel)
        sxx = sum(t[3] for t in sel)
        return (sxy / sxx if sxx else 0.0), sxx
    beta, sxx = beta_from(beta_blocks)
    beta_no0, sxx0 = beta_from([t for t in beta_blocks if t[1] not in (0, 1)])
    readb = set((p['call'], p['ib0']) for p in readp)
    beta_read, sxxr = beta_from([t for t in beta_blocks if (t[0], t[1]) in readb])
    P('beta p.77(b) (all complete arm-0 blocks of the calls, centred per block, with block 0 - by the letter of p.194(d)(5)): '
      '%.4f us/draw (sxx %.0f, blocks %d)' % (beta, sxx, len(beta_blocks)))
    P('beta by call: ' + ', '.join('%s %.4f' % (c, beta_from([t for t in beta_blocks if t[0] == c])[0]) for c in CALLS))
    P('DEBT D12 (p.197(b)(2); a row, not a condition): beta WITHOUT the blocks of pair 0 %.4f (sxx %.0f); beta over the arm-0 '
      'blocks of the read pairs only %.4f (sxx %.0f)' % (beta_no0, sxx0, beta_read, sxxr))
    ps = modes['NEW']

    def est(ps, b):
        return dict(simple=ms([p['b1']['dt_us'] - p['b0']['dt_us'] for p in ps]),
                    adj=ms([(p['b1']['dt_us'] - p['b0']['dt_us']) - b * (p['b1']['draws'] - p['b0']['draws']) for p in ps]),
                    ddraw=ms([p['b1']['draws'] - p['b0']['draws'] for p in ps]))
    E = est(ps, beta)
    hi = max(E['simple'][0] + 2 * E['simple'][1], E['adj'][0] + 2 * E['adj'][1])
    lo = min(E['simple'][0] - 2 * E['simple'][1], E['adj'][0] - 2 * E['adj'][1])
    rd = 'GAIN' if hi <= -100 else ('NO_GAIN' if lo > -100 else 'NOT_RESOLVED')
    if len(ps) < 10:
        rd = 'DEBT'
    P('NEW: d dt_us simple %s; adjusted (beta %.4f) %s; d draws %s' % (fmt(E['simple']), beta, fmt(E['adj']), fmt(E['ddraw'])))
    P('NEW: max(d + 2SE) %.1f; min(d - 2SE) %.1f => %s' % (hi, lo, rd))
    E2 = est(ps, beta_no0)
    hi2 = max(E2['simple'][0] + 2 * E2['simple'][1], E2['adj'][0] + 2 * E2['adj'][1])
    lo2 = min(E2['simple'][0] - 2 * E2['simple'][1], E2['adj'][0] - 2 * E2['adj'][1])
    P('DEBT D12 row: adjusted with beta without pair-0 blocks (%.4f) %s; max(d+2SE) %.1f, min(d-2SE) %.1f => by the same rule %s '
      '(a row, never a reading)' % (beta_no0, fmt(E2['adj']), hi2, lo2,
                                     'GAIN' if hi2 <= -100 else ('NO_GAIN' if lo2 > -100 else 'NOT_RESOLVED')))
    for o in ('(0,1)', '(1,0)'):
        q = [p for p in ps if p['order'] == o]
        P('NEW order %s: simple %s adjusted %s' % (o, fmt(est(q, beta)['simple']), fmt(est(q, beta)['adj'])))
    # per call and Cochran
    for name in ('simple', 'adj'):
        cm = []
        for c in CALLS:
            q = [p for p in ps if p['call'] == c]
            if q:
                cm.append((c, est(q, beta)[name]))
        mus = [t[1][0] for t in cm]
        sec = ms(mus)
        w = [1.0 / t[1][1] ** 2 for t in cm]
        xw = sum(wi * t[1][0] for wi, t in zip(w, cm)) / sum(w)
        Q = sum(wi * (t[1][0] - xw) ** 2 for wi, t in zip(w, cm))
        df = len(cm) - 1
        p = gammq(df / 2.0, Q / 2.0) if df > 0 else None
        P('between calls %s: mean of calls %s; Cochran Q %.3f df %d p %.4f; calls: %s' % (
            name, fmt(sec), Q, df, p, ', '.join('%s %s' % (c, fmt(t)) for c, t in cm)))
    # DRS pooled and per call
    def drs(q, a):
        k = sum(p['b%d' % a]['rt_kpx'] for p in q)
        t = sum(p['b%d' % a]['rt_att'] for p in q)
        return k / t if t else None
    d0, d1 = drs(ps, 0), drs(ps, 1)
    P('DRS pooled arm0 %.2f arm1 %.2f -> %s; rt_att<=0 rows %d' % (d0, d1, 'MIXED' if abs(d1 - d0) * 100 > d0 else 'no',
                                                                   sum(p['b0']['rt_att0'] + p['b1']['rt_att0'] for p in ps)))
    P('DRS by call: ' + ', '.join('%s %.2f/%.2f%s' % (c, drs([p for p in ps if p['call'] == c], 0), drs([p for p in ps if p['call'] == c], 1),
                                                     '' if abs(drs([p for p in ps if p['call'] == c], 1) - drs([p for p in ps if p['call'] == c], 0)) * 100
                                                     <= drs([p for p in ps if p['call'] == c], 0) else ' MIXED') for c in CALLS))
    # rows
    R = {}
    for k in ('bl_buf_us', 'mh_bind_us', 'cpu_gpu_us', 'gpu_busy_us', 'bda_scan', 'raw_stream', 'raw_cbank', 'raw_epoch', 'raw_slow',
              'raw_net', 'c', 'net_c', 'pf_rb_epoch_n', 'pf_rb_slow_n'):
        R[k] = ms([p['b1'][k] - p['b0'][k] for p in ps if p['b1'][k] is not None and p['b0'][k] is not None])
    P('NEW rows (arm1 - arm0; never conditions): ' + '; '.join('%s %s' % (k, fmt(v, 3 if k == 'c' else (2 if k.startswith('pf') else 1)))
                                                              for k, v in R.items()))
    P('pair 0 by call (not read): ' + ', '.join('%s %.1f %s' % (p['call'], p['b1']['dt_us'] - p['b0']['dt_us'], p['mode'])
                                                for p in allp if p['pair0']) +
      '; mean %s' % fmt(ms([p['b1']['dt_us'] - p['b0']['dt_us'] for p in allp if p['pair0']])))
    base = ms([p['b0']['dt_us'] for p in ps])
    P('BASE p.190(e)(7): mean dt_us of the arm-0 blocks of the read NEW pairs %.1f (%d blocks); speed 16667 / base = %.2f %%; '
      'arm-0 bl_buf level %.1f, bda_scan %.1f' % (base[0], base[2], 100 * 16667 / base[0], ms([p['b0']['bl_buf_us'] for p in ps])[0],
                                                   ms([p['b0']['bda_scan'] for p in ps])[0]))
    # ---- correctness tags
    P('== correctness tags s.137 (p.190(e)(3), 186(d), 188(v), 194(b), 184(b))')
    for tag in ('s4cs137', 'kk137', 's6s137'):
        if tag not in J:
            continue
        T = J[tag]
        S = T['sums']
        f5 = T['if5']
        P('%s log %s lines %d full rows %d (NEW %d, bda mean %.1f, tenths %s) partial %d death guard %d stdout %d dups %s' % (
            tag, T['log_sha256'][:16], T['lines'], S['full_rows'], S['full_rows_new'], S['bda_mean'], S['bda_tenths'],
            T['partial_rows'], T['death']['guard'], len(T['death']['stdout']), T['dups']))
        for key in ('IF5a', 'IF5b', 'IF5c'):
            if key in f5:
                e = f5[key]
                P('   %s: rows %d two %d |S_last| %d singles %s maxd %d (n %s) minpair %d maxS %d -> %s' % (
                    key, e['rows'], e['two'], abs(e['last']), e['singles'], e['maxd'], e['maxd_n'], e['minpair'], e['maxs'],
                    'FAIL' if e['fail'] else 'PASS'))
        P('   (iii) distinct n %d -> IF5 %s' % (f5['iii_distinct_n'], 'FAIL' if f5['FAIL'] else 'PASS'))
        P('   sums: ' + ', '.join('%s %d' % (k, S[k]) for k in BLN) + '; verify lines %s; cnt %s' % (
            T['verify'], {k: v for k, v in T['cnt'].items() if v}))
        P('   probe (positive control p.194(e); smallest failing E step/spread): %s' % T['probe'])
        if tag == 's4cs137':
            W = S['bln_miss_gen'] == 0 and S['bln_miss_new'] <= 4096 and S['bln_refuse'] == 0
            P('   (b): sum bln_bad %d > 0 and sum bln_sbad %d > 0 -> %s; witness W %s' % (
                S['bln_bad'], S['bln_sbad'], 'MET' if S['bln_bad'] > 0 and S['bln_sbad'] > 0 and not f5['FAIL'] else 'NOT MET/NOT READ',
                'ALIVE' if W else 'DEAD'))
        if tag == 'kk137':
            a4 = sum(v for k, v in T['verify'].items() if k.startswith('SYNC') and 'moved=0' in k)
            A = [S['bln_bad'] == 0, S['bln_path'] == 0, S['bln_pbad'] == 0, S['bln_sbad'] == 0 and a4 == 0, S['bln_chk'] > 0,
                 S['bln_skip'] > 0 and S['bln_srace'] / S['bln_skip'] <= 0.0002]
            P('   (v): A1 %s A2 %s A3 %s A4 %s A5 %s A7 %s (srace/skip %d/%d = %.3g) -> %s' % (
                tuple(A) + (S['bln_srace'], S['bln_skip'], S['bln_srace'] / S['bln_skip'] if S['bln_skip'] else float('nan'),
                            'MET' if all(A) and not f5['FAIL'] else 'NOT MET/NOT READ')))
            P('   DEBT D11\' (p.196(v); a row): sum bln_chk on NEW full rows (bda_scan <= 300) %d of %d on all full rows (%.4f); '
              'NEW full rows %d of %d; sum bad+path+pbad+sbad on NEW rows %d' % (
                  S['chk_new'], S['chk_full'], S['chk_new'] / S['chk_full'] if S['chk_full'] else 0, S['full_rows_new'],
                  S['full_rows'], S['bad_new']))
        if tag in ('kk137', 's6s137'):
            P('   hit share bln_hit/bln_n %d/%d = %.4f' % (S['bln_hit'], S['bln_n'], S['bln_hit'] / S['bln_n'] if S['bln_n'] else 0))
        if tag == 's6s137':
            P('   (d) row rule p.184(b): [Vulkan][E] %d, [Vulkan][W] %d, duplicate_message_limit lines %d; D1 full rows bda_scan <= 300: '
              '%d of %d -> %s' % (T['cnt']['[Vulkan][E]'], T['cnt']['[Vulkan][W]'], T['cnt']['duplicate_message_limit'],
                                   S['full_rows_new'], S['full_rows'], 'D1 met' if S['full_rows_new'] >= 500 else 'D1 < 500 - QUESTION (not read)'))
    # ---- calibration print on the 12 logs of s.136
    P('== calibration p.190(e)(2) on the 12 logs of s.136 (own tear form) + the positive control rt1_probe (p.194(e))')
    stop = 0
    for tag, value in CAL136:
        if tag not in J:
            P('%s: not parsed' % tag)
            continue
        T = J[tag]
        f5 = T['if5']
        keys = [k for k in ('IF5a', 'IF5b', 'IF5c') if k in f5]
        stop += 1 if f5['FAIL'] else 0
        P('%s (%s): ' % (tag, 'ABBA' if value is None and tag != 'kw136' else value) + '; '.join(
            '%s maxd %d (n %s) singles %d minpair %d maxS %d S_last %d two %d' % (
                k, f5[k]['maxd'], f5[k]['maxd_n'], len(f5[k]['singles']), f5[k]['minpair'], f5[k]['maxs'], f5[k]['last'], f5[k]['two'])
            for k in keys) + '; distinct n %d -> %s; partial %d; volume skip mean/max %s; probe %s' % (
            f5['iii_distinct_n'], 'FAIL' if f5['FAIL'] else 'PASS', T['partial_rows'], '-', T['probe']))
    P('CALIBRATION (own): %s %d/12' % ('PASS' if stop == 0 else 'STOP', sum(1 for t, _ in CAL136 if t in J and not J[t]['if5']['FAIL'])))


if __name__ == '__main__':
    if sys.argv[1] == 'parse':
        for t in sys.argv[2:]:
            do_parse(t)
    else:
        report()
