"""Read-only: device-local usage (MemStats heap=0) against the buffer-cache GC trigger, per log,
beside the BDA regime of the frames that follow each MemStats sample.

usage: python memstats.py <log> [<log> ...]
The trigger is recomputed from the logged heap-0 budget exactly as BufferCache::BufferCache does
(bufferCache.cpp:395-406) with GraphicContext::GetTotalMemoryBudget (vma.cpp, discrete branch).
"""
import re
import statistics as st
import sys

GiB = 1024 ** 3
MS = re.compile(rb'MemStats: heap=(\d+) flags=0x([0-9a-f]+) size=(\d+) usage=(\d+) budget=(\d+) allocation=(\d+) blocks=(\d+)')
FT = re.compile(rb'FrameTrace: n=(\d+)')
FD = re.compile(rb'FrameTrace-draw: n=(\d+) .*? buf_new=(\d+) .*? bda_scan=(\d+) bda_skip=(\d+)')
PM4GC = re.compile(rb'FrameTrace-pm4:.*?\bgc=(\d+)/(\d+)')


def triggers(heap0_budget):
    budget = heap0_budget - min(heap0_budget // 8, GiB)  # GetTotalMemoryBudget, discrete
    threshold = min(budget, 8 * GiB)
    expected = min(budget - 6 * threshold // 10, budget - GiB)
    critical = min(budget - 2 * threshold // 10, budget - GiB // 2)
    buf_trigger = max(expected, GiB)
    buf_critical = max(critical, 2 * GiB)
    tex_trigger = max((budget - threshold) // 2, 0)
    tex_pressure = max(min(budget - 6 * threshold // 10, budget - GiB), GiB + GiB // 2)
    return budget, buf_trigger, buf_critical, tex_trigger, tex_pressure


def main():
    for path in sys.argv[1:]:
        samples = []  # (frame, usage, budget, alloc, blocks)
        scan = {}
        bufnew = {}
        gcn = {}
        cur = 0
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'FrameTrace: n='):
                    cur = int(FT.match(line).group(1))
                elif line.startswith(b'FrameTrace-draw:'):
                    m = FD.match(line)
                    if m:
                        n = int(m.group(1))
                        bufnew[n] = int(m.group(2))
                        scan[n] = int(m.group(3))
                elif line.startswith(b'FrameTrace-pm4:'):
                    m = PM4GC.match(line)
                    if m:
                        gcn[cur] = int(m.group(2))
                elif line.startswith(b'MemStats: heap=0'):
                    m = MS.match(line)
                    if m:
                        samples.append((cur, int(m.group(4)), int(m.group(5)), int(m.group(6)), int(m.group(7))))
        print('=' * 100)
        print(path)
        if not samples:
            print('  no MemStats')
            continue
        b0 = samples[0][2]
        budget, bt, bc, tt, tp = triggers(b0)
        print('  heap0 budget %d -> total %d; buffer GC trigger %d (%.3f GiB) critical %d; texture trigger %d pressure %d' % (
            b0, budget, bt, bt / GiB, bc, tt, tp))
        for (n, usage, bud, alloc, blocks) in samples:
            nxt = [scan[k] for k in range(n + 1, n + 301) if k in scan]
            nb = [bufnew[k] for k in range(n + 1, n + 301) if k in bufnew]
            g = [gcn[k] for k in range(n + 1, n + 301) if k in gcn]
            old = sum(1 for v in nxt if v >= 500)
            print('  frame %6d usage %6.3f GiB (%s trigger by %+7.0f MiB) budget %s alloc %6.3f blocks %6.3f | next300: scan med %s OLDfrac %.2f buf_new mean %.2f gc/frame %.1f' % (
                n, usage / GiB, 'ABOVE' if usage >= bt else 'below', (usage - bt) / 2 ** 20,
                'same' if bud == b0 else str(bud), alloc / GiB, blocks / GiB,
                st.median(nxt) if nxt else '-', old / len(nxt) if nxt else float('nan'),
                sum(nb) / len(nb) if nb else float('nan'), sum(g) / len(g) if g else float('nan')))


if __name__ == '__main__':
    main()
