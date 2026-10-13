// Track M, M9d (KYTY_DIAG_T188, ROADMAP s122 item 785; design docs/track-m/m9a2/design_m9a2.md edition 2): the T188 sites
// of the texture cache. Every one is called at KYTY_DIAG_T188 >= 1 only and checks m_lock (lock_bad); the logic is in
// libs/diagT188.cpp, the GPU part (tint, readback) in T188Gpu below.
namespace {

struct T188Geo {
	std::array<DiagT188::Mip, 16> mips {};
	DiagT188::Geometry            g;
};

void T188Fill(const Image& image, T188Geo& out) {
	const auto levels = std::min<uint32_t>(image.info.resources.levels, static_cast<uint32_t>(out.mips.size()));
	for (uint32_t l = 0; l < levels; l++) {
		out.mips[l] = {image.info.mip_layout[l].offset, image.info.mip_layout[l].size};
	}
	out.g.address     = image.info.data.address;
	out.g.data_size   = image.info.data.size;
	out.g.source_size = image.SourceRange().size;
	out.g.levels      = levels;
	out.g.layers      = image.backing.image != nullptr ? image.backing.layers : image.info.resources.layers;
	out.g.volume      = image.info.IsVolume();
	out.g.mips        = out.mips.data();
}

DiagT188::ClassFields T188Fields(const Image& image) {
	DiagT188::ClassFields f;
	f.fmt     = static_cast<uint32_t>(image.info.pixel_format);
	f.tile    = static_cast<uint32_t>(image.info.tile_mode);
	f.w       = image.info.extent.width;
	f.h       = image.info.extent.height;
	f.levels  = image.info.resources.levels;
	f.layers  = image.info.resources.layers;
	f.cmp     = (image.info.IsBlock() ? 1u : 0u) |
	        (image.info.metadata.compression != VideoOutCompression::Uncompressed ? 2u : 0u);
	f.samples = image.info.samples;
	f.usage   = (image.usage.texture ? 1u : 0u) | (image.usage.storage ? 2u : 0u) | (image.usage.render_target ? 4u : 0u) |
	          (image.usage.depth_target ? 8u : 0u) | (image.usage.video_out ? 16u : 0u);
	f.vol     = image.info.IsVolume() ? 1u : 0u;
	return f;
}

DiagT188::Close T188SiteOf(const UploadSiteState& site) {
	switch (site.site) {
		case UploadSite::ColorTarget:
			return (site.reg_clear || site.fill_clear) ? DiagT188::Close::RtClr : DiagT188::Close::Rt;
		case UploadSite::DepthTarget: return DiagT188::Close::Dt;
		case UploadSite::StorageImage: return DiagT188::Close::Sto;
		case UploadSite::Sampled: return DiagT188::Close::Smp;
		case UploadSite::ClearOp: return DiagT188::Close::ClrOp;
		case UploadSite::Other: break;
	}
	return DiagT188::Close::Oth;
}

} // namespace

void TextureCache::T188Invalidate(Image& image, DiagT188::Writer writer, uint64_t address, uint64_t size) {
	const bool locked = m_lock.HeldByCurrentThread();
	T188Geo    geo;
	T188Fill(image, geo);
	if (locked) {
		T188Visit(image);
	}
	const bool in_pass =
	    m_scheduler.Active() && !m_scheduler.Current().IsInvalid() && m_scheduler.Current().IsRendering();
	(void)DiagT188::NoteInvalidate(image.t188, geo.g, T188Fields(image), image.IsGpuModified(), writer, address, size,
	                               in_pass, locked);
}

void TextureCache::T188CloseUpload(Image& image, uint32_t first, uint32_t end) {
	const bool locked = m_lock.HeldByCurrentThread();
	T188Geo    geo;
	T188Fill(image, geo);
	if (locked) {
		T188Visit(image); // rb1 of an older tint, after the upload it reads
	}
	const auto site = m_t188_vo ? DiagT188::Close::Vo : T188SiteOf(t_upload_site);
	const auto plan = DiagT188::CloseUpload(image.t188, geo.g, T188Fields(image), site, first, end,
	                                        image.source_first_level, image.pending_levels,
	                                        T188Gpu::TintFormatOk(image), image.IsCpuDirty(), locked);
	T188Tint(image, plan);
}

void TextureCache::T188PendDone(Image& image, uint32_t first, uint32_t end) {
	const bool locked = m_lock.HeldByCurrentThread();
	T188Geo    geo;
	T188Fill(image, geo);
	if (locked) {
		T188Visit(image);
	}
	const auto plan = DiagT188::PendDone(image.t188, geo.g, first, end, locked);
	T188Tint(image, plan);
}

void TextureCache::T188Close(Image& image, DiagT188::Close site) {
	const bool locked = m_lock.HeldByCurrentThread();
	if (locked) {
		T188Visit(image);
	}
	DiagT188::CloseNoUpload(image.t188, site, locked);
}

