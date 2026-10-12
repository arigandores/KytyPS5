"""M1a (HPP-835, ROADMAP p.752(g)(1)): coverage and consistency check of the upstream inventory.

Run from anywhere:  python docs/track-m/m1/check_m1a.py   (repo = two levels above this file's folder)
Checks: (1) every non-merge commit of 6a2987a7..dad900c6 has exactly one row in upstream.tsv and nothing else is there -> prints
'<n> of 564'; (2) class in {А, Б, В, В′, Г, Д}; one class per theme; (3) upstream_detail.tsv has the same sha/theme/class rows;
(4) every basis 'b3dc9c67:<path>:<N>' in upstream_detail.tsv: line N == anchor and line N+1 == anchor_plus1 (whitespace-stripped);
(5) every theme id appears in upstream.md. Prints ALL OK when all hold."""
import csv, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
GIT = 'git'
for g in ('C:/Program Files/Git/cmd/git.exe',):
    if os.path.exists(g):
        GIT = g
BASE, UP, OURS = '6a2987a7', 'dad900c6', 'b3dc9c67'
CLASSES = {'А', 'Б', 'В', 'В′', 'Г', 'Д'}
ok = True
def git(*a):
    return subprocess.run([GIT, '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')
def fail(msg):
    global ok
    ok = False
    print('FAIL', msg)
up = [l[:9] for l in git('rev-list', '--no-merges', '--reverse', '--abbrev=9', '--abbrev-commit', BASE + '..' + UP).split()]
rows = list(csv.reader(open(os.path.join(HERE, 'upstream.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
hdr, body = rows[0], rows[1:]
if hdr != ['sha', 'тема', 'класс', 'файлы']:
    fail('header ' + repr(hdr))
seen = {}
for r in body:
    if len(r) != 4:
        fail('row width ' + repr(r[:2]))
        continue
    k = r[0][:9]
    if k in seen:
        fail('duplicate ' + k)
    seen[k] = r
cover = sum(1 for h in up if h in seen)
extra = [k for k in seen if k not in set(up)]
print('%d of %d' % (cover, len(up)))
if cover != len(up) or len(up) != 564:
    fail('coverage %d of %d (expected 564)' % (cover, len(up)))
if extra:
    fail('rows not in range: ' + ' '.join(extra[:5]))
th = {}
for k, r in seen.items():
    if r[2] not in CLASSES:
        fail('class %s %s' % (k, r[2]))
    th.setdefault(r[1], set()).add(r[2])
for t, s in th.items():
    if len(s) != 1:
        fail('theme %s classes %s' % (t, s))
det = list(csv.DictReader(open(os.path.join(HERE, 'upstream_detail.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
if len(det) != len(body):
    fail('detail rows %d != %d' % (len(det), len(body)))
cache = {}
LINE = re.compile(r'b3dc9c67:([^:\s]+):(\d+)')
n_anchor = 0
for d in det:
    k = d['sha'][:9]
    if k not in seen or seen[k][1] != d['тема'] or seen[k][2] != d['класс']:
        fail('detail mismatch ' + k)
    m = LINE.search(d['основание'])
    if not m:
        continue
    p, n = m.group(1), int(m.group(2))
    if p not in cache:
        cache[p] = git('show', OURS + ':' + p).split('\n')
    L = cache[p]
    a = L[n - 1].strip() if 0 < n <= len(L) else None
    b = L[n].strip() if n < len(L) else None
    if a != d['якорь'].strip() or b != d['якорь_плюс1'].strip():
        fail('anchor %s %s:%d' % (k, p, n))
    n_anchor += 1
print('anchors checked', n_anchor)
md = open(os.path.join(HERE, 'upstream.md'), encoding='utf-8').read()
miss = [t for t in th if ('| ' + t + ' |') not in md]
if miss:
    fail('themes missing in upstream.md: ' + ' '.join(miss[:5]))
print('themes', len(th))
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
