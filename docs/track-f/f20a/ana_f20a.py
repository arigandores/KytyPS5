# F20a (HPP-551, ROADMAP s122 item 451(e)): the sample, B2 and B32 from the sweep records.
# Reads list_f20a.tsv, meta_f20a.jsonl, sweep_all.jsonl (merge_f20a.py); prints the tables of the report.
# Sample classes of a log (unique by sha256):
#   strict - binary of the course line (item 451(e)), no validation, no RenderDoc, the env of the tag json holds only
#            the harness constants HARN, input KYTY_KEYS and knobs whose value equals the binary's own default (DEF);
#            no stand line in the header (TestMinimize / GamePatch applied / PVar armed)
#   wide   - strict + the trace / cache-state knobs of track S (SOFT)
#   out    - everything else, with the first reason
# RC1 (review of the lead, HPP-551): the emulator flag '--shader-validation true' (the LAST occurrence in the cmdline of
# the tag json, field shader_validation of meta_f20a.py) runs the built-in SPIR-V check on every new translation, i.e. on
# the frames with a translation dump - a knob that changes the frame time.  Two variants of the sample:
#   nosval - (main) a log with the flag true is out, reason 'flag --shader-validation true'
#   asis   - (reference) as submitted in 0a9adb84: the flag is not read
# Every section heading carries the variant in brackets.  '--classes' prints one 'CLASS' line per unique log.
# Usage: python ana_f20a.py [dir] [nosval|asis] [--classes]
import collections, glob, json, math, os, re, sys

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
D = (ARGS[0] if ARGS else 'C:/kyty/f287/f20a').rstrip('/') + '/'
VARIANT = ARGS[1] if len(ARGS) > 1 else 'nosval'
assert VARIANT in ('nosval', 'asis'), VARIANT
V = '[%s] ' % VARIANT
SVAL = 'flag --shader-validation true'
TAB = chr(9)
COURSE = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f')
SG, INTRO = 'underwater_aerial_garden', 'intro_next'
HARN = {'KYTY_FRAME_TRACE', 'KYTY_GPU_HANG_ABORT_S', 'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_QUEUE_TRACE', 'KYTY_GPU_CLOCK_PIN',
        'KYTY_GPU_MARKERS', 'KYTY_GUEST_ARGS', 'KYTY_REC'}
INPUT = {'KYTY_KEYS'}
SOFT = {'KYTY_AV_TRACE', 'KYTY_SHADER_REGISTER_TRACE', 'KYTY_CACHE_MODE', 'KYTY_SHADER_SEED_PATH', 'KYTY_PIPELINE_SALT'}
d0 = {'KYTY_FIX_B26': '1', 'KYTY_FIX_B1B': '1', 'KYTY_FIX_DUALSRC': '1', 'KYTY_FIX_MINIMIZE': '0', 'KYTY_S_PCW': '0', 'KYTY_S_PCW_FORCE_MS': '0'}
d1 = dict(d0, KYTY_FIX_MINIMIZE='1', KYTY_FIX_B9A='1')
d2 = dict(d1, KYTY_PVAR='0')
d3 = dict(d2, KYTY_FIX_B42='1')
d4 = dict(d3, KYTY_FIX_SVAL='1')
d5 = dict(d4, KYTY_FIX_F10='1')
d6 = dict(d5, KYTY_S_PCW='1')
DEF = {'9235a7ac': {}, 'dac02fb9': d0, 'bbad499c': d1, '4aa62e95': d2, '540c035a': d3, '31cbfee8': d4, '631ff987': d5, 'adb0c82f': d6}
FXDIR = re.compile(r'/[^/]*fx[^/]*/')
STAND_HEAD = ('TestMinimize: config on', 'GamePatch: applied', 'PVar: armed', 'TestHidLoss: config on', 'TestAudioLoss:', 'MainStallTest',
              'PrepareHold')

rows = [l.rstrip(chr(10)).split(TAB) for l in open(D + 'list_f20a.tsv', encoding='utf-8') if l.strip()]
meta = {}
for l in open(D + 'meta_f20a.jsonl', encoding='utf-8'):
    r = json.loads(l)
    meta[r['path']] = r
recs = {}
for fn in [D + 'sweep_all.jsonl']:
    for l in open(fn, encoding='utf-8'):
        if l.startswith('{'):
            r = json.loads(l)
            recs[r['path']] = r
paths = [r[0] for r in rows]


