#include "graphics/host_gpu/renderer/pipeline/descriptorHeap.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/masterSemaphore.h"

#include <algorithm>
#include <cstdlib>

namespace Libs::Graphics {
namespace {

// Sets per pool and the descriptors backing them; both follow the knob "dspool" so one run can
// compare pool sizes. The pool sizes keep the ratios the 1024-set pool was built with.
uint32_t DescriptorHeapSets() {
	const auto value = Common::Gates::Value(Common::Gates::Knob::DescriptorPoolSets);
	return value < 64 ? 64u : value;
}

} // namespace

DescriptorHeap::DescriptorHeap(GraphicContext& graphics, MasterSemaphore& master_semaphore)
    : m_graphics(graphics), m_master_semaphore(master_semaphore) {
	CreateDescriptorPool();
}

DescriptorHeap::~DescriptorHeap() {
	if (std::getenv("KYTY_DESCRIPTOR_STATS") != nullptr) {
		LOGF("DescriptorHeap: allocation_calls=%llu resets=%llu reused=%llu pools=%zu\n",
		     static_cast<unsigned long long>(m_statistics.allocation_calls),
		     static_cast<unsigned long long>(m_statistics.pool_resets),
		     static_cast<unsigned long long>(m_statistics.reused_sets), m_pending_pools.size() + 1);
	}
	m_graphics.device.destroyDescriptorPool(m_current_pool.handle, nullptr);
	for (const auto& pool: m_pending_pools) {
		m_master_semaphore.Wait(pool.tick);
		m_graphics.device.destroyDescriptorPool(pool.handle, nullptr);
	}
	if (!m_ring_pools.empty()) {
		m_master_semaphore.Wait(m_ring_last_tick);
		for (const auto pool: m_ring_pools) {
			m_graphics.device.destroyDescriptorPool(pool, nullptr);
		}
	}
}

vk::DescriptorSet DescriptorHeap::CommitRing(vk::DescriptorSetLayout layout) {
	auto* ring = m_ring_last;
	if (layout != m_ring_last_layout || ring == nullptr) {
		ring               = &m_rings[layout];
		m_ring_last_layout = layout;
		m_ring_last        = ring;
	}
	const auto tick = m_master_semaphore.CurrentTick();
	if (ring->sets.empty() || !m_master_semaphore.IsFree(ring->ticks[ring->hint])) {
		// The known GPU tick is refreshed by the draw path every 200 us; ask the driver once
		// before growing, so a ring does not grow only because that value is stale.
		if (!ring->sets.empty()) {
			m_master_semaphore.Refresh();
		}
		if (ring->sets.empty() || !m_master_semaphore.IsFree(ring->ticks[ring->hint])) {
			// Rings never give memory back; past the cap a burst is served by the pools instead.
			static constexpr size_t RingMaxSets = 1024;
			if (ring->sets.size() >= RingMaxSets) {
				return nullptr;
			}
			GrowRing(layout, *ring);
		}
	}
	const auto index   = ring->hint;
	ring->ticks[index] = tick;
	ring->hint         = (index + 1) % ring->sets.size();
	m_ring_last_tick   = tick;
	Common::FrameStats::Add(Common::FrameStats::Counter::DescriptorRingIssued, 1);
	return ring->sets[index];
}

void DescriptorHeap::GrowRing(vk::DescriptorSetLayout layout, Ring& ring) {
	// Double the ring, at least 4 and at most one allocation call's worth of sets.
	auto count = static_cast<uint32_t>(std::clamp<size_t>(ring.sets.size(), 4, DescriptorSetBatch));
	std::array<vk::DescriptorSetLayout, DescriptorSetBatch> layouts;
	layouts.fill(layout);
	std::array<vk::DescriptorSet, DescriptorSetBatch> allocated;
	bool fresh_pool = false;
	if (m_ring_pools.empty()) {
		m_ring_pools.push_back(CreatePool(4096));
		fresh_pool = true;
	}
	for (;;) {
		vk::DescriptorSetAllocateInfo allocate {};
		allocate.descriptorPool     = m_ring_pools.back();
		allocate.descriptorSetCount = count;
		allocate.pSetLayouts        = layouts.data();
		const auto result = m_graphics.device.allocateDescriptorSets(&allocate, allocated.data());
		Common::FrameStats::Add(Common::FrameStats::Counter::DescriptorRingGrows, 1);
		if (result == vk::Result::eSuccess) {
			break;
		}
		EXIT_IF(result != vk::Result::eErrorOutOfPoolMemory &&
		        result != vk::Result::eErrorFragmentedPool);
		if (!fresh_pool) {
			m_ring_pools.push_back(CreatePool(4096));
			fresh_pool = true;
			continue;
		}
		// A fresh pool cannot hold this many sets of this layout: ask for fewer.
		EXIT_IF(count == 1);
		count /= 2;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::DescriptorRingSets, count);
	// New sets are free (tick 0) and go in front of the oldest one, which keeps the ring ordered
	// by the tick each set was last handed out for, starting at hint.
	const auto at = static_cast<std::ptrdiff_t>(ring.hint);
	ring.sets.insert(ring.sets.begin() + at, allocated.begin(), allocated.begin() + count);
	ring.ticks.insert(ring.ticks.begin() + at, count, uint64_t {0});
}

vk::DescriptorSet DescriptorHeap::Commit(vk::DescriptorSetLayout layout) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(layout == nullptr);

