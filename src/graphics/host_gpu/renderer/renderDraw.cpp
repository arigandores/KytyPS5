#include "graphics/host_gpu/renderer/renderDraw.h"

#include "graphics/presentation/renderDoc.h"

#include "common/frameStats.h"
#include "common/gates.h"
#include "common/rk3Census.h"

#include "common/assert.h"
#include "common/drawStat.h"
#include "common/common.h"
#include "common/envFlag.h"
#include "common/file.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/stringUtils.h"
#include "common/threads.h"
#include "graphics/guest_gpu/gpu_defs.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/guest_gpu/sliceCensus.h"
#include "graphics/guest_gpu/tile.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/commandRecorder.h"
#include "graphics/host_gpu/renderer/debug.h"
#include "graphics/host_gpu/renderer/depthRenderTarget.h"
#include "graphics/host_gpu/renderer/gpuCheckpoints.h"
#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"
#include "graphics/host_gpu/renderer/pipeline/shaderResourceBarrier.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/host_gpu/renderer/renderMemo.h"
#include "graphics/host_gpu/renderer/diagF5.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/BufferFormat.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"
#include "graphics/shader/shader.h"
#include "kernel/eventQueue.h"
#include "kernel/memory.h"
#include "kernel/pthread.h"
#include "libs/errno.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <mutex>
#include <tuple>
#include <type_traits>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <unordered_map>
#include <vector>

namespace Libs::Graphics {

std::pair<int32_t, uint32_t> ResolveDrawOffsets(uint32_t index_offset,
	                                           const ShaderVertexInputInfo& vs_input_info) {
	auto     vertex_offset   = static_cast<int32_t>(index_offset);
	uint32_t instance_offset = 0;
	if (!vs_input_info.fetch_embedded) {
		return {vertex_offset, instance_offset};
	}

	EXIT_IF(!vs_input_info.stage);
	const auto& program   = *vs_input_info.stage.program;
	const auto& resources = vs_input_info.stage.resources;
	if (index_offset == 0 &&
	    program.info.vertex_offset_sgpr >= static_cast<int32_t>(program.user_data_base)) {
		const auto index =
		    static_cast<uint32_t>(program.info.vertex_offset_sgpr) - program.user_data_base;
		if (index < resources.user_data.size()) {
			vertex_offset = static_cast<int32_t>(resources.user_data[index]);
		}
	}
	if (program.info.instance_offset_sgpr >= static_cast<int32_t>(program.user_data_base)) {
		const auto index =
		    static_cast<uint32_t>(program.info.instance_offset_sgpr) - program.user_data_base;
		if (index < resources.user_data.size()) {
			instance_offset = resources.user_data[index];
		}
	}

	return {vertex_offset, instance_offset};
}

std::vector<MeshIndexRange> SplitMeshRestartIndices(std::span<const uint8_t> indices,
                                                    uint32_t element_size) {
	EXIT_IF(element_size != 1 && element_size != 2 && element_size != 4);
	EXIT_IF(indices.size() % element_size != 0 || indices.size() / element_size > UINT32_MAX);
	const auto count = static_cast<uint32_t>(indices.size() / element_size);
	const auto marker = UINT32_MAX >> ((4 - element_size) * 8);
	std::vector<MeshIndexRange> ranges;
	uint32_t first = 0;
	for (uint32_t i = 0; i < count; ++i) {
		uint32_t index = 0;
		std::memcpy(&index, indices.data() + static_cast<size_t>(i) * element_size, element_size);
		if (index == marker) {
			if (i != first) {
				ranges.push_back({first, i - first});
			}
			first = i + 1;
		}
	}
	if (first != count) {
		ranges.push_back({first, count - first});
	}
	return ranges;
}

static std::atomic<uint32_t> g_draw_state_log_count   = 0;
static std::atomic<uint32_t> g_draw_input_log_count   = 0;
static std::atomic<uint32_t> g_mrt_state_log_count    = 0;

static std::atomic<uint32_t> g_framebuffer_skip_log_count = 0;

static float ConvertPolygonOffsetConstantFactor(float guest_factor, const HW::PolyOffset& offset,
                                                vk::Format host_depth_format) {
	if (offset.db_is_float_fmt) {
		return guest_factor;
	}

	int host_depth_bits = 0;
	switch (host_depth_format) {
		case vk::Format::eD16Unorm:
		case vk::Format::eD16UnormS8Uint: host_depth_bits = 16; break;
		case vk::Format::eD24UnormS8Uint: host_depth_bits = 24; break;
		default:
			// A fixed-point guest bias cannot be represented exactly by a floating-point host
			// attachment without VK_EXT_depth_bias_control.
			return guest_factor;
	}
	return std::ldexp(guest_factor, host_depth_bits + offset.neg_num_db_bits);
}

static const char* RenderColorTypeName(const RenderColorInfo& color) {
	return color.image_id ? "RenderTexture" : "NoColorOutput";
}

static void LogFramebufferSkip(const char* draw_name, const RenderColorInfo& color,
                               const RenderDepthInfo& depth, const CommandBuffer& buffer,
                               uint32_t index_count, uint32_t flags) {
	const auto& ctx  = buffer.GetRegisters();
	const auto& ucfg = buffer.GetUserConfig();
	if (!graphics_debug_dump_enabled()) {
		return;
	}

	auto log_id = g_framebuffer_skip_log_count.fetch_add(1, std::memory_order_relaxed);
	if (log_id >= 128) {
		return;
	}

	LOGF(
	    "DrawFramebufferSkip[%u]: %s color=%s color_addr=0x%010" PRIx64 " color_size=0x%016" PRIx64
	    " color_image=%s depth_format=%s depth_image=%s depth_vaddr_num=%d target_mask=0x%08" PRIx32
	    " prim=%u index_count=%u flags=0x%08" PRIx32 "\n",
	    log_id, draw_name, RenderColorTypeName(color), color.desc.info.data.address,
	    color.desc.info.data.size, color.image_id ? "yes" : "no",
	    vk::to_string(depth.desc.view_info.format).c_str(), depth.image_id ? "yes" : "no",
	    static_cast<int>(!depth.desc.info.data.Empty()) +
	        static_cast<int>(depth.desc.info.HasStencil()),
	    ctx.GetRenderTargetMask(), static_cast<uint32_t>(ucfg.GetPrimType()), index_count, flags);
}

static void LogMrtState(const char* draw_name, const CommandBuffer& buffer,
                        const ShaderPixelInputInfo& ps_input_info) {
	const auto& ctx            = buffer.GetRegisters();
	const auto& sh_regs        = ctx.GetShaderRegisters();
	const auto  rt_mask        = ctx.GetRenderTargetMask();
	const auto  cb_shader_mask = sh_regs.m_cbShaderMask;
	const auto& bc0            = ctx.GetBlendControl(0);

	auto log_id = g_mrt_state_log_count.fetch_add(1);
	if (log_id >= 32) {
		return;
	}

	LOGF("MrtState[%u]: %s rt_mask=0x%08" PRIx32 " cb_shader_mask=0x%08" PRIx32
	     " blend0=%s src=%u dst=%u alpha_src=%u alpha_dst=%u sep_alpha=%s\n",
	     log_id, draw_name, rt_mask, cb_shader_mask, bc0.enable ? "true" : "false",
	     bc0.color_srcblend, bc0.color_destblend, bc0.alpha_srcblend, bc0.alpha_destblend,
	     bc0.separate_alpha_blend ? "true" : "false");

	for (uint32_t i = 0; i < 8; i++) {
		const auto& rt  = ctx.GetRenderTarget(i);
		const auto& bc  = ctx.GetBlendControl(i);
		const auto  ctm = (rt_mask >> (i * 4u)) & 0x0fu;
		const auto  csm = (cb_shader_mask >> (i * 4u)) & 0x0fu;

		if (rt.base.addr == 0 && ps_input_info.target_output_mode[i] == 0 && ctm == 0 && csm == 0 &&
		    !bc.enable) {
			continue;
		}

		LOGF("MrtState[%u]: slot=%u addr=0x%010" PRIx64
		     " target_mask=0x%x shader_mask=0x%x out_mode=%u"
		     " fmt=0x%08" PRIx32 " nfmt=0x%08" PRIx32 " order=0x%08" PRIx32
		     " width=%u height=%u tile=%u"
		     " blend=%s src=%u dst=%u alpha_src=%u alpha_dst=%u\n",
		     log_id, i, rt.base.addr, ctm, csm, ps_input_info.target_output_mode[i],
		     static_cast<uint32_t>(rt.info.format), static_cast<uint32_t>(rt.info.channel_type),
		     static_cast<uint32_t>(rt.info.channel_order), rt.attrib2.width + 1,
		     rt.attrib2.height + 1, static_cast<uint32_t>(rt.attrib3.tile_mode),
		     bc.enable ? "true" : "false", bc.color_srcblend, bc.color_destblend, bc.alpha_srcblend,
		     bc.alpha_destblend);
	}
}

static void LogDrawTargetState(const char* draw_name, const RenderColorInfo& color,
                               const RenderDepthInfo& depth, const CommandBuffer& buffer,
                               const ShaderPixelInputInfo& ps_input_info, uint32_t index_count,
                               uint32_t flags) {
	const auto& ctx  = buffer.GetRegisters();
	const auto& ucfg = buffer.GetUserConfig();
	if (!color.image_id) {
		return;
	}

	auto log_id = g_draw_state_log_count.fetch_add(1);
	if (log_id >= 192) {
		return;
	}

	const auto& cc             = ctx.GetColorControl();
	const auto& bc             = ctx.GetBlendControl(color.target_slot);
	const auto& dc             = ctx.GetDepthControl();
	const auto& vp             = ctx.GetScreenViewport();
	const auto& vp0            = vp.viewports[0];
	const auto& ps_resources   = ps_input_info.stage.program->info;
	const auto  sampled_images = std::count_if(
	    ps_resources.images.begin(), ps_resources.images.end(), [](const auto& image) {
		    return image.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled;
	    });

	const auto extent = color.Extent();
	const auto sc     = calc_final_scissor(vp, ctx.GetScanModeControl(), extent, 0);

	LOGF(
	    "DrawTargetState[%u]: frame=%d %s target=%s addr=0x%010" PRIx64
	    " extent=%ux%u prim=%u index_count=%u flags=0x%08" PRIx32 " color_mask=0x%08" PRIx32
	    " cc_mode=%u cc_op=0x%02x"
	    " blend=%s src=%u dst=%u comb=%u ps_tex=%d sampled=%d storage=%d ps_kill=%s target_mode0=%u"
	    " depth_test=%s depth_write=%s depth_func=%u depth_clear=%s viewport=(%.1f,%.1f %.1fx%.1f) "
	    "scissor=(%d,%d)-(%d,%d)\n",
	    log_id, buffer.GetContext().GetGpu().GetFrameNum(), draw_name, RenderColorTypeName(color),
	    color.desc.info.data.address, extent.width, extent.height,
	    static_cast<uint32_t>(ucfg.GetPrimType()), index_count, flags, ctx.GetRenderTargetMask(),
	    cc.mode, cc.op,
	    bc.enable ? "true" : "false", bc.color_srcblend, bc.color_destblend, bc.color_comb_fcn,
	    static_cast<int>(ps_resources.images.size()), static_cast<int>(sampled_images),
	    static_cast<int>(ps_resources.images.size() - sampled_images),
	    ps_input_info.ps_pixel_kill_enable ? "true" : "false", ps_input_info.target_output_mode[0],
	    dc.z_enable ? "true" : "false", dc.z_write_enable ? "true" : "false", dc.zfunc,
	    depth.depth_clear_enable ? "true" : "false", vp0.xoffset - vp0.xscale,
	    vp0.yoffset - vp0.yscale, vp0.xscale * 2.0f, vp0.yscale * 2.0f, sc.left, sc.top, sc.right,
	    sc.bottom);

	LogMrtState(draw_name, buffer, ps_input_info);
}

static void LogDrawInputState(const CommandBuffer& buffer, const RenderColorInfo& color,
                              const ShaderVertexInputInfo& vs_input_info,
                              uint32_t index_type_and_size, uint32_t index_count,
                              const void* index_addr) {
	auto log_id = g_draw_input_log_count.fetch_add(1);
	if (log_id >= 64) {
		return;
	}

	LOGF("DrawInputState[%u]: frame=%d target=%s addr=0x%010" PRIx64
	     " index_type=%u index_count=%u index_addr=0x%016" PRIx64
	     " vs_resources=%d vs_buffers=%d\n",
	     log_id, buffer.GetContext().GetGpu().GetFrameNum(), RenderColorTypeName(color),
	     color.desc.info.data.address, index_type_and_size, index_count,
	     reinterpret_cast<uint64_t>(index_addr), vs_input_info.resources_num,
	     vs_input_info.buffers_num);

	for (int bi = 0; bi < vs_input_info.buffers_num; bi++) {
		const auto& b = vs_input_info.buffers[bi];
		LOGF("DrawInputState[%u]: vb[%d] addr=0x%010" PRIx64
		     " stride=%u records=%u fetch_index=%u attr_num=%d\n",
		     log_id, bi, b.addr, b.stride, b.num_records, b.fetch_index, b.attr_num);

		const auto* bytes = reinterpret_cast<const uint8_t*>(b.addr);
		if (bytes != nullptr && b.stride != 0) {
			const uint32_t records = std::min<uint32_t>(b.num_records, 4u);
			for (uint32_t rec = 0; rec < records; rec++) {
				const auto* rec_bytes = bytes + static_cast<uint64_t>(rec) * b.stride;
				const auto  dword_num = std::min<uint32_t>(b.stride / 4u, 12u);
				uint32_t    raw[12]   = {};
				float       flt[12]   = {};
				for (uint32_t i = 0; i < dword_num; i++) {
					std::memcpy(&raw[i], rec_bytes + i * 4u, sizeof(raw[i]));
					std::memcpy(&flt[i], rec_bytes + i * 4u, sizeof(flt[i]));
				}
				LOGF("DrawInputState[%u]: vb[%d].rec[%u] stride=%u dwords=%u raw=%08" PRIx32
				     " %08" PRIx32 " %08" PRIx32 " %08" PRIx32 " %08" PRIx32 " %08" PRIx32
				     " %08" PRIx32 " %08" PRIx32 " %08" PRIx32
				     " f=(%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f)\n",
				     log_id, bi, rec, b.stride, dword_num, raw[0], raw[1], raw[2], raw[3], raw[4],
				     raw[5], raw[6], raw[7], raw[8], flt[0], flt[1], flt[2], flt[3], flt[4], flt[5],
				     flt[6], flt[7], flt[8]);

				for (int ai = 0; ai < b.attr_num; ai++) {
					const auto  res_index = b.attr_indices[ai];
					const auto& r         = vs_input_info.resources[res_index];
					const auto& rd        = vs_input_info.resources_dst[res_index];
					const auto  offset    = b.attr_offsets[ai];
					if (offset + 4u <= b.stride &&
					    r.Format() == Prospero::BufferFormat::k8_8_8_8UNorm) {
						uint32_t packed = 0;
						std::memcpy(&packed, rec_bytes + offset, sizeof(packed));
						const auto r8 = (packed >> 0u) & 0xffu;
						const auto g8 = (packed >> 8u) & 0xffu;
						const auto b8 = (packed >> 16u) & 0xffu;
						const auto a8 = (packed >> 24u) & 0xffu;
						LOGF("DrawInputState[%u]: vb[%d].rec[%u].attr[%d] dst=v%d fmt=56 "
						     "rgba8=%02" PRIx32 "%02" PRIx32 "%02" PRIx32 "%02" PRIx32
						     " rgba=(%.3f,%.3f,%.3f,%.3f)\n",
						     log_id, bi, rec, ai, rd.register_start, r8, g8, b8, a8,
						     static_cast<double>(r8) / 255.0, static_cast<double>(g8) / 255.0,
						     static_cast<double>(b8) / 255.0, static_cast<double>(a8) / 255.0);
					}
				}
			}
		}

		for (int ai = 0; ai < b.attr_num; ai++) {
			const auto  res_index = b.attr_indices[ai];
			const auto& r         = vs_input_info.resources[res_index];
			const auto& rd        = vs_input_info.resources_dst[res_index];
			LOGF("DrawInputState[%u]: attr[%d] res=%d offset=%u dst=v%d regs=%d fetch_index=%u "
			     "sharp=%08" PRIx32 " %08" PRIx32 " %08" PRIx32 " %08" PRIx32 "\n",
			     log_id, ai, res_index, b.attr_offsets[ai], rd.register_start, rd.registers_num,
			     rd.fetch_index, r.fields[0], r.fields[1], r.fields[2], r.fields[3]);
		}
	}
}

// Upstream bce8924 / 586cbd4 / 940e42f / 29e9ea6 / 9a74ef1: the stencil test, the per-face ops,
// masks and reference are dynamic state now (the pipeline no longer bakes them, see the dynamic
// state list in shaders.cpp), and the two faces carry independent values.
// The record sink of gate "recpack" carries all five commands (RecordCmd::SetStencilTestEnable,
// SetStencilOp and the three masks, commandRecorder.h), so this state goes through the same
// sink as the rest of the dynamic state instead of draining the record ring for a direct
// handle. The dynamic-state cache of session 57 still decides whether anything is emitted at
// all: a scene keeps one stencil setup for hundreds of draws.
static bool StencilDynamicParamsChanged(const CommandBuffer& buffer, const RenderDepthInfo& depth) {
	// No short-circuit: every slot that describes the state we are about to emit must be updated.
	bool changed =
	    buffer.GraphicsStateChanged(GraphicsStateSlot::StencilTestEnable, depth.stencil_test_enable);
	if (depth.stencil_test_enable) {
		changed = buffer.GraphicsStateChanged(GraphicsStateSlot::StencilFront, depth.stencil_front) ||
		          changed;
		changed = buffer.GraphicsStateChanged(GraphicsStateSlot::StencilBack, depth.stencil_back) ||
		          changed;
	}
	return changed;
}

template <typename Sink>
static void SetStencilDynamicParams(Sink& vk_buffer, const RenderDepthInfo& depth) {
	vk_buffer.setStencilTestEnable(depth.stencil_test_enable ? VK_TRUE : VK_FALSE);
	if (depth.stencil_test_enable) {
		const auto set_stencil = [&](vk::StencilFaceFlagBits face, const vk::StencilOpState& state) {
			vk_buffer.setStencilOp(face, state.failOp, state.passOp, state.depthFailOp,
			                       state.compareOp);
			vk_buffer.setStencilCompareMask(face, state.compareMask);
			vk_buffer.setStencilWriteMask(face, state.writeMask);
			vk_buffer.setStencilReference(face, state.reference);
		};
		set_stencil(vk::StencilFaceFlagBits::eFront, depth.stencil_front);
		set_stencil(vk::StencilFaceFlagBits::eBack, depth.stencil_back);
	}
}

// Sink: vk::CommandBuffer, or RecordCommandWriter on the gate "recpack" path; both spell the calls
// alike, so the decisions below are shared.
template <typename Sink>
static void SetGraphicsDynamicParams(const CommandBuffer& buffer, Sink& vk_buffer,
                                     const ShaderVertexInputInfo& vs_input_info,
                                     const RenderColorInfo* colors, uint32_t color_count,
                                     const RenderDepthInfo& depth) {
	KYTY_PROFILER_FUNCTION();

	EXIT_IF(colors == nullptr);
	const auto& ctx = buffer.GetRegisters();

	const auto&  vp = ctx.GetScreenViewport();
	{
		// Session 67 watchdog: the guest viewport, read from the registers rather than from the
		// `viewports` array built below, whose clip_disable branch writes maxViewportDimensions and
		// would pin the maximum for the rest of the run. yscale is negative on a flipped viewport.
		const auto& guest  = vp.viewports[0];
		const auto  width  = static_cast<uint64_t>(std::lround(std::fabs(guest.xscale) * 2.0F));
		const auto  height = static_cast<uint64_t>(std::lround(std::fabs(guest.yscale) * 2.0F));
		Common::FrameStats::NoteMax(Common::FrameStats::Gauge::VpWidth,
		                            static_cast<uint32_t>(width));
		Common::FrameStats::NoteMax(Common::FrameStats::Gauge::VpHeight,
		                            static_cast<uint32_t>(height));
		Common::FrameStats::Add(Common::FrameStats::Counter::VpPixelsK, width * height / 1024U);
	}
	vk::Extent2D framebuffer_extent {};
	if (color_count > 0 && colors[0].image_id) {
		framebuffer_extent = colors[0].Extent();
	} else if (depth.image_id) {
		framebuffer_extent = {depth.desc.info.extent.width, depth.desc.info.extent.height};
	} else {
		const auto& limits = buffer.GetGraphics().GetPhysicalDeviceProperties().limits;
		framebuffer_extent = {limits.maxFramebufferWidth, limits.maxFramebufferHeight};
	}

	const auto& outputs = vs_input_info.stage.program->info.outputs;
	const bool  indexed_viewports =
	    std::any_of(outputs.begin(), outputs.end(), [](const auto& output) {
		    return output.kind == ShaderRecompiler::IR::StageOutputKind::ViewportIndex;
	    });
	constexpr uint32_t viewport_slots = std::size(HW::ScreenViewport {}.viewports);
	std::array<vk::Viewport, viewport_slots> viewports {};
	std::array<vk::Rect2D, viewport_slots>   scissors {};
	const uint32_t viewport_count = indexed_viewports ? viewport_slots : 1;
	for (uint32_t i = 0; i < viewport_count; i++) {
		const auto& guest    = vp.viewports[i];
		auto&       viewport = viewports[i];
		if (ctx.GetClipControl().clip_disable) {
			const auto& limits = buffer.GetGraphics().GetPhysicalDeviceProperties().limits;
			viewport.width  = static_cast<float>(std::min(limits.maxViewportDimensions[0], 16384u));
			viewport.height = static_cast<float>(std::min(limits.maxViewportDimensions[1], 16384u));
		} else {
			viewport.x      = guest.xoffset - guest.xscale;
			viewport.y      = guest.yoffset - guest.yscale;
			viewport.width  = guest.xscale * 2.0f;
			viewport.height = guest.yscale * 2.0f;
		}
		viewport.minDepth =
		    guest.zoffset - (ctx.GetClipControl().dx_clip_space ? 0.0f : guest.zscale);
		viewport.maxDepth = guest.zscale + guest.zoffset;

		const auto final_scissor =
		    calc_final_scissor(vp, ctx.GetScanModeControl(), framebuffer_extent, i);
		auto& scissor  = scissors[i];
		scissor.offset = {final_scissor.left, final_scissor.top};
		scissor.extent = {static_cast<uint32_t>(final_scissor.right - final_scissor.left),
		                  static_cast<uint32_t>(final_scissor.bottom - final_scissor.top)};
		if (viewport.width == 0.0f) {
			// Keep empty slots at their guest index; Vulkan requires a positive viewport width.
			viewport.width = 1.0f;
			scissor.extent = {0, 0};
		}
	}
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::Viewports, viewports.data(),
	                                viewport_count * sizeof(viewports[0]))) {
		vk_buffer.setViewportWithCount(viewport_count, viewports.data());
	}
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::Scissors, scissors.data(),
	                                viewport_count * sizeof(scissors[0]))) {
		vk_buffer.setScissorWithCount(viewport_count, scissors.data());
	}

	float line_width = ctx.GetLineWidth();
	if (line_width != 1.0f) {
		static bool logged = false;
		if (!logged) {
			LOGF("Render: temporary: clamping Vulkan line width %f to 1.0 because wideLines is "
			     "not enabled\n",
			     line_width);
			logged = true;
		}
		line_width = 1.0f;
	}
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::LineWidth, line_width)) {
		vk_buffer.setLineWidth(line_width);
	}
	const auto&      blend = ctx.GetBlendColor();
	const std::array blend_constants {blend.red, blend.green, blend.blue, blend.alpha};
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::BlendConstants, blend_constants)) {
		vk_buffer.setBlendConstants(blend_constants.data());
	}
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthTest, depth.depth_test_enable)) {
		vk_buffer.setDepthTestEnable(depth.depth_test_enable ? VK_TRUE : VK_FALSE);
	}
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthWrite, depth.depth_write_enable)) {
		vk_buffer.setDepthWriteEnable(depth.depth_write_enable ? VK_TRUE : VK_FALSE);
	}
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthCompare, depth.depth_compare_op)) {
		vk_buffer.setDepthCompareOp(depth.depth_compare_op);
	}

	const auto& mode              = ctx.GetModeControl();
	const auto& poly_offset       = ctx.GetPolyOffset();
	const bool  use_front         = mode.poly_offset_front_enable && !mode.cull_front;
	const bool  use_back          = mode.poly_offset_back_enable && !mode.cull_back;
	const bool  depth_bias_enable = use_front || use_back;
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthBiasEnable, depth_bias_enable)) {
		vk_buffer.setDepthBiasEnable(depth_bias_enable ? VK_TRUE : VK_FALSE);
	}
	if (depth_bias_enable) {
		// Vulkan has one bias for both faces. Prefer a visible front face when both are enabled.
		const float guest_constant_factor =
		    use_front ? poly_offset.front_offset : poly_offset.back_offset;
		const float constant_factor = ConvertPolygonOffsetConstantFactor(
		    guest_constant_factor, poly_offset, depth.desc.view_info.format);
		const float slope_factor =
		    (use_front ? poly_offset.front_scale : poly_offset.back_scale) / 16.0f;
		const std::array bias {constant_factor, poly_offset.clamp, slope_factor};
		if (buffer.GraphicsStateChanged(GraphicsStateSlot::DepthBias, bias)) {
			vk_buffer.setDepthBias(constant_factor, poly_offset.clamp, slope_factor);
		}
	}

	// The stencil dynamic state is not written here: it is guarded as a group by
	// StencilDynamicParamsChanged / SetStencilDynamicParams (see above), which both draw paths
	// call on the same sink right after this function.

#if defined(__APPLE__)
	// MoltenVK has no VK_EXT_color_write_enable; the pipeline is created without the
	// eColorWriteEnableEXT dynamic state and relies on the static colorWriteMask instead.
#else
	vk::Bool32 enable[RENDER_COLOR_ATTACHMENTS_MAX] = {};
	uint32_t attachment_count = 0;
	// Color-control operation selects special color-buffer paths, not the normal component write
	// mask. Attachment availability therefore follows the target write mask.
	for (uint32_t i = 0; i < color_count; i++) {
		const auto slot = colors[i].target_slot;
		EXIT_IF(slot >= RENDER_COLOR_ATTACHMENTS_MAX);
		attachment_count = std::max(attachment_count, slot + 1);
		enable[slot] = render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0
		                ? VK_TRUE
		                : VK_FALSE;
	}
	if (attachment_count != 0 &&
	    buffer.GraphicsStateChanged(GraphicsStateSlot::ColorWrite, enable,
	                                attachment_count * sizeof(enable[0]))) {
		vk_buffer.setColorWriteEnableEXT(attachment_count, enable);
	}
#endif
}

// Session 57, E1/E2 (gate "drawstat", common/drawStat.h). A draw's preparation runs from the
// render mutex to AcquireRenderTargets and its tail from there to the draw command; both masks are
// counted when the draw command is recorded (packet and direct path), where runs close too. Draws
// that return early (metadata/copy draws, no targets, pipeline still compiling) are not counted.
namespace {

constinit thread_local uint32_t t_draw_pure_run = 0; // E1: draws of the open run without blocking bits
constinit thread_local uint32_t t_draw_edge_run = 0; // E2: draws since the last hard boundary

void DrawStatAdd(Common::FrameStats::Counter first, uint32_t index, uint64_t value) {
	Common::FrameStats::Add(static_cast<Common::FrameStats::Counter>(static_cast<uint32_t>(first) + index),
	                        value);
}

void DrawStatCloseRun(uint32_t& run, Common::FrameStats::Counter runs, Common::FrameStats::Counter draws) {
	if (run != 0) {
		const auto bucket = Common::DrawStat::RunBucket(run);
		DrawStatAdd(runs, bucket, 1);
		DrawStatAdd(draws, bucket, run);
		run = 0;
	}
}

void DrawStatBegin() {
	const bool on = Common::Gates::Enabled(Common::Gates::Gate::DrawStat) && Common::FrameStats::Enabled();
	if (Common::DrawStat::On() != on) {
		Common::DrawStat::g_on.store(on, std::memory_order_relaxed);
		t_draw_pure_run           = 0;
		t_draw_edge_run           = 0;
		Common::DrawStat::t_edges = 0;
	}
	if (on) {
		Common::DrawStat::t_between |= Common::DrawStat::t_mask;
		Common::DrawStat::t_mask  = 0;
		Common::DrawStat::t_shift = 0;
	}
}

void DrawStatTail() {
	if (Common::DrawStat::On()) {
		Common::DrawStat::t_shift = 16;
	}
}

void DrawStatEmit() {
	namespace DS  = Common::DrawStat;
	using Counter = Common::FrameStats::Counter;
	if (!DS::On()) {
		return;
	}
	const uint32_t prep = DS::t_mask & 0xffffu;
	const uint32_t tail = DS::t_mask >> 16u;
	Common::FrameStats::Add(Counter::DrawStatDraws, 1);
	if ((prep & DS::HardMask) == 0) {
		Common::FrameStats::Add(Counter::DrawStatPure, 1);
	}
	if ((prep & (DS::HardMask | DS::SlowMask)) == 0) {
		Common::FrameStats::Add(Counter::DrawStatFast, 1);
	}
	if (prep == 0) {
		Common::FrameStats::Add(Counter::DrawStatClean, 1);
	}
	for (uint32_t bits = prep; bits != 0; bits &= bits - 1u) {
		DrawStatAdd(Counter::DrawDirtyImgNew, static_cast<uint32_t>(std::countr_zero(bits)), 1);
	}
	if ((tail & DS::HardMask) != 0) {
		Common::FrameStats::Add(Counter::DrawTailHard, 1);
		Common::FrameStats::Add(Counter::DrawTailImgUp, (tail & DS::ImgUp) != 0 ? 1u : 0u);
		Common::FrameStats::Add(Counter::DrawTailMeta, (tail & DS::Meta) != 0 ? 1u : 0u);
		Common::FrameStats::Add(Counter::DrawTailProt, (tail & DS::Prot) != 0 ? 1u : 0u);
		Common::FrameStats::Add(Counter::DrawTailSync, (tail & DS::Sync) != 0 ? 1u : 0u);
		Common::FrameStats::Add(Counter::DrawTailBarrier, (tail & DS::Barrier) != 0 ? 1u : 0u);
	}
	// Gate "dpslow": runs are cut by the slow bits too (M2 restricted to memo and epoch hits).
	const uint32_t blocking = Common::Gates::Enabled(Common::Gates::Gate::DrawStatSlow)
	                              ? (DS::HardMask | DS::SlowMask)
	                              : DS::HardMask;
	// Hard work since the previous counted draw (its tail after the draw command, early exits,
	// dispatches, DMA) invalidates what a worker would have resolved ahead: it cuts the run too.
	const uint32_t between = (DS::t_between | (DS::t_between >> 16u)) & 0xffffu;
	DS::t_between          = 0;
	if ((between & DS::HardMask) != 0) {
		Common::FrameStats::Add(Counter::DrawBetweenHard, 1);
	}
	if ((prep & blocking) == 0 && (between & blocking) == 0) {
		t_draw_pure_run++;
	} else {
		DrawStatCloseRun(t_draw_pure_run, Counter::DrawPureRuns1, Counter::DrawPureRunDraws1);
	}
	// A boundary noted since the previous draw command starts a new run with this draw.
	if (DS::t_edges != 0) {
		DrawStatCloseRun(t_draw_edge_run, Counter::EdgeRuns1, Counter::EdgeRunDraws1);
		for (uint32_t bits = DS::t_edges; bits != 0; bits &= bits - 1u) {
			DrawStatAdd(Counter::EdgeCutPass, static_cast<uint32_t>(std::countr_zero(bits)), 1);
		}
		DS::t_edges = 0;
	}
	t_draw_edge_run++;
	// What follows the draw command is work between this draw and the next one (t_between).
	DS::t_mask  = 0;
	DS::t_shift = 16;
}

using DrawStatCounter = Common::FrameStats::Counter;
static_assert(Common::DrawStat::Barrier == (1u << 15u) &&
              static_cast<uint32_t>(DrawStatCounter::DrawDirtyBarrier) -
                      static_cast<uint32_t>(DrawStatCounter::DrawDirtyImgNew) ==
                  15u);
static_assert(static_cast<uint32_t>(DrawStatCounter::DrawPureRuns64) -
                      static_cast<uint32_t>(DrawStatCounter::DrawPureRuns1) ==
                  6u &&
              static_cast<uint32_t>(DrawStatCounter::DrawPureRunDraws64) -
                      static_cast<uint32_t>(DrawStatCounter::DrawPureRunDraws1) ==
                  6u);
static_assert(static_cast<uint32_t>(DrawStatCounter::EdgeRuns64) -
                      static_cast<uint32_t>(DrawStatCounter::EdgeRuns1) ==
                  6u &&
              static_cast<uint32_t>(DrawStatCounter::EdgeRunDraws64) -
                      static_cast<uint32_t>(DrawStatCounter::EdgeRunDraws1) ==
                  6u);
static_assert(Common::DrawStat::EdgeSubmit == (1u << 4u) &&
              static_cast<uint32_t>(DrawStatCounter::EdgeCutSubmit) -
                      static_cast<uint32_t>(DrawStatCounter::EdgeCutPass) ==
                  4u);

} // namespace

static bool DrawHasValidVertexShader(const HW::Shader& sh_ctx) {

	const auto& vs = sh_ctx.GetVs();
	return ShaderAddressValid(vs.es_regs.data_addr);
}

static bool PixelShaderHasDepthOrCoverageSideEffects(const HW::ShaderRegisters& sh_regs) {
	const auto& db = sh_regs.db_shader_control;
	return db.shader_kill_enable || db.shader_z_export_enable || db.shader_mask_export_enable ||
	       db.shader_dual_export_enable || db.shader_execute_on_noop;
}

struct DrawRenderState {
	RenderDepthInfo       depth_info;
	RenderColorInfo       color_info[RENDER_COLOR_ATTACHMENTS_MAX] = {};
	uint32_t              color_count                              = 0;
	bool                  ps_active                                = true;
	std::array<ShaderVertexInputInfo, 3> vertex_info;
	ShaderPixelInputInfo  ps_input_info;
	PipelineCache::GraphicsPrograms programs;
	// Session 60, B3 (gate "progmemo"): the GetGraphicsPrograms call that last recorded into or
	// served from this object; 0 for a state no call has seen (a nested draw's local).
	uint64_t prog_memo_serial = 0;
};

// Track F, F16d (KYTY_DIAG_F6, ROADMAP s122 item 433(v)): one host draw at a recording site after the
// PrepareDrawRenderState / RtsPlaceA fork - the guest slots of the host attachments and the MRT exports of the pixel
// program by guest index (ShaderInfo::outputs, kind Mrt; the dual-source variant keeps the guest index). Reads only.
static void DiagF6NoteDraw(const CommandBuffer& buffer, const DrawRenderState& state, bool mesh, bool indirect,
                           bool indexed) {
	std::array<uint32_t, RENDER_COLOR_ATTACHMENTS_MAX> host_slots {};
	const uint32_t host_count = std::min<uint32_t>(state.color_count, RENDER_COLOR_ATTACHMENTS_MAX);
	for (uint32_t i = 0; i < host_count; i++) {
		host_slots[i] = state.color_info[i].target_slot;
	}
	const auto&              ps        = state.ps_input_info.stage;
	const bool               ps_on     = state.ps_active && ps;
	std::array<uint32_t, 16> mrt       = {};
	uint32_t                 mrt_count = 0;
	if (ps_on) {
		for (const auto& output: ps.program->info.outputs) {
			if (output.kind == ShaderRecompiler::IR::StageOutputKind::Mrt && mrt_count < mrt.size()) {
				mrt[mrt_count++] = output.index;
			}
		}
	}
	const auto kind = mesh       ? DiagF6::DrawKind::Mesh
	                 : indirect ? DiagF6::DrawKind::Indirect
	                 : indexed  ? DiagF6::DrawKind::Indexed
	                            : DiagF6::DrawKind::Auto;
	DiagF6::NoteDraw(buffer.GetRegisters(), host_slots.data(), host_count, ps_on, mrt.data(), mrt_count, kind);
}

