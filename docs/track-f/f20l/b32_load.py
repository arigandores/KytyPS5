"""Track F link F20l (HPP-631; ROADMAP s122 item 550 (d)(4)-(5)): the harness loader of the controls PK-D b32_pd (all logical CPUs) and
PK-D2 b32_pd2 (ceil(ncpu / 2) CPUs): busy processes at the ABOVE_NORMAL priority class, 400 ms, at 60 s after the first line
'Level has started: underwater_aerial_garden' of the live log (the arm of the stands KYTY_TEST_B32 is the same first level line).  ASCII.

    python b32_load.py --mode all|half --pidfile <game_pid.txt> --log <_kyty.txt> --out <load.json> --pids <load_pids.txt> --stop <file>
                       [--delay-s 60] [--burst-ms 400] [--wait-s 600]

Order: wait for the pid file of the own emulator (enter_scene.py writes it after the launch; _kyty.txt was moved to _kyty.prev.txt before
the launch, so the log read from offset 0 after the pid file is the new one), read the log incrementally (no tail -F: one open handle,
read of the new bytes every POLL s) until the level line; at the arm spawn the workers (they wait on an event; their pids go to --pids for
M6); at arm + delay: n_start = the last 'FrameTrace: n=' read up to that moment (the log is read to its end first), the event is set,
the workers spin until the deadline; after the burst the log is read to its end again: n_end.  load.json: status (done / no_arm / stopped /
no_pidfile), mode, ncpu, workers, priority class read back, t_arm / burst start / end (UTC and perf_counter), n_start, n_end, CPU s of
the workers during the burst.  The stop file or --wait-s ends it without a burst.
"""
import ctypes
import json
import math
import multiprocessing
import os
import re
import sys
import time

ABOVE_NORMAL = 0x8000
POLL = 0.05
LVL = b'Level has started: underwater_aerial_garden'
FT = re.compile(rb'FrameTrace: n=(\d+) ')


def utc(t=None):
    t = time.time() if t is None else t
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(t)) + ('.%03dZ' % int((t % 1) * 1000))


def set_prio():
    if os.name != 'nt':
        return None
    k = ctypes.windll.kernel32
    k.GetCurrentProcess.restype = ctypes.c_void_p         # the pseudo-handle -1 must not be truncated to a 32-bit int
    k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    k.GetPriorityClass.argtypes = [ctypes.c_void_p]
    h = ctypes.c_void_p(k.GetCurrentProcess())
    k.SetPriorityClass(h, ABOVE_NORMAL)
    return k.GetPriorityClass(h)


def worker(ev, deadline_q, ready_q, cpu_q):
    pc = set_prio()
    ready_q.put((os.getpid(), pc))
    ev.wait()
    deadline = deadline_q.get()
    c0 = time.process_time()
    x = 0
    while time.perf_counter() < deadline:
        x += 1
    cpu_q.put(time.process_time() - c0)


class LogReader:
    def __init__(self, path):
        self.path = path
        self.f = None
        self.buf = b''
        self.last_n = None
        self.level_seen = False

    def poll(self):
        if self.f is None:
            if not os.path.exists(self.path):
                return
            self.f = open(self.path, 'rb')
        data = self.f.read()
        if not data:
            return
        data = self.buf + data
        lines = data.split(b'\n')
        self.buf = lines.pop()
        for line in lines:
            if line.startswith(b'FrameTrace: n='):
                m = FT.match(line)
                if m:
                    self.last_n = int(m.group(1))
            elif not self.level_seen and LVL in line:
                self.level_seen = True


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv):
    mode = arg(argv, '--mode')
    if mode not in ('all', 'half'):
        print('usage: b32_load.py --mode all|half ...')
        return 2
    pidfile, logp, out, pids, stop = (arg(argv, k) for k in ('--pidfile', '--log', '--out', '--pids', '--stop'))
    delay = float(arg(argv, '--delay-s', 60))
    burst = float(arg(argv, '--burst-ms', 400)) / 1000.0
    wait_s = float(arg(argv, '--wait-s', 600))
    ncpu = os.cpu_count()
    nw = ncpu if mode == 'all' else int(math.ceil(ncpu / 2.0))
    res = dict(status=None, mode=mode, ncpu=ncpu, workers=nw, delay_s=delay, burst_ms=burst * 1000, priority_class=None)

    def done(status):
        res['status'] = status
        with open(out, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1)
        print('loader %s mode %s workers %d n_start %s n_end %s' % (status, mode, nw, res.get('n_start'), res.get('n_end')))
        return 0

    t0 = time.monotonic()
    while not os.path.exists(pidfile):
        if (stop and os.path.exists(stop)) or time.monotonic() - t0 > wait_s:
            return done('no_pidfile')
        time.sleep(POLL)
    lr = LogReader(logp)
    while not lr.level_seen:
        lr.poll()
        if (stop and os.path.exists(stop)) or time.monotonic() - t0 > wait_s:
            return done('no_arm')
        time.sleep(POLL)
    t_arm = time.perf_counter()
    res['t_arm'] = utc()
    ctx = multiprocessing.get_context('spawn')
    ev = ctx.Event()
    dq = ctx.Queue()
    rq = ctx.Queue()
    cq = ctx.Queue()
    procs = [ctx.Process(target=worker, args=(ev, dq, rq, cq), daemon=True) for _ in range(nw)]
    for p in procs:
        p.start()
    got = [rq.get(timeout=60) for _ in procs]
    res['priority_class'] = sorted(set(pc for _, pc in got))
    with open(pids, 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(str(pid) for pid, _ in got) + '\n')
    while time.perf_counter() < t_arm + delay:
        lr.poll()
        if stop and os.path.exists(stop):
            ev.set()
            for _ in procs:
                dq.put(0.0)
            return done('stopped')
        time.sleep(POLL)
    lr.poll()
    res['n_start'] = lr.last_n
    start = time.perf_counter()
    res['burst_start_utc'] = utc()
    for _ in procs:
        dq.put(start + burst)
    ev.set()
    cpus = []
    for _ in procs:
        try:
            cpus.append(cq.get(timeout=10))
        except Exception:  # noqa: BLE001
            break
    end = time.perf_counter()
    for p in procs:
        p.join(timeout=10)
    res['burst_end_utc'] = utc()
    res['burst_s'] = round(end - start, 4)
    res['arm_to_burst_s'] = round(start - t_arm, 3)
    res['worker_cpu_s'] = round(sum(cpus), 3)
    res['worker_cpu_n'] = len(cpus)
    time.sleep(0.3)
    lr.poll()
    res['n_end'] = lr.last_n
    res['exitcodes'] = sorted(set(p.exitcode for p in procs))
    return done('done')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