	if (Common::Gates::Enabled(Common::Gates::Gate::DescriptorRing)) {
		if (const auto set = CommitRing(layout); set != nullptr) {
			return set;
		}
		// The ring of this layout is at its cap and busy: the pooled path below serves this draw.
	}
	static const bool reuse_sets = [] {
		const auto* value = std::getenv("KYTY_DESCRIPTOR_REUSE");
		return value == nullptr || value[0] != '0';
	}();
	for (;;) {
		auto& batch = m_current_pool.sets[layout];
		if (batch.cursor < batch.sets.size() || Allocate(layout, batch)) {
			m_current_pool.used = true;
			m_statistics.reused_sets += batch.cursor < batch.retained;
			return batch.sets[batch.cursor++];
		}
		if (!m_current_pool.used) {
			// A retired pool can contain sets for a different scene's layouts. Nothing
			// from this activation was issued, so reclaim those allocations safely.
			ResetPool();
			auto& fresh = m_current_pool.sets[layout];
			EXIT_IF(!Allocate(layout, fresh));
			m_current_pool.used = true;
			return fresh.sets[fresh.cursor++];
		}
		m_current_pool.tick = m_master_semaphore.CurrentTick();
		m_pending_pools.push_back(std::move(m_current_pool));
		m_current_pool = {};
		if (m_master_semaphore.IsFree(m_pending_pools.front().tick)) {
			m_current_pool = std::move(m_pending_pools.front());
			m_pending_pools.pop_front();
			m_current_pool.used = false;
			if (reuse_sets) {
				// The last submission using any set in this pool has completed. All
				// writes are supplied again by CommitBindings before the next bind.
				for (auto& [key, retained]: m_current_pool.sets) {
					retained.cursor = 0;
					retained.retained = retained.sets.size();
				}
			} else {
				ResetPool();
			}
		} else {
			CreateDescriptorPool();
		}
	}
}

void DescriptorHeap::ResetPool() {
	EXIT_IF(m_current_pool.used);
	EXIT_IF(m_graphics.device.resetDescriptorPool(m_current_pool.handle, {}) != vk::Result::eSuccess);
	++m_statistics.pool_resets;
	m_current_pool.sets.clear();
	m_current_pool.allocated_count = 0;
}

bool DescriptorHeap::Allocate(vk::DescriptorSetLayout layout, Batch& batch) {
	if (batch.exhausted) return false;
	// Some drivers permit allocations beyond the pool sizes. Keep retained host
	// storage bounded and make retirement independent of that implementation choice.
	const auto pool_sets = DescriptorHeapSets();
	if (m_current_pool.allocated_count >= pool_sets) {
		batch.exhausted = true;
		return false;
	}
	if (batch.allocation == 0) {
		const auto knob  = Common::Gates::Value(Common::Gates::Knob::DescriptorSetBatch);
		batch.allocation = knob == 0 ? 1u : std::min(knob, DescriptorSetBatch);
	}
	batch.allocation = std::min(batch.allocation, pool_sets - m_current_pool.allocated_count);
	std::array<vk::DescriptorSetLayout, DescriptorSetBatch> layouts;
	layouts.fill(layout);
	std::array<vk::DescriptorSet, DescriptorSetBatch> allocated;

	vk::DescriptorSetAllocateInfo allocate {};
	allocate.descriptorPool = m_current_pool.handle;
	allocate.pSetLayouts    = layouts.data();

	for (;;) {
		allocate.descriptorSetCount = batch.allocation;
		++m_statistics.allocation_calls;
		const auto result = m_graphics.device.allocateDescriptorSets(&allocate, allocated.data());
		if (result == vk::Result::eSuccess) {
			m_current_pool.allocated_count += batch.allocation;
			Common::FrameStats::Add(Common::FrameStats::Counter::DescriptorAllocations, 1);
			batch.sets.insert(batch.sets.end(), allocated.begin(), allocated.begin() + batch.allocation);
			return true;
		}
		EXIT_IF(result != vk::Result::eErrorOutOfPoolMemory &&
		        result != vk::Result::eErrorFragmentedPool);
		if (batch.allocation == 1) {
			batch.exhausted = true;
			return false;
		}
		batch.allocation /= 2;
	}
}

void DescriptorHeap::CreateDescriptorPool() {
	m_current_pool.handle = CreatePool(DescriptorHeapSets());
}

vk::DescriptorPool DescriptorHeap::CreatePool(uint32_t sets) const {
	vk::DescriptorPool             handle     = nullptr;
	const std::array               pool_sizes = {
        vk::DescriptorPoolSize {vk::DescriptorType::eStorageBuffer, 8 * sets},
        vk::DescriptorPoolSize {vk::DescriptorType::eUniformBuffer, 4 * sets},
        vk::DescriptorPoolSize {vk::DescriptorType::eSampledImage, 8 * sets},
        vk::DescriptorPoolSize {vk::DescriptorType::eStorageImage, 1 * sets},
        vk::DescriptorPoolSize {vk::DescriptorType::eSampler, 1 * sets},
    };
	vk::DescriptorPoolCreateInfo create {};
	create.maxSets       = sets;
	create.poolSizeCount = static_cast<uint32_t>(pool_sizes.size());
	create.pPoolSizes    = pool_sizes.data();
	EXIT_IF(m_graphics.device.createDescriptorPool(&create, nullptr, &handle) !=
	        vk::Result::eSuccess);
	return handle;
}

} // namespace Libs::Graphics
