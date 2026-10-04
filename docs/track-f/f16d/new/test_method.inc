  // Track F, F16d (HPP-521, ROADMAP s122 items 421(g), 427(g) RC1(b), 433(g)): the test site of KYTY_DIAG_F5 /
  // KYTY_DIAG_F6 without the game. Each scenario drives one site on a synthetic cache state and checks the delta of
  // EVERY counter: with the knob on - the named counters by the named amounts and all others 0 (every branch of set B
  // exactly once, its own counter +1, the neighbours 0, the family identity); with the knob off (unset or "0") - no
  // counter moves and no line is printed. The driver runs the mode three times: KYTY_DIAG_F5 / KYTY_DIAG_F6 unset,
  // =0 and =1.
  struct F16dSnap {
    std::array<uint64_t, static_cast<size_t>(DiagF5::Counter::Count)> f5{};
    std::array<uint64_t, static_cast<size_t>(DiagF6::Counter::Count)> f6{};
  };
  static F16dSnap F16dTake() {
    F16dSnap snap;
    for (uint32_t i = 0; i < snap.f5.size(); i++) {
      snap.f5[i] = DiagF5::Get(static_cast<DiagF5::Counter>(i));
    }
    for (uint32_t i = 0; i < snap.f6.size(); i++) {
      snap.f6[i] = DiagF6::Get(static_cast<DiagF6::Counter>(i));
    }
    return snap;
  }
  using F16dWant5 = std::vector<std::pair<DiagF5::Counter, uint64_t>>;
  using F16dWant6 = std::vector<std::pair<DiagF6::Counter, uint64_t>>;
  inline static uint32_t f16d_checks = 0;
  static void F16dExpect(const char *stage, const F16dSnap &before, const F16dWant5 &want5,
                         const F16dWant6 &want6 = {}) {
    const auto now = F16dTake();
    for (uint32_t i = 0; i < now.f5.size(); i++) {
      uint64_t want = 0;
      if (DiagF5::On()) {
        for (const auto &[counter, amount] : want5) {
          if (static_cast<uint32_t>(counter) == i) {
            want += amount;
          }
        }
      }
      const auto got = now.f5[i] - before.f5[i];
      Require("DiagF5", stage, got == want,
              fmt::format("{}: delta {} != expected {}", DiagF5::Name(static_cast<DiagF5::Counter>(i)), got,
                          want));
    }
    for (uint32_t i = 0; i < now.f6.size(); i++) {
      uint64_t want = 0;
      if (DiagF6::On()) {
        for (const auto &[counter, amount] : want6) {
          if (static_cast<uint32_t>(counter) == i) {
            want += amount;
          }
        }
      }
      const auto got = now.f6[i] - before.f6[i];
      Require("DiagF6", stage, got == want,
              fmt::format("{}: delta {} != expected {}", DiagF6::Name(static_cast<DiagF6::Counter>(i)), got,
                          want));
    }
    f16d_checks++;
    std::printf("[f16d]    %-44s ok\n", stage);
  }
  // The family identities on the absolute values (item 427(g)(1)).
  // `meta_extra` - children of meta_refused_known added by pure calls (no parent) minus parents without a child.
  static void F16dIdentities(const char *stage, uint64_t meta_extra) {
    using C = DiagF5::Counter;
    const auto g = [](C c) { return DiagF5::Get(c); };
    const auto sum = [&](std::initializer_list<C> list) {
      uint64_t s = 0;
      for (const auto c : list) {
        s += g(c);
      }
      return s;
    };
    Require("DiagF5", stage,
            g(C::DccRtPending) == sum({C::DccRtCleared, C::DccRtSkipLevels, C::DccRtSkipPartial,
                                       C::DccRtSkipDecode, C::DccRtSkipLayers}) &&
                g(C::DccMatPending) == sum({C::DccMatCleared, C::DccMatUndecoded}) &&
                g(C::DccFce) == sum({C::DccFceImage, C::DccFceNoImage}) &&
                g(C::DccFillMeta) == sum({C::DccFillClear, C::DccFillUncompressed, C::DccFillUnknown}) &&
                g(C::MetaRefusedKnown) + meta_extra ==
                    sum({C::MetaCsTracked, C::MetaCsUntracked, C::MetaDmaUntracked, C::MetaDmaNoClear}) &&
                g(C::CmaskRtPending) == sum({C::CmaskRtCleared, C::CmaskRtSkipValue, C::CmaskRtSkipPartial,
                                             C::CmaskRtSkipDecode, C::CmaskRtSkipLayers}) &&
                g(C::CmaskFce) == sum({C::CmaskFceNoImage, C::CmaskFceMeta, C::CmaskFceMsaa, C::CmaskFceLayout,
                                       C::CmaskFceNoFill, C::CmaskFceDrawn, C::CmaskFceB42,
                                       C::CmaskFceUnapplied}) &&
                g(C::DccRt) <= g(C::RtResolves),
            "a family identity of DiagF5 is broken");
    using D = DiagF6::Counter;
    const auto h = [](D d) { return DiagF6::Get(d); };
    Require("DiagF6", stage,
            h(D::SBound) + h(D::SAddr0Fmt) + h(D::SAddr0NoFmt) + h(D::SMask0Addr) + h(D::SEmpty) ==
                    8 * h(D::Draws) &&
                h(D::HBound) + h(D::BoundMissing) == h(D::SBound) + h(D::BoundExtra) &&
                h(D::WTotal) == h(D::WBound) + h(D::WMask0) + h(D::WAddr0Fmt) + h(D::WAddr0NoFmt) + h(D::WGe8) &&
                h(D::DrawsIdx) + h(D::DrawsAuto) + h(D::DrawsInd) + h(D::DrawsMesh) == h(D::Draws) &&
                h(D::PsDraws) <= h(D::Draws),
            "an identity of DiagF6 is broken");
    std::printf("[f16d]    %-44s ok\n", stage);
  }

  void CheckDiagF5F6() {
    constexpr const char *name = "DiagF5F6";
    using C = DiagF5::Counter;
    const bool want5 = Common::EnvValueOn(std::getenv("KYTY_DIAG_F5"));
    const bool want6 = Common::EnvValueOn(std::getenv("KYTY_DIAG_F6"));
    Require(name, "knob read", DiagF5::On() == want5 && DiagF6::On() == want6,
            "DiagF5::On / DiagF6::On do not follow KYTY_DIAG_F5 / KYTY_DIAG_F6 (unset or \"\" or 0 = OFF)");
    std::printf("[f16d]    knobs: KYTY_DIAG_F5=%d KYTY_DIAG_F6=%d\n", DiagF5::On() ? 1 : 0, DiagF6::On() ? 1 : 0);

    // ---- pure helpers
    Require(name, "ViewLayerBits",
            DiagF5::ViewLayerBits(0, 1) == 1u && DiagF5::ViewLayerBits(3, 2) == 0x18u &&
                DiagF5::ViewLayerBits(0, 32) == UINT32_MAX && DiagF5::ViewLayerBits(31, 1) == 0x80000000u &&
                DiagF5::ViewLayerBits(32, 1) == UINT32_MAX && DiagF5::ViewLayerBits(30, 3) == UINT32_MAX &&
                DiagF5::ViewLayerBits(5, 0) == 0u,
            "view layer bits");
    Require(name, "DccFillClassOf",
            DiagF5::DccFillClassOf(0) == DiagF5::FillClass::Clear &&
                DiagF5::DccFillClassOf(0x20202020u) == DiagF5::FillClass::Clear &&
                DiagF5::DccFillClassOf(0x40404040u) == DiagF5::FillClass::Clear &&
                DiagF5::DccFillClassOf(0x80808080u) == DiagF5::FillClass::Clear &&
                DiagF5::DccFillClassOf(0xc0c0c0c0u) == DiagF5::FillClass::Clear &&
                DiagF5::DccFillClassOf(0xffffffffu) == DiagF5::FillClass::Uncompressed &&
                DiagF5::DccFillClassOf(0x41414141u) == DiagF5::FillClass::Unknown &&
                DiagF5::DccFillClassOf(0x00000040u) == DiagF5::FillClass::Unknown &&
                DiagF5::DccFillClassOf(0x3f800000u) == DiagF5::FillClass::Unknown,
            "the classification of TrackDccFill");
    {
      auto before = F16dTake();
      DiagF5::CsRefusals refusals;
      refusals.count = 2;
      refusals.addresses[0] = 0x1000;
      refusals.addresses[1] = 0x2000;
      if (DiagF5::On()) {
        DiagF5::NoteCsRefusals(refusals, 0x2000);
      }
      F16dExpect("cs refusals: one tracked, one not", before, {{C::MetaCsTracked, 1}, {C::MetaCsUntracked, 1}});
      before = F16dTake();
      if (DiagF5::On()) {
        DiagF5::NoteCsRefusals(refusals, 0);
      }
      F16dExpect("cs refusals: none tracked", before, {{C::MetaCsUntracked, 2}});
      before = F16dTake();
      if (DiagF5::On()) {
        DiagF5::NoteDmaRefusal(DiagF5::RefusalDcc, 0x40404040u);
        DiagF5::NoteDmaRefusal(DiagF5::RefusalDcc, 0xffffffffu);
        DiagF5::NoteDmaRefusal(DiagF5::RefusalCmask, 0);
        DiagF5::NoteDmaRefusal(DiagF5::RefusalCmask, 5);
        DiagF5::NoteDmaRefusal(DiagF5::RefusalNone, 0);
      }
      F16dExpect("dma refusal classes", before, {{C::MetaDmaUntracked, 2}, {C::MetaDmaNoClear, 2}});
    }

    // ---- DiagF6: a synthetic draw state (item 433(g)): a slot of every class, an export into every class
    {
      using D = DiagF6::Counter;
      HW::Context hw{};
      const auto fmt8888 = Prospero::ChannelLayout::k8_8_8_8;
      hw.SetColorBase(0, {.addr = 0x0000000300000000ull});
      hw.SetColorInfo(0, {.format = fmt8888});
      hw.SetColorBase(1, {.addr = 0});
      hw.SetColorInfo(1, {.format = fmt8888});
      hw.SetColorBase(2, {.addr = 0});
      hw.SetColorInfo(2, {.format = Prospero::ChannelLayout::kInvalid});
      hw.SetColorBase(3, {.addr = 0x0000000300100000ull});
      hw.SetColorInfo(3, {.format = fmt8888});
      hw.SetRenderTargetMask(0x0fffu); // slots 0-2 masked on, slot 3 masked off (base set), 4-7 empty
      const uint32_t host_ok[] = {0};
      const uint32_t host_extra[] = {0, 3};
      const uint32_t mrt[] = {0, 1, 2, 3, 4, 9};
      const F16dWant6 slots_once = {{D::SBound, 1}, {D::SAddr0Fmt, 1}, {D::SAddr0NoFmt, 1}, {D::SMask0Addr, 1},
                                    {D::SEmpty, 4}};
      const F16dWant6 writes = {{D::PsDraws, 1}, {D::WTotal, 6}, {D::WBound, 1}, {D::WAddr0Fmt, 1},
                                {D::WAddr0NoFmt, 1}, {D::WMask0, 2}, {D::WGe8, 1}};
      const auto plus = [](F16dWant6 a, const F16dWant6 &b) {
        a.insert(a.end(), b.begin(), b.end());
        return a;
      };
      const std::pair<DiagF6::DrawKind, D> kinds[] = {{DiagF6::DrawKind::Indexed, D::DrawsIdx},
                                                      {DiagF6::DrawKind::Auto, D::DrawsAuto},
                                                      {DiagF6::DrawKind::Indirect, D::DrawsInd},
                                                      {DiagF6::DrawKind::Mesh, D::DrawsMesh}};
      for (const auto &[kind, counter] : kinds) {
        const auto before = F16dTake();
        DiagF6::NoteDraw(hw, host_ok, 1, true, mrt, 6, kind);
        F16dExpect(fmt::format("f6 draw kind {} with ps", static_cast<uint32_t>(kind)).c_str(), before, {},
                   plus(plus({{D::Draws, 1}, {counter, 1}, {D::HBound, 1}}, slots_once), writes));
      }
      auto before = F16dTake();
      DiagF6::NoteDraw(hw, host_ok, 1, false, mrt, 6, DiagF6::DrawKind::Indexed);
      F16dExpect("f6 draw without ps: no export counted", before, {},
                 plus({{D::Draws, 1}, {D::DrawsIdx, 1}, {D::HBound, 1}}, slots_once));
      before = F16dTake();
      DiagF6::NoteDraw(hw, host_extra, 2, false, nullptr, 0, DiagF6::DrawKind::Auto);
      F16dExpect("f6 bound_extra (slot 3 bound, mask 0)", before, {},
                 plus({{D::Draws, 1}, {D::DrawsAuto, 1}, {D::HBound, 2}, {D::BoundExtra, 1}}, slots_once));
      before = F16dTake();
      DiagF6::NoteDraw(hw, nullptr, 0, false, nullptr, 0, DiagF6::DrawKind::Mesh);
      F16dExpect("f6 bound_missing (slot 0 not bound)", before, {},
                 plus({{D::Draws, 1}, {D::DrawsMesh, 1}, {D::BoundMissing, 1}}, slots_once));
      F16dIdentities("identities after the pure calls", DiagF5::On() ? 8 : 0);
    }

    // ---- the flip tick and the mode line (item 427(e))
    {
      const auto line = DiagF5::FormatLine(7);
      Require(name, "line form",
              line.rfind("DiagF5: frame=7 rt_resolves=", 0) == 0 && line.find(" zero_disp=") != std::string::npos &&
                  DiagF6::FormatLine(7).rfind("DiagF6: frame=7 draws=", 0) == 0 &&
                  DiagF6::FormatLine(7).find(" w_ge8=") != std::string::npos,
              "the line names every counter");
      const bool first5 = DiagF5::LogMode();
      const bool second5 = DiagF5::LogMode();
      const bool first6 = DiagF6::LogMode();
      const bool second6 = DiagF6::LogMode();
      Require(name, "mode line once",
              !second5 && !second6 && (DiagF5::On() || !first5) && (DiagF6::On() || !first6),
              "the mode line is printed more than once, or with the knob off");
      // Counters grew above with the knob on (NoteCsRefusals, NoteDraw): the first tick prints, a tick < 2 s later
      // with a growth does not, a tick >= 2 s later with a growth does, a tick without a growth does not.
      const bool t1 = DiagF5::TickAt(1, 100000);
      if (DiagF5::On()) {
        DiagF5::NoteDmaRefusal(DiagF5::RefusalCmask, 0);
      }
      const bool t2 = DiagF5::TickAt(2, 101999);
      const bool t3 = DiagF5::TickAt(3, 102000);
      const bool t4 = DiagF5::TickAt(4, 200000);
      const bool u1 = DiagF6::TickAt(1, 100000);
      const bool u2 = DiagF6::TickAt(2, 300000);
      Require(name, "tick",
              DiagF5::On() ? (t1 && !t2 && t3 && !t4) : (!t1 && !t2 && !t3 && !t4),
              fmt::format("DiagF5 tick {} {} {} {}", t1, t2, t3, t4));
      Require(name, "tick f6", DiagF6::On() ? (u1 && !u2) : (!u1 && !u2),
              fmt::format("DiagF6 tick {} {}", u1, u2));
      std::printf("[f16d]    %-44s ok (mode line first call: f5=%d f6=%d)\n", "tick and mode line", first5 ? 1 : 0,
                  first6 ? 1 : 0);
    }

    EnsureRuntimeContext();
    constexpr uintptr_t base = 0x0000000207000000ull;
    constexpr uint64_t allocation_size = 0x2000000;
    int64_t direct = -1;
    Require(name, "allocate",
            Libs::LibKernel::Memory::KernelAllocateDirectMemory(
                0, Libs::LibKernel::Memory::KernelGetDirectMemorySize(), allocation_size, 0x10000, 0, &direct) == 0,
            "F16d test allocation failed");
    void *mapped = reinterpret_cast<void *>(base);
    Require(name, "map",
            Libs::LibKernel::Memory::KernelMapDirectMemory(&mapped, allocation_size, 3, 0x10, direct, 0x10000) == 0 &&
                mapped == reinterpret_cast<void *>(base),
            "F16d test mapping failed");
    std::memset(mapped, 0x5a, allocation_size);

    // ---- A: a DCC colour target (PrepareDccClear, MaterializeDeferredDccClear, the DCC FCE scan, fills, ClearMeta)
    {
      constexpr uint64_t color = base;
      constexpr uint64_t dcc = base + 0x400000;
      constexpr uint64_t plain = base + 0x800000;
      constexpr uint64_t pending = base + 0xc00000;
      constexpr uint64_t cmask_entry = base + 0xd00000;
      constexpr uint64_t other_entry = base + 0xe00000;
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

      auto before = F16dTake();
      RenderColorInfo target{};
      RenderExecutorTestAccess::ResolveRenderColorTarget(executor, scheduler.Current(), target, 0);
      F16dExpect("A0 resolve DCC target", before, {{C::RtResolves, 1}, {C::DccRt, 1}});
      Require(name, "A0 descriptor",
              target.image_id && target.desc.info.metadata.kind == ImageMetadataKind::Dcc &&
                  target.desc.info.metadata.range.address == dcc && target.desc.info.metadata.range.size >= 0x200,
              "the DCC target was not resolved with its metadata");
      const auto id = target.image_id;
      const auto desc = target.desc;
      const auto msize = desc.info.metadata.range.size;
      const F16dWant5 fill_clear = {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1}};

      before = F16dTake();
      cache.TrackDccFill(dcc, msize, 0);
      F16dExpect("A1 fill of an unknown address (PendingDcc)", before, {{C::DccFillAll, 1}});
      before = F16dTake();
      (void)cache.FindRenderTarget(id, desc);
      F16dExpect("A2 PendingDcc -> Dcc, render-target clear", before,
                 {{C::DccFillMeta, 1}, {C::DccFillClear, 1}, {C::DccRtPending, 1}, {C::DccRtCleared, 1}});

      before = F16dTake();
      cache.TrackDccFill(dcc, msize / 2, 0);
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, desc);
      F16dExpect("A3 B dcc_rt_skip_partial", before, {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1},
                                                    {C::DccRtPending, 1}, {C::DccRtSkipPartial, 1}});

      before = F16dTake();
      cache.TrackDccFill(dcc, msize, 0);
      TextureCacheTestAccess::F16dImage(cache, id).info.resources.levels = 2;
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, desc);
      TextureCacheTestAccess::F16dImage(cache, id).info.resources.levels = 1;
      F16dExpect("A4 B dcc_rt_skip_levels", before, {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1},
                                                   {C::DccRtPending, 1}, {C::DccRtSkipLevels, 1}});

      before = F16dTake();
      auto no_register = desc;
      no_register.info.metadata.dcc_clear_register_valid = false;
      cache.TrackDccFill(dcc, msize, 0x20202020u);
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, no_register);
      F16dExpect("A5 B dcc_rt_skip_decode", before, {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1},
                                                   {C::DccRtPending, 1}, {C::DccRtSkipDecode, 1}});

      before = F16dTake();
      auto far_layer = desc;
      far_layer.view_info.base_layer = 32;
      far_layer.view_info.layer_count = 1;
      cache.TrackDccFill(dcc, msize, 0);
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, far_layer);
      F16dExpect("A6 B dcc_rt_skip_layers", before, {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1},
                                                   {C::DccRtPending, 1}, {C::DccRtSkipLayers, 1}});

      before = F16dTake();
      auto sampled = desc;
      sampled.type = BindingType::Texture;
      cache.TrackDccFill(dcc, msize / 2, 0);
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, sampled);
      F16dExpect("A7 texture path: no dcc_rt_* (RC4)", before, fill_clear);

      before = F16dTake();
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, desc);
      F16dExpect("A7b render target, partial fill again", before,
                 {{C::DccRtPending, 1}, {C::DccRtSkipPartial, 1}});

      before = F16dTake();
      cache.TrackDccFill(dcc, msize, 0xffffffffu);
      F16dExpect("A8 fill 0xff (uncompressed)", before,
                 {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillUncompressed, 1}});
      before = F16dTake();
      cache.TrackDccFill(dcc, msize, 0x12345678u);
      F16dExpect("A8b B dcc_fill_unknown", before,
                 {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillUnknown, 1}});
      before = F16dTake();
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, desc);
      F16dExpect("A8c unknown code: nothing pending", before, {});

      before = F16dTake();
      cache.TrackDccFill(dcc, msize, 0x20202020u);
      registers.SetColorDccAddr(0, {.addr = dcc + 0x100000});
      RenderExecutorTestAccess::F16dMaterialize(executor, scheduler.Current(), id);
      F16dExpect("A9 B dcc_mat_undecoded", before,
                 {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1}, {C::DccMatPending, 1},
                  {C::DccMatUndecoded, 1}});
      registers.SetColorDccAddr(0, {.addr = dcc});
      before = F16dTake();
      cache.TrackDccFill(dcc, msize, 0);
      RenderExecutorTestAccess::F16dMaterialize(executor, scheduler.Current(), id);
      F16dExpect("A9b materialized (code 00)", before,
                 {{C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1}, {C::DccMatPending, 1},
                  {C::DccMatCleared, 1}});
      before = F16dTake();
      RenderExecutorTestAccess::F16dMaterialize(executor, scheduler.Current(), id);
      F16dExpect("A9c nothing pending", before, {});

      before = F16dTake();
      registers.SetColorBase(1, {.addr = base + 0x1800000});
      registers.SetColorDccAddr(1, {.addr = base + 0x1c00000});
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      registers.SetColorBase(1, {.addr = 0});
      registers.SetColorDccAddr(1, {.addr = 0});
      F16dExpect("A10 FCE scan: DCC slot with image, B dcc_fce_no_image", before,
                 {{C::DccFce, 2}, {C::DccFceImage, 1}, {C::DccFceNoImage, 1}});

      before = F16dTake();
      TextureCacheTestAccess::F16dSetCmaskMeta(cache, other_entry, 0, 0, 0);
      auto other = desc;
      other.info.metadata.range.address = other_entry;
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, other);
      TextureCacheTestAccess::F16dPrepareDccClear(cache, id, desc);
      F16dExpect("A11 entry of another type reset (reference)", before, {{C::DccResetType, 1}});

      before = F16dTake();
      RenderColorInfo plain_target{};
      RenderExecutorTestAccess::ResolveRenderColorTarget(executor, scheduler.Current(), plain_target, 2);
      cache.TrackDccFill(pending, 0x1000, 0x40404040u);
      const bool adopted = cache.AdoptPendingDccForTexture(plain_target.image_id, pending);
      F16dExpect("A12 adoption PendingDcc -> Dcc for a texture", before,
                 {{C::RtResolves, 1}, {C::DccFillAll, 1}, {C::DccFillMeta, 1}, {C::DccFillClear, 1}});
      Require(name, "A12 adopted", adopted, "the pending fill was not adopted");

      before = F16dTake();
      TextureCacheTestAccess::F16dSetCmaskMeta(cache, cmask_entry, 0, 0, 0);
      uint8_t k_dcc = DiagF5::RefusalNone;
      uint8_t k_cmask = DiagF5::RefusalNone;
      uint8_t k_none = DiagF5::RefusalNone;
      const bool r_dcc = cache.ClearMeta(dcc, &k_dcc);
      const bool r_cmask = cache.ClearMeta(cmask_entry, &k_cmask);
      const bool r_none = cache.ClearMeta(base + 0x1f00000, &k_none);
      F16dExpect("A13 ClearMeta refusals of known metadata", before, {{C::MetaRefusedKnown, 2}});
      Require(name, "A13 kinds",
              !r_dcc && !r_cmask && !r_none && k_none == DiagF5::RefusalNone &&
                  (DiagF5::On() ? (k_dcc == DiagF5::RefusalDcc && k_cmask == DiagF5::RefusalCmask)
                                : (k_dcc == DiagF5::RefusalNone && k_cmask == DiagF5::RefusalNone)),
              "ClearMeta's answer or refusal kind");

      before = F16dTake();
      auto &buffers = context.GetBufferCache();
      buffers.FillBuffer(dcc, 0x100, 0x40404040u, false);
      buffers.FillBuffer(dcc, 0x100, 0xffffffffu, false);
      buffers.FillBuffer(cmask_entry, 0x100, 0, false);
      buffers.FillBuffer(cmask_entry, 0x100, 5, false);
      buffers.FillBuffer(base + 0x1f00000, 0x100, 0, false);
      F16dExpect("A14 DMA fill: B meta_dma_untracked x2, noclear x2", before,
                 {{C::MetaRefusedKnown, 4}, {C::MetaDmaUntracked, 2}, {C::MetaDmaNoClear, 2}});

      before = F16dTake();
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
      const bool consumed =
          RenderExecutorTestAccess::F16dMetaClear(executor, input, scheduler.Current(), &refusals);
      F16dExpect("A15 compute write refused (the parent in ClearMeta)", before, {{C::MetaRefusedKnown, 1}});
      Require(name, "A15 list",
              !consumed && (DiagF5::On() ? (refusals.count == 1 && refusals.addresses[0] == dcc) : refusals.count == 0),
              "the refused address was not handed to the dispatch");
      before = F16dTake();
      if (DiagF5::On()) {
        DiagF5::NoteCsRefusals(refusals, 0);
      }
      F16dExpect("A15b B meta_cs_untracked", before, {{C::MetaCsUntracked, 1}});
      before = F16dTake();
      if (DiagF5::On()) {
        DiagF5::NoteCsRefusals(refusals, dcc);
      }
      F16dExpect("A15c meta_cs_tracked", before, {{C::MetaCsTracked, 1}});

      RenderExecutorTestAccess::ResetBindings(executor);
      context.UnmapMemory(base, allocation_size);
      scheduler.Finish();
      LibKernel::Memory::InstallGpuResources(nullptr);
    }

    // ---- B: a 1024x1024 CMASK target (PrepareCmaskClear; the FCE scan on a target with CMASK metadata)
    {
      constexpr uint64_t color = base + 0x1000000;
      constexpr uint64_t meta = base + 0x1800000;
      RenderContext context(m_runtime_context);
      auto &scheduler = context.GetCommandScheduler();
      HW::Context registers{};
      HW::UserConfig user_config{};
      HW::Shader shaders{};
      registers.SetColorBase(0, {.addr = color});
      registers.SetColorInfo(0, {.cmask_fast_clear_enable = true,
                                 .format = Prospero::ChannelLayout::k16_16_16_16,
                                 .channel_type = Prospero::ChannelType::kFloat,
                                 .channel_order = Prospero::ChannelOrder::kStandard});
      registers.SetColorAttrib2(0, {.height = 1023, .width = 1023});
      registers.SetColorAttrib3(0, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,
                                    .metadata_pipe_aligned = true});
      registers.SetColorCmask(0, {.addr = meta});
      registers.SetColorClearWord0(0, {.word0 = 0x38003800});
      registers.SetColorClearWord1(0, {.word1 = 0x00005650});
      registers.SetRenderTargetMask(0x0f);
      scheduler.Begin(registers, user_config, shaders);
      context.MapMemory(base, allocation_size);
      auto &cache = context.GetTextureCache();
      auto &executor = context.GetRenderExecutor();

      auto before = F16dTake();
      RenderColorInfo target{};
      RenderExecutorTestAccess::ResolveRenderColorTarget(executor, scheduler.Current(), target, 0);
      F16dExpect("B0 resolve CMASK target", before, {{C::RtResolves, 1}});
      Require(name, "B0 descriptor",
              target.image_id && target.desc.info.metadata.kind == ImageMetadataKind::Cmask &&
                  target.desc.info.metadata.range.size == 0x2000,
              "the CMASK target was not resolved with its metadata");
      const auto id = target.image_id;
      const auto desc = target.desc;

      before = F16dTake();
      cache.TrackDccFill(meta, 0x2000, 0);
      (void)cache.FindRenderTarget(id, desc);
      F16dExpect("B1 CMASK clear", before, {{C::DccFillAll, 1}, {C::CmaskRtPending, 1}, {C::CmaskRtCleared, 1}});

      before = F16dTake();
      cache.TrackDccFill(meta, 0x1000, 0);
      TextureCacheTestAccess::F16dPrepareCmaskClear(cache, id, desc);
      F16dExpect("B2 B cmask_rt_skip_partial", before,
                 {{C::DccFillAll, 1}, {C::CmaskRtPending, 1}, {C::CmaskRtSkipPartial, 1}});

      before = F16dTake();
      cache.TrackDccFill(meta, 0x2000, 0);
      auto &image = TextureCacheTestAccess::F16dImage(cache, id);
      const auto backing_format = image.backing.format;
      image.backing.format = vk::Format::eD32Sfloat; // no packed colour decoding for it (DecodePackedColorClear)
      TextureCacheTestAccess::F16dPrepareCmaskClear(cache, id, desc);
      image.backing.format = backing_format;
      F16dExpect("B3 B cmask_rt_skip_decode", before,
                 {{C::DccFillAll, 1}, {C::CmaskRtPending, 1}, {C::CmaskRtSkipDecode, 1}});

      before = F16dTake();
      auto mip_view = desc;
      mip_view.view_info.base_level = 1;
      TextureCacheTestAccess::F16dPrepareCmaskClear(cache, id, mip_view);
      F16dExpect("B4 B cmask_rt_skip_layers", before, {{C::CmaskRtPending, 1}, {C::CmaskRtSkipLayers, 1}});

      before = F16dTake();
      TextureCacheTestAccess::F16dSetCmaskMeta(cache, meta, 1, UINT32_MAX, 0x2000);
      TextureCacheTestAccess::F16dPrepareCmaskClear(cache, id, desc);
      F16dExpect("B5 B cmask_rt_skip_value", before, {{C::CmaskRtPending, 1}, {C::CmaskRtSkipValue, 1}});

      before = F16dTake();
      TextureCacheTestAccess::F16dSetCmaskMeta(cache, meta, 0, 0, 0x2000);
      TextureCacheTestAccess::F16dPrepareCmaskClear(cache, id, desc);
      F16dExpect("B6 nothing pending", before, {});

      before = F16dTake();
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      F16dExpect("B7 FCE scan: CMASK target with metadata", before,
                 {{C::CmaskFce, 1}, {C::RtResolves, 1}, {C::CmaskFceMeta, 1}});

      RenderExecutorTestAccess::ResetBindings(executor);
      context.UnmapMemory(base, allocation_size);
      scheduler.Finish();
    }

    // ---- C: the FCE scan on CMASK targets without metadata (B42 class, MSAA, volume)
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

      auto before = F16dTake();
      RenderColorInfo target{};
      RenderExecutorTestAccess::ResolveRenderColorTarget(executor, scheduler.Current(), target, 0);
      F16dExpect("C0 resolve 960x540 CMASK target", before, {{C::RtResolves, 1}});
      Require(name, "C0 descriptor",
              target.image_id && target.desc.info.metadata.kind == ImageMetadataKind::None,
              "the 960x540 target got metadata");
      const auto id = target.image_id;

      before = F16dTake();
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      F16dExpect("C1 B cmask_fce_nofill", before, {{C::CmaskFce, 1}, {C::RtResolves, 1}, {C::CmaskFceNoFill, 1}});

      before = F16dTake();
      cache.TrackDccFill(meta, 0x1000, 0);
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      F16dExpect("C2 B42 hit applied", before,
                 {{C::DccFillAll, 1}, {C::CmaskFce, 1}, {C::CmaskRtPending, 1}, {C::CmaskRtCleared, 1},
                  {C::CmaskFceB42, 1}});

      before = F16dTake();
      cache.TrackDccFill(meta, 0x1000, 0);
      (void)cache.FindRenderTarget(id, target.desc);
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      F16dExpect("C3 B42 drawn (reference)", before, {{C::DccFillAll, 1}, {C::CmaskFce, 1}, {C::CmaskFceDrawn, 1}});

      before = F16dTake();
      cache.TrackDccFill(meta, 0x1000, 0);
      auto &image = TextureCacheTestAccess::F16dImage(cache, id);
      const auto backing_format = image.backing.format;
      image.backing.format = vk::Format::eD32Sfloat;
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      image.backing.format = backing_format;
      F16dExpect("C4 B cmask_fce_unapplied", before,
                 {{C::DccFillAll, 1}, {C::CmaskFce, 1}, {C::CmaskRtPending, 1}, {C::CmaskRtSkipDecode, 1},
                  {C::CmaskFceUnapplied, 1}});

      registers.SetColorBase(0, {.addr = 0});
      registers.SetColorBase(1, {.addr = base + 0x1200000});
      registers.SetColorInfo(1, {.cmask_fast_clear_enable = true,
                                 .format = Prospero::ChannelLayout::k8_8_8_8,
                                 .channel_type = Prospero::ChannelType::kUNorm,
                                 .channel_order = Prospero::ChannelOrder::kStandard});
      registers.SetColorAttrib(1, {.num_samples = 2, .num_fragments = 2});
      registers.SetColorAttrib2(1, {.height = 127, .width = 127});
      registers.SetColorAttrib3(1, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,
                                    .metadata_pipe_aligned = true});
      registers.SetColorCmask(1, {.addr = base + 0x1700000});
      before = F16dTake();
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      F16dExpect("C5 B cmask_fce_msaa", before, {{C::CmaskFce, 1}, {C::RtResolves, 1}, {C::CmaskFceMsaa, 1}});

      registers.SetColorBase(1, {.addr = 0});
      registers.SetColorBase(2, {.addr = base + 0x1400000});
      registers.SetColorInfo(2, {.cmask_fast_clear_enable = true,
                                 .format = Prospero::ChannelLayout::k8_8_8_8,
                                 .channel_type = Prospero::ChannelType::kUNorm,
                                 .channel_order = Prospero::ChannelOrder::kStandard});
      registers.SetColorAttrib2(2, {.height = 31, .width = 31});
      registers.SetColorAttrib3(2, {.depth = 31, .tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 2,
                                    .metadata_pipe_aligned = true});
      registers.SetColorCmask(2, {.addr = base + 0x1780000});
      before = F16dTake();
      RenderExecutorTestAccess::MaterializeColorClears(executor, scheduler.Current());
      F16dExpect("C6 cmask_fce_layout (volume)", before,
                 {{C::CmaskFce, 1}, {C::RtResolves, 1}, {C::CmaskFceLayout, 1}});

      RenderExecutorTestAccess::ResetBindings(executor);
      context.UnmapMemory(base, allocation_size);
      scheduler.Finish();
    }
    Require(name, "unmap", Libs::LibKernel::Memory::KernelMunmap(base, allocation_size) == 0, "F16d test unmap failed");
    Require(name, "release",
            Libs::LibKernel::Memory::KernelReleaseDirectMemory(direct, allocation_size) == 0,
            "F16d test release failed");
    // A13 adds 2 parents without a child; the pure CS / DMA calls (2 + 2 + 4), the tick (1) and A15c (1) add 10
    // children without a parent: children - parents = 8 beyond the balanced sites.
    F16dIdentities("identities after all scenarios", DiagF5::On() ? 8 : 0);
    std::printf("[f16d]    %-44s ok (%u checks)\n", name, f16d_checks);
  }
