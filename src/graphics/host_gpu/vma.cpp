#include "graphics/host_gpu/vulkanCommon.h"

#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wnullability-completeness"
#pragma clang diagnostic ignored "-Wunused-private-field"
#pragma clang diagnostic ignored "-Wunused-variable"
#endif

#define VMA_IMPLEMENTATION
#include <vk_mem_alloc.h>

#if defined(__clang__)
#pragma clang diagnostic pop
#endif

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "graphics/host_gpu/graphicContext.h"

#include <thread>
#include <mutex>
#include <functional>
#include <deque>
#include <cstring>
#include <condition_variable>
#include <algorithm>
#include <cinttypes>

namespace Libs::Graphics {

namespace {
const GraphicContext* g_memory_context = nullptr;
} // namespace

bool GraphicContext::CreateAllocator() {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(instance == nullptr || physical_device == nullptr || device == nullptr ||
	        allocator != nullptr);

	VmaVulkanFunctions functions {};
	functions.vkGetInstanceProcAddr = VULKAN_HPP_DEFAULT_DISPATCHER.vkGetInstanceProcAddr;
	functions.vkGetDeviceProcAddr   = VULKAN_HPP_DEFAULT_DISPATCHER.vkGetDeviceProcAddr;

	VmaAllocatorCreateInfo info {};
	info.instance         = instance;
	info.physicalDevice   = physical_device;
	info.device           = device;
	info.pVulkanFunctions = &functions;
	info.vulkanApiVersion = VULKAN_TARGET_API_VERSION;
	info.flags = VMA_ALLOCATOR_CREATE_BUFFER_DEVICE_ADDRESS_BIT;
	if (memory_budget_ext_enabled) {
		info.flags |= VMA_ALLOCATOR_CREATE_EXT_MEMORY_BUDGET_BIT;
	}

	const auto result = static_cast<vk::Result>(vmaCreateAllocator(&info, &allocator));
	if (result != vk::Result::eSuccess) {
		LOGF("vmaCreateAllocator failed: %s\n", vk::to_string(result).c_str());
		return false;
	}
	g_memory_context = this;
	CreateImagePool();
	return true;
}

void GraphicContext::CreateImagePool() {
	// Measured (session 25): sub-allocated sampled images make the GPU 25-40 % slower on NVIDIA
	// (56a1 558 -> 950 us, PS 57611 477 -> 751 us at equal clocks) - the driver's preference for a
	// dedicated allocation is not cosmetic. Opt-in only.
	const char* env = std::getenv("KYTY_IMAGE_POOL");
	if (env == nullptr || env[0] != '1') {
		return;
	}
	vk::ImageCreateInfo sample {};
	sample.imageType   = vk::ImageType::e2D;
	sample.format      = vk::Format::eBc7UnormBlock;
	sample.extent      = vk::Extent3D {1024, 1024, 1};
	sample.mipLevels   = 1;
	sample.arrayLayers = 1;
	sample.samples     = vk::SampleCountFlagBits::e1;
	sample.tiling      = vk::ImageTiling::eOptimal;
	sample.usage       = vk::ImageUsageFlagBits::eSampled | vk::ImageUsageFlagBits::eTransferDst |
	               vk::ImageUsageFlagBits::eTransferSrc;
	VmaAllocationCreateInfo alloc_info {};
	alloc_info.requiredFlags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
	uint32_t type_index      = 0;
	auto     result          = static_cast<vk::Result>(vmaFindMemoryTypeIndexForImageInfo(
        allocator, static_cast<const vk::ImageCreateInfo::NativeType*>(sample), &alloc_info,
        &type_index));
	if (result != vk::Result::eSuccess) {
		LOGF("ImagePool: no memory type for sampled images (%s)\n", vk::to_string(result).c_str());
		return;
	}
	VmaPoolCreateInfo pool_info {};
	pool_info.memoryTypeIndex = type_index;
	pool_info.blockSize       = 256ull * 1024 * 1024;
	result = static_cast<vk::Result>(vmaCreatePool(allocator, &pool_info, &image_pool));
	if (result != vk::Result::eSuccess) {
		LOGF("ImagePool: vmaCreatePool failed (%s)\n", vk::to_string(result).c_str());
		image_pool = nullptr;
		return;
	}
	LOGF("ImagePool: memory type %u, block 256 MB\n", type_index);
}

void VulkanLogMemoryStats() {
	const auto* context = g_memory_context;
	if (context == nullptr || context->allocator == nullptr) {
		return;
	}
	const auto& properties = context->GetPhysicalDeviceMemoryProperties();
	VmaBudget budgets[VK_MAX_MEMORY_HEAPS] {};
	vmaGetHeapBudgets(context->allocator, budgets);
	for (uint32_t i = 0; i < properties.memoryHeapCount; i++) {
		LOGF("MemStats: heap=%u flags=0x%x size=%" PRIu64 " usage=%" PRIu64 " budget=%" PRIu64
		     " allocation=%" PRIu64 " blocks=%" PRIu64 "\n",
		     i, static_cast<uint32_t>(properties.memoryHeaps[i].flags),
		     static_cast<uint64_t>(properties.memoryHeaps[i].size),
		     static_cast<uint64_t>(budgets[i].usage), static_cast<uint64_t>(budgets[i].budget),
		     static_cast<uint64_t>(budgets[i].statistics.allocationBytes),
		     static_cast<uint64_t>(budgets[i].statistics.blockBytes));
	}
}

// ---------------------------------------------------------------------------------------------
// Deferred destruction worker. vmaDestroyBuffer / vmaDestroyImage / vkDestroyImageView take
// 100-200 us each on the NVIDIA driver and ASTRO BOT retires several buffers and images per frame
// on the GuestGpu thread (0.8 ms/frame in the deferred-operation callbacks). VMA is internally
// synchronized and the objects are already unreachable when they get here.
namespace {

class DeferredDestroyer {
public:
	static DeferredDestroyer& Instance() {
		// Leaked on purpose: the worker may still be running during static destruction.
		static auto* instance = new DeferredDestroyer();
		return *instance;
	}

