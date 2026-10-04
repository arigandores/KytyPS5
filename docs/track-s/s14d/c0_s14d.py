# S14d (HPP-527), member (0) of ROADMAP s122 item 423(g)(1): the pre-falsifier of S-early "at registration" on the S10 logs.
# No game, no code.  Streams the raw logs C:/kyty/s288/s10/log_t2_*.txt in binary mode (sha256 in the output) and answers:
#   Q1  do the logs carry, for EVERY record of the predictor-B table (a permutation entering ProgramCache at the three
#       sites Compile / LoadFromTranslationCache / Resolve, including the keys loaded from the translation cache at start),
#       the resource specialization, the header class and the moment?  If yes - the upper bound C_mod^spec; if not -
#       "not computed" with the missing line named.
#   Q2  (executor variant, NOT the bound of the letter) the weaker necessary condition that IS computable: the class of the
#       target is non-empty before its registration (C_mod^cls, class cls_b; file names of snap0 as the cache index).
#   Q3  member (7): is the PM4 lead "guest submit -> GuestGpu processing" computable from the S10 lines.
#   Q4  member (5): the worker-count line of the asynchronous creation.
# Every number is [c] of the named lines; the reading labels are printed with the numbers.
import sys, os, re, hashlib, collections, time, json
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
if os.path.exists('C:/kyty/s288/STOP'): sys.exit(4)
SRC = 'C:/kyty/s288/s10/log_%s.txt'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s14d/c0_s14d.out.txt'
SNAP0 = 'C:/kyty/s288/snap0/MANIFEST.txt'
# counted arms of item 408(v) with the scorer rows of C:/kyty/s288/s10/fin_summary.txt (skip rows, held flips)
TAGS = [('t2_1', 'hero_kratos', (31, 34)), ('t2_2', 'hero_drake', (1, 2)), ('t2_4', 'armadillo_challenge_2', (1, 1)),
        ('t2_5', 'fragile_battle_4', (6, 9)), ('t2_7', 'fragile_battle_5', (9, 9)), ('t2_cs0', 'hero_kratos', (30, 32))]
COUNTED = ('t2_1', 't2_2', 't2_4', 't2_5', 't2_7')
# cls_b constant of the design revision (item 423(v)(3)): sh registers of the header WITHOUT these offsets, all cx registers
EXCL_SH = ('6', '8', '9', '80', '88', '89', 'c8', 'c9')
TYPE_OF_STAGE = {'PS': 1, 'VS': 2}
THR = 0.8

r_reg = re.compile(rb'^ShaderRegister: hash=([0-9a-f]+) type=(\d+) size=(\d+) scratch=(\d+) code=[0-9a-f]+ header=[0-9a-f]+ host_us=(\d+)(.*)$')
r_fu = re.compile(rb'^ShaderFirstUse: hash=([0-9a-f]+) stage=(\d+) words=(\d+) ud=(\d+) host_us=(\d+)')
r_sh = re.compile(rb'^AvTrace: shader ShaderRecompiler (\w+) hash=0x([0-9a-f]+) translate_us=(\d+) compile_us=(\d+) permutations=(\d+)')
r_spec = re.compile(rb'^AvTrace: shader-spec ShaderRecompiler (\w+) hash=0x([0-9a-f]+) perm=(\d+)(.*)$')
r_load = re.compile(rb'^AvTrace: shader-cache load hash=0x([0-9a-f]+) permutations=(\d+)')
r_pre = re.compile(rb'^PipelinePrecache: (\d+) recipes -> (\d+) graphics \+ (\d+) compute pipelines queued, (\d+) skipped, (\d+) sources loaded')
r_ft = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
r_ftx = re.compile(rb'^FrameTrace-x: n=(\d+) ')
r_skc = re.compile(rb' skc_held_inc=(\d+) skc_ap_skip=(\d+) ')
r_flip = re.compile(rb'^AvTrace: flip n=(\d+) t=(\d+) host=(\d+)')
r_wk = re.compile(rb'^AsyncPipelines: mode=(\d+) workers=(\d+)')
r_hdr = re.compile(rb'^\[\d+\]\[\d\d:\d\d:\d\d\.\d+\] (\S+)')
r_tok = re.compile(r' (cx)?([0-9a-f]+)=([0-9a-f]{8})')


