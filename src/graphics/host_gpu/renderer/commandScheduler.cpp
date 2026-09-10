#include "graphics/host_gpu/renderer/commandScheduler.h"

#include <mutex>
#include <string>
#include <map>
#include <cstdlib>

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "common/parallelCopy.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/gpuCheckpoints.h"

#include <algorithm>
#include <array>
#include <cstdio>
#include <optional>
#include <vector>

namespace Libs::Graphics {

static thread_local CommandScheduler* g_deferred_callback_scheduler = nullptr;

namespace {

void ReportVulkanFatal(GraphicContext& graphics, const char* what, vk::Result result,
                       uint64_t tick, uint32_t debug_op, uint64_t debug_submit, uint32_t arg0,
                       uint32_t arg1, uint32_t arg2, uint32_t arg3, uint64_t arg4) {
	ReportGpuCheckpoints(graphics);
	LOGF("%s failed: %s (%d), tick=%" PRIu64 " debug_op=%u debug_submit=%" PRIu64
	     " args=%u,%u,%u,%u,0x%016" PRIx64 "\n",
	     what, vk::to_string(result).c_str(), static_cast<int>(result), tick, debug_op,
	     debug_submit, arg0, arg1, arg2, arg3, arg4);
	std::printf("%s failed: %s (%d), tick=%" PRIu64 " debug_op=%u debug_submit=%" PRIu64
	            " args=%u,%u,%u,%u,0x%016" PRIx64 "\n",
	            what, vk::to_string(result).c_str(), static_cast<int>(result), tick, debug_op,
	            debug_submit, arg0, arg1, arg2, arg3, arg4);
	std::fflush(stdout);
}

} // namespace

CommandScheduler::CommandPool::CommandPool(GraphicContext& graphics, MasterSemaphore& master)
    : m_graphics(graphics), m_master(master) {
	EXIT_IF(graphics.queue_family == static_cast<uint32_t>(-1));
	vk::CommandPoolCreateInfo create {};
	create.queueFamilyIndex = graphics.queue_family;
	create.flags            = vk::CommandPoolCreateFlagBits::eTransient |
	                          vk::CommandPoolCreateFlagBits::eResetCommandBuffer;
	const auto result       = graphics.device.createCommandPool(&create, nullptr, &m_pool);
	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess || m_pool == nullptr);
}

CommandScheduler::CommandPool::~CommandPool() {
	m_graphics.device.destroyCommandPool(m_pool, nullptr);
}

size_t CommandScheduler::CommandPool::Grow() {
	const auto first = m_ticks.size();
	m_ticks.resize(first + GrowStep);
	m_buffers.resize(first + GrowStep);

	vk::CommandBufferAllocateInfo allocate {};
	allocate.commandPool        = m_pool;
	allocate.level              = vk::CommandBufferLevel::ePrimary;
	allocate.commandBufferCount = static_cast<uint32_t>(GrowStep);
	EXIT_IF(m_graphics.device.allocateCommandBuffers(&allocate, m_buffers.data() + first) !=
	        vk::Result::eSuccess);
	return first;
}

vk::CommandBuffer CommandScheduler::CommandPool::Commit() {
	auto       gpu_tick = m_master.KnownGpuTick();
	const auto search   = [this, &gpu_tick](size_t begin, size_t end) -> std::optional<size_t> {
		for (size_t index = begin; index < end; ++index) {
			if (gpu_tick >= m_ticks[index]) {
				m_ticks[index] = m_master.CurrentTick();
				return index;
			}
		}
		return std::nullopt;
	};

	auto found = search(m_hint, m_ticks.size());
	if (!found) {
		m_master.Refresh();
		gpu_tick = m_master.KnownGpuTick();
		found    = search(m_hint, m_ticks.size());
	}
	if (!found) {
		found = search(0, m_hint);
	}
	if (!found) {
		found           = Grow();
		m_ticks[*found] = m_master.CurrentTick();
	}

	m_hint = (*found + 1) % m_ticks.size();
	return m_buffers[*found];
}

