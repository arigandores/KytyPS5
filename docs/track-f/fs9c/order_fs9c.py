"""Track F link FS9c (HPP-673; ROADMAP s122 item 604 (d)(3)): the order of an FS9c tag with the series F25f (HPP-669, variant (v)(1) by
rule).  The lock is taken only (1) when it is free, (2) not earlier than 20 s after the last 'lock released' line of a foreign tag, and
(3) not inside the block of the F25f series that its seal names non-breakable (f25_c1 -> f25_c2: the last line of the F25f lock.log is
'lock released f25_c1...' - the live caches between them are the snapshot C1, a foreign tag is not taken there).
Lock logs read: every C:/kyty/<dir>/<dir>/runs/lock.log changed in the last 24 h except the own one (f287/fs9c).
Prints one line ORDER FREE (exit 0), ORDER LOCK (exit 3: the lock file exists), ORDER BLOCK (exit 1: inside the non-breakable block),
ORDER WAIT (exit 1: < 20 s after a foreign release; with --wait the script sleeps up to --wait seconds and checks again).
--logs a,b (fixtures only) - the lock logs; --lock F - the lock file; --now T - unix time.  ASCII only.
usage: python order_fs9c.py [--wait S]"""
import calendar
import glob
import os
import re
import sys
import time

OWN = 'C:/kyty/f287/fs9c/runs/lock.log'
F25F = 'C:/kyty/f287/f25f/runs/lock.log'
LOCK = 'C:/kyty/SEALED_RUN.lock'
GAP_S = 20
RX = re.compile(r'^lock (taken|released) (\S+) (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*$')
RX_C1 = re.compile(r'^f25_c1(_r\d+)?$')


def norm(p):
    return os.path.abspath(p).replace(chr(92), '/').lower()


def logs_default(now):
    out = []
    for p in glob.glob('C:/kyty/*/*/runs/lock.log'):
        if norm(p) == norm(OWN):
            continue
        try:
            if now - os.path.getmtime(p) > 86400:
                continue
        except OSError:
            continue
        out.append(p)
    return out


def last_line(p):
    try:
        with open(p, 'rb') as f:
            ls = [x.decode('ascii', 'replace').strip() for x in f.read().split(b'\n') if x.strip()]
    except OSError:
        return None
    return ls[-1] if ls else None


def state(logs, lock, now, f25f):
    if os.path.exists(lock):
        return 3, 'ORDER LOCK lock file exists'
    last_rel = None
    for p in logs:
        ln = last_line(p)
        m = RX.match(ln or '')
        if not m:
            continue
        if m.group(1) == 'released':
            t = calendar.timegm(time.strptime(m.group(3), '%Y-%m-%dT%H:%M:%SZ'))
            if last_rel is None or t > last_rel[0]:
                last_rel = (t, m.group(2), p.replace(chr(92), '/'))
        if norm(p) == norm(f25f) and m.group(1) == 'released' and RX_C1.match(m.group(2)):
            return 1, 'ORDER BLOCK F25f non-breakable block: last line of %s is "%s"' % (f25f, ln)
    if last_rel is not None and now - last_rel[0] < GAP_S:
        return 1, 'ORDER WAIT %.0f s after the release of %s (%s), need >= %d s' % (now - last_rel[0], last_rel[1], last_rel[2], GAP_S)
    if last_rel is None:
        return 0, 'ORDER FREE no foreign release line'
    return 0, 'ORDER FREE last foreign release %s %s, %.0f s ago' % (last_rel[1], last_rel[2], now - last_rel[0])


def main(argv):
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d  # noqa: E731
    lock = opt('--lock', LOCK)
    wait = float(opt('--wait', '0'))
    f25f = opt('--f25f', F25F)
    t0 = time.time()
    while True:
        now = float(opt('--now', time.time()))
        logs = opt('--logs').split(',') if opt('--logs') else logs_default(now)
        rc, line = state(logs, lock, now, f25f)
        if rc == 1 and line.startswith('ORDER WAIT') and time.time() - t0 < wait and '--now' not in argv:
            time.sleep(2)
            continue
        print(line)
        return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