def cls_b(typ, text):
    sh = []; cx = []
    for c, off, val in r_tok.findall(text):
        if c: cx.append((off, val))
        elif off not in EXCL_SH: sh.append((off, val))
    return (typ, tuple(sh), tuple(cx))


# ladder of register-only classes (sensitivity of the class-non-empty bound to the composition of the class).
# RSRC1 / RSRC2 = the two kept sh registers of a PS (a, b) and of a vertex stage (8a, 8b).
RSRC1 = ('a', '8a'); RSRC2 = ('b', '8b')
LADDER = [('L0 type only', lambda c: (c[0],)),
          ('L1 type + RSRC2', lambda c: (c[0], tuple(x for x in c[1] if x[0] in RSRC2))),
          ('L2 type + RSRC1 + RSRC2', lambda c: (c[0], c[1])),
          ('L3 type + all cx', lambda c: (c[0], c[2])),
          ('L4 type + RSRC1 + RSRC2 + all cx (= cls_b of S14a)', lambda c: c)]


def scan(tag, lv):
    d = dict(tag=tag, lv=lv, reg=collections.defaultdict(list), fu={}, sh=[], spec={}, loads=[], pre=None, ent=None,
             frames={}, order=[], workers=None, lag=0, acb=0, hdr=collections.Counter(), wlag=0, seed=None, tc=None,
             spec_before=0, spec_after=0, sh_before=0, save=0)
    h = hashlib.sha256(); n = 0; cur_n = None; last_host = None; pend = []
    with open(SRC % tag, 'rb') as f:
        for n, l in enumerate(f, 1):
            h.update(l)
            c = l[:1]
            if c == b'F':
                m = r_ft.match(l)
                if m:
                    cur_n = int(m.group(1)); d['frames'][cur_n] = dict(n=cur_n, dt=int(m.group(2)), line=n, skip=0, held=0, after=d['ent'] is not None)
                    d['order'].append(cur_n)
                    for x in pend: x['n'] = cur_n
                    pend = []
                    continue
                if l.startswith(b'FrameTrace-x: n='):
                    m = r_ftx.match(l); k = int(m.group(1)); s = r_skc.search(l)
                    if s and k in d['frames']:
                        d['frames'][k]['held'] = int(s.group(1)); d['frames'][k]['skip'] = int(s.group(2))
                    continue
                if l.startswith(b'FrameTrace-draw:') and b' da_wlag_us=' in l: d['wlag'] += 1
                continue
            if c == b'S':
                m = r_reg.match(l.rstrip(b'\r\n'))
                if m:
                    typ = int(m.group(2)); txt = m.group(6).decode('latin1')
                    d['reg'][m.group(1).decode()].append((n, int(m.group(5)), typ, cls_b(typ, txt)))
                    last_host = int(m.group(5)); continue
                m = r_fu.match(l)
                if m:
                    d['fu'].setdefault((m.group(1).decode(), int(m.group(2))), (n, int(m.group(5)))); last_host = int(m.group(5)); continue
                if l.startswith(b'ShaderSeed: compatibility='): d['seed'] = l.rstrip().decode('latin1'); continue
                if l.startswith(b'Shader translation cache:'): d['tc'] = l.rstrip().decode('latin1'); continue
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
                        d['sh'].append(x); pend.append(x)
                        if d['ent'] is None: d['sh_before'] += 1
                        continue
                    m = r_spec.match(l.rstrip(b'\r\n'))
                    if m:
                        d['spec'][n] = (m.group(1).decode(), m.group(2).decode(), int(m.group(3)), m.group(4).decode('latin1').strip())
                        if d['ent'] is None: d['spec_before'] += 1
                        else: d['spec_after'] += 1
                        continue
                    m = r_load.match(l)
                    if m: d['loads'].append((n, m.group(1).decode(), int(m.group(2)))); continue
                    if l.startswith(b'AvTrace: shader-cache save'): d['save'] += 1
                    continue
                m = r_wk.match(l)
                if m: d['workers'] = (int(m.group(1)), int(m.group(2)), n)
                continue
            if c == b'P':
                m = r_pre.match(l)
                if m: d['pre'] = (n,) + tuple(int(x) for x in m.groups())
                continue
            if c == b'G':
                if d['ent'] is None and l.startswith(b'GuestOut: Level has started: ' + lv.encode()): d['ent'] = n
                continue
            if c == b'L':
                if l.startswith(b'LagTrace:'): d['lag'] += 1
                continue
            if c == b'\t':
                if l.startswith(b'\t acb   = '): d['acb'] += 1
                continue
            if c == b'[':
                m = r_hdr.match(l)
                if m: d['hdr'][m.group(1).decode('latin1')] += 1
    d['lines'] = n; d['sha'] = h.hexdigest()
    return d


