# F21a (HPP-563, ROADMAP s122 item 462(zh)): merge of the sweep parts and the summary for B9 and for the witnesses of
# F3 / B26v / B26g.  Reads list_f21a.tsv, meta_f21a.jsonl, sweep_f21a.jsonl.p* of <dir>; writes sweep_all.jsonl (one
# record per path) and prints the summary (ASCII).  Measurement only.
#   distinct log  = one sha256 of the text (sha256_text for '.xz'); its tag json = the json of the first of its paths
#                   that has one
#   sample        = distinct logs of the eight course-line binaries (item 451(e)), any form, except: a fixture
#                   directory (every path has a component with 'fx'), no tag json (binary unknown), KYTY_FIX_B9A=0 in
#                   the env of the tag json.  FS6 (9325446c) is not installed - its logs are a separate line.
#   B9a set       = symbols of the library AudioPropagation_v1 (register section 17: 16 unresolved imports, F6a table)
#   saturated log = stub_lines >= 1024: the print is silent after 1024 calls per process (runtimeLinker.cpp:405), a
#                   zero of other names is not readable after the 1024th line
# Usage: python ana_f21a.py [dir]
import calendar, collections, glob, json, re, sys, time

D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f21a').rstrip('/') + '/'
TAB = chr(9)
RDK = 'r' + 'd'
COURSE = ['9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f']
B9A_DEFAULT_ON = ['bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f']
FS6 = '9325446c'
B9A_LIB = 'AudioPropagation_v1'
B9A16 = {'XKCN4gpeYsM': 'SystemUnregisterMaterial', 'VlBT16890mA': 'SystemSetRays', 'ZQXE-xS6MTE': 'PortalDestroy',
         '5vzOS2pHMFc': 'SourceSetAudioPaths', 'WXMhENV2NcA': 'PortalSetAttributes', 'b-dYXrjSNZU': 'PortalCreate',
         'S0JwP2AFTTE': 'RoomDestroy', 'x5VPqg5iyAk': 'SystemDestroy', 'd84otraxt2s': 'SourceCreate',
         '-wsUTr31yeg': 'SourceSetAttributes', 'aKJZx7wCma8': 'SourceGetRays', 'G+QLTfyLMYk': 'SourceGetAudioPathCount',
         'wkseM3LWPuc': 'SourceDestroy', 'hhz9pITnC8k': 'SourceRender', 'eEeKqFeNI3o': 'SourceGetAudioPath',
         'PBcrVpEqUVY': 'SourceCalculateAudioPaths'}
F3_37 = set('''06c29e2ccf89ce71 0b238107822b2137 0fd674b412730f37 0feb5b9bf0f8b349 230ae73860c0e217 33b57ee7c2815d43
40926493e8fda115 43d6a6fa21e811f7 49819ff3d8cf6f86 4c30c17701a2e4a1 57c4d5848e02ecdc 5a813991aa693677 5cd7ada004f6e1f7
6076621c96bb8e51 6128ac612db65f0f 62051a9a5b17f037 6231f9bb7f08d10c 6695669155ce8188 6a05ade1cdafab29 7378fe548d1a8a80
7ecb3bf6217e9a30 83643d26a1004a06 8a1d410d3cba3f08 92f9dd0d9be5c4f8 9895f6c0bb8e467c 995b65f5f7940958 a62a37f2455315c4
b2d06827515d177b bd3163e5cf418f11 c0f77151c2c0cecd c80fe4dc28c8e615 cb9abb6788229cce cfdceef703c56553 ee7048f4e20823c7
eeee030eca81d56b f37b3fc0c493045b fabc75e5191da1ce'''.split())
B26G = '57c4d5848e02ecdc'
B26V_PREFIX = ['433e4ced', 'f8e35038', '4468d530', '7bb50479']
HARNESS = {'KYTY_FRAME_TRACE', 'KYTY_GPU_HANG_ABORT_S', 'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_QUEUE_TRACE',
           'KYTY_GPU_CLOCK_PIN', 'KYTY_GPU_MARKERS', 'KYTY_GUEST_ARGS', 'KYTY_REC'}
F14A_DIRS = ['C:/kyty/s142', 'C:/kyty/s143', 'C:/kyty/s144', 'C:/kyty/s145', 'C:/kyty/s146', 'C:/kyty/f287/f13a',
             'C:/kyty/f287/fs4c', 'C:/kyty/f287/f12f']
