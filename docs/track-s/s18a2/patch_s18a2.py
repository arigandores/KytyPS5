#!/usr/bin/env python3
# S18a2 (HPP-650, ROADMAP s122 item 576(g)): ReplayCloseStop waits for the end of ReplayRebuild only when the rebuild
# runs in this start; without a rebuild it returns at once (the FS8 close path). Usage: patch_s18a2.py <repo root>
import sys
from pathlib import Path

root = Path(sys.argv[1])
NL = chr(10)


def patch(rel, pairs):
    p = root / rel
    raw = p.read_bytes()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', NL)
    for old, new in pairs:
        old_s = NL.join(old)
        new_s = NL.join(new)
        n = text.count(old_s)
        if n != 1:
            sys.exit(f'FAIL {rel}: anchor count {n}: {old[0]!r}')
        text = text.replace(old_s, new_s)
    if crlf:
        text = text.replace(NL, '\r\n')
    p.write_bytes(text.encode('utf-8'))
    print(f'OK {rel} ({len(pairs)} hunks, crlf={crlf})')


CPP = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
H = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.h'
WIN = 'src/graphics/presentation/window/window.cpp'
SR = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'

patch(CPP, [
    ([
        '// Track S, S17a2 (HPP-618, ROADMAP s122 item 532(b), RC1 of the S17b review): WindowPrepareShaders returned false (the',
        '// window was closed on the preparation screen) and the caller (emulator.cpp, Execute) ends the process by',
        '// std::quick_exit, which runs no destructor - ~PipelineCache never stores m_precache_stop. At KYTY_S_REPLAY 1 or 3 (the',
        '// rebuild may run on the precache thread) this stores m_precache_stop and joins the thread: the rebuild loop stops',
        '// before its next R-PIPE and takes its stopped branch (translation cache files of the sources it changed saved, no',
        '// pipelines.bin, no manifest, line "ShaderReplay: rebuild ... pipelines_bin=stopped"); PrecachePipelines stops before',
        '// its next recipe. The wait is at most one R-PIPE (or one recipe). At 0 and 2 nothing is done (the old close path).',
        'void PipelineCache::ReplayCloseStop() {',
        '\tif (!ShaderReplay::RebuildOn()) {',
        '\t\treturn;',
        '\t}',
        '\tconst auto begin = HostMicros();',
        '\tLOGF("ShaderReplay: close stop requested precache_active=%d\\n", m_precache_active.load() ? 1 : 0);',
        '\tm_precache_stop.store(true);',
        '\tif (m_precache_thread.joinable()) {',
        '\t\tm_precache_thread.join();',
        '\t}',
        '\tLOGF("ShaderReplay: close stop joined wait_ms=%" PRIu64 "\\n", (HostMicros() - begin) / 1000u);',
        '}',
    ], [
        '// Track S, S17a2 (HPP-618, ROADMAP s122 item 532(b), RC1 of the S17b review): WindowPrepareShaders returned false (the',
        '// window was closed on the preparation screen) and the caller (emulator.cpp, Execute) ends the process by',
        '// std::quick_exit, which runs no destructor - ~PipelineCache never stores m_precache_stop.',
        '// S18a2 (HPP-650, ROADMAP s122 item 576(g)(2), RC1 of the S18b review): only the rebuild is waited for, never the',
        '// PrecachePipelines phase (it ends with WaitForPendingPipelines - the whole pipeline queue).',
        '// (i) No rebuild in this start (KYTY_S_REPLAY 0 or 2, or StartPrecache set m_replay_rebuild false - no replay/',
        '// folder, compat mismatch, recipes current): returns at once - no m_precache_stop, no wait, no line (the FS8 path).',
        '// (ii) The rebuild runs: stores m_precache_stop and waits for m_replay_rebuild_done, stored by the precache thread',
        '// right after ReplayRebuild returned. The rebuild loop stops before its next R-PIPE and takes its stopped branch',
        '// (translation cache files of the sources it changed saved, no pipelines.bin, no manifest, line "ShaderReplay:',
        '// rebuild ... pipelines_bin=stopped"); the thread then skips PrecachePipelines (m_precache_stop is set) and is not',
        '// joined. The wait is at most one R-PIPE. The line "close stop joined" means "the rebuild ended".',
        '// (iii) The rebuild already ended (PrecachePipelines may run): the same two lines, no wait (wait_ms 0);',
        '// m_precache_stop only makes PrecachePipelines stop before its next recipe, nobody waits for it.',
        'void PipelineCache::ReplayCloseStop() {',
        '\tif (!ShaderReplay::RebuildOn() || !m_replay_rebuild) {',
        '\t\treturn;',
        '\t}',
        '\tconst auto begin = HostMicros();',
        '\tLOGF("ShaderReplay: close stop requested precache_active=%d\\n", m_precache_active.load() ? 1 : 0);',
        '\tm_precache_stop.store(true);',
        '\twhile (!m_replay_rebuild_done.load(std::memory_order_acquire)) {',
        '\t\tstd::this_thread::sleep_for(std::chrono::milliseconds(1));',
        '\t}',
        '\tLOGF("ShaderReplay: close stop joined wait_ms=%" PRIu64 "\\n", (HostMicros() - begin) / 1000u);',
        '}',
    ]),
    ([
        '\t\tif (m_replay_rebuild) [[unlikely]] {',
        '\t\t\tReplayRebuild();',
        '\t\t}',
    ], [
        '\t\tif (m_replay_rebuild) [[unlikely]] {',
        '\t\t\tReplayRebuild();',
        '\t\t\tm_replay_rebuild_done.store(true, std::memory_order_release); // S18a2: ReplayCloseStop waits for it',
        '\t\t}',
    ]),
])

