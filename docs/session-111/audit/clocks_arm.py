# Clocks per ABBA arm (audit 111): maps each GateArm block to wall time via the nearest preceding
# "[tid][HH:MM:SS.fff]" line (process-relative), then assigns nvidia-smi / cpu samples to blocks.
import re, sys, csv, statistics as st, datetime as dt
tag = sys.argv[1] if len(sys.argv) > 1 else 'shp111'
root = 'C:/kyty/s111/'
pat = re.compile(rb'^\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
blocks = []  # (block, arm, t_rel)
last = None
with open(root + 'log_%s.txt' % tag, 'rb') as f:
    for raw in f:
        m = pat.match(raw)
        if m:
            h, mi, s, ms = map(int, m.groups()); last = h * 3600 + mi * 60 + s + ms / 1000
            continue
        if raw.startswith(b'GateArm:'):
            m2 = re.match(rb'GateArm: arm=(\d+) arms=\d+ block=(\d+)', raw)
            blocks.append((int(m2.group(2)), int(m2.group(1)), last))
import json
meta = json.load(open(root + '%s.json' % tag))
launched = dt.datetime.fromisoformat(meta['launched'])
print('blocks', len(blocks), 'first', blocks[0], 'last', blocks[-1], 'launched', launched)
spans = []
for i in range(len(blocks) - 1):
    b, a, t = blocks[i]; t2 = blocks[i + 1][2]
    if b < 4 or t is None: continue
    spans.append((t + 0.3, t2 - 0.3, a))
# gpu
rows = list(csv.reader(open(root + 'gpuclk_%s.csv' % tag)))
hdr = [x.strip() for x in rows[0]]
by = {0: {k: [] for k in hdr[1:]}, 1: {k: [] for k in hdr[1:]}}
for r in rows[1:]:
    ts = dt.datetime.strptime(r[0].strip(), '%Y/%m/%d %H:%M:%S.%f')
    rel = (ts - launched).total_seconds()
    for lo, hi, a in spans:
        if lo <= rel < hi:
            for k, v in zip(hdr[1:], r[1:]):
                by[a][k].append(v.strip())
            break
for k in hdr[1:]:
    out = []
    for a in (0, 1):
        vals = by[a][k]
        if k.startswith('clocks_event'):
            c = {}
            for v in vals: c[v] = c.get(v, 0) + 1
            out.append('arm%d %s' % (a, c))
        else:
            nums = []
            for v in vals:
                try: nums.append(float(v.split()[0]))
                except: pass
            if nums: out.append('arm%d n %d med %.1f mean %.2f' % (a, len(nums), st.median(nums), sum(nums) / len(nums)))
    print('gpu', k, ' | '.join(out))
# cpu
rd = list(csv.DictReader(open(root + 'cpuclk_%s.csv' % tag)))
t0 = float(rd[0]['t_s'])
print('cpu first t_s', rd[0]['t_s'], 'last', rd[-1]['t_s'])
byc = {0: {}, 1: {}}
for r in rd:
    rel = float(r['t_s'])
    for lo, hi, a in spans:
        if lo <= rel < hi:
            for k, v in r.items():
                try: byc[a].setdefault(k, []).append(float(v))
                except: pass
            break
for k in ('perf_all', 'perf_ccd0', 'perf_ccd1', 'mhz_ccd0', 'mhz_ccd1', 'busy_all', 'busy_ccd0', 'busy_ccd1', 'c3_ccd0', 'c3_ccd1',
          'dpc_ms_ccd0', 'dpc_ms_ccd1', 'irq_ms_ccd0', 'irq_ms_ccd1', 'q_len', 'proc_cpu_s'):
    out = []
    for a in (0, 1):
        v = byc[a].get(k, [])
        if v: out.append('arm%d n %d med %.2f mean %.3f' % (a, len(v), st.median(v), sum(v) / len(v)))
    print('cpu', k, ' | '.join(out))