F14A_CUTOFF = calendar.timegm(time.strptime('2026-10-03 16:34:59', '%Y-%m-%d %H:%M:%S'))
FXC = re.compile('/[^/]*fx[^/]*/')
C = collections.Counter


def P(*a):
    print(' '.join(str(x) for x in a))


def short(p):
    return p.replace('C:/kyty/', '')


def dirname(p):
    return p[:p.rfind('/')]


def basename(p):
    return p[p.rfind('/') + 1:]


# ---- merge
recs = {}
raw = rep = 0
for fn in sorted(glob.glob(D + 'sweep_f21a.jsonl.p*')):
    for l in open(fn, encoding='utf-8'):
        if not l.startswith('{'):
            continue
        raw += 1
        r = json.loads(l)
        if r['path'] in recs:
            assert recs[r['path']] == r, r['path']
            rep += 1
        recs[r['path']] = r
with open(D + 'sweep_all.jsonl', 'w', encoding='ascii', newline=chr(10)) as f:
    for p in sorted(recs):
        f.write(json.dumps(recs[p], ensure_ascii=True, sort_keys=True) + chr(10))
rows = [l.rstrip(chr(10)).split(TAB) for l in open(D + 'list_f21a.tsv', encoding='utf-8') if l.strip()]
mtime = {r[0]: int(r[2]) for r in rows}
meta = {}
for l in open(D + 'meta_f21a.jsonl', encoding='utf-8'):
    m = json.loads(l)
    meta[m['path']] = m
P('== 1. Scope')
P('list rows', len(rows), 'distinct paths', len(set(r[0] for r in rows)), 'repeated paths', len(rows) - len(set(r[0] for r in rows)))
P('sweep records raw', raw, 'paths', len(recs), 'repeated equal records', rep, 'paths of the list without a record',
  len([r for r in rows if r[0] not in recs]), 'missing files', sum(1 for r in recs.values() if r.get('missing')))
if len(recs) != len(rows) or any(r.get('missing') for r in recs.values()):
    P('SWEEP NOT COMPLETE')
    sys.exit(1)
P('bytes', sum(r['size'] for r in recs.values()), 'stored;', 'lines', sum(r['lines'] for r in recs.values()), 'FrameTrace lines',
  sum(r['ft_n'] for r in recs.values()), 'frame hours %.1f' % (sum(r['ft_us'] for r in recs.values()) / 3.6e9),
  'xz', sum(1 for r in recs.values() if r['xz']), 'xz_rc != 0', sum(1 for r in recs.values() if r['xz'] and r.get('xz_rc') != 0))

# ---- identities
bad = []
for p, r in recs.items():
    if r['stub_lines'] != sum(s['n'] for s in r['stub']) + r['stub_bad'] + r['stub_unparsed']:
        bad.append(('stub sum', p))
    if r['stub_idx_restart'] == 0 and r['stub_max_idx'] + 1 != r['stub_lines']:
        bad.append(('idx', p))
    if r['stub_idx_restart'] == 0 and r['stub_lines'] > 1024:
        bad.append(('cap', p))
    for s in r['stub']:
        if sum(s['levels'].values()) != s['n']:
            bad.append(('stub levels', p))
    if r['ft_n'] < sum(l['frames'] for l in r['levels']):
        bad.append(('frames', p))
    if r['xz'] and r.get('xz_rc') != 0:
        bad.append(('xz_rc', p))
P('identities: failures', len(bad), bad[:10], '-', 'IDENTITIES ALL OK' if not bad else 'IDENTITIES FAILED')
P('invariants over all records: stub_bad', sum(r['stub_bad'] for r in recs.values()), 'stub_unparsed',
  sum(r['stub_unparsed'] for r in recs.values()), 'stub_idx_restart', sum(r['stub_idx_restart'] for r in recs.values()),
  'stub_plain', sum(r['stub_plain'] for r in recs.values()), "'=== Stubbed function' lines", sum(r['sfn'] for r in recs.values()),
  'levels_over', sum(r['levels_over'] for r in recs.values()))
for p, r in sorted(recs.items()):
    if r['stub_idx_restart'] or r['stub_bad'] or r['stub_unparsed'] or r['stub_plain']:
        P('   ', short(p), 'restart', r['stub_idx_restart'], 'bad', r['stub_bad'], 'unparsed', r['stub_unparsed'], 'plain', r['stub_plain'],
          'stub_lines', r['stub_lines'], 'max_idx', r['stub_max_idx'])

# ---- distinct logs and classes
groups = collections.OrderedDict()
for p in sorted(recs):
    r = recs[p]
    groups.setdefault(r.get('sha256_text') or r['sha256'], []).append(p)