namespace {

// Gate "drawstate" (session 57, B1): where a draw keeps its DrawRenderState. Off: a local
// value-initialized at the point `DrawRenderState state {}` was (16 208 B zeroed per draw). On: one
// state per thread that runs draws - the GuestGpu command processor; the thread_local is created
// only once the gate is on, on the first draw of that thread - and only the fields no writer
// covers are reset. Written before any read on every draw:
//  - color_info: ResolveRenderColorTarget writes every slot it hands out (reset or memo copy);
//  - depth_info: ResolveRenderDepthTarget resets it on a memo miss, copies it on a hit;
//  - vertex_info: PrepareProgram runs `info = {}` on every vertex-side stage it fills (the
//    vertex, mesh and LS/HS/TES paths);
//  - ps_input_info: RefreshShaders resets it.
// A nested draw on the same thread (none is known) takes the local. The state owns no Vulkan
// object (PipelineCache::GraphicsPrograms holds plain handles): its thread-exit destructor only
// frees the vectors of the two resource snapshots.
class DrawStateLease {
public:
	DrawStateLease() {
		if (Common::Gates::Enabled(Common::Gates::Gate::DrawStateReuse)) {
			auto& slot = Slot();
			if (!slot.in_use) {
				slot.in_use            = true;
				slot.state.color_count = 0;
				slot.state.ps_active   = true;
				slot.state.programs    = {};
				m_reused               = &slot;
				m_state                = &slot.state;
				return;
			}
		}
		m_state = &m_local.emplace();
	}
	~DrawStateLease() {
		if (m_reused != nullptr) {
			m_reused->in_use = false;
		}
	}
	DrawStateLease(const DrawStateLease&)            = delete;
	DrawStateLease& operator=(const DrawStateLease&) = delete;

	[[nodiscard]] DrawRenderState& State() const { return *m_state; }

private:
	struct ThreadState {
		DrawRenderState state;
		bool            in_use = false;
	};
	static ThreadState& Slot() {
		thread_local ThreadState slot;
		return slot;
	}

	std::optional<DrawRenderState> m_local;
	ThreadState*                   m_reused = nullptr;
	DrawRenderState*               m_state  = nullptr;
};

} // namespace

// Session 95, gate "framerep" (measurement only): the same FNV-1a mixer descriptors.cpp
// uses for the signature; kept local to each translation unit rather than exported,
// because it is a measurement detail and not an interface.
static inline uint64_t FrameRepMixDraw(uint64_t h, uint64_t v) {
	h ^= v;
	h *= 0x100000001b3ull;
	return h;
}

struct DrawCallInfo {
	CommandBufferDebugOp debug_op       = CommandBufferDebugOp::DrawIndex;
	uint32_t             index_count    = 0;
	uint32_t             instance_count = 0;
	uint32_t             first_instance = 0;

	[[nodiscard]] bool IsIndexed() const { return debug_op == CommandBufferDebugOp::DrawIndex; }
	[[nodiscard]] const char* Name() const { return IsIndexed() ? "DrawIndex" : "DrawIndexAuto"; }
};

// Gate "rtfast" (session 59): FindRenderTarget / FindDepthTarget for a slot whose previous
// acquisition recorded the same image, backing and view, while the image's bind_stamp and the
// metadata epoch have not moved since, is answered from the record. What those calls do on an
// unchanged image and are still applied here: the flags a download may have cleared
// (MarkGpuModified, usage) and the download enrolment. Everything else they do is either keyed by
// the stamp (RefreshImage: CPU-dirty, maybe-dirty, buffer-modified, tracking cuts), by the epoch
// (PrepareDccClear, PrepareCmaskClear, the HTile entry), by the checks below (registration,
// rebind, stencil association, pending top mips, the BC source trim) or is a debug name. The
// LRU touch is ResolveRender*Target's. A stencil plane always takes the slow path
// (AssociateStencil), and so does the debug-dump configuration (names, logs).
// Gate "rtfast": the metadata fields FindRenderTarget / FindDepthTarget act on.
static bool SameTargetMetadata(const ImageMetadataInfo& a, const ImageMetadataInfo& b) noexcept {
	return a.kind == b.kind && a.range.address == b.range.address && a.range.size == b.range.size &&
	       a.control == b.control && a.dcc_clear_word == b.dcc_clear_word &&
	       a.cmask_clear_words == b.cmask_clear_words && a.compression == b.compression &&
	       a.stencil_compressed == b.stencil_compressed &&
	       a.dcc_clear_register_valid == b.dcc_clear_register_valid &&
	       a.dcc_alpha_msb == b.dcc_alpha_msb;
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 126, knob "rk3cen" (KYTY_RK3_CENSUS, MEASUREMENT ONLY; docs/session-126/design126.md rev 2 with ROADMAP s122
// items 63, 64, 67): the K3 census.  Everything below runs on the GuestGpu thread only (the latch arms nowhere else) and
// touches only its own thread-local state, its counters and one gauge: no image, no cache, no lock, no allocation on the
// hot path (the table is allocated once, at the first armed draw).
//   C1/C2 the HW::Context hooks move per-context generations of the register groups (Rk3HookWrite / Rk3HookObject);
//   C3    Rk3Latch at the entry of DrawIndex / DrawAuto latches the knob for the draw (Common::Rk3::t_rk3);
//   C4    Rk3ResBegin / Rk3ResEnd time PrepareDrawRenderState; a span not consumed by C6 goes to rk3_res_x_ns;
//   C5    PathLap::MarkSpent(PathEmRtNs) - the pl_em_rt mark, returning what it charged;
//   C6    Rk3Post classifies the draw from the capture's OUTPUTS (colors[0..color_count), depth) and the generations -
//         value 1 reads no input of the resolution ([RC2]); value 3 adds the value witnesses V_D / V_key ([RC5]).
// ---------------------------------------------------------------------------------------------------------------------
namespace {

namespace Rk3 = Common::Rk3;

struct Rk3Target {
	ImageId       id;
	uint32_t      slot = 0;
	ImageViewInfo view {};
};

// Value 3 only: the D_census fields of each group (V_D), compared member-wise per group (operator==, the float clear
// value by its bits), so padding bytes never make two states differ.
struct Rk3Vd {
	std::array<HW::RenderTarget, 8> rt {};
	uint32_t                        mask = 0;
	HW::DepthControl                dc {};
	HW::RenderControl               rc {};
	HW::DepthStencilInfo            si {};
	HW::DepthRenderTarget           z {};
	HW::StencilControl              sc {};
	HW::StencilMask                 sm {};
	uint32_t                        dclear = 0;
	uint32_t                        sclear = 0;
};

// Value 3 only: V_key, the memo keys resolution builds for the targets A compares, in capture order, behind a header
// {color_count, has_depth} - length and order are part of the comparison ([RC5]).
static_assert(RENDER_COLOR_ATTACHMENTS_MAX == 8, "one G_slot group per colour slot");
inline constexpr size_t Rk3ColorKeyBytes = sizeof(ColorTargetMemoRegs) + sizeof(uint64_t);
inline constexpr size_t Rk3KeyMax        = 8 + RENDER_COLOR_ATTACHMENTS_MAX * Rk3ColorKeyBytes + sizeof(DepthTargetMemoBytes);

struct Rk3Entry {
	const void*                               ctx = nullptr;
	std::array<uint64_t, Rk3::GroupCount>     gen {};     // live generations, moved by the hooks
	bool                                      valid = false; // a record of the previous draw exists
	std::array<uint64_t, Rk3::GroupCount>     rec_gen {}; // generations when the record was written
	uint32_t                                  color_count = 0;
	uint32_t                                  slot_mask   = 0; // target_slot of colors[0..color_count)
	bool                                      has_depth   = false;
	std::array<Rk3Target, RENDER_COLOR_ATTACHMENTS_MAX> colors {};
	Rk3Target                                 depth {};
	bool                                      v_valid = false; // value 3: vd / key below belong to the record
	Rk3Vd                                     vd {};
	uint32_t                                  key_len = 0;
	std::array<uint8_t, Rk3KeyMax>            key {};
};

struct Rk3Table {
	std::array<Rk3Entry, 8> e {};
	uint32_t                used     = 0;
	const void*             prev_ctx = nullptr; // context of the previous armed draw (rk3_xctx)
};

constinit thread_local Rk3Table* t_rk3_table  = nullptr;
constinit thread_local bool      t_rk3_pend   = false; // a C4 span not yet consumed by C6
constinit thread_local uint64_t  t_rk3_res_ns = 0;     // ... its length
constinit thread_local int32_t   t_rk3_c4_idx = -1;    // the entry C4 saw (-1: none)
constinit thread_local std::array<uint64_t, Rk3::GroupCount> t_rk3_c4_gen {}; // its generations at C4 (rk3_acqw)
constinit thread_local uint32_t  t_rk3_slice  = 0;     // value 3: the draw's render_target_slice_offset
constinit thread_local bool      t_rk3_slow   = false; // a target of this draw took AcquireTargetView's slow path
constinit thread_local uint32_t  t_rk3_logged = 0;     // bits 1..3: mode line printed; 8..: refusal printed

Rk3Entry* Rk3Find(Rk3Table& t, const void* ctx) {
	for (uint32_t i = 0; i < t.used; i++) {
		if (t.e[i].ctx == ctx) {
			return &t.e[i];
		}
	}
	return nullptr;
}

Rk3Entry* Rk3FindOrAdd(Rk3Table& t, const void* ctx) {
	if (auto* e = Rk3Find(t, ctx); e != nullptr) {
		return e;
	}
	if (t.used == t.e.size()) {
		return nullptr;
	}
	auto& e   = t.e[t.used++];
	e.ctx     = ctx;
	e.gen     = {};
	e.valid   = false;
	e.v_valid = false;
	return &e;
}

// C1: counted on every armed hook; the generation moves only for a context of the table (a context that never drew has
// no record, so its first armed draw is R0 whatever was written before).
void Rk3HookWrite(const void* ctx, uint32_t group) {
	Common::FrameStats::Add(Common::FrameStats::Counter::Rk3WrSet, 1);
	auto* t = t_rk3_table;
	if (t == nullptr || group >= Rk3::GroupCount) {
		return;
	}
	if (auto* e = Rk3Find(*t, ctx); e != nullptr) {
		e->gen[group]++;
	}
}

// C2
void Rk3HookObject(const void* ctx) {
	Common::FrameStats::Add(Common::FrameStats::Counter::Rk3WrObj, 1);
	auto* t = t_rk3_table;
	if (t == nullptr) {
		return;
	}
	if (auto* e = Rk3Find(*t, ctx); e != nullptr) {
		for (auto& g: e->gen) {
			g++;
		}
	}
}

// A C4 span no C6 consumed goes to T13x whole ([RC3]).
void Rk3FlushPending() {
	if (t_rk3_pend) {
		Common::FrameStats::Add(Common::FrameStats::Counter::Rk3ResXNs, t_rk3_res_ns);
		Common::FrameStats::Add(Common::FrameStats::Counter::Rk3ResXN, 1);
	}
	t_rk3_pend   = false;
	t_rk3_res_ns = 0;
}

void Rk3Refuse(uint32_t bit, const char* reason) {
	if ((t_rk3_logged & (1u << bit)) == 0) {
		t_rk3_logged |= 1u << bit;
		LOGF("Rk3Census: refused reason=%s\n", reason);
	}
}

// C3, cold: the knob is nonzero or the previous draw was armed.
[[gnu::noinline]] void Rk3LatchSlow(uint32_t value) {
	namespace G = Common::Gates;
	uint32_t armed = 0;
	if (value != 0) {
		if (!Common::SkipCeil::t_gpu) {
			Common::FrameStats::Add(Common::FrameStats::Counter::Rk3Xthr, 1);
			Rk3Refuse(8, "thread");
		} else if (!Common::FrameStats::Enabled()) {
			Rk3Refuse(9, "frametrace");
		} else if (!G::Enabled(G::Gate::PathLap)) {
			Common::FrameStats::Add(Common::FrameStats::Counter::Rk3Nt, 1);
		} else if (G::Enabled(G::Gate::SamePassCensus)) {
			Rk3Refuse(11, "spcen");
		} else if (G::Enabled(G::Gate::SliceCensus)) {
			Rk3Refuse(12, "slicecen");
		} else if (G::Enabled(G::Gate::BindFloor)) {
			Rk3Refuse(13, "bindfloor");
		} else if (G::Value(G::Knob::M4Baton) != 0) {
			Rk3Refuse(14, "m4baton");
		} else if (G::Value(G::Knob::SkipCeil) != 0) {
			Rk3Refuse(15, "skipceil");
		} else if (G::Value(G::Knob::Spine) != 0) {
			Rk3Refuse(16, "spine"); // [RC9]
		} else {
			armed = value;
		}
	}
	if (armed == 0) {
		// Leaving the armed state (or refused): the records go, the pending C4 goes to rk3_res_x_ns (s.4.1).
		if (Rk3::t_rk3 != 0) {
			Rk3FlushPending();
			if (t_rk3_table != nullptr) {
				t_rk3_table->used     = 0;
				t_rk3_table->prev_ctx = nullptr;
			}
			t_rk3_c4_idx = -1;
		}
		Rk3::t_rk3 = 0;
		Rk3::t_hooks &= ~Rk3::HookRk3; // Session 127 (item 77(e)): the hook mask follows t_rk3
		return;
	}
	if (t_rk3_table == nullptr) {
		t_rk3_table = new Rk3Table();
	}
	if ((t_rk3_logged & (1u << armed)) == 0) {
		t_rk3_logged |= 1u << armed;
		LOGF("Rk3Census: mode %u ctx_slots=%u groups=%u d_setters=%u\n", armed,
		     static_cast<uint32_t>(t_rk3_table->e.size()), Rk3::GroupCount, Rk3::DSetters);
	}
	Rk3::t_rk3 = armed; // a change between 1, 2 and 3 keeps the records (one classification)
	Rk3::t_hooks |= Rk3::HookRk3; // Session 127 (item 77(e)): the hook mask follows t_rk3
	t_rk3_slow = false;
}

// C3: one relaxed knob load and one thread-local test while the knob is 0.
inline void Rk3Latch() {
	const auto value = Common::Gates::Value(Common::Gates::Knob::Rk3Cen);
	if (value != 0 || Rk3::t_rk3 != 0) [[unlikely]] {
		Rk3LatchSlow(value);
	}
}

[[gnu::noinline]] uint64_t Rk3ResBeginSlow(const void* ctx, uint32_t slice) {
	Rk3FlushPending();
	Common::FrameStats::Add(Common::FrameStats::Counter::Rk3C4N, 1);
	auto* e = Rk3FindOrAdd(*t_rk3_table, ctx);
	if (e != nullptr) {
		t_rk3_c4_idx = static_cast<int32_t>(e - t_rk3_table->e.data());
		t_rk3_c4_gen = e->gen;
	} else {
		t_rk3_c4_idx = -1;
	}
	if (Rk3::t_rk3 == 3) {
		t_rk3_slice = slice;
	}
	t_rk3_slow = false;
	return Common::FrameStats::NowNs();
}

// C4: 0 while the draw is not armed.
inline uint64_t Rk3ResBegin(const void* ctx, uint32_t slice) {
	if (Rk3::t_rk3 == 0) [[likely]] {
		return 0;
	}
	return Rk3ResBeginSlow(ctx, slice);
}

inline void Rk3ResEnd(uint64_t t0) {
	if (t0 != 0) [[unlikely]] {
		t_rk3_res_ns = Common::FrameStats::NowNs() - t0;
		t_rk3_pend   = true;
	}
}

// Value 2 only (s.4.4): the split of pl_em_rt inside AcquireRenderTargets; the timers inflate the span, so smoke only.
inline uint64_t Rk3SpBegin() {
	return Rk3::t_rk3 == 2 ? Common::FrameStats::NowNs() : 0;
}

inline void Rk3SpEnd(uint64_t t0, Common::FrameStats::Counter counter) {
	if (t0 != 0) [[unlikely]] {
		Common::FrameStats::Add(counter, Common::FrameStats::NowNs() - t0);
	}
}

// Value 3 only: V_D and V_key of the context as the resolution of this draw read it (nothing parses PM4 between).
void Rk3BuildVd(const HW::Context& hw, Rk3Vd& vd) {
	for (uint32_t s = 0; s < RENDER_COLOR_ATTACHMENTS_MAX; s++) {
		vd.rt[s] = hw.GetRenderTarget(s);
	}
	vd.mask   = hw.GetRenderTargetMask();
	vd.dc     = hw.GetDepthControl();
	vd.rc     = hw.GetRenderControl();
	vd.si     = hw.GetDepthStencilInfo();
	vd.z      = hw.GetDepthRenderTarget();
	vd.sc     = hw.GetStencilControl();
	vd.sm     = hw.GetStencilMask();
	vd.dclear = std::bit_cast<uint32_t>(hw.GetDepthClearValue());
	vd.sclear = hw.GetStencilClearValue();
}

uint32_t Rk3BuildKey(const HW::Context& hw, const RenderColorInfo* colors, uint32_t color_count,
                     const RenderDepthInfo& depth, std::array<uint8_t, Rk3KeyMax>& out) {
	const uint32_t header[2] = {color_count, depth.image_id ? 1u : 0u};
	std::memcpy(out.data(), header, sizeof(header));
	uint32_t len = sizeof(header);
	for (uint32_t i = 0; i < color_count; i++) {
		const auto          slot = colors[i].target_slot;
		ColorTargetMemoRegs regs {};
		BuildColorTargetMemoRegs(hw.GetRenderTarget(slot), regs);
		const auto extra =
		    ColorTargetMemoExtra(render_target_mask_slot(hw.GetRenderTargetMask(), slot), t_rk3_slice, slot, false, false);
		std::memcpy(out.data() + len, regs.data(), regs.size());
		len += static_cast<uint32_t>(regs.size());
		std::memcpy(out.data() + len, &extra, sizeof(extra));
		len += static_cast<uint32_t>(sizeof(extra));
	}
	if (depth.image_id) {
		DepthTargetMemoBytes key {};
		BuildDepthTargetMemoKey(hw, key);
		std::memcpy(out.data() + len, key.data(), key.size());
		len += static_cast<uint32_t>(key.size());
	}
	return len;
}

// Bit g of the result: group g's V_D fields differ between the two snapshots.
uint32_t Rk3VdDiff(const Rk3Vd& a, const Rk3Vd& b) {
	uint32_t diff = 0;
	if (a.mask != b.mask) {
		diff |= 1u << Rk3::GroupMask;
	}
	for (uint32_t s = 0; s < RENDER_COLOR_ATTACHMENTS_MAX; s++) {
		if (!(a.rt[s] == b.rt[s])) {
			diff |= 1u << (Rk3::GroupSlot0 + s);
		}
	}
	if (!(a.dc == b.dc) || !(a.rc == b.rc) || !(a.si == b.si)) {
		diff |= 1u << Rk3::GroupDact;
	}
	auto z = a.z; // G_depth holds the depth target without DB_STENCIL_INFO (a G_dact register)
	z.stencil_info = b.z.stencil_info;
	if (!(z == b.z) || !(a.sc == b.sc) || !(a.sm == b.sm) || a.dclear != b.dclear || a.sclear != b.sclear) {
		diff |= 1u << Rk3::GroupDepth;
	}
	return diff;
}

// Value 3 only ([RC2], [RC5], item 64(v), (e)): the value witnesses of this draw against the record of the same context,
// then this draw's V_D / V_key into the record.  Returns V (V_key equal to the record's).
[[gnu::noinline]] bool Rk3Witness(const HW::Context& hw, const RenderColorInfo* colors, uint32_t color_count,
                                  const RenderDepthInfo& depth, Rk3Entry* e, uint32_t changed) {
	Rk3Vd                          vd {};
	std::array<uint8_t, Rk3KeyMax> key {};
	Rk3BuildVd(hw, vd);
	const uint32_t key_len = Rk3BuildKey(hw, colors, color_count, depth, key);
	bool           v       = false;
	if (e != nullptr && e->valid && e->v_valid) {
		v = e->key_len == key_len && std::memcmp(e->key.data(), key.data(), key_len) == 0;
		// WMISS: a group whose generation did not move while its fields did - a write path the hooks missed.
		const uint32_t still = ~changed & ((1u << Rk3::GroupCount) - 1u);
		if ((Rk3VdDiff(vd, e->vd) & still) != 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::Rk3Wmiss, 1);
		}
	}
	if (e != nullptr) {
		e->vd      = vd;
		e->key_len = key_len;
		std::memcpy(e->key.data(), key.data(), key_len);
		e->v_valid = true;
	}
	return v;
}

// C6, cold (design s.4.3).  `ran`: the pathlap chain ran through C5, so `rt_ns` is this draw's pl_em_rt span.
[[gnu::noinline]] void Rk3Post(const HW::Context& hw, const RenderColorInfo* colors, uint32_t color_count,
                               const RenderDepthInfo& depth, bool ran, uint64_t rt_ns) {
	namespace FS = Common::FrameStats;
	using C      = FS::Counter;
	const uint64_t res_ns  = t_rk3_res_ns;
	const bool     had_c4  = t_rk3_pend;
	const bool     slow    = t_rk3_slow;
	const int32_t  c4_idx  = t_rk3_c4_idx;
	t_rk3_res_ns = 0; // [RC3]: consumed here
	t_rk3_pend   = false;
	t_rk3_slow   = false;
	t_rk3_c4_idx = -1;
	if (!ran) {
		FS::Add(C::Rk3Nt, 1);
		if (had_c4) { // not classified: its resolution counts whole, as a draw that did not reach C6
			FS::Add(C::Rk3ResXNs, res_ns);
			FS::Add(C::Rk3ResXN, 1);
		}
		return;
	}
	FS::NoteMax(FS::Gauge::Rk3C5Max, rt_ns > UINT32_MAX ? UINT32_MAX : static_cast<uint32_t>(rt_ns));
	FS::Add(C::Rk3N, 1);
	FS::Add(C::Rk3RtNs, rt_ns);
	FS::Add(C::Rk3ResNs, res_ns);
	const bool has_depth = static_cast<bool>(depth.image_id);
	const bool dclr      = has_depth && depth.depth_clear_enable;
	if (dclr) {
		FS::Add(C::Rk3Dclr, 1);
	}
	if (slow) {
		FS::Add(C::Rk3Slow, 1);
	}
	auto&       t   = *t_rk3_table;
	const void* ctx = &hw;
	if (t.prev_ctx != nullptr && t.prev_ctx != ctx) {
		FS::Add(C::Rk3Xctx, 1);
	}
	t.prev_ctx = ctx;
	auto* e    = Rk3Find(t, ctx); // C4 of this draw added it, unless the table was full
	if (e != nullptr && c4_idx == static_cast<int32_t>(e - t.e.data()) && e->gen != t_rk3_c4_gen) {
		FS::Add(C::Rk3Acqw, 1);
	}
	uint32_t slot_mask = 0;
	for (uint32_t i = 0; i < color_count; i++) {
		slot_mask |= 1u << colors[i].target_slot;
	}
	enum class Cls { R0, XW, WI, XID };
	Cls      cls     = Cls::R0;
	bool     xw_irr  = false;
	uint32_t changed = 0;
	if (e == nullptr) {
		FS::Add(C::Rk3Ovf, 1);
	} else if (e->valid) {
		// Rel(d) ([RC1]): G_mask, G_dact always; G_slot[n] for a slot that gave a target now or in the record; G_depth
		// when a depth target exists now or in the record.
		uint32_t rel = (1u << Rk3::GroupMask) | (1u << Rk3::GroupDact) | ((slot_mask | e->slot_mask) << Rk3::GroupSlot0);
		if (has_depth || e->has_depth) {
			rel |= 1u << Rk3::GroupDepth;
		}
		for (uint32_t g = 0; g < Rk3::GroupCount; g++) {
			if (e->gen[g] != e->rec_gen[g]) {
				changed |= 1u << g;
			}
		}
		if ((changed & rel) != 0) {
			cls = Cls::XW;
		} else {
			xw_irr  = changed != 0;
			// E1 (s.3.4): the target identity after the capture equals the record.
			bool e1 = e->color_count == color_count && e->has_depth == has_depth;
			for (uint32_t i = 0; e1 && i < color_count; i++) {
				e1 = colors[i].image_id == e->colors[i].id && colors[i].target_slot == e->colors[i].slot &&
				     colors[i].desc.view_info == e->colors[i].view;
			}
			if (e1 && has_depth) {
				e1 = depth.image_id == e->depth.id && depth.desc.view_info == e->depth.view;
			}
			cls = e1 ? Cls::WI : Cls::XID;
		}
	}
	const bool in_r0 = cls == Cls::R0;
	const bool in_w  = cls == Cls::WI || cls == Cls::XID;
	const bool in_r  = in_r0 || cls == Cls::WI;
	const bool in_r1 = in_r0 || (cls == Cls::WI && !xw_irr);
	if (in_r0) {
		FS::Add(C::Rk3Rec0, 1);
		FS::Add(C::Rk3RtRec0Ns, rt_ns);
	}
	if (cls == Cls::XW) {
		FS::Add(C::Rk3Xw, 1);
	}
	if (in_w) {
		FS::Add(C::Rk3W, 1);
		if (xw_irr) {
			FS::Add(C::Rk3XwIrr, 1);
		}
		FS::Add(cls == Cls::WI ? C::Rk3Wi : C::Rk3Xid, 1);
	}
	if (in_r0 || in_w) {
		FS::Add(C::Rk3RtWNs, rt_ns);
	}
	if (in_r) {
		FS::Add(C::Rk3RtRNs, rt_ns);
		FS::Add(C::Rk3ResRNs, res_ns);
		if (dclr) {
			FS::Add(C::Rk3RDclr, 1);
		}
		if (slow) {
			FS::Add(C::Rk3RSlow, 1);
		}
	}
	if (in_r1) {
		FS::Add(C::Rk3RtR1Ns, rt_ns);
		FS::Add(C::Rk3ResR1Ns, res_ns);
	}
	if (Rk3::t_rk3 == 2) {
		FS::Add(C::Rk3SpN, 1);
	}
	// Value 3 only: the value witnesses (the record's V_D / V_key are written there).
	if (Rk3::t_rk3 == 3) {
		const bool v = Rk3Witness(hw, colors, color_count, depth, e, changed);
		if (v) {
			FS::Add(C::Rk3V, 1);
			if (cls == Cls::XW) {
				FS::Add(C::Rk3Vw, 1);
			}
		}
		if (in_r0 || v) {
			FS::Add(C::Rk3RtVNs, rt_ns);
			FS::Add(C::Rk3ResVNs, res_ns);
		}
	}
	// The record of this draw.
	if (e != nullptr) {
		e->valid       = true;
		e->rec_gen     = e->gen;
		e->color_count = color_count;
		e->slot_mask   = slot_mask;
		e->has_depth   = has_depth;
		for (uint32_t i = 0; i < color_count; i++) {
			e->colors[i] = {colors[i].image_id, colors[i].target_slot, colors[i].desc.view_info};
		}
		e->depth = has_depth ? Rk3Target {depth.image_id, 0, depth.desc.view_info} : Rk3Target {};
		if (Rk3::t_rk3 != 3) {
			e->v_valid = false; // value 3 wrote V_D / V_key above; any other value leaves no witness record
		}
	}
}

} // namespace

// ---------------------------------------------------------------------------------------------------------------------
// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..6, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items
// 76(z), 77, 78, 79): the K3 prototype.  A draw of context C takes the outputs of its target resolution (place A,
// PrepareDrawRenderState) and capture (place B, AcquireRenderTargets) from the RECORD of C - the outputs of the last full
// draw on C - while no relevant register group was written since (s.2.1) and no non-register source moved (s.2.2).
//   0 the previous path; 1 skip; 2 self-check: the full path always runs, the record lives exactly as at 1 ([RC1]) and
//   every step is compared with it (s.5); 3 = 2 with the register source ignored by PA (positive control, s.6);
//   4 = 2 with PB items 3 (metadata epoch) and 4 (state_serial) not applied (positive control of place B; track F, F30d,
//   ROADMAP s122 item 643(v)); 5 = 2 with PB item 6 (the pinned pass, RtsXbPass) not applied (track F, F30k, ROADMAP
//   s122 item 655(g)(1)); 6 = 2 with the (a2) perturbation on every 4 096th PA and PB draw (a synthetic control of
//   the bit S chain; track F, F30o, ROADMAP s122 item 664(e)(1)).
// The latch arms only on the GuestGpu thread; everything below touches thread-local state, its counters and one gauge.
// The latch, places A and B and the post are RenderExecutor members (RtsLatchSlow, RtsPlaceA, RtsPlaceB, RtsPost) because
// the replay calls TextureCache::TouchImage and reads m_slot_images, which only RenderExecutor may.
// ---------------------------------------------------------------------------------------------------------------------
namespace {

using RtsGen = std::array<uint64_t, Rk3::GroupCount>;

// Self-check bits (s.5.2).  0x001 O, 0x002 K, 0x004 T, 0x008 F and 0x400 U are decided at place A, before the capture.
inline constexpr uint32_t kRtsBitsA = 0x001u | 0x002u | 0x004u | 0x008u | 0x400u;

// One target of the record (colours in resolution order, depth last), as the recorded capture left it.
struct RtsTarget {
	ImageId          id;
	uint32_t         slot               = 0;       // target_slot, UINT32_MAX = depth
	vk::Image        backing            = nullptr;
	vk::ImageView    view               = nullptr; // the view the recorded capture returned (= the rtfast record's)
	uint32_t         stamp              = 0;       // bind_stamp after the recorded capture
	uint32_t         source_first_level = 0;
	uint64_t         source_size        = 0;
	uint64_t         state_serial       = 0;       // backing.state_serial after the recorded capture (N3)
	uint32_t         htile_mask         = 0;       // depth only
	bool             is_bound           = false;
	vk::ImageLayout  att_layout         = vk::ImageLayout::eUndefined;
	vk::AccessFlags2 att_access;
	uint32_t         w = 0, h = 0;                 // colour Extent(), for the counter replay
	uint64_t         kpx = 0;
};

// One visit of the resolution loop: the colour slot, the color_info index it wrote, the memo slot it went through
// (UINT32_MAX: the inactive-slot path, colorRenderTarget.cpp:113-118) and whether it gave a target.
struct RtsVisit {
	uint32_t slot         = 0;
	uint32_t idx          = 0;
	uint32_t memo_slot    = UINT32_MAX;
	uint32_t memo_version = 0;
	bool     image        = false;
};

// The record of a context (s.4.4).  `pre` is the resolution output before the capture; the strict record demands the
// output after the capture equal to it in every field of bits 0x001 and 0x400 ([RC9], item 79(b)) - that is, in every
// field - so the one copy is also `post`.
struct RtsRecord {
	RtsGen                                                    gen {};       // generations the recorded resolution read
	uint32_t                                                  rel   = 0;    // Rel_skip of `mask` (s.2.1)
	uint32_t                                                  slice = 0;    // render_target_slice_offset (N7)
	uint32_t                                                  mask  = 0;    // CB_TARGET_MASK
	uint32_t                                                  bmin = 0, bmax = 0; // depth bounds, bits (N9)
	uint32_t                                                  n_idx = 0;    // color_info[0 .. n_idx) the resolution wrote
	uint32_t                                                  color_count = 0;
	std::array<RenderColorInfo, RENDER_COLOR_ATTACHMENTS_MAX> pre {};
	RenderDepthInfo                                           pre_depth;
	uint32_t                                                  nv = 0;
	std::array<RtsVisit, RENDER_COLOR_ATTACHMENTS_MAX>        v {};
	uint32_t                                                  dmemo_slot = UINT32_MAX, dmemo_version = 0;
	uint32_t                                                  nt = 0;       // targets: color_count + (depth ? 1 : 0)
	std::array<RtsTarget, RENDER_COLOR_ATTACHMENTS_MAX + 1>   t {};
	RenderState                                               state;
	PassExtentWitness                                         extents;
	uint64_t                                                  meta        = 0; // MetaEpoch() after the recorded capture
	uint64_t                                                  pass_serial = 0; // PassBeginSerial() of its pinned pass
	uint32_t                                                  age         = 0; // posts in a row that only re-pinned ([RC1])
	bool                                                      pinned      = false;
};

struct RtsEntry {
	const void* ctx     = nullptr;
	RtsGen      gen {};          // live generations, moved by the hooks
	bool        has_rec = false; // the record exists and no draw in flight has taken it (N12)
	RtsRecord   rec;
};

// What a full resolution of this draw leaves (I1, I2) and what place A read of the registers.
struct RtsDraft {
	uint32_t                                                  nv = 0;
	std::array<RtsVisit, RENDER_COLOR_ATTACHMENTS_MAX>        v {};
	uint32_t                                                  dmemo_slot = UINT32_MAX, dmemo_version = 0;
	uint32_t                                                  n_idx = 0;
	uint32_t                                                  color_count = 0;
	std::array<RenderColorInfo, RENDER_COLOR_ATTACHMENTS_MAX> pre {};
	RenderDepthInfo                                           pre_depth;
	uint32_t                                                  slice = 0, mask = 0, bmin = 0, bmax = 0;
	size_t                                                    bound0 = 0; // m_bound_images.size() before the resolution
};

struct RtsTable {
	std::array<RtsEntry, 8> e {};
	uint32_t                used = 0;
	RtsDraft                draft;
};

constinit thread_local uint32_t    t_rts          = 0;       // the value latched for the draw in flight (0 = off)
constinit thread_local RtsTable*   t_rts_table    = nullptr; // allocated at the first armed draw
constinit thread_local RtsEntry*   t_rts_entry    = nullptr; // the entry of this draw's context (nullptr: table full)
constinit thread_local RtsRecord*  t_rts_take     = nullptr; // the record taken at the latch, given back by the post
constinit thread_local bool        t_rts_live     = false;   // latched armed, the post not reached yet
constinit thread_local bool        t_rts_at_a     = false;   // ... place A reached
constinit thread_local bool        t_rts_pa       = false;   // PA held
constinit thread_local bool        t_rts_pb       = false;   // PA and PB held
constinit thread_local bool        t_rts_b        = false;   // place B ran through RtsPlaceB
constinit thread_local bool        t_rts_reg      = false;   // a Rel_skip group moved since the record ([RC2], reg=)
constinit thread_local bool        t_rts_pin      = false;   // the post left a record for AfterBegin to pin
constinit thread_local bool        t_rts_slow     = false;   // I3: a target took AcquireTargetView's slow path
constinit thread_local bool        t_rts_race     = false;   // ... and entered it with a bind_stamp moved since PB
constinit thread_local bool        t_rts_refind   = false;   // I4: the capture's dead-image re-find ran
constinit thread_local uint32_t    t_rts_bits     = 0;       // values 2/3: the bits place A found
constinit thread_local uint64_t    t_rts_meta0    = 0;       // MetaEpoch() before / after the full capture
constinit thread_local uint64_t    t_rts_meta1    = 0;
constinit thread_local uint64_t    t_rts_ser0     = 0;       // ImageStateSerial() before / after the full capture
constinit thread_local uint64_t    t_rts_ser1     = 0;
constinit thread_local bool        t_rts_open0    = false;   // IsRendering() before / after the full capture
constinit thread_local bool        t_rts_open1    = false;
constinit thread_local RtsGen      t_rts_gen_a {};           // the entry's generations at place A (rts_acqw)
constinit thread_local const void* t_rts_last_ctx = nullptr; // item 79(v)(1): context of the last armed draw at A
constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..22: mode line printed
constinit thread_local uint32_t    t_rts_lines    = 0;       // RtSkipVerify lines printed (at most 40)
constinit thread_local bool        t_rts_inj      = false;   // value 6: this draw was perturbed (F30o), cleared by the post
// Track F, F30o (ROADMAP s122 item 664(e)(1)): value 6 - PA and PB draws of the process counted at place B; every
// kRtsInjEvery-th one is perturbed.  Touched at value 6 only.
inline constexpr uint64_t   kRtsInjEvery = 4096;
std::atomic<uint64_t>       g_rts_inj_n {0};

RtsEntry* RtsFindOrAdd(RtsTable& t, const void* ctx) {
	for (uint32_t i = 0; i < t.used; i++) {
		if (t.e[i].ctx == ctx) {
			return &t.e[i];
		}
	}
	if (t.used == t.e.size()) {
		return nullptr;
	}
	auto& e   = t.e[t.used++];
	e.ctx     = ctx;
	e.gen     = {};
	e.has_rec = false;
	return &e;
}

// The hooks (item 77(e)): the generation of a context of the table moves; counted only at 2/3 ([RC3]).
void RtsHookWrite(const void* ctx, uint32_t group) {
	if (t_rts >= 2) {
		Common::FrameStats::Add(Common::FrameStats::Counter::RtsWr, 1);
	}
	auto* t = t_rts_table;
	if (t == nullptr || group >= Rk3::GroupCount) {
		return;
	}
	for (uint32_t i = 0; i < t->used; i++) {
		if (t->e[i].ctx == ctx) {
			t->e[i].gen[group]++;
			return;
		}
	}
}

void RtsHookObject(const void* ctx) {
	if (t_rts >= 2) {
		Common::FrameStats::Add(Common::FrameStats::Counter::RtsWrObj, 1);
	}
	auto* t = t_rts_table;
	if (t == nullptr) {
		return;
	}
	for (uint32_t i = 0; i < t->used; i++) {
		if (t->e[i].ctx == ctx) {
			for (auto& g: t->e[i].gen) {
				g++;
			}
			return;
		}
	}
}

// Rel_skip(C) (s.2.1): G_mask, G_dact, G_depth, G_slot[0] always, G_slot[n] for a slot the mask lets the loop visit.
uint32_t RtsRelSkip(uint32_t mask) {
	uint32_t rel = (1u << Rk3::GroupMask) | (1u << Rk3::GroupDact) | (1u << Rk3::GroupDepth) | (1u << Rk3::GroupSlot0);
	for (uint32_t n = 1; n < RENDER_COLOR_ATTACHMENTS_MAX; n++) {
		if (render_target_mask_slot(mask, n) != 0) {
			rel |= 1u << (Rk3::GroupSlot0 + n);
		}
	}
	return rel;
}

bool RtsMoved(const RtsGen& now, const RtsGen& rec, uint32_t rel) {
	for (uint32_t g = 0; g < Rk3::GroupCount; g++) {
		if ((rel & (1u << g)) != 0 && now[g] != rec[g]) {
			return true;
		}
	}
	return false;
}

// Member-wise, never memcmp of an aggregate (padding, the s83 lesson).
bool RtsSameMeta(const ImageMetadataInfo& a, const ImageMetadataInfo& b) {
	return a.range == b.range && a.kind == b.kind && a.control == b.control && a.dcc_clear_word == b.dcc_clear_word &&
	       a.cmask_clear_words == b.cmask_clear_words && a.compression == b.compression &&
	       a.stencil_compressed == b.stencil_compressed && a.dcc_clear_register_valid == b.dcc_clear_register_valid &&
	       a.dcc_alpha_msb == b.dcc_alpha_msb;
}

bool RtsSameDesc(const TextureCache::ImageDesc& a, const TextureCache::ImageDesc& b) {
	const auto& x = a.info;
	const auto& y = b.info;
	return x.data == y.data && x.stencil == y.stencil && RtsSameMeta(x.metadata, y.metadata) &&
	       x.htile_clear_mask == y.htile_clear_mask && x.pixel_format == y.pixel_format &&
	       x.guest_format == y.guest_format && x.type == y.type && x.extent == y.extent && x.resources == y.resources &&
	       x.pitch == y.pitch && x.bytes_per_block == y.bytes_per_block && x.samples == y.samples &&
	       x.tile_mode == y.tile_mode && x.bgra16 == y.bgra16 && x.mip_layout == y.mip_layout &&
	       a.view_info == b.view_info && a.type == b.type && a.source_first_level == b.source_first_level &&
	       a.source_size == b.source_size;
}

// Bits 0x001 (the outputs render reads, [RC2]) and 0x400 (the memo bookkeeping) of one colour entry.
uint32_t RtsDiffColor(const RenderColorInfo& a, const RenderColorInfo& b) {
	uint32_t bits = 0;
	if (a.image_id != b.image_id || a.target_slot != b.target_slot || a.guest_mip_level != b.guest_mip_level ||
	    a.guest_array_layer != b.guest_array_layer || a.export_mapping.packed != b.export_mapping.packed ||
	    !RtsSameDesc(a.desc, b.desc)) {
		bits |= 0x001u;
	}
	if (a.memo_slot != b.memo_slot || a.memo_version != b.memo_version) {
		bits |= 0x400u;
	}
	return bits;
}

// The same for the depth entry; floats by their bits.
uint32_t RtsDiffDepth(const RenderDepthInfo& a, const RenderDepthInfo& b) {
	const auto fb   = [](float v) { return std::bit_cast<uint32_t>(v); };
	uint32_t   bits = 0;
	if (!RtsSameDesc(a.desc, b.desc) || a.depth_clear_enable != b.depth_clear_enable ||
	    a.depth_load_clear_enable != b.depth_load_clear_enable || fb(a.depth_clear_value) != fb(b.depth_clear_value) ||
	    a.depth_test_enable != b.depth_test_enable || a.depth_write_enable != b.depth_write_enable ||
	    a.depth_compare_op != b.depth_compare_op || a.depth_bounds_test_enable != b.depth_bounds_test_enable ||
	    fb(a.depth_min_bounds) != fb(b.depth_min_bounds) || fb(a.depth_max_bounds) != fb(b.depth_max_bounds) ||
	    a.stencil_clear_enable != b.stencil_clear_enable || a.stencil_clear_value != b.stencil_clear_value ||
	    a.stencil_test_enable != b.stencil_test_enable || a.stencil_front != b.stencil_front ||
	    a.stencil_back != b.stencil_back || a.image_id != b.image_id) {
		bits |= 0x001u;
	}
	if (a.memo_slot != b.memo_slot || a.memo_version != b.memo_version) {
		bits |= 0x400u;
	}
	return bits;
}

// I1 (s.8.2): one colour visit of the full resolution.  Thread-local only.
void RtsDraftColor(uint32_t slot, uint32_t idx, const RenderColorInfo& r) noexcept {
	auto& d = t_rts_table->draft;
	if (d.nv < d.v.size()) {
		d.v[d.nv++] = RtsVisit {slot, idx, r.memo_slot, r.memo_version, static_cast<bool>(r.image_id)};
	}
}

// I2: the depth resolution (always through its memo, depthRenderTarget.cpp:284-361).
void RtsDraftDepth(const RenderDepthInfo& r) noexcept {
	auto& d         = t_rts_table->draft;
	d.dmemo_slot    = r.memo_slot;
	d.dmemo_version = r.memo_version;
}

// I3: a target took AcquireTargetView's slow path; the FIRST slow entry of the draw decides whether it entered with a
// bind_stamp moved since the fast record - a cross-thread race (s.5.2), exactly as t_sp_rt_stamp_race.
void RtsNoteSlow(bool stamp_moved) noexcept {
	if (!t_rts_slow) {
		t_rts_race = stamp_moved;
	}
	t_rts_slow = true;
}

// Values 2/3: one draw's self-check result (s.5.2).  A race suppresses only the capture bits.  xsrc (track F, F30k):
// the sources of bit X the post found - 1 attachment layout / access, 2 depth_load_clear_enable, 4 pass extents.
void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth, uint32_t xsrc) {
	namespace FS = Common::FrameStats;
	if (t_rts_race && (bits & kRtsBitsA) == 0) {
		FS::Add(FS::Counter::RtsRace, 1);
		return;
	}
	FS::Add(FS::Counter::RtsBad, 1);
	if (!t_rts_reg) {
		FS::Add(FS::Counter::RtsBadNoreg, 1);
	}
	// Track F, F30d (ROADMAP s122 item 643(v)(2)): the place B share of rts_bad, and its R / X part.
	if ((bits & 0x3f0u) != 0) {
		FS::Add(FS::Counter::RtsBadB, 1);
	}
	if ((bits & 0x030u) != 0) {
		FS::Add(FS::Counter::RtsBadRx, 1);
	}
	// Track F, F30k (ROADMAP s122 item 655(g)(2)): one counter per place B bit, X by its source.
	if ((bits & 0x010u) != 0) {
		FS::Add(FS::Counter::RtsBadR, 1);
	}
	if ((xsrc & 1u) != 0) {
		FS::Add(FS::Counter::RtsBadXr, 1);
	}
	if ((xsrc & 2u) != 0) {
		FS::Add(FS::Counter::RtsBadXc, 1);
	}
	if ((xsrc & 4u) != 0) {
		FS::Add(FS::Counter::RtsBadXe, 1);
	}
	if ((bits & 0x040u) != 0) {
		FS::Add(FS::Counter::RtsBadS, 1);
	}
	if ((bits & 0x080u) != 0) {
		FS::Add(FS::Counter::RtsBadP, 1);
	}
	if ((bits & 0x100u) != 0) {
		FS::Add(FS::Counter::RtsBadM, 1);
	}
	if ((bits & 0x200u) != 0) {
		FS::Add(FS::Counter::RtsBadL, 1);
	}
	if (t_rts_lines < 40) {
		t_rts_lines++;
		LOGF("RtSkipVerify: MISMATCH frame=%d bits=0x%03x reg=%u chain=%u colors=%u depth=%u pa=1 pb=%u mode=%u\n", frame,
		     bits, t_rts_reg ? 1u : 0u, age, colors, depth ? 1u : 0u, t_rts_pb ? 1u : 0u, t_rts);
	}
}

// Track F, F30o (ROADMAP s122 item 664(e)(1)), value 6: the tracked layout of every subresource of the view range is
// eColorAttachmentOptimal - read exactly as Image::GetBarriers will (the whole state while there are no subresource
// states, else the states of the range; a volume has one layer).  A range outside the image is not eligible.
bool RtsInjAttachLayout(const Image& image, ImageSubresourceRange r) noexcept {
	const uint32_t levels = image.info.resources.levels;
	const uint32_t layers = image.info.resources.layers;
	if (image.info.IsVolume()) {
		r.base_layer  = 0;
		r.layer_count = 1;
	}
	if (r.level_count == 0 || r.layer_count == 0 || r.base_level + r.level_count > levels ||
	    r.base_layer + r.layer_count > layers) {
		return false;
	}
	const auto& b = image.backing;
	if (b.subresource_states.empty()) {
		return b.state.layout == vk::ImageLayout::eColorAttachmentOptimal;
	}
	for (uint32_t level = r.base_level; level < r.base_level + r.level_count; level++) {
		for (uint32_t layer = r.base_layer; layer < r.base_layer + r.layer_count; layer++) {
			const size_t index = static_cast<size_t>(level) * layers + layer;
			if (index >= b.subresource_states.size() ||
			    b.subresource_states[index].layout != vk::ImageLayout::eColorAttachmentOptimal) {
				return false;
			}
		}
	}
	return true;
}

// Track F, F30o (ROADMAP s122 item 664(e)(1)), value 6, at place B after PB held and before the snapshots: on every
// kRtsInjEvery-th PA and PB draw, one Transit of the first colour target whose tracked layout is the attachment layout
// and which this draw does not sample, to eGeneral with the capture's access and view range (AcquireRenderTargets) -
// the same tracker path (GetBarriers, NoteStateChange, the pass end) under the same lock.  The capture then transits it
// back to eColorAttachmentOptimal between the snapshots: bit S.  Never the depth target, never a sampled target.
void RtsInject(uint32_t cc, const RenderColorInfo* colors, Image* const* img) {
	namespace FS = Common::FrameStats;
	if ((g_rts_inj_n.fetch_add(1, std::memory_order_relaxed) + 1) % kRtsInjEvery != 0) {
		return;
	}
	for (uint32_t i = 0; i < cc; i++) {
		Image&      image = *img[i];
		const auto& view = colors[i].desc.view_info;
		const ImageSubresourceRange range {view.base_level, view.level_count, view.base_layer, view.layer_count};
		if (image.binding.is_bound || !RtsInjAttachLayout(image, range)) {
			continue;
		}
		image.Transit(vk::ImageLayout::eGeneral,
		              vk::AccessFlagBits2::eColorAttachmentRead | vk::AccessFlagBits2::eColorAttachmentWrite, range,
		              vk::CommandBuffer {}, RenderPassEnd::TargetTransit);
		t_rts_inj = true;
		FS::Add(FS::Counter::RtsInj, 1);
		return;
	}
	FS::Add(FS::Counter::RtsInjNone, 1);
}

// The pin (s.4.3): after BeginRendering the record the post left is pinned to the pass this draw renders in.
void RtsAfterBegin() {
	if (t_rts_pin) {
		t_rts_pin = false;
		if (t_rts_entry != nullptr && t_rts_entry->has_rec) {
			t_rts_entry->rec.pass_serial = CommandBuffer::PassBeginSerial();
			t_rts_entry->rec.pinned      = true;
		}
	}
}

} // namespace