def snap0_index():
    idx = collections.defaultdict(set); sha = hashlib.sha256()
    with open(SNAP0, 'rb') as f:
        for l in f:
            sha.update(l)
            m = re.match(rb'^ShaderCache_PPSA21564/(cs|ps|vs)_([0-9a-f]{16})_([0-9a-f]{16})\.bin ', l)
            if m: idx[m.group(1).decode().upper()].add((m.group(2).decode(), m.group(3).decode()))
    return idx, sha.hexdigest()


out = []
P = out.append
t0 = time.time()
idx, idx_sha = snap0_index()
idx_h = dict((st, set(h for h, _ in v)) for st, v in idx.items())
P('S14d member (0) - pre-falsifier of S-early "at registration" on the S10 logs (ROADMAP s122 item 423(g)(1)); threshold %.1f' % THR)
P('snap0 cache index (file names of %s, sha256 %s): files VS %d PS %d CS %d; distinct hashes VS %d PS %d CS %d'
  % (SNAP0, idx_sha, len(idx['VS']), len(idx['PS']), len(idx['CS']), len(idx_h.get('VS', ())), len(idx_h.get('PS', ())), len(idx_h.get('CS', ()))))
P('cls_b = (type, sh registers of the header in header order without offsets %s, all cx registers in header order); cls_a is not '
  'computable from the logs (see Q1)' % ', '.join(EXCL_SH))
D = {}
for tag, lv, exp in TAGS:
    D[tag] = scan(tag, lv)
P('')
P('== inputs')
for tag, lv, exp in TAGS:
    d = D[tag]
    P('%s %s: lines %d sha256 %s; entry line %s; %s; %s' % (tag, lv, d['lines'], d['sha'], d['ent'], d['tc'], (d['seed'] or '')[:118]))

