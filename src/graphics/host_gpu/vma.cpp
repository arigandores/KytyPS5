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
	return true;
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

void GraphicContext::DestroyAllocator() {
	if (allocator == nullptr) {
		return;
	}
	VulkanDeferredDestroyFlush();
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

bool GraphicContext::CreateImage(const vk::ImageCreateInfo& image_info, VulkanImage& image) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(allocator == nullptr || image.image != nullptr || image.allocation != nullptr);

	VmaAllocationCreateInfo alloc_info {};
	alloc_info.requiredFlags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;

	vk::Image::CType native_image = VK_NULL_HANDLE;
	const auto        result       = static_cast<vk::Result>(
	    vmaCreateImage(allocator, static_cast<const vk::ImageCreateInfo::NativeType*>(image_info),
	                   &alloc_info, &native_image, &image.allocation, nullptr));
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
