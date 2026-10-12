"""M1a2 (HPP-837): check of the members of ROADMAP p.756(b)(1)-(6) on the edited inventory docs/track-m/m1/.
 (1) the 75 themes of m1b/rc1_themes.tsv: class != Г; T256 = А; the other 74 = А-резерв; each of the 48 FATAL/RT themes has
     >= 1 row in m1a2/signatures.tsv and a non-'-' column сигнатура in upstream_detail.tsv; every place of signatures.tsv
     and of upstream_parts.tsv / upstream_merges.tsv: line N == якорь, N+1 == якорь_плюс1 on b3dc9c67; T226 and T314 carry
     the whole-game LDS evidence;
 (2) T021 = В; T240 = Б and T185 = Б with доп_тема T313:А / T314:А-резерв on their commit; upstream_parts.tsv has the four
     part rows with these classes;
 (3) upstream_merges.tsv has 8cecaf4e with theme T053, class = class of T053, files = its combined diff; T053 rows carry the
     merge line; the files column of upstream.tsv = both sides of git diff-tree -r -M for all 564 commits;
 (4) column свидетели: non-'-' for T124, T116, T151, T017 and equal to the witness.tsv grouping for every theme;
 (5) T163, T239, T155, T178: class Д and строка_M1a2 with 'кадра ≥ 1 с' and 'п. 613(г)';
 (6) T021, T240, T069, T255, T007: строка_M1a2 with 'превращающая В в В′ или Б' (T240: in upstream_parts.tsv too);
 (7) upstream.md: rows '| T313 |', '| T314 |' and section '## 14.'; counts by class printed.
Read-only; exit 3 lock / 4 STOP. Usage: python check_m1a2.py -> ALL OK."""
import collections, csv, io, os, re, subprocess, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
HERE = os.path.dirname(os.path.abspath(__file__))
M1 = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(M1, '..', '..', '..'))
GIT = 'C:/Program Files/Git/cmd/git.exe' if os.path.exists('C:/Program Files/Git/cmd/git.exe') else 'git'
ok = True


def fail(msg):
    global ok
    ok = False
    print('FAIL', msg)


