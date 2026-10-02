"""port_gate146.py - session 146 step 0 (HPP-386): builds C:/kyty/s146/step2/gate146.py from C:/kyty/s145/step2/gate145.py by
anchored replacements.  Changes (item 309 (l)(5), item 300 (b)(2)-(4)): no session-144 pair (the (d) rows and --recheck144 go);
the reference of --start is the manifest after the warm-up i146_v of step 0 (runs146/cache_i146_v.after.json, sealed) - the
translation cache (PPSA21564 with its variant directory) must equal it; the W form member (b) of a made W reads its json env (no
KYTY_PIPELINE_PRECACHE: precache by default) instead of requiring no precache lines (the ShaderSeed / PipelinePrecache lines of
a W are printed as data); a W skipped by item 309 (k)(1) (skipped_<w>.txt) is passed over to the made tag before it.  LF,
ASCII; prints the sha256 of source and target."""
import hashlib
import sys

SRC = 'C:/kyty/s145/step2/gate145.py'
DST = 'C:/kyty/s146/step2/gate146.py'
t = open(SRC, 'rb').read().decode('ascii')
OK = [True]


def rep(old, new, count=1):
    global t
    n = t.count(old)
    if n != count:
        print('ANCHOR %d != %d: %r' % (n, count, old[:100]))
        OK[0] = False
        return
    t = t.replace(old, new)


head_end = t.index('import argparse')
t = '''"""gate146.py - the read-only gate of step 2 of session 146 (step 0 HPP-386; ROADMAP s122 item 273 (k)(3)-(4), 295 (v)-(e),
309 (k), (l)(5), 300 (b)(2)-(4); port of C:/kyty/s145/step2/gate145.py).  It reads the series files and the caches and writes
ONE ascii row into step2/times.txt:
    <UTC> GATE <what> PASS|STOP <reasons>; <details>
Modes (one per call):
  --start            before the first lock of step 2: (r) the sha256 of the reference runs146/cache_i146_v.after.json (the
                     cache manifest at the end of the warm-up i146_v of step 0, written by go146i.sh) = its seal line of
                     pred/01_sc146.md, else STOP; (s) the free space of the disk C: below 60 GiB -> STOP; (c)(1) the live caches
                     (path, size, sha256 - not mtime) against the reference: the translation cache _ShaderCache/PPSA21564 (its
                     root files and the variant directory variant_fixb26_fixb1b with its pipelines.bin) differs -> STOP (item
                     288 (v)(1)); _PipelineCache and GLCache differ -> the data segment "(c)(1) info driver caches: ..." (item 288
                     (v)(2)); then it WRITES the start manifest runs146/cache_start.json and names its sha256 in its row.
  --before <tag>     before the call of <tag> (after sc146.py --stop-check <tag>): a "GATE start PASS" row exists and every
                     made tag before <tag> has its own "GATE <tag> PASS" row; on the made tag P right before <tag> in the
                     sealed order (a W skipped by item 309 (k)(1) - skipped_<w>.txt - is passed over to the made tag before
                     it): (w) a window event -> STOP; (b) W - its json env carries KYTY_PIPELINE_PRECACHE (the W form of item
                     300 (b)(4): precache by default) -> STOP, the ShaderSeed: / PipelinePrecache: lines of log and stdout are
                     printed as data; V - 0 "ShaderSeed:" lines in log_P.txt -> STOP; (f) W - the form line of item 295 (b)(4)
                     failing -> STOP; (v) W - a failing row "W 295(b)(N)" in the admission line of score_P.txt (or the file /
                     the line missing) -> STOP; (e) V - the admission line of score_P.txt failing by "V positive control" or
                     "V shipped defaults" -> STOP; (l) the control w146_00 made - its layer limit lines >= 1 -> STOP; (c)(2)
                     w146_00 made -> runs146/cache_w146_00.before.json against the start manifest; (g) the last two made W
                     both with the key "attempt:timeout" -> STOP.
rc 0 PASS, rc 5 STOP, rc 2 usage.  READ ONLY on everything but the one times row and (--start only) the start manifest.  ASCII.
    python gate146.py --start | --before <tag>  [--root R] [--times F] [--ref M] [--live-manifest M] [--pred P]
Session 145 header (carried):
''' + t[3:head_end] + t[head_end:]
rep('''S145 = 'C:/kyty/s145'                 # absolute: a copy of this file elsewhere (a mutant) reads the same sc145 / cachemf145
sys.path.insert(0, S145)
import sc145      # noqa: E402  (read only: entry_of / scan; profile 145 is the module default)
import cachemf145  # noqa: E402  (read only: manifest of the live caches)
''', '''S146 = 'C:/kyty/s146'                 # absolute: a copy of this file elsewhere (a mutant) reads the same sc146 / cachemf146
sys.path.insert(0, S146)
import sc146      # noqa: E402  (read only: entry_of / scan / w_form4; profile 146 is the module default)
import cachemf146  # noqa: E402  (read only: manifest of the live caches)
''')
rep('''ROOT = 'C:/kyty/s145'
ROOT144 = 'C:/kyty/s144'
TIMES = ROOT + '/step2/times.txt'
REF = ROOT144 + '/runs144/cache_w144_20.after.json'
PRED = ROOT + '/pred/03_sc145.md'
REF_SEAL = 'C:/kyty/s144/runs144/cache_w144_20.after.json'   # item 295 (e): the name of its seal line
''', '''ROOT = 'C:/kyty/s146'
TIMES = ROOT + '/step2/times.txt'
REF = ROOT + '/runs146/cache_i146_v.after.json'
PRED = ROOT + '/pred/01_sc146.md'
REF_SEAL = 'runs146/cache_i146_v.after.json'                 # the name of its seal line (relative to the root)
''')
rep('''V144 = ('v144_09',)
''', '')
rep('''START_MF = 'runs145/cache_start.json'
RX_START = re.compile(r'^\\S+ GATE start PASS\\b.*start manifest runs145/cache_start\\.json sha256 ([0-9a-f]{64})')''',
    '''START_MF = 'runs146/cache_start.json'
RX_START = re.compile(r'^\\S+ GATE start PASS\\b.*start manifest runs146/cache_start\\.json sha256 ([0-9a-f]{64})')''')
i = t.index('def times144_log_sha(')
j = t.index('def mf_rows(')
t = t[:i] + t[j:]
rep('''def compare_manifest(files, ref_files, roots=cachemf145.ORDER, what='(c) %s differs from the s144 end'):''',
    '''def compare_manifest(files, ref_files, roots=cachemf146.ORDER, what='(c) %s differs from the end of the warm-up i146_v'):''')
