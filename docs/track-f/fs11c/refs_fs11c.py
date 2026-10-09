# -*- coding: utf-8 -*-
"""FS11c (HPP-716): the reference map of the seal docs/track-f/fs11c.md section 0 (rule 24(1)): every <commit>:<path>:<line> is checked by
git show - the line (leading blanks dropped) starts with its anchor and the next line starts with its +1 anchor.  A negative control (the
line moved by one) must fail.  Port of F29e refs_f29e.py.  Prints one line per reference and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_fs11c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
REFS = [
    ('cfd646d1', R, 24026, '647. **Звено F29f трека F (`HPP-705`, лид)', '(а) **Приёмка строкой.**'),
    ('cfd646d1', R, 24031, '(д) **Отгрузка FS11 — константы лида.**', '(е) **Реестр §94**'),
    ('cfd646d1', R, 24035, '(и) **Не заявляется:** п. 639(к), 645(ж), 646(д) целиком', '648. **Факт п. 647(ж)'),
    ('cfd646d1', R, 24061, '652. **Звено FS11b трека F (`HPP-715`, Red Team)', '(а) **Пересчёт лида [c]**'),
    ('cfd646d1', R, 24067, '(1) **Н1 — «не исправлено, читать так»:**', '(2) **Н2'),
    ('cfd646d1', R, 24068, '(2) **Н2 — «не исправлено, читать так»:**', '(3) **Н3'),
    ('cfd646d1', R, 24073, '(б) **Члены задания строкой.** Печать до первого тега ✓', '(в) **Наблюдение лида для F30g'),
    ('ee9632be', BC, 604, 'LOGF("FixB12: mode=%d', '}'),
    ('ee9632be', BC, 3439, 'LOGF("FixB12Stat: passes=%llu rewalk=%llu rwd=%llu lskip=%llu', 'static_cast<unsigned long long>(m_b12_rewalk)'),
    ('ee9632be', 'src/graphics/host_gpu/regionManager.h', 65, '// BufferCache\'s constructor prints "FixB12: mode=<0|1>" once per process.',
     '// Track F, FS11a'),
    ('775302f6', 'docs/track-f/f29e.md', 98, '| `b12_v` | удержание ≥ 300 с после первого кадра сцены', '| `b12_w` | процесс жив до конца удержания'),
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
