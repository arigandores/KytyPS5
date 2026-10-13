"""M9d (HPP-869, ROADMAP s122 item 785): KYTY_DIAG_T188 stage 1 + T109Stat - patch of the worktree (base M6a3 3d227024).
Exact anchors (whole lines); every anchor must occur once. CR is removed before the search and restored after.
Usage: python patch_m9d.py <worktree> <dir with diagT188.h/.cpp>. Lock checked first (exit 3). Prints ALL OK."""
import os
import shutil
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
WT = sys.argv[1]
NEW = sys.argv[2]
fails = []


class F:
    def __init__(self, rel):
        self.rel = rel
        self.path = os.path.join(WT, rel)
        raw = open(self.path, 'rb').read()
        self.crlf = b'\r\n' in raw
        self.t = raw.decode('utf-8').replace('\r\n', '\n')

    def rep(self, old, new, count=1):
        n = self.t.count(old)
        if n != count:
            fails.append('%s: anchor x%d (want %d): %r' % (self.rel, n, count, old[:90]))
            return
        self.t = self.t.replace(old, new)

    def save(self):
        t = self.t.replace('\n', '\r\n') if self.crlf else self.t
        open(self.path, 'wb').write(t.encode('utf-8'))


# ---------------------------------------------------------------- new files
for name in ('diagT188.h', 'diagT188.cpp'):
    shutil.copyfile(os.path.join(NEW, name), os.path.join(WT, 'src/libs', name))

# ---------------------------------------------------------------- regionManager.h
f = F('src/graphics/host_gpu/regionManager.h')
f.rep('''		m_owner.store(0, std::memory_order_relaxed);
		m_lock.clear(std::memory_order_release);
	}
''', '''		m_owner.store(0, std::memory_order_relaxed);
		m_lock.clear(std::memory_order_release);
	}
	// Track M, M9d (KYTY_DIAG_T188, ROADMAP s122 item 785): the lock check of the T188 sites (lock_bad) and the try of
	// its exit scan (S6). Neither is called at KYTY_DIAG_T188=0.
	[[nodiscard]] bool HeldByCurrentThread() const noexcept {
		return m_owner.load(std::memory_order_relaxed) == CurrentThread();
	}
	[[nodiscard]] bool TryLock() noexcept {
		const auto thread = CurrentThread();
		if (m_owner.load(std::memory_order_relaxed) == thread || m_lock.test_and_set(std::memory_order_acquire)) {
			return false;
		}
		m_owner.store(thread, std::memory_order_relaxed);
		return true;
	}
''')
f.save()

# ---------------------------------------------------------------- image.h
f = F('src/graphics/host_gpu/renderer/image/image.h')
f.rep('#include "graphics/host_gpu/renderer/renderTarget.h"\n',
      '#include "graphics/host_gpu/renderer/renderTarget.h"\n#include "libs/diagT188.h" // Track M, M9d (KYTY_DIAG_T188)\n')
f.rep('''	void MarkGpuModified() noexcept {
		// Session 123, knob "skipceil" = 2 (census, MEASUREMENT ONLY; design123.md s.3.1 W3 [N6]): the stamp is the FIRST
''', '''	void MarkGpuModified() noexcept {
		// Track M, M9d (KYTY_DIAG_T188, ROADMAP s122 item 785(b)(2)): Sw - the FIRST statement, before the census stamp
		// and the transition test: every write moves t188.wseq (and flags a pending readback), not only the first one.
		if (DiagT188::Mode() != 0) [[unlikely]] {
			DiagT188::NoteGpuWrite(t188);
		}
		// Session 123, knob "skipceil" = 2 (census, MEASUREMENT ONLY; design123.md s.3.1 W3 [N6]): the stamp is the FIRST
''')
f.rep('''	uint32_t              skc3_uid = 0;
''', '''	uint32_t              skc3_uid = 0;
	// Track M, M9d (KYTY_DIAG_T188, ROADMAP s122 item 785): the T188 episode state (diagT188.h); read and written only at
	// KYTY_DIAG_T188 >= 1, under TextureCache::m_lock except its atomics.
	DiagT188::ImageState  t188;
''')
f.save()

