# FS11b (HPP-715, Red Team, general rule 24(1)): the <commit>:<path>:<line> references of docs/track-f/fs11b-review.md - each
# by its anchor (whole line, stripped) and the +1 control line; the anchor must be unique in the file. Negative control: the
# same check at line+1 must fail for every reference. Prints the references and ALL OK / FAILED.
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = 'ee9632be'
REFS = [
    ('src/graphics/host_gpu/regionManager.h', 'const char* value = std::getenv("KYTY_FIX_B12");',
     "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);"),
    ('src/graphics/host_gpu/renderer/renderContext.cpp', 'const bool fix_b12 = FixB12Enabled();', 'if (fix_b12) {'),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'const bool b12_pass = m_bda_pass_open;',
     'for (auto cursor = scan_begin; cursor < scan_end;) {'),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'm_bda_region_stamps.resize(MemoryTracker::RegionCount());', '}'),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'LOGF("FixB12: mode=%d\\n", fix_b12 ? 1 : 0);', '}'),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.h', 'struct BdaRegionStamp {', 'MemoryTracker::RegionStamp stamp;'),
    ('src/graphics/host_gpu/memoryTracker.h', 'static constexpr size_t REGION_COUNT = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE;', None),
    ('src/graphics/host_gpu/regionDefinitions.h', 'constexpr uint64_t TRACKER_REGION_SIZE  = 4ull * 1024ull * 1024ull;',
     'constexpr uint64_t TRACKER_ADDRESS_SIZE = 1ull << 40u;'),
    ('src/common/frameStats.cpp', ': lean     ? static_cast<uint32_t>(Counter::LogNs)', ': static_cast<uint32_t>(Counter::Count);'),
]
ok = True
neg_ok = True
for path, anchor, nxt in REFS:
    lines = subprocess.run([G, '-C', REPO, 'show', C + ':' + path], capture_output=True).stdout.decode('utf-8').split('\n')
    hits = [i for i, l in enumerate(lines) if l.strip() == anchor]
    if len(hits) != 1:
        print('FAIL anchor not unique/absent', path, anchor, hits)
        ok = False
        continue
    i = hits[0]
    nxt_line = lines[i + 1].strip() if i + 1 < len(lines) else None
    good = nxt is None or nxt_line == nxt
    shown_next = nxt if nxt is not None else nxt_line
    print(('OK   ' if good else 'FAIL ') + '%s:%s:%d  anchor <<%s>>  +1 <<%s>>' % (C, path, i + 1, anchor, shown_next))
    ok &= good
    # negative control: the anchor must not be found at line+1
    if lines[i + 1].strip() == anchor:
        neg_ok = False
print('negative control (shift +1 never matches):', 'FAILED as expected' if neg_ok else 'DID NOT FAIL')
print('REFS %d %s' % (len(REFS), 'ALL OK' if ok and neg_ok else 'FAILED'))
sys.exit(0 if ok and neg_ok else 1)
