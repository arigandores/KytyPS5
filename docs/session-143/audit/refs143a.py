# refs143a.py - Session Auditor, s143 step 3 (HPP-300): the reference map of AUDIT143.md by general rule 24 (1):
# <commit>:<path>:<line> with an anchor (the text of the line) and the +1 control (the text of the next line).
# Also: the count of "dualSrcBlend" in src/ of the installed build commit, and the order "precache ready" -> first
# GuestOut line in the V logs (positions from aud143.json).
import subprocess, json, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
PH = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.h'
SH = 'src/graphics/host_gpu/renderer/pipeline/shaders.cpp'
RM = 'docs/ROADMAP.md'
REFS = [
    ('4fc501f4', PC, 5725, 'constexpr char RECIPES_MAGIC[] = "KytyPR1', ''),  # the +1 line is empty
    ('4fc501f4', PC, 5883, 'w.Pod(key.static_params);', 'w.Info(vs_input_info);'),
    ('4fc501f4', PC, 6039, 'void PipelineCache::FinishPreparation() {', 'if (m_precache_thread.joinable()) {'),
    ('4fc501f4', PC, 6141, 'void PipelineCache::StartPrecache() {', 'if (!PipelinePrecacheEnabled()'),
    ('4fc501f4', PC, 6146, 'm_recipes_path = m_program_cache->translation_cache.Directory() / "pipelines.bin";',
     'if (!Common::File::IsFileExisting(m_recipes_path)) {'),
    ('4fc501f4', PC, 6161, 'void PipelineCache::PrecachePipelines() {', '#if defined(_WIN32)'),
    ('4fc501f4', PC, 6232, 'r.Pod(key.static_params);', 'auto vs_info = std::make_shared<ShaderVertexInputInfo>();'),
    ('4fc501f4', PC, 6303, 'CreatePipelineInternal(m_graphics, *target, key.rendering, key.vertex_input,',
     'std::span<const ShaderVertexInputInfo>(vs_info.get(), 1),'),
    ('4fc501f4', PC, 6071, '"_ShaderSeeds") / PipelineCacheTitleId();', 'std::ifstream manifest(seed / "compatibility.txt");'),
    ('4fc501f4', PH, 44, 'struct PipelineStaticParameters {', 'bool                       negative_one_to_one'),
    ('4fc501f4', PH, 204, '// Called before the guest starts, once the precache producer AND its workers have finished.', ''),
    ('4fc501f4', SH, 260, 'case Prospero::BlendFactor::kSrc1Alpha: return vk::BlendFactor::eSrc1Alpha;',
     'case Prospero::BlendFactor::kOneMinusSrc1Alpha: return vk::BlendFactor::eOneMinusSrc1Alpha;'),
    ('4fc501f4', SH, 505, 'color_blend_attachment[i].srcColorBlendFactor =', 'GetBlendFactor(static_params.color_srcblend[i]);'),
    ('4fc501f4', 'src/graphics/guest_gpu/gpu_defs.h', 232, 'kSrc1Alpha             = 0x11,', 'kOneMinusSrc1Alpha     = 0x12,'),
    ('d82d238c', RM, 12368, '232. **', '   (а) **Порядок (общее правило 25):**'),
    ('d82d238c', RM, 12375, '   (б) **sha256 файлов инструкций (п. 231(з)):**', '   `1b9cb310`'),
    ('d82d238c', RM, 12319, '   (з) **Аудит (п. 230)', '   (п. 230(а)); применение'),
    ('d82d238c', RM, 12337, '   (и) **Цель с. 143', '   все 10 холодных входов'),
    ('d82d238c', RM, 12657, '239. **', '   Принято: харнесс `go143a.sh`'),
    ('d82d238c', RM, 12680, '   п. 231 не меняется; Session Auditor (`HPP-300`) сверяет файлы с. 142 по sha вместо кодов.', '   (в) **Правило 24:**'),
    ('d82d238c', RM, 12853, '242. **', '   лида на вопросы 1–4'),
    ('d82d238c', RM, 13045, '246. **', '   `43e72cbeb4a1931d'),
    ('d82d238c', RM, 13084, '   (ж) **Окно прогонов закрыто для звеньев треков P, F, S целиком', '   Emu Engineer: сборка'),
    ('d82d238c', RM, 13132, '248. **', '   перевода `HPP-322`'),
    ('d82d238c', RM, 13136, '   `HPP-299` берёт замок `v143_01` только когда', '   `next_one.sh v143_01`'),
    ('d82d238c', RM, 13142, '249. **', '   перевода звена; замка'),
    ('d82d238c', RM, 13156, '   (в) **Вопросы исполнителя 1–3', '   Auditor), без игры и без процессов эмулятора'),
]
cache = {}
ok = True
for commit, path, line, anchor, plus1 in REFS:
    k = (commit, path)
    if k not in cache:
        r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
        cache[k] = r.stdout.decode('utf-8', 'replace').splitlines()
    L = cache[k]
    a = L[line - 1] if 0 < line <= len(L) else ''
    b = L[line] if line < len(L) else ''
    good = (anchor in a) and (plus1 in b)
    ok &= good
    if not good:
        near = [i + 1 for i, x in enumerate(L) if anchor in x][:5]
        print('REF FAIL %s:%s:%d anchor %r in line: %s; +1 %r in next: %s; anchor found at %s; line text %r | next %r' % (
            commit, path, line, anchor[:40], anchor in a, plus1[:40], plus1 in b, near, a[:90], b[:90]))
    else:
        print('REF ok %s:%s:%d' % (commit, path, line))
print('REFS %d: %s' % (len(REFS), 'ALL OK' if ok else 'FAIL'))
r = subprocess.run([GIT, '-C', REPO, 'grep', '-c', '-i', 'dualSrcBlend', '4fc501f4', '--', 'src'], capture_output=True)
print('dualSrcBlend in 4fc501f4:src : rc %d (1 = no match), lines %r' % (r.returncode, r.stdout.decode()[:200]))
r = subprocess.run([GIT, '-C', REPO, 'grep', '-n', 'StartPrecache();', '4fc501f4', '--', PC], capture_output=True)
print('StartPrecache call:', r.stdout.decode().strip()[:200])
A = {x['tag']: x for x in json.load(open('C:/kyty/s143/step3/aud143.json'))}
good = 0
for i in range(1, 11):
    L = A['v143_%02d' % i]['log']
    rp = [p for p, t in L['raw']['ShaderPreparation:'] if 'ready completed' in t]
    go = L['first_pos'].get('GuestOut')
    if rp and go is not None and rp[0] < go:
        good += 1
    else:
        print('ORDER v143_%02d: ready %s first GuestOut %s' % (i, rp[:1], go))
print('ORDER "ShaderPreparation: ready" before the first GuestOut line: %d of 10 V logs' % good)
wg = sum(1 for i in range(1, 11) if A['w143_%02d' % i]['log']['count'].get('GuestOut') == 0)
wr = sum(1 for i in range(1, 11) if not [1 for p, t in A['w143_%02d' % i]['log']['raw']['ShaderPreparation:'] if 'ready completed' in t])
print('W logs with 0 GuestOut lines: %d of 10; W logs without "ShaderPreparation: ready": %d of 10' % (wg, wr))
print('ALL DONE')
