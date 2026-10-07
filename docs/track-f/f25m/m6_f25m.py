"""Track F link F25m (HPP-680; ROADMAP s122 item 596 (g), (d)(5), item 599 (b)(11), item 600 (b)(4)): M6 of the harness - port of
C:/kyty/f287/f20l3/m6_f20l3.py with two additions:
  (1) each line carries emu_t (seconds since the creation of the own emulator process, psutil create_time; '-' before the process) and
      qpc_ns (time.perf_counter_ns() of this process - the QPC on Windows) of the moment the sample was taken;
  (2) the calibration poller (a thread): every 50 ms it reads what the live log C:/kyty/KytyPS5/ps5 em/_kyty.txt grew by (from the start of
      the own emulator; a file shorter than the read offset is read again from 0) and for every new 'FrameTrace: n=<n>' line writes
      'CAL qpc_ns=<QPC ns of the sight> n=<n>' to --cal.  The reader pairs it with flip_ns of window n (the FrameStats::NowNs scale) - the
      event with both marks of item 600 (b)(4).
A ROW, NOT A GUARD: nothing refuses on it.  Names only in the local file (--local); the file for git (--out) writes every foreign process
as <app>.  The own emulator (pid of the pid file) is 'game', the loader workers 'loader', this sampler is out.  ASCII only.

    python m6_f25m.py --pidfile <game_pid.txt> --local <m6_local.txt> --out <m6.txt> --cal <cal.txt> --stop <file> [--loadpids <file>]
                      [--log <live log>] [--period 1] [--poll 0.05] [--max-s 900] [--fake <json list of snapshots>]

Line (both files): '<UTC> t=<s> emu_t=<s|-> qpc_ns=<int> game=<CPU s/s> loader=<CPU s/s> foreign=<CPU s/s> top=<name|<app>>:<pid>:<rate>,...'.
The last line: 'M6 end samples=<n> foreign_max=<x> foreign_mean=<x> cal_lines=<n>'.
"""
import json
import os
import re
import sys
import threading
import time

MIN_RATE = 0.5
TOP = 3
IGNORE = {'idle', 'system idle process'}
LIVE_LOG = 'C:/kyty/KytyPS5/ps5 em/_kyty.txt'
FT = re.compile(rb'^FrameTrace: n=(\d+) ')


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


def emu_t(pid):
    if pid is None:
        return None
    try:
        import psutil
        return time.time() - psutil.Process(pid).create_time()
    except Exception:  # noqa: BLE001
        return None


def line(t, et, qpc, rates, game, loader, own, masked):
    g = sum(r for (pid, _), r in rates.items() if pid == game)
    lo = sum(r for (pid, _), r in rates.items() if pid in loader)
    fr = [(r, pid, nm) for (pid, nm), r in rates.items() if pid != game and pid not in loader and pid != own and nm.lower() not in IGNORE]
    tot = sum(max(r, 0.0) for r, _, _ in fr)
    top = sorted([x for x in fr if x[0] >= MIN_RATE], reverse=True)[:TOP]
    tops = ','.join('%s:%d:%.2f' % ('<app>' if masked else nm, pid, r) for r, pid, nm in top) or '-'
    return '%s t=%.1f emu_t=%s qpc_ns=%d game=%.2f loader=%.2f foreign=%.2f top=%s' % (
        utc(), t, '-' if et is None else '%.3f' % et, qpc, g, lo, tot, tops), tot


class Poller(threading.Thread):
    """First sight of every FrameTrace n of the live log on the QPC scale."""

    def __init__(self, log, out, pidfile, stop_ev, poll):
        threading.Thread.__init__(self, daemon=True)
        self.log, self.out, self.pidfile, self.stop_ev, self.poll = log, out, pidfile, stop_ev, poll
        self.lines = 0

    def run(self):
        fo = open(self.out, 'w', encoding='ascii', newline='\n')
        while not self.stop_ev.is_set() and (not self.pidfile or game_pid(self.pidfile) is None):
            time.sleep(self.poll)
        if self.pidfile and game_pid(self.pidfile) is None:
            fo.close()
            return
        off = 0
        rest = b''
        seen = -1
        fh = None
        while True:
            last = self.stop_ev.is_set()
            try:
                if fh is None:
                    fh = open(self.log, 'rb')
                    off, rest = 0, b''
                size = os.fstat(fh.fileno()).st_size
                if size < off:
                    fh.close()
                    fh = open(self.log, 'rb')
                    off, rest = 0, b''
                fh.seek(off)
                data = fh.read()
                q = time.perf_counter_ns()
                off += len(data)
                if data:
                    chunk = rest + data
                    parts = chunk.split(b'\n')
                    rest = parts.pop()
                    for p in parts:
                        m = FT.match(p)
                        if m:
                            n = int(m.group(1))
                            if n > seen:
                                seen = n
                                fo.write('CAL qpc_ns=%d n=%d\n' % (q, n))
                                self.lines += 1
                    fo.flush()
            except OSError:
                fh = None
            if last:
                break
            time.sleep(self.poll)
        if fh is not None:
            fh.close()
        fo.close()


def main(argv):
    def a(k, d=None):
        return argv[argv.index(k) + 1] if k in argv else d
    pidf, local, out, stop, lp, cal = a('--pidfile'), a('--local'), a('--out'), a('--stop'), a('--loadpids'), a('--cal')
    period = float(a('--period', 1))
    poll = float(a('--poll', 0.05))
    max_s = float(a('--max-s', 900))
    fake = json.load(open(a('--fake'), encoding='ascii')) if a('--fake') else None
    own = os.getpid()
    t0 = time.monotonic()
    stop_ev = threading.Event()
    poller = None
    if cal and fake is None:
        poller = Poller(a('--log', LIVE_LOG), cal, pidf, stop_ev, poll)
        poller.start()
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
            qpc = 1000000000 * (k + 1)
            k += 1
        else:
            if (stop and os.path.exists(stop)) or time.monotonic() - t0 > max_s:
                break
            snap = snapshot()
            now = time.monotonic()
            qpc = time.perf_counter_ns()
        if prev is not None:
            dt = max(now - prev_t, 1e-6)
            rates = dict((key, (c - prev[key]) / dt) for key, c in snap.items() if key in prev)
            game = game_pid(pidf) if pidf else None
            loader = read_pids(lp) if lp else set()
            et = None if fake is not None else emu_t(game)
            tt = now - (0 if fake is not None else t0)
            ln, tot = line(tt, et, qpc, rates, game, loader, own, False)
            lm, _ = line(tt, et, qpc, rates, game, loader, own, True)
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
    stop_ev.set()
    if poller is not None:
        poller.join(30)
    end = 'M6 end samples=%d foreign_max=%.2f foreign_mean=%.2f cal_lines=%d' % (n, fmax, fsum / n if n else 0.0,
                                                                               poller.lines if poller else 0)
    fl.write(end + '\n')
    fo.write(end + '\n')
    fl.close()
    fo.close()
    print(end)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
