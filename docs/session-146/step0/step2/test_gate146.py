"""test_gate146.py - the fixtures of step2/gate146.py (step 0 HPP-386; ROADMAP s122 item 309 (k), (l)(5), item 300 (b)(2)-(4),
item 295 (v)-(e); new suite for the port of gate145.py - synthetic fixtures, one case per member and per edge):
  k1  --start: the live manifest = the reference (the manifest after the warm-up i146_v, sealed) -> PASS, writes
      runs146/cache_start.json (= the manifest read) and names its sha256 in the row
  k2  --start (c)(1): a translation-cache file or the variant pipelines.bin changed -> STOP; only a GLCache / _PipelineCache file
      changed, added or removed -> PASS with "(c)(1) info driver caches:" naming the file
  k3  --start (r): the reference sha != its seal line, a seal without the line, a missing reference -> STOP (r)
  k4  --start (s): 60 GiB free -> PASS, 1 byte less -> STOP (s); the row prints bytes, GiB, GB
  k5  --before w146_00 (the first tag): no "GATE start PASS" row -> STOP; with it -> PASS
  k6  W form on the shipment binary (b): a made W whose json env carries KYTY_PIPELINE_PRECACHE (0, 1 or empty) -> STOP (b);
      without it -> PASS (its ShaderSeed / PipelinePrecache lines are data, not a STOP); no json -> STOP (b)
  k7  (f): the form line of item 295 (b)(4) failing (limit 1000000, a filter, no limit) -> STOP (f)
  k8  (v): a W score failing one "W 295(b)(N)" row, the score missing, no admission line -> STOP (v)
  k9  (l): the control w146_00 with a layer limit line (log or stdout) -> STOP (l)
  k10 (c)(2): the control's before manifest = the start manifest -> PASS; one shader file differs -> STOP; the start manifest
      rewritten after its row -> STOP; missing -> STOP
  k11 (w): a window event on the made tag right before (minimized, Recovering in the stdout) -> STOP; lost focus only -> PASS
  k12 V (b)/(e): 0 ShaderSeed lines -> STOP (b); the admission line failing by "V positive control" -> STOP (e); score missing
      -> STOP (e)
  k13 item 309 (k)(1): a skipped W (skipped_<w>.txt) right before the tag is passed over to the made V before it; a tag
      before the made tag neither made nor skipped -> STOP
  k14 a made tag without its GATE row -> STOP (ungated call)
  k15 (g): the last two made W both with json outcome timeout before any GuestOut line -> STOP; one after GuestOut -> PASS
  k16 the constants: the root, the times, the reference and its seal name, the seal, 60 GiB, the start manifest, the strict and
      driver roots; no name of 145 in the code; ASCII and LF
  k17 the output in strict cp1250 without PYTHONIOENCODING (the gate under test as a child)
The suite is in the mutlib early-exit form: the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is
`sys.exit(0 if ok else 1)`.  Work dir C:/kyty/s146/step2/fx_gate.  The first line names the suite and the target by sha256;
the output ends ALL OK.
    python test_gate146.py [<gate146.py under test>] > test_gate146.out.txt
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
SRC = sys.argv[1] if len(sys.argv) > 1 else HERE + '/gate146.py'
print('suite test_gate146.py sha256 %s target gate146.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('gate146_under_test', SRC)
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)
S = G.sc146
BASE = Path('C:/kyty/s146/step2/fx_gate')
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
N = [0]
G.disk_free = lambda p: 100 * 2 ** 30
FORM = {'VK_LAYER_PATH': 'C:/VulkanSDK/1.4.357.0/Bin', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000'}
PASS_SCORE = 'TAG %s\n  admission: PASS\n'
SHADER = [['shader', 'a.bin', 10, 1, 'aa' * 32], ['shader', 'variant_fixb26_fixb1b/pipelines.bin', 20, 1, 'bb' * 32],
          ['shader', 'variant_fixb26_fixb1b/b.bin', 30, 1, 'cc' * 32]]
DRIVER = [['pipeline', 'p.bin', 5, 1, 'dd' * 32], ['glcache', 'g1', 6, 1, 'ee' * 32]]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def manifest(files):
    return dict(taken_utc='x', roots=[['shader', 's', True], ['pipeline', 'p', True], ['glcache', 'g', True]], files=files)


def fresh(name, ref_files=None, seal_ok=True):
    d = BASE / name
    (d / 'runs146').mkdir(parents=True)
    (d / 'step2').mkdir()
    (d / 'pred').mkdir()
    ref = d / 'runs146' / 'cache_i146_v.after.json'
    ref.write_text(json.dumps(manifest(SHADER + DRIVER if ref_files is None else ref_files)), encoding='ascii')
    sh = hashlib.sha256(ref.read_bytes()).hexdigest() if seal_ok else 'ff' * 32
    (d / 'pred' / '01_sc146.md').write_text('seal: %s runs146/cache_i146_v.after.json\n' % sh, encoding='utf-8')
    return d


def gate(d, *args, live=None):
    a = list(args) + ['--root', d.as_posix(), '--times', (d / 'step2' / 'times.txt').as_posix(), '--pred',
                      (d / 'pred' / '01_sc146.md').as_posix(), '--ref', (d / 'runs146' / 'cache_i146_v.after.json').as_posix()]
    if live is not None:
        lp = d / 'live.json'
        lp.write_text(json.dumps(manifest(live)), encoding='ascii')
        a += ['--live-manifest', lp.as_posix()]
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = G.main(a)
    return rc, b.getvalue().strip()


def rows(d, *what):
    with open(d / 'step2' / 'times.txt', 'a', encoding='ascii') as f:
        for w in what:
            if w == 'start':
                shutil.copyfile(d / 'runs146' / 'cache_i146_v.after.json', d / 'runs146' / 'cache_start.json')
                f.write('2026-10-02T00:00:00Z GATE start PASS; start manifest runs146/cache_start.json sha256 %s\n' %
                        hashlib.sha256((d / 'runs146' / 'cache_start.json').read_bytes()).hexdigest())
            else:
                f.write('2026-10-02T00:00:00Z GATE %s PASS; x\n' % w)


def mkw(d, tag, env=None, log=(b'ShaderSeed: x', b'PipelinePrecache: 10 recipes -> 1', b'GuestOut: a'), std=(),
        score=PASS_SCORE, outcome='ok', before_mf=True):
    json.dump(dict(tag=tag, attempts=[dict(outcome=outcome, level=S.level_of(tag))], env=dict(FORM if env is None else env),
                   cmdline=[]), open(d / ('%s.json' % tag), 'w', encoding='utf-8'))
    (d / ('log_%s.txt' % tag)).write_bytes(b''.join(x + b'\n' for x in log))
    (d / ('stdout_%s.txt' % tag)).write_bytes(b''.join(x + b'\n' for x in std))
    if score is not None:
        (d / ('score_%s.txt' % tag)).write_text(score % tag if '%s' in score else score, encoding='ascii')
    if tag == 'w146_00' and before_mf:
        shutil.copyfile(d / 'runs146' / 'cache_i146_v.after.json', d / 'runs146' / 'cache_w146_00.before.json')


def mkv(d, tag, log=(b'ShaderSeed: x', b'GuestOut: a'), std=(), score=PASS_SCORE):
    json.dump(dict(tag=tag, attempts=[dict(outcome='ok', level=S.level_of(tag))], env={}, cmdline=[]),
              open(d / ('%s.json' % tag), 'w', encoding='utf-8'))
    (d / ('log_%s.txt' % tag)).write_bytes(b''.join(x + b'\n' for x in log))
    (d / ('stdout_%s.txt' % tag)).write_bytes(b''.join(x + b'\n' for x in std))
    if score is not None:
        (d / ('score_%s.txt' % tag)).write_text(score % tag if '%s' in score else score, encoding='ascii')


ok = True
d = fresh('k1')
rc, out = gate(d, '--start', live=SHADER + DRIVER)
st = d / 'runs146' / 'cache_start.json'
ok &= case('k1 --start with the live manifest = the reference -> PASS; it writes the start manifest (its files = the manifest read) '
           'and names its sha256', rc == 0 and ' GATE start PASS' in out and st.is_file() and
           json.load(open(st))['files'] == SHADER + DRIVER and
           'start manifest runs146/cache_start.json sha256 %s' % hashlib.sha256(st.read_bytes()).hexdigest() in out)
for i, (name, live, want) in enumerate((
        ('a shader root file changed', [SHADER[0][:4] + ['ab' * 32]] + SHADER[1:] + DRIVER, 5),
        ('the variant pipelines.bin changed', SHADER[:1] + [SHADER[1][:4] + ['ab' * 32]] + SHADER[2:] + DRIVER, 5),
        ('a shader file added', SHADER + [['shader', 'variant_fixb26_fixb1b/n.bin', 1, 1, 'ab' * 32]] + DRIVER, 5),
        ('a shader file removed', SHADER[:2] + DRIVER, 5),
        ('a GLCache file changed', SHADER + DRIVER[:1] + [DRIVER[1][:4] + ['ab' * 32]], 0),
        ('a GLCache file added', SHADER + DRIVER + [['glcache', 'g2', 1, 1, 'ab' * 32]], 0),
        ('a _PipelineCache file removed', SHADER + DRIVER[1:], 0))):
    d = fresh('k2_%d' % i)
    rc, out = gate(d, '--start', live=live)
    ok &= case('k2 --start: %s -> rc %d%s' % (name, want, ' (c)(1) STOP' if want else ' with the driver info naming the file'),
               rc == want and ((('(c) shader differs from the end of the warm-up i146_v' in out) if want else
                                ('(c)(1) info driver caches:' in out and ('g2' in out or 'g1' in out or 'p.bin' in out)))))
d = fresh('k3a', seal_ok=False)
rc1, o1 = gate(d, '--start', live=SHADER + DRIVER)
d = fresh('k3b')
(d / 'pred' / '01_sc146.md').write_text('no line\n', encoding='utf-8')
rc2, o2 = gate(d, '--start', live=SHADER + DRIVER)
d = fresh('k3c')
(d / 'runs146' / 'cache_i146_v.after.json').unlink()
rc3, o3 = gate(d, '--start', live=SHADER + DRIVER)
ok &= case('k3 --start (r): the reference sha != its seal line, a seal without the line, a missing reference -> STOP (r); no start '
           'manifest without the reference', rc1 == 5 and '(r) the reference' in o1 and rc2 == 5 and '(r)' in o2 and
           rc3 == 5 and '(r)' in o3 and not (d / 'runs146' / 'cache_start.json').exists())
G.disk_free = lambda p: 60 * 2 ** 30
d = fresh('k4a')
rc1, o1 = gate(d, '--start', live=SHADER + DRIVER)
G.disk_free = lambda p: 60 * 2 ** 30 - 1
d = fresh('k4b')
rc2, o2 = gate(d, '--start', live=SHADER + DRIVER)
G.disk_free = lambda p: 100 * 2 ** 30
ok &= case('k4 --start (s): 60 GiB free -> PASS; 1 byte less -> STOP (s); the row prints bytes, GiB and GB',
           rc1 == 0 and rc2 == 5 and '(s) free space on C:/' in o2 and '%d bytes = 60.0 GiB = 64.4 GB' % (60 * 2 ** 30) in o1)
d = fresh('k5')
rc1, o1 = gate(d, '--before', 'w146_00')
rows(d, 'start')
rc2, o2 = gate(d, '--before', 'w146_00')
ok &= case('k5 --before w146_00: no start row -> STOP; with the start row -> PASS', rc1 == 5 and 'no "GATE start PASS" row' in o1
           and rc2 == 0)
for i, (name, env, want) in enumerate((('KYTY_PIPELINE_PRECACHE=0', dict(FORM, KYTY_PIPELINE_PRECACHE='0'), 5),
                                       ('KYTY_PIPELINE_PRECACHE=1', dict(FORM, KYTY_PIPELINE_PRECACHE='1'), 5),
                                       ('KYTY_PIPELINE_PRECACHE empty', dict(FORM, KYTY_PIPELINE_PRECACHE=''), 5),
                                       ('the form of item 300 (b)(4) with ShaderSeed / PipelinePrecache lines', FORM, 0))):
    d = fresh('k6_%d' % i)
    rows(d, 'start', 'w146_00')
    mkw(d, 'w146_00', env=env)
    rc, out = gate(d, '--before', 'r146_01')
    ok &= case('k6 (b) the control W with %s -> rc %d' % (name, want), rc == want and (
        ('(b) W w146_00: KYTY_PIPELINE_PRECACHE=' in out) if want else 'ShaderSeed/PipelinePrecache log 1/1' in out))
d = fresh('k6n')
rows(d, 'start', 'w146_00')
(d / 'attempt_w146_00.txt').write_text('made\n')
rc, out = gate(d, '--before', 'r146_01')
ok &= case('k6n (b) a made W without json -> STOP (b) not evaluable', rc == 5 and '(b) W w146_00: no json' in out)
for i, (name, env) in enumerate((('limit 1000000', dict(FORM, VK_LAYER_DUPLICATE_MESSAGE_LIMIT='1000000')),
                                 ('a message filter', dict(FORM, VK_LAYER_MESSAGE_ID_FILTER='x')),
                                 ('no limit', {'VK_LAYER_PATH': 'C:/VulkanSDK/1.4.357.0/Bin'}))):
    d = fresh('k7_%d' % i)
    rows(d, 'start', 'w146_00')
    mkw(d, 'w146_00', env=env)
    rc, out = gate(d, '--before', 'r146_01')
    ok &= case('k7 (f) the W form line with %s -> STOP (f)' % name, rc == 5 and '(f) W w146_00: the form line' in out)
for i, (name, score, frag) in enumerate((
        ('one row W 295(b)(2) failing', 'TAG w146_00\n  admission: FAIL W 295(b)(2) validation active (0)\n', '(v) W w146_00 fails'),
        ('two rows', 'TAG w146_00\n  admission: FAIL W 295(b)(1) x (1); W 295(b)(3) y (none)\n', '(b)(1),(b)(3)'),
        ('the score missing', None, 'score_w146_00.txt missing'),
        ('no admission line', 'TAG w146_00\n', 'no admission line'))):
    d = fresh('k8_%d' % i)
    rows(d, 'start', 'w146_00')
    mkw(d, 'w146_00', score=score)
    rc, out = gate(d, '--before', 'r146_01')
    ok &= case('k8 (v) %s -> STOP (v)' % name, rc == 5 and '(v)' in out and frag in out)
for i, (log, std) in enumerate((((b'ShaderSeed: x', b'GuestOut: a', G.LIMIT), ()), ((b'ShaderSeed: x', b'GuestOut: a'), (G.LIMIT,)))):
    d = fresh('k9_%d' % i)
    rows(d, 'start', 'w146_00', 'r146_01')
    mkw(d, 'w146_00', log=log, std=std)
    mkv(d, 'r146_01')
    rc, out = gate(d, '--before', 'r146_02')
    ok &= case('k9 (l) the control with a layer limit line in its %s -> STOP (l)' % ('log', 'stdout')[i],
               rc == 5 and '(l) the control W w146_00 has 1 layer limit line(s)' in out)
d = fresh('k10')
rows(d, 'start', 'w146_00', 'r146_01')
mkw(d, 'w146_00')
mkv(d, 'r146_01')
rc1, o1 = gate(d, '--before', 'r146_02')
(d / 'runs146' / 'cache_w146_00.before.json').write_text(json.dumps(manifest([SHADER[0][:4] + ['ab' * 32]] + SHADER[1:] + DRIVER)))
rc2, o2 = gate(d, '--before', 'r146_02')
shutil.copyfile(d / 'runs146' / 'cache_i146_v.after.json', d / 'runs146' / 'cache_w146_00.before.json')
(d / 'runs146' / 'cache_start.json').write_text(json.dumps(manifest(SHADER + DRIVER)) + ' ')
rc3, o3 = gate(d, '--before', 'r146_02')
(d / 'runs146' / 'cache_start.json').unlink()
rc4, o4 = gate(d, '--before', 'r146_02')
ok &= case('k10 (c)(2): the control before manifest = the start manifest -> PASS; one shader file differs -> STOP; the start '
           'manifest rewritten -> STOP; missing -> STOP', rc1 == 0 and rc2 == 5 and
           '(c)(2) shader differs from the start manifest' in o2 and rc3 == 5 and 'the reference was rewritten' in o3 and
           rc4 == 5 and '(c)(2) runs146/cache_start.json missing' in o4)
for i, (name, log, std, want) in enumerate((
        ('Window 1 minimized in the log', (b'ShaderSeed: x', b'Window 1 minimized'), (), 5),
        ('Recovering Vulkan swapchain in the stdout', (b'ShaderSeed: x',), (b'Recovering Vulkan swapchain (x)',), 5),
        ('lost keyboard focus only', (b'ShaderSeed: x', b'Window 1 lost keyboard focus'), (), 0))):
    d = fresh('k11_%d' % i)
    rows(d, 'start', 'w146_00', 'r146_01')
    mkw(d, 'w146_00')
    mkv(d, 'r146_01', log=log, std=std)
    rc, out = gate(d, '--before', 'r146_02')
    ok &= case('k11 (w) %s on the V right before -> rc %d' % (name, want), rc == want and (('(w) window event on r146_01' in out)
                                                                                     if want else True))
for i, (name, log, score, frag) in enumerate((
        ('0 ShaderSeed lines', (b'GuestOut: a',), PASS_SCORE, '(b) V r146_01: 0 ShaderSeed: lines'),
        ('V positive control failing', (b'ShaderSeed: x',), 'TAG r146_01\n  admission: FAIL V positive control: >= 1 (log 0)\n',
         '(e) V r146_01 rejected by a form member: V positive control'),
        ('the score missing', (b'ShaderSeed: x',), None, '(e) V r146_01: score_r146_01.txt missing'))):
    d = fresh('k12_%d' % i)
    rows(d, 'start', 'w146_00', 'r146_01')
    mkw(d, 'w146_00')
    mkv(d, 'r146_01', log=log, score=score)
    rc, out = gate(d, '--before', 'r146_02')
    ok &= case('k12 V %s -> STOP' % name, rc == 5 and frag in out)
d = fresh('k13')
pre = ['w146_00', 'r146_01', 'r146_02', 'r146_03', 'r146_04', 'v146_05', 'w146_05']
rows(d, 'start', *pre)
mkw(d, 'w146_00')
for x in ('r146_01', 'r146_02', 'r146_03', 'r146_04'):
    mkv(d, x)
mkv(d, 'v146_05', log=(b'ShaderSeed: x', b'Window 1 minimized'))
(d / 'skipped_w146_05.txt').write_text('SKIPPED_V_NOT_ENTERED w146_05 x\n')
rc1, o1 = gate(d, '--before', 'v146_06')
mkv(d, 'v146_05')
rc2, o2 = gate(d, '--before', 'v146_06')
(d / 'skipped_w146_05.txt').unlink()
rc3, o3 = gate(d, '--before', 'v146_06')
ok &= case('k13 item 309 (k)(1): the skipped W right before is passed over to the made V before it (its window event STOPs, '
           'clean -> PASS); the W neither made nor skipped -> STOP "not made"',
           rc1 == 5 and 'w146_05 SKIPPED_V_NOT_ENTERED (item 309 (k)(1)) - passed over' in o1 and '(w) window event on v146_05' in o1
           and rc2 == 0 and rc3 == 5 and 'the tag w146_05 before v146_06 was not made' in o3)
d = fresh('k14')
rows(d, 'start', 'w146_00')
mkw(d, 'w146_00')
mkv(d, 'r146_01')
rc, out = gate(d, '--before', 'r146_02')
ok &= case('k14 a made tag without its GATE row -> STOP (ungated call)', rc == 5 and 'made tag r146_01 has no "GATE r146_01 PASS" row'
           in out)
d = fresh('k15')
pre = ['w146_00', 'r146_01', 'r146_02', 'r146_03', 'r146_04', 'v146_05', 'w146_05', 'v146_06', 'w146_06']
rows(d, 'start', *pre)
mkw(d, 'w146_00')
for x in ('r146_01', 'r146_02', 'r146_03', 'r146_04', 'v146_05', 'v146_06'):
    mkv(d, x)
mkw(d, 'w146_05', outcome='timeout', log=(b'ShaderSeed: x', b'PipelinePrecache: 1 recipes -> 1'))
mkw(d, 'w146_06', outcome='timeout', log=(b'ShaderSeed: x', b'PipelinePrecache: 1 recipes -> 1'))
rc1, o1 = gate(d, '--before', 'v146_07')
mkw(d, 'w146_06', outcome='timeout', log=(b'ShaderSeed: x', b'GuestOut: a'))
rc2, o2 = gate(d, '--before', 'v146_07')
ok &= case('k15 (g): two W in a row with json outcome timeout before any GuestOut line -> STOP; the second after GuestOut -> PASS',
           rc1 == 5 and '(g) two W in a row with the key attempt:timeout: w146_05,w146_06' in o1 and rc2 == 0)
TXT = Path(SRC).read_bytes().decode('ascii')
CODE = TXT[TXT.index('import argparse'):]
ok &= case('k16 the constants: root s146, times, the reference runs146/cache_i146_v.after.json and its seal name, the seal '
           'pred/01_sc146.md, 60 GiB, the start manifest runs146/cache_start.json, strict = shader, driver = pipeline + glcache; '
           'no name of 145 in the code; ASCII and LF',
           G.ROOT == 'C:/kyty/s146' and G.TIMES == 'C:/kyty/s146/step2/times.txt' and
           G.REF == 'C:/kyty/s146/runs146/cache_i146_v.after.json' and G.REF_SEAL == 'runs146/cache_i146_v.after.json' and
           G.PRED == 'C:/kyty/s146/pred/01_sc146.md' and G.MIN_FREE == 60 * 2 ** 30 and G.START_MF == 'runs146/cache_start.json'
           and G.STRICT == ('shader',) and G.DRIVER == ('pipeline', 'glcache') and '145' not in CODE and '144' not in CODE and
           '\r' not in TXT)
dr = BASE / 'drv.py'
kd = fresh('k17')
dr.write_text('import sys, importlib.util\ns = importlib.util.spec_from_file_location("g", %r)\nG = importlib.util.module_from_spec(s)\n'
              's.loader.exec_module(G)\nG.disk_free = lambda p: 100 * 2 ** 30\n'
              'sys.exit(G.main(["--before", "w146_00", "--root", %r, "--times", %r, "--pred", %r]))\n' % (
                  SRC, kd.as_posix(), (kd / 'step2' / 'times.txt').as_posix(), (kd / 'pred' / '01_sc146.md').as_posix()),
              encoding='utf-8')
env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env2['PYTHONUTF8'] = '0'
pp = subprocess.run([sys.executable, str(dr)], capture_output=True, env=env2, timeout=120)
try:
    pp.stdout.decode('cp1250', errors='strict')
    enc = pp.returncode == 5 and b' GATE w146_00 STOP ' in pp.stdout and all(b < 128 for b in pp.stdout)
except UnicodeError:
    enc = False
ok &= case('k17 the gate in a child without PYTHONIOENCODING (console cp1250): ASCII row, rc 5 (no start row)', enc)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
