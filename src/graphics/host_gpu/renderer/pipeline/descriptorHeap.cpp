#include "graphics/host_gpu/renderer/pipeline/descriptorHeap.h"

#include "common/assert.h"
#include "common/logging/log.h"
#include "common/profiler.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/masterSemaphore.h"

#include <cstdlib>

namespace Libs::Graphics {
namespace {

constexpr uint32_t   DescriptorHeapCount = 1024;
constexpr std::array DescriptorPoolSizes = {
    vk::DescriptorPoolSize {vk::DescriptorType::eStorageBuffer, 8192},
    vk::DescriptorPoolSize {vk::DescriptorType::eUniformBuffer, 4096},
    vk::DescriptorPoolSize {vk::DescriptorType::eSampledImage, 8192},
    vk::DescriptorPoolSize {vk::DescriptorType::eStorageImage, 1024},
    vk::DescriptorPoolSize {vk::DescriptorType::eSampler, 1024},
};

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
}

vk::DescriptorSet DescriptorHeap::Commit(vk::DescriptorSetLayout layout) {
	KYTY_PROFILER_FUNCTION();
	EXIT_IF(layout == nullptr);

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
	if (m_current_pool.allocated_count == DescriptorHeapCount) {
		batch.exhausted = true;
		return false;
	}
	batch.allocation = std::min(batch.allocation, DescriptorHeapCount - m_current_pool.allocated_count);
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
	vk::DescriptorPoolCreateInfo create {};
	create.maxSets       = DescriptorHeapCount;
	create.poolSizeCount = static_cast<uint32_t>(DescriptorPoolSizes.size());
	create.pPoolSizes    = DescriptorPoolSizes.data();
	EXIT_IF(m_graphics.device.createDescriptorPool(&create, nullptr, &m_current_pool.handle) !=
	        vk::Result::eSuccess);
}

} // namespace Libs::Graphics
