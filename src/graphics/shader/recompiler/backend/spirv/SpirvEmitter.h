#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_

#include "common/common.h"
#include "common/stringUtils.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"

#include <string>
#include <vector>

namespace Libs::Graphics::ShaderRecompiler::Spirv {

namespace Emitter {
// Device robustBufferAccess2: storage-buffer loads emit no bounds branch (KYTY_ROBUST_LOADS=0/1
// overrides). Part of the translation cache signature.
void SetRobustBufferLoads(bool device_supported);
bool RobustBufferLoads();
// fp32 denormals (the game runs with FLOAT_MODE 0xc0: flushed). shaderDenormFlushToZeroFloat32 ->
// the module declares DenormFlushToZero; else !shaderDenormPreserveFloat32 (NVIDIA: neither is
// controllable, the hardware flushes) -> assumed without a declaration. In both cases the emitter
// drops its manual flush in front of RCP/RSQ/SQRT/EXP2/LOG2. KYTY_FTZ=0 emulate, 1 assume,
// 2 declare. Part of the translation cache signature.
void SetDenormFlushToZero(bool device_can_flush, bool device_can_preserve);
bool DenormFlushToZero();         // manual flush dropped
bool DenormFlushToZeroDeclared(); // execution mode emitted
// Session 103, KYTY_BVH_LOOP_CAP: a step budget per invocation for the programs of
// KYTY_BVH_LOOP_CAP_SET (hex hashes, comma-separated; default the BVH traversal
// 380bb9d636390bae that hung Sky Garden entries). Every loop-header execution spends one step;
// an invocation that exhausts the budget counts a trip and returns through the normal return
// path. Default 65536, 0 = off. Read once per process. The token is empty at the default and
// otherwise part of the translation cache signature (and of its directory).
uint32_t    BvhLoopCap();
int         BvhLoopCapSlot(uint64_t shader_hash); // index in the set, -1 = not capped
std::string BvhLoopCapSignatureToken();
// The trip counters live right after the fault bitmap (CACHING_NUMPAGES / 32 words), which the
// fault-buffer parser never touches: [0] trips, [1] normal returns that spent more than
// 1/16 of the budget, [2] the largest budget seen by [0]/[1], [8 + slot] trips per set entry.
inline constexpr uint32_t LoopTripWordBase = 1u << 21;
inline constexpr uint32_t LoopTripWords    = 16;
inline constexpr uint32_t LoopTripSlots    = 8;
// Session 103, KYTY_BDA_LEAN (M5', measurement only, default off): the BDA path as design G would
// build it - no fault-buffer store in pixel shaders, one page-table read per lookup (the null-page
// base read once per invocation), read-only PSB views (NonWritable, Restrict when the program
// writes no memory), and uvec4 loads for the 16-byte windows of a scalar load group behind a
// run-time alignment test. Needs the null-page mode. Part of the translation cache signature.
bool BdaLeanEnabled();
} // namespace Emitter

std::vector<uint32_t> EmitProgram(const IR::Program& program,
                                  ShaderStageInputInfo input_info);

} // namespace Libs::Graphics::ShaderRecompiler::Spirv

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_ */