vk::ImageView RenderExecutor::AcquireTargetView(TextureCache& cache, Image& image, ImageId id,
                                                const TextureCache::ImageDesc& desc,
                                                TargetViewFast& fast, bool depth_target,
                                                uint32_t guest_clear_regs) {
	namespace FS      = Common::FrameStats;
	// Session 123, knob "skipceil" = 2 (census, W3 (a)): an acquisition is not a certain write - W1 stamps the attachment.
	const Common::SkipCeil::AcqGuard skc_acq;
	// The linear-readback configuration enrols the image under the lock on every acquisition.
	const bool gate   = Common::Gates::Enabled(Common::Gates::Gate::RenderTargetFast) &&
	                  !graphics_debug_dump_enabled() && !cache.m_readback_linear_images;
	const bool stencil = depth_target && desc.info.HasStencil();
	const auto source  = image.SourceRange();
	// A stencil plane: AssociateStencil's record must still exist, cover the range and point at
	// this depth image (a freed record drops depth_id before its slot is reused).
	const auto stencil_kept = [&] {
		if (!stencil) {
			return true;
		}
		const auto* record = cache.m_slot_images.try_get(fast.stencil_record);
		return record != nullptr && record->depth_id == id &&
		       record->info.data.address == desc.info.stencil.address;
	};
	if (gate && fast.valid && fast.image_id == id &&
	    fast.backing == image.backing.image && image.registered && !image.depth_id &&
	    !image.binding.needs_rebind && image.pending_levels == 0 &&
	    fast.source_size == image.source_size &&
	    fast.source_first_level == image.source_first_level && fast.view_info == desc.view_info &&
	    SameTargetMetadata(fast.metadata, desc.info.metadata) &&
	    (!depth_target || fast.htile_clear_mask == image.info.htile_clear_mask)) {
		if (image.bind_stamp.load(std::memory_order_acquire) == fast.stamp &&
		    cache.MetaEpoch() == fast.meta_epoch && stencil_kept()) {
			image.MarkGpuModified();
			if (depth_target) {
				image.usage.depth_target = true;
			} else {
				image.usage.render_target = true;
			}
			FS::Add(FS::Counter::RtFastOk, 1);
			return fast.view;
		}
		FS::Add(FS::Counter::RtFastStale, 1);
	}
	const auto stamp = image.bind_stamp.load(std::memory_order_acquire);
	// Session 120, gate "spcen" (MEASUREMENT ONLY, RC1): an armed draw took the slow path; a bind_stamp that moved
	// since the census check (which saw stamp == fast.stamp) is a cross-thread race, decided HERE, before the Find
	// below can move the stamp itself.  Only the FIRST slow entry of the draw decides: a Find of an earlier target can
	// bump an aliasing later target's stamp, which is not a race (code review, lead's adoption).
	if (t_sp_rt_armed) {
		if (!t_sp_rt_slow) {
			t_sp_rt_stamp_race = stamp != fast.stamp;
		}
		t_sp_rt_slow = true;
	}
	if (Common::Rk3::t_rk3 != 0) [[unlikely]] {
		t_rk3_slow = true; // Session 126, knob "rk3cen" (rk3_slow): a target of this draw took the slow path
	}
	if (t_rts) [[unlikely]] {
		RtsNoteSlow(stamp != fast.stamp); // Session 127, knob "rtskip" (I3): the slow path and its bind_stamp race
	}
	const auto view  = depth_target ? cache.FindDepthTarget(id, desc) : cache.FindRenderTarget(id, desc);
	fast.valid       = false;
	FS::Add(FS::Counter::RtFastNo, 1);
	ImageId stencil_record;
	if (stencil) {
		FS::Add(FS::Counter::RtFastStencil, 1);
		if (gate) {
			stencil_record = cache.FindStencilAssociation(desc.info.stencil);
		}
	}
	// Recorded only after a call that left the image with nothing to do next time, and under a
	// stamp that did not move across it (a fault racing the call would otherwise be lost).
	if (gate && (!stencil || stencil_record) && image.pending_levels == 0 && !image.IsCpuDirty() &&
	    SameTargetMetadata(desc.info.metadata, image.info.metadata) &&
	    !image.IsBufferModified() && image.IsTracked() && image.track_addr == source.address &&
	    image.track_addr_end == source.End() &&
	    image.bind_stamp.load(std::memory_order_acquire) == stamp) {
		fast.image_id           = id;
		fast.backing            = image.backing.image;
		fast.view               = view;
		fast.view_info          = desc.view_info;
		fast.stencil_record     = stencil_record;
		fast.metadata           = desc.info.metadata;
		fast.htile_clear_mask   = image.info.htile_clear_mask;
		fast.meta_epoch         = cache.MetaEpoch();
		fast.source_size        = image.source_size;
		fast.source_first_level = image.source_first_level;
		fast.stamp              = stamp;
		fast.valid              = true;
		FS::Add(FS::Counter::RtFastRecord, 1);
	}
	return view;
}

// Session 120, gate "spcen" (MEASUREMENT ONLY, C:/kyty/s120/design/spcen.md s.3.7, spcen_review.md RC1-RC6,
// design120.md section 4): the draw's latch.  Namespace scope, not anonymous: it is the friend render.h names.  Armed:
// the census state is allocated at the first armed draw (never at gate 0).  Unarmed with a census state left by an
// earlier armed block (F7): every memo is invalidated, so no memo survives a draw the census did not see.
class SpDrawScope {
public:
	SpDrawScope(RenderExecutor& ex, bool on): m_ex(ex), m_on(on) {
		if (!on) {
			if (ex.m_sp != nullptr) {
				auto& sp      = *ex.m_sp;
				sp.rt.valid   = false;
				sp.rt.pending = false;
				for (auto& tr: sp.tr) {
					tr.valid = false;
				}
			}
			return;
		}
		if (ex.m_sp == nullptr) {
			ex.m_sp = std::make_unique<SpCensusState>();
			LOGF("SpCensus: mode 1 rt_targets=%u tr_slots=%u\n", RENDER_COLOR_ATTACHMENTS_MAX + 1u, kSpTrSlots);
		}
		ex.m_sp->armed = true;
	}
	~SpDrawScope() {
		if (m_on) {
			auto& sp      = *m_ex.m_sp;
			sp.armed      = false;
			sp.would_rt   = false;
			sp.would_rt_g = false;
			t_sp_rt_armed  = false;
			t_sp_dcc_armed = false;
		}
	}
	SpDrawScope(const SpDrawScope&)            = delete;
	SpDrawScope& operator=(const SpDrawScope&) = delete;
	[[nodiscard]] bool Armed() const noexcept { return m_on; }

private:
	RenderExecutor& m_ex;
	bool            m_on;
};

bool RenderExecutor::SpRtConfigOk(const TextureCache& cache) {
	return Common::Gates::Enabled(Common::Gates::Gate::RenderTargetFast) && !graphics_debug_dump_enabled() &&
	       !cache.m_readback_linear_images && !Common::Gates::Enabled(Common::Gates::Gate::SliceCensus);
}

bool RenderExecutor::SpStencilKept(const TextureCache& cache, const RenderDepthInfo& depth,
                                   const TargetViewFast& fast, ImageId id) {
	if (!depth.desc.info.HasStencil()) {
		return true;
	}
	const auto* record = cache.m_slot_images.try_get(fast.stencil_record);
	return record != nullptr && record->depth_id == id &&
	       record->info.data.address == depth.desc.info.stencil.address;
}

namespace {
// spcen.md s.4.1: the A reasons, first failing wins, in counter order (SpRtMissMemo ... SpRtMissPass).
enum SpRtWhy : uint32_t {
	kSpRtNone = 0,
	kSpRtMemo,
	kSpRtCfg,
	kSpRtDepthClear,
	kSpRtMeta,
	kSpRtIds,
	kSpRtLive,
	kSpRtSerial,
	kSpRtBound,
	kSpRtDepthSampled,
	kSpRtPass,
};
static_assert(static_cast<uint32_t>(Common::FrameStats::Counter::SpRtMissPass) -
                  static_cast<uint32_t>(Common::FrameStats::Counter::SpRtMissMemo) ==
              kSpRtPass - kSpRtMemo);
} // namespace

// Reads only (every image through try_get).  Evaluates whether the memo recorded by the previous armed draw of the
// open pass would return this draw's RenderState with no side effect but the replayable stores.
void RenderExecutor::SpRtCheck(CommandBuffer& buffer, const RenderColorInfo* colors, uint32_t color_count,
                               const RenderDepthInfo& depth) {
	namespace FS = Common::FrameStats;
	auto& sp    = *m_sp;
	auto& m     = sp.rt;
	auto& cache = m_context.GetTextureCache();
	if (m.pending) { // the recorder never reached BeginRendering
		m.pending = false;
		m.valid   = false;
	}
	sp.serial0  = ImageStateSerial();
	sp.meta0    = cache.MetaEpoch();
	sp.open0    = buffer.IsRendering();
	sp.draw_bad = 0;
	sp.raced    = false;
	const bool     has_depth = static_cast<bool>(depth.image_id);
	const uint32_t n         = color_count + (has_depth ? 1u : 0u);
	uint32_t       why       = kSpRtNone;
	if (!m.valid) {
		why = kSpRtMemo;
	} else if (!SpRtConfigOk(cache)) {
		why = kSpRtCfg;
	} else if (has_depth && depth.depth_clear_enable) {
		why = kSpRtDepthClear;
	} else if (sp.meta0 != m.meta_end) {
		why = kSpRtMeta;
	} else if (color_count != m.color_count || has_depth != m.has_depth || n > m.t.size()) {
		why = kSpRtIds;
	} else {
		for (uint32_t i = 0; i < n && why == kSpRtNone; i++) {
			const bool     d    = i == color_count;
			const auto&    t    = m.t[i];
			const ImageId  id   = d ? depth.image_id : colors[i].image_id;
			const uint32_t slot = d ? UINT32_MAX : colors[i].target_slot;
			const uint32_t ms   = d ? depth.memo_slot : colors[i].memo_slot;
			const uint32_t mv   = d ? depth.memo_version : colors[i].memo_version;
			if (id != t.id || slot != t.slot || ms == UINT32_MAX || ms != t.memo_slot || mv != t.memo_version ||
			    (!d && slot >= RENDER_COLOR_ATTACHMENTS_MAX)) {
				why = kSpRtIds;
				break;
			}
			Image*      img   = cache.m_slot_images.try_get(id); // RC2: never GetImage / []
			const auto& fast  = d ? m_depth_view_fast : m_color_view_fast[slot];
			const auto& desc  = d ? depth.desc : colors[i].desc;
			const auto  stamp = img != nullptr ? img->bind_stamp.load(std::memory_order_acquire) : 0u;
			// AcquireTargetView's whole fast predicate (renderDraw.cpp AcquireTargetView) restated against the live
			// record and the memo (F7: meta_epoch, source_*, view_info, metadata, depth htile mask included).
			if (img == nullptr || !img->registered || img->depth_id || img->binding.needs_rebind ||
			    img->pending_levels != 0 || img->backing.image != t.backing || stamp != t.stamp ||
			    img->source_size != t.source_size || img->source_first_level != t.source_first_level ||
			    !fast.valid || fast.image_id != id || fast.backing != t.backing || fast.view != t.view ||
			    fast.stamp != t.stamp || fast.meta_epoch != sp.meta0 || fast.source_size != img->source_size ||
			    fast.source_first_level != img->source_first_level || !(fast.view_info == desc.view_info) ||
			    !SameTargetMetadata(fast.metadata, desc.info.metadata) ||
			    (d && (fast.htile_clear_mask != img->info.htile_clear_mask ||
			           img->info.htile_clear_mask != t.htile_mask || !SpStencilKept(cache, depth, fast, id)))) {
				why = kSpRtLive;
				break;
			}
			if (img->backing.state_serial != t.state_serial) {
				why = kSpRtSerial;
				break;
			}
			if (!d && img->binding.is_bound != t.is_bound) {
				why = kSpRtBound;
				break;
			}
			sp.img[i] = img;
		}
		if (why == kSpRtNone && has_depth && sp.img[color_count]->binding.is_bound) {
			why = kSpRtDepthSampled;
		}
		if (why == kSpRtNone && !(sp.open0 && CommandBuffer::PassBeginSerial() == m.pass_serial)) {
			why = kSpRtPass;
		}
	}
	sp.would_rt   = why == kSpRtNone;
	sp.would_rt_g = sp.would_rt && sp.serial0 == m.serial_end; // the s119 global witness, nested
	FS::Add(FS::Counter::SpRtDraws, 1);
	if (!FS::PathLap::Running()) {
		FS::Add(FS::Counter::SpRtUntimed, 1);
	}
	if (sp.would_rt) {
		FS::Add(FS::Counter::SpRtWould, 1);
		FS::Add(FS::Counter::SpRtTargets, n);
		if (sp.would_rt_g) {
			FS::Add(FS::Counter::SpRtWouldGlobal, 1);
		}
	} else {
		FS::Add(static_cast<FS::Counter>(static_cast<uint32_t>(FS::Counter::SpRtMissMemo) + why - kSpRtMemo), 1);
	}
	t_sp_rt_slow       = false;
	t_sp_rt_refind     = false;
	t_sp_rt_stamp_race = false;
	t_sp_rt_armed      = true;
}

// After the full AcquireRenderTargets: the bad check (spcen.md s.5.1 + RC1 bit M), the timed dry replay (s.5.3) and
// the strict record (timed: sp_rt_rec_ns, RC5).  Targets are re-looked up with try_get (F8: the slow path can free).
void RenderExecutor::SpRtPost(CommandBuffer& buffer, const RenderColorInfo* colors, uint32_t color_count,
                              const RenderDepthInfo& depth, const RenderState& rendering) {
	namespace FS = Common::FrameStats;
	auto& sp    = *m_sp;
	auto& m     = sp.rt;
	auto& cache = m_context.GetTextureCache();
	t_sp_rt_armed = false;
	const uint64_t serial1   = ImageStateSerial();
	const uint64_t meta1     = cache.MetaEpoch();
	const bool     open1     = buffer.IsRendering();
	const bool     fallback  = t_sp_rt_slow || t_sp_rt_refind;
	const bool     raced     = t_sp_rt_stamp_race; // RC1: decided at the slow-path entry, never re-read after
	const bool     has_depth = static_cast<bool>(depth.image_id);
	const uint32_t n_all     = color_count + (has_depth ? 1u : 0u);
	const uint32_t n         = std::min<uint32_t>(n_all, static_cast<uint32_t>(sp.img.size()));
	sp.raced                 = raced;
	for (uint32_t i = 0; i < n; i++) {
		sp.img[i] = cache.m_slot_images.try_get(i == color_count ? depth.image_id : colors[i].image_id);
	}
	if (sp.would_rt) {
		uint32_t bad = 0;
		if (!(rendering == m.state)) {
			bad |= 0x01; // R: the RenderState it returned
		}
		if (serial1 != sp.serial0) {
			bad |= 0x02; // S: an image state written / a barrier
		}
		if (fallback) {
			bad |= 0x04; // F: FindRenderTarget / FindDepthTarget / the dead re-find
		}
		for (uint32_t i = 0; i < n; i++) {
			const ImageId id  = i == color_count ? depth.image_id : colors[i].image_id;
			const Image*  img = sp.img[i];
			if (id != m.t[i].id || img == nullptr) {
				bad |= 0x08; // I: target identity after the call (or the image is gone)
				continue;
			}
			if (img->binding.attachment_layout != m.t[i].att_layout ||
			    img->binding.attachment_access != m.t[i].att_access) {
				bad |= 0x10; // X: the side stores a hit replays
			}
		}
		if (has_depth && depth.depth_load_clear_enable) {
			bad |= 0x10;
		}
		if (g_pass_extents.max_width != m.extents.max_width || g_pass_extents.max_height != m.extents.max_height ||
		    g_pass_extents.true_kpx != m.extents.true_kpx) {
			bad |= 0x10;
		}
		if (sp.open0 && !open1) {
			bad |= 0x20; // P: the call closed the open pass
		}
		if (meta1 != sp.meta0) {
			bad |= 0x80; // M: the call moved MetaEpoch (no cross-thread writer, RC1)
		}
		if (bad != 0) {
			sp.draw_bad = bad;
			if (raced) {
				FS::Add(FS::Counter::SpRtRace, 1);
			} else {
				FS::Add(FS::Counter::SpRtBad, 1);
				if (sp.rt_logged++ < 40) {
					LOGF("SpRtMismatch: frame=%d why=0x%02x colors=%u depth=%u serial=%" PRIu64 "->%" PRIu64
					     " meta=%" PRIu64 "->%" PRIu64 " fallback=%u\n",
					     m_context.GetGpu().GetFrameNum(), bad, color_count, has_depth ? 1u : 0u, sp.serial0,
					     serial1, sp.meta0, meta1, fallback ? 1u : 0u);
				}
			}
		}
		// Dry replay: the loads and stores a real hit must still make (spcen.md s.5.3), into sp.sink, timed.
		const auto r0      = FS::NowNs();
		sp.sink.state      = m.state;
		sp.sink.extents    = m.extents;
		if (has_depth) {
			sp.sink.depth_load_clear = false; // F8: the depth_load_clear_enable output a hit still stores
		}
		for (uint32_t i = 0; i < n; i++) {
			const auto& t     = m.t[i];
			sp.sink.layout[i] = static_cast<uint32_t>(t.att_layout);
			sp.sink.access[i] = static_cast<uint64_t>(static_cast<VkAccessFlags2>(t.att_access));
			sp.sink.gpu_mod += (sp.img[i] != nullptr && sp.img[i]->IsGpuModified()) ? 1u : 0u; // MarkGpuModified
			sp.sink.usage |= 1u << i;                                                        // usage.*_target
			if (i < color_count) {
				FS::Add(FS::Counter::SpRtRepAtt, 1);     // = RtAttachments
				FS::Add(FS::Counter::SpRtRepKpx, t.kpx); // = RtPixelsK
				sp.sink.w = std::max(sp.sink.w, t.w);    // = the two NoteMax
				sp.sink.h = std::max(sp.sink.h, t.h);
			}
		}
		FS::Add(FS::Counter::SpRtRepNs, FS::NowNs() - r0);
	}
	// Record - strict: the call changed nothing and took no fallback (s119: "only if it emitted no barrier").
	const auto rec0   = FS::NowNs();
	bool       rec_ok = sp.draw_bad == 0 && !raced && n == n_all && SpRtConfigOk(cache) && serial1 == sp.serial0 &&
	              meta1 == sp.meta0 && !fallback &&
	              !(has_depth && (depth.depth_clear_enable || depth.depth_load_clear_enable));
	for (uint32_t i = 0; i < n && rec_ok; i++) {
		rec_ok = sp.img[i] != nullptr &&
		         (i == color_count ? depth.memo_slot : colors[i].memo_slot) != UINT32_MAX &&
		         (i == color_count || colors[i].target_slot < RENDER_COLOR_ATTACHMENTS_MAX);
	}
	if (rec_ok && has_depth && sp.img[color_count]->binding.is_bound) {
		rec_ok = false; // a sampled depth target is never a hit (spcen.md s.4.1 row 9)
	}
	m.valid   = false;
	m.pending = false;
	if (rec_ok) {
		if (!sp.would_rt) {
			// Full record from THIS draw (a clean would-hit keeps the content: it is equal by s.5.1).
			m.color_count = color_count;
			m.has_depth   = has_depth;
			m.state       = rendering;
			m.extents     = g_pass_extents;
			for (uint32_t i = 0; i < n; i++) {
				const bool   d   = i == color_count;
				const Image& img = *sp.img[i];
				auto&        t   = m.t[i];
				t.id             = d ? depth.image_id : colors[i].image_id;
				t.slot           = d ? UINT32_MAX : colors[i].target_slot;
				t.memo_slot      = d ? depth.memo_slot : colors[i].memo_slot;
				t.memo_version   = d ? depth.memo_version : colors[i].memo_version;
				t.backing        = img.backing.image;
				t.view           = d ? rendering.depth_stencil_attachment.image_view
				                     : rendering.color_attachments[colors[i].target_slot].image_view;
				t.stamp              = img.bind_stamp.load(std::memory_order_acquire);
				t.source_first_level = img.source_first_level;
				t.source_size        = img.source_size;
				t.state_serial       = img.backing.state_serial;
				t.htile_mask         = d ? img.info.htile_clear_mask : 0u;
				t.is_bound           = img.binding.is_bound;
				t.att_layout         = img.binding.attachment_layout;
				t.att_access         = img.binding.attachment_access;
				if (d) {
					t.w   = 0;
					t.h   = 0;
					t.kpx = 0;
				} else {
					const auto extent = colors[i].Extent();
					t.w               = extent.width;
					t.h               = extent.height;
					t.kpx             = static_cast<uint64_t>(extent.width) * extent.height / 1024U;
				}
			}
		}
		m.serial_end = serial1;
		m.meta_end   = meta1;
		m.pending    = true; // valid only once BeginRendering pins the pass (SpRtAfterBegin)
	}
	FS::Add(FS::Counter::SpRtRecNs, FS::NowNs() - rec0);
}

// Around BeginRendering (both paths): P2 (an open pass equal to the memo cannot restart) and the pin of the pending
// memo to the pass this draw renders in.  F8: on P2 the pending memo is invalidated, and P2 is bad only when the pass
// that restarted is the memo's own pinned pass; any other restart of a would-hit is the sp_rt_rst diagnostic.
void RenderExecutor::SpRtAfterBegin(bool open_before, uint64_t pass_before) {
	namespace FS = Common::FrameStats;
	auto&          sp         = *m_sp;
	auto&          m          = sp.rt;
	const uint64_t pass_after = CommandBuffer::PassBeginSerial();
	bool           p2         = false;
	if (sp.would_rt && pass_after != pass_before) {
		FS::Add(FS::Counter::SpRtRestart, 1);
		if (open_before && pass_before == m.pass_serial && sp.draw_bad == 0) {
			p2          = true;
			sp.draw_bad = 0x40;
			if (sp.raced) {
				FS::Add(FS::Counter::SpRtRace, 1);
			} else {
				FS::Add(FS::Counter::SpRtBad, 1);
				if (sp.rt_logged++ < 40) {
					LOGF("SpRtMismatch: frame=%d why=0x%02x pass=%" PRIu64 "->%" PRIu64 " memo_pass=%" PRIu64 "\n",
					     m_context.GetGpu().GetFrameNum(), 0x40u, pass_before, pass_after, m.pass_serial);
				}
			}
		}
	}
	if (m.pending) {
		const auto r0 = FS::NowNs();
		m.pending     = false;
		if (p2) {
			m.valid = false;
		} else {
			m.pass_serial = pass_after;
			m.valid       = true;
			FS::Add(FS::Counter::SpRtRecords, 1);
		}
		FS::Add(FS::Counter::SpRtRecNs, FS::NowNs() - r0);
	}
}

