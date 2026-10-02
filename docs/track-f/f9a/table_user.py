# F9a step 1 (ROADMAP s122 item 344 (v)(1)): table "video time -> present (.idx) -> log line" for the segments of the user
# play recording C:/kyty/play/20261002T221534Z, read from the 1 frame/s and 4 frames/s sheets (sheets1s/, sheets4/).
# Clock: the FrameTrace rows and the .idx records are put on one clock anchored at their ends (the method of sc146.py vcont:
# the last record = the end of the last row; a row ends where the dt_us of the rows after it, summed back, puts it).
# Marker counts: the lines of scan_log.json in [start - 2 s, end + 2 s] of every segment and in +-2 s of its first frame.
# ASCII output only.
import json, bisect, re
P = 'C:/kyty/play/20261002T221534Z/'
S = json.load(open('C:/kyty/f287/f9/scan_log.json'))
idx = []
for line in open(P + 'rec.mp4.idx'):
    a = line.split()
    if len(a) >= 3:
        idx.append((int(a[0]), int(a[1]), float(a[2])))
vf2 = {v: (p, t) for v, p, t in idx}
# FrameTrace rows: line number, n, dt_us
rows = []
want = set(S['frametrace'])
with open(P + 'log.txt', 'rb') as f:
    ln = 0
    for line in f:
        ln += 1
        if ln in want:
            m = re.search(rb'n=(\d+) dt_us=(\d+)', line)
            rows.append((ln, int(m.group(1)), int(m.group(2))))
end = idx[-1][2]
ends = [0.0] * len(rows)
t = end
for k in range(len(rows) - 1, -1, -1):
    ends[k] = t
    t -= rows[k][2] / 1e6
def row_at(ts):
    k = bisect.bisect_left(ends, ts)
    if k >= len(ends):
        k = len(ends) - 1
    if k > 0 and abs(ends[k - 1] - ts) < abs(ends[k] - ts):
        k -= 1
    return k
def line_at(ts):
    k = row_at(ts)
    return rows[k][0], rows[k][1], ends[k] - ts
hits = S['hits']
def count(t0, t1):
    a = line_at(t0)[0]; b = line_at(t1)[0]
    out = {}
    for key, v in hits.items():
        out[key] = sum(1 for n, _ in v if a <= n <= b)
    return a, b, out
# segments: (kind, label, first video s, last video s) from the sheets
SEG = [
    ('approach', 'walk on the path, pond comes into view', 34.0, 35.75),
    ('GLITCH', 'G1 pond far, camera turning to the pond', 36.0, 38.0),
    ('norm', 'N1 Astro at the pond edge', 39.25, 39.75),
    ('GLITCH', 'G2 pond seen from the bank', 40.0, 41.25),
    ('norm', 'N2 in water, camera above', 41.5, 42.0),
    ('GLITCH', 'G3 flash, then in water, side camera', 42.25, 49.0),
    ('norm', 'N3 in water, camera above, steps in water', 49.25, 52.5),
    ('GLITCH', 'G4 in water, side camera', 52.75, 55.25),
    ('norm', 'N4 in water, the same side camera as G4', 55.5, 57.75),
    ('norm', 'N5 standing in the stream, camera along the stream', 60.0, 95.0),
    ('GLITCH', 'G5 approach from the path, pond far', 194.5, 195.75),
    ('GLITCH', 'G6 flash, entering the pond', 197.25, 199.25),
    ('norm', 'N6 in water with flamingos, camera above', 199.5, 200.75),
    ('GLITCH', 'G7 in water, camera swings', 201.0, 201.75),
    ('norm', 'N7 in water with flamingos, steps', 202.0, 208.0),
    ('GLITCH', 'G8 camera swings to the tree side', 208.25, 212.5),
    ('norm', 'N8 in water, camera above', 212.75, 215.25),
    ('GLITCH', 'G9 long: standing in water at the tree side, low camera', 215.5, 266.25),
    ('norm', 'N9 leaves the pond', 266.5, 268.0),
    ('norm', 'N10 walking in the stream', 380.0, 385.0),
    ('GLITCH', 'G10 pond from the far bank (to the end of the recording)', 389.25, 407.5),
]
print('video_s  frame  present  host_s  log_line(FrameTrace)  n  | segment')
out = []
for kind, label, a, b in SEG:
    fa = int(round(a * 60)); fb = int(round(b * 60))
    pa, ta = vf2[fa]; pb, tb = vf2[min(fb, len(idx) - 1)]
    la, na, da = line_at(ta); lb, nb, db = line_at(tb)
    c0, c1, cnt = count(ta - 2.0, tb + 2.0)
    s0, s1, cs = count(ta - 2.0, ta + 2.0)
    rec = dict(kind=kind, label=label, v0=a, v1=b, f0=fa, f1=fb, p0=pa, p1=pb, t0=ta, t1=tb, line0=la, n0=na, line1=lb, n1=nb,
               d0_ms=round(da * 1000, 1), win_lines=[c0, c1], win=cnt, start_lines=[s0, s1], start=cs)
    out.append(rec)
    print('%7.2f-%7.2f f%5d-%5d p%5d-%5d t%7.2f-%7.2f L%7d-%7d n%5d-%5d %s %s' % (a, b, fa, fb, pa, pb, ta, tb, la, lb, na, nb, kind, label))
    print('    [start-2s, end+2s] lines %d-%d: %s' % (c0, c1, ' '.join('%s=%d' % (k.split(':')[0].split(' ')[0] if k != '[Vulkan]' else 'Vulkan', v) for k, v in cnt.items())))
    print('    start +-2s       lines %d-%d: %s' % (s0, s1, ' '.join('%s=%d' % (k.split(':')[0].split(' ')[0] if k != '[Vulkan]' else 'Vulkan', v) for k, v in cs.items())))
json.dump(out, open('C:/kyty/f287/f9/table_user.json', 'w'), indent=1)
lv = S['lvl'][-1][0]
k = bisect.bisect_left([r[0] for r in rows], lv)
print('level started line', lv, 'next FrameTrace n', rows[k][1], 'end', round(ends[k], 3), 'nearest idx present',
      min(idx, key=lambda r: abs(r[2] - ends[k]))[:2])
print('rows', len(rows), 'idx', len(idx), 'clock span rows', round(ends[-1] - ends[0] + rows[0][2] / 1e6, 2), 'idx span', round(idx[-1][2] - idx[0][2], 2))
print('all hits per key (whole log):', ' '.join('%s=%d' % (k, len(v)) for k, v in hits.items()))
for k2 in ('AsyncPipelines: skipped draw', 'PriorityStall'):
    for n, s in hits[k2]:
        j = bisect.bisect_left([r[0] for r in rows], n)
        j = min(j, len(rows) - 1)
        tt = ends[j]
        v = min(idx, key=lambda r: abs(r[2] - tt))
        print('  %s line %d -> video %.2f s (frame %d, present %d): %s' % (k2.split(':')[0], n, v[0] / 60.0, v[0], v[1], s[:110]))
