"""Audit 108: independent parser of a KytyPS5 FrameTrace log -> compact per-frame JSON (no session scorer imported)."""
import json
import re
import sys

FIELDS_MAIN = ('dt_us', 'draws', 'dispatches', 'cpu_gpu_us', 'gpu_busy_us', 'arm', 'blk')
FIELDS_DRAW = ('spin_gpu_us', 'rec_n', 'da_walk_us', 'da_queue_us', 'da_take_us', 'da_miss', 'da_hit',
               'da_late', 'da_walks')
FIELDS_X = ('cspfam_look', 'cspfam_skip', 'cs_sync_new', 'cs_sync_wait', 'cspf_have', 'cspf_new',
            'rt_att', 'rt_kpx', 'da_wjobs', 'da_wskip', 'da_wdrop', 'da_qcall')
TOK = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
MARKERS = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
           b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:', b'AsyncPipelines: skipped draw',
           b'GpuHangAbort', b'GpuClockPin:', b'RecordThread: started', b'GPU checkpoints', b'Recording:',
           b'AsyncCompute:', b'PipelinePrecache:', b'Level has started', b'CspFam', b'cspfam')


def main(log, out):
    frames = {}
    gate = []
    marks = {m.decode(): 0 for m in MARKERS}
    samples = {m.decode(): [] for m in MARKERS}
    lineno = 0
    first_ft_line = None
    with open(log, 'rb') as f:
        for raw in f:
            lineno += 1
            for m in MARKERS:
                if m in raw:
                    k = m.decode()
                    marks[k] += 1
                    if len(samples[k]) < 3:
                        samples[k].append((lineno, raw[:220].decode('utf-8', 'replace').rstrip()))
            if raw.startswith(b'GateArm:'):
                d = {k.decode(): int(v) for k, v in TOK.findall(raw)}
                d['text'] = raw.split(b'text=', 1)[1].strip().decode() if b'text=' in raw else None
                d['line'] = lineno
                gate.append(d)
                continue
            if not raw.startswith(b'FrameTrace'):
                continue
            if raw.startswith(b'FrameTrace: '):
                kind, fl = 'm', FIELDS_MAIN
            elif raw.startswith(b'FrameTrace-draw: '):
                kind, fl = 'd', FIELDS_DRAW
            elif raw.startswith(b'FrameTrace-x: '):
                kind, fl = 'x', FIELDS_X
            else:
                continue
            toks = dict(TOK.findall(raw))
            if b'n' not in toks:
                continue
            n = int(toks[b'n'])
            if first_ft_line is None:
                first_ft_line = lineno
            r = frames.setdefault(n, {})
            r['_' + kind] = r.get('_' + kind, 0) + 1
            for k in fl:
                kb = k.encode()
                if kb in toks:
                    r[k] = int(toks[kb])
    json.dump({'frames': frames, 'gate': gate, 'marks': marks, 'samples': samples, 'lines': lineno},
              open(out, 'w'))
    print(log, 'lines', lineno, 'frames', len(frames), 'gate', len(gate))
    for k, v in marks.items():
        if v:
            print('  mark', k, v, samples[k][:2])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
