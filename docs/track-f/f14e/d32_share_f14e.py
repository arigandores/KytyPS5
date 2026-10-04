# F14e member (g)(0)(a): for every D32_SFLOAT record of the F14c table (manual compare sites),
# is there a D16_UNORM record of the same capture and module on the same sampler binding?
# Input: docs/track-f/f14c/f14c_table.tsv (KytyPS5 1c40a04a). ASCII output only.
import csv, collections, os, sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('HALT lock'); sys.exit(3)
T = 'C:/kyty/KytyPS5/docs/track-f/f14c/f14c_table.tsv'
rows = list(csv.DictReader(open(T, encoding='utf-8'), delimiter='\t'))
by_smp = collections.defaultdict(lambda: collections.defaultdict(set))
mod_fmt = collections.defaultdict(set)
for r in rows:
    by_smp[(r['capture'], r['module'])][r['smp']].add(r['view_format'])
    mod_fmt[r['module']].add(r['view_format'])
rec = collections.Counter()
alone = []
for r in rows:
    n = int(r['n'])
    rec[r['view_format']] += n
    if r['view_format'] == 'D32_SFLOAT':
        if 'D16_UNORM' in by_smp[(r['capture'], r['module'])][r['smp']]:
            rec['D32_shared_with_D16'] += n
        else:
            alone.append(r)
print('table rows', len(rows))
print('records D16_UNORM', rec['D16_UNORM'], 'D32_SFLOAT', rec['D32_SFLOAT'])
print('D32 records with a D16 record on the same sampler binding (capture, module):', rec['D32_shared_with_D16'])
print('D32 rows without such a D16 row:', len(alone))
sets = collections.Counter(tuple(sorted(v)) for v in mod_fmt.values())
for k, v in sorted(sets.items()):
    print('modules with view formats %s: %d' % ('+'.join(k), v))
ok = rec['D32_shared_with_D16'] == rec['D32_SFLOAT'] and not alone and rec['D16_UNORM'] + rec['D32_SFLOAT'] == 123738
print('ALL OK' if ok else 'MISMATCH')
