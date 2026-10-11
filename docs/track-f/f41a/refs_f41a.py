# F41a (HPP-774): map of the report links <commit>:<path>:<line> - every link has an anchor (substring of the line) and a
# +1 control (start of the next line). build: resolve lines from anchors (first match after the 'after' anchor, if any)
# and write refs_f41a.tsv; check: re-read every link from git and compare; text: every link of the report is in the table.
# Code: KytyPS5 FS12 730ed40a; data of F12g: KytyPS5 5842bf43 (docs/track-f/f12g, unchanged since F12g).
# Usage: python refs_f41a.py build <out.tsv> | check <refs.tsv> | text <report.md> <refs.tsv>
import os, re, subprocess, sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
ROOT = 'C:/kyty/KytyPS5'
EMU = '730ed40a'
DOC = '5842bf43'
M = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp'
PR = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp'
FM = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
FMH = 'src/graphics/host_gpu/renderer/cache/faultManager.h'
CO = 'src/graphics/host_gpu/shaders/fault_buffer_process.comp'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
BH = 'src/graphics/host_gpu/renderer/cache/bufferCache.h'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
TC = 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
SH = 'src/graphics/host_gpu/renderer/pipeline/shaders.cpp'
GV = 'src/generate_version.cmake'
CM = 'CMakeLists.txt'
TS = 'tests/ShaderRecompilerComputeTests.cpp'
B138 = 'docs/track-f/f12g/rd_f12g_b138.txt'
K03 = 'docs/track-f/f12g/rd_f12g_k03.txt'
# key, commit, path, anchor, after-anchor (or '')
REFS = [
    ('m_record', EMU, M, 'void RecordBdaFault(EmitterState& state, uint32_t page) {', ''),
    ('m_word', EMU, M, 'Binary(state, spv::OpShiftRightLogical, TypeU32(state), page, ConstantU32(state, 5));', 'void RecordBdaFault('),
    ('m_load', EMU, M, 'state.builder.AddFunction(spv::OpLoad, TypeU32(state), value, pointer);', 'void RecordBdaFault('),
    ('m_store', EMU, M, 'state.builder.AddFunction(spv::OpStore, pointer,', 'void RecordBdaFault('),
    ('m_or', EMU, M, 'Binary(state, spv::OpBitwiseOr, TypeU32(state), value, bit));', 'void RecordBdaFault('),
    ('m_chain', EMU, M, 'uint32_t FaultElementPointer(EmitterState& state, uint32_t index) {', ''),
    ('m_nullpage_env', EMU, M, 'const char* value = std::getenv("KYTY_BDA_NULLPAGE");', ''),
    ('m_lean', EMU, M, 'static const bool enabled = Common::EnvFlagOn("KYTY_BDA_LEAN") && BdaNullPageEnabled();', ''),
    ('m_flush', EMU, M, 'void EmitBdaFaultFlush(EmitterState& state) {', ''),
    ('m_flush_call', EMU, M, 'EmitIfCondition(state, faulted, [&]() { RecordBdaFault(state, page); });', ''),
    ('m_atomic_tail', EMU, M, 'void AtomicTailU32(EmitterState& state, spv::Op op, uint32_t word, uint32_t value) {', ''),
    ('m_atomic_scope', EMU, M, 'ConstantU32(state, spv::ScopeDevice),', 'void AtomicTailU32('),
    ('m_track', EMU, M, 'const bool track_faults = !lean || state.program.stage != ShaderType::Pixel;', ''),
    ('m_page_sel', EMU, M, 'const auto page = Select(state, TypeU32(state), in_table,', 'void DefineGetBdaPointerNullPage('),
    ('m_null_base', EMU, M, 'const auto base = Select(state, type, missing, null_base, loaded);', ''),
    ('m_remember', EMU, M, 'const auto remembered = Select(state, TypeU32(state),', ''),
    ('m_remember_store', EMU, M, 'state.builder.AddFunction(OpStore, state.bda_fault_page_variable, remembered);', ''),
    ('m_legacy_def', EMU, M, 'void DefineGetBdaPointer(EmitterState& state) {', ''),
    ('m_legacy_call', EMU, M, 'RecordBdaFault(state, page);', 'EmitLabel(state, fault_label);'),
    ('p_return_tail', EMU, PR, 'EmitBdaFaultFlush(ctx.state);', 'void EmitReturnTail('),
    ('fm_maxfaults', EMU, FM, 'constexpr size_t MaxPageFaults    = 1024;', ''),
    ('fm_size', EMU, FM, 'LoopTripOffset + LoopTripBytes),', ''),
    ('fm_process', EMU, FM, 'void FaultManager::ProcessFaultBuffer() {', ''),
    ('fm_wait', EMU, FM, 'm_scheduler.Wait(wait_tick);', 'void FaultManager::ProcessFaultBuffer() {'),
    ('fm_dispatch', EMU, FM, 'command.dispatch(static_cast<uint32_t>(num_workgroups), 1, 1);', ''),
    ('fm_defer', EMU, FM, 'm_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset] {', ''),
    ('fm_log', EMU, FM, 'LOGF("Accessed non-GPU cached memory at 0x%016" PRIx64 "', ''),
    ('fm_find', EMU, FM, '(void)m_buffer_cache.FindBuffer(start, end - start);', ''),
    ('fmh_pending', EMU, FMH, 'static constexpr size_t MaxPendingFaults = 8;', ''),
    ('co_load', EMU, CO, 'uint word = fault_buffer[id];', ''),
    ('co_clear', EMU, CO, 'fault_buffer[id] = 0u;', ''),
    ('co_cap', EMU, CO, 'if (store_index >= MAX_PAGE_FAULTS) {', ''),
    ('rc_arm', EMU, RC, 'm_fault_process_pending       = true;', ''),
    ('rc_gc', EMU, RC, 'void RenderContext::RunGarbageCollector() {', ''),
    ('rc_gc_call', EMU, RC, 'm_buffer_cache.ProcessFaultBuffer();', 'void RenderContext::RunGarbageCollector() {'),
    ('bh_pagebits', EMU, BH, 'static constexpr uint32_t CACHING_PAGEBITS  = 14;', ''),
    ('bh_numpages', EMU, BH, 'static constexpr uint64_t CACHING_NUMPAGES  = uint64_t {1} << (40 - CACHING_PAGEBITS);', ''),
    ('bc_findbuffer', EMU, BC, 'BufferId BufferCache::FindBuffer(uint64_t vaddr, uint64_t size) {', ''),
    ('bc_create', EMU, BC, 'return CreateBuffer(vaddr, size);', 'BufferId BufferCache::FindBuffer('),
    ('bc_pt_write', EMU, BC, 'WriteDataBuffer(m_bda_pagetable_buffer, pages.first * sizeof(vk::DeviceAddress),', ''),
    ('tc_variant', EMU, TC, 'const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +', ''),
    ('tc_fixf19', EMU, TC, '(ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "");', ''),
    ('tc_folder', EMU, TC, 'std::string folder = "variant" + variant;', ''),
    ('tc_signature', EMU, TC, 'm_signature = std::string("KytySC") + std::to_string(FORMAT_VERSION) + ":" +', ''),
    ('gv_hash', EMU, GV, 'set(KYTY_SHADER_SOURCE_HASH "unknown")', ''),
    ('gv_glob', EMU, GV, '"${SHADER_SOURCE_DIR}/*.cpp" "${SHADER_SOURCE_DIR}/*.h" "${SHADER_SOURCE_DIR}/*.inc")', ''),
    ('cm_dir', EMU, CM, '-D SHADER_SOURCE_DIR=${KYTY_SOURCE_DIR}/graphics/shader', ''),
    ('cm_extra', EMU, CM, '-D SHADER_CACHE_EXTRA_FILES=', ''),
    ('pc_cached_module', EMU, PC, 'vk::ShaderModule CreateCachedModule(vk::Device device, const std::vector<uint32_t>& source) {', ''),
    ('pc_salt', EMU, PC, 'if (const char* salt = std::getenv("KYTY_PIPELINE_SALT"); salt != nullptr && salt[0] != 0) {', ''),
    ('pc_compile', EMU, PC, 'return CompileSPV(*words, device);', 'vk::ShaderModule CreateCachedModule('),
    ('pc_seed', EMU, PC, 'InstallShaderSeed();', 'void PipelineCache::StartPrecache() {'),
    ('pc_rebuild_skip', EMU, PC, 'skip = "recipes_current";', ''),
    ('sh_compile', EMU, SH, 'const auto module = CompileSPV(words, graphics.device);', ''),
    ('ts_bind', EMU, TS, '"BDA page table and fault buffer must be bound together");', ''),
    ('ts_fill', EMU, TS, 'cmd.fillBuffer(m_fault_buffer.buffer, 0, m_fault_buffer.size, 0);', ''),
    ('d_b138_pre', DOC, B138, 'eid 128281 pre ([], 8388672)', ''),
    ('d_b138_o1', DOC, B138, 'eid 128281 orig 1 ([(32824, \'000004a0\')]', ''),
    ('d_b138_o2', DOC, B138, 'eid 128281 orig 2 ([(32824, \'000004a0\')]', ''),
    ('d_b138_o4', DOC, B138, 'eid 128281 orig 4 ([(32824, \'000004a0\')]', ''),
    ('d_b138_o3', DOC, B138, 'eid 128281 orig 3 ([(32824, \'000204a0\')]', ''),
    ('d_b138_r1', DOC, B138, 'eid 128281 r1 1 ([(32824, \'000204a0\')]', ''),
    ('d_b138_44806', DOC, B138, 'eid 44806 orig 1 ([(32824, \'000204a0\')]', ''),
    ('d_k03_nzero', DOC, K03, 'NZERO 138 pre 2097168', '=== DISPATCH eid 128281'),
    ('d_k03_nzero_o1', DOC, K03, 'NZERO 138 o1 2097167', '=== DISPATCH eid 128281'),
    ('d_k03_ndiff', DOC, K03, 'NDIFF 138 o1 o2 1 of 2097168', '=== DISPATCH eid 128281'),
    ('d_k03_pt', DOC, K03, 'EQUAL_SHA 152 o1 o2 True', '=== DISPATCH eid 128281'),
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
        rx = re.compile(r'`(?:(' + EMU + '|' + DOC + r'):([^`:]+):|:)(\d+)`')
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