RenderState RenderExecutor::AcquireRenderTargets(CommandBuffer& buffer, RenderColorInfo* colors,
                                                 uint32_t color_count, RenderDepthInfo& depth,
                                                 const std::optional<PreparedBindings>& pixel) {
	EXIT_IF(colors == nullptr || color_count > RENDER_COLOR_ATTACHMENTS_MAX);
	auto&       cache = m_context.GetTextureCache();
	RenderState state {};
	state.width                 = std::numeric_limits<uint32_t>::max();
	state.height                = std::numeric_limits<uint32_t>::max();
	state.num_layers            = std::numeric_limits<uint32_t>::max();
	g_pass_extents              = {}; // session 72: rpa_tkpx / rpa_mix, see renderTarget.h
	uint32_t attachment_samples = 0;
	for (uint32_t i = 0; i < color_count; i++) {
		auto& target = colors[i];
		EXIT_IF(!target.image_id || target.target_slot >= RENDER_COLOR_ATTACHMENTS_MAX);
		// Pixel export locations are guest MRT indices. Disabled lower slots must remain holes,
		// otherwise a normal-only decal at MRT2 receives the shader's MRT0 color output.
		state.num_color_attachments = std::max(state.num_color_attachments, target.target_slot + 1);
		// Upstream dd408ff moved this re-find into PrepareGraphicsBindings, ahead of the
		// buffer uploads, and replaced it here with EXIT("color target changed after
		// render-state discovery"). Kept as the (then dead) fallback instead of the abort:
		// after that pass the condition is false, and any path that still changes the
		// target keeps the old behaviour instead of killing the emulator.
		const auto old_image = cache.m_slot_images.try_get(target.image_id);
		if (old_image == nullptr || (!old_image->registered && !old_image->info.data.Empty()) ||
		    old_image->binding.needs_rebind) {
			if (t_sp_rt_armed) {
				t_sp_rt_refind = true; // session 120, gate "spcen": never a memo from this draw
			}
			if (t_rts) [[unlikely]] {
				t_rts_refind = true; // Session 127, knob "rtskip" (I4): never a record from this draw
			}
			if (old_image != nullptr) {
				old_image->binding = {};
			}
			// Restore the guest view before re-finding, exactly as the shared pass does
			// (PrepareGraphicsBindings): FindImage overwrites base_level/base_layer when it remaps
			// the view onto a container image, so a second FindImage over the already remapped
			// descriptor would resolve a level relative to a level, not to the guest surface.
			target.desc.view_info.base_level = target.guest_mip_level;
			target.desc.view_info.base_layer = target.guest_array_layer;
			target.image_id = cache.FindImage(target.desc);
			BindRenderTarget(target.image_id);
		}
		// Gate "rtfast": the LRU touch GetImage did is ResolveRenderColorTarget's (its memo hit
		// and FindImage both touch).
		auto&      image      = cache.m_slot_images[target.image_id];
		// Session 71, candidate C3 (counters only): this slot's guest fast-clear registers, raw.
		// The same register block ResolveRenderColorTarget read for this draw - nothing between
		// PrepareDrawRenderState and here parses PM4 - but read BEFORE that function's
		// metadata-kind decision and its width%1024 / height%1024 guard, which is the point:
		// c3_ct_drop measures what the guard throws away, and no extent of the imgskip population
		// can pass it.
		const auto&    rt_regs = buffer.GetRegisters().GetRenderTarget(target.target_slot);
		const uint32_t guest_clear_regs =
		    (rt_regs.info.cmask_fast_clear_enable ? TextureCache::kRegColorFastClear : 0u) |
		    (rt_regs.cmask.addr != 0 ? TextureCache::kRegColorCmaskAddr : 0u) |
		    (rt_regs.info.dcc_compression_enable ? TextureCache::kRegColorDccEnable : 0u) |
		    (rt_regs.dcc_addr.addr != 0 ? TextureCache::kRegColorDccAddr : 0u) |
		    (rt_regs.dcc.dcc_clear_key_enable ? TextureCache::kRegColorDccKey : 0u);
		const auto rk3_sp_view = Rk3SpBegin(); // Session 126, knob "rk3cen" = 2 (rk3_sp_view_ns)
		const auto image_view = AcquireTargetView(cache, image, target.image_id, target.desc,
		                                          m_color_view_fast[target.target_slot], false,
		                                          guest_clear_regs);
		Rk3SpEnd(rk3_sp_view, Common::FrameStats::Counter::Rk3SpViewNs);
		SetVulkanObjectNameF(m_context.GetGraphics().device, image.backing.image,
		                     "Kyty.MRT{}.Image[guest=0x{:016x} size=0x{:x} format={}]",
		                     target.target_slot, image.info.data.address, image.info.data.size,
		                     static_cast<uint32_t>(image.info.pixel_format));
		SetVulkanObjectNameF(m_context.GetGraphics().device, image_view,
		                     "Kyty.MRT{}.View[guest=0x{:016x} mip={} layer={}+{}]",
		                     target.target_slot, image.info.data.address,
		                     target.desc.view_info.base_level, target.desc.view_info.base_layer,
		                     target.desc.view_info.layer_count);
		EXIT_IF(image.backing.samples != target.desc.info.samples || image_view == nullptr);
		if (attachment_samples == 0) {
			attachment_samples = target.desc.info.samples;
		} else if (attachment_samples != target.desc.info.samples) {
			EXIT("mixed color attachment sample counts are unsupported: %u and %u\n",
			     attachment_samples, target.desc.info.samples);
		}
		const auto& view   = target.desc.view_info;
		const auto  layout = image.binding.is_bound ? vk::ImageLayout::eGeneral
		                                            : vk::ImageLayout::eColorAttachmentOptimal;
		image.binding.attachment_layout = layout;
		image.binding.attachment_access =
		    vk::AccessFlagBits2::eColorAttachmentRead | vk::AccessFlagBits2::eColorAttachmentWrite;
		const auto rk3_sp_tr = Rk3SpBegin(); // Session 126, knob "rk3cen" = 2 (rk3_sp_tr_ns)
		image.Transit(layout, image.binding.attachment_access,
		              ImageSubresourceRange {view.base_level, view.level_count, view.base_layer,
		                                     view.layer_count},
		              vk::CommandBuffer {}, RenderPassEnd::TargetTransit);
		Rk3SpEnd(rk3_sp_tr, Common::FrameStats::Counter::Rk3SpTrNs);
		const auto extent       = target.Extent();
		// Session 67 watchdog: the frame's largest colour target. Taken here, inside the loop over
		// the attachments a draw actually binds, because `state` ends up clamped by the smallest of
		// them and falls back to maxFramebufferWidth when a draw binds none.
		Common::FrameStats::NoteMax(Common::FrameStats::Gauge::RtWidth, extent.width);
		Common::FrameStats::NoteMax(Common::FrameStats::Gauge::RtHeight, extent.height);
		Common::FrameStats::Add(Common::FrameStats::Counter::RtAttachments, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::RtPixelsK,
		                        static_cast<uint64_t>(extent.width) * extent.height / 1024U);
		state.width             = std::min(state.width, extent.width);
		state.height            = std::min(state.height, extent.height);
		state.num_layers        = std::min(state.num_layers, view.layer_count);
		// Session 72: the same attachment measured by its OWN extent, so the pass census can say
		// how much area the minimum above hides (rpa_tkpx, rpa_mix).
		g_pass_extents.max_width  = std::max(g_pass_extents.max_width, extent.width);
		g_pass_extents.max_height = std::max(g_pass_extents.max_height, extent.height);
		g_pass_extents.true_kpx +=
		    static_cast<uint64_t>(extent.width) * extent.height / 1024U;
		auto& attachment        = state.color_attachments[target.target_slot];
		attachment.image_view   = image_view;
		attachment.image_layout = layout;
	}
	bool skc3_depth_mat = false; // Session 124 (item 47(b)): the HTILE clear this acquisition materializes
	if (depth.image_id) {
		const auto owner = cache.m_slot_images.try_get(depth.image_id);
		if (owner == nullptr || !owner->registered || owner->binding.needs_rebind) {
			EXIT("depth target changed after render-state discovery\n");
		}
		auto&       depth_image = cache.m_slot_images[depth.image_id];
		// Session 71, candidate C3 (counters only). depth_clear_enable is the raw DB_RENDER_CONTROL
		// bit; stencil_clear_enable is already AND-ed with the format and the write mask in
		// depthRenderTarget.cpp, so it is the resolved form and is labelled as such. Depth is the
		// ONE attachment whose clear the guest states per pass - colour has no analogue, which is
		// the whole reason C3's premise is in question.
		const uint32_t guest_clear_regs =
		    (depth.depth_clear_enable ? TextureCache::kRegDepthClear : 0u) |
		    (depth.stencil_clear_enable ? TextureCache::kRegStencilClear : 0u);
		const auto  rk3_sp_view = Rk3SpBegin(); // Session 126, knob "rk3cen" = 2 (rk3_sp_view_ns)
		const auto  image_view  = AcquireTargetView(cache, depth_image, depth.image_id, depth.desc,
		                                            m_depth_view_fast, true, guest_clear_regs);
		Rk3SpEnd(rk3_sp_view, Common::FrameStats::Counter::Rk3SpViewNs);
		const auto  rk3_sp_dm   = Rk3SpBegin(); // Session 126, knob "rk3cen" = 2 (rk3_sp_dm_ns, to the feedback search)
		const auto& metadata   = depth.desc.info.metadata;
		if (metadata.kind == ImageMetadataKind::Htile && depth.depth_clear_enable &&
		    !cache.ClearMeta(metadata.range.address)) {
			EXIT("failed to acquire HTile metadata for a depth clear\n");
		}
		const bool meta_clear =
		    metadata.kind == ImageMetadataKind::Htile &&
		    cache.IsMetaCleared(metadata.range.address, depth.desc.view_info.base_layer);
		depth.depth_load_clear_enable = depth.depth_clear_enable || meta_clear;
		skc3_depth_mat                = meta_clear;
		if (meta_clear &&
		    !cache.TouchMeta(metadata.range.address, depth.desc.view_info.base_layer, false)) {
			EXIT("failed to consume HTile clear state\n");
		}
		auto& image = depth_image; // touched by ResolveRenderDepthTarget already
		SetVulkanObjectNameF(m_context.GetGraphics().device, image.backing.image,
		                     "Kyty.DepthTarget.Image[guest=0x{:016x} size=0x{:x} format={}]",
		                     image.info.data.address, image.info.data.size,
		                     static_cast<uint32_t>(image.info.pixel_format));
		SetVulkanObjectNameF(m_context.GetGraphics().device, image_view,
		                     "Kyty.DepthTarget.View[guest=0x{:016x} layer={}+{}]",
		                     image.info.data.address, depth.desc.view_info.base_layer,
		                     depth.desc.view_info.layer_count);
		EXIT_IF(image_view == nullptr || image.backing.samples != depth.desc.info.samples);
		if (attachment_samples == 0) {
			attachment_samples = depth.desc.info.samples;
		} else if (attachment_samples != depth.desc.info.samples) {
			EXIT("mixed color/depth sample counts are unsupported: %u and %u\n", attachment_samples,
			     depth.desc.info.samples);
		}
		const bool feedback = depth.depth_write_enable && pixel &&
		    std::ranges::any_of(pixel->images, [&](const TextureBinding& binding) {
			    if (binding.image_id != depth.image_id ||
			        binding.desc.type != TextureCache::BindingType::Texture) {
				    return false;
			    }
			    const auto native =
			        std::ranges::find(image.views, binding.image_view, &CachedImageView::view);
			    EXIT_IF(native == image.views.end());
			    const auto& sampled = native->info;
			    const auto& target = depth.desc.view_info;
			    return (sampled.aspect & vk::ImageAspectFlagBits::eDepth) &&
			           ImageRangeOverlaps(sampled.base_level, sampled.level_count,
			                              target.base_level, target.level_count) &&
			           ImageRangeOverlaps(sampled.base_layer, sampled.layer_count,
			                              target.base_layer, target.layer_count);
		    });
		Rk3SpEnd(rk3_sp_dm, Common::FrameStats::Counter::Rk3SpDmNs);
		if (feedback && !m_context.GetGraphics().attachment_feedback_loop_enabled) {
			EXIT("depth attachment feedback loop is not supported by the host\n");
		}
		const auto layout = feedback ? vk::ImageLayout::eAttachmentFeedbackLoopOptimalEXT
		                             : depth_attachment_layout(depth);
		// The attachment store writes even when guest depth/stencil tests do not.
		// For a sampled read-only attachment, include the shader read from the first transition.
		// Otherwise AcquireRenderTargets removes it and CommitBindings adds it again on every
		// draw, ending the render pass twice despite an unchanged read-only depth image.
		static const bool combine_readonly_access = [] {
			const auto* value = std::getenv("KYTY_READONLY_DEPTH_ACCESS");
			return value == nullptr || value[0] != '0';
		}();
		const bool sampled_readonly = combine_readonly_access && image.binding.is_bound &&
		    (layout == vk::ImageLayout::eDepthReadOnlyOptimal ||
		     layout == vk::ImageLayout::eStencilReadOnlyOptimal ||
		     layout == vk::ImageLayout::eDepthStencilReadOnlyOptimal);
		const auto access = vk::AccessFlagBits2::eDepthStencilAttachmentRead |
		                    vk::AccessFlagBits2::eDepthStencilAttachmentWrite |
		                    (sampled_readonly ? vk::AccessFlagBits2::eShaderRead : vk::AccessFlags2{});
		image.binding.attachment_layout = layout;
		image.binding.attachment_access = access;
		const auto& view                = depth.desc.view_info;
		if (meta_clear && (std::min(state.width, depth.desc.info.extent.width) <
		                       depth.desc.info.extent.width ||
		                   std::min(state.height, depth.desc.info.extent.height) <
		                       depth.desc.info.extent.height)) {
			// An HTile fast clear covers the whole depth slice, but a load-op clear only reaches
			// the render area of this draw. ASTRO BOT clears HTile and then renders a 1024x1024
			// probe into the 1920x1080 depth buffer before the depth pre-pass: a load-op clear
			// leaves the rest of the buffer stale and every later scene draw fails its depth test
			// there. Clear the attached slice explicitly instead.
			Common::DrawStat::Mark(Common::DrawStat::ImgUp);
			Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
			buffer.EndRendering(RenderPassEnd::Clear);
			image.Transit(vk::ImageLayout::eTransferDstOptimal,
			              vk::AccessFlagBits2::eTransferWrite, {}, buffer.Handle());
			const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eDepth,
			                                       view.base_level, view.level_count,
			                                       view.base_layer, view.layer_count};
			const vk::ClearDepthStencilValue clear {depth.depth_clear_value, 0u};
			buffer.Handle().clearDepthStencilImage(image.backing.image,
			                                       vk::ImageLayout::eTransferDstOptimal, &clear, 1,
			                                       &range);
			buffer.Scheduler().GpuMark(GpuTimeProfiler::Kind::Clear, 2);
			depth.depth_load_clear_enable = depth.depth_clear_enable;
		}
		const auto rk3_sp_tr = Rk3SpBegin(); // Session 126, knob "rk3cen" = 2 (rk3_sp_tr_ns)
		image.Transit(layout, access,
		              ImageSubresourceRange {view.base_level, view.level_count, view.base_layer,
		                                     view.layer_count},
		              vk::CommandBuffer {}, RenderPassEnd::TargetTransit);
		Rk3SpEnd(rk3_sp_tr, Common::FrameStats::Counter::Rk3SpTrNs);
		state.width               = std::min(state.width, depth.desc.info.extent.width);
		state.height              = std::min(state.height, depth.desc.info.extent.height);
		state.num_layers          = std::min(state.num_layers, view.layer_count);
		// Session 72: the depth attachment joins the extent witness for rpa_mix only - its area is
		// already reported separately as rpa_dkpx, so it is not added to true_kpx.
		g_pass_extents.max_width =
		    std::max(g_pass_extents.max_width, depth.desc.info.extent.width);
		g_pass_extents.max_height =
		    std::max(g_pass_extents.max_height, depth.desc.info.extent.height);
		const auto aspects        = ImageViewOps::DepthAspectMask(depth.desc.view_info.format);
		auto&      attachment     = state.depth_stencil_attachment;
		attachment.image_view     = image_view;
		attachment.image_layout   = layout;
		attachment.clear_value[0] = std::bit_cast<uint32_t>(depth.depth_clear_value);
		attachment.clear_value[1] = depth.stencil_clear_value;
		attachment.has_depth      = static_cast<bool>(aspects & vk::ImageAspectFlagBits::eDepth);
		attachment.depth_clear    = depth.depth_load_clear_enable;
		attachment.has_stencil    = static_cast<bool>(aspects & vk::ImageAspectFlagBits::eStencil);
		attachment.stencil_clear  = depth.stencil_clear_enable;
	}
	if (color_count == 0 && !depth.image_id) {
		const auto& limits = buffer.GetGraphics().GetPhysicalDeviceProperties().limits;
		state.width        = limits.maxFramebufferWidth;
		state.height       = limits.maxFramebufferHeight;
	} else if (attachment_samples == 0 ||
	           vulkan_sample_count(attachment_samples) == vk::SampleCountFlagBits {}) {
		EXIT("render state has no valid attachments\n");
	}
	if (state.num_layers == std::numeric_limits<uint32_t>::max()) {
		state.num_layers = 1;
	}
	EXIT_IF(state.width == 0 || state.height == 0 || state.num_layers == 0 ||
	        state.width == std::numeric_limits<uint32_t>::max() ||
	        state.height == std::numeric_limits<uint32_t>::max());
	// Gate "slicecen" (session 118): the targets this draw uses; the depth/stencil target is a write only when the draw
	// writes it (item 4).
	if (Common::Gates::Enabled(Common::Gates::Gate::SliceCensus)) {
		for (uint32_t i = 0; i < color_count; i++) {
			SliceCensus::Image(SliceCensus::ImageKey(colors[i].image_id.index, colors[i].image_id.generation), true);
		}
		if (depth.image_id) {
			SliceCensus::Image(SliceCensus::ImageKey(depth.image_id.index, depth.image_id.generation),
			                   static_cast<bool>(depth.AttachmentWriteAspects()));
		}
	}
	// Session 123, knob "skipceil" = 2 (census, MEASUREMENT ONLY; s.3.1 W1, s.3.3): every attachment is read first
	// (skc_x1_att), then stamped when the draw writes it - colour by the effective write mask of the pipeline
	// (ApplyMask, = colorWriteMask), depth / stencil by AttachmentWriteAspects (the convention of session 118).
	if (Common::SkipCeil::t_mode >= 2) [[unlikely]] {
		const auto& skc_regs = buffer.GetRegisters();
		const auto  rt_mask  = skc_regs.GetRenderTargetMask();
		// Session 124, knob "skipceil" = 3 (closure census, s.3.4): a colour attachment is read when blending is on and
		// the blend equation uses the destination - a destination factor other than ZERO, a source factor naming the
		// destination (DST_ALPHA .. SRC_ALPHA_SATURATE) or MIN / MAX; the host never enables a logic op.
		const auto skc3_blend_reads = [&skc_regs](uint32_t slot) {
			const auto& bc       = skc_regs.GetBlendControl(slot);
			const auto  dst_src  = [](uint8_t factor) { return factor >= 0x06u && factor <= 0x0au; };
			const auto  min_max  = [](uint8_t fcn) { return fcn == 0x02u || fcn == 0x03u; };
			if (!bc.enable || skc_regs.GetRenderTarget(slot).info.blend_bypass) {
				return false;
			}
			const bool color = bc.color_destblend != 0 || dst_src(bc.color_srcblend) || min_max(bc.color_comb_fcn);
			const bool alpha = bc.separate_alpha_blend &&
			                   (bc.alpha_destblend != 0 || dst_src(bc.alpha_srcblend) || min_max(bc.alpha_comb_fcn));
			return color || alpha;
		};
		for (uint32_t i = 0; i < color_count; i++) {
			const bool skc_writes =
			    colors[i].export_mapping.ApplyMask(render_target_mask_slot(rt_mask, colors[i].target_slot)) != 0;
			if (Common::SkipCeil::t_mode == 3) {
				SkcCensus::G3Attachment(cache, colors[i].image_id, colors[i].desc.view_info, skc_writes ? 1u : 0u,
				                        skc3_blend_reads(colors[i].target_slot) ? 1u : 0u);
			}
			SkcCensus::Attachment(cache, colors[i].image_id, skc_writes);
		}
		if (depth.image_id) {
			if (Common::SkipCeil::t_mode == 3) {
				// Depth is read by a test that is on and not ALWAYS, or by the depth-bounds test; stencil by its test.
				const auto skc3_wa    = depth.AttachmentWriteAspects();
				const bool skc3_rd    = (depth.depth_test_enable && depth.depth_compare_op != vk::CompareOp::eAlways) ||
				                        depth.depth_bounds_test_enable;
				const auto skc3_w     = static_cast<uint8_t>((skc3_wa & vk::ImageAspectFlagBits::eDepth ? 2u : 0u) |
				                                             (skc3_wa & vk::ImageAspectFlagBits::eStencil ? 4u : 0u));
				const auto skc3_r     = static_cast<uint8_t>((skc3_rd ? 2u : 0u) | (depth.stencil_test_enable ? 4u : 0u));
				if (skc3_depth_mat) {
					// ROADMAP s122 item 47(b): the materialized HTILE clear precedes the tests - an Lt write of this draw.
					SkcCensus::G3MatDepth(cache, depth.image_id, depth.desc.view_info);
				}
				SkcCensus::G3Attachment(cache, depth.image_id, depth.desc.view_info, skc3_w, skc3_r);
			}
			SkcCensus::Attachment(cache, depth.image_id, static_cast<bool>(depth.AttachmentWriteAspects()));
		}
	}
	return state;
}

// Guest GS/NGG draws use the mesh-shader path, including particle sprites.
// KYTY_GE_DRAWS=0 restores the diagnostic fallback that skips these draws.
static bool GeDrawsEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_GE_DRAWS");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

static std::atomic<uint32_t> g_shader_stage_log_count {0};

// KYTY_GE_TRACE=1: log every GS/NGG draw (skipped or not) without the 32-line cap.
static bool GeTraceEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_GE_TRACE");
		return value != nullptr && value[0] == '1';
	}();
	return enabled;
}

static bool ShouldSkipGeShader(const CommandBuffer& buffer, int frame) {
	const bool trace = GeTraceEnabled();
	if (GeDrawsEnabled() && !trace) {
		return false;
	}
	const auto& ctx         = buffer.GetRegisters();
	const auto& ucfg        = buffer.GetUserConfig();
	const auto& sh_ctx      = buffer.GetShaders();
	const auto& sh_regs     = ctx.GetShaderRegisters();
	const auto& ge_cntl     = ucfg.GetGeControl();
	const auto& vertex_info = sh_ctx.GetVs();
	const auto  stages      = ctx.GetShaderStages();

	const auto is_known_gs_out_prim_type = [](uint32_t value) {
		switch (static_cast<Prospero::GsOutputPrimitiveType>(value)) {
			case Prospero::GsOutputPrimitiveType::kPoints:
			case Prospero::GsOutputPrimitiveType::kLines:
			case Prospero::GsOutputPrimitiveType::kTriangles:
			case Prospero::GsOutputPrimitiveType::k2dRectangle:
			case Prospero::GsOutputPrimitiveType::kRectList: return true;
		}

		return false;
	};

	// GS_W32_EN selects the wave size; it does not enable a geometry stage. In
	// particular, fullscreen vertex draws such as ASTRO BOT's SkyApply use it.
	const auto stage_enables = stages & ~0x00400000u;
	const bool ps5_ngg_vertex_path =
	    stage_enables == 0x02002000 && vertex_info.es_regs.data_addr != 0 &&
	    sh_regs.m_vgtGsMaxVertOut == 0x00000000 &&
	    is_known_gs_out_prim_type(sh_regs.m_vgtGsOutPrimType);

	// Tessellation. The merge brought upstream's native LS/HS/TES path, which this pre-filter
	// used to hide: a patch draw sets HS_EN, which is outside {0, 0x02002000}, so every one of
	// them was logged as an unsupported GE draw and dropped.
	// AgcCreatePrimState (src/libs/agc.cpp) builds VGT_SHADER_STAGES_EN of a patch draw as the
	// GS half's register OR'ed with the HS half's, so the mask is one of the two vertex masks
	// above plus the tessellation stage bits. Field layout (gfx10.3; the wave-size bits are the
	// ones agc.cpp compares between the two halves, 1<<21 for HS and 1<<22 for GS, and the
	// HS_EN/GS_EN tests in shader/shader.cpp use bits 0x4 and 0x20):
	//   LS_EN 1:0, HS_EN 2, ES_EN 4:3, GS_EN 5, VS_EN 7:6, DYNAMIC_HS 8,
	//   HS_W32_EN 21, GS_W32_EN 22.
	// Extra bits a tessellated draw may carry: LS_EN | HS_EN | ES_EN | DYNAMIC_HS = 0x11f.
	// Deliberately still rejected, so that a skipped draw never becomes an abort inside the
	// shader front end: GS_EN (0x20) and the two wave32 bits (0x00600000), each of which
	// PrepareTessellationPrograms refuses with EXIT_NOT_IMPLEMENTED, and any tessellator
	// configuration other than the triangle / fractional-odd / clockwise one that
	// DefineTessellationExecutionModes (spirvEmitterTessellation.cpp) implements.
	constexpr uint32_t tess_stage_bits   = 0x0000011fu;
	constexpr uint32_t tess_reject_bits  = 0x00600020u;
	const uint32_t     tess_rest         = stage_enables & ~tess_stage_bits;
	const uint32_t     tf_param          = sh_regs.m_vgtTfParam;
	const bool         patch_draw        = ucfg.GetPrimType() == Prospero::PrimitiveType::kPatch;
	const bool tessellation_draw =
	    patch_draw && (stages & 0x00000004u) != 0 && (stages & tess_reject_bits) == 0 &&
	    (tess_rest == 0 || tess_rest == 0x02002000) && vertex_info.ls_regs.data_addr != 0 &&
	    vertex_info.hs_regs.data_addr != 0 && vertex_info.es_regs.data_addr != 0 &&
	    vertex_info.gs_regs.data_addr == 0 && (tf_param & 0x3u) == 1u &&
	    ((tf_param >> 2u) & 0x3u) == 2u && ((tf_param >> 5u) & 0x3u) == 2u;

	const bool unsupported_stage_mask =
	    !tessellation_draw && (stage_enables != 0 && stage_enables != 0x02002000);
	const bool unsupported_gs_stage = (vertex_info.es_regs.data_addr != 0 &&
	                                   vertex_info.gs_regs.data_addr != 0 && !ps5_ngg_vertex_path);
	// GE_CNTL group sizes control guest scheduling and do not constrain the host vertex path.
	// These registers describe the GS a tessellation assembly does not have (its own state is
	// VGT_LS_HS_CONFIG / VGT_TF_PARAM, read by PrepareTessellationPrograms), so they are not
	// applied to a recognized patch draw - otherwise GE_NGG_SUBGRP_CNTL alone would keep the
	// whole path dead.
	const bool ge_shader_regs =
	    !tessellation_draw &&
	    ((sh_regs.m_geNggSubgrpCntl != 0x00000000 && sh_regs.m_geNggSubgrpCntl != 0x00000001) ||
	     sh_regs.m_vgtGsMaxVertOut != 0x00000000 ||
	     !is_known_gs_out_prim_type(sh_regs.m_vgtGsOutPrimType) ||
	     sh_regs.m_geMaxOutputPerSubgroup > 0x00000040);
	// The primitive type alone decides tess_active in PipelineCache::GetGraphicsPrograms
	// (pipelineCache.cpp), so every kPatch draw that is not the assembly recognized above still
	// reaches PrepareTessellationPrograms and aborts there: EXIT_NOT_IMPLEMENTED on the stage
	// mask, on a program that is not kHsFront/kHsBack/kGs, or in
	// DefineTessellationExecutionModes. Before the merge kPatch had no host topology and
	// GetDrawTopology skipped such a draw; keep that outcome as a logged skip instead of a dead
	// emulator. This only ever adds skips: today every kPatch draw that gets past this function
	// aborts, so no draw that currently renders can be caught by it.
	const bool unsupported_patch_draw = patch_draw && !tessellation_draw;

	if (unsupported_stage_mask || unsupported_gs_stage || ge_shader_regs ||
	    unsupported_patch_draw) {
		static std::once_flag warning_once;
		std::call_once(warning_once, [] {
			std::printf("Warning: game uses unsupported graphics pipelines; some draw calls were "
			            "skipped.\n");
		});

		const auto log_id = g_shader_stage_log_count.fetch_add(1);
		if (log_id < 32 || trace) {
			LOGF("%s GE shader draw: frame=%d stages=0x%08" PRIx32
			     " prim_group=0x%04" PRIx16 " vert_group=0x%04" PRIx16 " ngg=0x%08" PRIx32
			     " max_out=0x%08" PRIx32 " gs_max_vert=0x%08" PRIx32 " gs_out_prim=0x%08" PRIx32
			     " es=0x%016" PRIx64 " gs=0x%016" PRIx64 " ps=0x%016" PRIx64 " n=%u\n",
			     GeDrawsEnabled() ? "Running" : "Skipping unsupported", frame, stages,
			     ge_cntl.primitive_group_size, ge_cntl.vertex_group_size,
			     sh_regs.m_geNggSubgrpCntl, sh_regs.m_geMaxOutputPerSubgroup,
			     sh_regs.m_vgtGsMaxVertOut, sh_regs.m_vgtGsOutPrimType,
			     vertex_info.es_regs.data_addr, vertex_info.gs_regs.data_addr,
			     sh_ctx.GetPs().ps_regs.data_addr, log_id + 1u);
		}
		return !GeDrawsEnabled();
	}

	return false;
}

static bool DrawHasActivePixelShader(const CommandBuffer& buffer) {
	const auto& ctx              = buffer.GetRegisters();
	const auto& sh_regs          = ctx.GetShaderRegisters();
	const bool  has_color_output = (ctx.GetRenderTargetMask() & sh_regs.m_cbShaderMask) != 0;
	return ShaderAddressValid(buffer.GetShaders().GetPs().ps_regs.data_addr) &&
	       (has_color_output || PixelShaderHasDepthOrCoverageSideEffects(sh_regs));
}

enum class CbColorMode : uint8_t {
	Disable            = 0,
	Normal             = 1,
	EliminateFastClear = 2,
	Resolve            = 3,
	FmaskDecompress    = 5,
	DccDecompress      = 6,
};

static bool ConsumeMetadataColorOperation(const CommandBuffer& buffer) {
	const auto& ctx  = buffer.GetRegisters();
	const auto  mode = ctx.GetColorControl().mode;
	// These special modes run color-buffer metadata or decompression operations. The shader is a
	// vehicle for that operation, and its exported color must not be applied as a normal draw.
	// Kyty stores expanded Vulkan images rather than compressed guest surfaces, so no equivalent
	// hardware pass is emitted. Tracked DCC clear state is materialized on attachment bind;
	// future CMask/FMask support can consume its state through the same TextureCache path.
	return mode == static_cast<uint8_t>(CbColorMode::EliminateFastClear) ||
	       mode == static_cast<uint8_t>(CbColorMode::FmaskDecompress) ||
	       mode == static_cast<uint8_t>(CbColorMode::DccDecompress);
}

struct DrawEmitInfo {
	int32_t  vertex_offset = 0;
	uint32_t first_vertex  = 0;
	uint32_t first_instance = 0;
	// GPU-side indirect draw: the arguments live in guest memory (sanitized copy bound at emit).
	uint64_t   indirect_args_addr = 0;
	vk::Buffer indirect_buffer    = nullptr;
	uint64_t   indirect_offset    = 0;
};

struct DrawIndexBufferSource {
	uint64_t      address   = 0;
	const void*   host_data = nullptr;
	uint64_t      size      = 0;
	vk::IndexType type      = vk::IndexType::eUint16;
	uint32_t      guest_element_size = 0;
};

struct PreparedIndexBuffer {
	vk::Buffer     buffer = nullptr;
	vk::DeviceSize offset = 0;
	vk::IndexType  type   = vk::IndexType::eUint16;
};

static uint64_t VertexBufferDescriptorSize(const ShaderVertexInputBuffer& buffer,
                                           const ShaderVertexInputInfo& info) {
	if (buffer.stride != 0 || buffer.num_records == 0) {
		return static_cast<uint64_t>(buffer.stride) * buffer.num_records;
	}

	uint64_t size = 0;
	for (int i = 0; i < buffer.attr_num; i++) {
		const auto& resource = info.resources[buffer.attr_indices[i]];
		// RDNA2 OOB_SELECT=2 only checks NumRecords != 0. A constant attribute still
		// fetches its entire format; NumRecords is not a byte count in this mode.
		const uint64_t extent = resource.OutOfBounds() == 2
		                            ? static_cast<uint64_t>(buffer.attr_offsets[i]) +
		                                  ShaderRecompiler::Format::GetFormatInfo(resource.Format()).byte_size
		                            : buffer.num_records;
		size = std::max(size, extent);
	}
	return size;
}

struct VertexBufferRange {
	uint64_t                     base_address  = 0;
	uint64_t                     requested_end = 0;
	uint64_t                     acquired_end  = 0;
	std::pair<Buffer*, uint64_t> binding;

	[[nodiscard]] uint64_t RequestedSize() const { return requested_end - base_address; }
};

struct PreparedVertexBuffers {
	static constexpr uint32_t MaxBuffers = ShaderVertexInputInfo::RES_MAX;

	std::array<vk::Buffer, MaxBuffers>     buffers {};
	std::array<vk::DeviceSize, MaxBuffers> offsets {};
	std::array<vk::DeviceSize, MaxBuffers> sizes {};
	uint32_t                               count = 0;
};

static PreparedVertexBuffers AcquireVertexBuffers(CommandBuffer&               buffer,
                                                  const ShaderVertexInputInfo& vs_input_info) {
	EXIT_IF(vs_input_info.buffers_num < 0 ||
	        vs_input_info.buffers_num > ShaderVertexInputInfo::RES_MAX);

	// Collect the non-empty guest vertex ranges.
	std::array<VertexBufferRange, ShaderVertexInputInfo::RES_MAX> ranges {};
	uint32_t                                                      range_count = 0;
	for (int i = 0; i < vs_input_info.buffers_num; i++) {
		const auto& vertex = vs_input_info.buffers[i];
		const auto  size   = VertexBufferDescriptorSize(vertex, vs_input_info);
		if (size == 0) {
			continue;
		}
		if (vertex.addr == 0 || size > UINT64_MAX - vertex.addr) {
			EXIT("invalid vertex buffer range: addr=0x%016" PRIx64 " size=0x%016" PRIx64 "\n",
			     vertex.addr, size);
		}
		ranges[range_count++] = {vertex.addr, vertex.addr + size};
	}

	std::sort(ranges.begin(), ranges.begin() + range_count,
	          [](const VertexBufferRange& left, const VertexBufferRange& right) {
		          return left.base_address < right.base_address;
	          });

	// Merge overlapping or touching ranges before acquiring host buffers.
	std::array<VertexBufferRange, ShaderVertexInputInfo::RES_MAX> merged_ranges {};
	uint32_t                                                      merged_count = 0;
	for (uint32_t i = 0; i < range_count; i++) {
		const auto& range = ranges[i];
		if (merged_count != 0 &&
		    merged_ranges[merged_count - 1].requested_end >= range.base_address) {
			merged_ranges[merged_count - 1].requested_end =
			    std::max(merged_ranges[merged_count - 1].requested_end, range.requested_end);
			continue;
		}
		merged_ranges[merged_count++] = {range.base_address, range.requested_end};
	}

	auto& cache = buffer.GetContext().GetBufferCache();
	for (uint32_t i = 0; i < merged_count; i++) {
		auto& range = merged_ranges[i];
		// PPSA20298
		const auto size =
		    Libs::LibKernel::Memory::ClampRangeSize(range.base_address, range.RequestedSize());
		range.acquired_end = range.base_address + size;
		range.binding      = cache.ObtainBuffer(range.base_address, size, false);
		// Session 123, knob "skipceil" = 2 (census, ROADMAP s122 item 34(v) by the rule of item 33(a)): the acquired merged
		// vertex range is a buffer read of this draw, ahead of its deferred W2 stamps.
		if (Common::SkipCeil::t_mode >= 2) [[unlikely]] {
			SkcCensus::ReadBuffer(cache, range.base_address, size, false);
		}
		SetVulkanObjectNameF(
		    buffer.GetContext().GetGraphics().device, range.binding.first->Handle(),
		    "Kyty.VertexBufferRange[guest=0x{:016x} size=0x{:x}]", range.base_address, size);
	}

	// Rebuild slot bindings, offsetting non-empty slots into their acquired merged range.
	PreparedVertexBuffers prepared;
	prepared.count             = static_cast<uint32_t>(vs_input_info.buffers_num);
	vk::Buffer     null_buffer = nullptr;
	vk::DeviceSize null_size   = 0;
	for (int i = 0; i < vs_input_info.buffers_num; i++) {
		const auto& vertex = vs_input_info.buffers[i];
		const auto  size   = VertexBufferDescriptorSize(vertex, vs_input_info);
		if (size == 0) {
			if (null_buffer == nullptr) {
				const auto& null = cache.GetBuffer(NULL_BUFFER_ID);
				null_buffer      = null.Handle();
				null_size        = null.Size();
			}
			prepared.buffers[i] = null_buffer;
			prepared.offsets[i] = 0;
			// Upstream 3f80151 made CommitVertexBuffers bind sized (bindVertexBuffers2), and
			// prepared.sizes is zero-initialized: an unused slot left at 0 would be bound as a
			// zero-byte range, so every fetch from it would leave its own binding and depend on
			// robustBufferAccess2 for the zeros. Bind the whole null buffer instead. (VK_WHOLE_SIZE
			// is also legal here - VUID-vkCmdBindVertexBuffers2-pSizes-03358 exempts it - but the
			// explicit size is what the descriptor path already hands out for this buffer.)
			prepared.sizes[i]   = null_size;
			continue;
		}

		const auto range = std::find_if(merged_ranges.begin(), merged_ranges.begin() + merged_count,
		                                [&](const VertexBufferRange& value) {
			                                return vertex.addr >= value.base_address &&
			                                       vertex.addr < value.acquired_end;
		                                });
		if (range == merged_ranges.begin() + merged_count) {
			EXIT("vertex buffer address is outside the acquired range: addr=0x%016" PRIx64 "\n",
			     vertex.addr);
		}

		prepared.buffers[i] = range->binding.first->Handle();
		prepared.offsets[i] = range->binding.second + vertex.addr - range->base_address;
		prepared.sizes[i]   = std::min(size, range->acquired_end - vertex.addr);
		SetVulkanObjectNameF(
		    buffer.GetContext().GetGraphics().device, prepared.buffers[i],
		    "Kyty.VertexBuffer[slot={} guest=0x{:016x} size=0x{:x} stride={} records={}]", i,
		    vertex.addr, size, vertex.stride, vertex.num_records);
	}

	return prepared;
}

