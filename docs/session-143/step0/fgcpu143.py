"""fgcpu143.py - the foreign-CPU row of every run of the chain go143a.sh (session 143 step 0, HPP-297; ROADMAP s122 item
231 (i)(4) and (l): debt D-4 "the background inside the lock was not measured" - the row is written at the end of every run,
inside the lock).  A ROW, NOT A GUARD: nothing refuses or admits on it.

    python fgcpu143.py --save <a.json>              right after the lock is taken: the per-process CPU seconds now
    python fgcpu143.py --since <a.json> [--span S]  at the end of the run, still inside the lock: ONE ASCII line

The line carries (1) the run average: for every process alive both at --save and now (same pid and name), its CPU seconds
used between the two snapshots divided by the wall seconds between them - the game and the chain's own short processes
(enter_scene.py, the emulator, the samplers) are not alive at both ends and are not in it; kyty_emulator, if alive at both
ends, is printed apart and not counted as foreign; (2) a sample of S seconds now (default 10) of every process alive at
both of its ends.  Totals are in CPU seconds per wall second and in % of the logical CPUs; the TOP processes by rate are
named.  Processes named Idle / System / System Idle Process (procload.IGNORE) and this sampler itself are left out.
Without the --save file the run part reads "n/a"; a failed snapshot prints "unavailable" - the line is always written.
The snapshot is procload.snapshot() (Get-Process Id, ProcessName, CPU), the same one the gate uses.  ASCII only.
"""
import json
import os
import sys
import time

import procload

IGNORE = procload.IGNORE
GAME = 'kyty_emulator'
SPAN = 10.0
TOP = 5


def snap_list(d):
    return [[pid, name, cpu] for (pid, name), cpu in sorted(d.items())]


def snap_dict(rows):
    return dict(((int(pid), str(name)), float(cpu or 0.0)) for pid, name, cpu in rows)


def rates(a, b, dt, me):
    """(foreign total CPU s/s, [(name, pid, rate)] sorted by rate, game rate, processes alive at both ends)."""
    rows = []
    game = 0.0
    both = 0
    for key, cpu in b.items():
        if key not in a or key[1].lower() in IGNORE or key[0] == me:
            continue
        both += 1
        r = max((cpu - a[key]) / dt, 0.0) if dt > 0 else 0.0
        if key[1].lower() == GAME:
            game += r
            continue
        rows.append((key[1], key[0], r))
    rows.sort(key=lambda x: (-x[2], x[0], x[1]))
    return sum(r for _, _, r in rows), rows, game, both


def part(label, wall, total, rows, game, both, ncpu):
    top = ', '.join('%s:%d:%.3f' % (n, p, r) for n, p, r in rows[:TOP]) or 'none'
    return ('%s %.1f s: foreign %.3f CPU s/s = %.1f %% of %d logical CPUs over %d processes alive at both ends; top %s; '
            'game %.3f' % (label, wall, total, 100.0 * total / ncpu if ncpu else 0.0, ncpu, both, top, game))


def ascii_line(s):
    return s.encode('ascii', 'replace').decode('ascii')


def main(argv=None, snapshot=None, clock=time.time, sleep=time.sleep, me=None, ncpu=None):
    argv = sys.argv[1:] if argv is None else argv
    snapshot = snapshot or procload.snapshot
    me = os.getpid() if me is None else me
    ncpu = ncpu or os.cpu_count() or 1
    if len(argv) >= 2 and argv[0] == '--save':
        try:
            s = snapshot()
            with open(argv[1], 'w', encoding='ascii') as f:
                json.dump(dict(t=clock(), procs=snap_list(s)), f)
            print('fgcpu143: saved %d processes into %s' % (len(s), argv[1]))
        except Exception as e:
            print(ascii_line('fgcpu143: save unavailable (%s: %s)' % (type(e).__name__, str(e)[:120])))
        return 0
    if len(argv) >= 2 and argv[0] == '--since':
        span = float(argv[argv.index('--span') + 1]) if '--span' in argv else SPAN
        try:
            t1 = clock()
            b = snapshot()
        except Exception as e:
            print(ascii_line('fgcpu143: unavailable (%s: %s)' % (type(e).__name__, str(e)[:120])))
            return 0
        run = 'run n/a (no snapshot at the lock: %s)' % argv[1]
        try:
            with open(argv[1], encoding='ascii') as f:
                saved = json.load(f)
            a = snap_dict(saved['procs'])
            wall = t1 - float(saved['t'])
            run = part('run', wall, *rates(a, b, wall, me), ncpu=ncpu)
        except (OSError, ValueError, KeyError, TypeError):
            pass
        try:
            sleep(span)
            t2 = clock()
            c = snapshot()
            now = part('now', t2 - t1, *rates(b, c, t2 - t1, me), ncpu=ncpu)
        except Exception as e:
            now = 'now unavailable (%s)' % type(e).__name__
        print(ascii_line('fgcpu143: %s | %s' % (run, now)))
        return 0
    print('usage: fgcpu143.py --save <a.json> | --since <a.json> [--span S]')
    return 2


if __name__ == '__main__':
    sys.exit(main())
