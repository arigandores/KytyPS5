#include "graphics/host_gpu/renderer/pipeline/descriptors.h"

#include "common/gates.h"

#include <mutex>
#include <unordered_set>
#include "common/alignment.h"
#include "common/frameStats.h"
#include "graphics/host_gpu/lodStats.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/gpuCheckpoints.h"
#include "graphics/host_gpu/renderer/renderMemo.h"
#include "graphics/host_gpu/renderer/shadowResolve.h"

#include "common/assert.h"
#include "common/drawStat.h"
#include "common/common.h"
#include "common/file.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "common/stringUtils.h"
#include "common/threads.h"
#include "graphics/guest_gpu/gpu_defs.h"
#include "graphics/guest_gpu/gpu_format.h"
#include "graphics/guest_gpu/graphicsRun.h"
#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/guest_gpu/tile.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/hostMemory.h"
#include "graphics/host_gpu/renderer/debug.h"
#include "graphics/host_gpu/renderer/image/imageView.h"
#include "graphics/host_gpu/renderer/image/textureCommon.h"
#include "graphics/host_gpu/renderer/pipeline/shaderResourceBarrier.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/recompiler/ir/passes/BindingLayout.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"
#include "graphics/shader/shader.h"
#include "kernel/memory.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <bit>
#include <fmt/format.h>
#include <limits>
#include <mutex>
#include <span>
#include <vector>

#ifdef min
#undef min
#endif
#ifdef max
#undef max
#endif

namespace Libs::Graphics {

namespace {

using BindingKind = ShaderRecompiler::IR::DescriptorBindingKind;

// KYTY_CBUFFER_DIRECT_COPY, switchable during a run through the shared gate file so that one
// gameplay run can compare the direct copy against the ObtainBuffer path on the same scene.
bool DirectConstantCopyEnabled() {
	return Common::Gates::Enabled(Common::Gates::Gate::ConstantCopy);
}

} // namespace

vk::DescriptorType NativeDescriptorType(BindingKind kind) {
	const auto image_class = ShaderRecompiler::IR::ImageBindingResourceClass(kind);
	if (image_class == ShaderRecompiler::IR::ImageResourceClass::Sampled) {
		return vk::DescriptorType::eSampledImage;
	}
	if (image_class == ShaderRecompiler::IR::ImageResourceClass::Storage) {
		return vk::DescriptorType::eStorageImage;
	}
	switch (kind) {
		case BindingKind::Samplers: return vk::DescriptorType::eSampler;
		case BindingKind::Buffers:
		case BindingKind::Gds:
		case BindingKind::BdaPagetable:
		case BindingKind::FaultBuffer:
		case BindingKind::FlattenedSrt:
		case BindingKind::ShaderData: return vk::DescriptorType::eStorageBuffer;
		case BindingKind::ConstBuffers: return vk::DescriptorType::eUniformBuffer;
		case BindingKind::Count: EXIT("invalid native descriptor binding kind");
	}
	EXIT("invalid native descriptor binding kind");
}

uint32_t NativeDescriptorCount(const ShaderRecompiler::IR::DescriptorBinding& binding) {
	return binding.resources.empty() ? 1u : static_cast<uint32_t>(binding.resources.size());
}

vk::DescriptorImageInfo MakeImageInfo(const TextureBinding& texture, uint32_t element) {
	vk::ImageView view = nullptr;
	if (texture.mip_views.empty()) {
		if (element == 0u) {
			view = texture.image_view;
		}
	} else if (element < texture.mip_views.size()) {
		view = texture.mip_views[element];
	}
	EXIT_IF(!texture.image_id || view == nullptr || texture.layout == vk::ImageLayout::eUndefined);
	return {nullptr, view, texture.layout};
}

static const char* ShaderStageResourceName(ShaderType stage) {
	switch (stage) {
		case ShaderType::Vertex: return "Vertex";
		case ShaderType::Mesh: return "Mesh";
		case ShaderType::Local: return "Local";
		case ShaderType::TessellationControl: return "Hull";
		case ShaderType::TessellationEvaluation: return "Domain";
		case ShaderType::Pixel: return "Pixel";
		case ShaderType::Compute: return "Compute";
		default: return "Unknown";
	}
}

static Prospero::ImageType TextureType(const ShaderTextureResource& descriptor) {
	const auto type = descriptor.Type();
	return type == Prospero::ImageType::kCube ? Prospero::ImageType::kColor2DArray : type;
}

static Prospero::ImageType TextureBaseType(Prospero::ImageType type) {
	switch (type) {
		case Prospero::ImageType::kColor1DArray: return Prospero::ImageType::kColor1D;
		case Prospero::ImageType::kColor2DArray:
		case Prospero::ImageType::kColor2DMsaa:
		case Prospero::ImageType::kColor2DMsaaArray: return Prospero::ImageType::kColor2D;
		default: return type;
	}
}

static bool IsMultisampledTexture(Prospero::ImageType type) {
	return type == Prospero::ImageType::kColor2DMsaa ||
	       type == Prospero::ImageType::kColor2DMsaaArray;
}

static vk::DescriptorBufferInfo
NativeStorageBuffer(RenderContext& context, const PreparedBindings::BufferSource& source,
                    const ShaderRecompiler::IR::BufferResource& resource, ShaderType stage,
                    uint32_t slot, uint32_t& buffer_offset, bool direct_copy,
                    uint8_t& buffer_class) {
	Common::FrameStats::Scope binding_scope(Common::FrameStats::Counter::BindBuffersNs);
	// Session 93, gate "bdacap" (MEASUREMENT ONLY, pred/01_bdacap.md).  The gate is the
	// FIRST operand of the &&, is read ONCE per call, and is read BEFORE cap_t0, so the
	// read lies OUTSIDE the interval it arms: at bdacap = 0 not one NowNs() and not one Add
	// below is executed and buffer_class stays None.  Enabled() and NOT TimingsEnabled(),
	// because a measurement run is KYTY_FRAME_TRACE=lite, where the Scope above records no
	// nanoseconds at all.  Nothing here feeds a value, a decision or a side effect: the
	// descriptor this function returns is byte for byte the same at either setting.
	const bool     cap    = Common::Gates::Enabled(Common::Gates::Gate::BdaCap) &&
	                        Common::FrameStats::Enabled();
	const uint64_t cap_t0 = cap ? Common::FrameStats::NowNs() : 0;
	buffer_class          = static_cast<uint8_t>(BdaCapClass::None);
	// Called exactly once on every path that RETURNS, so bc_null + bc_fmt + bc_cb +
	// bc_ring + bc_ok is the number of calls (control A2).  The EXIT() sites abort the
	// process and do not return, so they need no class.
	const auto cap_note = [cap, cap_t0, &buffer_class, &resource](BdaCapClass cls,
	                                                                uint64_t    bytes) {
		if (!cap) {
			return;
		}
		buffer_class     = static_cast<uint8_t>(cls);
		const auto    ns = Common::FrameStats::NowNs() - cap_t0;
		auto          which = Common::FrameStats::Counter::BdaCapOk;
		switch (cls) {
			case BdaCapClass::Null: which = Common::FrameStats::Counter::BdaCapNull; break;
			case BdaCapClass::Formatted:
				which = Common::FrameStats::Counter::BdaCapFormatted;
				break;
			case BdaCapClass::ConstBank:
				which = Common::FrameStats::Counter::BdaCapConstBank;
				break;
			case BdaCapClass::Ring: which = Common::FrameStats::Counter::BdaCapRing; break;
			default: break;
		}
		Common::FrameStats::Add(which, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapAllNs, ns);
		if (cls == BdaCapClass::Ok) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapOkNs, ns);
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapOkBytes, bytes);
		}
		// Session 94: the const-bank slots' own time (bc_cb_ns) -- the 58 % of all buffer
		// slots that BDA cannot express get a measured binding price of their own.
		if (cls == BdaCapClass::ConstBank) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapConstBankNs, ns);
		}
		// Session 94: the bc_ok slots a shader WRITES (or updates atomically) cannot move onto
		// BDA -- there is no store path -- yet s93's Ceiling_bind counted them.
		if (cls == BdaCapClass::Ok && (resource.written || resource.atomic)) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapOkWritten, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapOkWrittenNs, ns);
		}
	};
	buffer_offset = 0;

	const auto& [address, size, id] = source;
	if (address == 0 || size == 0) {
		cap_note(BdaCapClass::Null, 0);
		return {context.GetBufferCache().GetBuffer(NULL_BUFFER_ID).Handle(), 0, 16};
	}
	const auto& graphics   = context.GetGraphics();
	const bool  const_bank = ShaderRecompiler::IR::PackedStrideConstBank(resource.packed_stride);
	// Session 93, gate "bdacap": the class of every return BELOW the null one.  First match
	// wins -- formatted and const-bank are decided AHEAD of the ring, because neither can be
	// expressed through a device address wherever its bytes happen to live.
	const auto cap_class = [&resource, const_bank](bool ring) {
		if (resource.formatted) {
			return BdaCapClass::Formatted;
		}
		if (const_bank) {
			return BdaCapClass::ConstBank;
		}
		return ring ? BdaCapClass::Ring : BdaCapClass::Ok;
	};
	// Const-bank V#s are also bound as uniform buffers: align the range start to
	// minUniformBufferOffsetAlignment (64 on NVIDIA; a multiple of the storage alignment, so the
	// adjustment stays a multiple of the specialized base alignment).
	const auto alignment =
	    const_bank ? std::max<vk::DeviceSize>(
	                     graphics.StorageMinAlignment(),
	                     graphics.GetPhysicalDeviceProperties().limits.minUniformBufferOffsetAlignment)
	               : graphics.StorageMinAlignment();
	if (alignment == 0 ||
	    size > graphics.GetPhysicalDeviceProperties().limits.maxStorageBufferRange) {
		EXIT("storage buffer range or device alignment is unsupported\n");
	}
	if (direct_copy && !resource.written && !resource.formatted && (address & 3u) == 0 &&
	    ShaderRecompiler::IR::PackedStrideAlignedCopy(resource.packed_stride) &&
	    address % ShaderRecompiler::IR::PackedStrideBaseAlignment(resource.packed_stride) != 0) {
		auto& cache = context.GetBufferCache();
		if (!cache.IsRegionGpuModifiedFromGpu(address, size) && !cache.HasGpuDirtyBytes(address, size) &&
		    cache.TouchReadOnlyBuffer(id, address, size)) {
			// This read-only binding needs an aligned copy anyway. Prepare that final
			// copy directly, keeping the ordinary buffer's dirty bits intact for any
			// later BDA/descriptor use. GPU-owned data follows ObtainBuffer below.
			if (const_bank && size > graphics.GetPhysicalDeviceProperties().limits.maxUniformBufferRange) {
				EXIT("const-bank copy exceeds maxUniformBufferRange\n");
			}
			auto& stream = cache.GetUtilityBuffer(MemoryUsage::Stream);
			const auto copy_t0 = Common::FrameStats::TimingsEnabled() ? Common::FrameStats::NowNs() : 0;
			auto [data, stream_offset] = stream.Map(size, alignment);
			EXIT_IF(data == nullptr);
			if (!Libs::LibKernel::Memory::TryReadBacking(address, data, size)) {
				EXIT("storage buffer slot %u: direct const-bank source is unreadable\n", slot);
			}
			stream.Commit();
			if (copy_t0 != 0) {
				Common::FrameStats::Add(Common::FrameStats::Counter::CbankCopyNs,
				                        Common::FrameStats::NowNs() - copy_t0);
			}
			if (Common::Gates::Enabled(Common::Gates::Gate::CbStat)) [[unlikely]] {
				cache.NoteStreamCopy(address, size, stream_offset);
			}
			if (Common::FrameStats::Enabled()) {
				Common::FrameStats::Add(Common::FrameStats::Counter::CbankCopyCpu, 1);
				Common::FrameStats::Add(Common::FrameStats::Counter::CbankCopyBytes, size);
			}
			// Session 93, gate "bdacap": ring return 1 of 3 - the direct const-bank copy.
			cap_note(cap_class(true), size);
			return {stream.Handle(), stream_offset, size};
		}
	}
	// The last argument (gate "buffast"): this binding asks for the same range every draw.
	auto [buffer, offset] = context.GetBufferCache().ObtainBuffer(address, size, resource.written,
	                                                              resource.formatted, id, true);
	const auto aligned_offset = Common::AlignDown(offset, alignment);
	const auto adjustment     = offset - aligned_offset;
	const auto max_range      = graphics.GetPhysicalDeviceProperties().limits.maxStorageBufferRange;
	if (adjustment % sizeof(uint32_t) != 0 || adjustment >= 256 || size > max_range - adjustment) {
		EXIT("storage buffer offset adjustment is unsupported\n");
	}
	buffer_offset = static_cast<uint32_t>(adjustment);
	if (adjustment % ShaderRecompiler::IR::PackedStrideBaseAlignment(resource.packed_stride) != 0) {
		if (ShaderRecompiler::IR::PackedStrideAlignedCopy(resource.packed_stride)) {
			// The shader was specialized as 16-byte aligned (KYTY_CBANK_COPY): present the range
			// through an aligned copy in the stream ring. CPU-written constants (the common case)
			// are copied from guest memory; a range the GPU wrote is copied on the GPU.
			auto&      cache  = context.GetBufferCache();
			auto&      stream = cache.GetUtilityBuffer(MemoryUsage::Stream);
			const bool gpu = cache.IsRegionGpuModifiedFromGpu(address, size) ||
			                 cache.HasGpuDirtyBytes(address, size);
			const auto copy_t0 = Common::FrameStats::TimingsEnabled() ? Common::FrameStats::NowNs() : 0;
			auto [data, stream_offset] = stream.Map(size, alignment);
			EXIT_IF(data == nullptr);
			if (!gpu) {
				if (!Libs::LibKernel::Memory::TryReadBacking(address, data, size)) {
					EXIT("storage buffer slot %u: const-bank copy source 0x%016llx+0x%llx is unreadable\n",
					     slot, static_cast<unsigned long long>(address), static_cast<unsigned long long>(size));
				}
			}
			stream.Commit();
			if (!gpu && copy_t0 != 0) {
				Common::FrameStats::Add(Common::FrameStats::Counter::CbankCopyNs,
				                        Common::FrameStats::NowNs() - copy_t0);
			}
			if (!gpu && Common::Gates::Enabled(Common::Gates::Gate::CbStat)) [[unlikely]] {
				cache.NoteStreamCopy(address, size, stream_offset);
			}
			if (gpu) {
				auto& command = context.GetCommandScheduler().Current();
				stream.CopyFrom(command, *buffer, offset, stream_offset, size,
				                vk::AccessFlagBits::eShaderWrite | vk::AccessFlagBits::eTransferWrite,
				                vk::AccessFlagBits::eHostWrite, vk::AccessFlagBits::eShaderRead,
				                vk::AccessFlagBits::eUniformRead | vk::AccessFlagBits::eShaderRead);
			}
			if (Common::FrameStats::Enabled()) {
				Common::FrameStats::Add(gpu ? Common::FrameStats::Counter::CbankCopyGpu
				                            : Common::FrameStats::Counter::CbankCopyCpu,
				                        1);
				Common::FrameStats::Add(Common::FrameStats::Counter::CbankCopyBytes, size);
			}
			buffer_offset = 0;
			// Session 93, gate "bdacap": ring return 2 of 3 - the aligned const-bank copy.
			cap_note(cap_class(true), size);
			return {stream.Handle(), stream_offset, size};
		}
		// The shader was specialized on the V# base alignment (uvec2/uvec4 constant loads).
		EXIT("storage buffer slot %u: bound offset adjustment %u breaks the specialized base alignment %u\n",
		     slot, buffer_offset,
		     ShaderRecompiler::IR::PackedStrideBaseAlignment(resource.packed_stride));
	}
	const vk::DescriptorBufferInfo result {buffer->Handle(), aligned_offset, size + adjustment};
	if (const_bank &&
	    result.range > graphics.GetPhysicalDeviceProperties().limits.maxUniformBufferRange) {
		EXIT("storage buffer slot %u: const-bank range 0x%llx exceeds maxUniformBufferRange\n", slot,
		     static_cast<unsigned long long>(result.range));
	}
	// Upstream 01df42a widened this from "resource.formatted && resource.written" to every
	// written range. Its own reason -- reaching the content-based DCC metadata invalidation
	// (InvalidateDccMetadata) it added to InvalidateMemoryFromGPU -- does NOT apply here: this
	// merge kept our PendingDcc tracking and rejected that rework, so no metadata state is
	// touched by this call at all. What is left is the image half: InvalidateMemoryFromGPU marks
	// every image overlapping the range buffer-modified, so a plain (unformatted) storage write
	// into memory an image is built from is not read back later as stale texels. The widening is
	// kept because it can only cost an extra image upload, while the narrow condition can hand a
	// draw stale contents; it is also pure cost for the (common) writes that alias no image.
	if (resource.written) {
		context.GetTextureCache().InvalidateMemoryFromGPU(address, size);
	}
	const char* access = "Read";
	if (resource.written && resource.read) {
		access = "ReadWrite";
	} else if (resource.written) {
		access = "Write";
	}
	SetVulkanObjectNameF(
	    graphics.device, result.buffer,
	    "Kyty.{}.StorageBuffer[slot={} guest=0x{:016x} size=0x{:x} access={} formatted={}]",
	    ShaderStageResourceName(stage), slot, address, size, access, resource.formatted);
	// Session 93, gate "bdacap": the last return, and the THIRD ring path - ObtainBuffer can
	// hand back the stream ring itself (bufferCache.cpp:1314), which no local flag records,
	// so the handle is compared with the ring's exactly as the slotstat buf_ring column does.
	// The comparison sits behind `cap`, so it is not made at bdacap = 0.
	const bool cap_ring = cap && result.buffer == context.GetBufferCache()
	                                                  .GetUtilityBuffer(MemoryUsage::Stream)
	                                                  .Handle();
	cap_note(cap_class(cap_ring), size);
	return result;
}

bool IsSupportedDepthTextureEncoding(const ShaderTextureResource& descriptor, bool r128) {
	constexpr uint32_t field1_reserved_mask = 0x200fff00u;
	constexpr uint32_t field2_reserved_mask = 0xf0003000u;
	const uint32_t     field3_expected = descriptor.DstSelXYZW() |
	                                     (static_cast<uint32_t>(descriptor.BaseLevel()) << 12u) |
	                                     (static_cast<uint32_t>(descriptor.LastLevel()) << 16u) |
	                                     (static_cast<uint32_t>(descriptor.TileMode()) << 20u) |
	                                     (static_cast<uint32_t>(descriptor.Type()) << 28u);
	const uint32_t     field4_expected = descriptor.Depth() | (descriptor.BaseArray5() << 16u);
	const uint32_t     field5_expected = (static_cast<uint32_t>(descriptor.PerfMod5()) << 20u) |
	                                     (static_cast<uint32_t>(descriptor.MaxMip()) << 4u);
	const bool         common          = (descriptor.fields[1] & field1_reserved_mask) == 0 &&
	                                     (descriptor.fields[2] & field2_reserved_mask) == 0 &&
	                                     descriptor.fields[3] == field3_expected;
	if (r128) {
		return common && descriptor.fields[4] == 0 && descriptor.fields[5] == 0 &&
		       descriptor.fields[6] == 0 && descriptor.fields[7] == 0;
	}
	const bool full = common && descriptor.fields[4] == field4_expected &&
	                  descriptor.fields[5] == field5_expected;
	if (!full || (descriptor.fields[6] == 0 && descriptor.fields[7] != 0) ||
	    (descriptor.MsaaDepth() && !IsMultisampledTexture(descriptor.Type()))) {
		return false;
	}
	if (descriptor.fields[6] == 0) {
		return true;
	}
	constexpr uint32_t htile_control = 0x00280000u;
	const uint32_t expected_control  = htile_control | (descriptor.MsaaDepth() ? (1u << 10u) : 0u);
	const auto     metadata_addr     = descriptor.MetaAddr() << 8u;
	return (descriptor.fields[6] & 0x00ffffffu) == expected_control && metadata_addr != 0 &&
	       metadata_addr < TRACKER_ADDRESS_SIZE && (metadata_addr & 0x7fffu) == 0 &&
	       descriptor.TileMode() == Prospero::TileMode::kDepth;
}

static void ValidateSampledDepthBinding(const ShaderRecompiler::IR::ImageResource& resource,
                                        const ShaderTextureResource& descriptor, const Image& image,
                                        vk::Format view_format, uint64_t size) {
	const bool resource_ok = IsSupportedSampledDepthResource(resource);
	const bool encoding_ok = IsSupportedDepthTextureEncoding(descriptor, resource.r128);
	const bool view_ok =
	    IsSupportedSampledDepthView(image.info.pixel_format, view_format, descriptor.DstSelXYZW());
	if (resource_ok && encoding_ok && view_ok) {
		return;
	}
	const auto descriptor_pitch =
	    TileGetTexturePitch(descriptor.Format(), static_cast<uint32_t>(descriptor.Width5()) + 1u,
	                        descriptor.TileMode());
	EXIT("unsupported sampled depth image: resource=%d encoding=%d view=%d "
	     "class=%u numeric=%u dimension=%u mip_mode=%u read=%d written=%d atomic=%d compare=%d "
	     "guest_format=%u swizzle=0x%03x image_format=%d view_format=%d image_layers=%u "
	     "descriptor_type=%u base_array=%u depth=%u descriptor_pitch=%u target_pitch=%u "
	     "addr=0x%016" PRIx64 " size=0x%016" PRIx64
	     " dwords=%08x,%08x,%08x,%08x,%08x,%08x,%08x,%08x\n",
	     resource_ok, encoding_ok, view_ok,
	     static_cast<uint32_t>(resource.resource_class),
	     static_cast<uint32_t>(resource.numeric_class), static_cast<uint32_t>(resource.dimension),
	     static_cast<uint32_t>(resource.mip_mode), resource.read, resource.written, resource.atomic,
	     resource.depth_compare, static_cast<uint32_t>(descriptor.Format()),
	     descriptor.DstSelXYZW(), static_cast<int>(image.info.pixel_format),
	     static_cast<int>(view_format), image.info.resources.layers,
	     static_cast<uint32_t>(descriptor.Type()), descriptor.BaseArray5(), descriptor.Depth(),
	     descriptor_pitch, image.info.pitch, descriptor.Base40(), size, descriptor.fields[0],
	     descriptor.fields[1], descriptor.fields[2], descriptor.fields[3], descriptor.fields[4],
	     descriptor.fields[5], descriptor.fields[6], descriptor.fields[7]);
}

static bool IsSupportedStorageTextureDescriptor(const ShaderRecompiler::IR::ImageResource& resource,
                                                const ShaderTextureResource& descriptor) {
	const auto tile              = descriptor.TileMode();
	const bool is_color_1d       = descriptor.Type() == Prospero::ImageType::kColor1D;
	const bool is_color_1d_array = descriptor.Type() == Prospero::ImageType::kColor1DArray;
	const bool valid_1d_slice =
	    (is_color_1d && descriptor.Depth() == 0 && descriptor.BaseArray5() == 0) ||
	    (is_color_1d_array && descriptor.BaseArray5() <= descriptor.Depth());
	const bool is_1d = resource.dimension == ShaderRecompiler::Decoder::ImageDimension::Dim1D &&
	                   descriptor.Height5() == 0 && valid_1d_slice;
	const bool is_1d_array =
	    resource.dimension == ShaderRecompiler::Decoder::ImageDimension::Dim1DArray &&
	    is_color_1d_array && descriptor.Height5() == 0 &&
	    descriptor.BaseArray5() <= descriptor.Depth();
	const bool is_color_2d       = descriptor.Type() == Prospero::ImageType::kColor2D;
	const bool is_color_2d_array = descriptor.Type() == Prospero::ImageType::kColor2DArray;
	const bool valid_2d_slice =
	    (is_color_2d && descriptor.Depth() == 0 && descriptor.BaseArray5() == 0) ||
	    (is_color_2d_array && descriptor.BaseArray5() <= descriptor.Depth());
	const bool is_2d =
	    resource.dimension == ShaderRecompiler::Decoder::ImageDimension::Dim2D && valid_2d_slice;
	const bool is_cube = resource.cube && descriptor.Type() == Prospero::ImageType::kCube &&
	                     descriptor.Width5() == descriptor.Height5() &&
	                     descriptor.BaseArray5() <= descriptor.Depth() &&
	                     (descriptor.Depth() - descriptor.BaseArray5() + 1u) % 6u == 0;
	const bool is_2d_array =
	    resource.dimension == ShaderRecompiler::Decoder::ImageDimension::Dim2DArray &&
	    ((!resource.cube && is_color_2d_array && descriptor.BaseArray5() <= descriptor.Depth()) ||
	     is_cube);
	const bool is_3d = resource.dimension == ShaderRecompiler::Decoder::ImageDimension::Dim3D &&
	                   descriptor.Type() == Prospero::ImageType::kColor3D &&
	                   descriptor.BaseArray5() == 0;
	TileTextureBlockLayout tile_layout {};
	bool                   supported_tile = false;
	switch (tile) {
		case Prospero::TileMode::kLinear: supported_tile = true; break;
		case Prospero::TileMode::kDepth:
			supported_tile =
			    !resource.read && !Prospero::IsFmaskTextureFormat(descriptor.Format()) &&
			    (is_2d || is_2d_array) &&
			    TileGetTextureBlockLayout(descriptor.Format(), tile, false, tile_layout);
			break;
		case Prospero::TileMode::kStandard256B:
			supported_tile =
			    (is_2d || is_2d_array) &&
			    TileGetTextureBlockLayout(descriptor.Format(), tile, false, tile_layout);
			break;
		case Prospero::TileMode::kStandard4KB:
		case Prospero::TileMode::kStandard64KB:
			supported_tile =
			    TileGetTextureBlockLayout(descriptor.Format(), tile, is_3d, tile_layout);
			break;
		case Prospero::TileMode::kRenderTarget:
			supported_tile =
			    TileGetTextureBlockLayout(descriptor.Format(), tile, false, tile_layout);
			break;
		default: break;
	}
	const auto swizzle = descriptor.DstSelXYZW();
	const bool supported_swizzle =
	    IsValidImageSwizzle(swizzle) &&
	    (swizzle == DstSel(4, 5, 6, 7) || !resource.read || resource.atomic);
	// Storage views ignore max_mip for addressing; accept a stale max_mip below the view level
	// (ASTRO BOT writes the tail of a mip chain with base/last level above max_mip; the view
	// builder extends the level count the same way).
	const auto max_mip = resource.r128 ? descriptor.LastLevel()
	                                   : std::max(descriptor.MaxMip(), descriptor.LastLevel());
	const auto view_last_level =
	    resource.mip_mode == ShaderRecompiler::IR::ImageMipMode::DynamicStorage
	        ? descriptor.LastLevel()
	        : std::min(descriptor.LastLevel(), max_mip);
	return (is_1d || is_1d_array || is_2d || is_2d_array || is_3d) && supported_tile &&
	       descriptor.BaseLevel() <= view_last_level && view_last_level <= max_mip &&
	       descriptor.MinLod() == 0 && supported_swizzle && descriptor.BCSwizzle() == 0 &&
	       !descriptor.MsaaDepth();
}

static bool IsSupportedStorageTextureEncoding(const ShaderRecompiler::IR::ImageResource& resource,
                                              const ShaderTextureResource& descriptor) {
	constexpr uint32_t field1_reserved_mask = 0x200fff00u;
	constexpr uint32_t field2_reserved_mask = 0xf0003000u;
	constexpr uint32_t field5_expected      = 0x00700000u;
	constexpr uint32_t field5_max_mip_mask  = 0x000000f0u;
	const uint32_t     expected_field3 = descriptor.DstSelXYZW() |
	                                     (static_cast<uint32_t>(descriptor.BaseLevel()) << 12u) |
	                                     (static_cast<uint32_t>(descriptor.LastLevel()) << 16u) |
	                                     (static_cast<uint32_t>(descriptor.TileMode()) << 20u) |
	                                     (static_cast<uint32_t>(descriptor.Type()) << 28u);
	const uint32_t     expected_field4 =
	    descriptor.Depth() | (static_cast<uint32_t>(descriptor.BaseArray5()) << 16u);
	const bool common = (descriptor.fields[1] & field1_reserved_mask) == 0 &&
	                    (descriptor.fields[2] & field2_reserved_mask) == 0 &&
	                    descriptor.fields[3] == expected_field3;
	if (resource.r128) {
		return common && descriptor.fields[4] == 0 && descriptor.fields[5] == 0 &&
		       descriptor.fields[6] == 0 && descriptor.fields[7] == 0;
	}
	return common && descriptor.fields[4] == expected_field4 &&
	       (descriptor.fields[5] & ~field5_max_mip_mask) == field5_expected;
}

