# F44a (HPP-791): map of the report links <commit>:<path>:<line> - every link has an anchor (substring of the line) and a
# +1 control (start of the next line). build: resolve lines from anchors (first match after the 'after' anchor, if any)
# and write refs_f44a.tsv; check: re-read every link from git and compare; text: every link of the report is in the table.
# Code: KytyPS5 FS12 730ed40a (section 0) and the F44a commits (later sections, added to REFS with their commit).
# Form of refs_f43a.py (F43a, HPP-783).
# Usage: python refs_f44a.py build <out.tsv> | check <refs.tsv> | text <report.md> <refs.tsv>
import os, re, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
ROOT = 'C:/kyty/KytyPS5'
EMU = '730ed40a'
COMMITS = [EMU]
CO = 'src/graphics/host_gpu/shaders/fault_buffer_process.comp'
CM = 'CMakeLists.txt'
FM = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
FMH = 'src/graphics/host_gpu/renderer/cache/faultManager.h'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
BH = 'src/graphics/host_gpu/renderer/cache/bufferCache.h'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
# key, commit, path, anchor, after-anchor (or '')
REFS = [
    ('co_add', EMU, CO, 'const uint store_index = atomicAdd(download_buffer32[0], 1u) + 1u;', ''),
    ('co_cmp', EMU, CO, 'if (store_index >= MAX_PAGE_FAULTS) {', ''),
    ('cm_incl', EMU, CM, '${PROJECT_BINARY_DIR}', 'include_directories('),
    ('cm_gen', EMU, CM, 'set(gpu_tiler_generated_dir "${PROJECT_BINARY_DIR}/gpu_tiler_shaders")', ''),
    ('cm_hdr', EMU, CM, 'set(fault_buffer_shader_header "${gpu_tiler_generated_dir}/fault_buffer_process_spv.h")', ''),
    ('cm_max', EMU, CM, '-DCACHING_PAGEBITS=14 -DMAX_PAGE_FAULTS=1024', ''),
    ('cm_sym', EMU, CM, '-DSYMBOL=FAULT_BUFFER_PROCESS_SPV -P "${KYTY_SOURCE_DIR}/embed_spirv.cmake"', ''),
    ('cm_src', EMU, CM, 'list(APPEND kyty_emulator_src "${fault_buffer_shader_header}")', ''),
    ('cm_fn', EMU, CM, 'function(add_kyty_full_emulator_test target source)', ''),
    ('cm_exe', EMU, CM, 'add_executable(${target} EXCLUDE_FROM_ALL ${source} ${kyty_emulator_src})', ''),
    ('cm_inc', EMU, CM, 'target_include_directories(${target} PRIVATE ${inc_headers})', 'function(add_kyty_full_emulator_test'),
    ('cm_b4', EMU, CM, 'add_kyty_full_emulator_test(b4_race_stand', ''),
    ('cm_extra', EMU, CM, '-D SHADER_CACHE_EXTRA_FILES=', ''),
    ('fm_inc', EMU, FM, '#include "gpu_tiler_shaders/fault_buffer_process_spv.h"', ''),
    ('fm_max', EMU, FM, 'constexpr size_t MaxPageFaults    = 1024;', ''),
    ('fm_ctor', EMU, FM, 'FaultManager::FaultManager(GraphicContext& graphics, CommandScheduler& scheduler,', ''),
    ('fm_dl', EMU, FM, 'm_download_buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,', ''),
    ('fm_bvhlog', EMU, FM, 'LOGF("BvhLoopCap: cap=%u token=', ''),
    ('fm_spv', EMU, FM, 'const auto module = CompileSPV(FAULT_BUFFER_PROCESS_SPV, m_graphics.device);', ''),
    ('fm_proc', EMU, FM, 'void FaultManager::ProcessFaultBuffer() {', ''),
    ('fm_mapped', EMU, FM, 'auto*      mapped = m_download_buffer.Mapped().data() + offset;', ''),
    ('fm_memset', EMU, FM, 'std::memset(mapped, 0, PageFaultAreaSize);', ''),
    ('fm_flush', EMU, FM, 'm_download_buffer.Flush(offset, PageFaultAreaSize);', ''),
    ('fm_info', EMU, FM, '{m_download_buffer.Handle(), offset, PageFaultAreaSize},', ''),
    ('fm_tripinv', EMU, FM, 'm_trip_download.Invalidate(trip_offset, LoopTripBytes);', ''),
    ('fm_tripcpy', EMU, FM, 'std::memcpy(words.data(), m_trip_download.Mapped().data() + trip_offset,', ''),
    ('fm_inv', EMU, FM, 'm_download_buffer.Invalidate(offset, PageFaultAreaSize);', ''),
    ('fm_cast', EMU, FM, 'const auto* faults = std::bit_cast<const uint64_t*>(mapped);', ''),
    ('fm_count', EMU, FM, 'const auto  count  = static_cast<uint32_t>(faults[0]);', ''),
    ('fm_loop', EMU, FM, 'for (uint32_t index = 1; index <= count; ++index) {', ''),
    ('fm_add', EMU, FM, 'fault_ranges.Add(faults[index], BufferCache::CACHING_PAGESIZE);', ''),
    ('fm_log', EMU, FM, 'LOGF("Accessed non-GPU cached memory at 0x%016" PRIx64 "\\n", faults[index]);', ''),
    ('fm_find', EMU, FM, '(void)m_buffer_cache.FindBuffer(start, end - start);', ''),
    ('fmh_pend', EMU, FMH, 'static constexpr size_t MaxPendingFaults = 8;', ''),
    ('fmh_dl', EMU, FMH, 'Buffer                                     m_download_buffer;', ''),
    ('fmh_trip', EMU, FMH, 'Buffer                                     m_trip_download;', ''),
    ('bh_fm', EMU, BH, 'FaultManager                                      m_fault_manager;', ''),
    ('bc_ctor', EMU, BC, 'm_fault_manager(graphics, scheduler, *this),', ''),
    ('bc_proc', EMU, BC, 'm_fault_manager.ProcessFaultBuffer();', ''),
    ('rc_proc', EMU, RC, 'm_buffer_cache.ProcessFaultBuffer();', 'void RenderContext::RunGarbageCollector() {'),
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
        rx = re.compile(r'`(?:(' + '|'.join(COMMITS) + r'):([^`:]+):|:)(\d+)`')
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