static uint64_t DrawShaderHash(const ShaderStageRuntime& stage) {
	return (stage && stage.program != nullptr) ? stage.program->shader_hash : 0u;
}

// Session 98 (patch_s98b), KYTY_GPU_MARKERS / KYTY_QUEUE_TRACE=2: the op-ring entry of a draw
// (gpuCheckpoints.h).  Called only when GpuOpsActive(), right before the draw command(s).
static GpuMarkerSite BeginDrawMarker(CommandScheduler& scheduler, uint64_t submit_id,
                                     const DrawCallInfo& draw, const DrawRenderState& state,
                                     bool indirect, bool mesh, uint32_t mesh_groups) {
	const auto kind = mesh       ? GpuMarkerKind::Mesh
	                  : indirect ? (draw.IsIndexed() ? GpuMarkerKind::DrawIndexedIndirect
	                                                 : GpuMarkerKind::DrawIndirect)
	                  : draw.IsIndexed() ? GpuMarkerKind::DrawIndexed
	                                     : GpuMarkerKind::Draw;
	return GpuMarkerBegin(scheduler, kind, submit_id,
	                      state.ps_active ? DrawShaderHash(state.ps_input_info.stage) : 0u,
	                      DrawShaderHash(state.vertex_info[0].stage),
	                      mesh ? mesh_groups : draw.index_count, draw.instance_count, 0u,
	                      BindFloorCurrentOp().armed);
}

// Debug record of a draw: args=phase,index_count,instance_count,first_instance, arg4=PS hash,
// arg5=VS hash (see GpuCheckpoint output).
static void SetDrawDebugPhase(CommandBuffer& buffer, uint64_t submit_id, const DrawCallInfo& draw,
                              const DrawRenderState& state, uint32_t phase,
                              CommandBufferDebugOp op) {
	buffer.SetDebugInfo(static_cast<uint32_t>(op), submit_id, phase, draw.index_count,
	                    draw.instance_count, draw.first_instance,
	                    state.ps_active ? DrawShaderHash(state.ps_input_info.stage) : 0u,
	                    DrawShaderHash(state.vertex_info[0].stage));
}

static void SetDrawDebugPhase(CommandBuffer& buffer, uint64_t submit_id, const DrawCallInfo& draw,
                              const DrawRenderState& state, uint32_t phase) {
	SetDrawDebugPhase(buffer, submit_id, draw, state, phase, draw.debug_op);
}

// KYTY_GPU_CHECKPOINTS: draws are not followed by a barrier, so the breadcrumb written before the
// next operation may execute while an earlier draw is still running. In this mode every draw is
// bracketed: a marker outside the render pass before it and, after it, an all-commands barrier plus
// a DrawComplete marker. A device loss then leaves the hung draw (with its shader hashes) in the
// breadcrumb buffer.
static void RecordDrawStartBreadcrumb(CommandBuffer& buffer, uint64_t submit_id,
                                      const DrawCallInfo& draw, const DrawRenderState& state) {
	if (!buffer.GetGraphics().gpu_breadcrumbs_enabled && !buffer.GetGraphics().diagnostic_checkpoints_enabled) {
		return;
	}
	if (buffer.GetGraphics().gpu_breadcrumbs_enabled) buffer.Scheduler().EndRendering();
	SetDrawDebugPhase(buffer, submit_id, draw, state, 0x800u);
}

static void RecordDrawCompleteBreadcrumb(CommandBuffer& buffer, uint64_t submit_id,
                                         const DrawCallInfo& draw, const DrawRenderState& state) {
	if (!buffer.GetGraphics().gpu_breadcrumbs_enabled && !buffer.GetGraphics().diagnostic_checkpoints_enabled) {
		return;
	}
	if (buffer.GetGraphics().gpu_breadcrumbs_enabled) {
	buffer.Scheduler().EndRendering();
	VulkanMemoryBarrier barrier {};
	barrier.sType         = vk::StructureType::eMemoryBarrier;
	barrier.srcAccessMask = vk::AccessFlagBits::eMemoryWrite;
	barrier.dstAccessMask = vk::AccessFlagBits::eTransferWrite | vk::AccessFlagBits::eMemoryRead;
	buffer.Handle().pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
	                                vk::PipelineStageFlagBits::eTransfer, vk::DependencyFlags {},
	                                1, &barrier, 0, nullptr, 0, nullptr);
	}
	SetDrawDebugPhase(buffer, submit_id, draw, state, 0x900u, CommandBufferDebugOp::DrawComplete);
}

static bool GetDrawTopology(const HW::UserConfig& ucfg, bool auto_draw,
                            vk::PrimitiveTopology& topology) {

	topology = vk::PrimitiveTopology::ePointList;

	switch (ucfg.GetPrimType()) {
		case Prospero::PrimitiveType::kNone: return false;
		case Prospero::PrimitiveType::kPointList:
			topology = vk::PrimitiveTopology::ePointList;
			break;
		case Prospero::PrimitiveType::kLineList: topology = vk::PrimitiveTopology::eLineList; break;
		case Prospero::PrimitiveType::kLineStrip:
			topology = vk::PrimitiveTopology::eLineStrip;
			break;
		case Prospero::PrimitiveType::kTriList:
			topology = vk::PrimitiveTopology::eTriangleList;
			break;
		case Prospero::PrimitiveType::kTriFan:
			topology = vk::PrimitiveTopology::eTriangleFan;
			break;
		case Prospero::PrimitiveType::kTriStrip:
			topology = vk::PrimitiveTopology::eTriangleStrip;
			break;
		case Prospero::PrimitiveType::kPatch:
		case Prospero::PrimitiveType::kRectList:
			topology = vk::PrimitiveTopology::ePatchList;
			break;
		case Prospero::PrimitiveType::kRectListLegacy:
			if (!auto_draw) {
				EXIT("unknown primitive type: %u\n", static_cast<uint32_t>(ucfg.GetPrimType()));
			}
			topology = vk::PrimitiveTopology::eTriangleStrip;
			break;
		case Prospero::PrimitiveType::kQuadListLegacy:
			topology = vk::PrimitiveTopology::eTriangleFan;
			break;
		default: {
			static std::atomic_bool logged = false;
			if (!logged.exchange(true, std::memory_order_relaxed)) {
				std::printf("Skipping draw with unknown primitive type: %u\n",
				            static_cast<uint32_t>(ucfg.GetPrimType()));
			}
			return false;
		}
	}

	return true;
}

static bool ResolvePrimitiveRestart(const CommandBuffer& buffer,
                                    const DrawIndexBufferSource& source) {
	const auto control = buffer.GetUserConfig().GetPrimitiveResetControl();
	EXIT_NOT_IMPLEMENTED((control & ~0x3u) != 0);
	if ((control & 0x1u) == 0) {
		return false;
	}
	switch (buffer.GetUserConfig().GetPrimType()) {
		case Prospero::PrimitiveType::kLineStrip:
		case Prospero::PrimitiveType::kTriFan:
		case Prospero::PrimitiveType::kTriStrip: break;
		default: return false;
	}

	const auto element_size = source.guest_element_size;
	const auto index_mask   = UINT32_MAX >> ((4 - element_size) * 8);
	const auto reset_index  = buffer.GetRegisters().GetPrimitiveResetIndex();
	if ((control & 0x2u) != 0 && (reset_index & ~index_mask) != 0) {
		return false;
	}
	const auto restart_index = reset_index & index_mask;
	if (restart_index == index_mask) {
		// Use native restart; the 8-bit path widens its marker to 0xffff.
		return true;
	}

	// A game can set a custom reset value without using it in the index buffer.
	// Keep restart off in that case; fail if we actually find the value.
	// Scan before preparing draw resources: readback can restart the command buffer.
	EXIT_NOT_IMPLEMENTED(source.address == 0);
	const auto* indices = reinterpret_cast<const uint8_t*>(source.address);
	for (uint64_t offset = 0; offset < source.size; offset += element_size) {
		uint32_t index = 0;
		std::memcpy(&index, indices + offset, element_size);
		EXIT_NOT_IMPLEMENTED(index == restart_index);
	}
	return false;
}

bool RenderExecutor::PrepareDrawRenderState(CommandBuffer& buffer, const DrawCallInfo& draw,
                                            uint32_t            render_target_slice_offset,
                                            DrawRenderState& state) {
	Common::FrameStats::Scope targets_scope(Common::FrameStats::Counter::DrawTargetsNs);
	auto& ctx = buffer.GetRegisters();

	if (ResolveColorTargets(buffer, render_target_slice_offset)) {
		return false;
	}
	if (draw.IsIndexed()) {
		LogDrawPhase(draw.Name(), "ResolveRenderColorTarget");
	}
	for (uint32_t slot = 0; slot < RENDER_COLOR_ATTACHMENTS_MAX; slot++) {
		if (slot == 0 || (render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0 &&
		                  ctx.GetRenderTarget(slot).base.addr != 0)) {
			ResolveRenderColorTarget(buffer, state.color_info[state.color_count],
			                         render_target_slice_offset, slot);
			if (t_rts) [[unlikely]] {
				RtsDraftColor(slot, state.color_count, state.color_info[state.color_count]); // Session 127 (I1)
			}
			if (state.color_info[state.color_count].image_id) {
				state.color_count++;
			}
		}
	}
	if (draw.IsIndexed()) {
		LogDrawPhase(draw.Name(), "ResolveRenderDepthTarget");
	}
	ResolveRenderDepthTarget(buffer, state.depth_info);
	if (t_rts) [[unlikely]] {
		RtsDraftDepth(state.depth_info); // Session 127, knob "rtskip" (I2)
	}

	state.ps_active       = DrawHasActivePixelShader(buffer);
	if (state.color_count == 0 && !state.depth_info.image_id && !state.ps_active) {
		LogFramebufferSkip(draw.Name(), state.color_info[0], state.depth_info, buffer,
		                   draw.index_count, 0);
		return false;
	}

	return true;
}

static void RefreshShaders(CommandBuffer& buffer, const DrawCallInfo& draw,
                           DrawRenderState& state) {
	Common::FrameStats::Scope programs_scope(Common::FrameStats::Counter::DrawProgramsNs);
	auto& ctx    = buffer.GetRegisters();
	auto& sh_ctx = buffer.GetShaders();

	const auto& vertex_shader_info = sh_ctx.GetVs();
	const auto& pixel_shader_info  = sh_ctx.GetPs();
	const auto& shader_regs        = ctx.GetShaderRegisters();

	state.programs      = {};
	// Session 60, B3 (gate "progmemo"): an active pixel stage keeps the previous draw's input
	// info; PipelineCache::GetGraphicsPrograms resets it itself when the registers differ and
	// serves the draw from it when they do not. An inactive stage is reset as before, so that
	// stage.program stays null for it.
	const bool keep_pixel_info = state.ps_active &&
	                             Common::Gates::Enabled(Common::Gates::Gate::ProgMemo) &&
	                             Common::Gates::Enabled(Common::Gates::Gate::DrawStateReuse);
	if (keep_pixel_info) {
	} else if (Common::Gates::Enabled(Common::Gates::Gate::SnapshotKeep) &&
	           Common::Gates::Enabled(Common::Gates::Gate::DrawStateReuse)) {
		// Gate "snapkeep" (session 57, B4): the reset keeps the snapshot storage an earlier draw's
		// pixel stage left here; PipelineCache::GetGraphicsPrograms takes it back for this one. Until
		// then stage.program is null and no reader looks at an inactive pixel stage's resources.
		ShaderRecompiler::IR::ResourceSnapshot kept;
		std::swap(kept, state.ps_input_info.stage.resources);
		state.ps_input_info = {};
		std::swap(kept, state.ps_input_info.stage.resources);
	} else {
		state.ps_input_info = {};
	}
	std::array<Prospero::ColorComponentMapping, RENDER_COLOR_ATTACHMENTS_MAX>
	    target_export_mapping {};
	for (uint32_t i = 0; i < state.color_count; i++) {
		target_export_mapping[state.color_info[i].target_slot] = state.color_info[i].export_mapping;
	}
	auto& pipeline_cache = buffer.GetContext().GetPipelineCache();
	if (draw.IsIndexed()) {
		LogDrawPhase(draw.Name(), "GetGraphicsPrograms");
	}
	state.programs = pipeline_cache.GetGraphicsPrograms(
	    vertex_shader_info, pixel_shader_info, shader_regs, ctx, buffer.GetUserConfig(),
	    target_export_mapping, state.ps_active, state.vertex_info, state.ps_input_info,
	    &state.prog_memo_serial);
}

static PreparedIndexBuffer PrepareIndexBuffer(CommandBuffer&               buffer,
                                              const DrawIndexBufferSource& source) {
	PreparedIndexBuffer prepared;
	if (source.size == 0) {
		return prepared;
	}
	prepared.type = source.type;
	if (source.host_data != nullptr) {
		auto& stream = buffer.GetContext().GetBufferCache().GetUtilityBuffer(MemoryUsage::Stream);
		prepared.offset = stream.Copy(source.host_data, source.size, 16);
		prepared.buffer = stream.Handle();
		SetVulkanObjectNameF(buffer.GetContext().GetGraphics().device, prepared.buffer,
		                     "Kyty.IndexBuffer[guest=transient size=0x{:x} type={}]", source.size,
		                     static_cast<uint32_t>(source.type));
	} else {
		auto [buffer_ptr, offset] =
		    buffer.GetContext().GetBufferCache().ObtainBuffer(source.address, source.size, false);
		// Session 123, knob "skipceil" = 2 (census, ROADMAP s122 item 34(v) by the rule of item 33(a)): the index buffer in
		// guest memory is a buffer read of this draw, ahead of its deferred W2 stamps (host_data above is no buffer read).
		if (Common::SkipCeil::t_mode >= 2) [[unlikely]] {
			SkcCensus::ReadBuffer(buffer.GetContext().GetBufferCache(), source.address, source.size, false);
		}
		prepared.buffer = buffer_ptr->Handle();
		prepared.offset = offset;
		SetVulkanObjectNameF(buffer.GetContext().GetGraphics().device, prepared.buffer,
		                     "Kyty.IndexBuffer[guest=0x{:016x} size=0x{:x} type={}]",
		                     source.address, source.size, static_cast<uint32_t>(source.type));
	}
	return prepared;
}

template <typename Sink>
static void CommitVertexBuffers(Sink& vk_buffer, const PreparedVertexBuffers& prepared) {
	for (uint32_t i = 0; i < prepared.count; i++) {
		EXIT_IF(prepared.buffers[i] == nullptr);
	}
	if (prepared.count != 0) {
		// Guest descriptor bounds must survive allocation merging in the cache (upstream 3f80151):
		// a fetch past the guest descriptor must read zeros, not the neighbour that shares the
		// merged allocation. Both sinks bind sized: RecordCommandWriter carries the sizes through
		// RecordCmd::BindVertexBuffers2, so gate "recpack" keeps the same bounds as a direct draw.
		vk_buffer.bindVertexBuffers2(0, prepared.count, prepared.buffers.data(),
		                             prepared.offsets.data(), prepared.sizes.data(), nullptr);
	}
}

template <typename Sink>
static void CommitIndexBuffer(Sink& vk_buffer, const PreparedIndexBuffer& prepared) {
	if (prepared.buffer == nullptr) {
		return;
	}
	vk_buffer.bindIndexBuffer(prepared.buffer, prepared.offset, prepared.type);
}

static void LogDrawStateIfNeeded(const CommandBuffer& buffer, const DrawCallInfo& draw,
	                             const DrawRenderState& state, uint32_t index_type_and_size,
                                 const void* index_addr) {
	if (!graphics_debug_dump_enabled()) {
		return;
	}

	if (!draw.IsIndexed() &&
	    buffer.GetUserConfig().GetPrimType() != Prospero::PrimitiveType::kRectListLegacy) {
		return;
	}

	if (state.ps_active) {
		LogDrawTargetState(draw.Name(), state.color_info[0], state.depth_info, buffer,
		                   state.ps_input_info, draw.index_count, 0);
	}
	LogDrawInputState(buffer, state.color_info[0], state.vertex_info[0], index_type_and_size,
	                  draw.index_count, index_addr);
}

template <typename Sink>
static void EmitDrawPrimitives(const HW::UserConfig& ucfg, Sink& vk_buffer,
                               const ShaderVertexInputInfo& vs_input_info, const DrawCallInfo& draw,
                               const DrawEmitInfo& emit) {
	switch (ucfg.GetPrimType()) {
		case Prospero::PrimitiveType::kPointList:
		case Prospero::PrimitiveType::kLineList:
		case Prospero::PrimitiveType::kLineStrip:
		case Prospero::PrimitiveType::kTriList:
		case Prospero::PrimitiveType::kTriFan:
		case Prospero::PrimitiveType::kTriStrip:
		case Prospero::PrimitiveType::kRectList:
		case Prospero::PrimitiveType::kPatch:
			if (emit.indirect_buffer != nullptr) {
				if (draw.IsIndexed()) {
					vk_buffer.drawIndexedIndirect(emit.indirect_buffer, emit.indirect_offset, 1,
					                              sizeof(vk::DrawIndexedIndirectCommand));
				} else {
					vk_buffer.drawIndirect(emit.indirect_buffer, emit.indirect_offset, 1,
					                       sizeof(vk::DrawIndirectCommand));
				}
			} else if (draw.IsIndexed()) {
				vk_buffer.drawIndexed(draw.index_count, draw.instance_count, 0, emit.vertex_offset,
				                      emit.first_instance);
			} else {
				vk_buffer.draw(draw.index_count, draw.instance_count, emit.first_vertex,
				               emit.first_instance);
			}
			break;
		case Prospero::PrimitiveType::kRectListLegacy:
			EXIT_NOT_IMPLEMENTED(emit.indirect_buffer != nullptr);
			if (draw.IsIndexed()) {
				EXIT("unknown primitive type: %u\n", static_cast<uint32_t>(ucfg.GetPrimType()));
			}
			// Sarah
			EXIT_NOT_IMPLEMENTED(!(draw.index_count == 3 && vs_input_info.buffers_num == 0));
			vk_buffer.draw(4, draw.instance_count, emit.first_vertex, emit.first_instance);
			break;
		case Prospero::PrimitiveType::kQuadListLegacy:
			EXIT_NOT_IMPLEMENTED(emit.indirect_buffer != nullptr);
			EXIT_NOT_IMPLEMENTED((draw.index_count & 0x3u) != 0);
			for (uint32_t i = 0; i < draw.index_count; i += 4) {
				if (draw.IsIndexed()) {
					vk_buffer.drawIndexed(4, draw.instance_count, i, emit.vertex_offset,
					                      emit.first_instance);
				} else {
					vk_buffer.draw(4, draw.instance_count, i + emit.first_vertex,
					               emit.first_instance);
				}
			}
			break;
		default: EXIT("unknown primitive type: %u\n", static_cast<uint32_t>(ucfg.GetPrimType()));
	}
}

namespace {

// Session 86, gate "drawmerge" (MEASUREMENT ONLY, ROADMAP.md route D4).  The bounds are the
// translator's own hard caps, so exceeding one is a condition the translator forbids; a draw that
// does exceed one is EXCLUDED (dm_over) rather than truncated into a false match.
constexpr uint32_t DrawMergeStages   = 4;
constexpr uint32_t DrawMergeImages   = 64;
constexpr uint32_t DrawMergeSamplers = 32;
constexpr uint32_t DrawMergeBuffers  = 32;

struct DrawMergePrev {
	uint64_t pipeline = 0;
	bool     valid    = false;
	uint32_t img_n = 0, smp_n = 0, buf_n = 0, sd_n = 0;
	std::array<uint64_t, DrawMergeStages * DrawMergeImages>   image_view {};
	std::array<uint64_t, DrawMergeStages * DrawMergeSamplers> sampler {};
	std::array<uint64_t, DrawMergeStages * DrawMergeBuffers>  buffer_handle {};
	std::array<uint64_t, DrawMergeStages * DrawMergeBuffers>  buffer_offset {};
	std::array<uint64_t, DrawMergeStages * DrawMergeBuffers>  buffer_range {};
	// Session 86, correction 1: ONE FNV-1a HASH A STAGE, not raw dwords.  ShaderDataDwords()
	// is not bounded by any translator cap, so a fixed array made dm_over read 454 a frame
	// instead of 0 and silently deleted 8.7 % of the population.  A hash has no cap.
	std::array<uint64_t, DrawMergeStages>                     shader_data {};
};

constinit DrawMergePrev g_draw_merge_prev {};

// Session 94: returns the dm_buf1_ok verdict of THIS draw (false when bdacap is off), so the
// mergecost census can book the draw's time by it.  Nothing else changed.
bool NoteDrawMerge(uint64_t pipeline, std::span<PreparedBindings* const> stages, uint64_t stream,
                   bool mesh, bool verify) {
	namespace FS  = Common::FrameStats;
	using Counter = FS::Counter;

	// NO value-initialisers: only the live prefixes are read, and zeroing 6.6 KiB on every one of
	// ~5 000 draws a frame would cost more than the census it serves.
	std::array<uint64_t, DrawMergeStages * DrawMergeImages>   img;
	std::array<uint64_t, DrawMergeStages * DrawMergeSamplers> smp;
	std::array<uint64_t, DrawMergeStages * DrawMergeBuffers>  bufh;
	std::array<uint64_t, DrawMergeStages * DrawMergeBuffers>  bufo;
	std::array<uint64_t, DrawMergeStages * DrawMergeBuffers>  bufr;
	std::array<uint8_t, DrawMergeStages * DrawMergeBuffers>   bufring;
	// Session 93, gate "bdacap": the BdaCapClass NativeStorageBuffer gave each buffer slot,
	// carried over from PreparedBindings so dm_buf1_ok can name the class of the ONE slot
	// that differs.  Filled ONLY while bdacap is armed, and read only under the same gate.
	std::array<uint8_t, DrawMergeStages * DrawMergeBuffers>   bufcls;
	std::array<uint64_t, DrawMergeStages>                     sd;
	uint32_t img_n = 0, smp_n = 0, buf_n = 0, sd_n = 0, ring = 0;
	bool     over  = stages.size() > DrawMergeStages;
	const bool bdacap = Common::Gates::Enabled(Common::Gates::Gate::BdaCap);
	for (const auto* prepared: stages) {
		if (over) {
			break;
		}
		// The three bounds left are the translator's own hard caps - MaxImages 64,
		// MaxSamplers 32, MaxBuffers 32 - which sl_over = 0 has proved every frame since
		// session 84, so dm_over now counts a condition the translator forbids.
		if (prepared->images.size() > DrawMergeImages ||
		    prepared->samplers.size() > DrawMergeSamplers ||
		    prepared->buffers.size() > DrawMergeBuffers) {
			over = true;
			break;
		}
		for (const auto& binding: prepared->images) {
			img[img_n++] = static_cast<uint64_t>(
			    reinterpret_cast<uintptr_t>(static_cast<VkImageView>(binding.image_view)));
		}
		for (const auto sampler: prepared->samplers) {
			smp[smp_n++] = static_cast<uint64_t>(
			    reinterpret_cast<uintptr_t>(static_cast<VkSampler>(sampler)));
		}
		const uint32_t stage_base = buf_n;
		for (const auto& view: prepared->buffers) {
			const auto handle = static_cast<uint64_t>(
			    reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(view.buffer)));
			bufring[buf_n] = (handle != 0 && handle == stream) ? uint8_t {1} : uint8_t {0};
			ring += bufring[buf_n];
			bufh[buf_n] = handle;
			bufo[buf_n] = static_cast<uint64_t>(view.offset);
			bufr[buf_n] = static_cast<uint64_t>(view.range);
			buf_n++;
		}
		// Session 93, gate "bdacap": buffer_class is parallel to buffers by construction; the
		// size guard is belt and braces, and at bdacap = 0 this loop does not run at all.
		if (bdacap) {
			for (uint32_t bi = 0; bi < static_cast<uint32_t>(prepared->buffers.size()); bi++) {
				bufcls[stage_base + bi] = bi < prepared->buffer_class.size()
				                              ? prepared->buffer_class[bi]
				                              : uint8_t {0};
			}
		}
		uint64_t hash = 1469598103934665603ull;
		for (const auto dword: prepared->shader_data) {
			hash = (hash ^ dword) * 1099511628211ull;
		}
		sd[sd_n++] = hash;
	}
	FS::Add(Counter::DrawMergeDraws, 1);
	if (over) {
		// The previous signature is not comparable with anything after an excluded draw.
		FS::Add(Counter::DrawMergeOver, 1);
		g_draw_merge_prev.valid = false;
		return false;
	}
	FS::Add(Counter::DrawMergeBufSlots, buf_n);
	FS::Add(Counter::DrawMergeRing, ring);
	FS::Add(Counter::DrawMergeMesh, mesh ? 1u : 0u);

	auto&      prev      = g_draw_merge_prev;
	const bool same_pipe = prev.valid && prev.pipeline == pipeline;
	// Session 86, correction 2: the per-slot DIFFERENCE counters are accumulated whenever the
	// LENGTHS match, whether or not the pipeline does, so that dm_img_d is a usable
	// consistency reading against slotstat, which compares every commit.  The CLASSIFICATION
	// is unchanged and still requires the pipeline.
	const bool same_len = prev.valid && prev.img_n == img_n && prev.smp_n == smp_n &&
	                      prev.buf_n == buf_n && prev.sd_n == sd_n;
	const bool same_shape = same_pipe && same_len;
	uint32_t d_img = 0, d_smp = 0, d_buf = 0, d_bufnr = 0, d_sd = 0;
	// Session 93, gate "bdacap": WHICH non-ring slot differed.  Meaningless unless
	// d_bufnr == 1, and read only then.
	uint32_t nr_index = 0;
	if (same_len) {
		for (uint32_t i = 0; i < img_n; i++) {
			d_img += (img[i] != prev.image_view[i]) ? 1u : 0u;
		}
		for (uint32_t i = 0; i < smp_n; i++) {
			d_smp += (smp[i] != prev.sampler[i]) ? 1u : 0u;
		}
		for (uint32_t i = 0; i < buf_n; i++) {
			const bool differs = bufh[i] != prev.buffer_handle[i] ||
			                     bufo[i] != prev.buffer_offset[i] ||
			                     bufr[i] != prev.buffer_range[i];
			d_buf += differs ? 1u : 0u;
			d_bufnr += (differs && bufring[i] == 0) ? 1u : 0u;
			nr_index = (differs && bufring[i] == 0) ? i : nr_index;
		}
		for (uint32_t i = 0; i < sd_n; i++) {
			d_sd += (sd[i] != prev.shader_data[i]) ? 1u : 0u;
		}
		FS::Add(Counter::DrawMergeImageDiffs, d_img);
		FS::Add(Counter::DrawMergeSamplerDiffs, d_smp);
		FS::Add(Counter::DrawMergeBufferDiffs, d_buf);
	}
	FS::Add(Counter::DrawMergePipe, same_pipe ? 1u : 0u);

	// First match wins, in this order.  !same_shape (which includes !same_pipe and every length
	// change) falls straight through to dm_no.
	const auto classify = [&](uint32_t buffer_diffs, Counter same, Counter push, Counter one) {
		if (!same_shape || d_img != 0 || d_smp != 0) {
			return false;
		}
		if (buffer_diffs == 0) {
			FS::Add(d_sd == 0 ? same : push, 1);
			return true;
		}
		if (buffer_diffs == 1) {
			FS::Add(one, 1);
			return true;
		}
		return false;
	};
	const bool hit = classify(d_buf, Counter::DrawMergeSame, Counter::DrawMergePush,
	                          Counter::DrawMergeBuf1);
	classify(d_bufnr, Counter::DrawMergeSameNr, Counter::DrawMergePushNr,
	         Counter::DrawMergeBuf1Nr);
	// Session 93, gate "bdacap": of the draws dm_buf1_nr counts, those whose ONE differing
	// non-ring buffer slot NativeStorageBuffer classified bc_ok.  The predicate is the
	// dm_buf1_nr branch of classify() written out, because classify() also answers true for
	// its two zero-difference branches.  same_shape implies same_len, so nr_index was
	// written by the loop above, and bufcls was filled because bdacap is the first operand.
	const bool buf1_ok = bdacap && same_shape && d_img == 0 && d_smp == 0 && d_bufnr == 1 &&
	                     bufcls[nr_index] == static_cast<uint8_t>(BdaCapClass::Ok);
	if (buf1_ok) {
		FS::Add(Counter::DrawMergeBuf1Ok, 1);
	}
	FS::Add(Counter::DrawMergeNo, hit ? 0u : 1u);

	if (verify && same_len) {
		// The independent second implementation.  These are plain arrays of uint64_t / uint32_t,
		// which carry NO padding - session 83's bp_bad = 177 came from memcmp over a padded
		// AGGREGATE, which this deliberately is not - and only the live prefix is compared.
		const bool memcmp_same =
		    std::memcmp(img.data(), prev.image_view.data(), size_t {img_n} * sizeof(uint64_t)) == 0 &&
		    std::memcmp(smp.data(), prev.sampler.data(), size_t {smp_n} * sizeof(uint64_t)) == 0 &&
		    std::memcmp(bufh.data(), prev.buffer_handle.data(), size_t {buf_n} * sizeof(uint64_t)) == 0 &&
		    std::memcmp(bufo.data(), prev.buffer_offset.data(), size_t {buf_n} * sizeof(uint64_t)) == 0 &&
		    std::memcmp(bufr.data(), prev.buffer_range.data(), size_t {buf_n} * sizeof(uint64_t)) == 0 &&
		    std::memcmp(sd.data(), prev.shader_data.data(), size_t {sd_n} * sizeof(uint64_t)) == 0;
		const bool fields_same = d_img == 0 && d_smp == 0 && d_buf == 0 && d_sd == 0;
		if (memcmp_same != fields_same) {
			FS::Add(Counter::DrawMergeBad, 1);
			static std::atomic<uint32_t> logged {0};
			if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
				LOGF("DrawMergeVerify: MISMATCH memcmp=%d fields=%d img=%u smp=%u buf=%u sd=%u\n",
				     memcmp_same ? 1 : 0, fields_same ? 1 : 0, d_img, d_smp, d_buf, d_sd);
			}
		}
	}

	prev.pipeline = pipeline;
	prev.valid    = true;
	prev.img_n    = img_n;
	prev.smp_n    = smp_n;
	prev.buf_n    = buf_n;
	prev.sd_n     = sd_n;
	std::memcpy(prev.image_view.data(), img.data(), size_t {img_n} * sizeof(uint64_t));
	std::memcpy(prev.sampler.data(), smp.data(), size_t {smp_n} * sizeof(uint64_t));
	std::memcpy(prev.buffer_handle.data(), bufh.data(), size_t {buf_n} * sizeof(uint64_t));
	std::memcpy(prev.buffer_offset.data(), bufo.data(), size_t {buf_n} * sizeof(uint64_t));
	std::memcpy(prev.buffer_range.data(), bufr.data(), size_t {buf_n} * sizeof(uint64_t));
	std::memcpy(prev.shader_data.data(), sd.data(), size_t {sd_n} * sizeof(uint64_t));
	return buf1_ok;
}

} // namespace

// Session 127, knob "rtskip": the latch, cold half (s.4.1).  Runs while the knob is nonzero or the previous draw was armed.
// Settles the previous armed draw that never reached its post (N12, [RC7]), decides the value (refusals s.4.2), and on an
// armed draw takes the record of its context: the post gives it back, any return before the post leaves the context
// without a record.
[[gnu::noinline]] void RenderExecutor::RtsLatchSlow(CommandBuffer& buffer, uint32_t value) {
	namespace FS = Common::FrameStats;
	namespace G  = Common::Gates;
	using C      = FS::Counter;
	if (t_rts_live && t_rts >= 2) {
		if (t_rts_take != nullptr) {
			FS::Add(C::RtsLost, 1);
		}
		if (t_rts_at_a) {
			FS::Add(C::RtsEarly, 1);
		}
	}
	t_rts_live   = false;
	t_rts_at_a   = false;
	t_rts_pa     = false;
	t_rts_pb     = false;
	t_rts_b      = false;
	t_rts_reg    = false;
	t_rts_pin    = false;
	t_rts_slow   = false;
	t_rts_race   = false;
	t_rts_refind = false;
	t_rts_bits   = 0;
	t_rts_inj    = false; // track F, F30o: a perturbed draw that never reached its post
	t_rts_take   = nullptr;
	t_rts_entry  = nullptr;
	uint32_t armed = 0;
	if (value != 0) {
		const char* reason = nullptr;
		uint32_t    bit    = 0;
		if (!Common::SkipCeil::t_gpu) {
			FS::Add(C::RtsXthr, 1);
		} else if (G::Value(G::Knob::Rk3Cen) != 0) {
			reason = "rk3cen";
			bit    = 1;
		} else if (G::Value(G::Knob::Spine) != 0) {
			reason = "spine";
			bit    = 2;
		} else if (G::Enabled(G::Gate::SamePassCensus)) {
			reason = "spcen";
			bit    = 3;
		} else if (G::Enabled(G::Gate::SliceCensus)) {
			reason = "slicecen";
			bit    = 4;
		} else if (G::Value(G::Knob::SkipCeil) != 0) {
			reason = "skipceil";
			bit    = 5;
		} else if (G::Enabled(G::Gate::BindFloor)) {
			reason = "bindfloor";
			bit    = 6;
		} else if (G::Value(G::Knob::M4Baton) != 0) {
			reason = "m4baton";
			bit    = 7;
		} else if (!G::Enabled(G::Gate::RenderTargetFast)) {
			reason = "rtfast";
			bit    = 8;
		} else if (graphics_debug_dump_enabled()) {
			reason = "graphics_debug_dump";
			bit    = 9;
		} else if (!FastRenderMemoEnabled()) {
			reason = "render_memo_fast";
			bit    = 10;
		} else if (m_context.GetTextureCache().m_readback_linear_images) {
			reason = "readback_linear_images";
			bit    = 11;
		} else {
			armed = value;
		}
		if (reason != nullptr) {
			FS::Add(C::RtsRefuse, 1);
			if ((t_rts_logged & (1u << bit)) == 0) {
				t_rts_logged |= 1u << bit;
				LOGF("RtSkip: refused reason=%s\n", reason);
			}
		}
	}
	if (armed == 0) {
		// Leaving the armed state (or refused): the records go (s.4.1).
		if (t_rts != 0 && t_rts_table != nullptr) {
			t_rts_table->used = 0;
		}
		t_rts_last_ctx = nullptr;
		t_rts          = 0;
		Common::Rk3::t_hooks &= ~Common::Rk3::HookRts;
		return;
	}
	if (t_rts_table == nullptr) {
		t_rts_table = new RtsTable();
	}
	if ((t_rts_logged & (1u << (16u + armed))) == 0) {
		t_rts_logged |= 1u << (16u + armed);
		LOGF("RtSkip: mode %u ctx_slots=%u groups=%u rec_bytes=%u\n", armed,
		     static_cast<uint32_t>(t_rts_table->e.size()), Rk3::GroupCount, static_cast<uint32_t>(sizeof(RtsRecord)));
	}
	t_rts = armed; // a change between 1, 2 and 3 keeps the records
	Common::Rk3::t_hooks |= Common::Rk3::HookRts;
	if (!buffer.IsInvalid()) {
		t_rts_entry = RtsFindOrAdd(*t_rts_table, &buffer.GetRegisters());
		if (t_rts_entry != nullptr && t_rts_entry->has_rec) {
			t_rts_take           = &t_rts_entry->rec; // N12: taken until the post of this draw
			t_rts_entry->has_rec = false;
		}
	}
	t_rts_live = true;
}