bool CommandScheduler::InDeferredOperation() noexcept {
	return g_deferred_callback_scheduler != nullptr;
}

CommandScheduler::CommandScheduler(RenderContext& context, GraphicContext& graphics)
    : m_master(graphics), m_context(context), m_graphics(graphics),
      m_command_pool(graphics, m_master), m_command(*this),
      m_priority_thread([this](std::stop_token stop) { PriorityOperationsThread(stop); }),
      m_gpu_time(graphics, m_master) {
	InitTimestamps();
	// KYTY_ASYNC_COPY_GPU_WAIT=0: block the GuestGpu thread in Submit until the async copies
	// landed (the old behaviour) instead of making the queue wait for them.
	const char* gpu_wait = std::getenv("KYTY_ASYNC_COPY_GPU_WAIT");
	if (gpu_wait == nullptr || std::atoi(gpu_wait) != 0) {
		vk::SemaphoreTypeCreateInfo type_info {};
		type_info.semaphoreType = vk::SemaphoreType::eTimeline;
		type_info.initialValue  = 0;
		vk::SemaphoreCreateInfo create_info {};
		create_info.pNext = &type_info;
		const auto result = graphics.device.createSemaphore(&create_info, nullptr, &m_copy_semaphore);
		EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess || m_copy_semaphore == nullptr);
		m_copy_gpu_wait = true;
		Common::AddAsyncCopySignal(&CommandScheduler::SignalCopySemaphore, this);
	}
}

// Copy-pool thread: the async-copy completed mark advanced past a value some submit waits for.
void CommandScheduler::SignalCopySemaphore(uint64_t completed, void* user) {
	auto*                   self = static_cast<CommandScheduler*>(user);
	vk::SemaphoreSignalInfo info {};
	info.semaphore    = self->m_copy_semaphore;
	info.value        = completed;
	const auto result = self->m_graphics.device.signalSemaphore(&info);
	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
	static const bool trace = std::getenv("KYTY_ACOPY_TRACE") != nullptr;
	if (trace) {
		std::fprintf(stderr, "AcopyTrace: signal %llu\n", static_cast<unsigned long long>(completed));
	}
}

CommandScheduler::~CommandScheduler() {
	if (m_copy_gpu_wait) {
		Common::RemoveAsyncCopySignal(&CommandScheduler::SignalCopySemaphore, this);
		Common::WaitAsyncCopies();
	}
	Shutdown();
	if (m_copy_semaphore != nullptr) {
		m_graphics.device.destroySemaphore(m_copy_semaphore, nullptr);
		m_copy_semaphore = nullptr;
	}
	if (m_timestamp_pool != nullptr) {
		m_graphics.device.destroyQueryPool(m_timestamp_pool, nullptr);
		m_timestamp_pool = nullptr;
	}
}

void CommandScheduler::Shutdown() {
	{
		std::unique_lock lock(m_operation_mutex);
		if (m_operation_state == OperationState::Closed) {
			return;
		}
		if (g_deferred_callback_scheduler == this) {
			EXIT_IF(m_operation_state == OperationState::Open);
			// A priority callback cannot join its own runner, while a normal callback can be
			// executing inside the shutdown owner's final PopPendingOperations. The owning
			// thread will finish shutdown after this callback returns.
			return;
		}
		if (m_operation_state == OperationState::Draining) {
			m_operation_available.wait(
			    lock, [this] { return m_operation_state == OperationState::Closed; });
			return;
		}
		m_operation_state = OperationState::Draining;
	}
	if (!m_command.IsInvalid()) {
		Submit();
	}
	m_master.Wait(CurrentTick() - 1);
	PopPendingOperations();
	DrainPriorityOperations();
	m_priority_thread.request_stop();
	m_operation_available.notify_all();
	if (m_priority_thread.joinable()) {
		m_priority_thread.join();
	}
	{
		std::lock_guard lock(m_operation_mutex);
		EXIT_IF(!m_pending_operations.empty() || !m_priority_operations.empty() ||
		        m_priority_active);
		m_operation_state = OperationState::Closed;
	}
	m_operation_available.notify_all();
}

