#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDSCHEDULER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDSCHEDULER_H_

#include "common/common.h"
#include "common/uniqueFunction.h"
#include "graphics/host_gpu/renderer/commandRecorder.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"
#include "graphics/host_gpu/renderer/masterSemaphore.h"
#include "graphics/host_gpu/renderer/render.h"

#include <condition_variable>
#include <deque>
#include <mutex>

#include <memory>
#include <queue>

#include <thread>
#include <vector>

namespace Libs::Graphics {

// Blocks until every command buffer of every scheduler has been recorded (gate "recordthread")
// and handed to vkQueueSubmit (gate "asyncsubmit"). Call it before using the queue in a way that
// depends on all work queued so far (waitIdle, capture boundaries, a present submit, shutdown),
// and never while holding graphics.queue_mutex.
void DrainAsyncSubmits();
// Hands a command buffer the record thread has just ended to the submit thread. The tick was
// reserved by CommandScheduler::Submit on the resolving thread and its signal is already part of
// request.submit; the FIFO order is the order that thread published the ends in.
void EnqueueAsyncSubmit(const RecordSubmit& request, vk::CommandBuffer buffer);
// Submits queued for the submit thread and not yet handed to vkQueueSubmit (diagnostics).
[[nodiscard]] size_t AsyncSubmitBacklog();

class CommandScheduler {
public:
	CommandScheduler(RenderContext& context, GraphicContext& graphics);
	~CommandScheduler();
	KYTY_CLASS_NO_COPY(CommandScheduler);

	void           Begin(HW::Context& registers, HW::UserConfig& user_config, HW::Shader& shaders);
	void           BeginRendering(const RenderState& state);
	void           EndRendering(RenderPassEnd why = RenderPassEnd::Other);
	void           Flush();
	void           Flush(SubmitInfo& submit);
	void           FlushAndWait();
	void           Finish();
	CommandBuffer& BeginCommand();
	// allow_async = false: the caller waits for this submit right away, so it is made on this
	// thread (after the queued ones) instead of through the submit thread.
	uint64_t       Submit(SubmitInfo submit = {}, bool allow_async = true);
	// Deferred callbacks can observe an externally owned drain, but cannot initiate shutdown:
	// the priority runner cannot join itself.
	void                      Shutdown();
	void                      Wait(uint64_t tick);
	void                      PopPendingOperations();
	// Draw/dispatch variant: runs the completed callbacks with the known GPU tick and queries the
	// semaphore at most every 200 us (a vkGetSemaphoreCounterValue per draw cost 0.6 ms/frame).
	void                      PopPendingOperationsLazy();
	void                      PopPendingOperations(bool refresh_gpu_tick);
	void                      DrainPriorityOperations();
	void                      WaitPriorityOperations(uint64_t tick);
	void                      DeferOperation(Common::UniqueFunction<void>&& operation);
	void                      DeferPriorityOperation(Common::UniqueFunction<void>&& operation);
	[[nodiscard]] static bool InDeferredOperation() noexcept;

	[[nodiscard]] bool Active() const noexcept { return m_command.m_registers != nullptr; }
	void                           CheckActive() const;
	CommandBuffer&                 Current();
	[[nodiscard]] uint64_t         CurrentTick() const noexcept { return m_master.CurrentTick(); }
	[[nodiscard]] bool             IsFree(uint64_t tick);
	[[nodiscard]] MasterSemaphore& GetMasterSemaphore() noexcept { return m_master; }
	[[nodiscard]] RenderContext&   Context() const noexcept { return m_context; }
	[[nodiscard]] GraphicContext&  Graphics() const noexcept { return m_graphics; }
	// Host time (FrameStats::NowNs) of the last vkQueueSubmit; used to coalesce EOP flushes.
	[[nodiscard]] uint64_t LastSubmitNs() const noexcept { return m_last_submit_ns; }
	// KYTY_GPU_TIME=1 (gpuTimeProfiler.h): charge the GPU time up to this point of the current
	// command buffer to (kind, key, key2).
	void EnableGpuTime() { m_gpu_time.Enable(); }
	void GpuMark(GpuTimeProfiler::Kind kind, uint64_t key, uint64_t key2 = 0) {
		if (GpuTimeProfiler::Enabled() && !m_command.IsInvalid()) {
			GpuMarkSlow(kind, key, key2);
		}
	}

private:
	class CommandPool {
	public:
		CommandPool(GraphicContext& graphics, MasterSemaphore& master);
		~CommandPool();
		KYTY_CLASS_NO_COPY(CommandPool);

