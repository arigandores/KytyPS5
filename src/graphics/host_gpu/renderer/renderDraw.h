#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERDRAW_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERDRAW_H_

#include <cstdint>
#include <utility>
#include <span>
#include <vector>

namespace Libs::Graphics {

struct ShaderVertexInputInfo;

[[nodiscard]] std::pair<int32_t, uint32_t>
ResolveDrawOffsets(uint32_t index_offset, const ShaderVertexInputInfo& vs_input_info);

struct MeshIndexRange {
	uint32_t first = 0;
	uint32_t count = 0;
};

// Ranges between fixed-index restart markers, in original index-buffer order.
[[nodiscard]] std::vector<MeshIndexRange>
SplitMeshRestartIndices(std::span<const uint8_t> indices, uint32_t element_size);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERDRAW_H_