void CommandScheduler::Begin(HW::Context& registers, HW::UserConfig& user_config,
                             HW::Shader& shaders) {
	{
		std::lock_guard lock(m_operation_mutex);
		EXIT_IF(m_operation_state != OperationState::Open);
	}
	m_command.Bind(registers, user_config, shaders);

	if (m_command.IsInvalid()) {
		BeginNext();
	}
}

void CommandScheduler::BeginRendering(const RenderState& state) {
	Current().BeginRendering(state);
}

void CommandScheduler::EndRendering() {
	if (Active() && !m_command.IsInvalid()) {
		Current().EndRendering();
	}
}

void CommandScheduler::Flush() {
	SubmitInfo submit;
	Flush(submit);
}

void CommandScheduler::Flush(SubmitInfo& submit) {
	Submit(submit);
	BeginNext();
}

void CommandScheduler::FlushAndWait() {
	const auto tick = Submit();
	m_master.Wait(tick);
	BeginNext();
}

void CommandScheduler::Finish() {
	CheckActive();
	if (!m_command.IsInvalid()) {
		Submit();
	}
	m_master.Wait(CurrentTick() - 1);
	BeginNext();
	PopPendingOperations();
}

void CommandScheduler::Wait(uint64_t tick) {
	EXIT_IF(tick > CurrentTick());
	if (tick == CurrentTick()) {
		CheckActive();
		// A stream-buffer wrap can wait while a draw is being prepared through a reference to
		// Current(). The wrapper stays stable while its pooled Vulkan buffer is retired. Deferred
		// resources are released only at the next GPU operation boundary.
		const auto submitted_tick = Submit();
		EXIT_IF(submitted_tick != tick);
		m_master.Wait(tick);
		BeginNext();
	} else {
		m_master.Wait(tick);
	}
}

// Stable name ("+0x<rva>") for a DeferOperation call site; the RVA maps to a function through
// the linker map like the FaultTrace-gpu RIPs.
static const char* DeferredSiteName(const void* site) {
	static std::mutex                             mutex;
	static std::map<const void*, std::string>     names;
	std::lock_guard                               lock(mutex);
	auto [it, inserted] = names.try_emplace(site);
	if (inserted) {
		char text[32];
		std::snprintf(text, sizeof(text), "+0x%llx",
		              static_cast<unsigned long long>(Common::FrameStats::ModuleOffset(site)));
		it->second = text;
	}
	return it->second.c_str();
}

void CommandScheduler::PopPendingOperations() {
	PopPendingOperations(true);
}

void CommandScheduler::PopPendingOperationsLazy() {
	uint64_t front_tick = 0;
	{
		std::lock_guard lock(m_operation_mutex);
		if (m_pending_operations.empty()) {
			return;
		}
		front_tick = m_pending_operations.front().tick;
	}
	if (m_master.IsFree(front_tick)) {
		PopPendingOperations(false);
		return;
	}
	constexpr uint64_t RefreshIntervalNs = 200'000;
	const auto         now               = Common::FrameStats::NowNs();
	if (now - m_last_tick_refresh_ns < RefreshIntervalNs) {
		return;
	}
	m_last_tick_refresh_ns = now;
	PopPendingOperations(true);
}