rep('''def made(t, root):
    return os.path.isfile('%s/%s.json' % (root, t)) or os.path.isfile('%s/attempt_%s.txt' % (root, t))
''', '''def made(t, root):
    return os.path.isfile('%s/%s.json' % (root, t)) or os.path.isfile('%s/attempt_%s.txt' % (root, t))


def skipped(t, root):
    """Item 309 (k)(1): the W was not called (its V NOT_ENTERED) - the chain's marker skipped_<w>.txt."""
    return os.path.isfile('%s/skipped_%s.txt' % (root, t))
''')
rep('''    e = sc145.entry_of(t, root, pred_sha)''', '''    e = sc146.entry_of(t, root, pred_sha)''')
rep('''    seq = list(sc145.SEQ)''', '''    seq = list(sc146.SEQ)''')
rep('''    p = prior[-1] if prior else None
    if p is not None and not made(p, root):''', '''    p = prior[-1] if prior else None
    while p is not None and not made(p, root) and skipped(p, root):
        det.append('%s SKIPPED_V_NOT_ENTERED (item 309 (k)(1)) - passed over' % p)
        k = prior.index(p)
        p = prior[k - 1] if k > 0 else None
    if p is not None and not made(p, root):''')
rep('''        if p in sc145.W_TAGS:
            if lc is None or sc is None:
                bad.append('(b) W %s: log or stdout missing - member not evaluable' % p)
            elif lc[SEED] + lc[PRE] + sc[SEED] + sc[PRE] > 0:
                bad.append('(b) W %s: precache member of the emulator present (ShaderSeed/PipelinePrecache log %s stdout %s)'
                           % (p, fl(lc), fl(sc)))
            jp = '%s/%s.json' % (root, p)
            f4 = sc145.w_form4(json.load(open(jp, encoding='utf-8')).get('env') or {}) if os.path.isfile(jp) else (
                False, 'NO JSON')''', '''        if p in sc146.W_TAGS:
            jp = '%s/%s.json' % (root, p)
            env = (json.load(open(jp, encoding='utf-8')).get('env') or {}) if os.path.isfile(jp) else None
            if env is None:
                bad.append('(b) W %s: no json - the W form not evaluable' % p)
            elif 'KYTY_PIPELINE_PRECACHE' in env:
                bad.append('(b) W %s: KYTY_PIPELINE_PRECACHE=%s in its env - the W form of item 300 (b)(4) is precache by '
                           'default' % (p, env.get('KYTY_PIPELINE_PRECACHE')))
            f4 = sc146.w_form4(env) if env is not None else (False, 'NO JSON')''')
