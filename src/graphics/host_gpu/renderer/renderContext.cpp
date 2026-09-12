#include "graphics/host_gpu/renderer/renderContext.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/presentation/videoOut.h"
#include "kernel/memory.h"
#include "libs/errno.h"

#include <algorithm>
#include <atomic>
#include <cinttypes>
#include <cstdlib>

namespace Libs::Graphics {

RenderContext::RenderContext(GraphicContext& graphics)
    : m_graphics(graphics), m_render_executor(*this), m_command_scheduler(*this, graphics),
      m_descriptor_heap(graphics, m_command_scheduler.GetMasterSemaphore()),
      m_pipeline_cache(graphics), m_sampler_cache(graphics),
      m_buffer_cache(graphics, m_command_scheduler, m_page_manager, m_texture_cache),
      m_texture_cache(graphics, m_command_scheduler, m_page_manager, m_buffer_cache) {
	EXIT_NOT_IMPLEMENTED(!Common::Thread::IsMainThread());
	m_command_scheduler.EnableGpuTime();
}

RenderContext::~RenderContext() {
	ShutdownGpu();
	m_command_scheduler.Shutdown();
}

void RenderContext::InitializeGpu(VideoOut::VideoOutDriver* video_out) {
	EXIT_IF(m_gpu != nullptr);
	m_video_out = video_out;
	m_gpu       = std::make_unique<GuestGpu>(*this);
}

void RenderContext::ShutdownGpu() {
	if (m_gpu != nullptr) {
		m_gpu->Shutdown();
		m_gpu.reset();
	}
	if (m_video_out != nullptr) {
		if (m_command_scheduler.Active()) {
			m_command_scheduler.Finish();
		}
		m_command_scheduler.DrainPriorityOperations();
		m_video_out = nullptr;
	}
}

GuestGpu& RenderContext::GetGpu() const {
	EXIT_IF(m_gpu == nullptr);
	return *m_gpu;
}

VideoOut::VideoOutDriver& RenderContext::GetVideoOut() const {
	EXIT_IF(m_video_out == nullptr);
	return *m_video_out;
}

bool RenderContext::HandleFault(PageFaultAccess access, uint64_t fault_vaddr) noexcept {
	// The host reports the faulting byte, not the instruction's access width. Both caches
	// resolve its page; guessing a width can cross the end of a valid guest mapping.
	constexpr uint64_t fault_size = 1;
	if (!IsMapped(fault_vaddr, fault_size)) {
		return false;
	}
	// KYTY_FAULT_TRACE=1: log CPU page faults on GPU-tracked memory (address, access).
	static const bool trace = std::getenv("KYTY_FAULT_TRACE") != nullptr;
	if (access == PageFaultAccess::Write) {
		const auto t0 = trace ? Common::FrameStats::NowNs() : 0;
		(void)m_buffer_cache.WaitPendingHostReads(fault_vaddr & ~uint64_t {4095}, 4096);
		m_buffer_cache.InvalidateMemory(fault_vaddr, fault_size);
		const auto t1 = trace ? Common::FrameStats::NowNs() : 0;
		m_texture_cache.InvalidateMemory(fault_vaddr, fault_size);
		if (trace) {
			static std::atomic<uint64_t> count {0};
			const auto                   n = count.fetch_add(1, std::memory_order_relaxed);
			if (n < 3000000) {
				const auto t2 = Common::FrameStats::NowNs();
				LOGF("FaultTrace: write addr=0x%016" PRIx64 " n=%" PRIu64 " buf_us=%llu tex_us=%llu"
				     "\n",
				     fault_vaddr, n, static_cast<unsigned long long>((t1 - t0) / 1000u),
				     static_cast<unsigned long long>((t2 - t1) / 1000u));
			}
		}
	} else {
		if (trace) {
			static std::atomic<uint64_t> count {0};
			const auto                   n = count.fetch_add(1, std::memory_order_relaxed);
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
				     " %08x %08x %08x %08x %08x %08x %08x %08x"
				     "\n",
				     fault_vaddr, base, words[0], words[1], words[2], words[3], words[4], words[5],
				     words[6], words[7]);
			}
		}
	}
	return true;
}

bool RenderContext::InvalidateMemory(uint64_t vaddr, uint64_t size) {
	if (!IsMapped(vaddr, size)) {
		return false;
	}
	(void)m_buffer_cache.WaitPendingHostReads(vaddr, size);
	m_buffer_cache.InvalidateMemory(vaddr, size);
	m_texture_cache.InvalidateMemory(vaddr, size);
	return true;
}

void RenderContext::NoteStreamedRead(uint64_t vaddr, uint64_t size) {
	if (!IsMapped(vaddr, size)) {
		return;
	}
	m_buffer_cache.NoteStreamedRead(vaddr, size);
}

void RenderContext::ReleaseGuestStack(uint64_t vaddr, uint64_t size) {
	if (!IsMapped(vaddr, size) || m_gpu == nullptr) {
		return;
	}
	m_gpu->SendCommandSync([this, vaddr, size] {
		m_buffer_cache.DeleteBuffersOverlapping(vaddr, size);
		m_buffer_cache.InvalidateMemory(vaddr, size);
	});
}

bool RenderContext::IsMapped(uint64_t vaddr, uint64_t size) const noexcept {
	if (!GuestRange {vaddr, size}.Valid()) {
		return false;
	}
	std::shared_lock lock(m_mapped_ranges_mutex);
	return m_mapped_ranges.Contains(vaddr, size);
}

