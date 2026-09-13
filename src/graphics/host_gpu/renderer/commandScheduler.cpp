#include "graphics/host_gpu/renderer/commandScheduler.h"

#include <mutex>
#include <string>
#include <map>
#include <cstdlib>

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
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

// One thread that calls vkQueueSubmit for every scheduler, in the order the submits were queued.
class AsyncSubmitter {
public:
	struct Record {
		GraphicContext*   graphics  = nullptr;
		const void*       scheduler = nullptr;
		vk::Semaphore     master    = nullptr;
		vk::CommandBuffer buffer    = nullptr;
		SubmitInfo        submit;
		uint64_t          tick         = 0;
		uint32_t          debug_op     = 0;
		uint64_t          debug_submit = 0;
		uint32_t          arg0 = 0, arg1 = 0, arg2 = 0, arg3 = 0;
		uint64_t          arg4 = 0;
	};

	static AsyncSubmitter& Get() {
		// Leaked on purpose: schedulers may submit until the process exits.
		static auto* submitter = new AsyncSubmitter;
		return *submitter;
	}

	// Takes the tick of `master` and queues the submit under one lock, so ticks reach the queue in
	// order. Returns the tick.
	uint64_t Enqueue(Record record, MasterSemaphore& master) {
		uint64_t tick = 0;
		{
			std::lock_guard lock(m_mutex);
			if (!m_thread.joinable()) {
				m_thread = std::thread([this] { Loop(); });
			}
			tick = master.NextTick();
			record.tick = tick;
			record.submit.AddSignal(master.Handle(), tick);
			m_queue.push_back(std::move(record));
			m_enqueued++;
		}
		m_available.notify_one();
		Common::FrameStats::Add(Common::FrameStats::Counter::AsyncSubmits, 1);
		return tick;
	}

	// Waits for the submits queued before this call (later ones may still be queued).
	[[nodiscard]] size_t Backlog() {
		std::lock_guard lock(m_mutex);
		return static_cast<size_t>(m_enqueued - m_submitted);
	}

	// The tick is already reserved and signalled by record.submit (gate "recordthread").
	void EnqueueReserved(Record record) {
		{
			std::lock_guard lock(m_mutex);
			if (!m_thread.joinable()) {
				m_thread = std::thread([this] { Loop(); });
			}
			m_queue.push_back(std::move(record));
			m_enqueued++;
		}
		m_available.notify_one();
		Common::FrameStats::Add(Common::FrameStats::Counter::AsyncSubmits, 1);
	}

	void Drain() {
		std::unique_lock lock(m_mutex);
		const auto target = m_enqueued;
		if (m_submitted >= target) {
			return;
		}
		EXIT_IF(std::this_thread::get_id() == m_thread.get_id());
		const auto t0 = Common::FrameStats::NowNs();
		m_drained.wait(lock, [this, target] { return m_submitted >= target; });
		Common::FrameStats::Add(Common::FrameStats::Counter::AsyncSubmitDrains, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::AsyncSubmitDrainNs,
		                        Common::FrameStats::NowNs() - t0);
	}

private:
	void Loop() {
		for (;;) {
			Record record;
			{
				std::unique_lock lock(m_mutex);
				m_available.wait(lock, [this] { return !m_queue.empty(); });
				record = std::move(m_queue.front());
				m_queue.pop_front();
				m_busy = true;
			}
			const auto t0       = Common::FrameStats::NowNs();
			auto&      graphics = *record.graphics;
			vk::Result result;
			uint64_t   locked_ns = 0;
			{
				Common::LockGuard lock(graphics.queue_mutex);
				locked_ns    = Common::FrameStats::NowNs();
				auto& submit = record.submit;

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
				submit_info.pCommandBuffers      = &record.buffer;
				submit_info.signalSemaphoreCount = submit.num_signal_semaphores;
				submit_info.pSignalSemaphores    = submit.signal_semaphores.data();

				RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, false,
				                    vk::Result::eNotReady);
				result = graphics.queue.submit(1, &submit_info, nullptr);
				RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, true, result);
			}
			if (result != vk::Result::eSuccess) {
				ReportVulkanFatal(graphics, "vkQueueSubmit(async)", result, record.tick, record.debug_op,
				                  record.debug_submit, record.arg0, record.arg1, record.arg2, record.arg3,
				                  record.arg4);
			}
			EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
			Common::FrameStats::Add(Common::FrameStats::Counter::AsyncSubmitLockNs, locked_ns - t0);
			Common::FrameStats::Add(Common::FrameStats::Counter::AsyncSubmitNs,
			                        Common::FrameStats::NowNs() - locked_ns);
			{
				std::lock_guard lock(m_mutex);
				m_busy = false;
				m_submitted++;
			}
			m_drained.notify_all();
		}
	}

	std::mutex              m_mutex;
	std::condition_variable m_available;
	std::condition_variable m_drained;
	std::deque<Record>      m_queue;
	bool                    m_busy      = false;
	uint64_t                m_enqueued  = 0;
	uint64_t                m_submitted = 0;
	std::thread             m_thread;
};

} // namespace

