#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORHEAP_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORHEAP_H_

#include "common/common.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <array>
#include <deque>
#include <unordered_map>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
class MasterSemaphore;

class DescriptorHeap {
public:
	DescriptorHeap(GraphicContext& graphics, MasterSemaphore& master_semaphore);
	~DescriptorHeap();
	KYTY_CLASS_NO_COPY(DescriptorHeap);

	[[nodiscard]] vk::DescriptorSet Commit(vk::DescriptorSetLayout layout);
	struct Statistics {
		uint64_t allocation_calls = 0;
		uint64_t pool_resets = 0;
		uint64_t reused_sets = 0;
	};
	[[nodiscard]] const Statistics& GetStatistics() const noexcept { return m_statistics; }

private:
	// Upper bound of one vkAllocateDescriptorSets; the knob "dsbatch" picks the value used.
	static constexpr uint32_t DescriptorSetBatch = 256;

	struct Batch {
		std::vector<vk::DescriptorSet> sets;
		size_t                         cursor     = 0;
		size_t                         retained   = 0;
		uint32_t                       allocation = 0; // set from the knob on first use
		bool                           exhausted  = false;
	};
	struct Pool {
		vk::DescriptorPool handle = nullptr;
		std::unordered_map<vk::DescriptorSetLayout, Batch> sets;
		uint64_t tick = 0;
		uint32_t allocated_count = 0;
		bool used = false;
	};

	[[nodiscard]] bool Allocate(vk::DescriptorSetLayout layout, Batch& batch);
	void               CreateDescriptorPool();
	void               ResetPool();

	GraphicContext&                                     m_graphics;
	MasterSemaphore&                                    m_master_semaphore;
	Pool                                                m_current_pool;
	std::deque<Pool>                                    m_pending_pools;
	Statistics                                         m_statistics;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORHEAP_H_
