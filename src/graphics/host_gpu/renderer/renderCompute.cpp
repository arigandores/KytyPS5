#include "common/assert.h"
#include "common/common.h"
#include "common/emulatorConfig.h"
#include "common/file.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/stringUtils.h"
#include "common/threads.h"
#include "graphics/guest_gpu/gpu_defs.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/image/imageInfo.h"
#include "graphics/host_gpu/renderer/pipeline/descriptors.h"
#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"
#include "graphics/host_gpu/renderer/pipeline/shaderResourceBarrier.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"
#include "graphics/shader/shader.h"
#include "kernel/eventQueue.h"
#include "kernel/memory.h"
#include "kernel/pthread.h"
#include "libs/errno.h"

#include <algorithm>
#include <cstdlib>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <span>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

namespace Libs::Graphics {
static uint64_t BufferDescriptorSize(const ShaderBufferResource& descriptor) {
	const uint64_t records = descriptor.NumRecords();
	const uint64_t stride  = descriptor.Stride();
	if (stride != 0 && records > UINT64_MAX / stride) {
		EXIT("compute buffer descriptor footprint overflow\n");
	}
	return stride == 0 ? records : records * stride;
}

bool RenderExecutor::TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,
                                                const CommandBuffer&          buffer) {
	const auto& program   = *input.stage.program;
	const auto& resources = input.stage.resources;
	if (resources.buffers.size() != program.info.buffers.size()) {
		EXIT("compute runtime buffer count does not match shader metadata\n");
	}
	auto& cache = buffer.GetContext().GetTextureCache();
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		const auto& resource   = program.info.buffers[i];
		const auto  descriptor = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
		// A metadata resource that is also read is not proven to be a full overwrite. Execute it
		// conservatively instead of replacing the dispatch with a coarse full-surface clear.
		if (cache.IsMeta(descriptor.Base48()) && (!resource.written || resource.read)) {
			return false;
		}
	}

	if (!program.info.has_bitwise_xor) {
		for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
			const auto& resource = program.info.buffers[i];
			if (resource.written) {
				const auto descriptor =
				    DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
				if (cache.ClearMeta(descriptor.Base48())) {
					return true;
				}
			}
		}
	}
	return false;
}

bool ResolveComputeImageClear(const ShaderComputeInputInfo& input, uint32_t group_x,
                              uint32_t group_y, uint32_t group_z, uint32_t mode,
                              ShaderBufferResource& resolved_descriptor, uint32_t& resolved_clear,
                              uint64_t& resolved_size) {
	const auto& program   = *input.stage.program;
	const auto& resources = input.stage.resources;
	if (program.info.buffers.size() != 1 || resources.buffers.size() != 1 ||
	    !program.info.images.empty() || !program.info.samplers.empty() || program.info.uses_dma ||
	    !resources.images.empty() || !resources.samplers.empty()) {
		return false;
	}
	const auto& resource   = program.info.buffers.front();
	const auto& raw        = resources.buffers.front();
	const auto  descriptor = DecodeNativeDescriptor<ShaderBufferResource>(raw);
	if (!resource.formatted || !resource.written || resource.read || resource.atomic ||
	    resource.scalar || resource.max_byte_extent != 16 || descriptor.Stride() != 16 ||
	    descriptor.Format() != Prospero::BufferFormat::k32_32_32_32UInt ||
	    descriptor.SwizzleEnabled() || descriptor.IndexStride() != 0 || descriptor.AddTid() ||
	    resource.packed_stride != descriptor.PackedStride() || raw.dword_count != 4 ||
	    program.user_data_base != 0 || resources.user_data.size() != 8) {
		return false;
	}
	for (uint32_t i = 0; i < raw.dword_count; i++) {
		if (raw.dwords[i] != resources.user_data[i]) {
			return false;
		}
	}
	const uint32_t clear = resources.user_data[4];
	if (resources.user_data[5] != clear || resources.user_data[6] != clear ||
	    resources.user_data[7] != clear) {
		return false;
	}
	const bool full_dispatch =
	    input.dispatch_thread_dimensions && input.threads_num[0] == 64 &&
	    input.threads_num[1] == 1 && input.threads_num[2] == 1 && group_x != 0 && group_y == 1 &&
	    group_z == 1 && input.dispatch_threads_num[0] == group_x &&
	    input.dispatch_threads_num[1] == 1 && input.dispatch_threads_num[2] == 1 &&
	    input.group_id[0] && !input.group_id[1] && !input.group_id[2] &&
	    input.thread_ids_num == 1 && input.wave_size == 64 && !input.tg_size_en && mode == 0x61u &&
	    group_x % input.threads_num[0] == 0 && descriptor.NumRecords() == group_x;
	const auto size = BufferDescriptorSize(descriptor);
	if (!full_dispatch || size == 0) {
		return false;
	}
	resolved_descriptor = descriptor;
	resolved_clear      = clear;
	resolved_size       = size;
	return true;
}

static bool TryConsumeComputeImageClear(const ShaderComputeInputInfo& input, CommandBuffer& command,
                                        uint32_t group_x, uint32_t group_y, uint32_t group_z,
                                        uint32_t mode) {
	ShaderBufferResource descriptor;
	uint32_t             packed_clear = 0;
	uint64_t             size         = 0;
	if (!ResolveComputeImageClear(input, group_x, group_y, group_z, mode, descriptor, packed_clear,
	                              size)) {
		return false;
	}
	auto& cache = command.GetContext().GetTextureCache();
	if (!cache.ClearImageFromBuffer(command, descriptor.Base48(), size, packed_clear)) {
		// Recognized metadata-fill shaders access DCC as an ordinary storage buffer and may run
		// before the render target is bound. TryConsumeDccFill either consumes registered state
		// or retains a PendingDcc fill while allowing the dispatch to run.
		const bool registered_metadata =
		    cache.TryConsumeDccFill(descriptor.Base48(), size, packed_clear);
		static std::atomic<uint32_t> logged_metadata_clears {0};
		if (logged_metadata_clears.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("GraphicsRenderDispatchDirect: %s metadata clear shader=0x%016" PRIx64
			     " addr=0x%016" PRIx64 " size=0x%016" PRIx64 " value=0x%08" PRIx32 "\n",
			     registered_metadata ? "tracked" : "deferred", input.stage.program->shader_hash,
			     descriptor.Base48(), size, packed_clear);
		}
		if (registered_metadata) {
			return true;
		}
		return false;
	}
	static std::atomic<uint32_t> logged_clears {0};
	if (logged_clears.fetch_add(1, std::memory_order_relaxed) < 32) {
		LOGF("GraphicsRenderDispatchDirect: compute image clear shader=0x%016" PRIx64
		     " addr=0x%016" PRIx64 " size=0x%016" PRIx64 " value=0x%08" PRIx32 "\n",
		     input.stage.program->shader_hash, descriptor.Base48(), size, packed_clear);
	}
	return true;
}

