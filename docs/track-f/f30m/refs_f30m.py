# -*- coding: utf-8 -*-
"""F30m (HPP-723): the reference map of the seal docs/track-f/f30m.md section 0 (rule 24(1)): every <commit>:<path>:<line> is checked by
git show - the line (leading blanks dropped) starts with its anchor and the next line starts with its +1 anchor.  A negative control (the
line moved by one) must fail.  Port of F30f refs_f30f.py.  Prints one line per reference and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_f30m.py"""
import hashlib
import os
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
VO = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    ('0c91336f', R, 24089, '655. **Звено F30j трека F (`HPP-720`, лид): приёмка F30h и F30i;', '(а) **Приёмка строкой. F30h ✓'),
    ('0c91336f', R, 24092, '(в) **Решение лида по RC5(б) и RC6 — какие биты B считаются контролем', '(г) **Код F30k (Emu Engineer) — константы.**'),
    ('0c91336f', R, 24095, '(е) **Серия F30m (Harness Engineer, под замком через `procload.py`', '(ж) **Правило чтения F30n (лид) — до данных.**'),
    ('0c91336f', R, 24096, '(ж) **Правило чтения F30n (лид) — до данных.**', '(з) **Звенья.**'),
    ('0c91336f', R, 24100, '(л) **Не заявляется:**', '656. **Звено FS11d трека F (`HPP-717`, лид)'),
    ('0c91336f', R, 24107, '657. **Звено FS11d трека F (`HPP-717`, лид): факт п. 656(в) — FS11 `ea51ae80`', '(а) **Установка по шагам п. 656(в)(i)–(iv)**'),
    ('0c91336f', R, 24113, '658. **Звено F30l трека F (`HPP-722`, Red Team) ПРИНЯТО', '(а) **Приёмка строкой. F30l ✓**'),
    ('0c91336f', R, 24115, '(б) **RC1–RC4 печати F30m — приняты**', '(в) **Q1 — решение лида до данных F30m: прочтение (ii)'),
    ('0c91336f', R, 24116, '(в) **Q1 — решение лида до данных F30m: прочтение (ii)', '(г) **RC5–RC7 — приняты;'),
    ('3def0d25', 'docs/track-f/f30l-review.md', 76, '## 7. RC печати F30m', ''),   # +1 anchor '' = an empty line exactly
    ('6fbdcf67', RD, 1294, '//   ROADMAP s122 item 643(v)); 5 = 2 with PB item 6', '//   s122 item 655(g)(1)).'),
    ('6fbdcf67', RD, 1585, 'if ((xsrc & 1u) != 0) {', 'FS::Add(FS::Counter::RtsBadXr, 1);'),
    ('6fbdcf67', RD, 1608, 'LOGF("RtSkipVerify: MISMATCH frame=%d bits=0x%03x reg=%u', 'bits, t_rts_reg ? 1u : 0u, age,'),
    ('6fbdcf67', RD, 3705, 'if (t_rts != 5 && (!buffer.IsRendering()', 'return C::RtsXbPass;'),
    ('6fbdcf67', VO, 3191, '{"rts_bad_r", FS::Counter::RtsBadR, false},', '{"rts_bad_xr", FS::Counter::RtsBadXr, false},'),
    ('6fbdcf67', 'src/common/gates.cpp', 438, '{"KYTY_RT_SKIP", "rtskip", 1, 5},', '// Session 128, MEASUREMENT ONLY'),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    return cache[k]


def find(commit, path, a):
    L = lines(commit, path)
    hits = [i + 1 for i, l in enumerate(L) if l.lstrip().startswith(a)]
    return hits[0] if len(hits) == 1 else None


def ok_ref(commit, path, n, a, b):
    L = lines(commit, path)
    if n is None:
        return find(commit, path, a) is not None
    if n < 1 or n >= len(L):
        return False
    return L[n - 1].lstrip().startswith(a) and (L[n].lstrip().startswith(b) if b else L[n].strip() == '')


def esc(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')


def main():
    me = os.path.abspath(__file__)
    print('suite refs_f30m.py sha256 %s target docs/track-f/f30m.md' % hashlib.sha256(open(me, 'rb').read()).hexdigest())
    ok = True
    for c, p, n, a, b in REFS:
        good = ok_ref(c, p, n, a, b)
        ok &= good
        print('%s %s:%s:%s %s' % ('PASS' if good else 'FAIL', c, p, n if n is not None else 'heading (unique)', esc(a)[:70]))
    c, p, n, a, b = REFS[0]
    neg = ok_ref(c, p, n + 1, a, b)
    print('negative control (line +1): %s' % ('FAILED as expected' if not neg else 'PASSED - BAD'))
    c, p, n, a, b = REFS[13]
    neg2 = ok_ref(c, p, n - 1, a, b)
    print('negative control (code line -1): %s' % ('FAILED as expected' if not neg2 else 'PASSED - BAD'))
    ok &= not neg and not neg2
    print('refs %d' % len(REFS))
    if ok:
        print('ALL OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
