#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICSRUN_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICSRUN_H_

#include "common/abi.h"
#include "common/common.h"
#include "common/threads.h"
#include "common/uniqueFunction.h"
#include "graphics/guest_gpu/command_processor/commandProcessor.h"

#include <array>
#include <atomic>
#include <cstdint>
#include <deque>
#include <memory>
#include <mutex>
#include <span>
#include <thread>

namespace Libs::Graphics {

class RenderContext;

class GuestGpu final {
public:
	explicit GuestGpu(RenderContext& renderer);
	~GuestGpu();
	KYTY_CLASS_NO_COPY(GuestGpu);

	void               Shutdown();
	[[nodiscard]] bool IsStopping();
	void               SendCommand(Common::UniqueFunction<void>&& command);
	void               SendCommandSync(Common::UniqueFunction<void>&& command);

	// Submitted command memory is borrowed and must remain valid until GPU execution completes.
	void              Submit(std::span<const uint32_t> draw_commands,
	                         std::span<const uint32_t> constant_commands);
	void              SubmitCompute(uint32_t queue, std::span<const uint32_t> commands);
	void              SubmitFlipPreparation(uint64_t request_id);
	void              Done();
	[[nodiscard]] int GetFrameNum() const;

	[[nodiscard]] static bool IsGpuThread() noexcept;

	// Session 98 (patch_s98a): called by CommandProcessor at every GPU flip packet it processes
	// on this thread (descriptors.h, BindFloorNoteFlipPacket).
	void BindFloorFlipPacket();

private:
	static constexpr uint32_t ComputePipeCount     = 7;
	static constexpr uint32_t QueuesPerComputePipe = 8;
	static constexpr uint32_t ComputeQueueCount    = ComputePipeCount * QueuesPerComputePipe;
	static constexpr uint32_t ComputeQueueBase     = 0x20;
	static constexpr uint32_t QueueCount           = 1 + ComputeQueueCount;

	enum class SubmissionType { Graphics, Compute, FlipPreparation };

	struct Submission {
		SubmissionType            type     = SubmissionType::Graphics;
		uint32_t                  queue_id = 0;
		std::span<const uint32_t> commands;
		std::span<const uint32_t> constant_commands;
		Pm4Execution              command_execution;
		Pm4Execution              constant_execution;
		bool                      reset_processor   = false;
		bool                      started           = false;
		bool                      command_complete  = false;
		bool                      constant_complete = false;
		bool                      blocked           = false;
		uint64_t                  flip_request_id   = 0;
		uint64_t                  enqueue_ns        = 0;
		// Draw lookahead: id of a graphics submission in submission order (0 otherwise), and
		// whether the walker thread walked it at enqueue (gate "dawalk").
		uint64_t                  walk_id           = 0;
		bool                      walked_ahead      = false;
		// Session 98 (patch_s98a): the bindfloor latch state of this submission; bf.seq is
		// assigned at Enqueue under m_queue_mutex, monotonic over all queues.
		BindFloorSlice            bf;
	};

	void              Enqueue(Submission submission);
	// Session 98, KYTY_BIND_FLOOR_LATCH=1: record a completed submission / adopt a pending value
	// once every older submission is done.  Both under m_queue_mutex.
	void              BindFloorDoneLocked(const BindFloorSlice& slice);
	void              BindFloorResolveLocked();
	// KYTY_ASYNC_COMPUTE=1: shadow-walks the submission for compute dispatches and queues their
	// pipeline compiles; the shadow compute state persists per queue across submissions.
	// Gate "dawalk": hands the submission to the walker thread instead (compute prefetch and
	// draw lookahead both), and marks it walked.
	void              LookaheadSubmission(Submission& submission);
	void              WaitForIdle();
	void              ProcessCommands();
	bool              Process(Submission& submission);
	static void       ThreadRun(void* data);
	CommandProcessor& GetProcessor(uint32_t queue_id);

	RenderContext&                                 m_renderer;
	struct ComputeLookahead {
		HW::ComputeShaderInfo cs;
		bool                  valid = false;
	};
	std::array<ComputeLookahead, QueueCount>       m_lookahead {};
	Common::Mutex                                  m_lookahead_mutex;
	Common::Mutex                                  m_submission_mutex;
	Common::Mutex                                  m_queue_mutex;
	std::mutex                                     m_shutdown_mutex;
	Common::CondVar                                m_work_available;
	Common::CondVar                                m_idle;
	std::array<std::deque<Submission>, QueueCount> m_queues;
	std::deque<Common::UniqueFunction<void>>       m_commands;
	std::atomic_uint32_t                           m_pending_commands {0};
	uint32_t                                       m_next_queue        = 0;
	uint32_t                                       m_submission_count  = 0;
	bool                                           m_processing        = false;
	bool                                           m_graphics_done     = true;
	bool                                           m_accepting         = true;
	bool                                           m_stopping          = false;
	bool                                           m_shutdown_complete = false;

	std::unique_ptr<CommandProcessor>                                m_gfx_cp;
	std::array<std::unique_ptr<CommandProcessor>, ComputeQueueCount> m_compute_cp;

	uint64_t        m_submit_id = 0;
	// Session 98 (patch_s98a): submission sequence (m_queue_mutex) and, for mode 1, the ring of
	// recently completed submissions the flip packet scans for bf_xover (m_queue_mutex).
	struct BindFloorDone {
		uint64_t seq   = 0;
		uint64_t epoch = 0; // BindFloorFlipEpoch() at completion
		uint32_t queue = 0;
		uint32_t ops   = 0;
	};
	uint64_t                        m_bf_seq = 0;
	std::array<BindFloorDone, 512>  m_bf_done {};
	uint32_t                        m_bf_done_next = 0;
	uint64_t        m_walk_ids  = 0; // m_submission_mutex
	std::atomic_int m_done_num  = 0;
	std::jthread    m_thread;

	friend class CommandProcessor;
};
} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICSRUN_H_ */
