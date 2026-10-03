#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_FAULTMANAGER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_FAULTMANAGER_H_

#include "common/abi.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"

#include <array>
#include <atomic>
#include <cstdint>

namespace Libs::Graphics {

class BufferCache;

class FaultManager {
	static constexpr size_t MaxPendingFaults = 8;

public:
	FaultManager(GraphicContext& graphics, CommandScheduler& scheduler, BufferCache& buffer_cache);
	~FaultManager();
	KYTY_CLASS_NO_COPY(FaultManager);

	[[nodiscard]] Buffer* GetFaultBuffer() noexcept { return &m_fault_buffer; }
	void                  ProcessFaultBuffer();
	// KYTY_BVH_LOOP_CAP: zero the counter tail after the fault bitmap (needs a command buffer,
	// so the buffer cache calls it at its first registration, like the null page).
	void ClearLoopTripTail();
	// Track F, F11d (ROADMAP p.376(v)): the counter tail after the fault bitmap - the loop-cap words and,
	// at KYTY_DIAG_BVHNODES=1, the diagnostic words; ClearLoopTripTail zeroes all of it.
	[[nodiscard]] static uint64_t TailOffset();
	[[nodiscard]] static uint64_t TailBytes();

private:
	void ProcessDiagWords(uint64_t download_offset);

	GraphicContext&                            m_graphics;
	CommandScheduler&                          m_scheduler;
	BufferCache&                               m_buffer_cache;
	Buffer                                     m_fault_buffer;
	Buffer                                     m_download_buffer;
	std::array<uint64_t, MaxPendingFaults>      m_fault_areas {};
	Buffer                                     m_trip_download;
	std::array<uint32_t, 16>                   m_trip_last {};
	uint32_t                                   m_trip_lines = 0;
	// Track F, F11d: KYTY_DIAG_BVHNODES host state - read and written by the readbacks (deferred operations
	// of ProcessFaultBuffer), except m_tail_cleared: set by ClearLoopTripTail (buffer cache, first
	// registration), read when a readback is recorded; the diagnostic words are diffed only after it.
	std::array<uint32_t, 64>                   m_diag_last {};
	std::array<uint64_t, 64>                   m_diag_total {};
	uint64_t                                   m_diag_max_step    = 0;
	uint64_t                                   m_diag_last_log_ms = 0;
	uint32_t                                   m_diag_lines       = 0;
	bool                                       m_diag_pending     = false;
	std::atomic<bool>                          m_tail_cleared {false};
	uint32_t                                   m_current_area = 0;
	vk::DescriptorSetLayout                    m_fault_process_desc_layout = nullptr;
	vk::Pipeline                               m_fault_process_pipeline = nullptr;
	vk::PipelineLayout                         m_fault_process_pipeline_layout = nullptr;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_FAULTMANAGER_H_
