# M1b (HPP-836): independent coverage check of M1a inventory (own code, not check_m1a.py).
# Usage: python cov_m1b.py  (cwd = KytyPS5 repo root)
import subprocess, sys, csv, collections
BASE = '6a2987a7b29bbfefd7b102470e61a50a610c3e4a'
TIP = 'dad900c61d6c7ff8aefc9e666ca7c3de4bbf4176'
D = 'docs/track-m/m1/'
def git(*a):
    return subprocess.run(['git', *a], capture_output=True, check=True).stdout.decode('utf-8', 'replace')
ok = True
def bad(msg):
    global ok
    ok = False
    print('FAIL', msg)
up = git('rev-list', '--no-merges', f'{BASE}..{TIP}').split()
merges = git('rev-list', '--merges', f'{BASE}..{TIP}').split()
print('upstream no-merges', len(up), 'merges', len(merges), merges)
def rows(path):
    with open(D + path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
t = rows('upstream.tsv')
d = rows('upstream_detail.tsv')
print('rows tsv', len(t), 'detail', len(d))
# resolve abbreviated sha by unique prefix
def resolve(p):
    m = [s for s in up if s.startswith(p)]
    return m[0] if len(m) == 1 else None
seen = collections.Counter()
for r in t:
    s = resolve(r['sha'])
    if s is None:
        bad('tsv sha unresolved/ambiguous ' + r['sha'])
    else:
        seen[s] += 1
dup = [s for s, c in seen.items() if c > 1]
missing = [s for s in up if s not in seen]
print('resolved unique', len(seen), 'dup', len(dup), 'missing', len(missing))
if dup or missing or len(seen) != len(up):
    bad('coverage')
for s in missing[:20]:
    print('  missing', s)
# detail consistency
tm = {r['sha']: (r['тема'], r['класс']) for r in t}
dm = {r['sha']: (r['тема'], r['класс']) for r in d}
if set(tm) != set(dm):
    bad('tsv/detail sha sets differ')
diff = [s for s in tm if tm[s] != dm.get(s)]
print('tsv vs detail theme/class mismatch', len(diff))
if diff:
    bad('tsv/detail mismatch')
cls_by_theme = collections.defaultdict(set)
for r in t:
    cls_by_theme[r['тема']].add(r['класс'])
multi = [k for k, v in cls_by_theme.items() if len(v) > 1]
print('themes', len(cls_by_theme), 'multi-class', len(multi))
if multi:
    bad('multi-class themes ' + ','.join(multi))
cc = collections.Counter(r['класс'] for r in t)
tc = collections.Counter(next(iter(v)) for v in cls_by_theme.values())
print('commits by class', dict(sorted(cc.items())))
print('themes by class', dict(sorted(tc.items())))
# files column vs git (own diff-tree)
fdiff = 0
for r in t:
    s = resolve(r['sha'])
    if not s:
        continue
    g = set(x for x in git('diff-tree', '--no-commit-id', '--name-only', '-r', s).split('\n') if x)
    f = set(x for x in r['файлы'].split(';') if x and x != '-')
    if g != f:
        fdiff += 1
        if fdiff <= 10:
            print('  files differ', r['sha'], 'git-only', sorted(g - f)[:5], 'tsv-only', sorted(f - g)[:5])
print('files column differs from git diff-tree:', fdiff)
# merge commits: evil-merge content (combined diff non-empty)
for m in merges:
    cc_out = git('diff-tree', '--cc', '--name-only', m).split('\n')[1:]
    cc_out = [x for x in cc_out if x]
    print('merge', m[:9], 'combined-diff files', len(cc_out), cc_out[:10])
    if cc_out:
        bad('merge with own content not covered by any non-merge row: ' + m[:9])
print('ALL OK' if ok else 'FAILED')
