# Session 124 design (HPP-56), Probe Designer: per-arm and per-class means of FrameTrace / FrameTrace-x fields in a sealed
# ABBA log, window positions 10..87 of full blocks (88+ rows) by the blk= field of the main line.  Design rows only [I].
# Usage: python cls124.py <log> [field ...]   (x_ prefix = a FrameTrace-x field)
import re, sys
kv = re.compile(rb'(\w+)=(-?\d+)')
path = sys.argv[1]
keys = sys.argv[2:] or ['dt_us', 'cpu_gpu_us', 'x_gw_proc_ns', 'x_gw_flip_ns', 'x_gw_idle_ns', 'x_flip_rsv_wait_ns',
                        'x_flip_hold_ns', 'x_skc_pres_ns', 'x_skc_pres_n', 'x_skc_held']
main, x = {}, {}
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: '):
            d = {k.decode(): int(v) for k, v in kv.findall(line)}
            main[d['n']] = d
        elif line.startswith(b'FrameTrace-x: '):
            d = {k.decode(): int(v) for k, v in kv.findall(line)}
            x[d['n']] = d
rows = []
for n in sorted(main):
    if n in x and 'arm' in main[n]:
        r = dict(main[n])
        r.update({'x_' + k: v for k, v in x[n].items()})
        rows.append(r)
count = {}
for r in rows:
    b = r['blk']
    r['pos'] = count.get(b, 0)
    count[b] = r['pos'] + 1
full = {b for b, c in count.items() if c >= 88}
win = [r for r in rows if r['blk'] in full and 10 <= r['pos'] <= 87]
a0 = [r for r in win if r['arm'] == 0]
a1 = [r for r in win if r['arm'] == 1]
held = [r for r in a1 if r.get('x_skc_held', 0) >= 1]
rest = [r for r in a1 if r.get('x_skc_held', 0) == 0]
mean = lambda rs, k: sum(r.get(k, 0) for r in rs) / len(rs) if rs else float('nan')
print('rows arm0 %d arm1 held %d arm1 not-held %d' % (len(a0), len(held), len(rest)))
for k in keys:
    print('%-22s arm0 %14.1f  arm1-held %14.1f  arm1-not-held %14.1f' % (k, mean(a0, k), mean(held, k), mean(rest, k)))
