#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICCONTEXT_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICCONTEXT_H_

#include "common/abi.h"
#include "common/common.h"
#include "common/threads.h"
#include "graphics/host_gpu/vulkanCommon.h" // IWYU pragma: export

#include <atomic>
#include <functional>
#include <map>
#include <mutex>
#include <tuple>
#include <vector>
#include <vk_mem_alloc.h>

namespace Libs::Graphics {

struct VulkanImage;

// Runs `destroy` on a worker thread (Vulkan object destruction is externally synchronized only
// on the object itself, and the objects handed here are already retired). KYTY_ASYNC_DESTROY=0
// runs it inline. VulkanDeferredDestroyFlush waits for the queue to drain (device shutdown).
void VulkanDeferredDestroy(std::function<void()>&& destroy);
void VulkanDeferredDestroyFlush();
// MemStats: per-heap VMA budgets (KYTY_FRAME_TRACE, every 300 flips).
void VulkanLogMemoryStats();

inline constexpr uint32_t VULKAN_TARGET_API_VERSION = VK_API_VERSION_1_3;

struct GraphicContext {
	vk::Instance                       instance                              = nullptr;
	vk::DebugUtilsMessengerEXT         debug_messenger                       = nullptr;
	vk::PhysicalDevice                 physical_device                       = nullptr;
	vk::PhysicalDeviceProperties       physical_device_properties            = {};
	vk::PhysicalDeviceMemoryProperties physical_device_memory_properties     = {};
	vk::Device                         device                                = nullptr;
	VmaAllocator                       allocator                             = nullptr;
	// Sub-allocating pool for sampled images (KYTY_IMAGE_POOL=1, experiment): the driver prefers a
	// dedicated allocation for every image (vkAllocateMemory + vkBindImageMemory of ~250 images
	// cost ~35 ms at a scene cut), but sub-allocated images sample 25-40 % slower - off by default.
	VmaPool                            image_pool                            = nullptr;
	bool                               memory_budget_ext_enabled             = false;
	bool                               compute_subgroup_size_control_enabled = false;
	// VK_EXT_robustness2 robustBufferAccess2: out-of-range storage-buffer dwords read as zero,
	// so the shader emitter drops its own bounds branches (RobustBufferLoads).
	bool                               robust_buffer_access2_enabled         = false;
	// VK_EXT_robustness2 nullDescriptor: a VK_NULL_HANDLE buffer / image view in a descriptor
	// reads as zero and drops stores.  Used by the measurement gate "bindfloor" (session 97).
	bool                               null_descriptor_enabled               = false;
	// KYTY_PIPELINE_STATS=1: VK_KHR_pipeline_executable_properties (statistics + SASS dumps).
	bool                               pipeline_stats_enabled                = false;
	bool                               sample_rate_shading_enabled           = false;
	bool                               diagnostic_checkpoints_enabled        = false;
	bool                               gpu_breadcrumbs_enabled               = false;
	// Session 98 (patch_s98b): KYTY_GPU_MARKERS=1 and VK_AMD_buffer_marker present and loaded.
	bool                               gpu_markers_enabled                   = false;
	bool                               attachment_feedback_loop_enabled      = false;
	bool                               provoking_vertex_last_enabled         = false;
	// VK_EXT_external_memory_host (KYTY_HOST_IMPORT, default on): guest direct memory imported
	// as Vulkan buffers, so texture uploads read guest memory over PCIe without a host copy.
	bool                               external_memory_host_enabled          = false;
	uint64_t                           min_imported_host_pointer_alignment   = 0;
	// VK_EXT_image_view_min_lod (KYTY_MIP_DEFER, default on): sampled views of a texture whose
	// top mip levels are still pending clamp the LOD to the resident levels (TextureCache).
	bool                               image_view_min_lod_enabled            = false;
	// VK_KHR_dynamic_rendering_local_read (KYTY_LOCAL_READ, default on): a pipeline barrier whose
	// two stage masks are framebuffer-space stages may be recorded inside a render pass instance
	// started with vkCmdBeginRendering, so a shader-write barrier between two draws of the same
	// pass no longer has to end and restart the pass.
	bool                               dynamic_rendering_local_read_enabled  = false;
	bool                               supports_block_texel_view              = false;
	bool                                      mesh_shader_enabled                   = false;
	vk::PhysicalDeviceMeshShaderPropertiesEXT mesh_shader_properties                = {};
	uint32_t                           subgroup_size                         = 0;
	uint32_t                           min_subgroup_size                     = 0;
	uint32_t                           max_subgroup_size                     = 0;
	uint32_t                           max_push_descriptors                  = 0;
	vk::ShaderStageFlags               required_subgroup_size_stages         = {};
	Common::Mutex                      queue_mutex;
	uint32_t                           queue_family = static_cast<uint32_t>(-1);
	vk::Queue                          queue        = nullptr;

	[[nodiscard]] const vk::PhysicalDeviceProperties& GetPhysicalDeviceProperties() const {
		return physical_device_properties;
	}

	[[nodiscard]] const vk::PhysicalDeviceMemoryProperties&
	GetPhysicalDeviceMemoryProperties() const {
		return physical_device_memory_properties;
	}