void ValidateStorageTexture(const ShaderRecompiler::IR::ImageResource& resource,
                            const ShaderTextureResource& descriptor, uint64_t size) {
	const auto format        = descriptor.Format();
	const bool resource_ok   = IsSupportedStorageImageResource(resource);
	const bool descriptor_ok = IsSupportedStorageTextureDescriptor(resource, descriptor);
	const bool encoding_ok   = IsSupportedStorageTextureEncoding(resource, descriptor);
	const bool uint_resource    = resource.numeric_class == Prospero::TextureNumericClass::Uint;
	const bool raw_sint_storage = format == Prospero::BufferFormat::k32SInt && uint_resource &&
	                              resource.written && !resource.read && !resource.atomic;
	const auto numeric_class = Prospero::SampledTextureNumericClass(format);
	const bool format_ok =
	    raw_sint_storage ||
	    (numeric_class != Prospero::TextureNumericClass::Unsupported &&
	     numeric_class != Prospero::TextureNumericClass::Sint &&
	     uint_resource == (numeric_class == Prospero::TextureNumericClass::Uint) &&
	     (!resource.atomic || format == Prospero::BufferFormat::k32UInt));
	if (resource_ok && descriptor_ok && encoding_ok && format_ok && size != 0) {
		return;
	}
	EXIT("unsupported storage texture: resource=%d descriptor=%d encoding=%d format=%d "
	     "class=%u numeric=%u dimension=%u mip_mode=%u atomic=%d compare=%d "
	     "base_level=%u last_level=%u max_mip=%u min_lod=%u base_array=%u bc=%u msaa=%d "
	     "depth_tile_bpe=%u swizzle_ok=%d "
	     "addr=0x%016" PRIx64 " size=0x%016" PRIx64
	     " extent=%ux%ux%u type=%u format=%u tile=%u swizzle=0x%03x read=%d written=%d "
	     "dwords=%08x,%08x,%08x,%08x,%08x,%08x,%08x,%08x\n",
	     resource_ok, descriptor_ok, encoding_ok, format_ok,
	     static_cast<uint32_t>(resource.resource_class),
	     static_cast<uint32_t>(resource.numeric_class), static_cast<uint32_t>(resource.dimension),
	     static_cast<uint32_t>(resource.mip_mode), resource.atomic, resource.depth_compare,
	     descriptor.BaseLevel(), descriptor.LastLevel(), descriptor.MaxMip(), descriptor.MinLod(),
	     descriptor.BaseArray5(), descriptor.BCSwizzle(), descriptor.MsaaDepth(),
	     Prospero::RenderTargetBytesPerElement(format),
	     IsValidImageSwizzle(descriptor.DstSelXYZW()), descriptor.Base40(), size,
	     static_cast<uint32_t>(descriptor.Width5()) + 1u,
	     static_cast<uint32_t>(descriptor.Height5()) + 1u,
	     static_cast<uint32_t>(descriptor.Depth()) + 1u, static_cast<uint32_t>(descriptor.Type()),
	     static_cast<uint32_t>(format), static_cast<uint32_t>(descriptor.TileMode()),
	     descriptor.DstSelXYZW(), resource.read, resource.written, descriptor.fields[0],
	     descriptor.fields[1], descriptor.fields[2], descriptor.fields[3], descriptor.fields[4],
	     descriptor.fields[5], descriptor.fields[6], descriptor.fields[7]);
}

// Session 83, gate "bindpack": the key of the null-T# memo. NullTextureDesc below reads
// exactly three things - the numeric class, whether the binding is storage, and whether it is
// a native depth compare - so three by three keys cover every answer it can give. Nine.
static uint32_t NullTextureKey(const ShaderRecompiler::IR::ImageResource& resource,
                               TextureCache::BindingType                  binding) {
	uint32_t numeric = 0;
	switch (resource.numeric_class) {
		case Prospero::TextureNumericClass::Float: numeric = 0; break;
		case Prospero::TextureNumericClass::Uint: numeric = 1; break;
		case Prospero::TextureNumericClass::Sint: numeric = 2; break;
		default: EXIT("null image has unsupported numeric class\n");
	}
	const bool native_compare = binding == TextureCache::BindingType::Texture &&
	                            resource.depth_compare && !resource.manual_depth_compare;
	const uint32_t shape = binding == TextureCache::BindingType::Storage ? 2u
	                       : native_compare                             ? 1u
	                                                                    : 0u;
	return numeric * 3u + shape;
}

static TextureCache::ImageDesc NullTextureDesc(const ShaderRecompiler::IR::ImageResource& resource,
                                               TextureCache::BindingType                  binding) {
	TextureCache::ImageDesc desc {};
	switch (resource.numeric_class) {
		case Prospero::TextureNumericClass::Float:
			desc.info.guest_format = Prospero::BufferFormat::k32Float;
			break;
		case Prospero::TextureNumericClass::Uint:
			desc.info.guest_format = Prospero::BufferFormat::k32UInt;
			break;
		case Prospero::TextureNumericClass::Sint:
			desc.info.guest_format = Prospero::BufferFormat::k32SInt;
			break;
		default: EXIT("null image has unsupported numeric class\n");
	}
	desc.info.pixel_format    = VulkanFormat(desc.info.guest_format);
	const bool native_compare = binding == TextureCache::BindingType::Texture &&
	                            resource.depth_compare && !resource.manual_depth_compare;
	if (native_compare) {
		desc.info.pixel_format = vk::Format::eD32Sfloat;
	}
	desc.info.type            = Prospero::ImageType::kColor2D;
	desc.info.extent          = {1, 1, 1};
	desc.info.resources       = {1, 1};
	desc.info.bytes_per_block = 4;
	desc.info.samples         = 1;
	desc.info.mip_layout[0]   = {0, 0, 1, 1};
	desc.view_info.format     = desc.info.pixel_format;
	desc.view_info.type       = vk::ImageViewType::e2D;
	desc.view_info.aspect     = native_compare ? vk::ImageAspectFlagBits::eDepth
	                                          : vk::ImageAspectFlagBits::eColor;
	desc.view_info.usage      = binding == TextureCache::BindingType::Storage
	                                ? vk::ImageUsageFlagBits::eStorage
	                                : vk::ImageUsageFlagBits::eSampled;
	desc.type                 = binding;
	return desc;
}

// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053), route E measurement
// M3.  NullTextureDesc above aborts on a numeric class it cannot express.  Today that is
// reachable only from a genuinely null T#, which is rare; on the floor EVERY image slot goes
// through it, so a single such shader would kill the run.  A draw carrying one keeps the real
// path and is counted bf_skip instead.  Read-only, no side effect, no timestamp.
bool BindFloorStageSupported(const ShaderStageRuntime& runtime) {
	if (!runtime) {
		return false;
	}
	for (const auto& image: runtime.program->info.images) {
		switch (image.numeric_class) {
			case Prospero::TextureNumericClass::Float:
			case Prospero::TextureNumericClass::Uint:
			case Prospero::TextureNumericClass::Sint: break;
			default: return false;
		}
	}
	return true;
}

// Session 96, gate "bindfloor": the floor's replacement for PrepareBindings.  It writes the
// two things CommitBindings' emit half reads out of a PreparedBindings and nothing else:
// `runtime`, which carries program.bindings.descriptors (the SHAPE of the descriptor writes,
// which the floor does not change), and a zero shader_data of exactly ShaderDataDwords()
// entries, which keeps EXIT_IF(prepared->shader_data.size() != shader_data_dwords) true and
// gives the push constants a defined value.  images / buffers / samplers / gds /
// flattened_srt / shader_data_buffer stay EMPTY: the stubs are supplied in CommitBindings.
void BindFloorPrepareStage(const ShaderStageRuntime& runtime, PreparedBindings& prepared) {
	EXIT_IF(!runtime);
	prepared.Reset();
	prepared.runtime = &runtime;
	prepared.shader_data.assign(runtime.program->bindings.ShaderDataDwords(), 0u);
	// Session 97: CommitBindings reads this, not the gate.
	prepared.floor = true;
}

namespace {
// Session 97, gate "bindfloor": the per-op latch (descriptors.h).  Written only by
// BindFloorLatchOp on the thread that runs the op, read on that same thread; the GuestGpu
// thread is the only one that runs draws and dispatches, so no other thread ever sees a
// value it did not latch itself (a thread that never latched reads armed = false).
// Session 98 (patch_s98a): KYTY_BIND_FLOOR_LATCH selects how the value is taken (descriptors.h).
thread_local BindFloorOp t_bind_floor_op {};
std::atomic<bool>        g_bind_floor_ever {false};

// Session 98 (patch_s98a, MEASUREMENT ONLY; descriptors.h).  The slice GuestGpu::Process is
// running, published for its length by ThreadRun (nullptr on every other thread and between
// submissions: such a latcher reads seq 0, i.e. the base value, and is not accounted).
thread_local BindFloorSlice* t_bf_slice = nullptr;
// GPU flip packets processed so far (every mode; the frame clock of modes 1 and 2).
std::atomic<uint64_t> g_bf_flip_epoch {0};

// Mode 1, the frame latch.  Written only on GuestGpu (flip packets, ThreadRun resolution);
// relaxed atomics so that an off-thread latcher (m4baton relay, pinned off) reads the same
// values.  A value packs {armed (bit 32), bfmode (low 32 bits)}.
constexpr uint64_t    BfArmedBit = uint64_t {1} << 32u;
std::atomic<bool>     g_bf_base_init {false};
std::atomic<uint64_t> g_bf_base {0};
// Session 98 (patch_s98e): incomplete submissions whose sticky value is armed (mode 1 only).
std::atomic<uint32_t> g_bf_sticky_armed {0};
std::atomic<bool>     g_bf_pending_valid {false};
std::atomic<uint64_t> g_bf_pending_sflip {0};
std::atomic<uint64_t> g_bf_pending_value {0};
uint32_t              g_bf_pending_flips = 0;     // further flip packets seen while pending
bool                  g_bf_pending_older = false; // an older submission was in flight at the flip

// Mode 2, the GDS trigger.  The hold is per latching thread, like t_bind_floor_op.
thread_local bool            t_bf_hold       = false;
thread_local uint64_t        t_bf_hold_epoch = 0;
thread_local uint64_t        t_bf_hold_ops   = 0;
std::mutex                   g_gds_keys_mutex;
std::unordered_set<uint64_t> g_gds_keys;

struct BfKey {
	uint64_t key      = 0;
	bool     dispatch = false;
	uint64_t a0       = 0; // cs (dispatch) or vs (draw) data_addr
	uint64_t a1       = 0; // ps data_addr (draw)
};

uint64_t BfPack(bool armed, uint32_t mode) {
	return (armed ? BfArmedBit : 0u) | mode;
}

BindFloorOp BfUnpack(uint64_t value) {
	BindFloorOp op;
	op.armed = (value & BfArmedBit) != 0;
	op.mode  = static_cast<uint32_t>(value & 0xffffffffu);
	return op;
}

uint64_t BfLive() {
	return BfPack(Common::Gates::Enabled(Common::Gates::Gate::BindFloor),
	              Common::Gates::Value(Common::Gates::Knob::BindFloorMode));
}

void BfMarkEver(bool armed) {
	if (armed && !g_bind_floor_ever.load(std::memory_order_relaxed)) {
		g_bind_floor_ever.store(true, std::memory_order_relaxed);
	}
}

// Mode 1: the base starts as the live value at the first use (a schedule starts unarmed).
void BfInitBase() {
	if (g_bf_base_init.load(std::memory_order_acquire)) {
		return;
	}
	const uint64_t live = BfLive();
	g_bf_base.store(live, std::memory_order_relaxed);
	BfMarkEver((live & BfArmedBit) != 0);
	g_bf_base_init.store(true, std::memory_order_release);
	LOGF("BindFloorLatch: base armed=%d mode=%u\n", (live & BfArmedBit) != 0 ? 1 : 0,
	     static_cast<uint32_t>(live & 0xffffffffu));
}

// Mode 1: pending -> base.  bf_edge is booked here, once per adopted change of `armed`.
void BfAdopt(bool force) {
	const uint64_t value = g_bf_pending_value.load(std::memory_order_relaxed);
	const uint64_t old   = g_bf_base.load(std::memory_order_relaxed);
	g_bf_base.store(value, std::memory_order_relaxed);
	g_bf_pending_valid.store(false, std::memory_order_release);
	if (((old ^ value) & BfArmedBit) != 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorEdges, 1);
	}
	BfMarkEver((value & BfArmedBit) != 0);
	if (force) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorDeferForce, 1);
	} else if (g_bf_pending_older) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorDefer, 1);
	}
}

bool BfGdsKnown(uint64_t key) {
	std::lock_guard<std::mutex> lock(g_gds_keys_mutex);
	return g_gds_keys.find(key) != g_gds_keys.end();
}

// The draw key lives in the upper half of the key space (bit 63), a dispatch key is its CS
// address (< 2^48), so the two can never collide.  0 is "no key".
uint64_t BfDrawKey(uint64_t vs_addr, uint64_t ps_addr) {
	uint64_t h = vs_addr * 0x9E3779B97F4A7C15ull;
	h ^= ps_addr + 0x632BE59BD9B4E019ull + (h << 6u) + (h >> 2u);
	h ^= h >> 31u;
	h *= 0xBF58476D1CE4E5B9ull;
	h ^= h >> 29u;
	return h | (uint64_t {1} << 63u);
}

void BfLogTrigger(const char* what, const BfKey* key, uint64_t flips) {
	static std::atomic<uint32_t> logged {0};
	if (logged.fetch_add(1, std::memory_order_relaxed) >= 256) {
		return;
	}
	const uint64_t seq = t_bf_slice != nullptr ? t_bf_slice->seq : 0;
	if (key == nullptr) {
		LOGF("BindFloorTrigger: %s key=0x0 kind=aux held_ops=%" PRIu64 " flips=%" PRIu64
		     " seq=%" PRIu64 "\n",
		     what, t_bf_hold_ops, flips, seq);
	} else if (key->dispatch) {
		LOGF("BindFloorTrigger: %s key=0x%016" PRIx64 " kind=dispatch cs=0x%016" PRIx64
		     " held_ops=%" PRIu64 " flips=%" PRIu64 " seq=%" PRIu64 "\n",
		     what, key->key, key->a0, t_bf_hold_ops, flips, seq);
	} else {
		LOGF("BindFloorTrigger: %s key=0x%016" PRIx64 " kind=draw vs=0x%016" PRIx64
		     " ps=0x%016" PRIx64 " held_ops=%" PRIu64 " flips=%" PRIu64 " seq=%" PRIu64 "\n",
		     what, key->key, key->a0, key->a1, t_bf_hold_ops, flips, seq);
	}
}

// The one latch body.  op_site: a draw or dispatch (bf_mixed accounting, the only sites that may
// adopt a held falling edge in mode 2).  key: the op's shader key, non-null only in mode 2.
BindFloorOp BfLatch(bool op_site, const BfKey* key) {
	BindFloorOp    op;
	const uint32_t latch_mode = BindFloorLatchMode();
	if (latch_mode == 1) {
		// Frame latch: no live read here.  Never adopts.
		// Session 98 (patch_s98d): STICKY per submission - an op-site latch reuses the value its
		// submission fixed at its first op-site latch (two values for the flip-bearing DCB: before
		// and after its flip packet).  Non-op reads (compute prefetch) compute it every time.
		BfInitBase();
		auto* const slice      = t_bf_slice;
		bool*       sticky_set = nullptr;
		uint64_t*   sticky     = nullptr;
		if (op_site && slice != nullptr) {
			sticky_set = slice->after_flip ? &slice->sticky_post_set : &slice->sticky_pre_set;
			sticky     = slice->after_flip ? &slice->sticky_post : &slice->sticky_pre;
		}
		uint64_t value = 0;
		if (sticky_set != nullptr && *sticky_set) {
			value = *sticky;
		} else {
			value = g_bf_base.load(std::memory_order_relaxed);
			if (g_bf_pending_valid.load(std::memory_order_acquire)) {
				const uint64_t s_flip = g_bf_pending_sflip.load(std::memory_order_relaxed);
				if (slice != nullptr &&
				    (slice->seq > s_flip || (slice->seq == s_flip && slice->after_flip))) {
					value = g_bf_pending_value.load(std::memory_order_relaxed);
				}
			}
			if (sticky_set != nullptr) {
				*sticky     = value;
				*sticky_set = true;
				// Session 98 (patch_s98e): an armed sticky value may outlive base/pending (xover,
				// forced adoption); keep the GC keep-alive on until this submission completes.
				if ((value & BfArmedBit) != 0 && !slice->sticky_armed_counted) {
					slice->sticky_armed_counted = true;
					g_bf_sticky_armed.fetch_add(1, std::memory_order_relaxed);
				}
			}
		}
		op = BfUnpack(value);
		BfMarkEver(op.armed);
	} else if (latch_mode == 2) {
		const bool     live      = Common::Gates::Enabled(Common::Gates::Gate::BindFloor);
		const uint32_t live_mode = Common::Gates::Value(Common::Gates::Knob::BindFloorMode);
		const auto&    held      = t_bind_floor_op;
		if (held.armed && !live) {
			// A falling edge is pending: hold it until a learned GDS consumer (or the fallback).
			const uint64_t epoch = g_bf_flip_epoch.load(std::memory_order_relaxed);
			if (!t_bf_hold) {
				t_bf_hold       = true;
				t_bf_hold_epoch = epoch;
				t_bf_hold_ops   = 0;
			}
			bool adopt = false;
			if (op_site) {
				if (key != nullptr && key->key != 0 && BfGdsKnown(key->key)) {
					adopt = true;
					Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorTrigFire, 1);
					BfLogTrigger("fire", key, epoch - t_bf_hold_epoch);
				} else if (epoch - t_bf_hold_epoch >= 2) {
					adopt = true;
					Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorTrigFb, 1);
					BfLogTrigger("fallback", key, epoch - t_bf_hold_epoch);
				}
			}
			if (adopt) {
				op.armed  = false;
				op.mode   = live_mode;
				t_bf_hold = false;
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorEdges, 1);
			} else {
				op.armed = true;
				op.mode  = held.mode;
				if (op_site) {
					t_bf_hold_ops++;
					Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorTrigWait, 1);
				}
			}
		} else {
			// Rising edge or no change: per op, exactly as mode 0.
			t_bf_hold = false;
			op.armed  = live;
			op.mode   = live_mode;
			if (op.armed != held.armed) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorEdges, 1);
			}
			BfMarkEver(op.armed);
		}
	} else {
		// Mode 0: the session-97 per-op latch, verbatim.
		op.armed = Common::Gates::Enabled(Common::Gates::Gate::BindFloor);
		op.mode  = Common::Gates::Value(Common::Gates::Knob::BindFloorMode);
		// bf_edge: the latch changed value - one per schedule edge as the translating thread
		// saw it.  Counted in the flip of the op that saw the new value, so a falling edge is
		// booked in the first frame of the base arm; it is the only bf_* the base arm writes.
		if (op.armed != t_bind_floor_op.armed) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorEdges, 1);
		}
		if (op.armed && !g_bind_floor_ever.load(std::memory_order_relaxed)) {
			g_bind_floor_ever.store(true, std::memory_order_relaxed);
		}
	}
	if (key != nullptr) {
		op.key = key->key;
	}
	// bf_mixed: draw/dispatch latches only, split at this submission's flip packet.
	if (op_site && t_bf_slice != nullptr) {
		auto&         slice = *t_bf_slice;
		const uint8_t bit   = op.armed ? 1u : 2u;
		slice.ops++;
		if (slice.after_flip) {
			slice.bits_post |= bit;
		} else {
			slice.bits_pre |= bit;
		}
	}
	t_bind_floor_op = op;
	return op;
}
} // namespace

BindFloorOp BindFloorLatchOp() {
	return BfLatch(false, nullptr);
}

uint32_t BindFloorLatchMode() {
	static const uint32_t mode = [] {
		const char* value = std::getenv("KYTY_BIND_FLOOR_LATCH");
		uint32_t    m     = 0;
		if (value != nullptr && value[0] != '\0') {
			char*               end    = nullptr;
			const unsigned long parsed = std::strtoul(value, &end, 10);
			if (end == value || *end != '\0' || parsed > 2) {
				EXIT("KYTY_BIND_FLOOR_LATCH=%s: expected 0, 1 or 2\n", value);
			}
			m = static_cast<uint32_t>(parsed);
		}
		LOGF("BindFloorLatch: mode %u\n", m);
		return m;
	}();
	return mode;
}

uint32_t BindFloorClearMode() {
	static const uint32_t mode = [] {
		const char* value = std::getenv("KYTY_BIND_FLOOR_CLEAR");
		uint32_t    m     = 0;
		if (value != nullptr && value[0] != '\0') {
			char*               end    = nullptr;
			const unsigned long parsed = std::strtoul(value, &end, 10);
			if (end == value || *end != '\0' || parsed > 1) {
				EXIT("KYTY_BIND_FLOOR_CLEAR=%s: expected 0 or 1\n", value);
			}
			m = static_cast<uint32_t>(parsed);
		}
		LOGF("BindFloorClear: mode %u\n", m);
		return m;
	}();
	return mode;
}

BindFloorOp BindFloorLatchDraw(uint64_t vs_addr, uint64_t ps_addr) {
	if (BindFloorLatchMode() != 2) {
		return BfLatch(true, nullptr);
	}
	BfKey key;
	key.key      = BfDrawKey(vs_addr, ps_addr);
	key.dispatch = false;
	key.a0       = vs_addr;
	key.a1       = ps_addr;
	return BfLatch(true, &key);
}

BindFloorOp BindFloorLatchDispatch(uint64_t cs_addr) {
	if (BindFloorLatchMode() != 2) {
		return BfLatch(true, nullptr);
	}
	BfKey key;
	key.key      = cs_addr;
	key.dispatch = true;
	key.a0       = cs_addr;
	return BfLatch(true, &key);
}

bool BindFloorGcAuditSticky() {
	// Read-only independent subset: a current submission with a counted armed sticky
	// value must be held by GC. Process runs GC before SliceComplete removes its count.
	// No CurrentOp read (it can outlive a submission), live gate read, or latch adoption.
	return t_bf_slice != nullptr && t_bf_slice->sticky_armed_counted;
}

bool BindFloorGcHold() {
	switch (BindFloorLatchMode()) {
		case 1: {
			// Conservative: the LRU clock stops while either frame could be floored.
			BfInitBase();
			if ((g_bf_base.load(std::memory_order_relaxed) & BfArmedBit) != 0) {
				return true;
			}
			// Session 98 (patch_s98e): a submission still running on an armed sticky value.
			if (g_bf_sticky_armed.load(std::memory_order_relaxed) != 0) {
				return true;
			}
			return g_bf_pending_valid.load(std::memory_order_acquire) &&
			       (g_bf_pending_value.load(std::memory_order_relaxed) & BfArmedBit) != 0;
		}
		case 2:
			// The held value (a pending falling edge keeps it armed) or the live rising one.
			return t_bind_floor_op.armed ||
			       Common::Gates::Enabled(Common::Gates::Gate::BindFloor);
		default: return BindFloorLatchOp().armed;
	}
}

bool BindFloorDownloadSkip() {
	if (BindFloorLatchMode() == 0) {
		return Common::Gates::Enabled(Common::Gates::Gate::BindFloor) || BindFloorEverArmed();
	}
	return BindFloorCurrentOp().armed || BindFloorEverArmed();
}

bool BindFloorClearSkip() {
	// Session 98 (patch_s98d): only where ProgramCache::Get freezes the snapshot
	// (pipelineCache.cpp: bind_floor = armed && mode != 2).
	return BindFloorClearMode() == 1 && t_bind_floor_op.armed && t_bind_floor_op.mode != 2;
}

void BindFloorNoteGdsBarrier() {
	if (BindFloorLatchMode() != 2) {
		return;
	}
	const uint64_t key = t_bind_floor_op.key;
	if (key == 0) {
		return;
	}
	bool inserted = false;
	{
		std::lock_guard<std::mutex> lock(g_gds_keys_mutex);
		inserted = g_gds_keys.insert(key).second;
	}
	if (inserted) {
		static std::atomic<uint32_t> logged {0};
		if (logged.fetch_add(1, std::memory_order_relaxed) < 64) {
			LOGF("BindFloorTrigger: learn key=0x%016" PRIx64 " seq=%" PRIu64 "\n", key,
			     t_bf_slice != nullptr ? t_bf_slice->seq : uint64_t {0});
		}
	}
}

void BindFloorSetSlice(BindFloorSlice* slice) {
	t_bf_slice = slice;
}

uint64_t BindFloorSliceSeq() {
	return t_bf_slice != nullptr ? t_bf_slice->seq : 0;
}

void BindFloorSliceComplete(const BindFloorSlice& slice) {
	if (slice.sticky_armed_counted) {
		// Session 98 (patch_s98e): the submission is complete - its armed sticky value is gone.
		g_bf_sticky_armed.fetch_sub(1, std::memory_order_relaxed);
	}
	if (slice.bits_pre != 3 && slice.bits_post != 3) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorMixed, 1);
	static std::atomic<uint32_t> logged {0};
	if (logged.fetch_add(1, std::memory_order_relaxed) < 64) {
		LOGF("BindFloorMixed: seq=%" PRIu64 " queue=%u bits=%u/%u ops=%u\n", slice.seq,
		     slice.queue, static_cast<uint32_t>(slice.bits_pre),
		     static_cast<uint32_t>(slice.bits_post), slice.ops);
	}
}

uint64_t BindFloorFlipEpoch() {
	return g_bf_flip_epoch.load(std::memory_order_relaxed);
}

bool BindFloorNoteFlipPacket(const BindFloorFlipQueues* queues) {
	bool created = false;
	if (BindFloorLatchMode() == 1) {
		// Session 98 (patch_s98d): the frame latch places the frame boundary at the flip-bearing
		// submission's seq; a flip packet on a thread without a GuestGpu slice (the m4baton
		// relay, pinned 0) has none, and would silently collapse the boundary.
		if (t_bf_slice == nullptr) {
			EXIT("KYTY_BIND_FLOOR_LATCH=1: a GPU flip packet was processed on a thread without a "
			     "GuestGpu submission slice (the m4baton relay?) - the frame latch cannot place the "
			     "frame boundary; run with m4baton=0 or KYTY_BIND_FLOOR_LATCH=0\n");
		}
		BfInitBase();
		if (g_bf_pending_valid.load(std::memory_order_relaxed) && ++g_bf_pending_flips >= 2) {
			BfAdopt(true);
		}
		// The ONLY live read of the gate in mode 1.
		const uint64_t live = BfLive();
		if (!g_bf_pending_valid.load(std::memory_order_relaxed) &&
		    live != g_bf_base.load(std::memory_order_relaxed)) {
			g_bf_pending_value.store(live, std::memory_order_relaxed);
			g_bf_pending_sflip.store(BindFloorSliceSeq(), std::memory_order_relaxed);
			g_bf_pending_flips = 0;
			g_bf_pending_older = queues != nullptr && queues->older_in_flight;
			g_bf_pending_valid.store(true, std::memory_order_release);
			created = true;
			if (queues != nullptr) {
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorXover, queues->xover);
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorXoverAcb,
				                        queues->xover_acb);
			}
		}
	}
	g_bf_flip_epoch.fetch_add(1, std::memory_order_relaxed);
	// The rest of the flip-bearing DCB belongs to the next frame (every mode: bf_mixed).
	if (t_bf_slice != nullptr) {
		t_bf_slice->after_flip = true;
	}
	return created;
}

bool BindFloorPendingValid() {
	return g_bf_pending_valid.load(std::memory_order_acquire);
}

void BindFloorResolve(uint64_t min_front_seq) {
	if (BindFloorLatchMode() != 1 || !g_bf_pending_valid.load(std::memory_order_acquire)) {
		return;
	}
	if (min_front_seq > g_bf_pending_sflip.load(std::memory_order_relaxed)) {
		BfAdopt(false);
	}
}

const BindFloorOp& BindFloorCurrentOp() {
	return t_bind_floor_op;
}

