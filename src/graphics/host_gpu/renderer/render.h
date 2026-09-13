#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICSRENDER_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICSRENDER_H_

#include "common/abi.h"
#include "common/assert.h"
#include "common/common.h"
#include "graphics/host_gpu/renderer/indirectArgsSanitizer.h"
#include "graphics/host_gpu/renderer/pipeline/descriptors.h"
#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"
#include "graphics/host_gpu/renderer/renderTarget.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <atomic>
#include <array>
#include <memory>
#include <optional>
#include <span>
#include <vector>
#include <cstdlib>
#include <cstring>

namespace Libs::Graphics {

namespace HW {
class Context;
class UserConfig;
class Shader;
} // namespace HW

struct GraphicContext;
struct ShaderBufferResource;
struct ShaderComputeInputInfo;
struct RenderDepthInfo;
struct RenderColorInfo;
struct RenderExecutorMemo;
struct DrawCallInfo;
struct DrawEmitInfo;
struct DrawIndexBufferSource;
struct DrawRenderState;
class RenderContext;
class CommandScheduler;
class CommandRecorder;
struct RecordSubmit;
struct RenderExecutorTestAccess;

enum class CommandBufferDebugOp : uint32_t {
	DispatchDirect,
	DrawIndex,
	DrawIndexAuto,
	EopWrite,
	EopInterrupt,
	EopWriteBack,
	EopFlip,
	EopWriteBackFlip,
	EopOnlyFlip,
	DrawComplete,
	Unknown,
};

enum class DrawOffsetSource : uint8_t {
	DrawState,
	IndirectArgs,
};

struct DrawIndexArgs {
	uint32_t         index_count                = 0;
	const void*      index_addr                 = nullptr;
	uint32_t         instance_count             = 0;
	uint32_t         index_type_and_size        = 0;
	int32_t          base_vertex                = 0;
	uint32_t         first_instance             = 0;
	DrawOffsetSource offset_source              = DrawOffsetSource::DrawState;
	uint32_t         render_target_slice_offset = 0;
	// Guest address of the VkDrawIndexedIndirectCommand-compatible arguments; when set the GPU
	// reads count/instances/offsets from there (index_count = index buffer size, others unused).
	uint64_t         indirect_args_addr         = 0;
};

struct DrawAutoArgs {
	uint32_t         vertex_count               = 0;
	uint32_t         instance_count             = 0;
	uint32_t         first_vertex               = 0;
	uint32_t         first_instance             = 0;
	DrawOffsetSource offset_source              = DrawOffsetSource::DrawState;
	uint32_t         render_target_slice_offset = 0;
	uint64_t         indirect_args_addr         = 0; // see DrawIndexArgs
};

struct SubmitInfo {
	static constexpr uint32_t MaxSemaphores = 4;

	std::array<vk::Semaphore, MaxSemaphores>          wait_semaphores {};
	std::array<uint64_t, MaxSemaphores>               wait_ticks {};
	std::array<vk::PipelineStageFlags, MaxSemaphores> wait_stages {};
	std::array<vk::Semaphore, MaxSemaphores>          signal_semaphores {};
	std::array<uint64_t, MaxSemaphores>               signal_ticks {};
	uint32_t                                          num_wait_semaphores   = 0;
	uint32_t                                          num_signal_semaphores = 0;

	// WSI binary signals may not depend on a future host timeline signal. The caller
	// holds the render mutex, which also serializes guest-to-staging copy enqueueing.
	bool present = false;

	void AddWait(vk::Semaphore semaphore, uint64_t tick = 1,
	             vk::PipelineStageFlags stage = vk::PipelineStageFlagBits::eAllCommands) {
		EXIT_IF(semaphore == nullptr || num_wait_semaphores >= MaxSemaphores);
		wait_semaphores[num_wait_semaphores] = semaphore;
		wait_ticks[num_wait_semaphores]      = tick;
		wait_stages[num_wait_semaphores++]   = stage;
	}