# ---------------------------------------------------------------- Q1
P('')
P('== Q1: does every record of the predictor-B table carry specialization, class and moment in the log?')
P('   sites of the table (2b1b8787 pipelineCache.cpp:2057): resolve = startup precache (Resolve :4614), cache = lazy load at the first')
P('   use (LoadFromTranslationCache :2227, line "AvTrace: shader-cache load" :3656), compile = Compile (:3933, lines "AvTrace: shader-spec"')
P('   :4034 and "AvTrace: shader" :4042).  The only line that prints a specialization is :4034, on the compile site.')
q1_all = True
for tag, lv, exp in TAGS:
    d = D[tag]
    pre = d['pre']; nsh = len(d['sh']); nspec = len(d['spec'])
    # every "AvTrace: shader" line has its "shader-spec" line right before it (same hash and perm)
    paired = 0
    for x in d['sh']:
        s = d['spec'].get(x['line'] - 1)
        if s and s[1] == x['h'] and s[2] == x['perm']: paired += 1; x['spec'] = s[3]
        else: x['spec'] = None
    cls_ok = sum(1 for x in d['sh'] if any(r[0] < x['line'] for r in d['reg'].get(x['h'], ())))
    mom_ok = sum(1 for x in d['sh'] if x['host_lo'] is not None)
    nres = pre[5] if pre else None
    nload = len(d['loads']); pload = sum(p for _, _, p in d['loads'])
    ok = bool(pre) and nres == 0 and nload == 0 and paired == nsh
    q1_all &= ok
    P('%s: resolve: %s sources loaded (line %s, %s recipes) - lines per record with hash 0, with specialization 0, with a moment 0 '
      '(one summary line); cache: %d "shader-cache load" lines, %d permutations - specialization 0, moment field 0; '
      'compile: %d "AvTrace: shader" lines (%d before the entry), with the paired shader-spec line %d, with a registration of the '
      'hash before it (class cls_b) %d, with a host moment bracket from the preceding flip/register line %d; shader-spec lines %d '
      '(before the entry %d, after %d); shader-cache save %d -> every record carries all three: %s'
      % (tag, nres, pre[0] if pre else None, pre[1] if pre else None, nload, pload, nsh, d['sh_before'], paired, cls_ok, mom_ok,
         nspec, d['spec_before'], d['spec_after'], d['save'], 'YES' if ok else 'NO'))
tot_res = sum(D[t]['pre'][5] for t in COUNTED if D[t]['pre'])
tot_cmp = sum(len(D[t]['sh']) for t in COUNTED)
P('five counted arms: records of the table by site - resolve %d source loads without a per-record line, cache %d, compile %d; share of '
  'records without a specialization line %.4f' % (tot_res, sum(len(D[t]['loads']) for t in COUNTED), tot_cmp,
                                                 float(tot_res) / (tot_res + tot_cmp) if tot_res + tot_cmp else 0))
P('cls_a (registers + input semantics + user-data metadata): the line "ShaderRegister:" (pipelineCache.cpp:6380) prints the sh/cx registers '
  'only - input semantics and user-data metadata lines: 0 -> cls_a is not computable for any record')
P('Q1 ANSWER: %s' % ('YES - C_mod^spec is computed below' if q1_all else
  'NO -> C_mod^spec NOT COMPUTED (item 423(g)(1): phase A goes).  Missing lines [c]: (1) a per-record line of the Resolve site '
  '(startup precache: hash, key, specialization, moment) - the log has one summary line "PipelinePrecache: ... sources loaded"; '
  '(2) the specialization of a LoadFromTranslationCache record - "AvTrace: shader-cache load" prints hash, permutations and us only; '
  '(3) input semantics and user-data metadata of a registration (cls_a).  These are exactly the lines SEarlyKey src=resolve / src=cache '
  'and SEarlyReg cls_a of phase A.'))

