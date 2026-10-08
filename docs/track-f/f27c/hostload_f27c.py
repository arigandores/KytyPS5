"""F27c (HPP-694; ROADMAP s122 item 632 (v)(2)): the host load line of a tag - two snapshots of the per-process CPU time SPAN s apart
(procload.py snapshot), every foreign process above 0.5 CPU s/s and the sum over all non-system processes.  Names are never printed
(every process is '<app>').  Prints one line:
  hostload: over05 <n> max <r> total <t> procs [('<app>', <pid>, <rate>), ...]
and writes the same as JSON with --json F.  Exit 0 (a row, not a gate; the gate is procload.py).  ASCII only.
usage: python hostload_f27c.py [--json F] [--exclude-pid P]"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import procload  # noqa: E402

OVER = 0.5


def measure(snap=None, sleep=None, span=None):
    snap = snap or procload.snapshot
    sleep = sleep or time.sleep
    span = procload.SPAN if span is None else span
    a = snap()
    t0 = time.monotonic()
    sleep(span)
    b = snap()
    dt = max(time.monotonic() - t0, span) if sleep is time.sleep else span
    procs, total = [], 0.0
    for key, cpu in b.items():
        if key[1].lower() in procload.IGNORE or key not in a:
            continue
        rate = (cpu - a[key]) / dt
        total += max(rate, 0.0)
        if rate > OVER:
            procs.append(('<app>', key[0], round(rate, 3)))
    procs.sort(key=lambda r: -r[2])
    return dict(over05=len(procs), max=procs[0][2] if procs else 0.0, total=round(total, 3), procs=procs)


def line(r):
    return 'hostload: over05 %d max %.3f total %.3f procs %s' % (r['over05'], r['max'], r['total'], r['procs'])


def main(argv):
    r = measure()
    if '--exclude-pid' in argv:
        pid = int(argv[argv.index('--exclude-pid') + 1])
        r['procs'] = [p for p in r['procs'] if p[1] != pid]
        r['over05'] = len(r['procs'])
        r['max'] = r['procs'][0][2] if r['procs'] else 0.0
    print(line(r))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w', encoding='ascii') as f:
            json.dump(r, f)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
