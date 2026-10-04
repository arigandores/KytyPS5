# S14k (HPP-534), member (0') of ROADMAP s122 item 430(g)(2) with the addition of item 439(v): the upper bound
# C_mod^spec(cls_b) of S-early "at registration" in the form "existence".  No game, no emulator code.
# Inputs (read only, streamed in binary mode, sha256 of every input in the output):
#   the S14j dump of the translation cache of snap0  C:/kyty/s288/s14j/specdump_snap0.txt
#   six S10 logs                                      C:/kyty/s288/s10/log_t2_{1,2,4,5,7,cs0}.txt
#   the first scene frame of the scorer               C:/kyty/s288/s10/runs_s/<tag>.score.json  (field "first")
# Rule (letter of item 430(g)(2)):
#   target     - a new VS/PS module (line "AvTrace: shader ShaderRecompiler VS|PS" after the entry line) inside a series of
#                a counted arm; its specialization - the paired line "AvTrace: shader-spec"; its moment T - generous: the
#                LAST registration of its hash (line "ShaderRegister:", type of the stage) before its compile line; its
#                class - cls_b = (type, RSRC2) of its registrations before the compile line (set; generous);
#   candidate (i)  - a record (permutation) of the dump of the same stage whose file signature equals the full translation
#                signature of the log (item 439(v)) and whose hash is registered in this process before T; its class -
#                cls_b of ANY registration of its hash before T; m(r) = max(moment of the key = process start, first
#                registration of the hash) (item 430(d)(3)), so "available" = a registration of its hash before T exists;
#   candidate (ii) - a "compile" record of the process (VS/PS, any place of the log) with the moment before T; class - same;
#   predicted  - there is a candidate of the same class with EXACTLY equal specialization string.  The own hash of the
#                target is allowed (decisive number); "without the own hash" is a reference.
#   C_mod^spec(cls_b) = the weight share of the series in which ALL new VS/PS modules are predicted (five counted arms).
#   "before": generous union - by the log line order OR by host_us (for a compile record - its lower host bracket, the
#   last host stamp printed before its line); the strict variant (line order only) is printed as a reference.
#   Records of stage MS and CS are neither targets nor candidates.
# Outcome (item 430(g)(3), not changed here): < 0.8 -> "killed without the code of phase A" (read by the lead at S14e);
#   >= 0.8 -> phase A as is; failed > 0 in the dump, a fixture failure, a log of another signature -> NOT COMPUTED.
# Usage:  python c0p_s14k.py [out_dir]     (fixtures run first; the set ends with the line ALL OK)
import sys, os, re, io, hashlib, collections, time, json
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
if os.path.exists('C:/kyty/s288/STOP'): sys.exit(4)

SRC = 'C:/kyty/s288/s10/log_%s.txt'
DUMP = 'C:/kyty/s288/s14j/specdump_snap0.txt'
DUMP_SHA = '050a77129b5b0c475846052a1fb1fd6e50ef7797787df61464d09c3577d64478'      # item 439 (lead recount)
DUMP_TOTALS = (707, 707, 0, 1187)                                                   # files, read, failed, perms
SIG = 'KytySC3:699c1e4b7db359067b461e029b913c4b6e78dc90:robust:ftz:cbank'           # item 439(v)
SCORE = 'C:/kyty/s288/s10/runs_s/%s.score.json'
XCHECK = 'C:/kyty/s288/s14j/xcheck_s10.out.txt'    # reference only (not a gate)
# counted arms of item 408(v) with the scorer rows of C:/kyty/s288/s10/fin_summary.txt (skip rows, held flips)
TAGS = [('t2_1', 'hero_kratos', (31, 34)), ('t2_2', 'hero_drake', (1, 2)), ('t2_4', 'armadillo_challenge_2', (1, 1)),
        ('t2_5', 'fragile_battle_4', (6, 9)), ('t2_7', 'fragile_battle_5', (9, 9)), ('t2_cs0', 'hero_kratos', (30, 32))]
COUNTED = ('t2_1', 't2_2', 't2_4', 't2_5', 't2_7')
WEIGHTS = [35, 30, 3, 2, 15, 18]          # item 430(g)(2); sum 103
N_TARGETS = 33
THR = 0.8
TYPE_OF_STAGE = {'PS': 1, 'VS': 2}
RSRC2 = ('b', '8b')                       # cls_b = type + RSRC2 (item 430(v)); register absent -> empty tuple
REF_PAIR = ('9cef70d99e129f56', '9d04340df2d39aad')   # design 15.3: different hashes, one class, equal specialization

r_reg = re.compile(rb'^ShaderRegister: hash=([0-9a-f]+) type=(\d+) size=(\d+) scratch=(\d+) code=[0-9a-f]+ header=[0-9a-f]+ host_us=(\d+)(.*)$')
r_fu = re.compile(rb'^ShaderFirstUse: hash=([0-9a-f]+) stage=(\d+) words=(\d+) ud=(\d+) host_us=(\d+)')
r_sh = re.compile(rb'^AvTrace: shader ShaderRecompiler (\w+) hash=0x([0-9a-f]+) translate_us=(\d+) compile_us=(\d+) permutations=(\d+)')
r_spec = re.compile(rb'^AvTrace: shader-spec ShaderRecompiler (\w+) hash=0x([0-9a-f]+) perm=(\d+)(.*)$')
r_ft = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
r_ftx = re.compile(rb'^FrameTrace-x: n=(\d+) ')
r_skc = re.compile(rb' skc_held_inc=(\d+) skc_ap_skip=(\d+) ')
r_flip = re.compile(rb'^AvTrace: flip n=(\d+) t=(\d+) host=(\d+)')
r_tok = re.compile(r' (cx)?([0-9a-f]+)=([0-9a-f]{8})')
r_sig = re.compile(r'(KytySC3:[0-9a-f]{40}(?::[A-Za-z][A-Za-z0-9_]*)*)')
r_dsig = re.compile(rb'^SpecDump: file-sig file=(\S+) sig=(\S+)$')
r_drec = re.compile(rb'^SpecDump: file=(\S+) stage=(\w+) hash=0x([0-9a-f]{16}) perm=(\d+) spec=(.*)$')
r_dtot = re.compile(rb'^SpecDump: files=(\d+) read=(\d+) failed=(\d+) perms=(\d+)$')
r_dstg = re.compile(rb'^SpecDump: stage=(\w+) files=(\d+) read=(\d+) failed=(\d+) perms=(\d+)$')
# ONE parser of a specialization for both sources: the tail of "SpecDump: ... spec=" and the tail of "shader-spec ... perm=N".
r_spec_tok = re.compile(r'^(?:b:[0-9a-f]+/[0-9]+/[0-9a-f]+|i:[0-9]+/[0-9]+/[0-9]+/[0-9]+/[0-9a-f]+/[0-9]+)$')