void RenderExecutor::DispatchDirect(uint64_t submit_id, CommandBuffer& buffer,
                                    uint32_t thread_group_x, uint32_t thread_group_y,
                                    uint32_t thread_group_z, uint32_t mode,
                                    uint64_t indirect_args_addr) {
	EXIT_IF(buffer.IsInvalid());
	bool indirect = indirect_args_addr != 0;
	m_context.GetCommandScheduler().PopPendingOperations();
	auto& ctx    = buffer.GetRegisters();
	auto& sh_ctx = buffer.GetShaders();

	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::DispatchDirect), submit_id,
	                    thread_group_x, thread_group_y, thread_group_z, mode,
	                    sh_ctx.GetCs().cs_regs.data_addr);

	Common::LockGuard lock(m_context.GetMutex());
	if (sh_ctx.GetCs().cs_regs.data_addr == 0) {
		LOGF("GraphicsRenderDispatchDirect: temporary: ignoring dispatch with null CS shader, "
		     "groups=%ux%ux%u mode=%u\n",
		     thread_group_x, thread_group_y, thread_group_z, mode);
		return;
	}

	if (!ShaderAddressValid(sh_ctx.GetCs().cs_regs.data_addr)) {
		return;
	}

	constexpr uint32_t DISPATCH_INITIATOR_USE_THREAD_DIMENSIONS = 1u << 5u;
	constexpr uint32_t DISPATCH_INITIATOR_BASE_BITS             = 0x41u;
	constexpr uint32_t DISPATCH_INITIATOR_MODIFIER_BITS         = 0xa038u;
	constexpr uint32_t DISPATCH_INITIATOR_KNOWN_MASK =
	    DISPATCH_INITIATOR_BASE_BITS | DISPATCH_INITIATOR_MODIFIER_BITS;

	const uint32_t unknown_mode_bits = mode & ~DISPATCH_INITIATOR_KNOWN_MASK;
	if (unknown_mode_bits != 0) {
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("GraphicsRenderDispatchDirect: unknown dispatch initiator bits "
			     "mode=0x%08" PRIx32 " unknown=0x%08" PRIx32 " shader=0x%016" PRIx64
			     " groups=%ux%ux%u\n",
			     mode, unknown_mode_bits, sh_ctx.GetCs().cs_regs.data_addr, thread_group_x,
			     thread_group_y, thread_group_z);
		}
	}

	const auto& cs_regs = sh_ctx.GetCs();
	const auto& sh_regs = ctx.GetShaderRegisters();

	ShaderComputeInputInfo input_info {};
	const bool use_thread_dimensions = (mode & DISPATCH_INITIATOR_USE_THREAD_DIMENSIONS) != 0;
	input_info.dispatch_thread_dimensions = use_thread_dimensions;
	const auto compute_program =
	    m_context.GetPipelineCache().GetComputeProgram(cs_regs, sh_regs, input_info);
	if (use_thread_dimensions) {
		input_info.dispatch_threads_num[0]    = thread_group_x;
		input_info.dispatch_threads_num[1]    = thread_group_y;
		input_info.dispatch_threads_num[2]    = thread_group_z;
	}

	const uint32_t frame_num = static_cast<uint32_t>(m_context.GetGpu().GetFrameNum());
	const bool     large_workgroup =
	    (input_info.threads_num[0] * input_info.threads_num[1] * input_info.threads_num[2] >= 512);
	const auto& program   = *input_info.stage.program;
	const auto& resources = input_info.stage.resources;
	// Refresh the debug record with the shader hash now that the program is known (the checkpoint
	// marker then names the shader instead of its guest address).
	buffer.SetDebugInfo(static_cast<uint32_t>(CommandBufferDebugOp::DispatchDirect), submit_id,
	                    thread_group_x, thread_group_y, thread_group_z, mode, program.shader_hash);
	// Debug aid: KYTY_TRACE_CS=1 logs every direct dispatch whose raw X dimension is zero, and
	// KYTY_TRACE_CS=<hex hash>[,<hex hash>...] logs every dispatch of the listed shaders.
	static const std::vector<uint64_t> trace_cs = [] {
		std::vector<uint64_t> out;
		const char*           value = std::getenv("KYTY_TRACE_CS");
		if (value == nullptr) {
			return out;
		}
		std::string_view text(value);
		while (!text.empty()) {
			const auto comma = text.find(',');
			const auto item  = std::string(text.substr(0, comma));
			text             = comma == std::string_view::npos ? std::string_view {} : text.substr(comma + 1u);
			out.push_back(std::strtoull(item.c_str(), nullptr, 16));
		}
		return out;
	}();
	if (!trace_cs.empty()) {
		const bool listed = std::find(trace_cs.begin(), trace_cs.end(), program.shader_hash) != trace_cs.end();
		if (listed || (!indirect && thread_group_x == 0)) {
			LOGF("TraceCS: frame=%u shader=0x%016" PRIx64 " raw=%ux%ux%u mode=0x%08" PRIx32
			     " threads_dims=%d indirect=%d" "\n",
			     frame_num, program.shader_hash, thread_group_x, thread_group_y, thread_group_z, mode,
			     use_thread_dimensions ? 1 : 0, indirect ? 1 : 0);
		}
	}
	// Debug aid: KYTY_SKIP_CS=<hex hash> drops every dispatch of that compute shader.
	static const char* skip_cs = std::getenv("KYTY_SKIP_CS");
	if (skip_cs != nullptr && program.shader_hash == std::strtoull(skip_cs, nullptr, 16)) {
		static std::atomic<uint32_t> skip_log_count {0};
		if (skip_log_count.fetch_add(1, std::memory_order_relaxed) < 4) {
			LOGF("GraphicsRenderDispatchDirect: skipping CS 0x%016" PRIx64 " (KYTY_SKIP_CS)\n",
			     program.shader_hash);
		}
		ResetBindings();
		return;
	}
	if (!indirect && TryConsumeComputeMetaClear(input_info, buffer)) {
		ResetBindings();
		return;
	}
	if (!indirect && TryConsumeComputeImageClear(input_info, buffer, thread_group_x, thread_group_y,
	                                thread_group_z, mode)) {
		ResetBindings();
		return;
	}
	const auto sampled_images = std::count_if(
	    program.info.images.begin(), program.info.images.end(), [](const auto& image) {
		    return image.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled;
	    });
	const bool                   has_sampler = !program.info.samplers.empty();
	static std::atomic<uint32_t> dispatch_log_count {0};
	if ((large_workgroup || has_sampler) &&
	    dispatch_log_count.fetch_add(1, std::memory_order_relaxed) < 512) {
		LOGF("GraphicsRenderDispatchDirect: frame=%u shader=0x%016" PRIx64
		     " groups=%ux%ux%u mode=0x%08" PRIx32 " local=%ux%ux%u "
		     "buffers=%zu textures=%zu sampled=%zu storage=%zu samplers=%zu push=%u\n",
		     frame_num, sh_ctx.GetCs().cs_regs.data_addr, thread_group_x, thread_group_y,
		     thread_group_z, mode, input_info.threads_num[0], input_info.threads_num[1],
		     input_info.threads_num[2], program.info.buffers.size(), program.info.images.size(),
		     sampled_images, program.info.images.size() - sampled_images,
		     program.info.samplers.size(),
		     program.bindings.UsesPushData()
		         ? static_cast<uint32_t>(sizeof(ShaderRecompiler::IR::PushData))
		         : 0u);
		for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
			const auto& buffer = program.info.buffers[i];
			const auto  r      = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
			LOGF("  CS buffer[%u]: source=%u usage=%s addr=0x%012" PRIx64
			     " stride=%u records=%u format=%u\n",
			     i, buffer.source, buffer.written ? "read-write" : "read-only", r.Base48(),
			     r.Stride(), r.NumRecords(), r.RawFormat());
		}
		for (uint32_t i = 0; i < program.info.images.size(); i++) {
			const auto& image = program.info.images[i];
			const auto  r     = DecodeNativeDescriptor<ShaderTextureResource>(resources.images[i]);
			LOGF("  CS texture[%u]: source=%u usage=%s sampled=%s addr=0x%010" PRIx64
			     " type=%u fmt=%u extent=%ux%u depth=%u levels=%u tile=%u\n",
			     i, image.source, image.written ? "read-write" : "read-only",
			     image.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled
			         ? "true"
			         : "false",
			     r.Base40(), static_cast<uint32_t>(r.Type()), static_cast<uint32_t>(r.Format()),
			     static_cast<uint32_t>(r.Width5()) + 1u, static_cast<uint32_t>(r.Height5()) + 1u,
			     static_cast<uint32_t>(r.Depth()) + 1u,
			     r.Type() == Prospero::ImageType::kColor2DMsaa ||
			             r.Type() == Prospero::ImageType::kColor2DMsaaArray
			         ? 1u
			         : static_cast<uint32_t>(image.r128 ? r.LastLevel() : r.MaxMip()) + 1u,
			     static_cast<uint32_t>(r.TileMode()));
		}
		for (uint32_t i = 0; i < program.info.samplers.size(); i++) {
			const auto r = DecodeNativeDescriptor<ShaderSamplerResource>(resources.samplers[i]);
			LOGF("  CS sampler[%u]: source=%u clamp=%u/%u/%u filter=%u/%u/%u mip=%u "
			     "lod=%u-%u bias=%d\n",
			     i, program.info.samplers[i].source, static_cast<uint32_t>(r.ClampX()),
			     static_cast<uint32_t>(r.ClampY()), static_cast<uint32_t>(r.ClampZ()),
			     static_cast<uint32_t>(r.XyMagFilter()), static_cast<uint32_t>(r.XyMinFilter()),
			     static_cast<uint32_t>(r.ZFilter()), static_cast<uint32_t>(r.MipFilter()),
			     static_cast<uint32_t>(r.MinLod()), static_cast<uint32_t>(r.MaxLod()),
			     static_cast<int32_t>(r.LodBias()));
		}
	}

	// Debug aid: KYTY_DUMP_CS=<hex hash> logs every buffer binding of that compute shader together
	// with the CPU view of its first dwords and the buffer-cache ownership flags; KYTY_SYNC_DISPATCH
	// logs every dispatch before it is recorded (see CommandProcessor::DispatchDirect).
	static const char* dump_cs      = std::getenv("KYTY_DUMP_CS");
	static const bool  sync_dispatch = std::getenv("KYTY_SYNC_DISPATCH") != nullptr;
	// KYTY_DUMP_ADDR=<hex guest address> additionally dumps every dispatch whose buffer or image
	// binding covers that address (finds the producers of a buffer).
	static const uint64_t dump_addr = [] {
		const char* value = std::getenv("KYTY_DUMP_ADDR");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	bool dump_this = dump_cs != nullptr && program.shader_hash == std::strtoull(dump_cs, nullptr, 16);
	if (!dump_this && dump_addr != 0) {
		for (uint32_t i = 0; i < program.info.buffers.size() && !dump_this; i++) {
			const auto r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
			const auto base = r.Base48();
			const auto size = BufferDescriptorSize(r);
			dump_this       = base != 0 && dump_addr >= base && dump_addr < base + size;
		}
		for (uint32_t i = 0; i < program.info.images.size() && !dump_this; i++) {
			const auto r    = DecodeNativeDescriptor<ShaderTextureResource>(resources.images[i]);
			const auto base = r.Base40();
			constexpr uint64_t ImageSpan = 64ull * 1024 * 1024; // extent unknown here; generous
			dump_this = base != 0 && dump_addr >= base && dump_addr < base + ImageSpan;
		}
	}
	if (!dump_this) {
		dump_this = ShaderStageTouchesAnyBuffer(input_info.stage, DebugDumpAddresses());
	}
	if (DebugDumpFrame(frame_num)) {
		LOGF("DumpDispatch: frame=%u shader=0x%016" PRIx64 " groups=%ux%ux%u mode=0x%08" PRIx32
		     " local=%ux%ux%u indirect=0x%016" PRIx64 " buffers=%zu images=%zu uses_dma=%d\n",
		     frame_num, program.shader_hash, thread_group_x, thread_group_y, thread_group_z, mode,
		     input_info.threads_num[0], input_info.threads_num[1], input_info.threads_num[2],
		     indirect_args_addr, program.info.buffers.size(), program.info.images.size(),
		     program.info.uses_dma ? 1 : 0);
		for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
			const auto& res  = program.info.buffers[i];
			const auto  r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
			const auto  base = r.Base48();
			const auto  size = BufferDescriptorSize(r);
			LOGF("  DumpCS buffer[%u]: source=%u usage=%s addr=0x%012" PRIx64 " stride=%u "
			     "records=%u size=0x%" PRIx64 " format=%u\n",
			     i, res.source, res.written ? "read-write" : "read-only", base, r.Stride(),
			     r.NumRecords(), size, r.RawFormat());
		}
		for (uint32_t i = 0; i < program.info.images.size(); i++) {
			const auto& image = program.info.images[i];
			const auto  r     = DecodeNativeDescriptor<ShaderTextureResource>(resources.images[i]);
			LOGF("  DumpCS image[%u]: source=%u usage=%s class=%s addr=0x%010" PRIx64
			     " type=%u fmt=%u extent=%ux%u depth=%u tile=%u dstsel=0x%03x levels=%u..%u"
			     " maxmip=%u pitch=%u meta=0x%010" PRIx64 " dcc=%d\n",
			     i, image.source, image.written ? "read-write" : "read-only",
			     image.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled
			         ? "sampled"
			         : "storage",
			     r.Base40(), static_cast<uint32_t>(r.Type()), static_cast<uint32_t>(r.Format()),
			     static_cast<uint32_t>(r.Width5()) + 1u, static_cast<uint32_t>(r.Height5()) + 1u,
			     static_cast<uint32_t>(r.Depth()) + 1u, static_cast<uint32_t>(r.TileMode()),
			     r.DstSelXYZW(), static_cast<uint32_t>(r.BaseLevel()),
			     static_cast<uint32_t>(r.LastLevel()), static_cast<uint32_t>(r.MaxMip()),
			     static_cast<uint32_t>(r.ArrayPitch()), r.MetaAddr() << 8u,
			     r.MetaCompress() ? 1 : 0);
		}
	}
	if (sync_dispatch || dump_this) {
		LOGF("SyncDispatch: frame=%u shader=0x%016" PRIx64 " cs=0x%016" PRIx64
		     " groups=%ux%ux%u mode=0x%08" PRIx32 " local=%ux%ux%u indirect=0x%016" PRIx64
		     " buffers=%zu images=%zu uses_dma=%d\n",
		     frame_num, program.shader_hash, sh_ctx.GetCs().cs_regs.data_addr, thread_group_x,
		     thread_group_y, thread_group_z, mode, input_info.threads_num[0],
		     input_info.threads_num[1], input_info.threads_num[2], indirect_args_addr,
		     program.info.buffers.size(), program.info.images.size(), program.info.uses_dma ? 1 : 0);
	}
	if (dump_this) {
		auto& cache = m_context.GetBufferCache();
		for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
			const auto& res  = program.info.buffers[i];
			const auto  r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
			const auto  base = r.Base48();
			const auto  size = BufferDescriptorSize(r);
			uint32_t    head[8] {};
			const auto  head_size = static_cast<uint64_t>(std::min<uint64_t>(sizeof(head), size));
			const bool  readable =
			    base != 0 && head_size != 0 &&
			    Libs::LibKernel::Memory::TryReadBacking(base, head, head_size);
			LOGF("  DumpCS buffer[%u]: source=%u usage=%s addr=0x%012" PRIx64 " stride=%u "
			     "records=%u size=0x%" PRIx64 " gpu_modified=%d cpu_modified=%d gpu_dirty=%d "
			     "cpu_head=%s%08x %08x %08x %08x %08x %08x %08x %08x\n",
			     i, res.source, res.written ? "read-write" : "read-only", base, r.Stride(),
			     r.NumRecords(), size,
			     (base != 0 && size != 0 && cache.IsRegionGpuModified(base, size)) ? 1 : 0,
			     (base != 0 && size != 0 && cache.IsRegionCpuModified(base, size)) ? 1 : 0,
			     (base != 0 && size != 0 && cache.HasGpuDirtyBytes(base, size)) ? 1 : 0,
			     readable ? "" : "(unreadable) ", head[0], head[1], head[2], head[3], head[4],
			     head[5], head[6], head[7]);
		}
		for (uint32_t i = 0; i < program.info.images.size(); i++) {
			const auto& image = program.info.images[i];
			const auto  r     = DecodeNativeDescriptor<ShaderTextureResource>(resources.images[i]);
			LOGF("  DumpCS image[%u]: source=%u usage=%s class=%s addr=0x%010" PRIx64
			     " type=%u fmt=%u extent=%ux%u depth=%u tile=%u\n",
			     i, image.source, image.written ? "read-write" : "read-only",
			     image.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled
			         ? "sampled"
			         : "storage",
			     r.Base40(), static_cast<uint32_t>(r.Type()), static_cast<uint32_t>(r.Format()),
			     static_cast<uint32_t>(r.Width5()) + 1u, static_cast<uint32_t>(r.Height5()) + 1u,
			     static_cast<uint32_t>(r.Depth()) + 1u, static_cast<uint32_t>(r.TileMode()));
		}
		// KYTY_DUMP_CS_REUPLOAD=1: experiment - mark every read-only buffer of the dumped shader as
		// CPU-modified so that the binding below re-uploads the current guest memory. If a hang
		// disappears with this, the GPU copy was stale (a CPU write went unnoticed by the tracker).
		static const bool reupload = std::getenv("KYTY_DUMP_CS_REUPLOAD") != nullptr;
		for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
			const auto r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
			const auto base = r.Base48();
			const auto size = BufferDescriptorSize(r);
			if (base == 0 || size == 0 || size > (1u << 20) || program.info.buffers[i].written ||
			    cache.IsRegionGpuModified(base, size)) {
				continue;
			}
			std::vector<uint32_t> words(size / 4);
			uint32_t              sum = 0;
			if (Libs::LibKernel::Memory::TryReadBacking(base, words.data(), words.size() * 4)) {
				for (const auto w: words) {
					sum = sum * 31u + w;
				}
			}
			LOGF("  DumpCS buffer[%u] cpu checksum=0x%08x%s dwords[0:4]=%08x %08x %08x %08x\n", i,
			     sum, reupload ? " (re-uploaded)" : "", words.size() > 0 ? words[0] : 0u,
			     words.size() > 1 ? words[1] : 0u, words.size() > 2 ? words[2] : 0u,
			     words.size() > 3 ? words[3] : 0u);
			if (words.size() >= 4472) {
				LOGF("  DumpCS buffer[%u] cpu dwords[4468:4472]=%08x %08x %08x %08x\n", i,
				     words[4468], words[4469], words[4470], words[4471]);
			}
			if (reupload) {
				cache.InvalidateMemory(base, size);
			}
		}
		// Save the CPU copy of every small buffer binding (constants) of the first two dumped
		// dispatches to _dumpcpu_<hash>_<binding>_<n>.bin for offline inspection.
		{
			static std::atomic<uint32_t> cpu_dump_count {0};
			const auto snapshot = cpu_dump_count.fetch_add(1, std::memory_order_relaxed);
			if (snapshot < 2) {
				for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
					const auto r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
					const auto base = r.Base48();
					const auto size = BufferDescriptorSize(r);
					if (base == 0 || size == 0 || size > (64u << 10)) {
						continue;
					}
					std::vector<uint8_t> bytes(size);
					if (!Libs::LibKernel::Memory::TryReadBacking(base, bytes.data(), size)) {
						continue;
					}
					const auto name =
					    fmt::format("_dumpcpu_{:016x}_{}_{}.bin", program.shader_hash, i, snapshot);
					if (FILE* f = std::fopen(name.c_str(), "wb"); f != nullptr) {
						std::fwrite(bytes.data(), 1, bytes.size(), f);
						std::fclose(f);
					}
				}
			}
		}
		// KYTY_DUMP_CS_READBACK=1: download the GPU contents of every GPU-written buffer binding
		// before the dispatch, summarize it as a linked-list node array ({payload, next} records)
		// and save the first two snapshots to _dump_<hash>_<binding>.bin for offline analysis.
		static const bool readback = std::getenv("KYTY_DUMP_CS_READBACK") != nullptr;
		if (readback) {
			static std::atomic<uint32_t> readback_count {0};
			const auto snapshot = readback_count.fetch_add(1, std::memory_order_relaxed);
			for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
				const auto r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
				const auto base = r.Base48();
				const auto size = std::min<uint64_t>(BufferDescriptorSize(r), 32ull << 20);
				if (base == 0 || size < 8 || !cache.IsRegionGpuModified(base, size)) {
					continue;
				}
				cache.ReadMemory(base, size);
				std::vector<uint32_t> words(size / 4);
				if (!Libs::LibKernel::Memory::TryReadBacking(base, words.data(), words.size() * 4)) {
					LOGF("  DumpCS readback buffer[%u]: unreadable\n", i);
					continue;
				}
				const uint32_t dwords  = std::max<uint32_t>(r.Stride() / 4, 1u);
				const uint64_t records = words.size() / dwords;
				uint64_t nonzero = 0, self_loops = 0, out_of_range = 0, max_next = 0, printed = 0;
				for (uint64_t rec = 0; rec < records; rec++) {
					bool nz = false;
					for (uint32_t d = 0; d < dwords; d++) {
						nz = nz || words[rec * dwords + d] != 0;
					}
					if (!nz) {
						continue;
					}
					nonzero++;
					if (dwords >= 2) {
						const auto next = words[rec * dwords + 1];
						self_loops += next == rec ? 1 : 0;
						out_of_range += next >= records ? 1 : 0;
						max_next = std::max<uint64_t>(max_next, next);
					}
					if (printed < 8) {
						printed++;
						LOGF("    record[%" PRIu64 "]: %08x %08x %08x\n", rec, words[rec * dwords],
						     dwords > 1 ? words[rec * dwords + 1] : 0u,
						     dwords > 2 ? words[rec * dwords + 2] : 0u);
					}
				}
				// Linked-list cycle search: follow `next` (dword 1) from every nonzero record.
				uint64_t cycles = 0, longest = 0, first_cycle_node = UINT64_MAX;
				if (dwords >= 2 && records <= (4u << 20)) {
					std::vector<uint8_t> state(records, 0); // 0 new, 1 on path, 2 done
					std::vector<uint32_t> path;
					for (uint64_t start = 0; start < records; start++) {
						if (state[start] != 0) {
							continue;
						}
						bool nz = false;
						for (uint32_t d = 0; d < dwords; d++) {
							nz = nz || words[start * dwords + d] != 0;
						}
						if (!nz) {
							continue;
						}
						path.clear();
						uint64_t cur = start;
						while (cur != 0 && cur < records && state[cur] == 0) {
							state[cur] = 1;
							path.push_back(static_cast<uint32_t>(cur));
							cur = words[cur * dwords + 1];
						}
						if (cur != 0 && cur < records && state[cur] == 1) {
							cycles++;
							if (first_cycle_node == UINT64_MAX) {
								first_cycle_node = cur;
							}
						}
						longest = std::max<uint64_t>(longest, path.size());
						for (const auto p: path) {
							state[p] = 2;
						}
					}
				}
				LOGF("  DumpCS readback buffer[%u]: addr=0x%012" PRIx64 " size=0x%" PRIx64
				     " stride=%u records=%" PRIu64 " nonzero=%" PRIu64 " self_loops=%" PRIu64
				     " next_out_of_range=%" PRIu64 " max_next=%" PRIu64 " cycles=%" PRIu64
				     " first_cycle_node=%" PRIu64 " longest_chain=%" PRIu64 "\n",
				     i, base, size, r.Stride(), records, nonzero, self_loops, out_of_range, max_next,
				     cycles, first_cycle_node, longest);
				const auto name = fmt::format("_dump_{:016x}_{}_{}.bin", program.shader_hash, i,
				                              snapshot < 2 ? std::to_string(snapshot) : "latest");
				if (FILE* f = std::fopen(name.c_str(), "wb"); f != nullptr) {
					std::fwrite(words.data(), 4, words.size(), f);
					std::fclose(f);
				}
			}
		}
		if (indirect_args_addr != 0) {
			uint32_t args[3] {};
			const bool readable = Libs::LibKernel::Memory::TryReadBacking(indirect_args_addr, args, sizeof(args));
			LOGF("  DumpCS indirect args at 0x%016" PRIx64 ": %s%u,%u,%u gpu_modified=%d "
			     "cpu_modified=%d gpu_dirty=%d\n",
			     indirect_args_addr, readable ? "" : "(unreadable) ", args[0], args[1], args[2],
			     cache.IsRegionGpuModified(indirect_args_addr, sizeof(args)) ? 1 : 0,
			     cache.IsRegionCpuModified(indirect_args_addr, sizeof(args)) ? 1 : 0,
			     cache.HasGpuDirtyBytes(indirect_args_addr, sizeof(args)) ? 1 : 0);
		}
	}

	if (indirect && use_thread_dimensions) {
		// Converting thread counts to group counts on the GPU is not implemented; fall back to
		// the CPU view of the arguments.
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 8) {
			LOGF("GraphicsRenderDispatchDirect: indirect dispatch with thread dimensions uses the "
			     "CPU view of args at 0x%016" PRIx64 "\n",
			     indirect_args_addr);
		}
		indirect = false;
	}
	if (use_thread_dimensions) {
		auto groups_from_threads = [](uint32_t threads, uint32_t group_size) {
			return (threads == 0
			            ? 0u
			            : (threads + std::max(group_size, 1u) - 1u) / std::max(group_size, 1u));
		};

		const uint32_t old_x = thread_group_x;
		const uint32_t old_y = thread_group_y;
		const uint32_t old_z = thread_group_z;
		thread_group_x       = groups_from_threads(thread_group_x, cs_regs.cs_regs.num_thread_x);
		thread_group_y       = groups_from_threads(thread_group_y, cs_regs.cs_regs.num_thread_y);
		thread_group_z       = groups_from_threads(thread_group_z, cs_regs.cs_regs.num_thread_z);

		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("GraphicsRenderDispatchDirect: use-thread-dimensions %ux%ux%u / %ux%ux%u -> "
			     "groups %ux%ux%u\n",
			     old_x, old_y, old_z, std::max(cs_regs.cs_regs.num_thread_x, 1u),
			     std::max(cs_regs.cs_regs.num_thread_y, 1u),
			     std::max(cs_regs.cs_regs.num_thread_z, 1u), thread_group_x, thread_group_y,
			     thread_group_z);
		}
	}

	if (!indirect && (thread_group_x == 0 || thread_group_y == 0 || thread_group_z == 0)) {
		static std::atomic<uint32_t> log_count {0};
		if (log_count.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("GraphicsRenderDispatchDirect: skipping zero-sized dispatch groups=%ux%ux%u "
			     "mode=0x%08" PRIx32 " shader=0x%016" PRIx64 "\n",
			     thread_group_x, thread_group_y, thread_group_z, mode,
			     sh_ctx.GetCs().cs_regs.data_addr);
		}
		return;
	}

	buffer.EndRendering();
	auto& pipeline =
	    m_context.GetPipelineCache().CreateComputePipeline(input_info, compute_program);
	auto bindings = PrepareBindings(input_info.stage);
	FindBuffers(bindings);
	if (program.info.uses_dma) {
		m_context.GetGpuResources().PrepareBda();
	}
	RebindBuffers(bindings);
	RebindImages(bindings);

	auto vk_buffer = buffer.Handle();

	// Indirect arguments: the triple is read by the GPU from the cached buffer that mirrors guest
	// memory, so results of the compute shader that produced it are used, not the stale CPU copy
	// (games fill unwritten memory with patterns like 0xDEADBEEF). The values still pass through
	// a sanitizing pass, because a producer whose stores were dropped (BDA page not cached yet)
	// leaves garbage counts that would hang the host GPU. Recorded before CommitBindings: the
	// sanitizer pushes its own descriptor set.
	vk::Buffer indirect_vk_buffer;
	uint64_t   indirect_vk_offset = 0;
	if (indirect) {
		constexpr uint64_t ArgsSize = 3u * sizeof(uint32_t);
		auto&              cache    = m_context.GetBufferCache();
		static std::atomic<uint32_t> indirect_log_count {0};
		if (indirect_log_count.fetch_add(1, std::memory_order_relaxed) < 96) {
			LOGF("GraphicsRenderDispatchDirect: indirect args at 0x%016" PRIx64
			     " cpu_view=%u,%u,%u gpu_modified=%d cpu_modified=%d gpu_dirty=%d shader=0x%016" PRIx64
			     "\n",
			     indirect_args_addr, thread_group_x, thread_group_y, thread_group_z,
			     cache.IsRegionGpuModified(indirect_args_addr, ArgsSize) ? 1 : 0,
			     cache.IsRegionCpuModified(indirect_args_addr, ArgsSize) ? 1 : 0,
			     cache.HasGpuDirtyBytes(indirect_args_addr, ArgsSize) ? 1 : 0, program.shader_hash);
		}
		auto [args_buffer, args_offset] = cache.ObtainBuffer(indirect_args_addr, ArgsSize, false);
		EXIT_IF(args_buffer == nullptr);
		static const bool sanitize = std::getenv("KYTY_NO_INDIRECT_SANITIZE") == nullptr;
		if (sanitize) {
			if (m_indirect_sanitizer == nullptr) {
				m_indirect_sanitizer = std::make_unique<IndirectArgsSanitizer>(
				    m_context.GetGraphics(), m_context.GetCommandScheduler());
			}
			std::tie(indirect_vk_buffer, indirect_vk_offset) =
			    m_indirect_sanitizer->Sanitize(vk_buffer, *args_buffer, args_offset);
		} else {
			indirect_vk_buffer = args_buffer->Handle();
			indirect_vk_offset = args_offset;
			VulkanMemoryBarrier barrier {};
			barrier.sType = vk::StructureType::eMemoryBarrier;
			barrier.srcAccessMask =
			    vk::AccessFlagBits::eShaderWrite | vk::AccessFlagBits::eTransferWrite;
			barrier.dstAccessMask = vk::AccessFlagBits::eIndirectCommandRead;
			vk_buffer.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
			                          vk::PipelineStageFlagBits::eDrawIndirect,
			                          vk::DependencyFlags {}, 1, &barrier, 0, nullptr, 0, nullptr);
		}
	}

	PreparedBindings* descriptor_stage = &bindings;
	CommitBindings(buffer, vk::PipelineBindPoint::eCompute, pipeline,
	               std::span {&descriptor_stage, 1u});
	bool has_storage_writes = HasShaderBufferWrites(input_info.stage);
	has_storage_writes =
	    std::any_of(program.info.images.begin(), program.info.images.end(),
	                [](const auto& image) {
		                return image.written &&
		                       image.resource_class ==
		                           ShaderRecompiler::IR::ImageResourceClass::Storage;
	                }) ||
	    has_storage_writes;
	if (has_storage_writes) {
		// A host fence used to serialize every dispatch. Preserve its read-before-write ordering
		// while allowing the queue to execute asynchronously.
		ShaderWriteHazardBarrier(vk_buffer, vk::PipelineStageFlagBits::eComputeShader);
	}
	vk_buffer.bindPipeline(vk::PipelineBindPoint::eCompute, pipeline.pipeline);
	if (indirect) {
		vk_buffer.dispatchIndirect(indirect_vk_buffer, indirect_vk_offset);
	} else {
		vk_buffer.dispatch(thread_group_x, thread_group_y, thread_group_z);
	}

	// The removed host fence also ordered read-only dispatches before later writers.
	ShaderAccessBarrier(vk_buffer, vk::PipelineStageFlagBits::eComputeShader);
	ResetBindings();
}

