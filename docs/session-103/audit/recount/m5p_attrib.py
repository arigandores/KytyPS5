# Attribution check: does the item-sum increase of V2p show up in the whole-capture total?
# EventGPUDuration is known to be non-additive per event (zeros); if V2p only moved duration from
# neighbouring non-item events into item events, total_all would not grow by the item delta.
import json, statistics
R = 'C:/kyty/s103/m5p/real/'
b = json.load(open(R + 'bench_m5p103.json'))
plan = json.load(open(R + 'plan_m5p103.json'))
idx = {e: k for k, e in enumerate(b['events'])}
ITEMS = ['S%d' % i for i in range(1, 11)]
item_idx = {it: [idx[e] for e in plan['items'][it]['events']] for it in ITEMS}
main = [f for f in b['fetches'] if f['phase'] == 'main']
by = {(f['arm'], f['round']): f for f in main}
rounds = sorted(set(f['round'] for f in main))
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)
X8 = ['S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S9', 'S10']
for arm in ['A', 'V1', 'V2p']:
    d_items10 = []; d_items8 = []; d_total = []; d_rest = []
    for r in rounds:
        fa = by[('A', r)]; fx = by[(arm, r)]
        s10a = sum(sum(fa['d'][k] for k in item_idx[it]) for it in ITEMS)
        s10x = sum(sum(fx['d'][k] for k in item_idx[it]) for it in ITEMS)
        s8a = sum(sum(fa['d'][k] for k in item_idx[it]) for it in X8)
        s8x = sum(sum(fx['d'][k] for k in item_idx[it]) for it in X8)
        d_items10.append(s10x - s10a); d_items8.append(s8x - s8a)
        d_total.append(fx['total_all_us'] - fa['total_all_us'])
        d_rest.append((fx['total_all_us'] - s10x) - (fa['total_all_us'] - s10a))
    P(arm, 'vs A, median over rounds: d_items10 %.1f us, d_items8 %.1f us, d_total_all %.1f us, d_non_item %.1f us' % (
        statistics.median(d_items10), statistics.median(d_items8), statistics.median(d_total), statistics.median(d_rest)))
for arm in ['B', 'A', 'V1', 'V2p']:
    P(arm, 'median total_all_us %.1f' % statistics.median(by[(arm, r)]['total_all_us'] for r in rounds),
      'median n_results', statistics.median(by[(arm, r)]['n_results'] for r in rounds))
# whole-capture ratio V2p/A (reported only)
P('median_r total_all[V2p]/total_all[A] = %.4f' % statistics.median(by[('V2p', r)]['total_all_us'] / by[('A', r)]['total_all_us'] for r in rounds))
open('C:/kyty/s103/audit103/recount/m5p_attrib.out.txt', 'w').write('\n'.join(out) + '\n')
