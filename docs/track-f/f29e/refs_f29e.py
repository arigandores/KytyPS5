# -*- coding: utf-8 -*-
"""F29e (HPP-704): the reference map of the seal docs/track-f/f29e.md section 0 (rule 24(1)): every <commit>:<path>:<line> is checked by
git show - the line (leading blanks dropped) starts with its anchor and the next line starts with its +1 anchor (an empty +1 anchor = the
next line is empty).  A negative control (the line moved by one) must fail.  Port of FS10c refs_fs10c.py.  Prints one line per reference
and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_f29e.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
REFS = [
    ('87dafe31', R, 23939, '639. **Звено F29b трека F (`HPP-701`, лид)', '(а) **Приёмка строкой. F29a ✓**'),
    ('87dafe31', R, 23950, '(4) **Теги под замком — «нет вреда»** (F29e;', '**Чтение:** (1)–(4) все ✓'),
    ('87dafe31', R, 23951, '**Чтение:** (1)–(4) все ✓', '(ж) **Звенья F29**'),
    ('87dafe31', R, 23955, '(к) **Не заявляется:** что Б12 проявляется в игре', '640. **Звено F28b трека F'),
    ('87dafe31', R, 24000, '645. **Звено F29d трека F (`HPP-703`, ревью лида)', ''),
    ('87dafe31', R, 24002, '(а) **Приёмка.** Члены п. 639(е)(3)', ''),
    ('87dafe31', R, 24014, '(ж) **Не заявлять:** что Б12 проявляется в игре и с какой частотой; что окно RC1', '646. **Звено F29c3 трека F'),
    ('87dafe31', R, 24015, '646. **Звено F29c3 трека F (`HPP-713`', ''),
    ('87dafe31', R, 24023, '(г) **Порядок.** Решение ревью `HPP-713` — approve', ''),
    ('87dafe31', R, 24025, '(д) **Не заявлять:** что окно RC1 случается в игре', ''),
    ('c7d0c857', 'docs/track-f/f29c.md', 385, '- **sha256 `cabbd818397a8a299e7e64cf2d153197ad7e69e310015b5d473bb66f37802e95`**',
     '`C:/kyty/f287/bin/kyty_emulator_cabbd818.exe`'),
    ('726e751e', BC, 605, 'LOGF("FixB12: mode=%d', '}'),
    ('726e751e', BC, 3497, 'LOGF("FixB12Stat: passes=%llu rewalk=%llu rwd=%llu lskip=%llu', 'static_cast<unsigned long long>(m_b12_rewalk)'),
    ('18e339db', 'docs/track-f/fs10c.md', 70, '| `fs10_v` | `fs9_v`:', '| `fs10_w` | `fs9_w`:'),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.split(b'\n')
    return cache[k]


def ok_ref(commit, path, n, a, b):
    L = lines(commit, path)
    if not (1 <= n < len(L)):
        return False
    cur, nxt = L[n - 1].lstrip(), L[n].lstrip()
    good_b = nxt.rstrip(b'\r') == b'' if b == '' else nxt.startswith(b.encode('utf-8'))
    return cur.startswith(a.encode('utf-8')) and good_b


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
