"""S17a5 (HPP-638): the references of docs/track-s/s17a5/README.md - every anchor is the whole line N of
`git show <commit>:<path>` (OK), and the control: the same anchor is NOT the line N+1 (NOT OK expected).
Code of this link: main 5bd93ea1 (pipelineCache.cpp of the binary commit c0057ccb is the same blob); other files at
9238a182 (S17a4, unchanged by S17a5). Usage: python refs_s17a5.py (run in C:/kyty/KytyPS5); prints ALL OK."""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
M = '5bd93ea1'
A4 = '9238a182'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
WIN = 'src/graphics/presentation/window/window.cpp'
EMU = 'src/emulator.cpp'
AGC = 'src/libs/agc.cpp'
HI = 'src/graphics/host_gpu/renderer/cache/hostImport.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
REFS = [
    (M, PC, 58, '#include <thread>'),
    (M, PC, 4850, '\t\tStartPrecache();'),
    (M, PC, 4859, '\tm_precache_stop.store(true);'),
    (M, PC, 6586, '\tconst bool active = m_precache_active.load(std::memory_order_acquire);'),
    (M, PC, 6618, 'void PipelineCache::ReplayCloseStop() {'),
    (M, PC, 6619, '\tif (!ShaderReplay::RebuildOn()) {'),
    (M, PC, 6624, '\tm_precache_stop.store(true);'),
    (M, PC, 6626, '\t\tm_precache_thread.join();'),
    (M, PC, 6739, '\t\t} else if (RecipesFileCurrent(m_recipes_path, expected)) {'),
    (M, PC, 6745, '\t\tm_replay_rebuild = skip == nullptr;'),
    (M, PC, 6751, '\tm_precache_active.store(true, std::memory_order_release);'),
    (M, PC, 6754, '\t\t\tReplayRebuild();'),
    (M, PC, 6756, '\t\tif (!m_replay_rebuild || (!m_precache_stop.load() && Common::File::IsFileExisting(m_recipes_path))) {'),
    (M, PC, 6759, '\t\tm_precache_active.store(false, std::memory_order_release);'),
    (M, PC, 7183, 'void PipelineCache::ReplayRebuild() {'),
    (M, PC, 7324, '\t\tif (m_program_cache->LoadEntry(s.key, s.entry)) {'),
    (M, PC, 7343, '\t\t\tif (p.specialization == specialization &&'),
    (M, PC, 7345, '\t\t\t\tperms_cached++;'),
    (M, PC, 7392, '\t\t\t\tif (!cache.Save(key, s->entry.plan, s->entry.permutations)) {'),
    (M, PC, 7411, '\t\tif (m_precache_stop.load()) {'),
    (M, PC, 7414, '\t\tif (SR::TestStand() == SR::Stand::Stop && !stop_stand_done && processed >= records / 2u) {'),
    (M, PC, 7416, '\t\t\tLOGF("ShaderReplay: stand stop applied processed=%u records=%u\\n", processed, records);'),
    (M, PC, 7417, '\t\t\tSR::StandRequestClose();'),
    (M, PC, 7424, '\t\t\tconstexpr uint64_t StandStopWaitMs = 60000;'),
    (M, PC, 7426, '\t\t\twhile (!m_precache_stop.load() && HostMicros() - wait_begin < StandStopWaitMs * 1000u) {'),
    (M, PC, 7430, '\t\t\tif (m_precache_stop.load()) {'),
    (M, PC, 7431, '\t\t\t\tLOGF("ShaderReplay: stand stop seen waited_ms=%" PRIu64 " processed=%u records=%u\\n", waited_ms, processed,'),
    (M, PC, 7433, '\t\t\t\tbreak;'),
    (M, PC, 7435, '\t\t\tLOGF("ShaderReplay: stand stop timeout waited_ms=%" PRIu64 " processed=%u records=%u\\n", waited_ms, processed,'),
    (M, PC, 7438, '\t\tif (processed != 0 && processed % 128u == 0) {'),
    (M, PC, 7543, '\tconst bool stopped = m_precache_stop.load();'),
    (M, PC, 7544, '\tsave_dirty();'),
    (M, PC, 7578, '\tif (stopped) {'),
    (M, PC, 7579, '\t\trecipes_state = "stopped";'),
    (M, PC, 7600, '\t\tif (written != payload.size() || !flushed || !Common::File::RenameFile(temp, m_recipes_path)) {'),
    (M, PC, 7606, '\tif (!stopped && count != 0) {'),
    (M, PC, 7635, '\t     "group_sources=%u pipelines_bin=%s\\n",'),
    (A4, WIN, 992, '\tif (const char* value = std::getenv("KYTY_SHADER_PREPARE"); value != nullptr && value[0] == \'0\') {'),
    (A4, WIN, 1020, '\t\tif (!status.active && SDL_GetTicks64() - started >= hold_ms) break;'),
    (A4, WIN, 1023, '\t\t\tif (g_window->loop.event.type == SDL_QUIT ||'),
    (A4, WIN, 1029, '\t\t\t\tcache.ReplayCloseStop();'),
    (A4, EMU, 167, '\tsubsystems.Initialize<Libs::Graphics::Lifecycle>();'),
    (A4, EMU, 188, '\tif (!Libs::Graphics::WindowPrepareShaders()) {'),
    (A4, EMU, 243, '\tok = at_quick_exit(Common::Subsystems::EmergencyShutdownActive);'),
    (A4, WIN, 1030, '\t\t\t\treturn false;'),
    (A4, EMU, 262, '\tLoadElf(options.elf);'),
    (A4, AGC, 64, '\tauto& presenter = WindowInit(width, height);'),
    (A4, HI, 56, '\tPreload();'),
    (A4, BC, 551, '      m_host_import(graphics),'),
]
cache = {}
ok = True
for commit, path, line, anchor in REFS:
    if (commit, path) not in cache:
        text = subprocess.run([GIT, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        cache[(commit, path)] = text.decode('utf-8').replace('\r\n', '\n').split('\n')
    lines = cache[(commit, path)]
    hit = lines[line - 1] == anchor
    control = lines[line] == anchor
    print('%s:%s:%d %s | +1 %s | +1 text: %s' % (commit, path, line, 'OK' if hit else 'FAIL', 'OK' if control else 'NOT OK',
                                                lines[line].strip()[:90]))
    ok &= hit and not control
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
