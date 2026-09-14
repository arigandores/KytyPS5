#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include <chrono>
#include <cstdlib>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <atomic>

#include "common/alignment.h"
#include "common/assert.h"
#include "common/drawStat.h"
#include "common/gates.h"
#include "common/frameStats.h"
#include "common/parallelCopy.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "kernel/memory.h"

#include <algorithm>
#include <cinttypes>
#include <cstring>
#include <memory>
#include <utility>
#include <vector>

namespace Libs::Graphics {

namespace {

constexpr uint64_t MiB           = 1024 * 1024;
constexpr uint64_t GdsBufferSize = 64 * 1024;

// Gate "stkstat": SynchronizeBuffersInRange (the BDA scan of PrepareBda) runs on this thread.
constinit thread_local bool t_sticky_bda_scan = false;

bool BufferUploadEpochEnabled() {
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_BUFFER_UPLOAD_EPOCH");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

// Gate "buffast": one remembered answer of a read-only buffer request, keyed by the guest range
// the binding asks for. ASTRO BOT makes ~9.6 requests per draw out of a few thousand distinct
// ranges, so the table is sized like the texture memo rather than like the sampler one.
constexpr size_t BufFastSlots = 2048;
static_assert((BufFastSlots & (BufFastSlots - 1)) == 0);

struct BufFastSlot {
	uint64_t vaddr        = 0;
	uint64_t size         = 0;
	uint64_t region_epoch = 0; // MemoryTracker::RangeWriteEpoch, taken before the answer was made
	uint64_t registration = 0; // BufferCache::m_registration_epoch
	uint64_t touch_tick   = 0; // BufferCache::m_gc_tick of the last TouchBuffer through this slot
	uint64_t instance     = 0; // which BufferCache the answer belongs to (0 = the slot is empty)
	BufferId id {};
};

size_t BufFastIndex(uint64_t vaddr, uint64_t size) noexcept {
	const auto mixed = (vaddr >> 4u) * 0x9e3779b97f4a7c15ull + size * 0xff51afd7ed558ccdull;
	return static_cast<size_t>(mixed >> 32u) & (BufFastSlots - 1);
}

} // namespace

void BufferCache::WriteDataBuffer(Buffer& buffer, uint64_t address, const void* source,
                                  uint64_t size) {
	auto* bytes = static_cast<const uint8_t*>(source);
	while (size != 0) {
		const auto chunk  = std::min(size, m_staging_buffer.Size());
		const auto offset = m_staging_buffer.Copy(bytes, chunk, 4);
		buffer.CopyFrom(m_scheduler.Current(), m_staging_buffer, offset, buffer.Offset(address),
		                chunk, vk::AccessFlagBits::eHostWrite,
		                vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
		                vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
		                vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
		                RenderPassEnd::BufferUpload);
		bytes += chunk;
		address += chunk;
		size -= chunk;
	}
}

struct BufferCache::DownloadCopy {
	Buffer*  buffer        = nullptr;
	uint64_t source_offset = 0;
	uint64_t address       = 0;
	uint64_t size          = 0;
};

void BufferCache::Register(BufferId id) {
	ChangeRegister<true>(id);
}

void BufferCache::Unregister(BufferId id) {
	ChangeRegister<false>(id);
}

template <bool insert>
void BufferCache::ChangeRegister(BufferId id) {
	++m_registration_epoch;
	auto& buffer = m_slot_buffers[id];
	PageTable::PageRange pages {};
	EXIT_IF(!PageTable::TryGetPageRange(buffer.CpuAddress(), buffer.Size(), pages));
	for (size_t page = pages.first; page < pages.last_exclusive; ++page) {
		if constexpr (insert) {
			m_page_table[page] = id;
		} else {
			m_page_table[page] = {};
		}
	}
	const auto size_pages = pages.last_exclusive - pages.first;
	if constexpr (insert) {
		const auto [it, inserted] = m_buffers.emplace(buffer.CpuAddress(), id);
		(void)it;
		EXIT_IF(!inserted);
		m_total_used_memory += buffer.Size();
		buffer.lru_id         = m_lru_cache.Insert(id, m_gc_tick);
		buffer.lru_touch_tick = m_gc_tick;
		if (!m_bda_null_page_ready) {
			// Null-page BDA mode (shader emitter): page-table entry 0 (guest page 0, never
			// mapped) holds a zero-filled page that unmapped addresses resolve to. Written
			// here, at the first registration, because the constructor has no command buffer.
			m_bda_null_page_ready = true;
			m_bda_null_page.Fill(0, CACHING_PAGESIZE, 0);
			const vk::DeviceAddress null_page_address = m_bda_null_page.BufferDeviceAddress();
			WriteDataBuffer(m_bda_pagetable_buffer, 0, &null_page_address,
			                sizeof(null_page_address));
		}
		std::vector<vk::DeviceAddress> addresses;
		addresses.reserve(size_pages);
		for (uint64_t i = 0; i < size_pages; ++i) {
			addresses.push_back(buffer.BufferDeviceAddress() + (i << CACHING_PAGEBITS));
		}
		WriteDataBuffer(m_bda_pagetable_buffer, pages.first * sizeof(vk::DeviceAddress),
		                addresses.data(), addresses.size() * sizeof(vk::DeviceAddress));
	} else {
		const auto found = m_buffers.find(buffer.CpuAddress());
		EXIT_IF(found == m_buffers.end() || found->second != id);
		m_buffers.erase(found);
		EXIT_IF(buffer.Size() > m_total_used_memory);
		m_total_used_memory -= buffer.Size();
		m_lru_cache.Free(buffer.lru_id);
		m_bda_pagetable_buffer.Fill(pages.first * sizeof(vk::DeviceAddress),
		                            size_pages * sizeof(vk::DeviceAddress), 0);
		buffer.is_deleted = true;
	}
}

void BufferCache::TouchBuffer(Buffer& buffer) {
	if (!buffer.is_deleted) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BufLruTouches, 1);
		// Touch returns on `item.tick >= tick` for all but the first touch of a GC tick, and the
		// LRU node is cold (a deque block of its own). The copy is only set to a tick Insert/Touch
		// ran with and item ticks never decrease, so a matching copy proves the node holds it.
		if (buffer.lru_touch_tick == m_gc_tick) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BufLruRepeats, 1);
			if (!Common::Gates::Enabled(Common::Gates::Gate::BufLru)) {
				m_lru_cache.Touch(buffer.lru_id, m_gc_tick);
			}
		} else {
			buffer.lru_touch_tick = m_gc_tick;
			m_lru_cache.Touch(buffer.lru_id, m_gc_tick);
		}
		ClearPrefetchPending(buffer);
	}
}

bool BufferCache::TouchReadOnlyBuffer(BufferId id, uint64_t vaddr, uint64_t size) {
	auto* buffer = m_slot_buffers.try_get(id);
	if (buffer == nullptr || buffer->is_deleted || !buffer->IsInBounds(vaddr, size)) return false;
	TouchBuffer(*buffer);
	return true;
}

void BufferCache::ClearPrefetchPending(Buffer& buffer) {
	if (buffer.prefetch_pending) {
		buffer.prefetch_pending = false;
		m_prefetch_pending_bytes -= std::min(m_prefetch_pending_bytes, buffer.Size());
	}
}

void BufferCache::DeleteBuffer(BufferId id) {
	if (IsBufferInvalid(id)) {
		return;
	}
	ClearPrefetchPending(m_slot_buffers[id]);
	Unregister(id);
	if (m_scheduler.Active()) {
		m_scheduler.DeferOperation([this, id] { m_slot_buffers.erase(id); });
	} else {
		m_slot_buffers.erase(id);
	}
}

// KYTY_STAGING_MB=<n>: size of the upload staging ring (default 1024). A scene cut of ASTRO BOT
// uploads up to ~950 MB of textures in one frame; a 512 MB ring wrapped inside the frame and
// waited for the GPU to consume the first half (semwait_gpu 13-35 ms per cut).
uint64_t BufferCache::StagingRingBytes() {
	const char* value = std::getenv("KYTY_STAGING_MB");
	const auto  mb    = value != nullptr ? std::strtoull(value, nullptr, 10) : 1024u;
	return std::clamp<uint64_t>(mb, 64u, 4096u) * MiB;
}

// Copies a guest range into the staging ring through the backing view. Large ranges inside one
// mapping are queued to the copy pool (AsyncMemcpy) and complete before the next vkQueueSubmit;
// the rest is copied inline.
void BufferCache::CopyGuestToStaging(uint8_t* staging, uint64_t vaddr, uint64_t size) {
	const void* backing = nullptr;
	if (size >= Common::ASYNC_COPY_MIN_BYTES &&
	    Libs::LibKernel::Memory::TryGetBackingPointer(vaddr, size, &backing)) {
		Common::AsyncMemcpy(staging, backing, static_cast<size_t>(size));
		return;
	}
	if (!Libs::LibKernel::Memory::TryReadBacking(vaddr, staging, size) &&
	    !Libs::LibKernel::Memory::TryReadPrtBacking(vaddr, staging, size)) {
		// Not backed guest memory (module image, flexible memory): read the guest view directly.
		std::memcpy(staging, reinterpret_cast<const void*>(vaddr), static_cast<size_t>(size));
	}
}

std::pair<uint64_t, uint64_t> BufferCache::DownloadEnvelope(const DownloadCopy& copy) {
	if (copy.buffer == nullptr || copy.size == 0 || copy.source_offset > copy.buffer->Size() ||
	    copy.size > copy.buffer->Size() - copy.source_offset) {
		EXIT("BufferCache: invalid download copy\n");
	}
	const auto begin = Common::AlignDown(copy.source_offset, 4);
	if (copy.source_offset + copy.size > UINT64_MAX - 3) {
		EXIT("BufferCache: download copy alignment overflow\n");
	}
	const auto end = Common::AlignUp(copy.source_offset + copy.size, 4);
	if (end > copy.buffer->Size()) {
		EXIT("BufferCache: aligned download copy exceeds its owner\n");
	}
	return {begin, end - begin};
}

void BufferCache::DownloadBufferMemory(std::span<const DownloadCopy> copies, const char* reason) {
	Common::DrawStat::Mark(Common::DrawStat::Sync);
	Common::FrameStats::Scope download_scope(Common::FrameStats::Counter::DownloadNs,
	                                         Common::FrameStats::Counter::Downloads);
	// KYTY_FAULT_TRACE=1: every synchronous drain with its reason (a CPU write into GPU-written
	// memory, the buffer garbage collector, a guest stack release).
	static const bool drain_trace = std::getenv("KYTY_FAULT_TRACE") != nullptr;
	const auto        drain_t0    = drain_trace ? std::chrono::steady_clock::now()
	                                            : std::chrono::steady_clock::time_point {};
	uint64_t          drain_bytes = 0;
	if (drain_trace) {
		for (const auto& c: copies) {
			drain_bytes += c.size;
		}
	}
	const auto drain_report = [&] {
		if (!drain_trace) {
			return;
		}
		const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
		                    std::chrono::steady_clock::now() - drain_t0)
		                    .count();
		LOGF("DrainTrace: sync download reason=%s copies=%zu bytes=0x%" PRIx64 " first=0x%016" PRIx64
		     " took %lld us" "\n",
		     reason, copies.size(), drain_bytes, copies.empty() ? 0u : copies[0].address,
		     static_cast<long long>(us));
	};
	std::vector<DownloadCopy> batch;
	batch.reserve(copies.size());
	uint64_t                  packed_size = 0;
	auto&                     download    = m_download_buffer;
	const auto flush = [&] {
		const auto [mapped, base_offset] = download.Map(packed_size, DOWNLOAD_ALIGNMENT);
		EXIT_IF(mapped == nullptr);
		uint64_t cursor = 0;
		for (const auto& copy: batch) {
			const auto [source_begin, envelope_size] = DownloadEnvelope(copy);
			download.CopyFrom(m_scheduler.Current(), *copy.buffer, source_begin, base_offset + cursor,
			                  envelope_size, vk::AccessFlagBits::eMemoryWrite, vk::AccessFlags {},
			                  vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
			                  vk::AccessFlagBits::eHostRead, RenderPassEnd::Download);
			cursor += AlignDownload(envelope_size);
		}
		download.Commit();
		const auto completion_tick = m_scheduler.CurrentTick();
		{
			Common::FrameStats::SiteScope site_scope("download");
			m_scheduler.Finish();
			m_scheduler.WaitPriorityOperations(completion_tick);
		}
		cursor = 0;
		for (const auto& copy: batch) {
			const auto [source_begin, envelope_size] = DownloadEnvelope(copy);
			const auto offset = cursor + copy.source_offset - source_begin;
			download.Invalidate(base_offset + offset, copy.size);
			Libs::LibKernel::Memory::WriteBacking(copy.address, mapped + offset, copy.size);
			cursor += AlignDownload(envelope_size);
		}
		batch.clear();
		packed_size = 0;
	};
	for (auto copy: copies) {
		while (copy.size != 0) {
			const auto available = download.Size() - packed_size;
			const auto prefix    = copy.source_offset & 3u;
			const auto bytes     = std::min(copy.size, available - prefix);
			DownloadCopy part {copy.buffer, copy.source_offset, copy.address, bytes};
			const auto [source_begin, envelope_size] = DownloadEnvelope(part);
			(void)source_begin;
			packed_size += AlignDownload(envelope_size);
			batch.push_back(part);
			copy.source_offset += bytes;
			copy.address += bytes;
			copy.size -= bytes;
			if (packed_size == download.Size()) {
				flush();
			}
		}
	}
	drain_report();
}

