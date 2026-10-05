"""Track F link FS8c (HPP-573): the reference map of the seal docs/track-f/fs8c.md section 0 (general rule 24(1)): every link
<commit>:<path>:<line> - the line starts with the anchor (after leading blanks) and the next line starts with the +1 control.  Reads git
objects only (git show).  The first output line names the script with its sha256; the last line is ALL OK.  ASCII only."""
import hashlib, os, subprocess, sys

REPO = 'C:/kyty/KytyPS5'
C = 'b151e541'
REFS = [
    ('item 471 (g)(3) FS8c', C, 'docs/ROADMAP.md', 22623, '(3) **FS8c (Harness Engineer, \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c',
     '(4) **FS8d (\u043b\u0438\u0434; `blocked` \u043d\u0430 FS8c):**'),
    ('item 471 head', C, 'docs/ROADMAP.md', 22615, '471. **\u0417\u0432\u0435\u043d\u043e F14h \u0442\u0440\u0435\u043a\u0430 F',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 \u043f\u043e \u0447\u043b\u0435\u043d\u0430\u043c \u043f. 409(\u0433).**'),
    ('item 530 head', C, 'docs/ROADMAP.md', 23048, '530. **\u0417\u0432\u0435\u043d\u043e FS8b \u0442\u0440\u0435\u043a\u0430 F',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 \u043f\u043e \u0447\u043b\u0435\u043d\u0430\u043c \u043f. 471(\u0433)(2)'),
    ('item 530 (g) N1-N4', C, 'docs/ROADMAP.md', 23052, '(\u0433) **\u0414\u043e\u043b\u0433\u0438 (\u043f\u0440\u0430\u0432\u0438\u043b\u043e \u043f. 324(\u0438)(5)).** **\u041d1**',
     '(\u0434) **\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0439 \u043d\u0430 \u0432\u0440\u0435\u043c\u044f FS8c.**'),
    ('item 530 (d) installed', C, 'docs/ROADMAP.md', 23053, '(\u0434) **\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0439 \u043d\u0430 \u0432\u0440\u0435\u043c\u044f FS8c.**',
     '(\u0435) **\u0417\u0432\u0435\u043d\u044c\u044f:** `HPP-572` FS8b'),
    ('item 518 (v)(4) N4', C, 'docs/ROADMAP.md', 22955, '(4) **\u041d4 \u2014 \u0447\u043b\u0435\u043d \u043f\u0435\u0447\u0430\u0442\u0438 FS7c',
     '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f:** FS7b `HPP-566`'),
    ('item 295 (b) W form', C, 'docs/ROADMAP.md', 15337, '(\u0431) **RC1 \u2014 \u0440\u0435\u0448\u0435\u043d\u0438\u0435 (A).**',
     '\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440\u043e\u0432 \u043d\u0435 \u0441\u043a\u0440\u044b\u0432\u0430\u043b\u0438\u0441\u044c'),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite refs_fs8c.py sha256 %s' % sha(os.path.abspath(__file__)))
ok = True
cache = {}
for name, c, path, line, anchor, plus1 in REFS:
    key = (c, path)
    if key not in cache:
        cache[key] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % key], capture_output=True).stdout.decode('utf-8').split('\n')
    t = cache[key]
    a = t[line - 1].lstrip() if len(t) >= line else ''
    b = t[line].lstrip() if len(t) > line else ''
    good = a.startswith(anchor) and b.startswith(plus1)
    ok &= good
    print('%s %s %s:%s:%d' % ('OK' if good else 'BAD', name, c, path, line))
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'SOME BAD')