# ---------------------------------------------------------------- image.cpp
f = F('src/graphics/host_gpu/renderer/image/image.cpp')
f.rep('''	EXIT_IF(copies.empty() || buffer == nullptr || size == 0);
	m_scheduler.EndRendering(RenderPassEnd::ImageUpload);
''', '''	EXIT_IF(copies.empty() || buffer == nullptr || size == 0);
	m_scheduler.EndRendering(RenderPassEnd::ImageUpload);
	if (DiagT188::Mode() != 0) [[unlikely]] {
		DiagT188::NoteImageWrite(t188); // Track M, M9d (RC12): a write of the image after its tint
	}
''')
f.save()

# ---------------------------------------------------------------- textureCache.h
f = F('src/graphics/host_gpu/renderer/cache/textureCache.h')
f.rep('''	void                        UpdateImage(ImageId id);
''', '''	// Track M, M9d (KYTY_DIAG_T188): t188_video_out - the call of swapchain ResolveSurface (site Svo); nothing else reads it.
	void                        UpdateImage(ImageId id, bool t188_video_out = false);
''')
f.rep('''	void               InvalidateMemoryFromGPU(uint64_t address, uint64_t size);
''', '''	// Track M, M9d (KYTY_DIAG_T188, site S1): `writer` - which GPU write calls (read only at KYTY_DIAG_T188 >= 1).
	void               InvalidateMemoryFromGPU(uint64_t address, uint64_t size,
	                                           DiagT188::Writer writer = DiagT188::Writer::Unk);
''')
f.rep('''	[[nodiscard]] bool DownloadImageMemory(ImageId id);
''', '''	[[nodiscard]] bool DownloadImageMemory(ImageId id);
	// Track M, M9d (KYTY_DIAG_T188, ROADMAP s122 item 785): the T188 sites (called at mode >= 1 only; textureCache.cpp).
	// The caller holds m_lock - checked (lock_bad), and without it a site does no work.
	void        T188Invalidate(Image& image, DiagT188::Writer writer, uint64_t address, uint64_t size);
	void        T188CloseUpload(Image& image, uint32_t first, uint32_t end);
	void        T188PendDone(Image& image, uint32_t first, uint32_t end);
	void        T188Close(Image& image, DiagT188::Close site);
	void        T188Propagate(Image& destination, const Image& source);
	void        T188Visit(Image& image);
	void        T188Tint(Image& image, const DiagT188::TintPlan& plan);
	static void T188ExitHook(void* context);
	bool        m_t188_vo = false; // inside UpdateImage(id, true) (site Svo), under m_lock
''')
f.rep('''	friend struct SkcCensus;
};
''', '''	friend struct SkcCensus;
};

// Track M, M9d (KYTY_DIAG_T188, ROADMAP s122 item 785): the tint and its readback, shared by the T188 sites and the GPU
// stand (--t188-gpu-stand of shader_recompiler_compute_tests).
namespace T188Gpu {
// The image can be tinted and read back: colour, not block-compressed, not a volume, single-sampled, TRANSFER_DST and
// TRANSFER_SRC, a backing format with a row of DiagT188::MagentaCode.
[[nodiscard]] bool TintFormatOk(const Image& image);
// Records, in this order: the end of a pass, the transition of the image to TransferDstOptimal, clearColorImage
// (1, 0, 1, 1) of {level, 1, 0, layers} for every level of `mask`; then, for the i-th set bit of `rb_mask`, the copy of
// the centre texel of that level (layer 0 to rb_buffer + rb_offset + 32 * i; at layers >= 2 the last layer to + 16)
// and a transfer-to-host barrier.
void TintLevels(CommandBuffer& command, Image& image, uint32_t mask, uint32_t rb_mask, vk::Buffer rb_buffer,
                uint64_t rb_offset);
// The reads alone (rb1): infos[i] to rb_buffer + rb_offset + 32 * i (+ 16 for its last layer).
void ReadTexels(CommandBuffer& command, Image& image, const DiagT188::RbInfo* infos, uint32_t count, vk::Buffer rb_buffer,
                uint64_t rb_offset);
} // namespace T188Gpu
''')
f.save()

