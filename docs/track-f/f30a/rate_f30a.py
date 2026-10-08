# F30a (HPP-706, item 640(d)(1)(iv)): per level, from the knob-1 entries of the course line (dac02fb9 .. FS10) in
# sweep_f30a.jsonl - the skip share rts_skip / rts_n (what value 1 skips; the expected share of capture self-checks
# rts_chk_b / rts_n at value 2, same predicates and record rule), the per-frame rates of rts_n, rts_skip and rts_xa_reg (a
# Rel_skip register group moved: the draws value 3 compares and value 2 refuses - the predictor of a live value-3 control)
# and the PB refusals.  Entries with >= 1000 frames only; copies of one log (same binary, level, frames) once.
# usage: python rate_f30a.py <sweep.jsonl> <out.txt>
import json, re, sys
from collections import defaultdict

COURSE = {'abfded5e': 'FS10', '3861eeea': 'FS9', 'b3cee576': 'S18', '2c9b69b9': 'FS8', '8df61c00': 'FS7', '9325446c': 'FS6',
          'adb0c82f': 'S12', '631ff987': 'FS5', '31cbfee8': 'FS4', '540c035a': 'FS3', '4aa62e95': 'P23', 'bbad499c': 'FS2',
          'dac02fb9': 'dac02fb9'}
o = open(sys.argv[2], 'w', encoding='utf-8', newline='\n')
agg = defaultdict(lambda: defaultdict(int))
seen = set()
for line in open(sys.argv[1], encoding='utf-8'):
    r = json.loads(line)
    sha = r.get('binary_sha256') or ''
    b = COURSE.get(sha[:8]) if isinstance(sha, str) else None
    if b is None:
        continue
    vals = set(re.search(r'mode (\d)', l).group(1) for _, l in r.get('lines', {}).get('RTS', []) if 'mode ' in l)
    if vals != {'1'}:
        continue
    for e in r['entries'][1:]:
        if e['frames'] < 1000:
            continue
        lv = (re.search(r'Level has started: (\S*)', e['line']) or [None, '?'])[1] or '(empty)'
        key = (b, lv, e['frames'])
        if key in seen:
            continue
        seen.add(key)
        a = agg[lv]
        a['entries'] += 1
        a['frames'] += e['frames']
        for k, v in e['rts'].items():
            a[k] += v
print('level | entries | frames | rts_n/frame | skip share | xa_reg/frame | xa_rec/frame | xb_*/frame | rec_x/frame | ovf', file=o)
for lv in sorted(agg, key=lambda x: -agg[x]['frames']):
    a = agg[lv]
    f = a['frames']
    xb = sum(a[k] for k in a if k.startswith('rts_xb_'))
    print('%s | %d | %d | %.1f | %.4f | %.2f | %.2f | %.2f | %.2f | %d' % (
        lv, a['entries'], f, a['rts_n'] / f, a['rts_skip'] / a['rts_n'] if a['rts_n'] else float('nan'),
        a['rts_xa_reg'] / f, a['rts_xa_rec'] / f, xb / f, a['rts_rec_x'] / f, a['rts_ovf']), file=o)
o.close()
print(open(sys.argv[2], encoding='utf-8').read())