LOGS = []
b9a_values = C()
for sha, paths in groups.items():
    m = None
    for p in paths:
        if meta[p].get('binary_sha256'):
            m = meta[p]
            break
    b = m['binary_sha256'][:8] if m else None
    env = (m.get('env') or {}) if m else {}
    if all(FXC.search(p) for p in paths):
        cls = 'fixture dir'
    elif m is None:
        cls = 'no json'
    elif b == FS6:
        cls = 'FS6 not installed'
    elif b not in COURSE:
        cls = 'other binary'
    elif env.get('KYTY_FIX_B9A') == '0':
        cls = 'KYTY_FIX_B9A=0'
    else:
        cls = 'sample'
    if b in COURSE and 'KYTY_FIX_B9A' in env:
        b9a_values[(b, env['KYTY_FIX_B9A'])] += 1
    LOGS.append({'sha': sha, 'paths': paths, 'rec': recs[paths[0]], 'cls': cls, 'meta': m, 'bin': b or '-', 'env': env})
P()
P('== 2. Distinct logs and the sample')
P('distinct logs by sha256 of the text', len(LOGS), 'repeated copies', len(recs) - len(LOGS))
cl = C(L['cls'] for L in LOGS)
for k in ('other binary', 'no json', 'fixture dir', 'FS6 not installed', 'KYTY_FIX_B9A=0', 'sample'):
    P('   %-20s %d' % (k, cl.get(k, 0)))
P('KYTY_FIX_B9A values in the env of course-line logs (binary, value): ', dict(b9a_values))
S = [L for L in LOGS if L['cls'] == 'sample']
P('sample by binary:', ' '.join('%s %d' % (b, sum(1 for L in S if L['bin'] == b)) for b in COURSE))
P('sample forms: validation true', sum(1 for L in S if L['meta'].get('validation') == 'true'), '; RenderDoc flag', sum(1 for L in S if L['meta'].get(RDK)),
  '; --shader-validation true', sum(1 for L in S if L['meta'].get('shader_validation') == 'true'), '; cmd_extra',
  dict(C(' '.join(L['meta'].get('cmd_extra') or []) for L in S)))
ek = C()
for L in S:
    for k in L['env']:
        if k not in HARNESS:
            ek[k] += 1
P('sample env keys outside the harness constants (logs):', ' '.join('%s %d' % kv for kv in sorted(ek.items())))
P('sample: lines', sum(L['rec']['lines'] for L in S), 'FrameTrace lines', sum(L['rec']['ft_n'] for L in S),
  'frame hours %.1f' % (sum(L['rec']['ft_us'] for L in S) / 3.6e9), 'logs with --- Fatal Error ---', sum(1 for L in S if L['rec']['fatal']))


def stub_table(logs):
    agg = {}
    for L in logs:
        for s in L['rec']['stub']:
            a = agg.setdefault(s['symbol'], {'lib': s['lib'], 'nid': s['nid'], 'logs': 0, 'n': 0, 'levels': C(), 'bins': C(),
                                             'progs': set(), 'ex': None})
            a['logs'] += 1
            a['n'] += s['n']
            a['bins'][L['bin']] += 1
            a['progs'].add(s['program'])
            for k, v in s['levels'].items():
                a['levels'][k or '<before the first level line>'] += v
            if a['ex'] is None:
                a['ex'] = '%s:%d' % (short(L['paths'][0]), s['first_line'])
    return agg


def print_table(agg, only=None):
    n = 0
    for sym, a in sorted(agg.items(), key=lambda kv: (kv[1]['lib'], -kv[1]['n'])):
        inb9a = a['lib'] == B9A_LIB
        if only is not None and inb9a != only:
            continue
        n += 1
        name = (' = sceAudioPropagation' + B9A16[a['nid']]) if a['nid'] in B9A16 else (' (NOT in the 16 of F6a)' if inb9a else '')
        P('   %s%s | lib %s | program %s | logs %d | lines %d | binaries %s | levels %s | first %s' % (
            sym, name, a['lib'], ','.join(sorted(a['progs'])), a['logs'], a['n'],
            ' '.join('%s:%d' % kv for kv in sorted(a['bins'].items())),
            ' '.join('%s:%d' % kv for kv in sorted(a['levels'].items())), a['ex']))
    if n == 0:
        P('   (none)')
    return n


