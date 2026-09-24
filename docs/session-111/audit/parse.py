# Independent parser (audit 111). Does not import session scorers.
# Streams a Kyty log in binary mode; keeps selected fields of FrameTrace / -draw / -x rows keyed by n,
# plus GateArm lines, Gate: lines and marker line counts.
import re, sys, pickle
MAIN = ('dt_us', 'draws', 'dispatches', 'cpu_gpu_us', 'gpu_busy_us', 'arm', 'blk', 'cpu_main_us', 'cpu_present_us',
        'semwait_us', 'semwaits', 'faults', 'fault_us', 'submits', 'lat_us', 'cpu_proc_us', 'gpu_n')
DRAW = ('spin_gpu_us', 'rec_n', 'da_walk_us', 'da_take_us', 'da_queue_us', 'da_hit', 'da_miss', 'da_late', 'da_walks',
        'da_stale', 'sync_ups', 'img_up', 'img_up_kb', 'prot_us', 'rp_begin', 'srt_miss', 'da_work_us', 'spin_us',
        'faults_main', 'fault_main_us', 'da_draws', 'da_ready', 'smemo_hit')
X = ('cspfree_hit', 'cspfree_look', 'cspfree_bad', 'cspf_have', 'cspf_new', 'cs_sync_new', 'cs_sync_wait',
     'cs_sync_new_us', 'cs_sync_wait_us', 'da_wjobs', 'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'sync_up_kb',
     'rt_kpx', 'rt_att', 'vp_kpx', 'da_qcall', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn',
     'da_slot_bad', 'da_q_free', 'da_chk_ok', 'da_chk_bad',
     'pl_cont_n', 'pl_cont_wall_ns', 'pl_cont_cpu_ns', 'pl_cont_h0_n', 'pl_cont_h0_ns', 'pl_cont_h1_n', 'pl_cont_h1_ns',
     'pl_cont_h2_n', 'pl_cont_h2_ns', 'pl_cont_h3_n', 'pl_cont_h3_ns', 'pl_wq_hold_ns', 'pl_wq_hold_n', 'pl_wp_hold_ns',
     'pl_wp_hold_n', 'bl_trip', 'da_unchecked')
MARKERS = (b'DaSlotVerify: MISMATCH', b'DrawAheadVerify: MISMATCH', b'CspFreeVerify: MISMATCH', b'AsyncPipelines: skipped draw',
           b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---', b'GpuHangAbort',
           b'GpuWaitSlow', b'GpuClockPin:', b'CsStall:', b'ErrorDeviceLost', b'GpuCheckpoint', b'BvhLoopCapTrip:')
tok = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')


def parse(path):
    rows = {}; gates = []; gatelines = []; counts = {m: 0 for m in MARKERS}; examples = {}
    with open(path, 'rb') as f:
        for raw in f:
            if raw.startswith(b'GateArm:'):
                m = re.match(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+)', raw)
                gates.append((int(m.group(3)), int(m.group(1)), int(m.group(4)), raw.rstrip()))
                continue
            if raw.startswith(b'Gate: '):
                gatelines.append(raw.rstrip()); continue
            if raw.startswith(b'FrameTrace'):
                if raw.startswith(b'FrameTrace: '): want = MAIN
                elif raw.startswith(b'FrameTrace-draw: '): want = DRAW
                elif raw.startswith(b'FrameTrace-x: '): want = X
                else: continue
                d = dict(tok.findall(raw))
                if b'n' not in d: continue
                n = int(d[b'n']); r = rows.setdefault(n, {})
                for k in want:
                    v = d.get(k.encode())
                    if v is not None: r[k] = int(v)
                continue
            for m in MARKERS:
                if m in raw:
                    counts[m] += 1
                    examples.setdefault(m, raw[:300])
    return dict(rows=rows, gates=gates, gatelines=gatelines, counts=counts, examples=examples)


if __name__ == '__main__':
    tag, path = sys.argv[1], sys.argv[2]
    P = parse(path)
    pickle.dump(P, open('C:/kyty/s111/audit111/%s.pkl' % tag, 'wb'))
    print(tag, 'rows', len(P['rows']), 'gatearm', len(P['gates']), 'gate lines', len(P['gatelines']))
    for m, c in P['counts'].items():
        if c: print('  ', m.decode(), c, P['examples'][m][:200])
