# Independent parser (auditor, session 104). Does not import any session scorer.
# Usage: python parse_log.py <tag> [logpath]
import sys, re, pickle, os

tag = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s104/log_%s.txt' % tag
OUT = 'C:/kyty/s104/audit104/recount/%s.pkl' % tag

EXACT = {'dt_us', 'draws', 'dispatches', 'cpu_gpu_us', 'gpu_busy_us', 'arm', 'blk',
         'spin_gpu_us', 'rec_n', 'rt_att', 'rt_kpx', 'bda_n', 'n', 'lat_us', 'rt_w', 'rt_h'}
PREFIX = ('da_', 'bf_', 'gm_', 'mw_', 'a_', 'pl_', 'mh_', 'sh_')
tok = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')

rows = {}      # n -> {kind: dict}
dup = []       # (kind, n) duplicates
order = []
gate = []
markers = {}
marker_ctx = []
last_n = None
MARK = [b'GpuClockPin:', b'RecordThread: started', b'GPU checkpoints', b'GpuHangAbort',
        b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
        b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:', b'AsyncPipelines: skipped draw',
        b'ShadowResolve: worker', b'Recording:', b'ShaderSeed:', b'PipelinePrecache', b'diagnostic checkpoints',
        b'AsyncPipelines: flip']

def keep(k):
    return k in EXACT or k.startswith(PREFIX)

with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace'):
            if line.startswith(b'FrameTrace: '):
                kind = 'main'; body = line[12:]
            elif line.startswith(b'FrameTrace-draw: '):
                kind = 'draw'; body = line[17:]
            elif line.startswith(b'FrameTrace-x: '):
                kind = 'x'; body = line[14:]
            else:
                continue
            d = {}
            for k, v in tok.findall(body):
                ks = k.decode()
                if keep(ks):
                    if ks in d:
                        dup.append(('field', kind, ks))
                    d[ks] = int(v)
            if 'n' not in d:
                continue
            n = d['n']
            r = rows.setdefault(n, {})
            if kind in r:
                dup.append((kind, n))
            r[kind] = d
            if kind == 'main':
                order.append(n)
                last_n = n
            continue
        if line.startswith(b'GateArm:'):
            gate.append(line.rstrip(b'\r\n').decode('latin1'))
            continue
        for m in MARK:
            if m in line:
                markers[m.decode()] = markers.get(m.decode(), 0) + 1
                if len(marker_ctx) < 400:
                    marker_ctx.append((m.decode(), last_n, line[:300].decode('latin1').rstrip()))

pickle.dump({'rows': rows, 'dup': dup[:1000], 'ndup': len(dup), 'order': order, 'gate': gate,
             'markers': markers, 'marker_ctx': marker_ctx}, open(OUT, 'wb'))
print(tag, 'rows', len(rows), 'main', len(order), 'dup', len(dup), 'gate', len(gate))
print('markers', markers)
