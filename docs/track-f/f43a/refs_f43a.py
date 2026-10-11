# F43a (HPP-783): map of the report links <commit>:<path>:<line> - every link has an anchor (substring of the line) and a
# +1 control (start of the next line). build: resolve lines from anchors (first match after the 'after' anchor, if any)
# and write refs_f43a.tsv; check: re-read every link from git and compare; text: every link of the report is in the table.
# Code: KytyPS5 FS12 730ed40a. Form of refs_f41a.py (F41a, HPP-774).
# Usage: python refs_f43a.py build <out.tsv> | check <refs.tsv> | text <report.md> <refs.tsv>
import os, re, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
ROOT = 'C:/kyty/KytyPS5'
EMU = '730ed40a'
CO = 'src/graphics/host_gpu/shaders/fault_buffer_process.comp'
CM = 'CMakeLists.txt'
FM = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
FMH = 'src/graphics/host_gpu/renderer/cache/faultManager.h'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
BH = 'src/graphics/host_gpu/renderer/cache/bufferCache.h'
RD = 'src/graphics/host_gpu/regionDefinitions.h'
RS = 'src/graphics/host_gpu/rangeSet.h'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
GR = 'src/graphics/guest_gpu/graphicsRun.cpp'
SBH = 'src/graphics/host_gpu/renderer/cache/streamBuffer.h'
SB = 'src/graphics/host_gpu/renderer/cache/streamBuffer.cpp'
M = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp'
PR = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp'
SC = 'src/graphics/host_gpu/renderer/commandScheduler.cpp'
TS = 'tests/ShaderRecompilerComputeTests.cpp'
# key, commit, path, anchor, after-anchor (or '')
REFS = [
    ('co_word', EMU, CO, 'uint word = fault_buffer[id];', ''),
    ('co_zero', EMU, CO, 'fault_buffer[id] = 0u;', ''),
    ('co_add', EMU, CO, 'const uint store_index = atomicAdd(download_buffer32[0], 1u) + 1u;', ''),
    ('co_cmp', EMU, CO, 'if (store_index >= MAX_PAGE_FAULTS) {', ''),
    ('co_ret', EMU, CO, 'return;', 'if (store_index >= MAX_PAGE_FAULTS) {'),
    ('co_store', EMU, CO, 'download_buffer[store_index] = uint64_t(page) << CACHING_PAGEBITS;', ''),
    ('co_b32', EMU, CO, 'uint download_buffer32[];', ''),
    ('cm_max', EMU, CM, '-DCACHING_PAGEBITS=14 -DMAX_PAGE_FAULTS=1024', ''),
    ('fm_max', EMU, FM, 'constexpr size_t MaxPageFaults    = 1024;', ''),
    ('fm_area', EMU, FM, 'constexpr size_t PageFaultAreaSize = MaxPageFaults * sizeof(uint64_t);', ''),
    ('fm_dl', EMU, FM, 'MaxPendingFaults * PageFaultAreaSize),', ''),
    ('fm_proc', EMU, FM, 'void FaultManager::ProcessFaultBuffer() {', ''),
    ('fm_wait', EMU, FM, 'm_scheduler.Wait(wait_tick);', 'void FaultManager::ProcessFaultBuffer() {'),
    ('fm_off', EMU, FM, 'const auto offset = m_current_area * PageFaultAreaSize;', ''),
    ('fm_memset', EMU, FM, 'std::memset(mapped, 0, PageFaultAreaSize);', ''),
    ('fm_info', EMU, FM, '{m_download_buffer.Handle(), offset, PageFaultAreaSize},', ''),
    ('fm_disp', EMU, FM, 'command.dispatch(static_cast<uint32_t>(num_workgroups), 1, 1);', 'void FaultManager::ProcessFaultBuffer() {'),
    ('fm_defer', EMU, FM, 'm_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset] {', ''),
    ('fm_inv', EMU, FM, 'm_download_buffer.Invalidate(offset, PageFaultAreaSize);', ''),
    ('fm_count', EMU, FM, 'const auto  count  = static_cast<uint32_t>(faults[0]);', ''),
    ('fm_loop', EMU, FM, 'for (uint32_t index = 1; index <= count; ++index) {', ''),
    ('fm_add', EMU, FM, 'fault_ranges.Add(faults[index], BufferCache::CACHING_PAGESIZE);', ''),
    ('fm_log', EMU, FM, 'LOGF("Accessed non-GPU cached memory at 0x%016" PRIx64 "\\n", faults[index]);', ''),
    ('fm_exit32', EMU, FM, 'EXIT_IF(end - start > std::numeric_limits<uint32_t>::max());', ''),
    ('fm_find', EMU, FM, '(void)m_buffer_cache.FindBuffer(start, end - start);', ''),
    ('fm_next', EMU, FM, 'm_fault_areas[m_current_area++] = m_scheduler.CurrentTick();', ''),
    ('fm_mod', EMU, FM, 'm_current_area %= MaxPendingFaults;', ''),
    ('fmh_pend', EMU, FMH, 'static constexpr size_t MaxPendingFaults = 8;', ''),
    ('bc_find', EMU, BC, 'BufferId BufferCache::FindBuffer(uint64_t vaddr, uint64_t size) {', ''),
    ('bc_zero', EMU, BC, 'if (vaddr == 0) {', 'BufferId BufferCache::FindBuffer('),
    ('bc_inval', EMU, BC, 'EXIT("BufferCache: invalid buffer discovery request\\n");', ''),
    ('bc_create', EMU, BC, 'return CreateBuffer(vaddr, size);', 'BufferId BufferCache::FindBuffer('),
    ('bc_down', EMU, BC, 'vaddr = Common::AlignDown(vaddr, CACHING_PAGESIZE);', 'BufferId BufferCache::CreateBuffer('),
    ('bc_reg', EMU, BC, 'Register(id);', 'BufferId BufferCache::CreateBuffer('),
    ('bc_pt', EMU, BC, 'm_page_table[page] = id;', 'void BufferCache::ChangeRegister(BufferId id) {'),
    ('bc_null', EMU, BC, '// Null-page BDA mode (shader emitter): page-table entry 0 (guest page 0, never', ''),
    ('bc_ptw', EMU, BC, 'WriteDataBuffer(m_bda_pagetable_buffer, pages.first * sizeof(vk::DeviceAddress),', ''),
    ('bh_bits', EMU, BH, 'static constexpr uint32_t CACHING_PAGEBITS  = 14;', ''),
    ('bh_num', EMU, BH, 'static constexpr uint64_t CACHING_NUMPAGES  = uint64_t {1} << (40 - CACHING_PAGEBITS);', ''),
    ('rd_valid', EMU, RD, 'return address != 0 && size != 0 && address < TRACKER_ADDRESS_SIZE &&', ''),
    ('rs_exit', EMU, RS, 'EXIT("invalid range-set address or size\\n");', ''),
    ('rc_pend', EMU, RC, 'm_fault_process_pending       = true;', ''),
    ('rc_gc', EMU, RC, 'if (m_fault_process_pending) {', 'void RenderContext::RunGarbageCollector() {'),
    ('rc_proc', EMU, RC, 'm_buffer_cache.ProcessFaultBuffer();', 'void RenderContext::RunGarbageCollector() {'),
    ('gr_gc1', EMU, GR, 'm_renderer.RunGarbageCollector();', ''),
    ('gr_flip', EMU, GR, 'case SubmissionType::FlipPreparation:', ''),
    ('sbh_all', EMU, SBH, 'inline constexpr vk::BufferUsageFlags AllFlags =', ''),
    ('sbh_all2', EMU, SBH, 'ReadFlags | vk::BufferUsageFlagBits::eTransferDst | vk::BufferUsageFlagBits::eStorageBuffer;', ''),
    ('sb_ded', EMU, SB, 'with_bda && size >= dedicated_min_kb * 1024u ? VMA_ALLOCATION_CREATE_DEDICATED_MEMORY_BIT', ''),
    ('m_null', EMU, M, 'const char* value = std::getenv("KYTY_BDA_NULLPAGE");', ''),
    ('m_flush', EMU, M, 'void EmitBdaFaultFlush(EmitterState& state) {', ''),
    ('m_sel0', EMU, M, 'ConstantU32(state, 0));', 'uint32_t in_table = 0;'),
    ('m_remember', EMU, M, 'Binary(state, OpLogicalAnd, TypeBool(state), missing, active),', ''),
    ('m_lean', EMU, M, '// KYTY_BDA_LEAN: no fault store in pixel shaders (a miss reads the null page silently).', ''),
    ('pr_flush', EMU, PR, 'EmitBdaFaultFlush(', ''),
    ('sc_fifo', EMU, SC, '!m_master.IsFree(m_pending_operations.front().tick)) {', ''),
    ('ts_fill', EMU, TS, 'cmd.fillBuffer(m_fault_buffer.buffer, 0, m_fault_buffer.size, 0);', ''),
]


