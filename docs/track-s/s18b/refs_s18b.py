import subprocess
R = 'C:/kyty/KytyPS5'
C = '62ff7b5b'
P = 'src/graphics/host_gpu/renderer/pipeline/'
REFS = [
    (P + 'shaderReplay.cpp', "if (value == nullptr || value[0] == '\\0') {"),
    (P + 'shaderReplay.cpp', "if (value[0] < '0' || value[0] > '3' || value[1] != '\\0') {"),
    (P + 'shaderReplay.cpp', 'static const int mode = ParseMode(std::getenv("KYTY_S_REPLAY"));'),
    (P + 'shaderReplay.cpp', 'bool CaptureOn() {'),
    (P + 'shaderReplay.cpp', 'bool RebuildOn() {'),
    (P + 'shaderReplay.cpp', ': m_directory(std::move(directory)), m_compat(std::move(compat)) {}'),
    (P + 'shaderReplay.cpp', 'std::ifstream pointer(m_directory / "replay.cur");'),
    (P + 'shaderReplay.cpp', 'if (!(pointer >> current) || current == 0) {'),
    (P + 'shaderReplay.cpp', 'if (!Common::File::CreateDirectories(m_directory)) {'),
    (P + 'shaderReplay.cpp', 'm_thread       = std::thread([this] { Loop(); });'),
    (P + 'pipelineCache.cpp', 'if (mode == 0) {'),
    (P + 'pipelineCache.cpp', 'm_replay_store       = std::make_unique<ShaderReplay::Store>(directory, compat);'),
    (P + 'pipelineCache.cpp', 'if (ShaderReplay::CaptureOn()) {'),
    (P + 'pipelineCache.cpp', 'm_program_cache->replay_active    = true;'),
    (P + 'pipelineCache.cpp', 'if (!ShaderReplay::RebuildOn()) {'),
    (P + 'pipelineCache.cpp', '} else if (m_replay_state == "mismatch") {'),
    (P + 'pipelineCache.cpp', '} else if (m_replay_state != "ok" || m_replay_catalogue->pipes.empty()) {'),
    (P + 'pipelineCache.cpp', '} else if (RecipesFileCurrent(m_recipes_path, expected)) {'),
    (P + 'pipelineCache.cpp', 'm_replay_rebuild = skip == nullptr;'),
    (P + 'pipelineCache.cpp', 'if (m_replay_rebuild) [[unlikely]] {'),
    (P + 'pipelineCache.cpp', 'std::ofstream file(m_replay_store->Directory() / "rebuild_manifest.tsv", std::ios::binary | std::ios::trunc);'),
    (P + 'pipelineCache.cpp', 'void PipelineCache::ReplayCloseStop() {'),
    (P + 'pipelineCache.cpp', 'm_precache_stop.store(true);\n\tif (m_precache_thread.joinable()) {'),
    (P + 'pipelineCache.cpp', 'for (uint32_t i = 0; i < count && !r.Failed() && !m_precache_stop.load(); i++) {'),
    (P + 'pipelineCache.cpp', 'VulkanLogMemoryStats();\n\tWaitForPendingPipelines();'),
    (P + 'pipelineCache.cpp', 'm_jobs.push_back(std::move(job));'),
    (P + 'pipelineCache.cpp', 'if (replay_active) [[unlikely]] {'),
    (P + 'pipelineCache.cpp', 'if (replay_capture != nullptr) {'),
    (P + 'pipelineCache.cpp', 'if (m_replay_capture != nullptr) [[unlikely]] {'),
    ('src/graphics/presentation/window/window.cpp', 'cache.ReplayCloseStop();'),
]
for path, anchor in REFS:
    lines = subprocess.run(['git', '-C', R, 'show', f'{C}:{path}'], capture_output=True, check=True).stdout.decode('utf-8').split('\n')
    first = anchor.split('\n')[0]
    hits = [i for i, l in enumerate(lines) if l.strip() == first.strip() and
            ('\n' not in anchor or lines[i + 1].strip() == anchor.split('\n')[1].strip())]
    for i in hits:
        print(f'{C}:{path}:{i + 1}\t{lines[i].strip()}\t+1: {lines[i + 1].strip()}')
    if not hits:
        print('MISSING', path, anchor)
