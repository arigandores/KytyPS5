"""Cross-run context (not a verdict): mean dt/cpu_gpu/bda_scan over frames > 1800, in-block index 10..89 of the
90-frame grid starting at 1801, for earlier pinned Sky Garden runs, per arm= value on the main line."""
import sys, statistics, collections, json, re

LOGS = sys.argv[1:]


def kv(rest):
    d = {}
    for t in rest.split():
        if b'=' in t:
            k, v = t.split(b'=', 1)
            try:
                d[k.decode()] = int(v)
            except ValueError:
                pass
    return d


for p in LOGS:
    main = {}; draw = {}; env = []
    with open(p, 'rb') as f:
        for ln in f:
            if ln.startswith(b'FrameTrace: '):
                d = kv(ln[12:]); main[d['n']] = d
            elif ln.startswith(b'FrameTrace-draw: '):
                d = kv(ln[17:]); draw[d['n']] = {k: d.get(k) for k in ('bda_scan', 'da_walk_us')}
            elif ln.startswith(b'GateArm:') and len(env) < 2:
                env.append(ln.strip()[:120])
            elif ln.startswith(b'GpuClockPin'):
                env.append(ln.strip()[:40])
    last = max(main)
    per = collections.defaultdict(list)
    for n, d in main.items():
        if n <= 1800:
            continue
        b = (n - 1801) // 90; i = (n - 1801) % 90
        if not (10 <= i <= 89):
            continue
        if 1801 + 90 * (b + 1) - 1 > last:
            continue
        per[d.get('arm')].append((d['dt_us'], d['cpu_gpu_us'], (draw.get(n) or {}).get('bda_scan')))
    print(p)
    for e in env:
        print('   ', e)
    for a, rows in sorted(per.items()):
        print(f'   arm {a}: n={len(rows)} dt={statistics.fmean(r[0] for r in rows):.1f} '
              f'median_dt={statistics.median(r[0] for r in rows):.1f} cpu_gpu={statistics.fmean(r[1] for r in rows):.1f} '
              f'bda_scan_median={statistics.median(r[2] for r in rows if r[2] is not None)}')