void CommandScheduler::PopPendingOperations(bool refresh_gpu_tick) {
	{
		// Called before every draw and dispatch; the semaphore query is only worth it when
		// something waits for a tick.
		std::lock_guard lock(m_operation_mutex);
		if (m_pending_operations.empty()) {
			return;
		}
	}
	if (refresh_gpu_tick) {
		m_master.Refresh();
	}
	for (;;) {
		PendingOperation operation;
		{
			std::lock_guard lock(m_operation_mutex);
			if (m_pending_operations.empty() ||
			    !m_master.IsFree(m_pending_operations.front().tick)) {
				return;
			}
			operation = std::move(m_pending_operations.front());
			m_pending_operations.pop();
		}
		WaitPriorityOperations(operation.tick);
		{
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
			RunOperation(std::move(operation.callback));
			if (t0 != 0) {
				const auto ns = FS::NowNs() - t0;
				FS::Add(FS::Counter::PendingOpsNs, ns);
				FS::Add(FS::Counter::PendingOps, 1);
				FS::AddSite(FS::Table::PopSites, DeferredSiteName(operation.site), ns);
			}
		}
	}
}

void CommandScheduler::DeferOperation(Common::UniqueFunction<void>&& operation) {
	CheckActive();
	EXIT_IF(!operation);
	std::unique_lock lock(m_operation_mutex);
	if (m_operation_state == OperationState::Open) {
		m_pending_operations.push({std::move(operation), CurrentTick(), __builtin_return_address(0)});
		return;
	}
	if (g_deferred_callback_scheduler == this) {
		lock.unlock();
		operation();
		return;
	}
	m_operation_available.wait(lock,
	                           [this] { return m_operation_state == OperationState::Closed; });
	lock.unlock();
	operation();
}

void CommandScheduler::DeferPriorityOperation(Common::UniqueFunction<void>&& operation) {
	CheckActive();
	EXIT_IF(!operation);
	std::unique_lock lock(m_operation_mutex);
	if (m_operation_state == OperationState::Open) {
		m_priority_operations.push({std::move(operation), CurrentTick()});
		lock.unlock();
		m_operation_available.notify_one();
		return;
	}
	if (g_deferred_callback_scheduler == this) {
		lock.unlock();
		operation();
		return;
	}
	m_operation_available.wait(lock,
	                           [this] { return m_operation_state == OperationState::Closed; });
	lock.unlock();
	operation();
}

void CommandScheduler::PriorityOperationsThread(std::stop_token stop) {
	while (!stop.stop_requested()) {
		PendingOperation operation;
		{
			std::unique_lock lock(m_operation_mutex);
			m_operation_available.wait(lock, [this, &stop] {
				return stop.stop_requested() || !m_priority_operations.empty();
			});
			if (stop.stop_requested()) {
				return;
			}
			operation = std::move(m_priority_operations.front());
			m_priority_operations.pop();
			m_priority_active      = true;
			m_priority_active_tick = operation.tick;
		}
		m_master.Wait(operation.tick);
		if (!stop.stop_requested()) {
			RunOperation(std::move(operation.callback));
		}
		{
			std::lock_guard lock(m_operation_mutex);
			m_priority_active      = false;
			m_priority_active_tick = 0;
		}
		m_operation_available.notify_all();
	}
}

void CommandScheduler::DrainPriorityOperations() {
	EXIT_IF(g_deferred_callback_scheduler == this);
	std::unique_lock lock(m_operation_mutex);
	m_operation_available.wait(
	    lock, [this] { return m_priority_operations.empty() && !m_priority_active; });
}

void CommandScheduler::WaitPriorityOperations(uint64_t tick) {
	EXIT_IF(g_deferred_callback_scheduler == this);
	Common::FrameStats::Scope priority_scope(Common::FrameStats::Counter::PriorityWaitNs,
	                                         Common::FrameStats::Counter::PriorityWaits);
	std::unique_lock lock(m_operation_mutex);
	m_operation_available.wait(lock, [this, tick] {
		const bool active_before_or_at = m_priority_active && m_priority_active_tick <= tick;
		const bool queued_before_or_at =
		    !m_priority_operations.empty() && m_priority_operations.front().tick <= tick;
		return !active_before_or_at && !queued_before_or_at;
	});
}

void CommandScheduler::RunOperation(Common::UniqueFunction<void>&& operation) {
	auto* previous                = g_deferred_callback_scheduler;
	g_deferred_callback_scheduler = this;
	operation();
	g_deferred_callback_scheduler = previous;
}

