#!/usr/bin/env python3
"""refs_s0.py - S0 (HPP-294): every code reference of docs/track-s/s0-design.md pinned as <commit>:<path>:<line> with an
anchor (general rule 24 (1)): the anchor must be ON the line, and must NOT be on line + 1 (control).  ASCII output."""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = '4fc501f4'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
VO = 'src/graphics/presentation/videoOut.cpp'
GR = 'src/graphics/guest_gpu/graphicsRun.cpp'
CP = 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h'
CS = 'src/graphics/host_gpu/renderer/commandScheduler.cpp'
FS = 'src/common/frameStats.cpp'
EM = 'src/emulator.cpp'
WN = 'src/graphics/presentation/window/window.cpp'
TC = 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
TS = 'tests/shaderCfgTests.cpp'
REFS = (
    ('R1', PC, 228, 'return value == nullptr ? 1 : std::atoi(value);'),
    ('R2', PC, 238, 'return value == nullptr ? 4000u'),
    ('R3', PC, 252, 'return std::clamp(hw / 4u, 2u, 4u);'),
    ('R4', RD, 4429, 'if (pipeline_ptr == nullptr) {'),
    ('R5', RD, 4422, 'wait_when_held || m_skipped_draws.load'),
    ('R6', GR, 3828, 'TakeSkippedDraws() != 0'),
    ('R7', VO, 1191, 'if ((r.incomplete && hold_incomplete) || r.skip_ceil) {'),
    ('R8', VO, 1202, 'if (held.fetch_add(1, std::memory_order_relaxed) < 64) {'),
    ('R9', VO, 1209, 'm_presenter.Discard(*r.frame);'),
    ('R10', VO, 1186, "return value == nullptr || value[0] != '0';"),
    ('R11', PC, 5308, 'if (AsyncPipelinesMode() != 0 && !m_ready_shader_pairs.contains(pair_key)) {'),
    ('R12', PC, 5376, 'LibKernel::KernelTimeFreezeScope freeze_scope;'),
    ('R13', PC, 5127, 'm_ready_cv.wait_for(lock, std::chrono::microseconds(AsyncPipelineWaitUs()),'),
    ('R14', PC, 3916, 'LOGF("AvTrace: shader %s hash=0x%016"'),
    ('R15', PC, 5356, 'LOGF("AvTrace: pipeline gfx vs=%"'),
    ('R16', PC, 3516, 'LOGF("ShaderFirstUse: hash=%016"'),
    ('R17', PC, 6028, 'LOGF("ShaderRegister: hash=%016"'),
    ('R18', PC, 6076, 'if (stored != compatibility) {'),
    ('R19', PC, 6092, 'if (recipes_match(cache.Directory() / "pipelines.bin")) return;'),
    ('R20', PC, 393, 'std::getenv("KYTY_PIPELINE_SALT")'),
    ('R21', PC, 4585, 'fmt::format("{}.{:016x}.bin", title_id, XXH3_64bits(salt, std::strlen(salt)));'),
    ('R22', EM, 209, 'SetCacheTestEnvironment("KYTY_PIPELINE_CACHE", "0");'),
    ('R23', EM, 215, 'SetCacheTestEnvironment("KYTY_PIPELINE_SALT", salt.c_str());'),
    ('R24', PC, 5848, "return value == nullptr || value[0] != '0';"),
    ('R25', CP, 38, "return value == nullptr || value[0] != '0';"),
    ('R26', CP, 116, 'LOGF("CsPretranslate: hit hash=%016"'),
    ('R27', CP, 130, 'LOGF("CsPretranslate: miss hash=%016"'),
    ('R28', CP, 147, 'LOGF("CsPretranslate: summary queued=%zu'),
    ('R29', WN, 962, 'std::getenv("KYTY_SHADER_PREPARE")'),
    ('R30', PC, 1226, 'std::getenv("KYTY_DUMP_GCN");'),
    ('R31', PC, 1253, 'fmt::format("{}_{:016x}.bin", stage_name, shader_hash);'),
    ('R32', TS, 14208, 'std::getenv("KYTY_RECOMPILE"); recompile != nullptr'),
    ('R33', TS, 14531, 'std::getenv("KYTY_CFG_BENCH"); bench != nullptr'),
    ('R34', CS, 651, 'if (wait_us >= 50000) {'),
    ('R35', CS, 654, 'if (stall_logged.fetch_add(1, std::memory_order_relaxed) < 64) {'),
    ('R36', FS, 163, 'Common::EnvFlagOn("KYTY_AV_TRACE");'),
    ('R37', FS, 84, 'return value == nullptr || std::strcmp(value, "lite") != 0;'),
    ('R38', GR, 2030, 'std::getenv("KYTY_ASYNC_COMPUTE");'),
    ('R39', PC, 5926, 'if (now - last_us < 20000000u) {'),
    ('R40', RD, 4435, 'Common::FrameStats::Counter::SkcApSkip, 1);'),
    ('R41', VO, 1200, 'Common::FrameStats::Counter::SkcHeldInc, 1);'),
    ('R42', PC, 3528, 'LibKernel::KernelTimeFreezeScope load_freeze;'),
    ('R43', PC, 3927, 'std::printf("Shaders: VS %zu | PS %zu | CS %zu'),
    ('R44', TC, 559, 'std::getenv("KYTY_SHADER_CACHE");'),
    ('R45', RD, 4436, 'if (n < 200000u) {'),
    ('R46', PC, 2076, 'LOGF("AvTrace: shader-emit %s hash=0x%016"'),
    ('R47', PC, 5675, 'LOGF("AvTrace: pipeline cs cs=%"'),
    ('R48', PC, 6312, 'LOGF("AvTrace: pipeline gfx vs=%"'),
    ('R49', PC, 3531, 'LOGF("AvTrace: shader-cache load hash=0x%016"'),
    ('R50', PC, 6431, 'LOGF("PipelinePrecache: all pipelines created, %"'),
    ('R51', PC, 5963, 'LOGF("PipelinePrecache: saved %u recipes (%zu bytes)'),
    ('R52', RD, 4417, 'std::getenv("KYTY_ASYNC_PIPELINE_WAIT_HELD");'),
    ('R53', PC, 4577, 'std::getenv("KYTY_PIPELINE_CACHE"); env != nullptr && std::atoi(env) == 0'),
    ('R54', PC, 5363, 'm_ready_shader_pairs.insert(pair_key);'),
    ('R55', TS, 14274, 'recompile: vertex fetch/clip/mesh state is not supported'),
    ('R56', PC, 224, 'driver takes 170-500 ms per new shader module'),
    ('R57', PC, 3525, 'Common::FrameStats::Counter::ProgLapCold, 1);'),
)


def main():
    cache = {}
    ok = True
    for rid, path, line, anchor in REFS:
        if path not in cache:
            out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (C, path)], capture_output=True)
            if out.returncode != 0:
                print('%s FAIL git show %s' % (rid, path))
                ok = False
                continue
            cache[path] = out.stdout.decode('utf-8', 'replace').split(chr(10))
        lines = cache[path]
        here = line <= len(lines) and anchor in lines[line - 1]
        nxt = line < len(lines) and anchor in lines[line]
        good = here and not nxt
        ok &= good
        print('%s %s:%s:%d %s control+1 %s' % (rid, C, path, line, 'OK' if here else 'NOT OK', 'NOT OK' if not nxt else 'OK(!)'))
    print('refs: %d' % len(REFS))
    print('ALL OK' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
