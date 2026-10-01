"""fgcpu143.py - the foreign-CPU row of every run of the chain go143a.sh (session 143 step 0, HPP-297; link 1b HPP-321,
ROADMAP s122 item 231 (i)(4), (l): debt D-4 "the background inside the lock was not measured", and item 242 (a): the row
is written at the end of every run, inside the lock).  A ROW, NOT A GUARD: nothing refuses or admits on it; no threshold.

    python fgcpu143.py --save <a.json>                                right after the lock is taken
    python fgcpu143.py --since <a.json> [--span S] [--chain-pid P]   at the end of the run, inside the lock: ONE ASCII line

The run part of the line (the window from --save to now) carries the terms of item 242 (a):
  (1) the processes alive at both ends (same pid and name): their CPU seconds between the two snapshots / the wall seconds;
  (2) the processes new at the end (not alive at --save): ALL their CPU seconds (they were born inside the window) / the
      wall seconds, a term of its own, with names;
  (3) the system: GetSystemTimes (kernel32) - delta(kernel + user - idle) / delta wall, in CPU s/s and in % of the logical
      CPUs (kernel time includes idle time, so busy = kernel + user - idle);
      beside it the game (kyty_emulator alive at the end) and the chain (P - the Windows pid of the go143a.sh shell - and
      its descendants alive at the end, this sampler included) - out of (1) and (2);
  (4) the residual = (3) - (1) - (2) - game - chain, printed as a number as it is (a negative one is not clipped).  The game
      and the chain's short processes (enter_scene.py, the samplers, the video tools, the scorer) are dead at the end: the
      snapshots cannot see them, so their CPU is IN the residual - said in the line;
  (5) the blind zone, written in the line: processes born and dead inside the run are only in the system member.
The now part samples S seconds (default 10) the same way.  Totals are in CPU seconds per wall second and in % of the logical
CPUs; the TOP processes by rate are named.  Idle / System / System Idle Process (procload.IGNORE) are out of (1) and (2).
The snapshot is the process list of kernel32 (CreateToolhelp32Snapshot: pid, parent pid, image name) with the CPU of each
process by GetProcessTimes (kernel + user; a process that refuses the query counts 0, as Get-Process prints no CPU for it) -
no child process is started, so the sampler never sees itself as a newcomer.  Without the --save file the run part reads
"n/a"; a failed snapshot prints "unavailable" - the line is always written.  ASCII only.
"""
import ctypes
import json
import os
import sys
import time

IGNORE = {'idle', 'system', 'system idle process'}
GAME = 'kyty_emulator'
SPAN = 10.0
TOP = 5
BLIND = 'blind zone: processes born and dead inside the run: only in the system member'


def _win_snapshot():
    """({(pid, name): cpu seconds}, {pid: parent pid}) of every process now (kernel32, no child process)."""
    from ctypes import wintypes
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)

    class PE(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD),
                    ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', wintypes.DWORD),
                    ('cntThreads', wintypes.DWORD), ('th32ParentProcessID', wintypes.DWORD),
                    ('pcPriClassBase', ctypes.c_long), ('dwFlags', wintypes.DWORD), ('szExeFile', ctypes.c_wchar * 260)]
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PE)]
    k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PE)]
    k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    if snap in (None, wintypes.HANDLE(-1).value):
        raise OSError('CreateToolhelp32Snapshot failed')
    rows = []
    try:
        pe = PE()
        pe.dwSize = ctypes.sizeof(PE)
        more = k32.Process32FirstW(snap, ctypes.byref(pe))
        while more:
            rows.append((int(pe.th32ProcessID), int(pe.th32ParentProcessID), pe.szExeFile))
            more = k32.Process32NextW(snap, ctypes.byref(pe))
    finally:
        k32.CloseHandle(snap)
    cpu, parent = {}, {}
    ft = [wintypes.FILETIME() for _ in range(4)]
    for pid, ppid, exe in rows:
        name = exe[:-4] if exe.lower().endswith('.exe') else exe
        if pid == 0:
            name = 'Idle'
        sec = 0.0
        h = k32.OpenProcess(0x1000, False, pid) if pid else None
        if h:
            try:
                if k32.GetProcessTimes(h, *[ctypes.byref(x) for x in ft]):
                    sec = sum(((x.dwHighDateTime << 32) | x.dwLowDateTime) for x in ft[2:]) / 1e7
            finally:
                k32.CloseHandle(h)
        cpu[(pid, name)] = sec
        parent[pid] = ppid
    return cpu, parent