	void AddSignal(vk::Semaphore semaphore, uint64_t tick = 1) {
		EXIT_IF(semaphore == nullptr || num_signal_semaphores >= MaxSemaphores);
		signal_semaphores[num_signal_semaphores] = semaphore;
		signal_ticks[num_signal_semaphores++]    = tick;
	}
};

enum class GraphicsStateSlot : uint32_t {
	Viewports, Scissors, LineWidth, BlendConstants, DepthTest, DepthWrite, DepthCompare,
	DepthBiasEnable, DepthBias, StencilCompare, StencilWrite, StencilReference,
	ColorWrite, FeedbackLoop, Pipeline, Count
};

class CommandBuffer {
public:
	~CommandBuffer() = default;

	KYTY_CLASS_NO_COPY(CommandBuffer);

	[[nodiscard]] bool IsInvalid() const;

	void SetDebugInfo(uint32_t op, uint64_t submit_id, uint32_t arg0 = 0, uint32_t arg1 = 0,
	                  uint32_t arg2 = 0, uint32_t arg3 = 0, uint64_t arg4 = 0, uint64_t arg5 = 0);
	[[nodiscard]] bool IsRendering() const noexcept { return m_rendering; }
	void BeginRendering(const RenderState& state) const;
	// why: charged when a pass is actually open (FrameTrace-rp).
	void EndRendering(RenderPassEnd why = RenderPassEnd::Other) const;

	// Records on the calling thread. With a record thread (gate "recordthread") this first waits
	// for everything published to it, so the direct commands land in publication order.
	[[nodiscard]] vk::CommandBuffer Handle() const;
	// A site that only marks the buffer as used for the end-of-pipe bookkeeping
	// (GlobalBarrierRedundant) without recording anything: no drain is owed.
	void NoteHandleUse() const {
		EXIT_IF(IsInvalid());
		m_handle_uses++;
	}
	// The record thread of this buffer, or nullptr when it is recorded directly. Chosen once per
	// native command buffer, in CommandScheduler::BeginCommand.
	[[nodiscard]] CommandRecorder* Recorder() const noexcept { return m_recorder; }
	// Values belong to one native command-buffer recording. Utility graphics pipelines
	// must invalidate them because static state can invalidate previously set dynamic state.
	bool GraphicsStateChanged(GraphicsStateSlot slot, const void* bytes, size_t size) const {
		static const bool enabled = [] {
			const auto* value = std::getenv("KYTY_DYNAMIC_STATE_CACHE");
			return value == nullptr || value[0] != '0';
		}();
		if (!enabled) return true;
		auto& cached = m_graphics_state[static_cast<size_t>(slot)];
		if (cached.valid && cached.bytes.size() == size &&
		    std::memcmp(cached.bytes.data(), bytes, size) == 0) return false;
		cached.bytes.resize(size);
		std::memcpy(cached.bytes.data(), bytes, size);
		cached.valid = true;
		return true;
	}
	template <typename T>
	bool GraphicsStateChanged(GraphicsStateSlot slot, const T& value) const {
		return GraphicsStateChanged(slot, &value, sizeof(value));
	}
	void InvalidateGraphicsState() const {
		for (auto& state: m_graphics_state) state.valid = false;
	}
	void InvalidateGraphicsState(GraphicsStateSlot slot) const {
		m_graphics_state[static_cast<size_t>(slot)].valid = false;
	}
	// Every recording goes through Handle(); a global barrier is redundant when Handle() has not
	// been used since the previous one (nothing to order). Reset per command buffer.
	[[nodiscard]] bool GlobalBarrierRedundant() const noexcept {
		return m_barrier_mark == m_handle_uses;
	}
	void MarkGlobalBarrier() const noexcept { m_barrier_mark = m_handle_uses; }
	// Gate "swlocal": the shader-write barrier of a draw was recorded inside the open render pass
	// as a by-region fragment -> fragment dependency; the wide barrier is owed to everything that
	// can only observe the writes once the pass is closed, and EndRendering pays it.
	void NotePendingShaderWrite(vk::PipelineStageFlags stages) const noexcept {
		m_pending_shader_write |= stages;
	}
	// Gate "gdsepoch": true when this GDS consumer must issue the barrier. Records the state it
	// leaves behind either way, so the gate can be flipped between two flips without a hole.
	// consumer: 1 graphics, 2 compute.
	[[nodiscard]] bool ClaimGdsBarrier(uint64_t host_epoch, uint64_t shader_epoch,
	                                   uint32_t consumer, bool lazy) const noexcept {
		const bool first    = m_gds_barrier_consumer == 0;
		const bool host     = host_epoch != m_gds_barrier_host_epoch;
		const bool produced = shader_epoch != m_gds_barrier_shader_epoch;
		const bool kind     = consumer != m_gds_barrier_consumer;
		m_gds_barrier_host_epoch   = host_epoch;
		m_gds_barrier_shader_epoch = shader_epoch;
		m_gds_barrier_consumer     = consumer;
		// A host or transfer write to GDS, and the first consumer of a recording, always pay.
		if (first || host) {
			return true;
		}
		// Nothing reached GDS since the last barrier. Only the gate may act on that: with the
		// gate off the barrier is issued exactly as before.
		if (lazy && !produced) {
			return false;
		}
		// Shader -> shader. The GDS accesses of these shaders are DS_APPEND / DS_CONSUME, emitted
		// as device-scope atomics, which order themselves; a change of consumer kind still pays.
		return !lazy || kind;
	}
	[[nodiscard]] GraphicContext&   GetGraphics() const noexcept { return m_graphics; }
	[[nodiscard]] RenderContext&    GetContext() const noexcept { return m_context; }
	[[nodiscard]] HW::Context&      GetRegisters() const noexcept { return *m_registers; }
	[[nodiscard]] HW::UserConfig&   GetUserConfig() const noexcept { return *m_user_config; }
	[[nodiscard]] HW::Shader&       GetShaders() const noexcept { return *m_shaders; }

private:
	explicit CommandBuffer(CommandScheduler& scheduler);
	void Bind(HW::Context& registers, HW::UserConfig& user_config, HW::Shader& shaders) noexcept {
		m_registers   = &registers;
		m_user_config = &user_config;
		m_shaders     = &shaders;
	}