bool BindFloorEverArmed() {
	return g_bind_floor_ever.load(std::memory_order_relaxed);
}

static void PopulateTextureMipLayout(ImageInfo& info) {
	if (info.IsVolume() && info.tile_mode != Prospero::TileMode::kLinear) {
		TileSurfaceLayout            surface {};
		const TileSurfaceDescription description {
		    info.guest_format,  info.tile_mode,    TileSurfaceDimension::Dim3D, info.extent.width,
		    info.extent.height, info.extent.depth, info.resources.levels,       1};
		if (!TileGetTiledTextureLayout(description, surface)) {
			EXIT("unsupported normalized volume texture layout\n");
		}
		for (uint32_t level = 0; level < info.resources.levels; level++) {
			const auto& mip        = surface.mips[level];
			info.mip_layout[level] = {
			    mip.offset,
			    mip.size,
			    mip.padded_width,
			    mip.padded_height,
			};
		}
		return;
	}

	TileSizeOffset levels[16] {};
	TilePaddedSize padded[16] {};
	TileGetTextureSize(info.guest_format, info.extent.width, info.extent.height,
	                   info.resources.levels, info.tile_mode, nullptr, levels, padded);
	const auto texel_shift = info.IsBlock() ? 2u : 0u;
	for (uint32_t level = 0; level < info.resources.levels; level++) {
		const auto offset =
		    levels[level].src_size != 0 ? levels[level].src_offset : levels[level].offset;
		auto size = static_cast<uint64_t>(levels[level].src_size != 0 ? levels[level].src_size
		                                                              : levels[level].size);
		if (info.IsVolume()) {
			size *= std::max(info.extent.depth >> level, 1u);
		} else {
			size *= info.resources.layers;
		}
		info.mip_layout[level] = {
		    offset,
		    size,
		    padded[level].width >> texel_shift,
		    padded[level].height >> texel_shift,
		};
	}
}

// KYTY_TSHARP_MIN_LOD=0 disables the T# MIN_LOD clamp (debug A/B).
static bool TSharpMinLodEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_TSHARP_MIN_LOD");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

static ImageViewInfo TextureViewInfo(const ShaderRecompiler::IR::ImageResource& resource,
                                     const ShaderTextureResource& descriptor, vk::Format format,
                                     const SurfaceFormatInfo& surface_format, bool storage,
                                     uint32_t view_levels, uint32_t image_layers, bool min_lod_views) {
	ImageViewInfo view {};
	view.format      = format;
	view.aspect      = vk::ImageAspectFlagBits::eColor;
	view.base_level  = descriptor.BaseLevel();
	view.level_count = view_levels;
	// T# MIN_LOD (4.8 fixed point, relative to base_level). Texture streaming keeps the mip chain
	// addressing intact and raises MIN_LOD while the top levels are not resident yet; sampling
	// below it reads memory the streamer has not filled (ASTRO BOT: 4K wall/prop textures came
	// out as noise). Without VK_EXT_image_view_min_lod the whole levels are cut from the view.
	if (!storage && descriptor.MinLod() != 0 && view_levels > 1 && TSharpMinLodEnabled()) {
		static bool logged = false;
		if (!logged) {
			logged = true;
			LOGF("Texture: T# MIN_LOD %u/256 applied to a sampled view (%s)\n",
			     static_cast<uint32_t>(descriptor.MinLod()),
			     min_lod_views ? "VK_EXT_image_view_min_lod" : "base level shift");
		}
		if (min_lod_views) {
			view.min_lod = descriptor.MinLod();
		} else {
			const uint32_t whole = std::min<uint32_t>(descriptor.MinLod() >> 8u, view_levels - 1u);
			view.base_level += whole;
			view.level_count -= whole;
		}
	}
	view.usage   = storage ? vk::ImageUsageFlagBits::eStorage : vk::ImageUsageFlagBits::eSampled;
	view.mapping =
	    storage || surface_format.conversion_format != Prospero::BufferFormat::kInvalid
	        ? vk::ComponentMapping {}
	        : TextureGetComponentMapping(descriptor.DstSelXYZW(), surface_format.host_to_storage);
	switch (resource.dimension) {
		case ShaderRecompiler::Decoder::ImageDimension::Dim1D:
			view.type       = vk::ImageViewType::e1D;
			view.base_layer = descriptor.BaseArray5();
			if (view.base_layer >= image_layers) {
				EXIT("texture base layer is out of bounds\n");
			}
			view.layer_count = 1;
			break;
		case ShaderRecompiler::Decoder::ImageDimension::Dim1DArray:
			view.type       = vk::ImageViewType::e1DArray;
			view.base_layer = descriptor.BaseArray5();
			if (view.base_layer >= image_layers) {
				EXIT("texture array base layer is out of bounds\n");
			}
			view.layer_count = image_layers - view.base_layer;
			break;
		case ShaderRecompiler::Decoder::ImageDimension::Dim3D:
			view.type        = vk::ImageViewType::e3D;
			view.base_layer  = 0;
			view.layer_count = 1;
			break;
		case ShaderRecompiler::Decoder::ImageDimension::Dim2DArray:
		case ShaderRecompiler::Decoder::ImageDimension::Dim2DMsaaArray:
			view.type       = vk::ImageViewType::e2DArray;
			view.base_layer = descriptor.BaseArray5();
			if (view.base_layer >= image_layers) {
				EXIT("texture array base layer is out of bounds\n");
			}
			view.layer_count = image_layers - view.base_layer;
			break;
		case ShaderRecompiler::Decoder::ImageDimension::Dim2D:
		case ShaderRecompiler::Decoder::ImageDimension::Dim2DMsaa:
			view.type       = vk::ImageViewType::e2D;
			view.base_layer = descriptor.BaseArray5();
			if (view.base_layer >= image_layers) {
				EXIT("texture base layer is out of bounds\n");
			}
			view.layer_count = 1;
			break;
		default: EXIT("unsupported texture view dimension\n");
	}
	return view;
}

// Gate "texmemo2": MemoHashBytes of the ImageResource key bytes, which are constant per program
// resource, without hashing them on every binding.
static uint64_t MemoResourceKey(RenderExecutorMemo&                        memo,
                                const ShaderRecompiler::IR::ImageResource& resource) {
	const auto size = static_cast<size_t>(
	    reinterpret_cast<const uint8_t*>(&resource.indirect_resources) -
	    reinterpret_cast<const uint8_t*>(&resource));
	RenderExecutorMemo::ResourceKey probe {};
	if (size != sizeof(probe.words)) {
		return MemoHashBytes(&resource, size);
	}
	std::memcpy(probe.words.data(), &resource, sizeof(probe.words));
	const auto address = reinterpret_cast<uintptr_t>(&resource);
	auto&      entry   = memo.resource_keys[((address >> 6u) ^ (address >> 17u)) &
	                                        (RenderExecutorMemo::ResourceKeySlots - 1)];
	uint64_t   differ  = 0;
	for (size_t i = 0; i < probe.words.size(); i++) {
		differ |= entry.words[i] ^ probe.words[i];
	}
	if (entry.resource == &resource && differ == 0) {
		return entry.key;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::TexMemoKeyMisses, 1);
	entry.resource = &resource;
	entry.words    = probe.words;
	entry.key      = MemoHashBytes(&resource, size);
	return entry.key;
}

// Gate "texmemo2": the slot of a two-way set - the way whose tag matches, else the one to fill
// (an unused way, else the one used longer ago). The key itself is still compared on the slot.
static uint32_t MemoTextureWay(const RenderExecutorMemo& memo, uint64_t hash) {
	const auto  first = static_cast<uint32_t>(hash & (RenderExecutorMemo::TextureSlots - 2));
	const auto& a     = memo.texture_ways[first];
	const auto& b     = memo.texture_ways[first + 1];
	if (a.use != 0 && a.hash == hash) {
		return first;
	}
	if (b.use != 0 && b.hash == hash) {
		return first + 1;
	}
	if (a.use == 0) {
		return first;
	}
	if (b.use == 0) {
		return first + 1;
	}
	return a.use <= b.use ? first : first + 1;
}

// Gate "texfast": whether TextureCache::ConfigureImageSourceUnlocked(id, desc) would leave the
// image as it is - the same test on the same fields, all of which only the GuestGpu thread writes.
static bool TextureSourceSettled(const Image& image, const TextureCache::ImageDesc& desc) {
	if (!image.info.IsBlock() || image.IsGpuModified()) {
		return true;
	}
	const bool same  = image.info.data == desc.info.data && image.info.extent == desc.info.extent &&
	                   image.info.resources == desc.info.resources;
	const auto first = same ? desc.source_first_level : 0u;
	const auto size  = same && desc.source_size != 0 ? desc.source_size : image.info.data.size;
	if (image.binding.is_bound && first > image.source_first_level) {
		return true;
	}
	return first == image.source_first_level && size == image.SourceRange().size;
}

// Session 88, knob "bindwit" (MEASUREMENT ONLY): PrepareBindings arms these for the duration
// of its image loop ONLY, so the other call site of this template - ResolveTexture, reached
// from the repair loop of RebindImages - never marks and the two populations stay separate
// (b_texn reads 50 087 a frame against bl_res_n 47 727).  g_bind_wit_arm carries the knob
// value; the resolve writes g_bind_wit_mark at the point the memo-hit decision is complete -
// a real NowNs() at 2, the sentinel 1 at 1, which says "this call took the memo-hit path" and
// costs no timestamp.  So both values pay exactly ONE timestamp a slot and the price of the
// mark cancels in the difference of the arms.
static thread_local uint32_t g_bind_wit_arm  = 0;
static thread_local uint64_t g_bind_wit_mark = 0;

// Session 57, B2a: every result goes out through `emit`; the three returns hand it the same
// fields MakeTextureBinding / the brace initializer did (image_view null, layout undefined, no
// mip views, memo index UINT32_MAX / version 0 unless given).
template <typename Emit>
decltype(auto) RenderExecutor::ResolveTextureWith(const ShaderRecompiler::IR::ImageResource&   resource,
                                                  const ShaderRecompiler::IR::DescriptorValue& value,
                                                  Emit&&                                       emit) {
	Common::FrameStats::Scope resolve_scope(Common::FrameStats::Counter::BindResolveTexNs,
	                                        Common::FrameStats::Counter::BindResolveTex);
	auto descriptor = DecodeNativeDescriptor<ShaderTextureResource>(value);
	const bool storage = resource.written;
	if (storage) {
		ValidateStorageImageResource(resource);
	}

	auto& texture_cache = m_context.GetTextureCache();
	// Debug aid: KYTY_SKIP_TAIL_MIP_STORAGE=1 binds a dummy image for storage views that
	// address a mip level above the descriptor max_mip, to isolate GPU faults.
	static const bool skip_tail_mip_storage = std::getenv("KYTY_SKIP_TAIL_MIP_STORAGE") != nullptr;
	const bool tail_mip_storage = storage && !descriptor.IsNull() && !resource.r128 &&
	                              descriptor.LastLevel() > descriptor.MaxMip();
	if (descriptor.IsNull() || (skip_tail_mip_storage && tail_mip_storage)) {
		const auto binding = storage ? TextureCache::BindingType::Storage
		                             : TextureCache::BindingType::Texture;
		// Session 83, gate "bindpack" (PLAN_82_bind.md item 1). Both emit lambdas take
		// `const ImageDesc&`, so a hit copies nothing; the slot is re-validated against the
		// live image every time, which GetNullImage does not do for m_null_images.
		if (Common::Gates::Enabled(Common::Gates::Gate::BindPack)) {
			auto& slot = Memo().null_textures[NullTextureKey(resource, binding)];
			if (slot.valid && texture_cache.m_slot_images.try_get(slot.image_id) != nullptr) {
				if (Common::Gates::Enabled(Common::Gates::Gate::BindPackVerify)) {
					auto       check_desc = NullTextureDesc(resource, binding);
					const auto check_id   = texture_cache.FindImage(check_desc);
					// Field-wise and NOT memcmp: ImageDesc is an aggregate with padding, its copy
					// assignment is member-wise and carries none of it, and aggregate
					// initialisation leaves it indeterminate - so memcmp compares bytes that no
					// consumer of the desc ever loads. These are every field NullTextureDesc
					// writes, plus the ImageId, which is the only thing that can genuinely vary.
					const bool id_same   = check_id == slot.image_id;
					const bool type_same = check_desc.type == slot.desc.type;
					const bool fmt_same  = check_desc.info.pixel_format == slot.desc.info.pixel_format &&
					                      check_desc.info.guest_format == slot.desc.info.guest_format &&
					                      check_desc.info.type == slot.desc.info.type &&
					                      check_desc.info.extent == slot.desc.info.extent &&
					                      check_desc.info.bytes_per_block ==
					                          slot.desc.info.bytes_per_block &&
					                      check_desc.info.samples == slot.desc.info.samples;
					const bool view_same = check_desc.view_info == slot.desc.view_info;
					if (!id_same || !type_same || !fmt_same || !view_same) {
						Common::FrameStats::Add(Common::FrameStats::Counter::BindPackBad, 1);
						static std::atomic<uint32_t> logged {0};
						if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
							LOGF("BindPackVerify: MISMATCH null texture key=%u id=%u type=%u fmt=%u"
							     " view=%u\n",
							     NullTextureKey(resource, binding),
							     static_cast<uint32_t>(id_same), static_cast<uint32_t>(type_same),
							     static_cast<uint32_t>(fmt_same), static_cast<uint32_t>(view_same));
						}
					}
				}
				Common::FrameStats::Add(Common::FrameStats::Counter::NullTexHits, 1);
				return emit(slot.image_id, slot.desc);
			}
			auto       desc = NullTextureDesc(resource, binding);
			const auto id   = texture_cache.FindImage(desc);
			slot.desc       = desc;
			slot.image_id   = id;
			slot.valid      = true;
			Common::FrameStats::Add(Common::FrameStats::Counter::NullTexMisses, 1);
			return emit(id, desc);
		}
		auto       desc = NullTextureDesc(resource, binding);
		const auto id   = texture_cache.FindImage(desc);
		Common::FrameStats::Add(Common::FrameStats::Counter::NullTexMisses, 1);
		return emit(id, desc);
	}

	// Texture LOD statistics: count the binding for the T# counter bank (IT_GET_LOD_STATS reports it).
	if (!storage && descriptor.MipStatsCntEn()) {
		LodStats::Touch(descriptor.MipStatsCntId(), descriptor.BaseLevel());
	}
	static const bool lod_trace = std::getenv("KYTY_LOD_STATS_TRACE") != nullptr;
	if (lod_trace && !storage) {
		static std::atomic<uint32_t> traced {0};
		if (descriptor.Base40() >= 0x1000000000ull && traced.fetch_add(1) < 20000) {
			LOGF("LodStats: tsharp addr=0x%010" PRIx64 " %ux%u w=%08x %08x %08x %08x %08x %08x %08x %08x\n",
			     descriptor.Base40(), static_cast<uint32_t>(descriptor.Width5()) + 1u,
			     static_cast<uint32_t>(descriptor.Height5()) + 1u, descriptor.fields[0], descriptor.fields[1],
			     descriptor.fields[2], descriptor.fields[3], descriptor.fields[4], descriptor.fields[5],
			     descriptor.fields[6], descriptor.fields[7]);
		}
	}

	// Memo: the same T# with the same resource shape resolves to the same image while that image
	// is alive, registered and not flagged for rediscovery. Exact backing matches only (an
	// overlap view could be superseded by a later exact image).
	auto&          memo         = Memo();
	const bool     memo2        = Common::Gates::Enabled(Common::Gates::Gate::TexMemo2);
	const uint64_t resource_key =
	    memo2 ? MemoResourceKey(memo, resource)
	          : MemoHashBytes(&resource,
	                          reinterpret_cast<const uint8_t*>(&resource.indirect_resources) -
	                              reinterpret_cast<const uint8_t*>(&resource));
	const uint64_t memo_hash =
	    MemoHashBytes(descriptor.fields, sizeof(descriptor.fields), resource_key);
	const uint32_t memo_index =
	    memo2 ? MemoTextureWay(memo, memo_hash)
	          : static_cast<uint32_t>(memo_hash % RenderExecutorMemo::TextureSlots);
	auto& memo_slot = memo.textures[memo_index];
	const bool memo_key_match =
	    memo_slot.valid && memo_slot.resource_key == resource_key &&
	    std::memcmp(memo_slot.dwords.data(), descriptor.fields, sizeof(descriptor.fields)) == 0;
	if (!memo_key_match) {
		Common::FrameStats::Add(memo_slot.valid ? Common::FrameStats::Counter::TexMemoCollide
		                                        : Common::FrameStats::Counter::TexMemoEmpty,
		                        1);
	}
	if (memo_key_match) {
		auto* cached = texture_cache.m_slot_images.try_get(memo_slot.image_id);
		if (cached != nullptr && cached->registered && !cached->binding.needs_rebind &&
		    !cached->depth_id && cached->info.data == memo_slot.desc.info.data &&
		    cached->info.extent == memo_slot.desc.info.extent) {
			// Session 88, knob "bindwit": THE MEMO-HIT DECISION IS COMPLETE HERE.  Everything
			// above is the proof that the earlier resolution of this descriptor is still valid -
			// DecodeNativeDescriptor, the resource key, the hash over the eight T# dwords, the
			// memo index, the 32-byte memcmp, the slot lookup and the five-field liveness check.
			// Everything below - ConfigureImageSource, tick_accessed_last, TouchImage, the DCC
			// adoption, the way clock and emit - is not, and is what a per-stage amortisation of a
			// duplicate image slot could skip.  NOTE: ConfigureImageSource has its own early-out
			// (textureCache.cpp:1244-1247) which is a liveness test in substance; it is counted on
			// the SKIPPABLE side, which makes the measured witness a LOWER bound and the ceiling
			// built on it an UPPER one.  pred/01 section 2 says so before the run.
			if (g_bind_wit_arm == 2) {
				g_bind_wit_mark = Common::FrameStats::NowNs();
			}
			texture_cache.ConfigureImageSource(memo_slot.image_id, memo_slot.desc);
			cached->tick_accessed_last = m_context.GetCommandScheduler().CurrentTick();
			texture_cache.TouchImage(*cached);
			if (!cached->info.IsDepth() && descriptor.MetaCompress() && descriptor.MetaAddr() != 0) {
				// The adoption itself only ever turns an image with no metadata into a DCC one;
				// for an image that already carries this exact DCC range it locks the cache to
				// answer "yes". That answer is readable here, on the same fields this path
				// already reads.
				const auto meta_address = descriptor.MetaAddr() << 8u;
				const bool settled      = Common::Gates::Enabled(Common::Gates::Gate::MetaLock) &&
				                     cached->info.metadata.kind == ImageMetadataKind::Dcc &&
				                     cached->info.metadata.range.address == meta_address;
				if (!settled) {
					(void)texture_cache.AdoptPendingDccForTexture(memo_slot.image_id, meta_address);
				}
			}
			Common::FrameStats::Add(Common::FrameStats::Counter::BindTexMemoHits, 1);
			if (memo2) {
				memo.texture_ways[memo_index].use = ++memo.texture_clock;
			}
			// Session 88, knob "bindwit" = 1: the END of the memo-hit tail.  It is taken HERE, in
			// the same function and with the same independent work still ahead of it, rather than
			// in the caller after the resolve returns: on wit88a the caller position exposed the
			// rdtsc latency the inside position hides, the two arms differed by 2.84 ns a slot in
			// bl_res_us, and null control C8 FAILED at -3.78 % against its +-3 % band.  The
			// interval therefore excludes emit, which an amortisation would still have to do.
			if (g_bind_wit_arm == 1) {
				g_bind_wit_mark = Common::FrameStats::NowNs();
			}
			return emit(memo_slot.image_id, memo_slot.desc, memo_index,
			                          memo_slot.version);
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::TexMemoStale, 1);
		Common::DrawStat::Mark(Common::DrawStat::Memo);
		memo_slot.valid = false;
		memo_slot.version++;
		memo_slot.fast_view = nullptr;
	}

	const auto address      = descriptor.Base40();
	const auto width        = static_cast<uint32_t>(descriptor.Width5()) + 1u;
	const auto height       = static_cast<uint32_t>(descriptor.Height5()) + 1u;
	const auto base_level   = descriptor.BaseLevel();
	const auto last_level   = descriptor.LastLevel();
	const auto type         = TextureType(descriptor);
	const bool multisampled = IsMultisampledTexture(type);
	auto max_mip = resource.r128 ? last_level : descriptor.MaxMip();
	// Storage views address their mip level from the surface layout and ignore max_mip, and
	// games do bind a stale max_mip together with a higher base/last level when they write the
	// tail of a mip chain (ASTRO BOT downsampling a 480x270 buffer). Extend the level count.
	if (storage && !multisampled && last_level > max_mip) {
		max_mip = last_level;
	}
	const auto levels = multisampled ? 1u : static_cast<uint32_t>(max_mip) + 1u;
	const bool dynamic_storage =
	    storage && resource.mip_mode == ShaderRecompiler::IR::ImageMipMode::DynamicStorage;
	const auto view_last_level =
	    !multisampled && !dynamic_storage ? std::min(last_level, max_mip) : last_level;
	const auto tile       = descriptor.TileMode();
	const bool depth_tile = tile == Prospero::TileMode::kDepth;
	const bool msaa_tile  = depth_tile || tile == Prospero::TileMode::kRenderTarget;
	const bool msaa_array = type == Prospero::ImageType::kColor2DMsaaArray;
	if ((!multisampled && (base_level > view_last_level || view_last_level >= levels)) ||
	    (multisampled &&
	     (base_level != 0 || last_level == 0 || last_level > 3 || max_mip != last_level ||
	      !msaa_tile || (descriptor.MsaaDepth() && !depth_tile) ||
	      (!msaa_array && (descriptor.Depth() != 0 || descriptor.BaseArray5() != 0))))) {
		EXIT("unsupported texture mip view: base=%u last=%u levels=%u max=%u type=%u tile=%u "
		     "class=%u numeric=%u dimension=%u mip_mode=%u read=%d written=%d "
		     "dwords=%08x,%08x,%08x,%08x,%08x,%08x,%08x,%08x\n",
		     base_level, last_level, levels, descriptor.MaxMip(),
		     static_cast<uint32_t>(descriptor.Type()), static_cast<uint32_t>(tile),
		     static_cast<uint32_t>(resource.resource_class),
		     static_cast<uint32_t>(resource.numeric_class),
		     static_cast<uint32_t>(resource.dimension), static_cast<uint32_t>(resource.mip_mode),
		     resource.read, resource.written, descriptor.fields[0], descriptor.fields[1],
		     descriptor.fields[2], descriptor.fields[3], descriptor.fields[4], descriptor.fields[5],
		     descriptor.fields[6], descriptor.fields[7]);
	}
	const auto samples = multisampled ? 1u << last_level : 1u;
	const auto view_levels =
	    multisampled ? 1u : static_cast<uint32_t>(view_last_level - base_level) + 1u;
	const auto depth          = static_cast<uint32_t>(descriptor.Depth()) + 1u;
	const auto format         = descriptor.Format();
	const auto surface_format = TextureGetSurfaceFormatInfo(format);
	const bool shader_conversion =
	    surface_format.conversion_format != Prospero::BufferFormat::kInvalid;
	const bool sampled_numeric_class =
	    storage || resource.numeric_class == Prospero::SampledTextureNumericClass(format);
	if (!storage && resource.resource_class == ShaderRecompiler::IR::ImageResourceClass::Sampled &&
	    !sampled_numeric_class) {
		EXIT("sampled image numeric class mismatch: numeric=%u format=%u addr=0x%016" PRIx64 "\n",
		     static_cast<uint32_t>(resource.numeric_class), static_cast<uint32_t>(format), address);
	}

	const bool    volume       = type == Prospero::ImageType::kColor3D;
	const bool    layered      = type == Prospero::ImageType::kColor1DArray ||
	                             type == Prospero::ImageType::kColor2DArray ||
	                             type == Prospero::ImageType::kColor2DMsaaArray;
	const auto    image_layers = layered ? depth : 1u;
	uint32_t      pitch        = 0;
	TileSizeAlign size {};
	if (multisampled) {
		const auto bytes = Prospero::NumBytesPerElement(format);
		pitch            = depth_tile ? TileGetDepthPitch(width, bytes, last_level)
		                              : TileGetRenderTargetPitch(width, bytes, last_level);
		if (pitch == 0 || !TileGetRenderTargetSize(width, height, pitch, bytes, size, last_level) ||
		    size.size > UINT32_MAX / image_layers) {
			EXIT("unsupported multisample texture layout\n");
		}
		size.size *= image_layers;
	} else {
		pitch = TileGetTexturePitch(format, width, tile);
		TileGetTextureTotalSize(format, width, height, volume ? depth : image_layers, levels, tile,
		                        volume, size);
	}
	EXIT_NOT_IMPLEMENTED(size.size == 0 || size.align == 0 ||
	                     (address & (static_cast<uint64_t>(size.align) - 1u)) != 0);
	if (storage) {
		ValidateStorageTexture(resource, descriptor, size.size);
	}

	auto pixel_format = surface_format.vk_format;
	if (resource.depth_compare) {
		if (const auto* depth_format = FindGuestDepthFormatPolicy(format)) {
			pixel_format = depth_format->depth_attachment_format;
		}
	}
	const auto storage_view_format = storage && format == Prospero::BufferFormat::k32SInt
	                                     ? vk::Format::eR32Uint
	                                     : SrgbStorageViewFormat(pixel_format);
	const auto view_format         = storage && storage_view_format != vk::Format::eUndefined
	                                     ? storage_view_format
	                                     : pixel_format;
	const auto block_bytes         = Prospero::BlockCompressedBytesPerBlock(format);
	TextureCache::ImageDesc desc {};
	desc.info.data         = {address, size.size};
	desc.info.pixel_format = pixel_format;
	desc.info.guest_format = format;
	desc.info.type         = TextureBaseType(type);
	desc.info.extent       = {width, height, volume ? depth : 1u};
	desc.info.resources    = {levels, image_layers};
	desc.info.pitch        = pitch;
	desc.info.bytes_per_block =
	    block_bytes != 0 ? block_bytes : Prospero::NumBytesPerElement(format);
	desc.info.samples   = samples;
	desc.info.tile_mode = tile;
	if (!resource.r128 && descriptor.MetaCompress() && tile != Prospero::TileMode::kDepth &&
	    !desc.info.IsDepth()) {
		TileSizeAlign metadata_size {};
		(void)TileGetDccSize(width, height, volume ? depth : image_layers,
		                     desc.info.bytes_per_block, levels, tile, metadata_size,
		                     std::countr_zero(samples));
		desc.info.metadata.kind          = ImageMetadataKind::Dcc;
		desc.info.metadata.range         = {descriptor.MetaAddr() << 8u, metadata_size.size};
		desc.info.metadata.dcc_alpha_msb = descriptor.DccAlphaPos();
	}
	if (samples > 1) {
		desc.info.mip_layout[0] = {0, size.size, pitch, height};
	} else {
		PopulateTextureMipLayout(desc.info);
	}
	desc.view_info = TextureViewInfo(resource, descriptor, view_format, surface_format, storage,
	                                 view_levels, desc.info.resources.layers,
	                                 m_context.GetGraphics().image_view_min_lod_enabled);
	desc.type = storage ? TextureCache::BindingType::Storage : TextureCache::BindingType::Texture;

	auto       id                  = texture_cache.FindImage(desc, shader_conversion);
	auto*      image               = &texture_cache.GetImage(id);
	const bool stencil_association = static_cast<bool>(image->depth_id);
	if (stencil_association) {
		id    = image->depth_id;
		image = &texture_cache.GetImage(id);
	} else if (image->info.IsDepth()) {
		if (storage) {
			EXIT("depth target cannot be bound as a storage image\n");
		}
		ValidateSampledDepthBinding(resource, descriptor, *image, pixel_format, size.size);
	} else {
		if (storage) {
			ValidateStorageColorView(image->info.pixel_format, view_format,
			                         descriptor.DstSelXYZW());
		} else {
			(void)SelectSampledColorView(image->info.pixel_format, pixel_format,
			                             descriptor.DstSelXYZW());
		}
		// ASTRO BOT fast-clears a half-resolution RGBA16F surface through a DCC metadata fill
		// and, in frames with nothing to composite, samples it straight away without ever
		// binding it as a colour target. The fill stays PendingDcc (only FindRenderTarget
		// registers DCC), the host image keeps stale memory instead of the (0,0,0,1) clear and
		// the composite pass overwrites the whole scene with it (black cutscene frames).
		// Adopt the pending fill here so CommitBindings materializes the clear.
		if (descriptor.MetaCompress() && descriptor.MetaAddr() != 0) {
			(void)texture_cache.AdoptPendingDccForTexture(id, descriptor.MetaAddr() << 8u);
		}
	}
	const bool store = !stencil_association && image->info.data == desc.info.data &&
	                   image->info.extent == desc.info.extent;
	if (store) {
		std::memcpy(memo_slot.dwords.data(), descriptor.fields, sizeof(descriptor.fields));
		Common::DrawStat::Mark(Common::DrawStat::Memo);
		memo_slot.resource_key = resource_key;
		memo_slot.image_id     = id;
		memo_slot.desc         = desc;
		memo_slot.valid        = true;
		memo_slot.version++;
		memo_slot.fast_view = nullptr;
		if (memo2) {
			memo.texture_ways[memo_index] = {memo_hash, ++memo.texture_clock};
		}
	}
	return emit(id, desc, store ? memo_index : UINT32_MAX,
	                          store ? memo_slot.version : 0u);
}