void TextureCache::T188Propagate(Image& destination, const Image& source) {
	const bool locked = m_lock.HeldByCurrentThread();
	T188Geo    geo;
	T188Fill(destination, geo);
	if (locked) {
		T188Visit(destination);
	}
	DiagT188::Propagate(destination.t188, source.t188, geo.g, T188Fields(destination), locked);
}

// rb1: the first visit of a tinted image in a frame after its tint reads the same texels back (no wait here; the result
// is taken when the tick completes).
void TextureCache::T188Visit(Image& image) {
	if (DiagT188::Mode() < 2 || image.t188.rb_pend.load(std::memory_order_acquire) == 0) {
		return;
	}
	std::array<DiagT188::RbInfo, DiagT188::kLevels> infos {};
	const auto n = DiagT188::RbWant1(image.t188, GpuTimeProfiler::Frame(), infos.data(), DiagT188::kLevels);
	if (n == 0) {
		return;
	}
	auto& command = m_scheduler.Current();
	if (command.IsInvalid()) {
		DiagT188::RbNotRecorded1(infos.data(), n);
		return;
	}
	auto&          download = m_buffer_cache.GetUtilityBuffer(MemoryUsage::Download);
	const auto     mapping  = download.Map(32ull * n, 16);
	uint8_t* const mapped   = mapping.first;
	const uint64_t offset   = mapping.second;
	if (mapped == nullptr) {
		DiagT188::RbNotRecorded1(infos.data(), n);
		return;
	}
	download.Commit();
	T188Gpu::ReadTexels(command, image, infos.data(), n, download.Handle(), offset);
	m_scheduler.DeferOperation([&download, mapped, offset, n, infos] {
		download.Invalidate(offset, 32ull * n);
		for (uint32_t i = 0; i < n; i++) {
			const uint8_t* texel = mapped + 32ull * i;
			const bool     ok    = DiagT188::TexelIsMagenta(infos[i].fmt, texel) &&
			              (infos[i].last_layer == 0 || DiagT188::TexelIsMagenta(infos[i].fmt, texel + 16));
			DiagT188::RbDone1(infos[i].id, ok);
		}
	});
}

// The tint of a plan (mode >= 2) and its rb0, right after the clears in the same command buffer.
void TextureCache::T188Tint(Image& image, const DiagT188::TintPlan& plan) {
	if (plan.mask == 0) {
		return;
	}
	auto& command = m_scheduler.Current();
	EXIT_IF(command.IsInvalid());
	const auto     count    = static_cast<uint32_t>(std::popcount(plan.rb_mask));
	auto&          download = m_buffer_cache.GetUtilityBuffer(MemoryUsage::Download);
	uint8_t*       mapped   = nullptr;
	uint64_t       offset   = 0;
	if (count != 0) {
		const auto mapping = download.Map(32ull * count, 16);
		mapped             = mapping.first;
		offset             = mapping.second;
		if (mapped != nullptr) {
			download.Commit();
		}
	}
	T188Gpu::TintLevels(command, image, plan.mask, mapped != nullptr ? plan.rb_mask : 0u, download.Handle(), offset);
	if (count == 0) {
		return;
	}
	if (mapped == nullptr) {
		DiagT188::RbNotRecorded(plan);
		return;
	}
	T188Geo geo;
	T188Fill(image, geo);
	const auto     fmt   = static_cast<uint32_t>(image.backing.format);
	const bool     two   = geo.g.layers >= 2;
	const uint32_t first = DiagT188::RbBegin(image.t188, plan, geo.g, image.info.extent.width, image.info.extent.height,
	                                         fmt, GpuTimeProfiler::Frame());
	m_scheduler.DeferOperation([&download, mapped, offset, count, first, fmt, two] {
		download.Invalidate(offset, 32ull * count);
		for (uint32_t i = 0; i < count; i++) {
			const uint8_t* texel = mapped + 32ull * i;
			const bool     ok    = DiagT188::TexelIsMagenta(fmt, texel) && (!two || DiagT188::TexelIsMagenta(fmt, texel + 16));
			DiagT188::RbDone0(first + i, ok);
		}
	});
}

