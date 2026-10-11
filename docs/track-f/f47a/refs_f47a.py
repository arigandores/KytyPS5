# F47a (HPP-802): map of the report links <commit>:<path>:<line>. check: every link's line contains its anchor and the
# next line starts with its +1 control (git show); neg: every link with the anchor mutated must fail; text: every link
# written in the report is in the table and nothing else.
# Usage: python refs_f47a.py check | neg | text <report.md>
import re, subprocess, sys

ROOT = 'C:/kyty/KytyPS5'
# commit, path, line, anchor (substring of the line), +1 control (prefix of the next line; '' = empty line)
REFS = [
    ('7df0fe5f', 'docs/ROADMAP.md', 24649, '   (ж) **Б34 — следующая строка очереди K4, офлайн в форме п. 673(ж)(7) с RC14',
     '   (з) **Реестр §118** — этим коммитом: Ф26 (поправка к §117)'),
    ('7df0fe5f', 'docs/ROADMAP.md', 24280, '      (7) **Б34** — снимок RenderDoc по кадру от старта уровня',
     '   (з) **Звенья этого пункта**'),
    ('7df0fe5f', 'docs/track-f/f32b-review.md', 120, '**RC14 (строка 185, Б34).**',
     'вход, созданный эмулятором (устаревшая текстура или це'),
    ('7df0fe5f', 'docs/track-f/f32a.md', 157, '### 3.6 Б34 — заставка уровня на двух бинарях', ''),
    ('7df0fe5f', 'docs/track-f/register.md', 1656, '| Б34 (поправка к §104) | K4 / картинка |', ''),
]
cache = {}


def lines(commit, path):
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        cache[key] = out.decode('utf-8').split('\n')
    return cache[key]


def ok_link(commit, path, line, anchor, plus1):
    L = lines(commit, path)
    if line < 1 or line > len(L) - 1:
        return False
    nxt = L[line]
    return anchor in L[line - 1] and (nxt.startswith(plus1) if plus1 else nxt.strip() == '')


def main():
    mode = sys.argv[1]
    if mode == 'check':
        bad = 0
        for r in REFS:
            good = ok_link(*r)
            bad += not good
            print('%s %s:%s:%d' % ('ok ' if good else 'BAD', r[0], r[1], r[2]))
        print('links %d bad %d' % (len(REFS), bad))
        print('ALL OK' if bad == 0 else 'FAIL')
        return 0 if bad == 0 else 1
    if mode == 'neg':
        caught = 0
        for c, p, n, a, p1 in REFS:
            caught += (not ok_link(c, p, n, a + ' MUTANT', p1)) and (not ok_link(c, p, n + 1, a, p1))
        print('neg %d of %d caught (anchor mutant and line +1)' % (caught, len(REFS)))
        print('ALL OK' if caught == len(REFS) else 'FAIL')
        return 0 if caught == len(REFS) else 1
    if mode == 'text':
        text = open(sys.argv[2], encoding='utf-8').read()
        found = set(re.findall(r'`([0-9a-f]{8}):([^`:]+):(\d+)`', text))
        table = {(c, p, str(n)) for c, p, n, _, _ in REFS}
        extra, missing = found - table, table - found
        print('text links %d table %d extra %s missing %s' % (len(found), len(table), sorted(extra), sorted(missing)))
        print('ALL OK' if not extra and not missing else 'FAIL')
        return 0 if not extra and not missing else 1
    return 2


sys.exit(main())
