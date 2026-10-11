# F47a4 (HPP-818): copy of the F47b3 watch_f47b3.py, times lines F47b3 -> F47a4. Was: F47b3 (HPP-817): copy of the F47a2 watch_f47a2.py. Was: F47a2 (HPP-807): copy of the F47a watch_f47a.py, executable lines F47a -> F47a2 (names of times lines). Was:
# F47a (HPP-802): copy of the F43a watch_f43a.py, executable lines f43a -> f47a (names of times lines). Was:
# F43a (HPP-783): copy of the F40a watch_f40a.py, executable lines f40a -> f43a (names of times lines). Was:
# F40a (HPP-770): copy of the F37a watch_f37a.py, executable lines f37a -> f40a (paths, names). Was:
# F37a (HPP-761): copy of the F33a watch_f33a.py, executable lines f33a -> f37a (paths, names). Was:
# F33a (HPP-736): copy of the FS11a watch_fs11a.py, executable lines fs11a -> f33a (paths, names of times lines). Was:
# FS11a (HPP-714): copy of the FS10a watch_fs10a.py (fs10a -> fs11a, FS10a -> FS11a, HPP-684 -> HPP-714). Was:
# FS10a (HPP-684): copy of the FS9a watch_fs9a.py (fs9a -> fs10a, FS9a -> FS10a, HPP-671 -> HPP-684). Was:
# FS9a (HPP-671): copy of the FS8a watch_fs8a.py, times lines say FS10a. Was:
# FS8a (HPP-571): copy of the FS7a watch_fs7a.py, paths and names changed. Was:
# FS8a (HPP-571): copy of watch_fs6a.py, times lines say FS8a. Was:
# FS8a (HPP-571): copy of watch_f15c.py, times lines say FS8a. Was:
# F15c (HPP-514): copy of watch_f14e.py, times lines say F15c.
"""F14e (HPP-505, ROADMAP s122 item 431(v)): watchdog for a command longer than 60 s of a link without the lock while a
Harness Engineer link of a series is in progress.

    python watch_f14e.py [--limit S] [--tag NAME] -- <command> [args...]

Starts <command> as a child process and polls every POLL seconds (<= 2 s, item 431(v)(1)):
  - the lock file  (WD_LOCK,  default C:/kyty/SEALED_RUN.lock),
  - the STOP file  (WD_STOP,  default C:/kyty/f287/STOP),
  - any live process with 'procload.py' in its command line, except this watchdog itself.
On any of them the child tree is killed (taskkill /T /F), the watchdog prints 'KILLED: procload|lock|STOP <UTC>',
appends one line to the times file (WD_TIMES, default C:/kyty/f287/times.txt; not on 'lock' - rule 27, no write under
a foreign lock: the link writes that line after the release) and exits 7 (procload) / 3 (lock) /
4 (STOP); at --limit seconds it kills the tree and exits 6 ('STOPPED: limit'). Otherwise it exits with the child's code
and prints 'rc=<n> end <UTC>'. Before the start it refuses (exit 5 / 4 / 8) if the lock, STOP or procload.py is
already there - a step is repeated only when there is neither the lock nor a procload.py process (item 431(v)(1)).

Own load (item 431(v)(2)): the command line is read only once per new process (key pid + create time); the poll itself
is one process listing with pid, name and create time. The fixture fx_watch_f14e.py measures the watchdog's CPU s/s.
"""
import os
import subprocess
import sys
import time

import psutil