bool DebugDumpFrame(uint32_t frame) {
	struct Range {
		uint32_t first;
		uint32_t last;
	};
	static const std::vector<Range> ranges = [] {
		std::vector<Range> out;
		const char*        value = std::getenv("KYTY_DUMP_FRAME");
		if (value == nullptr) {
			return out;
		}
		std::string_view text(value);
		while (!text.empty()) {
			const auto comma = text.find(',');
			const auto item  = text.substr(0, comma);
			text             = comma == std::string_view::npos ? std::string_view {}
			                                                   : text.substr(comma + 1u);
			if (item.empty()) {
				continue;
			}
			const auto dash  = item.find('-');
			const auto first = static_cast<uint32_t>(std::strtoul(std::string(item.substr(0, dash)).c_str(), nullptr, 10));
			const auto last  = dash == std::string_view::npos
			                       ? first
			                       : static_cast<uint32_t>(std::strtoul(std::string(item.substr(dash + 1u)).c_str(), nullptr, 10));
			out.push_back({first, last});
		}
		return out;
	}();
	for (const auto& range: ranges) {
		if (frame >= range.first && frame <= range.last) {
			return true;
		}
	}
	return false;
}

uint64_t DebugDumpAddress() {
	static const uint64_t dump_addr = [] {
		const char* value = std::getenv("KYTY_DUMP_ADDR");
		return value != nullptr ? std::strtoull(value, nullptr, 16) : uint64_t {0};
	}();
	return dump_addr;
}

