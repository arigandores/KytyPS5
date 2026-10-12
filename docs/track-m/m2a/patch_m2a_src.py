"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)): translator themes of upstream wave 1 under KYTY_M_<theme> knobs
(default 0; at 0 the translation is byte for byte that of FS15). Applied to <root> (main C:/kyty/KytyPS5 and the
worktree C:/kyty/m657/m2/wt - the same patch). Anchors are whole lines; each must occur exactly once; CRLF files are
handled (\\r stripped before the search and restored after). Writes LF/CRLF as found, bytes.
Usage: python patch_m2a_src.py <root>"""
import os
import sys

ROOT = sys.argv[1]
SR = 'src/graphics/shader/recompiler/'
edits = []


def edit(path, anchor, new, mode='replace'):
    edits.append((path, anchor, new, mode))


# ---------------------------------------------------------------- knobs
edit(SR + 'frontend/decode/ShaderDecoder.h',
     'bool   FixF10Enabled();\n',
     'bool   FixF10Enabled();\n'
     '// Track M, M2a (HPP-838, ROADMAP s122 item 756(v)(1)): translator themes of upstream wave 1, one knob each -\n'
     '// KYTY_M_T234, KYTY_M_T233, KYTY_M_T256, KYTY_M_T306, KYTY_M_T032, KYTY_M_T203; default OFF (unset, empty, 0, false,\n'
     '// off, no = off; any other value as Common::EnvValueOn). Off: the translation is byte for byte that of FS15. Read once\n'
     '// per process; the translation cache keys the set of enabled themes with one token (MWave1SignatureToken) in its\n'
     '// signature and directory (shaderTranslationCache.cpp).\n'
     'enum class MTheme : uint32_t { T234 = 0, T233 = 1, T256 = 2, T306 = 3, T032 = 4, T203 = 5, Count = 6 };\n'
     'bool        MThemeEnabled(MTheme theme);\n'
     'uint32_t    MThemeMask(); // bit i = MTheme value i\n'
     'const char* MThemeKnob(MTheme theme);\n'
     '// "" when every theme is off, else ":mw1_<two hex digits of MThemeMask()>".\n'
     'std::string MWave1SignatureToken();\n',
     'replace')

edit(SR + 'frontend/decode/ShaderDecoder.cpp',
     '\t\tconst char* value = std::getenv("KYTY_FIX_F10");\n'
     '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);\n'
     '\t}();\n'
     '\treturn enabled;\n'
     '}\n',
     '\t\tconst char* value = std::getenv("KYTY_FIX_F10");\n'
     '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);\n'
     '\t}();\n'
     '\treturn enabled;\n'
     '}\n'
     '\n'
     'const char* MThemeKnob(MTheme theme) {\n'
     '\tstatic constexpr const char* knobs[] = {"KYTY_M_T234", "KYTY_M_T233", "KYTY_M_T256",\n'
     '\t                                        "KYTY_M_T306", "KYTY_M_T032", "KYTY_M_T203"};\n'
     '\tconst auto index = static_cast<uint32_t>(theme);\n'
     '\treturn index < static_cast<uint32_t>(MTheme::Count) ? knobs[index] : "";\n'
     '}\n'
     '\n'
     'uint32_t MThemeMask() {\n'
     '\t// Track M, M2a (HPP-838): default OFF - only a value Common::EnvValueOn accepts turns a theme on.\n'
     '\tstatic const uint32_t mask = [] {\n'
     '\t\tuint32_t result = 0;\n'
     '\t\tfor (uint32_t index = 0; index < static_cast<uint32_t>(MTheme::Count); index++) {\n'
     '\t\t\tif (Common::EnvValueOn(std::getenv(MThemeKnob(static_cast<MTheme>(index))))) {\n'
     '\t\t\t\tresult |= 1u << index;\n'
     '\t\t\t}\n'
     '\t\t}\n'
     '\t\treturn result;\n'
     '\t}();\n'
     '\treturn mask;\n'
     '}\n'
     '\n'
     'bool MThemeEnabled(MTheme theme) {\n'
     '\treturn (MThemeMask() >> static_cast<uint32_t>(theme) & 1u) != 0u;\n'
     '}\n'
     '\n'
     'std::string MWave1SignatureToken() {\n'
     '\tconst auto mask = MThemeMask();\n'
     '\tif (mask == 0u) {\n'
     '\t\treturn {};\n'
     '\t}\n'
     '\tstatic constexpr char digits[] = "0123456789abcdef";\n'
     '\treturn std::string(":mw1_") + digits[(mask >> 4u) & 0xfu] + digits[mask & 0xfu];\n'
     '}\n')

edit('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
     '\t                            (ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "");\n',
     '\t                            (ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "") +\n'
     '\t                            ShaderRecompiler::Decoder::MWave1SignatureToken();\n')

edit('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
     '\t// Track F, F14e (ROADMAP s122 item 409(v)): KYTY_FIX_F19=1 (the default since FS8a, p.471(g)(1)) adds ":fixf19" after\n'
     '\t// ":fixf10", last.\n',
     '\t// Track F, F14e (ROADMAP s122 item 409(v)): KYTY_FIX_F19=1 (the default since FS8a, p.471(g)(1)) adds ":fixf19" after\n'
     '\t// ":fixf10", last.\n'
     '\t// Track M, M2a (HPP-838, ROADMAP s122 item 756(v)(1)): any KYTY_M_<theme>=1 of wave 1 adds ":mw1_<mask>" after\n'
     '\t// ":fixf19", last - one token for the whole wave; every theme off adds nothing.\n'
     '\tLOGF("MWave1: mask=0x%02x T234=%d T233=%d T256=%d T306=%d T032=%d T203=%d\\n",\n'
     '\t     ShaderRecompiler::Decoder::MThemeMask(),\n'
     '\t     ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T234) ? 1 : 0,\n'
     '\t     ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T233) ? 1 : 0,\n'
     '\t     ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T256) ? 1 : 0,\n'
     '\t     ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T306) ? 1 : 0,\n'
     '\t     ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T032) ? 1 : 0,\n'
     '\t     ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T203) ? 1 : 0);\n')

# ---------------------------------------------------------------- T203
edit(SR + 'frontend/translate/Integer.cpp',
     'bool Translator::V_ALIGNBYTE_B32(const Decoder::Instruction& inst) {\n'
     '\tconst auto hi           = ReadU32(inst.src0);\n'
     '\tconst auto lo           = ReadU32(inst.src1);\n',
     'bool Translator::V_ALIGNBYTE_B32(const Decoder::Instruction& inst) {\n'
     '\tconst auto hi           = ReadU32(inst.src0);\n'
     '\tconst auto lo           = ReadU32(inst.src1);\n'
     '\tif (Decoder::MThemeEnabled(Decoder::MTheme::T203)) {\n'
     '\t\t// Track M, M2a (T203, upstream f18679e0; KYTY_M_T203): RDNA2 V_ALIGNBYTE_B32 is\n'
     '\t\t// D = ({S0, S1} >> (8 * S2[1:0]))[31:0] - only the two low bits of S2 select the byte.\n'
     '\t\tconst auto shift   = ir.ShiftLeftLogical(ir.BitwiseAnd(ReadU32(inst.src2), IR::U32(IR::Value(3u))),\n'
     '\t\t                                         IR::U32(IR::Value(3u)));\n'
     '\t\tconst auto lo_part = ir.ShiftRightLogical(lo, shift);\n'
     '\t\tconst auto inverse =\n'
     '\t\t    ir.BitwiseAnd(ir.ISub(IR::U32(IR::Value(32u)), shift), IR::U32(IR::Value(31u)));\n'
     '\t\tconst auto hi_part_raw = ir.ShiftLeftLogical(hi, inverse);\n'
     '\t\tconst auto hi_part     = ir.Select(ir.INotEqual(shift, IR::U32(IR::Value(0u))), hi_part_raw,\n'
     '\t\t                                   IR::U32(IR::Value(0u)));\n'
     '\t\tWriteOperand(DestinationOperand(inst), ir.BitwiseOr(lo_part, hi_part));\n'
     '\t\treturn true;\n'
     '\t}\n')

# ---------------------------------------------------------------- T234
edit(SR + 'frontend/decode/MemoryOps.cpp',
     '\t\tcase Opcode::DS_MIN_F32:\n'
     '\t\tcase Opcode::DS_MAX_F32: return 3u;\n',
     '\t\tcase Opcode::DS_MIN_F32:\n'
     '\t\t// Track M, M2a (T234, upstream e85279ea; KYTY_M_T234): DS_MIN/MAX_F32 read the address and DATA0 only.\n'
     '\t\tcase Opcode::DS_MAX_F32: return MThemeEnabled(MTheme::T234) ? 2u : 3u;\n')

edit(SR + 'frontend/translate/Memory.cpp',
     'bool Translator::DS_MINMAX_F32(const Decoder::Instruction& inst, IR::ValueOpcode opcode) {\n'
     '\tconst auto memory = MemoryInfoFromDecoded(inst);\n',
     'bool Translator::DS_MINMAX_F32(const Decoder::Instruction& inst, IR::ValueOpcode opcode) {\n'
     '\tconst auto memory = MemoryInfoFromDecoded(inst);\n'
     '\tif (Decoder::MThemeEnabled(Decoder::MTheme::T234)) {\n'
     '\t\t// Track M, M2a (T234, upstream e85279ea; KYTY_M_T234): two operands - MEM = min/max(MEM, DATA0); DATA1 is\n'
     '\t\t// not read (the game encodes 0 there, i.e. v0 - the address register of its ds_max_f32). The compare\n'
     '\t\t// argument carries DATA0 and is not used by the emitter at =1.\n'
     '\t\tconst auto address = ReadU32(MemorySourceAt(inst, 1));\n'
     '\t\tconst auto data    = ReadU32(MemorySourceAt(inst, 0));\n'
     '\t\tir.Emit(opcode, {address, data, data, ir.GetExec()}, AddMemoryInfo(memory, inst.pc));\n'
     '\t\treturn true;\n'
     '\t}\n')

edit(SR + 'backend/spirv/spirvEmitterMemory.cpp',
     '\t\t\t    AtomicUpdate(\n'
     '\t\t\t        ctx.state, EmitMemoryElementPointer(ctx.state, access.resource, access.index),\n'
     '\t\t\t        mem.kind, [&](uint32_t old) {\n'
     '\t\t\t\t        const auto old_f =\n'
     '\t\t\t\t            Unary(ctx.state, spv::OpBitcast, TypeF32(ctx.state), old);\n',
     '\t\t\t    AtomicUpdate(\n'
     '\t\t\t        ctx.state, EmitMemoryElementPointer(ctx.state, access.resource, access.index),\n'
     '\t\t\t        mem.kind, [&](uint32_t old) {\n'
     '\t\t\t\t        if (Decoder::MThemeEnabled(Decoder::MTheme::T234)) {\n'
     '\t\t\t\t\t        // Track M, M2a (T234, upstream e85279ea; KYTY_M_T234): min/max of the word and DATA0\n'
     '\t\t\t\t\t        // with the NaN and denormal order of the hardware; DATA1 is not read.\n'
     '\t\t\t\t\t        return EmitDsFloatAtomicReplacement(ctx.state, old, data, max_value);\n'
     '\t\t\t\t        }\n'
     '\t\t\t\t        const auto old_f =\n'
     '\t\t\t\t            Unary(ctx.state, spv::OpBitcast, TypeF32(ctx.state), old);\n')

edit(SR + 'backend/spirv/spirvEmitterInternal.h',
     'uint32_t EmitFloatAtomicReplacement(EmitterState& state, uint32_t old, uint32_t source,\n'
     '                                    bool max_value);\n',
     'uint32_t EmitFloatAtomicReplacement(EmitterState& state, uint32_t old, uint32_t source,\n'
     '                                    bool max_value);\n'
     '\n'
     '// Track M, M2a (T234, upstream e85279ea; KYTY_M_T234): DS_MIN/MAX_F32 replacement - a NaN operand yields the other\n'
     '// one, a signalling NaN is quieted, negative denormals tie with -0, positive denormals tie with each other, ties\n'
     '// select the source for min and the old value for max; the selected operand keeps its bits.\n'
     'uint32_t EmitDsFloatAtomicReplacement(EmitterState& state, uint32_t old, uint32_t source,\n'
     '                                      bool max_value);\n')

edit(SR + 'backend/spirv/spirvEmitterMemoryHelpers.cpp',
     '\treturn EmitSelectValueU32(\n'
     '\t    state, EmitLogicalAndBool(state, EmitLogicalNotBool(state, unordered), compare), source,\n'
     '\t    old);\n'
     '}\n',
     '\treturn EmitSelectValueU32(\n'
     '\t    state, EmitLogicalAndBool(state, EmitLogicalNotBool(state, unordered), compare), source,\n'
     '\t    old);\n'
     '}\n'
     '\n'
     'uint32_t EmitDsFloatAtomicReplacement(EmitterState& state, uint32_t old, uint32_t source,\n'
     '                                      bool max_value) {\n'
     '\tstruct OrderedBits {\n'
     '\t\tuint32_t nan;\n'
     '\t\tuint32_t signaling_nan;\n'
     '\t\tuint32_t key;\n'
     '\t};\n'
     '\tconst auto order_key = [&](uint32_t bits) {\n'
     '\t\tconst auto negative = EmitCompareU32Constant(state, spv::OpINotEqual,\n'
     '\t\t                                             EmitAndConstant(state, bits, 0x80000000u), 0u);\n'
     '\t\tconst auto negative_key = state.builder.AllocateId();\n'
     '\t\tstate.builder.AddFunction(spv::OpNot, TypeU32(state), negative_key, bits);\n'
     '\t\tconst auto positive_key =\n'
     '\t\t    EmitBinaryU32(state, spv::OpBitwiseXor, bits, ConstantU32(state, 0x80000000u));\n'
     '\t\treturn EmitSelectValueU32(state, negative, negative_key, positive_key);\n'
     '\t};\n'
     '\tconst auto classify = [&](uint32_t bits) {\n'
     '\t\tconst auto abs = EmitAndConstant(state, bits, 0x7fffffffu);\n'
     '\t\tconst auto nan = EmitCompareU32Constant(state, spv::OpUGreaterThan, abs, 0x7f800000u);\n'
     '\t\tconst auto signaling_nan = EmitLogicalAndBool(\n'
     '\t\t    state, nan, EmitCompareU32Constant(state, spv::OpIEqual,\n'
     '\t\t                                      EmitAndConstant(state, bits, 0x00400000u), 0u));\n'
     '\t\tconst auto small = EmitCompareU32Constant(state, spv::OpULessThan, abs, 0x00800000u);\n'
     '\t\tconst auto sign  = EmitAndConstant(state, bits, 0x80000000u);\n'
     '\t\tconst auto positive_denorm = EmitLogicalAndBool(\n'
     '\t\t    state, EmitCompareU32Constant(state, spv::OpIEqual, sign, 0u),\n'
     '\t\t    EmitCompareU32Constant(state, spv::OpINotEqual, abs, 0u));\n'
     '\t\t// Negative denorms tie with -0; positive denorms tie only with each other.\n'
     '\t\tconst auto small_bits =\n'
     '\t\t    EmitSelectValueU32(state, positive_denorm, ConstantU32(state, 1u), sign);\n'
     '\t\tconst auto key_bits = EmitSelectValueU32(state, small, small_bits, bits);\n'
     '\t\treturn OrderedBits {nan, signaling_nan, order_key(key_bits)};\n'
     '\t};\n'
     '\tconst auto lhs           = classify(old);\n'
     '\tconst auto rhs           = classify(source);\n'
     '\tconst auto choose_source = state.builder.AllocateId();\n'
     '\tstate.builder.AddFunction(max_value ? spv::OpUGreaterThan : spv::OpULessThanEqual,\n'
     '\t                          TypeBool(state), choose_source, rhs.key, lhs.key);\n'
     '\t// Keep original bits: ordering denorms does not flush the selected operand.\n'
     '\tauto result = EmitSelectValueU32(state, choose_source, source, old);\n'
     '\tresult      = EmitSelectValueU32(state, lhs.nan, source, result);\n'
     '\tresult      = EmitSelectValueU32(state, rhs.nan, old, result);\n'
     '\tresult      = EmitSelectValueU32(state, rhs.signaling_nan,\n'
     '\t                                EmitOrU32(state, source, ConstantU32(state, 0x00400000u)), result);\n'
     '\treturn EmitSelectValueU32(state, lhs.signaling_nan,\n'
     '\t                          EmitOrU32(state, old, ConstantU32(state, 0x00400000u)), result);\n'
     '}\n')

# ---------------------------------------------------------------- T233
edit(SR + 'ir/opcodes/ValueOpcodes.inc',
     'VALUE_OPCODE(SharedAtomicDec32, U32, U32, U32, U1)\n',
     'VALUE_OPCODE(SharedAtomicDec32, U32, U32, U32, U1)\n'
     '// Track M, M2a (T233, upstream d8be245c; KYTY_M_T233): legacy V_MAD/MAC/MADMK/MADAK_F32 - the product and the sum\n'
     '// are rounded separately (not fused); appended for cache compatibility.\n'
     'VALUE_OPCODE(FPMad32, F32, F32, F32, F32)\n')

edit(SR + 'ir/passes/PredicationElimination.cpp',
     '\t\tcase ValueOpcode::FPFma32:\n',
     '\t\tcase ValueOpcode::FPFma32:\n'
     '\t\tcase ValueOpcode::FPMad32:\n')

edit(SR + 'backend/spirv/spirvEmitterInstructions.h',
     'inline constexpr auto EmitFPFma32 =\n'
     '    EmitGlsl<GLSLstd450Fma, IR::Type::F32, uint32_t, uint32_t, uint32_t>;\n',
     'inline constexpr auto EmitFPFma32 =\n'
     '    EmitGlsl<GLSLstd450Fma, IR::Type::F32, uint32_t, uint32_t, uint32_t>;\n'
     '// Track M, M2a (T233; KYTY_M_T233): legacy MAD - OpFMul and OpFAdd, both NoContraction (spirvEmitterAlu.cpp).\n'
     'uint32_t EmitFPMad32(EmitterState& state, uint32_t arg0, uint32_t arg1, uint32_t arg2);\n')

edit(SR + 'backend/spirv/spirvEmitterAlu.cpp',
     'uint32_t EmitFPMedTri32(EmitterState& state, uint32_t a, uint32_t b, uint32_t c) {\n',
     'uint32_t EmitFPMad32(EmitterState& state, uint32_t a, uint32_t b, uint32_t c) {\n'
     '\t// Track M, M2a (T233, upstream d8be245c; KYTY_M_T233): legacy MAD/MAC round the product before the add. Denormals\n'
     '\t// follow our DenormFlushToZero mode: EmitFlushF32DenormToSignedZero flushes only when the module does not\n'
     '\t// (upstream 77d77221 / T237 - the commented-out variant - is not taken).\n'
     '\ta                  = EmitFlushF32DenormToSignedZero(state, a);\n'
     '\tb                  = EmitFlushF32DenormToSignedZero(state, b);\n'
     '\tc                  = EmitFlushF32DenormToSignedZero(state, c);\n'
     '\tconst auto product = EmitFPMul32(state, a, b);\n'
     '\tstate.builder.AddAnnotation(spv::OpDecorate, product, spv::DecorationNoContraction);\n'
     '\tconst auto sum = EmitFPAdd32(state, EmitFlushF32DenormToSignedZero(state, product), c);\n'
     '\tstate.builder.AddAnnotation(spv::OpDecorate, sum, spv::DecorationNoContraction);\n'
     '\treturn EmitFlushF32DenormToSignedZero(state, sum);\n'
     '}\n'
     '\n'
     'uint32_t EmitFPMedTri32(EmitterState& state, uint32_t a, uint32_t b, uint32_t c) {\n')

edit(SR + 'frontend/translate/Vector.cpp',
     'bool Translator::EmitVector(const Decoder::Instruction& inst) {\n',
     'namespace {\n'
     '\n'
     '// Track M, M2a (T233, upstream d8be245c; KYTY_M_T233): V_MAC_F32 (VOP2 0x1f, VOP3 0x11f), V_MADMK_F32 (0x20),\n'
     '// V_MADAK_F32 (0x21) and V_MAD_F32 (VOP3 0x141) are the legacy, unfused MAD; VOP2 0x2b-0x2d (VOP3 0x12b) are\n'
     '// V_FMAC/FMAMK/FMAAK_F32 - fused - and our decoder names them V_MAC/MADMK/MADAK_F32 too, so the raw opcode decides.\n'
     'IR::ValueOpcode LegacyMadOpcode(const Decoder::Instruction& inst) {\n'
     '\tif (!Decoder::MThemeEnabled(Decoder::MTheme::T233)) {\n'
     '\t\treturn IR::ValueOpcode::FPFma32;\n'
     '\t}\n'
     '\tif (inst.opcode != Decoder::Opcode::V_MAD_F32 && (inst.opcode_id & 0xffu) >= 0x2bu) {\n'
     '\t\treturn IR::ValueOpcode::FPFma32;\n'
     '\t}\n'
     '\treturn IR::ValueOpcode::FPMad32;\n'
     '}\n'
     '\n'
     '} // namespace\n'
     '\n'
     'bool Translator::EmitVector(const Decoder::Instruction& inst) {\n')

edit(SR + 'frontend/translate/Vector.cpp',
     '\t\tcase O::V_MAC_F32: return FloatTernary(inst, IR::ValueOpcode::FPFma32, true, true);\n'
     '\t\tcase O::V_MADMK_F32:\n'
     '\t\tcase O::V_MADAK_F32:\n'
     '\t\tcase O::V_MAD_F32:\n'
     '\t\tcase O::V_FMA_F32: return FloatTernary(inst, IR::ValueOpcode::FPFma32, false, true);\n',
     '\t\tcase O::V_MAC_F32: return FloatTernary(inst, LegacyMadOpcode(inst), true, true);\n'
     '\t\tcase O::V_MADMK_F32:\n'
     '\t\tcase O::V_MADAK_F32:\n'
     '\t\tcase O::V_MAD_F32: return FloatTernary(inst, LegacyMadOpcode(inst), false, true);\n'
     '\t\tcase O::V_FMA_F32: return FloatTernary(inst, IR::ValueOpcode::FPFma32, false, true);\n')

# ---------------------------------------------------------------- T256
edit(SR + 'backend/spirv/spirvEmitterFlow.cpp',
     '\tauto& state = ctx.state;\n'
     '\tif (exp.compr && !uint_output) {\n'
     '\t\tconst auto unpack =\n'
     '\t\t    MrtOutputMode(state, exp) == 5u ? GLSLstd450UnpackUnorm2x16 : GLSLstd450UnpackHalf2x16;\n',
     '\tauto& state = ctx.state;\n'
     '\t// Track M, M2a (T256, upstream b96871e2; KYTY_M_T256): compressed exports of SPI_SHADER_COL_FORMAT 6\n'
     '\t// (SNORM16_ABGR) unpack as signed normalized pairs and of format 8 (SINT16_ABGR) as sign-extended 16-bit\n'
     '\t// lanes (the raw path, as format 7 does with zero extension); off: both unpack as half.\n'
     '\tconst bool m_t256      = Decoder::MThemeEnabled(Decoder::MTheme::T256);\n'
     '\tconst auto output_mode = MrtOutputMode(state, exp);\n'
     '\tconst bool sint16_raw  = m_t256 && exp.compr && !uint_output && output_mode == 8u;\n'
     '\tif (exp.compr && !uint_output && !sint16_raw) {\n'
     '\t\tauto unpack = output_mode == 5u ? GLSLstd450UnpackUnorm2x16 : GLSLstd450UnpackHalf2x16;\n'
     '\t\tif (m_t256 && output_mode == 6u) {\n'
     '\t\t\tunpack = GLSLstd450UnpackSnorm2x16;\n'
     '\t\t}\n')

edit(SR + 'backend/spirv/spirvEmitterFlow.cpp',
     '\t\t\t\traw[component] = state.builder.AllocateId();\n'
     '\t\t\t\tstate.builder.AddFunction(spv::OpBitFieldUExtract, TypeU32(state), raw[component],\n'
     '\t\t\t\t                          packed, ConstantU32(state, lane * 16u),\n'
     '\t\t\t\t                          ConstantU32(state, 16));\n',
     '\t\t\t\traw[component] = state.builder.AllocateId();\n'
     '\t\t\t\tstate.builder.AddFunction(sint16_raw ? spv::OpBitFieldSExtract : spv::OpBitFieldUExtract,\n'
     '\t\t\t\t                          TypeU32(state), raw[component], packed,\n'
     '\t\t\t\t                          ConstantU32(state, lane * 16u), ConstantU32(state, 16));\n')

# ---------------------------------------------------------------- T306
edit(SR + 'backend/spirv/spirvEmitterImage.cpp',
     'uint32_t HorizontalOffsets(EmitterState& state, ImageDimension dimension) {\n',
     '// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the ConstOffset operand of a sample on <resource> from the\n'
     '// immediate packed offset (signed six-bit fields in the low bits of each byte), or 0 - the previous path, the\n'
     '// offset dropped, with a log line - for a cube image or a component outside the Vulkan minimum range [-8, 7].\n'
     'uint32_t MSampleConstOffset(ValueEmitContext& ctx, const IR::Inst& inst, uint32_t packed, uint32_t resource) {\n'
     '\tauto&       state      = ctx.state;\n'
     '\tconst auto& image      = state.program.info.images.at(resource);\n'
     '\tconst auto  components = ImageDimensionInfoFor(image.dimension).spatial_components;\n'
     '\tint32_t     values[3] {};\n'
     '\tbool        in_range = components >= 1u && components <= 3u;\n'
     '\tfor (uint32_t index = 0; in_range && index < components; index++) {\n'
     '\t\tconst auto bits = (packed >> (index * 8u)) & 0x3fu;\n'
     '\t\tvalues[index]   = static_cast<int32_t>(bits ^ 0x20u) - 0x20;\n'
     '\t\tin_range        = values[index] >= -8 && values[index] <= 7;\n'
     '\t}\n'
     '\tif (image.cube || !in_range) {\n'
     '\t\tLOGF("MTexOffset: shader=0x%016llx pc=0x%x offset=0x%08x previous path (%s)\\n",\n'
     '\t\t     static_cast<unsigned long long>(state.program.shader_hash), inst.Flags<IR::MemoryFlags>().pc, packed,\n'
     '\t\t     image.cube ? "cube" : "range");\n'
     '\t\treturn 0u;\n'
     '\t}\n'
     '\tif (components == 1u) {\n'
     '\t\treturn ConstantI32(state, values[0]);\n'
     '\t}\n'
     '\tconst auto x = ConstantI32(state, values[0]);\n'
     '\tconst auto y = ConstantI32(state, values[1]);\n'
     '\tif (components == 2u) {\n'
     '\t\treturn state.builder.Constant(spv::OpConstantComposite, TypeI32Vector(state, 2), x, y);\n'
     '\t}\n'
     '\treturn state.builder.Constant(spv::OpConstantComposite, TypeI32Vector(state, 3), x, y,\n'
     '\t                              ConstantI32(state, values[2]));\n'
     '}\n'
     '\n'
     '// Track M, M2a (T306; KYTY_M_T306): the packed offset of a sample when it is the same immediate for every lane that\n'
     '// executes the sample. At =1 the translator hands the offset dword over as SelectU32(exec of the sample, offset, 0)\n'
     '// (Translator::IMAGE_SAMPLE); the offset is exact when it is an immediate, or that wrapper around an immediate, or\n'
     '// the wrapper around SelectU32(c, immediate, old) - the VGPR written under the same lane mask c. Anything else (an\n'
     '// offset written under another mask, a computed offset): false, the previous path.\n'
     'bool MImmediateU32(IR::Value value, uint32_t& packed) {\n'
     '\tif (!value.IsImmediate() || value.GetType() != IR::Type::U32) {\n'
     '\t\treturn false;\n'
     '\t}\n'
     '\tpacked = value.U32();\n'
     '\treturn true;\n'
     '}\n'
     '\n'
     'bool MResolveSampleOffset(IR::Value value, uint32_t& packed) {\n'
     '\tvalue = value.Resolve();\n'
     '\tif (MImmediateU32(value, packed)) {\n'
     '\t\treturn true;\n'
     '\t}\n'
     '\tconst auto* wrapper = value.TryInstruction();\n'
     '\tif (wrapper == nullptr || wrapper->GetOpcode() != IR::ValueOpcode::SelectU32) {\n'
     '\t\treturn false;\n'
     '\t}\n'
     '\tconst auto exec  = wrapper->Arg(0).Resolve();\n'
     '\tconst auto inner = wrapper->Arg(1).Resolve();\n'
     '\tif (MImmediateU32(inner, packed)) {\n'
     '\t\treturn true;\n'
     '\t}\n'
     '\tconst auto* write = inner.TryInstruction();\n'
     '\treturn write != nullptr && write->GetOpcode() == IR::ValueOpcode::SelectU32 &&\n'
     '\t       write->Arg(0).Resolve() == exec && MImmediateU32(write->Arg(1).Resolve(), packed);\n'
     '}\n'
     '\n'
     'uint32_t HorizontalOffsets(EmitterState& state, ImageDimension dimension) {\n')

edit(SR + 'backend/spirv/spirvEmitterImage.cpp',
     '\t\tconst auto EmitSample = [&](uint32_t resource) {\n',
     '\t\t// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the texel offset of IMAGE_SAMPLE_*_O reaches the sample\n'
     '\t\t// as ConstOffset when it is an immediate (MSampleConstOffset); a non-constant offset keeps the previous path\n'
     '\t\t// (offset dropped) with a log line instead of failing the translation. Off: the previous path.\n'
     '\t\tbool     m_t306_offset = false;\n'
     '\t\tuint32_t m_t306_packed = 0;\n'
     '\t\tif (Decoder::MThemeEnabled(Decoder::MTheme::T306) && layout.offset != NoImageComponent &&\n'
     '\t\t    mem.image_address_components > layout.offset) {\n'
     '\t\t\tconst auto arg =\n'
     '\t\t\t    Decoder::ImageAddressComponentLayout(mem.image_sample_flags, layout.offset).bit_offset / 32u;\n'
     '\t\t\tif (arg < address->NumArgs() && MResolveSampleOffset(address->Arg(arg), m_t306_packed)) {\n'
     '\t\t\t\tm_t306_offset = true;\n'
     '\t\t\t} else {\n'
     '\t\t\t\tLOGF("MTexOffset: shader=0x%016llx pc=0x%x nonconstant offset, previous path\\n",\n'
     '\t\t\t\t     static_cast<unsigned long long>(state.program.shader_hash),\n'
     '\t\t\t\t     inst.Flags<IR::MemoryFlags>().pc);\n'
     '\t\t\t}\n'
     '\t\t}\n'
     '\t\tconst auto EmitSample = [&](uint32_t resource) {\n')

edit(SR + 'backend/spirv/spirvEmitterImage.cpp',
     '\t\t\tif (operand_mask != 0u) {\n'
     '\t\t\t\tsample_operands.push_back(operand_mask);\n'
     '\t\t\t\tsample_operands.insert(sample_operands.end(), operands.begin(), operands.end());\n'
     '\t\t\t}\n',
     '\t\t\tconst auto m_offset = m_t306_offset ? MSampleConstOffset(ctx, inst, m_t306_packed, resource) : 0u;\n'
     '\t\t\tconst auto sample_mask =\n'
     '\t\t\t    operand_mask | (m_offset != 0u ? static_cast<uint32_t>(spv::ImageOperandsConstOffsetMask) : 0u);\n'
     '\t\t\tif (sample_mask != 0u) {\n'
     '\t\t\t\tsample_operands.push_back(sample_mask);\n'
     '\t\t\t\tsample_operands.insert(sample_operands.end(), operands.begin(), operands.end());\n'
     '\t\t\t\tif (m_offset != 0u) {\n'
     '\t\t\t\t\tsample_operands.push_back(m_offset);\n'
     '\t\t\t\t}\n'
     '\t\t\t}\n')

edit(SR + 'frontend/translate/Memory.cpp',
     'bool Translator::IMAGE_SAMPLE(const Decoder::Instruction& inst) {\n'
     '\tconst auto memory   = MemoryInfoFromDecoded(inst);\n'
     '\tconst auto resource = GetImageResource(memory);\n'
     '\tconst auto sampler  = GetSamplerResource(memory);\n'
     '\tconst auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 0));\n',
     'bool Translator::IMAGE_SAMPLE(const Decoder::Instruction& inst) {\n'
     '\tconst auto memory   = MemoryInfoFromDecoded(inst);\n'
     '\tconst auto resource = GetImageResource(memory);\n'
     '\tconst auto sampler  = GetSamplerResource(memory);\n'
     '\tIR::Value  m_offset;\n'
     '\tif (Decoder::MThemeEnabled(Decoder::MTheme::T306) &&\n'
     '\t    (memory.image_sample_flags & Decoder::ImageSampleFlagOffset) != 0u) {\n'
     '\t\t// Track M, M2a (T306, upstream 984cfceb; KYTY_M_T306): the offset (address dword 0) seen through the lane mask\n'
     '\t\t// of this sample - the emitter (MResolveSampleOffset) proves an offset written under the same mask constant.\n'
     '\t\tm_offset = ir.Select(ir.GetExec(), IR::U32(ReadRawU32(OffsetOperand(PlainOperand(MemorySourceAt(inst, 0)), 0))),\n'
     '\t\t                     IR::U32(IR::Value(0u)));\n'
     '\t}\n'
     '\tconst auto address = MakeImageAddress(inst, MemorySourceAt(inst, 0));\n'
     '\tif (!m_offset.IsEmpty()) {\n'
     '\t\taddress.Instruction()->SetArg(0, m_offset);\n'
     '\t}\n')

# ---------------------------------------------------------------- T032
edit(SR + 'backend/spirv/spirvEmitterMemory.cpp',
     'void FormattedStore(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {\n'
     '\tEmitIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {\n'
     '\t\tconst auto resource = PrepareMemoryResourceAccess(ctx.state, mem);\n'
     '\t\tFormattedStorePrepared(ctx, inst, mem, 0u, resource, ctx.Arg(inst, inst.NumArgs() - 2));\n'
     '\t});\n'
     '}\n',
     '// Track M, M2a (T032; KYTY_M_T032): defined after PrepareFormattedMemory.\n'
     'void MStoreFormatted(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,\n'
     '                     const MemoryResourceAccess& resource, const Format::BufferFormatInfo& info, uint32_t data,\n'
     '                     uint32_t components);\n'
     '\n'
     'void FormattedStore(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {\n'
     '\tEmitIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {\n'
     '\t\tconst auto resource = PrepareMemoryResourceAccess(ctx.state, mem);\n'
     '\t\tif (Decoder::MThemeEnabled(Decoder::MTheme::T032)) {\n'
     '\t\t\tconst auto info = Format::GetFormatInfo(BufferFormat(ctx, mem));\n'
     '\t\t\tif (info.type != Format::ComponentType::Unknown) {\n'
     '\t\t\t\tMStoreFormatted(ctx, inst, mem, resource, info, ctx.Arg(inst, inst.NumArgs() - 2), 1u);\n'
     '\t\t\t\treturn;\n'
     '\t\t\t}\n'
     '\t\t}\n'
     '\t\tFormattedStorePrepared(ctx, inst, mem, 0u, resource, ctx.Arg(inst, inst.NumArgs() - 2));\n'
     '\t});\n'
     '}\n')

edit(SR + 'backend/spirv/spirvEmitterMemory.cpp',
     'void StoreFormattedInBounds(ValueEmitContext& ctx, const IR::MemoryInfo& mem,\n'
     '                            const PreparedFormattedMemory& plan, uint32_t component,\n'
     '                            uint32_t data) {\n',
     '// Track M, M2a (T032, upstream c66d977c, a6248c7c, 81f31263, de9c15fa; KYTY_M_T032): one component of a formatted\n'
     '// store encoded by the format of the V# - UNORM/SNORM: NaN -> 0, clamp, scale, round to nearest even; USCALED/\n'
     '// SSCALED: NaN -> 0, clamp, truncate toward zero; two-bit channels are unsigned in signed formats; FLOAT16: half;\n'
     '// any other type and width: the bits as they are.\n'
     'uint32_t MEncodeFormattedStoreComponent(ValueEmitContext& ctx, const Format::BufferFormatInfo& info,\n'
     '                                        uint32_t component, uint32_t data) {\n'
     '\tauto&      state      = ctx.state;\n'
     '\tconst auto bits       = info.component_bits[component];\n'
     '\tconst bool normalized = info.type == Format::ComponentType::Unorm ||\n'
     '\t                        info.type == Format::ComponentType::Snorm;\n'
     '\tconst bool scaled     = info.type == Format::ComponentType::Uscaled ||\n'
     '\t                        info.type == Format::ComponentType::Sscaled;\n'
     '\tif ((normalized || scaled) && bits >= 1u && bits < 32u) {\n'
     '\t\tconst bool is_signed = bits != 2u && (info.type == Format::ComponentType::Snorm ||\n'
     '\t\t                                      info.type == Format::ComponentType::Sscaled);\n'
     '\t\tconst auto max_value = static_cast<float>((1u << (bits - (is_signed ? 1u : 0u))) - 1u);\n'
     '\t\tconst auto lower =\n'
     '\t\t    normalized ? (is_signed ? -1.0f : 0.0f) : (is_signed ? -max_value - 1.0f : 0.0f);\n'
     '\t\tconst auto upper = normalized ? 1.0f : max_value;\n'
     '\t\tauto       value = Select(state, TypeF32(state), EmitClassifyF32Bits(state, data).nan,\n'
     '\t\t                          ConstantF32Value(state, 0.0f), EmitBitcastU32ToF32(state, data));\n'
     '\t\tvalue = EmitGlsl<GLSLstd450FClamp, IR::Type::F32, uint32_t, uint32_t, uint32_t>(\n'
     '\t\t    state, value, ConstantF32Value(state, lower), ConstantF32Value(state, upper));\n'
     '\t\tif (normalized) {\n'
     '\t\t\tvalue = EmitFPRoundEven32(state, EmitFPMul32(state, value, ConstantF32Value(state, max_value)));\n'
     '\t\t}\n'
     '\t\t// Float-to-integer conversion truncates scaled values toward zero.\n'
     '\t\tvalue = Unary(state, is_signed ? spv::OpConvertFToS : spv::OpConvertFToU,\n'
     '\t\t              is_signed ? TypeI32(state) : TypeU32(state), value);\n'
     '\t\treturn is_signed ? Unary(state, spv::OpBitcast, TypeU32(state), value) : value;\n'
     '\t}\n'
     '\tif (bits == 16u && info.type == Format::ComponentType::Float) {\n'
     '\t\tconst auto pair = state.builder.AllocateId();\n'
     '\t\tstate.builder.AddFunction(spv::OpCompositeConstruct, TypeF32Vector(state, 2), pair,\n'
     '\t\t                          EmitBitcastU32ToF32(state, data), ConstantF32Value(state, 0.0f));\n'
     '\t\treturn EmitPackHalf2x16(state, pair);\n'
     '\t}\n'
     '\treturn data;\n'
     '}\n'
     '\n'
     '// Track M, M2a (T032; KYTY_M_T032): every transferred component is encoded by the format of the V#. Non-packed\n'
     '// formats write the transferred components only, each in bounds as before (the components without a VGPR keep the\n'
     '// memory; upstream 81f31263 zero-fills them - [I], not taken); a packed bit-field format writes its one word whole\n'
     '// with the fields without a VGPR zero (as upstream).\n'
     'void MStoreFormatted(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,\n'
     '                     const MemoryResourceAccess& resource, const Format::BufferFormatInfo& info, uint32_t data,\n'
     '                     uint32_t components) {\n'
     '\tconst auto transferred =\n'
     '\t    info.packed_bitfield ? info.component_count : std::min(components, info.component_count);\n'
     '\tconst auto plan = PrepareFormattedMemory(ctx, inst, mem, resource, info, transferred, FormattedAccess::Store);\n'
     '\tEmitIfCondition(ctx.state, plan.in_bounds, [&]() {\n'
     '\t\tauto packed = ConstantU32(ctx.state, 0);\n'
     '\t\tfor (uint32_t component = 0; component < transferred; component++) {\n'
     '\t\t\tauto value = ConstantU32(ctx.state, 0);\n'
     '\t\t\tif (component < components) {\n'
     '\t\t\t\tvalue = data;\n'
     '\t\t\t\tif (components != 1u) {\n'
     '\t\t\t\t\tvalue = ctx.state.builder.AllocateId();\n'
     '\t\t\t\t\tctx.state.builder.AddFunction(spv::OpCompositeExtract, TypeU32(ctx.state), value, data,\n'
     '\t\t\t\t\t                              component);\n'
     '\t\t\t\t}\n'
     '\t\t\t}\n'
     '\t\t\tvalue           = MEncodeFormattedStoreComponent(ctx, info, component, value);\n'
     '\t\t\tconst auto bits = info.component_bits[component];\n'
     '\t\t\tif (info.packed_bitfield) {\n'
     '\t\t\t\tconst auto inserted = ctx.state.builder.AllocateId();\n'
     '\t\t\t\tctx.state.builder.AddFunction(spv::OpBitFieldInsert, TypeU32(ctx.state), inserted, packed, value,\n'
     '\t\t\t\t                              ConstantU32(ctx.state, info.component_bit_offset[component]),\n'
     '\t\t\t\t                              ConstantU32(ctx.state, bits));\n'
     '\t\t\t\tpacked = inserted;\n'
     '\t\t\t} else if (bits == 8u || bits == 16u) {\n'
     '\t\t\t\tStoreSubwordInBounds(ctx, mem, resource, plan.addresses[component], plan.indices[component], bits,\n'
     '\t\t\t\t                     value);\n'
     '\t\t\t} else {\n'
     '\t\t\t\tStoreWordInBounds(ctx, resource, plan.indices[component], value);\n'
     '\t\t\t}\n'
     '\t\t}\n'
     '\t\tif (info.packed_bitfield) {\n'
     '\t\t\tStoreWordInBounds(ctx, resource, plan.indices[0], packed);\n'
     '\t\t}\n'
     '\t});\n'
     '}\n'
     '\n'
     'void StoreFormattedInBounds(ValueEmitContext& ctx, const IR::MemoryInfo& mem,\n'
     '                            const PreparedFormattedMemory& plan, uint32_t component,\n'
     '                            uint32_t data) {\n')

edit(SR + 'backend/spirv/spirvEmitterMemory.cpp',
     '\t\tif (info.type != Format::ComponentType::Unknown) {\n'
     '\t\t\tconst auto plan = PrepareFormattedMemory(ctx, inst, mem, resource, info, components,\n'
     '\t\t\t                                         FormattedAccess::Store);\n',
     '\t\tif (info.type != Format::ComponentType::Unknown) {\n'
     '\t\t\tif (Decoder::MThemeEnabled(Decoder::MTheme::T032)) {\n'
     '\t\t\t\tMStoreFormatted(ctx, inst, mem, resource, info, composite, components);\n'
     '\t\t\t\treturn;\n'
     '\t\t\t}\n'
     '\t\t\tconst auto plan = PrepareFormattedMemory(ctx, inst, mem, resource, info, components,\n'
     '\t\t\t                                         FormattedAccess::Store);\n')


def main():
    files = {}
    for path, anchor, new, mode in edits:
        full = os.path.join(ROOT, path)
        if full not in files:
            raw = open(full, 'rb').read()
            crlf = b'\r\n' in raw
            files[full] = [raw.decode('utf-8').replace('\r\n', '\n'), crlf]
        text = files[full][0]
        n = text.count(anchor)
        if n != 1:
            print('ANCHOR COUNT %d in %s: %r' % (n, path, anchor[:80]))
            return 1
        files[full][0] = text.replace(anchor, new)
    for full, (text, crlf) in files.items():
        data = text.replace('\n', '\r\n') if crlf else text
        open(full, 'wb').write(data.encode('utf-8'))
        print('patched', full, 'crlf' if crlf else 'lf')
    print('edits', len(edits), 'files', len(files), 'OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
