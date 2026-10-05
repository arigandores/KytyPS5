import subprocess
import sys

C = '283a6ef9'
anchors = [
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'int Mode() {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'if (canon_stand && !g_canon_stand_done.load()) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'g_canon_stand_done.store(true);'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'bool Answer(Replayer* replayer, uint64_t address, uint32_t* value, bool clean) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'if (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value)) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'bool WriteFileAtomic(const std::filesystem::path& path, const std::vector<uint8_t>& data) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'if (!WriteFileAtomic(m_directory / "replay.cur", pointer)) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'void Push(Slot slot) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'const bool stopping = m_stop.load(std::memory_order_acquire);'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', '// (window.cpp, WindowPrepareShaders) returns and the shutdown path stores m_precache_stop.'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'if (TestStand() == Stand::Addr && !m_addr_stand_done) {'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderReplay.h', 'constexpr uint32_t FormatVersion      = 1;'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (mode == 0) {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'm_precache_stop.store(true);'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ReplayCapturePipe(1, vs_program.id, key.ps_shader_id, &key); // S17a'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ReplayCapturePipe(2, program.id, 0, nullptr); // S17a'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}", cache.Signature());'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (m_precache_stop.load()) {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (SR::TestStand() == SR::Stand::Spec && !spec_stand_done) {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (memo_entry->permutation->replay_flags != 0) [[unlikely]] {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (permutation->replay_flags != 0) [[unlikely]] {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (replay_active) [[unlikely]] {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (p.specialization == specialization &&'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'void PipelineCache::ReplayCapturePipe(uint32_t kind, uint64_t first_id, uint64_t second_id,'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ReplayInit(); // track S, S17a: returns at once at KYTY_S_REPLAY=0'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ReplayStop(); // track S, S17a: nothing at KYTY_S_REPLAY=0'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (m_replay_catalogue != nullptr) [[unlikely]] {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'if (m_replay_capture != nullptr) [[unlikely]] {'),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ShaderRecompiler::IR::MaterializeResources(source.resource_plan, recorder.Runtime(), snapshot,'),
    ('src/emulator.cpp', 'if (!Libs::Graphics::WindowPrepareShaders()) {'),
    ('src/common/platform/sysWindowsFileIO.cpp', 'return MoveFileW(src_wide.c_str(), dst_wide.c_str()) != 0;'),
    ('src/graphics/shader/shaderBindings.h', '[[nodiscard]] uint64_t MetaAddr() const {'),
    ('src/graphics/shader/shaderBindings.h', '[[nodiscard]] uint64_t Base40() const {'),
    ('src/graphics/shader/shaderBindings.h', '[[nodiscard]] uint64_t Base48() const {'),
    ('src/libs/agc.h', 'static constexpr auto        shutdown   = Libs::Graphics::Shutdown;'),
    ('src/graphics/shader/recompiler/ShaderRecompiler.cpp', 'static_cast<uint32_t>(options.user_data.size()), wave_size);'),
    ('docs/track-s/s17a/r_addr.py', 'T_META6, T_META7, INERT) and whose value is not in the canonical form of that role (shaderReplay.h, Role; the same rule'),
]
for path, a in anchors:
    t = subprocess.run(['git', 'show', C + ':' + path], capture_output=True).stdout.decode('utf-8').split('\n')
    hits = [i for i, l in enumerate(t) if l.strip() == a.strip()]
    if not hits:
        hits = [i for i, l in enumerate(t) if a.strip() in l]
    for i in hits[:4]:
        print('%s:%s:%d | %s || +1 %s' % (C, path, i + 1, t[i].strip()[:110], t[i + 1].strip()[:90]))
    if not hits:
        print('NOTFOUND', path, a)
