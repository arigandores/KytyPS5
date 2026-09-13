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
#include <cstring>
#include <span>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;

// M3 (docs/parallel-draw-path.md): the thread that resolves PM4 stops calling vkCmd* itself and
// publishes POD records of "what to record" into a ring arena; one record thread per scheduler
// consumes them in publication order and records into one primary command buffer.
//
// Step 0 moves only the lifetime of the native buffer (the pool, vkBeginCommandBuffer,
// vkEndCommandBuffer, the hand-off to the submit thread) and the two query-pool timestamps that
// bracket it. Every other site still records on the resolving thread: CommandBuffer::Handle()
// drains this queue first and then writes into the same buffer, so the order of commands is
// exactly the order it is today and sites can be moved one at a time.
//
// The invariant that makes the transitional state safe: a record may only be published at a point
// where the resolving thread holds no vk::CommandBuffer it is about to record into. Handle()
// drains, but the hot sites cache what it returned for a whole draw or dispatch (renderDraw.cpp
// and renderCompute.cpp keep `vk_buffer`), so a record published in the middle of a buffer lets
// the record thread call vkCmd* on the same VkCommandBuffer at the same time. That is a host
// external-synchronization violation: it corrupts the driver's command-pool block allocator and
// the process dies inside the driver, not inside the emulator. Only the buffer boundaries publish.
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
	Timestamp,   // the query-pool timestamps that bracket the buffer (KYTY_FRAME_TRACE)
	Generic,     // an arbitrary recording callback, for the rare sites
	// Gate "recpack" (M3 steps 1-2). A draw or a dispatch publishes its own commands once this
	// thread has taken every decision they depend on - render-pass state, the dynamic-state cache,
	// image layouts, the descriptor set it hands out - and keeps all of that state here; the record
	// thread only issues the calls. The invariant above holds for every record: after a publish the
	// resolving thread uses no vk::CommandBuffer it obtained before it, and a direct write takes a
	// fresh Handle(), which drains first (KYTY_RECORD_CHECK=1 checks the hot direct sites).
	PassEnd,     // RecordPassEnd: vkCmdEndRendering and/or the wide shader-write barrier a pass owed
	PassBegin,   // RenderState: vkCmdBeginRendering
	Bindings,    // RecordBindings: push constants, then push descriptors or update + bind
	Commands,    // RecordCmd stream: the tail of one draw or one dispatch
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

struct RecordPassEnd {
	uint32_t end_pass;            // 1: vkCmdEndRendering
	uint32_t shader_write_stages; // != 0: then ShaderWriteBarrier(stages), the debt of the pass
};
static_assert(std::is_trivially_copyable_v<RecordPassEnd>);
static_assert(std::is_trivially_copyable_v<RenderState>);

// RecordOp::Bindings: this header, `push_size` bytes of push constants padded to 8, then
// RecordDescriptorWrite[write_count], vk::DescriptorBufferInfo[buffer_count] and
// vk::DescriptorImageInfo[image_count]. Copies only: nothing points at the resolving thread.
struct RecordBindings {
	vk::PipelineLayout layout;
	vk::DescriptorSet  set; // nullptr: vkCmdPushDescriptorSetKHR, else vkUpdateDescriptorSets + bind
	uint32_t           bind_point;
	uint32_t           push_stages;
	uint32_t           push_size;
	uint32_t           write_count;
	uint32_t           buffer_count;
	uint32_t           image_count;
};
struct RecordDescriptorWrite {
	uint32_t binding;
	uint32_t type;
	uint32_t count;
	uint32_t buffer_start; // UINT32_MAX: none
	uint32_t image_start;  // UINT32_MAX: none
	uint32_t reserved;
};
static_assert(std::is_trivially_copyable_v<RecordBindings>);
static_assert(std::is_trivially_copyable_v<RecordDescriptorWrite>);
static_assert(sizeof(RecordBindings) == 40 && sizeof(RecordDescriptorWrite) == 24);
static_assert(sizeof(vk::DescriptorBufferInfo) == 24 && sizeof(vk::DescriptorImageInfo) == 24);
static_assert(sizeof(vk::Buffer) == 8 && sizeof(vk::Pipeline) == 8 &&
              sizeof(vk::PipelineLayout) == 8 && sizeof(vk::DeviceSize) == 8);