BufferCache::BufferCache(GraphicContext& graphics, CommandScheduler& scheduler,
                         PageManager& page_manager, TextureCache& texture_cache)
    : m_graphics(graphics), m_scheduler(scheduler), m_fault_manager(graphics, scheduler, *this),
      m_host_import(graphics),
      m_gds_buffer(graphics, scheduler, MemoryUsage::Stream, 0, AllFlags, GdsBufferSize),
      m_bda_pagetable_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
                             BDA_PAGETABLE_SIZE),
      m_bda_null_page(graphics, scheduler, MemoryUsage::DeviceLocal, 0,
                      AllFlags | vk::BufferUsageFlagBits::eShaderDeviceAddress, CACHING_PAGESIZE),
      m_memory_tracker(page_manager),
      m_staging_buffer(graphics, scheduler, MemoryUsage::Upload, StagingRingBytes()),
      m_stream_buffer(graphics, scheduler, MemoryUsage::Stream, 64 * MiB),
      m_download_buffer(graphics, scheduler, MemoryUsage::Download, 32 * MiB),
      m_device_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 128 * MiB),
      m_texture_cache(texture_cache) {
	std::memset(m_gds_buffer.Mapped().data(), 0, static_cast<size_t>(m_gds_buffer.Size()));
	m_gds_buffer.Flush(0, m_gds_buffer.Size());
	m_gds_host_epoch++;
	SetVulkanObjectNameF(m_graphics.device, m_bda_pagetable_buffer.Handle(),
	                     "BDA Page Table Buffer");
	// Null-page BDA mode (shader emitter): page-table entry 0 (guest page 0, never mapped)
	// holds a zero-filled page that unmapped addresses resolve to.
	SetVulkanObjectNameF(m_graphics.device, m_bda_null_page.Handle(), "BDA Null Page");
	const auto null_id =
	    m_slot_buffers.insert(m_graphics, m_scheduler, MemoryUsage::DeviceLocal, 0, AllFlags, 16);
	EXIT_IF(null_id != NULL_BUFFER_ID);
	SetVulkanObjectNameF(m_graphics.device, GetBuffer(null_id).Handle(), "Kyty.NullBuffer");
	if (!m_graphics.CanReportMemoryUsage()) {
		return;
	}
	constexpr int64_t GiB              = 1024ll * 1024 * 1024;
	constexpr int64_t target_threshold = 8 * GiB;
	const auto        budget =
	    static_cast<int64_t>(std::min<uint64_t>(m_graphics.GetTotalMemoryBudget(), INT64_MAX));
	const auto threshold = std::min(budget, target_threshold);
	const auto expected  = std::min(budget - 6 * threshold / 10, budget - GiB);
	const auto critical  = std::min(budget - 2 * threshold / 10, budget - GiB / 2);
	m_trigger_gc_memory  = static_cast<uint64_t>(std::max<int64_t>(expected, GiB));
	m_critical_gc_memory = static_cast<uint64_t>(std::max<int64_t>(critical, 2 * GiB));
}

BufferCache::~BufferCache() {
	if (!m_gpu_modified_ranges.Empty()) {
		EXIT("BufferCache: destroyed with pending GPU-modified ranges\n");
	}
	for (const auto& [vaddr, id]: m_buffers) {
		(void)vaddr;
		const auto& buffer = m_slot_buffers[id];
		if (m_memory_tracker.IsRegionGpuModified(buffer.CpuAddress(), buffer.Size())) {
			EXIT("BufferCache: destroyed with GPU-modified buffer\n");
		}
	}
	m_buffers.clear();
}

void BufferCache::InvalidateMemory(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: invalid memory-invalidation range\n");
	}
	m_memory_tracker.InvalidateRegion(
		vaddr, size, [this, vaddr, size] { ReadMemory(vaddr, size, true); },
		Common::Gates::Enabled(Common::Gates::Gate::ProtectBatch));
}

void BufferCache::InvalidateWriteFault(uint64_t fault_vaddr, uint64_t window_begin,
                                       uint64_t window_size) {
	// on_flush reads the faulting byte only, as InvalidateMemory(fault_vaddr, 1) does.
	m_memory_tracker.InvalidateWriteFault(
		fault_vaddr, window_begin, window_size,
		[this, fault_vaddr] { ReadMemory(fault_vaddr, 1, true); },
		Common::Gates::Enabled(Common::Gates::Gate::ProtectBatch));
}

uint64_t BufferCache::WriteFaultArmedPages(uint64_t fault_vaddr, uint64_t window_begin,
                                           uint64_t window_size) {
	return m_memory_tracker.WriteFaultArmedPages(fault_vaddr, window_begin, window_size);
}

void BufferCache::ReadMemory(uint64_t vaddr, uint64_t size, bool is_write) {
	if (!GuestGpu::IsGpuThread() && CommandScheduler::InDeferredOperation()) {
		EXIT("unsupported buffer readback from an asynchronous GPU completion, "
		     "addr=0x%016" PRIx64 " size=0x%016" PRIx64 "\n",
		     vaddr, size);
	}
	static const bool trace = std::getenv("KYTY_FAULT_TRACE") != nullptr;
	const auto        t0    = std::chrono::steady_clock::now();
	auto&             gpu   = m_scheduler.Context().GetGpu();
	// KYTY_STALE_READ=0: a guest CPU read of GPU-written memory waits for the GPU queue to
	// reach the read (old behaviour). Default: the read observes the last completed GPU data at
	// once, and the in-flight data lands in guest memory when the GPU completes it - the
	// hardware semantics of an unfenced read (ASTRO BOT reads the exposure value and other GPU
	// outputs every frame from its draw threads; each read cost a 10-16 ms drain).
	static const bool stale_reads = [] {
		const char* value = std::getenv("KYTY_STALE_READ");
		return value == nullptr || value[0] != '0';
	}();
	if (GuestGpu::IsGpuThread() || is_write) {
		gpu.SendCommandSync([this, vaddr, size, is_write] { ReadMemoryOnGpu(vaddr, size, is_write); });
	} else if (stale_reads) {
		if (m_memory_tracker.IsRegionGpuModified(vaddr, size)) {
			// Open the page right here (the GPU thread may be busy for milliseconds: a wait for
			// the flip, a shader compilation); it records the download of the whole window when
			// it gets to the command.
			m_memory_tracker.MarkRegionAsStaleReadable(vaddr, size);
			gpu.SendCommand([this, vaddr, size] { ServeStaleRead(vaddr, size); });
		}
	} else {
		// Guest thread: nothing to do if the page went clean meanwhile (prefetch, another drain).
		for (uint32_t attempt = 0; attempt < 64 && m_memory_tracker.IsRegionGpuModified(vaddr, size);
		     attempt++) {
			AsyncReadback job;
			gpu.SendCommandSync([this, vaddr, size, &job] { job = BeginAsyncReadback(vaddr, size); });
			if (job.pieces.empty()) {
				break;
			}
			{
				Common::FrameStats::SiteScope site_scope("download-guest");
				m_scheduler.GetMasterSemaphore().Wait(job.tick);
			}
			bool complete = false;
			gpu.SendCommandSync([this, &job, &complete] { complete = FinishAsyncReadback(job); });
			if (complete) {
				break;
			}
		}
	}
	if (trace) {
		const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
		                    std::chrono::steady_clock::now() - t0)
		                    .count();
		if (us >= 500) {
			LOGF("DrainTrace: ReadMemory %s addr=0x%016" PRIx64 " size=0x%" PRIx64 " took %lld us" "\n",
			     is_write ? "write" : "read ", vaddr, size, static_cast<long long>(us));
		}
	}
}

void BufferCache::ReadMemoryOnGpu(uint64_t vaddr, uint64_t size, bool is_write) {
	if (is_write && !IsRegionRegistered(vaddr, size)) {
		return;
	}
	auto& buffer = m_slot_buffers[FindBuffer(vaddr, size)];

	// Widen nearby CPU reads so they share one GPU drain.
	constexpr uint64_t WindowSize   = 512 * 1024;
	const auto         buffer_begin = buffer.CpuAddress();
	const auto         buffer_end   = buffer_begin + buffer.Size();
	const auto         window_begin = std::max(vaddr & ~(WindowSize - 1), buffer_begin);
	const auto window_end = std::min(std::max(window_begin + WindowSize, vaddr + size), buffer_end);

	std::vector<DownloadCopy> copies;
	m_memory_tracker.ForEachDownloadRange<false>(
	    window_begin, window_end - window_begin, [&](uint64_t address, uint64_t bytes) noexcept {
		    m_memory_tracker.ValidateGpuDirtyPages(m_gpu_modified_ranges, address, bytes,
		                                           "memory invalidation");
		    m_gpu_modified_ranges.ForEachInRange(address, bytes, [&](uint64_t start, uint64_t end) {
			    copies.push_back({&buffer, buffer.Offset(start), start, end - start});
		    });
	    });
	if (!copies.empty()) {
		// Remember the window: the same regions are read every frame (PrefetchHotReadbacks).
		auto& hot = m_hot_regions[vaddr >> HotBucketBits];
		hot.begin = hot.hits == 0 ? window_begin : std::min(hot.begin, window_begin);
		hot.end   = hot.hits == 0 ? window_end : std::max(hot.end, window_end);
		hot.hits++;
		hot.last_hit_frame = m_scheduler.Context().GetGpu().GetFrameNum();
		static const bool trace = std::getenv("KYTY_FAULT_TRACE") != nullptr;
		const auto        t0    = std::chrono::steady_clock::now();
		DownloadBufferMemory(copies, is_write ? "cpu-write" : "cpu-read");
		if (trace) {
			uint64_t bytes = 0;
			for (const auto& c: copies) {
				bytes += c.size;
			}
			const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
			                    std::chrono::steady_clock::now() - t0)
			                    .count();
			LOGF("DrainTrace: download %s addr=0x%016" PRIx64 " size=0x%" PRIx64 " copies=%zu bytes=0x%" PRIx64
			     " took %lld us" "\n",
			     is_write ? "write" : "read ", vaddr, size, copies.size(), bytes,
			     static_cast<long long>(us));
		}
		// The enumeration covered whole dirty pages and every exact interval on them.
		m_memory_tracker.UnmarkRegionAsGpuModified(window_begin, window_end - window_begin);
	}
	if (is_write) {
		m_memory_tracker.MarkRegionAsCpuModified(vaddr, size);
	}
}

BufferId BufferCache::FindBuffer(uint64_t vaddr, uint64_t size) {
	if (vaddr == 0) {
		return NULL_BUFFER_ID;
	}
	if (!GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: invalid buffer discovery request\n");
	}
	const auto* owner = m_page_table.Find(vaddr >> PageTable::kPageBits);
	if (owner != nullptr && *owner) {
		auto& buffer = m_slot_buffers[*owner];
		if (buffer.IsInBounds(vaddr, size)) {
			return *owner;
		}
	}
	return CreateBuffer(vaddr, size);
}

BufferCache::OverlapResult BufferCache::ResolveOverlaps(uint64_t vaddr, uint64_t size) {
	static constexpr int      StreamLeapThreshold = 16;
	static constexpr uint64_t StreamLeapSize      = CACHING_PAGESIZE * 128;

	auto       begin      = vaddr;
	auto       end        = vaddr + size;
	const auto find_first = [&](uint64_t address) {
		auto first = m_buffers.lower_bound(address);
		if (first != m_buffers.begin()) {
			const auto  previous = std::prev(first);
			const auto& buffer   = m_slot_buffers[previous->second];
			if (buffer.CpuAddress() + buffer.Size() > address) {
				first = previous;
			}
		}
		return first;
	};
	auto first           = find_first(begin);
	auto last            = first;
	int  stream_score    = 0;
	bool has_stream_leap = false;
	for (; last != m_buffers.end() && last->first < end; ++last) {
		const auto& buffer        = m_slot_buffers[last->second];
		const auto  buffer_begin  = buffer.CpuAddress();
		const auto  buffer_end    = buffer_begin + buffer.Size();
		const bool  expands_left  = buffer_begin < begin;
		const bool  expands_right = buffer_end > end;
		begin                     = std::min(begin, buffer_begin);
		end                       = std::max(end, buffer_end);
		if (!has_stream_leap && (stream_score += buffer.StreamScore()) > StreamLeapThreshold) {
			has_stream_leap = true;
			// Reserve space in the incoming stream's direction of growth.
			// The old buffer extending left of the request predicts growth to the right, and vice versa.
			if (expands_left) {
				end += std::min(StreamLeapSize, PageTable::kAddressSpaceSize - end);
			}
			if (expands_right) {
				const auto minimum = CACHING_PAGESIZE * 2;
				if (begin > minimum) {
					begin -= std::min(StreamLeapSize, begin - minimum);
				}
				first = find_first(begin);
				begin = std::min(begin, first->first);
			}
		}
	}
	return {first, last, begin, end, has_stream_leap};
}

void BufferCache::JoinOverlap(BufferId new_id, BufferId overlap_id, bool accumulate_stream_score) {
	auto& new_buffer = m_slot_buffers[new_id];
	auto& overlap    = m_slot_buffers[overlap_id];
	if (accumulate_stream_score) {
		new_buffer.IncreaseStreamScore(overlap.StreamScore() + 1);
	}
	new_buffer.CopyFrom(m_scheduler.Current(), overlap, 0,
	                    overlap.CpuAddress() - new_buffer.CpuAddress(), overlap.Size());
	DeleteBuffer(overlap_id);
}

BufferId BufferCache::CreateBuffer(uint64_t vaddr, uint64_t size) {
	EXIT_IF(m_scheduler.Current().IsInvalid());
	Common::DrawStat::Mark(Common::DrawStat::BufNew);
	const auto end = Common::AlignUp(vaddr + size, CACHING_PAGESIZE);
	vaddr = Common::AlignDown(vaddr, CACHING_PAGESIZE);
	size               = end - vaddr;
	const auto overlap = ResolveOverlaps(vaddr, size);

	const auto id = m_slot_buffers.insert(
	    m_graphics, m_scheduler, MemoryUsage::DeviceLocal, overlap.begin,
	    AllFlags | vk::BufferUsageFlagBits::eShaderDeviceAddress, overlap.end - overlap.begin);
	const auto& buffer = m_slot_buffers[id];
	SetVulkanObjectNameF(m_graphics.device, buffer.Handle(),
	                     "Kyty.GameBuffer[guest=0x{:016x} size=0x{:x}]", overlap.begin,
	                     overlap.end - overlap.begin);
	uint64_t joined_bytes = 0;
	uint32_t joined       = 0;
	for (auto it = overlap.first; it != overlap.last;) {
		const auto old_id = (it++)->second;
		joined_bytes += m_slot_buffers[old_id].Size();
		joined++;
		JoinOverlap(id, old_id, !overlap.has_stream_leap);
	}
	static const bool trace = std::getenv("KYTY_STREAM_TRACE") != nullptr;
	if (trace && joined_bytes >= (16u << 20)) {
		LOGF("BufferJoin: new=0x%016" PRIx64 " size=0x%" PRIx64 " joined=%u bytes=%" PRIu64 " leap=%d req=0x%016" PRIx64 "+0x%" PRIx64 "\n",
		     overlap.begin, overlap.end - overlap.begin, joined, joined_bytes, overlap.has_stream_leap ? 1 : 0, vaddr, size);
	}
	Register(id);
	return id;
}