# ---- B9
P()
P('== 3. B9: lines "Unresolved import stub called [" in the sample')
aggS = stub_table(S)
with_stub = [L for L in S if L['rec']['stub_lines']]
P('sample logs', len(S), '; logs with >= 1 stub line', len(with_stub), '; stub lines', sum(L['rec']['stub_lines'] for L in S),
  '; distinct symbols', len(aggS), '; distinct libraries', len(set(a['lib'] for a in aggS.values())))
P('3.1 names OUTSIDE the B9a set (library != %s):' % B9A_LIB)
n_out = print_table(aggS, only=False)
P('    => symbols outside the B9a set: %d; libraries: %s' % (n_out, sorted(set(a['lib'] for a in aggS.values() if a['lib'] != B9A_LIB))))
P('3.2 the B9a set (library %s) - separate line:' % B9A_LIB)
print_table(aggS, only=True)
b9a_logs = [L for L in S if any(s['lib'] == B9A_LIB for s in L['rec']['stub'])]
P('    B9a logs', len(b9a_logs), 'by binary', dict(C(L['bin'] for L in b9a_logs)), 'lines',
  sum(s['n'] for L in b9a_logs for s in L['rec']['stub'] if s['lib'] == B9A_LIB))
for L in b9a_logs:
    P('      %s %s stub_lines %d levels %s validation %s' % (L['bin'], short(L['paths'][0]), L['rec']['stub_lines'],
      [x['level'] for x in L['rec']['levels']], L['meta'].get('validation')))
P('    B9a lines on binaries with the default KYTY_FIX_B9A=1 (%s): %d' % (' '.join(B9A_DEFAULT_ON),
  sum(s['n'] for L in b9a_logs if L['bin'] in B9A_DEFAULT_ON for s in L['rec']['stub'] if s['lib'] == B9A_LIB)))
sat = [L for L in S if L['rec']['stub_lines'] >= 1024]
P('3.3 saturated logs (stub_lines >= 1024):', len(sat), [short(L['paths'][0]) for L in sat])
P('3.4 other markers in the sample: Late-resolved import lines', sum(L['rec']['late_n'] for L in S), 'in logs',
  sum(1 for L in S if L['rec']['late_n']), '; === Stubbed function lines', sum(L['rec']['sfn'] for L in S))
late = C()
for L in S:
    for nm in L['rec']['late']:
        late[nm] += 1
if late:
    P('    late-resolved names (logs):', ' '.join('%s:%d' % kv for kv in late.most_common(20)))
armed = [L for L in S if L['rec']['rel_plt'] + L['rec']['rel_nonplt'] > 0]
P('3.5 positive control of arming: sample logs with >= 1 line "Relocate: unresolved ... patched to stub":', len(armed), 'of', len(S),
  '; PLT lines', sum(L['rec']['rel_plt'] for L in S), 'non-PLT lines', sum(L['rec']['rel_nonplt'] for L in S))
for L in S:
    if L not in armed:
        P('    not armed:', L['bin'], short(L['paths'][0]), 'lines', L['rec']['lines'], 'ft', L['rec']['ft_n'], 'levels', len(L['rec']['levels']))
libs = {}
for L in S:
    for lib, v in L['rec']['rel_libs'].items():
        a = libs.setdefault(lib, [0, 0, 0, 0])
        a[0] += 1
        a[1] = max(a[1], v[2])
        a[2] += v[0]
        a[3] += v[1]
P('    libraries with stubbed imports (logs / max distinct symbols in a log / PLT lines / non-PLT lines):')
for lib, a in sorted(libs.items()):
    called = sum(1 for x in aggS.values() if x['lib'] == lib)
    P('      %-28s %4d / %3d / %6d / %6d ; symbols called in the sample: %d' % (lib, a[0], a[1], a[2], a[3], called))
prof = C(tuple(sorted((lib, v[2]) for lib, v in L['rec']['rel_libs'].items())) for L in armed)
top = prof.most_common(1)
P('    distinct profiles (library, symbols) of the stubbed imports over the armed logs:', len(prof), '; the most frequent covers',
  top[0][1] if top else 0, 'logs; stubbed symbols in it', sum(n for _, n in top[0][0]) if top else 0)
P('    FixB9a: lines - sample logs with >= 1 by binary:', dict(C(L['bin'] for L in S if L['rec']['b9a_n'])), '; texts',
  dict(C(L['rec']['b9a_first'] for L in S if L['rec']['b9a_n'])))

