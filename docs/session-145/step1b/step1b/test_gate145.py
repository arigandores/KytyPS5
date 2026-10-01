"""test_gate145.py - the fixtures of step2/gate145.py (step 0 HPP-350, link 1b HPP-379; ROADMAP s122 item 273 (k)(2)-(4),
item 295 (v), (e); port of C:/kyty/s144/step2/test_gate144.py) on REAL logs where one exists:
  g1  w143_01 (W with the start precache, stopped before "recipes ->") as w145_01        -> STOP by (b)
  g2  w142 (Sky Garden W with precache, held 310 s) as the control w145_00               -> STOP by (b) and (f)
  g3  f2c_b (W) in the form of item 295 (b)(4) as w145_01                                -> PASS; with the filter of step 0,
      with the limit 1000000, without the limit, with a filter "none" or "" in the env    -> STOP by (f)
  g4  v143_01 (V) as v145_02                                                              -> PASS
  g5  v143_01 with its "ShaderSeed:" lines cut                                            -> STOP by (b)
  g6  a manifest with one changed sha256 of pipelines.bin (start) against the s144 end    -> STOP by (c)(1); unchanged ->
      PASS; a GLCache file missing -> PASS with the info segment (item 288 (v)(2)); (c)(2) against the start manifest
  g7  two W jsons with outcome timeout before GuestOut                                    -> STOP by (g); different keys,
      timeout after GuestOut                                                              -> PASS
  g8  a V score rejected by "V positive control" / "V shipped defaults"                   -> STOP by (e)
  g9  (d): a seal with the real s144 sha lines -> PASS; another s144 times sha, another V log -> STOP
  g10 a made tag without its GATE row, no start row, the tag before not made              -> STOP
  g11 ascii output under a strict cp1250 console without PYTHONIOENCODING (the gate under test as a child)
  g12 w144_09 (the real W with "Window 1 minimized" and the Recovering line) as w145_01   -> STOP by (w); the Recovering
      line alone in the stdout -> STOP; a V with "minimized" -> STOP; lost focus / restored only -> PASS
  g13 the control w145_00 with a layer limit line in its log or its stdout                -> STOP by (l); 0 -> PASS
  g14 item 288 (v): a translation cache file changed -> STOP (c)(1); pipelines.bin changed -> STOP (c)(1); only
      _PipelineCache / GLCache changed -> PASS with "(c)(1) info driver caches:" naming the files and sha; a GLCache file
      added / removed -> PASS with the info; unchanged -> the info with zeros; the shader root gone -> STOP; --start writes
      runs145/cache_start.json (= the manifest read) and names its sha256 in its row; (c)(2) reads it: the control's
      manifest = start -> PASS, = the s144 end (driver caches differ from start) -> STOP, start manifest rewritten -> STOP,
      missing -> STOP, a start row without the sha -> STOP
  g15 item 295 (v): a W (control or another) whose score fails one row "W 295(b)(N)" (each of the four), two rows, the score
      missing, the admission line missing -> STOP (v) naming the members; another admission failure, PASS -> no (v); the
      score written by the scorer sc145.py --tag of a held W without validation-layer lines -> STOP (v) (b)(2),(b)(3)
  g16 item 295 (v): --start with 60 GiB free -> PASS, 1 byte less -> STOP (s); the row prints bytes, GiB and GB
  g17 item 295 (e): --start with the reference sha = its seal line -> PASS; a seal with another sha, a seal without the
      line, a missing reference -> STOP (r)
The suite is in the mutlib early-exit form (item 85 (v)(2)): one top-level BASE = Path(...) (the fixture directory), the
only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is `sys.exit(0 if ok else 1)`; the gate under
test is argv[1] (default step2/gate145.py), loaded by its path.  Work dir C:/kyty/s145/step2/fx_gate (hard links to the real
logs; cut copies removed at the end).  The first line names the suite and the target by sha256; the output ends ALL OK.
    python test_gate145.py [<gate145.py under test>] > test_gate145.out.txt
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
SRC = sys.argv[1] if len(sys.argv) > 1 else HERE + '/gate145.py'
print('suite test_gate145.py sha256 %s target gate145.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('gate145_under_test', SRC)
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

BASE = Path('C:/kyty/s145/step2/fx_gate')
FX = BASE.as_posix()
REF = G.REF
FILT = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
FORM = dict(KYTY_PIPELINE_PRECACHE='0', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
NCHECK = [0]
FAILS = []
FREE_OK = 100 * 2 ** 30
G.disk_free = lambda p: FREE_OK


def sha(p):
    return G.sha_file(p)


def check(name, cond, info=''):
    NCHECK[0] += 1
    print('%s %s %s' % ('ok  ' if cond else 'FAIL', name, G.asc(info)[:400]))
    if not cond:
        FAILS.append(name)
    return bool(cond)


def fresh(name):
    d = FX + '/' + name
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d + '/runs145')
    os.makedirs(d + '/step2')
    return d


def link(src, dst):
    try:
        os.link(src, dst)
    except OSError:
        shutil.copyfile(src, dst)


def wscore(root, dst, text='TAG %s\n  admission: PASS\n'):
    if text is not None:
        open('%s/score_%s.txt' % (root, dst), 'w', encoding='ascii').write(text % dst if '%s' in text else text)


def put_tag(root, src_root, src, dst, extra_env=None, drop_env=(), score='TAG %s\n  admission: PASS\n'):
    js = json.load(open('%s/%s.json' % (src_root, src), encoding='utf-8'))
    js['tag'] = dst
    env = dict(js.get('env') or {}, **(extra_env or {}))
    for k in drop_env:
        env.pop(k, None)
    js['env'] = env
    json.dump(js, open('%s/%s.json' % (root, dst), 'w', encoding='utf-8'))
    for a in ('log_%s.txt', 'stdout_%s.txt', '%s.stdout.txt'):
        if os.path.isfile(src_root + '/' + a % src):
            link(src_root + '/' + a % src, root + '/' + a % dst)
    if dst in G.sc145.W_TAGS:
        wscore(root, dst, score)


def synth_w(root, dst, outcome, log_lines=(), std_lines=(), env=None, score='TAG %s\n  admission: PASS\n'):
    json.dump(dict(tag=dst, attempts=[dict(outcome=outcome, level=G.sc145.level_of(dst))], env=dict(FORM if env is None
                                                                                                   else env), cmdline=[]),
              open('%s/%s.json' % (root, dst), 'w', encoding='utf-8'))
    open('%s/log_%s.txt' % (root, dst), 'wb').write(b''.join(x + b'\n' for x in log_lines))
    open('%s/stdout_%s.txt' % (root, dst), 'wb').write(b''.join(x + b'\n' for x in std_lines))
    wscore(root, dst, score)


def synth_v(root, dst, log_lines=(), std_lines=()):
    json.dump(dict(tag=dst, attempts=[dict(outcome='ok', level=G.sc145.level_of(dst))], env={}, cmdline=[]),
              open('%s/%s.json' % (root, dst), 'w', encoding='utf-8'))
    open('%s/log_%s.txt' % (root, dst), 'wb').write(b''.join(x + b'\n' for x in (b'ShaderSeed: x',) + tuple(log_lines)))
    open('%s/stdout_%s.txt' % (root, dst), 'wb').write(b''.join(x + b'\n' for x in std_lines))
    open('%s/score_%s.txt' % (root, dst), 'w', encoding='ascii').write('TAG %s\n  admission: PASS\n' % dst)


def rows(root, *what):
    """GATE <what> PASS rows; the start row also gets the start manifest runs145/cache_start.json (= the s144 end, as a
    clean --start would write it) and names its sha256 like gate145.py --start."""
    with open(root + '/step2/times.txt', 'a', encoding='ascii') as f:
        for w in what:
            if w == 'start':
                shutil.copyfile(REF, root + '/' + G.START_MF)
                f.write('2026-10-01T00:00:00Z GATE start PASS; fixture row | (c)(2) reference: start manifest %s sha256 %s\n'
                        % (G.START_MF, sha(root + '/' + G.START_MF)))
            else:
                f.write('2026-10-01T00:00:00Z GATE %s PASS; fixture row\n' % w)


def run(root, *argv):
    t = root + '/step2/times.txt'
    rc = G.main(list(argv) + ['--root', root, '--times', t])
    last = open(t, encoding='ascii').read().splitlines()[-1]
    return rc, last


def reasons(last):
    return last.split(' | ')[0]


def seal144(path, times_sha=None, pred_sha=None, ref_sha=None, ref_line=True):
    """A seal file with the two s144 lines and the reference line of pred/03_sc145.md (their real sha256 unless given)."""
    ts = times_sha or sha(G.ROOT144 + '/step2/times.txt')
    ps = pred_sha or sha(G.ROOT144 + '/pred/01_sc144.md')
    rs = ref_sha or sha(REF)
    open(path, 'w', encoding='utf-8').write('fixture seal 145\nseal: %s C:/kyty/s144/step2/times.txt\n'
                                            'seal: %s C:/kyty/s144/pred/01_sc144.md\n' % (ts, ps) +
                                            ('seal: %s C:/kyty/s144/runs144/cache_w144_20.after.json\n' % rs if ref_line
                                             else ''))
    return path


ok = True
if os.path.isdir(FX):
    shutil.rmtree(FX)
os.makedirs(FX)
# g1: w143_01 as w145_01
r = fresh('g1')
rows(r, 'start', 'w145_01')
put_tag(r, 'C:/kyty/s143', 'w143_01', 'w145_01', FORM, ('VK_LAYER_MESSAGE_ID_FILTER',))
rc, last = run(r, '--before', 'v145_02')
ok &= check('g1 w143_01 as w145_01 -> STOP', rc == 5, last)
ok &= check('g1 reason (b) W w145_01 precache member, no (f), no (v)', '(b) W w145_01: precache member' in last and '(f)' not in
            reasons(last) and '(v)' not in reasons(last), reasons(last))
# g2: w142 as w145_00, before w145_01
r = fresh('g2')
rows(r, 'start', 'w145_00')
put_tag(r, 'C:/kyty/s142', 'w142', 'w145_00')
shutil.copyfile(REF, r + '/runs145/cache_w145_00.before.json')
rc, last = run(r, '--before', 'w145_01')
ok &= check('g2 w142 as w145_00 -> STOP', rc == 5, last)
ok &= check('g2 reasons (b) W w145_00 and (f) the form line with the limit of s142 (1000000)', '(b) W w145_00: precache member' in last and
            '(f) W w145_00: the form line "W form: limit=1000000 filter=none" != "W form: limit=100000000 filter=none"' in last,
            reasons(last))
ok &= check('g2 (c)(2) same manifest passes; (l) the control has 0 limit lines',
            '(c)(2)' not in reasons(last) and '(l)' not in reasons(last) and 'w145_00 layer limit lines 0' in last, last)
# g3: f2c_b as w145_01 in the form of item 295 (b)(4) / not
r = fresh('g3')
rows(r, 'start', 'w145_01')
put_tag(r, 'C:/kyty/f287/f2c', 'f2c_b', 'w145_01', FORM, ('VK_LAYER_MESSAGE_ID_FILTER',))
rc, last = run(r, '--before', 'v145_02')
ok &= check('g3 f2c_b in the form of item 295 (b)(4) as w145_01 -> PASS', rc == 0 and ' GATE v145_02 PASS' in last, last)
ok &= check('g3 detail 0/0 in log and stdout, the form line, the W rows pass, no window event',
            'w145_01 ShaderSeed/PipelinePrecache log 0/0 stdout 0/0' in last and
            'w145_01 W form: limit=100000000 filter=none' in last and 'w145_01 W form rows of item 295 (b) pass' in last and
            'w145_01 window minimized/Recovering 0/0' in last, last)
BAD3 = ((dict(FORM, VK_LAYER_MESSAGE_ID_FILTER=FILT), (), 'with the filter of step 0'),
        (dict(FORM, VK_LAYER_DUPLICATE_MESSAGE_LIMIT='1000000'), ('VK_LAYER_MESSAGE_ID_FILTER',), 'with the limit 1000000'),
        (dict(KYTY_PIPELINE_PRECACHE='0'), ('VK_LAYER_MESSAGE_ID_FILTER', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT'),
         'without the limit'),
        (dict(FORM, VK_LAYER_MESSAGE_ID_FILTER='none'), (), 'with a filter "none" in the env'),
        (dict(FORM, VK_LAYER_MESSAGE_ID_FILTER=''), (), 'with an empty filter in the env'))
for i, (env, drop, name) in enumerate(BAD3):
    r = fresh('g3_%d' % i)
    rows(r, 'start', 'w145_01')
    put_tag(r, 'C:/kyty/f287/f2c', 'f2c_b', 'w145_01', env, drop)
    rc, last = run(r, '--before', 'v145_02')
    ok &= check('g3 f2c_b %s -> STOP (f)' % name, rc == 5 and '(f) W w145_01: the form line' in last, reasons(last))
# g4: v143_01 as v145_02 -> PASS
r = fresh('g4')
rows(r, 'start', 'v145_02')
put_tag(r, 'C:/kyty/s143', 'v143_01', 'v145_02')
shutil.copyfile('C:/kyty/s143/score_v143_01.txt', r + '/score_v145_02.txt')
rc, last = run(r, '--before', 'w145_02')
ok &= check('g4 v143_01 as v145_02 -> PASS', rc == 0 and ' GATE w145_02 PASS' in last, last)
# g5: v143_01 with the ShaderSeed: lines cut
r = fresh('g5')
rows(r, 'start', 'v145_02')
put_tag(r, 'C:/kyty/s143', 'v143_01', 'v145_02')
os.remove(r + '/log_v145_02.txt')
cut = 0
with open('C:/kyty/s143/log_v143_01.txt', 'rb') as fi, open(r + '/log_v145_02.txt', 'wb') as fo:
    for line in fi:
        if G.SEED in line:
            cut += 1
            continue
        fo.write(line)
shutil.copyfile('C:/kyty/s143/score_v143_01.txt', r + '/score_v145_02.txt')
rc, last = run(r, '--before', 'w145_02')
ok &= check('g5 %d ShaderSeed: line(s) cut' % cut, cut >= 1, str(cut))
ok &= check('g5 V without ShaderSeed: -> STOP (b)', rc == 5 and '(b) V v145_02: 0 ShaderSeed: lines' in last, reasons(last))
os.remove(r + '/log_v145_02.txt')
# g6: manifests against the s144 end
r = fresh('g6')
ref = json.load(open(REF, encoding='utf-8'))
same = r + '/same.json'
json.dump(ref, open(same, 'w', encoding='utf-8'))
ch = json.loads(json.dumps(ref))
i = [k for k, x in enumerate(ch['files']) if x[0] == 'shader' and x[1] == 'pipelines.bin'][0]
ch['files'][i][4] = '0' * 64
chp = r + '/changed.json'
json.dump(ch, open(chp, 'w', encoding='utf-8'))
sp = seal144(r + '/pred.md')
rc, last = run(r, '--start', '--live-manifest', same, '--pred', sp)
ok &= check('g6 start with the reference manifest and the real s144 files -> PASS', rc == 0 and ' GATE start PASS' in last, last)
ok &= check('g6 the reference is the end of the s144 series', REF == 'C:/kyty/s144/runs144/cache_w144_20.after.json' and
            G.REF_SEAL == REF, REF)
rc, last = run(r, '--start', '--live-manifest', chp, '--pred', sp)
ok &= check('g6 start with one changed sha -> STOP (c)', rc == 5 and '(c) shader differs from the s144 end: +0 -0 changed 1 '
            '(pipelines.bin)' in last, reasons(last))
mt = json.loads(json.dumps(ref))
mt['files'][i][3] = 1
mtp = r + '/mtime.json'
json.dump(mt, open(mtp, 'w', encoding='utf-8'))
rc, last = run(r, '--start', '--live-manifest', mtp, '--pred', sp)
ok &= check('g6 another mtime only -> PASS (content, not mtime)', rc == 0, reasons(last))
gl = json.loads(json.dumps(ref))
j = [k for k, x in enumerate(gl['files']) if x[0] == 'glcache'][0]
del gl['files'][j]
glp = r + '/gl.json'
json.dump(gl, open(glp, 'w', encoding='utf-8'))
rc, last = run(r, '--start', '--live-manifest', glp, '--pred', sp)
ok &= check('g6 a glcache file missing -> PASS with the info segment (item 288 (v)(2))', rc == 0 and
            '(c)(1) info driver caches: pipeline +0 -0 changed 0; glcache +0 -1 changed 0 (-%s %s)' % (
                ref['files'][j][1], ref['files'][j][4][:16]) in last and '(c) glcache' not in last, last)
r2 = fresh('g6b')
rows(r2, 'start', 'w145_00')
synth_w(r2, 'w145_00', 'ok')
shutil.copyfile(chp, r2 + '/runs145/cache_w145_00.before.json')
rc, last = run(r2, '--before', 'w145_01')
ok &= check('g6 (c)(2) cache_w145_00.before with one changed sha -> STOP', rc == 5 and '(c)(2) shader differs' in last,
            reasons(last))
os.remove(r2 + '/runs145/cache_w145_00.before.json')
rc, last = run(r2, '--before', 'w145_01')
ok &= check('g6 (c)(2) manifest missing -> STOP', rc == 5 and '(c)(2) runs145/cache_w145_00.before.json missing' in last,
            reasons(last))
# g7: W keys
r = fresh('g7')
rows(r, 'start', 'w145_00', 'w145_01')
synth_w(r, 'w145_00', 'timeout', [b'some line'], [b'x'])
synth_w(r, 'w145_01', 'timeout', [b'other line'], [b'y'])
shutil.copyfile(REF, r + '/runs145/cache_w145_00.before.json')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g7 two W timeout before GuestOut -> STOP (g)', rc == 5 and '(g) two W in a row with the key attempt:timeout: '
            'w145_00,w145_01' in last, reasons(last))
synth_w(r, 'w145_01', 'exited', [b'other line'], [b'y'])
rc, last = run(r, '--before', 'v145_02')
ok &= check('g7 timeout then exited (different keys) -> PASS', rc == 0, last)
synth_w(r, 'w145_01', 'timeout', [b'[1][00:00:01] GuestOut: hello'], [b'y'])
rc, last = run(r, '--before', 'v145_02')
ok &= check('g7 timeout after GuestOut has no key -> PASS', rc == 0 and 'timeout after GuestOut' in last, last)
synth_w(r, 'w145_01', 'timeout', [b'ShaderSeed: compatibility=x'], [b'y'])
rc, last = run(r, '--before', 'v145_02')
ok &= check('g7 synthetic W with a ShaderSeed: line -> STOP (b) too', rc == 5 and '(b) W w145_01' in last, reasons(last))
# g8: V admission
r = fresh('g8')
rows(r, 'start', 'v145_02')
put_tag(r, 'C:/kyty/s143', 'v143_01', 'v145_02')
for k in ('V positive control', 'V shipped defaults'):
    open(r + '/score_v145_02.txt', 'w', encoding='ascii').write(
        'TAG v145_02 ...\n  admission: FAIL %s: x (log 0)\n' % k)
    rc, last = run(r, '--before', 'w145_02')
    ok &= check('g8 %s -> STOP (e)' % k, rc == 5 and '(e) V v145_02 rejected by a form member: %s' % k in last, reasons(last))
open(r + '/score_v145_02.txt', 'w', encoding='ascii').write('  admission: FAIL video KYTY_REC (x)\n')
rc, last = run(r, '--before', 'w145_02')
ok &= check('g8 another admission failure -> not a form stop', rc == 0, reasons(last))
os.remove(r + '/score_v145_02.txt')
rc, last = run(r, '--before', 'w145_02')
ok &= check('g8 score missing -> STOP (e)', rc == 5 and 'score_v145_02.txt missing' in last, reasons(last))
# g9: (d)
r = fresh('g9')
rc, last = run(r, '--recheck144', '--pred', seal144(r + '/pred.md'))
ok &= check('g9 the real s144 times, seal and v144_09 log -> PASS', rc == 0 and ' GATE recheck144 PASS' in last, last)
rc, last = run(r, '--recheck144', '--pred', seal144(r + '/pred2.md', times_sha='f' * 64))
ok &= check('g9 a seal with another s144 times sha -> STOP (d)', rc == 5 and '(d) s144/step2/times.txt sha' in last,
            reasons(last))
x4 = r + '/x144'
os.makedirs(x4 + '/step2')
os.makedirs(x4 + '/pred')
shutil.copyfile(G.ROOT144 + '/pred/01_sc144.md', x4 + '/pred/01_sc144.md')
open(x4 + '/log_v144_09.txt', 'wb').write(b'another log\n')
open(x4 + '/step2/times.txt', 'w', encoding='ascii').write(
    '2026-10-01T00:00:00Z go144a v144_09 enter_scene end rc 0 log_v144_09.txt sha256 %s\n' % ('e' * 64))
rc, last = run(r, '--recheck144', '--root144', x4, '--pred', seal144(r + '/pred3.md', times_sha=sha(
    x4 + '/step2/times.txt')))
ok &= check('g9 a v144_09 log whose sha != the last go144a enter_scene end line -> STOP (d)', rc == 5 and
            '(d) log_v144_09 sha' in last and '(d) s144/step2/times.txt' not in reasons(last), reasons(last))
# g10: rows
r = fresh('g10')
synth_w(r, 'w145_00', 'ok')
shutil.copyfile(REF, r + '/runs145/cache_w145_00.before.json')
rc, last = run(r, '--before', 'w145_01')
ok &= check('g10 no start row and an ungated call -> STOP', rc == 5 and 'no "GATE start PASS"' in last
            and 'made tag w145_00 has no "GATE w145_00 PASS"' in last, reasons(last))
rows(r, 'start', 'w145_00')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g10 the tag before not made -> STOP', rc == 5 and 'the tag w145_01 before v145_02 was not made' in last,
            reasons(last))
rc, last = run(r, '--before', 'w145_01')
ok &= check('g10 clean control -> PASS', rc == 0, last)
rc, last = run(r, '--before', 'x145_99')
ok &= check('g10 unknown tag -> STOP', rc == 5, reasons(last))
rc, last = run(r, '--before', 'v144_09')
ok &= check('g10 the V of another session is no tag of the chain -> STOP', rc == 5, reasons(last))
# g11: ascii under strict cp1250 (the real gate as a child; a mutant under test (argv[1]) in process - mutlib allows no child of the
# suite: 'workers: FORCED TO 1', link 1b)
if os.path.normcase(os.path.abspath(SRC)) == os.path.normcase(os.path.abspath(HERE + '/gate145.py')):
    env = dict(os.environ)
    env.pop('PYTHONIOENCODING', None)
    env.pop('PYTHONUTF8', None)
    p = subprocess.run([sys.executable, SRC, '--recheck144', '--root', r, '--times', r + '/step2/times.txt', '--pred',
                        seal144(r + '/pred.md')], capture_output=True, env=env, timeout=300)
    try:
        p.stdout.decode('cp1250', 'strict')
        dec = True
    except UnicodeDecodeError:
        dec = False
    ok &= check('g11 subprocess rc 0, stdout strict cp1250 and ascii, no stderr', p.returncode == 0 and dec
                and all(b < 128 for b in p.stdout) and not p.stderr, p.stderr.decode('ascii', 'replace')[:200])
else:
    b11 = io.StringIO()
    with contextlib.redirect_stdout(b11):
        rc11 = G.main(['--recheck144', '--root', r, '--times', r + '/step2/times.txt', '--pred', seal144(r + '/pred.md')])
    ok &= check('g11 (the gate under test in process) rc 0, the printed row ascii', rc11 == 0 and
                all(ord(c) < 128 for c in b11.getvalue()), b11.getvalue()[:200])
ok &= check('g11 the times file is ascii', all(b < 128 for b in open(r + '/step2/times.txt', 'rb').read()))
# g12: window event
r = fresh('g12')
rows(r, 'start', 'w145_01')
put_tag(r, 'C:/kyty/s144', 'w144_09', 'w145_01', FORM)
rc, last = run(r, '--before', 'v145_02')
ok &= check('g12 the real w144_09 (minimized, Recovering) as w145_01 -> STOP (w) naming both counts, no (f)',
            rc == 5 and '(w) window event on w145_01: minimized 1, Recovering Vulkan swapchain 1' in last and
            '(f)' not in reasons(last), reasons(last))
r = fresh('g12b')
rows(r, 'start', 'w145_01')
synth_w(r, 'w145_01', 'ok', [b'line'], [b'Recovering Vulkan swapchain (x)'])
rc, last = run(r, '--before', 'v145_02')
ok &= check('g12 the Recovering line alone, in the stdout -> STOP (w)', rc == 5 and
            '(w) window event on w145_01: minimized 0, Recovering Vulkan swapchain 1' in last, reasons(last))
synth_w(r, 'w145_01', 'ok', [b'Window 1 lost keyboard focus', b'Window 1 restored', b'Window minimized',
                             b'Window 1 minimizedX'], [b'y'])
rc, last = run(r, '--before', 'v145_02')
ok &= check('g12 lost focus, restored, "Window minimized" without an id and "minimizedX" -> PASS', rc == 0 and
            'w145_01 window minimized/Recovering 0/0' in last, last)
r = fresh('g12c')
rows(r, 'start', 'w145_01', 'v145_02')
synth_w(r, 'w145_01', 'ok')
synth_v(r, 'v145_02', [b'Window 1 minimized'])
rc, last = run(r, '--before', 'w145_02')
ok &= check('g12 a V with "Window 1 minimized" -> STOP (w)', rc == 5 and '(w) window event on v145_02: minimized 1' in last,
            reasons(last))
synth_v(r, 'v145_02')
rc, last = run(r, '--before', 'w145_02')
ok &= check('g12 the same V without it -> PASS', rc == 0, last)
for name in ('log_v145_02.txt', 'stdout_v145_02.txt'):
    os.remove(r + '/' + name)
rc, last = run(r, '--before', 'w145_02')
ok &= check('g12 a V without its log and stdout -> STOP (w) not evaluable', rc == 5 and
            '(w) v145_02: log and stdout missing' in last, reasons(last))
# g13: the layer limit of the control
lim = b'[Vulkan][W][2]: (Warning - This VUID has now been reported 1000000 times, which is the duplicate_message_limit ' \
      b'value, this will be the last time reporting it).'
for i, (lg, sd) in enumerate((([lim], []), ([], [lim]))):
    r = fresh('g13_%d' % i)
    rows(r, 'start', 'w145_00')
    synth_w(r, 'w145_00', 'ok', lg, sd)
    shutil.copyfile(REF, r + '/runs145/cache_w145_00.before.json')
    rc, last = run(r, '--before', 'w145_01')
    ok &= check('g13 the control with a layer limit line in its %s -> STOP (l)' % ('log', 'stdout')[i], rc == 5 and
                '(l) the control W w145_00 has 1 layer limit line(s)' in last, reasons(last))
r = fresh('g13_2')
rows(r, 'start', 'w145_00', 'w145_01')
synth_w(r, 'w145_00', 'ok', [lim])
synth_w(r, 'w145_01', 'ok', [lim])
shutil.copyfile(REF, r + '/runs145/cache_w145_00.before.json')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g13 a limit line in a non-control W does not stop by (l); the control one still does two tags later', rc == 5 and
            '(l) the control W w145_00 has 1 layer limit line(s)' in last and 'w145_01 has' not in last, reasons(last))
# g14: item 288 (v) - the split of (c)(1) and the start manifest
r = fresh('g14')
sp = seal144(r + '/pred.md')


def mf(name, edit):
    m = json.loads(json.dumps(ref))
    edit(m)
    p = r + '/' + name + '.json'
    json.dump(m, open(p, 'w', encoding='utf-8'))
    return p


def idx(root, rel=None, skip=None):
    return [k for k, x in enumerate(ref['files']) if x[0] == root and (rel is None or x[1] == rel)
            and (skip is None or x[1] != skip)][0]


ish, ipb = idx('shader', skip='pipelines.bin'), idx('shader', 'pipelines.bin')
ipl, igl = idx('pipeline', 'PPSA21564.bin'), idx('glcache')
F = ref['files']
tr = mf('tr', lambda m: m['files'][ish].__setitem__(4, '1' * 64))
rc, last = run(r, '--start', '--live-manifest', tr, '--pred', sp)
ok &= check('g14 a translation cache file changed -> STOP (c)(1) shader', rc == 5 and
            '(c) shader differs from the s144 end: +0 -0 changed 1 (%s)' % F[ish][1] in last, reasons(last))
pbm = mf('pb', lambda m: m['files'][ipb].__setitem__(2, m['files'][ipb][2] + 1))
rc, last = run(r, '--start', '--live-manifest', pbm, '--pred', sp)
ok &= check('g14 pipelines.bin changed (size) -> STOP (c)(1) shader', rc == 5 and
            '(c) shader differs from the s144 end: +0 -0 changed 1 (pipelines.bin)' in last, reasons(last))


def drv_edit(m):
    m['files'][ipl][4] = '2' * 64
    m['files'][igl][4] = '3' * 64


drv = mf('drv', drv_edit)
rc, last = run(r, '--start', '--live-manifest', drv, '--pred', sp)
ok &= check('g14 only _PipelineCache and GLCache changed -> PASS', rc == 0 and ' GATE start PASS' in last, reasons(last))
ok &= check('g14 the info segment names both files with the old and new sha',
            '(c)(1) info driver caches: pipeline +0 -0 changed 1 (~PPSA21564.bin %s->%s); glcache +0 -0 changed 1 (~%s %s->%s) '
            '(item 288 (v)(2): data, not STOP)' % (F[ipl][4][:16], '2' * 16, F[igl][1], F[igl][4][:16], '3' * 16) in last, last)
add = mf('add', lambda m: m['files'].append(['glcache', 'x/new.bin', 5, 1, '4' * 64]))
rc, last = run(r, '--start', '--live-manifest', add, '--pred', sp)
ok &= check('g14 a GLCache file added -> PASS with the info', rc == 0 and
            'glcache +1 -0 changed 0 (+x/new.bin %s)' % ('4' * 16) in last, last)
rem = mf('rem', lambda m: m['files'].__delitem__(ipl))
rc, last = run(r, '--start', '--live-manifest', rem, '--pred', sp)
ok &= check('g14 a _PipelineCache file removed -> PASS with the info', rc == 0 and
            'pipeline +0 -1 changed 0 (-PPSA21564.bin %s)' % F[ipl][4][:16] in last, last)
rc, last = run(r, '--start', '--live-manifest', same, '--pred', sp)
ok &= check('g14 unchanged -> PASS, the info with zeros', rc == 0 and
            '(c)(1) info driver caches: pipeline +0 -0 changed 0; glcache +0 -0 changed 0 (item 288' in last, last)
nosh = mf('nosh', lambda m: m.__setitem__('files', [x for x in m['files'] if x[0] != 'shader']))
rc, last = run(r, '--start', '--live-manifest', nosh, '--pred', sp)
ok &= check('g14 the shader root gone -> STOP (c)(1)', rc == 5 and '(c) shader differs from the s144 end: +0 -%d' % sum(
    1 for x in F if x[0] == 'shader') in last, reasons(last))
r2 = fresh('g14b')
smf = r2 + '/' + G.START_MF
rc, last = run(r2, '--start', '--live-manifest', drv, '--pred', sp)
sm = json.load(open(smf, encoding='utf-8'))
ok &= check('g14 --start writes the start manifest = the manifest read and names its sha256 in its row',
            rc == 0 and sm['files'] == json.load(open(drv, encoding='utf-8'))['files'] and
            'start manifest runs145/cache_start.json sha256 %s' % sha(smf) in last and G.start_sha(r2 + '/step2/times.txt')
            == sha(smf), last)
rows(r2, 'w145_00')
synth_w(r2, 'w145_00', 'ok')
shutil.copyfile(drv, r2 + '/runs145/cache_w145_00.before.json')
rc, last = run(r2, '--before', 'w145_01')
ok &= check('g14 (c)(2) the control manifest = the start manifest -> PASS', rc == 0 and 'cache_w145_00.before %s vs start '
            'manifest %s' % (sha(drv)[:16], sha(smf)[:16]) in last, last)
shutil.copyfile(REF, r2 + '/runs145/cache_w145_00.before.json')
rc, last = run(r2, '--before', 'w145_01')
ok &= check('g14 (c)(2) the control manifest = the s144 end (driver caches differ from the start) -> STOP',
            rc == 5 and '(c)(2) pipeline differs from the start manifest: +0 -0 changed 1 (PPSA21564.bin)' in last and
            '(c)(2) glcache differs from the start manifest' in last and '(c)(2) shader' not in last, reasons(last))
shutil.copyfile(drv, r2 + '/runs145/cache_w145_00.before.json')
json.dump(sm, open(smf, 'w', encoding='ascii'), indent=1)
rc, last = run(r2, '--before', 'w145_01')
ok &= check('g14 (c)(2) the start manifest rewritten after its row -> STOP', rc == 5 and '(c)(2) runs145/cache_start.json '
            'sha256' in last and '(the reference was rewritten)' in last, reasons(last))
os.remove(smf)
rc, last = run(r2, '--before', 'w145_01')
ok &= check('g14 (c)(2) the start manifest missing -> STOP', rc == 5 and '(c)(2) runs145/cache_start.json missing' in last,
            reasons(last))
r3 = fresh('g14c')
with open(r3 + '/step2/times.txt', 'a', encoding='ascii') as f:
    f.write('2026-10-01T00:00:00Z GATE start PASS; fixture row without the sha\n')
shutil.copyfile(REF, r3 + '/' + G.START_MF)
rows(r3, 'w145_00')
synth_w(r3, 'w145_00', 'ok')
shutil.copyfile(REF, r3 + '/runs145/cache_w145_00.before.json')
rc, last = run(r3, '--before', 'w145_01')
ok &= check('g14 (c)(2) a start row without the sha of the start manifest -> STOP', rc == 5 and
            '(c)(2) no "GATE start PASS" row naming the sha256 of runs145/cache_start.json' in last, reasons(last))
# g15: item 295 (v) - the W form rows of the score
SC15 = (('(b)(1)', 'W 295(b)(1) 0 layer limit lines (x) (1)'), ('(b)(2)', 'W 295(b)(2) validation active: x (0)'),
        ('(b)(3)', 'W 295(b)(3) the last validation-layer line of the log x (none)'),
        ('(b)(4)', 'W 295(b)(4) form line "W form: limit=100000000 filter=none" x (W form: limit=1000000 filter=none)'))
for tg in ('w145_00', 'w145_01'):
    for mem, row in SC15:
        r = fresh('g15_%s_%s' % (tg, mem[4]))
        prev = {'w145_00': (), 'w145_01': ('w145_00',)}[tg]
        rows(r, 'start', *(prev + (tg,)))
        for t in prev:
            synth_w(r, t, 'ok')
        synth_w(r, tg, 'ok', score='TAG %s\n  admission: FAIL ' + row + '\n')
        shutil.copyfile(REF, r + '/runs145/cache_w145_00.before.json')
        nxt = G.sc145.SEQ[G.sc145.SEQ.index(tg) + 1]
        rc, last = run(r, '--before', nxt)
        ok &= check('g15 %s failing the row %s in its score -> STOP (v) naming it' % (tg, mem), rc == 5 and
                    '(v) W %s fails the W form row(s) %s of item 295 (b)' % (tg, mem) in last and
                    '%s W form rows of item 295 (b) %s' % (tg, mem) in last, reasons(last))
r = fresh('g15b')
rows(r, 'start', 'w145_01')
synth_w(r, 'w145_01', 'ok', score='TAG %s\n  admission: FAIL video x (y); W 295(b)(1) a (1); W 295(b)(3) b (none)\n')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g15 two failing W rows -> STOP (v) naming both', rc == 5 and
            '(v) W w145_01 fails the W form row(s) (b)(1),(b)(3) of item 295 (b)' in last, reasons(last))
synth_w(r, 'w145_01', 'ok', score=None)
os.remove(r + '/score_w145_01.txt')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g15 the W score missing -> STOP (v) not evaluable', rc == 5 and
            '(v) W w145_01: score_w145_01.txt missing - the W form rows of item 295 (b) not evaluable' in last, reasons(last))
synth_w(r, 'w145_01', 'ok', score='TAG %s\n  no line\n')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g15 a W score without its admission line -> STOP (v)', rc == 5 and
            '(v) W w145_01 fails the W form row(s) no admission line' in last, reasons(last))
synth_w(r, 'w145_01', 'ok', score='TAG %s\n  admission: FAIL gates empty (shipped defaults) (x)\n')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g15 another admission failure of the W -> no (v) stop', rc == 0 and '(v)' not in reasons(last), last)
r = fresh('g15c')
rows(r, 'start', 'w145_01')
synth_w(r, 'w145_01', 'ok')
sc_lines = [b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features, version = 2',
            b'[Vulkan][W][1]: Removing layer X because it is a duplicate',
            b'GuestOut: Level has started: rocket_hourglass'] + [
    ('FrameTrace: n=%d dt_us=150000 lat_us=5 gpu_proc=0 draws=3000 dispatches=1 faults=0' % n).encode() for n in range(1, 400)]
open(r + '/log_w145_01.txt', 'wb').write(b''.join(x + b'\n' for x in sc_lines))
pr15 = r + '/pred15.md'
open(pr15, 'w', encoding='utf-8').write('fixture seal g15c\n')
b15 = io.StringIO()
with contextlib.redirect_stdout(b15):
    G.sc145.main(['--tag', 'w145_01'], root=r, pred=pr15)
open(r + '/score_w145_01.txt', 'w', encoding='ascii').write(b15.getvalue())
rc, last = run(r, '--before', 'v145_02')
ok &= check('g15 the score of a held W without validation-layer lines written by the scorer sc145.py --tag -> STOP (v) '
            '(b)(2),(b)(3); (b)(1) and (b)(4) pass', rc == 5 and
            '(v) W w145_01 fails the W form row(s) (b)(2),(b)(3) of item 295 (b)' in last, reasons(last))
# g16: item 295 (v) - the free space of C: at --start
r = fresh('g16')
sp = seal144(r + '/pred.md')
G.disk_free = lambda p: 60 * 2 ** 30
rc, last = run(r, '--start', '--live-manifest', same, '--pred', sp)
ok &= check('g16 exactly 60 GiB free -> PASS; the row prints bytes, GiB and GB', rc == 0 and
            '(s) free on C:/ 64424509440 bytes = 60.0 GiB = 64.4 GB (STOP below 64424509440 bytes = 60 GiB)' in last, last)
G.disk_free = lambda p: 60 * 2 ** 30 - 1
rc, last = run(r, '--start', '--live-manifest', same, '--pred', sp)
ok &= check('g16 1 byte less than 60 GiB -> STOP (s)', rc == 5 and '(s) free space on C:/ 60.0 GiB < 60 GiB (item 295 (v))'
            in last, reasons(last))
G.disk_free = lambda p: FREE_OK
ok &= check('g16 the constants: 60 GiB, the disk C:/, the seal pred/03_sc145.md', G.MIN_FREE == 64424509440 and
            G.DISK == 'C:/' and G.PRED == 'C:/kyty/s145/pred/03_sc145.md', G.MIN_FREE)
# g17: item 295 (e) - the seal line of the reference
r = fresh('g17')
rc, last = run(r, '--start', '--live-manifest', same, '--pred', seal144(r + '/pred.md'))
ok &= check('g17 the reference sha = its seal line -> PASS, the row names both', rc == 0 and
            '(r) reference cache_w144_20.after.json sha256 %s (seal %s)' % (sha(REF)[:16], sha(REF)[:16]) in last, last)
rc, last = run(r, '--start', '--live-manifest', same, '--pred', seal144(r + '/pred2.md', ref_sha='a' * 64))
ok &= check('g17 a seal line with another sha -> STOP (r)', rc == 5 and '(r) the reference cache_w144_20.after.json sha256 %s '
            '!= its seal line %s (item 295 (e))' % (sha(REF)[:16], 'a' * 16) in last, reasons(last))
rc, last = run(r, '--start', '--live-manifest', same, '--pred', seal144(r + '/pred3.md', ref_line=False))
ok &= check('g17 a seal without the line -> STOP (r)', rc == 5 and '!= its seal line none (item 295 (e))' in last,
            reasons(last))
rc, last = run(r, '--start', '--live-manifest', same, '--pred', seal144(r + '/pred.md'), '--ref', r + '/none.json')
ok &= check('g17 a missing reference -> STOP (r)', rc == 5 and '(r) the reference none.json sha256 MISSING' in last,
            reasons(last))
rc, last = run(r, '--start', '--live-manifest', same, '--pred', seal144(r + '/pred4.md', ref_line=False), '--ref',
               r + '/none.json')
ok &= check('g17 a missing reference and a seal without its line -> STOP (r)', rc == 5 and
            '(r) the reference none.json sha256 MISSING != its seal line none' in last, reasons(last))
# g15d: a W made by its attempt marker only (no json, no log)
r = fresh('g15d')
rows(r, 'start', 'w145_01')
open(r + '/attempt_w145_01.txt', 'w', encoding='ascii').write('made\n')
rc, last = run(r, '--before', 'v145_02')
ok &= check('g15d a W made without json -> STOP (f) NO JSON and (v) score missing', rc == 5 and
            '(f) W w145_01: the form line "NO JSON"' in last and '(v) W w145_01: score_w145_01.txt missing' in last,
            reasons(last))
print('checks: %d / %s' % (NCHECK[0], 'ALL OK' if not FAILS else 'FAILED %d: %s' % (len(FAILS), ', '.join(FAILS))))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
