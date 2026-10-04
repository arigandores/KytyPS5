# S12b (HPP-495, Red Team): every code reference of docs/track-s/s12b-review.md checked by anchor and +1 line on its commit.
import subprocess, sys

PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
REFS = [
    ('4d9e8ab7', PC, 276, 'bool SPcwMode() {', '// Track S, S12a (HPP-494, ROADMAP s122 item 408(l)): default ON'),
    ('4d9e8ab7', PC, 281, "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);", '}();'),
    ('4d9e8ab7', PC, 4713, 'std::getenv("KYTY_PIPELINE_CACHE")', '"Vulkan pipeline cache: disabled (KYTY_PIPELINE_CACHE=0)"'),
    ('4d9e8ab7', PC, 4727, 'if (cache_exists) {', '"Vulkan pipeline cache: loading {}"'),
    ('4d9e8ab7', PC, 4755, 'PipelineCacheLog(', '"Vulkan pipeline cache: invalidating {} (driver, emulator, or data mismatch)"'),
    ('4d9e8ab7', PC, 4760, 'file.Close();', '"Vulkan pipeline cache: invalidating {} (invalid file size)"'),
    ('4d9e8ab7', PC, 4769, 'if (result != vk::Result::eSuccess && !initial_data.empty()) {', '"Vulkan pipeline cache: driver rejected {} ({}); starting empty"'),
    ('4d9e8ab7', PC, 4777, 'if (result != vk::Result::eSuccess) {', '"Vulkan pipeline cache: disabled ({})"'),
    ('4d9e8ab7', PC, 4782, 'if (!initial_data.empty()) {', '"Vulkan pipeline cache: loaded {} bytes from {}"'),
    ('4d9e8ab7', PC, 4807, 'if (SPcwMode()) {', '// S-pcw: the same 20 s period; the write goes to the writer thread'),
    ('4d9e8ab7', PC, 4884, 'void PipelineCache::Save() {', '// S-pcw: the writer thread finishes its write and exits before m_mutex is taken'),
    ('4d9e8ab7', PC, 4895, '!PcwDriverSaved()) {', 'WriteDriverCache();'),
    ('4d9e8ab7', PC, 4912, 'const uint32_t attempts = SPcwMode() ? 8u : 3u;', 'for (uint32_t attempt = 0; attempt < attempts; attempt++) {'),
    ('4d9e8ab7', PC, 4940, 'auto temp_path = m_driver_cache_path;', 'temp_path += ".tmp";'),
    ('4d9e8ab7', PC, 4951, 'if (prefix_written != prefix.size() || payload_written != payload.size() || !flushed ||', '!Common::File::RenameFile(temp_path, m_driver_cache_path)) {'),
    ('4d9e8ab7', PC, 6183, '#if defined(_WIN32)', 'SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_BELOW_NORMAL);'),
    ('4d9e8ab7', PC, 6201, 'if (!SPcwMode()) {', '// KYTY_S_PCW=0 stand: the production write, under m_mutex'),
    ('4d9e8ab7', PC, 6214, 'if (m_pcw_want_driver.exchange(false) || forced) {', '// Every creation counted before this load is in the data read below.'),
    ('4d9e8ab7', PC, 6397, 'if (SPcwMode()) {', '// S-pcw: the same condition; the writer thread writes it, off m_mutex.'),
    ('4d9e8ab7', 'src/common/file.cpp', 547, 'if (IsFileExisting(dst)) {', 'DeleteFile(dst);'),
    ('4d9e8ab7', 'src/common/platform/sysWindowsFileIO.cpp', 576, 'auto dst_wide = dst.wstring();', 'return MoveFileW(src_wide.c_str(), dst_wide.c_str()) != 0;'),
    ('4d9e8ab7', 'src/common/envFlag.h', 31, 'return !(equals("0") || equals("false") || equals("off") || equals("no"));', '}'),
]
ok = True
for c, p, n, anchor, plus1 in REFS:
    t = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').replace('\r', '').split('\n')
    a, b = t[n - 1], t[n]
    good = anchor in a and plus1 in b
    ok &= good
    print('%s %s:%s:%d' % ('OK ' if good else 'BAD', c, p, n))
print('ALL OK' if ok else 'REFS FAILED')
sys.exit(0 if ok else 1)