# ---------------------------------------------------------------- series and weights
P('')
P('== series (runs of FrameTrace rows with skc_ap_skip > 0 or skc_held_inc > 0 after the entry line; a gap of 1 clean row joins) and weights')
P('   weight of a series = its contribution to the scorer sum of item 408(g): rows with skc_ap_skip > 0 and n > the first scene frame +')
P('   sum skc_held_inc of the rows with n >= it (the first scene frame n - field "first" of C:/kyty/s288/s10/runs_s/<tag>.score.json)')
SER = {}
w_ok = True
for tag, lv, exp in TAGS:
    d = D[tag]
    rows = [d['frames'][k] for k in d['order'] if d['frames'][k]['line'] > (d['ent'] or 0)]
    first = json.load(open('C:/kyty/s288/s10/runs_s/%s.score.json' % tag, encoding='utf-8'))['first'][0]
    wsk = lambda r, first=first: 1 if r['skip'] > 0 and r['n'] > first else 0
    whe = lambda r, first=first: r['held'] if r['n'] >= first else 0
    sk = sum(wsk(r) for r in rows); he = sum(whe(r) for r in rows)
    same = (sk, he) == exp
    w_ok &= same
    bursts = []; cur = None; gap = 0
    for i, r in enumerate(rows):
        hit = r['skip'] > 0 or r['held'] > 0
        if hit:
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
        if not x['after'] or x['n'] is None: continue
        for s in ser:
            if s['a'] <= x['n'] <= s['b']: s['mods'].append(x); x['ser'] = s
    SER[tag] = ser
    P('%s: rows after the entry %d, first scene frame n %d; skip rows %d held %d (fin_summary %d / %d: %s); series %s; new modules after '
      'the entry %d (VS/PS %d), inside a series %d' % (tag, len(rows), first, sk, he, exp[0], exp[1], 'EQUAL' if same else 'DIFFERS',
      [(s['a'], s['b'], 'w=%d' % s['w'], 'mods=%d' % len(s['mods'])) for s in ser], sum(1 for x in d['sh'] if x['after']),
      sum(1 for x in d['sh'] if x['after'] and x['st'] in TYPE_OF_STAGE), sum(len(s['mods']) for s in ser)))
P('weights equal the scorer rows of fin_summary on all arms: %s' % ('YES' if w_ok else 'NO'))

# ---------------------------------------------------------------- Q2 class non-empty bound
P('')
P('== Q2 (executor variant; NOT the C_mod^spec of the letter): C_mod^cls - the weight share of the series in which EVERY new VS/PS module')
P('   has a non-empty class before its registration.  Necessary for any prediction by class: C_mod <= C_mod^spec <= C_mod^cls(cls_b), and')
P('   cls_a refines cls_b, so C_mod^cls(cls_a) <= C_mod^cls(cls_b).  Generous on every unknown: the registration of the target = its LAST')
P('   one before the compile line; a class-mate counts if it is registered (line) before that one and either has a file of the stage in')
P('   snap0 (loaded or not - unknown from the log) or was compiled in the process before it.  Modes: "other" - a class-mate of another')
P('   hash (design 6.2: known=1 is not queued); "any" - or the same hash with another key in snap0; "sure" - a class-mate first-used')
P('   (ShaderFirstUse line) before the registration, i.e. certainly in the table (a lower side of "other").')
tot = dict(w=0, other=0, anym=0, sure=0)
mods_all = []
for tag, lv, exp in TAGS:
    d = D[tag]
    by_cls = collections.defaultdict(list)   # cls -> [(line, hash)]
    for h, rl in d['reg'].items():
        for ln, hu, typ, c in rl: by_cls[c].append((ln, h))
    compiled = collections.defaultdict(list)
    for x in d['sh']: compiled[(x['st'], x['h'])].append(x['line'])
    fu_line = {}
    for (h, stg), (ln, hu) in d['fu'].items(): fu_line.setdefault(h, ln); fu_line[h] = min(fu_line[h], ln)
    for s in SER[tag]:
        ok_o = ok_a = ok_s = True; nm = 0
        for x in s['mods']:
            if x['st'] not in TYPE_OF_STAGE: continue
            nm += 1
            typ = TYPE_OF_STAGE[x['st']]
            regs = [r for r in d['reg'].get(x['h'], ()) if r[0] < x['line'] and r[2] == typ]
            if not regs:
                x.update(e_other=False, e_any=False, e_sure=False, mates=0, mates_file=0, mates_sure=0, ncls=0, treg=None, lead=None)
                ok_o = ok_a = ok_s = False; mods_all.append((tag, s, x)); continue
            treg = max(r[0] for r in regs); classes = set(r[3] for r in regs)
            mates = set()
            for c in classes:
                for ln, h in by_cls[c]:
                    if ln < treg and h != x['h']: mates.add(h)
            m_file = set(h for h in mates if h in idx_h.get(x['st'], ()) or any(l < treg for l in compiled.get((x['st'], h), ())))
            m_sure = set(h for h in mates if h in fu_line and fu_line[h] < treg)
            same = x['h'] in idx_h.get(x['st'], ())
            x.update(e_other=bool(m_file), e_any=bool(m_file) or same, e_sure=bool(m_sure), mates=len(mates), mates_file=len(m_file),
                     mates_sure=len(m_sure), ncls=len(classes), treg=treg, same=same,
                     lead=(d['fu'].get((x['h'], 1 if x['st'] == 'VS' else 2), (None, None))[1]))
            ok_o &= x['e_other']; ok_a &= x['e_any']; ok_s &= x['e_sure']
            mods_all.append((tag, s, x))
        s.update(nm=nm, ok_o=ok_o, ok_a=ok_a, ok_s=ok_s)
        P('%s series n %d..%d weight %d: new VS/PS modules %d; class non-empty for all - other %s, any %s, sure %s'
          % (tag, s['a'], s['b'], s['w'], nm, ok_o, ok_a, ok_s))
        for x in s['mods']:
            if x['st'] not in TYPE_OF_STAGE: continue
            P('    %s %s perm %d line %d frame %s: classes of its registrations %d; class-mates of another hash registered earlier %d, of them '
              'with a snap0 file or compiled earlier %d, first-used earlier %d; same hash in snap0 (another key) %s'
              % (x['st'], x['h'], x['perm'], x['line'], x['n'], x['ncls'], x['mates'], x['mates_file'], x['mates_sure'], x.get('same')))
        if tag in COUNTED:
            tot['w'] += s['w']; tot['other'] += s['w'] if ok_o else 0; tot['anym'] += s['w'] if ok_a else 0; tot['sure'] += s['w'] if ok_s else 0
