# F30a (HPP-706, item 640(d)(1)(iii)): BDA mode by level on the course line (dac02fb9 .. FS10) from entries_f30a.tsv.
# Copies of one log in several directories (same binary, level, frames, read-block mean) are counted once.  Only entries
# with >= 3 read blocks (SHORT out) and the knob at 1 (the shipped skip) are counted.
# usage: python sum_f30a.py <entries.tsv> <out.txt>
import csv, sys
from collections import defaultdict

COURSE_ORDER = ['dac02fb9', 'FS2', 'P23', 'FS3', 'FS4', 'FS5', 'S12', 'FS6', 'FS7', 'FS8', 'S18', 'FS9', 'FS10']
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8'), delimiter='\t'))
o = open(sys.argv[2], 'w', encoding='utf-8', newline='\n')
seen = set()
lev = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
dup = 0
for r in rows:
    if r['binary'] not in COURSE_ORDER or r['mode'] == 'SHORT' or r['rtskip_values'] != '1':
        continue
    key = (r['binary'], r['level'], r['frames'], r['mean_read'])
    if key in seen:
        dup += 1
        continue
    seen.add(key)
    lev[r['level']][r['binary']][r['mode']] += 1
print('course-line entries (>= 3 read blocks, knob 1), copies removed:', len(seen), 'copies:', dup, file=o)
tot = defaultdict(int)
for lv in lev:
    for b in lev[lv]:
        for m, n in lev[lv][b].items():
            tot[m] += n
print('modes:', dict(tot), file=o)
print('\nlevel | entries | OLD | NEW | MIXED | binaries (mode:count)', file=o)
for lv in sorted(lev, key=lambda x: (-sum(lev[x][b].get('OLD', 0) for b in lev[x]), x)):
    n = {m: sum(lev[lv][b].get(m, 0) for b in lev[lv]) for m in ('OLD', 'NEW', 'MIXED')}
    bins = ' '.join('%s:%s' % (b, ','.join('%s%d' % (m[0], c) for m, c in sorted(lev[lv][b].items())))
                    for b in COURSE_ORDER if b in lev[lv])
    print('%s | %d | %d | %d | %d | %s' % (lv, sum(n.values()), n['OLD'], n['NEW'], n['MIXED'], bins), file=o)
o.close()
print(open(sys.argv[2], encoding='utf-8').read())
