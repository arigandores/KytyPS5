"""Track F, F16k (HPP-583): check of every code reference of docs/track-f/f16k.md - the line <path>:<line> of commit
<C> (git show) contains the anchor; the next line (+1) is printed as the control. Output: one line per reference and
'ALL OK' / 'NOT OK' last.

    python refs_f16k.py > refs_f16k.txt
"""
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
C = "810909e3"
R = "src/graphics/host_gpu/renderer/"
REFS = [
    (R + "diagF5.h", 118, "F5CmuKept,"),
    (R + "diagF5.h", 124, "CmaskRtBucketOnly,"),
    (R + "diagF5.h", 183, "[[nodiscard]] bool FixCmuOn();"),
    (R + "diagF5.h", 212, "struct StaleProbe {"),
    (R + "diagF5.h", 336, "struct CsDispatch {"),
    (R + "diagF5.cpp", 245, "const char* IdNames[] = {"),
    (R + "diagF5.cpp", 571, "bool FixCmuOn() {"),
    (R + "diagF5.cpp", 585, "bool ExactRingOn() {"),
    (R + "diagF5.cpp", 628, "void NotePresent(uint32_t present) {"),
    (R + "diagF5.cpp", 647, "bool NoteCmuEvent(const CmuEventLine& line) {"),
    (R + "diagF5.cpp", 677, "static const bool on = Knob() && DiagF5::On();"),
    (R + "diagF5.cpp", 715, "void NoteFce(const FceEvent& e) {"),
    (R + "diagF5.cpp", 772, "void NoteBind(uint64_t image_address, BindKind kind"),
    (R + "diagF5.cpp", 790, "void NoteBufferAccess(uint64_t address, uint64_t size) {"),
    (R + "diagF5.cpp", 803, "void Emit(CsDispatch& d, const DiagF5::CsRefusals& refusals) {"),
    (R + "diagF5.cpp", 898, "void NoteClearApplied(ApplySite site"),
    (R + "diagF5.cpp", 929, "void NoteFill(uint64_t address) {"),
    (R + "diagF5.cpp", 961, "bool ServiceAt(uint32_t frame, bool exit) {"),
    (R + "diagF5.cpp", 982, "const auto cnt              = s.cnt;"),
    (R + "diagF5.cpp", 997, "const bool id_fce = "),
    (R + "cache/bufferCache.h", 473, "std::unordered_map<uint64_t, ExactRing> m_bucket_write_ring;"),
    (R + "cache/bufferCache.cpp", 1459, "DiagF5Id::NoteBufferAccess(vaddr, size);"),
    (R + "cache/bufferCache.cpp", 2866, "if (DiagF5::ExactRingOn()) [[unlikely]] {"),
    (R + "cache/bufferCache.cpp", 2875, "BufferCache::ExactWriteSeq BufferCache::LastGpuWriteSeqExact("),
    (R + "cache/textureCache.cpp", 1886, "class F5CmuScope {"),
    (R + "cache/textureCache.cpp", 1893, "~F5CmuScope() {"),
    (R + "cache/textureCache.cpp", 1977, "image.info.data.address, f5id ? &f5_probe : nullptr)) {"),
    (R + "cache/textureCache.cpp", 2081, "DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::DccRt"),
    (R + "cache/textureCache.cpp", 2086, "void TextureCache::PrepareCmaskClear(ImageId id, const ImageDesc& desc, bool fce"),
    (R + "cache/textureCache.cpp", 2094, "F5CmuScope f5 {fce, f5cmu};"),
    (R + "cache/textureCache.cpp", 2118, "f5.Probe())) {"),
    (R + "cache/textureCache.cpp", 2121, "f5.Decided();"),
    (R + "cache/textureCache.cpp", 2179, "f5.Cleared();"),
    (R + "cache/textureCache.cpp", 2188, "DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::CmaskRt"),
    (R + "cache/textureCache.cpp", 2592, "PrepareCmaskClear(id, desc, fce_materialize, f5cmu);"),
    (R + "cache/textureCache.cpp", 3370, "*f5id_snap = F5IdSnapOf(found->second);"),
    (R + "cache/textureCache.cpp", 3386, "void TextureCache::F5IdMetaSnap(uint64_t address, DiagF5Id::MetaSnap* out) {"),
    (R + "cache/textureCache.cpp", 3451, "DiagF5Id::NoteFill(address);"),
    (R + "cache/textureCache.cpp", 3464, "DiagF5Id::NoteFillSeq(m_f5id_stamp_address,"),
    (R + "cache/textureCache.cpp", 3494, "const auto last_seq    = m_buffer_cache.LastGpuWriteSeq(address, meta.fill_size, false);"),
    (R + "cache/textureCache.cpp", 3502, "if (f5_probe != nullptr) [[unlikely]] {"),
    (R + "cache/textureCache.cpp", 3507, "m_buffer_cache.LastGpuWriteSeqExact(address, meta.fill_size, meta.fill_seq);"),
    (R + "cache/textureCache.cpp", 3511, "if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {"),
    (R + "cache/textureCache.cpp", 3527, "ImageId TextureCache::FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address,"),
    (R + "cache/textureCache.cpp", 3575, "*f5id_miss = DiagF5Id::ScanReason("),
    (R + "cache/textureCache.cpp", 3580, "bool TextureCache::AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address, DiagF5Id::DccMiss* f5id_miss) {"),
    (R + "cache/textureCache.cpp", 3616, "const bool         f5_stale = PendingDccFillStale(metadata_address"),
    (R + "pipeline/descriptors.cpp", 3470, "thread_local bool t_f5id_fce_site = false;"),
    (R + "pipeline/descriptors.cpp", 3661, "DiagF5Id::NoteClearApplied(t_f5id_fce_site"),
    (R + "pipeline/descriptors.cpp", 3831, "F5IdSlotSizes F5IdSlotSizesOf(const HW::RenderTarget& rt) {"),
    (R + "pipeline/descriptors.cpp", 3859, "void F5IdNoteFceMiss(TextureCache& cache, BufferCache& buffers"),
    (R + "pipeline/descriptors.cpp", 3884, "const auto exact = buffers.LastGpuWriteSeqExact(e.dcc, e.dcc_size, since);"),
    (R + "pipeline/descriptors.cpp", 3888, "e.cpu_mod        = buffers.IsRegionCpuModified(e.dcc, e.dcc_size) ? 1 : 0;"),
    (R + "pipeline/descriptors.cpp", 3921, "DiagF5::CmuEvent f5_cmu {};"),
    (R + "pipeline/descriptors.cpp", 3930, "(void)cache.FindRenderTarget("),
    (R + "pipeline/descriptors.cpp", 3938, "DiagF5::On() ? &f5_cmu : nullptr);"),
    (R + "pipeline/descriptors.cpp", 3959, "(void)DiagF5::NoteCmuEvent({.present = DiagF5::Present(),"),
    (R + "pipeline/descriptors.cpp", 3994, "cache.F5IdMetaSnap(rt.dcc_addr.addr, &f5id_before);"),
    (R + "pipeline/descriptors.cpp", 3996, "const auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr, f5id ? &f5id_miss : nullptr);"),
    (R + "pipeline/descriptors.cpp", 4002, "F5IdNoteFceMiss(cache, m_context.GetBufferCache(), slot, rt, f5id_before, f5id_miss);"),
    (R + "pipeline/descriptors.cpp", 4017, "const F5IdFceSite f5id_site;"),
    (R + "pipeline/descriptors.cpp", 4029, "DiagF5Id::NoteBind(image.info.data.address, DiagF5Id::BindKind::Target"),
    (R + "pipeline/descriptors.cpp", 6706, "DiagF5Id::NoteBind(image.info.data.address, DiagF5Id::BindKind::Texture"),
    (R + "renderCompute.cpp", 77, "class F5IdCsHolder {"),
    (R + "renderCompute.cpp", 160, "auto* const f5id_snap = "),
    (R + "renderCompute.cpp", 178, "f5id->sizes[f5_refusals->count] = descriptor.GetSize();"),
    (R + "renderCompute.cpp", 631, "F5IdCsHolder f5id {f5_refusals};"),
    (R + "renderCompute.cpp", 640, "f5id.Class(DiagF5Id::CsClass::MetaClear, 0);"),
    (R + "renderCompute.cpp", 654, "f5id.Class(DiagF5Id::CsClass::ImgClear, 0);"),
    (R + "renderCompute.cpp", 662, "f5id.Class(DiagF5Id::CsClass::Exec, f5_tracked);"),
    (R + "renderCompute.cpp", 1263, "f5id.After(m_context.GetTextureCache());"),
    (R + "renderCompute.cpp", 1290, "f5id.After(m_context.GetTextureCache());"),
    ("src/graphics/guest_gpu/graphicsRun.cpp", 711, "(void)DiagF5Id::Service();"),
    ("src/graphics/guest_gpu/graphicsRun.cpp", 792, "(void)DiagF5Id::Service(true);"),
    ("src/graphics/presentation/window/vulkanWindow.cpp", 683, "(void)DiagF5::LogFixCmuMode();"),
    ("src/graphics/presentation/window/vulkanWindow.cpp", 684, "(void)DiagF5Id::LogMode();"),
    ("src/graphics/presentation/window/screenshot.cpp", 239, "m_presents++;"),
    ("src/graphics/presentation/window/screenshot.cpp", 243, "DiagF5::NotePresent(m_presents);"),
    ("src/graphics/presentation/window/screenshot.cpp", 371, "slot.present = m_presents;"),
    ("src/graphics/presentation/window/screenshot.cpp", 442, "job.present = slot.present;"),
    ("src/graphics/presentation/window/screenshot.cpp", 519, "std::fprintf(m_rec_index, "),
    ("src/graphics/presentation/window/swapchain.cpp", 947, "const bool screenshot = !preparing && m_impl->screenshot.Poll();"),
    ("CMakeLists.txt", 156, "graphics/host_gpu/renderer/image/imageInfo.h"),
    ("tests/ShaderRecompilerComputeTests.cpp", 10448, "void CheckF16k() {"),
    ("tests/ShaderRecompilerComputeTests.cpp", 34396, "if (argc == 2 && std::strcmp(argv[1], \"--f16k-only\") == 0) {"),
]


def main():
    cache = {}
    ok = True
    n = 0
    for path, line, anchor in REFS:
        if path not in cache:
            p = subprocess.run([G, "-C", REPO, "show", "%s:%s" % (C, path)], capture_output=True)
            cache[path] = p.stdout.decode("utf-8").split("\n")
        lines = cache[path]
        got = lines[line - 1] if 0 < line <= len(lines) else ""
        nxt = lines[line] if line < len(lines) else ""
        good = anchor in got
        ok &= good
        n += 1
        print("%s %s:%s:%d | %s | +1: %s" % ("OK " if good else "BAD", C, path, line, anchor[:70], nxt.strip()[:70]))
    print("%d references" % n)
    print("ALL OK" if ok else "NOT OK")
    return 0 if ok else 1


sys.exit(main())
