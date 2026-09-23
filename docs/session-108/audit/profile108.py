"""Audit 108: within-block profile of dt by frame index, by arm and by position in the ABBA quartet
(pos 0 = arm0 second-of-run, pos 1 = arm1 first-of-run, pos 2 = arm1 second-of-run, pos 3 = arm0 first-of-run)."""
import json
import math
import statistics as st
import sys

TAG = sys.argv[1] if len(sys.argv) > 1 else 'fam108'
P = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s108/audit108/p_%s.json' % TAG
d = json.load(open(P))
fr = {int(k): v for k, v in d['frames'].items()}
arm_of = {g['block']: g['arm'] for g in d['gate']}
START, PER = 1800, 90
quartets = []
for b in range(0, max(arm_of) + 1, 4):
    blocks = list(range(b, b + 4))
    if not all(k in arm_of for k in blocks):
        continue
    ok = all(all(n in fr and 'dt_us' in fr[n] for n in range(START + 1 + PER * k, START + 1 + PER * (k + 1)))
             for k in blocks)
    if ok and START + 1 + PER * b + 60 >= 2100:
        quartets.append(b)
print(TAG, 'complete quartets', len(quartets))


def prof(k, key='dt_us'):
    return [fr[START + 1 + PER * k + i][key] for i in range(PER)]


pos_prof = {p: [prof(b + p) for b in quartets] for p in range(4)}
# mean by segments
segs = ((0, 10), (10, 30), (30, 60), (60, 89), (89, 90))
print('mean dt by quartet position and within-block segment (us):')
print('  pos arm  ' + '  '.join('[%2d:%2d]' % s for s in segs) + '   [60:89]-[0:90]')
for p in range(4):
    arm = (0, 1, 1, 0)[p]
    row = []
    for lo, hi in segs:
        row.append(st.fmean(st.fmean(x[lo:hi]) for x in pos_prof[p]))
    print('  %d   %d   ' % (p, arm) + '  '.join('%8.0f' % v for v in row))
# deltas by orientation and segment
print('paired delta arm1-arm0 by orientation and segment:')
for name, (p1, p0) in (('AB (pos1-pos0)', (1, 0)), ('BA (pos2-pos3)', (2, 3))):
    for lo, hi in segs + ((60, 89),):
        v = [st.fmean(a[lo:hi]) - st.fmean(b[lo:hi]) for a, b in zip(pos_prof[p1], pos_prof[p0])]
        se = st.stdev(v) / math.sqrt(len(v))
        print('  %-15s [%2d:%2d] mean %8.1f  2SE %7.1f' % (name, lo, hi, st.fmean(v), 2 * se))
# arm0-arm0 and arm1-arm1 contrasts: second-of-run minus first-of-run within the same arm, kept window
for lo, hi in ((0, 89), (0, 90)):
    for name, (p1, p0) in (('AB (pos1-pos0)', (1, 0)), ('BA (pos2-pos3)', (2, 3))):
        v = [st.fmean(a[lo:hi]) - st.fmean(b[lo:hi]) for a, b in zip(pos_prof[p1], pos_prof[p0])]
        se = st.stdev(v) / math.sqrt(len(v))
        print('  full %-15s [%2d:%2d] mean %8.1f  2SE %7.1f' % (name, lo, hi, st.fmean(v), 2 * se))