# ---- levels
P()
P('== 4. Levels with the line "Level has started: <name>" in the sample')
lv = {}
for L in S:
    issat = L['rec']['stub_lines'] >= 1024
    for x in L['rec']['levels']:
        a = lv.setdefault(x['level'], {'logs': set(), 'ns_logs': set(), 'frames': 0, 'us': 0, 'ns_frames': 0, 'ns_us': 0, 'bins': set(), 'max_us': 0})
        a['logs'].add(L['sha'])
        a['frames'] += x['frames']
        a['us'] += x['sum_us']
        a['bins'].add(L['bin'])
        a['max_us'] = max(a['max_us'], x['sum_us'])
        if not issat:
            a['ns_logs'].add(L['sha'])
            a['ns_frames'] += x['frames']
            a['ns_us'] += x['sum_us']
P('(a) distinct levels in the sample (the letter of item 462(zh)):', len(lv))
P('(b) distinct levels in the logs that are not saturated:', sum(1 for a in lv.values() if a['ns_logs']))
P('(c) of (b), with >= 1 frame after the level line:', sum(1 for a in lv.values() if a['ns_frames'] > 0))
P('(d) of (b), with >= 120 s of frames in total:', sum(1 for a in lv.values() if a['ns_us'] >= 120e6), '; with >= 300 s:',
  sum(1 for a in lv.values() if a['ns_us'] >= 300e6), '; with one log holding >= 300 s (any log):', sum(1 for a in lv.values() if a['max_us'] >= 300e6))
P('logs of the sample without a named level line:', sum(1 for L in S if not L['rec']['levels']), '; empty level lines', sum(L['rec']['lvl_empty'] for L in S))
P('level | logs | logs not saturated | frames | seconds | seconds not saturated | binaries')
for name, a in sorted(lv.items()):
    P('   %-34s %3d %3d %8d %8.1f %8.1f  %s' % (name, len(a['logs']), len(a['ns_logs']), a['frames'], a['us'] / 1e6, a['ns_us'] / 1e6, ' '.join(sorted(a['bins']))))

# ---- context outside the sample
P()
P('== 5. Context outside the sample (not the sample; positive control of the marker)')
for cls in ('KYTY_FIX_B9A=0', 'FS6 not installed', 'other binary', 'no json', 'fixture dir'):
    G = [L for L in LOGS if L['cls'] == cls]
    agg = stub_table(G)
    P('%s: logs %d; with stub lines %d; stub lines %d; saturated %d; symbols %d; outside the B9a set %d' % (
        cls, len(G), sum(1 for L in G if L['rec']['stub_lines']), sum(L['rec']['stub_lines'] for L in G),
        sum(1 for L in G if L['rec']['stub_lines'] >= 1024), len(agg), sum(1 for a in agg.values() if a['lib'] != B9A_LIB)))
    if any(a['lib'] != B9A_LIB for a in agg.values()):
        print_table(agg, only=False)
    if cls == 'KYTY_FIX_B9A=0':
        for L in G:
            P('      %s %s stub_lines %d symbols %s' % (L['bin'], short(L['paths'][0]), L['rec']['stub_lines'],
              ' '.join('%s:%d' % (s['nid'], s['n']) for s in L['rec']['stub'])))
allagg = stub_table(LOGS)
P('all %d distinct logs: symbols called %d; outside the B9a set %d' % (len(LOGS), len(allagg), sum(1 for a in allagg.values() if a['lib'] != B9A_LIB)))

# ---- witnesses
P()
P('== 6. Witnesses of F3, B26v, B26g')


def restrack(c):
    return c in ('RESTRACK', 'RESTRACK_GBR1')


union = {}
for L in LOGS:
    for h, c in L['rec']['cs_skipped'].items():
        union.setdefault(h, C())[c] += 1
tgt_sweep = set(h for h, cc in union.items() if any(restrack(c) or c == 'BUDGET' for c in cc))
P('F3 target: 37 hashes of f14a_f3_hashes.tsv; union of RESTRACK + BUDGET over all swept logs', len(tgt_sweep), '; not in the 37:',
  sorted(tgt_sweep - F3_37), '; of the 37 not seen as skipped:', sorted(F3_37 - set(union)))
TGT = F3_37 | tgt_sweep
b26v = {}
for pref in B26V_PREFIX:
    full = sorted(h for h in union if h.startswith(pref))
    b26v[pref] = full
    P('B26v prefix', pref, '-> full', full, 'classes', dict(union[full[0]]) if full else {})
