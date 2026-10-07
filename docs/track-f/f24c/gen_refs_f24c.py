"""Track F link F24c (HPP-662): find the lines of the references of f24c.md by anchor text and write refs_f24c.tsv
(commit, path, line, anchor, +1 anchor = the stripped next line, cut to 60 characters). Each anchor is looked up as the
given occurrence (1-based) of a line containing it at that commit. Copy of docs/track-f/f24a/gen_refs_f24a.py with the
reference list of F24c. ASCII code, UTF-8 data.

    python gen_refs_f24c.py [--out refs_f24c.tsv]
"""
import os
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RM = 'src/graphics/host_gpu/regionManager.h'
MT = 'src/graphics/host_gpu/memoryTracker.h'
MC = 'src/graphics/host_gpu/memoryTracker.cpp'
RD = 'src/graphics/host_gpu/regionDefinitions.h'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
SB = 'src/graphics/host_gpu/renderer/cache/streamBuffer.h'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
GA = 'src/common/gates.cpp'
FS = 'src/common/frameStats.h'
ST = 'tests/B13EpochStand.cpp'
RMAP = 'docs/ROADMAP.md'
B = '238d019e'
F = '21f8ca76'

# (commit, path, anchor, occurrence)
REFS = [
    (B, MT, 'manager->ChangeState<DirtySource::Cpu, true>(manager->GetCpuAddr() + offset, bytes);', 1),
    (B, MT, 'manager->ChangeState<DirtySource::Cpu, true>(open_begin, open_size);', 1),
    (B, RM, 'bits.SetRangeRelaxed(start, end);', 1),
    (B, GA, '{"KYTY_REGION_EPOCH", "regionepoch", false},', 1),
    (B, BC, 'return {m_memory_tracker.CpuWriteEpoch(), 0};', 1),
    (B, SB, 'return epoch != 0 && upload_epoch == epoch && upload_epoch_kind == kind &&', 1),
    (B, BC, 'return {m_memory_tracker.RangeWriteEpoch(vaddr, size), 1};', 1),
    (B, MT, 'mixed = (mixed ^ manager->Epoch()) * 0x100000001b3ull;', 1),
    (B, BC, 'clean = m_memory_tracker.IsRegionCpuCleanFast(vaddr, size);', 1),
    (B, RM, '// HasCurrentUpload check fails. A BDA scan observing these epochs still acquires this', 1),
    (B, GA, '{"KYTY_BUF_FAST", "buffast", false},', 1),
    (B, BC, 'fast_epoch = m_memory_tracker.RangeWriteEpoch(vaddr, size);', 1),
    (B, BC, 'if (fast_epoch != 0 && m_memory_tracker.RangeWriteEpoch(vaddr, size) == fast_epoch) {', 1),
    (B, BC, 'const auto epoch      = m_memory_tracker.RangeWriteEpoch(vaddr, size);', 1),
    (B, BC, 'const uint64_t pre = m_memory_tracker.RangeWriteEpoch(vaddr, size);', 1),
    (B, PC, 'regions.push_back({index, tracker->RegionWriteStamp(index)});', 1),
    (B, PC, 'if (!(tracker->RegionWriteStamp(region.index) == region.stamp)) {', 1),
    (B, BC, 'const uint64_t bln_gwe = bln >= 2 ? m_memory_tracker.CpuWriteEpoch() : 0;', 1),
    (B, BC, 'const bool moved_g = m_memory_tracker.CpuWriteEpoch() != carry.gwe;', 1),
    (B, RC, 'const auto cpu_epoch          = m_buffer_cache.CpuWriteEpoch();', 1),
    (B, RC, 'const bool bda_cached = reuse && cpu_epoch == m_bda_cpu_epoch &&', 1),
    (B, RC, 'm_bda_cpu_epoch          = cpu_epoch;', 1),
    (B, BC, 'const bool bit_clear = use_bits && !BdaTakeRegionWrite(index);', 1),
    (B, BC, 'const auto stamp = m_memory_tracker.RegionWriteStamp(index);', 1),
    (B, BC, 'if (seen.generation == m_bda_stamp_generation && seen.stamp == stamp) {', 1),
    (B, BC, 'm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);', 1),
    (B, MC, 'BdaNoteRegionWrite(index);', 1),
    (B, RM, 'm_epoch.fetch_add(1, std::memory_order_release);', 3),
    (B, GA, '{"KYTY_ARM_DEFER", "armdefer", false},', 1),
    (B, RD, 'g_bda_write_bits[word].fetch_or(uint64_t {1} << (index % 64u), std::memory_order_release);', 1),
    (B, RD, 'if ((g_bda_write_bits[word].load(std::memory_order_acquire) & bit) == 0) {', 1),
    (B, MT, 'return m_cpu_epoch.load(std::memory_order_acquire);', 1),
    (B, RM, 'return m_epoch.load(std::memory_order_acquire);', 1),
    (B, FS, 'RbCen::g_rb_gen.fetch_add(1, std::memory_order_release);', 1),
    (B, RM, 'Common::B2Reuse::ResetCpu(Common::FrameStats::Counter::B2rRstCpuw);', 1),
    (B, RM, 'm_cpu_epoch.fetch_add(1, std::memory_order_release);', 2),
    (F, RM, '#include "common/envFlag.h"', 1),
    (F, RM, '[[nodiscard]] inline bool FixB13Enabled() noexcept {', 1),
    (F, RM, 'if (FixB13Enabled()) {', 1),
    (F, RM, 'm_epoch.fetch_add(1, std::memory_order_release);', 1),
    (F, RM, 'B13Test::Hook(11);', 1),
    (F, RM, 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);', 1),
    (F, RM, 'B13Test::Hook(12);', 1),
    (F, RM, 'm_cpu_epoch.fetch_add(1, std::memory_order_release);', 1),
    (F, RM, 'B13Test::Hook(13);', 1),
    (F, RM, 'Common::B2Reuse::ResetCpu(Common::FrameStats::Counter::B2rRstCpuw);', 1),
    (F, RM, '// Track F, F24c: KYTY_FIX_B13=0 - the text before F24c, verbatim', 1),
    (F, RM, 'UpdateProtection<!enable, false>();', 1),
    (F, MC, 'const bool               fix_b13 = FixB13Enabled();', 1),
    (F, MC, 'LOGF("FixB13: mode=%d', 1),
    (F, ST, 'const bool     point_ok =', 1),
    ('1e46c4bd', RMAP, '595. **Звено F24b трека F (`HPP-659`, лид): F24a (`HPP-658`) ПРИНЯТ', 1),
]


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = argv[argv.index('--out') + 1] if '--out' in argv else os.path.join(here, 'refs_f24c.tsv')
    rows = []
    cache = {}
    ok = True
    for c, p, a, occ in REFS:
        if (c, p) not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True)
            cache[(c, p)] = r.stdout.decode('utf-8', 'replace').split('\n') if r.returncode == 0 else []
        lines = cache[(c, p)]
        hits = [i for i, l in enumerate(lines) if a in l]
        if len(hits) < occ:
            ok = False
            print('FAIL %s:%s anchor %r occurrence %d of %d' % (c, p, a, occ, len(hits)))
            continue
        i = hits[occ - 1]
        nxt = lines[i + 1].strip()[:60] if i + 1 < len(lines) else ''
        rows.append('\t'.join([c, p, str(i + 1), a, nxt]))
        print('%s:%s:%d' % (c, p, i + 1))
    open(out_path, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('ROWS %d, %s' % (len(rows), 'ALL OK' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