bool CommandScheduler::IsFree(uint64_t tick) {
	if (m_master.IsFree(tick)) {
		return true;
	}
	m_master.Refresh();
	return m_master.IsFree(tick);
}

void CommandScheduler::CheckActive() const {
	EXIT_IF(!Active());
}

CommandBuffer& CommandScheduler::Current() {
	CheckActive();
	return m_command;
}

CommandBuffer& CommandScheduler::BeginCommand() {
	EXIT_IF(!m_command.IsInvalid());
	m_command.m_buffer = m_command_pool.Commit();
	m_command.Begin();
	BeginTimestamp();
	if (GpuTimeProfiler::Enabled()) {
		m_gpu_time.Begin(m_command.Handle(), CurrentTick());
	}
	return m_command;
}

uint64_t CommandScheduler::Submit(SubmitInfo submit) {
	EXIT_IF(m_command.IsInvalid());
	EXIT_IF(submit.num_wait_semaphores > SubmitInfo::MaxSemaphores ||
	        submit.num_signal_semaphores >= SubmitInfo::MaxSemaphores);
	const auto submit_t0 = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;

	// Guest -> staging copies queued by the buffer/texture caches (AsyncMemcpy) must land before
	// the GPU reads the staging ring: the queue waits for the copy semaphore to reach the number
	// of chunks queued so far (the pool signals it from a copy thread), or - with
	// KYTY_ASYNC_COPY_GPU_WAIT=0 - this thread blocks until they are done.
	if (submit.present) {
		// VUID-vkQueuePresentKHR-pWaitSemaphores-03268: finish host signals before
		// submitting the binary present signal. WaitAll includes the copy callbacks,
		// not just memcpy completion. This resolves earlier submits on the same queue
		// too, without waiting for their GPU work. The render mutex prevents new copies.
		Common::WaitAsyncCopies();
		if (submit_t0 != 0) {
			const auto ns = Common::FrameStats::NowNs() - submit_t0;
			Common::FrameStats::Add(Common::FrameStats::Counter::AsyncCopyWaitNs, ns);
		}
	} else if (Common::PendingAsyncCopies() != 0) {
		namespace FS = Common::FrameStats;
		if (m_copy_gpu_wait) {
			const auto sequence = Common::AsyncCopySequence();
			const bool complete = Common::RequestAsyncCopySignal(sequence);
			static const bool present_trace = std::getenv("KYTY_PRESENT_TRACE") != nullptr;
			if (present_trace && !complete) {
				LOGF("PresentTrace: copywait t=%llu scheduler=%p tick=%llu seq=%llu completed=%llu binary=%u\n",
				     (unsigned long long)FS::NowNs(), (void*)this, (unsigned long long)CurrentTick(),
				     (unsigned long long)sequence, (unsigned long long)Common::AsyncCopyCompleted(),
				     submit.num_signal_semaphores);
			}
			if (!complete) {
				submit.AddWait(m_copy_semaphore, sequence, vk::PipelineStageFlagBits::eAllCommands);
				FS::Add(FS::Counter::AsyncCopyGpuWaits, 1);
			}
			static const bool trace = std::getenv("KYTY_ACOPY_TRACE") != nullptr;
			if (trace) {
				uint64_t   value  = 0;
				const auto result = m_graphics.device.getSemaphoreCounterValue(m_copy_semaphore, &value);
				std::fprintf(stderr, "AcopyTrace: submit seq=%llu completed=%llu sem=%llu wait=%d (%d)\n",
				             static_cast<unsigned long long>(sequence),
				             static_cast<unsigned long long>(Common::AsyncCopyCompleted()),
				             static_cast<unsigned long long>(value), complete ? 0 : 1,
				             static_cast<int>(result));
			}
		} else {
			Common::WaitAsyncCopies();
			if (submit_t0 != 0) {
				FS::Add(FS::Counter::AsyncCopyWaitNs, FS::NowNs() - submit_t0);
				FS::Add(FS::Counter::AsyncCopyWaits, 1);
			}
		}
	}

	EndTimestamp();
	m_command.End();
	const auto buffer   = m_command.m_buffer;
	auto&      graphics = m_graphics;
	EXIT_IF(graphics.queue == nullptr);

	vk::Result result;
	uint64_t   tick;
	{
		Common::LockGuard lock(graphics.queue_mutex);
		tick = m_master.NextTick();
		submit.AddSignal(m_master.Handle(), tick);

		vk::TimelineSemaphoreSubmitInfo timeline_info {};
		timeline_info.waitSemaphoreValueCount   = submit.num_wait_semaphores;
		timeline_info.pWaitSemaphoreValues      = submit.wait_ticks.data();
		timeline_info.signalSemaphoreValueCount = submit.num_signal_semaphores;
		timeline_info.pSignalSemaphoreValues    = submit.signal_ticks.data();

		vk::SubmitInfo submit_info {};
		submit_info.pNext                = &timeline_info;
		submit_info.waitSemaphoreCount   = submit.num_wait_semaphores;
		submit_info.pWaitSemaphores      = submit.wait_semaphores.data();
		submit_info.pWaitDstStageMask    = submit.wait_stages.data();
		submit_info.commandBufferCount   = 1;
		submit_info.pCommandBuffers      = &buffer;
		submit_info.signalSemaphoreCount = submit.num_signal_semaphores;
		submit_info.pSignalSemaphores    = submit.signal_semaphores.data();

		result = graphics.queue.submit(1, &submit_info, nullptr);
	}

	if (result != vk::Result::eSuccess) {
		ReportVulkanFatal(graphics, "vkQueueSubmit", result, tick, m_command.m_debug_op,
		                  m_command.m_debug_submit_id, m_command.m_debug_arg0,
		                  m_command.m_debug_arg1, m_command.m_debug_arg2, m_command.m_debug_arg3,
		                  m_command.m_debug_arg4);
	}
	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);

	// Debug aid: KYTY_SYNC_SUBMIT=1 drains the queue after every submit so a device loss is
	// reported on the submit that caused it, together with its debug ids.
	static const bool sync_submit = std::getenv("KYTY_SYNC_SUBMIT") != nullptr;
	if (sync_submit) {
		const auto idle = graphics.queue.waitIdle();
		if (idle != vk::Result::eSuccess) {
			ReportVulkanFatal(graphics, "vkQueueWaitIdle(sync)", idle, tick, m_command.m_debug_op,
			                  m_command.m_debug_submit_id, m_command.m_debug_arg0,
			                  m_command.m_debug_arg1, m_command.m_debug_arg2,
			                  m_command.m_debug_arg3, m_command.m_debug_arg4);
		}
		EXIT_NOT_IMPLEMENTED(idle != vk::Result::eSuccess);
	}

	if (m_timestamp_slot >= 0) {
		std::lock_guard lock(m_timestamp_mutex);
		m_timestamp_pending.emplace_back(tick, static_cast<uint32_t>(m_timestamp_slot));
		m_timestamp_slot = -1;
	}
	HarvestTimestamps();
	if (GpuTimeProfiler::Enabled()) {
		m_gpu_time.Harvest();
	}
	m_last_submit_ns = Common::FrameStats::NowNs();
	if (submit_t0 != 0) {
		namespace FS  = Common::FrameStats;
		const auto ns = FS::NowNs() - submit_t0;
		FS::Add(FS::Counter::SubmitNs, ns);
		FS::Add(FS::Counter::Submits, 1);
		FS::AddSite(FS::Table::SubmitSites, FS::CurrentSite(), ns);
	}

	m_command.m_buffer = nullptr;
	return tick;
}

