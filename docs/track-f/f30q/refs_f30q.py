# -*- coding: utf-8 -*-
"""F30q (HPP-727): the reference map of the seal docs/track-f/f30q.md section 0 (rule 24(1)): every <commit>:<path>:<line> is checked by
git show - the line (leading blanks dropped) starts with its anchor and the next line starts with its +1 anchor.  A negative control (the
line moved by one) must fail.  Port of F30m refs_f30m.py (F30q: ROADMAP c4b2372d items 664-665, the code of T3 at ea38426b).  Prints one line per reference and ALL OK.  ASCII only (anchors printed escaped).
usage: python refs_f30q.py"""
import hashlib
import os
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
VO = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    ('c4b2372d', R, 24163, '664. **Звено F30n трека F (`HPP-724`, лид): чтение серии F30m', '(а) **Приёмка F30k–F30m сделана раньше:**'),
    ('c4b2372d', R, 24171, '(з) **Серия F30q (Harness Engineer, под замком через `procload.py`', '(и) **Правило чтения F30r (лид) — до данных.**'),
    ('c4b2372d', R, 24172, '(и) **Правило чтения F30r (лид) — до данных.**', '(к) **Звенья F30.**'),
    ('c4b2372d', R, 24177, '(о) **Не заявляется:** что `rtskip=1` верен по полям B', '665. **Звено F30p трека F (`HPP-726`, Red Team)'),
    ('c4b2372d', R, 24178, '665. **Звено F30p трека F (`HPP-726`, Red Team) принято', '(а) **Пересчёт лида [c, без игры и замка]:**'),
    ('c4b2372d', R, 24181, '(в) **RC1–RC5 — члены печати F30q (`HPP-727`, Harness Engineer;', '(г) **RC6 — решение лида, поправка п. 664(и)(1)'),
    ('c4b2372d', R, 24182, '(г) **RC6 — решение лида, поправка п. 664(и)(1) до данных', '(д) **Звенья.**'),
    ('ea38426b', RD, 1416, 'inline constexpr uint64_t   kRtsInjEvery = 4096;', 'std::atomic<uint64_t>       g_rts_inj_n {0};'),
    ('ea38426b', RD, 1654, 'void RtsInject(uint32_t cc, const RenderColorInfo* colors, Image* const* img) {', 'namespace FS = Common::FrameStats;'),
    ('ea38426b', RD, 3500, 'LOGF("RtSkip: mode %u ctx_slots=%u groups=%u rec_bytes=%u\\n", armed,', 'static_cast<uint32_t>(t_rts_table->e.size()), Rk3::'),
    ('ea38426b', VO, 3200, '{"rts_inj", FS::Counter::RtsInj, false},', '{"rts_inj_s", FS::Counter::RtsInjS, false},'),
    ('ea38426b', 'src/common/gates.cpp', 439, '{"KYTY_RT_SKIP", "rtskip", 1, 6},', '// Session 128, MEASUREMENT ONLY'),
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
    print('suite refs_f30q.py sha256 %s target docs/track-f/f30q.md' % hashlib.sha256(open(me, 'rb').read()).hexdigest())
    ok = True
    for c, p, n, a, b in REFS:
        good = ok_ref(c, p, n, a, b)
        ok &= good
        print('%s %s:%s:%s %s' % ('PASS' if good else 'FAIL', c, p, n if n is not None else 'heading (unique)', esc(a)[:70]))
    c, p, n, a, b = REFS[0]
    neg = ok_ref(c, p, n + 1, a, b)
    print('negative control (line +1): %s' % ('FAILED as expected' if not neg else 'PASSED - BAD'))
    c, p, n, a, b = REFS[9]
    neg2 = ok_ref(c, p, n - 1, a, b)
    print('negative control (code line -1): %s' % ('FAILED as expected' if not neg2 else 'PASSED - BAD'))
    ok &= not neg and not neg2
    print('refs %d' % len(REFS))
    if ok:
        print('ALL OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