TextureBinding RenderExecutor::ResolveTexture(const ShaderRecompiler::IR::ImageResource&   resource,
                                              const ShaderRecompiler::IR::DescriptorValue& value) {
	return ResolveTextureWith(resource, value,
	                          [](ImageId id, const TextureCache::ImageDesc& desc,
	                             uint32_t index = UINT32_MAX, uint32_t version = 0) {
		                          return TextureBinding(id, desc, index, version);
	                          });
}

RenderExecutorMemo& RenderExecutor::Memo() {
	if (!m_memo) {
		m_memo = std::make_shared<RenderExecutorMemo>();
	}
	return *m_memo;
}

static vk::Sampler NativeSampler(RenderContext&                       context,
                                 const ShaderRecompiler::IR::CompiledShaderInfo& program,
                                 uint32_t index,
                                 const ShaderRecompiler::IR::DescriptorValue& value) {
	Common::FrameStats::Scope sampler_scope(Common::FrameStats::Counter::BindSamplersNs);
	auto descriptor = DecodeNativeDescriptor<ShaderSamplerResource>(value);
	if (!program.info.samplers[index].depth_compare) {
		descriptor.fields[0] &= ~(0x7u << 12u);
	}
	if (program.info.samplers[index].force_point_filtering) {
		descriptor.SetPointFiltering();
	}
	return context.GetSamplerCache().GetSampler(descriptor);
}

// Session 95, gate "framerep" (measurement only): FNV-1a over 64-bit words.  Cheap, and
// the question it answers is "are these bytes the same as some draw's last frame", which
// a non-cryptographic hash answers at a collision rate far below the counters' resolution
// (2^-64 a pair against ~5 000 draws a frame).
static inline uint64_t FrameRepMix(uint64_t h, uint64_t v) {
	h ^= v;
	h *= 0x100000001b3ull;
	return h;
}

static uint64_t FrameRepWords(std::span<const uint32_t> data) {
	uint64_t     h = 0xcbf29ce484222325ull;
	const size_t n = data.size();
	size_t       i = 0;
	for (; i + 1 < n; i += 2) {
		h = FrameRepMix(h, (static_cast<uint64_t>(data[i + 1]) << 32u) |
		                       static_cast<uint64_t>(data[i]));
	}
	if (i < n) {
		h = FrameRepMix(h, static_cast<uint64_t>(data[i]));
	}
	return FrameRepMix(h, static_cast<uint64_t>(n));
}

static vk::DescriptorBufferInfo NativeUpload(RenderContext&            context,
                                             std::span<const uint32_t> data) {
	EXIT_IF(data.empty());
	// Session 68, gate "amut": a copy into the stream ring (the flattened SRT and the shader data).
	Common::FrameStats::MutScope mutate_scope(
	    Common::Gates::Enabled(Common::Gates::Gate::MutateTime));
	auto& command_buffer = context.GetCommandScheduler().Current();
	EXIT_IF(command_buffer.IsInvalid());
	auto&      buffer = context.GetBufferCache().GetUtilityBuffer(MemoryUsage::Stream);
	const auto offset = buffer.Copy(data.data(), data.size_bytes(), 256);
	return {buffer.Handle(), offset, data.size_bytes()};
}

void RenderExecutor::BindImage(ImageId id, bool storage, bool atomic) {
	auto& image = m_context.GetTextureCache().GetImage(id);
	if (image.info.data.Empty()) {
		return;
	}
	if (image.binding.is_bound) {
		image.binding.force_general |= image.binding.shader_write != storage;
	}
	image.binding.is_bound = true;
	image.binding.shader_write |= storage;
	// Gate "atomimg": the claim is per image, not per descriptor. One plain store through any
	// binding of this draw disqualifies the image even if another binding is atomic-only.
	// ImageResource::atomic says the shader uses image atomics on this resource, not that it
	// uses nothing else: ResourceTracking merges Write and Atomic into the same `written` flag.
	// A scan of this title's whole translation cache found 18 atomic-only descriptors, 104
	// plain-store-only and no mixed one, which is what makes the predicate exact here -- and
	// why the gate stays off by default.
	image.binding.shader_write_plain |= storage && !atomic;
	m_bound_images.push_back(id);
}

namespace {

// Upstream ea092a9: a DCC fast clear is encoded in the format its consumer views the surface
// through, not in the format of the host allocation. An image whose allocation is UNORM can be
// reused for a FLOAT descriptor (SameBacking / FormatsCompatible), and then the clear has to be
// written as 0x3c00, not as the UNORM 0xffff a transfer clear produces -- the FLOAT view reads
// that back as NaN. TextureCache::PrepareDccClear takes the format from the ImageDesc it is
// called with; RenderExecutor::MaterializeDeferredDccClear is declared in render.h without one
// and its two callers differ: the shader-binding path (CommitBindings) knows the view format of
// the binding that is about to read the surface, the fast-clear-eliminate register scan
// (MaterializeBoundTargetDccClears) has no descriptor at all. The binding path publishes its
// view format here for the duration of the call; eUndefined means "no consumer known" and the
// clear is then encoded in the allocation format, exactly as before.
// TODO(merge): give both MaterializeDeferredDccClear overloads a `vk::Format view_format`
// parameter in render.h and drop this hint.
thread_local vk::Format g_dcc_clear_view_format = vk::Format::eUndefined;

class DccClearViewFormat {
public:
	explicit DccClearViewFormat(vk::Format format) noexcept : m_saved(g_dcc_clear_view_format) {
		g_dcc_clear_view_format = format;
	}
	// Restores rather than clears: a nested call (none today) must not lose the outer hint.
	~DccClearViewFormat() { g_dcc_clear_view_format = m_saved; }
	KYTY_CLASS_NO_COPY(DccClearViewFormat);

private:
	vk::Format m_saved;
};

} // namespace

// A guest DCC fast clear only rewrites metadata, and the attachment path materializes it as a
// load-op clear when the surface is next bound as a colour attachment. ASTRO BOT clears its
// scene colour buffer, lights the deferred save-card tiles with compute image stores and only then
// binds the buffer as an attachment: the load-op clear erased the compute output and the cards
// stayed black. Clear the host image before any shader binding touches it and consume the
// metadata state so the later attachment bind loads instead of clearing.
void RenderExecutor::MaterializeDeferredDccClear(CommandBuffer& buffer, ImageId id) {
	MaterializeDeferredDccClear(buffer, id, m_context.GetTextureCache().GetImage(id));
}

void RenderExecutor::MaterializeDeferredDccClear(CommandBuffer& buffer, ImageId id, Image& image) {
	auto& cache = m_context.GetTextureCache();
	if (image.info.data.Empty() || image.info.IsDepth() || image.backing.image == nullptr ||
	    image.depth_id || !image.registered ||
	    image.info.metadata.kind != ImageMetadataKind::Dcc) {
		return;
	}
	const auto address = image.info.metadata.range.address;
	const auto layers  = std::min(image.info.resources.layers, 32u);
	uint32_t   fill    = 0xffffffffu;
	uint32_t   mask    = 0;
	if (Common::Gates::Enabled(Common::Gates::Gate::MetaLock)) {
		const auto layer_mask = layers >= 32u ? UINT32_MAX : (uint32_t {1} << layers) - 1u;
		mask                  = cache.MetaClearMask(address, &fill) & layer_mask;
	} else {
		for (uint32_t layer = 0; layer < layers; layer++) {
			if (cache.IsMetaCleared(address, layer, &fill)) {
				mask |= 1u << layer;
			}
		}
	}
	if (mask == 0) {
		return;
	}
	// Encode the clear in the format its consumer views the surface through (ea092a9) -- the
	// same rule TextureCache::PrepareDccClear applies to the metadata state it owns. The
	// aliased encoding goes through TextureCache::ClearImage, which renders the clear into a view
	// of that format; it can only do that for a single-level, single-sample, non-volume colour
	// image, so every other case keeps the transfer clear in the allocation format this path
	// always used. `g_dcc_clear_view_format` is the binding's view format, or eUndefined when the
	// caller has no descriptor (the register scan below).
	const auto native_format = image.info.pixel_format; // allocation format, == backing.format
	const bool can_alias = g_dcc_clear_view_format != vk::Format::eUndefined &&
	                       g_dcc_clear_view_format != image.backing.format &&
	                       image.info.resources.levels == 1 && image.info.samples == 1 &&
	                       !image.info.IsVolume();
	auto                clear_format = can_alias ? g_dcc_clear_view_format : native_format;
	const auto          code         = static_cast<uint8_t>(fill);
	vk::ClearColorValue clear {};
	// Decodes the pending key into `clear` the way `format` encodes it. Both the value and the
	// union member it lands in belong to that format, so the clear has to be written through
	// that very format and no other.
	const auto decode = [&](vk::Format format) -> bool {
		if (code == 0x20) {
			// Register-backed clear: use the clear word of the colour slot that still addresses
			// the surface. Without one the attachment path keeps handling it.
			const auto& hw = buffer.GetRegisters();
			for (uint32_t slot = 0; slot < 8; slot++) {
				const auto& rt = hw.GetRenderTarget(slot);
				if (rt.base.addr == image.info.data.address && rt.dcc_addr.addr == address &&
				    DecodePackedColorClear(format, rt.clear_word0.word0, rt.clear_word1.word1,
				                           clear)) {
					return true;
				}
			}
			return false;
		}
		return DecodeFixedDccClear(format, code, clear);
	};
	bool decoded = decode(clear_format);
	if (!decoded && can_alias) {
		// The consumer's view format has no DCC clear encoding of its own (a scaled or snorm
		// alias of the allocation, say): fall back to the allocation format and the transfer
		// clear this path always used. Declining instead would leave the surface stale AND its
		// metadata unconsumed, so the next attachment bind would load-op clear it over whatever
		// the shader wrote -- the exact bug this path exists to avoid.
		clear_format = native_format;
		decoded      = decode(clear_format);
	}
	// ClearImage's own condition for rendering through a view instead of a transfer clear.
	const bool aliased = clear_format != image.backing.format;
	static std::atomic<uint32_t> log_count = 0;
	static const bool dcc_trace = std::getenv("KYTY_DCC_TRACE") != nullptr;
	if (dcc_trace || log_count++ < 32) {
		LOGF("MaterializeDeferredDccClear: image=0x%016" PRIx64 " dcc=0x%016" PRIx64
		     " code=0x%02x layers=0x%08x format=%u view=%u decoded=%d\n",
		     image.info.data.address, address, static_cast<uint32_t>(code), mask,
		     static_cast<uint32_t>(image.info.pixel_format),
		     static_cast<uint32_t>(clear_format), decoded ? 1 : 0);
	}
	if (!decoded) {
		return;
	}
	Common::DrawStat::Mark(Common::DrawStat::ImgUp | Common::DrawStat::Meta);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	buffer.EndRendering(RenderPassEnd::Clear);
	if (!aliased) {
		image.Transit(vk::ImageLayout::eTransferDstOptimal, vk::AccessFlagBits2::eTransferWrite, {},
		              buffer.Handle());
	}
	for (uint32_t layer = 0; layer < layers; layer++) {
		if ((mask & (1u << layer)) == 0) {
			continue;
		}
		uint32_t count = 1;
		while (layer + count < layers && (mask & (1u << (layer + count))) != 0) {
			count++;
		}
		const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, 0,
		                                       image.info.resources.levels, layer, count};
		if (aliased) {
			// Reuse the encoder upstream fixed instead of repeating it: ClearImage transits the
			// image, renders the clear through a view of `clear_format` and commits the GPU
			// write. It reads and writes texture cache state, so it runs under the cache lock
			// like every other caller; nothing here holds that lock (MetaClearMask above and
			// TouchMeta below take it themselves).
			vk::ClearValue value {};
			value.color = clear;
			std::scoped_lock lock {cache.m_lock};
			cache.ClearImage(buffer, id, clear_format, range, value);
		} else {
			buffer.Handle().clearColorImage(image.backing.image,
			                                vk::ImageLayout::eTransferDstOptimal, &clear, 1,
			                                &range);
		}
		m_context.GetCommandScheduler().GpuMark(GpuTimeProfiler::Kind::Clear, 1);
		for (uint32_t consumed = layer; consumed < layer + count; consumed++) {
			if (!cache.TouchMeta(address, consumed, false)) {
				EXIT("failed to consume DCC clear state for a shader binding\n");
			}
		}
		layer += count - 1;
	}
	cache.MarkGpuWritten(id);
}

// A fast-clear-eliminate / DCC-decompress draw (CB_COLOR_CONTROL.MODE 2/6) binds the surface as
// a colour target with the CLEAR_WORD registers of its fast clear still loaded. Kyty skips the
// draw itself (host images are never compressed), but this is the last point where a
// register-backed clear (code 0x20) is decodable: after it the surface is only sampled and the
// registers move on to other targets. ASTRO BOT's cutscenes clear RGBA16F G-buffer/upscale
// surfaces this way and never bind them as attachments again before sampling them.
void RenderExecutor::MaterializeBoundTargetDccClears(CommandBuffer& buffer) {
	auto&       cache = m_context.GetTextureCache();
	const auto& hw    = buffer.GetRegisters();
	for (uint32_t slot = 0; slot < 8; slot++) {
		const auto& rt = hw.GetRenderTarget(slot);
		if (rt.base.addr != 0 && rt.cmask.addr != 0 && rt.info.cmask_fast_clear_enable &&
		    !rt.info.dcc_compression_enable) {
			RenderColorInfo color {};
			ResolveRenderColorTarget(buffer, color, 0, slot, true, true);
			if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {
				// Session 71, candidate C3 (counters only): the second entrance into
				// FindRenderTarget, which rt_fast_no never sees. Hand it the same registers the
				// branch above already tested, so c3_ct covers it and c3_ct + c3_dt - rt_fast_no
				// measures how often this path runs.
				(void)cache.FindRenderTarget(
				    color.image_id, color.desc,
				    (rt.info.cmask_fast_clear_enable ? TextureCache::kRegColorFastClear : 0u) |
				        (rt.cmask.addr != 0 ? TextureCache::kRegColorCmaskAddr : 0u) |
				        (rt.info.dcc_compression_enable ? TextureCache::kRegColorDccEnable : 0u) |
				        (rt.dcc_addr.addr != 0 ? TextureCache::kRegColorDccAddr : 0u) |
				        (rt.dcc.dcc_clear_key_enable ? TextureCache::kRegColorDccKey : 0u));
			}
			continue;
		}
		if (rt.base.addr == 0 || rt.dcc_addr.addr == 0) {
			continue;
		}
		const auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr);
		if (!id) {
			static std::atomic<uint32_t> miss_count = 0;
			static const bool dcc_trace = std::getenv("KYTY_DCC_TRACE") != nullptr;
			if (dcc_trace || miss_count++ < 32) {
				LOGF("MaterializeBoundTargetDccClears: no image for slot=%u base=0x%016" PRIx64
				     " dcc=0x%016" PRIx64 "\n",
				     slot, rt.base.addr, rt.dcc_addr.addr);
			}
			continue;
		}
		MaterializeDeferredDccClear(buffer, id);
	}
}

void RenderExecutor::BindRenderTarget(ImageId id) {
	auto& image             = m_context.GetTextureCache().GetImage(id);
	image.binding.is_target = true;
	m_bound_images.push_back(id);
}

void RenderExecutor::ResetBindings() {
	for (const auto id: m_bound_images) {
		if (auto* image = m_context.GetTextureCache().m_slot_images.try_get(id); image != nullptr) {
			image->binding = {};
		}
	}
	m_bound_images.clear();
}

bool RenderExecutor::ReuseBindingsEnabled() {
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_REUSE_BINDINGS");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

PreparedBindings RenderExecutor::PrepareBindings(const ShaderStageRuntime& runtime) {
	PreparedBindings prepared;
	PrepareBindings(runtime, prepared);
	return prepared;
}

namespace {

// Session 82, gate "bindkey" (measurement only).  FNV-1a over the inputs a binding memo would have
// to key on: the shader, every descriptor dword of the snapshot, and the user-data dwords the
// program reads.  Nothing here is used for a decision - see gates.h.
// Session 83, gate "bindpack" (PLAN_82_bind.md item 4). IR::FindBinding is an out-of-line
// linear scan of layout.descriptors, and a stage asks it three questions about the SAME
// layout: Gds here, FlattenedSrt and ShaderData in FindBuffers, whose `layout` IS
// program.bindings. One pass answers all three. Bit 3 marks the mask computed, so a zero
// mask can never be mistaken for "nothing present".
constexpr uint32_t KIND_GDS           = 1u;
constexpr uint32_t KIND_FLATTENED_SRT = 2u;
constexpr uint32_t KIND_SHADER_DATA   = 4u;
constexpr uint32_t KIND_COMPUTED      = 8u;

uint32_t BindingKindMask(const ShaderRecompiler::IR::BindingLayout& layout) {
	uint32_t mask = KIND_COMPUTED;
	for (const auto& binding: layout.descriptors) {
		switch (binding.kind) {
			case ShaderRecompiler::IR::DescriptorBindingKind::Gds: mask |= KIND_GDS; break;
			case ShaderRecompiler::IR::DescriptorBindingKind::FlattenedSrt:
				mask |= KIND_FLATTENED_SRT;
				break;
			case ShaderRecompiler::IR::DescriptorBindingKind::ShaderData:
				mask |= KIND_SHADER_DATA;
				break;
			default: break;
		}
	}
	return mask;
}

// The self-check of gate "bindpackcheck": the bit and the scan must agree, always.
void VerifyKind(uint32_t mask, uint32_t bit,
                const ShaderRecompiler::IR::BindingLayout&  layout,
                ShaderRecompiler::IR::DescriptorBindingKind kind) {
	const bool fast = (mask & bit) != 0;
	const bool slow = ShaderRecompiler::IR::FindBinding(layout, kind) != nullptr;
	if (fast == slow) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::BindPackBad, 1);
	static std::atomic<uint32_t> logged {0};
	if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
		LOGF("BindPackVerify: MISMATCH kind=%u fast=%u slow=%u\n",
		     static_cast<uint32_t>(kind), static_cast<uint32_t>(fast),
		     static_cast<uint32_t>(slow));
	}
}

uint64_t BindingInputKey(const ShaderRecompiler::IR::CompiledShaderInfo& program,
                         const ShaderRecompiler::IR::ResourceSnapshot& snapshot) {
	uint64_t h = 1469598103934665603ULL;
	auto mix   = [&h](uint64_t value) {
		for (int i = 0; i < 8; i++) {
			h ^= static_cast<uint8_t>(value >> (i * 8));
			h *= 1099511628211ULL;
		}
	};
	mix(program.shader_hash);
	auto mix_values = [&](const std::vector<ShaderRecompiler::IR::DescriptorValue>& values) {
		mix(values.size());
		for (const auto& value: values) {
			mix(value.dword_count);
			for (uint32_t i = 0; i < value.dword_count && i < value.dwords.size(); i++) {
				mix(value.dwords[i]);
			}
		}
	};
	mix_values(snapshot.images);
	mix_values(snapshot.samplers);
	mix_values(snapshot.buffers);
	for (const auto reg: program.bindings.user_data_registers) {
		const auto index = reg - program.user_data_base;
		mix(index < snapshot.user_data.size() ? snapshot.user_data[index] : 0u);
	}
	return h == 0 ? 1 : h;
}

} // namespace

void RenderExecutor::PrepareBindings(const ShaderStageRuntime& runtime, PreparedBindings& prepared) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(!runtime);
	const auto& program  = *runtime.program;
	const auto& snapshot = runtime.resources;
	// Session 85, gate "bindlap" (MEASUREMENT ONLY): the whole body, because every return
	// path has to be covered and a hand-written epilogue on each is how a lap gets lost.
	const bool                   bind_lap = Common::Gates::Enabled(Common::Gates::Gate::BindLap);
	Common::FrameStats::LapScope bind_lap_scope(bind_lap,
	                                            Common::FrameStats::Counter::BindLapPrepareNs);
	if (bind_lap) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapPrepares, 1);
	}
	prepared.Reset();
	prepared.runtime = &runtime;
	if (Common::Gates::Enabled(Common::Gates::Gate::BindPack)) {
		prepared.kind_mask = BindingKindMask(program.bindings);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindKindMasks, 1);
	}
	if (Common::Gates::Enabled(Common::Gates::Gate::BindKeyStat)) {
		// One slot per shader stage: consecutive draws are compared stage against stage.
		thread_local std::array<uint64_t, 16> previous_key {};
		const auto slot  = static_cast<uint32_t>(program.stage) % previous_key.size();
		prepared.key     = BindingInputKey(program, snapshot);
		prepared.key_hit = (previous_key[slot] != 0 && previous_key[slot] == prepared.key);
		previous_key[slot] = prepared.key;
		Common::FrameStats::Add(prepared.key_hit ? Common::FrameStats::Counter::BindKeyHit
		                                         : Common::FrameStats::Counter::BindKeyMiss,
		                        1);
	}
	// Session 86, D3: the rolling mark chain.  `bind_lap` is the gate value already read
	// above; the Enabled() half deliberately matches LapScope, so the split cannot record
	// into counters the frame will not print.
	uint64_t bl_t = bind_lap && Common::FrameStats::Enabled() ? Common::FrameStats::NowNs() : 0;
	// Session 87, gate "bindalt" (MEASUREMENT ONLY): ONE timestamp a slot, taken after the
	// resolve on half the stages and after the bind on the other half, so that an interval which
	// opens after a bind and closes after a resolve is exactly one ResolveTextureWith.  The
	// per-stage phase alternates, so every slot index is sampled in half the stages and the
	// sample is unbiased for the whole population.  Nothing is reordered: a two-pass split would
	// defer BindImage past the next slot's resolve, and BindImage writes Image::binding.is_bound,
	// which ConfigureImageSourceUnlocked (textureCache.cpp:1226 - "several bindings in one draw
	// may expose different LOD ranges of the same image"), ResolveOverlap, ResolveDepthOverlap
	// and ExpandImage all read, and which FindImage can invalidate by freeing the id outright.
	// The mark's own cost rides in every sampled interval AND once in every slot of bl_res_us,
	// so it cancels in bl_res_us/n - bl_rsv_us/n (pred/01 section 4).
	const bool                   bind_alt = bl_t != 0 && Common::Gates::Enabled(Common::Gates::Gate::BindAlt);
	static thread_local uint32_t bl_alt_stage = 0;
	const uint32_t               bl_alt_phase = bind_alt ? (bl_alt_stage++ & 1u) : 0;
	uint64_t                     bl_alt_t     = bl_t;
	uint64_t                     bl_alt_acc = 0;
	uint64_t                     bl_alt_acc0 = 0;
	uint32_t                     bl_alt_n = 0;
	uint32_t                     bl_alt_n0 = 0;
	// Session 88, knob "bindwit" (MEASUREMENT ONLY): the same one-mark-a-slot,
	// alternating-phase idiom as bindalt, with the mark MOVED rather than added.  At 1 it
	// closes after ResolveTextureWith returns, where bindalt closes it; at 2 it closes at the
	// memo-hit decision inside the resolve.  Both pay exactly one timestamp a slot, so the
	// price of the mark cancels EXACTLY in the arm difference and never has to be estimated -
	// the defect that made session 87 prediction A8 unevaluable.  Slots whose resolve did not
	// take the memo-hit path cannot be marked inside and go to bl_wnh_* instead: identical
	// code in both arms, so they are a null control that CAN fail.
	const uint32_t bind_wit = bl_t != 0 ? Common::Gates::Value(Common::Gates::Knob::BindWitness) : 0;
	static thread_local uint32_t bl_wit_stage = 0;
	const uint32_t               bl_wit_phase = bind_wit != 0 ? (bl_wit_stage++ & 1u) : 0;
	uint64_t                     bl_wit_t     = bl_t;
	uint64_t                     bl_wit_acc   = 0;
	uint64_t                     bl_wit_acc0  = 0;
	uint64_t                     bl_wnh_acc   = 0;
	uint32_t                     bl_wit_n     = 0;
	uint32_t                     bl_wit_n0    = 0;
	uint32_t                     bl_wnh_n     = 0;
	// Session 100, gate "blmove" (MEASUREMENT ONLY): two timestamps a stage in BOTH phases.
	// The phase alternates per stage TYPE (the `previous_key` idiom above), so each type
	// contributes equally to the two spans and the difference is not a comparison of unlike
	// stages.  Opened here, closed once - after the image loop in phase 0, after the
	// shader_data copy in phase 1.  Nothing between the two close sites is reordered.
	const bool blm = Common::FrameStats::Enabled() &&
	                 Common::Gates::Enabled(Common::Gates::Gate::BindLapMove);
	static thread_local std::array<uint32_t, 16> blm_turn {};
	const uint32_t blm_phase =
	    blm ? (blm_turn[static_cast<uint32_t>(program.stage) % blm_turn.size()]++ & 1u) : 0;
	const uint64_t blm_t0 = blm ? Common::FrameStats::NowNs() : 0;
	prepared.images.reserve(program.info.images.size());
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		if (bind_wit != 0) {
			// Armed PER SLOT, not for the whole loop: a stamp taken on a slot the alternating
			// phase does not sample is read by nobody and would be a SECOND timestamp on about
			// half the memo hits, breaking the symmetry that lets the price of the mark cancel.
			g_bind_wit_mark = 0;
			g_bind_wit_arm  = ((i & 1u) == bl_wit_phase) ? bind_wit : 0;
		}
		// Session 57, B2a: built in its vector element - one ImageDesc copy where the returned
		// binding and push_back made two. Reserved above, so no reallocation; BindImage does not
		// look at prepared.images, so running it after the insertion changes nothing.
		auto& binding = ResolveTextureWith(
		    program.info.images[i], snapshot.images[i],
		    [&prepared](ImageId id, const TextureCache::ImageDesc& desc, uint32_t index = UINT32_MAX,
		                uint32_t version = 0) -> TextureBinding& {
			    return prepared.images.emplace_back(id, desc, index, version);
		    });
		if (bind_alt && (i & 1u) == bl_alt_phase) {
			const auto bl_alt_now = Common::FrameStats::NowNs();
			if (i == 0) {
				bl_alt_acc0 = bl_alt_now - bl_alt_t;
				bl_alt_n0   = 1;
			} else {
				bl_alt_acc += bl_alt_now - bl_alt_t;
				bl_alt_n++;
			}
			bl_alt_t = bl_alt_now;
		}
		if (bind_wit != 0 && (i & 1u) == bl_wit_phase) {
			// g_bind_wit_mark is 0 when the resolve did not take the memo-hit path, 1 when it did
			// but this arm takes no timestamp inside, and a timestamp when it did and this arm
			// does.  Exactly one NowNs() is paid either way.
			const uint64_t stamped    = g_bind_wit_mark;
			const bool     hit        = stamped != 0;
			const uint64_t bl_wit_now = hit ? stamped : Common::FrameStats::NowNs();
			if (i == 0) {
				bl_wit_acc0 = bl_wit_now - bl_wit_t;
				bl_wit_n0   = 1;
			} else if (hit) {
				bl_wit_acc += bl_wit_now - bl_wit_t;
				bl_wit_n++;
			} else {
				bl_wnh_acc += bl_wit_now - bl_wit_t;
				bl_wnh_n++;
			}
			bl_wit_t = bl_wit_now;
		}
		BindImage(binding.image_id, binding.desc.type == TextureCache::BindingType::Storage,
		          program.info.images[i].atomic);
		if (bind_alt && (i & 1u) != bl_alt_phase) {
			bl_alt_t = Common::FrameStats::NowNs();
		}
		if (bind_wit != 0 && (i & 1u) != bl_wit_phase) {
			bl_wit_t = Common::FrameStats::NowNs();
		}
	}
	// The repair loop of RebindImages calls the same template through ResolveTexture; it must
	// not mark, so the arming ends with the loop.
	g_bind_wit_arm = 0;
	if (bl_t != 0) {
		const auto bl_now = Common::FrameStats::NowNs();
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapResolveNs, bl_now - bl_t);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapResolves,
		                        program.info.images.size());
		bl_t = bl_now;
	}
	if (blm && blm_phase == 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveSpan0Ns,
		                        Common::FrameStats::NowNs() - blm_t0);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveSpan0N, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveImages0,
		                        program.info.images.size());
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveSamplers0,
		                        program.info.samplers.size());
	}
	prepared.samplers.reserve(program.info.samplers.size());
	for (uint32_t i = 0; i < program.info.samplers.size(); i++) {
		prepared.samplers.push_back(NativeSampler(m_context, program, i, snapshot.samplers[i]));
	}
	if (bl_t != 0) {
		const auto bl_now = Common::FrameStats::NowNs();
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapSamplerNs, bl_now - bl_t);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapSamplers,
		                        program.info.samplers.size());
		bl_t = bl_now;
	}
	prepared.shader_data.reserve(program.bindings.ShaderDataDwords());
	for (const auto reg: program.bindings.user_data_registers) {
		prepared.shader_data.push_back(snapshot.user_data[reg - program.user_data_base]);
	}
	prepared.shader_data.resize(program.bindings.ShaderDataDwords());
	if (bl_t != 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapDataNs,
		                        Common::FrameStats::NowNs() - bl_t);
	}
	if (blm && blm_phase != 0) {
		// Exactly the same two timestamps and four Adds phase 0 paid, at the later site.
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveSpan1Ns,
		                        Common::FrameStats::NowNs() - blm_t0);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveSpan1N, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveImages1,
		                        program.info.images.size());
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapMoveSamplers1,
		                        program.info.samplers.size());
	}
	// Session 87, gate "bindalt": published here, past the last bindlap mark, so the four Adds
	// land in the DERIVED remainder of bl_prep_us and contaminate neither bl_res_us (the
	// quantity being split) nor bl_smp_us nor bl_sd_us.
	if (bind_alt) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindAltResolveNs, bl_alt_acc);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindAltResolves, bl_alt_n);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindAltResolve0Ns, bl_alt_acc0);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindAltResolve0s, bl_alt_n0);
	}
	// Session 88, knob "bindwit": published beside bindalt, past the last bindlap mark, so the
	// six Adds land in the DERIVED remainder of bl_prep_us and contaminate neither bl_res_us
	// (the quantity being divided) nor bl_smp_us nor bl_sd_us.
	if (bind_wit != 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindWitNs, bl_wit_acc);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindWits, bl_wit_n);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindWitMissNs, bl_wnh_acc);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindWitMisses, bl_wnh_n);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindWit0Ns, bl_wit_acc0);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindWit0s, bl_wit_n0);
	}
	const bool has_gds =
	    (prepared.kind_mask & KIND_COMPUTED) != 0
	        ? (prepared.kind_mask & KIND_GDS) != 0
	        : ShaderRecompiler::IR::FindBinding(
	              program.bindings, ShaderRecompiler::IR::DescriptorBindingKind::Gds) != nullptr;
	if (Common::Gates::Enabled(Common::Gates::Gate::BindPackVerify)) {
		VerifyKind(prepared.kind_mask, KIND_GDS, program.bindings,
		           ShaderRecompiler::IR::DescriptorBindingKind::Gds);
	}
	if (has_gds) {
		prepared.gds.buffer = m_context.GetBufferCache().GetGdsBuffer()->Handle();
	}
}

