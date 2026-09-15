#include "graphics/host_gpu/renderer/pipeline/descriptors.h"

#include "common/gates.h"
#include "common/alignment.h"
#include "common/frameStats.h"
#include "graphics/host_gpu/lodStats.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
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
		case ShaderType::Pixel: return "Pixel";
		case ShaderType::Compute: return "Compute";
		default: return "Unknown";
	}
}

static vk::ShaderStageFlags NativeShaderStage(ShaderType stage) {
	switch (stage) {
		case ShaderType::Vertex: return vk::ShaderStageFlagBits::eVertex;
		case ShaderType::Mesh: return vk::ShaderStageFlagBits::eMeshEXT;
		case ShaderType::Pixel: return vk::ShaderStageFlagBits::eFragment;
		case ShaderType::Compute: return vk::ShaderStageFlagBits::eCompute;
		default: EXIT("unknown native shader stage\n");
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
                    uint32_t slot, uint32_t& buffer_offset, bool direct_copy) {
	Common::FrameStats::Scope binding_scope(Common::FrameStats::Counter::BindBuffersNs);
	buffer_offset = 0;

	const auto& [address, size, id] = source;
	if (address == 0 || size == 0) {
		return {context.GetBufferCache().GetBuffer(NULL_BUFFER_ID).Handle(), 0, 16};
	}
	const auto& graphics   = context.GetGraphics();
	const bool  const_bank = ShaderRecompiler::IR::PackedStrideConstBank(resource.packed_stride);
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
	if (resource.formatted && resource.written) {
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
		auto       desc = NullTextureDesc(resource, storage ? TextureCache::BindingType::Storage
		                                                    : TextureCache::BindingType::Texture);
		const auto id   = texture_cache.FindImage(desc);
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

static vk::DescriptorBufferInfo NativeUpload(RenderContext&            context,
                                             std::span<const uint32_t> data) {
	EXIT_IF(data.empty());
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
	const auto          code    = static_cast<uint8_t>(fill);
	vk::ClearColorValue clear {};
	bool                decoded = false;
	if (code == 0x20) {
		// Register-backed clear: use the clear word of the colour slot that still addresses the
		// surface. Without one the attachment path keeps handling it.
		const auto& hw = buffer.GetRegisters();
		for (uint32_t slot = 0; slot < 8 && !decoded; slot++) {
			const auto& rt = hw.GetRenderTarget(slot);
			if (rt.base.addr == image.info.data.address && rt.dcc_addr.addr == address) {
				decoded = DecodePackedColorClear(image.info.pixel_format, rt.clear_word0.word0,
				                                 rt.clear_word1.word1, clear);
			}
		}
	} else {
		decoded = DecodeFixedDccClear(image.info.pixel_format, code, clear);
	}
	static std::atomic<uint32_t> log_count = 0;
	static const bool dcc_trace = std::getenv("KYTY_DCC_TRACE") != nullptr;
	if (dcc_trace || log_count++ < 32) {
		LOGF("MaterializeDeferredDccClear: image=0x%016" PRIx64 " dcc=0x%016" PRIx64
		     " code=0x%02x layers=0x%08x format=%u decoded=%d\n",
		     image.info.data.address, address, static_cast<uint32_t>(code), mask,
		     static_cast<uint32_t>(image.info.pixel_format), decoded ? 1 : 0);
	}
	if (!decoded) {
		return;
	}
	Common::DrawStat::Mark(Common::DrawStat::ImgUp | Common::DrawStat::Meta);
	Common::DrawStat::Cut(Common::DrawStat::EdgeUpload);
	buffer.EndRendering(RenderPassEnd::Clear);
	image.Transit(vk::ImageLayout::eTransferDstOptimal, vk::AccessFlagBits2::eTransferWrite, {},
	              buffer.Handle());
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
		buffer.Handle().clearColorImage(image.backing.image,
		                                vk::ImageLayout::eTransferDstOptimal, &clear, 1, &range);
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
				(void)cache.FindRenderTarget(color.image_id, color.desc);
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

void RenderExecutor::PrepareBindings(const ShaderStageRuntime& runtime, PreparedBindings& prepared) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(!runtime);
	const auto& program  = *runtime.program;
	const auto& snapshot = runtime.resources;
	prepared.Reset();
	prepared.runtime = &runtime;
	prepared.images.reserve(program.info.images.size());
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		// Session 57, B2a: built in its vector element - one ImageDesc copy where the returned
		// binding and push_back made two. Reserved above, so no reallocation; BindImage does not
		// look at prepared.images, so running it after the insertion changes nothing.
		auto& binding = ResolveTextureWith(
		    program.info.images[i], snapshot.images[i],
		    [&prepared](ImageId id, const TextureCache::ImageDesc& desc, uint32_t index = UINT32_MAX,
		                uint32_t version = 0) -> TextureBinding& {
			    return prepared.images.emplace_back(id, desc, index, version);
		    });
		BindImage(binding.image_id, binding.desc.type == TextureCache::BindingType::Storage,
		          program.info.images[i].atomic);
	}
	prepared.samplers.reserve(program.info.samplers.size());
	for (uint32_t i = 0; i < program.info.samplers.size(); i++) {
		prepared.samplers.push_back(NativeSampler(m_context, program, i, snapshot.samplers[i]));
	}
	prepared.shader_data.reserve(program.bindings.ShaderDataDwords());
	for (const auto reg: program.bindings.user_data_registers) {
		prepared.shader_data.push_back(snapshot.user_data[reg - program.user_data_base]);
	}
	prepared.shader_data.resize(program.bindings.ShaderDataDwords());
	if (ShaderRecompiler::IR::FindBinding(
	        program.bindings, ShaderRecompiler::IR::DescriptorBindingKind::Gds) != nullptr) {
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
	EXIT_IF(prepared.buffer_sources.size() != program.info.buffers.size());

	prepared.buffers.clear();
	prepared.buffers.reserve(program.info.buffers.size());
	EXIT_IF(prepared.shader_data.size() != layout.ShaderDataDwords());
	std::fill(prepared.shader_data.begin() + layout.memory_offset_dword,
	          prepared.shader_data.end(), 0);
	auto pack_memory_offset = [&](uint32_t index, uint32_t offset) {
		const auto dword = layout.memory_offset_dword + index / 4u;
		const auto shift = (index % 4u) * 8u;
		prepared.shader_data[dword] |= offset << shift;
	};
	const bool direct_copy = DirectConstantCopyEnabled();
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		uint32_t buffer_offset = 0;
		prepared.buffers.push_back(NativeStorageBuffer(m_context, prepared.buffer_sources[i],
		                                               program.info.buffers[i], program.stage, i,
		                                               buffer_offset, direct_copy));
		pack_memory_offset(i, buffer_offset);
	}
	Common::FrameStats::Scope upload_scope(Common::FrameStats::Counter::BindBufUploadNs);
	if (ShaderRecompiler::IR::FindBinding(
	        layout, ShaderRecompiler::IR::DescriptorBindingKind::FlattenedSrt) != nullptr) {
		prepared.flattened_srt = NativeUpload(m_context, snapshot.flattened_srt);
	}
	if (ShaderRecompiler::IR::FindBinding(
	        program.bindings, ShaderRecompiler::IR::DescriptorBindingKind::ShaderData) != nullptr) {
		prepared.shader_data_buffer = NativeUpload(m_context, prepared.shader_data);
	}
}

void RenderExecutor::RebindImages(PreparedBindings& prepared) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(prepared.runtime == nullptr || !*prepared.runtime);
	const auto& program  = *prepared.runtime->program;
	const auto& snapshot = prepared.runtime->resources;
	auto&       images   = prepared.images;
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

RenderExecutor::GraphicsBindings
RenderExecutor::PrepareGraphicsBindings(const ShaderStageRuntime& vertex,
                                        const ShaderStageRuntime& pixel, bool pixel_active) {
	GraphicsBindings bindings;
	PrepareGraphicsBindings(vertex, pixel, pixel_active, bindings);
	return bindings;
}

void RenderExecutor::PrepareGraphicsBindings(const ShaderStageRuntime& vertex,
                                             const ShaderStageRuntime& pixel, bool pixel_active,
                                             GraphicsBindings& bindings) {
	PrepareBindings(vertex, bindings.vertex);
	// Gate "bindspare": depth-only draws reset the pixel stage, which freed every vector of it
	// (vector<TextureBinding>::_Tidy from ~PreparedBindings) and the next draw allocated them
	// again. Park the storage in a spare instead; PrepareBindings resets the contents anyway.
	thread_local PreparedBindings pixel_spare;
	const bool                    spare = Common::Gates::Enabled(Common::Gates::Gate::BindSpare);
	if (pixel_active) {
		if (!bindings.pixel) {
			bindings.pixel.emplace();
			if (spare) {
				std::swap(*bindings.pixel, pixel_spare);
			}
		}
		PrepareBindings(pixel, *bindings.pixel);
	} else {
		if (spare && bindings.pixel) {
			std::swap(*bindings.pixel, pixel_spare);
		}
		bindings.pixel.reset();
	}
	FindBuffers(bindings.vertex);
	if (bindings.pixel) {
		FindBuffers(*bindings.pixel);
	}
	if (bindings.vertex.runtime->program->info.uses_dma ||
	    (bindings.pixel && bindings.pixel->runtime->program->info.uses_dma)) {
		m_context.PrepareBda();
	}
	RebindBuffers(bindings.vertex);
	if (bindings.pixel) {
		RebindBuffers(*bindings.pixel);
	}
	RebindImages(bindings.vertex);
	if (bindings.pixel) {
		RebindImages(*bindings.pixel);
	}
	ShadowQueue(bindings);
}

void RenderExecutor::ShadowQueue(const GraphicsBindings& bindings) {
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
	bool ok = add_stage(bindings.vertex);
	if (ok && bindings.pixel) {
		ok = add_stage(*bindings.pixel);
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

} // namespace

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
	ShaderRecompiler::IR::PushData push_data;
	bool                           has_push_data = false;
	constexpr auto                 GraphicsStages = vk::ShaderStageFlagBits::eVertex |
	                                                vk::ShaderStageFlagBits::eMeshEXT |
	                                                vk::ShaderStageFlagBits::eFragment;
	vk::ShaderStageFlags push_stages = pipeline_bind_point == vk::PipelineBindPoint::eGraphics
	                                       ? vk::ShaderStageFlagBits::eFragment
	                                       : vk::ShaderStageFlags {};
	for (const auto* prepared: prepared_bindings) {
		EXIT_IF(prepared == nullptr || prepared->runtime == nullptr || !*prepared->runtime);
		const auto& program = *prepared->runtime->program;
		write_count += program.bindings.descriptors.size();
		for (const auto& binding: program.bindings.descriptors) {
			descriptor_count += NativeDescriptorCount(binding);
		}
		const auto shader_stage = NativeShaderStage(program.stage);
		push_stages |= shader_stage;
		EXIT_IF((pipeline_bind_point == vk::PipelineBindPoint::eGraphics &&
		         (shader_stage & GraphicsStages) == vk::ShaderStageFlags {}) ||
		        (pipeline_bind_point == vk::PipelineBindPoint::eCompute &&
		         shader_stage != vk::ShaderStageFlagBits::eCompute));
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
	const bool cb_timed     = Common::DrawStat::On() &&
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
	const auto cb_finish = [&]() {
		if (!cb_timed) {
			return;
		}
		const auto emit = FS::NowNs() - cb_t;
		FS::Add(cb_pool ? FS::Counter::CommitPoolSets : FS::Counter::CommitPushSets, 1);
		FS::Add(cb_pool ? FS::Counter::CommitPoolTransitNs : FS::Counter::CommitPushTransitNs,
		        cb_transit);
		FS::Add(cb_pool ? FS::Counter::CommitPoolWriteNs : FS::Counter::CommitPushWriteNs,
		        cb_write);
		FS::Add(cb_pool ? FS::Counter::CommitPoolEmitNs : FS::Counter::CommitPushEmitNs, emit);
	};

	for (auto* prepared: prepared_bindings) {
		const auto& program       = *prepared->runtime->program;
		auto&       descriptors   = *prepared;
		const auto  shader_stage  = NativeShaderStage(program.stage);
		const auto  shader_stages = ShaderPipelineStages(shader_stage);
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

		for (uint32_t i = 0; i < program.info.images.size(); i++) {
			auto& image   = m_context.GetTextureCache().GetImage(descriptors.images[i].image_id);
			MaterializeDeferredDccClear(buffer, descriptors.images[i].image_id, image);
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

		m_image_occurrences.assign(descriptors.images.size(), 0);
		for (const auto& binding: program.bindings.descriptors) {
			vk::WriteDescriptorSet write {};
			write.dstBinding     = ShaderRecompiler::IR::NativeBinding(program.stage, binding.kind);
			write.descriptorType = NativeDescriptorType(binding.kind);
			write.descriptorCount   = NativeDescriptorCount(binding);
			const auto buffer_start = m_descriptor_buffers.size();
			const auto image_start  = m_descriptor_images.size();
			if (ShaderRecompiler::IR::ImageBindingResourceClass(binding.kind) !=
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
		for (uint32_t i = 0; i < descriptors.images.size(); i++) {
			const auto expected =
			    descriptors.images[i].mip_views.empty()
			        ? 1u
			        : static_cast<uint32_t>(descriptors.images[i].mip_views.size());
			EXIT_IF(m_image_occurrences[i] != expected);
		}

		const auto shader_data_dwords = program.bindings.ShaderDataDwords();
		EXIT_IF(prepared->shader_data.size() != shader_data_dwords);
		if (program.bindings.UsesPushData()) {
			std::ranges::copy(prepared->shader_data,
			                  push_data.dwords.begin() + program.bindings.push_data_start_dword);
			has_push_data = true;
		}
		cb_lap(cb_write);
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
		cb_finish();
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
	cb_finish();
}

} // namespace Libs::Graphics