// Session 127, knob "rtskip": place A (s.4.3), instead of PrepareDrawRenderState.  PA is evaluated by reading only
// (try_get, no Touch, no store); at 1 and PA the resolution is replaced by the record's outputs and the stores of its memo
// hits; otherwise the full resolution runs with its draft (I1, I2), and at 2/3 and PA it is compared with the record.
bool RenderExecutor::RtsPlaceA(CommandBuffer& buffer, const DrawCallInfo& draw, uint32_t render_target_slice_offset,
                               DrawRenderState& state) {
	namespace FS = Common::FrameStats;
	namespace G  = Common::Gates;
	using C      = FS::Counter;
	auto&       cache = m_context.GetTextureCache();
	const auto& ctx   = buffer.GetRegisters();
	const void* ctx_p = &ctx;
	FS::Add(C::RtsN, 1);
	// Item 79(v)(1): the thread's draw state holds what the last armed draw that reached A left there; only a draw of the
	// same context may take the record over it.  Written here, before any return: its resolution writes the state already.
	const bool same_ctx = t_rts_last_ctx == ctx_p;
	t_rts_last_ctx      = ctx_p;
	t_rts_at_a          = true;
	if (t_rts_entry != nullptr) {
		t_rts_gen_a = t_rts_entry->gen;
	}
	const RtsRecord* rec = t_rts_take;
	t_rts_reg            = rec != nullptr && RtsMoved(t_rts_entry->gen, rec->gen, rec->rel);
	auto&      memo      = Memo();
	const auto memo_same = [&memo](const RtsRecord& r) {
		for (uint32_t i = 0; i < r.nv; i++) {
			const auto& v = r.v[i];
			if (v.memo_slot != UINT32_MAX &&
			    !(memo.colors[v.memo_slot].valid && memo.colors[v.memo_slot].version == v.memo_version)) {
				return false;
			}
		}
		return r.dmemo_slot != UINT32_MAX && memo.depths[r.dmemo_slot].valid &&
		       memo.depths[r.dmemo_slot].version == r.dmemo_version;
	};
	// The resolution's own re-validation of a memo hit (colorRenderTarget.cpp:143-144, depthRenderTarget.cpp:298-299).
	const auto live = [&cache](ImageId id) {
		const auto* image = cache.m_slot_images.try_get(id);
		return image != nullptr && !(!image->registered && !image->info.data.Empty()) && !image->binding.needs_rebind;
	};
	// PA: the first failing item is the reason; value 3 does not apply item 3 ([RC2]: reg is computed anyway).
	C why = C::Count;
	if (rec == nullptr || !rec->pinned || !same_ctx) {
		why = C::RtsXaRec;
	} else if (!(G::Enabled(G::Gate::RenderTargetFast) && !graphics_debug_dump_enabled() &&
	             !cache.m_readback_linear_images && FastRenderMemoEnabled())) {
		why = C::RtsXaCfg;
	} else if (t_rts != 3 && t_rts_reg) {
		why = C::RtsXaReg;
	} else if (render_target_slice_offset != rec->slice) {
		why = C::RtsXaArg;
	} else if (ctx.GetColorControl().mode == 3 || std::bit_cast<uint32_t>(ctx.GetDepthBoundsMin()) != rec->bmin ||
	           std::bit_cast<uint32_t>(ctx.GetDepthBoundsMax()) != rec->bmax) {
		why = C::RtsXaUnh;
	} else if (!memo_same(*rec)) {
		why = C::RtsXaMemo;
	} else {
		for (uint32_t i = 0; i < rec->color_count && why == C::Count; i++) {
			if (!live(rec->pre[i].image_id)) {
				why = C::RtsXaImg;
			}
		}
		if (why == C::Count && rec->pre_depth.image_id && !live(rec->pre_depth.image_id)) {
			why = C::RtsXaImg;
		}
	}
	t_rts_pa = why == C::Count;
	if (!t_rts_pa) {
		FS::Add(why, 1);
	}
	if (t_rts == 1 && t_rts_pa) {
		// The skip (s.3.2): the record's outputs, then the stores of the resolution's memo hits in its order - the LRU
		// touch and BindRenderTarget of every colour target by slot, then of the depth target.
		for (uint32_t i = 0; i < rec->n_idx; i++) {
			state.color_info[i] = rec->pre[i];
		}
		state.color_count = rec->color_count;
		state.depth_info  = rec->pre_depth;
		const auto replay = [&](ImageId id) {
			auto* image               = cache.m_slot_images.try_get(id);
			image->tick_accessed_last = m_context.AgeTick();
			cache.TouchImage(*image);
			BindRenderTarget(id);
		};
		for (uint32_t i = 0; i < rec->color_count; i++) {
			replay(rec->pre[i].image_id);
		}
		if (rec->pre_depth.image_id) {
			replay(rec->pre_depth.image_id);
		}
		state.ps_active = DrawHasActivePixelShader(buffer);
		if (state.color_count == 0 && !state.depth_info.image_id && !state.ps_active) {
			LogFramebufferSkip(draw.Name(), state.color_info[0], state.depth_info, buffer, draw.index_count, 0);
			return false;
		}
		return true;
	}
	// The full resolution with its draft.
	auto& d         = t_rts_table->draft;
	d.nv            = 0;
	d.dmemo_slot    = UINT32_MAX;
	d.dmemo_version = 0;
	d.bound0        = m_bound_images.size();
	const bool prepared = PrepareDrawRenderState(buffer, draw, render_target_slice_offset, state);
	// [RC9]: "fresh before the capture" is sampled here, right after the resolution, before RefreshShaders.
	uint32_t n_idx = 0;
	for (uint32_t i = 0; i < d.nv; i++) {
		n_idx = std::max(n_idx, d.v[i].idx + 1u);
	}
	d.n_idx = n_idx;
	if (prepared && !t_rts_pa) {
		// The record a full update would take (s.4.4): the resolution half.
		for (uint32_t i = 0; i < n_idx; i++) {
			d.pre[i] = state.color_info[i];
		}
		d.color_count = state.color_count;
		d.pre_depth   = state.depth_info;
		d.slice       = render_target_slice_offset;
		d.mask        = ctx.GetRenderTargetMask();
		d.bmin        = std::bit_cast<uint32_t>(ctx.GetDepthBoundsMin());
		d.bmax        = std::bit_cast<uint32_t>(ctx.GetDepthBoundsMax());
	}
	if (t_rts >= 2 && t_rts_pa) {
		// The resolution half of the self-check (s.5.1 step 2, s.5.2).
		FS::Add(C::RtsPa, 1);
		FS::Add(C::RtsChk, 1);
		if (rec->age >= 1) {
			FS::Add(C::RtsChain2, 1);
		}
		FS::NoteMax(FS::Gauge::RtsChainMax, rec->age);
		uint32_t   bits   = 0;
		// F: the record returns false exactly for "no target and no active pixel stage" (the framebuffer skip).
		const bool expect = !(rec->color_count == 0 && !rec->pre_depth.image_id && !DrawHasActivePixelShader(buffer));
		if (prepared != expect) {
			bits |= 0x008u;
		}
		// O, U: the outputs before the capture against the record's.
		if (n_idx != rec->n_idx || state.color_count != rec->color_count) {
			bits |= 0x001u;
		}
		for (uint32_t i = 0; i < std::min(n_idx, rec->n_idx); i++) {
			bits |= RtsDiffColor(state.color_info[i], rec->pre[i]);
		}
		bits |= RtsDiffDepth(state.depth_info, rec->pre_depth);
		// K: no visited memo slot of the record was stored into or re-found by this resolution.
		if (!memo_same(*rec)) {
			bits |= 0x002u;
		}
		// T: the tail of m_bound_images this resolution added is the record's targets in resolution order.
		const uint32_t expect_n = rec->color_count + (rec->pre_depth.image_id ? 1u : 0u);
		if (m_bound_images.size() != d.bound0 + expect_n) {
			bits |= 0x004u;
		} else {
			for (uint32_t i = 0; i < expect_n; i++) {
				const ImageId id = i < rec->color_count ? rec->pre[i].image_id : rec->pre_depth.image_id;
				if (m_bound_images[d.bound0 + i] != id) {
					bits |= 0x004u;
				}
			}
		}
		t_rts_bits = bits;
		if (!prepared && bits != 0) {
			// The draw ends here (no post): its report is made now.
			RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, state.color_count,
			          static_cast<bool>(state.depth_info.image_id), 0);
		}
	}
	return prepared;
}

// Session 127, knob "rtskip": place B (s.4.3), instead of AcquireRenderTargets.  PB is evaluated by reading only after PA;
// at 1 and PB the capture is replaced by the record's RenderState and the stores it makes on unchanged images; otherwise
// the full capture runs between the snapshots the strict record (s.4.4) and the self-check (s.5.2) read.
RenderState RenderExecutor::RtsPlaceB(CommandBuffer& buffer, DrawRenderState& state,
                                      const std::optional<PreparedBindings>& pixel) {
	namespace FS = Common::FrameStats;
	namespace G  = Common::Gates;
	using C      = FS::Counter;
	auto&            cache = m_context.GetTextureCache();
	const RtsRecord* rec   = t_rts_take;
	t_rts_b                = true;
	const uint32_t cc      = state.color_count;
	const bool     hd      = static_cast<bool>(state.depth_info.image_id);
	std::array<Image*, RENDER_COLOR_ATTACHMENTS_MAX + 1> img {};
	const auto pb = [&]() -> C {
		// 1 (N1): the targets after the bindings are the record's (the bindings may re-find an alias target).
		if (cc != rec->color_count || hd != static_cast<bool>(rec->pre_depth.image_id)) {
			return C::RtsXbIds;
		}
		for (uint32_t i = 0; i < cc; i++) {
			const auto& c = state.color_info[i];
			const auto& p = rec->pre[i];
			if (c.image_id != p.image_id || c.target_slot != p.target_slot || !(c.desc.view_info == p.desc.view_info)) {
				return C::RtsXbIds;
			}
		}
		if (hd && (state.depth_info.image_id != rec->pre_depth.image_id ||
		           !(state.depth_info.desc.view_info == rec->pre_depth.desc.view_info))) {
			return C::RtsXbIds;
		}
		// 2 (N1, N2, [RC6]): the gate of the fast path, the same expression (AcquireTargetView), then its whole predicate
		// restated against the record and the live fast records (kSpRtLive of spcen), the re-find condition included.
		const bool gate = G::Enabled(G::Gate::RenderTargetFast) && !graphics_debug_dump_enabled() &&
		                  !cache.m_readback_linear_images;
		if (!gate) {
			return C::RtsXbLive;
		}
		for (uint32_t i = 0; i < rec->nt; i++) {
			const bool    d     = i == cc;
			const auto&   t     = rec->t[i];
			const ImageId id    = d ? state.depth_info.image_id : state.color_info[i].image_id;
			Image*        image = cache.m_slot_images.try_get(id);
			const auto&   fast  = d ? m_depth_view_fast : m_color_view_fast[t.slot];
			const auto&   desc  = d ? state.depth_info.desc : state.color_info[i].desc;
			const auto    stamp = image != nullptr ? image->bind_stamp.load(std::memory_order_acquire) : 0u;
			if (image == nullptr || !image->registered || image->depth_id || image->binding.needs_rebind ||
			    image->pending_levels != 0 || image->backing.image != t.backing || stamp != t.stamp ||
			    image->source_size != t.source_size || image->source_first_level != t.source_first_level ||
			    !fast.valid || fast.image_id != id || fast.backing != t.backing || fast.view != t.view ||
			    fast.stamp != t.stamp || fast.meta_epoch != rec->meta || fast.source_size != image->source_size ||
			    fast.source_first_level != image->source_first_level || !(fast.view_info == desc.view_info) ||
			    !SameTargetMetadata(fast.metadata, desc.info.metadata) ||
			    (d && (fast.htile_clear_mask != image->info.htile_clear_mask ||
			           image->info.htile_clear_mask != t.htile_mask ||
			           !SpStencilKept(cache, state.depth_info, fast, id)))) {
				return C::RtsXbLive;
			}
			img[i] = image;
		}
		// Items 3 and 4 are not applied at value 4 (track F, F30d, ROADMAP s122 item 643(v)(1)): the positive control of
		// place B - the full capture then runs against a record these two would have refused.
		if (t_rts != 4) {
			// 3 (N2, N4): the metadata epoch the record's fast records were taken at.
			if (cache.MetaEpoch() != rec->meta) {
				return C::RtsXbMeta;
			}
			// 4 (N3, [RC4]): no state record of a target was written since the record.
			for (uint32_t i = 0; i < rec->nt; i++) {
				if (img[i]->backing.state_serial != rec->t[i].state_serial) {
					return C::RtsXbSer;
				}
			}
		}
		// 5 (N3, N5, [RC5]): sampled by this draw as the record's colour targets were; the depth target not sampled and
		// not an image without data (then !is_bound means no feedback loop).
		for (uint32_t i = 0; i < cc; i++) {
			if (img[i]->binding.is_bound != rec->t[i].is_bound) {
				return C::RtsXbBound;
			}
		}
		if (hd && (img[cc]->binding.is_bound || img[cc]->info.data.Empty())) {
			return C::RtsXbBound;
		}
		// 6 (N10, N11 - a narrowing of the set, [RC4]): inside the pass the record is pinned to.  Not applied at value 5
		// (track F, F30k, ROADMAP s122 item 655(g)(1)): the full capture then runs against a record this item would refuse.
		if (t_rts != 5 && (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial)) {
			return C::RtsXbPass;
		}
		return C::Count;
	};
	bool pb_ok = false;
	if (t_rts_pa) {
		const C why = pb();
		pb_ok       = why == C::Count;
		if (!pb_ok) {
			FS::Add(why, 1);
		}
	}
	if (t_rts == 1 && pb_ok) {
		// The skip (s.3.2): the stores the fast path and the capture make on unchanged images, in the capture's order.
		t_rts_pb = true;
		FS::Add(C::RtsSkip, 1);
		for (uint32_t i = 0; i < rec->nt; i++) {
			const bool  d     = i == cc;
			const auto& t     = rec->t[i];
			auto&       image = *img[i];
			image.MarkGpuModified();
			if (d) {
				image.usage.depth_target = true;
			} else {
				image.usage.render_target = true;
			}
			image.binding.attachment_layout = t.att_layout;
			image.binding.attachment_access = t.att_access;
			if (!d) {
				FS::NoteMax(FS::Gauge::RtWidth, t.w);
				FS::NoteMax(FS::Gauge::RtHeight, t.h);
				FS::Add(C::RtAttachments, 1);
				FS::Add(C::RtPixelsK, t.kpx);
			}
		}
		if (hd) {
			state.depth_info.depth_load_clear_enable = false;
		}
		g_pass_extents = rec->extents;
		return rec->state;
	}
	if (t_rts >= 2 && pb_ok) {
		t_rts_pb = true;
		FS::Add(C::RtsPb, 1);
		FS::Add(C::RtsChkB, 1);
		// Track F, F30o (ROADMAP s122 item 664(e)(1)): value 6 - the (a2) perturbation, after PB, before the snapshots.
		if (t_rts == 6) [[unlikely]] {
			RtsInject(cc, state.color_info, img.data());
		}
	}
	// The full capture between the snapshots.
	t_rts_slow   = false;
	t_rts_race   = false;
	t_rts_refind = false;
	t_rts_meta0  = cache.MetaEpoch();
	t_rts_ser0   = ImageStateSerial();
	t_rts_open0  = buffer.IsRendering();
	auto rendering = AcquireRenderTargets(buffer, state.color_info, state.color_count, state.depth_info, pixel);
	t_rts_meta1    = cache.MetaEpoch();
	t_rts_ser1     = ImageStateSerial();
	t_rts_open1    = buffer.IsRendering();
	return rendering;
}

// Session 127, knob "rtskip": the post (s.4.3), right after place B.  The guard rts_acqw; at 2/3 the capture half of the
// self-check and the report; then the record by the rule of s.5.1, the same at 1, 2 and 3: PA and PB - re-pinned only;
// PA and not PB - its capture half from this draw; not PA - a full update from this draw; both by the strict rule.
void RenderExecutor::RtsPost(CommandBuffer& buffer, DrawRenderState& state, const RenderState& rendering) {
	namespace FS = Common::FrameStats;
	using C      = FS::Counter;
	(void)buffer;
	if (!t_rts_b) {
		return; // place B did not run through RtsPlaceB: the record stays taken (as any return before the post)
	}
	auto&          cache = m_context.GetTextureCache();
	RtsEntry*      e     = t_rts_entry;
	RtsRecord*     rec   = t_rts_take;
	const uint32_t cc    = state.color_count;
	const bool     hd    = static_cast<bool>(state.depth_info.image_id);
	t_rts_live           = false;
	t_rts_take           = nullptr;
	if (e != nullptr && e->gen != t_rts_gen_a) {
		FS::Add(C::RtsAcqw, 1); // N13: a register group written inside the draw
	}
	if (t_rts >= 2 && t_rts_pa) {
		uint32_t bits = t_rts_bits;
		uint32_t xsrc = 0; // track F, F30k: the sources of bit X (RtsReport)
		if (t_rts_pb) {
			if (!(rendering == rec->state)) {
				bits |= 0x010u; // R
			}
			for (uint32_t i = 0; i < rec->nt; i++) {
				const ImageId id    = i == cc ? state.depth_info.image_id : state.color_info[i].image_id;
				const Image*  image = cache.m_slot_images.try_get(id);
				if (image == nullptr || image->binding.attachment_layout != rec->t[i].att_layout ||
				    image->binding.attachment_access != rec->t[i].att_access) {
					bits |= 0x020u; // X
					xsrc |= 1u;
				}
			}
			if (hd && state.depth_info.depth_load_clear_enable) {
				bits |= 0x020u;
				xsrc |= 2u;
			}
			if (g_pass_extents.max_width != rec->extents.max_width ||
			    g_pass_extents.max_height != rec->extents.max_height ||
			    g_pass_extents.true_kpx != rec->extents.true_kpx) {
				bits |= 0x020u;
				xsrc |= 4u;
			}
			if (t_rts_ser1 != t_rts_ser0) {
				bits |= 0x040u; // S
			}
			if (t_rts_open0 && !t_rts_open1) {
				bits |= 0x080u; // P
			}
			if (t_rts_meta1 != t_rts_meta0) {
				bits |= 0x100u; // M
			}
			if (t_rts_slow || t_rts_refind) {
				bits |= 0x200u; // L
			}
		}
		// Track F, F30o (ROADMAP s122 item 664(e)(2)): the outcome of the perturbed draw - suppressed by the race filter
		// (the predicate of RtsReport, which runs iff bits != 0), else S, else neither.
		if (t_rts_inj) {
			t_rts_inj = false;
			if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {
				FS::Add(C::RtsInjRace, 1);
			} else if ((bits & 0x040u) != 0) {
				FS::Add(C::RtsInjS, 1);
			} else {
				FS::Add(C::RtsInjNos, 1);
			}
		}
		if (bits != 0) {
			RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);
		}
	}
	if (e == nullptr) {
		FS::Add(C::RtsOvf, 1); // the table is full: no record for this context
		return;
	}
	if (t_rts_pb) {
		// PA and PB (the skip at 1): the record is not refreshed, only re-pinned at BeginRendering ([RC1]).
		rec->age++;
		e->has_rec = true;
		t_rts_pin  = true;
		return;
	}
	// The strict record (s.4.4, items 79(b), 79(v)(2)).
	const bool             full      = !t_rts_pa;
	const RtsDraft&        d         = t_rts_table->draft;
	const RenderColorInfo* pre       = full ? d.pre.data() : rec->pre.data();
	const RenderDepthInfo& pre_depth = full ? d.pre_depth : rec->pre_depth;
	const uint32_t         pre_cc    = full ? d.color_count : rec->color_count;
	const uint32_t         nv        = full ? d.nv : rec->nv;
	const RtsVisit*        v         = full ? d.v.data() : rec->v.data();
	const uint32_t         dms       = full ? d.dmemo_slot : rec->dmemo_slot;
	const uint32_t         dmv       = full ? d.dmemo_version : rec->dmemo_version;
	std::array<Image*, RENDER_COLOR_ATTACHMENTS_MAX + 1> img {};
	bool ok = !t_rts_slow && !t_rts_refind && t_rts_meta1 == t_rts_meta0 && cc == pre_cc &&
	          hd == static_cast<bool>(pre_depth.image_id);
	if (ok && hd) {
		ok = !state.depth_info.depth_clear_enable && !state.depth_info.depth_load_clear_enable;
	}
	// pre == post in every field of bits 0x001 and 0x400 ([RC9], item 79(b)).
	for (uint32_t i = 0; i < cc && ok; i++) {
		ok = RtsDiffColor(state.color_info[i], pre[i]) == 0;
	}
	if (ok) {
		ok = RtsDiffDepth(state.depth_info, pre_depth) == 0;
	}
	for (uint32_t i = 0; i < cc + (hd ? 1u : 0u) && ok; i++) {
		const bool dd = i == cc;
		img[i]        = cache.m_slot_images.try_get(dd ? state.depth_info.image_id : state.color_info[i].image_id);
		ok            = img[i] != nullptr &&
		     (dd ? state.depth_info.memo_slot : state.color_info[i].memo_slot) != UINT32_MAX &&
		     (dd || state.color_info[i].target_slot < RENDER_COLOR_ATTACHMENTS_MAX);
	}
	if (ok && hd) {
		ok = !img[cc]->binding.is_bound && !img[cc]->info.data.Empty(); // N5, [RC5]
	}
	// Every visited colour slot went through its memo or the inactive-slot path; item 79(v)(2): pre equals the content of
	// the memo slot of the LAST visit that wrote each index (an earlier visit's output at that index is overwritten).
	auto& memo = Memo();
	for (uint32_t i = 0; i < nv && ok; i++) {
		if (v[i].memo_slot == UINT32_MAX) {
			ok = !v[i].image;
			continue;
		}
		const auto& m = memo.colors[v[i].memo_slot];
		ok            = m.valid && m.version == v[i].memo_version;
		bool last     = true;
		for (uint32_t j = i + 1; j < nv; j++) {
			if (v[j].idx == v[i].idx) {
				last = false;
			}
		}
		if (ok && last) {
			ok = RtsDiffColor(pre[v[i].idx], m.info) == 0;
		}
	}
	if (ok) {
		ok = dms != UINT32_MAX && memo.depths[dms].valid && memo.depths[dms].version == dmv &&
		     RtsDiffDepth(pre_depth, memo.depths[dms].info) == 0;
	}
	if (!ok) {
		FS::Add(C::RtsRecX, 1); // the context stays without a record
		return;
	}
	auto& r = e->rec;
	if (full) {
		r.gen         = t_rts_gen_a;
		r.slice       = d.slice;
		r.mask        = d.mask;
		r.rel         = RtsRelSkip(d.mask);
		r.bmin        = d.bmin;
		r.bmax        = d.bmax;
		r.n_idx       = d.n_idx;
		r.color_count = d.color_count;
		for (uint32_t i = 0; i < d.n_idx; i++) {
			r.pre[i] = d.pre[i];
		}
		r.pre_depth     = d.pre_depth;
		r.nv            = d.nv;
		r.v             = d.v;
		r.dmemo_slot    = d.dmemo_slot;
		r.dmemo_version = d.dmemo_version;
	}
	// The capture half (a full update, or PA and not PB).
	r.nt = cc + (hd ? 1u : 0u);
	for (uint32_t i = 0; i < r.nt; i++) {
		const bool   dd    = i == cc;
		const Image& image = *img[i];
		auto&        t     = r.t[i];
		t.id                 = dd ? state.depth_info.image_id : state.color_info[i].image_id;
		t.slot               = dd ? UINT32_MAX : state.color_info[i].target_slot;
		t.backing            = image.backing.image;
		t.view               = dd ? rendering.depth_stencil_attachment.image_view
		                          : rendering.color_attachments[state.color_info[i].target_slot].image_view;
		t.stamp              = image.bind_stamp.load(std::memory_order_acquire);
		t.source_first_level = image.source_first_level;
		t.source_size        = image.source_size;
		t.state_serial       = image.backing.state_serial;
		t.htile_mask         = dd ? image.info.htile_clear_mask : 0u;
		t.is_bound           = image.binding.is_bound;
		t.att_layout         = image.binding.attachment_layout;
		t.att_access         = image.binding.attachment_access;
		if (dd) {
			t.w   = 0;
			t.h   = 0;
			t.kpx = 0;
		} else {
			const auto extent = state.color_info[i].Extent();
			t.w               = extent.width;
			t.h               = extent.height;
			t.kpx             = static_cast<uint64_t>(extent.width) * extent.height / 1024U;
		}
	}
	r.state    = rendering;
	r.extents  = g_pass_extents;
	r.meta     = t_rts_meta1;
	r.age      = 0;
	r.pinned   = false; // valid for PA only once BeginRendering pins it
	e->has_rec = true;
	t_rts_pin  = true;
	if (t_rts >= 2) {
		FS::Add(C::RtsRec, 1);
	}
}

