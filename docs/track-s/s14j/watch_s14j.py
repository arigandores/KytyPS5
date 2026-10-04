"""S14j (HPP-533): watchdog of ROADMAP s122 item 431(v)(1) for a command longer than 60 s of a link without the lock.
Runs one command and polls every --poll seconds (default 1.0, item 431 asks <= 2 s): the command's process tree is killed
(taskkill /T /F) when the lock file appears, when the track STOP file appears, or when any process other than this
watchdog has 'procload.py' in its command line; then it prints 'KILLED: procload|lock|STOP <UTC>', appends the same to
--times and exits 7 / 3 / 4. A step limit --limit (default 540 s, the tool cap is 600 s) kills with exit 6 (rerun the
step: ninja is incremental). Before starting: lock -> exit 5, STOP -> exit 4, procload alive -> exit 7.

    python watch_s14j.py --log <file> --times <file> [--lock P] [--stop P] [--poll S] [--limit S] -- <command...>

The lock and STOP paths are arguments so the fixture never creates the real C:/kyty/SEALED_RUN.lock.
Own load: one psutil pass over process names per poll; command lines only of python-like processes.
"""
import datetime
import os
import subprocess
import sys
import time

import psutil

PATTERN = 'procload' + '.py'  # split so this file's own text never matches a grep for the pattern


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def procload_alive(skip):
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['pid'] in skip:
                continue
            name = (p.info['name'] or '').lower()
            if 'python' not in name and name not in ('py.exe', 'pyw.exe'):
                continue
            cmd = ' '.join(p.cmdline())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
            continue
        if PATTERN in cmd:
            return p.info['pid']
    return None


def main():
    argv = sys.argv[1:]
    if '--' not in argv:
        sys.exit('usage: watch_s14j.py --log F --times F [--lock P] [--stop P] [--poll S] [--limit S] -- cmd...')
    sep = argv.index('--')
    opts, cmd = argv[:sep], argv[sep + 1:]

    def opt(name, default):
        return opts[opts.index(name) + 1] if name in opts else default

    log = opt('--log', None)
    times = opt('--times', None)
    lock = opt('--lock', 'C:/kyty/SEALED_RUN.lock')
    stop = opt('--stop', 'C:/kyty/s288/STOP')
    poll = float(opt('--poll', '1.0'))
    limit = float(opt('--limit', '540'))
    me = {os.getpid()}

    def note(text):
        line = '%s %s' % (utc(), text)
        print(text if text.startswith(('KILLED', 'STOPPED', 'rc=', 'REFUSED')) else line, flush=True)
        if times:
            with open(times, 'a', encoding='utf-8') as f:
                f.write(line + '\n')

    if os.path.exists(lock):
        note('REFUSED: lock %s' % utc())
        sys.exit(5)
    if os.path.exists(stop):
        note('REFUSED: STOP %s' % utc())
        sys.exit(4)
    pid = procload_alive(me)
    if pid is not None:
        note('REFUSED: procload pid %d %s' % (pid, utc()))
        sys.exit(7)
    out = open(log, 'ab') if log else subprocess.DEVNULL
    child = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    me.add(child.pid)
    t0 = time.monotonic()

    def kill_tree():
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(child.pid)], capture_output=True)
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass

    while True:
        try:
            rc = child.wait(timeout=poll)
            note('rc=%d end %s' % (rc, utc()))
            sys.exit(rc)
        except subprocess.TimeoutExpired:
            pass
        reason = None
        if os.path.exists(lock):
            reason, code = 'lock', 3
        elif os.path.exists(stop):
            reason, code = 'STOP', 4
        else:
            pid = procload_alive(me)
            if pid is not None:
                reason, code = 'procload', 7
        if reason is None and time.monotonic() - t0 >= limit:
            kill_tree()
            note('STOPPED: %d s step limit %s' % (int(limit), utc()))
            sys.exit(6)
        if reason is not None:
            kill_tree()
            note('KILLED: %s %s' % (reason, utc()))
            sys.exit(code)


if __name__ == '__main__':
    main()
