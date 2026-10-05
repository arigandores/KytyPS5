# S17b2 (HPP-619): anchors <commit>:<path>:<line> with the anchor line and the +1 control, from git show.
import subprocess, sys
C = 'a2fee0d9'
P = 'src/graphics/host_gpu/renderer/pipeline/'
REFS = [
    ('src/graphics/presentation/window/window.cpp', 1029, 'cache.ReplayCloseStop();', 'return false;'),
    (P + 'pipelineCache.cpp', 6618, 'if (!ShaderReplay::RebuildOn()) {', 'return;'),
    (P + 'pipelineCache.cpp', 6623, 'm_precache_stop.store(true);', 'if (m_precache_thread.joinable()) {'),
    (P + 'pipelineCache.cpp', 6585, 'const bool active = m_precache_active.load(std::memory_order_acquire);', 'return {active, m_precache_total.load(), m_precache_completed.load(), m_precache_skipped.load()};'),
    (P + 'pipelineCache.cpp', 6755, 'if (!m_replay_rebuild || (!m_precache_stop.load() && Common::File::IsFileExisting(m_recipes_path))) {', 'PrecachePipelines();'),
    (P + 'pipelineCache.cpp', 6815, 'for (uint32_t i = 0; i < count && !r.Failed() && !m_precache_stop.load(); i++) {', 'const size_t record_begin = r.Pos();'),
    (P + 'pipelineCache.cpp', 7041, 'WaitForPendingPipelines();', 'LOGF("PipelinePrecache: all pipelines created, %" PRIu64 " ms\\n", (HostMicros() - t0) / 1000u);'),
    (P + 'pipelineCache.cpp', 5052, 'm_idle_cv.wait(lock, [this] { return m_jobs.empty() && m_jobs_active == 0; });', '}'),
    (P + 'pipelineCache.cpp', 250, 'return std::max(1u, static_cast<uint32_t>(std::atoi(value)));', '}'),
    (P + 'pipelineCache.cpp', 256, 'return std::clamp(hw / 4u, 2u, 4u);', '}();'),
    (P + 'pipelineCache.cpp', 5023, 'm_job_cv.wait(lock, [this] { return m_stop_workers || !m_jobs.empty(); });', 'if (m_jobs.empty()) {'),
    (P + 'pipelineCache.cpp', 7410, 'if (m_precache_stop.load()) {', 'break;'),
    (P + 'pipelineCache.cpp', 7413, 'if (SR::TestStand() == SR::Stand::Stop && !stop_stand_done && processed >= records / 2u) {', 'stop_stand_done = true;'),
    (P + 'pipelineCache.cpp', 7523, 'const bool stopped = m_precache_stop.load();', 'save_dirty();'),
    (P + 'pipelineCache.cpp', 7558, 'if (stopped) {', 'recipes_state = "stopped";'),
    (P + 'pipelineCache.cpp', 7586, 'if (!stopped && count != 0) {', '// S17a2 (item 532(g), RC3 of the S17b review): Signature() ends with its own newline (shaderTranslationCache.cpp);'),
    (P + 'pipelineCache.cpp', 7593, 'std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}\\n", signature);', 'for (const auto& [id, s]: sources) {'),
    (P + 'pipelineCache.cpp', 7548, '// Under m_mutex: ProgramCache::ReplayAdopt reads the map under it (KYTY_SHADER_PREPARE=0 lets the guest start', '// while this thread still runs).'),
    (P + 'pipelineCache.cpp', 6880, 'if (m_replay_capture != nullptr) [[unlikely]] {', 'ReplayCapturePipe(1, vs_program.id, key.ps_shader_id, &key); // S17a'),
    (P + 'pipelineCache.cpp', 4808, 'uint64_t ReplaySpecIdOf(uint64_t id) {', 'const auto ref = by_id.find(id);'),
    (P + 'shaderTranslationCache.cpp', 603, 'variant + "\\n";', 'm_enabled = true;'),
    (P + 'shaderReplay.cpp', 53, 'bool RebuildOn() {', 'return Mode() == 1 || Mode() == 3;'),
    (P + 'shaderReplay.cpp', 604, 'if (!base.ok || !base.complete || !(base.specialization == live)) {', 'why = "base";'),
    (P + 'shaderReplay.cpp', 687, 'const bool rejected = !check.ok || !check.complete || !(check.specialization == live);', 'LOGF("ShaderReplay: stand canon applied hash=0x%016" PRIx64 " rejected=%d\\n", plan.shader_hash, rejected ? 1 : 0);'),
    (P + 'shaderReplay.cpp', 696, 'if (!check.ok || !check.complete || !(check.specialization == live)) {', '// Diagnosis for the log (only on a failure): the words whose raw value alone makes the check pass.'),
    (P + 'shaderReplay.cpp', 708, 'why += fmt::format(" culprit={}:role{}:{:08x}->{:08x}", i, canonical[i].role, raw[i].value,', 'canonical[i].value);'),
    (P + 'shaderReplay.cpp', 1029, 'm_thread       = std::thread([this] { Loop(); });', '}'),
    (P + 'shaderReplay.cpp', 1084, 'if (m_unsaved >= 256u || (m_unsaved != 0 && NowMs() - m_last_save_ms >= 30000u)) {', 'SaveGeneration();'),
    (P + 'shaderReplay.cpp', 1158, 'if (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {', 'if (why.starts_with("self")) {'),
    (P + 'shaderReplay.cpp', 1168, 'm_stats.canon_mismatch = m_stats.canon_self + m_stats.canon_residual;', 'if (m_stats.canon_self + m_stats.canon_residual + m_stats.canon_base + m_stats.canon_big <= 20u) {'),
    (P + 'shaderReplay.h', 73, 'ROLE_T_LO    = 6,', 'ROLE_T_HI    = 7,'),
    ('src/emulator.cpp', 188, 'if (!Libs::Graphics::WindowPrepareShaders()) {', 'std::quick_exit(0);'),
    ('src/emulator.cpp', 198, 'Libs::Graphics::WindowRun();', 'std::quick_exit(0);'),
]
ok = True
for path, line, anchor, plus1 in REFS:
    text = subprocess.run(['git', 'show', C + ':' + path], capture_output=True, cwd='C:/kyty/KytyPS5').stdout.decode('utf-8')
    L = text.split('\n')
    a = L[line - 1].strip() if line - 1 < len(L) else None
    b = L[line].strip() if line < len(L) else None
    good = a == anchor.strip() and b == plus1.strip()
    ok &= good
    print(('OK  ' if good else 'BAD ') + C + ':' + path + ':' + str(line))
    if not good:
        print('    got  :', a)
        print('    got+1:', b)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