void RenderExecutor::FindBuffers(PreparedBindings& prepared) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(prepared.runtime == nullptr || !*prepared.runtime);
	const auto& program  = *prepared.runtime->program;
	const auto& snapshot = prepared.runtime->resources;
	auto&       cache    = m_context.GetBufferCache();

	Common::FrameStats::Scope find_scope(Common::FrameStats::Counter::BindBufFindNs,
	                                     Common::FrameStats::Counter::Count);
	Common::FrameStats::Add(Common::FrameStats::Counter::BindBufN, program.info.buffers.size());
	prepared.buffer_sources.clear();
	prepared.buffer_sources.reserve(program.info.buffers.size());
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		auto descriptor = DecodeNativeDescriptor<ShaderBufferResource>(snapshot.buffers[i]);
		const auto address = descriptor.Base48();
		const auto requested_size = descriptor.GetSize();
		if (address == 0 || requested_size == 0) {
			prepared.buffer_sources.push_back({});
			continue;
		}
		const auto size = Libs::LibKernel::Memory::ClampRangeSize(address, requested_size);
		prepared.buffer_sources.push_back({address, size, cache.FindBuffer(address, size)});
	}
}

void RenderExecutor::RebindBuffers(PreparedBindings& prepared) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(prepared.runtime == nullptr || !*prepared.runtime);
	const auto& program   = *prepared.runtime->program;
	const auto& snapshot  = prepared.runtime->resources;
	const auto& layout    = program.bindings;
	// Session 85, gate "bindlap": the buffer half.  bb_n is the prior denominator this must
	// match, exactly as sl_buf_n does.
	const bool                   bind_lap = Common::Gates::Enabled(Common::Gates::Gate::BindLap);
	Common::FrameStats::LapScope bind_lap_scope(bind_lap,
	                                            Common::FrameStats::Counter::BindLapBufferNs);
	if (bind_lap) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapBuffers,
		                        program.info.buffers.size());
	}
	EXIT_IF(prepared.buffer_sources.size() != program.info.buffers.size());

	prepared.buffers.clear();
	prepared.buffers.reserve(program.info.buffers.size());
	// Session 93, gate "bdacap": parallel to buffers, cleared and reserved with it.
	prepared.buffer_class.clear();
	prepared.buffer_class.reserve(program.info.buffers.size());
	EXIT_IF(prepared.shader_data.size() != layout.ShaderDataDwords());
	std::fill(prepared.shader_data.begin() + layout.memory_offset_dword,
	          prepared.shader_data.end(), 0);
	auto pack_memory_offset = [&](uint32_t index, uint32_t offset) {
		const auto dword = layout.memory_offset_dword + index / 4u;
		const auto shift = (index % 4u) * 8u;
		prepared.shader_data[dword] |= offset << shift;
	};
	const bool direct_copy = DirectConstantCopyEnabled();
	// Session 69: the writer half of ImgUploadWhy. A written storage buffer marks every image over
	// its range stale (NativeStorageBuffer -> InvalidateMemoryFromGPU), which is where 95 % of the
	// ~100 MB of image uploads per frame come from. Same env var as the image trace, so one run
	// prints both sides; large ranges only, so the four addresses that carry 90 MB stand out.
	static const bool writer_trace = std::getenv("KYTY_IMAGE_UPLOAD_TRACE") != nullptr;
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		uint32_t buffer_offset = 0;
		// Session 93, gate "bdacap": out-parameter, BdaCapClass::None unless the gate is armed.
		uint8_t  buffer_class  = static_cast<uint8_t>(BdaCapClass::None);
		if (writer_trace && program.info.buffers[i].written) {
			static const uint64_t min_bytes = [] {
				const auto* value = std::getenv("KYTY_IMAGE_WRITER_MIN_KB");
				return (value == nullptr ? uint64_t {1024} : std::strtoull(value, nullptr, 10)) * 1024u;
			}();
			static const uint32_t first_frame = [] {
				const auto* value = std::getenv("KYTY_IMAGE_UPLOAD_FROM");
				return value == nullptr ? 0u : static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
			}();
			const auto& src = prepared.buffer_sources[i];
			if (src.size >= min_bytes && GpuTimeProfiler::Frame() >= first_frame) {
				LOGF("ImgWriter: frame=%u shader=0x%016" PRIx64 " stage=%u slot=%u"
				     " guest=0x%016" PRIx64 " bytes=%" PRIu64 " read=%d formatted=%d\n",
				     GpuTimeProfiler::Frame(), program.shader_hash,
				     static_cast<uint32_t>(program.stage), i, src.address, src.size,
				     program.info.buffers[i].read ? 1 : 0,
				     program.info.buffers[i].formatted ? 1 : 0);
			}
		}
		prepared.buffers.push_back(NativeStorageBuffer(m_context, prepared.buffer_sources[i],
		                                               program.info.buffers[i], program.stage, i,
		                                               buffer_offset, direct_copy, buffer_class));
		prepared.buffer_class.push_back(buffer_class);
		pack_memory_offset(i, buffer_offset);
	}
	Common::FrameStats::Scope upload_scope(Common::FrameStats::Counter::BindBufUploadNs);
	const bool kinds_known = (prepared.kind_mask & KIND_COMPUTED) != 0;
	const bool has_srt =
	    kinds_known
	        ? (prepared.kind_mask & KIND_FLATTENED_SRT) != 0
	        : ShaderRecompiler::IR::FindBinding(
	              layout, ShaderRecompiler::IR::DescriptorBindingKind::FlattenedSrt) != nullptr;
	const bool has_shader_data =
	    kinds_known ? (prepared.kind_mask & KIND_SHADER_DATA) != 0
	                : ShaderRecompiler::IR::FindBinding(
	                      program.bindings,
	                      ShaderRecompiler::IR::DescriptorBindingKind::ShaderData) != nullptr;
	if (Common::Gates::Enabled(Common::Gates::Gate::BindPackVerify)) {
		VerifyKind(prepared.kind_mask, KIND_FLATTENED_SRT, layout,
		           ShaderRecompiler::IR::DescriptorBindingKind::FlattenedSrt);
		VerifyKind(prepared.kind_mask, KIND_SHADER_DATA, program.bindings,
		           ShaderRecompiler::IR::DescriptorBindingKind::ShaderData);
	}
	// Session 95, gate "framerep": the payload bytes are hashed HERE, where the span is
	// already in hand and about to be copied into the ring anyway.  The time is booked to
	// fr_pre_ns and subtracted from mc_pre_ns by the draw's scope, exactly as the mergecost
	// census subtracts mc_sig_ns from mc_post_ns; with the gate off nothing here runs.
	const bool fr_pay = Common::Gates::Enabled(Common::Gates::Gate::FrameRep) &&
	                    Common::FrameStats::Enabled();
	const auto fr_t0  = fr_pay ? Common::FrameStats::NowNs() : 0;
	if (has_srt) {
		if (fr_pay) {
			prepared.srt_hash = FrameRepWords(snapshot.flattened_srt);
			Common::FrameStats::Add(Common::FrameStats::Counter::FrameRepPayBytes,
			                        snapshot.flattened_srt.size() * sizeof(uint32_t));
			Common::FrameStats::Add(Common::FrameStats::Counter::FrameRepPayN, 1);
		}
		prepared.flattened_srt = NativeUpload(m_context, snapshot.flattened_srt);
	}
	if (has_shader_data) {
		if (fr_pay) {
			prepared.data_hash = FrameRepWords(prepared.shader_data);
			Common::FrameStats::Add(Common::FrameStats::Counter::FrameRepPayBytes,
			                        prepared.shader_data.size() * sizeof(uint32_t));
			Common::FrameStats::Add(Common::FrameStats::Counter::FrameRepPayN, 1);
		}
		prepared.shader_data_buffer = NativeUpload(m_context, prepared.shader_data);
	}
	if (fr_pay) {
		m_frame_rep.pre_ns += Common::FrameStats::NowNs() - fr_t0;
	}
}

void RenderExecutor::RebindImages(PreparedBindings& prepared) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(prepared.runtime == nullptr || !*prepared.runtime);
	const auto& program  = *prepared.runtime->program;
	const auto& snapshot = prepared.runtime->resources;
	auto&       images   = prepared.images;
	// Session 85, gate "bindlap": bl_img_us over bl_img_n is the average ns an image slot
	// costs here, and the per-outcome split comes from the OLS of price85.py against
	// texfast_ok / texfast_no, which this same function already counts.  bl_stage_n is the
	// arming proof AND the regressor that absorbs the instrument's own per-stage overhead.
	const bool                   bind_lap = Common::Gates::Enabled(Common::Gates::Gate::BindLap);
	Common::FrameStats::LapScope bind_lap_scope(bind_lap,
	                                            Common::FrameStats::Counter::BindLapImageNs);
	if (bind_lap) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapStages, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::BindLapImages,
		                        program.info.images.size());
	}
	EXIT_IF(images.size() != program.info.images.size());
	auto& texture_cache = m_context.GetTextureCache();
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		const auto old_image = texture_cache.m_slot_images.try_get(images[i].image_id);
		if (old_image == nullptr || (!old_image->registered && !old_image->info.data.Empty()) ||
		    old_image->binding.needs_rebind) {
			if (old_image != nullptr) {
				old_image->binding = {};
			}
			images[i] = ResolveTexture(program.info.images[i], snapshot.images[i]);
			BindImage(images[i].image_id,
			          images[i].desc.type == TextureCache::BindingType::Storage,
			          program.info.images[i].atomic);
		}
	}
	// Gate "texfast": a sampled binding resolved from a memo slot takes the view recorded in that
	// slot instead of calling FindTexture, while nothing FindTexture would act on has happened:
	//  - CPU invalidation, maybe-dirty marking, tracking cuts and buffer-side modification move
	//    Image::bind_stamp before they change the image. Guest-thread fault handlers do so under
	//    TextureCache::m_lock (InvalidateCpuAliases); every other writer is this thread.
	//  - what this thread owns is re-checked directly: registration, rebind flag, stencil
	//    association, pending top mips, the BC source trim (TextureSourceSettled), and the slot
	//    (version, image id) that pins the desc the view was made for.
	// A view is recorded only after FindTexture left the image clean, with the stamp read before
	// FindTexture and unchanged after the checks: a writer bumps first and holds the lock, so no
	// invalidation can slip in between the two reads unseen. DCC descs, storage and dynamic
	// storage bindings always run FindTexture. Also skipped on this path: the desc copy and the
	// GetImage (another LRU touch) after FindTexture.
	const bool fast       = Common::Gates::Enabled(Common::Gates::Gate::TexFast) &&
	                        !Config::GraphicsDebugDumpEnabled();
	const bool fast_check = fast && Common::Gates::Enabled(Common::Gates::Gate::TexFastCheck);
	auto*      memo       = fast ? &Memo() : nullptr;
	uint64_t   fast_ok = 0, fast_no = 0, fast_no_stamp = 0, fast_no_state = 0, fast_record = 0;
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		auto& binding = images[i];
		binding.mip_views.clear();
		const auto& resource = program.info.images[i];
		if (fast && resource.mip_mode != ShaderRecompiler::IR::ImageMipMode::DynamicStorage &&
		    binding.desc.type != TextureCache::BindingType::Storage) {
			auto&      image    = texture_cache.m_slot_images[binding.image_id];
			auto*      slot     = binding.memo_index < RenderExecutorMemo::TextureSlots
			                          ? &memo->textures[binding.memo_index]
			                          : nullptr;
			const bool eligible = slot != nullptr && slot->valid &&
			                      slot->version == binding.memo_version &&
			                      slot->image_id == binding.image_id &&
			                      binding.desc.info.metadata.kind != ImageMetadataKind::Dcc &&
			                      image.registered && !image.depth_id &&
			                      !image.binding.needs_rebind;
			vk::ImageView view = nullptr;
			if (eligible && slot->fast_view != nullptr) {
				if (image.bind_stamp.load(std::memory_order_acquire) != slot->fast_stamp) {
					fast_no_stamp++;
				} else if (image.pending_levels != 0 || !TextureSourceSettled(image, binding.desc)) {
					fast_no_state++;
				} else {
					view = slot->fast_view;
				}
			}
			if (view != nullptr) {
				fast_ok++;
				if (fast_check) {
					// Beyond the view: work FindTexture would have done that the fast path skipped
					// (a dirty or partly untracked image), seen under an unchanged stamp so that a
					// fault racing with this check does not count.
					const auto before     = image.bind_stamp.load(std::memory_order_acquire);
					const auto range      = image.SourceRange();
					const bool needs_work = image.IsCpuDirty() || image.IsBufferModified() ||
					                        !image.IsTracked() || image.track_addr != range.address ||
					                        image.track_addr_end != range.End();
					const bool unchanged  = before == slot->fast_stamp &&
					                        image.bind_stamp.load(std::memory_order_acquire) == before;
					const auto full = texture_cache.FindTexture(binding.image_id, binding.desc);
					if (full != view || (needs_work && unchanged)) {
						Common::FrameStats::Add(Common::FrameStats::Counter::TexFastBad, 1);
						static std::atomic<uint32_t> logged {0};
						if (logged.fetch_add(1, std::memory_order_relaxed) < 32) {
							LOGF("TexFastVerify: MISMATCH image=0x%016" PRIx64 " needs_work=%d memo_view=%p view=%p\n",
							     image.info.data.address, needs_work ? 1 : 0,
							     static_cast<void*>(static_cast<VkImageView>(view)),
							     static_cast<void*>(static_cast<VkImageView>(full)));
						}
						slot->fast_view = nullptr;
						view            = full;
					}
				}
				binding.image_view = view;
			} else {
				fast_no++;
				const auto stamp   = image.bind_stamp.load(std::memory_order_acquire);
				binding.image_view = texture_cache.FindTexture(binding.image_id, binding.desc);
				const auto source  = image.SourceRange();
				if (eligible && image.pending_levels == 0 && !image.IsCpuDirty() &&
				    !image.IsBufferModified() && image.IsTracked() &&
				    image.track_addr == source.address && image.track_addr_end == source.End() &&
				    TextureSourceSettled(image, binding.desc) &&
				    image.bind_stamp.load(std::memory_order_acquire) == stamp) {
					slot->fast_view  = binding.image_view;
					slot->fast_stamp = stamp;
					fast_record++;
					Common::DrawStat::Mark(Common::DrawStat::Memo);
				}
			}
			image.usage.texture = true;
			continue;
		}
		if (resource.mip_mode == ShaderRecompiler::IR::ImageMipMode::DynamicStorage) {
			EXIT_IF(resource.mip_count == 0u ||
			        resource.mip_count != binding.desc.view_info.level_count);
			binding.mip_views.reserve(resource.mip_count);
			for (uint32_t mip = 0; mip < resource.mip_count; mip++) {
				auto desc = binding.desc;
				desc.view_info.base_level += mip;
				desc.view_info.level_count = 1;
				binding.mip_views.push_back(texture_cache.FindTexture(binding.image_id, desc));
			}
			binding.image_view = binding.mip_views.front();
		} else {
			auto desc = binding.desc;
			if (desc.type == TextureCache::BindingType::Storage) {
				desc.view_info.level_count = 1;
			}
			binding.image_view = texture_cache.FindTexture(binding.image_id, desc);
		}
		auto&      image   = texture_cache.GetImage(binding.image_id);
		const bool storage = binding.desc.type == TextureCache::BindingType::Storage;
		image.usage.storage |= storage;
		image.usage.texture |= !storage;
	}
	if (fast && Common::FrameStats::Enabled()) {
		Common::FrameStats::Add(Common::FrameStats::Counter::TexFastOk, fast_ok);
		Common::FrameStats::Add(Common::FrameStats::Counter::TexFastNo, fast_no);
		Common::FrameStats::Add(Common::FrameStats::Counter::TexFastNoStamp, fast_no_stamp);
		Common::FrameStats::Add(Common::FrameStats::Counter::TexFastNoState, fast_no_state);
		Common::FrameStats::Add(Common::FrameStats::Counter::TexFastRecord, fast_record);
	}
}

void RenderExecutor::PrepareGraphicsBindings(std::span<PreparedBindings* const> stages,
                                             std::span<RenderColorInfo> colors) {
	bool uses_dma = false;
	for (auto* stage: stages) {
		FindBuffers(*stage);
		uses_dma |= stage->runtime->program->info.uses_dma;
	}
	// Session 93, gate "bdacap" (MEASUREMENT ONLY): draws where at least one stage already
	// sets info.uses_dma, i.e. where PrepareBda runs anyway and a slot converted to a device
	// address would cost no new binding.  Gate FIRST and read once per draw; at bdacap = 0
	// nothing is counted and nothing about the draw changes.
	if (Common::Gates::Enabled(Common::Gates::Gate::BdaCap) && Common::FrameStats::Enabled() &&
	    uses_dma) {
		Common::FrameStats::Add(Common::FrameStats::Counter::BdaCapDmaDraws, 1);
	}
	// Session 94, gate "bdaall" (MEASUREMENT ONLY, pred/02_bdaall.md): what PrepareBda
	// would cost if every draw needed the device-address table, which is what moving the
	// bc_ok V# slots onto BDA would make true.  The draw is otherwise untouched -- no slot is
	// converted, no shader changes -- so the contrast prices exactly the extra calls and
	// their side effects (earlier uploads, re-armed pages, pass ends).  bda_all_n counts the
	// calls made ONLY because of the gate; at 0 nothing here runs.
	bool bda_all = false;
	if (!uses_dma && Common::Gates::Enabled(Common::Gates::Gate::BdaAll)) {
		for (auto* stage: stages) {
			bda_all = bda_all || BdaAllCandidate(stage->runtime->program->info);
		}
		Common::FrameStats::Add(bda_all ? Common::FrameStats::Counter::BdaAllCalls
		                                : Common::FrameStats::Counter::BdaAllNoCandidate,
		                        1);
	}
	if (uses_dma || bda_all) {
		m_context.PrepareBda();
	}
	for (auto* stage: stages) {
		RebindImages(*stage);
	}
	auto& cache = m_context.GetTextureCache();
	for (auto& target: colors) {
		EXIT_IF(!target.image_id);
		const auto old_image = cache.m_slot_images.try_get(target.image_id);
		if (old_image == nullptr || (!old_image->registered && !old_image->info.data.Empty()) ||
		    old_image->binding.needs_rebind) {
			if (old_image != nullptr) {
				old_image->binding = {};
			}
			target.desc.view_info.base_level = target.guest_mip_level;
			target.desc.view_info.base_layer = target.guest_array_layer;
			target.image_id = cache.FindImage(target.desc);
			// Gate "rtfast": this re-find rewrote the description the target was memoized with,
			// so the memo slot has to move with it -- exactly like the re-finds in
			// ResolveRenderColorTarget / ResolveRenderDepthTarget. Without the write-back a
			// later "same slot, same version" hit keeps the rewritten description (gate on)
			// while a gate-off run replays the stored one, and the gate would change results
			// instead of only cost. The slot is written only while it still holds this very
			// info: another target may have taken it since, and then its key no longer matches
			// what is stored (a version mismatch already forces the full copy on the next hit).
			if (target.memo_slot != UINT32_MAX && m_memo != nullptr &&
			    target.memo_slot < m_memo->colors.size()) {
				auto& slot = m_memo->colors[target.memo_slot];
				if (slot.valid && slot.version == target.memo_version) {
					slot.version++; // a store like any other
					target.memo_version          = slot.version;
					slot.info.desc               = target.desc;
					slot.info.image_id           = target.image_id;
					slot.info.memo_slot          = target.memo_slot;
					slot.info.memo_version       = target.memo_version;
					Common::DrawStat::Mark(Common::DrawStat::Memo);
				}
			}
			BindRenderTarget(target.image_id);
		}
	}
	// Discovery can read back PS5 metadata and submit the scheduler. Reserve draw buffers only
	// after image identities are final; attachment layout transitions follow buffer alias copies.
	for (auto* stage: stages) {
		RebindBuffers(*stage);
	}
}

void RenderExecutor::ShadowQueue(std::span<PreparedBindings* const> stages) {
	namespace FS      = Common::FrameStats;
	const auto workers    = Common::Gates::Value(Common::Gates::Knob::ShadowResolve);
	const bool inline_run = Common::Gates::Enabled(Common::Gates::Gate::ShadowInline);
	if (workers == 0 && !inline_run) {
		return;
	}
	const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
	thread_local ShadowResolve::Job job;
	job.context      = &m_context;
	job.image_count  = 0;
	job.buffer_count = 0;
	const auto* memo      = m_memo.get();
	const bool  fast_gate = Common::Gates::Enabled(Common::Gates::Gate::TexFast) &&
	                        !Config::GraphicsDebugDumpEnabled();
	const auto add_stage = [&](const PreparedBindings& prepared) {
		const auto& program = *prepared.runtime->program;
		if (job.image_count + prepared.images.size() > ShadowResolve::MaxImages ||
		    job.buffer_count + prepared.buffer_sources.size() > ShadowResolve::MaxBuffers) {
			return false;
		}
		for (size_t i = 0; i < prepared.images.size(); i++) {
			const auto& binding  = prepared.images[i];
			const auto& resource = program.info.images[i];
			auto&       query    = job.images[job.image_count++];
			query.id                 = binding.image_id;
			query.data               = binding.desc.info.data;
			query.extent             = binding.desc.info.extent;
			query.resources          = binding.desc.info.resources;
			query.source_first_level = binding.desc.source_first_level;
			query.source_size        = binding.desc.source_size;
			query.eligible = fast_gate &&
			                 resource.mip_mode != ShaderRecompiler::IR::ImageMipMode::DynamicStorage &&
			                 binding.desc.type != TextureCache::BindingType::Storage &&
			                 binding.desc.info.metadata.kind != ImageMetadataKind::Dcc;
			query.has_view   = false;
			query.fast_stamp = 0;
			if (memo != nullptr && binding.memo_index < RenderExecutorMemo::TextureSlots) {
				const auto& slot = memo->textures[binding.memo_index];
				if (slot.valid && slot.version == binding.memo_version &&
				    slot.image_id == binding.image_id && slot.fast_view != nullptr) {
					query.has_view   = true;
					query.fast_stamp = slot.fast_stamp;
				}
			}
		}
		for (size_t i = 0; i < prepared.buffer_sources.size(); i++) {
			const auto& source = prepared.buffer_sources[i];
			auto&       query  = job.buffers[job.buffer_count++];
			query.address = source.address;
			query.size    = source.size;
			query.id      = source.id;
			query.written = program.info.buffers[i].written;
		}
		return true;
	};
	bool ok = true;
	// The same stage span the draw just prepared: one vertex stage (VS or mesh) or the three
	// tessellation stages, plus the pixel stage when it is active. A slot without a runtime never
	// reaches this span, but the guard keeps the probe out of undefined memory if one ever does.
	for (const auto* stage: stages) {
		if (!ok || stage == nullptr || stage->runtime == nullptr) {
			continue;
		}
		ok = add_stage(*stage);
	}
	if (!ok) {
		FS::Add(FS::Counter::ShadowOver, 1);
		return;
	}
	if (t0 != 0) {
		FS::Add(FS::Counter::ShadowPushNs, FS::NowNs() - t0);
	}
	if (inline_run) {
		ShadowResolve::Run(job, true);
	}
	if (workers != 0) {
		const auto t1 = t0 != 0 ? FS::NowNs() : 0;
		if (!ShadowResolve::Push(job)) {
			FS::Add(FS::Counter::ShadowDropped, 1);
		}
		if (t1 != 0) {
			FS::Add(FS::Counter::ShadowPushNs, FS::NowNs() - t1);
		}
	}
}