def parse_spec(tail):
    """tail (str) -> canonical specialization string, or None if a token does not parse.  Canonical = the tokens joined
    by one space; the tail must be exactly ' ' + canonical (or empty) - no trimming beyond the line end is applied, so
    equality of the canonical strings is the exact equality of the printed strings."""
    if tail == '': return ''
    if not tail.startswith(' '): return None
    toks = tail[1:].split(' ')
    for t in toks:
        if not r_spec_tok.match(t): return None
    return ' '.join(toks)


def cls_b(typ, text):
    return (typ, tuple((off, val) for c, off, val in r_tok.findall(text) if not c and off in RSRC2))


def read_dump(lines):
    d = dict(sig={}, recs=[], totals=None, stage={}, spec_lines=0, spec_bad=0, sha=None, lines=0, nosig=0)
    h = hashlib.sha256(); n = 0
    for n, l in enumerate(lines, 1):
        h.update(l); l = l.rstrip(b'\r\n')
        if not l.startswith(b'SpecDump: '): continue
        m = r_drec.match(l)
        if m:
            d['spec_lines'] += 1
            sp = parse_spec(m.group(5).decode('latin1'))
            if sp is None: d['spec_bad'] += 1; continue
            d['recs'].append(dict(file=m.group(1).decode(), st=m.group(2).decode(), h=m.group(3).decode(), perm=int(m.group(4)),
                                  spec=sp, line=n))
            continue
        m = r_dsig.match(l)
        if m: d['sig'][m.group(1).decode()] = m.group(2).decode(); continue
        m = r_dtot.match(l)
        if m: d['totals'] = tuple(int(x) for x in m.groups()); continue
        m = r_dstg.match(l)
        if m: d['stage'][m.group(1).decode()] = tuple(int(x) for x in m.groups()[1:])
    for r in d['recs']:
        r['sig'] = d['sig'].get(r['file'])
        if r['sig'] is None: d['nosig'] += 1
    d['lines'] = n; d['sha'] = h.hexdigest()
    return d


def scan_log(lines, lv):
    d = dict(lv=lv, reg=collections.defaultdict(list), sh=[], spec={}, ent=None, frames={}, order=[], sigs=collections.Counter(),
             spec_lines=0, spec_bad=0)
    h = hashlib.sha256(); n = 0; last_host = None; pend = []
    for n, l in enumerate(lines, 1):
        h.update(l)
        c = l[:1]
        if c == b'F':
            m = r_ft.match(l)
            if m:
                k = int(m.group(1)); d['frames'][k] = dict(n=k, line=n, skip=0, held=0); d['order'].append(k)
                for x in pend: x['n'] = k
                pend = []
                continue
            if l.startswith(b'FrameTrace-x: n='):
                m = r_ftx.match(l); k = int(m.group(1)); s = r_skc.search(l)
                if s and k in d['frames']:
                    d['frames'][k]['held'] = int(s.group(1)); d['frames'][k]['skip'] = int(s.group(2))
            continue
        if c == b'S':
            m = r_reg.match(l.rstrip(b'\r\n'))
            if m:
                typ = int(m.group(2))
                d['reg'][m.group(1).decode()].append((n, int(m.group(5)), typ, cls_b(typ, m.group(6).decode('latin1'))))
                last_host = int(m.group(5)); continue
            m = r_fu.match(l)
            if m: last_host = int(m.group(5)); continue
            if b'KytySC3:' in l:
                for s in r_sig.findall(l.decode('latin1')): d['sigs'][s] += 1
            continue
        if c == b'A':
            if l.startswith(b'AvTrace: flip'):
                m = r_flip.match(l)
                if m: last_host = int(m.group(3))
                continue
            if l.startswith(b'AvTrace: shader'):
                m = r_sh.match(l)
                if m:
                    x = dict(st=m.group(1).decode(), h=m.group(2).decode(), perm=int(m.group(5)), line=n, after=d['ent'] is not None,
                             host_lo=last_host, n=None)
                    d['sh'].append(x); pend.append(x); continue
                if l.startswith(b'AvTrace: shader-spec'):
                    d['spec_lines'] += 1
                    m = r_spec.match(l.rstrip(b'\r\n'))
                    sp = parse_spec(m.group(4).decode('latin1')) if m else None
                    if sp is None: d['spec_bad'] += 1; continue
                    d['spec'][n] = (m.group(1).decode(), m.group(2).decode(), int(m.group(3)), sp)
            continue
        if c == b'G':
            if d['ent'] is None and l.startswith(b'GuestOut: Level has started: ' + lv.encode()): d['ent'] = n
            continue
        if b'KytySC3:' in l:
            for s in r_sig.findall(l.decode('latin1')): d['sigs'][s] += 1
    d['lines'] = n; d['sha'] = h.hexdigest(); d['unpaired'] = 0
    for x in d['sh']:                       # the shader-spec line is printed right before its "AvTrace: shader" line
        s = d['spec'].get(x['line'] - 1)
        if s and s[0] == x['st'] and s[1] == x['h'] and s[2] == x['perm']: x['spec'] = s[3]
        else: x['spec'] = None; d['unpaired'] += 1
    return d


