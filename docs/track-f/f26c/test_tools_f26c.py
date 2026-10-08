"""F26c (HPP-692): fixtures of the chain tools - go_f26c.sh tag names (dry run), post_f26c.sh usage, queue_f26c.py (P > F > S),
runchk_f26c.py, guard_f26c.py block of 10 tags (item 630 (d)(3)) and the 600 s gap (item 534 (v)(3)), enter_scene.py option
--entry-at-level present.  First line names the suite and the targets with sha256; last line ALL OK.  ASCII only."""
import hashlib, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
W = HERE + '/fxtools'
shutil.rmtree(W, ignore_errors=True)
os.makedirs(W)
sha = lambda p: hashlib.sha256(open(HERE + '/' + p, 'rb').read()).hexdigest()[:16]  # noqa: E731
T = ['go_f26c.sh', 'post_f26c.sh', 'queue_f26c.py', 'runchk_f26c.py', 'guard_f26c.py', 'enter_scene.py']
print('suite test_tools_f26c.py sha256 %s targets %s' % (hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), ' '.join('%s %s' % (t, sha(t)) for t in T)))
bad = []
BASH = 'C:/Program Files/Git/bin/bash.exe' if os.path.exists('C:/Program Files/Git/bin/bash.exe') else 'bash'


def check(name, cond):
    print('%s %s' % ('ok  ' if cond else 'FAIL', name))
    if not cond:
        bad.append(name)


def run(args, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(args, capture_output=True, env=e)


for t in ('b25_01', 'b25_09', 'b25_10', 'b25_49', 'b25_50', 'b25_55', 'base', 'return'):
    c = run([BASH, HERE + '/go_f26c.sh', t], {'F26C_DRYRUN': '1'})
    check('go dry run accepts %s (hold 120, timeout 60, knobs of fs10_v)' % t, c.returncode == 0 and b'hold 120' in c.stdout and b'timeout 60' in c.stdout and b'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in c.stdout)
for t in ('b25_00', 'b25_56', 'b25_1', 'b25_100', 'fs10_v', ''):
    c = run([BASH, HERE + '/go_f26c.sh', t], {'F26C_DRYRUN': '1'})
    check('go refuses %r with rc 2' % t, c.returncode == 2)
c = run([BASH, HERE + '/post_f26c.sh', 'fs10_v'])
check('post refuses a foreign tag with rc 2', c.returncode == 2)
# queue
q = W + '/q.json'
json.dump([{'identifier': 'HPP-1', 'status': 'todo', 'title': 'track P link'}, {'identifier': 'HPP-692', 'status': 'in_progress', 'title': 'track F'}], open(q, 'w'))
c = run([sys.executable, HERE + '/queue_f26c.py', '--fake', q]); check('queue: a ready P link -> BUSY rc 1', c.returncode == 1 and b'QUEUE BUSY' in c.stdout)
json.dump([{'identifier': 'HPP-2', 'status': 'in_progress', 'title': 'track S link'}, {'identifier': 'HPP-3', 'status': 'blocked', 'title': 'track P x'},
           {'identifier': 'HPP-692', 'status': 'in_progress', 'title': 'track P own'}], open(q, 'w'))
c = run([sys.executable, HERE + '/queue_f26c.py', '--fake', q]); check('queue: S ready, P blocked, own skipped -> FREE rc 0', c.returncode == 0 and b'QUEUE FREE' in c.stdout)
# runchk
r = W + '/r.json'
json.dump({'executionRunId': 'abc', 'status': 'in_progress'}, open(r, 'w'))
c = run([sys.executable, HERE + '/runchk_f26c.py', '--fake', r], {'F26C_RUN_ID': 'abc'}); check('runchk: own run alive rc 0', c.returncode == 0)
c = run([sys.executable, HERE + '/runchk_f26c.py', '--fake', r], {'F26C_RUN_ID': 'xyz'}); check('runchk: other run -> GONE rc 1', c.returncode == 1)
# guard block of 10
sys.path.insert(0, HERE)
import guard_f26c as GD  # noqa: E402
b = W + '/block.txt'
import time
T0 = int(time.time()) - 5000
GD.block_add(b, 'CLEAN', T0)
rc, word = GD.open_block(b, [], T0 + 599)
check('open-block 599 s after a clean check: PENDING', rc == 9)
rc, word = GD.open_block(b, [], T0 + 600)
check('open-block 600 s after a clean check: OPEN', rc == 0 and word == 'OPEN')
for i in range(9):
    GD.main(['tag', 'b25_%02d' % (i + 1), '--block', b])
check('9 tags: block open', GD.block_state(GD.block_lines(b)) == ('open', 9))
GD.main(['tag', 'b25_10', '--block', b])
check('10th tag closes the block (CLOSE limit10)', GD.block_state(GD.block_lines(b))[0] == 'closed' and 'CLOSE limit10' in open(b).read())
T1 = int(time.time()) + 1
rc, word = GD.open_block(b, [], T1 + 100)
check('after the close a new block needs a fresh 600 s gap: PENDING', rc == 9)
rc, word = GD.open_block(b, [], T1 + 700)
check('600 s after the clean check past the close: OPEN', rc == 0)
rc, word = GD.open_block(W + '/b2.txt', [{'pid': 1}], 5000.0)
check('a found user process closes: rc 7', rc == 7)
src = open(HERE + '/enter_scene.py', encoding='utf-8').read()
check('enter_scene.py has --entry-at-level and ROOT f287/f26c', "'--entry-at-level'" in src and "ROOT = pathlib.Path('C:/kyty/f287/f26c')" in src)
c = run([sys.executable, HERE + '/enter_scene.py', '--help'])
check('enter_scene.py imports resolve in f26c (--help rc 0, option --entry-at-level listed; seal 2)', c.returncode == 0 and b'--entry-at-level' in c.stdout)
for helper in ('tempo_f26c.py', 'f26c_read.py', 'guard_f26c.py', 'hold_f26c.py', 'dispstate.py', 'procload.py', 'manifest_fs4c.py', 'runchk_f26c.py'):
    c = run([sys.executable, '-c', 'import sys; sys.path.insert(0, %r); import %s' % (HERE, helper[:-3])])
    check('import %s resolves' % helper, c.returncode == 0)
src = open(HERE + '/go_f26c.sh', encoding='utf-8').read()
check('go_f26c.sh: a run.txt without the launching line is not a tag (nostart)', "'--- attempt 1: launching'" in src)
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
c = subprocess.run([sys.executable, HERE + '/queue_f26c.py', '--fake', q], capture_output=True, env=env)
check('queue output in strict cp1250 rc 0', c.returncode == 0)
print('ALL OK' if not bad else 'FAILED %d: %s' % (len(bad), bad))
sys.exit(0 if not bad else 1)
