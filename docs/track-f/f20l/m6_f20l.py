"""Track F link F20l (HPP-631; ROADMAP s122 item 550 (e)(1), F20g s2.1 M6): the reference of the host interference during a tag - once per
1 s the CPU of the foreign processes (the form of the procload line: a process >= 0.5 CPU s/s, the top 3) and their sum.  A ROW, NOT A
GUARD: nothing refuses on it.  Names only in the local file (--local); the file for git (--out) writes every foreign process as <app>.
The own emulator (pid of the pid file) is 'game', the loader workers (pids of --loadpids) are 'loader', this sampler is out.  ASCII only.

    python m6_f20l.py --pidfile <game_pid.txt> --local <m6_local.txt> --out <m6.txt> --stop <file> [--loadpids <file>] [--period 1]
                      [--max-s 900] [--fake <json list of snapshots>]

Line (both files): '<UTC> t=<s> game=<CPU s/s> loader=<CPU s/s> foreign=<CPU s/s> top=<name|<app>>:<pid>:<rate>,...' (top: foreign
processes >= 0.5 CPU s/s, at most 3, by rate).  The last line: 'M6 end samples=<n> foreign_max=<x> foreign_mean=<x>'.
"""
import json
import os
import sys
import time

MIN_RATE = 0.5
TOP = 3
IGNORE = {'idle', 'system idle process'}


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def snapshot():
    import psutil
    out = {}
    for p in psutil.process_iter(['pid', 'name', 'cpu_times']):
        try:
            ct = p.info['cpu_times']
            if ct is None:
                continue
            out[(p.info['pid'], p.info['name'] or '?')] = ct.user + ct.system
        except Exception:  # noqa: BLE001
            continue
    return out


def read_pids(path):
    try:
        return set(int(x) for x in open(path, encoding='ascii').read().split() if x.strip().isdigit())
    except OSError:
        return set()


def game_pid(path):
    try:
        return int(open(path, encoding='ascii').read().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def line(t, rates, game, loader, own, masked):
    g = sum(r for (pid, _), r in rates.items() if pid == game)
    lo = sum(r for (pid, _), r in rates.items() if pid in loader)
    fr = [(r, pid, nm) for (pid, nm), r in rates.items() if pid != game and pid not in loader and pid != own and nm.lower() not in IGNORE]
    tot = sum(max(r, 0.0) for r, _, _ in fr)
    top = sorted([x for x in fr if x[0] >= MIN_RATE], reverse=True)[:TOP]
    tops = ','.join('%s:%d:%.2f' % ('<app>' if masked else nm, pid, r) for r, pid, nm in top) or '-'
    return '%s t=%.1f game=%.2f loader=%.2f foreign=%.2f top=%s' % (utc(), t, g, lo, tot, tops), tot


def main(argv):
    def a(k, d=None):
        return argv[argv.index(k) + 1] if k in argv else d
    pidf, local, out, stop, lp = a('--pidfile'), a('--local'), a('--out'), a('--stop'), a('--loadpids')
    period = float(a('--period', 1))
    max_s = float(a('--max-s', 900))
    fake = json.load(open(a('--fake'), encoding='ascii')) if a('--fake') else None
    own = os.getpid()
    t0 = time.monotonic()
    fl = open(local, 'w', encoding='utf-8', newline='\n')
    fo = open(out, 'w', encoding='ascii', newline='\n')
    prev = None
    prev_t = None
    n = 0
    fmax = 0.0
    fsum = 0.0
    k = 0
    while True:
        if fake is not None:
            if k >= len(fake):
                break
            snap = dict(((int(pid), nm), float(c)) for pid, nm, c in fake[k])
            now = float(k) * period
            k += 1
        else:
            if (stop and os.path.exists(stop)) or time.monotonic() - t0 > max_s:
                break
            snap = snapshot()
            now = time.monotonic()
        if prev is not None:
            dt = max(now - prev_t, 1e-6)
            rates = dict((key, (c - prev[key]) / dt) for key, c in snap.items() if key in prev)
            game = game_pid(pidf) if pidf else None
            loader = read_pids(lp) if lp else set()
            ln, tot = line(now - (0 if fake is not None else t0), rates, game, loader, own, False)
            lm, _ = line(now - (0 if fake is not None else t0), rates, game, loader, own, True)
            fl.write(ln + '\n')
            fo.write(lm + '\n')
            fl.flush()
            fo.flush()
            n += 1
            fmax = max(fmax, tot)
            fsum += tot
        prev, prev_t = snap, now
        if fake is None:
            time.sleep(max(0.0, period - (time.monotonic() - now)))
    end = 'M6 end samples=%d foreign_max=%.2f foreign_mean=%.2f' % (n, fmax, fsum / n if n else 0.0)
    fl.write(end + '\n')
    fo.write(end + '\n')
    fl.close()
    fo.close()
    print(end)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