	void Begin();
	void End() const;
	// Gate "recordthread": the native buffer is taken from the pool, begun and ended by the record
	// thread, which also hands an asynchronous submit to the submit thread.
	void BeginRecorded(uint64_t tick);
	void EndRecorded(const RecordSubmit& request) const;

	RenderContext&      m_context;
	GraphicContext&     m_graphics;
	// Owned by the record thread while its queue is not empty; the resolving thread may read it
	// after a drain. Whether a buffer is open is m_active, not this handle.
	vk::CommandBuffer   m_buffer          = nullptr;
	bool                m_active          = false;
	CommandRecorder*    m_recorder        = nullptr;
	uint32_t            m_debug_op        = 0;
	uint64_t            m_debug_submit_id = 0;
	uint32_t            m_debug_arg0      = 0;
	uint32_t            m_debug_arg1      = 0;
	uint32_t            m_debug_arg2      = 0;
	uint32_t            m_debug_arg3      = 0;
	uint64_t            m_debug_arg4      = 0;
	uint64_t            m_debug_arg5      = 0;
	mutable RenderState m_render_state;
	mutable bool        m_rendering   = false;
	// KYTY_FRAME_TRACE: the last pass EndRendering closed and why; the next real BeginRendering on
	// the same targets counts a restart for that reason.
	mutable RenderState   m_closed_state;
	mutable RenderPassEnd m_closed_why   = RenderPassEnd::Other;
	mutable bool          m_closed_valid = false;
	mutable vk::PipelineStageFlags m_pending_shader_write {};
	mutable uint64_t    m_gds_barrier_host_epoch   = 0;
	mutable uint64_t    m_gds_barrier_shader_epoch = 0;
	mutable uint32_t    m_gds_barrier_consumer     = 0;
	mutable uint64_t    m_handle_uses  = 0;
	mutable uint64_t    m_barrier_mark = 0;
	struct GraphicsStateValue { std::vector<uint8_t> bytes; bool valid = false; };
	mutable std::array<GraphicsStateValue, static_cast<size_t>(GraphicsStateSlot::Count)> m_graphics_state;
	HW::Context*        m_registers   = nullptr;
	HW::UserConfig*     m_user_config = nullptr;
	HW::Shader*         m_shaders     = nullptr;

