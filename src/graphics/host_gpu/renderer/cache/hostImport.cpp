#include "graphics/host_gpu/renderer/cache/hostImport.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "kernel/memory.h"

#include <algorithm>
#include <cstdlib>
#include <thread>
#include <vector>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

namespace Libs::Graphics {

namespace {

uint64_t ChunkBytes() {
	const char* value = std::getenv("KYTY_HOST_IMPORT_MB");
	const auto  mb    = value != nullptr ? std::strtoull(value, nullptr, 10) : 512u;
	return std::clamp<uint64_t>(mb, 64u, 4096u) << 20u;
}

} // namespace

HostImport::HostImport(GraphicContext& graphics): m_graphics(graphics) {
	if (!graphics.external_memory_host_enabled) {
		return;
	}
	m_base = Libs::LibKernel::Memory::GetBackingBase();
	m_size = Libs::LibKernel::Memory::GetBackingSize();
	const auto alignment = std::max<uint64_t>(graphics.min_imported_host_pointer_alignment, 4096u);
	if (m_base == 0 || m_size == 0 || (m_base % alignment) != 0 || (m_size % alignment) != 0) {
		LOGF("HostImport: backing alias unsuitable (base=0x%llx size=0x%llx alignment=%llu)\n",
		     static_cast<unsigned long long>(m_base), static_cast<unsigned long long>(m_size),
		     static_cast<unsigned long long>(alignment));
		return;
	}
	m_chunk_size = ChunkBytes();
	m_chunk_size -= m_chunk_size % alignment;
	m_chunks.resize(static_cast<size_t>((m_size + m_chunk_size - 1) / m_chunk_size));
	const char* sync = std::getenv("KYTY_HOST_IMPORT_SYNC");
	m_sync           = sync != nullptr && sync[0] == '1';
	m_available      = true;
	LOGF("HostImport: enabled, backing %llu MB in %zu chunks of %llu MB, import %s\n",
	     static_cast<unsigned long long>(m_size >> 20u), m_chunks.size(),
	     static_cast<unsigned long long>(m_chunk_size >> 20u),
	     m_sync ? "synchronous" : "in the background");
	Preload();
}

// Touches every page of the chunk through the alias: commits the untouched ones and warms the
// page-table entries the driver's import walks.
void HostImport::TouchChunk(size_t index) const {
	const auto        offset = index * m_chunk_size;
	const auto        size   = std::min(m_chunk_size, m_size - offset);
	volatile uint64_t sink   = 0;
	for (uint64_t page = 0; page < size; page += 4096u) {
		sink += *reinterpret_cast<const volatile uint8_t*>(m_base + offset + page);
	}
	(void)sink;
}

void HostImport::Preload() {
	const char* value   = std::getenv("KYTY_HOST_IMPORT_PRELOAD");
	bool        preload = false;
	if (value != nullptr) {
		preload = value[0] == '1';
	} else {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		MEMORYSTATUSEX status {};
		status.dwLength = sizeof(status);
		if (GlobalMemoryStatusEx(&status) != 0) {
			preload = status.ullTotalPhys >= m_size + (6ull << 30u);
			LOGF("HostImport: %llu MB of RAM, backing %llu MB: preload %s\n",
			     static_cast<unsigned long long>(status.ullTotalPhys >> 20u),
			     static_cast<unsigned long long>(m_size >> 20u), preload ? "on" : "off");
		}
#endif
	}
	if (!preload) {
		return;
	}
	const auto t0 = Common::FrameStats::NowNs();
	// Touching is page-fault bound and scales over cores; the imports serialize in the driver.
	{
		const unsigned           workers = std::clamp(std::thread::hardware_concurrency() / 2, 2u, 8u);
		std::atomic<size_t>      next {0};
		std::vector<std::thread> threads;
		for (unsigned t = 0; t < workers; t++) {
			threads.emplace_back([this, &next] {
				for (size_t index = next.fetch_add(1); index < m_chunks.size();
				     index        = next.fetch_add(1)) {
					TouchChunk(index);
				}
			});
		}
		for (auto& thread: threads) {
			thread.join();
		}
	}
	const auto t1 = Common::FrameStats::NowNs();
	for (size_t index = 0; index < m_chunks.size(); index++) {
		{
			std::lock_guard lock(m_mutex);
			m_chunks[index].state = State::Importing;
		}
		ImportChunk(index);
	}
	size_t ready = 0;
	for (const auto& chunk: m_chunks) {
		ready += chunk.state == State::Ready ? 1 : 0;
	}
	LOGF("HostImport: preloaded %zu/%zu chunks in %llu ms (pages touched in %llu ms)\n", ready,
	     m_chunks.size(), static_cast<unsigned long long>((Common::FrameStats::NowNs() - t0) / 1000000u),
	     static_cast<unsigned long long>((t1 - t0) / 1000000u));
}

HostImport::~HostImport() {
	while (m_in_flight.load() != 0) {
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	std::lock_guard lock(m_mutex);
	for (auto& chunk: m_chunks) {
		if (chunk.buffer != nullptr) {
			m_graphics.device.destroyBuffer(chunk.buffer, nullptr);
		}
		if (chunk.memory != nullptr) {
			m_graphics.device.freeMemory(chunk.memory, nullptr);
		}
	}
}

// Runs without the lock (the Vulkan calls are thread-safe on the device); publishes the result
// under it. The chunk is in state Importing meanwhile, so nobody else touches it.
void HostImport::ImportChunk(size_t index) {
	const auto       t0     = Common::FrameStats::NowNs();
	const auto       offset = index * m_chunk_size;
	const auto       size   = std::min(m_chunk_size, m_size - offset);
	auto*            host   = reinterpret_cast<void*>(m_base + offset);
	// Commit every page of the chunk first (a read through the alias is enough): the driver's
	// import locks the pages and would otherwise commit them itself under its device lock.
	TouchChunk(index);
	const auto t1 = Common::FrameStats::NowNs();
	vk::Buffer       buffer = nullptr;
	vk::DeviceMemory memory = nullptr;
	const auto       fail   = [&](const char* what, vk::Result result) {
		LOGF("HostImport: chunk %zu (%llu MB at 0x%llx) %s failed: %s\n", index,
		     static_cast<unsigned long long>(size >> 20u), static_cast<unsigned long long>(offset),
		     what, vk::to_string(result).c_str());
		if (buffer != nullptr) {
			m_graphics.device.destroyBuffer(buffer, nullptr);
		}
		if (memory != nullptr) {
			m_graphics.device.freeMemory(memory, nullptr);
		}
		std::lock_guard lock(m_mutex);
		m_chunks[index].state = State::Failed;
	};

	vk::MemoryHostPointerPropertiesEXT host_properties {};
	host_properties.sType = vk::StructureType::eMemoryHostPointerPropertiesEXT;
	auto result           = m_graphics.device.getMemoryHostPointerPropertiesEXT(
        vk::ExternalMemoryHandleTypeFlagBits::eHostAllocationEXT, host, &host_properties);
	if (result != vk::Result::eSuccess) {
		return fail("vkGetMemoryHostPointerPropertiesEXT", result);
	}

	vk::ExternalMemoryBufferCreateInfo external {};
	external.sType       = vk::StructureType::eExternalMemoryBufferCreateInfo;
	external.handleTypes = vk::ExternalMemoryHandleTypeFlagBits::eHostAllocationEXT;
	vk::BufferCreateInfo buffer_info {};
	buffer_info.sType = vk::StructureType::eBufferCreateInfo;
	buffer_info.pNext = &external;
	buffer_info.size  = size;
	buffer_info.usage = vk::BufferUsageFlagBits::eTransferSrc | vk::BufferUsageFlagBits::eStorageBuffer;
	result = m_graphics.device.createBuffer(&buffer_info, nullptr, &buffer);
	if (result != vk::Result::eSuccess) {
		return fail("vkCreateBuffer", result);
	}

	vk::MemoryRequirements requirements {};
	m_graphics.device.getBufferMemoryRequirements(buffer, &requirements);
	const auto& memory_properties = m_graphics.physical_device_memory_properties;
	const auto  allowed           = requirements.memoryTypeBits & host_properties.memoryTypeBits;
	uint32_t    type              = UINT32_MAX;
	for (uint32_t i = 0; i < memory_properties.memoryTypeCount; i++) {
		if ((allowed & (1u << i)) == 0u) {
			continue;
		}
		const auto flags = memory_properties.memoryTypes[i].propertyFlags;
		if (!(flags & vk::MemoryPropertyFlagBits::eHostVisible)) {
			continue;
		}
		// Prefer a cached type: the CPU keeps writing these pages (guest memory). GPU reads are
		// equally fast from either (measured: 48 GB/s DMA, 43 GB/s detile).
		if (type == UINT32_MAX || (flags & vk::MemoryPropertyFlagBits::eHostCached)) {
			type = i;
			if (flags & vk::MemoryPropertyFlagBits::eHostCached) {
				break;
			}
		}
	}
	if (type == UINT32_MAX) {
		return fail("memory type selection", vk::Result::eErrorFeatureNotPresent);
	}

	vk::ImportMemoryHostPointerInfoEXT import {};
	import.sType        = vk::StructureType::eImportMemoryHostPointerInfoEXT;
	import.handleType   = vk::ExternalMemoryHandleTypeFlagBits::eHostAllocationEXT;
	import.pHostPointer = host;
	vk::MemoryAllocateInfo allocate {};
	allocate.sType           = vk::StructureType::eMemoryAllocateInfo;
	allocate.pNext           = &import;
	allocate.allocationSize  = size;
	allocate.memoryTypeIndex = type;
	result = m_graphics.device.allocateMemory(&allocate, nullptr, &memory);
	if (result != vk::Result::eSuccess) {
		return fail("vkAllocateMemory(import)", result);
	}
	result = m_graphics.device.bindBufferMemory(buffer, memory, 0);
	if (result != vk::Result::eSuccess) {
		return fail("vkBindBufferMemory", result);
	}
	{
		std::lock_guard lock(m_mutex);
		m_chunks[index].buffer = buffer;
		m_chunks[index].memory = memory;
		m_chunks[index].state  = State::Ready;
	}
	const auto us = (Common::FrameStats::NowNs() - t1) / 1000u;
	LOGF("HostImport: chunk %zu imported (%llu MB at backing 0x%llx, memory type %u) in %llu us "
	     "(pages touched in %llu us)\n",
	     index, static_cast<unsigned long long>(size >> 20u),
	     static_cast<unsigned long long>(offset), type, static_cast<unsigned long long>(us),
	     static_cast<unsigned long long>((t1 - t0) / 1000u));
}

bool HostImport::Resolve(uint64_t backing_offset, uint64_t size, Region* region) {
	if (!m_available || region == nullptr || size == 0 || backing_offset >= m_size ||
	    size > m_size - backing_offset) {
		return false;
	}
	const auto index = static_cast<size_t>(backing_offset / m_chunk_size);
	{
		std::lock_guard lock(m_mutex);
		auto&           chunk = m_chunks[index];
		switch (chunk.state) {
			case State::Ready: break;
			case State::Failed:
			case State::Importing: return false;
			case State::Empty:
				chunk.state = State::Importing;
				m_in_flight.fetch_add(1);
				if (m_sync) {
					break;
				}
				std::thread([this, index] {
					ImportChunk(index);
					m_in_flight.fetch_sub(1);
				}).detach();
				return false;
		}
		if (chunk.state == State::Ready) {
			const auto chunk_start = index * m_chunk_size;
			const auto in_chunk    = backing_offset - chunk_start;
			const auto chunk_size  = std::min(m_chunk_size, m_size - chunk_start);
			region->buffer         = chunk.buffer;
			region->offset         = in_chunk;
			region->size           = std::min(size, chunk_size - in_chunk);
			return true;
		}
	}
	// Synchronous import (KYTY_HOST_IMPORT_SYNC=1) on the caller.
	ImportChunk(index);
	m_in_flight.fetch_sub(1);
	return Resolve(backing_offset, size, region);
}

} // namespace Libs::Graphics
