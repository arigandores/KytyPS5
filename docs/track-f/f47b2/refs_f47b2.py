# F47b2 (HPP-808): map of <commit>:<path>:<line> links of f47b2-review.md (form of refs_f47b.py). Each link: the line
# holds the anchor and the next line holds the +1 text (git show of the commit). Negative control: line+1 must fail.
import subprocess, sys
REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
SH = 'src/graphics/host_gpu/renderer/pipeline/shaders.cpp'
TH = 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h'
TC = 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
FA = 'docs/track-f/f47a2.md'
LINKS = [
    ('ea6c6e9e', SH, 337, 'static vk::ShaderModule CreateDualSourceVariant(', 'uint64_t ps_hash, uint32_t color_count) {'),
    ('ea6c6e9e', SH, 345, 'DualSrcBlend::RewriteLocation1ToIndex1(*pixel_program.spirv, words);', 'outcome != DualSrcBlend::Outcome::Patched) {'),
    ('ea6c6e9e', SH, 587, 'shader_stages[ps_stage_index].module = dual_src_module;', '}'),
    ('ea6c6e9e', TH, 22, 'struct Permutation {', 'ShaderRecompiler::IR::ResourceSpecialization specialization;'),
    ('ea6c6e9e', TH, 30, 'std::vector<Permutation>           permutations;', '};'),
    ('ea6c6e9e', TC, 783, 'w.PodVec(p.spirv);', '}'),
    ('ea6c6e9e', TC, 801, 'file.Write(m_signature.data()', 'file.Write(&payload_hash, sizeof(payload_hash), &w2);'),
    ('ea6c6e9e', BC, 2052, 'if (pieces.size() == 1) {', 'HostImport::Region region {};'),
    ('e63d6339', FA, 71, '| 1 | цвет точки на выходе D_b — литерал программы D_b', '| 2 | цвет — из буфера констант / вершинного цвета'),
    ('e63d6339', FA, 93, '1. **Программа D_b:** модуль PS события D_b в снимке', '`ps_<H>_<ключ>.bin` каталога варианта'),
    ('e63d6339', FA, 98, 'инструкции, дающие экспорт цвета MRT0', 'цепочку `s_mov` / `v_mov` / упаковки до `exp`'),
    ('e63d6339', FA, 100, '3. **Значение в снимке:** цвет, который D_b записал в точке', 'питающая выход, — V_c (справка).'),
    ('e63d6339', FA, 102, '4. **«Равно»:** V_g, приведённое к формату цели D_b', 'цвета зависит только от литералов'),
    ('e63d6339', FA, 87, 'Ч2 — событие заливки цели (clear)', 'гостя; читается по форме (б)(2) как C-buf'),
    ('e63d6339', FA, 129, '«Не равно» (⇒ `дефект` по (в)(4)) — **только**', 'своим разбором; для C-imm'),
    ('e63d6339', FA, 164, '| **П1** — тот же элемент, другой цвет или состояние', '| **П2** — значок HUD'),
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
