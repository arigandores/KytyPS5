#!/usr/bin/env python3
# S1 (Red Team): every code reference of s1-review.md - anchor at the line, control: anchor NOT equal to line+1.
import subprocess, sys
C = '4fc501f4'
P = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
V = 'src/graphics/presentation/videoOut.cpp'
R = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
T = 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
K = 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h'
E = 'src/emulator.cpp'
W = 'src/graphics/presentation/window/window.cpp'
REFS = [
    (P, 224, '// driver takes 170-500 ms per new shader module: serial compilation froze the frame for 1-5 s.'),
    (P, 228, 'return value == nullptr ? 1 : std::atoi(value);'),
    (P, 3519, 'DumpShaderGcn(stage, params.hash, params.code);'),
    (P, 3530, 'if (LoadFromTranslationCache(lookup_key, entry) && AvTraceEnabled()) {'),
    (P, 3864, 'DumpShaderGcn(options.stage, options.shader_hash, params.code);'),
    (P, 3869, 'prepared = pretranslation.Take(params.code, params.hash, input_info,'),
    (P, 3918, 'label, params.hash, translate_end - translate_begin, HostMicros() - translate_end,'),
    (P, 4578, 'PipelineCacheLog("Vulkan pipeline cache: disabled (KYTY_PIPELINE_CACHE=0)");'),
    (P, 4660, 'if (m_driver_cache == nullptr) {'),
    (P, 4806, 'PipelineCacheLog("Vulkan pipeline cache: saved {} bytes to {} ({} us)", payload.size(),'),
    (P, 5127, 'm_ready_cv.wait_for(lock, std::chrono::microseconds(AsyncPipelineWaitUs()),'),
    (P, 5354, 'Common::LockGuard lock(m_mutex);'),
    (P, 5362, 'MaybeWriteDriverCache();'),
    (P, 5376, 'LibKernel::KernelTimeFreezeScope freeze_scope;'),
    (P, 5399, 'MaybeWriteDriverCache();'),
    (P, 6008, 'known = m_program_cache->programs.contains(key);'),
    (P, 6012, 'if (!known) { m_program_cache->pretranslation.Enqueue({code, mapped.code_size_bytes / 4}, mapped.hash,'),
    (P, 6028, 'LOGF("ShaderRegister: hash=%016" PRIx64 " type=%u size=%u scratch=%u code=%016" PRIx64'),
    (P, 6092, 'if (recipes_match(cache.Directory() / "pipelines.bin")) return;'),
    (P, 6154, 'm_precache_active.store(false, std::memory_order_release);'),
    (P, 6430, 'WaitForPendingPipelines();'),
    (V, 1191, 'if ((r.incomplete && hold_incomplete) || r.skip_ceil) {'),
    (V, 1206, 'if (!r.skip_ceil && !r.incomplete) {'),
    (V, 1211, 'if (r.skip_ceil) {'),
    (R, 4422, 'wait_when_held || m_skipped_draws.load(std::memory_order_relaxed) == 0;'),
    (T, 639, 'if (std::memcmp(data.data(), m_signature.data(), m_signature.size()) != 0) {'),
    (K, 38, "return value == nullptr || value[0] != '0';"),
    (E, 209, 'SetCacheTestEnvironment("KYTY_PIPELINE_CACHE", "0");'),
    (E, 215, 'SetCacheTestEnvironment("KYTY_PIPELINE_SALT", salt.c_str());'),
    (W, 990, 'if (!status.active && SDL_GetTicks64() - started >= hold_ms) break;'),
    (P, 393, 'if (const char* salt = std::getenv("KYTY_PIPELINE_SALT"); salt != nullptr && salt[0] != 0) {'),
    (R, 4429, 'if (pipeline_ptr == nullptr) {'),
    (V, 1193, 'Common::FrameStats::Add(Common::FrameStats::Counter::SkcHeld, 1);'),
]
DOCS = [  # (commit, path, line, anchor prefix)
    ('6e2c892e', 'docs/shader-preparation.md', 48, 'Local verification after session 39 (2026-09-10)'),
    ('6e2c892e', 'docs/shader-preparation.md', 58, 'Session 41 verified and installed the refreshed seed'),
    ('db6a8ff2', 'docs/ROADMAP.md', 12139, '229. **Трек S — шейдеры без фризов'),
    ('455b3a25', 'docs/ROADMAP.md', 12480, '235. **Приёмка звена S0 трека S'),
]
cache = {}
ok = True
for path, line, anchor in REFS:
    if path not in cache:
        cache[path] = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (C, path)],
                                     capture_output=True).stdout.decode('utf-8').replace('\r', '').split('\n')
    L = cache[path]
    hit = L[line - 1].strip() == anchor
    ctrl = L[line].strip() == anchor
    ok &= hit and not ctrl
    print('%s %s:%s:%d anchor=%s control+1=%s' % ('OK' if hit and not ctrl else 'BAD', C, path, line, hit, 'NOT OK' if not ctrl else 'OK'))
for c, path, line, anchor in DOCS:
    L = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (c, path)],
                       capture_output=True).stdout.decode('utf-8').replace('\r', '').split('\n')
    hit = L[line - 1].strip().startswith(anchor)
    ctrl = L[line].strip().startswith(anchor)
    ok &= hit and not ctrl
    print('%s %s:%s:%d anchor=%s control+1=%s' % ('OK' if hit and not ctrl else 'BAD', c, path, line, hit, 'NOT OK' if not ctrl else 'OK'))
print('refs', len(REFS) + len(DOCS))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
