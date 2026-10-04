"""F14e (HPP-505, ROADMAP s122 item 431(g)): fixture of the watchdog watch_f14e.py, without the game and without the
lock. The real C:/kyty/SEALED_RUN.lock and C:/kyty/f287/STOP are never created: the watchdog gets substituted paths
(WD_LOCK, WD_STOP) and its own times file (WD_TIMES) in the fixture folder.

Cases (each: the long command is 'cmd /c python -c sleep(120)' - a tree of two processes):
  P  after >= 5 s a dummy process 'python <fx>/procload.py --wait-s 30' starts => watchdog 'KILLED: procload' and exit 7
     not later than 3 s after the dummy's start, the whole tree dead;
  L  after >= 5 s the substituted lock file appears => 'KILLED: lock', exit 3, <= 3 s, tree dead;
  S  after >= 5 s the substituted STOP file appears => 'KILLED: STOP', exit 4, <= 3 s, tree dead;
  R  a dummy procload.py lives before the start => the watchdog refuses (exit 8) and starts nothing;
  N  negative control: 'python -c sleep(15)' with no dummy => rc=0 end, no KILLED, wall >= 15 s; the watchdog's own CPU
     over the run < 0.5 CPU s/s (item 431(v)(2)) - printed.
Usage: python fx_watch_f14e.py <fx dir>. Prints one line per case and 'ALL OK' / 'FAILED'.
"""
import os
import subprocess
import sys
import time

import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
WATCH = os.path.join(HERE, 'watch_f14e.py')
PY = sys.executable


def tree_of(pid):
    try:
        p = psutil.Process(pid)
        return [(c.pid, c.create_time()) for c in p.children(recursive=True)]
    except psutil.Error:
        return []


def alive(entries):
    out = []
    for pid, ct in entries:
        try:
            if psutil.Process(pid).create_time() == ct:
                out.append(pid)
        except psutil.Error:
            pass
    return out


def start_watch(fx, cmd):
    env = dict(os.environ)
    env.update({'WD_LOCK': fx + '/FAKE_SEALED_RUN.lock', 'WD_STOP': fx + '/FAKE_STOP', 'WD_TIMES': fx + '/times_fx.txt'})
    return subprocess.Popen([PY, WATCH, '--tag', 'fx', '--'] + cmd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)


def dummy_procload(fx):
    return subprocess.Popen([PY, fx + '/procload.py', '--wait-s', '30'])


LONG = ['cmd', '/c', PY, '-c', 'import time; time.sleep(120)']


def real_clear():
    # Rule 27 / item 431: before every case - no real lock, no STOP, no live gate (argv ends with procload.py, not the
    # fixture dummy); otherwise the fixture stops at once (exit 5) and is rerun later.
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('HALT: real lock or STOP')
        sys.exit(5)
    for p in psutil.process_iter(['pid', 'cmdline']):
        args = [a.replace(chr(92), '/') for a in (p.info['cmdline'] or [])]
        if any(a.endswith('/procload.py') and '/f14e/fx/' not in a for a in args):
            print('HALT: real gate pid %d' % p.info['pid'])
            sys.exit(5)


def case_trigger(fx, name, trigger, want_word, want_rc):
    real_clear()
    w = start_watch(fx, LONG)
    time.sleep(6.0)
    tr = tree_of(w.pid)
    t0 = time.monotonic()
    extra = trigger()
    try:
        rc = w.wait(timeout=10)
    except subprocess.TimeoutExpired:
        w.kill()
        rc = None
    dt = time.monotonic() - t0
    out = w.stdout.read().decode('utf-8', 'replace').replace('\r', '')
    left = alive(tr)
    if extra is not None:
        extra.kill()
        extra.wait()
    for f in ('FAKE_SEALED_RUN.lock', 'FAKE_STOP'):
        if os.path.exists(fx + '/' + f):
            os.remove(fx + '/' + f)
    killed = [ln for ln in out.split('\n') if ln.startswith('KILLED: ')]
    ok = (rc == want_rc and len(killed) == 1 and killed[0].startswith('KILLED: %s ' % want_word) and dt <= 3.0
          and len(tr) >= 2 and not left)
    print('%s: rc=%s %s; trigger->exit %.2f s (<= 3); tree %d processes, alive after %s => %s'
          % (name, rc, killed[0] if killed else 'no KILLED line', dt, len(tr), left, 'OK' if ok else 'FAIL'))
    return ok


def main():
    fx = sys.argv[1].replace('\\', '/')
    os.makedirs(fx, exist_ok=True)
    with open(fx + '/procload.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write('# F14e fixture dummy: only sleeps; the real gate is never run.\nimport time\ntime.sleep(30)\n')
    for f in ('FAKE_SEALED_RUN.lock', 'FAKE_STOP', 'times_fx.txt'):
        if os.path.exists(fx + '/' + f):
            os.remove(fx + '/' + f)
    ok = True
    ok &= case_trigger(fx, 'P', lambda: dummy_procload(fx), 'procload', 7)

    def mk(path):
        open(path, 'w').close()
        return None
    ok &= case_trigger(fx, 'L', lambda: mk(fx + '/FAKE_SEALED_RUN.lock'), 'lock', 3)
    ok &= case_trigger(fx, 'S', lambda: mk(fx + '/FAKE_STOP'), 'STOP', 4)

    real_clear()
    d = dummy_procload(fx)
    time.sleep(1.0)
    w = start_watch(fx, [PY, '-c', 'import time; time.sleep(15)'])
    rc = w.wait(timeout=20)
    out = w.stdout.read().decode('utf-8', 'replace').replace('\r', '')
    d.kill()
    d.wait()
    good = rc == 8 and 'REFUSED: procload' in out and 'watch: start' not in out
    print('R: rc=%s %s => %s' % (rc, out.strip().split('\n')[0], 'OK' if good else 'FAIL'))
    ok &= good

    real_clear()
    t0 = time.monotonic()
    w = start_watch(fx, [PY, '-c', 'import time; time.sleep(15)'])
    wp = psutil.Process(w.pid)
    cpu0 = sum(wp.cpu_times()[:2])
    s0 = time.monotonic()
    time.sleep(4.0)
    cpu_m = sum(wp.cpu_times()[:2])
    s_m = time.monotonic()
    time.sleep(8.0)
    cpu1 = sum(wp.cpu_times()[:2])
    rate = (cpu1 - cpu0) / (time.monotonic() - s0)
    steady = (cpu1 - cpu_m) / (time.monotonic() - s_m)
    rc = w.wait(timeout=20)
    dt = time.monotonic() - t0
    out = w.stdout.read().decode('utf-8', 'replace').replace('\r', '')
    good = rc == 0 and 'KILLED' not in out and 'rc=0 end' in out and dt >= 15.0 and rate < 0.5
    print('N: rc=%s, KILLED lines %d, wall %.1f s (>= 15), watchdog CPU %.4f s/s from start, %.4f s/s steady (< 0.5) => %s'
          % (rc, out.count('KILLED'), dt, rate, steady, 'OK' if good else 'FAIL'))
    ok &= good
    tl = open(fx + '/times_fx.txt', encoding='utf-8').read().strip().split('\n') if os.path.exists(fx + '/times_fx.txt') else []
    good = (len(tl) == 2 and all('KILLED: ' in t for t in tl) and 'KILLED: procload' in tl[0]
            and 'KILLED: STOP' in tl[1])
    print('times lines (fixture file; lock line deferred by rule 27): %d %s => %s' % (len(tl), [t.split('KILLED: ')[-1].split(' ')[0] for t in tl],
                                                         'OK' if good else 'FAIL'))
    ok &= good
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