patch(H, [
    ([
        '\t// Track S, S17a2 (ROADMAP s122 item 532(b)): the window was closed on the preparation screen. At KYTY_S_REPLAY 1 or',
        '\t// 3 stores m_precache_stop and joins the precache/rebuild thread; at 0 and 2 returns at once.',
    ], [
        '\t// Track S, S17a2 (ROADMAP s122 item 532(b)): the window was closed on the preparation screen. S18a2 (item 576(g)):',
        '\t// when the rebuild runs in this start, stores m_precache_stop and waits for the end of ReplayRebuild (not for',
        '\t// PrecachePipelines); without a rebuild (any KYTY_S_REPLAY) returns at once.',
    ]),
    ([
        '\tbool                                     m_replay_rebuild     = false; // StartPrecache: the rebuild runs first',
    ], [
        '\tbool                                     m_replay_rebuild     = false; // StartPrecache: the rebuild runs first',
        '\t// S18a2 (item 576(g)(2)): stored true by the precache thread right after ReplayRebuild returned; read by',
        '\t// ReplayCloseStop (main thread) only when m_replay_rebuild is true. Never stored back to false.',
        '\tstd::atomic<bool>                        m_replay_rebuild_done {false};',
    ]),
])

patch(WIN, [
    ([
        '\t\t\t\t// Track S, S17a2 (ROADMAP s122 item 532(b)): the caller ends the process by std::quick_exit; at',
        '\t\t\t\t// KYTY_S_REPLAY 1 or 3 the precache/rebuild thread is stopped and joined first (nothing at 0 and 2).',
    ], [
        '\t\t\t\t// Track S, S17a2 (ROADMAP s122 item 532(b)): the caller ends the process by std::quick_exit; a rebuild',
        '\t\t\t\t// running in this start is stopped and waited for first (S18a2, item 576(g); nothing without a rebuild).',
    ]),
])

patch(SR, [
    ([
        '\t// (window.cpp, WindowPrepareShaders) returns false after PipelineCache::ReplayCloseStop stored m_precache_stop and',
        '\t// joined the precache/rebuild thread (S17a2, item 532(b)); then the caller ends the process by std::quick_exit.',
    ], [
        '\t// (window.cpp, WindowPrepareShaders) returns false after PipelineCache::ReplayCloseStop stored m_precache_stop and',
        '\t// waited for the end of the rebuild (S17a2, item 532(b); S18a2, item 576(g)); then the caller ends the process by',
        '\t// std::quick_exit.',
    ]),
])
print('ALL OK')