POLL = 1.5
LOCK = os.environ.get('WD_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('WD_STOP', 'C:/kyty/f287/STOP')
TIMES = os.environ.get('WD_TIMES', 'C:/kyty/f287/times.txt')
NEEDLE = 'procload.py'


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def times_line(text):
    with open(TIMES, 'a', encoding='utf-8', newline='\n') as f:
        f.write('%s %s\n' % (utc(), text))


class Scanner:
    """Finds live processes with NEEDLE in the command line; caches the command line per (pid, create_time)."""

    def __init__(self, own):
        self.own = own
        self.cache = {}

    def find(self):
        hits = []
        seen = set()
        for p in psutil.process_iter(['pid', 'create_time']):
            key = (p.info['pid'], p.info['create_time'])
            seen.add(key)
            if key[0] == self.own:
                continue
            if key not in self.cache:
                try:
                    cl = ' '.join(p.cmdline())
                except (psutil.Error, OSError):
                    cl = ''
                self.cache[key] = NEEDLE in cl
            if self.cache[key]:
                hits.append(key[0])
        for key in [k for k in self.cache if k not in seen]:
            del self.cache[key]
        return hits


def tree(pid):
    try:
        p = psutil.Process(pid)
        return {pid} | {c.pid for c in p.children(recursive=True)}
    except psutil.Error:
        return set()


def kill_tree(pid):
    subprocess.run(['taskkill', '/T', '/F', '/PID', str(pid)], capture_output=True)


def main():
    argv = sys.argv[1:]
    if '--' not in argv:
        print(__doc__)
        return 2
    opts, cmd = argv[:argv.index('--')], argv[argv.index('--') + 1:]
    limit = float(opts[opts.index('--limit') + 1]) if '--limit' in opts else None
    tag = opts[opts.index('--tag') + 1] if '--tag' in opts else os.path.basename(cmd[0])
    own = os.getpid()
    sc = Scanner(own)
    if os.path.exists(LOCK):
        print('REFUSED: lock %s' % utc(), flush=True)
        return 5
    if os.path.exists(STOP):
        print('REFUSED: STOP %s' % utc(), flush=True)
        return 4
    pre = sc.find()
    if pre:
        print('REFUSED: procload %s pids %s' % (utc(), pre), flush=True)
        return 8
    child = subprocess.Popen(cmd)
    t0 = time.monotonic()
    print('watch: start %s child %d poll %.1f s lock %s stop %s' % (utc(), child.pid, POLL, LOCK, STOP), flush=True)
    while True:
        rc = child.poll()
        if rc is not None:
            print('rc=%d end %s' % (rc, utc()), flush=True)
            return rc
        reason = None
        if os.path.exists(LOCK):
            reason = ('lock', 3)
        elif os.path.exists(STOP):
            reason = ('STOP', 4)
        else:
            hits = sc.find()
            if hits:
                reason = ('procload', 7)
        if reason is None and limit is not None and time.monotonic() - t0 >= limit:
            kill_tree(child.pid)
            child.wait()
            print('STOPPED: limit %.0f s %s' % (limit, utc()), flush=True)
            times_line('F47a4 watchdog %s: STOPPED limit %.0f s' % (tag, limit))
            return 6
        if reason is not None:
            alive_before = sorted(tree(child.pid))
            kill_tree(child.pid)
            child.wait()
            stamp = utc()
            deadline = time.monotonic() + 3.0
            left = [p for p in alive_before if psutil.pid_exists(p)]
            while left and time.monotonic() < deadline:
                for pid in left:
                    try:
                        psutil.Process(pid).kill()
                    except psutil.Error:
                        pass
                time.sleep(0.2)
                left = [p for p in alive_before if psutil.pid_exists(p)]
            extra = ' pids %s' % hits if reason[0] == 'procload' else ''
            print('KILLED: %s %s%s; tree %s, alive after %s' % (reason[0], stamp, extra, alive_before, left), flush=True)
            if reason[0] == 'lock':
                # Rule 27: no write under a foreign lock - the times line is written by the link after the release.
                print('times line deferred: lock present', flush=True)
            else:
                times_line('F47a4 watchdog %s: KILLED: %s %s%s' % (tag, reason[0], stamp, extra))
            return reason[1]
        time.sleep(POLL)


if __name__ == '__main__':
    sys.exit(main())
