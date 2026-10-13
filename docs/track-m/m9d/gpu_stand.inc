  // Track M, M9d (HPP-869, ROADMAP s122 item 785(d)): the GPU stand of KYTY_DIAG_T188 (--t188-gpu-stand), on the real
  // Vulkan device of this harness. Members (each prints "T188Gpu: member=<name> ... ok=<0|1>"):
  //   tint_<fmt>_l<layers>_t<l>  T188Gpu::TintLevels of level l (0 or 1 of 3) of an image whose levels were uploaded with
  //       their own colours: level l of every layer = the magenta code of the format, the other levels unchanged, the
  //       readback of the same call (rb0) magenta (mutants g1 baseMipLevel + 1, g2 layerCount 1, g3 readback before the
  //       clear; g4 - clear without the transition - is caught by the validation layer, see the driver);
  //   sw_first   Image::MarkGpuModified on a real Image: transition, full synchronization, a second call - wseq != sseq
  //       (m13: the stamp inside the transition branch);
  //   ovr        DB_RENDER_OVERRIDE through the real PM4 handlers: a range write 0x1-0x4 from DB_COUNT_CONTROL, a direct
  //       one and an indirect one count once each (m15: the count in the packet handler by its first register);
  //   s7         S2 then MarkGpuWritten through a real TextureCache: ep_new 1, cl_commit 1, lock_bad 0;
  //   rc12       a tinted (mode 3) tiled texture re-uploaded without an episode in a later frame: tint_rb0_ok 1,
  //       tint_rb1_over 1, tint_rb1_bad 0 (the driver runs it with KYTY_IMAGE_DETILE_FUSE=1 and 0; m14 - the flag only
  //       in Image::Upload - fails the fused arm).
  // Ends with "T188Gpu: total=<n> ok=<m> END".
  void CheckT188GpuStand() {
    constexpr const char *name = "T188GpuStand";
    EnsureRuntimeContext();
    int total = 0, passed = 0;
    const auto report = [&](const std::string &member, bool ok, const std::string &detail) {
      total++;
      passed += ok ? 1 : 0;
      std::printf("T188Gpu: member=%s %s ok=%d\n", member.c_str(), detail.c_str(), ok ? 1 : 0);
    };
    RenderContext resources(m_runtime_context);
    auto &scheduler = resources.GetCommandScheduler();
    HW::Context registers{};
    HW::UserConfig user_config{};
    HW::Shader shaders{};
    scheduler.Begin(registers, user_config, shaders);

    // ---- tint members
    struct Fmt {
      const char *name;
      vk::Format format;
      Prospero::BufferFormat guest;
      uint32_t bpb;
    };
    const Fmt formats[] = {
        {"rgba8", vk::Format::eR8G8B8A8Unorm, Prospero::BufferFormat::k8_8_8_8UNorm, 4},
        {"r16f", vk::Format::eR16Sfloat, Prospero::BufferFormat::k16Float, 2},
        {"rg8", vk::Format::eR8G8Unorm, Prospero::BufferFormat::k8_8UNorm, 2},
    };
    constexpr uint32_t W = 8, H = 8, LEVELS = 3;
    for (const auto &fmt : formats) {
      for (const uint32_t layers : {1u, 4u}) {
        for (const uint32_t tinted : {0u, 1u}) {
          ImageInfo info{};
          info.pixel_format = fmt.format;
          info.guest_format = fmt.guest;
          info.type = Prospero::ImageType::kColor2D;
          info.extent = {W, H, 1};
          info.resources = {LEVELS, layers};
          info.pitch = W;
          info.bytes_per_block = fmt.bpb;
          info.samples = 1;
          info.tile_mode = Prospero::TileMode::kLinear;
          uint64_t offset = 0;
          std::array<uint64_t, LEVELS> level_offset{};
          for (uint32_t l = 0; l < LEVELS; l++) {
            const uint32_t w = std::max(W >> l, 1u), h = std::max(H >> l, 1u);
            const uint64_t size = static_cast<uint64_t>(w) * h * fmt.bpb * layers;
            info.mip_layout[l] = {offset, size, w, h};
            level_offset[l] = offset;
            offset += size;
          }
          info.data = {0x205000000ull, offset}; // a valid guest range (no memory behind it is read)
          Libs::Graphics::Image image(m_runtime_context, scheduler, info);
          const std::string member = std::string("tint_") + fmt.name + "_l" + std::to_string(layers) + "_t" +
                                     std::to_string(tinted);
          if (!T188Gpu::TintFormatOk(image)) {
            report(member, false, "format_ok=0");
            continue;
          }
          // Level l, every texel of every layer: bytes (l * 40 + 10, 200, 30, 255) cut to the texel size (16-bit
          // float: 0x3400 + l) - never the magenta code.
          std::vector<uint8_t> fill(offset);
          const auto texel = [&](uint32_t l, uint8_t *out) {
            if (fmt.format == vk::Format::eR16Sfloat) {
              const uint16_t v = static_cast<uint16_t>(0x3400u + l);
              std::memcpy(out, &v, 2);
            } else {
              const uint8_t v[4] = {static_cast<uint8_t>(l * 40 + 10), 200, 30, 255};
              std::memcpy(out, v, fmt.bpb);
            }
          };
          std::vector<vk::BufferImageCopy> copies;
          for (uint32_t l = 0; l < LEVELS; l++) {
            const uint32_t w = std::max(W >> l, 1u), h = std::max(H >> l, 1u);
            for (uint64_t i = 0; i < info.mip_layout[l].size / fmt.bpb; i++) {
              texel(l, fill.data() + level_offset[l] + i * fmt.bpb);
            }
            for (uint32_t layer = 0; layer < layers; layer++) {
              vk::BufferImageCopy copy{};
              copy.bufferOffset = level_offset[l] + static_cast<uint64_t>(w) * h * fmt.bpb * layer;
              copy.imageSubresource = vk::ImageSubresourceLayers{vk::ImageAspectFlagBits::eColor, l, layer, 1};
              copy.imageExtent = vk::Extent3D{w, h, 1};
              copies.push_back(copy);
            }
          }
          std::vector<u32> words((offset + 3) / 4);
          std::memcpy(words.data(), fill.data(), offset);
          auto upload = CreateHostBuffer(name, words.size() * 4,
                                         vk::BufferUsageFlagBits::eTransferSrc, words);
          auto rb = CreateHostBuffer(name, 32, vk::BufferUsageFlagBits::eTransferDst,
                                     std::vector<u32>(8, 0));
          auto all = CreateHostBuffer(name, words.size() * 4, vk::BufferUsageFlagBits::eTransferDst,
                                      std::vector<u32>(words.size(), 0));
          image.Upload(copies, upload.buffer, 0, words.size() * 4);
          T188Gpu::TintLevels(scheduler.Current(), image, 1u << tinted, 1u << tinted, rb.buffer, 0);
          image.Download(copies, all.buffer, 0, words.size() * 4);
          VulkanMemoryBarrier barrier{};
          barrier.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
          barrier.dstAccessMask = vk::AccessFlagBits::eHostRead;
          scheduler.Current().Handle().pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
                                                       vk::PipelineStageFlagBits::eHost, {}, 1, &barrier, 0,
                                                       nullptr, 0, nullptr);
          scheduler.Finish();
          const auto rb_words = ReadBuffer(name, rb, 8);
          const auto all_words = ReadBuffer(name, all, words.size());
          const auto *rb_bytes = reinterpret_cast<const uint8_t *>(rb_words.data());
          const auto *got = reinterpret_cast<const uint8_t *>(all_words.data());
          const auto fmt_u = static_cast<uint32_t>(fmt.format);
          const bool rb_ok = DiagT188::TexelIsMagenta(fmt_u, rb_bytes) &&
                             (layers < 2 || DiagT188::TexelIsMagenta(fmt_u, rb_bytes + 16));
          uint64_t bad_tinted = 0, bad_other = 0;
          for (uint32_t l = 0; l < LEVELS; l++) {
            for (uint64_t i = 0; i < info.mip_layout[l].size / fmt.bpb; i++) {
              const uint8_t *t = got + level_offset[l] + i * fmt.bpb;
              if (l == tinted) {
                bad_tinted += DiagT188::TexelIsMagenta(fmt_u, t) ? 0 : 1;
              } else {
                bad_other += std::memcmp(t, fill.data() + level_offset[l] + i * fmt.bpb, fmt.bpb) == 0 ? 0 : 1;
              }
            }
          }
          report(member, rb_ok && bad_tinted == 0 && bad_other == 0,
                 "rb0=" + std::to_string(rb_ok ? 1 : 0) + " bad_tinted=" + std::to_string(bad_tinted) +
                     " bad_other=" + std::to_string(bad_other));
          DestroyBuffer(&upload);
          DestroyBuffer(&rb);
          DestroyBuffer(&all);
        }
      }
    }

    // ---- sw_first (m13)
    {
      DiagT188::g_mode = 1;
      ImageInfo info{};
      info.pixel_format = vk::Format::eR8G8B8A8Unorm;
      info.guest_format = Prospero::BufferFormat::k8_8_8_8UNorm;
      info.type = Prospero::ImageType::kColor2D;
      info.extent = {8, 8, 1};
      info.resources = {1, 1};
      info.pitch = 8;
      info.bytes_per_block = 4;
      info.samples = 1;
      info.tile_mode = Prospero::TileMode::kLinear;
      info.mip_layout[0] = {0, 256, 8, 8};
      info.data = {0x205100000ull, 256};
      Libs::Graphics::Image image(m_runtime_context, scheduler, info);
      image.MarkGpuModified();
      DiagT188::NoteSync(image.t188, true, true);
      image.MarkGpuModified();
      const auto w = image.t188.wseq.load(), s = image.t188.sseq.load();
      report("sw_first", w != s && w == 2 && s == 1,
             "wseq=" + std::to_string(w) + " sseq=" + std::to_string(s));
      image.ClearGpuModified();
    }

    // ---- ovr (m15)
    {
      DiagT188::g_mode = 1;
      DiagT109::ResetForStand();
      CommandProcessor processor(resources, 0);
      GraphicsInitJmpTablesCxIndirect();
      const uint32_t range[4] = {0u, 0u, 0x10000u, 0u}; // 0x1 .. 0x4: DB_RENDER_OVERRIDE (0x3) with bit 16
      (void)g_hw_ctx_func[Pm4::DB_COUNT_CONTROL](processor, 4u << 16u, Pm4::DB_COUNT_CONTROL, range, 0);
      const auto after_range = DiagT109::Read();
      const uint32_t single = 0u;
      (void)g_hw_ctx_func[Pm4::DB_RENDER_OVERRIDE](processor, 1u << 16u, Pm4::DB_RENDER_OVERRIDE, &single, 0);
      const auto after_direct = DiagT109::Read();
      g_hw_ctx_indirect_func[Pm4::DB_RENDER_OVERRIDE](processor, Pm4::DB_RENDER_OVERRIDE, 0x10000u);
      const auto after_indirect = DiagT109::Read();
      report("ovr",
             after_range.ovr_w == 1 && after_range.ovr_vpc == 1 && after_direct.ovr_w == 2 &&
                 after_direct.ovr_vpc == 1 && after_indirect.ovr_w == 3 && after_indirect.ovr_vpc == 2,
             "range=" + std::to_string(after_range.ovr_w) + "/" + std::to_string(after_range.ovr_vpc) +
                 " direct=" + std::to_string(after_direct.ovr_w) + "/" + std::to_string(after_direct.ovr_vpc) +
                 " indirect=" + std::to_string(after_indirect.ovr_w) + "/" + std::to_string(after_indirect.ovr_vpc));
    }

    auto &cache = resources.GetTextureCache();
    // ---- s7 (site S7 through CommitGpuWrite)
    {
      DiagT188::g_mode = 1;
      DiagT188::ResetForStand();
      ImageInfo info{};
      info.pixel_format = vk::Format::eR8G8B8A8Unorm;
      info.guest_format = Prospero::BufferFormat::k8_8_8_8UNorm;
      info.type = Prospero::ImageType::kColor2D;
      info.extent = {16, 16, 1};
      info.resources = {1, 1};
      info.pitch = 16;
      info.bytes_per_block = 4;
      info.samples = 1;
      info.tile_mode = Prospero::TileMode::kLinear;
      info.mip_layout[0] = {0, 1024, 16, 16};
      info.data = {0x204800000ull, 1024};
      const auto id = TextureCacheTestAccess::InsertImage(cache, info);
      cache.GetImage(id).MarkGpuModified();
      cache.InvalidateMemoryFromGPU(info.data.address + 0x40, 0x40, DiagT188::Writer::St);
      const auto ep_new = DiagT188::Read(DiagT188::C::ep_new);
      cache.MarkGpuWritten(id);
      const auto commit = DiagT188::Read(DiagT188::C::cl_commit);
      const auto lock_bad = DiagT188::Read(DiagT188::C::lock_bad);
      const auto part_st = DiagT188::Read(DiagT188::C::part_st);
      report("s7", ep_new == 1 && commit == 1 && lock_bad == 0 && part_st == 1,
             "ep_new=" + std::to_string(ep_new) + " cl_commit=" + std::to_string(commit) +
                 " part_st=" + std::to_string(part_st) + " lock_bad=" + std::to_string(lock_bad));
      TextureCacheTestAccess::T188Free(cache, id);
    }

    // ---- rc12: a tinted tiled texture re-uploaded without an episode in a later frame
    {
      DiagT188::g_mode = 3;
      DiagT188::ResetForStand();
      constexpr uint64_t base = 0x204a00000ull, mapped_size = 0x20000;
      int64_t direct = -1;
      Require(name, "allocate",
              LibKernel::Memory::KernelAllocateDirectMemory(0, LibKernel::Memory::KernelGetDirectMemorySize(),
                                                            mapped_size, 0x10000, 0, &direct) == 0,
              "rc12 allocation failed");
      void *mapped = reinterpret_cast<void *>(base);
      Require(name, "map",
              LibKernel::Memory::KernelMapDirectMemory(&mapped, mapped_size, 3, 0x10, direct, 0x10000) == 0 &&
                  mapped == reinterpret_cast<void *>(base),
              "rc12 mapping failed");
      resources.MapMemory(base, mapped_size);
      auto *words = static_cast<uint32_t *>(mapped);
      for (size_t i = 0; i < mapped_size / 4; ++i) {
        words[i] = 0x22cc4410u; // R 0x10, G 0x44, B 0xcc, A 0x22 - not magenta
      }
      ImageDesc desc{};
      desc.info.guest_format = Prospero::BufferFormat::k8_8_8_8UNorm;
      desc.info.pixel_format = vk::Format::eR8G8B8A8Unorm;
      desc.info.type = Prospero::ImageType::kColor2D;
      desc.info.tile_mode = Prospero::TileMode::kStandard64KB;
      desc.info.extent = {64, 64, 1};
      desc.info.resources = {1, 1};
      desc.info.pitch = 64;
      desc.info.bytes_per_block = 4;
      desc.info.samples = 1;
      TileSizeAlign total{};
      TileSizeOffset levels[16]{};
      TilePaddedSize padded[16]{};
      TileGetTextureSize(desc.info.guest_format, 64, 64, 1, desc.info.tile_mode, &total, levels, padded);
      desc.info.data = {base, total.size};
      desc.info.mip_layout[0] = {levels[0].src_size ? levels[0].src_offset : levels[0].offset,
                                 levels[0].src_size ? levels[0].src_size : levels[0].size, padded[0].width,
                                 padded[0].height};
      desc.view_info.format = desc.info.pixel_format;
      desc.view_info.type = vk::ImageViewType::e2D;
      desc.view_info.aspect = vk::ImageAspectFlagBits::eColor;
      desc.view_info.usage = vk::ImageUsageFlagBits::eSampled;
      desc.view_info.level_count = 1;
      desc.view_info.layer_count = 1;
      const auto id = cache.FindImage(desc);
      TextureCacheTestAccess::InitializeTexture(cache, id);
      const auto frame0 = GpuTimeProfiler::Frame();
      GpuTimeProfiler::SetFrame(frame0 + 10);
      cache.GetImage(id).MarkGpuModified();
      cache.InvalidateMemoryFromGPU(base + 0x100, 0x100, DiagT188::Writer::St);
      TextureCacheTestAccess::InitializeTexture(cache, id); // S3: closure, tint (mode 3) and rb0
      const bool storage = static_cast<bool>(cache.GetImage(id).backing.usage & vk::ImageUsageFlagBits::eStorage);
      scheduler.Finish();
      scheduler.PopPendingOperations();
      const auto rb0_ok = DiagT188::Read(DiagT188::C::tint_rb0_ok);
      GpuTimeProfiler::SetFrame(frame0 + 11);
      TextureCacheTestAccess::T188InvalidateCpu(cache, id, base, total.size);
      TextureCacheTestAccess::InitializeTexture(cache, id); // the re-upload without an episode; the visit issues rb1
      scheduler.Finish();
      scheduler.PopPendingOperations();
      const auto over = DiagT188::Read(DiagT188::C::tint_rb1_over);
      const auto bad = DiagT188::Read(DiagT188::C::tint_rb1_bad);
      const auto ok1 = DiagT188::Read(DiagT188::C::tint_rb1_ok);
      const char *fuse = std::getenv("KYTY_IMAGE_DETILE_FUSE");
      report("rc12",
             rb0_ok == 1 && over == 1 && bad == 0 && ok1 == 0 && DiagT188::Read(DiagT188::C::cl_oth) == 1 &&
                 DiagT188::Read(DiagT188::C::lock_bad) == 0,
             "fuse_env=" + std::string(fuse == nullptr ? "unset" : fuse) + " storage=" +
                 std::to_string(storage ? 1 : 0) + " fused=" +
                 std::to_string(Common::FrameStats::Enabled() ? Common::FrameStats::Read(Common::FrameStats::Counter::C1Fused) : 0) +
                 " rb0_ok=" + std::to_string(rb0_ok) + " rb1_over=" + std::to_string(over) + " rb1_bad=" +
                 std::to_string(bad) + " rb1_ok=" + std::to_string(ok1) +
                 " cl_oth=" + std::to_string(DiagT188::Read(DiagT188::C::cl_oth)) +
                 " tint_ep=" + std::to_string(DiagT188::Read(DiagT188::C::tint_ep)));
      GpuTimeProfiler::SetFrame(frame0);
      TextureCacheTestAccess::T188Free(cache, id);
    }
    DiagT188::g_mode = 0;
    scheduler.Finish();
    std::printf("T188Gpu: total=%d ok=%d END\n", total, passed);
    std::fflush(stdout);
  }

