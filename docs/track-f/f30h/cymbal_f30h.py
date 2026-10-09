# F30h (HPP-718, Probe Designer): where in a log rts_xb_ser / rts_xb_meta fire at value 1 (candidate gamma).  Read only.
# Usage: python cymbal_f30h.py <log>
import re
import sys

KV = re.compile(rb'(rts_[a-z0-9_]+)=(\d+)')
NRE = re.compile(rb'FrameTrace-x: n=(\d+)')
path = sys.argv[1]
frames = []
marks = []
version = None
modes = []
with open(path, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace-x:') and b'rts_' in line:
            m = NRE.match(line)
            d = {k.decode(): int(v) for k, v in KV.findall(line)}
            d['_n'] = int(m.group(1)) if m else -1
            frames.append(d)
        elif b'Level has started' in line or b'Level has finished' in line:
            marks.append((len(frames), line.strip()[:120].decode('utf-8', 'replace')))
        elif line.startswith(b'RtSkip: mode'):
            modes.append(line.strip().decode())
        elif version is None and b'version: Fork build' in line:
            version = line.strip()[:120].decode('utf-8', 'replace')
print('version', version)
print('modes', modes)
print('frames', len(frames))
for i, m in marks:
    print('mark at frame idx', i, m)
g = lambda d, k: d.get(k, 0)
S = {}
for d in frames:
    for k, v in d.items():
        if k.startswith('rts_'):
            S[k] = S.get(k, 0) + v
print('sums', {k: S[k] for k in sorted(S) if k.startswith('rts_x') or k in ('rts_skip', 'rts_n', 'rts_pa', 'rts_pb')})
fs = [d for d in frames if g(d, 'rts_xb_ser') > 0 or g(d, 'rts_xb_meta') > 0]
print('frames with ser|meta > 0:', len(fs))
# runs of frames
runs = []
prev = None
for d in fs:
    if prev is not None and d['_n'] == prev + 1:
        runs[-1][1] = d['_n']
        runs[-1][2] += g(d, 'rts_xb_ser')
        runs[-1][3] += g(d, 'rts_xb_meta')
    else:
        runs.append([d['_n'], d['_n'], g(d, 'rts_xb_ser'), g(d, 'rts_xb_meta')])
    prev = d['_n']
print('runs (first n, last n, ser, meta):', len(runs))
for r in runs[:40]:
    print('RUN', *r)
hist = {}
for d in fs:
    k = g(d, 'rts_xb_ser')
    hist[k] = hist.get(k, 0) + 1
print('per-frame ser histogram', sorted(hist.items())[:30])
print('ALL OK')