void CommandScheduler::InitTimestamps() {
	if (!Common::FrameStats::Enabled()) {
		return;
	}
	const auto& limits = m_graphics.physical_device_properties.limits;
	if (limits.timestampPeriod <= 0.0f) {
		return;
	}
	uint32_t count = 0;
	m_graphics.physical_device.getQueueFamilyProperties(&count, nullptr);
	std::vector<vk::QueueFamilyProperties> families(count);
	m_graphics.physical_device.getQueueFamilyProperties(&count, families.data());
	if (m_graphics.queue_family >= count ||
	    families[m_graphics.queue_family].timestampValidBits == 0) {
		LOGF("FrameTrace: queue family has no timestamp support, GPU time not measured" "\n");
		return;
	}
	vk::QueryPoolCreateInfo info {};
	info.sType      = vk::StructureType::eQueryPoolCreateInfo;
	info.queryType  = vk::QueryType::eTimestamp;
	info.queryCount = TimestampSlots * 2;
	if (m_graphics.device.createQueryPool(&info, nullptr, &m_timestamp_pool) !=
	    vk::Result::eSuccess) {
		m_timestamp_pool = nullptr;
		return;
	}
	m_timestamp_period_ns = static_cast<double>(limits.timestampPeriod);
	m_timestamp_bits      = families[m_graphics.queue_family].timestampValidBits;
}

