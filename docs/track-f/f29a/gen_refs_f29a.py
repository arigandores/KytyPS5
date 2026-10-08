"""F29a (HPP-699): the '<commit>:<path>:<line>' references of f29a.md, found by whole anchors (the line holds the anchor,
the next line holds the +1 anchor; both unique as a pair). Writes refs_f29a.tsv (commit, path, line, anchor, +1 anchor)
for refs_f29a.py. Copy of the F24a gen_refs idea. ASCII code.

    python gen_refs_f29a.py <commit> <out.tsv>
"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
BH = 'src/graphics/host_gpu/renderer/cache/bufferCache.h'
RS = 'src/graphics/host_gpu/rangeSet.h'
RM = 'src/graphics/host_gpu/regionManager.h'
MT = 'src/graphics/host_gpu/memoryTracker.cpp'
GT = 'src/common/gates.cpp'
KM = 'src/kernel/memory.cpp'
ST = 'tests/B12BdaStampStand.cpp'
REFS = [
    ('prep_foreach', RC, 'm_mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {',
     'm_buffer_cache.SynchronizeBuffersInRange(start, end - start);'),
    ('prep_narrow', RC, 'const auto narrow = Common::Gates::Value(Common::Gates::Knob::BdaNarrowStamps);',
     'm_buffer_cache.SetBdaNarrowCheck(narrow == 2);'),
    ('prep_map_bump', RC, 'if (m_mapping_epoch != m_bda_mapping_epoch) {', 'm_buffer_cache.InvalidateBdaRegionStamps();'),
    ('prep_reg_bump', RC, '} else if (registration_epoch != m_bda_registration_epoch) {', 'if (narrow == 1) {'),
    ('map_add', RC, 'm_mapped_ranges.Add(vaddr, size);', '++m_mapping_epoch;'),
    ('rs_merge', RS, 'while (it != m_ranges.end() && it->first <= last) {', 'begin = std::min(begin, it->first);'),
    ('rs_foreach', RS, 'for (const auto& [begin, end]: m_ranges) {', 'func(begin, end);'),
    ('rs_map', RS, 'std::map<uint64_t, uint64_t> m_ranges;', '};'),
    ('inr_last', BC, 'const auto last = std::prev(m_buffers.lower_bound(end));',
     'const auto& last_buffer = m_slot_buffers[last->second];'),
    ('inr_begin', BC, 'const auto scan_begin = std::max(vaddr, first->first);',
     'const auto scan_end = std::min(end, last_buffer.CpuAddress() + last_buffer.Size());'),
    ('inr_byregion', BC, 'if (Common::Gates::Enabled(Common::Gates::Gate::BdaRegionStamps)) {',
     'SynchronizeBuffersByRegion(scan_begin, scan_end);'),
    ('inr_full', BC, 'm_memory_tracker.CollectCpuModifiedRanges(scan_begin, scan_end - scan_begin, m_bda_dirty_ranges);',
     'SynchronizeBuffersOfDirtyRanges();'),
    ('br_index', BC, 'const auto index = cursor / TRACKER_REGION_SIZE;', 'const auto bytes ='),
    ('br_bitskip', BC, 'if (bit_clear && m_bda_region_stamps[index].generation == m_bda_stamp_generation) {',
     'Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsBitSkipped, 1);'),
    ('br_stamp', BC, 'const auto stamp = m_memory_tracker.RegionWriteStamp(index);', 'auto&      seen  = m_bda_region_stamps[index];'),
    ('br_skip', BC, 'if (seen.generation == m_bda_stamp_generation && seen.stamp == stamp) {',
     'Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsSkipped, 1);'),
    ('br_store', BC, 'seen = {stamp, m_bda_stamp_generation};',
     'Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsScanned, 1);'),
    ('br_check', BC, 'if (m_bda_narrow_check) {', '// Session 113 (item 14): the dirty bits and the region stamp read under the same region lock. Knob 1 would'),
    ('br_collect', BC, 'm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);', '}'),
    ('mark_gen0', BC, 'm_bda_region_stamps[index].generation = 0; // never the current generation: the next pass walks it',
     'Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionInv, 1);'),
    ('reg_mark', BC, 'MarkBdaRegions(buffer.CpuAddress(), buffer.Size());', '} else {'),
    ('bh_stamps', BH, 'std::vector<BdaRegionStamp>                        m_bda_region_stamps;',
     'uint64_t                                           m_bda_stamp_generation = 1;'),
    ('rm_b13_epoch', RM, 'm_epoch.fetch_add(1, std::memory_order_release);', '#if defined(KYTY_TEST_B13_HOOK)'),
    ('rm_b13_bit', RM, 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);', '#if defined(KYTY_TEST_B13_HOOK)'),
    ('mt_collect', MT, 'manager->ForEachModifiedRange<DirtySource::Cpu, false>(cursor, bytes, append);', '}'),
    ('gate_bdastamp', GT, '{"KYTY_BDA_REGION_STAMPS", "bdastamp", true},', '{"KYTY_BACKING_PAGES", "backpages", true},'),
    ('gate_bdabits', GT, '{"KYTY_BDA_WRITE_BITS", "bdabits", false},', '{"KYTY_BDA_WRITE_BITS_VERIFY", "bdabitscheck", false},'),
    ('gate_bdanarrow', GT, '{"KYTY_BDA_NARROW_STAMPS", "bdanarrow", 0, 2},', '// Session 114: UpdateTitle posts the title'),
    ('km_mapgpu', KM, 'GetGpuResources().MapMemory(vaddr, size);', '}'),
    ('km_runtime_map', KM, 'MapGpuRange(vaddr, mapped_size);', 'return vaddr;'),
    ('st_covered', ST, 'const bool is_lost  = !Covered(cache.synced, address, page);',
     'const bool is_dirty = tracker.IsRegionCpuModified(address, page);'),
    ('st_skip', ST, 'if (seen.generation == stamp_generation && seen.stamp == stamp) {', 'skipped++;'),
]


def main(commit, out_path):
    cache = {}
    rows = []
    ok = True
    for name, path, a, b in REFS:
        if path not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
            cache[path] = r.stdout.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n')
        L = cache[path]
        hits = []
        for i in range(len(L) - 1):
            if L[i].strip() == a.strip() or (a.strip() in L[i].strip() and len(a.strip()) > 40):
                nxt = L[i + 1].strip()
                if (b.strip() == '' and nxt == '') or (b.strip() != '' and b.strip() in nxt):
                    hits.append(i + 1)
        if len(hits) != 1:
            ok = False
            print('FAIL %s %s: %d hits %s' % (name, path, len(hits), hits[:5]))
            continue
        rows.append('\t'.join([commit, path, str(hits[0]), a, b]))
        print('ok %s %s:%s:%d' % (name, commit, path, hits[0]))
    open(out_path, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('GEN %d of %d, %s' % (len(rows), len(REFS), 'ALL OK' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
