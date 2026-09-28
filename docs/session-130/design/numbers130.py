# Session 130, design of knob "acinline" (Probe Designer, HPP-143): rows [c] from the sealed ac129 log of session 129
# (and, with a second argument, any other log of the same build: ack129 at armcopy=2).
# Blocks by GateArm: lines (never by blk); window positions 10..88 of item 55(b): FrameTrace n = F + 1 + p, where F is
# the frame= of the block's GateArm line (the form of the ac129 scorer); level = mean of the window rows. Arms by the
# TEXT of the GateArm line. Build edd17418, Sky Garden, pin. Read only; prints means per arm, the per-pair difference
# (arm 1 - arm 0, pairs (2k, 2k+1) of the ABBA order) of a few rows, and the derived per-call shares of design130.md s.2.
# Not a gain, a census.
import math
import re
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s129/log_ac129.txt'
KEYS = ['dt_us', 'draws', 'cpu_gpu_us', 'gpu_busy_us', 'bda_scan',
        'prot_gpu_us', 'prot_gpu', 'prot_gpu_ro_ns', 'prot_gpu_ro_n', 'prot_gpu_ro_pages',
        'prot_gpu_na_ns', 'prot_gpu_na_n', 'pc_elig_ns', 'pc_elig_n', 'pc_elig_pages',
        'sync_ups', 'sync_up_kb', 'sync_noop', 'stg_pool_n', 'stg_pool_b', 'stg_pool_ns',
        'stg_in_n', 'stg_inbig_n', 'stg_in_b', 'stg_in_gpu_b', 'stg_in_ns', 'up_tmp_n',
        'stg_img_pool_b', 'stg_img_in_b', 'bi_ok',
        'acopy_wait_us', 'acopy_waits', 'acopy_gpu_waits',
        'pb_wait_us', 'pb_wait_gpu_us', 'pb_wait_scope_us', 'pb_wait_range_us',
        'protw_us', 'prot_us', 'prot_calls', 'prot_ro', 'prot_ro_pages', 'prot_na', 'fw_n', 'faults', 'fault_us',
        'ac_n', 'ac_refuse', 'ac_offthr', 'ac_jobs', 'ac_chunks', 'ac_moved_n', 'ac_moved_ns', 'ac_moved_pages',
        'ac_kept_n', 'ac_kept_ns', 'ac_kept_inl_n', 'ac_kept_inl_ns', 'ac_kept_gap_n', 'ac_kept_gap_ns',
        'ac_kept_full_n', 'ac_kept_full_ns', 'ac_kept_tmp_n', 'ac_kept_tmp_ns', 'ac_kept_wr_n', 'ac_kept_wr_ns',
        'ac_kept_help_n', 'ac_kept_help_ns', 'ac_job_other_n', 'ac_job_nowork', 'ac_job_wait_ns',
        'ac_chk', 'ac_bad', 'ac_chk_ns', 'ac_jleft', 'ac_jremark', 'ac_gchk', 'ac_gbad', 'ac_gchk_ns', 'ac_gjleft',
        'ac_orphan', 'ac_cmp_pages', 'ac_cdiff', 'ac_cbad']
PAIR_KEYS = ['dt_us', 'cpu_gpu_us', 'prot_gpu_ro_ns', 'stg_pool_ns', 'stg_in_ns', 'acopy_wait_us', 'acopy_gpu_waits',
             'ac_kept_inl_ns', 'ac_moved_ns', 'pb_wait_gpu_us']
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
blockmean = []  # (arm_text, {key: mean over the window of this block})
for a, F in blocks:
    rs = [rows[F + 1 + p] for p in range(10, 89) if F + 1 + p in rows and 'dt_us' in rows[F + 1 + p]]
    if len(rs) < 79:
        continue  # an incomplete block (the tail of the run) - out of every mean, as the scorer drops it
    acc.setdefault(a, []).extend(rs)
    blockmean.append((a, {k: sum(r.get(k, 0) for r in rs) / len(rs) for k in PAIR_KEYS}))
if not blocks:
    # A single-arm run (ack129: no schedule, no GateArm line): every row from n = 2100 on (the scene is entered; the
    # form of design129 s.2.3 for runs without blocks). NOT the window of item 55(b) - a row of the whole run.
    acc['all(n>=2100)'] = [r for n, r in sorted(rows.items()) if n >= 2100 and 'dt_us' in r]
print('log', LOG, 'blocks', len(blocks), 'complete', len(blockmean))
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
arms = sorted(acc)
if len(arms) == 2:
    # pairs (2k, 2k+1) of the ABBA order: every pair holds one block of each arm
    diffs = {k: [] for k in PAIR_KEYS}
    for k2 in range(0, len(blockmean) - 1, 2):
        (a0, m0), (a1, m1) = blockmean[k2], blockmean[k2 + 1]
        if a0 == a1:
            continue
        lo, hi = (m0, m1) if a0 == arms[0] else (m1, m0)
        for k in PAIR_KEYS:
            diffs[k].append(hi[k] - lo[k])
    print('pairs', len(diffs['dt_us']), '(arm %s - arm %s)' % (arms[1], arms[0]))
    for k in PAIR_KEYS:
        d = diffs[k]
        if len(d) > 1:
            mu = sum(d) / len(d)
            se = math.sqrt(sum((x - mu) ** 2 for x in d) / (len(d) - 1) / len(d))
            print('  d %-18s %12.2f +- %8.2f (2SE)' % (k, mu, 2 * se))
for a in arms:
    m = mean[a]
    print('derived', a)
    def per(num, den, scale=1.0):
        return (m.get(num, 0) / scale) / m[den] if m.get(den) else float('nan')
    print('  ac_kept_inl_ns/1000 per ac_kept_inl_n   %8.3f us' % per('ac_kept_inl_ns', 'ac_kept_inl_n', 1000))
    print('  ac_moved_ns/1000 per ac_moved_n         %8.3f us' % per('ac_moved_ns', 'ac_moved_n', 1000))
    print('  ac_moved_pages per ac_moved_n           %8.3f' % per('ac_moved_pages', 'ac_moved_n'))
    print('  prot_gpu_ro_ns/1000 per prot_gpu_ro_n   %8.3f us' % per('prot_gpu_ro_ns', 'prot_gpu_ro_n', 1000))
    print('  prot_gpu_ro_pages per prot_gpu_ro_n     %8.3f' % per('prot_gpu_ro_pages', 'prot_gpu_ro_n'))
    print('  stg_pool_ns/1000 per stg_pool_n         %8.3f us' % per('stg_pool_ns', 'stg_pool_n', 1000))
    print('  stg_pool_b/1024 per stg_pool_n          %8.1f KiB' % per('stg_pool_b', 'stg_pool_n', 1024))
    print('  stg_in_ns/1000 per stg_in_n             %8.3f us' % per('stg_in_ns', 'stg_in_n', 1000))
    print('  stg_in_b/1024 per stg_in_n              %8.1f KiB' % per('stg_in_b', 'stg_in_n', 1024))
    print('  ac_kept_inl_n per stg_in_n              %8.3f' % per('ac_kept_inl_n', 'stg_in_n'))
    print('  stg_in_n per ac_n                       %8.3f' % per('stg_in_n', 'ac_n'))
    print('  ac_job_wait_ns/1000 per ac_chunks       %8.3f us' % per('ac_job_wait_ns', 'ac_chunks', 1000))
    kept = m.get('ac_kept_ns', 0)
    if kept:
        print('  ac_kept_inl_ns / ac_kept_ns             %8.4f' % (m.get('ac_kept_inl_ns', 0) / kept))
