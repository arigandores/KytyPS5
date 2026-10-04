"""S14j (HPP-533): fixture of watch_s14j.py before its first use (form of ROADMAP s122 item 431(g)): a dummy long command
under the watchdog; >= 5 s later a dummy process with the pattern in its command line (stub file fx/<pattern>, sleeps 30 s),
a fake lock file or a fake STOP file appears => the watchdog prints KILLED: <reason> not later than 3 s after it and the
dummy tree is dead; negative control - nothing appears, the command runs to its end with rc=0; refusal before start and
the step limit. The real C:/kyty/SEALED_RUN.lock and C:/kyty/s288/STOP are never created (paths are arguments).
Ends with ALL OK.

    python fx_watch_s14j.py <s14j dir>
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil

D = Path(sys.argv[1])
FX = D / 'fx'
FX.mkdir(exist_ok=True)
WATCH = str(D / 'watch_s14j.py')
LOCK = FX / 'FAKE_SEALED_RUN.lock'
STOP = FX / 'FAKE_STOP'
STUB = FX / ('procload' + '.py')
STUB.write_text('import time\ntime.sleep(30)\n', encoding='utf-8')
LOG = FX / 'fx_watch.log'
PY = sys.executable
SLEEP = [PY, '-c', 'import time; time.sleep(120)']
ok = True
for p in (LOCK, STOP):
    if p.exists():
        p.unlink()

sys.path.insert(0, str(D))
import watch_s14j  # noqa: E402

real = watch_s14j.procload_alive({os.getpid()})
if real is not None:
    print('NOT RUN: a real procload process is alive (pid %d) - rerun later' % real)
    sys.exit(2)


def watch(cmd, extra=()):
    args = [PY, WATCH, '--log', str(LOG), '--lock', str(LOCK), '--stop', str(STOP), '--poll', '1.0', *extra, '--', *cmd]
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def grandchildren(w):
    try:
        return [c.pid for c in psutil.Process(w.pid).children(recursive=True)]
    except psutil.NoSuchProcess:
        return []


def check(name, cond, detail=''):
    global ok
    print('%s %s %s' % ('PASS' if cond else 'FAIL', name, detail))
    ok &= bool(cond)


# 1. negative control: the command runs to its end.
t = time.monotonic()
w = watch([PY, '-c', 'import time; time.sleep(6)'])
out, _ = w.communicate(timeout=60)
check('negative rc=0', w.returncode == 0 and 'rc=0 end' in out, '(rc=%s, %.1f s) %s' % (w.returncode, time.monotonic() - t,
                                                                                    out.strip()))


# 2-4. a trigger 5 s after the start.
def trigger_case(name, make, undo, code):
    w = watch(SLEEP)
    time.sleep(5)
    kids = grandchildren(w)
    t0 = time.monotonic()
    extra = make()
    out, _ = w.communicate(timeout=60)
    dt = time.monotonic() - t0
    undo(extra)
    time.sleep(0.5)
    alive = [k for k in kids if psutil.pid_exists(k)]
    check('%s exit %d' % (name, code), w.returncode == code, '(rc=%s)' % w.returncode)
    check('%s KILLED line' % name, ('KILLED: %s ' % name) in out, out.strip())
    check('%s within 3 s' % name, dt <= 3.0, '(%.2f s)' % dt)
    check('%s tree dead' % name, kids and not alive, '(tree %s, alive %s)' % (kids, alive))


def start_stub():
    return subprocess.Popen([PY, str(STUB)])


def stop_stub(p):
    p.kill()
    p.wait()


trigger_case('procload', start_stub, stop_stub, 7)
trigger_case('lock', lambda: LOCK.write_text('fixture', encoding='utf-8'), lambda _: LOCK.unlink(), 3)
trigger_case('STOP', lambda: STOP.write_text('fixture', encoding='utf-8'), lambda _: STOP.unlink(), 4)

# 5. refusal before the start.
LOCK.write_text('fixture', encoding='utf-8')
w = watch(SLEEP)
out, _ = w.communicate(timeout=30)
LOCK.unlink()
check('refuse lock exit 5', w.returncode == 5 and 'REFUSED: lock' in out, out.strip())
p = start_stub()
time.sleep(1)
w = watch(SLEEP)
out, _ = w.communicate(timeout=30)
stop_stub(p)
check('refuse procload exit 7', w.returncode == 7 and 'REFUSED: procload' in out, out.strip())

# 6. step limit.
w = watch(SLEEP, ('--limit', '3'))
kids = []
time.sleep(1.5)
kids = grandchildren(w)
out, _ = w.communicate(timeout=60)
time.sleep(0.5)
check('limit exit 6', w.returncode == 6 and 'STOPPED: 3 s step limit' in out and not any(psutil.pid_exists(k) for k in kids),
      out.strip())

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
