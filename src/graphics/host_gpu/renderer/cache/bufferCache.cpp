#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include <chrono>
#include <cstdlib>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <atomic>

#include "common/assert.h"
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
#include <array>
#include <cinttypes>
#include <cstring>
#include <memory>
#include <utility>
#include <vector>

namespace Libs::Graphics {

namespace {

constexpr uint64_t MiB           = 1024 * 1024;
constexpr uint64_t GdsBufferSize = 64 * 1024;

} // namespace

void BufferCache::WriteDataBuffer(Buffer& buffer, uint64_t address, const void* source,
                                  uint64_t size) {
	auto* bytes = static_cast<const uint8_t*>(source);
	while (size != 0) {
		const auto chunk  = std::min(size, m_staging_buffer.Size());
		const auto offset = m_staging_buffer.Copy(bytes, chunk, 4);
		buffer.CopyFrom(m_scheduler.Current(), m_staging_buffer, offset, buffer.Offset(address),
		                chunk, vk::AccessFlagBits::eHostWrite);
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
		buffer.lru_id = m_lru_cache.Insert(id, m_gc_tick);
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

void BufferCache::TouchBuffer(const Buffer& buffer) {
	if (!buffer.is_deleted) {
		m_lru_cache.Touch(buffer.lru_id, m_gc_tick);
	}
}

void BufferCache::DeleteBuffer(BufferId id) {
	auto* buffer = m_slot_buffers.try_get(id);
	if (buffer == nullptr || buffer->is_deleted) {
		return;
	}
	Unregister(id);
	if (m_scheduler.Active()) {
		m_scheduler.DeferOperation([this, id] { m_slot_buffers.erase(id); });
	} else {
		m_slot_buffers.erase(id);
	}
}

std::pair<uint64_t, uint64_t> BufferCache::DownloadEnvelope(const DownloadCopy& copy) {
	if (copy.buffer == nullptr || copy.size == 0 || copy.source_offset > copy.buffer->Size() ||
	    copy.size > copy.buffer->Size() - copy.source_offset) {
		EXIT("BufferCache: invalid download copy\n");
	}
	const auto begin = copy.source_offset & ~uint64_t {3};
	if (copy.source_offset > UINT64_MAX - copy.size ||
	    copy.source_offset + copy.size > UINT64_MAX - 3) {
		EXIT("BufferCache: download copy alignment overflow\n");
	}
	const auto end = (copy.source_offset + copy.size + 3) & ~uint64_t {3};
	if (end > copy.buffer->Size()) {
		EXIT("BufferCache: aligned download copy exceeds its owner\n");
	}
	return {begin, end - begin};
}

void BufferCache::DownloadBufferMemory(std::span<const DownloadCopy> copies) {
	Common::FrameStats::Scope download_scope(Common::FrameStats::Counter::DownloadNs,
	                                         Common::FrameStats::Counter::Downloads);
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
			                  vk::AccessFlagBits::eHostRead);
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
	if (!batch.empty()) {
		flush();
	}
	for (const auto& copy: copies) {
		m_gpu_modified_ranges.Subtract(copy.address, copy.size);
	}
}

BufferCache::BufferCache(GraphicContext& graphics, CommandScheduler& scheduler,
                         PageManager& page_manager, TextureCache& texture_cache)
	: m_graphics(graphics), m_scheduler(scheduler),
	  m_fault_manager(graphics, scheduler, *this, CACHING_PAGEBITS, CACHING_NUMPAGES),
	  m_gds_buffer(graphics, scheduler, MemoryUsage::Stream, 0, AllFlags, GdsBufferSize),
	  m_bda_pagetable_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 0, AllFlags,
	                         BDA_PAGETABLE_SIZE),
	  m_bda_null_page(graphics, scheduler, MemoryUsage::DeviceLocal, 0,
	                  AllFlags | vk::BufferUsageFlagBits::eShaderDeviceAddress, CACHING_PAGESIZE),
	  m_memory_tracker(page_manager),
	  m_staging_buffer(graphics, scheduler, MemoryUsage::Upload, 512 * MiB),
	  m_stream_buffer(graphics, scheduler, MemoryUsage::Stream, 64 * MiB),
	  m_download_buffer(graphics, scheduler, MemoryUsage::Download, 32 * MiB),
	  m_device_buffer(graphics, scheduler, MemoryUsage::DeviceLocal, 128 * MiB),
	  m_texture_cache(texture_cache) {
	std::memset(m_gds_buffer.Mapped().data(), 0, static_cast<size_t>(m_gds_buffer.Size()));
	m_gds_buffer.Flush(0, m_gds_buffer.Size());
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
	m_memory_tracker.InvalidateRegion(vaddr, size,
	                                  [this, vaddr, size] { ReadMemory(vaddr, size, true); });
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
	    window_begin, window_end - window_begin,
	    [&](uint64_t address, uint64_t bytes) noexcept {
		    m_memory_tracker.ValidateGpuDirtyPages(m_gpu_modified_ranges, address, bytes,
		                                           "memory invalidation");
	    },
	    [&](uint64_t address, uint64_t bytes) noexcept {
		    for (const auto range: m_gpu_modified_ranges.Intersections(address, bytes)) {
			    copies.push_back(
			        {&buffer, buffer.Offset(range.address), range.address, range.size});
		    }
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
		DownloadBufferMemory(copies);
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
			if (expands_right) {
				end += std::min(StreamLeapSize, PageTable::kAddressSpaceSize - end);
			}
			if (expands_left) {
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
	const auto end = (vaddr + size + CACHING_PAGESIZE - 1) & ~(CACHING_PAGESIZE - 1);
	vaddr &= ~(CACHING_PAGESIZE - 1);
	size               = end - vaddr;
	const auto overlap = ResolveOverlaps(vaddr, size);

	const auto id = m_slot_buffers.insert(
	    m_graphics, m_scheduler, MemoryUsage::DeviceLocal, overlap.begin,
	    AllFlags | vk::BufferUsageFlagBits::eShaderDeviceAddress, overlap.end - overlap.begin);
	const auto& buffer = m_slot_buffers[id];
	SetVulkanObjectNameF(m_graphics.device, buffer.Handle(),
	                     "Kyty.GameBuffer[guest=0x{:016x} size=0x{:x}]", overlap.begin,
	                     overlap.end - overlap.begin);
	for (auto it = overlap.first; it != overlap.last;) {
		const auto old_id = (it++)->second;
		JoinOverlap(id, old_id, !overlap.has_stream_leap);
	}
	Register(id);
	return id;
}

bool BufferCache::SynchronizeBuffer(Buffer& buffer, uint64_t vaddr, uint64_t size, bool is_written,
                                    bool is_texel_buffer) {
	std::vector<vk::BufferCopy> copies;
	uint64_t                    total_size = 0;
	vk::Buffer                  source;
	m_memory_tracker.ForEachUploadRange(
	    vaddr, size, is_written,
	    [&](uint64_t address, uint64_t bytes) noexcept {
		    copies.emplace_back(total_size, buffer.Offset(address), bytes);
		    total_size += bytes;
	    },
	    [&]() noexcept { source = UploadCopies(buffer, copies, total_size); });
	if (source) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SyncBufUploads, 1);
		auto& command = m_scheduler.Current();
		command.EndRendering();
		const auto native = command.Handle();
		vk::BufferMemoryBarrier before {};
		before.sType         = vk::StructureType::eBufferMemoryBarrier;
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
		native.copyBuffer(source, buffer.Handle(), static_cast<uint32_t>(copies.size()),
		                  copies.data());
		auto after          = before;
		after.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
		after.dstAccessMask = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite;
		native.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
		                       vk::PipelineStageFlagBits::eAllCommands,
		                       vk::DependencyFlagBits::eByRegion, 0, nullptr, 1, &after, 0, nullptr);
		m_scheduler.GpuMark(GpuTimeProfiler::Kind::BufferUpload,
		                    std::bit_width(total_size >> 10u)); // log2 of KiB
	}
	if (is_texel_buffer && !is_written) {
		return SynchronizeBufferFromImage(buffer, vaddr, size);
	}
	return false;
}

