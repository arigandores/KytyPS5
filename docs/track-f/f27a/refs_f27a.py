"""F27a (HPP-690, track F): code references of the report - <commit>:<path>:<line> with the anchor (the whole line,
stripped) and the +1 control line (general rule 24(1)).  Offline, read-only: git show only.
Usage: python refs_f27a.py  (run from C:/kyty/KytyPS5); prints the table and ALL OK when every anchor is found exactly
once at the printed line and the +1 line equals the recorded control."""
import subprocess
import sys

PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
CS = 'src/graphics/host_gpu/renderer/commandScheduler.cpp'
EM = 'src/emulator.cpp'

# (id, commit, path, anchor, +1 control)
REFS = [
    ('R1', '25f3886', PC,
     '// Called with m_mutex held right after a new pipeline was created. The process is often ended',
     '// without running destructors (the window is closed by the OS, a debugger, a timeout), so the'),
    ('R2', '25f3886', PC,
     'void PipelineCache::MaybeWriteDriverCache() {',
     'MaybeWriteRecipes();'),
    ('R3', '25f3886', PC,
     'PipelineCacheLog("Vulkan pipeline cache: saved {} bytes to {} ({} us)", payload.size(),',
     'Common::PathToString(m_driver_cache_path), HostMicros() - write_begin);'),
    ('R4', '25f3886', PC,
     'LOGF("AvTrace: pipeline gfx vs=%" PRIu64 " ps=%" PRIu64 " us=%" PRIu64 " total=%" PRIu64 "\\n",',
     'vs_id, ps_id, HostMicros() - create_begin,'),
    ('R5', '25f3886', PC,
     'PipeLockHolder    holder(m_lock_holder, 3);',
     'if (AvTraceEnabled()) {'),
    ('R6', '25f3886', CS,
     'if (wait_us >= 50000) {',
     'Common::FrameStats::Add(Common::FrameStats::Counter::PrioStall, 1);'),
    ('R7', 'dc5d4712', PC,
     'const char* value = std::getenv("KYTY_S_PCW");',
     "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);"),
    ('R8', 'dc5d4712', PC,
     '// S-pcw: the same 20 s period; the write goes to the writer thread (one flag: requests merge).',
     'm_pcw_want_driver.store(true);'),
    ('R8b', '25f3886', PC,
     '" total=%" PRIu64 " async wait_us=%" PRIu64 " pending=%u\\n",',
     'vs_id, ps_id, create_end - create_begin,'),
    ('R9', 'dc5d4712', PC,
     'const bool saved = WriteDriverCache(forced ? " forced" : "");',
     'm_pcw_gen.fetch_add(1);'),
    ('R10', 'dc5d4712', EM,
     'SetCacheTestEnvironment("KYTY_PIPELINE_CACHE", "0");',
     'if (selected == "cold") {'),
    ('R11', 'dc5d4712', PC,
     'm_driver_cache_path = std::filesystem::path("_PipelineCache") /',
     'fmt::format("{}.{:016x}.bin", title_id, XXH3_64bits(salt, std::strlen(salt)));'),
    ('R12', 'dc5d4712', PC,
     'const char* value = std::getenv("KYTY_PIPELINE_PRECACHE");',
     "return value == nullptr || value[0] != '0';"),
    ('R13', 'dc5d4712', PC,
     'void PipelineCache::RecordGraphicsRecipe(const GraphicsPipelineKey&   key,',
     'const ShaderVertexInputInfo& vs_input_info,'),
]


def lines_of(commit, path):
    out = subprocess.run(['git', 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
    return [l.strip() for l in out.decode('utf-8', 'replace').split('\n')]


def main():
    ok = True
    cache = {}
    for rid, commit, path, anchor, ctl in REFS:
        key = (commit, path)
        if key not in cache:
            cache[key] = lines_of(commit, path)
        t = cache[key]
        hits = [i for i, l in enumerate(t) if l == anchor]
        good = len(hits) == 1 and hits[0] + 1 < len(t) and t[hits[0] + 1] == ctl
        # every anchor must occur exactly once in its file
        line = hits[0] + 1 if hits else None
        print('%s %s:%s:%s  hits=%d  +1 %s  | %s' % (rid, commit, path, line, len(hits), 'ok' if good else 'BAD', anchor))
        ok &= good
    print('ALL OK' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
