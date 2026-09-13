#include "graphics/host_gpu/renderer/masterSemaphore.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/gpuCheckpoints.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <cinttypes>
#include <cstdio>
#include <cstdlib>

namespace Libs::Graphics {

namespace {

// Diagnostic runs give up on a queue that stopped completing work instead of waiting forever:
// a wedged submission keeps the whole host GPU busy, so the sooner the process exits, the sooner
// the driver recovers. Counted in 2 s wait timeouts; KYTY_GPU_HANG_ABORT_S=0 waits forever.
uint32_t HangAbortTimeouts() {
	static const uint32_t timeouts = [] {
		const auto* value   = std::getenv("KYTY_GPU_HANG_ABORT_S");
		const auto  seconds = value != nullptr ? std::strtoul(value, nullptr, 10) : 8u;
		if (seconds == 0) {
			return UINT32_MAX;
		}
		return static_cast<uint32_t>((seconds + 1u) / 2u);
	}();
	return timeouts;
}

} // namespace

MasterSemaphore::MasterSemaphore(GraphicContext& graphics): m_graphics(graphics) {
	vk::SemaphoreTypeCreateInfo type_info {};
	type_info.semaphoreType = vk::SemaphoreType::eTimeline;
	type_info.initialValue  = 0;

	vk::SemaphoreCreateInfo create_info {};
	create_info.pNext = &type_info;

	const auto result = m_graphics.device.createSemaphore(&create_info, nullptr, &m_semaphore);
	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess || m_semaphore == nullptr);
}

MasterSemaphore::~MasterSemaphore() {
	if (m_semaphore != nullptr) {
		m_graphics.device.destroySemaphore(m_semaphore, nullptr);
	}
}

void MasterSemaphore::Refresh() {
	uint64_t   counter = 0;
	const auto result  = m_graphics.device.getSemaphoreCounterValue(m_semaphore, &counter);
	if (result == vk::Result::eErrorDeviceLost) {
		ReportGpuCheckpoints(m_graphics);
	}
	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);

	auto known = m_gpu_tick.load(std::memory_order_acquire);
	while (known < counter &&
	       !m_gpu_tick.compare_exchange_weak(known, counter, std::memory_order_release,
	                                         std::memory_order_relaxed)) {
	}
}

void MasterSemaphore::Wait(uint64_t tick) {
	if (IsFree(tick)) {
		return;
	}
	Refresh();
	if (IsFree(tick)) {
		return;
	}

	vk::SemaphoreWaitInfo wait_info {};
	wait_info.semaphoreCount = 1;
	wait_info.pSemaphores    = &m_semaphore;
	wait_info.pValues        = &tick;

	vk::Result result;
	{
		namespace FS  = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		const bool diagnostic = m_graphics.diagnostic_checkpoints_enabled || m_graphics.gpu_breadcrumbs_enabled ||
		                        GpuQueueTraceEnabled();
		bool reported = false;
		uint32_t timeouts = 0;
		do {
			result = m_graphics.device.waitSemaphores(&wait_info,
			    diagnostic ? uint64_t {2000000000} : UINT64_MAX);
			if (diagnostic && result == vk::Result::eTimeout) {
				timeouts++;
			}
			if (diagnostic && result == vk::Result::eTimeout && timeouts >= HangAbortTimeouts()) {
				// The queue stopped completing work. Waiting longer keeps the host GPU busy with a
				// wedged submission (the desktop freezes with it), so report once more and leave:
				// the process exit releases the queue and lets the driver recover.
				LOGF("GpuHangAbort: role=%u requested=%" PRIu64 " known=%" PRIu64 " current=%" PRIu64
				     " master=%p after=%us submit_backlog=%zu\n",
				     static_cast<uint32_t>(FS::CurrentRole()), tick,
				     m_gpu_tick.load(std::memory_order_acquire), CurrentTick(),
				     static_cast<void*>(m_semaphore), timeouts * 2u, AsyncSubmitBacklog());
				std::printf("GpuHangAbort: requested=%" PRIu64 " known=%" PRIu64 " after=%us\n",
				            tick, m_gpu_tick.load(std::memory_order_acquire), timeouts * 2u);
				ReportGpuCheckpointHistory();
				ReportGpuSubmissionHistory();
				Log::Flush();
				std::fflush(stdout);
				EXIT("GPU stopped completing submissions\n");
			}
			if (diagnostic && result == vk::Result::eTimeout && !reported) {
				LOGF("GpuWaitSlow: role=%u requested=%" PRIu64 " known=%" PRIu64 " current=%" PRIu64
				     " master=%p submit_backlog=%zu\n",
				     static_cast<uint32_t>(FS::CurrentRole()), tick, m_gpu_tick.load(std::memory_order_acquire),
				     CurrentTick(), static_cast<void*>(m_semaphore), AsyncSubmitBacklog());
				std::printf("GpuWaitSlow: role=%u requested=%" PRIu64 "\n",
				            static_cast<uint32_t>(FS::CurrentRole()), tick);
				ReportGpuCheckpointHistory();
				ReportGpuSubmissionHistory();
				Log::Flush();
				reported = true;
			}
		} while (diagnostic && result == vk::Result::eTimeout);
		if (t0 != 0) {
			const auto ns = FS::NowNs() - t0;
			FS::Add(FS::Counter::SemWaitNs, ns);
			FS::Add(FS::Counter::SemWaits, 1);
			if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
				FS::Add(FS::Counter::SemWaitGpuNs, ns);
			}
			FS::AddSite(FS::Table::WaitSites, FS::CurrentSite(), ns);
		}
	}
	if (result != vk::Result::eSuccess) {
		LOGF("vkWaitSemaphores failed: %s (%d), tick=%" PRIu64 "\n",
		     vk::to_string(result).c_str(), static_cast<int>(result), tick);
		std::printf("vkWaitSemaphores failed: %s (%d), tick=%" PRIu64 "\n",
		            vk::to_string(result).c_str(), static_cast<int>(result), tick);
		if (result == vk::Result::eErrorDeviceLost) ReportGpuCheckpoints(m_graphics);
		else ReportGpuCheckpointHistory();
	}
	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
	Refresh();
}

} // namespace Libs::Graphics
