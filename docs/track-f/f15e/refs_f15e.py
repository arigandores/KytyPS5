"""F15e (HPP-516): the reference map of the seal docs/track-f/f15e.md (general rule 24(1)): every reference <commit>:<path>:<line> with
its anchor (the start of the line) and the +1 control (the start of the next line), checked by git show.  Prints ASCII; ends with ALL OK.
usage: python refs_f15e.py   (run in C:/kyty/KytyPS5)"""
import subprocess, sys

REFS = [
    ('412(g)(5)', '107fc085', 'docs/ROADMAP.md', 21903, '   (5) **Тег под замком — «нет вреда»** (F15e;',
     '   `31cbfee8` — sha256 до и после; манифест sha256'),
    ('412(d)', '107fc085', 'docs/ROADMAP.md', 21913, '   (д) **Звенья F15** (стадия review лида',
     '   F14e `HPP-505`, затем это звено)'),
    ('445(v)', '107fc085', 'docs/ROADMAP.md', 22429, '   (в) **Долги (правило п. 324(и)(5)):** Н1',
     '   (г) **Поправка к заданию F15e (`HPP-516`):**'),
    ('445(g)', '107fc085', 'docs/ROADMAP.md', 22430, '   (г) **Поправка к заданию F15e (`HPP-516`):**',
     '   (д) **Звенья:** F15d `HPP-515`'),
    ('437', '107fc085', 'docs/ROADMAP.md', 22346, '437. **Звено S12d трека S (`HPP-497`, лид):',
     '   (а) **Приёмка строкой.** S12a'),
    ('438', '107fc085', 'docs/ROADMAP.md', 22357, '438. **Звено S12d трека S (`HPP-497`, лид): факт п. 437(в)',
     '   (а) **Установка по форме п. 394(д)(4)**'),
]
cache = {}
bad = 0
for name, c, path, line, anchor, plus1 in REFS:
    key = (c, path)
    if key not in cache:
        cache[key] = subprocess.run(['git', 'show', '%s:%s' % (c, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    t = cache[key]
    ok_a = len(t) >= line and t[line - 1].startswith(anchor)
    ok_p = len(t) > line and t[line].startswith(plus1)
    if not (ok_a and ok_p):
        bad += 1
    print('ref %s %s:%s:%d anchor %s +1 %s' % (name, c, path, line, 'OK' if ok_a else 'BAD', 'OK' if ok_p else 'BAD'))
print('refs %d bad %d' % (len(REFS), bad))
if bad:
    sys.exit(1)
print('ALL OK')