// Witness for "nothing has written this range since it was uploaded". The global CPU epoch is
// bumped by every page fault in the process, so with it a recorded upload is stale within the same
// frame; the region epochs of the range itself only move when that range is written (gate
// "regionepoch").
std::pair<uint64_t, uint8_t> BufferCache::UploadEpoch(uint64_t vaddr, uint64_t size) {
	if (Common::Gates::Enabled(Common::Gates::Gate::RegionEpoch)) {
		return {m_memory_tracker.RangeWriteEpoch(vaddr, size), 1};
	}
	return {m_memory_tracker.CpuWriteEpoch(), 0};
}

// Gate "syncfree". A read-only synchronization of a range whose tracking regions all exist and
// hold no CPU-dirty page does nothing under the region locks: the mask of ForEachModifiedRange is
// empty, clearing it changes no bit, and UpdateProtection finds m_writable == m_cpu_dirty (every
// locked writer of m_cpu_dirty republishes m_writable before it releases the lock). The lock is
// skipped when a lock-free read says the range is clean. Why a stale "clean" is safe:
// - CPU-dirty bits are cleared only on this thread (ForEachUploadRange runs on the GuestGpu
//   thread), so a clear bit was not being cleared under this read; every other writer sets bits
//   through BitArray::SetRangeRelaxed, which a relaxed read may observe word by word.
// - A guest thread announcing a write after this read publishes the bits BEFORE the epochs
//   (RegionManager::ChangeState). Its epochs therefore move after this read, and this read comes
//   after the epoch snapshot SynchronizeBuffer took first and stores as the buffer's upload
//   epoch: the next HasCurrentUpload check fails and the next synchronization finds the bits
//   under the lock. The write itself resumes only after its announcement, i.e. after this read.
// Only the GuestGpu thread may skip.
bool BufferCache::SyncFreeSkip(uint64_t vaddr, uint64_t size) {
	if (!Common::Gates::Enabled(Common::Gates::Gate::SyncFree) || !GuestGpu::IsGpuThread() ||
		!m_memory_tracker.IsRegionCpuCleanFast(vaddr, size)) {
		return false;
	}
	if (Common::Gates::Enabled(Common::Gates::Gate::SyncFreeVerify) &&
		m_memory_tracker.IsRegionCpuModified(vaddr, size)) {
		// A guest thread may have announced a write between the two queries; only a second
		// lock-free answer that still reads "clean" contradicts the locked one.
		if (m_memory_tracker.IsRegionCpuCleanFast(vaddr, size)) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SyncFreeMismatch, 1);
			static std::atomic<uint32_t> logged {0};
			if (logged.fetch_add(1, std::memory_order_relaxed) < 64) {
				LOGF("SyncFreeVerify: MISMATCH addr=0x%016" PRIx64 " size=0x%" PRIx64 "\n", vaddr, size);
			}
		}
		return false; // take the locked path
	}
	return true;
}

void BufferCache::NoteWriteFault(uint64_t fault_vaddr, uint64_t window_begin,
                                 uint64_t window_size) {
	const auto page = fault_vaddr & ~(TRACKER_PAGE_SIZE - 1);
	if (Common::Gates::Enabled(Common::Gates::Gate::StickyStat) && Common::FrameStats::Enabled()) {
		// A1 ceiling (gate "stkstat"): did this page write-fault in this or the previous frame as well.
		// The faulting page only, whatever the "faultkb" window opened. No lock and no allocation here
		// (a vectored exception handler of any thread): the stamps live in the tracking region.
		namespace FS    = Common::FrameStats;
		const auto kind = m_memory_tracker.NoteWriteFaultStat(fault_vaddr, GpuTimeProfiler::Frame());
		FS::Add(FS::Counter::StickyFaults, 1);
		if (kind != 0) {
			FS::Add(FS::Counter::StickyFaultRepeat, 1);
			if (kind == 2) {
				FS::Add(FS::Counter::StickyFaultRepeatSame, 1);
			}
			if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
				FS::Add(FS::Counter::StickyFaultRepeatGpu, 1);
			}
			if (m_texture_cache.MayHaveImages(page, TRACKER_PAGE_SIZE)) {
				FS::Add(FS::Counter::StickyFaultRepeatImg, 1);
			}
		}
	}
	// pb_stuck: one thread faulting on one page again and again means its handler returns while the
	// host protection still denies the write. Must stay 0 (with and without "protbatch").
	// Repeats alone are normal: the upload of every frame clears the CPU-dirty bits and arms the
	// write watcher again, so a guest thread that keeps writing one buffer faults on the same page
	// every frame. A handler that returns on a page the host still protects faults again at once,
	// so the watchdog measures repeats inside one millisecond.
	static thread_local uint64_t last_page = 0;
	static thread_local uint64_t last_ns   = 0;
	static thread_local uint32_t repeats   = 0;
	const auto                   now_ns    = Common::FrameStats::NowNs();
	if (page != last_page || now_ns - last_ns > 1000000u) {
		last_page = page;
		repeats   = 0;
	}
	last_ns = now_ns;
	if (page == last_page && ++repeats >= 32 && (repeats & (repeats - 1u)) == 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BatchStuck, 1);
		static std::atomic<uint32_t> logged {0};
		if (logged.fetch_add(1, std::memory_order_relaxed) < 16) {
			LOGF("ProtectBatch: STUCK write faults addr=0x%016" PRIx64 " repeats=%u\n", fault_vaddr,
				 repeats);
		}
	}
	if (Common::Gates::Enabled(Common::Gates::Gate::ProtectBatchVerify)) {
		static thread_local uint32_t sample = 0;
		if ((sample++ & 7u) == 0) {
			// The faulting page first (Verify probes three pages of a range), then the range the
			// fault opened (knob "faultkb").
			m_memory_tracker.VerifyProtection(fault_vaddr & ~(TRACKER_PAGE_SIZE - 1), TRACKER_PAGE_SIZE);
			if (window_size != TRACKER_PAGE_SIZE) {
				m_memory_tracker.VerifyProtection(window_begin, window_size);
			}
		}
	}
}

bool BufferCache::SynchronizeBuffer(Buffer& buffer, uint64_t vaddr, uint64_t size, bool is_written,
                                    bool is_texel_buffer) {
	Common::FrameStats::Scope sync_scope(Common::FrameStats::Counter::BindBufSyncNs);
	// Gate "stkstat" (A1 ceiling; statistics only): the candidate pages a sticky mechanism would
	// compare with their shadow on this synchronization - every one but a small read-only ObtainBuffer
	// request, which would take the stream copy instead (stk_stream_hot) - and the arm history of the
	// upload below (RegionManager::NoteUploadStat).
	const bool       sticky_stat = !is_written && Common::Gates::Enabled(Common::Gates::Gate::StickyStat) &&
	                               Common::FrameStats::Enabled();
	StickyUploadStat upload_stat {};
	if (sticky_stat) {
		upload_stat.frame           = GpuTimeProfiler::Frame();
		upload_stat.bda             = t_sticky_bda_scan;
		upload_stat.may_have_images = [](void* context, uint64_t page) noexcept {
			return static_cast<BufferCache*>(context)->m_texture_cache.MayHaveImages(page, TRACKER_PAGE_SIZE);
		};
		upload_stat.context = this;
		if (upload_stat.bda || size > CACHING_PAGESIZE) {
			Common::FrameStats::Add(Common::FrameStats::Counter::StickyCheckEstimate,
			                        m_memory_tracker.StickyCandidatePages(vaddr, size, upload_stat.frame, false));
		}
	}
	const auto [cpu_epoch, epoch_kind] = UploadEpoch(vaddr, size);
	if (BufferUploadEpochEnabled() && !is_written &&
	    buffer.HasCurrentUpload(cpu_epoch, epoch_kind, vaddr, size)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BufEpochHits, 1);
		return is_texel_buffer ? SynchronizeBufferFromImage(buffer, vaddr, size) : false;
	}
	std::vector<vk::BufferCopy> copies;
	uint64_t                    total_size = 0;
	vk::Buffer                  source;
	bool                        provisional = false; // gate "armdefer": pages left dirty to settle
	if (!is_written && SyncFreeSkip(vaddr, size)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SyncFreeSkips, 1);
	} else {
		provisional = m_memory_tracker.ForEachUploadRange(
			vaddr, size, is_written,
			[&](uint64_t address, uint64_t bytes) noexcept {
				copies.emplace_back(total_size, buffer.Offset(address), bytes);
				total_size += bytes;
			},
			[&]() noexcept { source = UploadCopies(buffer, copies, total_size); },
			Common::Gates::Enabled(Common::Gates::Gate::ProtectBatch),
			sticky_stat ? &upload_stat : nullptr);
		if (source && Common::Gates::Enabled(Common::Gates::Gate::ProtectBatchVerify)) {
			m_memory_tracker.VerifyProtection(vaddr, size);
		}
	}
	if (!is_written && copies.empty()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SyncNoop, 1);
	}
	RecordBufferCopies(buffer, source, copies, total_size);
	// Keep the epoch from before synchronization, so concurrent writes force another upload.
	// This is only the requested interval: a different part of the same buffer may remain dirty.
	// A provisional upload (gate "armdefer") records no current epoch: its pages are still dirty
	// and the next synchronization has to find them.
	buffer.upload_epoch = provisional ? 0 : cpu_epoch;
	buffer.upload_epoch_kind = epoch_kind;
	buffer.upload_begin = vaddr;
	buffer.upload_end = vaddr + size;
	if (is_texel_buffer && !is_written) {
		return SynchronizeBufferFromImage(buffer, vaddr, size);
	}
	return false;
}

void BufferCache::RecordBufferCopies(Buffer& buffer, vk::Buffer source,
                                     std::span<const vk::BufferCopy> copies, uint64_t total_size) {
	if (!source) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::SyncBufUploads, 1);
	Common::FrameStats::Add(Common::FrameStats::Counter::SyncBufUploadBytes, total_size);
	{
		// Session 61, item 2 ceiling: an upload with no draw or dispatch started by this thread
		// since the previous upload could have shared its barrier pair and pass break.
		thread_local uint32_t last_ops = UINT32_MAX;
		if (last_ops == Common::DrawStat::t_ops) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SyncBufUploadSeries, 1);
		}
		last_ops = Common::DrawStat::t_ops;
	}
	auto& command = m_scheduler.Current();
	command.EndRendering(RenderPassEnd::BufferUpload);
	const auto native = command.Handle();
	vk::BufferMemoryBarrier before {};
	before.srcAccessMask = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite |
	                       vk::AccessFlagBits::eTransferRead |
	                       vk::AccessFlagBits::eTransferWrite;
	before.dstAccessMask       = vk::AccessFlagBits::eTransferWrite;
	before.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	before.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	before.buffer              = buffer.Handle();
	before.offset              = 0;
	before.size                = buffer.Size();
	native.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
	                       vk::PipelineStageFlagBits::eTransfer,
	                       vk::DependencyFlagBits::eByRegion, 0, nullptr, 1, &before, 0, nullptr);
	native.copyBuffer(source, buffer.Handle(), static_cast<uint32_t>(copies.size()), copies.data());
	auto after          = before;
	after.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
	after.dstAccessMask = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite;
	native.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
	                       vk::PipelineStageFlagBits::eAllCommands,
	                       vk::DependencyFlagBits::eByRegion, 0, nullptr, 1, &after, 0, nullptr);
	m_scheduler.GpuMark(GpuTimeProfiler::Kind::BufferUpload,
	                    std::bit_width(total_size >> 10u)); // log2 of KiB
}

vk::Buffer BufferCache::UploadCopies(Buffer& buffer, std::span<vk::BufferCopy> copies,
                                     uint64_t total_size) {
	if (copies.empty()) {
		return nullptr;
	}
	Common::DrawStat::Mark(Common::DrawStat::BufUp);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);

	auto [mapped, base_offset] = m_staging_buffer.Map(total_size, 4);
	if (mapped != nullptr) {
		for (auto& copy: copies) {
			const auto address = buffer.CpuAddress() + copy.dstOffset;
			CopyGuestToStaging(mapped + copy.srcOffset, address, copy.size);
			copy.srcOffset += base_offset;
		}
		if (!m_staging_buffer.IsCoherent()) {
			Common::WaitAsyncCopies(); // Commit flushes the range
		}
		m_staging_buffer.Commit();
		return m_staging_buffer.Handle();
	}

	auto temporary = std::make_unique<Buffer>(m_graphics, m_scheduler, MemoryUsage::Upload, 0,
	                                         vk::BufferUsageFlagBits::eTransferSrc, total_size);
	for (const auto& copy: copies) {
		const auto address = buffer.CpuAddress() + copy.dstOffset;
		std::memcpy(temporary->Mapped().data() + copy.srcOffset,
		            reinterpret_cast<const void*>(address), copy.size);
	}
	temporary->Flush(0, total_size);
	const auto handle = temporary->Handle();
	m_scheduler.DeferOperation([owner = std::move(temporary)]() mutable { owner.reset(); });
	return handle;
}