	friend class CommandScheduler;
};

class RenderExecutor {
public:
	explicit RenderExecutor(RenderContext& context): m_context(context) {}
	KYTY_CLASS_NO_COPY(RenderExecutor);

	// indirect_args_addr != 0: the group counts live in guest memory (typically written by a
	// previous compute shader) and are consumed on the GPU with vkCmdDispatchIndirect; the
	// thread_group_* values are then only the (possibly stale) CPU view for logging.
	void DispatchDirect(uint64_t submit_id, CommandBuffer& buffer, uint32_t thread_group_x,
	                    uint32_t thread_group_y, uint32_t thread_group_z, uint32_t mode,
	                    uint64_t indirect_args_addr = 0);

	[[nodiscard]] PreparedBindings PrepareBindings(const ShaderStageRuntime& runtime);
	void PrepareBindings(const ShaderStageRuntime& runtime, PreparedBindings& prepared);
	void                           FindBuffers(PreparedBindings& bindings);
	void                           RebindBuffers(PreparedBindings& bindings);
	void                           RebindImages(PreparedBindings& bindings);
	void CommitBindings(CommandBuffer& buffer, vk::PipelineBindPoint pipeline_bind_point,
	                    const PipelineCache::Pipeline&     pipeline,
	                    std::span<PreparedBindings* const> bindings);

private:
	void DrawIndex(uint64_t submit_id, CommandBuffer& buffer, const DrawIndexArgs& args);
	void DrawAuto(uint64_t submit_id, CommandBuffer& buffer, const DrawAutoArgs& args);

	struct GraphicsBindings {
		PreparedBindings                vertex;
		std::optional<PreparedBindings> pixel;
	};

	[[nodiscard]] TextureBinding ResolveTexture(const ShaderRecompiler::IR::ImageResource& resource,
	                                            const ShaderRecompiler::IR::DescriptorValue& value);
	[[nodiscard]] GraphicsBindings PrepareGraphicsBindings(const ShaderStageRuntime& vertex,
	                                                       const ShaderStageRuntime& pixel,
	                                                       bool                      pixel_active);
	void PrepareGraphicsBindings(const ShaderStageRuntime& vertex, const ShaderStageRuntime& pixel,
	                             bool pixel_active, GraphicsBindings& bindings);
	static bool ReuseBindingsEnabled();
	// Draw and dispatch preparation is serialized by the render mutex. Keep their storage
	// separate and reset it before each operation; runtime pointers are valid through commit.
	GraphicsBindings m_graphics_bindings;
	PreparedBindings m_compute_bindings;