// RecordOp::Commands: uint32_t stream bytes, uint32_t reserved, then per command a RecordCmdHeader
// and its payload padded to 8, executed in order. Every payload offset is a multiple of 8 inside a
// 16-aligned record, so the arrays can be handed to the driver in place.
enum class RecordCmd : uint16_t {
	BindVertexBuffers,        // aux count: vk::Buffer[count], vk::DeviceSize[count]
	BindIndexBuffer,          // aux vk::IndexType: vk::Buffer, vk::DeviceSize
	SetViewports,             // aux count: vk::Viewport[count]
	SetScissors,              // aux count: vk::Rect2D[count]
	SetLineWidth,             // float
	SetBlendConstants,        // float[4]
	SetDepthTestEnable,       // aux
	SetDepthWriteEnable,      // aux
	SetDepthCompareOp,        // aux
	SetDepthBiasEnable,       // aux
	SetDepthBias,             // float constant, clamp, slope
	SetStencilCompareMask,    // aux face: uint32_t
	SetStencilWriteMask,      // aux face: uint32_t
	SetStencilReference,      // aux face: uint32_t
	SetColorWriteEnable,      // aux count: vk::Bool32[count]
	SetFeedbackLoop,          // aux vk::ImageAspectFlags
	BindPipeline,             // aux vk::PipelineBindPoint: vk::Pipeline
	PushConstants,            // aux stages: vk::PipelineLayout, uint32_t offset, uint32_t size, bytes
	Draw,                     // uint32_t vertices, instances, first vertex, first instance
	DrawIndexed,              // uint32_t indices, instances, first index, vertex offset, first instance
	DrawIndirect,             // vk::Buffer, vk::DeviceSize, uint32_t count, uint32_t stride
	DrawIndexedIndirect,      // same
	DrawMeshTasks,            // uint32_t x, y, z
	Dispatch,                 // uint32_t x, y, z
	DispatchIndirect,         // vk::Buffer, vk::DeviceSize
	ShaderWriteBarrierLocal,  // aux vk::PipelineStageFlags
	ShaderWriteHazardBarrier, // aux vk::PipelineStageFlags
	ShaderAccessBarrier,      // aux vk::PipelineStageFlags
};
struct RecordCmdHeader {
	uint16_t cmd;
	uint16_t size; // payload bytes before padding
	uint32_t aux;
};
static_assert(sizeof(RecordCmdHeader) == 8);

class CommandRecorder final {
public:
	// commit: takes the next native command buffer of the scheduler's pool whose previous
	// submission has completed. Called on the record thread, which owns the pool while it runs.
	// current: where the handle of the buffer being recorded is published; the resolving thread
	// may read it once Drain() has returned.
	using CommitFn = vk::CommandBuffer (*)(void* user, uint64_t tick);

	// device: the record thread's vkUpdateDescriptorSets (RecordOp::Bindings).
	CommandRecorder(CommitFn commit, void* user, vk::CommandBuffer* current, vk::Device device);
	~CommandRecorder();
	KYTY_CLASS_NO_COPY(CommandRecorder);