std::pair<Buffer*, uint64_t> BufferCache::ObtainBuffer(uint64_t vaddr, uint64_t size,
                                                       bool is_written, bool is_texel_buffer,
                                                       BufferId id, bool memoizable) {
	Common::FrameStats::Scope obtain_scope(Common::FrameStats::Counter::ObtainBufNs);
	Common::FrameStats::Add(Common::FrameStats::Counter::ObtainBufs, 1);
	// Gate "buffast": a read-only binding asking for a guest range it already asked for takes the
	// buffer the previous request resolved, instead of FindBuffer + TouchBuffer +
	// SynchronizeBuffer, while nothing those would act on has happened:
	//  - a CPU write to the range moves the write epochs of its tracking regions
	//    (RegionManager::ChangeState<Cpu, true>) - the witness the "regionepoch" gate already
	//    gives HasCurrentUpload, but kept per range here instead of per buffer, where the ranges
	//    of one buffer overwrite each other's upload interval. The epochs are published under
	//    the region lock after the dirty bits and before the pages become writable, so a write
	//    that crossed an upload always moves them after the snapshot below (see SyncFreeSkip).
	//    Untracking announces itself the same way (UntrackMemory marks CPU-dirty), and a range
	//    whose regions do not all exist stamps as 0 and is never remembered.
	//  - creating, joining or deleting a buffer moves m_registration_epoch (ChangeRegister), so
	//    an unchanged one means this id still owns this range, at the same address and size.
	//  - the LRU is left where the slow path leaves it: the first hit of a GC tick still touches,
	//    which is all TouchBuffer does with "buflru" on and what keeps the collector from
	//    retiring a buffer that only memo hits use (it also clears prefetch_pending once a tick).
	// A GPU write needs no witness of its own: it lands in the owner buffer the answer names, and
	// the stream-ring shortcut below is only taken for a CPU-dirty range, which moves the epochs.
	// Written requests take ownership and texel requests ask the texture cache for an image
	// download on every call, so neither is ever answered or recorded here.
	BufFastSlot* fast_slot  = nullptr;
	uint64_t     fast_epoch = 0;
	if (memoizable && Common::Gates::Enabled(Common::Gates::Gate::BufFast)) {
		// The cache has no lock of its own and is written by the GuestGpu thread only, so only
		// that thread may read m_registration_epoch, the slot vector and the page table here.
		// The memo answers before the sanity check of the slow path below, so a request made
		// without a recording command buffer has to reach that check instead of being served here.
		if (is_written || is_texel_buffer || !GuestGpu::IsGpuThread() ||
		    !GuestRange {vaddr, size}.Valid() || m_scheduler.Current().IsInvalid()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BufFastSkip, 1);
		} else {
			thread_local std::vector<BufFastSlot> slots;
			if (slots.empty()) {
				slots.resize(BufFastSlots);
			}
			fast_slot = &slots[BufFastIndex(vaddr, size)];
			// Taken before every answer below, so that the recording at the end can prove that
			// no write was announced while the answer was being made.
			fast_epoch = m_memory_tracker.RangeWriteEpoch(vaddr, size);
			if (fast_slot->instance != m_instance || fast_slot->vaddr != vaddr ||
			    fast_slot->size != size) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BufFastNo, 1);
			} else {
				// Kept beside the pointer for the self-check below: FindBuffer may create a
				// buffer, and creating one joins and deletes the buffers it overlaps - the
				// remembered one among them, whose slot is then handed out again at the same
				// address. The identity of an answer is its id, not where the Buffer lives.
				const auto remembered_id = fast_slot->id;
				auto* remembered = fast_slot->registration == m_registration_epoch &&
				                           fast_epoch != 0 && fast_slot->region_epoch == fast_epoch
				                       ? m_slot_buffers.try_get(fast_slot->id)
				                       : nullptr;
				if (remembered == nullptr || remembered->is_deleted) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BufFastStale, 1);
				} else {
					if (fast_slot->touch_tick != m_gc_tick) {
						TouchBuffer(*remembered);
						fast_slot->touch_tick = m_gc_tick;
					}
					Common::FrameStats::Add(Common::FrameStats::Counter::BufFastOk, 1);
					if (!Common::Gates::Enabled(Common::Gates::Gate::BufFastCheck)) {
						return {remembered, remembered->Offset(vaddr)};
					}
					// Gate "buffastcheck": beside every hit, the work the gate replaced. A write
					// announced between the two epoch reads is a race, not a mismatch, so only an
					// unchanged witness may accuse the memo of having skipped an upload.
					const bool dirty = m_memory_tracker.IsRegionCpuModified(vaddr, size);
					const bool unchanged =
					    m_memory_tracker.RangeWriteEpoch(vaddr, size) == fast_epoch;
					auto full_id = id;
					if (IsBufferInvalid(full_id) ||
					    !m_slot_buffers[full_id].IsInBounds(vaddr, size)) {
						full_id = FindBuffer(vaddr, size);
					}
					auto& full = m_slot_buffers[full_id];
					TouchBuffer(full);
					(void)SynchronizeBuffer(full, vaddr, size, false, false);
					if (full_id != remembered_id || (dirty && unchanged)) {
						Common::FrameStats::Add(Common::FrameStats::Counter::BufFastBad, 1);
						static std::atomic<uint32_t> logged {0};
						if (logged.fetch_add(1, std::memory_order_relaxed) < 32) {
							LOGF("BufFastVerify: MISMATCH addr=0x%016" PRIx64 " size=0x%" PRIx64
							     " cpu_dirty=%d memo=%" PRIu32 " full=%" PRIu32 "\n",
							     vaddr, size, dirty && unchanged ? 1 : 0, remembered_id.index,
							     full_id.index);
						}
						*fast_slot = {};
					}
					return {&full, full.Offset(vaddr)};
				}
			}
		}
	}
	// Records what the paths below answered. The witness was taken before them and has to be
	// unchanged after: an announcement that crossed the upload leaves bytes the upload missed,
	// and its epoch move is the only thing that tells the next request about them.
	const auto remember = [&](BufferId resolved_id) {
		if (fast_slot == nullptr) {
			return;
		}
		if (fast_epoch != 0 && m_memory_tracker.RangeWriteEpoch(vaddr, size) == fast_epoch) {
			*fast_slot = {vaddr, size, fast_epoch, m_registration_epoch, m_gc_tick, m_instance,
			              resolved_id};
		} else {
			Common::FrameStats::Add(Common::FrameStats::Counter::BufFastSkip, 1);
			*fast_slot = {};
		}
	};
	if (!is_written && size <= CACHING_PAGESIZE &&
	    Common::Gates::Enabled(Common::Gates::Gate::StickyStat) && Common::FrameStats::Enabled() &&
	    GuestRange {vaddr, size}.Valid() &&
	    m_memory_tracker.StickyCandidatePages(vaddr, size, GpuTimeProfiler::Frame(), true) != 0) {
		// Gate "stkstat": a sticky page keeps this small read-only request CPU-dirty - a stream copy on
		// every call instead of the upload-epoch fast path.
		Common::FrameStats::Add(Common::FrameStats::Counter::StickyStreamHot, 1);
	}
	auto& command = m_scheduler.Current();
	if (command.IsInvalid() || !GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: buffer request requires a recording command buffer\n");
	}
	auto* buffer = m_slot_buffers.try_get(id);
	const auto [current_epoch, current_kind] = UploadEpoch(vaddr, size);
	if (BufferUploadEpochEnabled() && !is_written && buffer != nullptr && !buffer->is_deleted &&
	    buffer->IsInBounds(vaddr, size) &&
	    buffer->HasCurrentUpload(current_epoch, current_kind, vaddr, size)) {
		TouchBuffer(*buffer);
		(void)SynchronizeBuffer(*buffer, vaddr, size, false, is_texel_buffer);
		remember(id);
		return {buffer, buffer->Offset(vaddr)};
	}

	static const bool combined_query = [] {
		const auto* value = std::getenv("KYTY_BUFFER_COMBINED_QUERY");
		return value == nullptr || value[0] != '0';
	}();
	if (!is_written && size <= CACHING_PAGESIZE &&
	    (combined_query ? IsRegionCpuModifiedAndGpuCleanFromGpu(vaddr, size)
	                    : (!IsRegionGpuModifiedFromGpu(vaddr, size) &&
	                       m_memory_tracker.IsRegionCpuModified(vaddr, size)))) {
		const auto alignment = std::max<uint64_t>(
		    m_graphics.physical_device_properties.limits.minUniformBufferOffsetAlignment, 1);
		auto [mapped, offset] = m_stream_buffer.Map(size, alignment, false);
		if (mapped != nullptr && Libs::LibKernel::Memory::TryReadBacking(vaddr, mapped, size)) {
			m_stream_buffer.Commit();
			if (fast_slot != nullptr) {
				// A ring offset is fresh on every call: there is nothing to remember, and the
				// range is CPU-dirty anyway (that is why this path was taken).
				Common::FrameStats::Add(Common::FrameStats::Counter::BufFastSkip, 1);
				*fast_slot = {};
			}
			return {&m_stream_buffer, offset};
		}
	}

	Common::DrawStat::Mark(Common::DrawStat::BufSlow);
	if (IsBufferInvalid(id) || !m_slot_buffers[id].IsInBounds(vaddr, size)) {
		id = FindBuffer(vaddr, size);
	}
	auto& resolved = m_slot_buffers[id];
	TouchBuffer(resolved);
	(void)SynchronizeBuffer(resolved, vaddr, size, is_written, is_texel_buffer);
	if (is_written) {
		Common::DrawStat::Mark(Common::DrawStat::GpuWrite);
		m_gpu_modified_ranges.Add(vaddr, size);
		NoteGpuWrite(vaddr, size);
	}
	remember(id);
	return {&resolved, resolved.Offset(vaddr)};
}

namespace {
bool StreamPrefetchEnabled(); // defined with the stream prefetch below
} // namespace

// KYTY_STREAM_TRACE=1: where the bytes of each large image upload come from (a synchronized native
// buffer, or a fresh staging copy of guest memory) with the StreamRead clock, to correlate uploads
// at scene cuts with the file reads that produced the data.
void BufferCache::TraceImageUpload(uint64_t vaddr, uint64_t size, const char* path) {
	static const bool stream_trace = std::getenv("KYTY_STREAM_TRACE") != nullptr;
	if (!stream_trace || size < (256u << 10)) {
		return;
	}
	const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
	                    std::chrono::steady_clock::now().time_since_epoch())
	                    .count();
	LOGF("ImgUpload: addr=0x%016" PRIx64 " size=0x%" PRIx64 " %s t=%lld" "\n", vaddr, size, path,
	     static_cast<long long>(us));
}

BufferCache::ImageSource BufferCache::ObtainBufferForImage(uint64_t vaddr, uint64_t size,
                                                           bool pending_levels) {
	if (!GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: invalid image source\n");
	}
	const auto* owner = m_page_table.Find(vaddr >> PageTable::kPageBits);
	if (owner != nullptr && *owner) {
		auto& buffer = m_slot_buffers[*owner];
		if (buffer.IsInBounds(vaddr, size)) {
			TouchBuffer(buffer);
			(void)SynchronizeBuffer(buffer, vaddr, size, false, false);
			TraceImageUpload(vaddr, size, "owner");
			const auto offset = buffer.Offset(vaddr);
			return {buffer.Handle(), offset, buffer.Size() - offset};
		}
	}
	if (IsRegionGpuModifiedFromGpu(vaddr, size)) {
		TraceImageUpload(vaddr, size, "gpu-buffer");
		const auto [buffer, offset] = ObtainBuffer(vaddr, size, false, false);
		return {buffer->Handle(), offset, buffer->Size() - offset};
	}
	// Debug aid: KYTY_DUMP_TEX=<hex guest address> saves the staging copy of that image source to
	// _tex_<n>.bin (first three uploads).
	static const uint64_t dump_tex = [] {
		const char* value = std::getenv("KYTY_DUMP_TEX");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	if (vaddr != dump_tex) {
		ImageSource imported {};
		if (ObtainImportedImageSource(vaddr, size, &imported, !pending_levels)) {
			TraceImageUpload(vaddr, size, "import:no-owner");
			return imported;
		}
	}
	TraceImageUpload(vaddr, size, "staging:no-owner");

	auto [staging, stage_offset] = m_staging_buffer.Map(size, 16);
	if (staging == nullptr) {
		EXIT("BufferCache: failed to map staging for a guest image\n");
	}
	{
		Common::FrameStats::Scope copy_scope(Common::FrameStats::Counter::ImgCopyNs);
		CopyGuestToStaging(staging, vaddr, size);
		if (!m_staging_buffer.IsCoherent()) {
			Common::WaitAsyncCopies(); // Commit flushes the range
		}
	}
	m_staging_buffer.Commit();
	if (dump_tex != 0 && vaddr == dump_tex) {
		Common::WaitAsyncCopies();
		static std::atomic<uint32_t> dumped {0};
		const auto                   n = dumped.fetch_add(1);
		if (n < 3) {
			const auto name = "_tex_" + std::to_string(n) + ".bin";
			if (FILE* f = std::fopen(name.c_str(), "wb"); f != nullptr) {
				std::fwrite(staging, 1, static_cast<size_t>(size), f);
				std::fclose(f);
			}
		}
	}
	return {m_staging_buffer.Handle(), stage_offset, m_staging_buffer.Size() - stage_offset, true};
}

// KYTY_HOST_IMPORT_MIN_KB=<n> (default 64): smaller image sources keep the staging path (a
// scratch buffer and two barriers per source do not pay off for tiny images).
bool BufferCache::ObtainImportedImageSource(uint64_t vaddr, uint64_t size,
                                            ImageSource* result, bool reupload_check) {
	static const uint64_t min_bytes = [] {
		const char* value = std::getenv("KYTY_HOST_IMPORT_MIN_KB");
		return (value != nullptr ? std::strtoull(value, nullptr, 10) : uint64_t {64}) * 1024u;
	}();
	if (!m_host_import.Available() || size < min_bytes || result == nullptr) {
		return false;
	}
	// KYTY_HOST_IMPORT_REUPLOAD_TICKS=<n> (default 64): an image uploaded again within n ticks
	// of its previous upload is CPU-animated (video frames, UI); it takes the staging snapshot
	// so the next CPU write does not wait for the GPU read (HostReadWait).
	static const uint64_t reupload_ticks = [] {
		const char* value = std::getenv("KYTY_HOST_IMPORT_REUPLOAD_TICKS");
		return value != nullptr ? std::strtoull(value, nullptr, 10) : uint64_t {64};
	}();
	const auto tick = m_scheduler.CurrentTick();
	if (reupload_check) {
		if (m_import_last_tick.size() > 4096) {
			const auto stale = 4 * reupload_ticks;
			std::erase_if(m_import_last_tick, [tick, stale](const auto& entry) {
				return tick - entry.second > stale;
			});
		}
		auto [it, inserted] = m_import_last_tick.try_emplace(vaddr, tick);
		if (!inserted) {
			const auto since = tick - it->second;
			it->second       = tick;
			if (since < reupload_ticks) {
				return false;
			}
		}
	}
	auto& pieces = m_import_pieces;
	if (!Libs::LibKernel::Memory::TryGetBackingPieces(vaddr, size, &pieces)) {
		return false;
	}
	// One physical piece inside one chunk (nearly every image): the tiler reads the imported
	// buffer itself, no copy at all. Otherwise the pieces are gathered into a device-local
	// scratch buffer on the GPU.
	if (pieces.size() == 1) {
		HostImport::Region region {};
		if (!m_host_import.Resolve(pieces[0].backing_offset, size, &region)) {
			return false;
		}
		if (region.size == size) {
			NotePendingHostRead(vaddr, size, m_scheduler.CurrentTick());
			Common::FrameStats::Add(Common::FrameStats::Counter::ImgImports, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::ImgImportBytes, size);
			*result = {region.buffer, region.offset, size, true, true};
			return true;
		}
	}
	struct ImportCopy {
		vk::Buffer     source;
		vk::BufferCopy region;
	};
	static thread_local std::vector<ImportCopy> copies;
	copies.clear();
	uint64_t destination = 0;
	for (const auto& piece: pieces) {
		auto offset = piece.backing_offset;
		auto left   = piece.size;
		while (left != 0) {
			HostImport::Region region {};
			if (!m_host_import.Resolve(offset, left, &region)) {
				return false;
			}
			copies.push_back({region.buffer, {region.offset, destination, region.size}});
			offset += region.size;
			destination += region.size;
			left -= region.size;
		}
	}

	auto scratch = std::make_unique<Buffer>(m_graphics, m_scheduler, MemoryUsage::DeviceLocal, 0,
	                                        AllFlags, size);
	auto& command = m_scheduler.Current();
	command.EndRendering(RenderPassEnd::ImageUpload);
	const auto native = command.Handle();
	// No host barrier: the guest wrote the pages before this command buffer is submitted, and
	// vkQueueSubmit makes prior host writes visible to the device.
	static thread_local std::vector<vk::BufferCopy> regions;
	for (size_t i = 0; i < copies.size();) {
		regions.clear();
		size_t j = i;
		while (j < copies.size() && copies[j].source == copies[i].source) {
			regions.push_back(copies[j].region);
			j++;
		}
		native.copyBuffer(copies[i].source, scratch->Handle(), static_cast<uint32_t>(regions.size()),
		                  regions.data());
		i = j;
	}
	vk::BufferMemoryBarrier after {};
	after.srcAccessMask       = vk::AccessFlagBits::eTransferWrite;
	after.dstAccessMask       = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite;
	after.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	after.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	after.buffer              = scratch->Handle();
	after.offset              = 0;
	after.size                = size;
	native.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
	                       vk::PipelineStageFlagBits::eAllCommands, {}, 0, nullptr, 1, &after, 0,
	                       nullptr);
	NotePendingHostRead(vaddr, size, m_scheduler.CurrentTick());
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgImports, 1);
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgImportBytes, size);
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgImportPieces, copies.size());
	*result = {scratch->Handle(), 0, size};
	m_scheduler.DeferOperation([owner = std::move(scratch)]() mutable { owner.reset(); });
	return true;
}