const std::vector<uint64_t>& DebugDumpAddresses() {
	static const std::vector<uint64_t> addresses = [] {
		std::vector<uint64_t> list;
		const char*           value = std::getenv("KYTY_DUMP_ADDRS");
		while (value != nullptr && *value != 0) {
			char*      end  = nullptr;
			const auto addr = std::strtoull(value, &end, 16);
			if (end == value) {
				break;
			}
			if (addr != 0) {
				list.push_back(addr);
			}
			value = (*end == ',') ? end + 1 : end;
		}
		return list;
	}();
	return addresses;
}

bool ShaderStageTouchesAnyBuffer(const ShaderStageRuntime& stage,
                                 const std::vector<uint64_t>& addresses) {
	if (!stage || addresses.empty()) {
		return false;
	}
	const auto& program   = *stage.program;
	const auto& resources = stage.resources;
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		const auto r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
		const auto base = r.Base48();
		const auto size = BufferDescriptorSize(r);
		if (base == 0) {
			continue;
		}
		for (const auto address: addresses) {
			if (address >= base && address < base + size) {
				return true;
			}
		}
	}
	return false;
}

bool ShaderStageTouchesAddress(const ShaderStageRuntime& stage, uint64_t address) {
	if (!stage || address == 0) {
		return false;
	}
	const auto& program   = *stage.program;
	const auto& resources = stage.resources;
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		const auto r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
		const auto base = r.Base48();
		const auto size = BufferDescriptorSize(r);
		if (base != 0 && address >= base && address < base + size) {
			return true;
		}
	}
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		const auto r    = DecodeNativeDescriptor<ShaderTextureResource>(resources.images[i]);
		const auto base = r.Base40();
		constexpr uint64_t ImageSpan = 64ull * 1024 * 1024; // extent unknown here; generous
		if (base != 0 && address >= base && address < base + ImageSpan) {
			return true;
		}
	}
	return false;
}