def tag(p):
    return p.replace('C:/kyty/', '')


def cp(k, n, lo=True):
    # Clopper-Pearson bound of a binomial proportion, two-sided 95 %
    if n == 0:
        return float('nan')
    if (lo and k == 0):
        return 0.0
    if (not lo and k == n):
        return 1.0
    a = 0.025

    def cdf(p, kk):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, kk + 1))
    x, y = 0.0, 1.0
    for _ in range(60):
        m = (x + y) / 2
        if lo:
            if 1 - cdf(m, k - 1) < a:
                x = m
            else:
                y = m
        else:
            if cdf(m, k) > a:
                x = m
            else:
                y = m
    return (x + y) / 2


print(V + '(0) LIST')
print('  rows', len(rows), 'distinct paths', len(set(paths)), 'records', len(recs), 'missing', sum(1 for p in paths if recs[p].get('missing')))
roots = collections.OrderedDict()
for p, s, mt, root, js in rows:
    roots.setdefault(root, [0, 0])
    roots[root][0] += 1
    roots[root][1] += int(s)
print('  roots', len(roots), ':', ' '.join('%s:%d' % (k.replace('C:/kyty/', ''), v[0]) for k, v in roots.items()))
by_sha = collections.OrderedDict()
for p in sorted(paths, key=lambda p: ('/lead/' in p or FXDIR.search(p) is not None or '/old/' in p, re.search(r'_a\d+\.txt', p) is not None, len(p), p)):
    by_sha.setdefault(recs[p]['sha256'], []).append(p)
texts = set(recs[p].get('sha256_text') or recs[p]['sha256'] for p in paths)
print('  distinct sha256 (stored file)', len(by_sha), '; distinct sha256 of the text (xz unpacked)', len(texts), '; repeated copies', len(paths) - len(by_sha))
print('  bytes', sum(int(r[1]) for r in rows), 'lines', sum(recs[p]['lines'] for p in paths), 'frames', sum(recs[p]['ft_n'] for p in paths),
      'frame time h %.1f' % (sum(recs[p]['ft_us'] for p in paths) / 3.6e9))
uniq = [v[0] for v in by_sha.values()]
print('  directories with fx in a path component (fixtures, out of the sample):', sorted(set(FXDIR.search(p).group(0) for p in paths if FXDIR.search(p))))


def classify(p):
    m, r = meta[p], recs[p]
    b = (m['binary_sha256'] or '')[:8]
    if FXDIR.search(p):
        return 'out', 'fixture directory (synthetic log)'
    if not b:
        return 'out', 'no tag json (binary unknown)'
    if b not in COURSE:
        return 'out', 'binary not of the course line'
    if m['validation'] != 'false' or r['cnt']['vk'] >= 100:
        return 'out', 'validation'
    if m['rd']:
        return 'out', 'RenderDoc'
    if VARIANT == 'nosval' and m.get('shader_validation') == 'true':
        return 'out', SVAL
    env = m['env'] or {}
    soft = False
    for k in sorted(env):
        if k in HARN or k in INPUT:
            continue
        if k in DEF[b] and env[k] == DEF[b][k]:
            continue
        if k in SOFT:
            soft = True
            continue
        return 'out', 'knob ' + k + ('=' + env[k] if len(env[k]) < 12 else '')
    for h in r['head']:
        if h.startswith(STAND_HEAD):
            return 'out', 'stand line in the header: ' + h[:24]
    if any(h.startswith('Gate') for h in r['head']) or r['cnt']['gatearm']:
        return 'out', 'gate line in the header'
    return ('wide' if soft else 'strict'), ''


cls = {p: classify(p) for p in uniq}
print()
print(V + '(1) EXCLUSION CASCADE (unique logs by sha256: %d)' % len(uniq))
c = collections.Counter()
for p in uniq:
    k, why = cls[p]
    c[k if k != 'out' else 'out: ' + (why if not why.startswith('knob') else 'knob')] += 1
for k, v in c.most_common():
    print('  %4d %s' % (v, k))
print('  knobs that put a log of a course binary (no validation, no RenderDoc) out, first knob in name order:')
kc = collections.Counter(cls[p][1] for p in uniq if cls[p][1].startswith('knob') or cls[p][1].startswith('stand') or cls[p][1].startswith('gate'))
for k, v in sorted(kc.items()):
    print('    %3d %s' % (v, k))