# ---------------------------------------------------------------- textureCache.cpp
f = F('src/graphics/host_gpu/renderer/cache/textureCache.cpp')
f.rep('#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)\n',
      '#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)\n#include "libs/diagT188.h" // Track M, M9d (KYTY_DIAG_T188)\n')
f.rep('''#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cinttypes>
''', '''#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cinttypes>
''')
f.rep('''#include <tuple>
#include <unordered_map>
''', '''#include <thread>
#include <tuple>
#include <unordered_map>
''')
# constructor / destructor
f.rep('''		m_trigger_gc_memory = static_cast<uint64_t>(std::max<int64_t>((budget - threshold) / 2, 0));
	}
}

TextureCache::~TextureCache() {
''', '''		m_trigger_gc_memory = static_cast<uint64_t>(std::max<int64_t>((budget - threshold) / 2, 0));
	}
	// Track M, M9d (KYTY_DIAG_T188): "T188: mode=" once per process at any value; the exit hook (S6) at mode >= 1.
	DiagT188::PrintModeLine();
	if (DiagT188::Mode() >= 1) {
		DiagT188::SetExitHook(&TextureCache::T188ExitHook, this);
	}
}

TextureCache::~TextureCache() {
	if (DiagT188::Mode() >= 1) {
		DiagT188::SetExitHook(nullptr, this); // Track M, M9d
	}
''')
# S5
f.rep('''	TraceImageLifetime("free", image.info, reason, line, image.frame_accessed_last);
''', '''	TraceImageLifetime("free", image.info, reason, line, image.frame_accessed_last);
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		DiagT188::NoteFree(image.t188, m_lock.HeldByCurrentThread()); // Track M, M9d: S5
	}
''')
# S8
f.rep('''	if (source.IsBufferModified()) {
		if (source.info.data == destination.info.data) {
			destination.MarkBufferModified();
		}
		return;
	}
''', '''	if (source.IsBufferModified()) {
		if (source.info.data == destination.info.data) {
			destination.MarkBufferModified();
			if (DiagT188::Mode() >= 1) [[unlikely]] {
				T188Propagate(destination, source); // Track M, M9d: S8
			}
		}
		return;
	}
''')
# S7b
f.rep('''	destination.ClearBufferModified();
}

void TextureCache::CopyImageMip(''', '''	if (DiagT188::Mode() >= 1) [[unlikely]] {
		DiagT188::NoteImageWrite(destination.t188);       // Track M, M9d (RC12): the copy wrote the destination
		T188Close(destination, DiagT188::Close::CopyDst); // S7b
	}
	destination.ClearBufferModified();
}

void TextureCache::CopyImageMip(''')
f.rep('''	destination.CopyMip(source, mip, layer);
''', '''	destination.CopyMip(source, mip, layer);
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		DiagT188::NoteImageWrite(destination.t188); // Track M, M9d (RC12): the mip copy wrote the destination
	}
''')
# S3c
f.rep('''	if (image.pending_levels <= first) {
		image.pending_levels = 0;
		image.pending_bytes = 0;
	}
''', '''	if (image.pending_levels <= first) {
		image.pending_levels = 0;
		image.pending_bytes = 0;
		if (DiagT188::Mode() >= 1) [[unlikely]] {
			DiagT188::PendDrop(image.t188, m_lock.HeldByCurrentThread()); // Track M, M9d: S3c
		}
	}
''')
# UploadImage body (RC12)
f.rep('''	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 48(b), M2 (N1)
	const auto& info    = image.info;
''', '''	Common::SkipCeil::NoteOffThread3(); // ROADMAP s122 item 48(b), M2 (N1)
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		// Track M, M9d (RC12): every upload writes the image - both branches (DetileToImage, Image::Upload), both calls
		// (CompletePendingUpload, InitializeImage), with or without an episode.
		DiagT188::NoteImageWrite(image.t188);
	}
	const auto& info    = image.info;
''')
# S3b
f.rep('''	m_frame_upload_bytes += uploaded;
	m_frame_pending_bytes += uploaded;
	image.pending_bytes = 0;
''', '''	m_frame_upload_bytes += uploaded;
	m_frame_pending_bytes += uploaded;
	image.pending_bytes = 0;
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		T188PendDone(image, image.source_first_level, levels); // Track M, M9d: S3b
	}
''')
# S4
f.rep('''	if (image.info.metadata.compression != VideoOutCompression::Uncompressed) {
		if (image.IsCpuDirty()) {
			image.RefreshComplete();
		}
		return;
	}
	if (image.info.samples > 1) {
		return;
	}
	const bool upload = image.IsBufferModified() || image.IsCpuDirty();
''', '''	if (image.info.metadata.compression != VideoOutCompression::Uncompressed) {
		if (DiagT188::Mode() >= 1) [[unlikely]] {
			T188Close(image, DiagT188::Close::Cmp); // Track M, M9d: S4
		}
		if (image.IsCpuDirty()) {
			image.RefreshComplete();
		}
		return;
	}
	if (image.info.samples > 1) {
		if (DiagT188::Mode() >= 1) [[unlikely]] {
			T188Close(image, DiagT188::Close::Msaa); // Track M, M9d: S4
		}
		return;
	}
	const bool upload = image.IsBufferModified() || image.IsCpuDirty();
''')
# S7c
f.rep('''		Common::FrameStats::Add(Common::FrameStats::Counter::ImgSkippedKb,
		                        image.SourceRange().size / 1024u);
		image.ClearBufferModified();
''', '''		Common::FrameStats::Add(Common::FrameStats::Counter::ImgSkippedKb,
		                        image.SourceRange().size / 1024u);
		if (DiagT188::Mode() >= 1) [[unlikely]] {
			T188Close(image, DiagT188::Close::Skip); // Track M, M9d: S7c
		}
		image.ClearBufferModified();
''')
# S3
f.rep('''		// Session 71, C1: key 0, see CompletePendingUpload above.
		m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 0, image.info.data.size >> 20u);
		image.ClearBufferModified();
	}
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
}
''', '''		// Session 71, C1: key 0, see CompletePendingUpload above.
		m_scheduler.GpuMark(GpuTimeProfiler::Kind::ImageUpload, 0, image.info.data.size >> 20u);
		if (DiagT188::Mode() >= 1) [[unlikely]] {
			T188CloseUpload(image, first_level, image.info.resources.levels); // Track M, M9d: S3
		}
		image.ClearBufferModified();
	}
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
}

@@T188_MEMBERS@@
''')
# Svo
f.rep('''void TextureCache::UpdateImage(ImageId id) {
	std::scoped_lock lock {m_lock};
	auto&            image = m_slot_images[id];
	TouchImage(image);
	RefreshImage(id);
}
''', '''void TextureCache::UpdateImage(ImageId id, bool t188_video_out) {
	std::scoped_lock lock {m_lock};
	auto&            image = m_slot_images[id];
	TouchImage(image);
	if (t188_video_out && DiagT188::Mode() >= 1) [[unlikely]] {
		// Track M, M9d: site Svo - an S3 closure inside counts cl_vo; the visit may read a tinted image back.
		m_t188_vo = true;
		RefreshImage(id);
		m_t188_vo = false;
		T188Visit(m_slot_images[id]);
		return;
	}
	RefreshImage(id);
}
''')
# S7
f.rep('''	CompletePendingUpload(image);
	image.ClearBufferModified();
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
	image.MarkGpuModified();
}
''', '''	CompletePendingUpload(image);
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		T188Close(image, DiagT188::Close::Commit); // Track M, M9d: S7
	}
	image.ClearBufferModified();
	if (image.IsCpuDirty()) {
		image.RefreshComplete();
	}
	image.MarkGpuModified();
}
''')
# ClearImage (RC12)
f.rep('''	auto& image = m_slot_images[id];
	TraceWatchedImage("clear", image);
''', '''	auto& image = m_slot_images[id];
	TraceWatchedImage("clear", image);
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		DiagT188::NoteImageWrite(image.t188); // Track M, M9d (RC12): the clear writes the image
	}
''')
# Ss
f.rep('''	m_texture_cache.DownloadImage(image, buffer, buf_offset, copy_size, std::move(transfer));
	return true;
}
''', '''	m_texture_cache.DownloadImage(image, buffer, buf_offset, copy_size, std::move(transfer));
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		// Track M, M9d: Ss - a synchronization of every level (a volume is always whole) stamps sseq := wseq.
		DiagT188::NoteSync(image.t188, levels == image.info.resources.levels,
		                   m_texture_cache.m_lock.HeldByCurrentThread());
	}
	return true;
}
''')
# Sd
f.rep('''	m_scheduler.DeferPriorityOperation([&download, range, mapped, offset] {
		download.Invalidate(offset, range.size);
		LibKernel::Memory::WriteBacking(range.address, mapped, range.size);
	});
	return true;
}
''', '''	m_scheduler.DeferPriorityOperation([&download, range, mapped, offset] {
		download.Invalidate(offset, range.size);
		LibKernel::Memory::WriteBacking(range.address, mapped, range.size);
	});
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		DiagT188::NoteDownload(image.t188, m_lock.HeldByCurrentThread()); // Track M, M9d: Sd - dseq := wseq
	}
	return true;
}
''')
# S2
f.rep('''void TextureCache::InvalidateMemoryFromGPU(uint64_t address, uint64_t size) {
''', '''void TextureCache::InvalidateMemoryFromGPU(uint64_t address, uint64_t size, DiagT188::Writer writer) {
''')
f.rep('''	const bool diag_m5w2 = DiagM5W2::On();
	if (diag_m5w2) [[unlikely]] {
		DiagM5W2::NoteInvalidateCall();
	}
''', '''	const bool diag_m5w2 = DiagM5W2::On();
	if (diag_m5w2) [[unlikely]] {
		DiagM5W2::NoteInvalidateCall();
	}
	const bool diag_t188 = DiagT188::Mode() >= 1; // Track M, M9d
''')
f.rep('''			DiagM5W2::NoteInvalidateImage(image.IsGpuModified(), image.info.data.address, image.info.data.size,
			                              image.SourceRange().size, address, size); // M6a2: + inv_part_src
		}
''', '''			DiagM5W2::NoteInvalidateImage(image.IsGpuModified(), image.info.data.address, image.info.data.size,
			                              image.SourceRange().size, address, size); // M6a2: + inv_part_src
		}
		if (diag_t188) [[unlikely]] {
			T188Invalidate(image, writer, address, size); // Track M, M9d: S2 (before ClearGpuModified)
		}
''')
members = open(os.path.join(NEW, 'tc_members.inc'), encoding='utf-8').read().replace('\r\n', '\n')
f.rep('@@T188_MEMBERS@@\n', members)
f.save()