	// tick: the tick this buffer will signal, for the pool's reuse bookkeeping.
	void PushBeginBuffer(uint64_t tick);
	void PushEndBuffer(const RecordSubmit& request);
	// reset != 0: vkCmdResetQueryPool(pool, query, reset) before the write (outside a pass only).
	void PushTimestamp(vk::QueryPool pool, uint32_t query, uint32_t reset, bool bottom);
	// No GPU-time marks here: they are published in the middle of a command buffer, where the
	// resolving thread still owns the handle (see the note above and CommandScheduler::GpuMarkSlow).
	void PushGeneric(Common::UniqueFunction<void, vk::CommandBuffer>&& command);
	// Gate "recpack". None of these may be called while this thread still uses a vk::CommandBuffer
	// it obtained before the call.
	void PushPassEnd(bool end_pass, vk::PipelineStageFlags shader_write_stages);
	void PushPassBegin(const RenderState& state);
	// Copies everything: the writes may point into `buffers` and `images` only.
	void PushBindings(vk::PipelineBindPoint bind_point, vk::PipelineLayout layout,
	                  vk::DescriptorSet set, vk::ShaderStageFlags push_stages,
	                  std::span<const uint32_t>                 push,
	                  std::span<const vk::WriteDescriptorSet>   writes,
	                  std::span<const vk::DescriptorBufferInfo> buffers,
	                  std::span<const vk::DescriptorImageInfo>  images);
	// In-place publication, one open record at a time: BeginRecord reserves `max_payload` bytes
	// and returns them, EndRecord publishes the first `payload_size` of them, AbandonRecord none.
	[[nodiscard]] uint8_t* BeginRecord(RecordOp op, uint32_t max_payload);
	// publish=false (gate "recbatch"): the record stays invisible to the record thread until the next
	// publish - an EndRecord with publish=true, PublishStaged, a Pad or a wait for arena space.
	void                   EndRecord(uint32_t payload_size, bool publish = true);
	void                   AbandonRecord() noexcept { m_open_slot = nullptr; }
	// True between BeginRecord and EndRecord/AbandonRecord: nothing may be recorded directly into
	// the command buffer while a record is being filled (CommandBuffer::Handle).
	[[nodiscard]] bool     HasOpenRecord() const noexcept { return m_open_slot != nullptr; }
	// Records ended so far, published or staged; producer thread (KYTY_RECORD_CHECK).
	[[nodiscard]] uint64_t Published() const noexcept { return m_records; }
	// Gate "recbatch": makes every staged record visible to the record thread. Producer thread only.
	// CommandBuffer::Handle calls it before its drain, so a direct write never lands ahead of a
	// staged record.
	void                   PublishStaged();
	// Records ended and not published yet; producer thread (KYTY_RECORD_CHECK).
	[[nodiscard]] bool     HasStaged() const noexcept { return m_published != m_head_local; }

	// Waits until everything published before this call has been recorded. Never call it from the
	// record thread. Staged records are not published by it: the producer calls PublishStaged first.
	void Drain();
	// Bytes published and not recorded yet (diagnostics).
	[[nodiscard]] size_t Backlog() const noexcept;

private:
	static constexpr uint32_t RecordAlign = 16;

	void     Loop();
	[[nodiscard]] bool SpinFor(uint64_t tail);
	void     ExecuteBindings(const uint8_t* payload);
	void     ExecuteCommands(const uint8_t* payload);
	void     Stop();
	uint8_t* Reserve(uint32_t bytes);
	void     Publish();
	void     PushRecord(RecordOp op, const void* payload, uint32_t payload_size, bool publish = true);
	void     Execute(const RecordHeader& header, const uint8_t* payload);
	void     WakeConsumer();
	void     WakeWaiters();

	// Session 57, A4: grouped by the thread that writes them, one cache line per group, so neither
	// thread writes a line the other reads for every record (the open-slot fields used to share a
	// line with m_data/m_mask, which the record thread reads per record).

	// Read-only once the constructor has returned; both threads.
	alignas(64) std::unique_ptr<uint8_t[]> m_data;
	uint64_t                   m_capacity = 0;
	uint64_t                   m_mask     = 0;
	CommitFn                   m_commit   = nullptr;
	void*                      m_user     = nullptr;
	vk::CommandBuffer*         m_current  = nullptr;
	vk::Device                 m_device   = nullptr;
	// The producer is the GuestGpu thread (its role when it created the recorder): the *_gpu
	// counters and gate "recpin" apply to this recorder, not to the presentation thread's.
	bool                       m_gpu      = false;
	bool                       m_stats    = false; // FrameStats::Enabled() at construction

	// Producer only. The ring is single-producer and m_producer is the assert that says so.
	alignas(64) uint8_t*       m_open_slot  = nullptr; // the record between BeginRecord and EndRecord
	uint32_t                   m_open_bytes = 0;
	RecordOp                   m_open_op    = RecordOp::Pad;
	uint64_t                   m_head_local = 0; // bytes of every ended record, published or staged
	uint64_t                   m_published  = 0; // the value of the last m_head store
	uint64_t                   m_tail_seen  = 0; // an m_tail read before: a lower bound of the tail
	std::thread::id            m_producer;
	uint64_t                   m_records    = 0;
	uint64_t                   m_full       = 0;

