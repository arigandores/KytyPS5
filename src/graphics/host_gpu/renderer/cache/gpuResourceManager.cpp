#include "graphics/host_gpu/renderer/cache/gpuResourceManager.h"

#include "common/frameStats.h"

#include "common/assert.h"
#include "common/logging/log.h"
#include "kernel/memory.h"

#include <atomic>
#include <cinttypes>
#include <cstdlib>
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
namespace Libs::Graphics {

GpuResourceManager::GpuResourceManager(GraphicContext& graphics, CommandScheduler& scheduler)
    : m_scheduler(scheduler), m_buffer_cache(graphics, scheduler, m_page_manager, m_texture_cache),
      m_texture_cache(graphics, scheduler, m_page_manager, m_buffer_cache) {}

GpuResourceManager::~GpuResourceManager() = default;

bool GpuResourceManager::HandleFault(PageFaultAccess access, uint64_t fault_vaddr) noexcept {
	constexpr uint64_t fault_size = 8;
	if (!IsMapped(fault_vaddr, fault_size)) {
		return false;
	}
	// KYTY_FAULT_TRACE=1: log CPU page faults on GPU-tracked memory (address, access).
	static const bool trace = std::getenv("KYTY_FAULT_TRACE") != nullptr;
	if (access == PageFaultAccess::Write) {
		const auto t0 = trace ? Common::FrameStats::NowNs() : 0;
		m_buffer_cache.InvalidateMemory(fault_vaddr, fault_size);
		const auto t1 = trace ? Common::FrameStats::NowNs() : 0;
		m_texture_cache.InvalidateMemory(fault_vaddr, fault_size);
		if (trace) {
			static std::atomic<uint64_t> count {0};
			const auto n = count.fetch_add(1, std::memory_order_relaxed);
			if (n < 3000000) {
				const auto t2 = Common::FrameStats::NowNs();
				LOGF("FaultTrace: write addr=0x%016" PRIx64 " n=%" PRIu64 " buf_us=%llu tex_us=%llu" "\n",
				     fault_vaddr, n, static_cast<unsigned long long>((t1 - t0) / 1000u),
				     static_cast<unsigned long long>((t2 - t1) / 1000u));
			}
		}
	} else {
		if (trace) {
			static std::atomic<uint64_t> count {0};
			const auto n = count.fetch_add(1, std::memory_order_relaxed);
			if (n < 3000000) {
				LOGF("FaultTrace: read  addr=0x%016" PRIx64 " n=%" PRIu64 "\n", fault_vaddr, n);
			}
		}
		m_buffer_cache.ReadMemory(fault_vaddr, fault_size);
		if (trace) {
			// What the CPU is about to read, after the download.
			const auto base = fault_vaddr & ~uint64_t {15};
			uint32_t   words[8] {};
			if (Libs::LibKernel::Memory::TryReadBacking(base, words, sizeof(words))) {
				LOGF("FaultData: addr=0x%016" PRIx64 " base=0x%016" PRIx64
				     " %08x %08x %08x %08x %08x %08x %08x %08x" "\n",
				     fault_vaddr, base, words[0], words[1], words[2], words[3], words[4], words[5],
				     words[6], words[7]);
			}
		}
	}
	return true;
}

bool GpuResourceManager::InvalidateMemory(uint64_t vaddr, uint64_t size) {
	if (!IsMapped(vaddr, size)) {
		return false;
	}
	m_buffer_cache.InvalidateMemory(vaddr, size);
	m_texture_cache.InvalidateMemory(vaddr, size);
	return true;
}

void GpuResourceManager::NoteStreamedRead(uint64_t vaddr, uint64_t size) {
	if (!IsMapped(vaddr, size)) {
		return;
	}
	m_buffer_cache.NoteStreamedRead(vaddr, size);
}

void GpuResourceManager::ReleaseGuestStack(uint64_t vaddr, uint64_t size) {
	if (!IsMapped(vaddr, size)) {
		return;
	}
	m_scheduler.Context().GetGpu().SendCommandSync([this, vaddr, size] {
		m_buffer_cache.DeleteBuffersOverlapping(vaddr, size);
		m_buffer_cache.InvalidateMemory(vaddr, size);
	});
}

bool GpuResourceManager::IsMapped(uint64_t vaddr, uint64_t size) const noexcept {
	if (!GuestRange {vaddr, size}.Valid()) {
		return false;
	}
	std::shared_lock lock(m_mapped_ranges_mutex);
	return m_mapped_ranges.Contains(vaddr, size);
}

void GpuResourceManager::MapMemory(uint64_t vaddr, uint64_t size) {
	{
		std::lock_guard lock(m_mapped_ranges_mutex);
		m_mapped_ranges.Add(vaddr, size);
	}
	m_page_manager.OnGpuMap(vaddr, size);
}

void GpuResourceManager::UnmapMemory(uint64_t vaddr, uint64_t size) {
	if (CommandScheduler::InDeferredOperation()) {
		EXIT("unsupported memory unmap from an asynchronous GPU completion, "
		     "addr=0x%016" PRIx64 " size=0x%016" PRIx64 "\n",
		     vaddr, size);
	}
	const auto unmap = [this, vaddr, size] {
		if (m_scheduler.Active()) {
			const auto tick = m_scheduler.CurrentTick();
			Common::FrameStats::SiteScope site_scope("unmap");
			m_scheduler.Finish();
			m_scheduler.WaitPriorityOperations(tick);
		}
		m_buffer_cache.InvalidateMemory(vaddr, size);
		m_texture_cache.UnmapMemory(vaddr, size);
		m_page_manager.OnGpuUnmap(vaddr, size);
		std::lock_guard lock(m_mapped_ranges_mutex);
		m_mapped_ranges.Subtract(vaddr, size);
	};
	if (m_gpu == nullptr) {
		unmap();
		return;
	}
	m_gpu->SendCommandSync(unmap);
}

void GpuResourceManager::PrepareBda() {
	std::shared_lock lock(m_mapped_ranges_mutex);
	m_mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {
		m_buffer_cache.SynchronizeBuffersInRange(start, end - start);
	});
	m_fault_process_pending = true;
}

void GpuResourceManager::RunGarbageCollector() {
	if (m_fault_process_pending) {
		m_fault_process_pending = false;
		m_buffer_cache.ProcessFaultBuffer();
	}
	m_texture_cache.ProcessDownloadImages();
	m_texture_cache.RunGarbageCollector();
	m_buffer_cache.RunGarbageCollector();
}

} // namespace Libs::Graphics