	[[nodiscard]] vk::FormatProperties GetFormatProperties(vk::Format format) const {
		std::scoped_lock lock(m_format_properties_mutex);
		auto [it, inserted] = m_format_properties.try_emplace(format);
		if (inserted) {
			physical_device.getFormatProperties(format, &it->second);
		}
		return it->second;
	}

	[[nodiscard]] vk::Result GetImageFormatProperties(vk::Format format, vk::ImageType type,
	                                                  vk::ImageTiling            tiling,
	                                                  vk::ImageUsageFlags        usage,
	                                                  vk::ImageCreateFlags       flags,
	                                                  vk::ImageFormatProperties* properties) const {
		using Key = std::tuple<vk::Format, vk::ImageType, vk::ImageTiling, vk::ImageUsageFlags,
		                       vk::ImageCreateFlags>;
		std::scoped_lock lock(m_image_format_properties_mutex);
		auto [it, inserted] =
		    m_image_format_properties.try_emplace(Key {format, type, tiling, usage, flags});
		if (inserted) {
			it->second.first = physical_device.getImageFormatProperties(format, type, tiling, usage,
			                                                            flags, &it->second.second);
		}
		if (properties != nullptr) {
			*properties = it->second.second;
		}
		return it->second.first;
	}

	[[nodiscard]] bool SupportsComputeWave64() const noexcept {
		return subgroup_size == 64u || compute_subgroup_size_control_enabled;
	}

	[[nodiscard]] vk::DeviceSize StorageMinAlignment() const {
		const auto alignment = physical_device_properties.limits.minStorageBufferOffsetAlignment;
		return alignment != 0 ? alignment : 1;
	}

	[[nodiscard]] bool CreateAllocator();
	void               DestroyAllocator();
	void               LogMemoryBudget() const;
	[[nodiscard]] bool CanReportMemoryUsage() const noexcept { return memory_budget_ext_enabled; }
	[[nodiscard]] uint64_t GetDeviceMemoryUsage() const;
	[[nodiscard]] uint64_t GetTotalMemoryBudget() const;
	[[nodiscard]] bool     CreateImage(const vk::ImageCreateInfo& info, VulkanImage& image);
	void                   CreateImagePool();
	void                   DeleteImage(VulkanImage& image);
	// Keeps a retired image for CreateImage to hand out again (gate "imgrecycle"). The caller
	// guarantees the GPU no longer uses it; falls back to DeleteImage when it cannot be kept.
	void                   RecycleImage(VulkanImage& image);

	uint32_t screen_width  = 0;
	uint32_t screen_height = 0;

private:
	mutable std::mutex                                 m_format_properties_mutex;
	mutable std::map<vk::Format, vk::FormatProperties> m_format_properties;
	mutable std::mutex                                 m_image_format_properties_mutex;
	mutable std::map<std::tuple<vk::Format, vk::ImageType, vk::ImageTiling, vk::ImageUsageFlags,
	                            vk::ImageCreateFlags>,
	                 std::pair<vk::Result, vk::ImageFormatProperties>>
	    m_image_format_properties;
};

struct VulkanImageState {
	vk::PipelineStageFlags2 pl_stage    = vk::PipelineStageFlagBits2::eAllCommands;
	vk::AccessFlags2        access_mask = vk::AccessFlagBits2::eNone;
	vk::ImageLayout         layout      = vk::ImageLayout::eUndefined;
	// Gate "atomimg": the write recorded here was made with image atomics only. Two such writes
	// in a row need no barrier between them; every other repeated write still does.
	bool                    atomic_write = false;
};

// Session 120, gate "spcen" (MEASUREMENT ONLY, ALWAYS counted - C:/kyty/s120/design/spcen.md s.1, s.3.1): the image
// layout/access state machine moved.  Global serial and per-backing serial (VulkanImage::state_serial); both move
// together, in Image::GetBarriers when it changes a state record (a barrier, a value change of `state`, a resize or
// clear of `subresource_states`) and in GraphicContext::CreateImage.  Write-only on every path but the census.
inline std::atomic<uint64_t> g_image_state_serial {0};
[[nodiscard]] inline uint64_t ImageStateSerial() noexcept {
	return g_image_state_serial.load(std::memory_order_relaxed);
}

struct VulkanImage {
	VulkanImage() = default;
	KYTY_CLASS_NO_COPY(VulkanImage);

	vk::Format                    format      = vk::Format::eUndefined;
	vk::ImageType                 image_type  = vk::ImageType::e2D;
	vk::Extent3D                  extent      = {1, 1, 1};
	uint32_t                      layers      = 1;
	uint32_t                      mip_levels  = 1;
	uint32_t                      samples     = 1;
	vk::ImageUsageFlags           usage       = {};
	vk::ImageCreateFlags          flags       = {};
	vk::Image                     image       = nullptr;
	VulkanImageState              state;
	std::vector<VulkanImageState> subresource_states;
	// Session 120, gate "spcen": see g_image_state_serial.  Grows VulkanImage 104 -> 112 B (both arms).
	uint64_t                      state_serial = 0;
	VmaAllocation                allocation = nullptr;

	void NoteStateChange() noexcept {
		state_serial++; // written where `state` itself is written (under the render mutex)
		g_image_state_serial.fetch_add(1, std::memory_order_relaxed);
	}
};



} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_GRAPHICCONTEXT_H_ */