void RenderExecutor::ExecutePreparedDraw(uint64_t submit_id, CommandBuffer& buffer,
                                         const DrawCallInfo& draw, DrawRenderState& state,
                                         vk::PrimitiveTopology topology, const DrawEmitInfo& emit,
                                         const DrawIndexBufferSource& index_source,
                                         bool primitive_restart_enable) {
	// Diagnostic only: isolate a draw family in a full recorded gameplay run.
	static const uint64_t skip_ps = [] {
		const auto* value = std::getenv("KYTY_SKIP_DRAW_PS");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	static const int skip_after = [] {
		const auto* value = std::getenv("KYTY_SKIP_DRAW_AFTER_FRAME");
		return value != nullptr ? std::atoi(value) : 0;
	}();
	if (skip_ps != 0 && state.ps_active && state.ps_input_info.stage &&
	    state.ps_input_info.stage.program->shader_hash == skip_ps &&
	    m_context.GetGpu().GetFrameNum() >= skip_after) {
		static bool logged = false;
		if (!logged) {
			LOGF("SkipDrawDiagnostic: ps=%016" PRIx64 " after_frame=%d\n", skip_ps, skip_after);
			logged = true;
		}
		return;
	}
	auto& ucfg = buffer.GetUserConfig();
	const auto vertex_stages =
	    std::span {state.vertex_info.data(), state.programs.VertexStageCount()};
	const bool mesh_active = state.vertex_info[0].stage.program->stage == ShaderType::Mesh;
	uint32_t   mesh_groups = 0;
	// Gate "recpack", decided once for the whole draw (CommandBuffer::PacketsWanted). MeshRestart
	// and the legacy quad lists emit a variable number of draws and keep the direct path.
	const bool packet = buffer.PacketsWanted() && !(mesh_active && primitive_restart_enable) &&
	                    ucfg.GetPrimType() != Prospero::PrimitiveType::kQuadListLegacy;
	std::vector<MeshIndexRange> restart_ranges;
	if (mesh_active) {
		const auto& mesh = state.vertex_info[0].mesh;
		if (mesh.primitives_per_group == 0) {
			EXIT("unsupported mesh draw: primitive=%u indexed=%u restart=%u\n",
			     static_cast<uint32_t>(ucfg.GetPrimType()), draw.IsIndexed(), primitive_restart_enable);
		}
		const auto primitives = mesh.InputPrimitiveCount(draw.index_count);
		if (primitives == 0 || draw.instance_count == 0) {
			return;
		}
		if (primitive_restart_enable) {
			EXIT_NOT_IMPLEMENTED(!draw.IsIndexed() || emit.indirect_args_addr != 0);
			static std::atomic<uint32_t> logged {0};
			const bool log_restart = logged.fetch_add(1) < 16;
			if (log_restart) {
				LOGF("MeshRestartBegin: frame=%d primitive=%u indices=%u width=%u address=0x%016" PRIx64 "\n",
				     m_context.GetGpu().GetFrameNum(), mesh.input_primitive, draw.index_count,
				     index_source.guest_element_size, index_source.address);
			}
			// Read on the GPU command lane before preparing bindings: current GPU-written
			// indices must be downloaded, and that download can restart the command buffer.
			const auto bytes = static_cast<uint64_t>(draw.index_count) * index_source.guest_element_size;
			m_context.GetBufferCache().ReadMemory(index_source.address, bytes);
			std::vector<uint8_t> indices(bytes);
			EXIT_IF(!LibKernel::Memory::TryReadBacking(index_source.address, indices.data(), bytes));
			restart_ranges = SplitMeshRestartIndices(indices, index_source.guest_element_size);
			std::erase_if(restart_ranges, [&](const MeshIndexRange& range) {
				return mesh.InputPrimitiveCount(range.count) == 0;
			});
			if (restart_ranges.empty()) {
				return;
			}
			if (log_restart) {
				LOGF("MeshRestart: primitive=%u indices=%u width=%u ranges=%zu instances=%u\n",
				     mesh.input_primitive, draw.index_count, index_source.guest_element_size,
				     restart_ranges.size(), draw.instance_count);
			}
		}
		mesh_groups        = (primitives - 1u) / mesh.primitives_per_group + 1u;
		if (primitive_restart_enable) {
			mesh_groups = 0;
			for (const auto& range: restart_ranges) {
				mesh_groups = std::max(mesh_groups,
				    (mesh.InputPrimitiveCount(range.count) - 1u) / mesh.primitives_per_group + 1u);
			}
		}
		const auto& limits = m_context.GetGraphics().mesh_shader_properties;
		const auto instances = primitive_restart_enable ? 1u : draw.instance_count;
		if (mesh_groups > limits.maxMeshWorkGroupCount[0] ||
		    instances > limits.maxMeshWorkGroupCount[1] ||
		    static_cast<uint64_t>(mesh_groups) * instances >
		        limits.maxMeshWorkGroupTotalCount) {
			EXIT("mesh draw exceeds host workgroup limits: %ux%u\n", mesh_groups,
			     draw.instance_count);
		}
	}

	if (mesh_active && draw.IsIndexed()) {
		// Register the original guest indices for shader reads; PrepareGraphicsBindings
		// synchronizes registered BDA ranges before any draw commands are committed.
		(void)m_context.GetBufferCache().FindBuffer(
		    index_source.address, static_cast<uint64_t>(draw.index_count) *
		                              index_source.guest_element_size);
	}
	Common::FrameStats::Lap lap;
	// Session 82, gate "bindkey" (measurement only): time the whole binding phase and split it by
	// whether every stage's binding input repeated the previous draw's.
	const auto bind_key_t0 = Common::Gates::Enabled(Common::Gates::Gate::BindKeyStat) &&
	                                 Common::FrameStats::Enabled()
	                             ? Common::FrameStats::NowNs()
	                             : 0;
	LogDrawPhase(draw.Name(), "PrepareBindings");
	// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053), route E
	// measurement M3: the CEILING STUB.  THE PICTURE IS ALLOWED TO BREAK (ROADMAP.md:1048).
	// Session 97: this reads the LATCH taken at the top of DrawIndex / DrawAuto, the same value
	// ProgramCache::Get read for this draw.  Session 96 read the gate here and claimed that a
	// flip could not arm half a draw - true only inside this function: CommitBindings read the
	// gate again, and a falling edge between the two reads killed bf96b.
	// REMOVED from this function: PrepareBindings (the SRT resolve of every image, buffer and
	// sampler slot of every stage), PrepareGraphicsBindings (RebindImages, RebindBuffers, the
	// buffer uploads, PrepareBda, the per-slot synchronisations) and the pixel bindings
	// AcquireRenderTargets reads.  KEPT: the PM4 parse above, the render targets, the vertex
	// and index buffers, the pipeline lookup, CommitBindings' emit half and the whole record /
	// "recpack" tail.  bf_skip: a stage whose image numeric class NullTextureDesc cannot
	// express would abort the process, so that draw keeps the real path.
	bool bind_floor = BindFloorCurrentOp().armed;
	if (bind_floor) {
		for (uint32_t i = 0; i < vertex_stages.size() && bind_floor; i++) {
			bind_floor = BindFloorStageSupported(state.vertex_info[i].stage);
		}
		if (bind_floor && state.ps_active) {
			bind_floor = BindFloorStageSupported(state.ps_input_info.stage);
		}
		Common::FrameStats::Add(bind_floor ? Common::FrameStats::Counter::BindFloorDraws
		                                   : Common::FrameStats::Counter::BindFloorSkips,
		                        1);
		if (!bind_floor) {
			static std::atomic<uint32_t> floor_logged {0};
			if (floor_logged.fetch_add(1, std::memory_order_relaxed) < 64) {
				LOGF("BindFloor: skipped draw %s frame=%d vs=0x%016" PRIx64 " ps=0x%016" PRIx64
				     " reason=image-numeric-class\n",
				     draw.Name(), m_context.GetGpu().GetFrameNum(),
				     state.vertex_info[0].stage
				         ? state.vertex_info[0].stage.program->shader_hash
				         : uint64_t {0},
				     (state.ps_active && state.ps_input_info.stage)
				         ? state.ps_input_info.stage.program->shader_hash
				         : uint64_t {0});
			}
		}
	}
	// Session 98 (patch_s98d), KYTY_BIND_FLOOR_CLEAR=1 (MEASUREMENT ONLY): an ARMED draw the floor
	// cannot express (bf_skip) would run the REAL PrepareBindings over the frozen floor snapshot
	// and write through stale addresses on the GPU: drop it.
	if (!bind_floor && BindFloorClearSkip()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorSkipDrop, 1);
		return;
	}
	// Session 133, knob "rbcen" (design133.md rev 2 s.3.1): M1 - the draw chain opens on the borrowed start of mh_bind.
	Common::RbCen::ChainOpen();
	// Session 83, gate "bindpack" (PLAN_82_bind.md item 9): while ReuseBindingsEnabled() is on -
	// the default - `bindings` binds to m_graphics_bindings and this object is never read, but it
	// is still array<PreparedBindings,3> with five vectors each: fifteen empty-vector
	// constructors and destructors on the stack of every draw.
	const bool reuse_bindings = ReuseBindingsEnabled();
	std::optional<GraphicsBindings> local_bindings;
	if (!reuse_bindings || !Common::Gates::Enabled(Common::Gates::Gate::BindPack)) {
		local_bindings.emplace();
		// Session 84: item 9 shipped in session 83 with no arming counter, which the
		// pre-registration could not admit.  One Add in EACH arm - symmetric, so proving the
		// arming cannot bias the contrast in either direction.
		Common::FrameStats::Add(Common::FrameStats::Counter::BindPackLocalMake, 1);
	} else {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindPackLocalSkip, 1);
	}
	auto& bindings = reuse_bindings ? m_graphics_bindings : *local_bindings;
	// Upstream 6d1ba58 + 7516068: a draw runs one vertex stage (VS or mesh) or the three
	// tessellation stages LS/HS/TES; every one of them is prepared, then one shared resource
	// pass covers them all. Ours keeps preparing in place (gate "reusebindings"): the vectors
	// of the previous draw are reused instead of being freed and grown again.
	std::array<PreparedBindings*, 4> descriptor_stages {};
	uint32_t                         stage_count = 0;
	for (uint32_t i = 0; i < vertex_stages.size(); i++) {
		// Session 96, gate "bindfloor": the floor fills only `runtime` and a zero shader_data of
		// the declared length - every field CommitBindings' emit half reads.
		if (bind_floor) {
			BindFloorPrepareStage(state.vertex_info[i].stage, bindings.vertex[i]);
		} else {
			Common::RbCen::ChainMark(&Common::RbCen::Tls::stage); // Pa (knob "rbcen")
			PrepareBindings(state.vertex_info[i].stage, bindings.vertex[i]);
			Common::RbCen::ChainSkip(); // Pb
		}
		descriptor_stages[stage_count++] = &bindings.vertex[i];
	}
	// Gate "bindspare": depth-only draws reset the pixel stage, which freed every vector of it
	// (vector<TextureBinding>::_Tidy from ~PreparedBindings) and the next draw allocated them
	// again. Park the storage in a spare instead; PrepareBindings resets the contents anyway.
	thread_local PreparedBindings pixel_spare;
	const bool                    spare = Common::Gates::Enabled(Common::Gates::Gate::BindSpare);
	if (state.ps_active) {
		if (!bindings.pixel) {
			bindings.pixel.emplace();
			if (spare) {
				std::swap(*bindings.pixel, pixel_spare);
			}
		}
		// Session 96, gate "bindfloor": as for the vertex stages above.
		if (bind_floor) {
			BindFloorPrepareStage(state.ps_input_info.stage, *bindings.pixel);
		} else {
			Common::RbCen::ChainMark(&Common::RbCen::Tls::stage); // Pa (knob "rbcen")
			PrepareBindings(state.ps_input_info.stage, *bindings.pixel);
			Common::RbCen::ChainSkip(); // Pb
		}
		descriptor_stages[stage_count++] = &*bindings.pixel;
	} else {
		if (spare && bindings.pixel) {
			std::swap(*bindings.pixel, pixel_spare);
		}
		bindings.pixel.reset();
	}
	const auto stages = std::span {descriptor_stages.data(), stage_count};
	// Session 68, gate "pxstat": time the binding interval separately for depth-only draws (24 % of
	// them bind no pixel resources - do they still pay the full price?).
	const auto px_t0 = Common::Gates::Enabled(Common::Gates::Gate::PixelOffStat) &&
	                           Common::FrameStats::Enabled()
	                       ? Common::FrameStats::NowNs()
	                       : 0;
	// Upstream dd408ff passes the color targets in: their identities are resolved with the
	// image aliases, before the buffer uploads of RebindBuffers.
	// Session 96, gate "bindfloor": THIS CALL is the floor's main target - RebindImages,
	// RebindBuffers, the buffer uploads, PrepareBda and the per-slot synchronisations all live
	// inside it.  At bfmode=2/3 the calibrated idle is burned exactly where it stood, on this
	// thread and inside the render mutex (ROADMAP.md:1062-1065).
	Common::RbCen::ChainMark(&Common::RbCen::Tls::stage); // M2 (knob "rbcen", s.3.1)
	if (!bind_floor) {
		PrepareGraphicsBindings(stages, std::span {state.color_info, state.color_count});
	} else {
		BindFloorBurnSlice();
	}
	// Session 64 (shadowResolve.h), measurement only, both gates default 0.
	ShadowQueue(stages);
	if (px_t0 != 0) {
		const auto spent = Common::FrameStats::NowNs() - px_t0;
		Common::FrameStats::Add(state.ps_active ? Common::FrameStats::Counter::PxOnBindNs
		                                        : Common::FrameStats::Counter::PxOffBindNs,
		                        spent);
		Common::FrameStats::Add(state.ps_active ? Common::FrameStats::Counter::PxOnDraws
		                                        : Common::FrameStats::Counter::PxOffDraws,
		                        1);
	}
	if (bind_key_t0 != 0) {
		bool all_hit = stage_count > 0;
		for (uint32_t i = 0; i < stage_count; i++) {
			all_hit = all_hit && descriptor_stages[i]->key_hit;
		}
		const auto spent = Common::FrameStats::NowNs() - bind_key_t0;
		Common::FrameStats::Add(all_hit ? Common::FrameStats::Counter::BindKeyHitNs
		                                : Common::FrameStats::Counter::BindKeyMissNs,
		                        spent);
		Common::FrameStats::Add(all_hit ? Common::FrameStats::Counter::BindKeyDrawHit
		                                : Common::FrameStats::Counter::BindKeyDrawMiss,
		                        1);
	}
	lap.Mark(Common::FrameStats::Counter::DrawBindingsNs);
	// Session 69, gate "mutsite": everything above this line, back to the mh_prog_us mark, is the
	// bindings half of the draw (descriptors, texture cache, buffer cache, sampler cache, uploads).
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldBindingsNs);
	// Session 133, knob "rbcen" (design133.md rev 2 s.3.1): F - the chain closes on the stamp of the mark above (T8) and
	// is booked here, outside mh_bind.
	Common::RbCen::ChainFlush();
	Common::FrameStats::HoldLap::Count(Common::FrameStats::Counter::HoldDraws);
	// The rest of this function is mh_emit_us, closed by a destructor because the function has
	// three exits and the default one (gate "recpack", line ~2220) is in the middle of it.
	Common::FrameStats::HoldPhase emit_phase(Common::FrameStats::Counter::HoldEmitNs);
	// Session 96, gate "pathlap" (MEASUREMENT ONLY, pred/01_pathlap.md): the same chain as the
	// FrameStats::Lap above, re-taken with an idiom that reads in a KYTY_FRAME_TRACE=lite run.
	// Its own thread-local cursor, so it does not disturb the mh_* chain it sits inside.  Opened
	// where HoldPhase(HoldEmitNs) is opened, so sum(pl_em_*) == mh_emit_us on these draws.
	Common::FrameStats::PathLap path_emit(
	    Common::Gates::Enabled(Common::Gates::Gate::PathLap),
	    Common::FrameStats::Counter::PathEmRestNs);
	Common::FrameStats::PathLap::Count(Common::FrameStats::Counter::PathEmN);
	// Session 68, gate "amut": the rest of this function is the apply-and-record half of the draw -
	// vertex and index buffers, the pipeline lookup (which creates pipelines), CommitBindings,
	// BeginRendering, the dynamic state, EmitDrawPrimitives. None of it can leave the serial path.
	Common::FrameStats::MutScope mutate_scope(
	    Common::Gates::Enabled(Common::Gates::Gate::MutateTime));
	static const uint64_t watched_image = [] {
		const auto* value = std::getenv("KYTY_IMAGE_WATCH");
		return value == nullptr ? uint64_t {0} : std::strtoull(value, nullptr, 0);
	}();
	if (watched_image != 0) {
		for (uint32_t i = 0; i < state.color_count; ++i) {
			const auto& color = state.color_info[i];
			if (!color.image_id || color.desc.info.data.address != watched_image) continue;
			const auto& ctx = buffer.GetRegisters();
			const auto& rt = ctx.GetRenderTarget(color.target_slot);
			LOGF("ImageWatchDraw: frame=%u image=0x%016" PRIx64 " slot=%u vs=0x%016" PRIx64
			     " ps=0x%016" PRIx64 " indices=%u instances=%u mask=0x%x mode=%u"
			     " clear=%08x/%08x cmask=0x%016" PRIx64 " dcc=0x%016" PRIx64 "\n",
			     GpuTimeProfiler::Frame(), watched_image, color.target_slot,
			     DrawShaderHash(state.vertex_info[0].stage),
			     state.ps_active ? DrawShaderHash(state.ps_input_info.stage) : 0u,
			     draw.index_count, draw.instance_count, ctx.GetRenderTargetMask(),
			     ctx.GetColorControl().mode, rt.clear_word0.word0, rt.clear_word1.word1,
			     rt.cmask.addr, rt.dcc_addr.addr);
			static const bool dump_watched = Common::EnvFlagOn("KYTY_IMAGE_WATCH_BINDINGS");
			static uint32_t watched_dumps = 0;
			if (dump_watched && GpuTimeProfiler::Frame() >= 14000 && watched_dumps++ < 16) {
				DumpShaderStageBindings(m_context, "WatchVS", state.vertex_info[0].stage);
				if (state.ps_active) DumpShaderStageBindings(m_context, "WatchPS", state.ps_input_info.stage);
			}
		}
	}
	const bool frame_dump =
	    DebugDumpFrame(static_cast<uint32_t>(m_context.GetGpu().GetFrameNum()));
	const auto& dump_addrs = DebugDumpAddresses();
	if (const auto dump_addr = DebugDumpAddress();
	    dump_addr != 0 || frame_dump || !dump_addrs.empty()) {
		const auto& vs     = state.vertex_info[0].stage;
		const auto& ps     = state.ps_input_info.stage;
		const bool  vs_hit = ShaderStageTouchesAddress(vs, dump_addr) ||
		                    ShaderStageTouchesAnyBuffer(vs, dump_addrs);
		const bool ps_hit = state.ps_active && (ShaderStageTouchesAddress(ps, dump_addr) ||
		                                        ShaderStageTouchesAnyBuffer(ps, dump_addrs));
		bool        rt_hit = false;
		for (uint32_t i = 0; i < state.color_count; i++) {
			const auto& c = state.color_info[i];
			if (c.image_id && c.desc.info.data.address != 0 &&
			    dump_addr >= c.desc.info.data.address &&
			    dump_addr < c.desc.info.data.address + c.desc.info.data.size) {
				rt_hit = true;
			}
		}
		const bool  bda    = (vs && vs.program->info.uses_dma) ||
		                 (state.ps_active && ps && ps.program->info.uses_dma);
		static std::atomic<uint32_t> bda_log_count {0};
		if (vs_hit || ps_hit || rt_hit || frame_dump ||
		    (bda && dump_addr != 0 &&
		     bda_log_count.fetch_add(1, std::memory_order_relaxed) < 4096)) {
			LOGF("DumpDraw: %s submit=%" PRIu64 " frame=%d vs=0x%016" PRIx64 " ps=0x%016" PRIx64
			     " touches=%s%s%s%s bda=%d index_count=%u instances=%u\n",
			     draw.Name(), submit_id, m_context.GetGpu().GetFrameNum(),
			     vs ? vs.program->shader_hash : 0u,
			     (state.ps_active && ps) ? ps.program->shader_hash : 0u, vs_hit ? "VS " : "",
			     ps_hit ? "PS " : "", rt_hit ? "RT " : "", frame_dump ? "FRAME" : "", bda ? 1 : 0,
			     draw.index_count, draw.instance_count);
			if (vs_hit || ps_hit || rt_hit || frame_dump) {
				for (uint32_t i = 0; i < state.color_count; i++) {
					const auto& c = state.color_info[i];
					if (!c.image_id) {
						continue;
					}
					LOGF("  DumpRT[%u]: addr=0x%010" PRIx64 " size=0x%" PRIx64 " vk_format=%d"
					     " extent=%ux%u mip=%u export_mapping=0x%02x out_mode=%u\n",
					     i, c.desc.info.data.address, c.desc.info.data.size,
					     static_cast<int>(c.desc.view_info.format), c.Extent().width,
					     c.Extent().height, c.guest_mip_level, c.export_mapping.packed,
					     state.ps_active ? state.ps_input_info.target_output_mode[i] : 0u);
				}
				DumpShaderStageBindings(m_context, "VS", vs);
				if (state.ps_active) {
					DumpShaderStageBindings(m_context, "PS", ps);
				}
				// KYTY_DUMP_TEX=<hex addr>: when the PS reads that address, read every bound PS image
				// back at draw time (first three draws) into _texdraw_<n>_<i>.bin.
				static const uint64_t dump_tex = [] {
					const char* value = std::getenv("KYTY_DUMP_TEX");
					return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
				}();
				if (dump_tex != 0) {
					// Render target at dump_tex: read it back before this draw runs (content left by
					// the previous draws), _rtdraw_<n>.bin.
					for (uint32_t i = 0; i < state.color_count; i++) {
						const auto& c = state.color_info[i];
						if (c.image_id && c.desc.info.data.address == dump_tex) {
							static std::atomic<uint32_t> rt_dumped {0};
							const auto                   n = rt_dumped.fetch_add(1);
							if (n < 4) {
								LOGF("DumpTex: RT before draw %s ps=0x%016" PRIx64 "\n", draw.Name(),
								     (state.ps_active && ps) ? ps.program->shader_hash : 0u);
								m_context.GetTextureCache().DebugDumpImage(
								    c.image_id, "_rtdraw_" + std::to_string(n) + ".bin");
							}
						}
					}
				}
				if (dump_tex != 0 && state.ps_active && ps && bindings.pixel.has_value() &&
				    ShaderStageTouchesAddress(ps, dump_tex)) {
					static std::atomic<uint32_t> dumped {0};
					const auto                   n = dumped.fetch_add(1);
					if (n < 3) {
						auto& images = bindings.pixel->images;
						for (uint32_t i = 0; i < images.size(); i++) {
							m_context.GetTextureCache().DebugDumpImage(
							    images[i].image_id,
							    "_texdraw_" + std::to_string(n) + "_" + std::to_string(i) + ".bin");
						}
					}
				}
			}
		}
	}
	PreparedVertexBuffers vertex_bindings;
	PreparedIndexBuffer   index_binding;
	if (!mesh_active) {
		LogDrawPhase(draw.Name(), "PrepareVertexBuffers");
		vertex_bindings = AcquireVertexBuffers(buffer, state.vertex_info[0]);
		index_binding   = PrepareIndexBuffer(buffer, index_source);
	}
	// Session 123, knob "skipceil" = 2 (census, [N1], ROADMAP s122 item 34(v)): the binding, vertex and index reads of this
	// draw are done - its W2 stamps now (moved here from the tail of PrepareGraphicsBindings; the bindfloor path never ran
	// PrepareGraphicsBindings, so it queued none and applies none, as before).
	if (!bind_floor && Common::SkipCeil::t_mode >= 2) [[unlikely]] {
		SkcCensus::ApplyW2(m_context.GetTextureCache(), m_context.GetBufferCache());
	}
	lap.Mark(Common::FrameStats::Counter::DrawVertexNs);
	Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmVtxNs);
	DrawStatTail();
	// Session 120, gate "spcen" (MEASUREMENT ONLY, spcen.md s.3.7, design120.md section 4): latch the gate ONCE for
	// this draw - CommitBindings and the BeginRendering sites read the latch, never the gate (the s97 lesson) - and
	// evaluate WITHOUT ACTING whether a same-pass render-target memo could skip the AcquireRenderTargets below.  Gate
	// first: FrameStats::Enabled() is out of line and must not run at gate 0.
	SpDrawScope sp_scope(*this, !bind_floor &&
	                                Common::Gates::Enabled(Common::Gates::Gate::SamePassCensus) &&
	                                Common::FrameStats::Enabled());
	if (sp_scope.Armed()) {
		SpRtCheck(buffer, state.color_info, state.color_count, state.depth_info);
		Common::FrameStats::PathLap::MarkSplit(Common::FrameStats::Counter::PathEmSpChkNs,
		                                       Common::FrameStats::Counter::SpRtChkHitNs, m_sp->would_rt,
		                                       Common::FrameStats::Counter::SpRtChkHitNs, false);
	}
	// Session 96, gate "bindfloor": AcquireRenderTargets walks bindings.pixel->images to decide
	// the depth feedback loop, and on the floor that vector is EMPTY while image.views is not,
	// so the floor passes no pixel bindings at all (the std::nullopt default).  The ONLY thing
	// this changes is that decision; the targets themselves are acquired identically, which is
	// what "keep the render-target capture" means.  Two calls, not a ternary on the optional:
	// a ternary would copy the whole PreparedBindings in the non-floor arm.
	// Session 127, knob "rtskip" (place B): at 0, on the floor and under an armed spcen - the previous calls.
	const auto rendering =
	    t_rts != 0 && !bind_floor && !sp_scope.Armed()
	        ? RtsPlaceB(buffer, state, bindings.pixel)
	    : bind_floor ? AcquireRenderTargets(buffer, state.color_info, state.color_count,
	                                        state.depth_info)
	                 : AcquireRenderTargets(buffer, state.color_info, state.color_count,
	                                        state.depth_info, bindings.pixel);
	// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(a)): the W1 writes AcquireRenderTargets queued
	// go to the graph now, after every image read of this draw - on both paths, bindfloor included.
	if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
		SkcCensus::G3ApplyAttach();
	}
	lap.Mark(Common::FrameStats::Counter::DrawAcquireRtNs);
	if (sp_scope.Armed()) {
		// Session 120, gate "spcen": the same pl_em_rt span, also charged to the would-hit subsets; then the bad check,
		// the dry replay and the record in their own span.
		Common::FrameStats::PathLap::MarkSplit(Common::FrameStats::Counter::PathEmRtNs,
		                                       Common::FrameStats::Counter::PathEmRtHitNs, m_sp->would_rt,
		                                       Common::FrameStats::Counter::PathEmRtHitGNs, m_sp->would_rt_g);
		SpRtPost(buffer, state.color_info, state.color_count, state.depth_info, rendering);
		Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmSpPostNs);
	} else {
		// Session 126, knob "rk3cen" (MEASUREMENT ONLY, design126.md rev 2 s.4.2): C5 is the same mark, returning what it
		// charged; the census post C6 follows it directly - no emulation code between them (ROADMAP s122 item 67(b)) - and
		// charges its own span to pl_em_rk3_ns.
		const bool rk3_ran   = Common::Rk3::t_rk3 != 0 && Common::FrameStats::PathLap::Running();
		const auto rk3_spent = Common::FrameStats::PathLap::MarkSpent(Common::FrameStats::Counter::PathEmRtNs); // gate 0: as before
		if (Common::Rk3::t_rk3 != 0) [[unlikely]] {
			Rk3Post(buffer.GetRegisters(), state.color_info, state.color_count, state.depth_info, rk3_ran, rk3_spent);
			Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmRk3Ns);
		}
		if (t_rts != 0) [[unlikely]] {
			RtsPost(buffer, state, rendering); // Session 127, knob "rtskip": the record; the self-check at 2/3
		}
	}
	DrawEmitInfo emit_info = emit;
	if (emit_info.indirect_args_addr != 0 && !mesh_active) {
		// The arguments were produced by the GPU (culling); reading them on the CPU would drain the
		// queue. Bind the cached buffer through the sanitizer: counts clamped to the index buffer
		// size / an instance limit so garbage cannot hang the device.
		const uint32_t dwords =
		    draw.IsIndexed() ? sizeof(vk::DrawIndexedIndirectCommand) / sizeof(uint32_t)
		                     : sizeof(vk::DrawIndirectCommand) / sizeof(uint32_t);
		auto [args_buffer, args_offset] = m_context.GetBufferCache().ObtainBuffer(
		    emit_info.indirect_args_addr, uint64_t {dwords} * sizeof(uint32_t), false);
		EXIT_IF(args_buffer == nullptr);
		// Session 123, knob "skipceil" = 2 (census, [N2]): the arguments are a read of this draw.
		if (Common::SkipCeil::t_mode >= 2) [[unlikely]] {
			SkcCensus::ReadIndirectArgs(m_context.GetBufferCache(), emit_info.indirect_args_addr,
			                            uint64_t {dwords} * sizeof(uint32_t));
		}
		if (m_indirect_sanitizer == nullptr) {
			m_indirect_sanitizer = std::make_unique<IndirectArgsSanitizer>(
			    m_context.GetGraphics(), buffer.Scheduler());
		}
		constexpr uint32_t MaxInstances = 1u << 20u;
		const std::array<uint32_t, 5> limits =
		    draw.IsIndexed() ? std::array<uint32_t, 5> {draw.index_count, MaxInstances,
		                                               UINT32_MAX, UINT32_MAX, UINT32_MAX}
		                     : std::array<uint32_t, 5> {UINT32_MAX, MaxInstances,
		                                               UINT32_MAX, UINT32_MAX, 0};
		buffer.Scheduler().EndRendering(RenderPassEnd::Sanitize);
		std::tie(emit_info.indirect_buffer, emit_info.indirect_offset) =
		    m_indirect_sanitizer->Sanitize(*args_buffer, args_offset, dwords,
		                                   limits, true);
		buffer.Scheduler().GpuMark(GpuTimeProfiler::Kind::Other, 1);
	}

	if (draw.IsIndexed()) {
		LogDrawPhase(draw.Name(), "CreatePipeline");
	}
	// Once a draw of this frame was skipped the flip is held anyway (KYTY_ASYNC_HOLD_FRAME), so
	// waiting for further pipelines of the same frame only lengthens it: a scene cut queues 20-30
	// new pipelines and every posting draw waited its 4 ms (~50 ms per cut).
	// KYTY_ASYNC_PIPELINE_WAIT_HELD=1 restores the wait.
	static const bool wait_when_held = [] {
		const char* value = std::getenv("KYTY_ASYNC_PIPELINE_WAIT_HELD");
		const char* hold  = std::getenv("KYTY_ASYNC_HOLD_FRAME");
		return (value != nullptr && value[0] == '1') || (hold != nullptr && hold[0] == '0');
	}();
	const bool allow_pipeline_wait =
	    wait_when_held || m_skipped_draws.load(std::memory_order_relaxed) == 0;
	auto* pipeline_ptr = m_context.GetPipelineCache().GetGraphicsPipeline(
	    std::span {state.color_info, state.color_count}, state.depth_info, vertex_stages, buffer,
	    state.ps_active ? &state.ps_input_info : nullptr, topology, primitive_restart_enable,
	    state.programs, allow_pipeline_wait);
	lap.Mark(Common::FrameStats::Counter::DrawPipelineNs);
	Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmPipeNs);
	if (pipeline_ptr == nullptr) {
		// The pipeline is being compiled by a worker thread (KYTY_ASYNC_PIPELINES): skip the draw
		// instead of freezing the frame; the caller resets the bindings.
		static std::atomic<uint32_t> skipped {0};
		const auto                   n = skipped.fetch_add(1, std::memory_order_relaxed);
		m_skipped_draws.fetch_add(1, std::memory_order_relaxed);
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcApSkip, 1); // Session 123, S_live ([RC15/M2])
		if (n < 200000u) {
			const auto& vs = state.vertex_info[0].stage;
			const auto& ps = state.ps_input_info.stage;
			LOGF("AsyncPipelines: skipped draw %s frame=%d vs=0x%016" PRIx64 " ps=0x%016" PRIx64
			     " pending=%u total_skipped=%u\n",
			     draw.Name(), m_context.GetGpu().GetFrameNum(), vs ? vs.program->shader_hash : 0u,
			     (state.ps_active && ps) ? ps.program->shader_hash : 0u,
			     m_context.GetPipelineCache().PendingPipelineCount(), n + 1u);
		}
		return;
	}
	auto& pipeline = *pipeline_ptr;
	// Session 71, gate G-area: which pass shape this draw goes into. One Add, no loop, no
	// decision; Add self-guards on the count limit, which is zero unless FrameStats is enabled.
	// Keyed by the attachment SLOT count - the same key GpuMark(RenderPass, 1,
	// num_color_attachments) uses in context.cpp, so a KYTY_GPU_TIME run and FrameTrace-x line
	// up. Placed after the async-pipeline skip return and before the recpack / direct split, so
	// one site covers both paths and no skipped draw is counted. sum(rpd_aN) must equal draws,
	// and sum(N * rpd_aN) must equal rt_att whenever rpa_slot == rpa_att.
	Common::FrameStats::Add(
	    static_cast<Common::FrameStats::Counter>(
	        static_cast<uint32_t>(Common::FrameStats::Counter::PassDraw0) +
	        RenderPassShapeBucket(rendering.num_color_attachments)),
	    1);

	// Session 86, gate "drawmerge" (MEASUREMENT ONLY, ROADMAP.md route D4): placed exactly
	// where the session-71 pass-shape Add is placed and for the same reason - past the
	// async-pipeline skip return and before the recpack / direct split, so one site covers
	// both paths and no skipped draw is counted.  Dispatches never reach this function.
	// Session 94, gate "mergecost" (MEASUREMENT ONLY, pred/01_mergecost.md): the class point.
	// The draw is armed iff the gate was on at its entry; the stamp before NoteDrawMerge closes
	// the PRE-CLASS interval, the stamp after it opens the POST-CLASS one, so the drawmerge
	// census's own time (mc_dm_ns) lies in neither.  The scope below books both by what the
	// census and CommitBindings decided (dm_buf1_ok, P) when the function exits.
	const bool     merge_armed = m_merge_cost.draw_t0 != 0;
	const uint64_t merge_t0    = merge_armed ? Common::FrameStats::NowNs() : 0;
	m_merge_cost.armed  = merge_armed;
	m_merge_cost.ok     = false;
	m_merge_cost.p      = false;
	m_merge_cost.sig_ns = 0;
	if (!merge_armed) {
		// An unarmed block must not leave a stale previous signature for the next armed one.
		m_merge_cost.prev_valid = false;
	}
	if (Common::Gates::Enabled(Common::Gates::Gate::DrawMerge)) {
		m_merge_cost.ok = NoteDrawMerge(static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
		                  static_cast<VkPipeline>(pipeline.pipeline))),
		              stages,
		              static_cast<uint64_t>(reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(
		                  m_context.GetBufferCache()
		                      .GetUtilityBuffer(MemoryUsage::Stream)
		                      .Handle()))),
		              mesh_active,
		              Common::Gates::Enabled(Common::Gates::Gate::DrawMergeVerify));
	}
	struct MergeCostScope {
		MergeCostState& mc;
		FrameRepState&  fr;
		uint64_t        pre_ns;
		uint64_t        t0;
		~MergeCostScope() {
			namespace FS = Common::FrameStats;
			if (t0 != 0) {
				const auto raw  = FS::NowNs() - t0;
				// Session 95: the framerep walk and the payload hashing are subtracted the same
				// way the mergecost census is, so mc_pre_ns / mc_post_ns keep meaning what they
				// meant in session 94 and the two arms are comparable.  Both are 0 when off.
				const auto sub  = mc.sig_ns + fr.post_ns;
				const auto post = raw > sub ? raw - sub : 0;
				const auto pre  = pre_ns > fr.pre_ns ? pre_ns - fr.pre_ns : 0;
				FS::Add(FS::Counter::MergeCostDraws, 1);
				FS::Add(FS::Counter::MergeCostPreNs, pre);
				FS::Add(FS::Counter::MergeCostPostNs, post);
				FS::Add(FS::Counter::FrameRepPreNs, fr.pre_ns);
				if (fr.armed) {
					const auto own = pre + post;
					FS::Add(FS::Counter::FrameRepAllNs, own);
					FS::Add(FS::Counter::FrameRepIdNs, fr.hit_id ? own : 0u);
					FS::Add(FS::Counter::FrameRepIdRNs, fr.hit_idr ? own : 0u);
					FS::Add(FS::Counter::FrameRepIdMNs, fr.hit_idm ? own : 0u);
					FS::Add(FS::Counter::FrameRepPayNs, fr.hit_pay ? own : 0u);
					FS::Add(FS::Counter::FrameRepFullNs, fr.hit_full ? own : 0u);
				}
				if (mc.p) {
					FS::Add(FS::Counter::MergeCostPrePNs, pre);
					FS::Add(FS::Counter::MergeCostPostPNs, post);
				}
				if (mc.ok) {
					FS::Add(FS::Counter::MergeCostOkDraws, 1);
					FS::Add(FS::Counter::MergeCostPreOkNs, pre);
					FS::Add(FS::Counter::MergeCostPostOkNs, post);
					FS::Add(FS::Counter::MergeCostSameOk, mc.p ? 1u : 0u);
					FS::Add(FS::Counter::MergeCostPostPOkNs, mc.p ? post : 0u);
				}
			}
			mc.armed   = false;
			mc.draw_t0 = 0;
			fr.pre_ns  = 0;
			fr.post_ns = 0;
			fr.armed   = false;
			fr.hit_idr = false;
			fr.hit_idm = false;
		}
	};
	uint64_t merge_t1 = 0;
	if (merge_armed) {
		merge_t1 = Common::FrameStats::NowNs();
		Common::FrameStats::Add(Common::FrameStats::Counter::MergeCostCensusNs,
		                        merge_t1 - merge_t0);
	}
	MergeCostScope merge_scope {m_merge_cost, m_frame_rep,
	                            merge_armed ? merge_t0 - m_merge_cost.draw_t0 : 0,
	                            merge_t1};
	// Session 95, gate "framerep": the draw's own arguments and its index / vertex buffer
	// identities, hashed here because this is the one place that has all of them, and
	// BEFORE CommitBindings so the census can fold them into H_full.  Cheap and
	// unconditional in shape; the hash itself is skipped when the gate is off.
	if (Common::Gates::Enabled(Common::Gates::Gate::FrameRep) &&
	    Common::FrameStats::Enabled()) {
		const auto fr_a0 = Common::FrameStats::NowNs();
		uint64_t   a     = 0x27d4eb2f165667c5ull;
		a = FrameRepMixDraw(a, static_cast<uint64_t>(draw.debug_op));
		a = FrameRepMixDraw(a, draw.index_count);
		a = FrameRepMixDraw(a, draw.instance_count);
		a = FrameRepMixDraw(a, draw.first_instance);
		a = FrameRepMixDraw(a, static_cast<uint64_t>(static_cast<uint32_t>(emit.vertex_offset)));
		a = FrameRepMixDraw(a, emit.first_vertex);
		a = FrameRepMixDraw(a, emit.first_instance);
		a = FrameRepMixDraw(a, emit.indirect_args_addr);
		a = FrameRepMixDraw(a, emit.indirect_offset);
		a = FrameRepMixDraw(a, index_source.address);
		a = FrameRepMixDraw(a, index_source.size);
		a = FrameRepMixDraw(a, static_cast<uint64_t>(index_source.type));
		a = FrameRepMixDraw(a, index_source.guest_element_size);
		a = FrameRepMixDraw(a, static_cast<uint64_t>(topology));
		a = FrameRepMixDraw(a, primitive_restart_enable ? 1u : 0u);
		a = FrameRepMixDraw(a, vertex_bindings.count);
		for (uint32_t v = 0; v < vertex_bindings.count; v++) {
			a = FrameRepMixDraw(a, static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
			                           static_cast<VkBuffer>(vertex_bindings.buffers[v]))));
			a = FrameRepMixDraw(a, static_cast<uint64_t>(vertex_bindings.offsets[v]));
			a = FrameRepMixDraw(a, static_cast<uint64_t>(vertex_bindings.sizes[v]));
		}
		m_frame_rep.args = a;
		m_frame_rep.pre_ns += Common::FrameStats::NowNs() - fr_a0;
	} else {
		m_frame_rep.args = 0;
	}

	// Gate "recpack" (commandRecorder.h): nothing below records on this thread. Every decision -
	// pass state, the dynamic-state cache, the shader-write debt, the descriptor set - is taken
	// here exactly as on the direct path, and the record thread receives the resulting calls.
	// Buffer order: the direct barriers of CommitBindings (fresh handles), its bindings record, the
	// pass records, then the tail of this draw. The vertex and index binds follow the bindings
	// instead of preceding them: they are state setters, independent of descriptors, barriers and
	// pass boundaries, and the mesh push constants still land over the 128 bytes of the bindings.
	// A submit during preparation may have given this draw a buffer without a record thread; that
	// draw takes the direct path.
	if (packet && buffer.Recorder() != nullptr) {
		SetDrawDebugPhase(buffer, submit_id, draw, state, draw.IsIndexed() ? 0x100u : 0x200u);
		CommitBindings(buffer, vk::PipelineBindPoint::eGraphics, pipeline, stages, true);
		lap.Mark(Common::FrameStats::Counter::DrawCommitNs);
		Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmComNs);

		LogDrawPhase(draw.Name(), "BeginRendering");
		if (!draw.IsIndexed()) {
			SetDrawDebugPhase(buffer, submit_id, draw, state, 0x400u);
		}
		// Session 120, gate "spcen": P2 and the pin of the pending memo (SpRtAfterBegin).
		const bool     sp_open = sp_scope.Armed() && buffer.IsRendering();
		const uint64_t sp_pass = sp_scope.Armed() ? CommandBuffer::PassBeginSerial() : 0;
		buffer.BeginRenderingPacket(rendering);
		if (sp_scope.Armed()) {
			SpRtAfterBegin(sp_open, sp_pass);
		}
		if (t_rts != 0) [[unlikely]] {
			RtsAfterBegin(); // Session 127, knob "rtskip": pin the record to the pass this draw renders in
		}
		DrawStatEmit();
		RecordCommandWriter tail(*buffer.Recorder());
		buffer.NoteHandleUse();
		if (!mesh_active) {
			CommitVertexBuffers(tail, vertex_bindings);
			CommitIndexBuffer(tail, index_binding);
		}
		SetGraphicsDynamicParams(buffer, tail, vertex_stages.back(), state.color_info,
		                         state.color_count, state.depth_info);
		// Same sink and the same place in the draw tail as on the direct path below.
		if (StencilDynamicParamsChanged(buffer, state.depth_info)) {
			SetStencilDynamicParams(tail, state.depth_info);
		}
		if (m_context.GetGraphics().attachment_feedback_loop_enabled) {
			const auto feedback =
			    rendering.depth_stencil_attachment.image_layout ==
			            vk::ImageLayout::eAttachmentFeedbackLoopOptimalEXT
			        ? vk::ImageAspectFlags {vk::ImageAspectFlagBits::eDepth}
			        : vk::ImageAspectFlags {};
			if (buffer.GraphicsStateChanged(GraphicsStateSlot::FeedbackLoop, feedback)) {
				tail.setAttachmentFeedbackLoopEnableEXT(feedback);
			}
		}
		if (buffer.GraphicsStateChanged(GraphicsStateSlot::Pipeline, pipeline.pipeline)) {
			tail.bindPipeline(vk::PipelineBindPoint::eGraphics, pipeline.pipeline);
		}
		if (rendering.num_color_attachments == 0) {
			// This pipeline does not declare dynamic color-write enables.
			buffer.InvalidateGraphicsState(GraphicsStateSlot::ColorWrite);
		}
		if (!draw.IsIndexed()) {
			SetDrawDebugPhase(buffer, submit_id, draw, state, 0x500u);
		}
		// Session 98 (patch_s98b): GPU marker TOP (no-op unless KYTY_GPU_MARKERS).
		GpuMarkerSite gpu_marker;
		if (GpuOpsActive()) {
			gpu_marker = BeginDrawMarker(buffer.Scheduler(), submit_id, draw, state,
			                             emit_info.indirect_buffer != nullptr, mesh_active,
			                             mesh_groups);
		}
		GpuMarkerTop(tail, gpu_marker);
		if (DiagF6::On()) [[unlikely]] {
			DiagF6NoteDraw(buffer, state, mesh_active, emit_info.indirect_buffer != nullptr, draw.IsIndexed()); // F16d
		}
		if (mesh_active) {
			const uint32_t draw_data[] {
			    draw.index_count,
			    draw.IsIndexed() ? static_cast<uint32_t>(emit.vertex_offset) : emit.first_vertex,
			    emit.first_instance, index_source.guest_element_size,
			    static_cast<uint32_t>(index_source.address),
			    static_cast<uint32_t>(index_source.address >> 32u)};
			static_assert(std::size(draw_data) == ShaderRecompiler::IR::PushData::MeshDrawDwordCount);
			tail.pushConstants(pipeline.pipeline_layout,
			                   vk::ShaderStageFlagBits::eMeshEXT | vk::ShaderStageFlagBits::eFragment,
			                   0, sizeof(draw_data), draw_data);
			tail.drawMeshTasksEXT(mesh_groups, draw.instance_count, 1);
		} else {
			EmitDrawPrimitives(ucfg, tail, state.vertex_info[0], draw, emit_info);
		}
		GpuMarkerBottom(tail, gpu_marker); // Session 98 (patch_s98b)
		if (!draw.IsIndexed()) {
			SetDrawDebugPhase(buffer, submit_id, draw, state, 0x600u);
		}
		vk::PipelineStageFlags packet_write_stages = {};
		bool                   packet_atomic_only  = true;
		for (const auto& stage: vertex_stages) {
			if (HasShaderBufferWrites(stage.stage, packet_atomic_only)) {
				packet_write_stages |= ShaderPipelineStages(NativeShaderStage(stage.logical_stage));
			}
		}
		if (state.ps_active && HasShaderBufferWrites(state.ps_input_info.stage, packet_atomic_only)) {
			packet_write_stages |= vk::PipelineStageFlagBits::eFragmentShader;
		}
		bool wide_barrier = false;
		if (packet_write_stages) {
			Common::FrameStats::Add(packet_atomic_only
			                            ? Common::FrameStats::Counter::ShaderWriteBarriersDeferrable
			                            : Common::FrameStats::Counter::ShaderWriteBarriersPlain,
			                        1);
			if (packet_atomic_only && buffer.IsRendering() &&
			    Common::Gates::Enabled(Common::Gates::Gate::ShaderWriteDefer)) {
				buffer.NotePendingShaderWrite(packet_write_stages);
				Common::FrameStats::Add(Common::FrameStats::Counter::ShaderWriteBarriersDeferred, 1);
			} else {
				// Session 71: the predicate of gate "swlocal", evaluated and counted whether or not
				// the gate is on. The gate still chooses the branch below, so no decision changes -
				// this only sizes the population (swbar_loc is 0 in every s69/s70 log).
				const auto packet_blocked = packet_write_stages & ~FramebufferSpaceStages();
				const bool packet_local_ok =
				    m_context.GetGraphics().dynamic_rendering_local_read_enabled &&
				    buffer.IsRendering() && !packet_blocked;
				Common::FrameStats::Add(
				    packet_local_ok ? Common::FrameStats::Counter::ShaderWriteLocalEligible
				    : (packet_blocked & vk::PipelineStageFlagBits::eMeshShaderEXT)
				        ? Common::FrameStats::Counter::ShaderWriteLocalMeshBlocked
				    : packet_blocked ? Common::FrameStats::Counter::ShaderWriteLocalStageBlocked
				                     : Common::FrameStats::Counter::ShaderWriteLocalClosed,
				    1);
				if (packet_local_ok &&
				    Common::Gates::Enabled(Common::Gates::Gate::ShaderWriteLocal)) {
					tail.shaderWriteBarrierLocal(packet_write_stages);
					buffer.NotePendingShaderWrite(packet_write_stages);
				} else {
					wide_barrier = true;
				}
			}
		}
		tail.Commit(false);
		if (wide_barrier) {
			buffer.EndRenderingPacket(RenderPassEnd::ShaderWrite);
			buffer.ShaderWriteBarrierPacket(packet_write_stages);
		}
		LogDrawPhase(draw.Name(), "DrawComplete");
		if (!draw.IsIndexed()) {
			SetDrawDebugPhase(buffer, submit_id, draw, state, 0x700u);
		}
		lap.Mark(Common::FrameStats::Counter::DrawEmitNs);
		Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmRecNs);
		return;
	}

	// Resource preparation above may synchronously finish and restart the scheduler. From this
	// point onward, every operation targets the current command buffer and cannot touch guest
	// memory.
	auto       vk_buffer    = buffer.Handle();
	const auto publish_mark = buffer.PublishMark();
	RecordDrawStartBreadcrumb(buffer, submit_id, draw, state);
	SetDrawDebugPhase(buffer, submit_id, draw, state, draw.IsIndexed() ? 0x100u : 0x200u);
	if (!mesh_active) {
		CommitVertexBuffers(vk_buffer, vertex_bindings);
	}
	if (bindings.pixel.has_value()) {
		if (!draw.IsIndexed()) {
			SetDrawDebugPhase(buffer, submit_id, draw, state, 0x300u);
		}
	}
	CommitBindings(buffer, vk::PipelineBindPoint::eGraphics, pipeline, stages);
	lap.Mark(Common::FrameStats::Counter::DrawCommitNs);
	Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmComNs);
	buffer.CheckNoPublish(publish_mark);
	if (!mesh_active) {
		CommitIndexBuffer(vk_buffer, index_binding);
	}

	SetGraphicsDynamicParams(buffer, vk_buffer, vertex_stages.back(), state.color_info,
	                         state.color_count, state.depth_info);
	if (StencilDynamicParamsChanged(buffer, state.depth_info)) {
		SetStencilDynamicParams(vk_buffer, state.depth_info);
	}
	if (m_context.GetGraphics().attachment_feedback_loop_enabled) {
		const auto feedback =
		    rendering.depth_stencil_attachment.image_layout ==
		            vk::ImageLayout::eAttachmentFeedbackLoopOptimalEXT
		        ? vk::ImageAspectFlags {vk::ImageAspectFlagBits::eDepth}
		        : vk::ImageAspectFlags {};
		if (buffer.GraphicsStateChanged(GraphicsStateSlot::FeedbackLoop, feedback)) {
			vk_buffer.setAttachmentFeedbackLoopEnableEXT(feedback);
		}
	}

	LogDrawPhase(draw.Name(), "BeginRendering");
	if (!draw.IsIndexed()) {
		SetDrawDebugPhase(buffer, submit_id, draw, state, 0x400u);
	}
	// Session 120, gate "spcen": P2 and the pin of the pending memo (SpRtAfterBegin).
	const bool     sp_open = sp_scope.Armed() && buffer.IsRendering();
	const uint64_t sp_pass = sp_scope.Armed() ? CommandBuffer::PassBeginSerial() : 0;
	buffer.Scheduler().BeginRendering(rendering);
	if (sp_scope.Armed()) {
		SpRtAfterBegin(sp_open, sp_pass);
	}
	if (t_rts != 0) [[unlikely]] {
		RtsAfterBegin(); // Session 127, knob "rtskip": pin the record to the pass this draw renders in
	}
	DrawStatEmit();
	buffer.CheckNoPublish(publish_mark);
	if (buffer.GraphicsStateChanged(GraphicsStateSlot::Pipeline, pipeline.pipeline)) {
		vk_buffer.bindPipeline(vk::PipelineBindPoint::eGraphics, pipeline.pipeline);
	}
	if (rendering.num_color_attachments == 0) {
		// This pipeline does not declare dynamic color-write enables.
		buffer.InvalidateGraphicsState(GraphicsStateSlot::ColorWrite);
	}
	if (!draw.IsIndexed()) {
		SetDrawDebugPhase(buffer, submit_id, draw, state, 0x500u);
	}
	// Session 98 (patch_s98b): GPU marker TOP (no-op unless KYTY_GPU_MARKERS).
	GpuMarkerSite gpu_marker;
	if (GpuOpsActive()) {
		gpu_marker = BeginDrawMarker(buffer.Scheduler(), submit_id, draw, state,
		                             emit_info.indirect_buffer != nullptr, mesh_active, mesh_groups);
	}
	GpuMarkerTop(vk_buffer, gpu_marker);
	if (DiagF6::On()) [[unlikely]] {
		DiagF6NoteDraw(buffer, state, mesh_active, emit_info.indirect_buffer != nullptr, draw.IsIndexed()); // F16d
	}
	if (mesh_active) {
		const auto emit_mesh = [&](uint32_t first, uint32_t count, uint32_t instance,
		                           uint32_t groups, uint32_t instances) {
			const auto address = index_source.address + static_cast<uint64_t>(first) *
			                                              index_source.guest_element_size;
			const uint32_t draw_data[] {
			    count, draw.IsIndexed() ? static_cast<uint32_t>(emit.vertex_offset) : emit.first_vertex,
			    instance, index_source.guest_element_size,
			    static_cast<uint32_t>(address), static_cast<uint32_t>(address >> 32u)};
			static_assert(std::size(draw_data) == ShaderRecompiler::IR::PushData::MeshDrawDwordCount);
			vk_buffer.pushConstants(pipeline.pipeline_layout,
			                        vk::ShaderStageFlagBits::eMeshEXT | vk::ShaderStageFlagBits::eFragment,
			                        0, sizeof(draw_data), draw_data);
			vk_buffer.drawMeshTasksEXT(groups, instances, 1);
		};
		if (primitive_restart_enable) {
			// Preserve instance/rasterization order; each range starts a new fan center
			// (or strip winding) but keeps the original base vertex and instance ID.
			const auto& mesh = state.vertex_info[0].mesh;
			for (uint32_t instance = 0; instance < draw.instance_count; ++instance) {
				for (const auto& range: restart_ranges) {
					const auto groups = (mesh.InputPrimitiveCount(range.count) - 1u) /
					                        mesh.primitives_per_group + 1u;
					emit_mesh(range.first, range.count, emit.first_instance + instance, groups, 1);
				}
			}
		} else {
			emit_mesh(0, draw.index_count, emit.first_instance, mesh_groups, draw.instance_count);
		}
	} else {
		EmitDrawPrimitives(ucfg, vk_buffer, state.vertex_info[0], draw, emit_info);
	}
	GpuMarkerBottom(vk_buffer, gpu_marker); // Session 98 (patch_s98b)
	if (GpuTimeProfiler::Enabled()) {
		const auto& vs = state.vertex_info[0].stage;
		const auto& ps = state.ps_input_info.stage;
		buffer.Scheduler().GpuMark(
		    GpuTimeProfiler::Kind::Draw, (state.ps_active && ps) ? ps.program->shader_hash : 0u,
		    vs ? vs.program->shader_hash : 0u);
	}

	if (!draw.IsIndexed()) {
		SetDrawDebugPhase(buffer, submit_id, draw, state, 0x600u);
	}
	vk::PipelineStageFlags shader_write_stages = {};
	bool                   atomic_only         = true;
	// Upstream 7516068: every vertex-side stage the draw ran can write buffers, and the stage
	// flag follows its logical stage (LS/HS/TES/mesh/vertex). Ours keeps the "atomic only"
	// witness of gate "swdefer".
	for (const auto& stage: vertex_stages) {
		if (HasShaderBufferWrites(stage.stage, atomic_only)) {
			shader_write_stages |= ShaderPipelineStages(NativeShaderStage(stage.logical_stage));
		}
	}
	if (state.ps_active && HasShaderBufferWrites(state.ps_input_info.stage, atomic_only)) {
		shader_write_stages |= vk::PipelineStageFlagBits::eFragmentShader;
	}
	if (shader_write_stages) {
		// The ceiling of gate "swdefer", counted whether or not it is on: BufferResource::atomic
		// means "an atomic was seen", so a draw only counts when every buffer it writes has it.
		Common::FrameStats::Add(atomic_only
		                            ? Common::FrameStats::Counter::ShaderWriteBarriersDeferrable
		                            : Common::FrameStats::Counter::ShaderWriteBarriersPlain,
		                        1);
		// Gate "swdefer": while the pass is open and every written buffer of this draw is only
		// ever written atomically, the barrier is owed rather than issued, and the pass survives.
		// Device-scope atomics order themselves; EndRendering pays the wide barrier.
		if (atomic_only && buffer.IsRendering() &&
		    Common::Gates::Enabled(Common::Gates::Gate::ShaderWriteDefer)) {
			buffer.NotePendingShaderWrite(shader_write_stages);
			Common::FrameStats::Add(Common::FrameStats::Counter::ShaderWriteBarriersDeferred, 1);
			buffer.Scheduler().GpuMark(GpuTimeProfiler::Kind::Barrier, 1);
			LogDrawPhase(draw.Name(), "DrawComplete");
			if (!draw.IsIndexed()) {
				SetDrawDebugPhase(buffer, submit_id, draw, state, 0x700u);
			}
			RecordDrawCompleteBreadcrumb(buffer, submit_id, draw, state);
			lap.Mark(Common::FrameStats::Counter::DrawEmitNs);
			Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmRecNs);
			return;
		}
		// Gate "swlocal": a fragment-only shader-write barrier can be recorded inside the open
		// pass instead of tearing it down, and the wide barrier is owed until the pass closes.
		// Session 71: the predicate is evaluated and counted whether or not the gate is on; the
		// gate still chooses the branch, so no decision changes.
		const auto blocked  = shader_write_stages & ~FramebufferSpaceStages();
		const bool local_ok = m_context.GetGraphics().dynamic_rendering_local_read_enabled &&
		                      buffer.IsRendering() && !blocked;
		Common::FrameStats::Add(
		    local_ok ? Common::FrameStats::Counter::ShaderWriteLocalEligible
		    : (blocked & vk::PipelineStageFlagBits::eMeshShaderEXT)
		        ? Common::FrameStats::Counter::ShaderWriteLocalMeshBlocked
		    : blocked ? Common::FrameStats::Counter::ShaderWriteLocalStageBlocked
		              : Common::FrameStats::Counter::ShaderWriteLocalClosed,
		    1);
		const bool local = local_ok && Common::Gates::Enabled(Common::Gates::Gate::ShaderWriteLocal);
		if (local) {
			buffer.CheckNoPublish(publish_mark);
			ShaderWriteBarrierLocal(vk_buffer, shader_write_stages);
			buffer.NotePendingShaderWrite(shader_write_stages);
		} else {
			buffer.Scheduler().EndRendering(RenderPassEnd::ShaderWrite);
			buffer.CheckNoPublish(publish_mark);
			ShaderWriteBarrier(vk_buffer, shader_write_stages);
		}
		buffer.Scheduler().GpuMark(GpuTimeProfiler::Kind::Barrier, 1);
	}
	LogDrawPhase(draw.Name(), "DrawComplete");
	if (!draw.IsIndexed()) {
		SetDrawDebugPhase(buffer, submit_id, draw, state, 0x700u);
	}
	RecordDrawCompleteBreadcrumb(buffer, submit_id, draw, state);
	lap.Mark(Common::FrameStats::Counter::DrawEmitNs);
	Common::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmRecNs);
}

