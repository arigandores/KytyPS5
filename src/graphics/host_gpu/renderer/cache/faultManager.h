#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_FAULTMANAGER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_FAULTMANAGER_H_

#include "common/abi.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"

#include <array>
#include <cstdint>
#include <functional>

namespace Libs::Graphics {

class BufferCache;

// Track F, F29 (KYTY_FIX_F29, ROADMAP s122 item 698): one area of the fault download buffer is a counter word
// (faults[0], low 32 bits) and the records faults[1..1023] written by fault_buffer_process.comp. With 1 024 or more
// set bits in one pass the counter is 1 023 + T > 1 023 while only 1 023 records exist; reading faults[1..counter]
// then goes past the area (and past the whole buffer for the last area). ParseFaultArea is the one parse of an area:
// FaultManager::ProcessFaultBuffer and the stand tests/F29FaultStand.cpp call this function, not a copy.
//   raw   - the counter word as read;
//   count - the records visited: clamp ? min(raw, 1 023) : raw (clamp = false is the path before the fix).
// visit(index, value) is called for index = 1 ... count in order. With clamp and raw > 1 023 the function writes the
// line "FixF29: overflow pass= area= count= read= total=" (not more than 32 lines per process; total - the passes
// with an overflow since the start of the process, counted only with clamp). pass carries the fields of that line.
struct FaultAreaParse {
	uint32_t raw   = 0;
	uint32_t count = 0;
};
struct FaultAreaPass {
	uint64_t pass = 0;
	uint32_t area = 0;
};
using FaultAreaVisitor = std::function<void(uint32_t index, uint64_t value)>;

// KYTY_FIX_F29 (default 1 since FS14a, HPP-812, ROADMAP s122 item 712(g)(1)): the value is read once per process
// (unset or "" - on; 0/false/off/no - off; any other value as EnvValueOn).
[[nodiscard]] bool           FixF29Enabled();
FaultAreaParse ParseFaultArea(const uint64_t* area, bool clamp, const FaultAreaVisitor& visit,
                              const FaultAreaPass& pass = {});

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

private:
	GraphicContext&                            m_graphics;
	CommandScheduler&                          m_scheduler;
	BufferCache&                               m_buffer_cache;
	Buffer                                     m_fault_buffer;
	Buffer                                     m_download_buffer;
	std::array<uint64_t, MaxPendingFaults>      m_fault_areas {};
	Buffer                                     m_trip_download;
	std::array<uint32_t, 16>                   m_trip_last {};
	uint32_t                                   m_trip_lines = 0;
	uint32_t                                   m_current_area = 0;
	uint64_t                                   m_fix_f29_pass = 0; // KYTY_FIX_F29: passes, grows only at 1
	vk::DescriptorSetLayout                    m_fault_process_desc_layout = nullptr;
	vk::Pipeline                               m_fault_process_pipeline = nullptr;
	vk::PipelineLayout                         m_fault_process_pipeline_layout = nullptr;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_CACHE_FAULTMANAGER_H_