void BufferCache::NotePendingHostRead(uint64_t vaddr, uint64_t size, uint64_t tick) {
	std::lock_guard lock(m_pending_host_reads_mutex);
	if (m_pending_host_reads.size() >= 512) {
		// Drop the entries whose copies the GPU has completed (one semaphore query).
		const auto known = m_scheduler.IsFree(tick - 1) ? tick - 1
		                                                 : m_scheduler.GetMasterSemaphore().KnownGpuTick();
		std::erase_if(m_pending_host_reads,
		              [known](const PendingHostRead& entry) { return entry.tick <= known; });
	}
	m_pending_host_reads.push_back({vaddr, size, tick});
}

bool BufferCache::HasPendingHostReads(uint64_t vaddr, uint64_t size) {
	if (!m_host_import.Available() || size == 0 || UINT64_MAX - vaddr < size) {
		return false;
	}
	std::lock_guard lock(m_pending_host_reads_mutex);
	if (m_pending_host_reads.empty()) {
		return false;
	}
	const auto known = m_scheduler.GetMasterSemaphore().KnownGpuTick();
	for (const auto& entry: m_pending_host_reads) {
		if (entry.tick > known && entry.vaddr < vaddr + size && vaddr < entry.vaddr + entry.size) {
			return true;
		}
	}
	return false;
}

bool BufferCache::WaitPendingHostReads(uint64_t vaddr, uint64_t size) {
	if (!m_host_import.Available() || size == 0 || UINT64_MAX - vaddr < size) {
		return false;
	}
	uint64_t tick = 0;
	{
		std::lock_guard lock(m_pending_host_reads_mutex);
		if (m_pending_host_reads.empty()) {
			return false;
		}
		const auto known = m_scheduler.GetMasterSemaphore().KnownGpuTick();
		for (const auto& entry: m_pending_host_reads) {
			if (entry.tick > known && entry.vaddr < vaddr + size && vaddr < entry.vaddr + entry.size) {
				tick = std::max(tick, entry.tick);
			}
		}
	}
	if (tick == 0) {
		return false;
	}
	if (CommandScheduler::InDeferredOperation()) {
		return false; // a completion callback cannot wait for the queue
	}
	Common::FrameStats::Scope wait_scope(Common::FrameStats::Counter::HostReadWaitNs,
	                                     Common::FrameStats::Counter::HostReadWaits);
	static const bool trace = std::getenv("KYTY_FAULT_TRACE") != nullptr;
	const auto        t0    = trace ? Common::FrameStats::NowNs() : 0;
	const auto        wait  = [this, tick] {
		if (!m_scheduler.IsFree(tick)) {
			Common::FrameStats::SiteScope site_scope("host-read");
			m_scheduler.Wait(tick); // submits the recording command buffer when tick is current
		}
	};
	if (GuestGpu::IsGpuThread()) {
		wait();
	} else {
		m_scheduler.Context().GetGpu().SendCommandSync(wait);
	}
	{
		std::lock_guard lock(m_pending_host_reads_mutex);
		std::erase_if(m_pending_host_reads,
		              [tick](const PendingHostRead& entry) { return entry.tick <= tick; });
	}
	if (trace) {
		LOGF("HostReadWait: addr=0x%016" PRIx64 " size=0x%" PRIx64 " tick=%llu current=%llu %s took %llu us" "\n",
		     vaddr, size, static_cast<unsigned long long>(tick),
		     static_cast<unsigned long long>(m_scheduler.CurrentTick()),
		     GuestGpu::IsGpuThread() ? "gpu-thread" : "guest-thread",
		     static_cast<unsigned long long>((Common::FrameStats::NowNs() - t0) / 1000u));
	}
	return true;
}

void BufferCache::FillBuffer(uint64_t vaddr, uint64_t size, uint32_t value, bool is_gds) {
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	static const uint64_t peek_addr_fill = [] {
		const char* value = std::getenv("KYTY_PEEK_ADDR");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	if (peek_addr_fill != 0 && !is_gds && vaddr <= peek_addr_fill && peek_addr_fill < vaddr + size) {
		LOGF("Peek: dma fill covers addr: dst=0x%016" PRIx64 " size=0x%" PRIx64 " value=0x%08x" "\n",
		     vaddr, size, value);
	}
	if ((vaddr & 3u) != 0 || size == 0 || (size & 3u) != 0 || size > UINT64_MAX - vaddr) {
		EXIT("BufferCache: fill range must be dword aligned\n");
	}
	if (is_gds) {
		if (vaddr > m_gds_buffer.Size() || size > m_gds_buffer.Size() - vaddr) {
			EXIT("BufferCache: GDS fill range is out of bounds\n");
		}
		m_gds_buffer.Fill(vaddr, size, value);
		// Buffer::Fill brackets the transfer itself; the epoch makes the next GDS consumer pay
		// its barrier even when the lazy gate is on.
		m_gds_host_epoch++;
		return;
	}
	if (vaddr == 0) {
		EXIT("BufferCache: invalid fill memory address\n");
	}
	(void)m_texture_cache.ClearMeta(vaddr);
	if (!IsRegionGpuModified(vaddr, size)) {
		// Access the guest mapping so write faults invalidate cached buffers and images.
		auto* destination = reinterpret_cast<uint32_t*>(vaddr);
		std::fill(destination, destination + size / sizeof(uint32_t), value);
		return;
	}

	m_texture_cache.InvalidateMemoryFromGPU(vaddr, size);
	auto [dst, dst_offset] = ObtainBuffer(vaddr, size, true, true);
	dst->Fill(dst_offset, size, value);
}

void BufferCache::CopyBuffer(uint64_t dst_vaddr, uint64_t src_vaddr, uint64_t size, bool dst_gds,
                             bool src_gds) {
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	// KYTY_PEEK_ADDR=<hex>: log DMA copies whose destination covers the address.
	static const uint64_t peek_addr = [] {
		const char* value = std::getenv("KYTY_PEEK_ADDR");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	if (peek_addr != 0 && !dst_gds && dst_vaddr <= peek_addr && peek_addr < dst_vaddr + size) {
		LOGF("Peek: dma copy covers addr: src=0x%016" PRIx64 " dst=0x%016" PRIx64 " size=0x%" PRIx64
		     " src_gds=%d" "\n", src_vaddr, dst_vaddr, size, static_cast<int>(src_gds));
	}
	// KYTY_STREAM_TRACE=1: log large DMA copies (texture streaming) with a timestamp.
	static const bool stream_trace = std::getenv("KYTY_STREAM_TRACE") != nullptr;
	if (stream_trace && size >= (1u << 20)) {
		const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
		                    std::chrono::steady_clock::now().time_since_epoch())
		                    .count();
		LOGF("StreamTrace: dma src=0x%016" PRIx64 " dst=0x%016" PRIx64 " size=0x%" PRIx64 " t=%lld" "\n",
		     src_vaddr, dst_vaddr, size, static_cast<long long>(us));
	}
	const bool dst_memory = !dst_gds;
	const bool src_memory = !src_gds;
	if ((dst_memory && dst_vaddr == 0) || (src_memory && src_vaddr == 0) || size == 0 ||
	    ((dst_gds || src_gds) && ((dst_vaddr | src_vaddr | size) & 3u) != 0) ||
	    size > UINT64_MAX - dst_vaddr || size > UINT64_MAX - src_vaddr || (dst_gds && src_gds) ||
	    (dst_gds && (dst_vaddr > m_gds_buffer.Size() || size > m_gds_buffer.Size() - dst_vaddr)) ||
	    (src_gds && (src_vaddr > m_gds_buffer.Size() || size > m_gds_buffer.Size() - src_vaddr))) {
		EXIT("BufferCache: invalid copy range, src=0x%016" PRIx64 " dst=0x%016" PRIx64
		     " size=0x%016" PRIx64 " src_gds=%d dst_gds=%d\n",
		     src_vaddr, dst_vaddr, size, static_cast<int>(src_gds), static_cast<int>(dst_gds));
	}
	if (src_memory && dst_memory && !IsRegionGpuModified(dst_vaddr, size) &&
	    !IsRegionGpuModified(src_vaddr, size) && !m_texture_cache.FindImageFromRange(src_vaddr, size)) {
		std::memcpy(reinterpret_cast<void*>(dst_vaddr), reinterpret_cast<const void*>(src_vaddr),
		            size);
		return;
	}

	auto& command = m_scheduler.Current();
	if (dst_memory) {
		m_texture_cache.InvalidateMemoryFromGPU(dst_vaddr, size);
	}
	const auto src_id      = src_memory ? FindBuffer(src_vaddr, size) : BufferId {};
	const auto dst_id      = dst_memory ? FindBuffer(dst_vaddr, size) : BufferId {};
	auto [src, src_offset] = src_memory ? ObtainBuffer(src_vaddr, size, false, true, src_id)
	                                    : std::pair {&m_gds_buffer, src_vaddr};
	auto [dst, dst_offset] = dst_memory ? ObtainBuffer(dst_vaddr, size, true, true, dst_id)
	                                    : std::pair {&m_gds_buffer, dst_vaddr};
	dst->CopyFrom(command, *src, src_offset, dst_offset, size);
	if (dst_gds) {
		m_gds_host_epoch++;
	}
}

bool BufferCache::IsRegionRegistered(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: invalid registered-region query\n");
	}
	// Cached buffers are ordered and non-overlapping. The last buffer beginning before the query
	// end is therefore the only possible intersection.
	const auto candidate = m_buffers.lower_bound(vaddr + size);
	if (candidate == m_buffers.begin()) {
		return false;
	}
	const auto& [address, id] = *std::prev(candidate);
	return address + m_slot_buffers[id].Size() > vaddr;
}

bool BufferCache::IsRegionGpuModified(uint64_t vaddr, uint64_t size) {
	return m_memory_tracker.IsRegionGpuModified(vaddr, size);
}

// Gate "tfcheck": a lock-free answer disagreed with the locked one. For the GPU query any
// mismatch is a real defect (this thread is the only writer of GPU-dirty state). For the
// combined query a guest thread may have announced a CPU write between the two calls, so
// the caller re-reads the lock-free answer once and only reports what still disagrees.
static void ReportTrackFreeMismatch(const char* query, uint64_t vaddr, uint64_t size,
                                    bool fast, bool locked) {
	Common::FrameStats::Add(Common::FrameStats::Counter::TrackFreeMismatch, 1);
	static std::atomic<uint32_t> logged {0};
	if (logged.fetch_add(1, std::memory_order_relaxed) < 64) {
		LOGF("TrackFreeVerify: MISMATCH %s addr=0x%016" PRIx64 " size=0x%" PRIx64
		     " fast=%d locked=%d" "\n",
		     query, vaddr, size, fast ? 1 : 0, locked ? 1 : 0);
	}
}

bool BufferCache::IsRegionGpuModifiedFromGpu(uint64_t vaddr, uint64_t size) {
	// The lock-free answer is only exact on the thread that owns every change of the GPU-dirty
	// bits. Any other caller takes the locked query, in release builds too.
	if (!GuestGpu::IsGpuThread() ||
	    !Common::Gates::Enabled(Common::Gates::Gate::TrackLockFree)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::TrackFreeLocked, 1);
		return m_memory_tracker.IsRegionGpuModified(vaddr, size);
	}
	const bool fast = m_memory_tracker.IsRegionGpuModifiedFast(vaddr, size);
	Common::FrameStats::Add(Common::FrameStats::Counter::TrackFreeHits, 1);
	if (Common::Gates::Enabled(Common::Gates::Gate::TrackLockFreeVerify)) {
		const bool locked = m_memory_tracker.IsRegionGpuModified(vaddr, size);
		if (locked != fast && m_memory_tracker.IsRegionGpuModifiedFast(vaddr, size) != locked) {
			ReportTrackFreeMismatch("gpu", vaddr, size, fast, locked);
		}
	}
	return fast;
}

