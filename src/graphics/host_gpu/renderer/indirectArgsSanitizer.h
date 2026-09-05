#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_INDIRECTARGSSANITIZER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_INDIRECTARGSSANITIZER_H_

#include "common/abi.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <cstdint>
#include <utility>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
class CommandScheduler;

// Validates dispatch-indirect group counts on the GPU before vkCmdDispatchIndirect consumes them.
// The producing compute shader may never have written the arguments (for example a BDA store to a
// page that was not cached yet), leaving fill patterns like 0xDEADBEEF in memory; dispatching such
// counts hangs the host GPU. A one-thread compute pass copies the triple into a private ring
// buffer and zeroes it when any component exceeds the device limit.
class IndirectArgsSanitizer {
public:
	IndirectArgsSanitizer(GraphicContext& graphics, CommandScheduler& scheduler);
	~IndirectArgsSanitizer();
	KYTY_CLASS_NO_COPY(IndirectArgsSanitizer);

	// Records the sanitizing pass into `command`. `source` must hold the 12-byte argument triple at
	// `source_offset`. Returns the buffer and offset to pass to vkCmdDispatchIndirect. Must be
	// recorded before the consuming pipeline's descriptors are pushed: it binds its own layout.
	[[nodiscard]] std::pair<vk::Buffer, uint64_t> Sanitize(vk::CommandBuffer command,
	                                                        const Buffer&     source,
	                                                        uint64_t          source_offset);

private:
	static constexpr uint32_t SlotSize  = 16;
	static constexpr uint32_t SlotCount = 4096;

	GraphicContext&         m_graphics;
	CommandScheduler&       m_scheduler;
	Buffer                  m_args_buffer;
	std::vector<uint64_t>   m_slot_ticks;
	uint32_t                m_next_slot       = 0;
	vk::DescriptorSetLayout m_desc_layout     = nullptr;
	vk::PipelineLayout      m_pipeline_layout = nullptr;
	vk::Pipeline            m_pipeline        = nullptr;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_INDIRECTARGSSANITIZER_H_
