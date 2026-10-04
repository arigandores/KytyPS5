# F19a (HPP-543): identities of the sweep records (sweep_new.jsonl.p*) and the cross-check against five_f19a.py.
# Usage: python selfcheck_f19a.py <dir>      (prints 'ALL OK' or the failures)
import glob, json, sys
d = sys.argv[1]
recs = []
for p in sorted(glob.glob(d + '/sweep_new.jsonl.p*')):
    recs += [json.loads(l) for l in open(p, encoding='utf-8') if l.startswith('{')]
bad = []
for r in recs:
    if r.get('missing'):
        bad.append(('missing', r['path']))
        continue
    for k in ('ctl', 'mt', 'win', 'lvl', 'slow'):
        ln = [x[0] for x in r[k]]
        if any(b <= a for a, b in zip(ln, ln[1:])):
            bad.append(('order ' + k, r['path']))
        if any(x[0] > r['lines'] or x[2] > r['ft_n'] or x[3] > r['ft_us'] for x in r[k]):
            bad.append(('range ' + k, r['path']))
    if any(s[5] < 1000000 for s in r['slow']):
        bad.append(('slow dt', r['path']))
    if sum(s[5] for s in r['slow']) > r['ft_us']:
        bad.append(('slow sum', r['path']))
    if len(r['slow']) + r['slow_over'] != r['slow_n']:
        bad.append(('slow count', r['path']))
    if r.get('xz_rc', 0) != 0:
        bad.append(('xz rc', r['path']))
    late = [int(c[4].split('=')[1]) for c in r['mt'] if c[4].startswith('MainTaskLate: us=')]
    if r['mt_over'] == 0 and (max(late) if late else 0) != r['mt_late_max']:
        bad.append(('late max', r['path']))
# cross-check: the values printed by five_f19a.py for the five logs (independent line-by-line reader)
want = {'C:/kyty/s114/log_ctl114a.txt.xz': (781643, 6025, 189464064, 3001715, [(501474, 2972, 3034886)]),
        'C:/kyty/s114/log_ctl114b.txt.xz': (910321, 5913, 187146784, 3000429, []),
        'C:/kyty/s115/log_boot115a.txt.xz': (448461, 1928, 67681786, 10341415, []),
        'C:/kyty/s115/log_boot115c.txt.xz': (445858, 1939, 67715454, 10268377, []),
        'C:/kyty/s122/log_edes122.txt': (848110, 7249, 145412813, 23812688, [(642532, 4945, 23796476)])}
seen = 0
for r in recs:
    w = want.get(r['path'])
    if w:
        seen += 1
        got = (r['lines'], r['ft_n'], r['ft_us'], r['mt_late_max'], [(s[0], s[4], s[5]) for s in r['slow']])
        if got != w:
            bad.append(('five mismatch', r['path'], got))
if seen < 5:
    bad.append(('five logs seen', seen))
print('records', len(recs), 'distinct paths', len(set(r['path'] for r in recs)), 'five cross-checked', seen)
for b in bad:
    print('FAIL', b)
print('ALL OK' if not bad else 'FAILED %d' % len(bad))