# ---------------------------------------------------------------- writers (S1)
f = F('src/graphics/host_gpu/renderer/cache/bufferCache.cpp')
f.rep('''	m_texture_cache.InvalidateMemoryFromGPU(vaddr, size);
	auto [dst, dst_offset] = ObtainBuffer(vaddr, size, true, true);
''', '''	m_texture_cache.InvalidateMemoryFromGPU(vaddr, size, DiagT188::Writer::Fill); // Track M, M9d: S1 (fill)
	auto [dst, dst_offset] = ObtainBuffer(vaddr, size, true, true);
''')
f.rep('''		m_texture_cache.InvalidateMemoryFromGPU(dst_vaddr, size);
''', '''		m_texture_cache.InvalidateMemoryFromGPU(dst_vaddr, size, DiagT188::Writer::Copy); // Track M, M9d: S1 (copy)
''')
f.save()
f = F('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp')
f.rep('''		context.GetTextureCache().InvalidateMemoryFromGPU(address, size);
''', '''		context.GetTextureCache().InvalidateMemoryFromGPU(address, size, DiagT188::Writer::St); // Track M, M9d: S1 (st)
''')
f.save()

# ---------------------------------------------------------------- Svo caller
f = F('src/graphics/presentation/window/swapchain.cpp')
f.rep('''		image.usage.video_out = true;
		cache.UpdateImage(image_id);
''', '''		image.usage.video_out = true;
		cache.UpdateImage(image_id, true); // Track M, M9d: true - site Svo of KYTY_DIAG_T188 (read only at mode >= 1)
''')
f.save()

