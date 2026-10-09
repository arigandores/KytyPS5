# F31a: per-queue AgcDriverSubmitAcb sizes (dwords) per guest frame from a log.
# Lines (src/libs/agc.cpp AgcDriverSubmitAcb): "\t queue  = 0x..", "\t packet = 0x..", "\t acb   = 0x..", "\t size  = 0x..", "\t flags = 0x.."
# Frame boundary: "FrameTrace: n=<k>" (the submits before it belong to frame k, approx: log lines are async-mixed).
import sys, re, json, collections
path = sys.argv[1]
out = sys.argv[2]
rq = re.compile(rb'^\t queue  = 0x([0-9a-f]+)')
ra = re.compile(rb'^\t acb   = 0x([0-9a-f]+)')
rs = re.compile(rb'^\t size  = 0x([0-9a-f]+)')
rf = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+).*? draws=(\d+).*? dispatches=(\d+)')
rlvl = re.compile(rb'Level has started: (\S+)')
q = None; a = None
cur = collections.defaultdict(lambda: [0, 0, 0])  # queue -> [n_submits, sum_dw, max_dw]
frames = []
bases = collections.defaultdict(collections.Counter)  # queue -> acb addr counter
maxdw = collections.defaultdict(int)
lvl_line = None
n = 0
with open(path, 'rb') as f:
    for line in f:
        n += 1
        m = rq.match(line)
        if m:
            q = int(m.group(1), 16); a = None
            continue
        if q is not None:
            m = ra.match(line)
            if m:
                a = int(m.group(1), 16); continue
            m = rs.match(line)
            if m and a is not None:
                s = int(m.group(1), 16)
                c = cur[q]; c[0] += 1; c[1] += s; c[2] = max(c[2], s)
                bases[q][a] += 1
                maxdw[q] = max(maxdw[q], s)
                q = None; a = None
                continue
        if line.startswith(b'FrameTrace: '):
            m = rf.match(line)
            if m:
                frames.append({'n': int(m.group(1)), 'dt': int(m.group(2)), 'draws': int(m.group(3)), 'disp': int(m.group(4)), 'line': n,
                               'q': {('%x' % k): v[:] for k, v in cur.items()}})
                cur.clear()
            continue
        if lvl_line is None:
            m = rlvl.search(line)
            if m and m.group(1) != b'':
                lvl_line = n
res = {'path': path, 'lines': n, 'level_line': lvl_line, 'frames': len(frames),
       'maxdw': {('%x' % k): v for k, v in maxdw.items()},
       'bases': {('%x' % k): {('%x' % b): c for b, c in v.most_common(12)} for k, v in bases.items()},
       'nbases': {('%x' % k): len(v) for k, v in bases.items()}}
with open(out, 'w', encoding='utf-8') as o:
    o.write(json.dumps(res) + '\n')
    for fr in frames:
        o.write(json.dumps(fr) + '\n')
print(json.dumps(res, indent=1)[:4000])