print('  env keys of the logs of course binaries without validation and RenderDoc (unique logs), class and count:')
ek = collections.Counter()
ncb = 0
for p in uniq:
    m = meta[p]
    b = (m['binary_sha256'] or '')[:8]
    if b in COURSE and m['validation'] == 'false' and not m['rd'] and not FXDIR.search(p):
        ncb += 1
        for k, v in (m['env'] or {}).items():
            kl = 'harness' if k in HARN else 'input' if k in INPUT else 'soft (wide only)' if k in SOFT else \
                ('default of the binary' if (k in DEF[b] and v == DEF[b][k]) else 'OUT')
            ek[(k, kl)] += 1
print('    logs', ncb)
for (k, kl), v in sorted(ek.items()):
    print('    %-34s %-22s %d' % (k, kl, v))
print()
print(V + '(1a) FLAG --shader-validation true (the last occurrence in the cmdline of the tag json)')
sv = [p for p in uniq if meta[p].get('shader_validation') == 'true']
svc = [p for p in sv if (meta[p]['binary_sha256'] or '')[:8] in COURSE and meta[p]['validation'] == 'false' and not meta[p]['rd'] and not FXDIR.search(p)]
print('  unique logs with the flag true: %d; of them on course binaries without validation, RenderDoc and fixtures: %d' % (len(sv), len(svc)))
for p in sorted(svc):
    print('    %s %s class %s %s levels %s' % (tag(p), meta[p]['binary_sha256'][:8], cls[p][0], cls[p][1] or '-', [s['level'] for s in recs[p]['scenes']]))
nsv = sum(1 for p in uniq if cls[p][0] != 'out' and meta[p].get('shader_validation') == 'true')
print('  logs of the sample (strict or wide) with the flag true: %d' % nsv)
assert VARIANT != 'nosval' or nsv == 0, nsv
if '--classes' in sys.argv:
    for p in sorted(uniq):
        print('CLASS' + TAB + p + TAB + cls[p][0] + TAB + (cls[p][1] or '-'))


def scenes_of(p, level):
    return [(i, s) for i, s in enumerate(recs[p]['scenes']) if s['level'] == level and s['first_n'] is not None]


def attr(x, b):
    # item 451(e): the interval of the frame
    if x['pcs']:
        return 'B33' if b != 'adb0c82f' else 'pcs on adb0c82f'
    if x['trip']:
        return 'B1b'
    if x['ir'] or x['gcn']:
        return 'B5'
    if x['prio']:
        return 'prio only'
    return 'nothing [U]'


def marks(x):
    return 'il %d io %d pcs %d/%d trip %d prio %d/%d ir %d gcn %d skip %d cs %d mtl %d win %d%s' % (
        x['il'], x['io'], x['pcs'], x['pcs_us'], x['trip'], x['prio'], x['prio_us'], x['ir'], x['gcn'], x['skip'], x['cs'], x['mtl'], x['win'],
        ' CUT' if x['cut'] else '')


print()
print(V + '(2) SAMPLE LOGS (strict and wide; every Sky Garden / intro_next scene with a first scene frame)')
print('  class | log | binary | copies | level | first_n | last_n | scene s | hold s | frames | k100 window / hold | k1s w/h | max w/h us | slow rows over')
sample = [p for p in uniq if cls[p][0] in ('strict', 'wide')]
other = collections.Counter()
for p in sorted(sample, key=lambda p: (cls[p][0], COURSE.index(meta[p]['binary_sha256'][:8]), p)):
    r = recs[p]
    lv = [s['level'] for s in r['scenes']]
    sc = scenes_of(p, SG) + scenes_of(p, INTRO)
    if not sc:
        other[cls[p][0]] += 1
        continue
    for i, s in sc:
        print('  %s | %s | %s | %d | %s | %d | %s | %.1f | %.1f | %d | %d / %d | %d/%d | %d/%d | %d' % (
            cls[p][0], tag(p), meta[p]['binary_sha256'][:8], len(by_sha[r['sha256']]), s['level'], s['first_n'], s['last_n'], s['sum_us'] / 1e6,
            s['sum_h'] / 1e6, s['frames'], s['k100_w'], s['k100_h'], s['k1s_w'], s['k1s_h'], s['max_w'], s['max_h'], r['slow_over']))
    env = {k: v for k, v in (meta[p]['env'] or {}).items() if k not in HARN}
    if env:
        print('        env beyond the harness constants:', {k: v[:50] for k, v in env.items()})

