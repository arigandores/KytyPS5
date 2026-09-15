#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_SHADERCOMPILER_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_SHADERCOMPILER_H_

#include "graphics/shader/shader.h"

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <span>
#include <vector>

namespace Libs::Graphics {

namespace HW {
class Context;
class UserConfig;
} // namespace HW

// Session 59, B5: the user SGPRs of a stage, inline. At most 32 user SGPRs plus the 8-word prefix
// the NGG path inserts; a stage declaring more than the array holds is a broken register block,
// not a case to serve.
struct ShaderUserSgprs {
	static constexpr uint32_t Capacity = 48;

	ShaderUserSgprs() = default;
	explicit ShaderUserSgprs(std::span<const uint32_t> values) { Assign(values); }

	// A block longer than the array is clamped: the register block a stage declares more than
	// 32 user SGPRs for is already over-read by the span it comes from, and the draw and
	// lookahead paths reject such counts (HW::UserSgprInfo::SGPRS_MAX).
	void Assign(std::span<const uint32_t> values) {
		count = static_cast<uint32_t>(std::min<size_t>(values.size(), Capacity));
		std::copy(values.begin(), values.begin() + count, words.begin());
	}
	// The NGG path: `n` zero words in front of the current ones.
	void PrependZeros(uint32_t n) {
		n = std::min(n, Capacity - count);
		std::copy_backward(words.begin(), words.begin() + count, words.begin() + count + n);
		std::fill(words.begin(), words.begin() + n, 0u);
		count += n;
	}

	[[nodiscard]] size_t          size() const noexcept { return count; }
	[[nodiscard]] bool            empty() const noexcept { return count == 0; }
	[[nodiscard]] const uint32_t* data() const noexcept { return words.data(); }
	[[nodiscard]] uint32_t*       data() noexcept { return words.data(); }
	[[nodiscard]] const uint32_t* begin() const noexcept { return words.data(); }
	[[nodiscard]] const uint32_t* end() const noexcept { return words.data() + count; }
	[[nodiscard]] uint32_t&       operator[](size_t index) noexcept { return words[index]; }
	[[nodiscard]] uint32_t        operator[](size_t index) const noexcept { return words[index]; }
	operator std::span<const uint32_t>() const noexcept { return {words.data(), count}; } // NOLINT

	std::array<uint32_t, Capacity> words {};
	uint32_t                       count = 0;
};

struct ShaderParams {
	std::span<const uint32_t> code;
	ShaderUserSgprs            user_data;
	uint64_t                  hash = 0;
	std::span<const uint32_t> back_code;

	[[nodiscard]] uint64_t Base() const {
		return reinterpret_cast<uint64_t>(code.data());
	}
};

void BuildStageStaticKey(const ShaderVertexInputInfo& input_info, std::vector<uint32_t>& key);
void BuildStageStaticKey(const ShaderPixelInputInfo& input_info, std::vector<uint32_t>& key);
void BuildStageStaticKey(const ShaderComputeInputInfo& input_info, std::vector<uint32_t>& key);

ShaderParams PrepareProgram(const HW::VertexShaderInfo& regs, const HW::Context& context,
                            const HW::UserConfig& user_config, ShaderVertexInputInfo& input_info);
std::array<ShaderParams, 3>
PrepareTessellationPrograms(const HW::VertexShaderInfo& regs, const HW::Context& context,
                            std::array<ShaderVertexInputInfo, 3>& input_info);
ShaderParams PrepareProgram(
    const HW::PixelShaderInfo& regs, const HW::ShaderRegisters& sh,
    std::span<const Prospero::ColorComponentMapping, 8> target_export_mapping,
    ShaderPixelInputInfo&                               input_info);
ShaderParams PrepareProgram(const HW::ComputeShaderInfo& regs, const HW::ShaderRegisters& sh,
                            ShaderComputeInputInfo& input_info);

} // namespace Libs::Graphics

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_SHADERCOMPILER_H_ */