bool BufferCache::IsRegionCpuModifiedAndGpuCleanFromGpu(uint64_t vaddr, uint64_t size) {
	if (!GuestGpu::IsGpuThread() ||
	    !Common::Gates::Enabled(Common::Gates::Gate::TrackLockFree)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::TrackFreeLocked, 1);
		return m_memory_tracker.IsRegionCpuModifiedAndGpuClean(vaddr, size);
	}
	const bool fast = m_memory_tracker.IsRegionCpuModifiedAndGpuCleanFast(vaddr, size);
	Common::FrameStats::Add(Common::FrameStats::Counter::TrackFreeHits, 1);
	if (Common::Gates::Enabled(Common::Gates::Gate::TrackLockFreeVerify)) {
		const bool locked = m_memory_tracker.IsRegionCpuModifiedAndGpuClean(vaddr, size);
		if (locked != fast &&
		    m_memory_tracker.IsRegionCpuModifiedAndGpuCleanFast(vaddr, size) != locked) {
			ReportTrackFreeMismatch("combined", vaddr, size, fast, locked);
		}
	}
	return fast;
}

bool BufferCache::HasGpuDirtyBytes(uint64_t vaddr, uint64_t size) {
	return m_gpu_modified_ranges.Intersects(vaddr, size);
}

bool BufferCache::IsRegionCpuModified(uint64_t vaddr, uint64_t size) {
	return m_memory_tracker.IsRegionCpuModified(vaddr, size);
}

void BufferCache::RunGarbageCollector() {
	const auto tick = m_gc_tick++;
	if (m_graphics.CanReportMemoryUsage()) {
		m_total_used_memory = m_graphics.GetDeviceMemoryUsage();
	}
	if (m_total_used_memory < m_trigger_gc_memory) {
		return;
	}

	const bool     aggressive = m_total_used_memory >= m_critical_gc_memory;
	const uint64_t age        = std::min<uint64_t>(aggressive ? 80 : 160, tick);
	const size_t   limit      = aggressive ? 64 : 32;

	std::vector<BufferId>     dirty_buffers;
	std::vector<DownloadCopy> copies;
	size_t                    retire_count = 0;
	m_lru_cache.ForEachItemBelow(tick - age, [&](BufferId id) {
		auto& buffer = m_slot_buffers[id];
		EXIT_IF(buffer.is_deleted);
		m_memory_tracker.ValidateGpuDirtyOwnership(m_gpu_modified_ranges, buffer.CpuAddress(),
		                                           buffer.Size(), "garbage collection");
		const bool dirty = m_memory_tracker.IsRegionGpuModified(buffer.CpuAddress(), buffer.Size());
		if (dirty && !aggressive) {
			return false;
		}
		if (buffer.prefetch_pending && !aggressive) {
			return false; // streamed data waiting for its first bind
		}
		if (dirty) {
			// Every range the set holds inside the buffer (the tracker pages may disagree after
			// a stale-readable window; the set is what the download subtracts).
			m_gpu_modified_ranges.ForEachInRange(
			    buffer.CpuAddress(), buffer.Size(), [&](uint64_t start, uint64_t end) {
				    copies.push_back({&buffer, start - buffer.CpuAddress(), start, end - start});
			    });
			dirty_buffers.push_back(id);
		} else {
			m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
			DeleteBuffer(id);
		}
		return ++retire_count == limit;
	});
	if (dirty_buffers.empty()) {
		return;
	}

	LOGF("BufferCache: gc drains %zu gpu-dirty buffers (usage %" PRIu64 " MB, trigger %" PRIu64
	     " MB, critical %" PRIu64 " MB, aggressive=%d)" "\n",
	     dirty_buffers.size(), m_total_used_memory >> 20u, m_trigger_gc_memory >> 20u,
	     m_critical_gc_memory >> 20u, aggressive ? 1 : 0);
	if (!copies.empty()) {
		DownloadBufferMemory(copies, "gc");
	}
	for (const auto id: dirty_buffers) {
		auto& buffer = m_slot_buffers[id];
		m_memory_tracker.UnmarkRegionAsGpuModified(buffer.CpuAddress(), buffer.Size());
		if (m_memory_tracker.IsRegionGpuModified(buffer.CpuAddress(), buffer.Size()) ||
		    m_gpu_modified_ranges.Intersects(buffer.CpuAddress(), buffer.Size())) {
			// Tracker and range set disagreed (seen once the usage crossed the critical
			// threshold): the buffer goes away, so its GPU ownership goes with it.
			static std::atomic<uint32_t> log_count {0};
			if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
				LOGF("BufferCache: gc cleared inconsistent GPU ownership of 0x%016" PRIx64
				     " size=0x%" PRIx64 "\n",
				     buffer.CpuAddress(), buffer.Size());
			}
			m_gpu_modified_ranges.Subtract(buffer.CpuAddress(), buffer.Size());
			m_memory_tracker.UnmarkRegionAsGpuModified(buffer.CpuAddress(), buffer.Size());
		}
		m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
		Unregister(id);
		m_slot_buffers.erase(id);
	}
}

void BufferCache::ProcessFaultBuffer() {
	m_fault_manager.ProcessFaultBuffer();
}

// ---- Asynchronous readback (guest thread waits, GPU thread keeps going) --------------------------
//
// A CPU read of GPU-written memory needs the GPU to reach the copy that brings the data back. The
// old path executed the whole readback on the GPU thread (record, submit, wait, write back), so
// every such read stopped PM4 processing for the full GPU queue depth (1.5-4 ms) while the guest
// thread waited too. Now the GPU thread only records the copies and submits (BeginAsyncReadback);
// the guest thread waits for that tick itself and then asks the GPU thread to apply the bytes
// (FinishAsyncReadback), which it does at the next packet boundary unless a newer GPU write to the
// region was recorded meanwhile - then the read is retried.

BufferCache::AsyncReadback BufferCache::BeginAsyncReadback(uint64_t vaddr, uint64_t size) {
	AsyncReadback job;
	if (!IsRegionRegistered(vaddr, size)) {
		return job;
	}
	auto& buffer = m_slot_buffers[FindBuffer(vaddr, size)];

	constexpr uint64_t WindowSize   = 512 * 1024;
	const auto         buffer_begin = buffer.CpuAddress();
	const auto         buffer_end   = buffer_begin + buffer.Size();
	const auto         window_begin = std::max(vaddr & ~(WindowSize - 1), buffer_begin);
	const auto window_end = std::min(std::max(window_begin + WindowSize, vaddr + size), buffer_end);

	uint64_t packed = 0;
	m_memory_tracker.ForEachDownloadRange<false>(
	    window_begin, window_end - window_begin, [&](uint64_t address, uint64_t bytes) noexcept {
		    m_memory_tracker.ValidateGpuDirtyPages(m_gpu_modified_ranges, address, bytes,
		                                           "memory invalidation");
		    m_gpu_modified_ranges.ForEachInRange(address, bytes, [&](uint64_t start, uint64_t end) {
			    job.pieces.push_back({start, end - start, packed});
			    packed += AlignDownload((end - start) + (start & 3u));
		    });
	    });
	if (job.pieces.empty()) {
		return job;
	}
	if (packed > m_download_buffer.Size() / 2) {
		// Very large readback: use the synchronous path (rare).
		job.pieces.clear();
		ReadMemoryOnGpu(vaddr, size, false);
		return job;
	}
	{
		auto& hot = m_hot_regions[vaddr >> HotBucketBits];
		hot.begin = hot.hits == 0 ? window_begin : std::min(hot.begin, window_begin);
		hot.end   = hot.hits == 0 ? window_end : std::max(hot.end, window_end);
		hot.hits++;
		hot.last_hit_frame = m_scheduler.Context().GetGpu().GetFrameNum();
	}
	Common::FrameStats::Scope download_scope(Common::FrameStats::Counter::DownloadNs,
	                                         Common::FrameStats::Counter::Downloads);
	const auto [mapped, base_offset] = m_download_buffer.Map(packed, DOWNLOAD_ALIGNMENT);
	EXIT_IF(mapped == nullptr);
	for (const auto& piece: job.pieces) {
		const auto source_begin = piece.address & ~uint64_t {3};
		const auto envelope     = piece.size + (piece.address - source_begin);
		m_download_buffer.CopyFrom(m_scheduler.Current(), buffer, buffer.Offset(source_begin),
		                           base_offset + piece.offset, envelope,
		                           vk::AccessFlagBits::eMemoryWrite, vk::AccessFlags {},
		                           vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
		                           vk::AccessFlagBits::eHostRead, RenderPassEnd::Download);
	}
	m_download_buffer.Commit();
	job.mapped      = mapped;
	job.base_offset = base_offset;
	job.seq         = m_gpu_write_seq;
	job.tick        = m_scheduler.CurrentTick();
	{
		Common::FrameStats::SiteScope site_scope("download-async");
		m_scheduler.Flush();
	}
	return job;
}

void BufferCache::ApplyReadbackPieces(const std::vector<ReadbackPiece>& pieces, const uint8_t* data,
                                      uint64_t seq) {
	uint64_t cursor = 0;
	for (const auto& piece: pieces) {
		// Skip pieces that went clean meanwhile (a synchronous drain, or a CPU write after it):
		// guest memory already holds newer data there.
		if (m_memory_tracker.IsRegionGpuModified(piece.address, piece.size)) {
			Libs::LibKernel::Memory::WriteBacking(piece.address, data + cursor, piece.size);
			if (LastGpuWriteSeq(piece.address, piece.size) <= seq) {
				m_memory_tracker.UnmarkRegionAsGpuModified(piece.address, piece.size);
				m_gpu_modified_ranges.Subtract(piece.address, piece.size);
			}
		}
		cursor += piece.size;
	}
}

void BufferCache::ServeStaleRead(uint64_t vaddr, uint64_t size) {
	static std::atomic<uint32_t> log_count {0};
	if (!m_memory_tracker.IsRegionGpuModified(vaddr, size)) {
		return;
	}
	if (!IsRegionRegistered(vaddr, size)) {
		// Dirty tracker state without a buffer: nothing to download. Make the page readable so
		// the faulting instruction can proceed.
		m_memory_tracker.MarkRegionAsStaleReadable(vaddr, size);
		return;
	}
	auto& buffer = m_slot_buffers[FindBuffer(vaddr, size)];

	constexpr uint64_t WindowSize   = 512 * 1024;
	const auto         buffer_begin = buffer.CpuAddress();
	const auto         buffer_end   = buffer_begin + buffer.Size();
	const auto         window_begin = std::max(vaddr & ~(WindowSize - 1), buffer_begin);
	const auto window_end = std::min(std::max(window_begin + WindowSize, vaddr + size), buffer_end);

	std::vector<ReadbackPiece> pieces;
	uint64_t                   packed = 0;
	m_memory_tracker.ForEachDownloadRange<false>(
	    window_begin, window_end - window_begin, [&](uint64_t address, uint64_t bytes) noexcept {
		    m_gpu_modified_ranges.ForEachInRange(address, bytes, [&](uint64_t start, uint64_t end) {
			    pieces.push_back({start, end - start, packed});
			    packed += AlignDownload((end - start) + (start & 3u));
		    });
	    });
	auto& hot = m_hot_regions[vaddr >> HotBucketBits];
	hot.begin = hot.hits == 0 ? window_begin : std::min(hot.begin, window_begin);
	hot.end   = hot.hits == 0 ? window_end : std::max(hot.end, window_end);
	hot.hits++;
	hot.last_hit_frame = m_scheduler.Context().GetGpu().GetFrameNum();

	// The read proceeds on whatever guest memory holds now (the last completed data).
	for (const auto& piece: pieces) {
		m_memory_tracker.MarkRegionAsStaleReadable(piece.address, piece.size);
	}
	m_memory_tracker.MarkRegionAsStaleReadable(vaddr, size);

	if (pieces.empty() || packed > m_download_buffer.Size() / 2 || hot.in_flight) {
		// Nothing to fetch, too large for the ring, or a download of this region is already on
		// its way (it applies the data when the GPU completes; PrefetchHotReadbacks keeps the
		// region fresh every slice).
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("StaleRead: addr=0x%016" PRIx64 " pieces=%zu bytes=0x%" PRIx64 " in_flight=%d (no download)" "\n",
			     vaddr, pieces.size(), packed, hot.in_flight ? 1 : 0);
		}
		return;
	}
	const auto [mapped, base_offset] = m_download_buffer.Map(packed, DOWNLOAD_ALIGNMENT);
	if (mapped == nullptr) {
		return;
	}
	for (const auto& piece: pieces) {
		const auto source_begin = piece.address & ~uint64_t {3};
		const auto envelope     = piece.size + (piece.address - source_begin);
		m_download_buffer.CopyFrom(m_scheduler.Current(), buffer, buffer.Offset(source_begin),
		                           base_offset + piece.offset, envelope,
		                           vk::AccessFlagBits::eMemoryWrite, vk::AccessFlags {},
		                           vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
		                           vk::AccessFlagBits::eHostRead, RenderPassEnd::Download);
	}
	m_download_buffer.Commit();
	hot.in_flight     = true;
	const auto seq    = m_gpu_write_seq;
	const auto bucket = vaddr >> HotBucketBits;
	if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
		LOGF("StaleRead: addr=0x%016" PRIx64 " window=0x%016" PRIx64 "-0x%016" PRIx64
		     " pieces=%zu bytes=0x%" PRIx64 " hits=%u tick=%" PRIu64 "\n",
		     vaddr, window_begin, window_end, pieces.size(), packed, hot.hits,
		     m_scheduler.CurrentTick());
	}
	auto& gpu = m_scheduler.Context().GetGpu();
	m_scheduler.DeferPriorityOperation([this, &gpu, bucket, pieces = std::move(pieces), mapped,
	                                    base_offset, seq]() mutable {
		std::vector<uint8_t> data;
		uint64_t             total = 0;
		for (const auto& piece: pieces) {
			total += piece.size;
		}
		data.reserve(total);
		for (const auto& piece: pieces) {
			const auto skew = piece.address & 3u;
			m_download_buffer.Invalidate(base_offset + piece.offset, piece.size + skew);
			const auto* source = mapped + piece.offset + skew;
			data.insert(data.end(), source, source + piece.size);
		}
		if (gpu.IsStopping()) {
			return;
		}
		gpu.SendCommand([this, bucket, pieces = std::move(pieces), data = std::move(data), seq] {
			if (auto it = m_hot_regions.find(bucket); it != m_hot_regions.end()) {
				it->second.in_flight = false;
			}
			ApplyReadbackPieces(pieces, data.data(), seq);
		});
	});
	{
		Common::FrameStats::SiteScope site_scope("download-stale");
		m_scheduler.Flush();
	}
}

