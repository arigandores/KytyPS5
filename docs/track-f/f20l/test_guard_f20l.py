"""F20l (HPP-631; port of F20e test_guard_f20l.py): fixtures of the guard of the user game (ROADMAP s122 item 534, general rule 33) - guard_f20l.py members and edges, the
pid-only kill of enter_scene.py, the order of the guard in go_f20l.sh and the block checks of launch_f20l.sh (dry run 2).
usage: python test_guard_f20l.py   (ASCII only; the last line is ALL OK)"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
BASH = shutil.which('bash') or 'bash'
sys.path.insert(0, HERE)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_guard_f20l.py sha256 %s target guard_f20l.py sha256 %s go_f20l.sh sha256 %s launch_f20l.sh sha256 %s enter_scene.py sha256 %s'
      % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'guard_f20l.py')), sha(os.path.join(HERE, 'go_f20l.sh')),
         sha(os.path.join(HERE, 'launch_f20l.sh')), sha(os.path.join(HERE, 'enter_scene.py'))))
import guard_f20l as GD  # noqa: E402
import enter_scene as ES  # noqa: E402

fails = []
n = [0]


def check(name, cond):
    n[0] += 1
    if not cond:
        fails.append(name)
        print('FAIL', name)


TD = tempfile.mkdtemp()
UDIR = os.path.join(TD, 'SecretUserFolder')
os.makedirs(UDIR)
open(os.path.join(UDIR, 'kyty_emulator.exe'), 'w').close()
ODIR = os.path.join(TD, 'Elsewhere')
os.makedirs(ODIR)
NOW = time.time()
OWN = (5000, NOW)
P_OWN = dict(pid=5000, name='kyty_emulator.exe', path=os.path.join(TD, 'x', 'kyty_emulator.exe'), start=NOW + 3)
P_OWN_LATE = dict(pid=5000, name='kyty_emulator.exe', path=None, start=NOW + 16)
P_USER_EMU = dict(pid=6000, name='KYTY_EMULATOR.EXE', path=None, start=NOW)
P_LAUNCH = dict(pid=7000, name='SecretLauncher.exe', path=os.path.join(UDIR, 'SecretLauncher.exe'), start=NOW)
P_OTHER = dict(pid=8000, name='SecretTool.exe', path=os.path.join(ODIR, 'SecretTool.exe'), start=NOW)
P_NOPATH = dict(pid=9000, name='SecretSvc.exe', path=None, start=None)
# --- members of user_procs
check('own emulator (pid, start within 15 s) not counted', GD.user_procs([P_OWN], OWN) == [])
check('own pid with start 16 s off = user emulator', GD.user_procs([P_OWN_LATE], OWN) == [(5000, 'emulator')])
check('own emulator without the pid file = user emulator', GD.user_procs([P_OWN], None) == [(5000, 'emulator')])
check('another kyty_emulator.exe (any case, no path) = user emulator', GD.user_procs([P_USER_EMU], OWN) == [(6000, 'emulator')])
check('process beside a kyty_emulator.exe = launcher', GD.user_procs([P_LAUNCH], OWN) == [(7000, 'launcher')])
check('process elsewhere not counted', GD.user_procs([P_OTHER], OWN) == [])
check('process without path not counted', GD.user_procs([P_NOPATH], OWN) == [])
check('pid 0 / 4 / self not counted', GD.user_procs([dict(P_USER_EMU, pid=0), dict(P_USER_EMU, pid=4), dict(P_USER_EMU, pid=os.getpid())], OWN) == [])
allp = [P_OWN, P_USER_EMU, P_LAUNCH, P_OTHER, P_NOPATH]
txt = GD.fmt(GD.user_procs(allp, OWN))
check('fmt: FOUND 2 with <app>', txt.startswith('GUARD FOUND 2:') and txt.count('<app>') == 2)
check('fmt: no input name or path in the output', 'Secret' not in txt and 'kyty_emulator' not in txt.lower() and TD not in txt)
check('fmt: clean', GD.fmt([]) == 'GUARD CLEAN')
# --- CLI scan on a fake list (rc 7 / 0), pid file of the own emulator, cp1250 strict output without PYTHONIOENCODING
FK = os.path.join(TD, 'procs.json')
json.dump(allp, open(FK, 'w'))
PF = os.path.join(TD, 'game_pid.txt')
open(PF, 'w').write('%d %.3f\n' % OWN)
ENV0 = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
p = subprocess.run([sys.executable, os.path.join(HERE, 'guard_f20l.py'), 'scan', '--pidfile', PF, '--fake', FK], capture_output=True, env=ENV0)
out = p.stdout.decode('cp1250', 'strict')
check('cli scan: rc 7, FOUND 2', p.returncode == 7 and 'GUARD FOUND 2' in out and 'Secret' not in out)
json.dump([P_OWN, P_OTHER], open(FK, 'w'))
p = subprocess.run([sys.executable, os.path.join(HERE, 'guard_f20l.py'), 'scan', '--pidfile', PF, '--fake', FK], capture_output=True, env=ENV0)
check('cli scan: own + other -> rc 0 CLEAN (cp1250)', p.returncode == 0 and p.stdout.decode('cp1250', 'strict').strip() == 'GUARD CLEAN')
# --- kill_own: by pid only, only the own emulator
calls = []
keep_run, keep_procs = GD.subprocess.run, GD.procs
GD.subprocess.run = lambda a, **k: calls.append(a) or types.SimpleNamespace(returncode=0)
GD.procs = lambda: [P_OWN, P_USER_EMU]
msg = GD.kill_own(PF)
check('kill_own: taskkill /F /T /PID <own pid> only', calls == [['taskkill', '/F', '/T', '/PID', '5000']] and 'killed by pid' in msg)
calls.clear()
GD.procs = lambda: [P_OWN_LATE, P_USER_EMU]
msg = GD.kill_own(PF)
check('kill_own: own pid reused by another start -> nothing killed', calls == [] and 'not alive' in msg)
msg = GD.kill_own(os.path.join(TD, 'nope.txt'))
check('kill_own: no pid file -> nothing killed', calls == [] and 'no pid file' in msg)
# --- watch: user process in 2 polls in a row -> flag, own killed by pid; 1 poll only -> nothing
seq = []
GD.scan = (lambda real: (lambda pidfile=None: seq.pop(0) if seq else []))(GD.scan)
GD.WATCH_POLL_S = 0.01
GD.procs = lambda: [P_OWN]


def run_watch(s, wait_s=0.5):
    seq[:] = s
    calls.clear()
    fl, st = os.path.join(TD, 'USER_FOUND'), os.path.join(TD, 'watch.stop')
    for f in (fl, st):
        if os.path.exists(f):
            os.remove(f)
    th = threading.Timer(wait_s, lambda: open(st, 'w').close())
    th.start()
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        GD.watch(PF, fl, st)
    th.join()
    return os.path.exists(fl), list(calls)


fl, cl = run_watch([[(6000, 'emulator')], [], [(6000, 'emulator')], []])
check('watch: never 2 polls in a row -> no flag, no kill', not fl and cl == [])
fl, cl = run_watch([[], [(6000, 'emulator')], [(6000, 'emulator')]])
check('watch: 2 polls in a row -> flag and own killed by pid only', fl and cl and all(c == ['taskkill', '/F', '/T', '/PID', '5000'] for c in cl))
check('watch: flag text masked', 'Secret' not in open(os.path.join(TD, 'USER_FOUND')).read())
# --- wait_gone returns after the user process is gone
seq[:] = [[(6000, 'emulator')], [(6000, 'emulator')], []]
import io  # noqa: E402
import contextlib  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()) as b:
    rc = GD.wait_gone(PF, 0.01)
check('wait_gone: rc 0 after the user process left', rc == 0 and not seq and 'GUARD CLEAN' in b.getvalue())
check('wait_gone: CLI poll capped at 10 s', GD.GONE_POLL_S == 10.0)
GD.subprocess.run, GD.procs = keep_run, keep_procs
# --- blocks (item 534 (3))
BF = os.path.join(TD, 'block.txt')
T0 = 1000000.0
check('block: first clean -> PENDING 9', GD.open_block(BF, [], T0) == (9, 'PENDING'))
check('block: 599 s later -> PENDING', GD.open_block(BF, [], T0 + 599) == (9, 'PENDING'))
check('block: 600 s after the first -> OPEN', GD.open_block(BF, [], T0 + 600) == (0, 'OPEN'))
st = GD.block_state(GD.block_lines(BF))
check('block: state open, 0 tags', st == ('open', 0))
for i in range(5):
    GD.block_add(BF, 'TAG f20_v%02d' % (i + 1), T0 + 700 + i)
check('block: 5 tags -> open', GD.block_state(GD.block_lines(BF)) == ('open', 5))
GD.block_add(BF, 'TAG f20_v06', T0 + 800)
check('block: 6 tags -> closed', GD.block_state(GD.block_lines(BF))[0] == 'closed')
check('block: after close, old CLEAN does not count -> PENDING', GD.open_block(BF, [], T0 + 2000) == (9, 'PENDING'))
check('block: FOUND -> rc 7, closed', GD.open_block(BF, [(1, 'emulator')], T0 + 2700) == (7, 'FOUND'))
check('block: clean 700 s after the pending one but FOUND between -> PENDING', GD.open_block(BF, [], T0 + 2701) == (9, 'PENDING'))
check('block: next clean 600 s later -> OPEN', GD.open_block(BF, [], T0 + 3301) == (0, 'OPEN'))
GD.block_add(BF, 'FOUND 1', T0 + 3302)
check('block: FOUND line between tags closes the block', GD.block_state(GD.block_lines(BF))[0] == 'closed')
# --- launch_f20l.sh dry run 2: block checks after the window
LB, LT = os.path.join(TD, 'lblock.txt'), os.path.join(TD, 'times.txt')
LENV = dict(os.environ, F20L_TIMES=LT, F20L_DRYRUN='2', F20L_GUARD_BLOCK=LB, F20L_GUARD_FAKE=FK, F20L_QUEUE_SKIP='1')


def launch():
    if os.path.exists(LT):
        os.remove(LT)
    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l.sh'), 'b32_pd'], capture_output=True, text=True, env=LENV)
    return p.returncode, p.stdout, open(LT).read() if os.path.exists(LT) else ''


json.dump([P_OTHER], open(FK, 'w'))
rc, out, tl = launch()
check('launch: block not open -> rc 8, times line', rc == 8 and 'block closed' in out and 'not launched' in tl)
GD.block_add(LB, 'CLEAN', time.time() - 700)
GD.block_add(LB, 'OPEN', time.time() - 1)
rc, out, tl = launch()
check('launch: open block, clean -> dry run 2 rc 0', rc == 0 and 'dryrun2' in out)
json.dump([P_OTHER, P_USER_EMU], open(FK, 'w'))
rc, out, tl = launch()
check('launch: user emulator -> rc 7, block closed, times line masked', rc == 7 and 'block closed' in tl and 'Secret' not in tl + out)
check('launch: block file closed after the find', GD.block_state(GD.block_lines(LB))[0] == 'closed')
p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l.sh'), 'b32_pd2'], capture_output=True, text=True, env=dict(os.environ, F20L_DRYRUN='1'))
check('go: dry run 1 names the form (pd2: loader half, KYTY_DIAG_B32=1)', p.returncode == 0 and 'loader half' in p.stdout and 'KYTY_DIAG_B32=1' in p.stdout)
# --- enter_scene.kill_game: pid only, never the image name
ecalls = []


class G:
    pid = 4242
    killed = False

    def poll(self):
        return None

    def wait(self, timeout=None):
        raise subprocess.TimeoutExpired('x', timeout)

    def kill(self):
        G.killed = True


keep = ES.subprocess.run
ES.subprocess.run = lambda a, **k: ecalls.append(a)
ES.kill_game(G())
ES.subprocess.run = keep
check('enter_scene kill_game: only taskkill /F /T /PID <pid>, then kill() of the handle', ecalls == [['taskkill', '/F', '/T', '/PID', '4242']] and G.killed)
src = open(os.path.join(HERE, 'enter_scene.py'), encoding='ascii').read()
check('enter_scene: pid file written after Popen', "os.environ.get('F20E_PIDFILE')" in src and src.index('F20E_PIDFILE') > src.index('game = subprocess.Popen'))
# --- no kill by image name anywhere in the harness
for nm in ('go_f20l.sh', 'launch_f20l.sh', 'enter_scene.py', 'guard_f20l.py', 'wait_f20l.sh', 'post_f20l.sh'):
    s = open(os.path.join(HERE, nm), encoding='ascii').read()
    check('%s: no kill by image name' % nm, '//IM' not in s and "'/IM'" not in s and '/IM ' not in s and 'taskkill //F //IM' not in s)
# --- order of the guard in go_f20l.sh
go = open(os.path.join(HERE, 'go_f20l.sh'), encoding='ascii').read()
i_pre = go.index('GS=$(python $G/guard_f20l.py scan) ||')
i_mk = go.index('mkdir -p $OUT')
i_lock = go.index('echo "lock taken $T $(u)" >> $G/runs/lock.log')
i_post = go.index('GS=$(python $G/guard_f20l.py scan) ||', i_lock)
i_mf = go.index('python $G/manifest_fs4c.py $OUT/manifest_before.tsv')
i_cp = go.index('cp -a "$SRC"')
i_watch = go.index('guard_f20l.py watch')
i_es = go.index('python $G/enter_scene.py')
i_gone = go.index('guard_f20l.py wait-gone')
i_ret = go.index('rm -rf "$LIVE"')
i_mrun = go.index('manifest_fs4c.py $OUT/manifest_run.tsv')
check('go: guard before the lock', i_pre < i_mk < i_lock)
check('go: guard right after the lock, before the manifest and the copy', i_lock < i_post < i_mf < i_cp)
check('go: post-lock find releases the lock and moves runs/<tag> without touching caches',
      'rm -f $LOCK; echo "lock released $T $(u)" >> $G/runs/lock.log; mv $OUT $OUT.user_' in go[i_post:i_post + 400])
check('go: watcher started before enter_scene with the pid file', i_watch < i_es and 'F20E_PIDFILE=$OUT/game_pid.txt python $G/enter_scene.py' in go)
check('go: wait for the user process before the run manifest and the return', i_gone < i_mrun < i_ret)
check('go: kill at the exit and after the run by pid file only', go.count('guard_f20l.py kill-own --pidfile $OUT/game_pid.txt') == 2)
i_bin = go.index('cp "$BIN" "$GAME"')
i_bret = go.index('cp "$PINNED" "$GAME"')
check('go: test binary installed after the cache copy, before enter_scene', i_cp < i_bin < i_es)
check('go: FS8 returned after the wait for the user process, before the run manifest', i_gone < i_bret < i_mrun)
check('go: M6 and the loader start before enter_scene, stop files touched after it and at the exit', go.index('m6_f20l.py') < i_es and go.index('b32_load.py') < i_es and go.count('touch $OUT/watch.stop $OUT/m6.stop $OUT/load.stop') == 1 and 'touch $OUT/m6.stop $OUT/load.stop' in go[:i_mf])
check('go: USER_FOUND -> runs/<tag>.user_*, nostart -> .nostart_*', 'mv $OUT $OUT.user_' in go[go.index('if [ -e $OUT/USER_FOUND ]; then\n      UF'):]
      and 'mv $OUT $OUT.nostart_' in go)
for nm in ('guard_f20l.py', 'test_guard_f20l.py', 'go_f20l.sh', 'launch_f20l.sh', 'enter_scene.py'):
    check('%s ASCII only' % nm, all(b < 128 for b in open(os.path.join(HERE, nm), 'rb').read()))
shutil.rmtree(TD, ignore_errors=True)
print('checks %d, failed %d' % (n[0], len(fails)))
if fails:
    print('FAILED:', fails)
    sys.exit(1)
print('ALL OK')