def git(*a):
    return subprocess.run([GIT, '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')


def tsv(path):
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


cache = {}


def anchor(place, a, b, what):
    m = re.fullmatch(r'b3dc9c67:([^:]+):(\d+)', place)
    if not m:
        fail('place form %s %s' % (what, place))
        return
    p, n = m.group(1), int(m.group(2))
    if p not in cache:
        cache[p] = git('show', 'b3dc9c67:' + p).split('\n')
    L = cache[p]
    if not (0 < n < len(L)) or L[n - 1].strip() != a.strip() or L[n].strip() != b.strip():
        fail('anchor %s %s' % (what, place))


up = tsv(os.path.join(M1, 'upstream.tsv'))
det = tsv(os.path.join(M1, 'upstream_detail.tsv'))
parts = tsv(os.path.join(M1, 'upstream_parts.tsv'))
merges = tsv(os.path.join(M1, 'upstream_merges.tsv'))
sig = tsv(os.path.join(HERE, 'signatures.tsv'))
wit = tsv(os.path.join(HERE, 'witness.tsv'))
rc1 = {r['тема']: r['вид'] for r in tsv(os.path.join(M1, 'm1b', 'rc1_themes.tsv'))}
cls = {}
for r in up:
    cls.setdefault(r['тема'], set()).add(r['класс'])
cls = {t: next(iter(v)) for t, v in cls.items()}
by_theme = collections.defaultdict(list)
for d in det:
    by_theme[d['тема']].append(d)
# (1)
n1 = collections.Counter()
for t, kind in rc1.items():
    want = 'А' if t == 'T256' else 'А-резерв'
    if cls.get(t) != want:
        fail('(1) class %s %s != %s' % (t, cls.get(t), want))
    n1[cls.get(t)] += 1
fr = [t for t, k in rc1.items() if k in ('FATAL', 'RT')]
sig_t = collections.Counter(r['тема'] for r in sig)
for t in fr:
    if sig_t[t] == 0:
        fail('(1) no signatures.tsv row ' + t)
    if any(d['сигнатура'] in ('', '-') for d in by_theme[t]):
        fail('(1) empty column сигнатура ' + t)
for r in sig:
    anchor(r['место'], r['якорь'], r['якорь_плюс1'], 'sig ' + r['тема'])
for t in ('T226',):
    if not all('190 CS-программ' in d['строка_M1a2'] for d in by_theme[t]):
        fail('(1) LDS evidence ' + t)
print('(1) RC1 themes', len(rc1), dict(n1), 'FATAL/RT', len(fr), 'signature rows', len(sig),
      'printed', sum(1 for r in sig if r['сигнатура'] != '-'))
# (2)
if cls.get('T021') != 'В':
    fail('(2) T021 class')
for t, sha, extra in (('T240', '57c97ebd8', 'T313:А'), ('T185', 'e6cb880ad', 'T314:А-резерв')):
    if cls.get(t) != 'Б':
        fail('(2) %s class %s' % (t, cls.get(t)))
    rows = [r for r in up if r['sha'].startswith(sha)]
    if len(rows) != 1 or rows[0]['доп_тема'] != extra:
        fail('(2) доп_тема ' + sha)
others = [r['sha'] for r in up if r['доп_тема'] != '-' and not r['sha'].startswith(('57c97ebd8', 'e6cb880ad'))]
if others:
    fail('(2) unexpected доп_тема ' + ' '.join(others))
pc = {(p['тема'], p['класс']) for p in parts}
for want in (('T240', 'Б'), ('T313', 'А'), ('T185', 'Б'), ('T314', 'А-резерв')):
    if want not in pc:
        fail('(2) part row %s' % (want,))
for p in parts:
    anchor(p['основание'], p['якорь'], p['якорь_плюс1'], 'part ' + p['тема'])
if not any('190 CS-программ' in p['строка_M1a2'] for p in parts if p['тема'] == 'T314'):
    fail('(2)/(1) LDS evidence T314')
print('(2) T021', cls.get('T021'), 'T240', cls.get('T240'), 'T185', cls.get('T185'), 'parts', sorted(pc))
# (3)
cc = [x for x in git('diff-tree', '--cc', '--name-only', '8cecaf4e').split('\n')[1:] if x]
mm = [m for m in merges if '8cecaf4e'.startswith(m['sha'][:8])]
if len(mm) != 1 or mm[0]['тема'] != 'T053' or mm[0]['класс'] != cls.get('T053') or set(mm[0]['файлы'].split(';')) != set(cc):
    fail('(3) merge row')
else:
    anchor(mm[0]['основание'], mm[0]['якорь'], mm[0]['якорь_плюс1'], 'merge')
if not all('8cecaf4e' in d['строка_M1a2'] for d in by_theme['T053']):
    fail('(3) T053 merge line')
nf = 0
for r in up:
    g = set()
    for line in git('diff-tree', '--no-commit-id', '-r', '-M', '--name-status', r['sha']).split('\n'):
        if line:
            g.update(line.split('\t')[1:])
    if g != set(x for x in r['файлы'].split(';') if x and x != '-'):
        nf += 1
        fail('(3) files ' + r['sha'])
print('(3) merge rows', len(merges), 'files column vs -M both sides: differ', nf)
# (4)
wt = collections.defaultdict(set)
for r in wit:
    wt[r['тема']].add(r['ключ'])
for t in ('T124', 'T116', 'T151', 'T017'):
    if not wt[t] or any(d['свидетели'] in ('', '-') for d in by_theme[t]):
        fail('(4) witness ' + t)
for t, ds in by_theme.items():
    for d in ds:
        for k in wt.get(t, ()):
            if '«%s»' % k not in d['свидетели']:
                fail('(4) witness key missing %s %r' % (t, k))
        if t not in wt and t not in ('T124', 'T116', 'T151', 'T017') and d['свидетели'] != '-':
            fail('(4) witness without witness.tsv row ' + t)
print('(4) themes with witnesses', len(wt), 'rows', len(wit))
# (5)
for t in ('T163', 'T239', 'T155', 'T178'):
    if cls.get(t) != 'Д' or not all('кадра ≥ 1 с' in d['строка_M1a2'] and 'п. 613(г)' in d['строка_M1a2'] for d in by_theme[t]):
        fail('(5) ' + t)
# (6)
for t in ('T021', 'T240', 'T069', 'T255', 'T007'):
    if not all('превращающая В в В′ или Б' in d['строка_M1a2'] or 'снимающая или подтверждающая' in d['строка_M1a2']
               for d in by_theme[t]):
        fail('(6) ' + t)
print('(5)-(6) lines checked')
# (7)
md = open(os.path.join(M1, 'upstream.md'), encoding='utf-8').read()
for s in ('| T313 |', '| T314 |', '\n## 14. '):
    if s not in md:
        fail('(7) upstream.md lacks %r' % s)
NL = chr(10)
sec10 = md[md.index(NL + '## 10. '):md.index(NL + '## 11. ')]
n10 = 0
for line in sec10.split(NL):
    m = re.match(r'^\| (T\d{3}) \| [^|]*\| ([^|]+) \|', line)
    if m:
        n10 += 1
        t, c = m.group(1), m.group(2).strip()
        want = cls.get(t) or {p['тема']: p['класс'] for p in parts}.get(t)
        if not (c == want or c.startswith(want + ' (M1a2;')):
            fail('(7) §10 class cell %s %r != %s' % (t, c, want))
print('(7) §10 rows', n10)
cc_cls = collections.Counter(r['класс'] for r in up)
tc = collections.Counter(cls.values())
print('commits by class', dict(sorted(cc_cls.items())), 'sum', sum(cc_cls.values()))
print('themes by class', dict(sorted(tc.items())), 'sum', sum(tc.values()), '+ parts T313 А, T314 А-резерв')
if cc_cls['Г'] != 375 - 110:
    fail('Г commits %d != 265' % cc_cls['Г'])
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
