"""F34a: check <commit>:<path>:<line> references of docs/track-f/f34a.md (general rule 24(1)).

Each ref: anchor must be in the line, the +1 control must be in the next line; negative control: the anchor shifted
by +1 line must NOT match (prints NOT OK for the shifted copy, as expected).  Last line ALL OK only if every real ref
matches and every shifted copy fails.
"""
import subprocess, sys

K = 'C:/kyty/KytyPS5'
P = 'C:/kyty/KytyPS5/ps5 em'
REFS = [
    (K, '595b38dd', 'docs/ROADMAP.md', 24254, '673. **Звено F32c трека F (`HPP-735`, лид)', '(а) **Приёмка F32a (`HPP-733`).**'),
    (K, '595b38dd', 'docs/ROADMAP.md', 24283, '(2) **F34 = Б6 (K3).** `F34a` (Probe Designer, офлайн)', '(3) **Довод свипа (RC1, RC8), офлайн.**'),
    (K, '595b38dd', 'docs/ROADMAP.md', 24288, '(л) **Не заявляется:** что игра корректна на какой-либо сцене', ''),
    (K, '595b38dd', 'docs/track-f/register.md', 153, '| Б6 | K3 | наблюдение (дефект не показан)', '| Б4 | K1 (при выходе)'),
    (K, '595b38dd', 'src/kernel/pvar.h', 275, 'FlipQueue::Flip, after flip_status.count++', 'void PublishFlip(uint64_t count);'),
    (K, '595b38dd', 'src/graphics/presentation/videoOut.cpp', 1465, 'LOGF("FrameTrace: n=%" PRIu64 " dt_us=%llu', '" gpu_blocked=%llu submits=%llu'),
    (K, '595b38dd', 'src/graphics/presentation/window/inputScript.cpp', 201, 'LOGF("InputScript: press %s at %.2f s (present %u)', 'i++;'),
    (P, '2e021a2', 'HANDOFF.md', 4523, 'интерьер корабля, крупный план Astro, экстерьер, зелёный пришелец на НЛО', '5. **ПРИОРИТЕТ №1'),
    (P, '2e021a2', 'HANDOFF.md', 4617, 'проходит целиком (пришелец → разрыв корабля → планета → пустыня', '6a. **Небо пустыни'),
    (P, '2e021a2', 'HANDOFF.md', 4622, '6b. «Падающие частицы»/дым в комнате с пришельцем', 'дымка комнаты оказалась текстурой стен'),
    (P, '2e021a2', 'HANDOFF.md', 5752, 'Стандарт: `KYTY_KEYS="@2170:j,@2460:j"` → `intro_next`', ''),
    (P, '2e021a2', 'HANDOFF.md', 2879, 'ненадёжен (`d67a` дошёл до `worldmap` и не доехал до `intro_next`)', 'за 13,4 с'),
    (P, '2e021a2', 'HANDOFF.md', 6739, '**Битые текстуры (e0045fe).** Стенки комнаты с пришельцем', '(`rd_drawtex.py`)'),
]


def lines(repo, rev, path):
    out = subprocess.run(['git', '-C', repo, 'show', '%s:%s' % (rev, path)], capture_output=True).stdout
    return out.decode('utf-8').split('\n')


ok = True
cache = {}
for repo, rev, path, n, anchor, plus1 in REFS:
    key = (repo, rev, path)
    if key not in cache:
        cache[key] = lines(repo, rev, path)
    L = cache[key]
    good = n - 1 < len(L) and anchor in L[n - 1] and (plus1 == '' or plus1 in L[n])
    shifted = n < len(L) and anchor in L[n]
    print('%s %s:%s:%d' % ('OK    ' if good else 'BAD   ', rev, path, n))
    print('%s %s:%s:%d (shift +1, negative control)' % ('NOT OK' if not shifted else 'MATCH!', rev, path, n + 1))
    ok &= good and not shifted
print('refs', len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
