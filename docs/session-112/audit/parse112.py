# Independent parser (audit 112). Does not import any session scorer.
# Streams a Kyty log in binary mode; keeps selected fields of FrameTrace / -draw / -x rows keyed by n,
# GateArm lines, Gate: lines and marker line counts (with first example).
import re, sys, pickle, os
MAIN = ('dt_us', 'draws', 'dispatches', 'cpu_gpu_us', 'gpu_busy_us', 'arm', 'blk', 'cpu_main_us', 'cpu_present_us',
        'semwait_us', 'semwaits', 'faults', 'fault_us', 'submits', 'lat_us', 'cpu_proc_us', 'gpu_n')
DRAW = ('spin_gpu_us', 'spin_us', 'rec_n', 'da_walk_us', 'da_take_us', 'da_queue_us', 'da_hit', 'da_miss', 'da_late',
        'da_walks', 'da_stale', 'da_q', 'da_nohint', 'da_present', 'da_busy', 'da_done', 'da_work_us', 'sync_ups',
        'img_up', 'img_up_kb', 'prot_us', 'rp_begin', 'srt_miss', 'faults_main', 'fault_main_us', 'da_draws',
        'da_ready', 'smemo_hit', 'bda_scan', 'bda_skip', 'bda_n', 'bda_us', 'da_move', 'da_probe', 'da_runs',
        'cpu_record_us', 'da_words', 'da_refresh', 'da_noplan', 'da_fail', 'memo_hit', 'memo_miss')
X = ('cspfree_hit', 'cspfree_look', 'cspfree_bad', 'cspf_have', 'cspf_new', 'cs_sync_new', 'cs_sync_wait',
     'cs_sync_new_us', 'cs_sync_wait_us', 'da_wjobs', 'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'sync_up_kb',
     'rt_kpx', 'rt_att', 'vp_kpx', 'da_qcall', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn',
     'da_slot_bad', 'da_q_free', 'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield',
     'pl_cont_n', 'pl_cont_wall_ns', 'pl_wq_hold_ns', 'pl_wq_hold_n', 'pl_wp_hold_ns', 'pl_wp_hold_n', 'bl_trip',
     'da_unchecked', 'da_req', 'da_fan', 'da_unused', 'da_probe_q', 'bda_hit', 'da_direct', 'pmemo_hit', 'pmemo_miss',
     'gclk_n', 'gclk_pin', 'gclk_adv', 'gclk_sadv', 'gw_idle_ns', 'cspfam_look', 'cspfam_skip')
MARKERS = (b'DaSlotVerify: MISMATCH', b'DrawAheadVerify: MISMATCH', b'CspFreeVerify: MISMATCH',
           b'AsyncPipelines: skipped draw', b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---',
           b'--- abort() ---', b'GpuHangAbort', b'GpuWaitSlow', b'GpuClockPin:', b'CsStall:', b'ErrorDeviceLost',
           b'GpuCheckpoint', b'BvhLoopCapTrip:', b'Unhandled exception', b'BdaRegime', b'CtxCheck: MISMATCH')
tok = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')


def parse(path):
    rows = {}; gates = []; gatelines = []; counts = {m: 0 for m in MARKERS}; examples = {}
    with open(path, 'rb') as f:
        for raw in f:
            c = raw[:1]
            if c == b'G':
                if raw.startswith(b'GateArm:'):
                    m = re.match(rb'GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)',
                                 raw.rstrip())
                    gates.append((int(m.group(3)), int(m.group(1)), int(m.group(4)), int(m.group(2)), int(m.group(5)),
                                  int(m.group(6)), m.group(7)))
                    continue
                if raw.startswith(b'Gate: '):
                    gatelines.append(raw.rstrip()); continue
            if c == b'F' and raw.startswith(b'FrameTrace'):
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
    for arg in sys.argv[1:]:
        tag, path = arg.split('=', 1)
        out = 'C:/kyty/s112/audit112/pkl/%s.pkl' % tag
        if os.path.exists(out):
            print(tag, 'exists'); continue
        P = parse(path)
        os.makedirs('C:/kyty/s112/audit112/pkl', exist_ok=True)
        pickle.dump(P, open(out, 'wb'))
        print(tag, 'rows', len(P['rows']), 'gatearm', len(P['gates']), 'gate lines', len(P['gatelines']), flush=True)
        for m, cnt in P['counts'].items():
            if cnt: print('  ', m.decode(), cnt, P['examples'][m][:160])