	// Written by the producer, polled by the record thread. The flag sits here because the producer
	// reads it right after its head store, from a line it then owns; the record thread writes it
	// only on its way to sleep.
	alignas(64) std::atomic<uint64_t> m_head {0}; // published bytes
	std::atomic<bool>                 m_consumer_waiting {false};
	std::atomic<bool>                 m_stop {false};
	// Set (sequentially consistent) before this producer's first relaxed head store (gate
	// "recrelax"); from then on the record thread flushes store buffers before it sleeps.
	std::atomic<bool>                 m_relaxed_ever {false};

	// Record thread (m_waiters: drains, rarely written).
	alignas(64) std::atomic<uint64_t> m_tail {0}; // recorded bytes
	std::atomic<uint32_t>             m_waiters {0};
	vk::CommandBuffer                 m_buffer       = nullptr;
	uint64_t                          m_peak_backlog = 0; // read by Stop after the join
	uint32_t                          m_ccd_tick     = 0;
	// The vk::WriteDescriptorSet array rebuilt for each Bindings record.
	std::vector<vk::WriteDescriptorSet> m_writes;

	// Sleeping and waking.
	alignas(64) std::mutex            m_mutex;
	std::condition_variable           m_progress; // tail advanced: space and drains
	std::condition_variable           m_pending;  // head advanced: work for the consumer
	std::thread                       m_thread;
};

// Gate "recpack": one RecordOp::Commands record, built in place in the arena. The method names and
// arguments follow vk::CommandBuffer, so renderDraw.cpp records the same template code either
// directly or through this writer. Nothing else may be published on the recorder while a writer
// is open (CommandRecorder::BeginRecord allows one open record).
class RecordCommandWriter final {
public:
	// A draw tail needs about 1.5 KiB at most (32 vertex buffers, 16 viewports and scissors, all
	// dynamic state, one draw); a dispatch well under 100 bytes.
	static constexpr uint32_t MaxBytes = 4096;

	explicit RecordCommandWriter(CommandRecorder& recorder)
	    : m_recorder(recorder), m_data(recorder.BeginRecord(RecordOp::Commands, MaxBytes)) {}
	~RecordCommandWriter() {
		// An early exit between BeginRecord and Commit (a return, or a check that fires) would
		// otherwise leave the reservation open: the next BeginRecord would reserve over it and the
		// record thread would read a half-written record.
		if (m_data != nullptr) {
			m_recorder.AbandonRecord();
		}
	}
	KYTY_CLASS_NO_COPY(RecordCommandWriter);

	// Publishes the stream (nothing when it is empty). dispatch: counted as rec_pack_cs.
	void Commit(bool dispatch);

