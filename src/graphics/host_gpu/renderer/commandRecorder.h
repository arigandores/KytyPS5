#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDRECORDER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDRECORDER_H_

#include "common/common.h"
#include "common/uniqueFunction.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <mutex>
#include <thread>
#include <type_traits>

namespace Libs::Graphics {

struct GraphicContext;

// M3 (docs/parallel-draw-path.md): the thread that resolves PM4 stops calling vkCmd* itself and
// publishes POD records of "what to record" into a ring arena; one record thread per scheduler
// consumes them in publication order and records into one primary command buffer.
//
// Step 0 moves only the lifetime of the native buffer (the pool, vkBeginCommandBuffer,
// vkEndCommandBuffer, the hand-off to the submit thread) and the timestamps. Every other site
// still records on the resolving thread: CommandBuffer::Handle() drains this queue first and then
// writes into the same buffer, so the order of commands is exactly the order it is today and
// sites can be moved one at a time.
//
// The producer is the single thread that owns the scheduler (GuestGpu for the renderer, the
// presentation thread for the swapchain); the consumer is the record thread. Head and tail are
// monotonic byte offsets into a power-of-two ring, so a drain is "tail >= the head at the time of
// the call" and the release/acquire pair on the tail also publishes everything the record thread
// wrote outside the arena (the native buffer handle).
enum class RecordOp : uint16_t {
	Pad = 0,     // filler up to the end of the ring; no work
	BeginBuffer, // take the next free buffer from the scheduler's pool and begin it
	EndBuffer,   // end it and, for an asynchronous submit, hand it to the submit thread
	Timestamp,   // query-pool timestamps (KYTY_FRAME_TRACE) and GpuTimeProfiler marks
	Generic,     // an arbitrary recording callback, for the rare sites
};

struct alignas(16) RecordHeader {
	uint32_t size; // header + payload, a multiple of the record alignment
	uint16_t op;
	uint16_t reserved;
};
static_assert(sizeof(RecordHeader) == 16);

// What CommandScheduler::Submit decided before it handed the buffer to the record thread. The
// tick is already reserved and its signal is already part of `submit`.
struct RecordSubmit {
	GraphicContext* graphics     = nullptr;
	const void*     scheduler    = nullptr;
	vk::Semaphore   master       = nullptr;
	SubmitInfo      submit;
	uint64_t        tick         = 0;
	uint64_t        debug_submit = 0;
	uint64_t        arg4         = 0;
	uint32_t        debug_op     = 0;
	uint32_t        arg0         = 0;
	uint32_t        arg1         = 0;
	uint32_t        arg2         = 0;
	uint32_t        arg3         = 0;
	// false: the caller submits this buffer itself right after draining the queue.
	bool            async        = false;
};
static_assert(std::is_trivially_copyable_v<RecordSubmit>);

class CommandRecorder final {
public:
	// commit: takes the next native command buffer of the scheduler's pool whose previous
	// submission has completed. Called on the record thread, which owns the pool while it runs.
	// current: where the handle of the buffer being recorded is published; the resolving thread
	// may read it once Drain() has returned.
	using CommitFn = vk::CommandBuffer (*)(void* user, uint64_t tick);

	CommandRecorder(CommitFn commit, void* user, vk::CommandBuffer* current,
	                GpuTimeProfiler* gpu_time);
	~CommandRecorder();
	KYTY_CLASS_NO_COPY(CommandRecorder);

	// tick: the tick this buffer will signal, for the pool's reuse bookkeeping.
	void PushBeginBuffer(uint64_t tick);
	void PushEndBuffer(const RecordSubmit& request);
	// reset != 0: vkCmdResetQueryPool(pool, query, reset) before the write (outside a pass only).
	void PushTimestamp(vk::QueryPool pool, uint32_t query, uint32_t reset, bool bottom);
	// begin: GpuTimeProfiler::Begin, otherwise ::Mark.
	void PushGpuTime(uint64_t tick, bool begin, GpuTimeProfiler::Kind kind, uint64_t key,
	                 uint64_t key2);
	void PushGeneric(Common::UniqueFunction<void, vk::CommandBuffer>&& command);

	// Waits until everything published before this call has been recorded. Never call it from the
	// record thread.
	void Drain();
	// Bytes published and not recorded yet (diagnostics).
	[[nodiscard]] size_t Backlog() const noexcept;

private:
	static constexpr uint32_t RecordAlign = 16;

	void     Loop();
	void     Stop();
	uint8_t* Reserve(uint32_t bytes);
	void     Publish(uint32_t bytes);
	void     PushRecord(RecordOp op, const void* payload, uint32_t payload_size);
	void     Execute(const RecordHeader& header, const uint8_t* payload);
	void     WakeConsumer();
	void     WakeWaiters();

	CommitFn           m_commit  = nullptr;
	void*              m_user    = nullptr;
	vk::CommandBuffer* m_current = nullptr;
	GpuTimeProfiler*   m_gpu_time = nullptr;
	vk::CommandBuffer  m_buffer   = nullptr; // record thread only

	std::unique_ptr<uint8_t[]> m_data;
	uint64_t                   m_capacity = 0;
	uint64_t                   m_mask     = 0;

	alignas(64) std::atomic<uint64_t> m_head {0}; // published bytes (producer)
	alignas(64) std::atomic<uint64_t> m_tail {0}; // recorded bytes (consumer)
	alignas(64) std::mutex            m_mutex;
	std::condition_variable           m_progress; // tail advanced: space and drains
	std::condition_variable           m_pending;  // head advanced: work for the consumer
	std::atomic<uint32_t>             m_waiters {0};
	std::atomic<bool>                 m_consumer_waiting {false};
	std::atomic<bool>                 m_stop {false};
	std::thread                       m_thread;
};

// Waits for every recorder in the process; part of DrainAsyncSubmits().
void DrainRecordQueues();
// Bytes published and not recorded yet across every recorder (diagnostics).
[[nodiscard]] size_t RecordBacklog();
// Gate "recordthread", plus the cases the record thread has to stay out of: the breadcrumb and
// checkpoint modes record their own commands from CommandBuffer::SetDebugInfo and exist to name
// the last command before a hang, and a RenderDoc capture must see the frame recorded the way the
// thread that resolved it wrote it.
[[nodiscard]] bool RecordThreadWanted(const GraphicContext& graphics);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDRECORDER_H_