	void ResolveRenderColorTarget(CommandBuffer& buffer, RenderColorInfo& target,
	                              uint32_t render_target_slice_offset, uint32_t render_target_slot,
	                              bool ignore_target_mask = false, bool exact_format = false);
	void ResolveRenderDepthTarget(CommandBuffer& buffer, RenderDepthInfo& target);
	[[nodiscard]] bool DepthStencilCopy(CommandBuffer& buffer);
	[[nodiscard]] bool PrepareDrawRenderState(CommandBuffer& buffer,
	                                          const DrawCallInfo& draw,
	                                          uint32_t            render_target_slice_offset,
	                                          DrawRenderState& state);
	void ExecutePreparedDraw(uint64_t submit_id, CommandBuffer& buffer, const DrawCallInfo& draw,
	                         DrawRenderState& state, vk::PrimitiveTopology topology,
	                         const DrawEmitInfo& emit, const DrawIndexBufferSource& index_source,
	                         bool primitive_restart_enable);
	[[nodiscard]] RenderState AcquireRenderTargets(CommandBuffer& buffer, RenderColorInfo* colors,
	                                               uint32_t color_count, RenderDepthInfo& depth,
	                                               const std::optional<PreparedBindings>& pixel = std::nullopt);
	[[nodiscard]] bool        ResolveColorTargets(CommandBuffer& buffer,
	                                              uint32_t render_target_slice_offset);
	// atomic: this descriptor writes the image with image atomics only (ImageResource::atomic).
	void                      BindImage(ImageId id, bool storage, bool atomic = false);
	void                      MaterializeDeferredDccClear(CommandBuffer& buffer, ImageId id);
	void                      MaterializeBoundTargetDccClears(CommandBuffer& buffer);
	void                      BindRenderTarget(ImageId id);
	void                      ResetBindings();
	[[nodiscard]] bool        TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,
	                                                     const CommandBuffer&          buffer);
	[[nodiscard]] bool TryConsumeComputeImageClear(const ShaderComputeInputInfo& input,
	                                              CommandBuffer& command, uint32_t group_x,
	                                              uint32_t group_y, uint32_t group_z, uint32_t mode);

	RenderContext&                        m_context;
	std::unique_ptr<IndirectArgsSanitizer> m_indirect_sanitizer;
	std::vector<ImageId>                  m_bound_images;
	// Draws skipped because their pipeline was still compiling (KYTY_ASYNC_PIPELINES); read and
	// reset at every flip to mark frames that must not be presented.
	std::atomic<uint32_t>                 m_skipped_draws {0};

public:
	uint32_t TakeSkippedDraws() { return m_skipped_draws.exchange(0, std::memory_order_relaxed); }

private:
	std::vector<vk::DescriptorBufferInfo> m_descriptor_buffers;
	std::vector<vk::DescriptorImageInfo>  m_descriptor_images;
	std::vector<vk::WriteDescriptorSet>   m_descriptor_writes;
	std::vector<uint32_t>                 m_image_occurrences;
	// Hot-path memos (renderMemo.h); created on first use so the header stays light.
	std::shared_ptr<RenderExecutorMemo>   m_memo;
	[[nodiscard]] RenderExecutorMemo&     Memo();

	friend class CommandProcessor;
	friend struct RenderExecutorTestAccess;
};

// Debug aid (KYTY_DUMP_ADDR=<hex guest address>): find every draw or dispatch whose buffer or
// image bindings cover the address, and log its bindings.
[[nodiscard]] uint64_t DebugDumpAddress();
// KYTY_DUMP_ADDRS=<hex>[,<hex>...]: like KYTY_DUMP_ADDR but several addresses, matched against
// buffer bindings only (the image match uses a 64 MiB window and is too noisy for lists).
[[nodiscard]] const std::vector<uint64_t>& DebugDumpAddresses();
[[nodiscard]] bool ShaderStageTouchesAnyBuffer(const ShaderStageRuntime& stage,
                                                const std::vector<uint64_t>& addresses);
// KYTY_DUMP_FRAME=<n>[,<n>|<a>-<b>...]: log every draw and dispatch of the listed frames with
// their render targets and bindings (a whole-frame dependency trace).
[[nodiscard]] bool DebugDumpFrame(uint32_t frame);
[[nodiscard]] bool     ShaderStageTouchesAddress(const ShaderStageRuntime& stage, uint64_t address);
void DumpShaderStageBindings(RenderContext& context, const char* label,
                             const ShaderStageRuntime& stage);

[[nodiscard]] bool ResolveComputeBufferFill(const ShaderComputeInputInfo& input, uint32_t group_x,
                                            uint32_t group_y, uint32_t group_z, uint32_t mode,
                                            ShaderBufferResource& descriptor,
                                            uint32_t& packed_clear, uint64_t& size);

} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICSRENDER_H_ */
