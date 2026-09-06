#pragma once

#include <cstdint>

namespace Libs::Graphics::ShaderRecompiler::IR {

enum class ScalarReg : uint16_t {};
enum class VectorReg : uint16_t {};

// s0..s105 plus two slots for the VCC halves: wave32 programs use vcc_hi (107) as an ordinary
// SGPR, so the translator maps it onto that slot.
constexpr uint32_t NumScalarRegs = 108;
constexpr uint32_t VccHiScalarReg = 107;
// Wave32: slot 106 only carries the mask tag of vcc_lo (its value lives in the VCC state).
constexpr uint32_t VccLoScalarReg = 106;
constexpr uint32_t NumVectorRegs = 256;

constexpr uint32_t RegIndex(ScalarReg reg) {
	return static_cast<uint32_t>(reg);
}

constexpr uint32_t RegIndex(VectorReg reg) {
	return static_cast<uint32_t>(reg);
}

} // namespace Libs::Graphics::ShaderRecompiler::IR