def _win_systimes():
    """(idle, kernel, user) seconds summed over the logical CPUs since boot (GetSystemTimes)."""
    from ctypes import wintypes
    ft = [wintypes.FILETIME() for _ in range(3)]
    if not ctypes.WinDLL('kernel32').GetSystemTimes(*[ctypes.byref(x) for x in ft]):
        raise OSError('GetSystemTimes failed')
    return tuple(((x.dwHighDateTime << 32) | x.dwLowDateTime) / 1e7 for x in ft)


def snap_list(d):
    return [[pid, name, cpu] for (pid, name), cpu in sorted(d.items())]


def snap_dict(rows):
    return dict(((int(pid), str(name)), float(cpu or 0.0)) for pid, name, cpu in rows)


def descendants(parent, roots):
    """The pids of roots and of every process whose parent chain reaches one of them (a cycle-safe walk)."""
    kids = {}
    for pid, ppid in parent.items():
        if pid != ppid:
            kids.setdefault(ppid, []).append(pid)
    out = set()
    todo = [r for r in roots if r is not None]
    while todo:
        p = todo.pop()
        if p in out:
            continue
        out.add(p)
        todo.extend(kids.get(p, []))
    return out


def terms(a, b, dt, chain):
    """The terms of item 242 (a) from snapshot a to snapshot b over dt wall seconds: dict(both=(total, rows, n),
    new=(total, rows, n), game=rate, chain=(rate, n)); rows are (name, pid, rate) sorted by rate."""
    both, new = [], []
    game = 0.0
    ch, nch = 0.0, 0
    for key, cpu in b.items():
        if key[1].lower() in IGNORE:
            continue
        alive = key in a
        r = (max(cpu - a[key], 0.0) if alive else max(cpu, 0.0)) / dt if dt > 0 else 0.0
        if key[0] in chain:
            ch += r
            nch += 1
        elif key[1].lower() == GAME:
            game += r
        elif alive:
            both.append((key[1], key[0], r))
        else:
            new.append((key[1], key[0], r))
    out = dict(game=game, chain=(ch, nch))
    for k, rows in (('both', both), ('new', new)):
        rows.sort(key=lambda x: (-x[2], x[0], x[1]))
        out[k] = (sum(r for _, _, r in rows), rows, len(rows))
    return out


def sysrate(s0, s1, dt):
    """Item 242 (a)(3): delta(kernel + user - idle) / delta wall; None when a reading is missing."""
    if s0 is None or s1 is None or dt <= 0:
        return None
    return ((s1[1] - s0[1]) + (s1[2] - s0[2]) - (s1[0] - s0[0])) / dt


def pct(x, ncpu):
    return 100.0 * x / ncpu if ncpu else 0.0


def top(rows):
    return ', '.join('%s:%d:%.3f' % (n, p, r) for n, p, r in rows[:TOP]) or 'none'


