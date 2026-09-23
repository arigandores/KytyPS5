# Recompute session-102 X = median_r S[V2]/S[A] over S2-S7,S9,S10 from the s102 raw bench (for P4').
import json, statistics
b = json.load(open('C:/kyty/s102/m5/real/bench_m5cap102.json'))
p = json.load(open('C:/kyty/s102/m5/real/plan_m5cap102.json'))
idx = {e: k for k, e in enumerate(b['events'])}
items = ['S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S9', 'S10']
ii = [idx[e] for it in items for e in p['items'][it]['events']]
main = [f for f in b['fetches'] if f['phase'] == 'main']
by = {(f['arm'], f['round']): sum(f['d'][k] for k in ii) for f in main}
rounds = sorted(set(f['round'] for f in main))
x = statistics.median(by[('V2', r)] / by[('A', r)] for r in rounds)
print('s102 arms', sorted(set(f['arm'] for f in main)), 'rounds', len(rounds), 'X(8 items) = %.6f' % x)
open('C:/kyty/s103/audit103/recount/x102_recount.out.txt', 'w').write('X102 eight items %.6f rounds %d\n' % (x, len(rounds)))
