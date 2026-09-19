"""Parent's direct check of admitted endpoints and fixed-population key numbers."""
import json
import math
from pathlib import Path
import statistics as st
import sys

root = Path('C:/kyty/s99')
tag = sys.argv[1]
score = json.loads((root / 'settled_runs' / f'{tag}_score.json').read_text())
assert score['status'] == 'ADMITTED_SETTLED_MEASUREMENT'
fields = set('n arm blk draws dt_us rt_kpx rt_att cpu_gpu_us spin_gpu_us bf_burn_cpu_ns bf_burn_ns'.split())
rows = {}
with (root / f'log_{tag}.txt').open('rb') as source:
    for line in source:
        if not line.startswith((b'FrameTrace:', b'FrameTrace-draw:', b'FrameTrace-x:')):
            continue
        values = {}
        for token in line.split()[1:]:
            if b'=' in token:
                key, value = token.split(b'=', 1)
                key = key.decode()
                if key in fields:
                    values[key] = int(value)
        rows.setdefault(values['n'], {}).update(values)
assert sorted(rows) == list(range(min(rows), max(rows) + 1))
blocks = {}
for first in range(1801, max(rows) + 1, 90):
    complete = range(first, first + 90)
    if first + 60 >= 2100 and all(n in rows for n in complete):
        blocks[(first - 1801) // 90] = list(range(first + 60, first + 89))
chosen = []
for quartet in range(0, max(blocks) + 1, 4):
    if all(block in blocks for block in range(quartet, quartet + 4)):
        chosen.extend(range(quartet, quartet + 4))
groups = [[], []]
net_blocks = []
for block in chosen:
    arm = (0, 1, 1, 0)[block % 4]
    chunk = [rows[n] for n in blocks[block]]
    assert all(row['arm'] == arm and row['blk'] == block for row in chunk)
    groups[arm].extend(chunk)
    if arm:
        net_blocks.append(st.fmean(row['cpu_gpu_us'] - row['spin_gpu_us'] -
                                   row['bf_burn_cpu_ns'] / 1000 for row in chunk) / 1000)
draws = [st.fmean(row['draws'] for row in group) for group in groups]
area = [sum(row['rt_kpx'] for row in group) / sum(row['rt_att'] for row in group) for group in groups]
dt = [st.fmean(row['dt_us'] for row in group) for group in groups]
result = dict(tag=tag, pairs=len(chosen)//2, rows_per_arm=[len(group) for group in groups],
              work_pct=100*(draws[1]/draws[0]-1), area_split_pct=100*(area[1]/area[0]-1),
              dt_relative=abs(dt[1]-dt[0])/dt[0], B_cpu_ms=st.median(net_blocks))
for name in ('work_pct', 'area_split_pct', 'dt_relative'):
    assert math.isclose(result[name], score['metrics'][name], abs_tol=1e-10)
assert result['pairs'] == score['metrics']['pairs']
assert math.isclose(result['B_cpu_ms'], score['endpoints']['B_cpu_ms'], abs_tol=1e-10)
print(json.dumps(result, indent=2))
with (root / 'settled_runs' / f'{tag}_parent_recount.json').open('x') as target:
    json.dump(result, target, indent=2)