def part(label, wall, t, sysr, ncpu, chain_pid):
    bt, brows, bn = t['both']
    nt, nrows, nn = t['new']
    ch, nch = t['chain']
    s = ('%s %.1f s: (1) alive at both ends: foreign %.3f CPU s/s = %.1f %% of %d logical CPUs over %d processes; top %s | '
         '(2) new at the end: foreign %.3f CPU s/s = %.1f %% over %d processes; top %s | ' % (
             label, wall, bt, pct(bt, ncpu), ncpu, bn, top(brows), nt, pct(nt, ncpu), nn, top(nrows)))
    if sysr is None:
        s += '(3) system unavailable | game %.3f, chain (pid %s and its descendants alive at the end) %.3f over %d | (4) ' \
             'residual n/a' % (t['game'], chain_pid, ch, nch)
    else:
        res = sysr - bt - nt - t['game'] - ch
        s += ('(3) system (GetSystemTimes) %.3f CPU s/s = %.1f %% | game %.3f, chain (pid %s and its descendants alive at '
              'the end) %.3f over %d | (4) residual = (3) - (1) - (2) - game - chain = %.3f CPU s/s (the game and the '
              "chain's processes dead at the end are in it)" % (sysr, pct(sysr, ncpu), t['game'], chain_pid, ch, nch, res))
    return s + ' | ' + BLIND


def ascii_line(s):
    return s.encode('ascii', 'replace').decode('ascii')


def main(argv=None, snapshot=None, systimes=None, clock=time.time, sleep=time.sleep, me=None, ncpu=None):
    argv = sys.argv[1:] if argv is None else argv
    snapshot = snapshot or _win_snapshot
    systimes = systimes or _win_systimes
    me = os.getpid() if me is None else me
    ncpu = ncpu or os.cpu_count() or 1

    def systry():
        try:
            return tuple(float(x) for x in systimes())
        except Exception:
            return None
    if len(argv) >= 2 and argv[0] == '--save':
        try:
            s, par = snapshot()
            sy = systry()
            with open(argv[1], 'w', encoding='ascii') as f:
                json.dump(dict(t=clock(), procs=snap_list(s), sys=sy), f)
            print('fgcpu143: saved %d processes into %s (system times %s)' % (
                len(s), argv[1], 'yes' if sy is not None else 'unavailable'))
        except Exception as e:
            print(ascii_line('fgcpu143: save unavailable (%s: %s)' % (type(e).__name__, str(e)[:120])))
        return 0
    if len(argv) >= 2 and argv[0] == '--since':
        span = float(argv[argv.index('--span') + 1]) if '--span' in argv else SPAN
        cpid = None
        if '--chain-pid' in argv:
            try:
                cpid = int(argv[argv.index('--chain-pid') + 1])
            except (ValueError, IndexError):
                cpid = None
        try:
            t1 = clock()
            b, pb = snapshot()
            s1 = systry()
        except Exception as e:
            print(ascii_line('fgcpu143: unavailable (%s: %s)' % (type(e).__name__, str(e)[:120])))
            return 0
        chain = descendants(pb, [me, cpid])
        run = 'run n/a (no snapshot at the lock: %s)' % argv[1]
        try:
            with open(argv[1], encoding='ascii') as f:
                saved = json.load(f)
            a = snap_dict(saved['procs'])
            wall = t1 - float(saved['t'])
            s0 = tuple(saved['sys']) if saved.get('sys') else None
            run = part('run', wall, terms(a, b, wall, chain), sysrate(s0, s1, wall), ncpu, cpid)
        except (OSError, ValueError, KeyError, TypeError):
            pass
        try:
            sleep(span)
            t2 = clock()
            c, pc = snapshot()
            s2 = systry()
            now = part('now', t2 - t1, terms(b, c, t2 - t1, descendants(pc, [me, cpid])), sysrate(s1, s2, t2 - t1),
                       ncpu, cpid)
        except Exception as e:
            now = 'now unavailable (%s)' % type(e).__name__
        print(ascii_line('fgcpu143: %s || %s' % (run, now)))
        return 0
    print('usage: fgcpu143.py --save <a.json> | --since <a.json> [--span S] [--chain-pid P]')
    return 2


if __name__ == '__main__':
    sys.exit(main())
