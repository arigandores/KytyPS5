# Recount of vdg112 (audit 112): GO terms, per-arm levels, transitions.
import sys, statistics as st
sys.path.insert(0, 'C:/kyty/s112/audit112')
from abba112 import *

P = load('vdg112'); rows = P['rows']
print('rows', len(rows), 'gatearm', len(P['gates']), 'gate lines', len(P['gatelines']))
print('markers', {k.decode(): v for k, v in P['counts'].items() if v})
texts = {}
for g in P['gates']:
    texts.setdefault(g[1], set()).add((g[3], g[4], g[5], g[6]))
print('arm texts', texts)
print('Gate lines sample', P['gatelines'][:6])
smc = [l for l in P['gatelines'] if b'smemocheck' in l]
print('smemocheck gate lines', smc[:3], len(smc))
xrows = [n for n in rows if 'da_chk_ok' in rows[n]]
tot = {}
for k in ('da_slot_bad', 'da_chk_ok', 'da_chk_bad', 'da_q_free', 'da_q_noguard', 'da_guard_busy', 'da_guard_yield',
          'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_qcall', 'cspfree_hit', 'cspfree_bad', 'da_hit'):
    tot[k] = sum(rows[n].get(k, 0) for n in rows)
print('x rows', len(xrows))
for k, v in tot.items():
    print('  total %-14s %d' % (k, v))
# rows missing any of the 13 fields
F13 = ('da_slot_bad', 'da_chk_ok', 'da_chk_bad', 'da_q_free', 'da_q_noguard', 'da_guard_busy', 'da_guard_yield',
       'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_qcall', 'cspfree_hit', 'cspfree_bad')
print('x rows missing a field', sum(1 for n in xrows if any(k not in rows[n] for k in F13)))
# per arm (by the row's own arm/blk and in-block position 10..89)
byblk = {}
for n in sorted(rows):
    r = rows[n]
    if 'blk' in r and 'arm' in r:
        byblk.setdefault(r['blk'], []).append(n)
per = {0: [], 1: []}
for b, ns in byblk.items():
    arm = rows[ns[0]]['arm']
    if any(rows[n]['arm'] != arm for n in ns):
        print('mixed arm in block', b)
    for n in ns[10:90]:
        per[arm].append(n)
for a in (0, 1):
    ns = per[a]
    hit = sum(rows[n].get('da_hit', 0) for n in ns)
    chk = sum(rows[n].get('da_chk_ok', 0) + rows[n].get('da_chk_bad', 0) for n in ns)
    print('arm %d main rows %d  checks/hits %.6f  median q_free %.1f  median q_noguard %.1f  sum q_free %d  sum q_noguard %d  med qcall %.1f  sum yield %d  sum guard_busy %d' % (
        a, len(ns), chk / hit, st.median(rows[n]['da_q_free'] for n in ns), st.median(rows[n]['da_q_noguard'] for n in ns),
        sum(rows[n]['da_q_free'] for n in ns), sum(rows[n]['da_q_noguard'] for n in ns),
        st.median(rows[n]['da_qcall'] for n in ns), sum(rows[n]['da_guard_yield'] for n in ns),
        sum(rows[n]['da_guard_busy'] for n in ns)))
# transitions: rows 0..9 of blocks where the arm changes: any bad?
trans_bad = 0; trans_rows = 0; trans_chk = 0; trans_hit = 0
for b, ns in byblk.items():
    for n in ns[:10]:
        trans_rows += 1
        trans_bad += rows[n].get('da_chk_bad', 0) + rows[n].get('da_slot_bad', 0)
        trans_chk += rows[n].get('da_chk_ok', 0); trans_hit += rows[n].get('da_hit', 0)
print('transition rows (0..9)', trans_rows, 'bad', trans_bad, 'checks/hits %.6f' % (trans_chk / max(1, trans_hit)))
# overall checks/hits over all rows
print('all rows checks/hits %.6f' % ((tot['da_chk_ok'] + tot['da_chk_bad']) / tot['da_hit']))
# number of arm switches actually executed
sw = sum(1 for i in range(1, len(P['gates'])) if P['gates'][i][1] != P['gates'][i - 1][1])
print('arm switches', sw)
# rows with both q_free and q_noguard > 0 (straddle rows)
both = [n for n in rows if rows[n].get('da_q_free', 0) > 0 and rows[n].get('da_q_noguard', 0) > 0]
print('rows with both q_free and q_noguard > 0:', len(both))
print('frame range', min(rows), max(rows))
print('dt level per arm (main rows) med', {a: st.median(rows[n]['dt_us'] for n in per[a]) for a in (0, 1)})