// Session 123, knob "skipceil" (MEASUREMENT ONLY): a draw reached the skip site off the GuestGpu thread while the
// knob is on (skc_xthr, must read 0; the only known path, the m4baton relay, is refused at the latch).
static void SkipCeilOffThreadDraw() {
	if (Common::Gates::Value(Common::Gates::Knob::SkipCeil) != 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcXthr, 1);
	}
}

void RenderExecutor::DrawIndex(uint64_t submit_id, CommandBuffer& buffer,
                               const DrawIndexArgs& args) {
	KYTY_PROFILER_FUNCTION();
	RenderDocNoteGpuWork();
	Rk3Latch(); // Session 126, knob "rk3cen" (C3): latched for this draw, before any return
	// Session 127, knob "rtskip" (s.4.1): latched ONCE for this draw, before any return - one knob load and one thread-local
	// test while the knob is 0 and the previous draw was not armed.
	if (const auto rts_value = Common::Gates::Value(Common::Gates::Knob::RtSkip); rts_value != 0 || t_rts != 0)
	    [[unlikely]] {
		RtsLatchSlow(buffer, rts_value);
	}
	// Session 123, knob "skipceil" (MEASUREMENT ONLY, design123.md s.1.4): a draw of a skippable frame, before any return.
	if (Common::SkipCeil::t_skip) [[unlikely]] {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcSd, 1);
	}

	EXIT_IF(buffer.IsInvalid());
	EXIT_IF(args.offset_source == DrawOffsetSource::DrawState && args.first_instance != 0);
	{
		Common::FrameStats::Scope pop_scope(Common::FrameStats::Counter::DrawPopNs);
		buffer.Scheduler().PopPendingOperationsLazy();
	}
	auto& ucfg   = buffer.GetUserConfig();
	auto& sh_ctx = buffer.GetShaders();

	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::DrawIndex), submit_id,
	                    args.index_count, 0, 1, args.instance_count,
	                    reinterpret_cast<uint64_t>(args.index_addr));

	// Session 68, gate "amut": the render mutex is one object for draw, dispatch and present, so
	// the time it is held is the serial floor of any threading scheme (renderContext.h:80).
	// Session 69, gate "mutsite": arms the same MutexMark and adds the phase chain below.
	const bool mut_site = Common::Gates::Enabled(Common::Gates::Gate::MutexSites);
	const auto lock_t0  = (Common::Gates::Enabled(Common::Gates::Gate::MutateTime) || mut_site) &&
	                             Common::FrameStats::Enabled()
	                         ? Common::FrameStats::NowNs()
	                         : 0;
	Common::LockGuard            lock(m_context.GetMutex());
	Common::FrameStats::MutexMark lock_mark(lock_t0);
	// The destructor books whatever is left to mh_tail_us, so the draws that return early out of
	// the middle of the critical section still account for their whole hold.
	Common::FrameStats::HoldLap hold_lap(mut_site, Common::FrameStats::Counter::HoldTailNs);
	Common::FrameStats::HoldLap::Count(Common::FrameStats::Counter::HoldEntries);
	// Session 105, knob "ctxtick" >= 2: check the buffer and mark the thread as inside a draw.
	const CtxTick::OpScope ctx_op(m_context, buffer, "draw-index");
	// Session 123, knob "skipceil" = 2 (census, s.3.1): the draw is one census operation - K up to the skip site of a
	// skippable frame (D from there on), R in a translated frame.
	const SkcCensus::OpScope skc_op(m_context.GetTextureCache(),
	                                Common::SkipCeil::t_skip ? Common::SkipCeil::KindK : Common::SkipCeil::KindR, true);
	// Session 97, gate "bindfloor": latch the floor decision for this whole draw before
	// RefreshShaders reaches ProgramCache::Get (descriptors.h, BindFloorLatchOp).
	// Session 98: the draw's op-site latch; the two addresses are the GDS-trigger key, hashed
	// only at KYTY_BIND_FLOOR_LATCH=2.
	BindFloorLatchDraw(sh_ctx.GetVs().es_regs.data_addr, sh_ctx.GetPs().ps_regs.data_addr);
	// Session 94, gate "mergecost": the start of this draw's pre-class interval, right after
	// the render mutex (the lock wait is outside it, as it is outside every mh_* phase).
	m_merge_cost.draw_t0 = Common::Gates::Enabled(Common::Gates::Gate::MergeCost) &&
	                               Common::FrameStats::Enabled()
	                           ? Common::FrameStats::NowNs()
	                           : 0;
	DrawStatBegin();
	if (args.index_count == 0 || args.instance_count == 0) {
		if (Common::SkipCeil::t_skip) [[unlikely]] {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcZeroD, 1); // Session 123
		}
		return;
	}

	// Session 123, knob "skipceil": the guest's metadata operation and depth copy in the draw wrapper execute in every
	// frame (operations K, class K14; skc_keepd).
	if (ConsumeMetadataColorOperation(buffer)) {
		MaterializeBoundTargetDccClears(buffer);
		ResetBindings();
		if (Common::SkipCeil::t_skip) [[unlikely]] {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcKeepD, 1);
		}
		return;
	}
	if (DepthStencilCopy(buffer)) {
		ResetBindings();
		if (Common::SkipCeil::t_skip) [[unlikely]] {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcKeepD, 1);
		}
		return;
	}

	// Session 123, knob "skipceil" (MEASUREMENT ONLY, design123.md s.1.4): the skip site - below it everything is the
	// host translation of the draw.  Mode 1 returns here (no binding exists yet, nothing to reset; m_skipped_draws is not
	// touched); mode 2 translates it as a D operation of the census.
	if (Common::SkipCeil::t_skip) [[unlikely]] {
		if (Common::SkipCeil::t_mode == 1) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcSkipD, 1);
			return;
		}
		SkcCensus::SkipSiteD();
	} else if (!Common::SkipCeil::t_gpu) [[unlikely]] {
		SkipCeilOffThreadDraw();
	}

	if (!DrawHasValidVertexShader(sh_ctx)) {
		if (Common::SkipCeil::t_mode == 3 && Common::SkipCeil::t_skip) [[unlikely]] {
			SkcCensus::G3Empty(); // Session 124 ([RC13]): a D draw without work
		}
		return;
	}

	if (ShouldSkipGeShader(buffer, m_context.GetGpu().GetFrameNum())) {
		if (Common::SkipCeil::t_mode == 3 && Common::SkipCeil::t_skip) [[unlikely]] {
			SkcCensus::G3Empty(); // Session 124 ([RC13])
		}
		return;
	}

	if (graphics_debug_dump_enabled()) {
		LOGF("GraphicsRenderDrawIndex():Shader:\n");
		uc_print("GraphicsRenderDrawIndex():UserConfig:", ucfg);
		hw_print(buffer);

		LOGF("GraphicsRenderDrawIndex():Parameters:\n"
		     "\t index_type_and_size = 0x%08" PRIx32 "\n"
		     "\t index_count         = 0x%08" PRIx32 "\n"
		     "\t index_addr          = 0x%016" PRIx64 "\n"
		     "\t instance_count      = 0x%08" PRIx32 "\n"
		     "\t base_vertex         = 0x%08" PRIx32 "\n"
		     "\t first_instance      = 0x%08" PRIx32 "\n",
		     args.index_type_and_size, args.index_count,
		     reinterpret_cast<uint64_t>(args.index_addr), args.instance_count,
		     static_cast<uint32_t>(args.base_vertex), args.first_instance);
	}

	uc_check(ucfg);

	{
		Common::FrameStats::Scope check_scope(Common::FrameStats::Counter::DrawCheckNs);
		hw_check(buffer);
	}

	vk::PrimitiveTopology topology = vk::PrimitiveTopology::ePointList;
	if (!GetDrawTopology(ucfg, false, topology)) {
		return;
	}

	DrawIndexBufferSource index_source {};
	index_source.address = reinterpret_cast<uint64_t>(args.index_addr);
	switch (static_cast<Prospero::IndexType>(args.index_type_and_size)) {
		case Prospero::IndexType::kIndex16:
			index_source.type               = vk::IndexType::eUint16;
			index_source.guest_element_size = 2;
			break;
		case Prospero::IndexType::kIndex32:
			index_source.type               = vk::IndexType::eUint32;
			index_source.guest_element_size = 4;
			break;
		case Prospero::IndexType::kIndex8:
			index_source.guest_element_size = 1;
			break;
		default: EXIT("unknown index_type_and_size: %u\n", args.index_type_and_size);
	}
	index_source.size = static_cast<uint64_t>(args.index_count) * index_source.guest_element_size;
	const bool primitive_restart = ResolvePrimitiveRestart(buffer, index_source);

	std::vector<uint16_t> expanded_indices;
	if (index_source.guest_element_size == 1) {
		EXIT_NOT_IMPLEMENTED(args.index_addr == nullptr);
		const auto* src = static_cast<const uint8_t*>(args.index_addr);
		expanded_indices.resize(args.index_count);
		for (uint32_t i = 0; i < args.index_count; i++) {
			expanded_indices[i] = primitive_restart && src[i] == 0xffu ? 0xffffu : src[i];
		}
		index_source.host_data = expanded_indices.data();
		index_source.size      = expanded_indices.size() * sizeof(uint16_t);
	}

	const DrawCallInfo draw {CommandBufferDebugOp::DrawIndex, args.index_count,
	                        args.instance_count, args.first_instance};
	DrawStateLease state_lease; // gate "drawstate"
	auto&          state = state_lease.State();
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldPrologueNs);
	{
		// Session 83, knob "mutwide" bit 0: PrepareDrawRenderState reaches FindRenderTarget and
		// FindDepthTarget, which DESIGN_82_parallel.md 4 classifies EXCLUSIVE on
		// TextureCache::m_lock, yet mh_rt_us carries no MutScope and so sits outside a_mut_us.
		Common::FrameStats::MutScope wide_rt(
		    (Common::Gates::Value(Common::Gates::Knob::MutWide) & 1u) != 0,
		    Common::FrameStats::Counter::MutWideScopes);
		// Session 126, knob "rk3cen" (C4): the span of the target resolution of an armed draw.
		const auto rk3_c4    = Rk3ResBegin(&buffer.GetRegisters(), args.render_target_slice_offset);
		// Session 127, knob "rtskip" (place A): at 0 the previous call.
		const bool prepared  = t_rts == 0 ? PrepareDrawRenderState(buffer, draw, args.render_target_slice_offset, state)
		                                  : RtsPlaceA(buffer, draw, args.render_target_slice_offset, state);
		Rk3ResEnd(rk3_c4);
		if (!prepared) {
			ResetBindings();
			return;
		}
	}
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldTargetsNs);

	{
		// Session 83, knob "mutwide" bit 1: RefreshShaders reaches ProgramCache and PipelineCache,
		// whose maps DESIGN_82_parallel.md 5.3 keeps EXCLUSIVE while the memo holds iterators.
		Common::FrameStats::MutScope wide_prog(
		    (Common::Gates::Value(Common::Gates::Knob::MutWide) & 2u) != 0,
		    Common::FrameStats::Counter::MutWideScopes);
		RefreshShaders(buffer, draw, state);
	}
	// Session 133, knob "rbcen" (MEASUREMENT ONLY; design133.md rev 2 s.2.2): the latch of this draw, before the mark
	// that opens mh_bind - its price lands in mh_prog_us.
	Common::RbCen::Latch(Common::Gates::Value(Common::Gates::Knob::RebindCensus), mut_site,
	                     Common::Gates::Value(Common::Gates::Knob::RebindSlowCensus)); // session 135, knob "rbslow"
	Common::B2Reuse::OpBegin(); // Session 134, knob "b2reuse" (s.2.2): the operation of b2r_hit_draw
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldProgramsNs);

	LogDrawStateIfNeeded(buffer, draw, state, args.index_type_and_size,
	                     args.index_addr);

	const bool indirect = args.offset_source == DrawOffsetSource::IndirectArgs;
	const auto [vertex_offset, instance_offset] =
	    indirect ? std::pair<int32_t, uint32_t> {0, args.first_instance}
	             : ResolveDrawOffsets(ucfg.GetIndexOffset(), state.vertex_info[0]);

	DrawEmitInfo emit {};
	emit.indirect_args_addr = args.indirect_args_addr;
	emit.vertex_offset      = vertex_offset + args.base_vertex;
	emit.first_instance     = instance_offset;

	ExecutePreparedDraw(submit_id, buffer, draw, state, topology, emit, index_source,
	                    primitive_restart);
	ResetBindings();
}

// NOLINTNEXTLINE(readability-function-cognitive-complexity)
void RenderExecutor::DrawAuto(uint64_t submit_id, CommandBuffer& buffer, const DrawAutoArgs& args) {
	KYTY_PROFILER_FUNCTION();
	RenderDocNoteGpuWork();
	Rk3Latch(); // Session 126, knob "rk3cen" (C3): latched for this draw, before any return
	// Session 127, knob "rtskip" (s.4.1): latched ONCE for this draw, before any return - one knob load and one thread-local
	// test while the knob is 0 and the previous draw was not armed.
	if (const auto rts_value = Common::Gates::Value(Common::Gates::Knob::RtSkip); rts_value != 0 || t_rts != 0)
	    [[unlikely]] {
		RtsLatchSlow(buffer, rts_value);
	}
	// Session 123, knob "skipceil" (MEASUREMENT ONLY, design123.md s.1.4): a draw of a skippable frame, before any return.
	if (Common::SkipCeil::t_skip) [[unlikely]] {
		Common::FrameStats::Add(Common::FrameStats::Counter::SkcSd, 1);
	}

	EXIT_IF(buffer.IsInvalid());
	EXIT_IF(args.offset_source == DrawOffsetSource::DrawState && args.first_instance != 0);
	{
		Common::FrameStats::Scope pop_scope(Common::FrameStats::Counter::DrawPopNs);
		buffer.Scheduler().PopPendingOperationsLazy();
	}
	auto& ucfg   = buffer.GetUserConfig();
	auto& sh_ctx = buffer.GetShaders();

	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::DrawIndexAuto), submit_id,
	                    args.vertex_count, 0, args.first_vertex, args.instance_count,
	                    args.first_instance);

	// Session 68, gate "amut", and session 69 gate "mutsite": see DrawIndex above.
	const bool mut_site = Common::Gates::Enabled(Common::Gates::Gate::MutexSites);
	const auto lock_t0  = (Common::Gates::Enabled(Common::Gates::Gate::MutateTime) || mut_site) &&
	                             Common::FrameStats::Enabled()
	                         ? Common::FrameStats::NowNs()
	                         : 0;
	Common::LockGuard            lock(m_context.GetMutex());
	Common::FrameStats::MutexMark lock_mark(lock_t0);
	Common::FrameStats::HoldLap hold_lap(mut_site, Common::FrameStats::Counter::HoldTailNs);
	Common::FrameStats::HoldLap::Count(Common::FrameStats::Counter::HoldEntries);
	// Session 105, knob "ctxtick" >= 2: see DrawIndex above.
	const CtxTick::OpScope ctx_op(m_context, buffer, "draw-auto");
	// Session 123, knob "skipceil" = 2 (census, s.3.1): the draw is one census operation - K up to the skip site of a
	// skippable frame (D from there on), R in a translated frame.
	const SkcCensus::OpScope skc_op(m_context.GetTextureCache(),
	                                Common::SkipCeil::t_skip ? Common::SkipCeil::KindK : Common::SkipCeil::KindR, true);
	// Session 97, gate "bindfloor": latch the floor decision for this whole draw before
	// RefreshShaders reaches ProgramCache::Get (descriptors.h, BindFloorLatchOp).
	// Session 98: the draw's op-site latch; the two addresses are the GDS-trigger key, hashed
	// only at KYTY_BIND_FLOOR_LATCH=2.
	BindFloorLatchDraw(sh_ctx.GetVs().es_regs.data_addr, sh_ctx.GetPs().ps_regs.data_addr);
	// Session 94, gate "mergecost": the start of this draw's pre-class interval, right after
	// the render mutex (the lock wait is outside it, as it is outside every mh_* phase).
	m_merge_cost.draw_t0 = Common::Gates::Enabled(Common::Gates::Gate::MergeCost) &&
	                               Common::FrameStats::Enabled()
	                           ? Common::FrameStats::NowNs()
	                           : 0;
	DrawStatBegin();
	if (args.vertex_count == 0 || args.instance_count == 0) {
		if (Common::SkipCeil::t_skip) [[unlikely]] {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcZeroD, 1); // Session 123
		}
		return;
	}

	// Session 123, knob "skipceil": the guest's metadata operation and depth copy in the draw wrapper execute in every
	// frame (operations K, class K14; skc_keepd).
	if (ConsumeMetadataColorOperation(buffer)) {
		MaterializeBoundTargetDccClears(buffer);
		ResetBindings();
		if (Common::SkipCeil::t_skip) [[unlikely]] {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcKeepD, 1);
		}
		return;
	}
	if (DepthStencilCopy(buffer)) {
		ResetBindings();
		if (Common::SkipCeil::t_skip) [[unlikely]] {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcKeepD, 1);
		}
		return;
	}

	// Session 123, knob "skipceil" (MEASUREMENT ONLY, design123.md s.1.4): the skip site - below it everything is the
	// host translation of the draw.  Mode 1 returns here (no binding exists yet, nothing to reset; m_skipped_draws is not
	// touched); mode 2 translates it as a D operation of the census.
	if (Common::SkipCeil::t_skip) [[unlikely]] {
		if (Common::SkipCeil::t_mode == 1) {
			Common::FrameStats::Add(Common::FrameStats::Counter::SkcSkipD, 1);
			return;
		}
		SkcCensus::SkipSiteD();
	} else if (!Common::SkipCeil::t_gpu) [[unlikely]] {
		SkipCeilOffThreadDraw();
	}

	if (!DrawHasValidVertexShader(sh_ctx)) {
		if (Common::SkipCeil::t_mode == 3 && Common::SkipCeil::t_skip) [[unlikely]] {
			SkcCensus::G3Empty(); // Session 124 ([RC13]): a D draw without work
		}
		return;
	}

	if (ShouldSkipGeShader(buffer, m_context.GetGpu().GetFrameNum())) {
		if (Common::SkipCeil::t_mode == 3 && Common::SkipCeil::t_skip) [[unlikely]] {
			SkcCensus::G3Empty(); // Session 124 ([RC13])
		}
		return;
	}

	if (graphics_debug_dump_enabled()) {
		LOGF("GraphicsRenderDrawIndexAuto():Shader:\n");
		uc_print("GraphicsRenderDrawIndexAuto():UserConfig:", ucfg);
		hw_print(buffer);

		LOGF("GraphicsRenderDrawIndexAuto():Parameters:\n"
		     "\t vertex_count        = 0x%08" PRIx32 "\n"
		     "\t instance_count      = 0x%08" PRIx32 "\n"
		     "\t first_vertex        = 0x%08" PRIx32 "\n"
		     "\t first_instance      = 0x%08" PRIx32 "\n",
		     args.vertex_count, args.instance_count, args.first_vertex, args.first_instance);
	}

	uc_check(ucfg);

	{
		Common::FrameStats::Scope check_scope(Common::FrameStats::Counter::DrawCheckNs);
		hw_check(buffer);
	}

	const DrawCallInfo draw {CommandBufferDebugOp::DrawIndexAuto,
	                         args.vertex_count, args.instance_count, args.first_instance};

	DrawStateLease state_lease; // gate "drawstate"
	auto&          state = state_lease.State();
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldPrologueNs);
	{
		// Session 83, knob "mutwide" bit 0: PrepareDrawRenderState reaches FindRenderTarget and
		// FindDepthTarget, which DESIGN_82_parallel.md 4 classifies EXCLUSIVE on
		// TextureCache::m_lock, yet mh_rt_us carries no MutScope and so sits outside a_mut_us.
		Common::FrameStats::MutScope wide_rt(
		    (Common::Gates::Value(Common::Gates::Knob::MutWide) & 1u) != 0,
		    Common::FrameStats::Counter::MutWideScopes);
		// Session 126, knob "rk3cen" (C4): the span of the target resolution of an armed draw.
		const auto rk3_c4    = Rk3ResBegin(&buffer.GetRegisters(), args.render_target_slice_offset);
		// Session 127, knob "rtskip" (place A): at 0 the previous call.
		const bool prepared  = t_rts == 0 ? PrepareDrawRenderState(buffer, draw, args.render_target_slice_offset, state)
		                                  : RtsPlaceA(buffer, draw, args.render_target_slice_offset, state);
		Rk3ResEnd(rk3_c4);
		if (!prepared) {
			ResetBindings();
			return;
		}
	}
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldTargetsNs);

	// Unlike DrawIndex the topology is resolved here, so its cost lands in mh_prog_us.
	vk::PrimitiveTopology topology = vk::PrimitiveTopology::ePointList;
	{
		// Session 83, knob "mutwide" bit 1: RefreshShaders reaches ProgramCache and PipelineCache,
		// whose maps DESIGN_82_parallel.md 5.3 keeps EXCLUSIVE while the memo holds iterators.
		Common::FrameStats::MutScope wide_prog(
		    (Common::Gates::Value(Common::Gates::Knob::MutWide) & 2u) != 0,
		    Common::FrameStats::Counter::MutWideScopes);
		if (!GetDrawTopology(ucfg, true, topology)) {
			ResetBindings();
			return;
		}
		RefreshShaders(buffer, draw, state);
	}
	// Session 133, knob "rbcen" (MEASUREMENT ONLY; design133.md rev 2 s.2.2): the latch of this draw, before the mark
	// that opens mh_bind - its price lands in mh_prog_us.
	Common::RbCen::Latch(Common::Gates::Value(Common::Gates::Knob::RebindCensus), mut_site,
	                     Common::Gates::Value(Common::Gates::Knob::RebindSlowCensus)); // session 135, knob "rbslow"
	Common::B2Reuse::OpBegin(); // Session 134, knob "b2reuse" (s.2.2): the operation of b2r_hit_draw
	Common::FrameStats::HoldLap::Mark(Common::FrameStats::Counter::HoldProgramsNs);

	const bool rect_list = ucfg.GetPrimType() == Prospero::PrimitiveType::kRectList;
	if (rect_list && state.vertex_info[0].buffers_num == 0 &&
	    state.vertex_info[0].stage.program->param_export_mask == 0 &&
	    state.ps_input_info.input_num != 0) {
		if (graphics_debug_dump_enabled()) {
			LOGF("DrawIndexAuto: skipping rect-list draw with no VS param exports and PS inputs: "
			     "ps_inputs=%u ps=0x%016" PRIx64 " es=0x%016" PRIx64 " gs=0x%016" PRIx64 "\n",
			     state.ps_input_info.input_num, sh_ctx.GetPs().ps_regs.data_addr,
			     sh_ctx.GetVs().es_regs.data_addr, sh_ctx.GetVs().gs_regs.data_addr);
		}
		ResetBindings();
		return;
	}

	LogDrawStateIfNeeded(buffer, draw, state, 0, nullptr);

	const bool indirect = args.offset_source == DrawOffsetSource::IndirectArgs;
	const auto [vertex_offset, instance_offset] =
	    indirect ? std::pair<int32_t, uint32_t> {0, args.first_instance}
	             : ResolveDrawOffsets(ucfg.GetIndexOffset(), state.vertex_info[0]);
	DrawEmitInfo emit {};
	emit.indirect_args_addr = args.indirect_args_addr;
	emit.first_vertex =
	    static_cast<uint32_t>(vertex_offset + static_cast<int32_t>(args.first_vertex));
	emit.first_instance = instance_offset;

	DrawIndexBufferSource index_source {};
	ExecutePreparedDraw(submit_id, buffer, draw, state, topology, emit, index_source, false);
	ResetBindings();
}

bool RenderExecutor::ResolveColorTargets(CommandBuffer& buffer, uint32_t render_target_slice_offset) {
	const auto& hw = buffer.GetRegisters();
	if (hw.GetColorControl().mode != 3) {
		return false;
	}

	const auto& src_rt = hw.GetRenderTarget(0);
	const auto& dst_rt = hw.GetRenderTarget(1);
	if (src_rt.base.addr == 0 || dst_rt.base.addr == 0) {
		return false;
	}

	RenderColorInfo src {};
	RenderColorInfo dst {};
	ResolveRenderColorTarget(buffer, src, render_target_slice_offset, 0, true, true);
	ResolveRenderColorTarget(buffer, dst, render_target_slice_offset, 1, true, true);
	if (!src.image_id || !dst.image_id) {
		return false;
	}
	if (src.desc.info.data.address == dst.desc.info.data.address &&
	    src.guest_mip_level == dst.guest_mip_level &&
	    src.guest_array_layer == dst.guest_array_layer) {
		return true;
	}

	auto& cache = m_context.GetTextureCache();
	// Session 124, knob "skipceil" = 3 (closure census, ROADMAP s122 item 47(e), N4): the resolve reads one level and
	// layer of the MSAA source and writes one level and layer of the destination.
	if (Common::SkipCeil::t_mode == 3) [[unlikely]] {
		SkcCensus::G3ReadSub(cache, src.image_id, SkcCensus::Sub {src.guest_mip_level, 1, src.guest_array_layer, 1, 0, 1});
	}
	{
		const SkcCensus::SubScope skc3_sub(SkcCensus::Sub {dst.guest_mip_level, 1, dst.guest_array_layer, 1, 0, 1});
		cache.MarkGpuWritten(dst.image_id);
	}
	auto& source      = cache.GetImage(src.image_id);
	auto& destination = cache.GetImage(dst.image_id);
	destination.Resolve(source, {src.guest_mip_level, 1, src.guest_array_layer, 1},
	                    {dst.guest_mip_level, 1, dst.guest_array_layer, 1});
	return true;
}

} // namespace Libs::Graphics

// Session 126, knob "rk3cen" (C1, C2): the cold halves of the HW::Context hooks (common/rk3Census.h).
// Session 127 (item 77(e)): one mask, a table per armed bit; rk3_wr_* / rts_wr* count only under their own bit.
void Common::Rk3::NoteWriteCold(const void* ctx, uint32_t group) noexcept {
	if ((t_hooks & HookRk3) != 0) {
		Libs::Graphics::Rk3HookWrite(ctx, group);
	}
	if ((t_hooks & HookRts) != 0) {
		Libs::Graphics::RtsHookWrite(ctx, group);
	}
}
void Common::Rk3::NoteObjectCold(const void* ctx) noexcept {
	if ((t_hooks & HookRk3) != 0) {
		Libs::Graphics::Rk3HookObject(ctx);
	}
	if ((t_hooks & HookRts) != 0) {
		Libs::Graphics::RtsHookObject(ctx);
	}
}