five = [(t, s, x) for t, s, x in mods_all if t in COUNTED]
P('five counted arms: series %d, weight %d; new VS/PS modules inside the series %d: class non-empty - other %d, any %d, sure %d; with 0 class-mates '
  'registered earlier %d' % (sum(len(SER[t]) for t in COUNTED), tot['w'], len(five), sum(1 for _, _, x in five if x['e_other']),
  sum(1 for _, _, x in five if x['e_any']), sum(1 for _, _, x in five if x['e_sure']), sum(1 for _, _, x in five if x['mates'] == 0)))
if tot['w']:
    co = float(tot['other']) / tot['w']; ca = float(tot['anym']) / tot['w']; cs = float(tot['sure']) / tot['w']
    P('C_mod^cls(cls_b): other %.4f (%d / %d), any %.4f (%d / %d); lower side "sure" %.4f (%d / %d)'
      % (co, tot['other'], tot['w'], ca, tot['anym'], tot['w'], cs, tot['sure'], tot['w']))
    if ca < THR:
        P('Q2 READING: C_mod^cls(any) < %.1f -> C_mod^spec < %.1f for cls_b and for cls_a by the chain of inequalities (a bound through a '
          'weaker necessary condition; the letter of item 423(g)(1) names C_mod^spec - a question to the lead)' % (THR, THR))
    elif co < THR:
        P('Q2 READING: C_mod^cls(other) < %.1f <= C_mod^cls(any): the bound kills only the predictor that never uses the same hash '
          '(design 6.2); with the same hash allowed it does not - no kill by this member' % THR)
    else:
        P('Q2 READING: C_mod^cls >= %.1f in both modes - the class is almost never empty; the condition does not bound C_mod from above '
          'below the threshold.  No kill by this member; says nothing about the keys' % THR)

