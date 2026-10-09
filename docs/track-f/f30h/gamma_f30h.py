# F30h (HPP-718, Probe Designer): candidate (gamma) - entries of the F30a sweep (1 078 logs, s127..FS10, knob values as run)
# where PB items 3/4 refuse with PA applied: rts_xb_ser or rts_xb_meta >= 100 per entry.  Read only.
# Usage: python gamma_f30h.py <sweep_f30a.jsonl[.xz]>
import json
import lzma
import re
import sys
from collections import defaultdict

src = sys.argv[1]
op = lzma.open if src.endswith('.xz') else open
TH = 100
n_logs = n_ent = 0
hits = []
per_level = defaultdict(lambda: [0, 0, 0, 0, 0, 0])  # entries, ser, meta, pb, skip, hits
tot = defaultdict(int)
with op(src, 'rt', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        n_logs += 1
        for e in d.get('entries', []):
            r = e.get('rts') or {}
            if not r:
                continue
            n_ent += 1
            m = re.search(r'Level has started: (\S*)', e.get('line', ''))
            lvl = m.group(1) if m else '(pre)'
            ser = r.get('rts_xb_ser', 0)
            meta = r.get('rts_xb_meta', 0)
            for k in ('rts_xb_ser', 'rts_xb_meta', 'rts_pb', 'rts_skip', 'rts_pa', 'rts_n'):
                tot[k] += r.get(k, 0)
            pl = per_level[lvl]
            pl[0] += 1
            pl[1] += ser
            pl[2] += meta
            pl[3] += r.get('rts_pb', 0)
            pl[4] += r.get('rts_skip', 0)
            if ser >= TH or meta >= TH:
                pl[5] += 1
                hits.append((d['path'], lvl, e.get('frames'), ser, meta, r.get('rts_skip', 0), r.get('rts_pb', 0),
                             r.get('rts_xa_reg', 0), e.get('bda_mean')))
print('logs', n_logs, 'entries_with_rts', n_ent)
print('totals', dict(tot))
print('entries with rts_xb_ser or rts_xb_meta >= %d: %d' % (TH, len(hits)))
for h in hits:
    print('HIT', *h)
print('per level (entries, sum ser, sum meta, sum pb, sum skip, hit entries) - levels with ser+meta > 0:')
for lvl, pl in sorted(per_level.items(), key=lambda x: -(x[1][1] + x[1][2])):
    if pl[1] + pl[2] > 0:
        print('LVL', lvl, *pl)
print('levels total', len(per_level))
print('ALL OK')
