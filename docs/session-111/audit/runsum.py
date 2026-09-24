# Per-run means (rows n >= FIRST, optional arm split) of selected FrameTrace fields (audit 111).
import sys, re
tok = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
F = ['main:dt_us', 'main:cpu_gpu_us', 'main:gpu_busy_us', 'main:draws', 'main:semwait_us', 'draw:bda_scan', 'draw:da_take_us',
     'draw:da_queue_us', 'draw:da_walk_us', 'draw:da_hit', 'draw:da_miss', 'draw:da_late', 'draw:spin_gpu_us',
     'x:da_qcall', 'x:da_q_free', 'x:da_guard_busy', 'x:da_q_taking', 'x:da_hint_defer', 'x:cspfree_hit', 'x:pl_cont_wall_ns',
     'x:pl_wq_hold_ns', 'x:pl_wq_hold_n', 'x:da_chk_ok', 'x:rt_kpx']
RUNS = {
    'shp110': 'C:/kyty/s110/log_shp110.txt', 'vid110': 'C:/kyty/s110/log_vid110.txt',
    'obs111': 'C:/kyty/s111/log_obs111.txt', 'vds111': 'C:/kyty/s111/log_vds111.txt', 'vds111b': 'C:/kyty/s111/log_vds111b.txt',
    'shp111': 'C:/kyty/s111/log_shp111.txt', 'vss111': 'C:/kyty/s111/log_vss111.txt', 'vid111': 'C:/kyty/s111/log_vid111.txt',
}
first = int(sys.argv[1]) if len(sys.argv) > 1 else 2100
for tag in sys.argv[2:] or RUNS:
    rows = {}
    with open(RUNS[tag], 'rb') as f:
        for raw in f:
            if not raw.startswith(b'FrameTrace'): continue
            sp = raw.find(b' '); kind = raw[:sp]
            if kind == b'FrameTrace:': pre = 'main'
            elif kind == b'FrameTrace-draw:': pre = 'draw'
            elif kind == b'FrameTrace-x:': pre = 'x'
            else: continue
            d = tok.findall(raw)
            if not d or d[0][0] != b'n': continue
            n = int(d[0][1])
            if n < first: continue
            r = rows.setdefault(n, {})
            dd = dict(d)
            for k in F:
                p, name = k.split(':')
                if p == pre and name.encode() in dd: r[k] = int(dd[name.encode()])
            if pre == 'main' and b'arm' in dd: r['arm'] = int(dd[b'arm'])
    groups = {}
    for n, r in rows.items():
        if 'main:dt_us' not in r: continue
        groups.setdefault(r.get('arm', -1), []).append(r)
    for a, rs in sorted(groups.items()):
        out = []
        for k in F:
            v = [r[k] for r in rs if k in r]
            if v: out.append('%s=%.1f' % (k.split(':')[1], sum(v) / len(v)))
        print('%-8s arm%-2d rows %5d  %s' % (tag, a, len(rs), ' '.join(out)))
