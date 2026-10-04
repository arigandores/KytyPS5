"""Track F, F16l2 (HPP-591, Red Team): every <commit>:<path>:<line> of docs/track-f/f16l2-review.md by its anchor and +1
(whole stripped lines for code; prefix for ROADMAP lines). Prints ALL OK or the failures."""
import subprocess
import sys

REPO = "C:/kyty/KytyPS5"
E = "ed4f96d8"
RC = "src/graphics/host_gpu/renderer/renderCompute.cpp"
TC = "src/graphics/host_gpu/renderer/cache/textureCache.cpp"
DS = "src/graphics/host_gpu/renderer/pipeline/descriptors.cpp"
BC = "src/graphics/host_gpu/renderer/cache/bufferCache.cpp"
T = "tests/ShaderRecompilerComputeTests.cpp"
RM = "src/graphics/host_gpu/regionManager.h"
BS = chr(92)
REFS = [
    ("781ec04f", "docs/ROADMAP.md", 22795, "496. **Звено F16l трека F (`HPP-584`, Red Team) ПРИНЯТО лидом",
     "(а) **Приёмка строкой. F16l ✓**", "prefix"),
    ("b3ec1d4c", "docs/ROADMAP.md", 22823, "500. **Звено F16k2 трека F (`HPP-590`, Emu Engineer) ПРИНЯТО лидом",
     "(а) **Приёмка по п. 496(б)(1)–(6). F16k2 ✓.**", "prefix"),
    (E, DS, 3887, "const bool large = exact.seq == 0 && buffers.LargeGpuWriteSeq() > since;",
     "e.wr_after       = exact.seq != 0    ? DiagF5Id::WrAfter::Exact", "exact"),
    (E, BC, 2856, "if (size > (16u << 20)) {", "m_large_write_seq = seq;", "exact"),
    (E, T, 11124, "BTA::F16kNoteGpuWrite(buffers, base, 0x1000001); // 16 MB + 1 after the fill",
     "const auto g2 = scan2(dx_large, 6001);", "exact"),
    (E, DS, 3898, "e.cpu_mod = cpu_now || !seen || fill_epoch == 0 || buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch",
     "? 1", "exact"),
    (E, "src/graphics/host_gpu/memoryTracker.h", 52, "return mixed == 0 ? 1 : mixed;", "}", "exact"),
    (E, BC, 2908, "if (size == 0 || !GuestRange {vaddr, size}.Valid()) {", "return 0;", "exact"),
    (E, T, 11131, "buffers.InvalidateMemory(dx_cpu + 0x10, 4);", "(void)buffers.ObtainBuffer(dx_cpu, 0x10000, false, false);",
     "exact"),
    (E, RC, 85, "m_cache->F5IdNoteStampLate();", "}", "exact"),
    (E, TC, 3460, "if (m_f5id_stamp_address != 0 && !m_f5id_stamp_late) {", "DiagF5Id::NoteStampLate();", "exact"),
    (E, TC, 3532, "f5_probe->cpu         = true; // Track F, F16k2 (RC4): why=cpu", "} else {", "exact"),
    (E, TC, 3538, "if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {", "return false;", "exact"),
    (E, TC, 1898, "if (m_decide && DiagF5::On()) [[unlikely]] {", "switch (fix) {", "exact"),
    (E, TC, 1915, "if (m_out != nullptr) [[unlikely]] {", "m_out->fix = fix;", "exact"),
    (E, DS, 3995, "if (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&",
     "f5_cmu.fix != DiagF5::CmuFix::Fresh) [[unlikely]] {", "exact"),
    (E, "src/graphics/host_gpu/renderer/diagF5.cpp", 674, "bool NoteCmuNoHit(const CmuEventLine& line, bool drawn) {",
     "const auto n = g_cmu_nohit_events.fetch_add(1, std::memory_order_relaxed) + 1;", "exact"),
    (E, "src/graphics/host_gpu/renderer/diagF5.cpp", 654, "bool NoteCmuEvent(const CmuEventLine& line) {",
     "const auto n = g_cmu_events.fetch_add(1, std::memory_order_relaxed) + 1;", "exact"),
    (E, T, 10783, "// ---- K7 (Track F, F16k2, RC5, ROADMAP s122 item 496(b)(5)): an FCE acquisition without a B42 hit - a 1024x1024",
     "// target carries CMASK metadata from its registers, so FixB42Probe answers None (cmask_fce_meta) and no cmask_fce", "exact"),
    (E, TC, 1889, ": m_out(out), m_decide(fce && DiagF5::FixCmuOn()), m_rt_count(!fce && DiagF5Id::On()) {",
     "m_probe.exact_decides = m_decide;", "exact"),
    (E, TC, 2599, "PrepareCmaskClear(id, desc, fce_materialize, f5cmu); // Track F, F16k: the FCE acquisition and its decision",
     "}", "exact"),
    (E, DS, 3950, "DiagF5::On() ? &f5_cmu : nullptr); // Track F, F16k: its decision for the event line", "}", "exact"),
    (E, DS, 3967, "if (DiagF5::On() && b42.kind == FixB42Kind::Hit) [[unlikely]] {",
     "// Track F, F16k (item 492(v)(4)): the event line of a B42 hit - the last present number of the video", "exact"),
    (E, DS, 3708, "if (!color.image_id || info.metadata.kind != ImageMetadataKind::None || info.samples != 1 ||",
     "info.resources.levels != 1 || info.IsVolume() ||", "exact"),
    (E, DS, 3728, "if (fill.b42_draw_seq > fill.b42_fill_seq) {", "probe.kind = FixB42Kind::Drawn;", "exact"),
    (E, DS, 3927, "if (b42.kind == FixB42Kind::Hit && FixB42Enabled()) {",
     "color.desc.info.metadata.kind              = ImageMetadataKind::Cmask;", "exact"),
    (E, DS, 3934, "if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {",
     "// Session 71, candidate C3 (counters only): the second entrance into", "exact"),
    (E, "src/graphics/host_gpu/renderer/diagF5.h", 208, "CmuFix fix = CmuFix::Off;", "CmuWhy why = CmuWhy::None;", "exact"),
    (E, RC, 319, "cache.TrackDccFill(descriptor.Base48(), size, packed_clear);", "if (f5_tracked != nullptr) [[unlikely]] {",
     "exact"),
    (E, RC, 654, "TryConsumeComputeImageClear(input_info, buffer, thread_group_x, thread_group_y,",
     "thread_group_z, mode, f5_on ? &f5_tracked : nullptr)) {", "exact"),
    (E, RC, 493, "Common::LockGuard            lock(m_context.GetMutex());", "Common::FrameStats::MutexMark lock_mark(lock_t0);",
     "exact"),
    (E, RC, 1100, "if (!bind_floor && BindFloorClearSkip()) {",
     "Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorSkipDrop, 1);", "exact"),
    (E, RC, 615, "const bool floor_clear_skip = !indirect && BindFloorClearSkip();", "if (floor_clear_skip) {", "exact"),
    (E, "src/graphics/host_gpu/renderer/cache/textureCache.h", 344, "TrackingSpinLock                                  m_lock;",
     "PageManager&                                      m_page_manager;", "exact"),
    (E, RC, 636, "F5IdCsHolder f5id {f5_refusals};", "if (DiagF5Id::On()) [[unlikely]] {", "exact"),
    (E, RC, 504, "const SkcCensus::OpScope skc_op(m_context.GetTextureCache(), Common::SkipCeil::KindCS, false);",
     "// Session 97, gate \"bindfloor\": latch the floor decision for this whole dispatch before", "exact"),
    (E, TC, 3471, "void TextureCache::StampPendingDccFill() {", "std::scoped_lock lock {m_lock};", "exact"),
    (E, TC, 3497, "void TextureCache::F5IdNoteStampLate() {", "if (!DiagF5Id::On()) {", "exact"),
    (E, RC, 638, "f5id.Arm(input_info, m_context.GetTextureCache());", "}", "exact"),
    (E, T, 11159, "cache.TrackDccFill(dx_late, 0x1000, 0);", "cache.F5IdNoteStampLate();", "exact"),
    ("11faf668", "docs/track-f/f16k2/mut_f16k2.py", 38, "\"m12_no_stamp_late\": (R + \"cache/textureCache.cpp\",",
     "\"" + BS + "t" + BS + "tm_f5id_stamp_late = true;" + BS + "n" + BS + "t" + BS + "tDiagF5Id::NoteStampLate();" + BS + "n\",",
     "exact"),
    (E, RM, 222, "m_cpu_epoch.fetch_add(1, std::memory_order_release);", "m_epoch.fetch_add(1, std::memory_order_release);", "exact"),
    (E, RM, 413, "const bool provisional = request_pages != 0 || armed_pages != settled_pages;", "if (provisional) {", "exact"),
    (E, RM, 184, "if (m_cpu_dirty.AnyInRange(start, end)) {",
     "EXIT(\"GPU dirty state conflicts with CPU dirty state" + BS + "n\");", "exact"),
    (E, RC, 651, "return;", "}", "exact"),
    (E, RC, 662, "return;", "}", "exact"),
    (E, RC, 1049, "return;", "}", "exact"),
    (E, RC, 1103, "return;", "}", "exact"),
    (E, RC, 1273, "return;", "}", "exact"),
    (E, RC, 1267, "m_context.GetTextureCache().StampPendingDccFill();",
     "f5id.After(m_context.GetTextureCache()); // Track F, F16k (KYTY_DIAG_F5ID): the entries after the write", "exact"),
    (E, RC, 1294, "m_context.GetTextureCache().StampPendingDccFill();",
     "f5id.After(m_context.GetTextureCache()); // Track F, F16k (KYTY_DIAG_F5ID): the entries after the write", "exact"),
    (E, "src/graphics/host_gpu/renderer/cache/textureCache.h", 423, "class OpScope {", "public:", "exact"),
    (E, "src/graphics/host_gpu/renderer/commandScheduler.h", 203, "class OpScope {", "public:", "exact"),
]
cache = {}
fails = 0
for commit, path, line, anchor, plus1, mode in REFS:
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % key], capture_output=True)
        if out.returncode != 0:
            print("FAIL %s:%s - git show rc %d" % (commit, path, out.returncode))
            fails += 1
            cache[key] = None
            continue
        cache[key] = out.stdout.decode("utf-8").split("\n")
    lines = cache[key]
    if lines is None:
        continue
    a = lines[line - 1].strip() if line - 1 < len(lines) else ""
    b = lines[line].strip() if line < len(lines) else ""
    if mode == "prefix":
        ok = a.startswith(anchor) and b.startswith(plus1)
    else:
        ok = a == anchor and b == plus1
    print("%s %s:%s:%d" % ("ok  " if ok else "FAIL", commit, path, line))
    if not ok:
        fails += 1
        print("     got:   %r" % a[:140])
        print("     got+1: %r" % b[:140])
print("refs %d, failed %d" % (len(REFS), fails))
print("ALL OK" if fails == 0 else "FAILED")
sys.exit(0 if fails == 0 else 1)
