# -*- coding: utf-8 -*-
"""F30f (HPP-711): the reference map of the seal docs/track-f/f30f.md section 0 (rule 24(1)): every <commit>:<path>:<line> is checked by
git show - the line (leading blanks dropped) starts with its anchor and the next line starts with its +1 anchor.  A negative control (the
line moved by one) must fail.  Port of F29e refs_f29e.py.  Prints one line per reference and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_f30f.py"""
import hashlib
import os
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
VO = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    ('e52d4b2a', R, 23981, '643. **Звено F30c трека F (`HPP-708`, лид): F30a (`HPP-706`) и отзыв F', '(а) **Приёмка строкой. F30a ✓**'),
    ('e52d4b2a', R, 23985, '(г) **RC2–RC7 — исполнение.**', '(д) **Константы правила (поправка к п. 640(е) до д'),
    ('e52d4b2a', R, 23986, '(д) **Константы правила (поправка к п. 640(е) до данных серии;', '(е) **Звенья**'),
    ('e52d4b2a', R, 23991, '644. **Звено F30e трека F (`HPP-710`, ревью лида)', '(а) **Приёмка строкой. F30e ✓**'),
    ('e52d4b2a', R, 23993, '(б) **RC1 — член печати F30f у `c4`**', '(в) **RC2 — члены печати F30f у `c4`:**'),
    ('e52d4b2a', R, 23994, '(в) **RC2 — члены печати F30f у `c4`:**', '(г) **RC3 — К_B, решение лида:'),
    ('e52d4b2a', R, 23995, '(г) **RC3 — К_B, решение лида:', '(д) **RC4 — члены печати F30f:**'),
    ('e52d4b2a', R, 23996, '(д) **RC4 — члены печати F30f:**', '(е) **Замечание без сценария отказа**'),
    ('e52d4b2a', R, 24037, '649. **Ответ лида на вопрос F30f (`HPP-711`', '(а) **Проверено лидом [c]**'),
    ('e52d4b2a', R, 24039, '(б) **В1 — член (Д7) у каждого тега серии', '(в) **В2 — провал у `c4`'),
    ('e52d4b2a', R, 24040, '(в) **В2 — провал у `c4`', '(г) **В3 — `c3` `NOT_ADMITTED`'),
    ('e52d4b2a', R, 24041, '(г) **В3 — `c3` `NOT_ADMITTED`', '(д) **В4 — форма S9:**'),
    ('e52d4b2a', R, 24042, '(д) **В4 — форма S9:**', '(е) **В5 — удержание:**'),
    ('e52d4b2a', R, 24043, '(е) **В5 — удержание:**', '(ж) **Звенья:**'),
    ('67ea41df', R, 24053, '651. **Ответ лида на вопрос F30f В6 (`HPP-711`', '(а) **Проверено лидом [c]** (свой скрипт'),
    ('67ea41df', R, 24055, '(б) **Член «разбор» у каждого тега серии', '(в) **Следствие нарушения'),
    ('67ea41df', R, 24056, '(в) **Следствие нарушения', '(г) **Справка о связи (не решение):**'),
    ('585d997d', RD, 1605,'if ((bits & 0x030u) != 0) {', 'FS::Add(FS::Counter::RtsBadRx, 1);'),
    ('585d997d', RD, 1610, 'LOGF("RtSkipVerify: MISMATCH frame=%d bits=0x%03x reg=%u', 'bits, t_rts_reg ? 1u : 0u, age,'),
    ('585d997d', RD, 3438, 'LOGF("RtSkip: mode %u ctx_slots=%u groups=%u rec_bytes=%u', 'static_cast<uint32_t>(t_rts_table->e.size())'),
    ('585d997d', RD, 3683, 'if (t_rts != 4) {', "// 3 (N2, N4): the metadata epoch"),
    ('585d997d', VO, 3255, '{"rts_bad_b", FS::Counter::RtsBadB, false},', '{"rts_bad_rx", FS::Counter::RtsBadRx, false},'),
    ('585d997d', 'src/common/gates.cpp', 438, '{"KYTY_RT_SKIP", "rtskip", 1, 4},', '// Session 128, MEASUREMENT ONLY'),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    return cache[k]


def ok_ref(commit, path, n, a, b):
    L = lines(commit, path)
    if n < 1 or n >= len(L):
        return False
    return L[n - 1].lstrip().startswith(a) and L[n].lstrip().startswith(b)


def esc(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')


def main():
    me = os.path.abspath(__file__)
    print('suite refs_f30f.py sha256 %s target docs/track-f/f30f.md' % hashlib.sha256(open(me, 'rb').read()).hexdigest())
    ok = True
    for c, p, n, a, b in REFS:
        good = ok_ref(c, p, n, a, b)
        ok &= good
        print('%s %s:%s:%d %s' % ('PASS' if good else 'FAIL', c, p, n, esc(a)[:70]))
    c, p, n, a, b = REFS[0]
    neg = ok_ref(c, p, n + 1, a, b)
    print('negative control (line +1): %s' % ('FAILED as expected' if not neg else 'PASSED - BAD'))
    ok &= not neg
    print('refs %d' % len(REFS))
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