void RenderContext::MapMemory(uint64_t vaddr, uint64_t size) {
	std::lock_guard lock(m_mapped_ranges_mutex);
	m_mapped_ranges.Add(vaddr, size);
	++m_mapping_epoch;
}

void RenderContext::UnmapMemory(uint64_t vaddr, uint64_t size) {
	if (CommandScheduler::InDeferredOperation()) {
		EXIT("unsupported memory unmap from an asynchronous GPU completion, "
		     "addr=0x%016" PRIx64 " size=0x%016" PRIx64 "\n",
		     vaddr, size);
	}
	const auto unmap = [this, vaddr, size] {
		if (m_command_scheduler.Active()) {
			const auto                        tick = m_command_scheduler.CurrentTick();
			Common::FrameStats::SiteScope     site_scope("unmap");
			m_command_scheduler.Finish();
			m_command_scheduler.WaitPriorityOperations(tick);
		}
		m_buffer_cache.InvalidateMemory(vaddr, size);
		m_texture_cache.UnmapMemory(vaddr, size);
		std::lock_guard lock(m_mapped_ranges_mutex);
		m_mapped_ranges.Subtract(vaddr, size);
		++m_mapping_epoch;
	};
	// Shutdown still owns the GPU while queued rendering drains, but its command lane no
	// longer accepts external work. Use the guest GPU's state for the teardown route.
	if (m_gpu == nullptr || m_gpu->IsStopping()) {
		unmap();
		return;
	}
	m_gpu->SendCommandSync(unmap);
}

void RenderContext::PrepareBda() {
	Common::FrameStats::Scope scope(Common::FrameStats::Counter::BdaPrepareNs,
	                                Common::FrameStats::Counter::BdaPrepares);
	std::shared_lock          lock(m_mapped_ranges_mutex);
	static const bool         reuse = [] {
		const auto* value = std::getenv("KYTY_BDA_EPOCH_CACHE");
		return value == nullptr || value[0] != '0';
	}();
	const auto cpu_epoch          = m_buffer_cache.CpuWriteEpoch();
	const auto registration_epoch = m_buffer_cache.RegistrationEpoch();
	m_fault_process_pending       = true;
	if (reuse && cpu_epoch == m_bda_cpu_epoch && registration_epoch == m_bda_registration_epoch &&
	    m_mapping_epoch == m_bda_mapping_epoch) {
		return;
	}
	m_mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {
		m_buffer_cache.SynchronizeBuffersInRange(start, end - start);
	});
	// Save the epochs from BEFORE the scan. A concurrent invalidation must force another scan,
	// even if it occurred in a region already visited. Never cache guest bytes or clear dirtiness.
	m_bda_cpu_epoch          = cpu_epoch;
	m_bda_registration_epoch = registration_epoch;
	m_bda_mapping_epoch      = m_mapping_epoch;
}

void RenderContext::RunGarbageCollector() {
	if (m_fault_process_pending) {
		m_fault_process_pending = false;
		m_buffer_cache.ProcessFaultBuffer();
	}
	m_texture_cache.ProcessDownloadImages();
	m_texture_cache.RunGarbageCollector();
	m_buffer_cache.RunGarbageCollector();
}

void RenderContext::AddInterruptEq(LibKernel::EventQueue::KernelEqueue eq, int event_id) {
	Common::LockGuard lock(m_interrupt_mutex);

	auto it = std::find_if(
	    m_interrupt_eqs.begin(), m_interrupt_eqs.end(),
	    [eq, event_id](const auto& entry) { return entry.eq == eq && entry.event_id == event_id; });
	if (it != m_interrupt_eqs.end()) {
		return;
	}

	m_interrupt_eqs.push_back({eq, event_id});
}

void RenderContext::DeleteInterruptEq(LibKernel::EventQueue::KernelEqueue eq, int event_id) {
	Common::LockGuard lock(m_interrupt_mutex);

	auto it = std::find_if(
	    m_interrupt_eqs.begin(), m_interrupt_eqs.end(),
	    [eq, event_id](const auto& entry) { return entry.eq == eq && entry.event_id == event_id; });
	if (it == m_interrupt_eqs.end()) {
		return;
	}

	m_interrupt_eqs.erase(it);
}

void RenderContext::TriggerInterrupt(int event_id, uint32_t context_id) {
	std::vector<InterruptEqRegistration> registrations;
	{
		Common::LockGuard lock(m_interrupt_mutex);
		for (const auto& registration: m_interrupt_eqs) {
			if (registration.event_id == event_id) {
				registrations.push_back(registration);
			}
		}
	}

	for (const auto& registration: registrations) {
		const auto result = LibKernel::EventQueue::KernelTriggerEvent(
		    registration.eq, static_cast<uintptr_t>(registration.event_id),
		    LibKernel::EventQueue::KERNEL_EVFILT_GRAPHICS,
		    reinterpret_cast<void*>(static_cast<uintptr_t>(context_id)));
		if (result == LibKernel::KERNEL_ERROR_EBADF || result == LibKernel::KERNEL_ERROR_ENOENT) {
			DeleteInterruptEq(registration.eq, registration.event_id);
			continue;
		}
		EXIT_NOT_IMPLEMENTED(result != OK);
	}
}

} // namespace Libs::Graphics