void DumpShaderStageBindings(RenderContext& context, const char* label,
                             const ShaderStageRuntime& stage) {
	if (!stage) {
		return;
	}
	const auto& program   = *stage.program;
	const auto& resources = stage.resources;
	auto&       cache     = context.GetBufferCache();
	LOGF("  Dump%s: shader=0x%016" PRIx64 " buffers=%zu images=%zu uses_dma=%d\n", label,
	     program.shader_hash, program.info.buffers.size(), program.info.images.size(),
	     program.info.uses_dma ? 1 : 0);
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		const auto& res  = program.info.buffers[i];
		const auto  r    = DecodeNativeDescriptor<ShaderBufferResource>(resources.buffers[i]);
		const auto  base = r.Base48();
		const auto  size = BufferDescriptorSize(r);
		LOGF("  Dump%s buffer[%u]: source=%u usage=%s addr=0x%012" PRIx64 " stride=%u records=%u "
		     "size=0x%" PRIx64 " gpu_modified=%d cpu_modified=%d\n",
		     label, i, res.source, res.written ? "read-write" : "read-only", base, r.Stride(),
		     r.NumRecords(), size,
		     (base != 0 && size != 0 && cache.IsRegionGpuModified(base, size)) ? 1 : 0,
		     (base != 0 && size != 0 && cache.IsRegionCpuModified(base, size)) ? 1 : 0);
	}
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		const auto& image = program.info.images[i];
		const auto  r     = DecodeNativeDescriptor<ShaderTextureResource>(resources.images[i]);
		const uint64_t probe_size =
		    static_cast<uint64_t>(static_cast<uint32_t>(r.Width5()) + 1u) *
		    (static_cast<uint32_t>(r.Height5()) + 1u) *
		    std::max<uint32_t>(Prospero::NumBytesPerElement(r.Format()), 1u);
		const bool probe = r.Base40() != 0 && probe_size != 0;
		LOGF("  Dump%s image[%u]: source=%u usage=%s class=%s addr=0x%010" PRIx64
		     " type=%u fmt=%u extent=%ux%u depth=%u tile=%u dstsel=0x%03x levels=%u..%u"
		     " maxmip=%u pitch=%u meta=0x%010" PRIx64 " dcc=%d gpu_modified=%d cpu_modified=%d"
		     " gpu_dirty=%d\n",
		     label, i, image.source, image.written ? "read-write" : "read-only",
		     image.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled ? "sampled"
		                                                                               : "storage",
		     r.Base40(), static_cast<uint32_t>(r.Type()), static_cast<uint32_t>(r.Format()),
		     static_cast<uint32_t>(r.Width5()) + 1u, static_cast<uint32_t>(r.Height5()) + 1u,
		     static_cast<uint32_t>(r.Depth()) + 1u, static_cast<uint32_t>(r.TileMode()),
		     r.DstSelXYZW(), static_cast<uint32_t>(r.BaseLevel()),
		     static_cast<uint32_t>(r.LastLevel()), static_cast<uint32_t>(r.MaxMip()),
		     static_cast<uint32_t>(r.ArrayPitch()), r.MetaAddr() << 8u,
		     r.MetaCompress() ? 1 : 0,
		     probe && cache.IsRegionGpuModified(r.Base40(), probe_size) ? 1 : 0,
		     probe && cache.IsRegionCpuModified(r.Base40(), probe_size) ? 1 : 0,
		     probe && cache.HasGpuDirtyBytes(r.Base40(), probe_size) ? 1 : 0);
	}
	for (uint32_t i = 0; i < program.info.samplers.size() && i < resources.samplers.size(); i++) {
		const auto r = DecodeNativeDescriptor<ShaderSamplerResource>(resources.samplers[i]);
		LOGF("  Dump%s sampler[%u]: source=%u raw=%08x %08x %08x %08x clamp=%u/%u/%u filter=%u/%u z=%u"
		     " mip=%u aniso=%u/%u/%u lod=%u..%u bias=%u/%u unorm_coords=%d force_srgb=%d"
		     " trunc=%d filter_mode=%u depth_cmp=%u border=%u/%u disable_degamma=%d\n",
		     label, i, program.info.samplers[i].source, r.fields[0], r.fields[1], r.fields[2],
		     r.fields[3], static_cast<uint32_t>(r.ClampX()), static_cast<uint32_t>(r.ClampY()),
		     static_cast<uint32_t>(r.ClampZ()), static_cast<uint32_t>(r.XyMagFilter()),
		     static_cast<uint32_t>(r.XyMinFilter()), static_cast<uint32_t>(r.ZFilter()),
		     static_cast<uint32_t>(r.MipFilter()), static_cast<uint32_t>(r.MaxAnisoRatio()),
		     static_cast<uint32_t>(r.AnisoThreshold()), static_cast<uint32_t>(r.AnisoBias()),
		     static_cast<uint32_t>(r.MinLod()), static_cast<uint32_t>(r.MaxLod()),
		     static_cast<uint32_t>(r.LodBias()), static_cast<uint32_t>(r.LodBiasSec()),
		     r.ForceUnormCoords() ? 1 : 0, r.ForceSrgb() ? 1 : 0, r.TruncCoord() ? 1 : 0,
		     static_cast<uint32_t>(r.FilterMode()), static_cast<uint32_t>(r.DepthCompareFunc()),
		     static_cast<uint32_t>(r.BorderColorPtr()), static_cast<uint32_t>(r.BorderColorType()),
		     r.DisableDegamma() ? 1 : 0);
	}
}

} // namespace Libs::Graphics