		vk::CommandBuffer Commit();
		// Stamped with the tick the buffer will signal. The record thread passes the tick the
		// resolving thread saw when it began the buffer, not the one current by then.
		vk::CommandBuffer Commit(uint64_t tick);

	private:
		static constexpr size_t GrowStep = 4;

		size_t Grow();

		GraphicContext&                m_graphics;
		MasterSemaphore&               m_master;
		vk::CommandPool                m_pool = nullptr;
		std::vector<vk::CommandBuffer> m_buffers;
		std::vector<uint64_t>          m_ticks;
		size_t                         m_hint = 0;
	};

	enum class OperationState { Open, Draining, Closed };

	struct PendingOperation {
		Common::UniqueFunction<void> callback;
		uint64_t                     tick = 0;
		const void*                  site = nullptr; // DeferOperation caller (FrameTrace-pops)
	};

	// Gate "recordthread": the record thread of this scheduler, created on first use, and the
	// pool hook it records through (the pool belongs to that thread while it runs).
	[[nodiscard]] CommandRecorder* Recorder();
	static vk::CommandBuffer       CommitPoolBuffer(void* user, uint64_t tick);
	void                           GpuMarkSlow(GpuTimeProfiler::Kind kind, uint64_t key,
	                                           uint64_t key2);
	void BeginNext();
	void PriorityOperationsThread(std::stop_token stop);
	void RunOperation(Common::UniqueFunction<void>&& operation);
	// KYTY_FRAME_TRACE: GPU execution time of every command buffer through timestamp queries
	// (top-of-pipe after begin, bottom-of-pipe before end), harvested once the master semaphore
	// shows the batch complete and summed into FrameStats::GpuBusyNs.
	void InitTimestamps();
	void BeginTimestamp();
	void EndTimestamp();
	void HarvestTimestamps();

	MasterSemaphore              m_master;
	RenderContext&               m_context;
	GraphicContext&              m_graphics;
	CommandPool                  m_command_pool;
	CommandBuffer                m_command;
	std::queue<PendingOperation> m_pending_operations;
	std::queue<PendingOperation> m_priority_operations;
	std::mutex                   m_operation_mutex;
	std::condition_variable      m_operation_available;
	std::jthread                 m_priority_thread;
	bool                         m_priority_active      = false;
	uint64_t                     m_priority_active_tick = 0;
	uint64_t                     m_last_tick_refresh_ns = 0;
	OperationState               m_operation_state      = OperationState::Open;
	static constexpr uint32_t                 TimestampSlots        = 4096;
	vk::QueryPool                             m_timestamp_pool      = nullptr;
	// Timeline semaphore signalled from the copy pool (host) with the async-copy completed mark;
	// submits that reference staging filled by AsyncMemcpy wait for it on the GPU.
	static void SignalCopySemaphore(uint64_t completed, void* user);
	vk::Semaphore                             m_copy_semaphore      = nullptr;
	bool                                      m_copy_gpu_wait       = false;
	double                                    m_timestamp_period_ns = 0.0;
	uint32_t                                  m_timestamp_bits      = 64;
	uint32_t                                  m_timestamp_next      = 0;
	int64_t                                   m_timestamp_slot      = -1;
	std::deque<std::pair<uint64_t, uint32_t>> m_timestamp_pending;
	std::mutex                                m_timestamp_mutex;
	uint64_t                                  m_last_submit_ns = 0;
	GpuTimeProfiler                           m_gpu_time;
	// Declared last: its destructor stops the record thread before anything it points at dies.
	std::unique_ptr<CommandRecorder>          m_recorder;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDSCHEDULER_H_