vk::Buffer BufferCache::UploadCopies(Buffer& buffer, std::span<vk::BufferCopy> copies,
                                     uint64_t total_size) {
	if (copies.empty()) {
		return nullptr;
	}

	auto [mapped, base_offset] = m_staging_buffer.Map(total_size, 4);
	if (mapped != nullptr) {
		for (auto& copy: copies) {
			const auto address = buffer.CpuAddress() + copy.dstOffset;
			std::memcpy(mapped + copy.srcOffset, reinterpret_cast<const void*>(address), copy.size);
			copy.srcOffset += base_offset;
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
                                                       BufferId id) {
	Common::FrameStats::Add(Common::FrameStats::Counter::ObtainBufs, 1);
	auto& command = m_scheduler.Current();
	if (command.IsInvalid() || !GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: buffer request requires a recording command buffer\n");
	}

	if (!is_written && size <= CACHING_PAGESIZE &&
	    !m_memory_tracker.IsRegionGpuModified(vaddr, size) &&
	    m_memory_tracker.IsRegionCpuModified(vaddr, size)) {
		const auto alignment = std::max<uint64_t>(
		    m_graphics.physical_device_properties.limits.minUniformBufferOffsetAlignment, 1);
		auto [mapped, offset] = m_stream_buffer.Map(size, alignment, false);
		if (mapped != nullptr && Libs::LibKernel::Memory::TryReadBacking(vaddr, mapped, size)) {
			m_stream_buffer.Commit();
			return {&m_stream_buffer, offset};
		}
	}

	auto* buffer = m_slot_buffers.try_get(id);
	if (buffer == nullptr || buffer->is_deleted || !buffer->IsInBounds(vaddr, size)) {
		id     = FindBuffer(vaddr, size);
		buffer = &m_slot_buffers[id];
	}
	TouchBuffer(*buffer);
	(void)SynchronizeBuffer(*buffer, vaddr, size, is_written, is_texel_buffer);
	if (is_written) {
		m_gpu_modified_ranges.Add(vaddr, size);
		NoteGpuWrite(vaddr, size);
	}
	return {buffer, buffer->Offset(vaddr)};
}

std::pair<Buffer*, uint64_t> BufferCache::ObtainBufferForImage(uint64_t vaddr, uint64_t size) {
	if (!GuestRange {vaddr, size}.Valid()) {
		EXIT("BufferCache: invalid image source\n");
	}
	auto find_owner = [&]() -> Buffer* {
		const auto* owner = m_page_table.Find(vaddr >> PageTable::kPageBits);
		if (owner == nullptr || !*owner) {
			return nullptr;
		}
		auto& buffer = m_slot_buffers[*owner];
		return buffer.IsInBounds(vaddr, size) ? &buffer : nullptr;
	};

	{
		const bool cpu_modified            = m_memory_tracker.IsRegionCpuModified(vaddr, size);
		const bool gpu_modified            = m_memory_tracker.IsRegionGpuModified(vaddr, size);
		const bool has_dirty_buffer_source = m_gpu_modified_ranges.Intersects(vaddr, size);
		m_memory_tracker.ValidateGpuDirtyOwnership(m_gpu_modified_ranges, vaddr, size,
		                                           "image source");

		auto* owner = find_owner();
		if (has_dirty_buffer_source && owner == nullptr) {
			if (!IsRegionRegistered(vaddr, size)) {
				EXIT("BufferCache: GPU-dirty image source has no native buffer\n");
			}
			owner = &m_slot_buffers[FindBuffer(vaddr, size)];
		}
		if (owner != nullptr && !cpu_modified && (!gpu_modified || has_dirty_buffer_source)) {
			TouchBuffer(*owner);
			return {owner, owner->Offset(vaddr)};
		}
		if (has_dirty_buffer_source && owner == nullptr) {
			EXIT("BufferCache: GPU-dirty image source could not resolve its native owner\n");
		}
	}

	auto [staging, stage_offset] = m_staging_buffer.Map(size, 16);
	if (staging == nullptr) {
		EXIT("BufferCache: failed to map staging for a guest image\n");
	}
	{
		Common::FrameStats::Scope copy_scope(Common::FrameStats::Counter::ImgCopyNs);
		const void*               backing = nullptr;
		if (size >= Common::PARALLEL_COPY_MIN_BYTES &&
		    Libs::LibKernel::Memory::TryGetBackingPointer(vaddr, size, &backing)) {
			// Large image inside one mapping: spread the copy over the worker pool.
			Common::ParallelMemcpy(staging, backing, static_cast<size_t>(size));
		} else if (!Libs::LibKernel::Memory::TryReadBacking(vaddr, staging, size) &&
		           !Libs::LibKernel::Memory::TryReadPrtBacking(vaddr, staging, size)) {
			EXIT("BufferCache: failed to read mapped guest image backing\n");
		}
	}
	m_staging_buffer.Commit();
	// Debug aid: KYTY_DUMP_TEX=<hex guest address> saves the staging copy of that image source to
	// _tex_<n>.bin (first three uploads) and logs which upload path is taken.
	static const uint64_t dump_tex = [] {
		const char* value = std::getenv("KYTY_DUMP_TEX");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	const bool dump_this = dump_tex != 0 && vaddr == dump_tex;
	if (dump_this) {
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

	const bool has_dirty_buffer_source = m_gpu_modified_ranges.Intersects(vaddr, size);
	auto*      owner                   = find_owner();
	if (has_dirty_buffer_source && owner == nullptr) {
		EXIT("BufferCache: GPU-dirty image source lost its native owner\n");
	}
	if (owner == nullptr ||
	    (m_memory_tracker.IsRegionGpuModified(vaddr, size) && !has_dirty_buffer_source)) {
		if (dump_this) {
			LOGF("DumpTex: image source 0x%012" PRIx64 " size=0x%" PRIx64 " via staging (owner=%d)\n",
			     vaddr, size, owner != nullptr ? 1 : 0);
		}
		return {&m_staging_buffer, stage_offset};
	}

	TouchBuffer(*owner);
	std::vector<std::pair<uint64_t, uint64_t>> uploads;
	m_memory_tracker.ForEachUploadRange(
	    vaddr, size, false,
	    [&](uint64_t address, uint64_t upload_size) noexcept {
		    uploads.emplace_back(address, upload_size);
	    },
	    [&]() noexcept {
		    for (const auto& [address, upload_size]: uploads) {
			    owner->CopyFrom(m_scheduler.Current(), m_staging_buffer,
			                    stage_offset + address - vaddr, owner->Offset(address), upload_size,
			                    vk::AccessFlagBits::eHostWrite);
		    }
	    });
	if (dump_this) {
		uint64_t bytes = 0;
		for (const auto& [address, upload_size]: uploads) {
			bytes += upload_size;
		}
		LOGF("DumpTex: image source 0x%012" PRIx64 " size=0x%" PRIx64 " via owner buffer (offset=0x%" PRIx64
		     ", owner size=0x%" PRIx64 ") dirty ranges=%zu dirty bytes=0x%" PRIx64 " first=0x%012" PRIx64
		     "+0x%" PRIx64 "\n",
		     vaddr, size, owner->Offset(vaddr), owner->Size(), uploads.size(), bytes,
		     uploads.empty() ? 0ull : uploads.front().first,
		     uploads.empty() ? 0ull : uploads.front().second);
	}
	return {owner, owner->Offset(vaddr)};
}

void BufferCache::WriteHostMemory(uint64_t vaddr, std::span<const uint8_t> data) {
	if (vaddr == 0 || data.empty() || data.size() > UINT64_MAX - vaddr) {
		EXIT("BufferCache: invalid host DMA write\n");
	}
	Libs::LibKernel::Memory::WriteBacking(vaddr, data.data(), data.size());

	const auto end = vaddr + data.size();
	for (const auto& [address, id]: m_buffers) {
		auto&      buffer     = m_slot_buffers[id];
		const auto buffer_end = address + buffer.Size();
		const auto begin      = std::max(vaddr, address);
		const auto range_end  = std::min(end, buffer_end);
		if (begin >= range_end) {
			continue;
		}
		WriteDataBuffer(buffer, begin, data.data() + begin - vaddr, range_end - begin);
		TouchBuffer(buffer);
	}
}

void BufferCache::FillBuffer(uint64_t vaddr, uint64_t size, uint32_t value, bool is_gds) {
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
		return;
	}
	if (vaddr == 0) {
		EXIT("BufferCache: invalid fill memory address\n");
	}
	(void)m_texture_cache.ClearMeta(vaddr);
	{
		const auto region = m_texture_cache.QueryRegion(vaddr, size);
		if (!HasGpuDirtyBytes(vaddr, size) && !region.gpu_image_bytes) {
			if (region.image_bytes) {
				m_texture_cache.InvalidateMemory(vaddr, size);
			}
			std::array<uint32_t, 4096> values;
			values.fill(value);
			const std::span<const uint8_t> bytes {reinterpret_cast<const uint8_t*>(values.data()),
			                                      sizeof(values)};
			for (uint64_t offset = 0; offset < size;) {
				const auto chunk = std::min<uint64_t>(size - offset, bytes.size());
				WriteHostMemory(vaddr + offset, bytes.first(chunk));
				offset += chunk;
			}
			return;
		}
	}

	m_texture_cache.InvalidateMemoryFromGPU(vaddr, size);
	const auto id          = FindBuffer(vaddr, size);
	auto [dst, dst_offset] = ObtainBuffer(vaddr, size, true, true, id);
	EXIT_IF(dst == nullptr);
	dst->Fill(dst_offset, size, value);
}

void BufferCache::CopyBuffer(uint64_t dst_vaddr, uint64_t src_vaddr, uint64_t size, bool dst_gds,
                             bool src_gds) {
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
	if (src_memory || dst_memory) {
		const auto src_region =
		    src_memory ? m_texture_cache.QueryRegion(src_vaddr, size) : TextureCache::RegionInfo {};
		const auto dst_region =
		    dst_memory ? m_texture_cache.QueryRegion(dst_vaddr, size) : TextureCache::RegionInfo {};
		if (src_memory && dst_memory && !HasGpuDirtyBytes(src_vaddr, size) &&
		    !HasGpuDirtyBytes(dst_vaddr, size) && !src_region.gpu_image_bytes &&
		    !dst_region.gpu_image_bytes) {
			if (dst_region.image_bytes) {
				m_texture_cache.InvalidateMemory(dst_vaddr, size);
			}
			std::array<uint8_t, 64 * 1024> bytes;
			for (uint64_t offset = 0; offset < size;) {
				const auto chunk = std::min<uint64_t>(size - offset, bytes.size());
				if (!Libs::LibKernel::Memory::TryReadBacking(src_vaddr + offset, bytes.data(),
				                                             chunk)) {
					EXIT("BufferCache: host DMA source has no direct backing\n");
				}
				WriteHostMemory(dst_vaddr + offset, std::span {bytes}.first(chunk));
				offset += chunk;
			}
			return;
		}
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
	EXIT_IF(src == nullptr || dst == nullptr);
	if (src == dst && src_offset < dst_offset + size && dst_offset < src_offset + size) {
		EXIT("BufferCache: resolved Vulkan copy ranges overlap\n");
	}
	dst->CopyFrom(command, *src, src_offset, dst_offset, size);
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

	std::vector<BufferId> dirty_buffers;
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
		if (dirty) {
			m_memory_tracker.ForEachDownloadRange<false>(
			    buffer.CpuAddress(), buffer.Size(),
			    [&](uint64_t dirty_address, uint64_t dirty_size) noexcept {
				    m_memory_tracker.ValidateGpuDirtyPages(m_gpu_modified_ranges, dirty_address,
				                                           dirty_size, "garbage collection");
			    },
			    [&](uint64_t dirty_address, uint64_t dirty_size) noexcept {
				    m_gpu_modified_ranges.ForEachIntersection(
				        dirty_address, dirty_size, [&](RangeSet::Range range) {
					    copies.push_back({&buffer, range.address - buffer.CpuAddress(),
					                      range.address, range.size});
				        });
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

	EXIT_IF(copies.empty());
	DownloadBufferMemory(copies);
	for (const auto id: dirty_buffers) {
		auto& buffer = m_slot_buffers[id];
		m_memory_tracker.UnmarkRegionAsGpuModified(buffer.CpuAddress(), buffer.Size());
		if (m_memory_tracker.IsRegionGpuModified(buffer.CpuAddress(), buffer.Size()) ||
		    m_gpu_modified_ranges.Intersects(buffer.CpuAddress(), buffer.Size())) {
			EXIT("BufferCache: garbage collection retained GPU ownership\n");
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
	    window_begin, window_end - window_begin,
	    [&](uint64_t address, uint64_t bytes) noexcept {
		    m_memory_tracker.ValidateGpuDirtyPages(m_gpu_modified_ranges, address, bytes,
		                                           "memory invalidation");
	    },
	    [&](uint64_t address, uint64_t bytes) noexcept {
		    for (const auto range: m_gpu_modified_ranges.Intersections(address, bytes)) {
			    job.pieces.push_back({range.address, range.size, packed});
			    packed += AlignDownload(range.size + (range.address & 3u));
		    }
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
		                           vk::AccessFlagBits::eHostRead);
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
		    for (const auto range: m_gpu_modified_ranges.Intersections(address, bytes)) {
			    pieces.push_back({range.address, range.size, packed});
			    packed += AlignDownload(range.size + (range.address & 3u));
		    }
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
		                           vk::AccessFlagBits::eHostRead);
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
			    for (const auto range: m_gpu_modified_ranges.Intersections(address, bytes)) {
				    pieces.push_back({range.address, range.size, packed});
				    packed += AlignDownload(range.size + (range.address & 3u));
			    }
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
			                           vk::AccessFlagBits::eHostRead);
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

void BufferCache::SynchronizeBuffersInRange(uint64_t vaddr, uint64_t size) {
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
