"""F16k (HPP-583, ROADMAP s122 item 492(z)(2), (g)(6)): the test site --f16k-only in tests/ShaderRecompilerComputeTests.cpp.

    python p_tests.py <repo root>

LF in, LF out. Every anchor is whole lines and must occur once. The F16d mode --diag-f5-only is not touched.
"""
import sys

ROOT = sys.argv[1]
PATH = ROOT + "/tests/ShaderRecompilerComputeTests.cpp"


def sub_once(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit("anchor count %d for %r" % (n, old[:80]))
    return text.replace(old, new)


data = open(PATH, "rb").read()
if b"\r" in data:
    raise SystemExit("CR in " + PATH)
t = data.decode("utf-8")

t = sub_once(t, r'''#include "graphics/host_gpu/renderer/diagF5.h"
''', r'''#include "graphics/host_gpu/renderer/diagF5.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"
''')

t = sub_once(t, r'''  static void DiscardVerifiedGpuWrite(BufferCache &cache, uint64_t address, uint64_t size) {
    // Test teardown after checking the GPU result; this mapping is about to be discarded.
    cache.m_gpu_modified_ranges.Subtract(address, size);
    cache.m_memory_tracker.UnmarkRegionAsGpuModified(address, size);
  }
};
''', r'''  static void DiscardVerifiedGpuWrite(BufferCache &cache, uint64_t address, uint64_t size) {
    // Test teardown after checking the GPU result; this mapping is about to be discarded.
    cache.m_gpu_modified_ranges.Subtract(address, size);
    cache.m_memory_tracker.UnmarkRegionAsGpuModified(address, size);
  }

  // Track F, F16k (HPP-583): a GPU write as ObtainBuffer records it, and the size of the exact journal.
  static void F16kNoteGpuWrite(BufferCache &cache, uint64_t vaddr, uint64_t size) { cache.NoteGpuWrite(vaddr, size); }
  static size_t F16kRingBuckets(const BufferCache &cache) { return cache.m_bucket_write_ring.size(); }
};
''')

t = sub_once(t, r'''  static Image &F16dImage(TextureCache &cache, ImageId id) { return cache.m_slot_images[id]; }
''', r'''  static Image &F16dImage(TextureCache &cache, ImageId id) { return cache.m_slot_images[id]; }
  // Track F, F16k (HPP-583): a metadata entry removed (the next TrackDccFill starts a PendingDcc fill again).
  static void F16kEraseMeta(TextureCache &cache, uint64_t address) {
    std::lock_guard lock(cache.m_lock);
    cache.m_surface_metas.erase(address);
  }
  static void F16kPrepareCmaskClear(TextureCache &cache, ImageId id, const TextureCache::ImageDesc &desc, bool fce,
                                    DiagF5::CmuEvent *event) {
    auto lock = Lock(cache);
    cache.PrepareCmaskClear(id, desc, fce, event);
  }
''')

t = sub_once(t, r'''  static bool F16dMetaClear(RenderExecutor &executor, const ShaderComputeInputInfo &input,
                            const CommandBuffer &buffer, DiagF5::CsRefusals *refusals) {
    return executor.TryConsumeComputeMetaClear(input, buffer, refusals);
  }
''', r'''  static bool F16dMetaClear(RenderExecutor &executor, const ShaderComputeInputInfo &input,
                            const CommandBuffer &buffer, DiagF5::CsRefusals *refusals) {
    return executor.TryConsumeComputeMetaClear(input, buffer, refusals);
  }
  // Track F, F16k (HPP-583): the meta-clear shortcut with the KYTY_DIAG_F5ID side, and a target binding.
  static bool F16kMetaClear(RenderExecutor &executor, const ShaderComputeInputInfo &input, const CommandBuffer &buffer,
                            DiagF5::CsRefusals *refusals, DiagF5Id::CsDispatch *f5id) {
    return executor.TryConsumeComputeMetaClear(input, buffer, refusals, f5id);
  }
  static void F16kBindRenderTarget(RenderExecutor &executor, ImageId id) { executor.BindRenderTarget(id); }
''')

t = sub_once(t, r'''  if (argc == 2 && std::strcmp(argv[1], "--cmask-clear-only") == 0) {
''', r'''  if (argc == 2 && std::strcmp(argv[1], "--f16k-only") == 0) {
    // Track F, F16k (HPP-583): the KYTY_FIX_F5CMU / KYTY_DIAG_F5ID test site; run with the knob combinations of
    // docs/track-f/f16k/run_tests_f16k.py.
    VulkanHarness vulkan;
    vulkan.CheckF16k();
    std::printf("F16k test site: ALL OK\n");
    return 0;
  }
  if (argc == 2 && std::strcmp(argv[1], "--cmask-clear-only") == 0) {
''')

TEST = r'''  // Track F, F16k (HPP-583, ROADMAP s122 item 492(z)(2), (g)(6)): the test site of KYTY_FIX_F5CMU and KYTY_DIAG_F5ID
  // without the game. The arms (run_tests_f16k.py) set KYTY_DIAG_F5 / KYTY_FIX_F5CMU / KYTY_DIAG_F5ID; every check below
  // states what it expects with the knob on and with it off: with KYTY_FIX_F5CMU off every decision is the old one (the
  // expected `applied` of the old path), with KYTY_DIAG_F5ID off nothing of DiagF5Id counts or prints.
  inline static uint32_t f16k_checks = 0;
  static void F16kOk(const char *stage) {
    f16k_checks++;
    std::printf("[f16k]    %-60s ok\n", stage);
  }
  static std::string F16kLast(const char *prefix) {
    const auto lines = DiagF5::RecentLines();
    for (auto it = lines.rbegin(); it != lines.rend(); ++it) {
      if (it->rfind(prefix, 0) == 0) {
        return *it;
      }
    }
    return {};
  }
  static size_t F16kCount(const char *prefix) {
    size_t n = 0;
    for (const auto &line : DiagF5::RecentLines()) {
      n += line.rfind(prefix, 0) == 0 ? 1 : 0;
    }
    return n;
  }
  static size_t F16kExact(const char *text) {
    size_t n = 0;
    for (const auto &line : DiagF5::RecentLines()) {
      n += line == text ? 1 : 0;
    }
    return n;
  }
  static std::string F16kField(const std::string &line, const char *key) {
    const auto k = std::string(" ") + key + "=";
    auto at = line.find(k);
    if (at == std::string::npos) {
      return "<none>";
    }
    at += k.size();
    const auto end = line.find(' ', at);
    return line.substr(at, end == std::string::npos ? std::string::npos : end - at);
  }
  using F16kSnap = std::array<uint64_t, static_cast<size_t>(DiagF5::Counter::Count)>;
  static F16kSnap F16kRead() {
    F16kSnap snap{};
    for (uint32_t i = 0; i < snap.size(); i++) {
      snap[i] = DiagF5::Get(static_cast<DiagF5::Counter>(i));
    }
    return snap;
  }
  // The delta of the named DiagF5 counters (each must equal its want; listed counters only).
  static void F16kDelta(const char *stage, const F16kSnap &before, const F16dWant5 &want) {
    const auto now = F16kRead();
    for (const auto &[counter, amount] : want) {
      const auto got = now[static_cast<size_t>(counter)] - before[static_cast<size_t>(counter)];
      Require("F16k", stage, got == amount,
              fmt::format("{}: delta {} != expected {}", DiagF5::Name(counter), got, amount));
    }
  }

  void CheckF16k() {
    constexpr const char *name = "F16k";
    using C = DiagF5::Counter;
    using BTA = BufferCacheTestAccess;
    using TTA = TextureCacheTestAccess;
    using RTA = RenderExecutorTestAccess;
    const bool f5 = Common::EnvValueOn(std::getenv("KYTY_DIAG_F5"));
    const bool cmu = Common::EnvValueOn(std::getenv("KYTY_FIX_F5CMU"));
    const bool knob = Common::EnvValueOn(std::getenv("KYTY_DIAG_F5ID"));
    const bool id = knob && f5;
    const bool ring = cmu || id;
    Require(name, "knob read",
            DiagF5::On() == f5 && DiagF5::FixCmuOn() == cmu && DiagF5Id::Knob() == knob && DiagF5Id::On() == id &&
                DiagF5::ExactRingOn() == ring,
            "the knobs do not follow KYTY_DIAG_F5 / KYTY_FIX_F5CMU / KYTY_DIAG_F5ID");
    std::printf("[f16k]    knobs: KYTY_DIAG_F5=%d KYTY_FIX_F5CMU=%d KYTY_DIAG_F5ID=%d (effective %d), ring %d\n", f5 ? 1 : 0,
                cmu ? 1 : 0, knob ? 1 : 0, id ? 1 : 0, ring ? 1 : 0);
    DiagF5::ClearRecentLines();

    // ---- the mode lines (item 492(v)(1), (g)(1))
    {
      const bool m1 = DiagF5::LogFixCmuMode();
      const bool m2 = DiagF5::LogFixCmuMode();
      const bool i1 = DiagF5Id::LogMode();
      const bool i2 = DiagF5Id::LogMode();
      Require(name, "mode lines",
              m1 == cmu && !m2 && i1 == knob && !i2 && F16kExact("FixF5Cmu: mode=1") == (cmu ? 1u : 0u) &&
                  F16kExact("DiagF5Id: mode=1") == (id ? 1u : 0u) &&
                  F16kExact("DiagF5Id: mode=0 needs=KYTY_DIAG_F5") == (knob && !f5 ? 1u : 0u),
              "a mode line is missing, repeated or printed with its knob off");
      F16kOk("mode lines");
    }

    // ---- pure helpers
    {
      using M = DiagF5Id::Miss;
      const auto r4 = DiagF5Id::ScanReason(2, true, 0x1234, 3);
      const auto r2 = DiagF5Id::ScanReason(0, true, 0x1234, 3);
      const auto r3 = DiagF5Id::ScanReason(0, false, 0, 3);
      const auto r1 = DiagF5Id::ScanReason(0, false, 0, -1);
      Require(name, "ScanReason",
              r4.why == M::R4 && r4.info == 2 && r2.why == M::R2 && r2.info == 0x1234 && r3.why == M::R3 &&
                  r3.info == 3 && r1.why == M::R1 && r1.info == 0,
              "the scan reasons R1-R4");
      using F = DiagF5::CmuFix;
      using W = DiagF5::CmuWhy;
      Require(name, "names",
              std::string(DiagF5::CmuFixName(F::Off)) == "off" && std::string(DiagF5::CmuFixName(F::Fresh)) == "fresh" &&
                  std::string(DiagF5::CmuFixName(F::ExactStale)) == "exact_stale" &&
                  std::string(DiagF5::CmuFixName(F::Kept)) == "kept" &&
                  std::string(DiagF5::CmuFixName(F::KeptApplied)) == "kept_applied" &&
                  std::string(DiagF5::CmuFixName(F::Fallback)) == "fallback" &&
                  std::string(DiagF5::CmuWhyName(W::Value)) == "value" &&
                  std::string(DiagF5::CmuWhyName(W::Mask)) == "mask" &&
                  std::string(DiagF5::CmuWhyName(W::Range)) == "range" &&
                  std::string(DiagF5::CmuWhyName(W::Partial)) == "partial" &&
                  std::string(DiagF5::CmuWhyName(W::Decode)) == "decode" &&
                  std::string(DiagF5::CmuWhyName(W::Layers)) == "layers" &&
                  std::string(DiagF5::CmuWhyName(W::NoLayer)) == "nolayer" &&
                  std::string(DiagF5Id::MetaTypeName(DiagF5Id::MetaType::Absent)) == "absent" &&
                  std::string(DiagF5Id::MetaTypeName(DiagF5Id::MetaType::Dcc)) == "Dcc" &&
                  std::string(DiagF5::Name(C::F5CmuKept)) == "f5cmu_kept" &&
                  std::string(DiagF5::Name(C::CmaskRtBucketOnly)) == "cmask_rt_bucket_only",
              "a name of the new enums or counters");
      DiagF5::StaleProbe p{};
      const bool fresh = !DiagF5::StaleBucketOnly(p);
      p.bucket_stale = true;
      const bool only = DiagF5::StaleBucketOnly(p);
      p.fallback = true;
      const bool fb = !DiagF5::StaleBucketOnly(p);
      p.fallback = false;
      p.exact_stale = true;
      const bool ex = !DiagF5::StaleBucketOnly(p);
      Require(name, "StaleBucketOnly", fresh && only && fb && ex, "StaleBucketOnly");
      const auto line = DiagF5::FormatCmuEvent(3, {.present = 7, .gpu = 9, .image = 0x10, .cmask = 0x20, .width = 1920,
                                                   .height = 1080, .applied = false,
                                                   .event = {F::Kept, W::Decode}});
      Require(name, "event line form",
              line == "DiagF5Ev: cmask_fce n=3 present=7 gpu=9 image=0x0000000000000010 cmask=0x0000000000000020 "
                      "extent=1920x1080 applied=0 fix=kept why=decode",
              "the event line: " + line);
      F16kOk("pure helpers (ScanReason R1-R4, names, StaleBucketOnly, event line)");
    }

    EnsureRuntimeContext();
    constexpr uintptr_t base = 0x0000000207000000ull;
    constexpr uint64_t allocation_size = 0x2000000;
    int64_t direct = -1;
    Require(name, "allocate",
            Libs::LibKernel::Memory::KernelAllocateDirectMemory(
                0, Libs::LibKernel::Memory::KernelGetDirectMemorySize(), allocation_size, 0x10000, 0, &direct) == 0,
            "F16k test allocation failed");
    void *mapped = reinterpret_cast<void *>(base);
    Require(name, "map",
            Libs::LibKernel::Memory::KernelMapDirectMemory(&mapped, allocation_size, 3, 0x10, direct, 0x10000) == 0 &&
                mapped == reinterpret_cast<void *>(base),
            "F16k test mapping failed");
    std::memset(mapped, 0x5a, allocation_size);

    // ---- R: the exact journal (item 492(v)(3)): a neighbour in the bucket, a crossing write, K + 1 newer writes
    {
      RenderContext context(m_runtime_context);
      auto &buffers = context.GetBufferCache();
      constexpr uint64_t b = base + 0x100000;
      BTA::F16kNoteGpuWrite(buffers, b, 0x1000); // the fill
      const auto s1 = buffers.LastGpuWriteSeq(b, 0x1000, false);
      BTA::F16kNoteGpuWrite(buffers, b + 0x1000, 0x1000); // a neighbour: same 64 KB bucket, no overlap
      const auto bucket = buffers.LastGpuWriteSeq(b, 0x1000, false);
      const auto e1 = buffers.LastGpuWriteSeqExact(b, 0x1000, s1);
      Require(name, "R1 neighbour",
              bucket > s1 && (ring ? (e1.seq == 0 && !e1.fallback) : (e1.seq == 0 && e1.fallback)),
              fmt::format("bucket {} fill {} exact {} fallback {}", bucket, s1, e1.seq, e1.fallback));
      BTA::F16kNoteGpuWrite(buffers, b + 0x800, 0x100); // crossing the fill
      const auto s3 = buffers.LastGpuWriteSeq(b, 0x1000, false);
      const auto e2 = buffers.LastGpuWriteSeqExact(b, 0x1000, s1);
      Require(name, "R2 crossing",
              ring ? (e2.seq == s3 && !e2.fallback) : (e2.seq == 0 && e2.fallback),
              fmt::format("exact {} last {} fallback {}", e2.seq, s3, e2.fallback));
      const auto e3 = buffers.LastGpuWriteSeqExact(b, 0x1000, s3);
      Require(name, "R3 nothing newer", e3.seq == 0 && !e3.fallback, "a bucket without a newer write is clean");
      constexpr uint64_t c = base + 0x200000;
      BTA::F16kNoteGpuWrite(buffers, c, 0x1000);
      const auto t1 = buffers.LastGpuWriteSeq(c, 0x1000, false);
      for (uint32_t i = 0; i < 7; i++) {
        BTA::F16kNoteGpuWrite(buffers, c + 0x2000 + i * 0x100, 0x100);
      }
      const auto k7 = buffers.LastGpuWriteSeqExact(c, 0x1000, t1);
      BTA::F16kNoteGpuWrite(buffers, c + 0x3000, 0x100);
      const auto k8 = buffers.LastGpuWriteSeqExact(c, 0x1000, t1);
      Require(name, "R4 K = 8: 7 newer keep the history, the 8th newer one is a fallback",
              ring ? (k7.seq == 0 && !k7.fallback && k8.seq == 0 && k8.fallback) : (k7.fallback && k8.fallback),
              fmt::format("k7 {} {} k8 {} {}", k7.seq, k7.fallback, k8.seq, k8.fallback));
      constexpr uint64_t d = base + 0x300000;
      BTA::F16kNoteGpuWrite(buffers, d, 0x20000); // a fill over two buckets
      const auto u1 = buffers.LastGpuWriteSeq(d, 0x20000, false);
      BTA::F16kNoteGpuWrite(buffers, d + 0x10000 + 0x100, 0x10); // crossing it in the second bucket
      const auto u2 = buffers.LastGpuWriteSeq(d, 0x20000, false);
      const auto e4 = buffers.LastGpuWriteSeqExact(d, 0x20000, u1);
      Require(name, "R5 two buckets", ring ? (e4.seq == u2 && !e4.fallback) : e4.fallback, "a write in the 2nd bucket");
      // K writes since the process start, none crossing: the ring holds the whole history (no fallback); one more
      // drops the first one (fallback).
      constexpr uint64_t e = base + 0x500000;
      for (uint32_t i = 0; i < 8; i++) {
        BTA::F16kNoteGpuWrite(buffers, e + 0x2000 + i * 0x100, 0x100);
      }
      const auto f8 = buffers.LastGpuWriteSeqExact(e, 0x1000, 0);
      BTA::F16kNoteGpuWrite(buffers, e + 0x3000, 0x100);
      const auto f9 = buffers.LastGpuWriteSeqExact(e, 0x1000, 0);
      Require(name, "R7 K writes since the start: complete history; K + 1: fallback",
              ring ? (f8.seq == 0 && !f8.fallback && f9.seq == 0 && f9.fallback) : (f8.fallback && f9.fallback),
              fmt::format("f8 {} {} f9 {} {}", f8.seq, f8.fallback, f9.seq, f9.fallback));
      BTA::F16kNoteGpuWrite(buffers, base + 0x1000000, 0x1000001); // > 16 MB: no bucket, no ring
      Require(name, "R6 the ring is written only with a knob",
              (BTA::F16kRingBuckets(buffers) == 5) == ring && (BTA::F16kRingBuckets(buffers) == 0) == !ring,
              fmt::format("ring buckets {}", BTA::F16kRingBuckets(buffers)));
      F16kOk("R exact journal: neighbour, crossing, K+1 fallback (2 forms), 2 buckets, =0 not written");
    }

    // ---- K: KYTY_FIX_F5CMU at the FCE acquisition (item 492(z)(2)): a 960x540 CMASK target, a B42 hit on a PendingDcc
    // fill of 0 that the bucket check finds stale or not.
    {
      constexpr uint64_t color = base + 0x1000000;
      constexpr uint64_t meta = base + 0x1600000;
      RenderContext context(m_runtime_context);
      auto &scheduler = context.GetCommandScheduler();
      HW::Context registers{};
      HW::UserConfig user_config{};
      HW::Shader shaders{};
      registers.SetColorBase(0, {.addr = color});
      registers.SetColorInfo(0, {.cmask_fast_clear_enable = true,
                                 .format = Prospero::ChannelLayout::k8_8_8_8,
                                 .channel_type = Prospero::ChannelType::kUNorm,
                                 .channel_order = Prospero::ChannelOrder::kStandard});
      registers.SetColorAttrib2(0, {.height = 539, .width = 959});
      registers.SetColorAttrib3(0, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,
                                    .metadata_pipe_aligned = true});
      registers.SetColorCmask(0, {.addr = meta});
      registers.SetColorClearWord0(0, {.word0 = 0xff000000u});
      registers.SetColorClearWord1(0, {.word1 = 0});
      registers.SetRenderTargetMask(0x0f);
      scheduler.Begin(registers, user_config, shaders);
      context.MapMemory(base, allocation_size);
      auto &cache = context.GetTextureCache();
      auto &executor = context.GetRenderExecutor();
      auto &buffers = context.GetBufferCache();
      RenderColorInfo target{};
      RTA::ResolveRenderColorTarget(executor, scheduler.Current(), target, 0);
      Require(name, "K0 target", target.image_id && target.desc.info.metadata.kind == ImageMetadataKind::None,
              "the 960x540 target");
      const auto tid = target.image_id;
      // The test memory was written by the CPU (memset): a read acquisition uploads it, so the stale check below sees
      // GPU writes only (a CPU-modified range is stale by both checks).
      (void)buffers.ObtainBuffer(meta, 0x10000, false, false);
      Require(name, "K0 CPU-clean metadata", !buffers.IsRegionCpuModified(meta, 0x10000),
              "the metadata range is still CPU-modified after a read acquisition");
      // A PendingDcc fill of 0 at `meta`, stamped with its own GPU write (as StampPendingDccFill after the dispatch).
      const auto arm_fill = [&] {
        TTA::F16kEraseMeta(cache, meta);
        cache.TrackDccFill(meta, 0x1000, 0);
        BTA::F16kNoteGpuWrite(buffers, meta, 0x1000);
        cache.StampPendingDccFill();
      };
      struct Case {
        const char *stage;
        int writes; // 0 none, 1 neighbour, 2 crossing, 3 nine neighbours, 4 neighbour + no packed decoding
        const char *fix_on;
        bool applied_on;
        bool applied_off; // the old path
        const char *why_on;
        F16dWant5 counters_on;
      };
      const Case cases[] = {
          {"K1 fresh: no write after the fill", 0, "fresh", true, true, "<none>", {}},
          {"K2 neighbour: bucket stale, exact kept, cleared", 1, "kept_applied", true, false, "<none>",
           {{C::F5CmuKept, 1}, {C::F5CmuKeptApplied, 1}}},
          {"K3 crossing write: stale by both", 2, "exact_stale", false, false, "<none>", {{C::F5CmuExactStale, 1}}},
          {"K4 K+1 neighbours: ring fallback", 3, "fallback", false, false, "<none>", {{C::F5CmuFallback, 1}}},
          {"K5 kept without a clear (decode refused)", 4, "kept", false, false, "decode", {{C::F5CmuKept, 1}}},
      };
      for (const auto &k : cases) {
        arm_fill();
        if (k.writes == 1 || k.writes == 4) {
          BTA::F16kNoteGpuWrite(buffers, meta + 0x1000, 0x100);
        } else if (k.writes == 2) {
          BTA::F16kNoteGpuWrite(buffers, meta + 0x800, 0x100);
        } else if (k.writes == 3) {
          for (uint32_t i = 0; i < 9; i++) {
            BTA::F16kNoteGpuWrite(buffers, meta + 0x2000 + i * 0x100, 0x100);
          }
        }
        auto &image = TTA::F16dImage(cache, tid);
        const auto backing_format = image.backing.format;
        if (k.writes == 4) {
          image.backing.format = vk::Format::eD32Sfloat; // no packed colour decoding (DecodePackedColorClear)
        }
        const auto lines = F16kCount("DiagF5Ev:");
        const auto before = F16kRead();
        RTA::MaterializeColorClears(executor, scheduler.Current());
        image.backing.format = backing_format;
        const bool want_applied = cmu ? k.applied_on : k.applied_off;
        const auto after = cache.QueryMetaFill(meta, tid);
        const bool applied = after.found && after.cmask && after.fill_value == 0 && after.clear_mask != UINT32_MAX;
        Require(name, k.stage, applied == want_applied,
                fmt::format("applied {} != expected {} (fill 0x{:x} mask 0x{:x})", applied, want_applied,
                            after.fill_value, after.clear_mask));
        F16dWant5 want = {{C::CmaskFce, f5 ? 1u : 0u},
                          {want_applied ? C::CmaskFceB42 : C::CmaskFceUnapplied, f5 ? 1u : 0u}};
        for (const auto &[counter, amount] : k.counters_on) {
          want.push_back({counter, cmu && f5 ? amount : 0u});
        }
        for (const auto counter : {C::F5CmuKept, C::F5CmuKeptApplied, C::F5CmuExactStale, C::F5CmuFallback}) {
          if (std::none_of(k.counters_on.begin(), k.counters_on.end(),
                           [&](const auto &p) { return p.first == counter; })) {
            want.push_back({counter, 0});
          }
        }
        want.push_back({C::DccStaleBucketOnly, 0});
        want.push_back({C::DccStaleFallback, 0});
        want.push_back({C::CmaskRtBucketOnly, 0});
        F16kDelta(k.stage, before, want);
        if (f5) {
          const auto line = F16kLast("DiagF5Ev: cmask_fce ");
          Require(name, k.stage,
                  F16kCount("DiagF5Ev:") == lines + 1 && F16kField(line, "fix") == (cmu ? k.fix_on : "off") &&
                      F16kField(line, "applied") == (want_applied ? "1" : "0") &&
                      F16kField(line, "why") == (cmu ? k.why_on : "<none>") &&
                      F16kField(line, "image") == fmt::format("0x{:016x}", color) &&
                      F16kField(line, "cmask") == fmt::format("0x{:016x}", meta) &&
                      F16kField(line, "extent") == "960x540" && F16kField(line, "present") != "<none>" &&
                      F16kField(line, "gpu") != "<none>",
                  "the event line: " + line);
        } else {
          Require(name, k.stage, F16kCount("DiagF5Ev:") == 0, "an event line with KYTY_DIAG_F5 off");
        }
        F16kOk(k.stage);
      }
      // K6: a draw-path acquisition of a CMASK target is not decided by the exact check (item 492(b), V-F16i-1): the
      // bucket answer drops the fill with KYTY_FIX_F5CMU on as well; KYTY_DIAG_F5ID counts cmask_rt_bucket_only.
      {
        auto desc = target.desc;
        desc.info.metadata.kind = ImageMetadataKind::Cmask;
        desc.info.metadata.range = {meta, 0x1000};
        desc.info.metadata.cmask_clear_words = {0xff000000u, 0};
        arm_fill();
        BTA::F16kNoteGpuWrite(buffers, meta + 0x1000, 0x100);
        const auto before = F16kRead();
        (void)cache.FindRenderTarget(tid, desc);
        const auto after = cache.QueryMetaFill(meta, tid);
        Require(name, "K6 draw acquisition", after.found && after.cmask && after.fill_value == 0xffffffffu,
                fmt::format("the fill was kept on a draw acquisition (fill 0x{:x})", after.fill_value));
        F16kDelta("K6 draw acquisition", before,
                  {{C::CmaskRtBucketOnly, id ? 1u : 0u}, {C::F5CmuKept, 0}, {C::F5CmuKeptApplied, 0},
                   {C::F5CmuExactStale, 0}, {C::F5CmuFallback, 0}});
        // The same through PrepareCmaskClear with an event pointer and fce = false: fix=off whatever the knob.
        arm_fill();
        BTA::F16kNoteGpuWrite(buffers, meta + 0x1000, 0x100);
        DiagF5::CmuEvent event{DiagF5::CmuFix::Fresh, DiagF5::CmuWhy::Mask};
        TTA::F16kPrepareCmaskClear(cache, tid, desc, false, &event);
        Require(name, "K6 event of a draw acquisition",
                event.fix == DiagF5::CmuFix::Off && event.why == DiagF5::CmuWhy::None, "fix != off");
        F16kOk("K6 draw acquisition: old decision, cmask_rt_bucket_only only");
      }
      RTA::ResetBindings(executor);
      context.UnmapMemory(base, allocation_size);
      scheduler.Finish();
    }

    // ---- D: F26 at the DCC sites and the reasons of branch 2 (item 492(g)(2), (5))
    {
      constexpr uint64_t color = base;
      constexpr uint64_t dcc = base + 0x400000;
      constexpr uint64_t plain = base + 0x800000;
      constexpr uint64_t pending = base + 0xc00000;
      constexpr uint64_t cmask_entry = base + 0xd00000;
      constexpr uint64_t absent = base + 0xd80000;
      constexpr uint64_t dx_none = base + 0xe00000;
      constexpr uint64_t dx_exact = base + 0xe40000;
      constexpr uint64_t dx_fallback = base + 0xe80000;
      RenderContext context(m_runtime_context);
      LibKernel::Memory::InstallGpuResources(&context);
      auto &scheduler = context.GetCommandScheduler();
      HW::Context registers{};
      HW::UserConfig user_config{};
      HW::Shader shaders{};
      registers.SetColorBase(0, {.addr = color});
      registers.SetColorInfo(0, {.dcc_compression_enable = true,
                                 .format = Prospero::ChannelLayout::k10_10_10_2,
                                 .channel_type = Prospero::ChannelType::kUNorm,
                                 .channel_order = Prospero::ChannelOrder::kStandard});
      registers.SetColorAttrib2(0, {.height = 255, .width = 255});
      registers.SetColorAttrib3(0, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,
                                    .metadata_pipe_aligned = true});
      registers.SetColorDccAddr(0, {.addr = dcc});
      registers.SetColorClearWord0(0, {.word0 = 0});
      registers.SetColorClearWord1(0, {.word1 = 0});
      registers.SetColorBase(2, {.addr = plain});
      registers.SetColorInfo(2, {.format = Prospero::ChannelLayout::k8_8_8_8,
                                 .channel_type = Prospero::ChannelType::kUNorm,
                                 .channel_order = Prospero::ChannelOrder::kStandard});
      registers.SetColorAttrib2(2, {.height = 63, .width = 63});
      registers.SetColorAttrib3(2, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,
                                    .metadata_pipe_aligned = true});
      registers.SetRenderTargetMask(0x0f0fu);
      scheduler.Begin(registers, user_config, shaders);
      context.MapMemory(base, allocation_size);
      auto &cache = context.GetTextureCache();
      auto &executor = context.GetRenderExecutor();
      auto &buffers = context.GetBufferCache();
      RenderColorInfo target{};
      RTA::ResolveRenderColorTarget(executor, scheduler.Current(), target, 0);
      const auto did = target.image_id;
      const auto desc = target.desc;
      const auto msize = desc.info.metadata.range.size;
      Require(name, "D0 DCC target", did && desc.info.metadata.kind == ImageMetadataKind::Dcc && msize >= 0x200 &&
                                         msize <= 0x8000, fmt::format("metadata size 0x{:x}", msize));
      RenderColorInfo plain_target{};
      RTA::ResolveRenderColorTarget(executor, scheduler.Current(), plain_target, 2);
      const auto pid = plain_target.image_id;
      (void)buffers.ObtainBuffer(dcc, 0x10000, false, false);
      (void)buffers.ObtainBuffer(pending, 0x10000, false, false);
      Require(name, "D0 CPU-clean metadata",
              !buffers.IsRegionCpuModified(dcc, 0x10000) && !buffers.IsRegionCpuModified(pending, 0x10000),
              "the metadata ranges are still CPU-modified after a read acquisition");
      const auto stamp_fill = [&](uint64_t address, uint64_t size, uint32_t value) {
        TTA::F16kEraseMeta(cache, address);
        cache.TrackDccFill(address, size, value);
        BTA::F16kNoteGpuWrite(buffers, address, size);
        cache.StampPendingDccFill();
      };
      // D1-D3: PrepareDccClear on a stale PendingDcc fill (the decision is the old one: the fill is dropped)
      {
        auto before = F16kRead();
        stamp_fill(dcc, msize, 0);
        BTA::F16kNoteGpuWrite(buffers, dcc + msize, 0x100);
        TTA::F16dPrepareDccClear(cache, did, desc);
        F16kDelta("D1 PrepareDccClear, neighbour", before,
                  {{C::DccResetStale, f5 ? 1u : 0u}, {C::DccStaleBucketOnly, id ? 1u : 0u}, {C::DccStaleFallback, 0}});
        F16kOk("D1 F26 PrepareDccClear: dcc_stale_bucket_only");
        before = F16kRead();
        stamp_fill(dcc, msize, 0);
        for (uint32_t i = 0; i < 9; i++) {
          BTA::F16kNoteGpuWrite(buffers, dcc + 0x8000 + i * 0x100, 0x100);
        }
        TTA::F16dPrepareDccClear(cache, did, desc);
        F16kDelta("D2 PrepareDccClear, K+1", before,
                  {{C::DccResetStale, f5 ? 1u : 0u}, {C::DccStaleBucketOnly, 0}, {C::DccStaleFallback, id ? 1u : 0u}});
        F16kOk("D2 F26 PrepareDccClear: dcc_stale_fallback");
        before = F16kRead();
        stamp_fill(dcc, msize, 0);
        BTA::F16kNoteGpuWrite(buffers, dcc, 0x10);
        TTA::F16dPrepareDccClear(cache, did, desc);
        F16kDelta("D3 PrepareDccClear, crossing", before,
                  {{C::DccResetStale, f5 ? 1u : 0u}, {C::DccStaleBucketOnly, 0}, {C::DccStaleFallback, 0}});
        F16kOk("D3 F26 PrepareDccClear: crossing - not counted");
      }
      // D4-D10: the reasons of FindDccSurfaceImage / AdoptPendingDccForTexture (a function of the cache state; the
      // pointer is passed by the test in every arm).
      {
        using M = DiagF5Id::Miss;
        DiagF5Id::DccMiss m{};
        const auto check = [&](const char *stage, bool cond, const std::string &what) {
          Require(name, stage, cond, what);
          F16kOk(stage);
        };
        auto before = F16kRead();
        stamp_fill(pending, 0x1000, 0x40404040u);
        BTA::F16kNoteGpuWrite(buffers, pending + 0x1000, 0x100);
        m = {};
        const bool adopted = cache.AdoptPendingDccForTexture(pid, pending, &m);
        F16kDelta("D4 adoption of a stale fill", before,
                  {{C::DccResetStale, f5 ? 1u : 0u}, {C::DccStaleBucketOnly, id ? 1u : 0u}});
        check("D4 F26 adoption: R7, dcc_stale_bucket_only", !adopted && m.why == M::R7, "adoption of a stale fill");
        m = {};
        check("D5 R1 no image", !cache.FindDccSurfaceImage(base + 0x1800000, base + 0x1c00000, &m) && m.why == M::R1,
              "R1");
        m = {};
        check("D6 owner: no reason",
              cache.FindDccSurfaceImage(color, dcc, &m) == did && m.why == M::None, "owner");
        m = {};
        check("D7 R2 a DCC image on another address",
              !cache.FindDccSurfaceImage(color, dcc + 0x100000, &m) && m.why == M::R2 && m.info == dcc, "R2");
        m = {};
        check("D8 R5 no entry", !cache.FindDccSurfaceImage(plain, absent, &m) && m.why == M::R5, "R5");
        TTA::F16dSetCmaskMeta(cache, cmask_entry, 0, 0, 0);
        m = {};
        check("D9 R6 an entry that is not PendingDcc",
              !cache.FindDccSurfaceImage(plain, cmask_entry, &m) && m.why == M::R6 &&
                  m.info == static_cast<uint64_t>(DiagF5Id::MetaType::CMask),
              "R6");
        auto &pimage = TTA::F16dImage(cache, pid);
        pimage.info.metadata.kind = ImageMetadataKind::Cmask;
        m = {};
        const bool r3 = !cache.FindDccSurfaceImage(plain, absent, &m) && m.why == M::R3 &&
                        m.info == static_cast<uint64_t>(ImageMetadataKind::Cmask);
        pimage.info.metadata.kind = ImageMetadataKind::None;
        check("D10 R3 another metadata kind", r3, "R3");
      }
      // D11-D16: branch 2 through the FCE scan: slot 1 = the plain image's base with a DCC address the cache does not
      // know (R5); wr_after none / exact / fallback; the next access target / texture / none with buf_reads / exit with
      // cleared; the sum line and its identities.
      {
        registers.SetColorInfo(1, {.dcc_compression_enable = true,
                                   .format = Prospero::ChannelLayout::k8_8_8_8,
                                   .channel_type = Prospero::ChannelType::kUNorm,
                                   .channel_order = Prospero::ChannelOrder::kStandard});
        registers.SetColorAttrib2(1, {.height = 63, .width = 63});
        registers.SetColorAttrib3(1, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,
                                      .metadata_pipe_aligned = true});
        registers.SetColorBase(1, {.addr = plain});
        const auto scan = [&](uint64_t dcc_address, uint32_t frame) {
          registers.SetColorDccAddr(1, {.addr = dcc_address});
          GpuTimeProfiler::SetFrame(frame);
          RTA::MaterializeColorClears(executor, scheduler.Current());
        };
        BTA::F16kNoteGpuWrite(buffers, dx_exact + 0x10, 0x10);
        for (uint32_t i = 0; i < 9; i++) {
          BTA::F16kNoteGpuWrite(buffers, dx_fallback + 0x2000 + i * 0x100, 0x100);
        }
        const auto fce_lines = F16kCount("DiagF5Id: fce ");
        auto before = F16kRead();
        scan(dx_none, 1000);
        const auto l1 = F16kLast("DiagF5Id: fce ");
        scan(dx_exact, 1000);
        const auto l2 = F16kLast("DiagF5Id: fce ");
        scan(dx_fallback, 1000);
        const auto l3 = F16kLast("DiagF5Id: fce ");
        F16kDelta("D11 three FCE misses", before, {{C::DccFce, f5 ? 6u : 0u}, {C::DccFceNoImage, f5 ? 3u : 0u}});
        if (id) {
          Require(name, "D11 event lines",
                  F16kCount("DiagF5Id: fce ") == fce_lines + 3 && F16kField(l1, "reason") == "r5" &&
                      F16kField(l1, "entry") == "absent" && F16kField(l1, "wr_after") == "none" &&
                      (F16kField(l1, "cpu_mod") == "0" || F16kField(l1, "cpu_mod") == "1") &&
                      F16kField(l1, "dcc_en") == "1" &&
                      F16kField(l1, "base") == fmt::format("0x{:016x}", plain) &&
                      F16kField(l1, "dcc") == fmt::format("0x{:016x}", dx_none) &&
                      F16kField(l1, "dcc_size") == "0x1000" && F16kField(l1, "extent") == "64x64" &&
                      F16kField(l2, "wr_after") == "exact" && F16kField(l3, "wr_after") == "fallback" &&
                      DiagF5Id::Count("r5") == 3 && DiagF5Id::Count("fce") == 3 && DiagF5Id::OpenRecords() == 1,
                  "the fce lines: " + l1 + " | " + l2 + " | " + l3);
        } else {
          Require(name, "D11 nothing with KYTY_DIAG_F5ID off",
                  F16kCount("DiagF5Id: fce ") == 0 && DiagF5Id::Count("fce") == 0 && DiagF5Id::OpenRecords() == 0,
                  "an F5ID event with the knob off");
        }
        F16kOk("D11 branch 2 events: r5, wr_after none/exact/fallback");
        if (id) {
          // target: the record of `plain` (three events merged) is bound by BindRenderTarget, closed by the service
          RTA::F16kBindRenderTarget(executor, pid);
          const bool s1 = DiagF5Id::ServiceAt(1001, false);
          const auto n1 = F16kLast("DiagF5Id: fce_next ");
          Require(name, "D12 kind=target",
                  s1 && F16kField(n1, "kind") == "target" && F16kField(n1, "merged") == "2" &&
                      F16kField(n1, "cleared") == "0" && F16kField(n1, "meta") == "None" &&
                      DiagF5Id::Count("next_target") == 1 && DiagF5Id::OpenRecords() == 0,
                  "fce_next: " + n1);
          F16kOk("D12 fce_next kind=target");
          scan(dx_none, 2000);
          DiagF5Id::NoteBind(plain, DiagF5Id::BindKind::Texture, ImageMetadataKind::Dcc, 0x1234, 2003);
          (void)DiagF5Id::ServiceAt(2004, false);
          const auto n2 = F16kLast("DiagF5Id: fce_next ");
          Require(name, "D13 kind=texture",
                  F16kField(n2, "kind") == "texture" && F16kField(n2, "dframes") == "3" &&
                      F16kField(n2, "meta") == "Dcc@0x1234" && DiagF5Id::Count("next_texture") == 1,
                  "fce_next: " + n2);
          F16kOk("D13 fce_next kind=texture");
          scan(dx_none, 3000);
          DiagF5Id::NoteBufferAccess(plain + 0x10, 0x10);
          DiagF5Id::NoteBufferAccess(plain - 0x100, 0x10); // outside: not counted
          (void)DiagF5Id::ServiceAt(3599, false);
          const bool open_599 = DiagF5Id::OpenRecords() == 1;
          (void)DiagF5Id::ServiceAt(3600, false);
          const auto n3 = F16kLast("DiagF5Id: fce_next ");
          Require(name, "D14 kind=none after 600 frames, buf_reads",
                  open_599 && F16kField(n3, "kind") == "none" && F16kField(n3, "buf_reads") == "1" &&
                      F16kField(n3, "dframes") == "600" && DiagF5Id::Count("next_none") == 1 &&
                      DiagF5Id::Count("next_bufreads") == 1,
                  "fce_next: " + n3);
          F16kOk("D14 fce_next kind=none, buf_reads");
          scan(dx_none, 4000);
          DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::Mat, dx_none, plain, 4001);
          const bool sx = DiagF5Id::ServiceAt(4002, true);
          const auto n4 = F16kLast("DiagF5Id: fce_next ");
          const auto sum = F16kLast("DiagF5Id: sum ");
          Require(name, "D15 kind=exit, cleared, the exit sum line",
                  sx && F16kField(n4, "kind") == "exit" && F16kField(n4, "cleared") == "1" &&
                      DiagF5Id::Count("next_exit") == 1 && DiagF5Id::Count("next_cleared") == 1 &&
                      F16kField(sum, "exit") == "1" && F16kField(sum, "id_fce") == "ok" &&
                      F16kField(sum, "r5") == "6" && F16kField(sum, "dcc_fce_no_image") == "6",
                  "fce_next: " + n4 + " sum: " + sum);
          F16kOk("D15 fce_next kind=exit, cleared; sum id_fce=ok");
          // the key lines of the changed keys follow the sum line
          Require(name, "D16 key lines",
                  F16kCount("DiagF5Id: key site=fce ") >= 3, "no key line of branch 2");
          F16kOk("D16 key lines");
        } else {
          Require(name, "D12 no service with KYTY_DIAG_F5ID off",
                  !DiagF5Id::ServiceAt(5000, false) && !DiagF5Id::ServiceAt(5000, true) &&
                      F16kCount("DiagF5Id:") == (knob && !f5 ? 1u : 0u),
                  "a DiagF5Id line with the knob off");
          F16kOk("D12 no DiagF5Id service with the knob off");
        }
      }
      // D17: the refused entry and the buffer size in the KYTY_DIAG_F5ID side of TryConsumeComputeMetaClear
      {
        cache.TrackDccFill(dcc, msize, 0x20202020u); // the DCC entry of the target (type Dcc after D1-D3)
        ShaderRecompiler::IR::CompiledShaderInfo program{};
        program.stage = ShaderType::Compute;
        ShaderRecompiler::IR::BufferResource resource{};
        resource.read = false;
        resource.written = true;
        resource.formatted = true;
        program.info.buffers.push_back(resource);
        ShaderBufferResource descriptor{};
        descriptor.UpdateAddress48(dcc);
        descriptor.fields[1] |= 16u << 16u;
        descriptor.fields[2] = 8;
        descriptor.fields[3] =
            DstSel(4, 5, 6, 7) | (static_cast<uint32_t>(Prospero::BufferFormat::k32_32_32_32UInt) << 12u);
        ShaderRecompiler::IR::DescriptorValue value{};
        value.dword_count = 4;
        std::copy_n(descriptor.fields, value.dword_count, value.dwords.begin());
        ShaderComputeInputInfo input{};
        input.stage.program = &program;
        input.stage.resources.buffers.push_back(value);
        DiagF5::CsRefusals refusals;
        DiagF5Id::CsDispatch dispatch{};
        const bool consumed =
            RTA::F16kMetaClear(executor, input, scheduler.Current(), f5 ? &refusals : nullptr, &dispatch);
        Require(name, "D17 refused entry",
                !consumed && (f5 ? (refusals.count == 1 && dispatch.before[0].type == DiagF5Id::MetaType::Dcc &&
                                    dispatch.before[0].clear_mask == UINT32_MAX &&
                                    dispatch.before[0].fill_value == 0x20202020u &&
                                    dispatch.sizes[0] == descriptor.GetSize() && !dispatch.reads[0])
                                 : dispatch.before[0].type == DiagF5Id::MetaType::Absent),
                fmt::format("count {} type {} size 0x{:x}", refusals.count,
                            static_cast<uint32_t>(dispatch.before[0].type), dispatch.sizes[0]));
        F16kOk("D17 TryConsumeComputeMetaClear: the refused entry and size");
      }
      RTA::ResetBindings(executor);
      context.UnmapMemory(base, allocation_size);
      scheduler.Finish();
      LibKernel::Memory::InstallGpuResources(nullptr);
    }

    // ---- S: branch 3 through Emit (the classes, sub, vclass, changed, marks, stale_apply) with DiagF5::NoteCsRefusals as
    // DispatchDirect pairs them, then the sum line's id_cs; KYTY_DIAG_F5ID only (the pure calls count with any knob).
    if (id) {
      using K = DiagF5Id::CsClass;
      using MT = DiagF5Id::MetaType;
      constexpr uint64_t a1 = 0x500000000ull; // PendingDcc, mask set
      constexpr uint64_t a2 = 0x500010000ull; // Dcc, mask set
      constexpr uint64_t a3 = 0x500020000ull; // CMask, mask 0
      DiagF5::CsRefusals r;
      r.count = 3;
      r.addresses[0] = a1;
      r.addresses[1] = a2;
      r.addresses[2] = a3;
      const auto make = [&](K outcome, uint64_t tracked, DiagF5Id::CsSub sub, uint32_t value) {
        DiagF5Id::CsDispatch d{};
        d.shader = 0xabcdef;
        d.frame = 5000;
        d.classed = true;
        d.outcome = outcome;
        d.tracked = tracked;
        d.sub = sub;
        d.value = value;
        d.before[0] = {MT::PendingDcc, UINT32_MAX, 0, 0x1000, 3};
        d.before[1] = {MT::Dcc, 1, 0x20202020u, 0x1000, 0};
        d.before[2] = {MT::CMask, 0, 0, 0x1000, 0};
        d.sizes = {0x1000, 0x1000, 0x1000};
        return d;
      };
      const auto get = [](const char *n) { return DiagF5Id::Count(n); };
      const auto c0 = std::array{get("img_clear"), get("meta_clear"), get("tracked"), get("tracked_other"),
                                 get("exec_nofill"), get("exec_fill_clear"), get("exec_fill_other"), get("changed"),
                                 get("changed_na"), get("marks_set"), get("stale_apply"), get("marks_dropped")};
      auto d1 = make(K::ImgClear, 0, DiagF5Id::CsSub::FillShape, 0);
      DiagF5Id::Emit(d1, r);
      DiagF5::NoteCsRefusals(r, 0);
      DiagF5Id::Emit(d1, r); // once only
      auto d2 = make(K::Exec, a2, DiagF5Id::CsSub::NoFill, 0);
      d2.has_after = true;
      d2.after = d2.before;
      DiagF5Id::Emit(d2, r);
      DiagF5::NoteCsRefusals(r, a2);
      auto d3 = make(K::Exec, 0, DiagF5Id::CsSub::NoFill, 0);
      d3.has_after = true;
      d3.after = d3.before;
      DiagF5Id::Emit(d3, r);
      DiagF5::NoteCsRefusals(r, 0);
      auto d4 = make(K::Exec, 0, DiagF5Id::CsSub::FillShape, 0x20202020u);
      d4.has_after = true;
      d4.after = d4.before;
      d4.after[1].clear_mask = 0;
      DiagF5Id::Emit(d4, r);
      DiagF5::NoteCsRefusals(r, 0);
      auto d5 = make(K::Exec, 0, DiagF5Id::CsSub::FillShape, 0x12345678u);
      DiagF5Id::Emit(d5, r); // no snapshot after: changed=na
      DiagF5::NoteCsRefusals(r, 0);
      auto d6 = make(K::MetaClear, 0, DiagF5Id::CsSub::NoFill, 0);
      DiagF5Id::Emit(d6, r);
      DiagF5::NoteCsRefusals(r, 0);
      const auto c1 = std::array{get("img_clear"), get("meta_clear"), get("tracked"), get("tracked_other"),
                                 get("exec_nofill"), get("exec_fill_clear"), get("exec_fill_other"), get("changed"),
                                 get("changed_na"), get("marks_set"), get("stale_apply"), get("marks_dropped")};
      // img_clear 3; tracked 1 + tracked_other 2; exec_nofill 3; fill_shape 0x20202020: a1 (DCC code 20) clear, a2 clear,
      // a3 (CMASK, value != 0) other; fill_shape 0x12345678: 3 other; meta_clear 3. changed: d2-d4 ran with a snapshot
      // after (tracked + tracked_other 3, exec 3, exec 3 with one change) = 1 changed, d5 3 na. Marks: img_clear a1;
      // tracked_other a1; exec a1, a2 (x3 dispatches) = 1 + 1 + 2 * 3 = 8 set.
      const std::array<uint64_t, 12> want{3, 3, 1, 2, 3, 2, 4, 1, 3, 8, 0, 0};
      bool ok = true;
      for (size_t i = 0; i < want.size(); i++) {
        ok &= c1[i] - c0[i] == want[i];
      }
      Require(name, "S1 classes",
              ok && DiagF5Id::Marks() == 2,
              fmt::format("deltas {} {} {} {} {} {} {} {} {} {} marks {}", c1[0] - c0[0], c1[1] - c0[1], c1[2] - c0[2],
                          c1[3] - c0[3], c1[4] - c0[4], c1[5] - c0[5], c1[6] - c0[6], c1[7] - c0[7], c1[8] - c0[8],
                          c1[9] - c0[9], DiagF5Id::Marks()));
      const auto cs_line = F16kLast("DiagF5Id: cs ");
      Require(name, "S1 cs line",
              F16kField(cs_line, "class") == "meta_clear" && F16kField(cs_line, "shader") == "0x0000000000abcdef" &&
                  F16kField(cs_line, "changed") == "-" && F16kField(cs_line, "entry") == "CMask",
              "cs line: " + cs_line);
      F16kOk("S1 branch 3 classes, sub, vclass, changed, marks");
      DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::Mat, a2, 0x600000000ull, 5100);
      const auto st = F16kLast("DiagF5Id: stale_apply ");
      DiagF5Id::NoteFill(a1);
      DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::DccRt, a1, 0x600000000ull, 5101);
      Require(name, "S2 stale_apply",
              get("stale_apply") - c1[10] == 1 && get("marks_dropped") - c1[11] == 1 && DiagF5Id::Marks() == 0 &&
                  F16kField(st, "site") == "mat" && F16kField(st, "addr") == "0x0000000500010000" &&
                  F16kField(st, "class") == "exec" && F16kField(st, "dframes") == "100",
              "stale_apply: " + st);
      F16kOk("S2 stale_apply by a mark, a new fill drops the mark");
      const bool p1 = DiagF5Id::ServiceAt(9000, false);
      const auto sum1 = F16kLast("DiagF5Id: sum ");
      Require(name, "S3 sum line identities",
              p1 && F16kField(sum1, "id_cs") == "ok" && F16kField(sum1, "id_fce") == "ok" &&
                  F16kField(sum1, "exit") == "0",
              "sum: " + sum1);
      F16kOk("S3 sum line: id_cs=ok, id_fce=ok");
      // the rate: a growth 599 frames later prints nothing, 600 frames later prints
      auto d7 = make(K::ImgClear, 0, DiagF5Id::CsSub::NoFill, 0);
      DiagF5Id::Emit(d7, r);
      DiagF5::NoteCsRefusals(r, 0);
      const bool p2 = DiagF5Id::ServiceAt(9599, false);
      const bool p3 = DiagF5Id::ServiceAt(9600, false);
      const bool p4 = DiagF5Id::ServiceAt(10300, false); // no growth
      Require(name, "S4 sum line rate", !p2 && p3 && !p4, fmt::format("{} {} {}", p2, p3, p4));
      F16kOk("S4 sum line: at most once per 600 frames, on growth");
      // the identity detects a class without its DiagF5 counter (a defect of the code would look like this)
      auto d8 = make(K::ImgClear, 0, DiagF5Id::CsSub::NoFill, 0);
      DiagF5Id::Emit(d8, r);
      (void)DiagF5Id::ServiceAt(20000, true);
      const auto sum2 = F16kLast("DiagF5Id: sum ");
      Require(name, "S5 identity violation detected", F16kField(sum2, "id_cs") == "bad", "sum: " + sum2);
      F16kOk("S5 negative control: id_cs=bad without the DiagF5 counter");
    } else {
      Require(name, "S0 knob off",
              DiagF5Id::Count("cs") == 0 && DiagF5Id::Count("fce") == 0 && DiagF5Id::Marks() == 0 &&
                  DiagF5Id::OpenRecords() == 0,
              "a DiagF5Id counter moved with the knob off");
      F16kOk("S0 branch 3: nothing counted with KYTY_DIAG_F5ID off");
    }

    // ---- Z: the counters of an arm without the knob stay 0 over the whole run (item 492(v)(5)-(6))
    {
      const auto g = [](C c) { return DiagF5::Get(c); };
      Require(name, "Z f5cmu_* only with KYTY_FIX_F5CMU and KYTY_DIAG_F5",
              (cmu && f5) || (g(C::F5CmuKept) == 0 && g(C::F5CmuKeptApplied) == 0 && g(C::F5CmuExactStale) == 0 &&
                              g(C::F5CmuFallback) == 0),
              "an f5cmu counter moved");
      Require(name, "Z identity kept_applied <= kept", g(C::F5CmuKeptApplied) <= g(C::F5CmuKept), "kept_applied > kept");
      Require(name, "Z F26 only with KYTY_DIAG_F5ID",
              id || (g(C::DccStaleBucketOnly) == 0 && g(C::DccStaleFallback) == 0 && g(C::CmaskRtBucketOnly) == 0),
              "an F26 counter moved");
      Require(name, "Z lines",
              (cmu || F16kCount("FixF5Cmu:") == 0) && (f5 || F16kCount("DiagF5Ev:") == 0) &&
                  (knob || F16kCount("DiagF5Id:") == 0),
              "a line with its knob off");
      F16kOk("Z counters and lines of the knobs off");
    }
    Require(name, "unmap", Libs::LibKernel::Memory::KernelMunmap(base, allocation_size) == 0, "F16k test unmap failed");
    Require(name, "release",
            Libs::LibKernel::Memory::KernelReleaseDirectMemory(direct, allocation_size) == 0,
            "F16k test release failed");
    std::printf("[f16k]    %-60s ok (%u checks)\n", name, f16k_checks);
  }

  void CheckCmaskRegisterClear() {
'''

t = sub_once(t, r'''  void CheckCmaskRegisterClear() {
''', TEST)

open(PATH, "wb").write(t.encode("utf-8"))
print("patched", PATH)
