# Session 128, design of knob "protceil" (Probe Designer): rows [c] from the sealed k3p127 log of session 127.
# Blocks by GateArm: lines (never by blk); window positions 10..88 of item 55(b); level = mean of window rows.
# Arm 0 = rtskip=0, arm 1 = rtskip=1 (build 98d98eee, Sky Garden, BDA NEW, pin). Read only; prints means per arm.
import re
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s127/log_k3p127.txt'
KEYS = ['dt_us', 'cpu_gpu_us', 'cpu_main_us', 'draws', 'faults', 'fault_us',
        'faults_main', 'fault_main_us', 'sync_ups', 'bb_upload', 'bb_sync',
        'img_up', 'img_up_kb', 'prot_us', 'prot_pages', 'protw_us', 'protw_pages',
        'prot_calls', 'prot_ro', 'prot_ro_pages', 'prot_na', 'prot_na_pages', 'prot_rw_us', 'prot_rw_pages',
        'prot_gpu_us', 'prot_gpu', 'prot_gpu_pages', 'prot_held_us', 'bda_us', 'bda_n', 'bda_scan',
        'prot_spin_gpu_us', 'prot_spin_gpu_calls', 'sync_noop', 'sf_skip',
        'pb_pages', 'pb_flush', 'pb_runs', 'pb_kb', 'pb_merged', 'pb_wait_us', 'pb_wait_gpu_us',
        'pb_inval_flush', 'pb_refault', 'pb_stuck', 'pb_wait_sync_us', 'pb_wait_scope_us', 'pb_wait_range_us',
        'pb_wait_worker_us', 'pb_sync_noprot', 'fw_n', 'fw_widened', 'sync_up_kb', 'rt_kpx', 'rt_att']
kv = re.compile(rb'([a-z0-9_]+)=(\d+)')
rows = {}
order = []          # (block, arm_text, n) for main rows
block = -1
arm_text = None
with open(LOG, 'rb') as f:
    for line in f:
        if line.startswith(b'GateArm:') or b' GateArm: ' in line[:40]:
            m = re.search(rb'text=(\S+)', line)
            block += 1
            arm_text = m.group(1).decode() if m else '?'
            continue
        for tag in (b'FrameTrace: ', b'FrameTrace-draw: ', b'FrameTrace-x: '):
            i = line.find(tag)
            if i < 0:
                continue
            d = {k.decode(): int(v) for k, v in kv.findall(line[i + len(tag):])}
            n = d.get('n')
            if n is None:
                break
            rows.setdefault(n, {}).update(d)
            if tag == b'FrameTrace: ' and block >= 0:
                order.append((block, arm_text, n))
            break
pos = {}
count = {}
for b, a, n in order:
    count[b] = count.get(b, 0)
    pos[n] = (b, a, count[b])
    count[b] += 1
acc = {}
for n, (b, a, p) in pos.items():
    if 10 <= p <= 88:
        acc.setdefault(a, []).append(rows[n])
print('log', LOG, 'blocks', block + 1)
for a in sorted(acc):
    rs = acc[a]
    print('arm', a, 'rows', len(rs))
    for k in KEYS:
        vals = [r[k] for r in rs if k in r]
        if vals:
            print('  %-20s %12.1f' % (k, sum(vals) / len(vals)))
        else:
            print('  %-20s %12s' % (k, 'absent'))