B26V = set(h for v in b26v.values() for h in v)
P('B26g', B26G, 'classes', dict(union.get(B26G, {})))
for title, G in (('sample', S), ('all distinct logs', LOGS)):
    arm = [L for L in G if L['rec']['cs_skipped']]
    rq = [L for L in G if L['rec']['cs_req']]
    lines_rq = sum(v[0] + v[1] for L in G for v in L['rec']['cs_req'].values())
    P('%s: logs %d; armed (>= 1 line "CsPretranslate: skipped") %d; control - logs with >= 1 miss|hit line of any hash %d, lines %d (miss %d, hit %d), distinct hashes %d' % (
        title, len(G), len(arm), len(rq), lines_rq, sum(v[0] for L in G for v in L['rec']['cs_req'].values()),
        sum(v[1] for L in G for v in L['rec']['cs_req'].values()), len(set(h for L in G for h in L['rec']['cs_req']))))
    P('   profile (RESTRACK incl. GBR1, BUDGET) of the armed logs:', dict(C((sum(1 for c in L['rec']['cs_skipped'].values() if restrack(c)),
      sum(1 for c in L['rec']['cs_skipped'].values() if c == 'BUDGET')) for L in arm)))
    for name, hs in (('F3 (37 + union)', TGT), ('B26v', B26V), ('B26g', {B26G})):
        w = [(L, h, L['rec']['cs_req'][h]) for L in G for h in L['rec']['cs_req'] if h in hs]
        P('   %s: miss|hit lines with these hashes: %d in %d logs' % (name, sum(v[0] + v[1] for _, _, v in w), len(set(L['sha'] for L, _, _ in w))))
        for L, h, v in w[:20]:
            P('      WITNESS %s %s:%d hash %s miss %d hit %d reason %s' % (L['bin'], short(L['paths'][0]), v[2], h, v[0], v[1], v[3]))
    co = [L for L in G if L['rec']['cfg_out']]
    P("   'shader CFG build failed' outside a 'CsPretranslate:' line: %d lines in %d logs" % (sum(L['rec']['cfg_out'] for L in G), len(co)))
    for L in co[:20]:
        P('      WITNESS %s %s:%s %s' % (L['bin'], short(L['paths'][0]), L['rec']['cfg_out_first'][0], L['rec']['cfg_out_first'][1][:150]))
    na = [L for L in G if not L['rec']['cs_skipped']]
    P('   not armed (0 skipped lines): %d logs; by class/binary %s; with KYTY_CS_PRETRANSLATE in env %d' % (len(na),
      dict(C((L['cls'], L['bin']) for L in na).most_common(12)), sum(1 for L in na if 'KYTY_CS_PRETRANSLATE' in L['env'])))
P('sample by binary: armed logs / logs with miss|hit / B26v class')
for b in COURSE:
    G = [L for L in S if L['bin'] == b]
    cls = C(L['rec']['cs_skipped'].get(h) for L in G for h in B26V if h in L['rec']['cs_skipped'])
    P('   %s logs %d armed %d with miss|hit %d ; classes of the 4 B26v hashes %s ; class of B26g %s' % (b, len(G),
      sum(1 for L in G if L['rec']['cs_skipped']), sum(1 for L in G if L['rec']['cs_req']), dict(cls),
      dict(C(L['rec']['cs_skipped'].get(B26G) for L in G if B26G in L['rec']['cs_skipped']))))

# ---- regression against F14a
P()
P('== 7. Regression against f14a_f3.py (162 logs: 0 normal-path lines, control 343 lines in 23 logs, 37 hashes, 20 logs without skipped)')
F = [p for p in recs if dirname(p) in F14A_DIRS and basename(p).startswith('log_') and mtime[p] < F14A_CUTOFF]
u = set()
for p in F:
    for h, c in recs[p]['cs_skipped'].items():
        if restrack(c) or c == 'BUDGET':
            u.add(h)
got = (len(F), sum(v[0] + v[1] for p in F for h, v in recs[p]['cs_req'].items() if h in u),
       sum(v[0] + v[1] for p in F for v in recs[p]['cs_req'].values()), sum(1 for p in F if recs[p]['cs_req']), len(u),
       sum(1 for p in F if not recs[p]['cs_skipped']), sum(recs[p]['cfg_out'] for p in F))
P('paths %d; target lines %d; control lines %d in %d logs; target hashes %d; logs without skipped %d; cfg_out %d' % got)
P('REGRESS F14A OK' if got == (162, 0, 343, 23, 37, 20, 0) and u == F3_37 else 'REGRESS F14A DIFFERS')
