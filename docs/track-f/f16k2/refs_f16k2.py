"""Track F, F16k2 (HPP-590): check of every code reference of docs/track-f/f16k2.md - the line <path>:<line> of commit
<C> (git show) contains the anchor; the next line (+1) is printed as the control. Output: one line per reference and
'ALL OK' / 'NOT OK' last. Copy of f16k/refs_f16k.py with the F16k2 references.

    python refs_f16k2.py > refs_f16k2.txt
"""
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
C = "ed4f96d8"
R = "src/graphics/host_gpu/renderer/"
REFS = [
    (R + "diagF5.h", 127, "F5CmuExactCpu,"),
    (R + "diagF5.h", 204, "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu };"),
    (R + "diagF5.h", 223, "bool cpu           = false;"),
    (R + "diagF5.h", 258, "[[nodiscard]] std::string FormatCmuNoHit(uint64_t n, const CmuEventLine& line, bool drawn);"),
    (R + "diagF5.h", 259, "bool                      NoteCmuNoHit(const CmuEventLine& line, bool drawn);"),
    (R + "diagF5.h", 299, "enum class WrAfter : uint8_t { None, Exact, Fallback, Na, Large };"),
    (R + "diagF5.h", 379, "void     NoteFillSeq(uint64_t address, uint64_t seq, uint64_t cpu_epoch);"),
    (R + "diagF5.h", 381, "[[nodiscard]] bool     FillCpuEpoch(uint64_t address, uint64_t* cpu_epoch);"),
    (R + "diagF5.h", 384, "void NoteStampLate();"),
    (R + "diagF5.cpp", 218, "\"f5cmu_exact_cpu\","),
    (R + "diagF5.cpp", 253, "\"stamp_late\","),
    (R + "diagF5.cpp", 291, "kStampLate, // Track F, F16k2 (RC3)"),
    (R + "diagF5.cpp", 354, "std::map<uint64_t, uint64_t>    fill_cpu_epoch;"),
    (R + "diagF5.cpp", 388, "case Id::WrAfter::Large: return \"large\";"),
    (R + "diagF5.cpp", 617, "case CmuWhy::Cpu: return \"cpu\";"),
    (R + "diagF5.cpp", 632, "std::atomic<uint64_t> g_cmu_nohit_events {0};"),
    (R + "diagF5.cpp", 663, "std::string FormatCmuNoHit(uint64_t n, const CmuEventLine& line, bool drawn) {"),
    (R + "diagF5.cpp", 674, "bool NoteCmuNoHit(const CmuEventLine& line, bool drawn) {"),
    (R + "diagF5.cpp", 968, "void NoteFillSeq(uint64_t address, uint64_t seq, uint64_t cpu_epoch) {"),
    (R + "diagF5.cpp", 982, "bool FillCpuEpoch(uint64_t address, uint64_t* cpu_epoch) {"),
    (R + "diagF5.cpp", 993, "void NoteStampLate() {"),
    (R + "diagF5.cpp", 1109, "s.fill_cpu_epoch.clear();"),
    (R + "cache/bufferCache.h", 493, "[[nodiscard]] uint64_t LargeGpuWriteSeq() const noexcept { return m_large_write_seq; }"),
    (R + "cache/bufferCache.h", 494, "[[nodiscard]] uint64_t F5IdRangeWriteEpoch(uint64_t vaddr, uint64_t size);"),
    (R + "cache/bufferCache.cpp", 2856, "if (size > (16u << 20)) {"),
    (R + "cache/bufferCache.cpp", 2906, "uint64_t BufferCache::F5IdRangeWriteEpoch(uint64_t vaddr, uint64_t size) {"),
    (R + "cache/textureCache.h", 181, "void F5IdNoteStampLate();"),
    (R + "cache/textureCache.h", 354, "bool                                              m_f5id_stamp_late    = false;"),
    (R + "cache/textureCache.cpp", 1908, "DiagF5::Add(DiagF5::Counter::F5CmuExactCpu); // Track F, F16k2 (RC4)"),
    (R + "cache/textureCache.cpp", 1920, ": fix == DiagF5::CmuFix::ExactStale && m_probe.cpu ? DiagF5::CmuWhy::Cpu"),
    (R + "cache/textureCache.cpp", 3460, "if (m_f5id_stamp_address != 0 && !m_f5id_stamp_late) {"),
    (R + "cache/textureCache.cpp", 3461, "DiagF5Id::NoteStampLate();"),
    (R + "cache/textureCache.cpp", 3465, "m_f5id_stamp_late    = false;"),
    (R + "cache/textureCache.cpp", 3477, "DiagF5Id::NoteFillSeq(m_f5id_stamp_address,"),
    (R + "cache/textureCache.cpp", 3479, "m_buffer_cache.F5IdRangeWriteEpoch(m_f5id_stamp_address, m_f5id_stamp_size));"),
    (R + "cache/textureCache.cpp", 3482, "m_f5id_stamp_late    = false;"),
    (R + "cache/textureCache.cpp", 3497, "void TextureCache::F5IdNoteStampLate() {"),
    (R + "cache/textureCache.cpp", 3503, "m_f5id_stamp_late = true;"),
    (R + "cache/textureCache.cpp", 3504, "DiagF5Id::NoteStampLate();"),
    (R + "cache/textureCache.cpp", 3530, "if (cpu_written) {"),
    (R + "cache/textureCache.cpp", 3532, "f5_probe->cpu         = true; // Track F, F16k2 (RC4): why=cpu"),
    (R + "cache/textureCache.cpp", 3538, "if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {"),
    (R + "cache/textureCache.cpp", 2599, "PrepareCmaskClear(id, desc, fce_materialize, f5cmu);"),
    (R + "pipeline/descriptors.cpp", 3942, "(void)cache.FindRenderTarget("),
    (R + "pipeline/descriptors.cpp", 3708, "if (!color.image_id || info.metadata.kind != ImageMetadataKind::None || info.samples != 1 ||"),
    (R + "pipeline/descriptors.cpp", 3729, "probe.kind = FixB42Kind::Drawn;"),
    (R + "pipeline/descriptors.cpp", 3859, "void F5IdNoteFceMiss(TextureCache& cache, BufferCache& buffers, uint32_t slot, const HW::RenderTarget& rt,"),
    (R + "pipeline/descriptors.cpp", 3887, "const bool large = exact.seq == 0 && buffers.LargeGpuWriteSeq() > since;"),
    (R + "pipeline/descriptors.cpp", 3896, "const bool seen       = DiagF5Id::FillCpuEpoch(e.dcc, &fill_epoch);"),
    (R + "pipeline/descriptors.cpp", 3898, "e.cpu_mod = cpu_now || !seen || fill_epoch == 0 || buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch"),
    (R + "pipeline/descriptors.cpp", 3928, "color.desc.info.metadata.kind              = ImageMetadataKind::Cmask;"),
    (R + "pipeline/descriptors.cpp", 3934, "if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {"),
    (R + "pipeline/descriptors.cpp", 3967, "if (DiagF5::On() && b42.kind == FixB42Kind::Hit) [[unlikely]] {"),
    (R + "pipeline/descriptors.cpp", 3995, "if (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&"),
    (R + "pipeline/descriptors.cpp", 3997, "(void)DiagF5::NoteCmuNoHit({.present = DiagF5::Present(),"),
    (R + "renderCompute.cpp", 85, "m_cache->F5IdNoteStampLate();"),
    (R + "renderCompute.cpp", 91, "void Arm(const ShaderComputeInputInfo& input, TextureCache& cache) {"),
    (R + "renderCompute.cpp", 493, "Common::LockGuard            lock(m_context.GetMutex());"),
    (R + "renderCompute.cpp", 636, "F5IdCsHolder f5id {f5_refusals};"),
    (R + "renderCompute.cpp", 638, "f5id.Arm(input_info, m_context.GetTextureCache());"),
    (R + "renderCompute.cpp", 1049, "return;"),
    (R + "renderCompute.cpp", 1103, "return;"),
    (R + "renderCompute.cpp", 1267, "m_context.GetTextureCache().StampPendingDccFill();"),
    (R + "renderCompute.cpp", 1294, "m_context.GetTextureCache().StampPendingDccFill();"),
    (R + "colorRenderTarget.cpp", 454, "desc.info.metadata.kind = ImageMetadataKind::Cmask;"),
    ("src/graphics/host_gpu/regionManager.h", 129, "m_cpu_dirty.Fill();"),
    ("src/graphics/host_gpu/regionManager.h", 618, "std::atomic<uint64_t>  m_epoch {1};"),
    ("src/graphics/host_gpu/memoryTracker.cpp", 59, "RegionManager* MemoryTracker::GetOrCreateRegion(uint64_t index) {"),
    ("src/graphics/host_gpu/memoryTracker.h", 35, "[[nodiscard]] uint64_t RangeWriteEpoch(uint64_t vaddr, uint64_t size) noexcept {"),
    ("src/graphics/host_gpu/memoryTracker.h", 45, "return 0; // an untracked region is CPU-dirty by definition"),
    ("tests/ShaderRecompilerComputeTests.cpp", 10448, "void CheckF16k() {"),
    ("tests/ShaderRecompilerComputeTests.cpp", 10541, "Require(name, \"no-hit line form\","),
    ("tests/ShaderRecompilerComputeTests.cpp", 10685, "{\"K8 CPU-modified CMASK page, no crossing GPU write: why=cpu\""),
    ("tests/ShaderRecompilerComputeTests.cpp", 10783, "// ---- K7 (Track F, F16k2, RC5, ROADMAP s122 item 496(b)(5))"),
    ("tests/ShaderRecompilerComputeTests.cpp", 11098, "// D18-D20 (Track F, F16k2, ROADMAP s122 item 496(b)(1)-(3))"),
    ("tests/ShaderRecompilerComputeTests.cpp", 11177, "Require(name, \"D20 stamp_late in the sum line\","),
    ("tests/ShaderRecompilerComputeTests.cpp", 11356, "Require(name, \"Z identity exact_cpu <= exact_stale (F16k2)\""),
    ("tests/ShaderRecompilerComputeTests.cpp", 34592, "if (argc == 2 && std::strcmp(argv[1], \"--f16k-only\") == 0) {"),
]


def main():
    cache = {}
    ok = True
    out = []
    for path, line, anchor in REFS:
        if path not in cache:
            cache[path] = subprocess.run([G, "-C", REPO, "show", "%s:%s" % (C, path)], capture_output=True).stdout.decode(
                "utf-8").split("\n")
        lines = cache[path]
        here = lines[line - 1] if 0 < line <= len(lines) else ""
        good = anchor in here
        ok &= good
        nxt = lines[line] if line < len(lines) else ""
        out.append("%s %s:%s:%d | %s | +1: %s" % ("OK " if good else "BAD", C, path, line, anchor[:70], nxt.strip()[:90]))
    out.append("refs %d" % len(REFS))
    out.append("ALL OK" if ok else "NOT OK")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if ok else 1


sys.exit(main())