// Session 57, E9 (gate "drawstat"): the ceiling of descriptor-set reuse with dynamic offsets (B9).
// Each graphics write is compared with the last write of the same set layout (a set layout belongs
// to one pipeline) and with the previous graphics write. With dynamic storage buffers only the
// offset moves: the handle and the range stay in the set, so "base" compares handles with ranges.
// CommitBindings runs under the render mutex on the GuestGpu thread: plain globals.
//
// Session 58, B9: "base" says that a write repeats up to its offsets, not how many offsets moved.
// Every moved offset costs one dynamic descriptor, and a device grants only
// maxDescriptorSet{Storage,Uniform}BuffersDynamic of them per pipeline layout, so the slot keeps
// the offsets themselves as well: the repeating writes then split into the ones that would fit
// that budget and the ones that never can.
namespace {

// Buffer descriptors whose offset is kept per layout. One stage binds up to ShaderInfo::MaxBuffers
// storage views plus their const-bank aliases and the five fixed buffer bindings, so two stages can
// pass this; the sets that do are counted apart (e9_dyn_cap) instead of being measured wrong.
constexpr uint32_t SetStatMaxBuffers = 64;

struct DescriptorSetStat {
	uint64_t layout  = 0;
	uint64_t images  = 0;
	uint64_t buffers = 0;
	uint64_t ranges  = 0;
	uint64_t full    = 0;
	// B9. An offset is kept as its low 32 bits: every buffer bound here is far below 4 GiB.
	// `moved` accumulates over the layout and not over the write, because the descriptor type is
	// declared on the set layout: one draw that moves a descriptor makes it dynamic for all draws.
	uint32_t                                buffer_count = 0;
	uint64_t                                moved        = 0;
	uint64_t                                uniforms     = 0;
	std::array<uint32_t, SetStatMaxBuffers> offsets {};
};

constinit DescriptorSetStat g_set_stats[16384] {};
constinit DescriptorSetStat g_set_last {};
constinit uint32_t          g_set_run = 0;
constinit bool              g_dyn_limits_noted = false;

constexpr uint64_t SetStatMix(uint64_t hash, uint64_t value) noexcept {
	return hash ^ (value + 0x9e3779b97f4a7c15ull + (hash << 6u) + (hash >> 2u));
}

// B9: how many buffer descriptors would have to carry a dynamic offset for this write to reuse the
// set of `last`, and whether the device budget stretches that far. Called for the writes that
// already repeat the images, the handles and the ranges -- everything else of them is in place.
void NoteDynamicOffsetStat(RenderContext& context, const DescriptorSetStat& last,
                           DescriptorSetStat& current) {
	using Counter              = Common::FrameStats::Counter;
	const auto& limits         = context.GetGraphics().GetPhysicalDeviceProperties().limits;
	const auto  storage_budget = limits.maxDescriptorSetStorageBuffersDynamic;
	const auto  uniform_budget = limits.maxDescriptorSetUniformBuffersDynamic;
	if (!g_dyn_limits_noted) {
		// Once: the trace line prints per-frame deltas, so the two budgets show up in the first
		// frame that carries a counted write and stay out of every other frame's numbers.
		g_dyn_limits_noted = true;
		Common::FrameStats::Add(Counter::E9DynLimit, storage_budget);
		Common::FrameStats::Add(Counter::E9DynLimitUniform, uniform_budget);
	}
	if (current.buffer_count > SetStatMaxBuffers || last.buffer_count != current.buffer_count) {
		// Not measurable, counted apart instead of measured wrong: above the cap the offsets of
		// both writes are truncated, and a different buffer count behind an equal `ranges` hash is
		// a collision of that hash - the two writes do not repeat each other at all, and the tail
		// of the longer one would be compared against the zeros of the shorter and reported as
		// moved. `last.buffer_count > SetStatMaxBuffers` falls into the same check.
		Common::FrameStats::Add(Counter::E9DynCapped, 1);
		return;
	}
	uint64_t moved = 0;
	for (uint32_t i = 0; i < current.buffer_count; i++) {
		moved |= last.offsets[i] != current.offsets[i] ? uint64_t {1} << i : uint64_t {0};
	}
	current.moved |= moved;
	const auto storage_n = static_cast<uint32_t>(std::popcount(moved & ~current.uniforms));
	const auto uniform_n = static_cast<uint32_t>(std::popcount(moved & current.uniforms));
	const auto needed    = storage_n + uniform_n;
	Common::FrameStats::Add(storage_n <= storage_budget && uniform_n <= uniform_budget
	                            ? Counter::E9DynOk
	                            : Counter::E9DynOver,
	                        1);
	if (needed != 0) {
		// 1 | 2 | 3-4 | 5-8 | >8: the budget is a small power of two, so a bucket edge sits on it.
		const auto bucket = needed == 1u   ? 0u
		                    : needed <= 2u ? 1u
		                    : needed <= 4u ? 2u
		                    : needed <= 8u ? 3u
		                                   : 4u;
		Common::FrameStats::Add(
		    static_cast<Counter>(static_cast<uint32_t>(Counter::E9DynNeed1) + bucket), 1);
	}
	// The layout, not this pair of writes: a descriptor that ever moves is dynamic in every draw,
	// so a layout past the budget stays past it whatever the two writes at hand look like.
	const auto layout_storage =
	    static_cast<uint32_t>(std::popcount(current.moved & ~current.uniforms));
	const auto layout_uniform =
	    static_cast<uint32_t>(std::popcount(current.moved & current.uniforms));
	Common::FrameStats::Add(Counter::E9DynLayoutOver, layout_storage > storage_budget ||
	                                                          layout_uniform > uniform_budget
	                                                      ? 1u
	                                                      : 0u);
}

void NoteDescriptorSetStat(RenderContext& context, const PipelineCache::Pipeline& pipeline,
                           std::span<const vk::DescriptorImageInfo>  images,
                           std::span<const vk::DescriptorBufferInfo> buffers,
                           std::span<const vk::WriteDescriptorSet>   writes) {
	using Counter = Common::FrameStats::Counter;
	if (pipeline.uses_push_descriptors) {
		Common::FrameStats::Add(Counter::E9Push, 1);
		return;
	}
	const auto stream = reinterpret_cast<uintptr_t>(
	    static_cast<VkBuffer>(context.GetBufferCache().GetUtilityBuffer(MemoryUsage::Stream).Handle()));
	DescriptorSetStat current {};
	current.layout = reinterpret_cast<uintptr_t>(static_cast<VkDescriptorSetLayout>(pipeline.descriptor_set_layout));
	// Field by field: DescriptorImageInfo has padding after its layout.
	for (const auto& image: images) {
		current.images = SetStatMix(current.images, reinterpret_cast<uintptr_t>(static_cast<VkSampler>(image.sampler)));
		current.images = SetStatMix(current.images, reinterpret_cast<uintptr_t>(static_cast<VkImageView>(image.imageView)));
		current.images = SetStatMix(current.images, static_cast<uint64_t>(image.imageLayout));
	}
	uint64_t streams     = 0;
	current.buffer_count = static_cast<uint32_t>(buffers.size());
	for (uint32_t i = 0; i < buffers.size(); i++) {
		const auto& buffer = buffers[i];
		const auto handle = reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(buffer.buffer));
		current.buffers   = SetStatMix(current.buffers, handle);
		current.ranges    = SetStatMix(SetStatMix(current.ranges, handle), buffer.range);
		current.full      = SetStatMix(SetStatMix(SetStatMix(current.full, handle), buffer.range), buffer.offset);
		streams += handle == stream ? 1u : 0u;
		if (i < SetStatMaxBuffers) {
			current.offsets[i] = static_cast<uint32_t>(buffer.offset);
		}
	}
	// B9: a uniform view spends the separate maxDescriptorSetUniformBuffersDynamic budget. The
	// infos of one write are a contiguous slice of `buffers`, so a descriptor's index is the
	// distance from its front (the vector is reserved before the writes are built, and the write
	// keeps the pointer it got then).
	for (const auto& write: writes) {
		if (write.pBufferInfo == nullptr ||
		    write.descriptorType != vk::DescriptorType::eUniformBuffer) {
			continue;
		}
		const auto first = static_cast<size_t>(write.pBufferInfo - buffers.data());
		for (uint32_t i = 0; i < write.descriptorCount; i++) {
			if (first + i < SetStatMaxBuffers) {
				current.uniforms |= uint64_t {1} << (first + i);
			}
		}
	}
	Common::FrameStats::Add(Counter::E9Sets, 1);
	Common::FrameStats::Add(Counter::E9BufferInfos, buffers.size());
	Common::FrameStats::Add(Counter::E9StreamInfos, streams);

	auto& last = g_set_stats[((current.layout >> 6u) ^ (current.layout >> 17u)) & (std::size(g_set_stats) - 1u)];
	if (last.layout == current.layout) {
		const bool same_images = last.images == current.images;
		const bool same_ranges = last.ranges == current.ranges;
		Common::FrameStats::Add(Counter::E9Seen, 1);
		Common::FrameStats::Add(Counter::E9SameImages, same_images ? 1u : 0u);
		Common::FrameStats::Add(Counter::E9SameBuffers, last.buffers == current.buffers ? 1u : 0u);
		Common::FrameStats::Add(Counter::E9SameBufferRanges, same_ranges ? 1u : 0u);
		Common::FrameStats::Add(Counter::E9SameBase, same_images && same_ranges ? 1u : 0u);
		Common::FrameStats::Add(Counter::E9SameFull, same_images && last.full == current.full ? 1u : 0u);
		// B9 lives inside e9_base, and the moved descriptors of the layout carry over the slot.
		current.moved = last.moved;
		if (same_images && same_ranges) {
			NoteDynamicOffsetStat(context, last, current);
		}
	}
	const bool adjacent = g_set_last.layout == current.layout;
	Common::FrameStats::Add(Counter::E9Adjacent, adjacent ? 1u : 0u);
	if (adjacent && g_set_last.images == current.images && g_set_last.ranges == current.ranges) {
		Common::FrameStats::Add(Counter::E9AdjacentBase, 1);
		g_set_run++;
	} else {
		if (g_set_run != 0) {
			Common::FrameStats::Add(
			    static_cast<Counter>(static_cast<uint32_t>(Counter::E9RunDraws1) + Common::DrawStat::RunBucket(g_set_run)),
			    g_set_run);
		}
		g_set_run = 1;
	}
	last       = current;
	g_set_last = current;
}

static_assert(static_cast<uint32_t>(Common::FrameStats::Counter::E9RunDraws64) -
                  static_cast<uint32_t>(Common::FrameStats::Counter::E9RunDraws1) ==
              6u);
static_assert(static_cast<uint32_t>(Common::FrameStats::Counter::E9DynNeedMore) -
                  static_cast<uint32_t>(Common::FrameStats::Counter::E9DynNeed1) ==
              4u);

// Session 84, gate "slotstat" (MEASUREMENT ONLY): the route-C census, pred/02_slotstat.md.
// How many of the ~95 000 descriptor slots a frame are identical to the slot the same stage bound
// in the previous committed draw.  bindkey hashes a whole stage into one key and
// NoteDescriptorSetStat hashes a whole set into four words; neither can say how many individual
// slots repeated, which is the only quantity on this path with a ceiling above 1 ms.
//
// Capacities are the translation-time hard bounds of ShaderInfo (MaxImages 64, MaxSamplers 32,
// MaxBuffers 32) and ShaderType's nine values, all < 16.  A slot past them is counted in sl_over
// and NOT measured, rather than aliased onto another slot's history.  Plain globals in the house
// style of g_set_stats above: CommitBindings runs on the GuestGpu thread under the render mutex.
constexpr uint32_t SlotStatStages   = 16;
constexpr uint32_t SlotStatImages   = 64;
constexpr uint32_t SlotStatSamplers = 32;
constexpr uint32_t SlotStatBuffers  = 32;

struct SlotStatPrev {
	// Session 85: WHICH SHADER filled this row.  FACTS s84 3.5 bias 3 - the row was keyed
	// (ShaderType, positional index) with no shader identity, so index i denoted a different
	// logical binding whenever the previous commit on that stage ran another shader, and a
	// positional match there is not skippable by any partial update.  One comparison per
	// stage removes the bias instead of bounding it.
	std::array<uint64_t, SlotStatStages>                    shader {};
	std::array<uint64_t, SlotStatStages * SlotStatImages>   image_view {};
	std::array<uint32_t, SlotStatStages * SlotStatImages>   image_layout {};
	std::array<uint64_t, SlotStatStages * SlotStatSamplers> sampler {};
	std::array<uint64_t, SlotStatStages * SlotStatBuffers>  buffer_handle {};
	std::array<uint64_t, SlotStatStages * SlotStatBuffers>  buffer_offset {};
	std::array<uint64_t, SlotStatStages * SlotStatBuffers>  buffer_range {};
};

// The self-check of gate "bindpackcheck" for item 11: the numbers cached on the Pipeline and the
// numbers the per-draw walk produces must agree, always.  Field by field, with the failing one
// named in the log - session 83's first cut compared padding bytes with memcmp and reported 177
// false disagreements a frame.
void VerifyDescSetCounts(const PipelineCache::Pipeline&     pipeline,
                         std::span<PreparedBindings* const> prepared_bindings,
                         vk::PipelineBindPoint              pipeline_bind_point) {
	size_t               descriptor_count = 0;
	size_t               write_count      = 0;
	vk::ShaderStageFlags push_stages      = pipeline_bind_point == vk::PipelineBindPoint::eGraphics
	                                            ? vk::ShaderStageFlags {vk::ShaderStageFlagBits::eFragment}
	                                            : vk::ShaderStageFlags {};
	for (const auto* prepared: prepared_bindings) {
		const auto& program = *prepared->runtime->program;
		write_count += program.bindings.descriptors.size();
		for (const auto& binding: program.bindings.descriptors) {
			descriptor_count += NativeDescriptorCount(binding);
		}
		push_stages |= NativeShaderStage(program.stage);
	}
	const bool same_desc  = descriptor_count == pipeline.descriptor_count;
	const bool same_write = write_count == pipeline.write_count;
	const bool same_stage = push_stages == pipeline.push_stages;
	if (same_desc && same_write && same_stage) {
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::BindPackBad, 1);
	static std::atomic<uint32_t> logged {0};
	if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
		LOGF("BindPackVerify: MISMATCH descset field=%s cached=%u live=%u\n",
		     !same_desc ? "descriptor_count" : (!same_write ? "write_count" : "push_stages"),
		     !same_desc ? pipeline.descriptor_count
		                : (!same_write ? pipeline.write_count
		                               : static_cast<uint32_t>(
		                                     static_cast<VkShaderStageFlags>(pipeline.push_stages))),
		     !same_desc ? static_cast<uint32_t>(descriptor_count)
		                : (!same_write ? static_cast<uint32_t>(write_count)
		                               : static_cast<uint32_t>(
		                                     static_cast<VkShaderStageFlags>(push_stages))));
	}
}

constinit SlotStatPrev g_slot_prev {};

void NoteSlotStat(ShaderType stage, uint64_t shader,
                  const ShaderRecompiler::IR::BindingLayout& layout,
                  const PreparedBindings& prepared, uint64_t stream, uint64_t null_buffer,
                  bool verify) {
	using Counter    = Common::FrameStats::Counter;
	const uint32_t s = static_cast<uint32_t>(stage) % SlotStatStages;
	uint64_t       over = 0;
	// Session 85: did the SAME shader fill this row last time?  Read before anything is
	// stored, written after every loop, so the whole commit sees one answer.
	const bool same_shader = shader != 0 && shader == g_slot_prev.shader[s];

	uint64_t img_n = 0, img_same = 0, img_view = 0;
	uint64_t img_same_sh = 0, img_null = 0, img_elem = 0;
	// Session 86: duplicates WITHIN this stage.  The 64-bit filter decides only whether to
	// SCAN, never whether a slot is a duplicate, so it has no false negatives.  NO value
	// initialiser on the two arrays - "{}" would memset 768 bytes on every stage; only the
	// first seen_n entries are ever read.
	uint64_t img_dup = 0, img_dupv = 0, seen_mask = 0;
	uint32_t seen_n = 0;
	std::array<uint32_t, SlotStatImages> seen_id;
	std::array<uint64_t, SlotStatImages> seen_view;
	for (uint32_t i = 0; i < prepared.images.size(); i++) {
		if (i >= SlotStatImages) {
			over++;
			continue;
		}
		const auto key =
		    static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
		        static_cast<VkImageView>(prepared.images[i].image_view)));
		const auto slot_layout = static_cast<uint32_t>(prepared.images[i].layout);
		auto&      prev_view   = g_slot_prev.image_view[s * SlotStatImages + i];
		auto&      prev_layout = g_slot_prev.image_layout[s * SlotStatImages + i];
		// A null view was never bound, so it is never "the same slot as last time".
		const bool same_view = key != 0 && key == prev_view;
		img_n++;
		img_view += same_view ? 1u : 0u;
		img_same += (same_view && slot_layout == prev_layout) ? 1u : 0u;
		// Session 85.  Bias 3 removed: a positional match under a different shader is not a
		// repeat of anything.  Bias 1 measured: a null T# resolves through FindImage to a REAL
		// shared 1x1 image with a stable view, so it can never fail the key != 0 guard.  Bias 2
		// measured: this is ONE binding but max(1, mip_views.size()) descriptor ELEMENTS, and
		// only element 0 is compared.
		img_same_sh += (same_view && slot_layout == prev_layout && same_shader) ? 1u : 0u;
		img_null += prepared.images[i].desc.info.data.Empty() ? 1u : 0u;
		img_elem += prepared.images[i].mip_views.empty()
		                ? 1u
		                : static_cast<uint64_t>(prepared.images[i].mip_views.size());
		// Session 86: image_id is the identity RebindImages indexes m_slot_images with, and it
		// is the granularity of the witness.  The VIEW is the stronger key: two slots sharing a
		// VkImageView share a VkImage, and for a non-depth image binding.layout is a function of
		// the image, so the descriptor ELEMENT is identical too.  The scan keeps going after an
		// id match and breaks only on the stronger one.
		const uint32_t id_index = prepared.images[i].image_id.index;
		const uint64_t id_bit   = uint64_t {1} << (id_index & 63u);
		if ((seen_mask & id_bit) != 0) {
			bool dup = false, dupv = false;
			for (uint32_t j = 0; j < seen_n; j++) {
				if (seen_id[j] == id_index) {
					dup = true;
					if (key != 0 && seen_view[j] == key) {
						dupv = true;
						break;
					}
				}
			}
			img_dup  += dup ? 1u : 0u;
			img_dupv += dupv ? 1u : 0u;
		}
		seen_mask |= id_bit;
		seen_id[seen_n]   = id_index;
		seen_view[seen_n] = key;
		seen_n++;
		prev_view   = key;
		prev_layout = slot_layout;
	}

	uint64_t smp_n = 0, smp_same = 0, smp_same_sh = 0;
	for (uint32_t i = 0; i < prepared.samplers.size(); i++) {
		if (i >= SlotStatSamplers) {
			over++;
			continue;
		}
		const auto key = static_cast<uint64_t>(
		    reinterpret_cast<uintptr_t>(static_cast<VkSampler>(prepared.samplers[i])));
		auto& prev = g_slot_prev.sampler[s * SlotStatSamplers + i];
		smp_n++;
		smp_same += (key != 0 && key == prev) ? 1u : 0u;
		smp_same_sh += (key != 0 && key == prev && same_shader) ? 1u : 0u;
		prev = key;
	}

	uint64_t buf_n = 0, buf_same = 0, buf_ring = 0, buf_same_sh = 0, buf_null = 0;
	for (uint32_t i = 0; i < prepared.buffers.size(); i++) {
		if (i >= SlotStatBuffers) {
			over++;
			continue;
		}
		const auto& view = prepared.buffers[i];
		const auto  handle = static_cast<uint64_t>(
		     reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(view.buffer)));
		const auto offset = static_cast<uint64_t>(view.offset);
		const auto range  = static_cast<uint64_t>(view.range);
		auto&      prev_handle = g_slot_prev.buffer_handle[s * SlotStatBuffers + i];
		auto&      prev_offset = g_slot_prev.buffer_offset[s * SlotStatBuffers + i];
		auto&      prev_range  = g_slot_prev.buffer_range[s * SlotStatBuffers + i];
		buf_n++;
		buf_same += (handle != 0 && handle == prev_handle && offset == prev_offset &&
		             range == prev_range)
		                ? 1u
		                : 0u;
		buf_same_sh += (handle != 0 && handle == prev_handle && offset == prev_offset &&
		                range == prev_range && same_shader)
		                   ? 1u
		                   : 0u;
		// A const-bank copy and every NativeUpload take a fresh stream-ring offset every draw, so
		// these slots cannot repeat by construction.  Counted apart so the denominator can be
		// corrected rather than quietly biased down.
		buf_ring += (handle != 0 && handle == stream) ? 1u : 0u;
		// Session 85, bias 1's unmeasured half: NativeStorageBuffer returns a CONSTANT
		// {GetBuffer(NULL_BUFFER_ID).Handle(), 0, 16} for address == 0 || size == 0, so a
		// degenerate buffer slot is a guaranteed repeat of a descriptor nothing chose.
		buf_null += (null_buffer != 0 && handle == null_buffer && offset == 0 && range == 16)
		                ? 1u
		                : 0u;
		prev_handle = handle;
		prev_offset = offset;
		prev_range  = range;
	}

	g_slot_prev.shader[s] = shader;

	// Session 85, gate "slotstatcheck": the ELEMENTS the write list will emit for this stage,
	// derived from the compiled layout rather than from the runtime vectors.  binding.resources
	// .size() and NOT NativeDescriptorCount is the right quantity here: the emit loop of
	// CommitBindings iterates binding.resources, so an image binding with no resources emits
	// zero elements although NativeDescriptorCount answers 1.
	uint64_t layout_img_elem = 0, layout_smp_elem = 0;
	for (const auto& binding: layout.descriptors) {
		if (binding.kind == ShaderRecompiler::IR::DescriptorBindingKind::Samplers) {
			layout_smp_elem += binding.resources.size();
		} else if (ShaderRecompiler::IR::ImageBindingResourceClass(binding.kind) !=
		           ShaderRecompiler::IR::ImageResourceClass::None) {
			layout_img_elem += binding.resources.size();
		}
	}

	namespace FS = Common::FrameStats;
	FS::Add(Counter::SlotStages, 1);
	const bool all_same = (img_n + smp_n + buf_n) != 0 && over == 0 && img_same == img_n &&
	                      smp_same == smp_n && buf_same == buf_n;
	FS::Add(Counter::SlotStagesAll, all_same ? 1u : 0u);
	FS::Add(Counter::SlotStagesAllShader, (all_same && same_shader) ? 1u : 0u);
	FS::Add(Counter::SlotShaderChanges, same_shader ? 0u : 1u);
	FS::Add(Counter::SlotImagesSameShader, img_same_sh);
	FS::Add(Counter::SlotSamplersSameShader, smp_same_sh);
	FS::Add(Counter::SlotBuffersSameShader, buf_same_sh);
	FS::Add(Counter::SlotImagesNull, img_null);
	FS::Add(Counter::SlotBuffersNull, buf_null);
	FS::Add(Counter::SlotImageElements, img_elem);
	FS::Add(Counter::SlotSamplerElements, layout_smp_elem);
	if (verify) {
		// The image identity is GUARANTEED: session 84's D2 assertion requires
		// m_image_occurrences[i] == max(1, mip_views.size()) for EVERY i, so every entry of
		// prepared.images is referenced at least once and the two sums must agree exactly.
		// img_elem < img_n would mean the census counted bindings the write list never emits.
		// The SAMPLER identity is NOT guaranteed by anything in the tree and is therefore only
		// measured (sl_smp_elem), never accused.
		// Session 86: a VkImageView belongs to exactly one live image, so a view duplicate is
		// ALWAYS an id duplicate.  img_dupv > img_dup can only mean the scan is wrong.
		if (img_dupv > img_dup) {
			FS::Add(Counter::SlotBad, 1);
			static std::atomic<uint32_t> dup_logged {0};
			if (dup_logged.fetch_add(1, std::memory_order_relaxed) < 40) {
				LOGF("SlotStatVerify: MISMATCH stage=%u img_dup=%llu img_dupv=%llu img_n=%llu\n",
				     s, static_cast<unsigned long long>(img_dup),
				     static_cast<unsigned long long>(img_dupv),
				     static_cast<unsigned long long>(img_n));
			}
		}
		const bool elem_ok = layout_img_elem == img_elem && img_elem >= img_n;
		if (!elem_ok && over == 0) {
			FS::Add(Counter::SlotBad, 1);
			static std::atomic<uint32_t> logged {0};
			if (logged.fetch_add(1, std::memory_order_relaxed) < 40) {
				LOGF("SlotStatVerify: MISMATCH stage=%u layout_img_elem=%llu img_elem=%llu "
				     "img_n=%llu smp_elem=%llu smp_n=%llu\n",
				     s, static_cast<unsigned long long>(layout_img_elem),
				     static_cast<unsigned long long>(img_elem),
				     static_cast<unsigned long long>(img_n),
				     static_cast<unsigned long long>(layout_smp_elem),
				     static_cast<unsigned long long>(smp_n));
			}
		}
	}
	FS::Add(Counter::SlotImageDups, img_dup);
	FS::Add(Counter::SlotImageDupViews, img_dupv);
	FS::Add(Counter::SlotImageDupStages, img_dup != 0 ? 1u : 0u);
	FS::Add(Counter::SlotImageSq,
	        static_cast<uint64_t>(seen_n) * (seen_n > 0 ? seen_n - 1u : 0u) / 2u);
	FS::Add(Counter::SlotImages, img_n);
	FS::Add(Counter::SlotImagesSame, img_same);
	FS::Add(Counter::SlotImagesView, img_view);
	FS::Add(Counter::SlotSamplers, smp_n);
	FS::Add(Counter::SlotSamplersSame, smp_same);
	FS::Add(Counter::SlotBuffers, buf_n);
	FS::Add(Counter::SlotBuffersSame, buf_same);
	FS::Add(Counter::SlotBuffersRing, buf_ring);
	FS::Add(Counter::SlotOverflow, over);
}

} // namespace

// Sessions 96/99, knob "bfburn" at "bfmode"=2 or 3 (MEASUREMENT ONLY): the
// calibrated idle.  The floor makes the frame SHORTER, and a shorter frame lets DRS raise the
// resolution, so the two arms would no longer draw the same area and every per-frame number
// would be comparing two different scenes.  This burns the difference back on the very thread
// and at the very point the removed work occupied - the translation thread, inside the render
// mutex - so the arms keep the same frame length.  The budget is a whole frame's worth of
// microseconds and is spread over the draws and dispatches by the PREVIOUS frame's
// population, which is the only count available before the frame ends.  bf_burn_ns is what
// was really burned, never what was asked for.  Modes 0/1 return without burning.
void RenderExecutor::BindFloorBurnSlice() {
	// Read the latched mode once: bindings-only needs its own DRS calibration too.
	const auto mode = BindFloorCurrentOp().mode;
	if (mode != 2 && mode != 3) {
		return;
	}
	const uint64_t budget_us = Common::Gates::Value(Common::Gates::Knob::BindFloorBurn);
	if (budget_us == 0) {
		return;
	}
	auto&     floor = m_bind_floor;
	const int frame = m_context.GetGpu().GetFrameNum();
	if (frame != floor.burn_frame) {
		// The first frame has no population to spread over; 5 000 is this scene's order of
		// magnitude and it self-corrects on the next frame.
		floor.last_draws = floor.draws != 0 ? floor.draws : 5000u;
		floor.burn_frame = frame;
		floor.draws      = 0;
		floor.burned_ns  = 0;
		floor.budget_ns  = budget_us * 1000ull;
	}
	floor.draws++;
	if (floor.burned_ns >= floor.budget_ns) {
		return;
	}
	// Cumulative target, so a budget smaller than the draw count is still burned (the slice
	// is zero on most draws and one tick on the rest) instead of being rounded away.
	const uint64_t target = floor.budget_ns * floor.draws / floor.last_draws;
	if (target <= floor.burned_ns) {
		return;
	}
	uint64_t slice = target - floor.burned_ns;
	if (slice > floor.budget_ns - floor.burned_ns) {
		slice = floor.budget_ns - floor.burned_ns;
	}
	// Session 99, measurement only: a parallel CPU readout, NEVER the budget clock.
	// Initialised once at the first actual burn; modes 0/1 and zero budgets never reach it.
	static const bool cpu_probe = [] {
		const char* value = std::getenv("KYTY_BIND_FLOOR_CPU");
		const bool on = value != nullptr && value[0] == '1' && value[1] == '\0';
		LOGF("BindFloorCpu: mode %u\n", on ? 1u : 0u);
		return on;
	}();
	uint64_t cpu_begin = 0;
	uint64_t probe_ns  = 0;
	if (cpu_probe) {
		const uint64_t probe_begin = Common::FrameStats::NowNs();
		cpu_begin = Common::FrameStats::ThreadCpuNs(Common::FrameStats::ThreadRole::Gpu);
		probe_ns = Common::FrameStats::NowNs() - probe_begin;
	}
	const uint64_t begin = Common::FrameStats::NowNs();
	uint64_t       now   = begin;
	while (now - begin < slice) {
		now = Common::FrameStats::NowNs();
	}
	if (cpu_probe) {
		const uint64_t probe_begin = Common::FrameStats::NowNs();
		const uint64_t cpu_end =
		    Common::FrameStats::ThreadCpuNs(Common::FrameStats::ThreadRole::Gpu);
		probe_ns += Common::FrameStats::NowNs() - probe_begin;
		// Zero samples (including a zero delta) fail visibly. Do not substitute wall time.
		if (cpu_begin != 0 && cpu_end > cpu_begin) {
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnCpuNs,
			                        cpu_end - cpu_begin);
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnCpuN, 1);
		} else {
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnCpuBad, 1);
		}
		// Both query costs are bounded, including the tails outside the CPU sample span.
		// Probe/counter overhead is intentionally not deducted from cpu_gpu_us.
		Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnProbeNs, probe_ns);
	}
	floor.burned_ns += now - begin;
	Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnNs, now - begin);
}

