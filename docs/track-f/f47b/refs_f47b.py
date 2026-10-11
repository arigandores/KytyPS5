# F47b (HPP-803): map of <commit>:<path>:<line> links of f47b-review.md. Each link: the line holds the anchor and the
# next line holds the +1 text (git show of the commit). Negative control: every link with line+1 must fail the anchor.
import subprocess, sys
REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
LINKS = [
    ('d0bfaf1f', 'src/graphics/presentation/videoOut.cpp', 1274, 'm_presenter.Present(*r.frame);', 'b32.End(0, false);'),
    ('d0bfaf1f', 'src/graphics/presentation/videoOut.cpp', 1280, 'Graphics::RenderDocOnGuestFlip(m_presenter.Renderer());', ''),
    ('d0bfaf1f', 'src/graphics/presentation/renderDoc.cpp', 229, 'if (state == RenderDocState::Requested) {', 'StartCapture();'),
    ('d0bfaf1f', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 1966, 'if (IsRegionGpuModifiedFromGpu(vaddr, size)) {', 'TraceImageUpload(vaddr, size, "gpu-buffer");'),
    ('d0bfaf1f', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 1977, 'if (vaddr != dump_tex) {', 'ImageSource imported {};'),
    ('d0bfaf1f', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 2004, 'if (n < 3) {', 'const auto name = "_tex_" + std::to_string(n) + ".bin";'),
    ('d0bfaf1f', 'src/graphics/guest_gpu/graphicsRun.cpp', 921, 'KYTY_RD_LEVEL_FRAME=<n>[,<n>...]', '<KYTY_RD_LEVEL>" (default intro_next)'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 18, 'во всех 17 записях Sky Garden на бинарях с FS8', 'и 10 тестовых бинарей треков'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 45, 'Уровни: Sky Garden 77', '(`batch_list.tsv`, 60 записей)'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 153, '**Фаза заставки названа до тега:**', 'за 12 снимков) ⇒ s ∈ [729; 761]'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 159, 'миниатюра каждого `renderdoccmd thumb`', 'K, Wt — строка на снимок.'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 175, 'один повтор `f47_rd2` с сеткой `730,733,…,763`', 'Вероятность промаха первого тега'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 181, 'Форма `f47_rd` без `--rd`, с `KYTY_REC` и `KYTY_DUMP_TEX=', '`bufferCache.cpp` `ObtainImageSource`)'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 183, 'при `KYTY_DUMP_TEX` адрес идёт по пути staging', '(детектор §1.3), иначе дамп не годен.'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 204, '- **T.** М2а (байты): байты T# в памяти гостя', 'игра открыла в логе'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 211, 'член провенанса: значения — точные 0 / 1', 'цвета [I: стечение устаревших байт'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 213, '- **R.** Цепочка продолжается на продукт ГП', '- **N.** М2 = «не равно» по определению'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 216, '**Реплей воспроизводит** (член исхода)', 'сохранённой конечной цели'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 221, '- **П1 (положительный):** значок HUD', '§4.2–§4.3; ожидается класс T'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 223, '- **Н1 (мутант байта):**', 'изменённого блока.'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 225, '- **Н2 (чужой вход):**', '- **Н3 (продукт ГП):**'),
    ('d0bfaf1f', 'docs/track-f/f47a.md', 237, '4. Хотя бы в одной точке: М2а «не равно»', 'названным местом (событие, ресурс, адрес)'),
]


def show(c, p):
    r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True)
    if r.returncode:
        return None
    return r.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')


cache = {}
bad = 0
neg = 0
for c, p, n, a, nxt in LINKS:
    key = (c, p)
    if key not in cache:
        cache[key] = show(c, p)
    L = cache[key]
    ok = L is not None and n - 1 < len(L) and a in L[n - 1] and nxt in L[n]
    if not ok:
        bad += 1
        print('BAD', c, p, n, repr(L[n - 1][:90]) if L and n - 1 < len(L) else None)
    if L is not None and n < len(L) and a in L[n]:
        print('NEG not caught', c, p, n)
    else:
        neg += 1
print('links %d bad %d neg %d of %d' % (len(LINKS), bad, neg, len(LINKS)))
print('ALL OK' if bad == 0 and neg == len(LINKS) else 'FAIL')
sys.exit(0 if bad == 0 and neg == len(LINKS) else 1)