print('  sample logs without a scene of the two (other levels by -lvl):', dict(other))

for which in ('strict', 'wide'):
    S = [p for p in uniq if cls[p][0] == 'strict' or (which == 'wide' and cls[p][0] == 'wide')]
    print()
    print(V + '(3) B2, sample %s: Sky Garden entries with first_n < 900 and last_n >= 1100; frames dt >= 100 ms with n 900..1000' % which)
    ent = []
    for p in S:
        for i, s in scenes_of(p, SG):
            if s['first_n'] < 900 and s['last_n'] is not None and s['last_n'] >= 1100:
                hits = [x for x in recs[p]['slow'] if x['scene'] == i and x['q'] == 0 and 900 <= x['n'] <= 1000]
                ent.append((p, s, hits))
    k = sum(1 for e in ent if e[2])
    n = len(ent)
    print('  entries N = %d; entries with >= 1 frame: %d; frames: %d' % (n, k, sum(len(e[2]) for e in ent)))
    if n:
        print('  p = %d/%d = %.3f, 95 %% interval (Clopper-Pearson) [%.3f; %.3f]' % (k, n, k / n, cp(k, n, True), cp(k, n, False)))
    print('  by binary:', dict(collections.Counter(meta[e[0]]['binary_sha256'][:8] for e in ent)))
    print('  first_n of the entries:', sorted(e[1]['first_n'] for e in ent))
    for p, s, hits in ent:
        for x in hits:
            print('    HIT', tag(p), meta[p]['binary_sha256'][:8], 'n', x['n'], 'dt_us', x['dt_us'], 'idx', x['idx'], 't_before %.2f s' % (x['t_before_us'] / 1e6), '|', marks(x),
                  '|', attr(x, meta[p]['binary_sha256'][:8]), '| top', [(a[:40], b) for a, b in x['top'][:5]])
    print('  slow_over of these logs:', sum(recs[e[0]]['slow_over'] for e in ent))
    for level in (SG, INTRO):
        print()
        print(V + '(4) B32, sample %s, %s: holds with scene time >= 300 s; frames dt >= 100 ms that START at or after 10 s of scene time' % (which, level))
        H = []
        for p in S:
            for i, s in scenes_of(p, level):
                if s['sum_us'] >= 300000000:
                    hs = [x for x in recs[p]['slow'] if x['scene'] == i and x['q'] == 0 and x['t_before_us'] >= 10000000]
                    assert len(hs) == s['k100_h'] or recs[p]['slow_over'], (p, len(hs), s['k100_h'])
                    H.append((p, s, hs))
        n = len(H)
        print('  holds N = %d; by binary: %s' % (n, dict(collections.Counter(meta[e[0]]['binary_sha256'][:8] for e in H))))
        ac = collections.Counter()
        hold_un = 0
        hold_prio = 0
        hold_any = 0
        for p, s, hs in H:
            b = meta[p]['binary_sha256'][:8]
            kinds = [attr(x, b) for x in hs]
            ac.update(kinds)
            hold_any += bool(hs)
            hold_un += any(k in ('nothing [U]', 'pcs on adb0c82f') for k in kinds)
            hold_prio += any(k in ('nothing [U]', 'pcs on adb0c82f', 'prio only') for k in kinds)
            for x in hs:
                print('    FRAME', tag(p), b, 'n', x['n'], 'dt_us', x['dt_us'], 't_before %.1f s' % (x['t_before_us'] / 1e6), 'draws', x['draws'], '|', marks(x), '|', attr(x, b),
                      '| top', [(a[:40], bb) for a, bb in x['top'][:4]])
        print('  frames by attribution:', dict(ac))
        if n:
            print('  holds with >= 1 frame: %d of %d' % (hold_any, n))
            print('  holds with >= 1 frame WITHOUT attribution (nothing): %d of %d, p = %.3f [%.3f; %.3f]' % (hold_un, n, hold_un / n, cp(hold_un, n, True), cp(hold_un, n, False)))
            print('  holds with >= 1 frame without attribution or with PriorityStall only: %d of %d, p = %.3f [%.3f; %.3f]' % (
                hold_prio, n, hold_prio / n, cp(hold_prio, n, True), cp(hold_prio, n, False)))
            print('  hold time of these holds, s: %.1f' % (sum(e[1]['sum_h'] for e in H) / 1e6))
        # frames that straddle the 10 s border
        st = [(p, x) for p in S for i, s in scenes_of(p, level) for x in recs[p]['slow']
              if x['scene'] == i and x['q'] == 0 and x['t_before_us'] < 10000000 < x['t_before_us'] + x['dt_us']]
        print('  frames that start inside the window and end after 10 s:', [(tag(p), x['n'], x['dt_us']) for p, x in st])