def show(commit, path):
    r = subprocess.run(['git', '-C', ROOT, 'show', commit + ':' + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('git show failed ' + commit + ' ' + path)
    return r.stdout.decode('utf-8', 'replace').replace(chr(13), '').split(chr(10))


def resolve(lines, anchor, after):
    start = 0
    if after:
        hits = [i for i, l in enumerate(lines) if after in l]
        if not hits:
            return None
        start = hits[0]
    for i in range(start, len(lines)):
        if anchor in lines[i]:
            return i + 1
    return None


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    mode, path = sys.argv[1], sys.argv[2]
    cache = {}
    if mode == 'build':
        rows = []
        for key, c, p, anchor, after in REFS:
            lines = cache.setdefault((c, p), show(c, p))
            n = resolve(lines, anchor, after)
            if n is None:
                print('NOT FOUND', key)
                sys.exit(1)
            plus1 = lines[n].strip()[:40] if n < len(lines) else ''
            rows.append((key, c, p, str(n), anchor, plus1))
            print(key, c + ':' + p + ':' + str(n))
        with open(path, 'w', encoding='utf-8', newline=chr(10)) as o:
            for r in rows:
                o.write(chr(9).join(r) + chr(10))
        print('rows', len(rows))
        return
    if mode == 'text':
        table = set()
        for l in open(sys.argv[3], encoding='utf-8'):
            if l.strip():
                k, c, p, n = l.split(chr(9))[:4]
                table.add((c, p, n))
        text = open(path, encoding='utf-8').read()
        rx = re.compile(r'`(?:(' + EMU + r'):([^`:]+):|:)(\d+)`')
        last, seen, miss = None, 0, 0
        for m in rx.finditer(text):
            if m.group(1):
                last = (m.group(1), m.group(2))
            if last is None:
                continue
            seen += 1
            if (last[0], last[1], m.group(3)) not in table:
                miss += 1
                print('MISSING', last[0] + ':' + last[1] + ':' + m.group(3))
        print('text links', seen, 'missing', miss)
        print('ALL OK' if miss == 0 and seen > 0 else 'FAIL')
        return
    bad = 0
    n_rows = 0
    for l in open(path, encoding='utf-8'):
        if not l.strip():
            continue
        n_rows += 1
        key, c, p, n, anchor, plus1 = l.rstrip(chr(10)).split(chr(9))
        lines = cache.setdefault((c, p), show(c, p))
        i = int(n)
        ok = i <= len(lines) and anchor in lines[i - 1] and (i >= len(lines) or lines[i].strip()[:40] == plus1)
        if not ok:
            bad += 1
            print('BAD', key, c + ':' + p + ':' + n)
    print('links', n_rows, 'bad', bad)
    print('ALL OK' if bad == 0 and n_rows > 0 else 'FAIL')


main()