	void bindVertexBuffers(uint32_t first, uint32_t count, const vk::Buffer* buffers,
	                       const vk::DeviceSize* offsets) {
		EXIT_IF(first != 0);
		auto* out = Append(RecordCmd::BindVertexBuffers, count, count * 16u);
		std::memcpy(out, buffers, count * sizeof(vk::Buffer));
		std::memcpy(out + count * sizeof(vk::Buffer), offsets, count * sizeof(vk::DeviceSize));
	}
	void bindIndexBuffer(vk::Buffer buffer, vk::DeviceSize offset, vk::IndexType type) {
		auto* out = Append(RecordCmd::BindIndexBuffer, static_cast<uint32_t>(type), 16u);
		std::memcpy(out, &buffer, sizeof(buffer));
		std::memcpy(out + 8, &offset, sizeof(offset));
	}
	void setViewportWithCount(uint32_t count, const vk::Viewport* viewports) {
		const auto bytes = count * static_cast<uint32_t>(sizeof(vk::Viewport));
		std::memcpy(Append(RecordCmd::SetViewports, count, bytes), viewports, bytes);
	}
	void setScissorWithCount(uint32_t count, const vk::Rect2D* scissors) {
		const auto bytes = count * static_cast<uint32_t>(sizeof(vk::Rect2D));
		std::memcpy(Append(RecordCmd::SetScissors, count, bytes), scissors, bytes);
	}
	void setLineWidth(float width) { Value(RecordCmd::SetLineWidth, 0, width); }
	void setBlendConstants(const float* constants) {
		std::memcpy(Append(RecordCmd::SetBlendConstants, 0, 4u * sizeof(float)), constants,
		            4u * sizeof(float));
	}
	void setDepthTestEnable(vk::Bool32 enable) {
		(void)Append(RecordCmd::SetDepthTestEnable, enable, 0);
	}
	void setDepthWriteEnable(vk::Bool32 enable) {
		(void)Append(RecordCmd::SetDepthWriteEnable, enable, 0);
	}
	void setDepthCompareOp(vk::CompareOp op) {
		(void)Append(RecordCmd::SetDepthCompareOp, static_cast<uint32_t>(op), 0);
	}
	void setDepthBiasEnable(vk::Bool32 enable) {
		(void)Append(RecordCmd::SetDepthBiasEnable, enable, 0);
	}
	void setDepthBias(float constant, float clamp, float slope) {
		const float values[] {constant, clamp, slope};
		std::memcpy(Append(RecordCmd::SetDepthBias, 0, sizeof(values)), values, sizeof(values));
	}
	void setStencilCompareMask(vk::StencilFaceFlags face, uint32_t mask) {
		Value(RecordCmd::SetStencilCompareMask, static_cast<uint32_t>(face), mask);
	}
	void setStencilWriteMask(vk::StencilFaceFlags face, uint32_t mask) {
		Value(RecordCmd::SetStencilWriteMask, static_cast<uint32_t>(face), mask);
	}
	void setStencilReference(vk::StencilFaceFlags face, uint32_t reference) {
		Value(RecordCmd::SetStencilReference, static_cast<uint32_t>(face), reference);
	}
	void setColorWriteEnableEXT(uint32_t count, const vk::Bool32* enables) {
		const auto bytes = count * static_cast<uint32_t>(sizeof(vk::Bool32));
		std::memcpy(Append(RecordCmd::SetColorWriteEnable, count, bytes), enables, bytes);
	}
	void setAttachmentFeedbackLoopEnableEXT(vk::ImageAspectFlags aspects) {
		(void)Append(RecordCmd::SetFeedbackLoop, static_cast<uint32_t>(aspects), 0);
	}
	void bindPipeline(vk::PipelineBindPoint point, vk::Pipeline pipeline) {
		Value(RecordCmd::BindPipeline, static_cast<uint32_t>(point), pipeline);
	}
	void pushConstants(vk::PipelineLayout layout, vk::ShaderStageFlags stages, uint32_t offset,
	                   uint32_t size, const void* values) {
		EXIT_IF(size > 1024u);
		auto* out = Append(RecordCmd::PushConstants, static_cast<uint32_t>(stages), 16u + size);
		std::memcpy(out, &layout, sizeof(layout));
		std::memcpy(out + 8, &offset, sizeof(offset));
		std::memcpy(out + 12, &size, sizeof(size));
		std::memcpy(out + 16, values, size);
	}
	void draw(uint32_t vertices, uint32_t instances, uint32_t first_vertex, uint32_t first_instance) {
		const uint32_t values[] {vertices, instances, first_vertex, first_instance};
		std::memcpy(Append(RecordCmd::Draw, 0, sizeof(values)), values, sizeof(values));
	}
	void drawIndexed(uint32_t indices, uint32_t instances, uint32_t first_index,
	                 int32_t vertex_offset, uint32_t first_instance) {
		const uint32_t values[] {indices, instances, first_index,
		                         static_cast<uint32_t>(vertex_offset), first_instance};
		std::memcpy(Append(RecordCmd::DrawIndexed, 0, sizeof(values)), values, sizeof(values));
	}
	void drawIndirect(vk::Buffer buffer, vk::DeviceSize offset, uint32_t count, uint32_t stride) {
		Indirect(RecordCmd::DrawIndirect, buffer, offset, count, stride);
	}
	void drawIndexedIndirect(vk::Buffer buffer, vk::DeviceSize offset, uint32_t count,
	                         uint32_t stride) {
		Indirect(RecordCmd::DrawIndexedIndirect, buffer, offset, count, stride);
	}
	void drawMeshTasksEXT(uint32_t x, uint32_t y, uint32_t z) {
		const uint32_t values[] {x, y, z};
		std::memcpy(Append(RecordCmd::DrawMeshTasks, 0, sizeof(values)), values, sizeof(values));
	}
	void dispatch(uint32_t x, uint32_t y, uint32_t z) {
		const uint32_t values[] {x, y, z};
		std::memcpy(Append(RecordCmd::Dispatch, 0, sizeof(values)), values, sizeof(values));
	}
	void dispatchIndirect(vk::Buffer buffer, vk::DeviceSize offset) {
		auto* out = Append(RecordCmd::DispatchIndirect, 0, 16u);
		std::memcpy(out, &buffer, sizeof(buffer));
		std::memcpy(out + 8, &offset, sizeof(offset));
	}
	void shaderWriteBarrierLocal(vk::PipelineStageFlags stages) {
		(void)Append(RecordCmd::ShaderWriteBarrierLocal, static_cast<uint32_t>(stages), 0);
	}
	void shaderWriteHazardBarrier(vk::PipelineStageFlags stages) {
		(void)Append(RecordCmd::ShaderWriteHazardBarrier, static_cast<uint32_t>(stages), 0);
	}
	void shaderAccessBarrier(vk::PipelineStageFlags stages) {
		(void)Append(RecordCmd::ShaderAccessBarrier, static_cast<uint32_t>(stages), 0);
	}

private:
	uint8_t* Append(RecordCmd cmd, uint32_t aux, uint32_t size) {
		const uint32_t padded = (size + 7u) & ~7u;
		// Checked in every build: the slot is a fixed 4 KiB of the ring, and overrunning it would
		// corrupt the records after it.
		if (m_data == nullptr || size > UINT16_MAX ||
		    m_used + sizeof(RecordCmdHeader) + padded > MaxBytes) {
			EXIT("record command stream overflow: cmd=%u size=%u used=%u\n",
			     static_cast<uint32_t>(cmd), size, m_used);
		}
		const RecordCmdHeader header {static_cast<uint16_t>(cmd), static_cast<uint16_t>(size), aux};
		std::memcpy(m_data + m_used, &header, sizeof(header));
		auto* payload = m_data + m_used + sizeof(header);
		m_used += static_cast<uint32_t>(sizeof(header)) + padded;
		return payload;
	}
	template <typename T>
	void Value(RecordCmd cmd, uint32_t aux, const T& value) {
		std::memcpy(Append(cmd, aux, sizeof(T)), &value, sizeof(T));
	}
	void Indirect(RecordCmd cmd, vk::Buffer buffer, vk::DeviceSize offset, uint32_t count,
	              uint32_t stride) {
		auto* out = Append(cmd, 0, 24u);
		std::memcpy(out, &buffer, sizeof(buffer));
		std::memcpy(out + 8, &offset, sizeof(offset));
		std::memcpy(out + 16, &count, sizeof(count));
		std::memcpy(out + 20, &stride, sizeof(stride));
	}

	CommandRecorder& m_recorder;
	uint8_t*         m_data = nullptr;
	uint32_t         m_used = 8; // the stream length word comes first
};

// The vkCmdBeginRendering of a RenderState, for both threads (defined in context.cpp).
void RecordBeginRendering(vk::CommandBuffer command, const RenderState& state);

// Waits for every recorder in the process; part of DrainAsyncSubmits().
void DrainRecordQueues();
// Bytes published and not recorded yet across every recorder (diagnostics).
[[nodiscard]] size_t RecordBacklog();
// Gate "recordthread" (KYTY_RECORD_THREAD at start, the gate file after it), read once per native
// command buffer by CommandScheduler::BeginCommand - the only point where the command pool and the
// handle change owner. On top of it, the cases the record thread has to stay out of: the
// breadcrumb and checkpoint modes record their own commands from CommandBuffer::SetDebugInfo and
// exist to name the last command before a hang, and a RenderDoc capture must see the frame
// recorded the way the thread that resolved it wrote it.
[[nodiscard]] bool RecordThreadWanted(const GraphicContext& graphics);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_COMMANDRECORDER_H_
