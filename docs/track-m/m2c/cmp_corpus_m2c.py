"""M2c (HPP-840, task member (1)): own comparison of the T1 corpus run C:/kyty/m657/m2c/corpus (corpus_m2a.py run; base =
FS15 bfac84be copy, the rest = main 666a434a build emu_main.exe). Reads <config>/<row>/rc.txt and out.spv only (not the
M2a table). Members: every process rc 0; u and z = base byte for byte on every row; per config the rows / programs
(hash16 of t1_base.tsv) that differ from base; all = union of the six themes; MS1 = union of T234, T233, T306, T032, T203.
Prints the table and ALL OK / FAIL."""
import csv
import hashlib
import os

OUT = 'C:/kyty/m657/m2c/corpus'
T1 = 'C:/kyty/s288/s7/t1_base.tsv'
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']
CONFIGS = ['base', 'u', 'z'] + ['t' + t for t in THEMES] + ['all']


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest() if os.path.exists(path) else None


rows = sorted(os.listdir(OUT + '/base'))
hash_of = {}
with open(T1, encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t')
    head = next(rd)
    for rec in rd:
        d = dict(zip(head, rec))
        rid = d.get('rid') or d.get('row') or rec[0]
        hash_of[rid] = d.get('hash16') or d.get('hash') or ''
ok = True
bad_rc = []
shas = {}
for c in CONFIGS:
    for r in rows:
        rc = open('%s/%s/%s/rc.txt' % (OUT, c, r)).read().strip() if os.path.exists('%s/%s/%s/rc.txt' % (OUT, c, r)) else 'missing'
        if rc != '0':
            bad_rc.append((c, r, rc))
        shas[c, r] = sha('%s/%s/%s/out.spv' % (OUT, c, r))
print('rows', len(rows), 'configs', len(CONFIGS), 'rc != 0:', len(bad_rc), bad_rc[:5])
ok &= not bad_rc and len(rows) == 269
diff = {}
for c in CONFIGS[1:]:
    d = [r for r in rows if shas[c, r] != shas['base', r] or shas[c, r] is None]
    diff[c] = d
    progs = sorted({hash_of.get(r, '?' + r) for r in d})
    print('%-6s rows_diff %3d programs %3d %s' % (c, len(d), len(progs), ' '.join(progs[:4]) if len(progs) <= 4 else ''))
ok &= not diff['u'] and not diff['z']
union_all = set()
for t in THEMES:
    union_all |= set(diff['t' + t])
union_ms1 = set()
for t in THEMES:
    if t != 'T256':
        union_ms1 |= set(diff['t' + t])
print('all == union of six themes:', set(diff['all']) == union_all, '| MS1 union rows', len(union_ms1),
      'programs', len({hash_of.get(r, r) for r in union_ms1}))
ok &= set(diff['all']) == union_all
print('ALL OK' if ok else 'FAIL')
