# Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), 742 (e), 744 (g)-(d)): copy of the F47d (HPP-809) file hostload_f47d.py with the names moved (f47d -> f47i, F47D -> F47I, F47d -> F47i, HPP-809 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 702 (g)): copy of the F44c (HPP-793) file hostload_f44c.py with the names moved (f44c -> f47i, F44C -> F47I, F44c -> F47i, HPP-793 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file hostload_f38c.py with the names moved (f38c -> f47i, F38C -> F47I, F38c -> F47i, HPP-765 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 691 (d)(4)): copy of the FS12c (HPP-752) file hostload_fs12c.py with the names moved (fs12c -> f47i, FS12C -> F47I, FS12c -> F47i, HPP-752 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file hostload_f33e.py with the names moved (f33e -> f47i, F33E -> F47I, F33e -> F47i, HPP-746 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file hostload_f34c.py with the names moved (f34c -> f47i, F34C -> F47I, F34c -> F47i, HPP-740 -> HPP-826); no change of meaning.
# Track F link F47i (HPP-826; ROADMAP s122 item 673 (z)(2), 674, 676): copy of the F31c (HPP-731) file hostload_f31c.py with the names moved (f31c -> f47i, F31C -> F47I, HPP-731 -> HPP-826); no change of meaning.
# Track F link F31c (HPP-826; ROADMAP s122 item 667 (d)): copy of the F26c (HPP-692) file hostload_f26c.py with the names moved (f26c -> f47i, HPP-692 -> HPP-826, F26C_ -> F47I_); no change of meaning.
"""F26c (HPP-826; ROADMAP s122 item 632 (v)(2)): the host load line of a tag - two snapshots of the per-process CPU time SPAN s apart
(procload.py snapshot), every foreign process above 0.5 CPU s/s and the sum over all non-system processes.  Names are never printed
(every process is '<app>').  Prints one line:
  hostload: over05 <n> max <r> total <t> procs [('<app>', <pid>, <rate>), ...]
and writes the same as JSON with --json F.  Exit 0 (a row, not a gate; the gate is procload.py).  ASCII only.
usage: python hostload_f47i.py [--json F] [--exclude-pid P]"""
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
