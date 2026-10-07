"""Track F link F24a (HPP-658): find the lines of the references of f24a.md by anchor text and write refs_f24a.tsv
(commit, path, line, anchor, +1 anchor = the stripped next line, cut to 60 characters). Each anchor must occur exactly
once in the file at that commit (or the given occurrence). ASCII code, UTF-8 data.

    python gen_refs_f24a.py
"""
import os
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RM = 'src/graphics/host_gpu/regionManager.h'
MT = 'src/graphics/host_gpu/memoryTracker.h'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
GA = 'src/common/gates.cpp'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
MC = 'src/graphics/host_gpu/memoryTracker.cpp'
RD = 'src/graphics/host_gpu/regionDefinitions.h'
RMAP = 'docs/ROADMAP.md'

# (name, commit, path, anchor, occurrence)
REFS = []
for c in ('707e0d7d', '0005e11f'):
    REFS += [
        ('b13_global_' + c, c, RM, 'm_cpu_epoch.fetch_add(1, std::memory_order_release);', 1),
        ('b13_comment_' + c, c, RM, 'HasCurrentUpload check fails. A BDA scan observing these epochs still acquires this', 1),
        ('b13_region_' + c, c, RM, 'm_epoch.fetch_add(1, std::memory_order_release);', 1),
        ('b13_note_' + c, c, RM, 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);', 1),
        ('b13_bit_' + c, c, RM, '// Gate "bdabits": the map mirrors this epoch, so it is set here and never later.', 1),
        ('b13_epoch_' + c, c, RM, 'return m_epoch.load(std::memory_order_acquire);', 1),
        ('b13_bits_first_' + c, c, RM, 'bits.SetRangeRelaxed(start, end);', 1),
        ('b13_cpuepoch_' + c, c, MT, 'return m_cpu_epoch.load(std::memory_order_acquire);', 1),
        ('b13_stamp_' + c, c, MT, 'const auto* manager = m_regions[index].load(std::memory_order_acquire);', 1),
        ('b13_inval_' + c, c, MT, 'manager->ChangeState<DirtySource::Cpu, true>(manager->GetCpuAddr() + offset, bytes);', 1),
        ('b13_fault_' + c, c, MT, 'manager->ChangeState<DirtySource::Cpu, true>(open_begin, open_size);', 1),
        ('b13_rc_epoch_' + c, c, RC, 'const auto cpu_epoch          = m_buffer_cache.CpuWriteEpoch();', 1),
        ('b13_rc_cached_' + c, c, RC, 'const bool bda_cached = reuse && cpu_epoch == m_bda_cpu_epoch &&', 1),
        ('b13_rc_store_' + c, c, RC, 'm_bda_cpu_epoch          = cpu_epoch;', 1),
        ('b13_bc_bit_' + c, c, BC, 'const bool bit_clear = use_bits && !BdaTakeRegionWrite(index);', 1),
        ('b13_bc_stamp_' + c, c, BC, 'const auto stamp = m_memory_tracker.RegionWriteStamp(index);', 1),
        ('b13_bc_skip_' + c, c, BC, 'if (seen.generation == m_bda_stamp_generation && seen.stamp == stamp) {', 1),
        ('b13_bc_collect_' + c, c, BC, 'm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);', 1),
        ('b13_bc_gate_' + c, c, BC, 'if (Common::Gates::Enabled(Common::Gates::Gate::BdaRegionStamps)) {', 1),
        ('b13_gate_stamp_' + c, c, GA, '{"KYTY_BDA_REGION_STAMPS", "bdastamp", true},', 1),
        ('b13_gate_bits_' + c, c, GA, '{"KYTY_BDA_WRITE_BITS", "bdabits", false},', 1),
        ('b13_collect_lock_' + c, c, MC, 'manager->ForEachModifiedRange<DirtySource::Cpu, false>(cursor, bytes, append);', 1),
        ('b27_guard_' + c, c, PC, 'static void GuardSlot(AheadSlot& slot) {', 1),
        ('b27_yield_' + c, c, PC, 'Common::FrameStats::Add(Common::FrameStats::Counter::DaGuardYield, 1);', 1),
        ('b27_vec_' + c, c, PC, 'std::vector<std::thread>              ahead_threads; // ahead_queue_mutex (AheadStartThreads) / shutdown', 1),
        ('b27_count_' + c, c, PC, 'std::atomic<uint32_t>                 ahead_thread_count {0};', 1),
        ('b27_start_' + c, c, PC, 'void AheadStartThreads(uint32_t wanted) {', 1),
        ('b27_stop_' + c, c, PC, 'void AheadStopThreads() {', 1),
        ('b27_qlock_' + c, c, PC, 'queue_lock(ahead_queue_mutex);', 1),
        ('b27_startcall_' + c, c, PC, 'AheadStartThreads(wanted);', 1),
        ('b27_notify_' + c, c, PC, 'if (ahead_threads.size() > wanted) {', 1),
        ('b27_wake_' + c, c, PC, 'wake_all = ahead_thread_count.load(std::memory_order_relaxed) >', 1),
        ('b27_dtor_' + c, c, PC, 'AheadStopThreads();', 1),
        ('b27_take_' + c, c, PC, 'if (!TryGuardSlot(slot)) {', 1),
        ('b27_taking_' + c, c, PC, 'slot.state.store(AheadTaking, std::memory_order_relaxed);', 1),
        ('b27_run_' + c, c, PC, 'if (!slot.state.compare_exchange_strong(expected, AheadRunning, std::memory_order_acq_rel)) {', 1),
        ('b27_gate_' + c, c, GA, '{"KYTY_DRAW_AHEAD_SLOT", "daslot", 1, 2},', 1),
    ]
