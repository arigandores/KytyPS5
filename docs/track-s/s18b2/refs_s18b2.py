import subprocess, sys
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
# (rev, path, line, anchor substring, +1 substring)
REFS = [
    ('7c31481b', PC, 6626, 'if (!ShaderReplay::RebuildOn() || !m_replay_rebuild) {', 'return;'),
    ('7c31481b', PC, 6630, 'LOGF("ShaderReplay: close stop requested', 'm_precache_stop.store(true);'),
    ('7c31481b', PC, 6632, 'while (!m_replay_rebuild_done.load(std::memory_order_acquire)) {', 'std::this_thread::sleep_for'),
    ('7c31481b', PC, 6635, 'LOGF("ShaderReplay: close stop joined', '}'),
    ('7c31481b', PC, 6752, 'm_replay_rebuild = skip == nullptr;', '}'),
    ('7c31481b', PC, 6754, 'if (!m_replay_rebuild && !Common::File::IsFileExisting(m_recipes_path)) {', 'LOGF("PipelinePrecache: no'),
    ('7c31481b', PC, 6762, 'm_replay_rebuild_done.store(true, std::memory_order_release);', '}'),
    ('7c31481b', PC, 6764, 'if (!m_replay_rebuild || (!m_precache_stop.load() && Common::File::IsFileExisting(m_recipes_path))) {', 'PrecachePipelines();'),
    ('7c31481b', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.h', 401, 'm_replay_rebuild_done {false};', 'm_replay_hits_logged = false;'),
    ('7c31481b', 'src/graphics/presentation/window/window.cpp', 1030, 'cache.ReplayCloseStop();', 'return false;'),
    ('0005e11f', 'src/emulator.cpp', 188, 'if (!Libs::Graphics::WindowPrepareShaders()) {', 'std::quick_exit(0);'),
    ('0005e11f', 'src/emulator.cpp', 243, 'ok = at_quick_exit(Common::Subsystems::EmergencyShutdownActive);', 'EXIT_NOT_IMPLEMENTED(ok != 0);'),
    ('0005e11f', 'src/common/logging/log.h', 19, 'emergency_shutdown = Log::Shutdown;', ''),
    ('0005e11f', PC, 4840, 'StartWorkers();', 'StartPrecache();'),
    ('0005e11f', PC, 6717, 'if (!PipelinePrecacheEnabled() || !m_program_cache->translation_cache.Enabled()) {', 'return;'),
    ('0005e11f', PC, 6727, 'if (!ShaderReplay::RebuildOn()) {', 'skip = "mode";'),
    ('0005e11f', PC, 7425, 'while (!m_precache_stop.load() && HostMicros() - wait_begin < StandStopWaitMs * 1000u) {', 'std::this_thread::sleep_for(std::chrono::milliseconds(5));'),
    ('0005e11f', PC, 7542, 'const bool stopped = m_precache_stop.load();', 'save_dirty();'),
    ('0005e11f', PC, 6815, 'for (uint32_t i = 0; i < count && !r.Failed() && !m_precache_stop.load(); i++) {', ''),
    ('0005e11f', 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 59, 'bool RebuildOn() {', 'return Mode() == 1 || Mode() == 3;'),
]
ok = True
for rev, path, n, a, b in REFS:
    lines = subprocess.run([GIT, 'show', f'{rev}:{path}'], cwd=REPO, capture_output=True, check=True).stdout.decode('utf-8', 'replace').split('\n')
    la = lines[n - 1].strip() if n - 1 < len(lines) else ''
    lb = lines[n].strip() if n < len(lines) else ''
    g = (a in la) and (b in lb)
    ok &= g
    print('OK ' if g else 'BAD', f'{rev}:{path}:{n}', '|', la[:80], '|', lb[:60])
print('refs', len(REFS))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