def series_of(d, first):
    """series = runs of FrameTrace rows after the entry line with skc_ap_skip > 0 or skc_held_inc > 0 (a gap of 1 clean row
    joins); weight = rows with skip > 0 and n > first + sum of held of rows with n >= first (scorer domain, item 408(g))."""
    rows = [d['frames'][k] for k in d['order'] if d['frames'][k]['line'] > (d['ent'] or 0)]
    wsk = lambda r: 1 if r['skip'] > 0 and r['n'] > first else 0
    whe = lambda r: r['held'] if r['n'] >= first else 0
    sk = sum(wsk(r) for r in rows); he = sum(whe(r) for r in rows)
    bursts = []; cur = None; gap = 0
    for i, r in enumerate(rows):
        if r['skip'] > 0 or r['held'] > 0:
            if cur is None: cur = [i, i]
            else: cur[1] = i
            gap = 0
        elif cur is not None:
            gap += 1
            if gap > 1: bursts.append(cur); cur = None
    if cur is not None: bursts.append(cur)
    ser = []
    for a, b in bursts:
        fr = rows[a:b + 1]
        ser.append(dict(a=fr[0]['n'], b=fr[-1]['n'], w=sum(wsk(r) for r in fr) + sum(whe(r) for r in fr), mods=[]))
    for x in d['sh']:
        x['ser'] = None
        if not x['after'] or x['n'] is None or x['st'] not in TYPE_OF_STAGE: continue
        for s in ser:
            if s['a'] <= x['n'] <= s['b']: s['mods'].append(x); x['ser'] = s
    return ser, (sk, he), len(rows)


def dump_index(dump, sig):
    """candidates (i): records of stage VS/PS whose file signature equals the signature of the log (item 439(v))."""
    idx = collections.defaultdict(set); by_sig = collections.Counter(); n = 0
    for r in dump['recs']:
        if r['st'] not in TYPE_OF_STAGE: continue
        by_sig[r['sig']] += 1
        if r['sig'] != sig: continue
        idx[(r['st'], r['spec'])].add(r['h']); n += 1
    return idx, n, by_sig


def predict(x, d, idx, strict=False, first=False, incl=False, late=False, nocls=False, nomoment=False):
    """the existence predicate for one target x of the log d against the candidate index idx.  Returns a dict:
    ok - predicted (own hash allowed), ok_other - predicted by a candidate of another hash, src - sources found.
    Decisive call - all switches off.  Reference switches (each one only widens the candidate set, except strict / first):
    strict - "before" by the line order only; first - T = the first registration; incl - the records of the OWN hash are
    available at T itself (m(r) <= T); late - a compile record counts up to the compile line of the target; nocls - the
    class is ignored; nomoment - a dump record needs no registration at all and a compile record counts as with late."""
    typ = TYPE_OF_STAGE[x['st']]
    regs = [r for r in d['reg'].get(x['h'], ()) if r[0] < x['line'] and r[2] == typ]
    res = dict(ok=False, ok_other=False, src=[], T=None, ncls=0, nspec_stage=0, nspec_avail=0)
    if not regs or x.get('spec') is None: return res
    T = min(regs) if first else max(regs)
    tcls = set(r[3] for r in regs)
    res['T'] = T[:2]; res['ncls'] = len(tcls)

    def before_reg(r, h):
        return (r[0] < T[0] or (not strict and r[1] < T[1]) or (incl and h == x['h'] and r[0] <= T[0])
                or (nomoment and r[0] < x['line']))

    def classes(h):
        return set(r[3] for r in d['reg'].get(h, ()) if r[2] == typ and before_reg(r, h))

    for h in sorted(idx.get((x['st'], x['spec']), ())):               # (i) records of the dump
        res['nspec_stage'] += 1
        c = classes(h)
        if not c and not nomoment: continue                            # m(r) >= T: the hash is not registered before T
        res['nspec_avail'] += 1
        if nocls or (c & tcls): res['src'].append(('dump', h))
    for y in d['sh']:                                                  # (ii) compile records of the process
        if y is x or y['st'] != x['st'] or y.get('spec') != x['spec']: continue
        if not (y['line'] < T[0] or (not strict and y['host_lo'] is not None and y['host_lo'] < T[1])
                or ((late or nomoment) and y['line'] < x['line'])): continue
        if nocls or (classes(y['h']) & tcls): res['src'].append(('compile', y['h']))
    res['ok'] = bool(res['src'])
    res['ok_other'] = any(h != x['h'] for _, h in res['src'])
    return res


def bound(logs, series, idx_of, counted, **kw):
    """C_mod^spec over the series of the counted arms.  Returns (weight predicted, weight, weight predicted 'other', rows)."""
    w = wp = wo = 0; rows = []
    for tag in counted:
        for s in series[tag]:
            oka = oko = True
            for x in s['mods']:
                p = predict(x, logs[tag], idx_of[tag], **kw)
                oka &= p['ok']; oko &= p['ok_other']; rows.append((tag, s, x, p))
            w += s['w']; wp += s['w'] if oka else 0; wo += s['w'] if oko else 0
    return wp, w, wo, rows


# ------------------------------------------------------------------------------------------------ fixtures
def fx_log(regs, compiles, sig=SIG, ent_at=5, frames=()):
    """a synthetic log: regs = [(line, hash, type, rsrc2, host)], compiles = [(line, stage, hash, spec_tail, perm)] (the
    shader-spec line takes line - 1), frames = [(line, n, held, skip)]; unused lines are filler."""
    L = {}
    L[1] = 'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:%s::10288:376' % sig
    L[ent_at] = 'GuestOut: Level has started: fx_level'
    for ln, h, typ, rs, host in regs:
        off = 'b' if typ == 1 else '8b'
        L[ln] = ('ShaderRegister: hash=%s type=%d size=64 scratch=0 code=0000000900000000 header=0000000900000100 host_us=%d'
                 ' %s=11111111 %s=%s cx1b1=00000000' % (h, typ, host, 'a' if typ == 1 else '8a', off, rs))
    for ln, st, h, tail, perm in compiles:
        L[ln - 1] = 'AvTrace: shader-spec ShaderRecompiler %s hash=0x%s perm=%d%s' % (st, h, perm, tail)
        L[ln] = 'AvTrace: shader ShaderRecompiler %s hash=0x%s translate_us=10 compile_us=10 permutations=%d' % (st, h, perm)
    for ln, n, held, skip in frames:
        L[ln] = 'FrameTrace: n=%d dt_us=16667' % n
        L[ln + 1] = 'FrameTrace-x: n=%d a=1 skc_held_inc=%d skc_ap_skip=%d z=0' % (n, held, skip)
    out = []
    for i in range(1, max(L) + 1): out.append((L.get(i, 'filler %d' % i) + '\n').encode('latin1'))
    return out


