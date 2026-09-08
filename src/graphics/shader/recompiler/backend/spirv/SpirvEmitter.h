#ifndef EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_
#define EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_

#include "common/common.h"
#include "common/stringUtils.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"

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
} // namespace Emitter

void AnalyzeProgramRequirements(IR::Program& program);

std::vector<uint32_t> EmitProgram(const IR::Program& program,
                                  ShaderStageInputInfo input_info);

} // namespace Libs::Graphics::ShaderRecompiler::Spirv

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_ */