bool BufferCache::FinishAsyncReadback(const AsyncReadback& job) {
	bool complete = true;
	for (const auto& piece: job.pieces) {
		if (LastGpuWriteSeq(piece.address, piece.size) > job.seq) {
			complete = false;
			continue;
		}
		const auto skew = piece.address & 3u;
		m_download_buffer.Invalidate(job.base_offset + piece.offset, piece.size + skew);
		Libs::LibKernel::Memory::WriteBacking(piece.address, job.mapped + piece.offset + skew,
		                                      piece.size);
		m_memory_tracker.UnmarkRegionAsGpuModified(piece.address, piece.size);
		m_gpu_modified_ranges.Subtract(piece.address, piece.size);
	}
	return complete;
}

// ---- Readback prefetch -------------------------------------------------------------------------
//
// ASTRO BOT reads a few GPU-written buffers from the CPU every frame (feedback counters and
// indirect arguments). Each read page-faults on a GPU-dirty page and ReadMemoryOnGpu drains the
// whole GPU queue on the GPU thread - 1.5-4 ms per read during which no PM4 is processed and the
// GPU starves afterwards. The regions are the same every frame, so at the end of every submission
// slice the dirty parts of the hot regions are copied into the download ring behind the work just
// recorded; when the copy completes (priority thread) the bytes are handed to the GPU thread, which
// writes them into the guest backing and clears the dirty state - unless a newer GPU write to the
// same bucket was recorded meanwhile, in which case the data is dropped and the next slice tries
// again. A CPU read that arrives before the prefetch completes still takes the drain path.
// KYTY_READBACK_PREFETCH=0 disables the prefetch.

void BufferCache::NoteGpuWrite(uint64_t vaddr, uint64_t size) {
	const auto seq = ++m_gpu_write_seq;
	if (size > (16u << 20)) {
		m_large_write_seq = seq;
		return;
	}
	const auto first = vaddr >> HotBucketBits;
	const auto last  = (vaddr + size - 1) >> HotBucketBits;
	for (auto bucket = first; bucket <= last; bucket++) {
		m_bucket_write_seq[bucket] = seq;
	}
}

uint64_t BufferCache::LastGpuWriteSeq(uint64_t vaddr, uint64_t size, bool include_large) const {
	auto       result = include_large ? m_large_write_seq : uint64_t {0};
	const auto first  = vaddr >> HotBucketBits;
	const auto last   = (vaddr + size - 1) >> HotBucketBits;
	for (auto bucket = first; bucket <= last; bucket++) {
		if (const auto it = m_bucket_write_seq.find(bucket); it != m_bucket_write_seq.end()) {
			result = std::max(result, it->second);
		}
	}
	return result;
}

// --- Texture streaming prefetch -------------------------------------------------------------
// ASTRO BOT streams textures with file reads into fixed slots of its GPU heaps and binds them
// hundreds of milliseconds (or tens of seconds) later, up to 1 GB at a scene cut. Without
// prefetch every one of those images is copied guest -> staging in the cut frame (60-100 ms of
// memcpy). Reads are queued here and synchronized into native buffers ahead of time; the image
// upload then takes the "owner" path of ObtainBufferForImage.

namespace {

bool StreamPrefetchEnabled() {
	static const bool enabled = [] {
		// Experimental (session 21): ahead-of-time synchronization of streamed file data into
		// native buffers. Halves the staging copies at scene cuts but doubles VRAM use and adds
		// GC churn (worse p99); off until the mirror has its own budget and eviction policy.
		const char* value = std::getenv("KYTY_STREAM_PREFETCH");
		return value != nullptr && value[0] == '1';
	}();
	return enabled;
}

uint64_t StreamPrefetchBudgetNs() {
	static const uint64_t budget = [] {
		const char* value = std::getenv("KYTY_STREAM_PREFETCH_US");
		return (value != nullptr ? std::strtoull(value, nullptr, 10) : 3000ull) * 1000ull;
	}();
	return budget;
}

uint64_t StreamNowNs() {
	return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
	                                 std::chrono::steady_clock::now().time_since_epoch())
	                                 .count());
}

} // namespace

void BufferCache::NoteStreamedRead(uint64_t vaddr, uint64_t size) {
	if (!StreamPrefetchEnabled() || !GuestRange {vaddr, size}.Valid()) {
		return;
	}
	std::lock_guard lock(m_streamed_mutex);
	if (m_streamed_ranges.size() >= 16384) {
		m_streamed_ranges.erase(m_streamed_ranges.begin(),
		                        m_streamed_ranges.begin() + m_streamed_ranges.size() / 2);
	}
	m_streamed_ranges.emplace_back(vaddr, size);
}

bool BufferCache::IsRegionFullyRegistered(uint64_t vaddr, uint64_t size) {
	// Every byte of [vaddr, vaddr + size) belongs to a live cached buffer.
	auto cursor = vaddr;
	const auto end = vaddr + size;
	while (cursor < end) {
		auto it = m_buffers.upper_bound(cursor);
		if (it == m_buffers.begin()) {
			return false;
		}
		--it;
		const auto& buffer = m_slot_buffers[it->second];
		const auto  begin  = buffer.CpuAddress();
		const auto  stop   = begin + buffer.Size();
		if (begin > cursor || stop <= cursor) {
			return false;
		}
		cursor = stop;
	}
	return true;
}

void BufferCache::PrefetchStreamedRanges() {
	if (!StreamPrefetchEnabled() || m_scheduler.Current().IsInvalid()) {
		return;
	}
	{
		std::lock_guard lock(m_streamed_mutex);
		if (!m_streamed_ranges.empty()) {
			m_streamed_pending.insert(m_streamed_pending.end(), m_streamed_ranges.begin(),
			                          m_streamed_ranges.end());
			m_streamed_ranges.clear();
		}
	}
	if (m_streamed_pending.empty()) {
		return;
	}
	const auto frame = m_scheduler.Context().GetGpu().GetFrameNum();
	if (frame != m_streamed_frame) {
		m_streamed_frame    = frame;
		m_streamed_spent_ns = 0;
	}
	const auto budget = StreamPrefetchBudgetNs();
	if (m_streamed_spent_ns >= budget) {
		return;
	}
	static const uint64_t pending_cap = [] {
		const char* value = std::getenv("KYTY_STREAM_PREFETCH_MB");
		return (value != nullptr ? std::strtoull(value, nullptr, 10) : 2048ull) << 20u;
	}();
	if (m_prefetch_pending_bytes >= pending_cap) {
		m_streamed_pending.clear(); // over budget: these will take the staging path when bound
		return;
	}
	// Coalesce: consecutive chunks of one file arrive as separate reads.
	auto& pending = m_streamed_pending;
	std::sort(pending.begin(), pending.end());
	std::vector<std::pair<uint64_t, uint64_t>> merged;
	merged.reserve(pending.size());
	for (const auto& [addr, size]: pending) {
		if (!merged.empty() && addr <= merged.back().first + merged.back().second) {
			merged.back().second =
			    std::max(merged.back().first + merged.back().second, addr + size) - merged.back().first;
		} else {
			merged.emplace_back(addr, size);
		}
	}
	pending.clear();

	static const bool trace = std::getenv("KYTY_STREAM_TRACE") != nullptr;
	const auto        t0    = StreamNowNs();
	uint64_t          bytes = 0;
	uint32_t          done  = 0;
	size_t            index = 0;
	for (; index < merged.size(); index++) {
		if (m_streamed_spent_ns + (StreamNowNs() - t0) >= budget) {
			break;
		}
		const auto [addr, size] = merged[index];
		if (!m_memory_tracker.IsRegionCpuModified(addr, size) ||
		    m_memory_tracker.IsRegionGpuModified(addr, size)) {
			continue; // already synchronized, or GPU data that must not be overwritten
		}
		// Memory reused for a thread stack must never be write-protected by us: hold the gate so
		// that a stack registered during the synchronization waits and then unprotects itself.
		// The buffer is page-rounded (CreateBuffer) and later synchronizations cover the whole
		// buffer: test the rounded range.
		const auto rounded_begin = addr & ~(CACHING_PAGESIZE - 1);
		const auto rounded_end   = (addr + size + CACHING_PAGESIZE - 1) & ~(CACHING_PAGESIZE - 1);
		Libs::LibKernel::Memory::LockGuestStackGate();
		if (Libs::LibKernel::Memory::OverlapsGuestStack(rounded_begin, rounded_end - rounded_begin)) {
			Libs::LibKernel::Memory::UnlockGuestStackGate();
			continue;
		}
		if (trace) {
			LOGF("StreamPrefetch: obtain addr=0x%016" PRIx64 " size=0x%" PRIx64 "\n", addr, size);
		}
		// Edge pages owned by a neighbouring buffer (consecutive reads share a cache page) are
		// synchronized in place and left out, so the new buffer never overlaps and never joins.
		auto begin = addr;
		auto end   = addr + size;
		const auto owned_by_other = [&](uint64_t page_addr) {
			const auto* owner = m_page_table.Find(page_addr >> PageTable::kPageBits);
			return owner != nullptr && *owner;
		};
		if (owned_by_other(rounded_begin)) {
			const auto page_end = std::min(rounded_begin + CACHING_PAGESIZE, end);
			(void)ObtainBuffer(begin, page_end - begin, false, false);
			begin = page_end;
		}
		if (begin < end && owned_by_other(rounded_end - CACHING_PAGESIZE) &&
		    rounded_end - CACHING_PAGESIZE >= begin) {
			const auto page_begin = std::max(rounded_end - CACHING_PAGESIZE, begin);
			(void)ObtainBuffer(page_begin, end - page_begin, false, false);
			end = page_begin;
		}
		if (begin >= end) {
			Libs::LibKernel::Memory::UnlockGuestStackGate();
			bytes += size;
			done++;
			continue;
		}
		auto [prefetched, prefetched_offset] = ObtainBuffer(begin, end - begin, false, false);
		(void)prefetched_offset;
		if (prefetched != nullptr && !prefetched->prefetch_pending && prefetched != &m_stream_buffer) {
			prefetched->prefetch_pending = true;
			m_prefetch_pending_bytes += prefetched->Size();
		}
		Libs::LibKernel::Memory::UnlockGuestStackGate();
		bytes += size;
		done++;
	}
	// Leftover goes back to the queue for the next slice.
	pending.insert(pending.end(), merged.begin() + index, merged.end());
	const auto spent = StreamNowNs() - t0;
	m_streamed_spent_ns += spent;
	if (Common::FrameStats::Enabled()) {
		Common::FrameStats::AddSite(Common::FrameStats::Table::Pm4Sites, "stream-prefetch", spent);
	}
	if (trace && (done != 0 || !pending.empty())) {
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1) < 4096) {
			LOGF("StreamPrefetch: frame=%d ranges=%u bytes=%" PRIu64 " us=%" PRIu64 " left=%zu\n", frame,
			     done, bytes, spent / 1000u, pending.size());
		}
	}
}

void BufferCache::DeleteBuffersOverlapping(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		return;
	}
	std::vector<BufferId> ids;
	{
		auto it = m_buffers.lower_bound(vaddr + size);
		while (it != m_buffers.begin()) {
			--it;
			const auto& buffer = m_slot_buffers[it->second];
			if (buffer.CpuAddress() + buffer.Size() <= vaddr) {
				break;
			}
			ids.push_back(it->second);
		}
	}
	if (ids.empty()) {
		static const bool trace0 = std::getenv("KYTY_STREAM_TRACE") != nullptr;
		if (trace0) {
			std::fprintf(stderr, "GuestStack: no buffers for stack 0x%016llx size=0x%llx" "\n",
			             static_cast<unsigned long long>(vaddr), static_cast<unsigned long long>(size));
			std::fflush(stderr);
		}
		return;
	}
	std::vector<DownloadCopy> copies;
	std::vector<BufferId>     dirty_buffers;
	for (const auto id: ids) {
		auto& buffer = m_slot_buffers[id];
		if (m_memory_tracker.IsRegionGpuModified(buffer.CpuAddress(), buffer.Size())) {
			m_memory_tracker.ForEachDownloadRange<false>(
			    buffer.CpuAddress(), buffer.Size(),
			    [&](uint64_t dirty_address, uint64_t dirty_size) noexcept {
				    m_gpu_modified_ranges.ForEachInRange(
				        dirty_address, dirty_size, [&](uint64_t start, uint64_t end) {
					        copies.push_back({&buffer, start - buffer.CpuAddress(), start,
					                          end - start});
				        });
			    });
			dirty_buffers.push_back(id);
		} else {
			m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
			DeleteBuffer(id);
		}
	}
	if (!copies.empty()) {
		DownloadBufferMemory(copies, "stack");
	}
	for (const auto id: dirty_buffers) {
		auto& buffer = m_slot_buffers[id];
		m_memory_tracker.UnmarkRegionAsGpuModified(buffer.CpuAddress(), buffer.Size());
		m_memory_tracker.UntrackMemory(buffer.CpuAddress(), buffer.Size());
		DeleteBuffer(id);
	}
	static const bool trace = std::getenv("KYTY_STREAM_TRACE") != nullptr;
	if (trace) {
		std::fprintf(stderr, "GuestStack: released %zu buffers for stack 0x%016llx size=0x%llx" "\n", ids.size(),
		             static_cast<unsigned long long>(vaddr), static_cast<unsigned long long>(size));
		std::fflush(stderr);
		LOGF("GuestStack: released %zu buffers (%zu gpu-dirty) for stack 0x%016" PRIx64 " size=0x%" PRIx64 "\n",
		     ids.size(), dirty_buffers.size(), vaddr, size);
	}
}