# ---------------------------------------------------------------- T109
f = F('src/graphics/host_gpu/renderer/renderDraw.cpp')
f.rep('#include "libs/errno.h"\n', '#include "libs/errno.h"\n#include "libs/diagT188.h" // Track M, M9d (KYTY_DIAG_T188, T109)\n')
f.rep('''	if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthBiasEnable, depth_bias_enable)) {
		vk_buffer.setDepthBiasEnable(depth_bias_enable ? VK_TRUE : VK_FALSE);
	}
''', '''	if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthBiasEnable, depth_bias_enable)) {
		vk_buffer.setDepthBiasEnable(depth_bias_enable ? VK_TRUE : VK_FALSE);
	}
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		// Track M, M9d (T109, ROADMAP s122 item 785(b)(4)): the draw with its computed viewports - the array
		// setViewportWithCount took above, after minDepth / maxDepth.
		DiagT109::NoteDraw(depth.image_id ? static_cast<uint32_t>(depth.desc.view_info.format) : 0u,
		                   depth.depth_test_enable, depth.depth_write_enable,
		                   ctx.GetShaderRegisters().db_shader_control.shader_z_export_enable, depth_bias_enable,
		                   reinterpret_cast<const VkViewport*>(viewports.data()), viewport_count);
	}
''')
f.save()
f = F('src/graphics/guest_gpu/command_processor/pm4Handlers.cpp')
f.rep('#include "libs/errno.h"\n', '#include "libs/errno.h"\n#include "libs/diagT188.h" // Track M, M9d (KYTY_DIAG_T188, T109)\n')
f.rep('''	if (cmd_offset == Pm4::DB_RENDER_OVERRIDE) {
		HW::DepthRenderOverride control;
''', '''	if (cmd_offset == Pm4::DB_RENDER_OVERRIDE) {
		if (DiagT188::Mode() >= 1) [[unlikely]] {
			// Track M, M9d (T109, RC14): the one place every write of the register reaches (direct packet, range from
			// DB_COUNT_CONTROL, indirect paths).
			DiagT109::NoteRenderOverride(value);
		}
		HW::DepthRenderOverride control;
''')
f.save()