print()
print(V + '(5) CONTEXT, not the sample: every other unique log with a Sky Garden scene (first_n < 900, last_n >= 1100) - B2 window n 900..1000')
ctx = collections.OrderedDict()
for p in uniq:
    if cls[p][0] != 'out':
        continue
    b = (meta[p]['binary_sha256'] or 'none')[:8]
    why = cls[p][1]
    grp = 'course binary, ' + ('validation' if why == 'validation' else 'RenderDoc' if why == 'RenderDoc' else '--shader-validation true' if why == SVAL else 'knob / stand') if b in COURSE else 'other binary' if b != 'none' else 'no json'
    if FXDIR.search(p):
        continue
    for i, s in scenes_of(p, SG):
        if s['first_n'] < 900 and s['last_n'] is not None and s['last_n'] >= 1100:
            hits = [x for x in recs[p]['slow'] if x['scene'] == i and x['q'] == 0 and 900 <= x['n'] <= 1000]
            ctx.setdefault(grp, []).append((p, b, s, hits))
for g, L in ctx.items():
    k = sum(1 for e in L if e[3])
    print('  %s: entries %d, with a frame %d' % (g, len(L), k))
    for p, b, s, hits in L:
        for x in hits:
            print('      ', tag(p), b, 'first_n', s['first_n'], 'n', x['n'], 'dt_us', x['dt_us'], 'idx', x['idx'], '|', marks(x), '|', attr(x, b))
print()
print(V + '(6) CONTEXT: holds >= 300 s of the two scenes in the logs OUT of the sample, by group; hold frames >= 100 ms by attribution')
for level in (SG, INTRO):
    g = collections.OrderedDict()
    for p in uniq:
        if cls[p][0] != 'out' or FXDIR.search(p):
            continue
        b = (meta[p]['binary_sha256'] or 'none')[:8]
        why = cls[p][1]
        grp = ('course binary, ' + ('validation' if why == 'validation' else 'RenderDoc' if why == 'RenderDoc' else '--shader-validation true' if why == SVAL else 'knob / stand')) if b in COURSE else 'other binary' if b != 'none' else 'no json'
        for i, s in scenes_of(p, level):
            if s['sum_us'] >= 300000000:
                hs = [x for x in recs[p]['slow'] if x['scene'] == i and x['q'] == 0 and x['t_before_us'] >= 10000000]
                e = g.setdefault(grp, [0, 0, collections.Counter(), s['k100_h'] * 0])
                e[0] += 1
                e[1] += bool(s['k100_h'])
                e[2].update(attr(x, b) for x in hs)
    print('  %s:' % level, {k: (v[0], v[1], dict(v[2])) for k, v in g.items()} or 'no hold >= 300 s')
print('  intro_next scenes with a first scene frame in ALL unique logs:', sum(len(scenes_of(p, INTRO)) for p in uniq),
      '; of them on course binaries:', sum(len(scenes_of(p, INTRO)) for p in uniq if (meta[p]['binary_sha256'] or '')[:8] in COURSE),
      '; the longest scene time, s: %.1f' % (max([s['sum_us'] for p in uniq for i, s in scenes_of(p, INTRO)] or [0]) / 1e6))
print('  levels of the logs of course binaries without -lvl in the guest args:', collections.Counter(
    str(meta[p]['guest_args']) for p in uniq if (meta[p]['binary_sha256'] or '')[:8] in COURSE and '-lvl' not in (meta[p]['guest_args'] or '')))
print()
print(V + '(7) SAMPLE: frames >= 100 ms inside the entry window (first 10 s), by idx and attribution (context of the border of B2)')
for p in sorted(sample):
    b = meta[p]['binary_sha256'][:8]
    for i, s in scenes_of(p, SG):
        ws = [x for x in recs[p]['slow'] if x['scene'] == i and x['q'] == 0 and x['t_before_us'] < 10000000]
        print('  ', tag(p), b, 'first_n', s['first_n'], 'hold_first_n', s['hold_first_n'], [(x['n'], x['dt_us'], attr(x, b)) for x in ws])
