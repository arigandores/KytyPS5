# F20a (HPP-551): references of f20a.md (general rule 24(1)): <commit>:<path>:<line> with an anchor and the +1 control.
#   python refs_f20a.py <refs.tsv> <report.md>
# writes <refs.tsv> (commit, path, line, anchor, +1 text) from SPEC after checking every row against
# 'git show <commit>:<path>' (the anchor must stand in the line, the +1 text must start the next line), then checks
# that every 'name.md:<line>' written in the report is a row of the table.  Prints 'refs N of N',
# 'report refs M of M', 'ALL OK'.
import re, subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
DOC = '457655e2'
SPEC = [
    (DOC, 'docs/ROADMAP.md', 22463, '451. **Звено F19b трека F (`HPP-544`, лид; приёмка F19a', '(а) **Приёмка строкой. F19a ✓**'),
    (DOC, 'docs/ROADMAP.md', 22476, '(е) **Звенья (стадия review лида у каждого звена исполнителя):**', '(ж) **Ф24 (новая строка, K4, наблюдение):**'),
    (DOC, 'docs/track-f/register.md', 149, '| Б2 | K3 | дефект (происхождение [U]) | кадр 183–197 мс на n 949–954 Sky Garden', '| Б31 | K3 | дефект |'),
    (DOC, 'docs/track-f/register.md', 151, '| Б32 | K3 (строка лида п. 219(в)) |', '| Б34 |'),
]
tsv, report = sys.argv[1], sys.argv[2]
cache = {}


def lines(commit, path):
    if (commit, path) not in cache:
        o = subprocess.run([GIT, '-C', REPO, 'show', commit + ':' + path], capture_output=True)
        cache[(commit, path)] = o.stdout.decode('utf-8', 'replace').split('\n')
    return cache[(commit, path)]


ok = 0
names = set()
rows = []
for commit, path, line, anchor, plus1 in SPEC:
    L = lines(commit, path)
    a = L[line - 1] if line - 1 < len(L) else ''
    b = L[line] if line < len(L) else ''
    good = anchor in a and b.strip().startswith(plus1)
    ok += good
    if not good:
        print('FAIL %s:%s:%d' % (commit, path, line))
    names.add((path.rsplit('/', 1)[1], line))
    rows.append('\t'.join([commit, path, str(line), anchor, plus1]))
with open(tsv, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(rows) + '\n')
print('refs %d of %d' % (ok, len(SPEC)))
text = open(report, encoding='utf-8').read()
cited = set((m.group(1), int(m.group(2))) for m in re.finditer(r'([A-Za-z0-9_]+\.md):(\d+)', text))
miss = sorted(c for c in cited if c not in names)
for c in miss:
    print('NOT IN TABLE %s:%d' % c)
print('report refs %d of %d' % (len(cited) - len(miss), len(cited)))
good = ok == len(SPEC) and not miss
print('ALL OK' if good else 'FAILED')
sys.exit(0 if good else 1)