void BufferCache::PrefetchHotReadbacks() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_READBACK_PREFETCH");
		return value == nullptr || value[0] != '0';
	}();
	if (!enabled || m_hot_regions.empty() || m_scheduler.Current().IsInvalid()) {
		return;
	}
	static std::atomic<uint32_t> log_count {0};
	const auto frame = m_scheduler.Context().GetGpu().GetFrameNum();
	for (auto& [bucket, hot]: m_hot_regions) {
		if (hot.hits < 2 || hot.in_flight || frame - hot.last_hit_frame > 120) {
			continue;
		}
		if (!IsRegionRegistered(hot.begin, 1)) {
			continue;
		}
		const auto id = FindBuffer(hot.begin, 1);
		if (!id) {
			continue;
		}
		auto&      buffer = m_slot_buffers[id];
		const auto begin  = std::max(hot.begin, buffer.CpuAddress());
		const auto end    = std::min(hot.end, buffer.CpuAddress() + buffer.Size());
		if (begin >= end) {
			continue;
		}
		std::vector<ReadbackPiece> pieces;
		uint64_t           packed = 0;
		m_memory_tracker.ForEachDownloadRange<false>(
		    begin, end - begin, [&](uint64_t address, uint64_t bytes) noexcept {
			    m_gpu_modified_ranges.ForEachInRange(
			        address, bytes, [&](uint64_t first, uint64_t last) {
				        pieces.push_back({first, last - first, packed});
				        packed += AlignDownload((last - first) + (first & 3u));
			        });
		    });
		if (pieces.empty() || packed > (4u << 20)) {
			continue;
		}
		const auto [mapped, base_offset] = m_download_buffer.Map(packed, DOWNLOAD_ALIGNMENT);
		if (mapped == nullptr) {
			continue;
		}
		for (const auto& piece: pieces) {
			const auto source_begin = piece.address & ~uint64_t {3};
			const auto envelope     = piece.size + (piece.address - source_begin);
			m_download_buffer.CopyFrom(m_scheduler.Current(), buffer, buffer.Offset(source_begin),
			                           base_offset + piece.offset, envelope,
			                           vk::AccessFlagBits::eMemoryWrite, vk::AccessFlags {},
			                           vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite,
			                           vk::AccessFlagBits::eHostRead, RenderPassEnd::Download);
		}
		m_download_buffer.Commit();
		hot.in_flight  = true;
		const auto seq = m_gpu_write_seq;
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 16) {
			LOGF("ReadbackPrefetch: frame=%d region=0x%016" PRIx64 "-0x%016" PRIx64
			     " pieces=%zu bytes=0x%" PRIx64 " hits=%u\n",
			     frame, begin, end, pieces.size(), packed, hot.hits);
		}
		auto& gpu = m_scheduler.Context().GetGpu();
		m_scheduler.DeferPriorityOperation([this, &gpu, bucket, pieces = std::move(pieces), mapped,
		                                    base_offset, seq]() mutable {
			// Priority thread: the copies have completed. Take the bytes out of the ring now (the
			// ring slot is only guarded by the GPU tick) and let the GPU thread apply them.
			std::vector<uint8_t> data;
			uint64_t             total = 0;
			for (const auto& piece: pieces) {
				total += piece.size;
			}
			data.reserve(total);
			for (const auto& piece: pieces) {
				const auto skew = piece.address & 3u;
				m_download_buffer.Invalidate(base_offset + piece.offset, piece.size + skew);
				const auto* source = mapped + piece.offset + skew;
				data.insert(data.end(), source, source + piece.size);
			}
			if (gpu.IsStopping()) {
				return;
			}
			gpu.SendCommand([this, bucket, pieces = std::move(pieces), data = std::move(data), seq] {
				if (auto it = m_hot_regions.find(bucket); it != m_hot_regions.end()) {
					it->second.in_flight = false;
				}
				ApplyReadbackPieces(pieces, data.data(), seq);
			});
		});
	}
}

// Gate "protbatch2": the collecting half of a read-only synchronization of the dirty-range pass.
// Consumes the CPU-dirty bits of the range and arms its write watchers into the pass batch scope,
// where they only become pending; the caller applies them and only then copies the bytes.
// The statistics of gate "stkstat" (session 57, A1 ceiling) are not collected on this path.
bool BufferCache::CollectBufferUpload(Buffer& buffer, uint64_t vaddr, uint64_t size,
                                      std::vector<vk::BufferCopy>& copies, uint64_t& total_size) {
	Common::FrameStats::Scope sync_scope(Common::FrameStats::Counter::BindBufSyncNs);
	const auto [cpu_epoch, epoch_kind] = UploadEpoch(vaddr, size);
	if (BufferUploadEpochEnabled() && buffer.HasCurrentUpload(cpu_epoch, epoch_kind, vaddr, size)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BufEpochHits, 1);
		return false;
	}
	if (SyncFreeSkip(vaddr, size)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SyncFreeSkips, 1);
	} else {
		m_memory_tracker.ForEachUploadRange(
		    vaddr, size, false,
		    [&](uint64_t address, uint64_t bytes) noexcept {
			    copies.emplace_back(total_size, buffer.Offset(address), bytes);
			    total_size += bytes;
		    },
		    []() noexcept {}, true, nullptr, true);
	}
	// Keep the epoch from before synchronization, so concurrent writes force another upload.
	// This is only the requested interval: a different part of the same buffer may remain dirty.
	buffer.upload_epoch      = cpu_epoch;
	buffer.upload_epoch_kind = epoch_kind;
	buffer.upload_begin      = vaddr;
	buffer.upload_end        = vaddr + size;
	if (copies.empty()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SyncNoop, 1);
		return false;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::PassUploads, 1);
	return true;
}

// Gate "protbatch2" (phase 2 of "protbatch"). The pass arms the write watchers of every buffer it
// synchronizes behind one flush per tracking region instead of one scope flush and one range flush
// per buffer: the CPU-dirty bits of all of them are consumed first (every watcher change only marks
// its pages pending), the flush applies the merged runs, and only then are the guest bytes copied.
// Why no guest write is lost: what ForEachUploadRange has to guarantee is that a page whose CPU-dirty
// bit it cleared is read-only on the host before anything reads that page. The single flush covers
// every range the pass noted and returns before the first copy of the pass, so it holds for all of
// them. A guest write landing before the flush precedes every copy and is part of it; one landing
// after it faults, which marks the page CPU-dirty again for the next pass, exactly as before.
void BufferCache::SynchronizeBuffersOfDirtyRangesBatched(PageManager::PassScope& pass) {
	if (m_in_pass) {
		// The collected uploads are members, and they stay live across the copy phase below, where
		// UploadCopies may wait for the GPU and run deferred operations. No path reaches a second
		// pass from there today; if one ever does, it would silently copy this pass's ranges from
		// the wrong buffers instead of being noticed here.
		EXIT("BufferCache: reentrant dirty-range pass\n");
	}
	m_in_pass           = true;
	m_pass_upload_count = 0;
	{
		// One scope for the whole pass: the watcher changes of every buffer below land in its slots
		// and are applied together, so runs of neighbouring buffers become one host call.
		PageManager::BatchScope batch(m_memory_tracker.Pages(), true);
		for (const auto& range: m_bda_dirty_ranges) {
			auto it = m_buffers.upper_bound(range.address);
			if (it != m_buffers.begin()) --it;
			for (; it != m_buffers.end() && it->first < range.End(); ++it) {
				const auto id     = it->second;
				auto&      buffer = m_slot_buffers[id];
				const auto start  = std::max(buffer.CpuAddress(), range.address);
				const auto finish = std::min(buffer.CpuAddress() + buffer.Size(), range.End());
				if (start >= finish) {
					continue;
				}
				Common::FrameStats::Add(Common::FrameStats::Counter::PassSyncs, 1);
				// Noted before the bits are consumed: the flush of this window has to cover
				// whatever the collection below arms inside it.
				pass.Note(start, finish - start);
				if (m_pass_upload_count == m_pass_uploads.size()) {
					m_pass_uploads.emplace_back();
				}
				auto& upload      = m_pass_uploads[m_pass_upload_count];
				upload.id         = id;
				upload.vaddr      = start;
				upload.size       = finish - start;
				upload.total_size = 0;
				upload.copies.clear();
				if (CollectBufferUpload(buffer, start, finish - start, upload.copies,
				                        upload.total_size)) {
					m_pass_upload_count++;
				}
			}
		}
		batch.Flush(); // the watchers this pass deferred
		pass.Flush();  // and whatever another caller left pending on the same ranges
		if (Common::Gates::Enabled(Common::Gates::Gate::ProtectBatchVerify)) {
			// Self-check "pbcheck": after the single flush every range of the pass must already read
			// back as read-only on the host, exactly as after a flush of its own.
			for (size_t index = 0; index < m_pass_upload_count; index++) {
				const auto& upload = m_pass_uploads[index];
				m_memory_tracker.VerifyProtection(upload.vaddr, upload.size);
			}
		}
	}
	for (size_t index = 0; index < m_pass_upload_count; index++) {
		auto&      upload = m_pass_uploads[index];
		auto&      buffer = m_slot_buffers[upload.id];
		const auto source = UploadCopies(buffer, upload.copies, upload.total_size);
		RecordBufferCopies(buffer, source, upload.copies, upload.total_size);
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::PassPasses, 1);
	m_in_pass = false;
}

// Uploads the CPU-written parts of every registered buffer intersecting m_bda_dirty_ranges.
void BufferCache::SynchronizeBuffersOfDirtyRanges() {
	if (m_bda_dirty_ranges.empty()) {
		return;
	}
	// The pass scope attributes the host protection calls of this pass to it (pb2_vp*) with the gate
	// off as well, which is how the ceiling of the merge is read before it is switched on. It only
	// owns the protection of the ranges - and therefore only flushes - on the batched path.
	const bool batched = Common::Gates::Enabled(Common::Gates::Gate::ProtectBatchPass) &&
	                     Common::Gates::Enabled(Common::Gates::Gate::ProtectBatch);
	PageManager::PassScope pass(m_memory_tracker.Pages(), batched);
	if (batched) {
		SynchronizeBuffersOfDirtyRangesBatched(pass);
		return;
	}
	for (const auto& range: m_bda_dirty_ranges) {
		auto it = m_buffers.upper_bound(range.address);
		if (it != m_buffers.begin()) --it;
		for (; it != m_buffers.end() && it->first < range.End(); ++it) {
			auto&      buffer = m_slot_buffers[it->second];
			const auto start  = std::max(buffer.CpuAddress(), range.address);
			const auto finish = std::min(buffer.CpuAddress() + buffer.Size(), range.End());
			if (start < finish) {
				Common::FrameStats::Add(Common::FrameStats::Counter::PassSyncs, 1);
				pass.Note(start, finish - start); // pb2_reg only: this scope flushes nothing
				(void)SynchronizeBuffer(buffer, start, finish - start, false, false);
			}
		}
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::PassPasses, 1);
}

// Incremental variant (gate "bdastamp"): only regions that announced a CPU write since the last
// scan are locked and walked. The witness is read and stored BEFORE the region is scanned, so a
// write racing with the scan is seen by the next preparation instead of being lost.
void BufferCache::SynchronizeBuffersByRegion(uint64_t scan_begin, uint64_t scan_end) {
	if (m_bda_region_stamps.empty()) {
		m_bda_region_stamps.resize(MemoryTracker::RegionCount());
	}
	for (auto cursor = scan_begin; cursor < scan_end;) {
		const auto index = cursor / TRACKER_REGION_SIZE;
		const auto bytes =
		    std::min(scan_end - cursor, TRACKER_REGION_SIZE - cursor % TRACKER_REGION_SIZE);
		const auto stamp = m_memory_tracker.RegionWriteStamp(index);
		auto&      seen  = m_bda_region_stamps[index];
		if (seen.generation == m_bda_stamp_generation && seen.stamp == stamp) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsSkipped, 1);
			cursor += bytes;
			continue;
		}
		seen = {stamp, m_bda_stamp_generation};
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsScanned, 1);
		m_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);
		SynchronizeBuffersOfDirtyRanges();
		cursor += bytes;
	}
}

void BufferCache::SynchronizeBuffersInRange(uint64_t vaddr, uint64_t size) {
	// Gate "stkstat": the synchronizations below run for the BDA scan (stk_arm_hot_bda, stk_chk_est).
	struct BdaScanScope {
		BdaScanScope() noexcept { t_sticky_bda_scan = true; }
		~BdaScanScope() { t_sticky_bda_scan = false; }
		BdaScanScope(const BdaScanScope&)            = delete;
		BdaScanScope& operator=(const BdaScanScope&) = delete;
	} bda_scan_scope;
	static const bool dirty_ranges = [] {
		const auto* value = std::getenv("KYTY_BDA_DIRTY_RANGES");
		return value == nullptr || value[0] != '0';
	}();
	if (dirty_ranges) {
		// Most guest mappings have no BDA buffer at all. Bound the tracker scan by the
		// first/last registered owner intersecting this mapping, without scanning the buffer list.
		const auto end = vaddr + size;
		auto first = m_buffers.upper_bound(vaddr);
		if (first != m_buffers.begin()) {
			const auto previous = std::prev(first);
			const auto& buffer = m_slot_buffers[previous->second];
			if (buffer.CpuAddress() + buffer.Size() > vaddr) first = previous;
		}
		if (first == m_buffers.end() || first->first >= end) return;
		const auto last = std::prev(m_buffers.lower_bound(end));
		const auto& last_buffer = m_slot_buffers[last->second];
		const auto scan_begin = std::max(vaddr, first->first);
		const auto scan_end = std::min(end, last_buffer.CpuAddress() + last_buffer.Size());
		// Enumerate dirtiness once per tracking region, rather than re-locking/reconciling
		// every registered buffer for every BDA draw. This is only a candidate snapshot:
		// SynchronizeBuffer still consumes current dirty bits and arms write protection.
		// CPU writes after the snapshot remain dirty for the next preparation.
		if (Common::Gates::Enabled(Common::Gates::Gate::BdaRegionStamps)) {
			SynchronizeBuffersByRegion(scan_begin, scan_end);
			return;
		}
		m_memory_tracker.CollectCpuModifiedRanges(scan_begin, scan_end - scan_begin, m_bda_dirty_ranges);
		SynchronizeBuffersOfDirtyRanges();
		return;
	}
	const auto end = vaddr + size;
	auto       it  = m_buffers.upper_bound(vaddr);
	if (it != m_buffers.begin()) {
		--it;
	}
	for (; it != m_buffers.end() && it->first < end; ++it) {
		auto&      buffer = m_slot_buffers[it->second];
		const auto start  = std::max(buffer.CpuAddress(), vaddr);
		const auto finish = std::min(buffer.CpuAddress() + buffer.Size(), end);
		if (start < finish) {
			(void)SynchronizeBuffer(buffer, start, finish - start, false, false);
		}
	}
}

} // namespace Libs::Graphics