def fx_dump(recs, failed=0, vs_failed=0):
    """recs = [(file, stage, hash, perm, spec_tail, sig)]"""
    out = []; seen = set()
    for f, st, h, perm, tail, sig in recs:
        if f not in seen: out.append('SpecDump: file-sig file=%s sig=%s' % (f, sig)); seen.add(f)
        out.append('SpecDump: file=%s stage=%s hash=0x%s perm=%d spec=%s' % (f, st, h, perm, tail))
    out.append('SpecDump: stage=PS files=1 read=1 failed=0 perms=1')
    out.append('SpecDump: stage=VS files=1 read=1 failed=%d perms=1' % vs_failed)
    out.append('SpecDump: files=%d read=%d failed=%d perms=%d' % (len(seen), len(seen) - failed, failed, len(recs)))
    return [(s + '\n').encode('latin1') for s in out]


def computable(dump, logs, fixtures_ok, expect_sha=None, expect_totals=None):
    """the 'NOT COMPUTED' gate of item 430(g)(3) + item 439(v).  Returns the list of reasons (empty = computable)."""
    why = []
    if not fixtures_ok: why.append('fixtures failed')
    if dump['totals'] is None: why.append('dump: no totals line')
    else:
        if dump['totals'][2] > 0: why.append('dump: failed %d > 0' % dump['totals'][2])
        if expect_totals and dump['totals'] != expect_totals: why.append('dump: totals %s differ from the accepted %s' % (dump['totals'], expect_totals))
    for st in ('VS', 'PS'):
        if st not in dump['stage']: why.append('dump: no stage line %s' % st)
        elif dump['stage'][st][2] > 0: why.append('dump: failed %d > 0 on stage %s' % (dump['stage'][st][2], st))
    if expect_sha and dump['sha'] != expect_sha: why.append('dump: sha256 differs from the accepted input')
    if dump['spec_bad']: why.append('dump: %d specialization lines not parsed' % dump['spec_bad'])
    if dump['nosig']: why.append('dump: %d records without a file-sig line' % dump['nosig'])
    for tag, d in logs.items():
        if list(d['sigs']) != [SIG]: why.append('log %s: translation signature %s differs from %s' % (tag, sorted(d['sigs']), SIG))
        if d['spec_bad']: why.append('log %s: %d shader-spec lines not parsed' % (tag, d['spec_bad']))
        if d['unpaired']: why.append('log %s: %d compile lines without the paired shader-spec line' % (tag, d['unpaired']))
        if d['ent'] is None: why.append('log %s: no entry line' % tag)
    return why


