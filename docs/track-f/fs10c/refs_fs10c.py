# -*- coding: utf-8 -*-
"""FS10c (HPP-686): the reference map of the seal docs/track-f/fs10c.md section 0 (rule 24(1)): every <commit>:<path>:<line> is checked by
git show - the line starts with its anchor and the next line starts with its +1 anchor.  A negative control (the line moved by one) must
fail.  Port of FS9c refs_fs9c.py.  Prints one line per reference and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_fs10c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
REFS = [
    ('80f59338', R, 23825, '   (е) **Отгрузка FS10 — константы лида.**', '   (ж) **Долги (п. 324(и)).**'),
    ('80f59338', R, 23819, '624. **Звено F25n трека F (`HPP-681`, лид)', '   (а) **Приёмка строкой.** F25k ✓'),
    ('80f59338', R, 23826, '   (ж) **Долги (п. 324(и)).**', '   (з) **Реестр §83**'),
    ('80f59338', R, 23830, '   (л) **Не заявляется:** п. 613(и)', '625. **Факт п. 624(и)'),
    ('80f59338', R, 23834, '   (б) **Н1 — решение лида: ДА, тег `fs10_f1` в FS10c.**', '   (в) **Н2 — не исправлено, читать так:**'),
    ('80f59338', R, 23836, '   (г) **Н3 — не исправлено, читать так**', '   (д) **Звенья.**'),
    ('80f59338', R, 23832, '626. **Звено FS10b трека F (`HPP-685`, Red Team)', '   (а) **Приёмка строкой. FS10b ✓**'),
    ('80f59338', R, 23815, '   (в) **Прямое указание пользователя — постоянное правило харнесса всех треков', '   (г) **Отступление исполнителя**'),
    ('80f59338', R, 23786, '   (г) **Решение 3 — печать 2 до первого `_r1`.**', '   (д) **Долги и прошлые серии.**'),
    ('80f59338', R, 23787, '   (д) **Долги и прошлые серии.**', '   (е) **Звенья.**'),
    ('80f59338', R, 23792, '   (б) **Решение.** Член п. 620(г)(2) для тега формы W', '   (в) **Основание.**'),
    ('7fd1053f', 'docs/track-f/fs10a.md', 34, '- **Бинарь FS10: sha256 `abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe`**',
     '  `C:/kyty/f287/bin/kyty_emulator_abfded5e.exe`'),
    ('e3094279', 'docs/track-f/f25m/go_f25m.sh', 126, '  b36_f1) LV=$POT; PRE=B; UF=""; SD=300; H=150;', '  b36_k01|b36_k03|'),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.split(b'\n')
    return cache[k]


def ok_ref(commit, path, n, a, b):
    L = lines(commit, path)
    return n >= 1 and n < len(L) and L[n - 1].startswith(a.encode('utf-8')) and L[n].startswith(b.encode('utf-8'))


def main():
    bad = 0
    for commit, path, n, a, b in REFS:
        good = ok_ref(commit, path, n, a, b)
        bad += not good
        print('%s %s:%s:%d anchor %s' % ('OK  ' if good else 'BAD ', commit, path, n, a.encode('ascii', 'backslashreplace').decode()[:60]))
    neg = ok_ref(REFS[0][0], REFS[0][1], REFS[0][2] + 1, REFS[0][3], REFS[0][4])
    print('negative control (line + 1): %s' % ('FAILED as expected' if not neg else 'PASSED - BAD'))
    bad += neg
    print('REFS %d, mismatches %d' % (len(REFS), bad))
    print('ALL OK' if bad == 0 else 'FAILED')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