	[[nodiscard]] static bool Enabled() {
		static const bool enabled = [] {
			const char* value = std::getenv("KYTY_ASYNC_DESTROY");
			return value == nullptr || std::strcmp(value, "0") != 0;
		}();
		return enabled;
	}

	void Push(std::function<void()>&& fn) {
		std::lock_guard lock(m_mutex);
		if (!m_started) {
			m_started = true;
			std::thread([this] { Run(); }).detach();
		}
		m_queue.push_back(std::move(fn));
		m_available.notify_one();
	}

	void Flush() {
		std::unique_lock lock(m_mutex);
		m_drained.wait(lock, [this] { return m_queue.empty() && !m_running; });
	}

private:
	void Run() {
		std::unique_lock lock(m_mutex);
		for (;;) {
			m_available.wait(lock, [this] { return !m_queue.empty(); });
			auto fn = std::move(m_queue.front());
			m_queue.pop_front();
			m_running = true;
			lock.unlock();
			fn();
			lock.lock();
			m_running = false;
			if (m_queue.empty()) {
				m_drained.notify_all();
			}
		}
	}

	std::mutex                        m_mutex;
	std::condition_variable           m_available;
	std::condition_variable           m_drained;
	std::deque<std::function<void()>> m_queue;
	bool                              m_started = false;
	bool                              m_running = false;
};

} // namespace

void VulkanDeferredDestroy(std::function<void()>&& destroy) {
	if (!DeferredDestroyer::Enabled()) {
		destroy();
		return;
	}
	DeferredDestroyer::Instance().Push(std::move(destroy));
}

void VulkanDeferredDestroyFlush() {
	if (DeferredDestroyer::Enabled()) {
		DeferredDestroyer::Instance().Flush();
	}
}

namespace {
void ReleaseRecycledImages();
} // namespace

void GraphicContext::DestroyAllocator() {
	if (allocator == nullptr) {
		return;
	}
	ReleaseRecycledImages();
	VulkanDeferredDestroyFlush();
	if (image_pool != nullptr) {
		vmaDestroyPool(allocator, image_pool);
		image_pool = nullptr;
	}
	vmaDestroyAllocator(allocator);
	allocator = nullptr;
}

void GraphicContext::LogMemoryBudget() const {
	if (allocator == nullptr || physical_device == nullptr) {
		return;
	}

	const auto& properties = GetPhysicalDeviceMemoryProperties();
	VmaBudget   budgets[VK_MAX_MEMORY_HEAPS] {};
	vmaGetHeapBudgets(allocator, budgets);
	for (uint32_t i = 0; i < properties.memoryHeapCount; i++) {
		LOGF("VMA heap %u: usage=%" PRIu64 ", budget=%" PRIu64 ", allocation=%" PRIu64
		     ", blocks=%" PRIu64 "\n",
		     i, static_cast<uint64_t>(budgets[i].usage), static_cast<uint64_t>(budgets[i].budget),
		     static_cast<uint64_t>(budgets[i].statistics.allocationBytes),
		     static_cast<uint64_t>(budgets[i].statistics.blockBytes));
	}
}

uint64_t GraphicContext::GetDeviceMemoryUsage() const {
	if (!CanReportMemoryUsage() || allocator == nullptr) {
		return 0;
	}
	VmaBudget budgets[VK_MAX_MEMORY_HEAPS] {};
	vmaGetHeapBudgets(allocator, budgets);
	const bool discrete =
	    physical_device_properties.deviceType == vk::PhysicalDeviceType::eDiscreteGpu;
	uint64_t usage = 0;
	for (uint32_t heap = 0; heap < physical_device_memory_properties.memoryHeapCount; heap++) {
		const bool device_local =
		    static_cast<bool>(physical_device_memory_properties.memoryHeaps[heap].flags &
		                      vk::MemoryHeapFlagBits::eDeviceLocal);
		if (!discrete || device_local) {
			usage += budgets[heap].usage;
		}
	}
	return usage;
}

uint64_t GraphicContext::GetTotalMemoryBudget() const {
	if (allocator == nullptr) {
		return 0;
	}
	VmaBudget budgets[VK_MAX_MEMORY_HEAPS] {};
	vmaGetHeapBudgets(allocator, budgets);
	const bool discrete =
	    physical_device_properties.deviceType == vk::PhysicalDeviceType::eDiscreteGpu;
	uint64_t budget = 0;
	uint64_t local  = 0;
	uint64_t usage  = 0;
	for (uint32_t heap = 0; heap < physical_device_memory_properties.memoryHeapCount; heap++) {
		const auto& properties = physical_device_memory_properties.memoryHeaps[heap];
		const bool  device_local =
		    static_cast<bool>(properties.flags & vk::MemoryHeapFlagBits::eDeviceLocal);
		if (device_local) {
			local += properties.size;
		}
		if (!discrete || device_local) {
			budget += CanReportMemoryUsage() ? budgets[heap].budget : properties.size;
			usage += CanReportMemoryUsage() ? budgets[heap].usage : 0;
		}
	}
	if (discrete) {
		return budget - std::min<uint64_t>(budget / 8, 1024ull * 1024 * 1024);
	}
	constexpr uint64_t system_reserve = 8ull * 1024 * 1024 * 1024;
	const auto         available      = budget > usage ? budget - usage : uint64_t {0};
	return std::max(local, available > system_reserve ? available - system_reserve : uint64_t {0});
}

namespace {

// Retired images of the texture cache kept for reuse (gate "imgrecycle").
struct RecycledImage {
	VmaAllocator         allocator  = nullptr;
	vk::Format           format     = vk::Format::eUndefined;
	vk::ImageType        image_type = vk::ImageType::e2D;
	vk::Extent3D         extent     = {};
	uint32_t             layers     = 0;
	uint32_t             mip_levels = 0;
	uint32_t             samples    = 0;
	vk::ImageUsageFlags  usage      = {};
	vk::ImageCreateFlags flags      = {};
	vk::Image            image      = nullptr;
	VmaAllocation        allocation = nullptr;
	uint64_t             bytes      = 0;
	uint64_t             retired_ns = 0;
};

constexpr uint64_t RecycleMaxBytes = 256ull << 20u;
constexpr size_t   RecycleMaxCount = 64;
constexpr uint64_t RecycleMaxAgeNs = 2'000'000'000ull;

std::mutex                g_recycle_mutex;
std::deque<RecycledImage> g_recycled;
uint64_t                  g_recycled_bytes = 0;

// g_recycle_mutex held: destroys entries beyond the limits (all of them with `everything`),
// oldest first.
void TrimRecycledImages(uint64_t now_ns, bool everything = false) {
	while (!g_recycled.empty() &&
	       (everything || g_recycled_bytes > RecycleMaxBytes || g_recycled.size() > RecycleMaxCount ||
	        now_ns - g_recycled.front().retired_ns > RecycleMaxAgeNs)) {
		const auto entry = g_recycled.front();
		g_recycled.pop_front();
		g_recycled_bytes -= entry.bytes;
		VulkanDeferredDestroy([entry] {
			vmaDestroyImage(entry.allocator, entry.image, entry.allocation);
		});
	}
}

void ReleaseRecycledImages() {
	std::lock_guard lock(g_recycle_mutex);
	TrimRecycledImages(0, true);
}

} // namespace

void GraphicContext::RecycleImage(VulkanImage& image) {
	EXIT_IF(allocator == nullptr || image.image == nullptr || image.allocation == nullptr);
	if (image_pool != nullptr || !Common::Gates::Enabled(Common::Gates::Gate::ImageRecycle)) {
		ReleaseRecycledImages(); // the gate may have been switched off with entries still kept
		DeleteImage(image);
		return;
	}
	VmaAllocationInfo allocation_info {};
	vmaGetAllocationInfo(allocator, image.allocation, &allocation_info);
	{
		std::lock_guard lock(g_recycle_mutex);
		const auto      now = Common::FrameStats::NowNs();
		g_recycled.push_back({allocator, image.format, image.image_type, image.extent, image.layers,
		                      image.mip_levels, image.samples, image.usage, image.flags, image.image,
		                      image.allocation, allocation_info.size, now});
		g_recycled_bytes += allocation_info.size;
		TrimRecycledImages(now);
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::ImgRecyclePuts, 1);
	image.image      = nullptr;
	image.allocation = nullptr;
}

bool GraphicContext::CreateImage(const vk::ImageCreateInfo& image_info, VulkanImage& image) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(allocator == nullptr || image.image != nullptr || image.allocation != nullptr);

