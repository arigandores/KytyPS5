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
// Device shaderDenormFlushToZeroFloat32: the module declares DenormFlushToZero for fp32 (the
// game runs with FLOAT_MODE 0xc0) and the emitter drops its manual denormal flush in front of
// RCP/RSQ/SQRT/EXP2/LOG2 (KYTY_FTZ=0/1 overrides). Part of the translation cache signature.
void SetDenormFlushToZero(bool device_supported);
bool DenormFlushToZero();
} // namespace Emitter

void AnalyzeProgramRequirements(IR::Program& program);

std::vector<uint32_t> EmitProgram(const IR::Program& program,
                                  ShaderStageInputInfo input_info);

} // namespace Libs::Graphics::ShaderRecompiler::Spirv

#endif /* EMULATOR_INCLUDE_EMULATOR_GRAPHICS_SHADER_RECOMPILER_SPIRVEMITTER_H_ */
