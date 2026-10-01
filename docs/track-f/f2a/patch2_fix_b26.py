# F2a (HPP-307) patch 2: B26b - S_BREV_B64 (SOP1 0x0c) and V_CMP_LE_U64 (VOPC 0xe3) under KYTY_FIX_B26
# (ROADMAP p.237(g)(3); plan docs/track-f/f1-b26.md section 5 with RC5/RC6 of docs/track-f/f1-review.md).
import sys
sys.path.insert(0, 'C:/kyty/f287/f2a')
import patchlib

S = 'C:/kyty/KytyPS5/src/graphics/shader/recompiler/'
H = S + 'frontend/decode/ShaderDecoder.h'
DC = S + 'frontend/decode/ShaderDecoder.cpp'
SA = S + 'frontend/decode/ScalarAluOps.cpp'
VA = S + 'frontend/decode/VectorAluOps.cpp'
TS = S + 'frontend/translate/Scalar.cpp'
TV = S + 'frontend/translate/Vector.cpp'
STC = 'C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'

patchlib.apply(H, [
    (['\tEXP,', '\tCOUNT'],
     ['\tEXP,',
      '\t// Track F, F2a (ROADMAP p.237): decoded only while KYTY_FIX_B26 is on (GateFixB26).',
      '\tS_BREV_B64,',
      '\tV_CMP_LE_U64,',
      '\tCOUNT'], 'replace'),
    (['void SetUnsupported(Instruction& inst, Family family, uint32_t opcode_id, const char* reason);'],
     ['// Track F, F2a (HPP-307, ROADMAP p.237(g)(3)): KYTY_FIX_B26, default ON (unset or empty = on; 0, false,',
      '// off, no = off, as Common::EnvValueOn). Off: SOP1 0x0c (S_BREV_B64) and VOPC 0xe3 (V_CMP_LE_U64, also',
      '// its VOP3 form) decode as UNSUPPORTED exactly as before the fix. Read once per process; the',
      '// translation cache keys the value in its signature and directory (shaderTranslationCache.cpp).',
      'bool   FixB26Enabled();',
      'Opcode GateFixB26(Opcode opcode);'], 'after'),
])

patchlib.apply(DC, [
    (['#include "common/assert.h"'], ['#include "common/envFlag.h"'], 'after'),
    (['#include <bit>'], ['#include <cstdlib>'], 'after'),
    (['Family GetInstructionFamily(uint32_t word) {'],
     ['bool FixB26Enabled() {',
      '\tstatic const bool enabled = [] {',
      '\t\tconst char* value = std::getenv("KYTY_FIX_B26");',
      "\t\treturn value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
      '\t}();',
      '\treturn enabled;',
      '}',
      '',
      'Opcode GateFixB26(Opcode opcode) {',
      '\tif ((opcode == Opcode::S_BREV_B64 || opcode == Opcode::V_CMP_LE_U64) && !FixB26Enabled()) {',
      '\t\treturn Opcode::UNSUPPORTED;',
      '\t}',
      '\treturn opcode;',
      '}',
      ''], 'before'),
    (['\t\tcase Opcode::S_BREV_B32:'],
     ['\t\tcase Opcode::S_BREV_B64:'], 'after'),
])

patchlib.apply(SA, [
    (['    {0x0bu, Opcode::S_BREV_B32},'],
     ['    {0x0cu, Opcode::S_BREV_B64},'], 'after'),
    (['\tinst.opcode    = Detail::LookupOpcode(SOP1_OPS, opcode);'],
     ['\tinst.opcode    = GateFixB26(Detail::LookupOpcode(SOP1_OPS, opcode));'], 'replace'),
])