// S6 (both exits of Execute): the readbacks in flight get up to 2 s, m_lock is tried for up to 2 s (a thread that holds it
// forever must not hang the exit); with it, the images are scanned (ep_bad (v)); then the exit lines.
void TextureCache::T188ExitHook(void* context) {
	auto*      cache    = static_cast<TextureCache*>(context);
	const auto deadline = [](int ms) { return std::chrono::steady_clock::now() + std::chrono::milliseconds(ms); };
	for (const auto until = deadline(2000); DiagT188::RbInFlight() != 0 && std::chrono::steady_clock::now() < until;) {
		std::this_thread::sleep_for(std::chrono::milliseconds(10));
	}
	bool locked = false;
	for (const auto until = deadline(2000); !(locked = cache->m_lock.TryLock()) && std::chrono::steady_clock::now() < until;) {
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	if (locked) {
		uint64_t open = 0;
		uint64_t wait = 0;
		cache->m_slot_images.ForEach([&](ImageId, const Image& image) {
			open += image.t188.open ? 1u : 0u;
			wait += image.t188.wait ? 1u : 0u;
		});
		DiagT188::ExitScan(open, wait);
	}
	DiagT188::PrintExit();
	if (locked) {
		cache->m_lock.unlock();
	}
}

namespace T188Gpu {

bool TintFormatOk(const Image& image) {
	if (image.backing.image == nullptr || image.info.IsDepth() || image.info.IsBlock() || image.info.IsVolume() ||
	    image.info.samples != 1 || image.backing.samples != 1) {
		return false;
	}
	const auto usage = image.backing.usage;
	if (!(usage & vk::ImageUsageFlagBits::eTransferDst) || !(usage & vk::ImageUsageFlagBits::eTransferSrc)) {
		return false;
	}
	uint8_t  code[16];
	uint32_t bytes = 0;
	return DiagT188::MagentaCode(static_cast<uint32_t>(image.backing.format), code, &bytes);
}

void TintLevels(CommandBuffer& command, Image& image, uint32_t mask, uint32_t rb_mask, vk::Buffer rb_buffer,
                uint64_t rb_offset) {
	if (mask == 0) {
		return;
	}
	command.EndRendering(RenderPassEnd::Clear);
	image.Transit(vk::ImageLayout::eTransferDstOptimal, vk::AccessFlagBits2::eTransferWrite, {}, command.Handle());
	const vk::ClearColorValue magenta {std::array<float, 4> {1.0f, 0.0f, 1.0f, 1.0f}};
	const uint32_t            layers = image.backing.layers;
	for (uint32_t l = 0; l < DiagT188::kLevels; l++) {
		if ((mask & (1u << l)) == 0) {
			continue;
		}
		const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, l, 1, 0, layers};
		command.Handle().clearColorImage(image.backing.image, vk::ImageLayout::eTransferDstOptimal, &magenta, 1,
		                                 &range);
	}
	if (rb_mask == 0) {
		return;
	}
	std::array<DiagT188::RbInfo, DiagT188::kLevels> infos {};
	uint32_t                                        n = 0;
	for (uint32_t l = 0; l < DiagT188::kLevels; l++) {
		if ((rb_mask & (1u << l)) == 0) {
			continue;
		}
		infos[n++] = {0, l, std::max(image.info.extent.width >> l, 1u) / 2, std::max(image.info.extent.height >> l, 1u) / 2,
		              layers >= 2 ? layers - 1 : 0u, static_cast<uint32_t>(image.backing.format)};
	}
	ReadTexels(command, image, infos.data(), n, rb_buffer, rb_offset);
}

void ReadTexels(CommandBuffer& command, Image& image, const DiagT188::RbInfo* infos, uint32_t count, vk::Buffer rb_buffer,
                uint64_t rb_offset) {
	if (count == 0) {
		return;
	}
	std::vector<vk::BufferImageCopy> copies;
	const auto add = [&](const DiagT188::RbInfo& info, uint32_t layer, uint64_t buffer_offset) {
		vk::BufferImageCopy copy {};
		copy.bufferOffset     = buffer_offset;
		copy.imageSubresource = vk::ImageSubresourceLayers {vk::ImageAspectFlagBits::eColor, info.level, layer, 1};
		copy.imageOffset      = vk::Offset3D {static_cast<int32_t>(info.x), static_cast<int32_t>(info.y), 0};
		copy.imageExtent      = vk::Extent3D {1, 1, 1};
		copies.push_back(copy);
	};
	for (uint32_t i = 0; i < count; i++) {
		add(infos[i], 0, rb_offset + 32ull * i);
		if (infos[i].last_layer != 0) {
			add(infos[i], infos[i].last_layer, rb_offset + 32ull * i + 16);
		}
	}
	image.Download(copies, rb_buffer, rb_offset, 32ull * count);
	vk::BufferMemoryBarrier barrier {};
	barrier.srcAccessMask       = vk::AccessFlagBits::eTransferWrite;
	barrier.dstAccessMask       = vk::AccessFlagBits::eHostRead;
	barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.buffer              = rb_buffer;
	barrier.offset              = rb_offset;
	barrier.size                = 32ull * count;
	command.Handle().pipelineBarrier(vk::PipelineStageFlagBits::eTransfer, vk::PipelineStageFlagBits::eHost, {}, 0,
	                                 nullptr, 1, &barrier, 0, nullptr);
}

} // namespace T188Gpu
