"""Read-only sweep: for each archived log, device-local usage vs the buffer-GC trigger at every
MemStats sample (frame >= 600) and the BDA level of the 300 frames that follow it.

usage: python sweep.py <out.tsv> <log> [<log> ...]
Columns: log, frame, usage_mib, trigger_mib, delta_mib, blocks_mib, alloc_mib, frames, old_frac, buf_new_mean
"""
import re
import sys

GiB = 1024 ** 3
MiB = 1024 ** 2
MS = re.compile(rb'MemStats: heap=0 .*? usage=(\d+) budget=(\d+) allocation=(\d+) blocks=(\d+)')
FD = re.compile(rb'FrameTrace-draw: n=(\d+) .*? buf_new=(\d+) .*? bda_scan=(\d+) ')


def trigger(heap0_budget):
    budget = heap0_budget - min(heap0_budget // 8, GiB)
    threshold = min(budget, 8 * GiB)
    return max(min(budget - 6 * threshold // 10, budget - GiB), GiB)


def one(path, out):
    samples = []
    scan = {}
    bufnew = {}
    cur = 0
    first_budget = None
    with open(path, 'rb') as f:
        for line in f:
            c = line[:12]
            if c == b'FrameTrace: ':
                m = re.match(rb'FrameTrace: n=(\d+)', line)
                if m:
                    cur = int(m.group(1))
            elif c == b'FrameTrace-d' and line.startswith(b'FrameTrace-draw:'):
                m = FD.match(line)
                if m:
                    n = int(m.group(1))
                    bufnew[n] = int(m.group(2))
                    scan[n] = int(m.group(3))
            elif c == b'MemStats: he' and line.startswith(b'MemStats: heap=0'):
                m = MS.match(line)
                if m:
                    u, b, a, bl = (int(x) for x in m.groups())
                    if first_budget is None:
                        first_budget = b
                    samples.append((cur, u, b, a, bl))
    if first_budget is None:
        out.write('%s\tNO_MEMSTATS\n' % path)
        return
    trig = trigger(first_budget)
    for (n, u, b, a, bl) in samples:
        if n < 600:
            continue
        nxt = [scan[k] for k in range(n + 1, n + 301) if k in scan]
        nb = [bufnew[k] for k in range(n + 1, n + 301) if k in bufnew]
        if not nxt:
            continue
        old = sum(1 for v in nxt if v >= 500) / len(nxt)
        out.write('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.3f\t%.3f\t%d\n' % (
            path, n, u // MiB, trig // MiB, (u - trig) // MiB, bl // MiB, a // MiB, len(nxt), old,
            sum(nb) / len(nb) if nb else -1, b // MiB))
    out.flush()


def main():
    with open(sys.argv[1], 'w') as out:
        out.write('log\tframe\tusage_mib\ttrigger_mib\tdelta_mib\tblocks_mib\talloc_mib\tframes\told_frac\tbuf_new_mean\tbudget_mib\n')
        paths = []
        for arg in sys.argv[2:]:
            if arg.startswith('@'):
                paths += [x.strip() for x in open(arg[1:]).read().splitlines() if x.strip()]
            else:
                paths.append(arg)
        for p in paths:
            try:
                one(p, out)
            except Exception as e:  # noqa: BLE001 - a broken log must not stop the sweep
                out.write('%s\tERROR %r\n' % (p, e))
            out.flush()


if __name__ == '__main__':
    main()