	if (image_pool == nullptr && image_info.pNext == nullptr &&
	    image_info.tiling == vk::ImageTiling::eOptimal &&
	    image_info.sharingMode == vk::SharingMode::eExclusive &&
	    Common::Gates::Enabled(Common::Gates::Gate::ImageRecycle)) {
		std::lock_guard lock(g_recycle_mutex);
		TrimRecycledImages(Common::FrameStats::NowNs());
		const auto found = std::find_if(g_recycled.begin(), g_recycled.end(), [&](const RecycledImage& entry) {
			return entry.allocator == allocator &&
			       entry.format == image_info.format && entry.image_type == image_info.imageType &&
			       entry.extent == image_info.extent && entry.layers == image_info.arrayLayers &&
			       entry.mip_levels == image_info.mipLevels &&
			       entry.samples == static_cast<uint32_t>(image_info.samples) &&
			       entry.usage == image_info.usage && entry.flags == image_info.flags;
		});
		if (found != g_recycled.end()) {
			image.image      = found->image;
			image.allocation = found->allocation;
			g_recycled_bytes -= found->bytes;
			g_recycled.erase(found);
			image.format     = image_info.format;
			image.image_type = image_info.imageType;
			image.extent     = image_info.extent;
			image.layers     = image_info.arrayLayers;
			image.mip_levels = image_info.mipLevels;
			image.samples    = static_cast<uint32_t>(image_info.samples);
			image.usage      = image_info.usage;
			image.flags      = image_info.flags;
			// Whatever layout the image was left in, the first transition from undefined is valid
			// and discards the old content, as for a new image.
			image.state      = {.layout = vk::ImageLayout::eUndefined};
			image.subresource_states.clear();
			Common::FrameStats::Add(Common::FrameStats::Counter::ImgRecycleHits, 1);
			return true;
		}
	}

