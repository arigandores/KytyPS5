"""F29c (HPP-702): the '<commit>:<path>:<line>' references of f29c.md, found by whole anchors (the line holds the anchor,
the next line holds the +1 anchor; the pair must be unique). Writes refs_f29c.tsv (commit, path, line, anchor, +1 anchor)
for refs_f29c.py and prints 'name commit:path:line'. Copy of the F29a gen_refs_f29a.py with the anchors of F29c. ASCII.

    python gen_refs_f29c.py <commit> <out.tsv>
"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
BH = 'src/graphics/host_gpu/renderer/cache/bufferCache.h'
RM = 'src/graphics/host_gpu/regionManager.h'
GR = 'src/graphics/guest_gpu/graphicsRun.cpp'
RCO = 'src/graphics/host_gpu/renderer/renderCompute.cpp'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
DS = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
FS = 'src/common/frameStats.h'
VO = 'src/graphics/presentation/videoOut.cpp'
ST = 'tests/B12BdaStampStand.cpp'
BS = chr(92)
REFS = [
    ('rc_fix', RC, 'const bool fix_b12 = FixB12Enabled();', 'if (fix_b12) {'),
    ('rc_begin', RC, 'm_buffer_cache.BeginBdaPass();', '}'),
    ('rc_foreach', RC, 'm_mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {',
     'm_buffer_cache.SynchronizeBuffersInRange(start, end - start);'),
    ('rc_end', RC, 'm_buffer_cache.EndBdaPass();', '}'),
    ('rc_cached', RC, 'if (bda_cached) {', '// Session 83: how many of the 181 calls a frame never scan at all.'),
    ('bc_begin', BC, 'void BufferCache::BeginBdaPass() noexcept {', 'm_bda_pass++;'),
    ('bc_endfn', BC, 'void BufferCache::EndBdaPass() {', 'm_bda_pass_open = false;'),
    ('bc_stat', BC, 'LOGF("FixB12Stat: passes=%llu rewalk=%llu rwd=%llu' + BS + 'n", static_cast<unsigned long long>(m_bda_pass),',
     'static_cast<unsigned long long>(m_b12_rewalk), static_cast<unsigned long long>(m_b12_rwd));'),
    ('bc_mode', BC, 'LOGF("FixB12: mode=%d' + BS + 'n", fix_b12 ? 1 : 0);', '}'),
    ('bc_b12pass', BC, 'const bool b12_pass = m_bda_pass_open;', 'for (auto cursor = scan_begin; cursor < scan_end;) {'),
    ('bc_revisit', BC, 'if (b12_pass && m_bda_region_stamps[index].walked_pass == m_bda_pass) {',
     'm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);'),
    ('bc_rwd', BC, 'if (DirtyRangesTouchBuffers()) {', 'm_b12_rwd++;'),
    ('bc_revisit_sync', BC, 'SynchronizeBuffersOfDirtyRanges();', 'cursor += bytes;'),
    ('bc_bit', BC, 'const bool bit_clear = use_bits && !BdaTakeRegionWrite(index);',
     'if (bit_clear && m_bda_region_stamps[index].generation == m_bda_stamp_generation) {'),
    ('bc_store', BC, 'seen = {stamp, m_bda_stamp_generation};', 'if (b12_pass) {'),
    ('bc_walked', BC, 'seen.walked_pass = m_bda_pass;', '}'),
    ('bc_mark', BC, 'm_bda_region_stamps[index].generation = 0; // never the current generation: the next pass walks it',
     'Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionInv, 1);'),
    ('bc_batched', BC, 'SynchronizeBuffersOfDirtyRangesBatched(pass);', 'return;'),
    ('bc_reentrant', BC, 'EXIT("BufferCache: reentrant dirty-range pass' + BS + 'n");', '}'),
    ('bh_walked', BH, 'uint64_t                   walked_pass = 0;', '};'),
    ('bh_pass', BH, 'uint64_t                                           m_bda_pass      = 0;',
     'bool                                               m_bda_pass_open = false;'),
    ('rm_fix', RM, '[[nodiscard]] inline bool FixB12Enabled() noexcept {',
     'static const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_B12"));'),
    ('gr_lock', GR, 'Common::LockGuard lock(renderer.GetMutex());', 'renderer.PrepareBda();'),
    ('rco_lock', RCO, 'Common::LockGuard            lock(m_context.GetMutex());', None),
    ('rco_call', RCO, 'm_context.PrepareBda();', None),
    ('rco_fn', RCO, 'void RenderExecutor::DispatchDirect(uint64_t submit_id, CommandBuffer& buffer,', None),
    ('rd_drawindex', RD, 'void RenderExecutor::DrawIndex(uint64_t submit_id, CommandBuffer& buffer,', None),
    ('ds_call', DS, 'm_context.PrepareBda();', 'if (rb_chain) {'),
    ('rd_ped', RD, 'PrepareGraphicsBindings(stages, std::span {state.color_info, state.color_count});', None),
    ('fs_rewalk', FS, 'BdaB12Rewalk,            // bda_b12_rewalk', 'BdaB12Rwd,               // bda_b12_rwd'),
    ('vo_rewalk', VO, '{"bda_b12_rewalk", FS::Counter::BdaB12Rewalk, false},', '{"bda_b12_rwd", FS::Counter::BdaB12Rwd, false},'),
    ('st_revisit', ST, 'if (b12_pass && region_stamps[index].walked_pass == bda_pass) {',
     'tracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);'),
    ('st_walked', ST, 'seen.walked_pass = bda_pass;', '}'),
    ('st_begin', ST, 'cache.BeginBdaPass();', '}'),
    ('st_end', ST, 'cache.EndBdaPass();', '}'),
    ('st_hook', ST, 'if (hook != nullptr) { // stand-only: between the first and the second range', 'auto* fire = hook;'),
]


def main(argv):
    commit, out = argv[0], argv[1]
    cache = {}
    rows = []
    ok = True
    for name, path, a, b in REFS:
        if path not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True)
            cache[path] = r.stdout.decode('utf-8', 'replace').split('\n')
        lines = cache[path]
        hits = []
        for i in range(len(lines) - 1):
            if a in lines[i].strip() and (b is None or b in lines[i + 1].strip()):
                hits.append(i + 1)
        if len(hits) != 1:
            ok = False
            print('FAIL %s %s hits %s' % (name, path, hits))
            continue
        ln = hits[0]
        nxt = lines[ln].strip() if b is None else b
        rows.append('%s\t%s\t%d\t%s\t%s' % (commit, path, ln, a, nxt))
        print('%s `%s:%s:%d`' % (name, commit, path, ln))
    open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('GEN %d of %d, %s' % (len(rows), len(REFS), 'ALL OK' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
