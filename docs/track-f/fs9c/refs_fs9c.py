# -*- coding: utf-8 -*-
"""FS9c (HPP-673): the reference map of the seal docs/track-f/fs9c.md (rule 24(1)): every <commit>:<path>:<line> is checked by git show -
the line starts with its anchor and the next line starts with its +1 anchor.  A negative control (the line moved by one) must fail.
Port of F24e refs_f24e.py.  Prints one line per reference and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_fs9c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
REFS = [
    ('07d31ad3', R, 23654, '604. **Звено F24f трека F (`HPP-665`, лид)', '   (а) **Приёмка строкой по членам п. 595(е).**'),
    ('07d31ad3', R, 23659, '   (д) **Отгрузка — FS9, девятый бинарь отгрузки трека F', '   (1) **FS9a (Emu Engineer, без замка).**'),
    ('07d31ad3', R, 23662, '   (3) **FS9c (Harness Engineer, под замком;', '   - `fs9_v` — форма `b13_v`'),
    ('07d31ad3', R, 23663, '   - `fs9_v` — форма `b13_v`', '   - `fs9_w` — форма `b13_w`'),
    ('07d31ad3', R, 23664, '   - `fs9_w` — форма `b13_w`', '   Одна попытка на тег;'),
    ('07d31ad3', R, 23665, '   Одна попытка на тег;', '   (4) **FS9d (лид):**'),
    ('07d31ad3', R, 23658, '   (г) **Вывод: Б13 `FIXED`**', '   (д) **Отгрузка — FS9'),
    ('4a1e7c97', R, 23671, '   (и) **Не заявляется:** что Б13 проявляется в игре', '605. **Факт п. 604(ж)'),
    ('07d31ad3', R, 23096, '   (г) **Общее правило 33', '   (д) **Сообщение пользователю**'),
    ('07d31ad3', R, 23506, '587. **Звено S18c2', '   (а) **Приёмка строкой (правило 24):**'),
    ('07d31ad3', R, 23538, '590. **Звено S18d', '   (а) **Установка по шагам'),
    ('ccfdb1ff', 'docs/track-f/f25f/f25f_seal_body.md', 62, '- **Неразрывный блок серии (п. 604, вариант (в)(1)):**',
     '  в этот промежуток не берётся.'),
    ('aee72cee', 'docs/track-f/f24e.md', 140, '## 8. Варианты исполнителя', ''),
    ('aee72cee', 'docs/track-f/f24e.md', 149, '## 9. Отчёт тегов', ''),
    ('84dbb96b', 'docs/track-f/fs9a.md', 26, '- **Бинарь FS9: sha256 `3861eeeae6f2487682b0519195c10d2b4d927029462e695f3634b5bdddea4eb5`**',
     '  `C:/kyty/f287/bin/kyty_emulator_3861eeea.exe`'),
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