# ---------------------------------------------------------------- input of the offline check RC5(b)
rows5 = ['tag\tlevel\tstage\thash\tin_snap0_index\tseries']
seen5 = set()
lvof = dict((t, l) for t, l, _ in TAGS)
for tag, s, x in mods_all:
    if tag not in COUNTED or (tag, x['st'], x['h']) in seen5: continue
    seen5.add((tag, x['st'], x['h']))
    rows5.append('\t'.join([tag, lvof[tag], x['st'], x['h'], '1' if x['h'] in idx_h.get(x['st'], ()) else '0', '%d..%d' % (s['a'], s['b'])]))
open(os.path.join(os.path.dirname(OUT), 'new_modules_s14d.tsv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rows5) + '\n')
P('')
P('== input of the offline check RC5(b): new_modules_s14d.tsv - distinct (arm, stage, hash) of the new VS/PS modules inside the series %d, '
  'of them with the hash present in the snap0 index under another key %d, absent %d' % (len(rows5) - 1,
  sum(1 for r in rows5[1:] if r.split('\t')[4] == '1'), sum(1 for r in rows5[1:] if r.split('\t')[4] == '0')))

# ---------------------------------------------------------------- ladder
P('')
P('== ladder (sensitivity of C_mod^cls to the composition of a register-only class; same rules as Q2, five counted arms)')
for name, fn in LADDER:
    w = wo = wa = 0; n_o = n_a = n_all = 0; pop = []
    for tag in COUNTED:
        d = D[tag]
        by = collections.defaultdict(list)
        for h, rl in d['reg'].items():
            for ln, hu, typ, c in rl: by[fn(c)].append((ln, h))
        compiled = collections.defaultdict(list)
        for x in d['sh']: compiled[(x['st'], x['h'])].append(x['line'])
        for typ in (1, 2):
            pop.append(len(set(k for k in by if k[0] == typ)))
        for s in SER[tag]:
            ok_o = ok_a = True
            for x in s['mods']:
                if x['st'] not in TYPE_OF_STAGE: continue
                typ = TYPE_OF_STAGE[x['st']]
                regs = [r for r in d['reg'].get(x['h'], ()) if r[0] < x['line'] and r[2] == typ]
                n_all += 1
                if not regs: ok_o = ok_a = False; continue
                treg = max(r[0] for r in regs); classes = set(fn(r[3]) for r in regs)
                mates = set(h for c in classes for ln, h in by[c] if ln < treg and h != x['h'])
                e_o = any(h in idx_h.get(x['st'], ()) or any(l < treg for l in compiled.get((x['st'], h), ())) for h in mates)
                e_a = e_o or x['h'] in idx_h.get(x['st'], ())
                n_o += e_o; n_a += e_a; ok_o &= e_o; ok_a &= e_a
            w += s['w']; wo += s['w'] if ok_o else 0; wa += s['w'] if ok_a else 0
    P('%s: classes per arm PS/VS %s; new VS/PS modules with a non-empty class - other %d of %d, any %d of %d; C_mod^cls other %.4f (%d / %d), '
      'any %.4f (%d / %d)' % (name, pop, n_o, n_all, n_a, n_all, float(wo) / w, wo, w, float(wa) / w, wa, w))

# ---------------------------------------------------------------- reference: homogeneity of the specialization inside a class
P('')
P('== reference (not a bound): specialization of the compile-observed records by class cls_b, all six logs')
recs = {}
for tag, lv, exp in TAGS:
    d = D[tag]
    for x in d['sh']:
        if x['st'] not in TYPE_OF_STAGE or not x.get('spec'): continue
        regs = [r for r in d['reg'].get(x['h'], ()) if r[0] < x['line'] and r[2] == TYPE_OF_STAGE[x['st']]]
        if not regs: continue
        c = max(regs)[3]
        recs.setdefault((x['st'], x['h'], x['spec']), c)
bych = collections.defaultdict(set); bycls = collections.defaultdict(set)
for (st, h, sp), c in recs.items():
    bych[(st, h)].add(sp); bycls[c].add((h, sp))
multi = dict((c, v) for c, v in bycls.items() if len(set(h for h, _ in v)) > 1)
P('distinct (stage, hash, specialization) records %d; distinct hashes %d, of them with more than one specialization %d; classes %d, classes '
  'with two or more hashes %d' % (len(recs), len(bych), sum(1 for v in bych.values() if len(v) > 1), len(bycls), len(multi)))
pairs = eq = 0
for c, v in multi.items():
    v = sorted(v)
    for i in range(len(v)):
        for j in range(i + 1, len(v)):
            if v[i][0] == v[j][0]: continue
            pairs += 1; eq += 1 if v[i][1] == v[j][1] else 0
    P('   class of type %d with hashes %s: distinct specializations %d' % (c[0], sorted(set(h for h, _ in v)), len(set(sp for _, sp in v))))
P('pairs of records of different hashes in one class %d, with equal specialization %d' % (pairs, eq))

# ---------------------------------------------------------------- classes overall
P('')
P('== reference: population of cls_b among the registrations (per arm)')
for tag, lv, exp in TAGS:
    d = D[tag]
    for typ, nm in ((1, 'PS'), (2, 'VS')):
        cl = collections.defaultdict(set)
        for h, rl in d['reg'].items():
            for ln, hu, t, c in rl:
                if t == typ: cl[c].add(h)
        sizes = sorted((len(v) for v in cl.values()), reverse=True)
        nh = len(set(h for v in cl.values() for h in v))
        P('%s type %d (%s): distinct hashes %d, classes %d, singleton classes %d, largest %s; hashes with a snap0 file of the stage %d'
          % (tag, typ, nm, nh, len(cl), sum(1 for x in sizes if x == 1), sizes[:5],
             sum(1 for h in set(h for v in cl.values() for h in v) if h in idx_h.get(nm, ()))))

# ---------------------------------------------------------------- Q3 PM4 lead
P('')
P('== Q3 (member 7): the PM4 lead "guest submit -> GuestGpu processing"')
P('   guest side: AgcDriverSubmitAcb prints "\\t acb   = " (2b1b8787 agc.cpp:4347) without a moment; the name header "[tid][time] lib::func()"')
P('   is printed for the libkernel functions only.  GuestGpu side: the lag "Enqueue -> first slice" exists in the code as the line "LagTrace:"')
P('   (graphicsRun.cpp:960) under KYTY_LAG_TRACE=1, lag >= 2000 us only; the counter da_wlag_us is the lag of the draw-ahead walk.')
for tag, lv, exp in TAGS:
    d = D[tag]
    agc = sum(v for k, v in d['hdr'].items() if re.search(r'[Aa]gc|[Ss]ubmit', k))
    P('%s: "acb =" lines %d; timed name headers %d kinds (%d lines), of them agc / submit %d; "LagTrace:" lines %d; FrameTrace-draw rows with '
      'da_wlag_us %d' % (tag, d['acb'], len(d['hdr']), sum(d['hdr'].values()), agc, d['lag'], d['wlag']))
lag_any = any(D[t]['lag'] for t, _, _ in TAGS)
P('Q3 ANSWER: %s' % ('computable - LagTrace lines present' if lag_any else
  'NOT COMPUTABLE from the S10 logs [c]: the guest submit line has no moment (no host_us, no timed header) and the GuestGpu side line '
  '"LagTrace:" is absent (KYTY_LAG_TRACE was not set in S10).  The form "by the PM4 lead" stays parked (item 423(g))'))

# ---------------------------------------------------------------- Q4 workers
P('')
P('== Q4 (member 5): the worker-count line of the asynchronous creation exists already (2b1b8787 pipelineCache.cpp:4825)')
for tag, lv, exp in TAGS:
    P('%s: AsyncPipelines: mode=%s workers=%s (line %s)' % ((tag,) + (D[tag]['workers'] or (None, None, None))))
P('')
P('wall %.1f s' % (time.time() - t0))
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
