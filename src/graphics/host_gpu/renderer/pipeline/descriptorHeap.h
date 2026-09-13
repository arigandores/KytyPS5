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
	// Gate "dsring": one ring of sets per layout, each set stamped with the tick it was last
	// handed out for. Commit dispatches here while the gate is on.
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
	[[nodiscard]] vk::DescriptorPool CreatePool(uint32_t sets) const;
	void               ResetPool();

	// Gate "dsring". The batches above are keyed by layout, but a pool is retired as soon as one
	// layout's batch runs out and a reused pool is reset by the first layout it has no sets for:
	// with a layout per pipeline, a fresh pool serves exactly dspool/dsbatch layouts, and Sky
	// Garden allocated ~250 times a frame, about twice the sets it used. A ring never resets: the
	// set at `hint` is the one handed out longest ago, so when its tick is not complete no set of
	// the ring is, and the ring grows at that position (the order stays oldest-first from hint).
	struct Ring {
		std::vector<vk::DescriptorSet> sets;
		std::vector<uint64_t>          ticks;
		size_t                         hint = 0;
	};
	[[nodiscard]] vk::DescriptorSet CommitRing(vk::DescriptorSetLayout layout);
	void                            GrowRing(vk::DescriptorSetLayout layout, Ring& ring);

	GraphicContext&                                     m_graphics;
	MasterSemaphore&                                    m_master_semaphore;
	Pool                                                m_current_pool;
	std::deque<Pool>                                    m_pending_pools;
	// Gate "dsring". Node-based map: a Ring& stays valid while other layouts are added.
	std::unordered_map<vk::DescriptorSetLayout, Ring>   m_rings;
	std::vector<vk::DescriptorPool>                     m_ring_pools; // never reset, grow only
	vk::DescriptorSetLayout                             m_ring_last_layout = nullptr;
	Ring*                                               m_ring_last        = nullptr;
	uint64_t                                            m_ring_last_tick   = 0;
	Statistics                                         m_statistics;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORHEAP_H_