void CommandScheduler::BeginTimestamp() {
	m_timestamp_slot = -1;
	if (m_timestamp_pool == nullptr || m_command.IsInvalid()) {
		return;
	}
	std::lock_guard lock(m_timestamp_mutex);
	// Slots are handed out round-robin and harvested in order, so with fewer than TimestampSlots
	// pending the next slot cannot still be in flight.
	if (m_timestamp_pending.size() >= TimestampSlots) {
		return;
	}
	const auto slot  = m_timestamp_next;
	m_timestamp_next = (m_timestamp_next + 1) % TimestampSlots;
	auto cmd         = m_command.Handle();
	cmd.resetQueryPool(m_timestamp_pool, slot * 2, 2);
	cmd.writeTimestamp(vk::PipelineStageFlagBits::eTopOfPipe, m_timestamp_pool, slot * 2);
	m_timestamp_slot = slot;
}

void CommandScheduler::EndTimestamp() {
	if (m_timestamp_slot < 0 || m_command.IsInvalid()) {
		return;
	}
	m_command.Handle().writeTimestamp(vk::PipelineStageFlagBits::eBottomOfPipe, m_timestamp_pool,
	                                  static_cast<uint32_t>(m_timestamp_slot) * 2 + 1);
}

void CommandScheduler::HarvestTimestamps() {
	if (m_timestamp_pool == nullptr) {
		return;
	}
	std::lock_guard lock(m_timestamp_mutex);
	if (m_timestamp_pending.empty()) {
		return;
	}
	if (!m_master.IsFree(m_timestamp_pending.front().first)) {
		m_master.Refresh();
	}
	while (!m_timestamp_pending.empty() && m_master.IsFree(m_timestamp_pending.front().first)) {
		const auto              slot = m_timestamp_pending.front().second;
		std::array<uint64_t, 2> values {};
		const auto              result = m_graphics.device.getQueryPoolResults(
            m_timestamp_pool, slot * 2, 2, sizeof(values), values.data(), sizeof(uint64_t),
            vk::QueryResultFlagBits::e64);
		if (result == vk::Result::eNotReady) {
			break;
		}
		m_timestamp_pending.pop_front();
		if (result != vk::Result::eSuccess) {
			continue;
		}
		uint64_t delta = values[1] - values[0];
		if (m_timestamp_bits < 64) {
			delta &= (uint64_t {1} << m_timestamp_bits) - 1;
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::GpuBusyNs,
		                        static_cast<uint64_t>(static_cast<double>(delta) * m_timestamp_period_ns));
		Common::FrameStats::Add(Common::FrameStats::Counter::GpuMeasured, 1);
	}
}

void CommandScheduler::BeginNext() {
	CheckActive();
	BeginCommand();
}

} // namespace Libs::Graphics