void DrainAsyncSubmits() {
	// Commands that are not written yet are queued work too: the presenter submits on its own
	// scheduler from a buffer the GuestGpu thread filled, so the record queues go first.
	DrainRecordQueues();
	AsyncSubmitter::Get().Drain();
}

void EnqueueAsyncSubmit(const RecordSubmit& request, vk::CommandBuffer buffer) {
	EXIT_IF(request.graphics == nullptr || buffer == nullptr);
	AsyncSubmitter::Record record;
	record.graphics     = request.graphics;
	record.scheduler    = request.scheduler;
	record.master       = request.master;
	record.buffer       = buffer;
	record.submit       = request.submit;
	record.tick         = request.tick;
	record.debug_op     = request.debug_op;
	record.debug_submit = request.debug_submit;
	record.arg0         = request.arg0;
	record.arg1         = request.arg1;
	record.arg2         = request.arg2;
	record.arg3         = request.arg3;
	record.arg4         = request.arg4;
	AsyncSubmitter::Get().EnqueueReserved(std::move(record));
}

size_t AsyncSubmitBacklog() {
	return AsyncSubmitter::Get().Backlog();
}

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
	return Commit(m_master.CurrentTick());
}

vk::CommandBuffer CommandScheduler::CommandPool::Commit(uint64_t tick) {
	auto       gpu_tick = m_master.KnownGpuTick();
	const auto search   = [this, &gpu_tick, tick](size_t begin, size_t end) -> std::optional<size_t> {
		for (size_t index = begin; index < end; ++index) {
			if (gpu_tick >= m_ticks[index]) {
				m_ticks[index] = tick;
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
		m_ticks[*found] = tick;
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
	DrainAsyncSubmits();
	m_master.Wait(CurrentTick() - 1);
	PopPendingOperations();
	DrainPriorityOperations();
	m_priority_thread.request_stop();
	m_operation_available.notify_all();
	if (m_priority_thread.joinable()) {
		m_priority_thread.join();
	}
	// Nothing records after this point: stop the record thread while the pool, the profiler and
	// the command buffer it points at are all still alive.
	m_command.m_recorder = nullptr;
	m_recorder.reset();
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

void CommandScheduler::EndRendering(RenderPassEnd why) {
	if (Active() && !m_command.IsInvalid()) {
		Current().EndRendering(why);
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
	const auto tick = Submit({}, false);
	m_master.Wait(tick);
	BeginNext();
}

void CommandScheduler::Finish() {
	CheckActive();
	if (!m_command.IsInvalid()) {
		Submit({}, false);
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
		const auto submitted_tick = Submit({}, false);
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

CommandRecorder* CommandScheduler::Recorder() {
	if (m_recorder == nullptr) {
		m_recorder = std::make_unique<CommandRecorder>(&CommandScheduler::CommitPoolBuffer, this,
		                                              &m_command.m_buffer, m_graphics.device);
	}
	return m_recorder.get();
}

vk::CommandBuffer CommandScheduler::CommitPoolBuffer(void* user, uint64_t tick) {
	EXIT_IF(user == nullptr);
	return static_cast<CommandScheduler*>(user)->m_command_pool.Commit(tick);
}

void CommandScheduler::GpuMarkSlow(GpuTimeProfiler::Kind kind, uint64_t key, uint64_t key2) {
	// Always on this thread, through Handle(), which drains the record thread first. A GPU-time
	// mark lands in the middle of a command buffer, and every caller of GpuMark is holding a
	// vk::CommandBuffer it took from Handle() earlier in the same draw or dispatch
	// (renderDraw.cpp:1622, renderCompute.cpp:754) and keeps recording into it right after the
	// mark. Publishing the mark instead put the record thread inside the same VkCommandBuffer at
	// the same time: an external-synchronization violation that corrupts the driver's command
	// pool and kills the process inside nvoglv64.
	m_gpu_time.Mark(m_command.Handle(), CurrentTick(), kind, key, key2);
}

CommandBuffer& CommandScheduler::BeginCommand() {
	EXIT_IF(!m_command.IsInvalid());
	// The choice is made once per native command buffer, so the dynamic-state cache and the
	// global-barrier mark keep belonging to exactly one recording.
	auto* wanted = RecordThreadWanted(m_graphics) ? Recorder() : nullptr;
	if (wanted == nullptr && m_recorder != nullptr) {
		// The gate went off while a buffer was queued: the record thread owns the command pool
		// until its queue is empty, and the direct path below takes a buffer from it.
		m_recorder->Drain();
	}
	if ((wanted != nullptr) != m_record_thread_on) {
		// Gate "recordthread" moves only here, at a buffer boundary; switching off drained above.
		m_record_thread_on = wanted != nullptr;
		LOGF("RecordThread: scheduler=%p record thread %s from tick %llu\n", static_cast<void*>(this),
		     m_record_thread_on ? "on" : "off", static_cast<unsigned long long>(CurrentTick()));
	}
	m_command.m_recorder = wanted;
	m_command.m_active   = true;
	if (m_command.m_recorder != nullptr) {
		// CurrentTick() is the tick this buffer will signal: the same value the direct path
		// stamps the pooled buffer with.
		m_command.BeginRecorded(CurrentTick());
	} else {
		m_command.m_buffer = m_command_pool.Commit();
		m_command.Begin();
	}
	BeginTimestamp();
	if (GpuTimeProfiler::Enabled()) {
		// Same rule as GpuMarkSlow. Handle() drains, so the record thread has already taken the
		// buffer from the pool and begun it by the time the chunk reset is recorded here, and the
		// order is the one the direct path produces: vkBeginCommandBuffer, the frame-trace
		// top-of-pipe timestamp, then the GPU-time chunk.
		m_gpu_time.Begin(m_command.Handle(), CurrentTick());
	}
	return m_command;
}

uint64_t CommandScheduler::Submit(SubmitInfo submit, bool allow_async) {
	EXIT_IF(m_command.IsInvalid());
	EXIT_IF(submit.num_wait_semaphores > SubmitInfo::MaxSemaphores ||
	        submit.num_signal_semaphores >= SubmitInfo::MaxSemaphores);
	const auto submit_t0 = Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
	// Semaphores the caller brought (WSI) are observed outside the scheduler's timeline: such a
	// submit is made synchronously.
	const bool caller_semaphores = submit.num_wait_semaphores != 0 || submit.num_signal_semaphores != 0;

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
	auto& graphics = m_graphics;
	EXIT_IF(graphics.queue == nullptr);

	static const bool sync_submit = std::getenv("KYTY_SYNC_SUBMIT") != nullptr;
	uint64_t          tick        = 0;
	const bool        async = allow_async && !sync_submit && !submit.present && !caller_semaphores &&
	                          Common::Gates::Enabled(Common::Gates::Gate::AsyncSubmit);
	auto* recorder = m_command.m_recorder;
	if (recorder != nullptr) {
		// Gate "recordthread": the record thread ends the buffer and, for an asynchronous submit,
		// queues it. The tick is reserved here, on this thread, because CurrentTick() has to keep
		// naming the command buffer being filled - the stream-buffer watches, the descriptor
		// pools, the sanitiser slots and the deferred operations stamp their ownership with it.
		RecordSubmit request;
		request.async = async;
		if (async) {
			tick = m_master.NextTick();
			submit.AddSignal(m_master.Handle(), tick);
			request.graphics     = &graphics;
			request.scheduler    = this;
			request.master       = m_master.Handle();
			request.submit       = submit;
			request.tick         = tick;
			request.debug_op     = m_command.m_debug_op;
			request.debug_submit = m_command.m_debug_submit_id;
			request.arg0         = m_command.m_debug_arg0;
			request.arg1         = m_command.m_debug_arg1;
			request.arg2         = m_command.m_debug_arg2;
			request.arg3         = m_command.m_debug_arg3;
			request.arg4         = m_command.m_debug_arg4;
		}
		m_command.EndRecorded(request);
	} else {
		m_command.End();
	}
	if (async) {
		if (recorder == nullptr) {
			AsyncSubmitter::Record record;
			record.graphics     = &graphics;
			record.scheduler    = this;
			record.master       = m_master.Handle();
			record.buffer       = m_command.m_buffer;
			record.submit       = submit;
			record.debug_op     = m_command.m_debug_op;
			record.debug_submit = m_command.m_debug_submit_id;
			record.arg0         = m_command.m_debug_arg0;
			record.arg1         = m_command.m_debug_arg1;
			record.arg2         = m_command.m_debug_arg2;
			record.arg3         = m_command.m_debug_arg3;
			record.arg4         = m_command.m_debug_arg4;
			tick                = AsyncSubmitter::Get().Enqueue(std::move(record), m_master);
			m_command.m_buffer  = nullptr;
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
		m_command.m_active = false;
		return tick;
	}
	// Synchronous: everything queued before goes first, including commands no record thread has
	// written yet. After it the handle belongs to this thread again.
	DrainAsyncSubmits();
	const auto buffer = m_command.m_buffer;
	EXIT_IF(buffer == nullptr);
	if (submit.present) {
		// A submit drained ahead of this one may have queued a copy since the wait above; the
		// binary present signal must not depend on a host signal still to come.
		Common::WaitAsyncCopies();
	}

	vk::Result result;
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

		RecordGpuSubmission(this, m_master.Handle(), tick, submit, false, vk::Result::eNotReady);
		result = graphics.queue.submit(1, &submit_info, nullptr);
		RecordGpuSubmission(this, m_master.Handle(), tick, submit, true, result);
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
	m_command.m_active = false;
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
	if (m_command.m_recorder != nullptr) {
		m_command.m_recorder->PushTimestamp(m_timestamp_pool, slot * 2, 2, false);
	} else {
		auto cmd = m_command.Handle();
		cmd.resetQueryPool(m_timestamp_pool, slot * 2, 2);
		cmd.writeTimestamp(vk::PipelineStageFlagBits::eTopOfPipe, m_timestamp_pool, slot * 2);
	}
	m_timestamp_slot = slot;
}

void CommandScheduler::EndTimestamp() {
	if (m_timestamp_slot < 0 || m_command.IsInvalid()) {
		return;
	}
	if (m_command.m_recorder != nullptr) {
		m_command.m_recorder->PushTimestamp(
		    m_timestamp_pool, static_cast<uint32_t>(m_timestamp_slot) * 2 + 1, 0, true);
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
