# Session 129, design of knob "armcopy" (Probe Designer): rows [c] from the sealed pd128 log of session 128.
# Blocks by GateArm: lines (never by blk); window positions 10..88 of item 55(b): FrameTrace n = F + 1 + p, where F is
# the frame= of the block's GateArm line (the form of the pd128 scorer, ROADMAP s122 item 95(a)); level = mean of the
# window rows. Arms: protceil=0 (the shipped state, rtskip=1) and protceil=2 (the dose). Build 45d36512, Sky Garden,
# pin. Read only; prints means per arm and the derived shares of section 3 of design129.md. Not a gain, a census.
import re
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s128/log_pd128.txt'
KEYS = ['dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'bda_scan',
        'prot_gpu_us', 'prot_gpu', 'prot_gpu_ro_ns', 'prot_gpu_ro_n', 'prot_gpu_ro_pages',
        'prot_gpu_na_ns', 'prot_gpu_na_n', 'prot_gpu_rw_ns', 'prot_gpu_rw_n',
        'pc_op0', 'pc_elig_ns', 'pc_elig_n', 'pc_elig_pages', 'pc_elig_scope_n', 'pc_elig_rng_n',
        'pc_dose_n', 'pc_dose_ns',
        'sync_ups', 'sync_up_kb', 'sync_noop', 'stg_pool_n', 'stg_pool_b', 'stg_pool_ns',
        'stg_in_n', 'stg_inbig_n', 'stg_in_b', 'stg_in_gpu_b', 'stg_in_ns', 'up_tmp_n', 'up_tmp_b',
        'stg_img_pool_b', 'stg_img_in_b', 'bi_ok',
        'acopy_wait_us', 'acopy_waits', 'acopy_gpu_waits',
        'pb_wait_us', 'pb_wait_gpu_us', 'pb_wait_scope_us', 'pb_wait_range_us', 'pb_wait_sync_us',
        'pb_wait_worker_us', 'pb_flush', 'pb_runs', 'pb_merged', 'pb_inval_flush', 'pb_refault',
        'protw_us', 'protw_pages', 'prot_us', 'prot_calls', 'prot_ro', 'prot_na', 'fw_n', 'faults', 'fault_us']
kv = re.compile(rb'([a-z0-9_]+)=(\d+)')
gate = re.compile(rb'GateArm: arm=(\d+) .*?frame=(\d+) .*?text=(\S+)')
rows = {}
blocks = []  # (arm_text, F)
with open(LOG, 'rb') as f:
    for line in f:
        if b'GateArm: ' in line[:40]:
            m = gate.search(line)
            if m:
                blocks.append((m.group(3).decode(), int(m.group(2))))
            continue
        for tag in (b'FrameTrace: ', b'FrameTrace-draw: ', b'FrameTrace-x: '):
            i = line.find(tag)
            if i < 0:
                continue
            d = {k.decode(): int(v) for k, v in kv.findall(line[i + len(tag):])}
            n = d.get('n')
            if n is not None:
                rows.setdefault(n, {}).update(d)
            break
acc = {}
for a, F in blocks:
    for p in range(10, 89):
        r = rows.get(F + 1 + p)
        if r is not None and 'dt_us' in r:
            acc.setdefault(a, []).append(r)
print('log', LOG, 'blocks', len(blocks))
mean = {}
for a in sorted(acc):
    rs = acc[a]
    print('arm', a, 'rows', len(rs))
    mean[a] = {}
    for k in KEYS:
        vals = [r[k] for r in rs if k in r]
        if vals:
            mean[a][k] = sum(vals) / len(vals)
            print('  %-20s %14.2f   (rows %d)' % (k, mean[a][k], len(vals)))
        else:
            print('  %-20s %14s' % (k, 'absent'))
m = mean.get('protceil=0', {})
if m:
    g = lambda k: m.get(k, float('nan'))
    print('derived, arm protceil=0 (window 10..88 of item 55(b))')
    print('  pc_elig_ns/1000 (us)                     %10.1f' % (g('pc_elig_ns') / 1000))
    print('  pc_elig_ns / prot_gpu_ro_ns              %10.4f' % (g('pc_elig_ns') / g('prot_gpu_ro_ns')))
    print('  ns per eligible call                     %10.1f' % (g('pc_elig_ns') / g('pc_elig_n')))
    sync_n = g('pc_elig_n') - g('pc_elig_scope_n') - g('pc_elig_rng_n')
    print('  eligible calls: scope / range / sync     %10.1f %10.1f %10.1f' % (g('pc_elig_scope_n'), g('pc_elig_rng_n'), sync_n))
    copies = g('stg_pool_n') + g('stg_in_n') + g('stg_inbig_n')
    print('  copies: pooled / inline small / inline big %8.1f %8.1f %8.1f  (sum %.1f)' % (g('stg_pool_n'), g('stg_in_n'), g('stg_inbig_n'), copies))
    print('  pooled share of copies (count)           %10.4f' % (g('stg_pool_n') / copies))
    print('  pooled share of copied bytes             %10.4f' % (g('stg_pool_b') / (g('stg_pool_b') + g('stg_in_b'))))
    print('  pooled bytes per pooled copy (KiB)       %10.1f' % (g('stg_pool_b') / g('stg_pool_n') / 1024))
    print('  inline bytes per inline copy (KiB)       %10.1f' % (g('stg_in_b') / max(g('stg_in_n') + g('stg_inbig_n'), 1e-9) / 1024))
    print('  stg_pool_ns/1000 (us, GuestGpu hand-over) %9.1f' % (g('stg_pool_ns') / 1000))