	VmaAllocationCreateInfo alloc_info {};
	alloc_info.requiredFlags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
	const bool attachment    = static_cast<bool>(
        image_info.usage & (vk::ImageUsageFlagBits::eColorAttachment |
                            vk::ImageUsageFlagBits::eDepthStencilAttachment));
	if (image_pool != nullptr && !attachment && image_info.samples == vk::SampleCountFlagBits::e1) {
		alloc_info.pool = image_pool;
	}

	vk::Image::CType native_image = VK_NULL_HANDLE;
	auto             result       = static_cast<vk::Result>(
	    vmaCreateImage(allocator, static_cast<const vk::ImageCreateInfo::NativeType*>(image_info),
	                   &alloc_info, &native_image, &image.allocation, nullptr));
	if (result != vk::Result::eSuccess && alloc_info.pool == nullptr) {
		// Memory kept for reuse may be what is missing.
		ReleaseRecycledImages();
		VulkanDeferredDestroyFlush();
		native_image = VK_NULL_HANDLE;
		result       = static_cast<vk::Result>(vmaCreateImage(
            allocator, static_cast<const vk::ImageCreateInfo::NativeType*>(image_info), &alloc_info,
            &native_image, &image.allocation, nullptr));
	}
	if (result != vk::Result::eSuccess && alloc_info.pool != nullptr) {
		// Memory type or size the pool cannot serve: fall back to the default allocation path.
		alloc_info.pool = nullptr;
		native_image    = VK_NULL_HANDLE;
		result          = static_cast<vk::Result>(vmaCreateImage(
            allocator, static_cast<const vk::ImageCreateInfo::NativeType*>(image_info), &alloc_info,
            &native_image, &image.allocation, nullptr));
	}
	image.image = native_image;
	if (result != vk::Result::eSuccess) {
		LogMemoryBudget();
		return false;
	}

	image.format     = image_info.format;
	image.image_type = image_info.imageType;
	image.extent     = image_info.extent;
	image.layers     = image_info.arrayLayers;
	image.mip_levels = image_info.mipLevels;
	image.samples    = static_cast<uint32_t>(image_info.samples);
	image.usage      = image_info.usage;
	image.flags      = image_info.flags;
	image.state      = {.layout = image_info.initialLayout};
	image.subresource_states.clear();

	return true;
}

void GraphicContext::DeleteImage(VulkanImage& image) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(allocator == nullptr || image.image == nullptr || image.allocation == nullptr);

	{
		const auto vma_allocator = allocator;
		const auto vk_image      = image.image;
		const auto allocation    = image.allocation;
		VulkanDeferredDestroy([vma_allocator, vk_image, allocation] {
			vmaDestroyImage(vma_allocator, vk_image, allocation);
		});
	}
	image.image      = nullptr;
	image.allocation = nullptr;
}

} // namespace Libs::Graphics
