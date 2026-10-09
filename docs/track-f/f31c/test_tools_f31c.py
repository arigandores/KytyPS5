"""F31c (HPP-731): fixtures of the chain tools (port of F26c test_tools_f26c.py without the block of item 534 - item 634 / 660 / 661):
go_f31c.sh tag names (dry run: hold 300, timeout 60, knobs of fs11_v), launch_f31c.sh / post_f31c.sh usage, the form linter
form634_check.py --series on this folder (ALL OK) and a negative control (a guard call put into a copy of the launcher fails), the first
executable line of go_f31c.sh and launch_f31c.sh is the linter, queue_f31c.py (P > F > S), runchk_f31c.py, the gate 1.5 / 4 and
hostload_f31c.py (name masked), enter_scene.py option --entry-at-level and ROOT f287/f31c, imports of the helpers.  First line names the
suite and the targets with sha256; last line ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
W = HERE + '/fxtools'
shutil.rmtree(W, ignore_errors=True)
os.makedirs(W)
sha = lambda p: hashlib.sha256(open(HERE + '/' + p, 'rb').read()).hexdigest()[:16]  # noqa: E731
T = ['go_f31c.sh', 'launch_f31c.sh', 'post_f31c.sh', 'queue_f31c.py', 'runchk_f31c.py', 'enter_scene.py', 'hostload_f31c.py']
print('suite test_tools_f31c.py sha256 %s targets %s' % (hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), ' '.join('%s %s' % (t, sha(t)) for t in T)))
bad = []
BASH = 'C:/Program Files/Git/bin/bash.exe' if os.path.exists('C:/Program Files/Git/bin/bash.exe') else 'bash'
LINT = 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py'


def check(name, cond):
    print('%s %s' % ('ok  ' if cond else 'FAIL', name))
    if not cond:
        bad.append(name)


def run(args, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(args, capture_output=True, env=e)


for t in ('b25m_01', 'b25m_09', 'b25m_10', 'b25m_19', 'b25m_20', 'b25m_29', 'b25m_30', 'b25m_36', 'base', 'return'):
    c = run([BASH, HERE + '/go_f31c.sh', t], {'F31C_DRYRUN': '1'})
    check('go dry run accepts %s (hold 300, timeout 60, mini_giants_garden, knobs of fs11_v)' % t, c.returncode == 0 and b'hold 300' in c.stdout and b'timeout 60' in c.stdout
          and b'level mini_giants_garden' in c.stdout and b'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in c.stdout)
for t in ('b25m_00', 'b25m_37', 'b25m_40', 'b25m_1', 'b25m_100', 'b25_01', 'fs11_v', ''):
    c = run([BASH, HERE + '/go_f31c.sh', t], {'F31C_DRYRUN': '1'})
    check('go refuses %r with rc 2' % t, c.returncode == 2)
for t in ('b25m_37', 'b25_01', ''):
    c = run([BASH, HERE + '/launch_f31c.sh', t], {'F31C_DRYRUN': '2', 'F31C_TIMES': W + '/t.txt', 'F31C_QUEUE_SKIP': '1', 'F31C_DISP_SKIP': '1'})
    check('launch refuses %r with rc 2' % t, c.returncode == 2)
c = run([BASH, HERE + '/post_f31c.sh', 'b25_01'])
check('post refuses a foreign tag with rc 2', c.returncode == 2)
# the form linter (item 661 (b)(1))
c = run([sys.executable, LINT, '--series', HERE])
check('form634_check.py --series f31c: ALL OK', c.returncode == 0 and c.stdout.strip().endswith(b'ALL OK'))
NEG = W + '/neg'
os.makedirs(NEG)
for f in ('go_f31c.sh', 'launch_f31c.sh'):
    shutil.copy(HERE + '/' + f, NEG + '/' + f)
open(NEG + '/launch_f31c.sh', 'a').write('GS=$(python $G/guard_f31c.py check)\n')
c = run([sys.executable, LINT, '--series', NEG])
check('negative control: a guard check in a copy of the launcher fails the linter', c.returncode == 1 and b'FORM634 FAILED' in c.stdout)
for f in ('go_f31c.sh', 'launch_f31c.sh'):
    L = [l for l in open(HERE + '/' + f, encoding='ascii').read().split('\n') if l.strip() and not l.strip().startswith('#')]
    check('%s: first executable line is the linter --series (exit 10)' % f, L[0] == 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f31c || exit 10')
src = open(HERE + '/launch_f31c.sh', encoding='ascii').read()
check('launch has no guard / hold / block word outside comments', not any(w in l for l in src.split('\n') if not l.strip().startswith('#') for w in ('guard_', 'hold_', 'block')))
# queue
q = W + '/q.json'
json.dump([{'identifier': 'HPP-1', 'status': 'todo', 'title': 'track P link'}, {'identifier': 'HPP-731', 'status': 'in_progress', 'title': 'track F'}], open(q, 'w'))
c = run([sys.executable, HERE + '/queue_f31c.py', '--fake', q]); check('queue: a ready P link -> BUSY rc 1', c.returncode == 1 and b'QUEUE BUSY' in c.stdout)
json.dump([{'identifier': 'HPP-2', 'status': 'in_progress', 'title': 'track S link'}, {'identifier': 'HPP-3', 'status': 'blocked', 'title': 'track P x'},
           {'identifier': 'HPP-731', 'status': 'in_progress', 'title': 'track P own'}], open(q, 'w'))
c = run([sys.executable, HERE + '/queue_f31c.py', '--fake', q]); check('queue: S ready, P blocked, own skipped -> FREE rc 0', c.returncode == 0 and b'QUEUE FREE' in c.stdout)
# runchk
r = W + '/r.json'
json.dump({'executionRunId': 'abc', 'status': 'in_progress'}, open(r, 'w'))
c = run([sys.executable, HERE + '/runchk_f31c.py', '--fake', r], {'F31C_RUN_ID': 'abc'}); check('runchk: own run alive rc 0', c.returncode == 0)
c = run([sys.executable, HERE + '/runchk_f31c.py', '--fake', r], {'F31C_RUN_ID': 'xyz'}); check('runchk: other run -> GONE rc 1', c.returncode == 1)
# the gate 1.5 / 4 (item 632 (v)(1) form) and hostload_f31c.py
sys.path.insert(0, HERE)
import procload as PL  # noqa: E402
import hostload_f31c as HL  # noqa: E402


def fake_snaps(rate_a, rate_b):
    s = [{(1, 'idle'): 0.0, (10, 'userjob'): 0.0, (11, 'other'): 0.0}, {(1, 'idle'): 99.0, (10, 'userjob'): rate_a * PL.SPAN, (11, 'other'): rate_b * PL.SPAN}]
    return lambda: s.pop(0)


PL.mutlib_alive = lambda: []
_sleep, _mono = PL.time.sleep, PL.time.monotonic
PL.time.sleep = lambda s: None
for ra, rb, mr, mt, want in ((0.75, 0.1, 0.5, None, 1), (0.75, 0.1, 1.5, 4.0, 0), (1.6, 0.1, 1.5, 4.0, 1), (1.4, 1.4, 1.5, 4.0, 0), (1.4, 1.4, 1.5, 2.5, 1)):
    PL.snapshot = fake_snaps(ra, rb)
    PL.time.monotonic = (lambda it: (lambda: next(it)))(iter([0.0, PL.SPAN]))
    off = PL.offenders(mr, mt)
    check('gate rates %.2f/%.2f at %.1f/%s: offenders %d (want %d)' % (ra, rb, mr, mt, len(off), want), len(off) == want)
PL.time.sleep, PL.time.monotonic = _sleep, _mono
r = HL.measure(snap=fake_snaps(0.75, 0.2), sleep=lambda s: None, span=10.0)
check('hostload: one process above 0.5, name masked, total 0.95', r['over05'] == 1 and r['procs'][0][0] == '<app>' and abs(r['total'] - 0.95) < 1e-6 and 'userjob' not in HL.line(r))
src = open(HERE + '/go_f31c.sh', encoding='ascii').read()
check('go_f31c.sh gate uses 1.5 / 4', src.count('--max-rate 1.5 --max-total 4') == 1)
check('go_f31c.sh: a run.txt without the launching line is not a tag (nostart)', "'--- attempt 1: launching'" in src)
check('go_f31c.sh: FS11 full sha and level mini_giants_garden', 'TB=ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce' in src and 'LV=mini_giants_garden' in src)
check('go_f31c.sh: no KYTY_REC / KYTY_GAME_PATCH / validation / KYTY_GPU_CHECKPOINTS in code lines',
      not any(w in l for l in src.split('\n') if not l.strip().startswith('#') for w in ('KYTY_REC', 'KYTY_GAME_PATCH', '--vulkan-validation', 'KYTY_GPU_CHECKPOINTS', '--rec')))
src = open(HERE + '/enter_scene.py', encoding='utf-8').read()
check('enter_scene.py has --entry-at-level and ROOT f287/f31c', "'--entry-at-level'" in src and "ROOT = pathlib.Path('C:/kyty/f287/f31c')" in src)
check("enter_scene.py env constants KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8' (= fs11_v)", "KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8'" in src)
c = run([sys.executable, HERE + '/enter_scene.py', '--help'])
check('enter_scene.py imports resolve in f31c (--help rc 0, option --entry-at-level listed)', c.returncode == 0 and b'--entry-at-level' in c.stdout)
for helper in ('hostload_f31c.py', 'tempo_f31c.py', 'f31c_read.py', 'guard_f31c.py', 'hold_f31c.py', 'dispstate.py', 'procload.py', 'manifest_fs4c.py',
               'runchk_f31c.py', 'run_safety99.py', 'sweep_f26a.py'):
    c = run([sys.executable, '-c', 'import sys; sys.path.insert(0, %r); import %s' % (HERE, helper[:-3])])
    check('import %s resolves' % helper, c.returncode == 0)
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
c = subprocess.run([sys.executable, HERE + '/queue_f31c.py', '--fake', q], capture_output=True, env=env)
check('queue output in strict cp1250 rc 0', c.returncode == 0)
print('ALL OK' if not bad else 'FAILED %d: %s' % (len(bad), bad))
sys.exit(0 if not bad else 1)