REFS += [
    ('row_b13', '00c7264b', RMAP, '| \u043f\u043e\u0440\u044f\u0434\u043e\u043a \u044d\u043f\u043e\u0445 \u0432 `ChangeState<Cpu,true>`', 1),
    ('row_b27', '00c7264b', RMAP, '| \u0434\u043e\u043b\u0433\u0438 \u043a\u043e\u0434\u0430 `daslot`:', 1),
    ('hook_decl', '1570d110', RM, 'void Hook(int point) noexcept;', 1),
    ('hook_1', '1570d110', RM, 'B13Test::Hook(1); // Track F, F24a: between the global and the region epoch', 1),
    ('hook_swap', '1570d110', RM, '#if defined(KYTY_TEST_B13_SWAP)', 1),
    ('hook_2', '1570d110', RM, 'B13Test::Hook(2); // Track F, F24a: after both epochs, before the bdabits bit', 1),
    ('stand_prepare', '1570d110', 'tests/B13EpochStand.cpp', 'Outcome Prepare(Decided&& on_decided) {', 1),
    ('stand_verbatim', '1570d110', 'tests/B27DaSlotStand.cpp', '// BEGIN VERBATIM pipelineCache.cpp', 1),
    ('b27_commit_guard', '0ddca1ee', PC, 'Common::FrameStats::Add(Common::FrameStats::Counter::DaGuardYield, 1);', 1),
    ('b27_commit_count', '0ddca1ee', PC, 'std::atomic<uint32_t>                 ahead_thread_count {0};', 1),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cache = {}
    rows = []
    for name, c, p, anchor, occ in REFS:
        if (c, p) not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True)
            cache[(c, p)] = r.stdout.decode('utf-8').split('\n')
        lines = cache[(c, p)]
        hits = [i for i, l in enumerate(lines) if anchor in l]
        if len(hits) < occ:
            sys.exit('%s: anchor hits %d < %d: %s %s' % (name, len(hits), occ, c, p))
        i = hits[occ - 1]
        nxt = lines[i + 1].strip()[:60]
        rows.append('\t'.join([c, p, str(i + 1), anchor.strip()[:80], nxt]))
        print('%-22s `%s:%s:%d`  hits=%d  +1=%s' % (name, c, p, i + 1, len(hits), nxt))
    open(os.path.join(here, 'refs_f24a.tsv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')


main()