rep('''                bad.append('(f) W %s: the form line "%s" != "%s" or VK_LAYER_MESSAGE_ID_FILTER in its env (item 295 (b)(4))' % (
                    p, f4[1], sc145.W_FORM_LINE))''', '''                bad.append('(f) W %s: the form line "%s" != "%s" or VK_LAYER_MESSAGE_ID_FILTER in its env (item 295 (b)(4))' % (
                    p, f4[1], sc146.W_FORM_LINE))''')
rep('''    c0 = sc145.CONTROL[0]''', '''    c0 = sc146.CONTROL[0]''')
rep('''        mp = '%s/runs145/cache_%s.before.json' % (root, c0)''', '''        mp = '%s/runs146/cache_%s.before.json' % (root, c0)''')
rep('''    ws = [t for t in prior if t in sc145.W_TAGS and made(t, root)][-2:]''', '''    ws = [t for t in prior if t in sc146.W_TAGS and made(t, root)][-2:]''')
rep('''def start(root, root144, pred, ref, live):
    bad, det = check144(root144, pred)
    want = seal_sha(pred, REF_SEAL)''', '''def start(root, pred, ref, live):
    bad, det = [], []
    want = seal_sha(pred, REF_SEAL)''')
rep('''        rrows, files = cachemf145.manifest(cachemf145.default_roots())''', '''        rrows, files = cachemf146.manifest(cachemf146.default_roots())''')
rep('''    b2, d2 = compare_manifest(files, rf, roots=STRICT, what='(c) %s differs from the s144 end')''',
    '''    b2, d2 = compare_manifest(files, rf, roots=STRICT, what='(c) %s differs from the end of the warm-up i146_v')''')
rep('''        pipelines_sig(cachemf145.default_roots()['shader'] + '/pipelines.bin') if not live else 'n/a'))''',
    '''        pipelines_sig(cachemf146.default_roots()['shader'] + '/variant_fixb26_fixb1b/pipelines.bin') if not live else 'n/a'))''')
rep('''    pb = [r for r in files if r[0] == 'shader' and r[1] == 'pipelines.bin']''',
    '''    pb = [r for r in files if r[0] == 'shader' and r[1] == 'variant_fixb26_fixb1b/pipelines.bin']''')
rep('''    g.add_argument('--recheck144', action='store_true')
    ap.add_argument('--root', default=ROOT)
    ap.add_argument('--root144', default=ROOT144)
''', '''    ap.add_argument('--root', default=ROOT)
''')
rep('''        bad, det = start(a.root, a.root144, a.pred, a.ref, a.live_manifest)
    elif a.recheck144:
        what = 'recheck144'
        bad, det = check144(a.root144, a.pred)
    else:''', '''        bad, det = start(a.root, a.pred, a.ref, a.live_manifest)
    else:''')
rep('''    want = seal_sha(pred, REF_SEAL)
    got = sha_file(ref) if os.path.isfile(ref) else None''', '''    want = seal_sha(pred, REF_SEAL) if os.path.isfile(pred) else None
    got = sha_file(ref) if os.path.isfile(ref) else None''')
rep('''(pred/02_sc145.md), or None.''', '''(pred/01_sc146.md), or None.''')
rep('''without the death-marker key of sc145.py and
    without a GuestOut line in its log; else the sc145 key or None.''', '''without the death-marker key of sc146.py and
    without a GuestOut line in its log; else the sc146 key or None.''')
code = t[t.index('import argparse'):]
for w in ('sc145', 'cachemf145', 'runs145', 'check144', 'ROOT144', 'V144'):
    if w in code:
        print('gate146: %s left in the code' % w)
        OK[0] = False
if any(ord(c) > 127 for c in t):
    print('NON-ASCII')
    OK[0] = False
open(DST, 'wb').write(t.encode('ascii'))
print('port_gate146: %s %s -> %s %s' % (SRC, hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:16], DST,
                                         hashlib.sha256(t.encode('ascii')).hexdigest()[:16]))
print('ALL OK' if OK[0] else 'SOME FAILED')
sys.exit(0 if OK[0] else 1)