void RenderExecutor::CommitBindings(CommandBuffer&                     buffer,
                                    vk::PipelineBindPoint              pipeline_bind_point,
                                    const PipelineCache::Pipeline&     pipeline,
                                    std::span<PreparedBindings* const> prepared_bindings,
                                    bool                               packet) {
	KYTY_PROFILER_FUNCTION();
	// No handle up front: the GDS barrier takes a fresh one after its EndRendering, the transitions
	// take one only when they issue a barrier, and the direct writes at the end take one right
	// before they record. Gate "recpack" takes none.
	size_t descriptor_count = 0;
	size_t write_count      = 0;
	// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053), route E
	// measurement M3: the CEILING STUB.  THE PICTURE IS ALLOWED TO BREAK - sealed at
	// ROADMAP.md:1048, and the only reason this may exist.  Read ONCE per commit, before
	// anything below is decided, so a schedule flip landing inside a commit cannot arm half
	// of it.  Never to be shipped: it binds WRONG data by construction.
	// REMOVED below: the per-slot image transitions and their MaterializeDeferredDccClear
	// (the loop runs zero times), the GDS barrier and its EndRendering (the floor's
	// PreparedBindings carry no GDS buffer, so that block is not entered), the slot census,
	// and every SOURCE of the descriptor writes.
	// KEPT, byte for byte: the SHAPE of the writes (program.bindings.descriptors, still read
	// out of prepared->runtime->program - which is why `prepared` and `runtime` are still
	// needed), the dstSet, updateDescriptorSets, bindDescriptorSets, pushDescriptorSetKHR,
	// the push constants, the gate "recpack" packet and the census hooks.
	// Session 97: the branch is the one the stages were PREPARED with (PreparedBindings::floor),
	// never a second read of the gate.  Session 96 read the gate here again; a falling edge
	// between that read and ExecutePreparedDraw's own (the calibrated burn sits in between)
	// sent floor-prepared stages - images / buffers / samplers EMPTY - down the real branch,
	// and bf96b died silently on it.  A draw whose stages disagree cannot be committed.
	const bool bind_floor = !prepared_bindings.empty() && prepared_bindings.front() != nullptr &&
	                        prepared_bindings.front()->floor;
	for (const auto* floor_stage: prepared_bindings) {
		EXIT_IF(floor_stage == nullptr || floor_stage->floor != bind_floor);
	}
	if (bind_floor) {
		m_bind_floor.commit++;
		// The nine null-image slots are rebuilt once a frame instead of being validated per
		// slot: a per-slot liveness check is exactly the per-slot work the floor removes.
		if (const int frame_now = m_context.GetGpu().GetFrameNum();
		    frame_now != m_bind_floor.nulls_frame) {
			m_bind_floor.nulls_frame = frame_now;
			for (auto& null_slot: m_bind_floor.nulls) {
				null_slot.valid = false;
			}
		}
	}
	// The CONSTANT triplet NativeStorageBuffer already returns for a degenerate V# (the
	// `address == 0 || size == 0` return of this file).  The floor binds it for every buffer
	// view; taken once a commit, and only while the gate is on.
	// Session 97 (patch D): with VK_EXT_robustness2 nullDescriptor the floor binds TRUE null
	// descriptors - reads zero, stores dropped, no memory behind them.  The triplet above was
	// SHARED with the shipped path's degenerate V#s, and floor stores into it were read back
	// as garbage by both paths for the rest of the process (rv97a: two GPU execution hangs).
	const bool floor_null = bind_floor && m_context.GetGraphics().null_descriptor_enabled;
	if (bind_floor && !floor_null) {
		static std::atomic<bool> warned {false};
		if (!warned.exchange(true, std::memory_order_relaxed)) {
			LOGF("BindFloor: nullDescriptor unavailable - the floor binds the SHARED null buffer"
			     " and null images, and its stores pollute them\n");
		}
	}
	const vk::DescriptorBufferInfo floor_buffer =
	    floor_null ? vk::DescriptorBufferInfo {nullptr, 0, VK_WHOLE_SIZE}
	    : bind_floor
	        ? vk::DescriptorBufferInfo {
	              m_context.GetBufferCache().GetBuffer(NULL_BUFFER_ID).Handle(), 0, 16}
	        : vk::DescriptorBufferInfo {};
	ShaderRecompiler::IR::PushData push_data;
	bool                           has_push_data = false;
	constexpr auto                 GraphicsStages =
	    vk::ShaderStageFlagBits::eVertex | vk::ShaderStageFlagBits::eMeshEXT |
	    vk::ShaderStageFlagBits::eTessellationControl |
	    vk::ShaderStageFlagBits::eTessellationEvaluation | vk::ShaderStageFlagBits::eFragment;
	vk::ShaderStageFlags push_stages = pipeline_bind_point == vk::PipelineBindPoint::eGraphics
	                                       ? vk::ShaderStageFlagBits::eFragment
	                                       : vk::ShaderStageFlags {};
	// Session 84, gate "bindpack" (PLAN_82_bind.md item 11, D1): the three numbers this loop
	// builds are constants of the pipeline and are cached on it.  Only the inner descriptor walk
	// is skipped - both EXIT_IFs stay, so a null prepared and a stage/bind-point mismatch still
	// abort by name instead of turning into a null dereference further down.
	const bool bind_pack = Common::Gates::Enabled(Common::Gates::Gate::BindPack);
	for (const auto* prepared: prepared_bindings) {
		EXIT_IF(prepared == nullptr || prepared->runtime == nullptr || !*prepared->runtime);
		const auto& program = *prepared->runtime->program;
		if (!bind_pack) {
			write_count += program.bindings.descriptors.size();
			for (const auto& binding: program.bindings.descriptors) {
				descriptor_count += NativeDescriptorCount(binding);
			}
		}
		const auto shader_stage = NativeShaderStage(program.stage);
		if (!bind_pack) {
			push_stages |= shader_stage;
		}
		EXIT_IF((pipeline_bind_point == vk::PipelineBindPoint::eGraphics &&
		         (shader_stage & GraphicsStages) == vk::ShaderStageFlags {}) ||
		        (pipeline_bind_point == vk::PipelineBindPoint::eCompute &&
		         shader_stage != vk::ShaderStageFlagBits::eCompute));
	}
	if (bind_pack) {
		descriptor_count = pipeline.descriptor_count;
		write_count      = pipeline.write_count;
		push_stages      = pipeline.push_stages;
		Common::FrameStats::Add(Common::FrameStats::Counter::BindPackDescSets, 1);
		if (Common::Gates::Enabled(Common::Gates::Gate::BindPackVerify)) {
			VerifyDescSetCounts(pipeline, prepared_bindings, pipeline_bind_point);
		}
	}
	m_descriptor_buffers.clear();
	m_descriptor_images.clear();
	m_descriptor_writes.clear();
	m_descriptor_buffers.reserve(descriptor_count);
	m_descriptor_images.reserve(descriptor_count);
	m_descriptor_writes.reserve(write_count);
	// Session 59, B9 ceiling (gate "drawstat"): the cost of a set on this thread, split into the
	// transitions, the write-list build and the emit, per pooled / push pipeline.
	namespace FS            = Common::FrameStats;
	// Session 85, gate "bindlap": the commit-side split already exists here and is NOT
	// TimingsEnabled-gated (DrawStat::On() is Gates::Enabled(DrawStat) && FrameStats::
	// Enabled(), renderDraw.cpp DrawStatBegin), so it reads under lite whenever drawstat=1 -
	// it has read 0 in every session only because that gate is off.  bindlap therefore takes
	// no second set of timestamps; it reuses these and writes its own counters.  The
	// cb_pool_* / cb_push_* Adds stay behind DrawStat::On() so their meaning is unchanged.
	const bool bind_lap     = Common::Gates::Enabled(Common::Gates::Gate::BindLap);
	// Session 101, gate "cbmove" (MEASUREMENT ONLY): read ONCE a commit, like every other
	// gate in this function, so a schedule flip landing inside a commit cannot arm half of
	// it.  The two turn tables alternate the phase per stage TYPE and per commit SHAPE, so
	// each kind contributes equally to both spans of its pair.
	const bool cm           = Common::FrameStats::Enabled() &&
	                Common::Gates::Enabled(Common::Gates::Gate::CommitLapMove);
	static thread_local std::array<uint32_t, 16> cm_turn {};
	static thread_local std::array<uint32_t, 16> cm_eturn {};
	// Session 94, gate "mergecost": armed per draw at its class point (renderDraw.cpp), never
	// by a gate read here, so a flip landing inside a draw cannot arm half of it.
	const bool merge_cost   = m_merge_cost.armed &&
	                        pipeline_bind_point == vk::PipelineBindPoint::eGraphics;
	const bool cb_timed     = (Common::DrawStat::On() || bind_lap || merge_cost) &&
	                      pipeline_bind_point == vk::PipelineBindPoint::eGraphics;
	const bool cb_pool      = !pipeline.uses_push_descriptors;
	uint64_t   cb_t         = cb_timed ? FS::NowNs() : 0;
	uint64_t   cb_transit   = 0;
	uint64_t   cb_write     = 0;
	const auto cb_lap       = [&](uint64_t& sum) {
		if (cb_timed) {
			const auto now = FS::NowNs();
			sum += now - cb_t;
			cb_t = now;
		}
	};
	uint64_t   cb_emit      = 0;
	const auto cb_finish = [&]() {
		if (!cb_timed) {
			return;
		}
		const auto emit = FS::NowNs() - cb_t;
		cb_emit         = emit;
		if (Common::DrawStat::On()) {
			FS::Add(cb_pool ? FS::Counter::CommitPoolSets : FS::Counter::CommitPushSets, 1);
			FS::Add(cb_pool ? FS::Counter::CommitPoolTransitNs : FS::Counter::CommitPushTransitNs,
			        cb_transit);
			FS::Add(cb_pool ? FS::Counter::CommitPoolWriteNs : FS::Counter::CommitPushWriteNs,
			        cb_write);
			FS::Add(cb_pool ? FS::Counter::CommitPoolEmitNs : FS::Counter::CommitPushEmitNs, emit);
		}
		if (bind_lap) {
			FS::Add(FS::Counter::BindLapCommits, 1);
			FS::Add(FS::Counter::BindLapTransitNs, cb_transit);
			FS::Add(FS::Counter::BindLapWriteNs, cb_write);
			FS::Add(FS::Counter::BindLapEmitNs, emit);
		}
	};

	// Session 84, gate "slotstat": the stream-ring handle the census needs, taken once per
	// commit rather than once per stage, and only when the gate is on.
	const bool     slot_stat   = Common::Gates::Enabled(Common::Gates::Gate::SlotStat);
	const uint64_t slot_stream =
	    slot_stat ? static_cast<uint64_t>(reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(
	                    m_context.GetBufferCache().GetUtilityBuffer(MemoryUsage::Stream).Handle())))
	              : 0;
	// Session 85: the CONSTANT descriptor NativeStorageBuffer returns for a degenerate V#,
	// taken once a commit exactly as the stream handle is.  FACTS s84 3.5 left this
	// population [NM]; it is the half of bias 1 nobody has ever counted.
	const uint64_t slot_null =
	    slot_stat ? static_cast<uint64_t>(reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(
	                    m_context.GetBufferCache().GetBuffer(NULL_BUFFER_ID).Handle())))
	              : 0;
	const bool slot_verify =
	    slot_stat && Common::Gates::Enabled(Common::Gates::Gate::SlotStatVerify);

	// Session 96, gate "bindfloor": the stub SOURCES of one descriptor binding, pushed into
	// the same two vectors and in the same order the real sources are pushed in, so the write
	// built around them below is identical in shape, count and order.  Written as a lambda
	// inside CommitBindings on purpose: the floor is a BRANCH of this function, not a second
	// copy of it, and everything past the write-building loop stays untouched code.
	//   image views -> the existing null image (NullTextureDesc + FindImage + FindTexture),
	//                  memoised in nine slots and transited to eGeneral once a commit;
	//   samplers    -> one stable handle from the sampler cache, which is never cleared;
	//   buffer views-> the null-buffer triplet above;
	//   BdaPagetable / FaultBuffer -> UNCHANGED, they never came from PreparedBindings.
	const auto floor_sources = [&](const ShaderRecompiler::IR::CompiledShaderInfo& program,
	                               const ShaderRecompiler::IR::DescriptorBinding&  binding) {
		if (ShaderRecompiler::IR::ImageBindingResourceClass(binding.kind) !=
		        ShaderRecompiler::IR::ImageResourceClass::None &&
		    floor_null) {
			// Session 97 (patch D): a null image view - no image, no transit, no shared state.
			for ([[maybe_unused]] const auto resource: binding.resources) {
				m_descriptor_images.emplace_back(nullptr, nullptr, vk::ImageLayout::eGeneral);
			}
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorImages,
			                        binding.resources.size());
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorNullDescs,
			                        binding.resources.size());
			return;
		}
		if (ShaderRecompiler::IR::ImageBindingResourceClass(binding.kind) !=
		    ShaderRecompiler::IR::ImageResourceClass::None) {
			auto& texture_cache = m_context.GetTextureCache();
			for (const auto resource: binding.resources) {
				const auto& image_resource = program.info.images.at(resource);
				const auto  type           = image_resource.written
				                                 ? TextureCache::BindingType::Storage
				                                 : TextureCache::BindingType::Texture;
				auto& slot = m_bind_floor.nulls.at(NullTextureKey(image_resource, type));
				if (!slot.valid) {
					auto desc       = NullTextureDesc(image_resource, type);
					slot.image_id   = texture_cache.FindImage(desc);
					slot.view       = texture_cache.FindTexture(slot.image_id, desc);
					slot.transit    = 0;
					slot.valid      = true;
				}
				if (slot.transit != m_bind_floor.commit) {
					// Once per commit per CLASS, at most nine times, and the same eGeneral the
					// shipped path gives a null image (the info.data.Empty() branch above).  Not a
					// per-slot synchronisation: it does not depend on the slot's contents at all.
					slot.transit = m_bind_floor.commit;
					auto& null_image = texture_cache.GetImage(slot.image_id);
					null_image.Transit(vk::ImageLayout::eGeneral,
					                   type == TextureCache::BindingType::Storage
					                       ? vk::AccessFlagBits2::eShaderRead |
					                             vk::AccessFlagBits2::eShaderWrite
					                       : vk::AccessFlags2 {vk::AccessFlagBits2::eShaderRead},
					                   {}, vk::CommandBuffer {}, RenderPassEnd::BindingTransit, false,
					                   packet);
					Common::FrameStats::Add(
					    Common::FrameStats::Counter::BindFloorNullTrans, 1);
				}
				m_descriptor_images.emplace_back(nullptr, slot.view, vk::ImageLayout::eGeneral);
			}
			Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorImages,
			                        binding.resources.size());
			return;
		}
		switch (binding.kind) {
			case BindingKind::Buffers:
			case BindingKind::ConstBuffers:
				for ([[maybe_unused]] const auto resource: binding.resources) {
					m_descriptor_buffers.push_back(floor_buffer);
				}
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBuffers,
				                        binding.resources.size());
				if (floor_null) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorNullDescs,
					                        binding.resources.size());
				}
				break;
			case BindingKind::BdaPagetable:
			case BindingKind::FaultBuffer: {
				// Unchanged: these two are properties of the buffer cache, not of a draw's
				// bindings, so the floor has nothing to take away from them.
				auto&       cache      = m_context.GetBufferCache();
				const auto* bda_buffer = binding.kind == BindingKind::BdaPagetable
				                             ? cache.GetBdaPageTableBuffer()
				                             : cache.GetFaultBuffer();
				m_descriptor_buffers.emplace_back(bda_buffer->Handle(), 0, bda_buffer->Size());
				break;
			}
			case BindingKind::FlattenedSrt:
			case BindingKind::ShaderData:
			case BindingKind::Gds:
				m_descriptor_buffers.push_back(floor_buffer);
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorBuffers, 1);
				if (floor_null) {
					Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorNullDescs, 1);
				}
				break;
			case BindingKind::Samplers:
				if (m_bind_floor.sampler == nullptr) {
					m_bind_floor.sampler =
					    m_context.GetSamplerCache().GetSampler(ShaderSamplerResource {});
				}
				for ([[maybe_unused]] const auto resource: binding.resources) {
					m_descriptor_images.emplace_back(m_bind_floor.sampler, nullptr,
					                                 vk::ImageLayout::eUndefined);
				}
				Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorSamplers,
				                        binding.resources.size());
				break;
			case BindingKind::Count: EXIT("invalid descriptor binding kind");
		}
	};
	for (auto* prepared: prepared_bindings) {
		const auto& program       = *prepared->runtime->program;
		auto&       descriptors   = *prepared;
		const auto  shader_stage  = NativeShaderStage(program.stage);
		const auto  shader_stages = ShaderPipelineStages(shader_stage);
		// Session 101, gate "cbmove": one timestamp a stage in BOTH phases, opened here and
		// closed once - after cb_lap(cb_transit) in phase 0, after cb_lap(cb_write) in
		// phase 1.  Nothing between the two close sites is reordered.
		const uint32_t cm_phase =
		    cm ? (cm_turn[static_cast<uint32_t>(program.stage) % cm_turn.size()]++ & 1u) : 0;
		const uint64_t cm_t0 = cm ? Common::FrameStats::NowNs() : 0;
		if (descriptors.gds.buffer != nullptr) {
			// Gate "gdsepoch": skipping must not call EndRendering(Gds) -- leaving the pass open
			// is the whole point, and this barrier is the first closer of every OIT draw once the
			// shader-write barrier stays inside the pass (gate "swlocal").
			auto&      gds_cache    = m_context.GetBufferCache();
			const auto gds_consumer =
			    pipeline_bind_point == vk::PipelineBindPoint::eGraphics ? 1u : 2u;
			const bool gds_needed = buffer.ClaimGdsBarrier(
			    gds_cache.GdsHostEpoch(), gds_cache.GdsShaderEpoch(), gds_consumer,
			    Common::Gates::Enabled(Common::Gates::Gate::GdsEpoch));
			if (gds_needed) {
				Common::FrameStats::Add(Common::FrameStats::Counter::GdsBarriers, 1);
				// Session 98, KYTY_BIND_FLOOR_LATCH=2: this op is a real GDS consumer; learn its
				// key (only reachable unfloored - the floor leaves gds.buffer empty).
				BindFloorNoteGdsBarrier();
				GpuMarkerNoteGds(); // Session 98 (patch_s98b): the next op carries gds=1
				Common::DrawStat::Mark(Common::DrawStat::Barrier);
				Common::DrawStat::Cut(Common::DrawStat::EdgeBarrier);
				buffer.EndRendering(RenderPassEnd::Gds);
				const auto barrier = MakeGdsDependency(descriptors.gds.buffer);
				buffer.Handle().pipelineBarrier(
				    vk::PipelineStageFlagBits::eHost | vk::PipelineStageFlagBits::eTransfer |
				        vk::PipelineStageFlagBits::eAllGraphics |
				        vk::PipelineStageFlagBits::eComputeShader,
				    shader_stages, vk::DependencyFlags {}, 0, nullptr, 1, &barrier, 0, nullptr);
			} else {
				Common::FrameStats::Add(Common::FrameStats::Counter::GdsBarriersSkipped, 1);
			}
			// This stage is itself a GDS producer for whoever comes next.
			gds_cache.NoteGdsShaderAccess();
		}

		// Session 96, gate "bindfloor": on the floor there is nothing here to transit -
		// descriptors.images is empty and the <= 9 null images are transited once a commit
		// inside floor_sources below (bf_null_tr).  Everything this loop does - the deferred
		// DCC materialisation, the per-slot layout decision and its barrier - IS the per-slot
		// synchronisation the floor exists to remove.
		const uint32_t floor_transit_count =
		    bind_floor ? 0u : static_cast<uint32_t>(program.info.images.size());
		// Session 97: the loop below indexes images[] unchecked.  The real path fills it to
		// exactly program.info.images.size() (RebindImages already EXIT_IFs that), so this
		// can only fire on a stage this branch should never have seen - loud, not silent.
		EXIT_IF(descriptors.images.size() < floor_transit_count);
		for (uint32_t i = 0; i < floor_transit_count; i++) {
			auto& image   = m_context.GetTextureCache().GetImage(descriptors.images[i].image_id);
			{
				// This binding is the consumer of a deferred DCC clear still pending on the
				// image, so its view format is the one the clear has to be encoded in (ea092a9,
				// see the hint above MaterializeDeferredDccClear).
				const DccClearViewFormat clear_view {descriptors.images[i].desc.view_info.format};
				MaterializeDeferredDccClear(buffer, descriptors.images[i].image_id, image);
			}
			auto& binding = descriptors.images[i];
			const auto&                 view = binding.desc.view_info;
			const ImageSubresourceRange range {view.base_level, view.level_count, view.base_layer,
			                                   view.layer_count};
			const bool storage = binding.desc.type == TextureCache::BindingType::Storage;
			// Gate "atomimg" (C1): every storage binding of this image in this draw writes it
			// with image atomics only, so two such draws need no barrier between them. Graphics
			// only -- a dispatch closes the pass anyway and must keep its real dependency.
			const bool atomic_write =
			    pipeline_bind_point == vk::PipelineBindPoint::eGraphics &&
			    image.binding.shader_write && !image.binding.shader_write_plain;
			if (image.info.data.Empty()) {
				image.Transit(vk::ImageLayout::eGeneral,
				              storage ? vk::AccessFlagBits2::eShaderRead |
				                            vk::AccessFlagBits2::eShaderWrite
				                      : vk::AccessFlagBits2::eShaderRead,
				              range, vk::CommandBuffer {}, RenderPassEnd::BindingTransit,
				              storage && atomic_write, packet);
			} else if (image.binding.is_target) {
				const auto layout = image.binding.attachment_layout;
				EXIT_IF(layout == vk::ImageLayout::eUndefined);
				if (image.info.IsDepth()) {
					const auto host_view =
					    std::ranges::find(image.views, binding.image_view, &CachedImageView::view);
					EXIT_IF(storage || host_view == image.views.end());
					const auto aspect = host_view->info.aspect;
					const bool depth_feedback =
					    layout == vk::ImageLayout::eAttachmentFeedbackLoopOptimalEXT &&
					    program.stage == ShaderType::Pixel;
					const bool depth_read =
					    depth_feedback || layout == vk::ImageLayout::eDepthReadOnlyOptimal ||
					    layout == vk::ImageLayout::eDepthStencilReadOnlyOptimal ||
					    layout == vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal;
					const bool stencil_read =
					    layout == vk::ImageLayout::eStencilReadOnlyOptimal ||
					    layout == vk::ImageLayout::eDepthStencilReadOnlyOptimal ||
					    layout == vk::ImageLayout::eDepthAttachmentStencilReadOnlyOptimal;
					if ((aspect & vk::ImageAspectFlagBits::eDepth && !depth_read) ||
					    (aspect & vk::ImageAspectFlagBits::eStencil && !stencil_read)) {
						EXIT("sampling a writable depth/stencil attachment aspect\n");
					}
				}
				image.Transit(layout,
				              image.binding.attachment_access | vk::AccessFlagBits2::eShaderRead |
				                  (image.binding.shader_write ? vk::AccessFlagBits2::eShaderWrite
				                                              : vk::AccessFlags2 {}),
				              {}, vk::CommandBuffer {}, RenderPassEnd::BindingTransit, atomic_write,
				              packet);
			} else if (image.binding.force_general && !image.info.IsDepth()) {
				const vk::AccessFlags2 storage_access = image.binding.shader_write
				                                            ? vk::AccessFlagBits2::eShaderWrite
				                                            : vk::AccessFlags2 {};
				image.Transit(vk::ImageLayout::eGeneral,
				              vk::AccessFlagBits2::eShaderRead | storage_access, {}, vk::CommandBuffer {},
				              RenderPassEnd::BindingTransit, atomic_write, packet);
			} else if (storage) {
				image.Transit(vk::ImageLayout::eGeneral,
				              vk::AccessFlagBits2::eShaderRead | vk::AccessFlagBits2::eShaderWrite,
				              range, vk::CommandBuffer {}, RenderPassEnd::BindingTransit, atomic_write,
				              packet);
			} else {
				image.Transit(image.info.IsDepth() ? vk::ImageLayout::eDepthStencilReadOnlyOptimal
				                                   : vk::ImageLayout::eShaderReadOnlyOptimal,
				              vk::AccessFlagBits2::eShaderRead, range, vk::CommandBuffer {},
				              RenderPassEnd::BindingTransit, false, packet);
			}
			binding.layout = image.backing.state.layout;
		}
		cb_lap(cb_transit);
		if (cm && cm_phase == 0) {
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveStage0Ns,
			                        Common::FrameStats::NowNs() - cm_t0);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveStage0N, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveImages0,
			                        program.info.images.size());
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveBindings0,
			                        program.bindings.descriptors.size());
		}

		// Session 96, gate "bindfloor": the census walks PreparedBindings, which the floor
		// leaves empty; the two gates are not combinable and the census stands down.
		if (slot_stat && !bind_floor) {
			NoteSlotStat(program.stage, program.shader_hash, program.bindings, descriptors,
			             slot_stream, slot_null, slot_verify);
		}

		m_image_occurrences.assign(descriptors.images.size(), 0);
		for (const auto& binding: program.bindings.descriptors) {
			vk::WriteDescriptorSet write {};
			write.dstBinding     = ShaderRecompiler::IR::NativeBinding(program.stage, binding.kind);
			write.descriptorType = NativeDescriptorType(binding.kind);
			write.descriptorCount   = NativeDescriptorCount(binding);
			const auto buffer_start = m_descriptor_buffers.size();
			const auto image_start  = m_descriptor_images.size();
			// Session 96, gate "bindfloor": the ONE line that swaps the sources.  The
			// write itself - dstBinding, descriptorType, descriptorCount, pBufferInfo,
			// pImageInfo and the push_back below - is the shipped code, unchanged.
			if (bind_floor) {
				floor_sources(program, binding);
			} else if (ShaderRecompiler::IR::ImageBindingResourceClass(binding.kind) !=
			    ShaderRecompiler::IR::ImageResourceClass::None) {
				for (const auto resource: binding.resources) {
					m_descriptor_images.push_back(MakeImageInfo(
					    descriptors.images.at(resource), m_image_occurrences.at(resource)++));
				}
			} else {
				switch (binding.kind) {
					case BindingKind::Buffers:
					case BindingKind::ConstBuffers:
						// ConstBuffers: the same views as uniform-buffer descriptors (the range
						// was bound at the uniform offset alignment and checked against
						// maxUniformBufferRange in NativeStorageBuffer).
						for (const auto resource: binding.resources) {
							const auto& view = descriptors.buffers.at(resource);
							EXIT_IF(view.buffer == nullptr);
							m_descriptor_buffers.push_back(view);
						}
						break;
					case BindingKind::BdaPagetable:
					case BindingKind::FaultBuffer: {
						auto&       cache      = m_context.GetBufferCache();
						const auto* bda_buffer = binding.kind == BindingKind::BdaPagetable
						                             ? cache.GetBdaPageTableBuffer()
						                             : cache.GetFaultBuffer();
						m_descriptor_buffers.emplace_back(bda_buffer->Handle(), 0,
						                                  bda_buffer->Size());
						break;
					}
					case BindingKind::FlattenedSrt:
					case BindingKind::ShaderData:
					case BindingKind::Gds: {
						const vk::DescriptorBufferInfo* view = &descriptors.gds;
						if (binding.kind == BindingKind::FlattenedSrt) {
							view = &descriptors.flattened_srt;
						} else if (binding.kind == BindingKind::ShaderData) {
							view = &descriptors.shader_data_buffer;
						}
						EXIT_IF(view->buffer == nullptr);
						m_descriptor_buffers.push_back(*view);
						break;
					}
					case BindingKind::Samplers:
						for (const auto resource: binding.resources) {
							const auto sampler = descriptors.samplers.at(resource);
							EXIT_IF(sampler == nullptr);
							m_descriptor_images.emplace_back(sampler, nullptr,
							                                 vk::ImageLayout::eUndefined);
						}
						break;
					case BindingKind::Count: EXIT("invalid descriptor binding kind");
				}
			}
			if (m_descriptor_buffers.size() != buffer_start) {
				write.pBufferInfo = m_descriptor_buffers.data() + buffer_start;
			}
			if (m_descriptor_images.size() != image_start) {
				write.pImageInfo = m_descriptor_images.data() + image_start;
			}
			m_descriptor_writes.push_back(write);
		}
		// Session 84, gate "bindpack" (PLAN_82_bind.md item 11, D2): a pure assertion with no
		// consumer, run per stage per draw over every bound image.  The vector's load-bearing
		// uses - the assign above and the at(resource)++ that selects mip_views[element] - are
		// untouched.  It stays available through gate "drawstat".
		if (!bind_pack || Common::DrawStat::On()) {
			for (uint32_t i = 0; i < descriptors.images.size(); i++) {
				const auto expected =
				    descriptors.images[i].mip_views.empty()
				        ? 1u
				        : static_cast<uint32_t>(descriptors.images[i].mip_views.size());
				EXIT_IF(m_image_occurrences[i] != expected);
			}
		}

		const auto shader_data_dwords = program.bindings.ShaderDataDwords();
		EXIT_IF(prepared->shader_data.size() != shader_data_dwords);
		if (program.bindings.UsesPushData()) {
			std::ranges::copy(prepared->shader_data,
			                  push_data.dwords.begin() + program.bindings.push_data_start_dword);
			has_push_data = true;
		}
		cb_lap(cb_write);
		if (cm && cm_phase != 0) {
			// Exactly the same two timestamps and four Adds phase 0 paid, at the later site.
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveStage1Ns,
			                        Common::FrameStats::NowNs() - cm_t0);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveStage1N, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveImages1,
			                        program.info.images.size());
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveBindings1,
			                        program.bindings.descriptors.size());
		}
	}

	// Session 101, gate "cbmove": the emit pair opens exactly where bl_em_us's region
	// begins - immediately after the last cb_lap(cb_write) - and phase 0 closes at once,
	// so its span is the price of the mark pair itself and cm_e1 - cm_e0 is the emit with
	// that price removed.  The phase alternates per commit SHAPE, so commits of the same
	// write_count contribute equally to both spans.
	const uint32_t cm_ephase =
	    cm ? (cm_eturn[write_count % cm_eturn.size()]++ & 1u) : 0;
	const uint64_t cm_e0 = cm ? Common::FrameStats::NowNs() : 0;
	if (cm && cm_ephase == 0) {
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveEmit0Ns,
		                        Common::FrameStats::NowNs() - cm_e0);
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveEmit0N, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveWrites0, write_count);
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveDesc0, descriptor_count);
	}

	// Session 96, gate "bindfloor": which emit this commit went out through.  bf_push +
	// bf_pool is the number of commits the floor took, draws and dispatches together.
	if (bind_floor) {
		Common::FrameStats::Add(cb_pool ? Common::FrameStats::Counter::BindFloorPool
		                                : Common::FrameStats::Counter::BindFloorPush,
		                        1);
	}
	if (Common::DrawStat::On() && pipeline_bind_point == vk::PipelineBindPoint::eGraphics &&
	    !m_descriptor_writes.empty()) {
		NoteDescriptorSetStat(m_context, pipeline, m_descriptor_images, m_descriptor_buffers,
		                      m_descriptor_writes);
	}
	if (packet) {
		// Gate "recpack": the push constants and the writes go to the record thread as one record
		// holding copies of the writes and their infos; it issues pushConstants and push
		// descriptors, or vkUpdateDescriptorSets + bind. The set is still handed out here:
		// DescriptorHeap stamps it with this thread's tick, and the record thread's update of it runs
		// before that tick can complete, so no two updates of a set ever overlap.
		EXIT_IF(buffer.Recorder() == nullptr);
		vk::DescriptorSet set = nullptr;
		if (!m_descriptor_writes.empty()) {
			EXIT_IF(pipeline.descriptor_set_layout == nullptr);
			if (!pipeline.uses_push_descriptors) {
				set = m_context.GetDescriptorHeap().Commit(pipeline.descriptor_set_layout);
			}
		}
		if (has_push_data || !m_descriptor_writes.empty()) {
			buffer.PushBindingsPacket(
			    pipeline_bind_point, pipeline.pipeline_layout, set, push_stages,
			    has_push_data ? std::span<const uint32_t> {push_data.dwords}
			                  : std::span<const uint32_t> {},
			    m_descriptor_writes, m_descriptor_buffers, m_descriptor_images);
		}
		if (cm && cm_ephase != 0) {
			// The same two timestamps and four Adds phase 0 paid, at the later site.
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveEmit1Ns,
			                        Common::FrameStats::NowNs() - cm_e0);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveEmit1N, 1);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveWrites1, write_count);
			Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveDesc1,
			                        descriptor_count);
		}
		cb_finish();
		if (merge_cost) {
			MergeCostCensus(pipeline, prepared_bindings, cb_transit, cb_write, cb_emit, true);
		}
		return;
	}
	// Taken after every barrier above, right before the writes that use it.
	const auto vk_buffer    = buffer.Handle();
	const auto publish_mark = buffer.PublishMark();
	if (has_push_data) {
		vk_buffer.pushConstants(pipeline.pipeline_layout, push_stages, 0, sizeof(push_data),
		                        push_data.dwords.data());
	}

	if (!m_descriptor_writes.empty()) {
		EXIT_IF(pipeline.descriptor_set_layout == nullptr);
		if (pipeline.uses_push_descriptors) {
			vk_buffer.pushDescriptorSetKHR(pipeline_bind_point, pipeline.pipeline_layout, 0,
			                               static_cast<uint32_t>(m_descriptor_writes.size()),
			                               m_descriptor_writes.data());
		} else {
			const auto set = m_context.GetDescriptorHeap().Commit(pipeline.descriptor_set_layout);
			for (auto& write: m_descriptor_writes) {
				write.dstSet = set;
			}
			m_context.GetGraphics().device.updateDescriptorSets(
			    static_cast<uint32_t>(m_descriptor_writes.size()), m_descriptor_writes.data(), 0,
			    nullptr);
			buffer.CheckNoPublish(publish_mark);
			vk_buffer.bindDescriptorSets(pipeline_bind_point, pipeline.pipeline_layout, 0, 1, &set,
			                             0, nullptr);
		}
	}
	if (cm && cm_ephase != 0) {
		// The same two timestamps and four Adds phase 0 paid, at the later site.
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveEmit1Ns,
		                        Common::FrameStats::NowNs() - cm_e0);
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveEmit1N, 1);
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveWrites1, write_count);
		Common::FrameStats::Add(Common::FrameStats::Counter::CommitLapMoveDesc1, descriptor_count);
	}
	cb_finish();
	if (merge_cost) {
		MergeCostCensus(pipeline, prepared_bindings, cb_transit, cb_write, cb_emit, false);
	}
}

