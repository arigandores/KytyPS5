# S5d (Red Team): every code / ROADMAP anchor of docs/track-s/s5d-review.md - whole-line anchor substring at line N, control
# substring at N+1, read from git show <commit>:<path>.  Prints ALL OK or MISMATCH.
import subprocess
REPO = 'C:/kyty/KytyPS5'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
RM = 'docs/ROADMAP.md'
A = [
    ('2ce6326e', PC, 1307, 'LOGF("GcnDumpReg: skip type=%u hash=%016" PRIx64 " size=%u', 'size_bytes);'),
    ('2ce6326e', PC, 4750, 'm_pcw_want_driver.store(true);', 'm_driver_cache_saved_us = now;'),
    ('2ce6326e', PC, 4836, 'if ((m_driver_cache_unsaved != 0 || m_driver_cache_saved_us == 0) && !PcwDriverSaved()) {', 'WriteDriverCache();'),
    ('2ce6326e', PC, 4853, 'const uint32_t attempts = SPcwMode() ? 8u : 3u;', 'for (uint32_t attempt = 0; attempt < attempts; attempt++) {'),
    ('2ce6326e', PC, 5219, 'const bool     pcw_trace   = PcwOverlapTrace();', 'const uint64_t pcw_gen0    = pcw_trace ? m_pcw_gen.load() : 0;'),
    ('2ce6326e', PC, 5228, 'PcwNoteOverlap("wait gfx", programs.vertex[0].id, ps_input_info != nullptr ? programs.pixel.id : 0,', 'pcw_gen0, HostMicros() - pcw_wait_t0);'),
    ('2ce6326e', PC, 5445, 'EnqueueJob([this, job, target, vs_id, ps_id, pair_key, queued_at] {', ''),
    ('2ce6326e', PC, 5447, 'CreatePipelineInternal(', ''),
    ('2ce6326e', PC, 5713, 'EnqueueJob([this, job, target, module, id, hash, queued_at] {', 'const auto create_begin = HostMicros();'),
    ('2ce6326e', PC, 5715, 'CreatePipelineInternal(m_graphics, *target, *job, module, m_driver_cache);', 'EXIT_NOT_IMPLEMENTED(target->pipeline == nullptr);'),
    ('2ce6326e', PC, 5809, 'pcw_gen0   = PcwOverlapTrace() ? m_pcw_gen.load() : 0; // S5c, RC3', 'wait_begin = HostMicros();'),
    ('2ce6326e', PC, 5816, 'PcwNoteOverlap("wait cs", compute_program.id, 0, pcw_gen0, HostMicros() - wait_begin);', '}'),
    ('2ce6326e', PC, 5819, 'const auto stall_us = HostMicros() - wait_begin;', 'Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncWaitUs, stall_us);'),
    ('2ce6326e', PC, 6120, 'return SPcwMode() && m_pcw_saved_any && m_pcw_saved_created == m_pcw_created.load() && !m_pcw_want_driver.load();', '}'),
    ('2ce6326e', PC, 6155, 'if (m_pcw_want_driver.exchange(false) || forced) {', '// Every creation counted before this load is in the data read below.'),
    ('2ce6326e', PC, 6158, 'm_pcw_gen.fetch_add(1); // odd: a write is in flight', 'const bool saved = WriteDriverCache(forced ? " forced" : "");'),
    ('2ce6326e', PC, 6160, 'm_pcw_gen.fetch_add(1);', 'if (saved) {'),
    ('2ce6326e', PC, 6185, 'lock_us                      = hold_begin - lock_begin;', 'if (m_recipes_path.empty() || m_recipe_count == 0) {'),
    ('2ce6326e', PC, 6202, 'hold_us   = HostMicros() - hold_begin;', '}'),
    ('2ce6326e', PC, 6205, 'LOGF("AvTrace: pcw recipes copied=%zu count=%u lock_us=%" PRIu64 " hold_us=%" PRIu64', 'lock_us, hold_us);'),
    ('2ce6326e', PC, 6249, 'if ((gen0 & 1u) == 0 && gen1 == gen0) {', 'return;'),
    ('2ce6326e', PC, 6341, 'm_pcw_want_driver.store(true);', 'm_driver_cache_saved_us = HostMicros();'),
    ('2ce6326e', PC, 6602, 'CreatePipelineInternal(m_graphics, *target, key.rendering, key.vertex_input,', ''),
    ('2ce6326e', PC, 6677, 'CreatePipelineInternal(m_graphics, *target, *info, module, m_driver_cache);', ''),
    ('a1e8bc90', RM, 12994, '245. **Приёмка звена S5b трека S (`HPP-317`, Red Team;', 'заданий S5c/S5d).** Отзыв'),
    ('a1e8bc90', RM, 13008, '**Гейты до S6:** подпись транслятора бинаря = `699c1e4b…`', '`git diff 4fc501f4` дерева — только два файла;'),
    ('a1e8bc90', RM, 13016, '(б) **RC2–RC5 — к исполнению Emu Engineer в звене S5c**', 'RC2 — `&& !m_pcw_want_driver.load()` в `PcwDriverSaved()`;'),
    ('a1e8bc90', RM, 13022, '(в) **RC6 — решение:**', '3, как прежде; правка в S5c).'),
]
cache = {}
ok = True
for c, p, n, a, b in A:
    if (c, p) not in cache:
        cache[(c, p)] = subprocess.run(['git', '-C', REPO, 'show', c + ':' + p], capture_output=True,
                                       check=True).stdout.decode('utf-8').split(chr(10))
    L = cache[(c, p)]
    good = a in L[n - 1] and b in L[n]
    ok &= good
    print('OK ' if good else 'BAD', c, p.split('/')[-1], n)
print('ALL OK' if ok else 'MISMATCH')
