#include "common/assert.h"
#include "common/drawStat.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/common.h"
#include "common/profiler.h"
#include "common/threads.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/commandRecorder.h"
#include "graphics/host_gpu/renderer/debug.h"
#include "graphics/host_gpu/renderer/depthRenderTarget.h"
#include "graphics/host_gpu/renderer/gpuCheckpoints.h"
#include "graphics/host_gpu/renderer/image/imageView.h"
#include "graphics/host_gpu/renderer/pipeline/shaderResourceBarrier.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <algorithm>
#include <bit>
#include <cstring>
namespace Libs::Graphics {

namespace {

[[nodiscard]] Common::FrameStats::Counter RenderPassEndCounter(Common::FrameStats::Counter first,
                                                              RenderPassEnd              why) {
	return static_cast<Common::FrameStats::Counter>(static_cast<uint32_t>(first) +
	                                                static_cast<uint32_t>(why));
}

static_assert(static_cast<uint32_t>(Common::FrameStats::Counter::RpEndOther) -
                  static_cast<uint32_t>(Common::FrameStats::Counter::RpEndState) ==
              static_cast<uint32_t>(RenderPassEnd::Other));
static_assert(static_cast<uint32_t>(Common::FrameStats::Counter::RpRestartState) -
                  static_cast<uint32_t>(Common::FrameStats::Counter::RpEndState) ==
              static_cast<uint32_t>(RenderPassEnd::Count));
static_assert(static_cast<uint32_t>(Common::FrameStats::Counter::RpRestartOther) -
                  static_cast<uint32_t>(Common::FrameStats::Counter::RpRestartState) ==
              static_cast<uint32_t>(RenderPassEnd::Other));

// The beginning pass records to the same attachments, in the same layouts, over the same render
// area as the pass that ended: the two differ at most in their load-op clears.
[[nodiscard]] bool SameRenderTargets(const RenderState& a, const RenderState& b) {
	const auto same = [](const RenderAttachment& x, const RenderAttachment& y) {
		return x.image_view == y.image_view && x.image_layout == y.image_layout &&
		       x.has_depth == y.has_depth && x.has_stencil == y.has_stencil;
	};
	if (a.width != b.width || a.height != b.height || a.num_layers != b.num_layers ||
	    a.num_color_attachments != b.num_color_attachments ||
	    !same(a.depth_stencil_attachment, b.depth_stencil_attachment)) {
		return false;
	}
	for (uint32_t i = 0; i < a.num_color_attachments; i++) {
		if (!same(a.color_attachments[i], b.color_attachments[i])) {
			return false;
		}
	}
	return true;
}

} // namespace

CommandBuffer::CommandBuffer(CommandScheduler& scheduler)
    : m_context(scheduler.Context()), m_graphics(scheduler.Graphics()) {}

bool CommandBuffer::IsInvalid() const {
	// Not m_buffer: with a record thread the handle belongs to that thread until the queue is
	// drained, while "a command buffer is open" is a decision of the resolving thread.
	return !m_active;
}

vk::CommandBuffer CommandBuffer::Handle() const {
	m_handle_uses++;
	EXIT_IF(IsInvalid());
	// A command recorded here while a packet is being filled would be executed before that packet,
	// not after it: the drain below only waits for what is already published.
	EXIT_IF(m_recorder != nullptr && m_recorder->HasOpenRecord());
	if (m_recorder != nullptr) {
		// Gate "recbatch": records ended without a publish go first. The drain below waits only for
		// published records, and this direct write would otherwise be recorded ahead of them.
		m_recorder->PublishStaged();
		// Transitional (M3 step 0): this site still records vkCmd* itself. Let the record thread
		// finish everything published so far - that also publishes m_buffer - and then record
		// into the same buffer on this thread. Callers keep the returned handle for a whole draw
		// or dispatch, so nothing may be published to the recorder before the next Handle(): the
		// record thread would call vkCmd* on the same VkCommandBuffer while they still record.
		namespace FS  = Common::FrameStats;
		const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
		if (m_recorder->Backlog() != 0) {
			// The costly kind: this thread now waits for the record thread (rec_direct_busy).
			FS::Add(FS::Counter::RecordDirectBusy, 1);
		}
		m_recorder->Drain();
		FS::Add(FS::Counter::RecordDirect, 1);
		if (t0 != 0) {
			FS::Add(FS::Counter::RecordDirectNs, FS::NowNs() - t0);
		}
	}
	return m_buffer;
}

void CommandBuffer::BeginRecorded(uint64_t tick) {
	EXIT_IF(m_rendering || m_recorder == nullptr);
	// One use for beginning the buffer, as the direct path counts through Begin()'s Handle(): with
	// zero uses the first global barrier of the recording would look redundant (KYTY_BARRIER_DEDUP).
	m_handle_uses          = 1;
	m_barrier_mark         = 0;
	m_pending_shader_write = {};
	// Same reset as Begin(): the GDS barrier state belongs to one recording, and the first
	// consumer of a new command buffer has to pay its barrier again.
	m_gds_barrier_host_epoch   = 0;
	m_gds_barrier_shader_epoch = 0;
	m_gds_barrier_consumer     = 0;
	InvalidateGraphicsState();
	m_recorder->PushBeginBuffer(tick);
}

void CommandBuffer::EndRecorded(const RecordSubmit& request) const {
	EXIT_IF(m_recorder == nullptr);
	// Nothing holds a handle here, so with gate "recpack" the pass end is a record too: a direct
	// one would make every submit wait until the whole buffer has been recorded.
	if (PacketsWanted()) {
		EndRenderingPacket(RenderPassEnd::Submit);
	} else {
		EndRendering(RenderPassEnd::Submit);
	}
	m_recorder->PushEndBuffer(request);
}

void CommandBuffer::Begin() {
	EXIT_IF(m_rendering || IsInvalid());
	m_handle_uses  = 0;
	m_barrier_mark = 0;
	m_pending_shader_write = {};
	m_gds_barrier_host_epoch   = 0;
	m_gds_barrier_shader_epoch = 0;
	m_gds_barrier_consumer     = 0;
	InvalidateGraphicsState();
	auto buffer = Handle();

	vk::CommandBufferBeginInfo begin_info {};
	begin_info.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;

	auto result = buffer.begin(&begin_info);

	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
}

void CommandBuffer::End() const {
	EndRendering(RenderPassEnd::Submit);
	auto buffer = Handle();

	auto result = buffer.end();

	EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
}

void CommandBuffer::SetDebugInfo(uint32_t op, uint64_t submit_id, uint32_t arg0, uint32_t arg1,
                                 uint32_t arg2, uint32_t arg3, uint64_t arg4, uint64_t arg5) {
	m_debug_op        = op;
	m_debug_submit_id = submit_id;
	m_debug_arg0      = arg0;
	m_debug_arg1      = arg1;
	m_debug_arg2      = arg2;
	m_debug_arg3      = arg3;
	m_debug_arg4      = arg4;
	m_debug_arg5      = arg5;
	// m_buffer belongs to the record thread until the next drain, so it must not be read here.
	// Nothing is lost: RecordThreadWanted refuses the record thread whenever a checkpoint or
	// breadcrumb mode is on, so the two are never both active.
	RecordGpuCheckpoint(m_graphics, m_context.GetCommandScheduler(),
	                    m_recorder != nullptr ? vk::CommandBuffer {nullptr} : m_buffer, m_rendering,
	                    op, submit_id, arg0, arg1, arg2, arg3, arg4, arg5);
}

bool CommandBuffer::PacketsWanted() const {
	return m_recorder != nullptr && Common::Gates::Enabled(Common::Gates::Gate::RecordPackets) &&
	       !GpuTimeProfiler::Enabled();
}

uint64_t CommandBuffer::PublishMark() const noexcept {
	return m_recorder != nullptr ? m_recorder->Published() : uint64_t {0};
}

void CommandBuffer::CheckNoPublish(uint64_t mark) const {
	static const bool check = [] {
		const auto* value = std::getenv("KYTY_RECORD_CHECK");
		return value != nullptr && value[0] == '1';
	}();
	if (check && PublishMark() != mark) {
		EXIT("RecordCheck: a record was published while a vk::CommandBuffer taken before it was still "
		     "in use (published: %llu at take, %llu now)\n",
		     static_cast<unsigned long long>(mark), static_cast<unsigned long long>(PublishMark()));
	}
}

void CommandBuffer::BeginRendering(const RenderState& state) const {
	BeginRenderingImpl(state, false);
}

void CommandBuffer::BeginRenderingPacket(const RenderState& state) const {
	BeginRenderingImpl(state, true);
}

void CommandBuffer::EndRendering(RenderPassEnd why) const {
	EndRenderingImpl(why, false);
}

void CommandBuffer::EndRenderingPacket(RenderPassEnd why) const {
	EndRenderingImpl(why, true);
}

void CommandBuffer::ShaderWriteBarrierPacket(vk::PipelineStageFlags stages) const {
	Common::DrawStat::Cut(Common::DrawStat::EdgeBarrier);
	EXIT_IF(m_recorder == nullptr || !stages);
	m_handle_uses++;
	m_recorder->PushPassEnd(false, stages);
	// Gate "recbatch": this barrier follows its draw's Commands record (renderDraw.cpp), so no later
	// record of that draw carries it; publish it together with the pass end staged before it.
	m_recorder->PublishStaged();
}

void CommandBuffer::PushBindingsPacket(vk::PipelineBindPoint bind_point, vk::PipelineLayout layout,
                                       vk::DescriptorSet set, vk::ShaderStageFlags push_stages,
                                       std::span<const uint32_t>                 push,
                                       std::span<const vk::WriteDescriptorSet>   writes,
                                       std::span<const vk::DescriptorBufferInfo> buffers,
                                       std::span<const vk::DescriptorImageInfo>  images) const {
	EXIT_IF(m_recorder == nullptr);
	m_handle_uses++;
	m_recorder->PushBindings(bind_point, layout, set, push_stages, push, writes, buffers, images);
}

void CommandBuffer::BeginRenderingImpl(const RenderState& state, bool packet) const {
	if (m_rendering && m_render_state == state) {
		return;
	}
	EXIT_IF(state.width == 0 || state.height == 0 || state.num_layers == 0 ||
	        state.num_color_attachments > RENDER_COLOR_ATTACHMENTS_MAX);
	EXIT_IF(packet && m_recorder == nullptr);
	EndRenderingImpl(RenderPassEnd::State, packet);
	Common::FrameStats::Add(Common::FrameStats::Counter::RenderPassBegins, 1);
	if (m_closed_valid) {
		m_closed_valid = false;
		if (SameRenderTargets(m_closed_state, state)) {
			Common::FrameStats::Add(
			    RenderPassEndCounter(Common::FrameStats::Counter::RpRestartState, m_closed_why), 1);
		}
	}

	if (packet) {
		m_handle_uses++;
		m_recorder->PushPassBegin(state);
	} else {
		RecordBeginRendering(Handle(), state);
	}
	m_render_state = state;
	m_rendering    = true;
	if (!packet && GpuTimeProfiler::Enabled()) {
		m_context.GetCommandScheduler().GpuMark(GpuTimeProfiler::Kind::RenderPass, 1,
		                                        state.num_color_attachments);
	}
}

void RecordBeginRendering(vk::CommandBuffer command, const RenderState& state) {
	std::array<vk::RenderingAttachmentInfo, RENDER_COLOR_ATTACHMENTS_MAX> colors {};
	for (uint32_t i = 0; i < state.num_color_attachments; i++) {
		const auto& attachment = state.color_attachments[i];
		colors[i].imageView    = attachment.image_view;
		colors[i].imageLayout  = attachment.image_layout;
		colors[i].loadOp =
		    attachment.is_clear ? vk::AttachmentLoadOp::eClear : vk::AttachmentLoadOp::eLoad;
		colors[i].storeOp                 = vk::AttachmentStoreOp::eStore;
		colors[i].clearValue.color.uint32 = attachment.clear_value;
	}

	const auto&                 depth_stencil = state.depth_stencil_attachment;
	vk::RenderingAttachmentInfo depth {};
	depth.imageView   = depth_stencil.image_view;
	depth.imageLayout = depth_stencil.image_layout;
	depth.loadOp =
	    depth_stencil.depth_clear ? vk::AttachmentLoadOp::eClear : vk::AttachmentLoadOp::eLoad;
	depth.storeOp                       = vk::AttachmentStoreOp::eStore;
	depth.clearValue.depthStencil.depth = std::bit_cast<float>(depth_stencil.clear_value[0]);

	vk::RenderingAttachmentInfo stencil {};
	stencil.imageView   = depth_stencil.image_view;
	stencil.imageLayout = depth_stencil.image_layout;
	stencil.loadOp =
	    depth_stencil.stencil_clear ? vk::AttachmentLoadOp::eClear : vk::AttachmentLoadOp::eLoad;
	stencil.storeOp                         = vk::AttachmentStoreOp::eStore;
	stencil.clearValue.depthStencil.stencil = depth_stencil.clear_value[1];

	vk::RenderingInfo rendering {};
	rendering.renderArea.extent    = {state.width, state.height};
	rendering.layerCount           = state.num_layers;
	rendering.colorAttachmentCount = state.num_color_attachments;
	rendering.pColorAttachments    = colors.data();
	rendering.pDepthAttachment     = depth_stencil.has_depth ? &depth : nullptr;
	rendering.pStencilAttachment   = depth_stencil.has_stencil ? &stencil : nullptr;
	command.beginRendering(rendering);
}

void CommandBuffer::EndRenderingImpl(RenderPassEnd why, bool packet) const {
	// Packet pass changes are taken only where GPU-time marks are off: marks record through Handle().
	EXIT_IF(packet && (m_recorder == nullptr || GpuTimeProfiler::Enabled()));
	if (!m_rendering) {
		// A debt without an open pass cannot happen today (it is only taken on while rendering),
		// but if it ever does, paying it here is the difference between a barrier and no barrier.
		if (m_pending_shader_write) {
			const auto stages      = m_pending_shader_write;
			m_pending_shader_write = {};
			Common::FrameStats::Add(Common::FrameStats::Counter::ShaderWriteBarriersFlushed, 1);
			Common::DrawStat::Cut(Common::DrawStat::EdgeBarrier);
			if (packet) {
				m_handle_uses++;
				m_recorder->PushPassEnd(false, stages);
			} else {
				ShaderWriteBarrier(Handle(), stages);
			}
		}
		return;
	}
	if (!packet) {
		Handle().endRendering();
	}
	m_rendering = false;
	Common::DrawStat::Cut(Common::DrawStat::EdgePass);
	if (Common::FrameStats::Enabled()) {
		Common::FrameStats::Add(RenderPassEndCounter(Common::FrameStats::Counter::RpEndState, why),
		                        1);
		m_closed_state = m_render_state;
		m_closed_why   = why;
		m_closed_valid = true;
	}
	m_render_state = {};
	if (!packet && GpuTimeProfiler::Enabled()) {
		m_context.GetCommandScheduler().GpuMark(GpuTimeProfiler::Kind::RenderPass, 2);
	}
	const auto stages      = m_pending_shader_write;
	m_pending_shader_write = {};
	if (stages) {
		Common::FrameStats::Add(Common::FrameStats::Counter::ShaderWriteBarriersFlushed, 1);
		Common::DrawStat::Cut(Common::DrawStat::EdgeBarrier);
	}
	if (packet) {
		// One record: the pass end, then the wide barrier the pass owed.
		m_handle_uses++;
		m_recorder->PushPassEnd(true, stages);
	} else if (stages) {
		ShaderWriteBarrier(Handle(), stages);
	}
}

} // namespace Libs::Graphics