// Session 94, gate "mergecost" (MEASUREMENT ONLY, pred/01_mergecost.md).  Runs AFTER the
// commit was timed and walks the writes CommitBindings just built, in the order it built
// them, into the signature the set would have once every bc_ok buffer slot were carried by
// a device address: a bc_ok entry becomes a fixed sentinel (its triplet is kept aside for
// mc_p_eq), every other entry is kept as it is -- image views with their layouts, samplers,
// const-bank / ring / formatted / null buffers, the flattened-SRT and shader-data uploads,
// GDS, the BDA table and the fault buffer.  Equal to the previous graphics commit's
// signature under the same pipeline layout (P) means the converted draw could reuse that
// set.  The walk needs the bdacap classes, so a commit without them is counted mc_bad and
// never compared.  Its own time is handed to the draw's post-class timer, which subtracts it.
void RenderExecutor::MergeCostCensus(const PipelineCache::Pipeline&     pipeline,
                                     std::span<PreparedBindings* const> prepared_bindings,
                                     uint64_t transit_ns, uint64_t write_ns,
                                     uint64_t emit_ns, bool packet) {
	namespace FS  = Common::FrameStats;
	using Counter = FS::Counter;
	using ShaderRecompiler::IR::DescriptorBindingKind;
	constexpr uint8_t  TagShape   = 0;
	constexpr uint8_t  TagImage   = 1;
	constexpr uint8_t  TagSampler = 2;
	constexpr uint8_t  TagRing    = 3;
	constexpr uint8_t  TagBuffer  = 4;
	constexpr uint8_t  TagOk      = 5;
	constexpr uint8_t  TagSrt     = 6;
	constexpr uint8_t  TagFixed   = 7;
	constexpr uint32_t WhyFirst   = 1u << 8u;
	constexpr uint32_t WhyCb      = 1u << 9u;
	constexpr uint64_t OkSentinel = 0x0b0b0b0b0b0b0b0bull;
	const uint64_t     t0         = FS::NowNs();
	auto&              mc         = m_merge_cost;
	const auto handle_of = [](vk::Buffer b) {
		return static_cast<uint64_t>(reinterpret_cast<uintptr_t>(static_cast<VkBuffer>(b)));
	};
	const uint64_t stream =
	    handle_of(m_context.GetBufferCache().GetUtilityBuffer(MemoryUsage::Stream).Handle());
	mc.sig.clear();
	mc.tag.clear();
	mc.ok_raw.clear();
	// Session 95, gate "framerep": the gate is read ONCE per census, and the draw is armed
	// by that single read.  RebindBuffers read it a few microseconds earlier for the payload
	// hashes; the two can only disagree on the single draw that straddles a schedule block
	// boundary, which costs that draw a miss and nothing else.
	auto&      fr       = m_frame_rep;
	const bool fr_armed = Common::Gates::Enabled(Common::Gates::Gate::FrameRep) &&
	                      Common::FrameStats::Enabled();
	fr.armed    = fr_armed;
	fr.hit_id   = false;
	fr.hit_idr  = false;
	fr.hit_idm  = false;
	fr.hit_pay  = false;
	fr.hit_full = false;
	fr.hit_ring = false;
	fr.srt_h.clear();
	const uint64_t fr_t0 = fr_armed ? FS::NowNs() : 0;
	if (fr_armed) {
		const int frame_now = m_context.GetGpu().GetFrameNum();
		if (frame_now != fr.frame) {
			// Rotate: the frame being built becomes N-1, and the oldest table is cleared and
			// becomes the new current one.  Indices, never a copy of 384 KiB tables.
			fr.frame = frame_now;
			fr.cur   = (fr.cur + 1u) & 3u;
			fr.id[fr.cur].Clear();
			fr.idr[fr.cur].Clear();
			fr.idm[fr.cur].Clear();
			fr.pay[fr.cur].Clear();
			fr.full[fr.cur].Clear();
		}
	}
	const auto put = [&mc](uint8_t tag, uint64_t value) {
		mc.sig.push_back(value);
		mc.tag.push_back(tag);
	};
	const auto put3 = [&put](uint8_t tag, const vk::DescriptorBufferInfo& info, uint64_t h) {
		put(tag, h);
		put(tag, static_cast<uint64_t>(info.offset));
		put(tag, static_cast<uint64_t>(info.range));
	};
	bool     bad      = false;
	uint32_t ok_slots = 0;
	uint32_t mask_x   = 0;
	uint32_t wslots   = 0;
	// The layout DEFINITION: push-descriptor flag and push stages; the stage, kind and count
	// words below carry the rest.  One VkPipelineLayout is created per pipeline, so its
	// handle would make "same layout" mean "same pipeline".
	put(TagShape, (pipeline.uses_push_descriptors ? (1ull << 40u) : 0ull) |
	                  static_cast<uint64_t>(static_cast<VkShaderStageFlags>(pipeline.push_stages)));
	size_t   bi       = 0;
	size_t   ii       = 0;
	for (const auto* prepared: prepared_bindings) {
		if (bad) {
			break;
		}
		const auto& program = *prepared->runtime->program;
		put(TagShape, (static_cast<uint64_t>(program.stage) << 32u) |
		                  static_cast<uint64_t>(program.bindings.descriptors.size()));
		for (const auto& binding: program.bindings.descriptors) {
			if (bad) {
				break;
			}
			put(TagShape, (static_cast<uint64_t>(binding.kind) << 32u) |
			                  static_cast<uint64_t>(binding.resources.size()));
			if (ShaderRecompiler::IR::ImageBindingResourceClass(binding.kind) !=
			    ShaderRecompiler::IR::ImageResourceClass::None) {
				for (size_t r = 0; r < binding.resources.size(); r++) {
					if (ii >= m_descriptor_images.size()) {
						bad = true;
						break;
					}
					const auto& info = m_descriptor_images[ii++];
					put(TagImage, static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
					                  static_cast<VkImageView>(info.imageView))));
					put(TagImage, static_cast<uint64_t>(info.imageLayout));
					put(TagImage, static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
					                  static_cast<VkSampler>(info.sampler))));
				}
				continue;
			}
			switch (binding.kind) {
				case DescriptorBindingKind::Buffers:
				case DescriptorBindingKind::ConstBuffers:
					for (const auto resource: binding.resources) {
						if (bi >= m_descriptor_buffers.size() ||
						    resource >= program.info.buffers.size()) {
							bad = true;
							break;
						}
						const auto& info = m_descriptor_buffers[bi++];
						const auto  h    = handle_of(info.buffer);
						const auto& res  = program.info.buffers[resource];
						// The mask is the slot's STATIC convertibility, so a convertible slot served by
						// the ring in one draw and by a cached buffer in the next is masked in both;
						// its bdacap class only labels it.  ConstBuffers views are const-bank.
						if (binding.kind == DescriptorBindingKind::Buffers && BdaConvertible(res)) {
							const bool cls_ok = resource < prepared->buffer_class.size() &&
							                    prepared->buffer_class[resource] ==
							                        static_cast<uint8_t>(BdaCapClass::Ok);
							put(TagOk, OkSentinel);
							put(TagOk, 0);
							put(TagOk, 0);
							mc.ok_raw.push_back(h);
							mc.ok_raw.push_back(static_cast<uint64_t>(info.offset));
							mc.ok_raw.push_back(static_cast<uint64_t>(info.range));
							ok_slots += cls_ok ? 1u : 0u;
							mask_x += cls_ok ? 0u : 1u;
						} else {
							if (binding.kind == DescriptorBindingKind::Buffers && !res.formatted &&
							    !ShaderRecompiler::IR::PackedStrideConstBank(res.packed_stride)) {
								wslots++;
							}
							put3((h != 0 && h == stream) ? TagRing : TagBuffer, info, h);
						}
					}
					break;
				case DescriptorBindingKind::FlattenedSrt:
				case DescriptorBindingKind::ShaderData:
				case DescriptorBindingKind::BdaPagetable:
				case DescriptorBindingKind::FaultBuffer:
				case DescriptorBindingKind::Gds: {
					if (bi >= m_descriptor_buffers.size()) {
						bad = true;
						break;
					}
					const auto& info = m_descriptor_buffers[bi++];
					const bool  srt  = binding.kind == DescriptorBindingKind::FlattenedSrt ||
					                 binding.kind == DescriptorBindingKind::ShaderData;
					put3(srt ? TagSrt : TagFixed, info, handle_of(info.buffer));
					if (srt && fr_armed) {
						// In the walk's own order, so the second walk can consume them by tag.
						fr.srt_h.push_back(binding.kind == DescriptorBindingKind::FlattenedSrt
						                       ? prepared->srt_hash
						                       : prepared->data_hash);
					}
					break;
				}
				case DescriptorBindingKind::Samplers:
					for (size_t r = 0; r < binding.resources.size(); r++) {
						if (ii >= m_descriptor_images.size()) {
							bad = true;
							break;
						}
						const auto& info = m_descriptor_images[ii++];
						put(TagSampler, static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
						                    static_cast<VkSampler>(info.sampler))));
					}
					break;
				default: bad = true; break;
			}
		}
	}
	if (bi != m_descriptor_buffers.size() || ii != m_descriptor_images.size()) {
		bad = true;
	}
	const uint64_t layout = static_cast<uint64_t>(reinterpret_cast<uintptr_t>(
	    static_cast<VkPipelineLayout>(pipeline.pipeline_layout)));
	const uint64_t tick   = m_context.GetCommandScheduler().CurrentTick();
	const uint64_t pipe   = static_cast<uint64_t>(
	    reinterpret_cast<uintptr_t>(static_cast<VkPipeline>(pipeline.pipeline)));
	if (bad) {
		FS::Add(Counter::MergeCostBad, 1);
		mc.prev_valid = false;
		mc.p          = false;
	} else {
		uint32_t why = 0;
		if (!mc.prev_valid) {
			why |= WhyFirst;
		} else {
			// A new command buffer has no set bound: never P, whatever the signature says.
			if (mc.prev_tick != tick) {
				why |= WhyCb;
			}
			if (mc.prev_sig.size() != mc.sig.size()) {
				why |= 1u << TagShape;
			} else {
				for (size_t i = 0; i < mc.sig.size(); i++) {
					const auto a = mc.tag[i];
					const auto b = mc.prev_tag[i];
					if (a != b) {
						// A kept buffer entry that went ring <-> cached is a ring difference.
						const bool bufs = (a == TagRing || a == TagBuffer) &&
						                  (b == TagRing || b == TagBuffer);
						why |= bufs ? (1u << TagRing) : (1u << TagShape);
					} else if (mc.sig[i] != mc.prev_sig[i]) {
						why |= 1u << a;
					}
				}
			}
		}
		bool has_ring = false;
		bool has_srt  = false;
		for (const auto t: mc.tag) {
			has_ring = has_ring || t == TagRing;
			has_srt  = has_srt || t == TagSrt;
		}
		const bool p         = why == 0;
		const bool same_pipe = mc.prev_valid && mc.prev_pipeline == pipe;
		FS::Add(Counter::MergeCostSigDraws, 1);
		FS::Add(Counter::MergeCostOkSlots, ok_slots);
		FS::Add(Counter::MergeCostMaskOk, ok_slots);
		FS::Add(Counter::MergeCostMaskOther, mask_x);
		FS::Add(Counter::MergeCostWrittenSlots, wslots);
		FS::Add(Counter::MergeCostPacket, packet ? 1u : 0u);
		FS::Add(Counter::MergeCostHasRing, has_ring ? 1u : 0u);
		FS::Add(Counter::MergeCostHasSrt, has_srt ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffCb, (why & WhyCb) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostTransitNs, transit_ns);
		FS::Add(Counter::MergeCostWriteNs, write_ns);
		FS::Add(Counter::MergeCostEmitNs, emit_ns);
		FS::Add(Counter::MergeCostDiffFirst, (why & WhyFirst) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffShape, (why & (1u << TagShape)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffImage, (why & (1u << TagImage)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffSampler, (why & (1u << TagSampler)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffRing, (why & (1u << TagRing)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffBuffer, (why & (1u << TagBuffer)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffSrt, (why & (1u << TagSrt)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffFixed, (why & (1u << TagFixed)) != 0 ? 1u : 0u);
		FS::Add(Counter::MergeCostDiffRingSrtOnly,
		        (why != 0 && (why & ~((1u << TagRing) | (1u << TagSrt))) == 0) ? 1u : 0u);
		if (p) {
			FS::Add(Counter::MergeCostSame, 1);
			FS::Add(Counter::MergeCostTransitPNs, transit_ns);
			FS::Add(Counter::MergeCostWritePNs, write_ns);
			FS::Add(Counter::MergeCostEmitPNs, emit_ns);
			FS::Add(Counter::MergeCostSamePipe, same_pipe ? 1u : 0u);
			FS::Add(Counter::MergeCostSamePush, pipeline.uses_push_descriptors ? 1u : 0u);
			FS::Add(Counter::MergeCostSameEqPipe,
			        (same_pipe && mc.ok_raw == mc.prev_ok_raw) ? 1u : 0u);
		}
		mc.p = p;
		std::swap(mc.sig, mc.prev_sig);
		std::swap(mc.tag, mc.prev_tag);
		std::swap(mc.ok_raw, mc.prev_ok_raw);
		mc.prev_layout   = layout;
		mc.prev_tick     = tick;
		mc.prev_pipeline = pipe;
		mc.prev_valid    = true;
	}
	const auto spent = FS::NowNs() - t0;
	mc.sig_ns += spent;
	FS::Add(Counter::MergeCostSigNs, spent);
	// ---- session 95, gate "framerep": the second walk -----------------------------------
	// It runs over the signature the census just built, in the SAME order, and consumes
	// ok_raw and srt_h by tag.  A walk that does not line up sets fr_bad and scores nothing.
	if (fr_armed) {
		FS::Add(Counter::FrameRepDraws, 1);
		if (bad) {
			FS::Add(Counter::FrameRepBad, 1);
		} else {
			uint64_t h_ident = 0x9e3779b97f4a7c15ull;
			// Session 95 repair: the same accumulator with the ring-served convertible slots
			// collapsed (their address is fresh every draw by construction), and the one with
			// every convertible slot masked - session 94's signature, the ceiling.
			uint64_t h_identr = 0x9e3779b97f4a7c15ull;
			uint64_t h_identm = 0x9e3779b97f4a7c15ull;
			uint64_t h_pay   = 0xff51afd7ed558ccdull;
			size_t   j       = 0;
			size_t   k       = 0;
			bool     ring    = false;
			bool     ok_ring = false;
			uint32_t ok_slots = 0;
			uint32_t n_img   = 0;
			uint32_t n_buf   = 0;
			bool     walk_ok = true;
			for (size_t i = 0; i < mc.prev_sig.size();) {
				const uint8_t tg = mc.prev_tag[i];
				if (tg == TagRing) {
					// The ring offset is fresh every draw by construction: a fixed marker.
					h_ident  = FrameRepMix(h_ident, 0x8b1a9953c4611296ull);
					h_identr = FrameRepMix(h_identr, 0x8b1a9953c4611296ull);
					h_identm = FrameRepMix(h_identm, 0x8b1a9953c4611296ull);
					ring     = true;
					i += 3;
				} else if (tg == TagOk) {
					// Session 94 masked these; the strict reading needs them UNMASKED - but a
					// convertible slot SERVED BY THE RING carries a fresh offset every draw, so
					// the repaired reading collapses exactly those, and the masked reading
					// collapses all of them (session 94's signature).
					ok_slots++;
					h_identm = FrameRepMix(h_identm, 0x0b0b0b0b0b0b0b0bull);
					if (j + 3 > mc.prev_ok_raw.size()) {
						walk_ok = false;
					} else if (mc.prev_ok_raw[j] != 0 && mc.prev_ok_raw[j] == stream) {
						ok_ring  = true;
						h_identr = FrameRepMix(h_identr, 0x8b1a9953c4611296ull);
						for (int q = 0; q < 3; q++) {
							h_ident = FrameRepMix(h_ident, mc.prev_ok_raw[j++]);
						}
					} else {
						for (int q = 0; q < 3; q++) {
							const uint64_t v = mc.prev_ok_raw[j++];
							h_ident  = FrameRepMix(h_ident, v);
							h_identr = FrameRepMix(h_identr, v);
						}
					}
					i += 3;
				} else if (tg == TagSrt) {
					// The descriptor is a ring slice: a marker for H_ident, the PAYLOAD for H_pay.
					h_ident  = FrameRepMix(h_ident, 0x2545f4914f6cdd1dull);
					h_identr = FrameRepMix(h_identr, 0x2545f4914f6cdd1dull);
					h_identm = FrameRepMix(h_identm, 0x2545f4914f6cdd1dull);
					if (k >= fr.srt_h.size()) {
						walk_ok = false;
					} else {
						h_pay = FrameRepMix(h_pay, fr.srt_h[k++]);
					}
					i += 3;
				} else {
					h_ident  = FrameRepMix(h_ident, mc.prev_sig[i]);
					h_identr = FrameRepMix(h_identr, mc.prev_sig[i]);
					h_identm = FrameRepMix(h_identm, mc.prev_sig[i]);
					n_img += (tg == TagImage) ? 1u : 0u;
					n_buf += (tg == TagBuffer) ? 1u : 0u;
					i += 1;
				}
				if (!walk_ok) {
					break;
				}
			}
			if (!walk_ok || j != mc.prev_ok_raw.size() || k != fr.srt_h.size()) {
				FS::Add(Counter::FrameRepBad, 1);
			} else {
				h_ident |= static_cast<uint64_t>(h_ident == 0);
				h_identr |= static_cast<uint64_t>(h_identr == 0);
				h_identm |= static_cast<uint64_t>(h_identm == 0);
				// H_pay and H_full are built on the REPAIRED identity: a replay decision would
				// be taken on a canonicalised identity, not on fresh ring addresses.
				const uint64_t hp = FrameRepMix(h_identr, h_pay) |
				                    static_cast<uint64_t>(FrameRepMix(h_identr, h_pay) == 0);
				const uint64_t hf = FrameRepMix(hp, fr.args) |
				                    static_cast<uint64_t>(FrameRepMix(hp, fr.args) == 0);
				const uint32_t p1 = (fr.cur + 3u) & 3u;
				const uint32_t p2 = (fr.cur + 2u) & 3u;
				const uint32_t p3 = (fr.cur + 1u) & 3u;
				const bool     i1 = fr.id[p1].Take(h_ident);
				FS::Add(Counter::FrameRepId1, i1 ? 1u : 0u);
				FS::Add(Counter::FrameRepId2, fr.id[p2].Take(h_ident) ? 1u : 0u);
				FS::Add(Counter::FrameRepId3, fr.id[p3].Take(h_ident) ? 1u : 0u);
				const bool     r1 = fr.idr[p1].Take(h_identr);
				FS::Add(Counter::FrameRepIdR1, r1 ? 1u : 0u);
				FS::Add(Counter::FrameRepIdR2, fr.idr[p2].Take(h_identr) ? 1u : 0u);
				FS::Add(Counter::FrameRepIdR3, fr.idr[p3].Take(h_identr) ? 1u : 0u);
				const bool     m1 = fr.idm[p1].Take(h_identm);
				FS::Add(Counter::FrameRepIdM1, m1 ? 1u : 0u);
				FS::Add(Counter::FrameRepOkRing, ok_ring ? 1u : 0u);
				FS::Add(Counter::FrameRepOkSlots, ok_slots);
				FS::Add(Counter::FrameRepImgN, n_img);
				FS::Add(Counter::FrameRepBufN, n_buf);
				fr.hit_idr = r1;
				fr.hit_idm = m1;
				const bool y1 = fr.pay[p1].Take(hp);
				FS::Add(Counter::FrameRepPay1, y1 ? 1u : 0u);
				const bool f1 = fr.full[p1].Take(hf);
				FS::Add(Counter::FrameRepFull1, f1 ? 1u : 0u);
				FS::Add(Counter::FrameRepFull2, fr.full[p2].Take(hf) ? 1u : 0u);
				FS::Add(Counter::FrameRepFull3, fr.full[p3].Take(hf) ? 1u : 0u);
				FS::Add(Counter::FrameRepRing, (i1 && ring) ? 1u : 0u);
				fr.hit_id   = i1;
				fr.hit_pay  = y1;
				fr.hit_full = f1;
				fr.hit_ring = ring;
				const bool o1 = fr.id[fr.cur].Insert(h_ident);
				const bool o4 = fr.idr[fr.cur].Insert(h_identr);
				const bool o5 = fr.idm[fr.cur].Insert(h_identm);
				const bool o2 = fr.pay[fr.cur].Insert(hp);
				const bool o3 = fr.full[fr.cur].Insert(hf);
				FS::Add(Counter::FrameRepOverflow,
				        (o1 && o2 && o3 && o4 && o5) ? 0u : 1u);
			}
		}
		const auto fr_spent = FS::NowNs() - fr_t0;
		fr.post_ns += fr_spent;
		FS::Add(Counter::FrameRepSigNs, fr_spent);
	}
}

} // namespace Libs::Graphics