patchlib.apply(VA, [
    (['    {0xe2u, Opcode::V_CMP_EQ_U64, false},  {0xe4u, Opcode::V_CMP_GT_U64, false},'],
     ['    {0xe2u, Opcode::V_CMP_EQ_U64, false},  {0xe3u, Opcode::V_CMP_LE_U64, false},',
      '    {0xe4u, Opcode::V_CMP_GT_U64, false},'], 'replace'),
    (['\t\treturn Detail::LookupOpcode(VOPC_OPS, opcode);'],
     ['\t\treturn GateFixB26(Detail::LookupOpcode(VOPC_OPS, opcode));'], 'replace'),
    (['\tinst.opcode    = Detail::LookupOpcode(VOPC_OPS, opcode);'],
     ['\tinst.opcode    = GateFixB26(Detail::LookupOpcode(VOPC_OPS, opcode));'], 'replace'),
])

patchlib.apply(TS, [
    (['\t\tcase O::S_BREV_B32:',
      '\t\t\treturn SimpleInteger(inst, IR::ValueOpcode::BitReverse32, IR::Type::U32, false, false,',
      '\t\t\t                     false);'],
     ['\t\tcase O::S_BREV_B64: {',
      '\t\t\t// Track F, F2a: D.u64[63:0] = S0.u64[0:63] (ISA RDNA2 12.3). ReadU32Pair zero-extends a',
      '\t\t\t// literal (6.2.1, unsigned 64-bit) and sign-extends a negative inline constant; SCC is kept.',
      '\t\t\tconst auto source = ReadU32Pair(inst.src0);',
      '\t\t\tWriteU32Pair(inst.dst, {IR::U32(ir.Emit(IR::ValueOpcode::BitReverse32, {source[1]})),',
      '\t\t\t                        IR::U32(ir.Emit(IR::ValueOpcode::BitReverse32, {source[0]}))});',
      '\t\t\treturn true;',
      '\t\t}'], 'after'),
])

patchlib.apply(TV, [
    (['\t\tcase O::V_CMP_GT_U64:',
      '\t\t\tEmitIntegerCompare(inst, IR::ValueOpcode::UGreaterThan64, IR::Type::U64, false, false);',
      '\t\t\treturn true;'],
     ['\t\tcase O::V_CMP_LE_U64: {',
      '\t\t\t// Track F, F2a: lane bit = (S0.u64 <= S1.u64) (ISA RDNA2 12.9) as NOT (S0 > S1). The negation is',
      '\t\t\t// per lane and BEFORE EmitCompareResult ANDs with EXEC, so a lane off in EXEC writes 0.',
      '\t\t\tconst auto lhs = ReadOperand(inst.src0, IR::Type::U64);',
      '\t\t\tconst auto rhs = ReadOperand(inst.src1, IR::Type::U64);',
      '\t\t\tEmitCompareResult(',
      '\t\t\t    inst, ir.LogicalNot(IR::U1(ir.Emit(IR::ValueOpcode::UGreaterThan64, {lhs, rhs}))), false,',
      '\t\t\t    false);',
      '\t\t\treturn true;',
      '\t\t}'], 'after'),
])

patchlib.apply(STC, [
    (['#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"'],
     ['#include "graphics/shader/recompiler/frontend/decode/ShaderDecoder.h"'], 'after'),
    (['\t// Session 103: a non-default translator variant (KYTY_BVH_LOOP_CAP override, KYTY_BDA_LEAN)',
      '\t// gets its own signature token AND its own directory - file names do not carry the',
      '\t// signature, so a variant run would otherwise overwrite the default cache and pipelines.bin.',
      '\tconst std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +',
      '\t                            (ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? ":bdalean" : "");'],
     ['\t// Session 103: a non-default translator variant (KYTY_BVH_LOOP_CAP override, KYTY_BDA_LEAN)',
      '\t// gets its own signature token AND its own directory - file names do not carry the',
      '\t// signature, so a variant run would otherwise overwrite the default cache and pipelines.bin.',
      '\t// Track F, F2a (RC5 of the F1b review): KYTY_FIX_B26=1 (the default) adds ":fixb26", so the',
      '\t// translations of =1 and =0 never share a signature or a directory.',
      '\tconst std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +',
      '\t                            (ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? ":bdalean" : "") +',
      '\t                            (ShaderRecompiler::Decoder::FixB26Enabled() ? ":fixb26" : "");'], 'replace'),
])