def fixtures(P):
    ok = True
    A, B, C, D4 = 'a' * 16, 'b' * 16, 'c' * 16, 'd' * 16
    S1 = ' b:e000010/0/fac i:1/3/1/0/fac/4294967295'
    S2 = ' b:e000010/0/fac i:1/3/1/0/fac/4294967295 b:2000010/0/fac'      # S1 is a prefix of S2
    S3 = ' b:2000001/0/fac'
    NEW = ' b:7777777/7/777'
    OTHER = 'KytySC3:780ea8acc4dd17525bed7c23661f649f50ce4d79:robust:ftz:cbank'
    FR = [(40, 10, 0, 0), (60, 11, 2, 1), (70, 12, 0, 0), (80, 13, 0, 0)]

    def run(name, regs, comps, drecs, want, want_other=None, sig=SIG, frames=FR, tgt=-1, **kw):
        nonlocal ok
        d = scan_log(fx_log(regs, comps, sig=sig, frames=frames), 'fx_level')
        du = read_dump(fx_dump(drecs))
        idx, _, _ = dump_index(du, SIG)
        tg = [x for x in d['sh'] if x['after']]
        p = predict(tg[tgt], d, idx, **kw)
        good = p['ok'] == want and (want_other is None or p['ok_other'] == want_other)
        ok &= good
        P('  fixture %-58s predicted %-5s other-hash %-5s -> %s' % (name, p['ok'], p['ok_other'], 'ok' if good else 'FAILED'))
        return d, du, p

    regAB = [(10, A, 2, '00000004', 100), (20, B, 2, '00000004', 200)]
    tB = [(50, 'VS', B, S1, 1)]
    run('F1 positive: class-mate of the dump, equal spec', regAB, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], True, True)
    run('F2 negative: target spec replaced by an unseen string', regAB, [(50, 'VS', B, NEW, 1)], [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False)
    run('F3a prefix only: candidate longer than the target', regAB, tB, [('vs_a.bin', 'VS', A, 1, S2, SIG)], False, False)
    run('F3b prefix only: target longer than the candidate', regAB, [(50, 'VS', B, S2, 1)], [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False)
    # F4 class with alternation: the records of the class alternate S1 / S3 and the LAST one before T is S3 - existence finds S1
    run('F4a alternating specs in the class, last one differs', regAB, tB,
        [('vs_a.bin', 'VS', A, 1, S1, SIG), ('vs_a.bin', 'VS', A, 2, S3, SIG), ('vs_a.bin', 'VS', A, 3, S1, SIG), ('vs_a.bin', 'VS', A, 4, S3, SIG)], True, True)
    # the hash of the candidate alternates between two classes before T: class of a record = ANY of its registrations before T
    regalt = [(8, A, 2, '00000004', 80), (9, A, 2, '00000008', 90), (10, A, 2, '00000004', 100), (11, A, 2, '00000008', 110),
              (20, B, 2, '00000004', 200)]
    run('F4b alternating classes of the candidate hash (4, 8, 4, 8)', regalt, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], True, True)
    regalt2 = [(8, A, 2, '00000008', 80), (20, B, 2, '00000004', 200), (22, A, 2, '00000004', 220)]
    run('F4c class of the candidate equals only AFTER T', regalt2, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False)
    run('F5 another class, equal spec', [(10, A, 2, '00000008', 100), (20, B, 2, '00000004', 200)], tB,
        [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False)
    run('F6 candidate hash registered only after T', [(20, B, 2, '00000004', 200), (22, A, 2, '00000004', 220)], tB,
        [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False)
    run('F7a another stage (PS record, VS target)', [(10, A, 1, '00000004', 100), (20, B, 2, '00000004', 200)], tB,
        [('ps_a.bin', 'PS', A, 1, S1, SIG)], False, False)
    run('F7b MS and CS records are not candidates', regAB, tB,
        [('vs_a.bin', 'MS', A, 1, S1, SIG), ('cs_a.bin', 'CS', A, 1, S1, SIG)], False, False)
    run('F8 record of another file signature (item 439(v))', regAB, tB, [('vs_a.bin', 'VS', A, 1, S1, OTHER)], False, False)
    # own hash: a record of the hash of the target is available "before T" only if the hash has an EARLIER registration
    run('F9a own hash, registered twice before the compile', [(8, B, 2, '00000004', 80), (20, B, 2, '00000004', 200)], tB,
        [('vs_b.bin', 'VS', B, 1, S1, SIG)], True, False)
    run('F9b own hash, single registration (= T): letter - no', regAB, tB, [('vs_b.bin', 'VS', B, 1, S1, SIG)], False, False)
    run('F9c own hash, single registration, reference incl: yes', regAB, tB, [('vs_b.bin', 'VS', B, 1, S1, SIG)], True, False, incl=True)
    # compile records of the process (ii)
    regC = [(10, A, 2, '00000004', 100), (20, B, 2, '00000004', 200)]
    run('F10a compile record of a class-mate before T', [(6, A, 2, '00000004', 60), (20, B, 2, '00000004', 200)],
        [(12, 'VS', A, S1, 1), (50, 'VS', B, S1, 1)], [], True, True)
    run('F10b compile record of a class-mate after T', regC, [(30, 'VS', A, S1, 1), (50, 'VS', B, S1, 1)], [], False, False)
    run('F10c own hash compiled twice, re-registered between', [(6, B, 2, '00000004', 60), (20, B, 2, '00000004', 200)],
        [(12, 'VS', B, S1, 1), (50, 'VS', B, S1, 1)], [], True, False)
    run('F10d the target is not its own candidate', [(20, B, 2, '00000004', 200)], tB, [], False, False)
    run('F10e compile record before the entry line counts', [(2, A, 2, '00000004', 20), (20, B, 2, '00000004', 200)],
        [(4, 'VS', A, S1, 1), (50, 'VS', B, S1, 1)], [], True, True)
    # generous target moment: last registration before the compile (candidate registered between the first and the last)
    reglast = [(8, B, 2, '00000004', 80), (15, A, 2, '00000004', 150), (20, B, 2, '00000004', 200)]
    run('F11a generous T = last registration: found', reglast, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], True, True)
    run('F11b reference T = first registration: not found', reglast, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False, first=True)
    # host order against line order: the candidate registration is printed after T but stamped before it
    reghost = [(20, B, 2, '00000004', 200), (22, A, 2, '00000004', 150)]
    run('F12a generous "before" by host_us: found', reghost, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], True, True)
    run('F12b strict line order: not found', reghost, tB, [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False, strict=True)
    run('F12c reference late: class-mate compiled after T, before', regC, [(30, 'VS', A, S1, 1), (50, 'VS', B, S1, 1)], [], True, True, late=True)
    run('F12d reference nocls: another class counts', [(10, A, 2, '00000008', 100), (20, B, 2, '00000004', 200)], tB,
        [('vs_a.bin', 'VS', A, 1, S1, SIG)], True, True, nocls=True)
    run('F12e reference nocls + nomoment: unregistered hash counts', [(20, B, 2, '00000004', 200)], tB,
        [('vs_a.bin', 'VS', A, 1, S1, SIG)], True, True, nocls=True, nomoment=True)
    run('F12f nocls + nomoment still needs the equal spec', [(20, B, 2, '00000004', 200)], tB,
        [('vs_a.bin', 'VS', A, 1, S2, SIG)], False, False, nocls=True, nomoment=True)
    run('F13 target without a registration before its compile', [(10, A, 2, '00000004', 100), (55, B, 2, '00000004', 550)], tB,
        [('vs_a.bin', 'VS', A, 1, S1, SIG)], False, False)

    # F14 weights: series 1 (frame 11, weight 3) holds two targets, series 2 (frame 21, weight 5) holds one
    regs = [(10, A, 2, '00000004', 100), (20, B, 2, '00000004', 200), (21, C, 2, '00000004', 210), (22, D4, 2, '00000004', 220)]
    frames = [(40, 10, 0, 0), (60, 11, 2, 1), (70, 12, 0, 0), (80, 13, 0, 0), (100, 21, 4, 1), (110, 22, 0, 0), (120, 23, 0, 0)]

    def wcase(name, comps, want):
        nonlocal ok
        d = scan_log(fx_log(regs, comps, frames=frames), 'fx_level')
        du = read_dump(fx_dump([('vs_a.bin', 'VS', A, 1, S1, SIG)]))
        idx, ncand, by_sig = dump_index(du, SIG)
        ser, (sk, he), _ = series_of(d, 10)
        wp, w, wo, rows = bound({'fx': d}, {'fx': ser}, {'fx': idx}, ('fx',))
        good = (wp, w) == want and [s['w'] for s in ser] == [3, 5]
        ok &= good
        P('  fixture %-58s C = %d / %d (want %d / %d), series weights %s -> %s' % (name, wp, w, want[0], want[1], [s['w'] for s in ser], 'ok' if good else 'FAILED'))
    wcase('F14a both series predicted', [(50, 'VS', B, S1, 1), (52, 'VS', C, S1, 1), (95, 'VS', D4, S1, 1)], (8, 8))
    wcase('F14b one of two modules of series 1 unpredicted', [(50, 'VS', B, S1, 1), (52, 'VS', C, NEW, 1), (95, 'VS', D4, S1, 1)], (5, 8))
    wcase('F14c series 2 unpredicted', [(50, 'VS', B, S1, 1), (52, 'VS', C, S1, 1), (95, 'VS', D4, S3, 1)], (3, 8))

    # F15 one parser for both sources
    good_tails = ['', S1, S2, ' i:2/5/1/0/204/4294967295', ' b:1/0/fac']
    bad_tails = [' b:e000010/0', ' x:1/2/3', '  b:e000010/0/fac', ' b:e000010/0/fac ', 'b:e000010/0/fac', ' b:E000010/0/fac', ' i:1/3/1/0/fac']
    g = all(parse_spec(t) is not None for t in good_tails) and all(parse_spec(t) is None for t in bad_tails)
    d = scan_log(fx_log(regAB, [(50, 'VS', B, S1, 1), (56, 'VS', B, ' b:e000010/0', 1)]), 'fx_level')
    du = read_dump(fx_dump([('vs_a.bin', 'VS', A, 1, S1, SIG), ('vs_a.bin', 'VS', A, 2, ' x:1/2/3', SIG)]))
    g &= d['spec_lines'] == 2 and d['spec_bad'] == 1 and du['spec_lines'] == 2 and du['spec_bad'] == 1
    g &= d['sh'][0]['spec'] == du['recs'][0]['spec'] == parse_spec(S1)
    ok &= g
    P('  fixture %-58s -> %s' % ('F15 one parser: 5 good and 7 bad tails, both line kinds', 'ok' if g else 'FAILED'))

    # F16 the NOT COMPUTED gate
    base_log = scan_log(fx_log(regAB, tB), 'fx_level')
    base_dump = read_dump(fx_dump([('vs_a.bin', 'VS', A, 1, S1, SIG)]))
    cases = [('F16a clean inputs are computable', computable(base_dump, {'fx': base_log}, True) == []),
             ('F16b dump failed > 0', computable(read_dump(fx_dump([('vs_a.bin', 'VS', A, 1, S1, SIG)], failed=1)), {'fx': base_log}, True) != []),
             ('F16c dump failed > 0 on stage VS', computable(read_dump(fx_dump([('vs_a.bin', 'VS', A, 1, S1, SIG)], vs_failed=1)), {'fx': base_log}, True) != []),
             ('F16d log of another translation signature', computable(base_dump, {'fx': scan_log(fx_log(regAB, tB, sig=OTHER), 'fx_level')}, True) != []),
             ('F16e fixture failure', computable(base_dump, {'fx': base_log}, False) != []),
             ('F16f unparsed spec line in a log', computable(base_dump, {'fx': d}, True) != []),
             ('F16g unparsed spec line in the dump', computable(du, {'fx': base_log}, True) != []),
             ('F16h dump sha256 differs from the accepted', computable(base_dump, {'fx': base_log}, True, expect_sha='0' * 64) != []),
             ('F16i candidates counted by signature',
              dump_index(read_dump(fx_dump([('vs_a.bin', 'VS', A, 1, S1, SIG), ('vs_c.bin', 'VS', C, 1, S1, OTHER), ('cs_c.bin', 'CS', C, 1, S1, SIG)])), SIG)[1:]
              == (1, collections.Counter({SIG: 1, OTHER: 1})))]
    for name, g in cases:
        ok &= g
        P('  fixture %-58s -> %s' % (name, 'ok' if g else 'FAILED'))
    return ok


# ------------------------------------------------------------------------------------------------ main
def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s14k'
    out = []; P = out.append; t0 = time.time()
    P('S14k member (0\') - upper bound C_mod^spec(cls_b), form "existence" (ROADMAP s122 items 430(g)(2), 439(v)); threshold %.1f' % THR)
    P('script sha256 %s' % hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest())
    P('')
    P('== fixtures')
    fx_out = []
    fx_ok = fixtures(fx_out.append)
    out.extend(fx_out)
    P('fixtures: %d lines, failed %d' % (len(fx_out), sum(1 for l in fx_out if l.endswith('FAILED'))))
    P('ALL OK' if fx_ok else 'FIXTURES FAILED')
    open(os.path.join(out_dir, 'c0p_fixtures.out.txt'), 'w', encoding='utf-8', newline='\n').write(
        '\n'.join(fx_out + ['ALL OK' if fx_ok else 'FIXTURES FAILED']) + '\n')

    P('')
    P('== inputs')
    with open(DUMP, 'rb') as f: dump = read_dump(f)
    P('dump %s: lines %d sha256 %s (accepted %s: %s); totals files=%s read=%s failed=%s perms=%s; stage lines %s'
      % ((DUMP, dump['lines'], dump['sha'], DUMP_SHA[:8], 'EQUAL' if dump['sha'] == DUMP_SHA else 'DIFFERS') + (dump['totals'] or (None,) * 4)
         + (dict((k, 'files=%d read=%d failed=%d perms=%d' % v) for k, v in sorted(dump['stage'].items())),)))
    st_n = collections.Counter(r['st'] for r in dump['recs'])
    P('dump records (permutation lines) %d: %s; specialization lines parsed by parse_spec %d of %d (%.1f %%); file-sig lines %d, groups %s; '
      'records without a file-sig line %d' % (len(dump['recs']), dict(sorted(st_n.items())), dump['spec_lines'] - dump['spec_bad'], dump['spec_lines'],
      100.0 * (dump['spec_lines'] - dump['spec_bad']) / max(1, dump['spec_lines']), len(dump['sig']),
      sorted(collections.Counter(s.split(':')[1][:8] for s in dump['sig'].values()).items(), key=lambda kv: -kv[1]), dump['nosig']))
    logs = {}; ser = {}; idx_of = {}; w_ok = True
    for tag, lv, exp in TAGS:
        with open(SRC % tag, 'rb') as f: d = scan_log(f, lv)
        logs[tag] = d
        first = json.load(open(SCORE % tag, encoding='utf-8'))['first'][0]
        s, got, nrows = series_of(d, first)
        ser[tag] = s; d['first'] = first; d['got'] = got
        w_ok &= got == exp
        sig = list(d['sigs'])[0] if len(d['sigs']) == 1 else None
        idx, ncand, by_sig = dump_index(dump, sig)
        idx_of[tag] = idx; d['ncand'] = ncand
        P('%s %s: lines %d sha256 %s; entry line %s; translation signature %s (lines with it %d; equals %s: %s); dump records VS/PS by file '
          'signature: %s -> candidates (i) %d; shader-spec lines parsed %d of %d (%.1f %%); compile lines %d, unpaired %d'
          % (tag, lv, d['lines'], d['sha'], d['ent'], sorted(d['sigs']), sum(d['sigs'].values()), SIG.split(':')[1][:8],
             'YES' if list(d['sigs']) == [SIG] else 'NO', dict((k.split(':')[1][:8] if k else None, v) for k, v in by_sig.items()), ncand,
             d['spec_lines'] - d['spec_bad'], d['spec_lines'], 100.0 * (d['spec_lines'] - d['spec_bad']) / max(1, d['spec_lines']),
             len(d['sh']), d['unpaired']))

    P('')
    P('== series and weights (same rule as S14d c0_s14d.py; scorer domain)')
    for tag, lv, exp in TAGS:
        d = logs[tag]
        P('%s: first scene frame n %d; skip rows %d held %d (fin_summary %d / %d: %s); series %s'
          % (tag, d['first'], d['got'][0], d['got'][1], exp[0], exp[1], 'EQUAL' if d['got'] == exp else 'DIFFERS',
             [(s['a'], s['b'], 'w=%d' % s['w'], 'VS/PS mods=%d' % len(s['mods'])) for s in ser[tag]]))
    wl = [s['w'] for t in COUNTED for s in ser[t]]; nt = sum(len(s['mods']) for t in COUNTED for s in ser[t])
    P('five counted arms: series weights %s (rule: %s), sum %d; targets %d (rule: %d)' % (wl, WEIGHTS, sum(wl), nt, N_TARGETS))

    why = computable(dump, logs, fx_ok, expect_sha=DUMP_SHA, expect_totals=DUMP_TOTALS)
    if not w_ok: why.append('series weights differ from fin_summary')
    if wl != WEIGHTS or nt != N_TARGETS: why.append('series weights / targets differ from item 430(g)(2)')

    P('')
    P('== targets (decisive: T = last registration before the compile, "before" = line order OR host_us, own hash allowed)')
    wp, w, wo, rows = bound(logs, ser, idx_of, COUNTED)
    all_rows = rows + bound(logs, ser, idx_of, ('t2_cs0',))[3]
    cur = None
    for tag, s, x, p in all_rows:
        if cur is not s:
            cur = s
            rr = [q for q in all_rows if q[1] is s]
            P('%s series n %d..%d weight %d: new VS/PS modules %d, predicted %d (by another hash %d) -> series predicted %s'
              % (tag, s['a'], s['b'], s['w'], len(rr), sum(1 for q in rr if q[3]['ok']), sum(1 for q in rr if q[3]['ok_other']),
                 all(q[3]['ok'] for q in rr)))
        src = collections.Counter(('%s-%s' % (k, 'own' if h == x['h'] else 'other')) for k, h in p['src'])
        P('    %s %s perm %d line %d frame %s: T line %s host %s; classes %d; spec %d tokens sha %s; dump records of the stage with the equal '
          'spec: hashes %d, registered before T %d; candidates of the class with the equal spec: %s -> %s'
          % (x['st'], x['h'], x['perm'], x['line'], x['n'], p['T'][0] if p['T'] else None, p['T'][1] if p['T'] else None, p['ncls'],
             len(x['spec'].split(' ')) if x['spec'] else 0, hashlib.sha256((x['spec'] or '').encode()).hexdigest()[:12], p['nspec_stage'],
             p['nspec_avail'], dict(sorted(src.items())) or 'none',
             'PREDICTED' if p['ok_other'] else ('PREDICTED (own hash only)' if p['ok'] else 'not predicted')))
    multi = sum(1 for _, _, _, p in rows if p['ncls'] > 1)
    P('five counted arms: targets %d, predicted %d (by another hash %d, by the own hash only %d), not predicted %d; targets with more than '
      'one class among their registrations %d' % (len(rows), sum(1 for r in rows if r[3]['ok']), sum(1 for r in rows if r[3]['ok_other']),
      sum(1 for r in rows if r[3]['ok'] and not r[3]['ok_other']), sum(1 for r in rows if not r[3]['ok']), multi))

    P('')
    P('== reference pair of the design 15.3 (different hashes of one class with equal specialization): found if its second record is a target')
    P('   matching level = class and exact spec equality with the moment member of candidate (ii) switched off (switch late); rule level = the')
    P('   letter of candidate (ii): the first record must enter the table before T (the last registration of the target before its compile)')
    pair_match = True; pair_rule = True; ref_n = 0
    for tag, lv, exp in TAGS:
        d = logs[tag]
        a = [x for x in d['sh'] if x['h'] == REF_PAIR[0]]; b = [x for x in d['sh'] if x['h'] == REF_PAIR[1]]
        for y in b:
            firsts = [x for x in a if x['line'] < y['line'] and x.get('spec') == y.get('spec') and x['st'] == y['st']]
            if not firsts: continue
            row = [r for r in all_rows if r[2] is y]
            if not row:
                P('%s: %s line %d after %s line %d, equal spec - the second record is not a target (outside the series)'
                  % (tag, y['h'], y['line'], REF_PAIR[0], firsts[0]['line']))
                continue
            f_rule = ('compile', REF_PAIR[0]) in row[0][3]['src']
            f_match = ('compile', REF_PAIR[0]) in predict(y, d, idx_of[tag], late=True)['src']
            T = row[0][3]['T']
            ref_n += 1; pair_match &= f_match; pair_rule &= f_rule
            P('%s: second record %s compile line %d is a target (T line %d host %d); first record %s compile line %d host bracket %s; equal spec: '
              'found at the matching level %s; found by the rule %s%s' % (tag, y['h'], y['line'], T[0], T[1], REF_PAIR[0], firsts[0]['line'],
              firsts[0]['host_lo'], f_match, f_rule, '' if f_rule else
              ' - the first record is compiled %d lines AFTER T, it is not in the table at the registration of the target' % (firsts[0]['line'] - T[0])))
    P('reference pair: cases with the second record a target %d; matching level %s; rule level %s'
      % (ref_n, 'ALL FOUND' if pair_match and ref_n else 'FAILED', 'ALL FOUND' if pair_rule and ref_n else 'NOT FOUND (moment member)'))
    if not (pair_match and ref_n): why.append('reference pair control failed at the matching level')

    P('')
    P('== references (do not enter the rule)')
    REFS = (('R1 strict "before" (line order only)', dict(strict=True)),
            ('R2 T = FIRST registration of the target (predictor B, design 6.1 A3)', dict(first=True)),
            ('R3 own hash available at T itself (m(r) <= T; executor variant, more generous)', dict(incl=True)),
            ('R4 = R3 + a compile record counts up to the compile line of the target', dict(incl=True, late=True)),
            ('R5 class ignored (type only), moments by the letter', dict(nocls=True)),
            ('R6 ceiling: class ignored, no moment (any dump record of the stage and signature, any earlier compile)', dict(nocls=True, nomoment=True)))
    ref_val = {}
    for name, kw in REFS:
        a, b, c, rr = bound(logs, ser, idx_of, COUNTED, **kw)
        ref_val[name[:2]] = float(a) / b
        P('%s: C_mod^spec %.4f (%d / %d), without the own hash %.4f (%d / %d); targets predicted %d of %d, by another hash %d; weights of the '
          'predicted series %s' % (name, float(a) / b, a, b, float(c) / b, c, b, sum(1 for r in rr if r[3]['ok']), len(rr),
          sum(1 for r in rr if r[3]['ok_other']), [s2['w'] for t in COUNTED for s2 in ser[t] if all(r[3]['ok'] for r in rr if r[1] is s2)]))
    n_any = sum(1 for _, _, x, p in rows if p['nspec_stage'] > 0); n_av = sum(1 for _, _, x, p in rows if p['nspec_avail'] > 0)
    P('class-free: targets whose spec string exists in the dump for the stage (any hash, any moment) %d of %d; with a hash registered before T %d'
      % (n_any, len(rows), n_av))
    a, b, c, rr = bound(logs, ser, idx_of, ('t2_cs0',))
    P('t2_cs0 (repeat of hero_kratos, not in the sum): C_mod^spec %.4f (%d / %d), without the own hash %.4f (%d / %d); targets predicted %d of %d'
      % (float(a) / b, a, b, float(c) / b, c, b, sum(1 for r in rr if r[3]['ok']), len(rr)))
    # the same spec string against the same hash in the dump: a compiled module whose (hash, spec string) is already in snap0
    own = [(t, x) for t, s, x, p in rows if x['h'] in idx_of[t].get((x['st'], x['spec']), ())]
    P('targets compiled although the dump holds a record of the SAME hash with the equal spec string: %d of %d (%s) - the spec string is not '
      'the whole key of a module (the file name carries the hash of the key: <stage>_<hash>_<key hash>.bin), so equality of the strings is '
      'more generous than equality of the keys' % (len(own), len(rows), ', '.join('%s %s' % (t, x['h'][:8]) for t, x in own) or '-'))
    # cross-check with the independent tool of S14j (xcheck_s14j.py, output xcheck_s10.out.txt; its statistic: shader-spec lines
    # of ALL stages for which a file of the same stage and hash has the permutation of the SAME number with the equal spec tail)
    allidx = set((r['st'], r['h'], r['spec']) for r in dump['recs'] if r['sig'] == SIG)
    permidx = set((r['st'], r['h'], r['perm'], r['spec']) for r in dump['recs'] if r['sig'] == SIG)
    xc = {}
    try:
        for l in open(XCHECK, encoding='utf-8'):
            m = re.match(r'^C:/kyty/s288/s10/log_(\w+)\.txt sha256 [0-9a-f]+: (?:EQUAL (\d+))?', l)
            if m: xc[m.group(1)] = int(m.group(2) or 0)
    except IOError: pass
    for tag, lv, exp in TAGS:
        d = logs[tag]
        n_perm = sum(1 for (st, h, perm, sp) in d['spec'].values() if (st, h, perm, sp) in permidx)
        n_eq = sum(1 for (st, h, perm, sp) in d['spec'].values() if (st, h, sp) in allidx)
        P('cross-check %s: shader-spec lines (all stages) %d; a dump record of the same stage, hash, permutation number and spec string %d - '
          'S14j xcheck_s10.out.txt EQUAL %s: %s; of the same stage, hash and spec string under any permutation number %d'
          % (tag, len(d['spec']), n_perm, xc.get(tag), 'EQUAL' if xc.get(tag) == n_perm else 'DIFFERS', n_eq))
    P('')
    P('== outcome')
    c_dec = float(wp) / w if w else 0.0
    P('C_mod^spec(cls_b) = %.4f (%d / %d) - decisive (own hash allowed); without the own hash %.4f (%d / %d) - reference'
      % (c_dec, wp, w, float(wo) / w if w else 0.0, wo, w))
    P('robustness: the most generous reference R6 (class ignored, no moment) %.4f %s %.1f' % (ref_val['R6'], '<' if ref_val['R6'] < THR else '>=', THR))
    if why:
        P('OUTCOME: NOT COMPUTED - %s (item 430(g)(3): phase A goes)' % '; '.join(why))
    else:
        if c_dec < THR:
            P('OUTCOME: C_mod^spec(cls_b) %.4f < %.1f -> by item 430(g)(3) the candidate is "killed without the code of phase A" (read by the lead '
              'at the acceptance of S14e, if Red Team does not find that the number is not an upper bound)' % (c_dec, THR))
        else:
            P('OUTCOME: C_mod^spec(cls_b) %.4f >= %.1f -> by item 430(g)(3) phase A goes as is' % (c_dec, THR))
        if not pair_rule:
            P('QUESTION TO THE LEAD (the outcome above is the executor reading): the control "the reference pair of 15.3 is found if its second '
              'record is a target" holds at the matching level only; by the rule the pair is not a prediction (the first record enters the table '
              'after T).  If the control is read as "found by the rule", the outcome is NOT COMPUTED')
    P('')
    P('wall %.1f s' % (time.time() - t0))
    open(os.path.join(out_dir, 'c0p_s14k.out.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    # table of the targets for the reviewers
    tsv = ['arm\tseries\tweight\tstage\thash\tperm\tline\tT_line\tT_host\tspec_sha12\tspec_tokens\tpredicted\tby_other_hash\tsources']
    for tag, s, x, p in all_rows:
        tsv.append('\t'.join(str(v) for v in (tag, '%d..%d' % (s['a'], s['b']), s['w'], x['st'], x['h'], x['perm'], x['line'],
                   p['T'][0] if p['T'] else '', p['T'][1] if p['T'] else '', hashlib.sha256((x['spec'] or '').encode()).hexdigest()[:12],
                   len(x['spec'].split(' ')) if x['spec'] else 0, int(p['ok']), int(p['ok_other']),
                   ','.join(sorted(set('%s:%s' % (k, h) for k, h in p['src']))) or '-')))
    open(os.path.join(out_dir, 'targets_s14k.tsv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tsv) + '\n')
    print('\n'.join(out))
    return 0 if fx_ok else 1


if __name__ == '__main__':
    sys.exit(main())
