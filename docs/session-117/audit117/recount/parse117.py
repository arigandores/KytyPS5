"""Independent recount parser for spn117 (audit lens RECOUNT). Written from scratch; does not import spn117.py.
Reads the emulator log in binary and dumps per-stream per-frame dicts to a pickle for the analysis script."""
import pickle, re, sys, collections

LOG = 'C:/kyty/s117/log_spn117.txt'
STDOUT = 'C:/kyty/s117/stdout_spn117.txt'
OUT = 'C:/kyty/s117/audit117/recount/parsed117.pkl'

PFX = {b'FrameTrace: ': 'main', b'FrameTrace-draw: ': 'draw', b'FrameTrace-x: ': 'x'}
MARKERS = [b'GpuHangAbort', b'GpuWaitSlow', b'GpuMarkerHung', b'GpuCheckpointHang', b'ErrorDeviceLost',
           b'std::terminate', b'abort()', b'fatal', b'Fatal', b'FATAL', b'Unhandled exception', b'--- Error ---',
           b'--- Fatal Error ---', b'AsyncPipelines: skipped draw', b'DeviceLost', b'device lost']
OTHER = [b'GateArm:', b'Gate:', b'Spine', b'GpuClockPin', b'PrepareMainPresent', b'GpuWall', b'BufferGc:',
         b'GpuMarker', b'CsStall:', b'PriorityStall:', b'GpuIdlePrio:', b'Vulkan: GPU checkpoints',
         b'AsyncPipelines', b'RecordThread']


def parse_kv(rest):
    d = {}
    for tok in rest.split():
        if b'=' not in tok:
            continue
        k, v = tok.split(b'=', 1)
        try:
            d[k.decode()] = int(v)
        except ValueError:
            try:
                d[k.decode()] = float(v)
            except ValueError:
                d[k.decode()] = v.decode(errors='replace')
    return d


def main():
    streams = {'main': collections.defaultdict(list), 'draw': collections.defaultdict(list),
               'x': collections.defaultdict(list)}
    order = {'main': [], 'draw': [], 'x': []}
    markers = []
    other = []
    nlines = 0
    with open(LOG, 'rb') as f:
        for i, ln in enumerate(f):
            nlines += 1
            hit = False
            for p, s in PFX.items():
                if ln.startswith(p):
                    d = parse_kv(ln[len(p):])
                    n = d.get('n')
                    streams[s][n].append(d)
                    order[s].append(n)
                    hit = True
                    break
            if hit:
                continue
            for m in MARKERS:
                if m in ln:
                    markers.append((i, m.decode(), ln[:300]))
                    break
            for o in OTHER:
                if o in ln:
                    other.append((i, o.decode(), ln[:400]))
                    break
    smark = []
    with open(STDOUT, 'rb') as f:
        for i, ln in enumerate(f):
            for m in MARKERS:
                if m in ln:
                    smark.append((i, m.decode(), ln[:300]))
                    break
    pickle.dump({'streams': {k: dict(v) for k, v in streams.items()}, 'order': order, 'markers': markers,
                 'other': other, 'stdout_markers': smark, 'nlines': nlines}, open(OUT, 'wb'))
    print('lines', nlines, 'main', len(order['main']), 'draw', len(order['draw']), 'x', len(order['x']))
    print('markers in log', len(markers), 'in stdout', len(smark))


if __name__ == '__main__':
    main()
