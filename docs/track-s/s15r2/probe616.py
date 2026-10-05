"""probe616.py - S15r2 (HPP-616), Red Team: own probes P1 on the code of S15a2 (enter_scene_s15.py), no game.

Stand-in emulator = python; every file goes under the work dir argv[1]; close_game of the probe records the call and kills
the stand-in by its pid only (game.kill()), never by image name.
    python probe616.py <work dir> <enter_scene_s15.py under test> [neg]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
import types

W = pathlib.Path(sys.argv[1])
SRC = sys.argv[2]
NEG = len(sys.argv) > 3 and sys.argv[3] == 'neg'
print('probe616 target %s sha256 %s%s' % (SRC, hashlib.sha256(pathlib.Path(SRC).read_bytes()).hexdigest(),
                                          ' (negative control)' if NEG else ''))
sys.path.insert(0, 'C:/kyty/s288')
sys.path.insert(0, os.path.dirname(os.path.abspath(SRC)))
spec = importlib.util.spec_from_file_location('es15_probe', SRC)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

shutil.rmtree(W, ignore_errors=True)
EMU = W / 'emu'
ROOT = W / 'root'
EMU.mkdir(parents=True)
ROOT.mkdir(parents=True)
E.EMU, E.ROOT = EMU, ROOT
E.STABLE_FRAMES, E.STABLE_DRAWS = 5, 100
TORN = 'FrameTrace: n=6GuestOut: x dt_us=30000 draws=3000'
STAND = W / 'stand.py'
STAND.write_text('''import os, sys, time, pathlib
emu, idxp, pidp, pre, live, torn, dtx = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6], sys.argv[7]
open(pidp, 'w').write(str(os.getpid()))
f = open(emu / '_kyty.txt', 'w', newline='\\n')
f.write('LevelDocument Loaded: lvl\\nGuestOut: Level has started: lvl\\n')
for n in range(12):
    f.write('FrameTrace: n=%d dt_us=99000 lat_us=5 gpu_proc=0 draws=3000 cpu_main_us=1 cpu_gpu_us=1\\n' % (n + 1))
f.flush()
with open(idxp, 'w', newline='\\n') as g:
    for k in range(12):
        g.write('%d %d 0.0\\n' % (k, k))
time.sleep(pre)
if torn != '-':
    f.write(torn + '\\n')
if dtx != '-':
    f.write('FrameTrace: n=13 dt_us=%s lat_us=5 gpu_proc=0 draws=3000\\n' % dtx)
f.flush()
time.sleep(live)
f.close()
''', encoding='ascii')
CLOSED = []


def close_rec(game):
    CLOSED.append(game.pid)
    if game.poll() is None:
        game.kill()
        game.wait(timeout=20)


def reap(pidp):
    try:
        pid = int(pathlib.Path(pidp).read_text())
    except Exception:
        return
    subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True)


def run(tag, pre, live, torn=TORN, dtx='-', hold_u='120:3000:300'):
    del CLOSED[:]
    pidp = W / ('%s.pid' % tag)
    opts = types.SimpleNamespace(level='lvl', timeout=60, hold=300, hold_u=hold_u, rec=True)
    args = [sys.executable, str(STAND), str(EMU), (ROOT / ('rec_%s.mp4.idx' % tag)).as_posix(), str(pidp), str(pre), str(live),
            torn, dtx]
    E.close_game = close_rec
    out = io.StringIO()
    t0 = time.monotonic()
    err = None
    res = None
    try:
        with contextlib.redirect_stdout(out):
            res = E.attempt('attempt 1', tag, opts, dict(os.environ), args, 1)
    except BaseException as error:
        err = '%s: %s' % (type(error).__name__, error)
    wall = time.monotonic() - t0
    try:
        pid = int(pidp.read_text())
        alive = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'], capture_output=True, text=True).stdout
        alive = str(pid) in alive
    except Exception:
        pid, alive = None, None
    reap(pidp)
    text = out.getvalue()
    he = (res or {}).get('hold_end')
    print('%s: exception out of attempt: %s' % (tag, err))
    print('%s: outcome %s; hold_end %s' % (tag, (res or {}).get('outcome'), json.dumps(he, sort_keys=True)))
    print('%s: close_game calls %d; stand-in alive after attempt() returned: %s; hold_exit present %s value %r; hold_s %r; '
          'ft_total %r; wall %.1f s' % (tag, len(CLOSED), alive, 'hold_exit' in (res or {}), (res or {}).get('hold_exit'),
                                         (res or {}).get('hold_s'), (res or {}).get('ft_total'), wall))
    lines = [l for l in text.splitlines() if l.startswith('U hold') or 'Traceback' in l or l.startswith('WARNING')]
    for l in lines:
        print('%s: stdout| %s' % (tag, l[:220]))
    return res, err, alive, he


ok = True
# Q1: the torn row arrives 3 s INTO the hold (clean polls before it) - the in-loop path after several clean polls
res, err, alive, he = run('q1', 3, 30)
q1 = err is None and res and res['outcome'] == 'ok' and (he or {}).get('cause') == 'error ValueError' and len(CLOSED) == 1 and \
    alive is False and 'hold_exit' in res and res.get('hold_exit') is None and (res.get('hold_s') or 0) >= 2 and \
    (res.get('hold_s') or 99) < 25 and res.get('ft_total') is not None and (he or {}).get('anchor') == 'fi'
print('Q1 %s' % ('PASS' if q1 else 'FAIL'))
ok &= bool(q1)
# Q2: the stand-in writes the torn row and exits at once - whichever of the two paths meets it, cause error, hold_exit = 0
res, err, alive, he = run('q2', 2, 0)
q2 = err is None and res and (he or {}).get('cause') == 'error ValueError' and alive is False and 'hold_exit' in res and \
    res.get('hold_exit') == 0 and len(CLOSED) == 1
print('Q2 %s' % ('PASS' if q2 else 'FAIL'))
ok &= bool(q2)
# Q3: another exception type out of UHold.feed (ft_field raises on dt_us=777) -> the type name in the cause
_ff = E.ft_field


def ff(line, name):
    if name == b'dt_us' and b' dt_us=777 ' in line:
        raise ZeroDivisionError('probe Q3')
    return _ff(line, name)


E.ft_field = ff
try:
    res, err, alive, he = run('q3', 2, 30, torn='-', dtx='777')
finally:
    E.ft_field = _ff
q3 = err is None and res and (he or {}).get('cause') == 'error ZeroDivisionError' and len(CLOSED) == 1 and alive is False and \
    'hold_exit' in res
print('Q3 %s' % ('PASS' if q3 else 'FAIL'))
ok &= bool(q3)
# Q4: a clean hold of the same stand-in (no torn row, game exits after 3 s) -> "game ended", unchanged path
res, err, alive, he = run('q4', 3, 0, torn='-')
q4 = err is None and res and (he or {}).get('cause') == 'game ended' and res.get('hold_exit') == 0 and len(CLOSED) == 1
print('Q4 %s' % ('PASS' if q4 else 'FAIL'))
ok &= bool(q4)
if NEG:
    print('NEGATIVE CONTROL: Q1-Q3 are expected to FAIL on the code of seal 14; Q4 to PASS')
print('ALL OK' if ok else 'NOT ALL OK')