# ---------------------------------------------------------------- periodic and exit lines
f = F('src/libs/libAudio2.cpp')
f.rep('#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)\n',
      '#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)\n#include "libs/diagT188.h" // Track M, M9d (KYTY_DIAG_T188)\n')
f.rep('''		DiagM5W2::NoteAudioPush(); // M6a: the periodic "M5W2Stat:" line every 4096 queued pushes
	}
''', '''		DiagM5W2::NoteAudioPush(); // M6a: the periodic "M5W2Stat:" line every 4096 queued pushes
	}
	if (DiagT188::Mode() >= 1) [[unlikely]] {
		DiagT188::NoteAudioPush(); // M9d: the periodic "T188Stat:" / "T109Stat:" lines every 4096 queued pushes
	}
''')
f.save()
f = F('src/emulator.cpp')
f.rep('#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)\n',
      '#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)\n#include "libs/diagT188.h" // Track M, M9d (KYTY_DIAG_T188)\n')
f.rep('''		Libs::DiagM5W2::PrintExitStat(); // Track M, M6a: "M5W2Stat: when=exit" (KYTY_DIAG_M5W2=1 only)
		std::quick_exit(0);
''', '''		Libs::DiagM5W2::PrintExitStat(); // Track M, M6a: "M5W2Stat: when=exit" (KYTY_DIAG_M5W2=1 only)
		Libs::DiagT188::PrintExitStat(); // Track M, M9d: "T188Stat/T188Img/T109Stat: when=exit" (KYTY_DIAG_T188 >= 1)
		std::quick_exit(0);
''')
f.rep('''	Libs::DiagM5W2::PrintExitStat(); // Track M, M6a: "M5W2Stat: when=exit" (KYTY_DIAG_M5W2=1 only)
	std::quick_exit(0);
''', '''	Libs::DiagM5W2::PrintExitStat(); // Track M, M6a: "M5W2Stat: when=exit" (KYTY_DIAG_M5W2=1 only)
	Libs::DiagT188::PrintExitStat(); // Track M, M9d: "T188Stat/T188Img/T109Stat: when=exit" (KYTY_DIAG_T188 >= 1)
	std::quick_exit(0);
''')
f.save()

if fails:
    for x in fails:
        print('FAIL', x)
    sys.exit(1)
print('ALL OK')
