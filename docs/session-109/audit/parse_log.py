"""Audit 109: independent raw-log parser (does NOT import any session scorer).
usage: python parse_log.py <tag>   -> C:/kyty/s109/audit109/parsed/<tag>.pkl
Keeps: every FrameTrace / FrameTrace-draw / FrameTrace-x row (selected fields), per-block sums of ALL numeric
fields for the frm-style kept window (n >= 1801, (n-1801) % 90 in [60, 88]), event lines with the last main n seen.
"""
import pickle
import re
import sys
from pathlib import Path

tag = sys.argv[1]
root = Path(sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s109')
out_dir = Path('C:/kyty/s109/audit109/parsed')
out_dir.mkdir(parents=True, exist_ok=True)
log = root / ('log_%s.txt' % tag)

TOK = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
MAIN_KEEP = {b'n', b'dt_us', b'lat_us', b'gpu_busy_us', b'gpu_n', b'submits', b'submit_us', b'semwaits',
             b'semwait_us', b'semwait_gpu_us', b'draws', b'dispatches', b'cpu_gpu_us', b'cpu_main_us',
             b'cpu_present_us', b'cpu_proc_us', b'arm', b'blk', b'prios', b'dmas', b'faults', b'wrm_stalls',
             b'rt_w', b'rt_h'}
DRAW_KEEP = {b'n', b'spin_gpu_us', b'rec_n', b'da_walk_us', b'da_walks', b'da_queue_us', b'da_take_us', b'da_hit',
             b'da_miss', b'da_late', b'da_stale', b'img_up', b'img_up_kb', b'pops', b'acopy_waits'}
X_PREFIXES = (b'cs_sync', b'cspf', b'cspfam', b'cspfree', b'cspm', b'da_w', b'pl_', b'gw_', b'rt_att', b'rt_kpx',
              b'bf_', b'gm_', b'mw_n', b'a_hold', b'a_mut', b'sh_jobs', b'da_qcall', b'rec_spin', b'rec_sleep',
              b'gclk')
EVENTS = (b'AsyncCompute:', b'GateArm:', b'GpuClockPin', b'PipelinePrecache', b'CspFreeVerify', b'--- Error',
          b'--- Fatal', b'--- std::terminate', b'--- abort', b'ErrorDeviceLost', b'Unhandled exception',
          b'GpuWaitSlow', b'GpuHangAbort', b'AsyncPipelines: skipped', b'Level has started', b'RecordThread: started',
          b'GPU checkpoints', b'Recording:', b'AvTrace: pipeline', b'Shader translation cache: dropping')

main, draw, x = {}, {}, {}
order = []
events = []
dup = {'main': 0, 'draw': 0, 'x': 0}
blocksum = {}  # (kind, block) -> {field: sum}
blockcnt = {}
last_n = None
line_no = 0


def in_window(n):
    if n < 1801:
        return None
    k = (n - 1801) % 90
    if 60 <= k <= 88:
        return (n - 1801) // 90
    return None


with open(log, 'rb') as f:
    for raw in f:
        line_no += 1
        if raw.startswith(b'FrameTrace'):
            if raw.startswith(b'FrameTrace: '):
                kind, store, keep = 'main', main, MAIN_KEEP
            elif raw.startswith(b'FrameTrace-draw: '):
                kind, store, keep = 'draw', draw, DRAW_KEEP
            elif raw.startswith(b'FrameTrace-x: '):
                kind, store, keep = 'x', x, None
            else:
                continue
            toks = TOK.findall(raw)
            if not toks or toks[0][0] != b'n':
                continue
            n = int(toks[0][1])
            if n in store:
                dup[kind] += 1
            if kind == 'main':
                order.append(n)
                last_n = n
            row = {}
            for k, v in toks:
                if keep is None:
                    if k == b'n' or k.startswith(X_PREFIXES):
                        row[k.decode()] = int(v)
                elif k in keep:
                    row[k.decode()] = int(v)
            store[n] = row
            b = in_window(n)
            if b is not None:
                s = blocksum.setdefault((kind, b), {})
                for k, v in toks:
                    kk = k.decode()
                    s[kk] = s.get(kk, 0) + int(v)
                blockcnt[(kind, b)] = blockcnt.get((kind, b), 0) + 1
            continue
        head = raw[:120]
        for e in EVENTS:
            if e in head:
                events.append((line_no, last_n, raw[:400].decode('utf-8', 'replace').rstrip()))
                break

with open(out_dir / ('%s.pkl' % tag), 'wb') as h:
    pickle.dump({'tag': tag, 'main': main, 'draw': draw, 'x': x, 'order': order, 'events': events, 'dup': dup,
                 'blocksum': blocksum, 'blockcnt': blockcnt, 'lines': line_no}, h)
print(tag, 'lines', line_no, 'main', len(main), 'draw', len(draw), 'x', len(x), 'events', len(events), 'dup', dup)
