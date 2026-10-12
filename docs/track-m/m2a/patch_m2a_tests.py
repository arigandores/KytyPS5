"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(i), (iv)): tests of the translator themes of wave 1.
tests/shaderCfgTests.cpp: TestMWave1Translator (T234 decoder, T256 export unpack, T233 fused/unfused structure) and the
KYTY_M_DECODE mode (the translator's own decoder over a raw GCN dump - member (ii)).
tests/ShaderRecompilerComputeTests.cpp: the GPU gate cases MWave1Cases (expected = reference), --m-wave1-case <name>,
--m-wave1-list, --m-wave1-cache; the old cases that encode the pre-fix answer follow their knob.
Whole-line anchors, each exactly once; CRLF kept. Usage: python patch_m2a_tests.py <root>"""
import os
import sys

ROOT = sys.argv[1]
edits = []


def edit(path, anchor, new):
    edits.append((path, anchor, new))


CFG = 'tests/shaderCfgTests.cpp'
CMP = 'tests/ShaderRecompilerComputeTests.cpp'

# ------------------------------------------------------------------ shaderCfgTests.cpp
edit(CFG,
     'void TestNewShaderRecompilerCfgStraightLine() {\n',
     '// Track M, M2a (HPP-838, ROADMAP s122 item 756(v)(1)): translator themes of wave 1 at the knob values of this process\n'
     '// (KYTY_M_<theme>, read once). Each block checks the answer of its knob: at 1 the ISA reference, at 0 the previous\n'
     '// translation, which differs from the reference (the reproduction of the theme at 0; numbers - the GPU gate\n'
     '// --m-wave1-case of shader_recompiler_compute_tests).\n'
     'uint32_t MWave1CountExtInst(const std::vector<uint32_t> &binary, uint32_t ext_inst) {\n'
     '  uint32_t count = 0;\n'
     '  for (size_t i = 5; i < binary.size();) {\n'
     '    const uint32_t word_count = binary[i] >> 16u;\n'
     '    if (word_count == 0 || i + word_count > binary.size()) {\n'
     '      break;\n'
     '    }\n'
     '    if ((binary[i] & 0xffffu) == 12u && word_count >= 5u && binary[i + 4] == ext_inst) {\n'
     '      count++;\n'
     '    }\n'
     '    i += word_count;\n'
     '  }\n'
     '  return count;\n'
     '}\n'
     '\n'
     'uint32_t MWave1CountDecoration(const std::vector<uint32_t> &binary, uint32_t decoration) {\n'
     '  uint32_t count = 0;\n'
     '  for (size_t i = 5; i < binary.size();) {\n'
     '    const uint32_t word_count = binary[i] >> 16u;\n'
     '    if (word_count == 0 || i + word_count > binary.size()) {\n'
     '      break;\n'
     '    }\n'
     '    if ((binary[i] & 0xffffu) == 71u && word_count >= 3u && binary[i + 2] == decoration) {\n'
     '      count++;\n'
     '    }\n'
     '    i += word_count;\n'
     '  }\n'
     '  return count;\n'
     '}\n'
     '\n'
     'void TestMWave1Translator() {\n'
     '  namespace D = ShaderRecompiler::Decoder;\n'
     '  std::fprintf(stderr, "[mw1] mask=0x%02x token=%s\\n", D::MThemeMask(), D::MWave1SignatureToken().c_str());\n'
     '  {\n'
     '    // T234: DS_MIN/MAX_F32 read the address and DATA0 only (reference: two operands).\n'
     '    const bool on = D::MThemeEnabled(D::MTheme::T234);\n'
     '    for (bool max_value : {false, true}) {\n'
     '      const uint32_t shader[] = {EncodeDs0(max_value ? 0x13 : 0x12, 4), EncodeDs1Ex(0, 250, 7, 1)};\n'
     '      D::Instruction decoded;\n'
     '      D::DecodeInstruction(shader, 0u, decoded);\n'
     '      std::fprintf(stderr, "[mw1] T234 knob=%d %s src_count=%u reference=2\\n", on ? 1 : 0,\n'
     '                   max_value ? "ds_max_f32" : "ds_min_f32", decoded.src_count);\n'
     '      Check(decoded.opcode == (max_value ? D::Opcode::DS_MAX_F32 : D::Opcode::DS_MIN_F32) &&\n'
     '                decoded.src_count == (on ? 2u : 3u),\n'
     '            "T234: DS float min/max source count does not follow KYTY_M_T234");\n'
     '    }\n'
     '  }\n'
     '  {\n'
     '    // T256: compressed export of SPI_SHADER_COL_FORMAT 6 (SNORM16_ABGR) unpacks with UnpackSnorm2x16 (GLSL 60),\n'
     '    // of format 8 (SINT16_ABGR) with sign extension; at 0 both unpack as half (GLSL 62).\n'
     '    const bool on = D::MThemeEnabled(D::MTheme::T256);\n'
     '    const uint32_t shader[] = {\n'
     '        EncodeExp0(0x00, 0xf, true, true),\n'
     '        EncodeExp1(0, 1, 0, 0), // compressed MRT0\n'
     '        0xbf810000u,\n'
     '    };\n'
     '    auto options = MakeCompileOptions(ShaderType::Pixel);\n'
     '    ShaderPixelInputInfo snorm16_info;\n'
     '    snorm16_info.target_output_mode[0] = 6;\n'
     '    options.input_info.pixel = &snorm16_info;\n'
     '    auto snorm16 = RecompileForTest(shader, options);\n'
     '    const auto snorm_unpack = MWave1CountExtInst(snorm16.spirv, 60);\n'
     '    const auto snorm_half = MWave1CountExtInst(snorm16.spirv, 62);\n'
     '    CheckSpirvBinaryValidates(snorm16.spirv);\n'
     '    ShaderPixelInputInfo sint16_info;\n'
     '    sint16_info.target_output_mode[0] = 8;\n'
     '    options.input_info.pixel = &sint16_info;\n'
     '    auto sint16 = RecompileForTest(shader, options);\n'
     '    const auto sint_source = DisassembleSpirvBinary(sint16.spirv);\n'
     '    const auto sint_sext = CountSourceOccurrences(sint_source, "OpBitFieldSExtract");\n'
     '    const auto sint_half = MWave1CountExtInst(sint16.spirv, 62);\n'
     '    CheckSpirvBinaryValidates(sint16.spirv);\n'
     '    std::fprintf(stderr,\n'
     '                 "[mw1] T256 knob=%d mode6 UnpackSnorm2x16=%u UnpackHalf2x16=%u mode8 SExtract=%u "\n'
     '                 "UnpackHalf2x16=%u reference=snorm/sext\\n",\n'
     '                 on ? 1 : 0, snorm_unpack, snorm_half, sint_sext, sint_half);\n'
     '    Check(on ? (snorm_unpack == 2u && snorm_half == 0u) : (snorm_unpack == 0u && snorm_half == 2u),\n'
     '          "T256: SNORM16 compressed export does not follow KYTY_M_T256");\n'
     '    Check(on ? (sint_sext == 4u && sint_half == 0u) : (sint_sext == 0u && sint_half == 2u),\n'
     '          "T256: SINT16 compressed export does not follow KYTY_M_T256");\n'
     '  }\n'
     '  {\n'
     '    // T233: legacy V_MAD_F32 (VOP3 0x141), V_MAC_F32 (VOP2 0x1f, VOP3 0x11f), V_MADMK_F32 (0x20), V_MADAK_F32\n'
     '    // (0x21) are not fused - OpFMul + OpFAdd with NoContraction (decoration 42); V_FMAC_F32 (0x2b) and V_FMA_F32\n'
     '    // (VOP3 0x14b) stay GLSL Fma (50).\n'
     '    const bool on = D::MThemeEnabled(D::MTheme::T233);\n'
     '    const auto vop2 = [](uint32_t op, uint32_t vdst, uint32_t src0, uint32_t vsrc1) {\n'
     '      return (op << 25u) | (vdst << 17u) | (vsrc1 << 9u) | src0;\n'
     '    };\n'
     '    const auto vop3w0 = [](uint32_t op, uint32_t vdst) { return (0x35u << 26u) | (op << 16u) | vdst; };\n'
     '    const auto vop3w1 = [](uint32_t s0, uint32_t s1, uint32_t s2) { return (s2 << 18u) | (s1 << 9u) | s0; };\n'
     '    const uint32_t legacy_shader[] = {\n'
     '        vop3w0(0x141, 10), vop3w1(256, 257, 258),       // v_mad_f32 v10, v0, v1, v2\n'
     '        vop2(0x1f, 2, 256, 1),                           // v_mac_f32 v2, v0, v1\n'
     '        vop2(0x20, 11, 256, 1), 0x3f800800u,             // v_madmk_f32 v11, v0, K, v1\n'
     '        vop2(0x21, 12, 256, 1), 0xbf801000u,             // v_madak_f32 v12, v0, v1, K\n'
     '        EncodeExp0(0x00, 0xf, true), EncodeExp1(10, 2, 11, 12),\n'
     '        0xbf810000u,\n'
     '    };\n'
     '    const uint32_t mixed_shader[] = {\n'
     '        vop3w0(0x11f, 3), vop3w1(256, 257, 0),           // v_mac_f32 (VOP3) v3, v0, v1\n'
     '        vop2(0x2b, 4, 256, 1),                           // v_fmac_f32 v4, v0, v1\n'
     '        vop3w0(0x14b, 13), vop3w1(256, 257, 258),       // v_fma_f32 v13, v0, v1, v2\n'
     '        EncodeExp0(0x00, 0xf, true), EncodeExp1(3, 4, 13, 13),\n'
     '        0xbf810000u,\n'
     '    };\n'
     '    auto options = MakeCompileOptions(ShaderType::Pixel);\n'
     '    ShaderPixelInputInfo info;\n'
     '    options.input_info.pixel = &info;\n'
     '    auto legacy = RecompileForTest(legacy_shader, options);\n'
     '    CheckSpirvBinaryValidates(legacy.spirv);\n'
     '    auto mixed = RecompileForTest(mixed_shader, options);\n'
     '    CheckSpirvBinaryValidates(mixed.spirv);\n'
     '    const auto fma = MWave1CountExtInst(legacy.spirv, 50) + MWave1CountExtInst(mixed.spirv, 50);\n'
     '    const auto no_contraction =\n'
     '        MWave1CountDecoration(legacy.spirv, 42) + MWave1CountDecoration(mixed.spirv, 42);\n'
     '    std::fprintf(stderr, "[mw1] T233 knob=%d Fma=%u NoContraction=%u reference=Fma 2 NoContraction 10\\n",\n'
     '                 on ? 1 : 0, fma, no_contraction);\n'
     '    Check(on ? (fma == 2u && no_contraction == 10u) : (fma == 7u && no_contraction == 0u),\n'
     '          "T233: legacy MAD fusion does not follow KYTY_M_T233");\n'
     '  }\n'
     '}\n'
     '\n'
     'void TestNewShaderRecompilerCfgStraightLine() {\n')

edit(CFG,
     '  RUN(TestShaderReplayWalkBits);\n',
     '  RUN(TestShaderReplayWalkBits);\n'
     '  RUN(TestMWave1Translator);\n')

edit(CFG,
     '  if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {\n',
     '  if (const char *m_decode = std::getenv("KYTY_M_DECODE"); m_decode != nullptr && m_decode[0] != 0) {\n'
     '    // Track M, M2a (HPP-838, ROADMAP s122 item 756(v)(1)(ii)): the translator\'s own decoder over a raw GCN dump\n'
     '    // (_Shaders/original form) - one line per instruction: pc, family, raw opcode id, the decoder\'s text.\n'
     '    namespace D = ShaderRecompiler::Decoder;\n'
     '    std::vector<uint32_t> code;\n'
     '    if (FILE *file = std::fopen(m_decode, "rb"); file != nullptr) {\n'
     '      uint32_t word = 0;\n'
     '      while (std::fread(&word, sizeof(word), 1, file) == 1) {\n'
     '        code.push_back(word);\n'
     '      }\n'
     '      std::fclose(file);\n'
     '    } else {\n'
     '      std::fprintf(stderr, "m-decode: cannot open %s\\n", m_decode);\n'
     '      return 1;\n'
     '    }\n'
     '    D::Program program;\n'
     '    D::DecodeProgram(std::span<const uint32_t>(code), program);\n'
     '    for (const auto &inst : program.instructions) {\n'
     '      std::printf("pc=0x%05x fam=%d op=0x%03x %s\\n", inst.pc, static_cast<int>(inst.family), inst.opcode_id,\n'
     '                  D::InstructionToString(inst).c_str());\n'
     '    }\n'
     '    std::printf("m-decode: words=%zu instructions=%zu\\n", code.size(), program.instructions.size());\n'
     '    return 0;\n'
     '  }\n'
     '  if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {\n')

# ------------------------------------------------------------------ ShaderRecompilerComputeTests.cpp
edit(CMP,
     '      {0x55667788u, 0x44556677u, 0x22334455u, 0x11223344u, 0x00112233u,\n'
     '       0x00000011u, 0u, 0u},\n',
     '      // Track M, M2a (T203): at KYTY_M_T203=1 only S2[1:0] selects the byte (the reference).\n'
     '      ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T203)\n'
     '          ? std::vector<u32>{0x55667788u, 0x44556677u, 0x22334455u, 0x55667788u, 0x44556677u,\n'
     '                             0x22334455u, 0x55667788u, 0x22334455u}\n'
     '          : std::vector<u32>{0x55667788u, 0x44556677u, 0x22334455u, 0x11223344u, 0x00112233u,\n'
     '                             0x00000011u, 0u, 0u},\n')

edit(CMP,
     '  test.expected = {0x41100000u, 0x3f800000u};\n',
     '  // Track M, M2a (T234): at KYTY_M_T234=1 DATA1 is not read - min/max of the word and DATA0 (the reference).\n'
     '  test.expected = ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T234)\n'
     '                      ? std::vector<u32>{0x40800000u, 0x40800000u}\n'
     '                      : std::vector<u32>{0x41100000u, 0x3f800000u};\n')

edit(CMP,
     '  test.name = "ImageSampleA16OffsetKeepsTexelOffset32BitOnGpu";\n'
     '  test.code = code;\n'
     '  test.expected = {0x3f800000u, 0x40000000u, 0x40400000u, 0x40800000u};\n',
     '  test.name = "ImageSampleA16OffsetKeepsTexelOffset32BitOnGpu";\n'
     '  test.code = code;\n'
     '  test.expected = {0x3f800000u, 0x40000000u, 0x40400000u, 0x40800000u};\n'
     '  if (ShaderRecompiler::Decoder::MThemeEnabled(ShaderRecompiler::Decoder::MTheme::T306)) {\n'
     '    // Track M, M2a (T306): at KYTY_M_T306=1 the +1 X offset reaches the sample - texel (3, 1) (the reference).\n'
     '    SetRgbaPixel(&image, 4, 3, 1, 0x40a00000u, 0x40c00000u, 0x40e00000u, 0x41000000u);\n'
     '    test.expected = {0x40a00000u, 0x40c00000u, 0x40e00000u, 0x41000000u};\n'
     '  }\n')

edit(CMP,
     '  auto result = ShaderRecompiler::CompileProgram(\n'
     '      std::move(translated), options, specialization);\n'
     '  for (const auto &[text, expected] : test.decoded_counts) {\n',
     '  auto result = ShaderRecompiler::CompileProgram(\n'
     '      std::move(translated), options, specialization);\n'
     '  if (std::getenv("KYTY_M_DUMP_IR") != nullptr) {\n'
     '    // Track M, M2a (HPP-838): the decoded program and the IR of a case (diagnostics of the --m-wave1-case gate).\n'
     '    std::printf("%s\\n==== IR ====\\n%s\\n", result.decoded_dump.c_str(), result.ir_dump.c_str());\n'
     '  }\n'
     '  for (const auto &[text, expected] : test.decoded_counts) {\n')

MW1_CASES = r'''
// Track M, M2a (HPP-838, ROADMAP s122 item 756(v)(1)(i), (iv)): GPU test gate of the translator themes of wave 1. Every
// case expects the reference (RDNA2 ISA description / LLVM AMDGPU semantics; [I] about silicon). One case per process
// (--m-wave1-case <name>): rc 0 and "ALL OK" = the answer at the knob values of the process equals the reference; an
// abort with the readback = it differs (at 0 - the reproduction of the theme, at 1 - a failure or a caught mutant).
TestCase MWave1T234DsMinMaxIgnoresData1() {
  using O = ShaderOpcode;
  std::vector<u32> code;
  AppendVMovU32(&code, 1, 0);
  AppendVMovLiteral(&code, 2, 0x40800000u);
  code.push_back(EncodeDs0(0x0d, 0));
  code.push_back(EncodeDs1(0, 2, 1));
  code.push_back(EncodeDs0(0x0d, 4));
  code.push_back(EncodeDs1(0, 2, 1));
  AppendVMovLiteral(&code, 4, 0x41100000u); // DATA0 of ds_min_f32: 9.0
  AppendVMovLiteral(&code, 5, 0x40000000u); // DATA1 of ds_min_f32: 2.0 (not an operand)
  code.push_back(EncodeDs0(0x12, 0));
  code.push_back(EncodeDs1Ex(0, 5, 4, 1));
  AppendVMovLiteral(&code, 6, 0x3f800000u); // DATA0 of ds_max_f32: 1.0
  AppendVMovLiteral(&code, 7, 0x40400000u); // DATA1 of ds_max_f32: 3.0 (not an operand)
  code.push_back(EncodeDs0(0x13, 4));
  code.push_back(EncodeDs1Ex(0, 7, 6, 1));
  code.push_back(EncodeDs0(0x36, 0));
  code.push_back(EncodeDs1(8, 0, 1));
  code.push_back(EncodeDs0(0x36, 4));
  code.push_back(EncodeDs1(9, 0, 1));
  AppendStoreVgpr(&code, 8, 0);
  AppendStoreVgpr(&code, 9, 1);
  AppendEnd(&code);
  TestCase test;
  test.name = "MW1T234DsMinMaxIgnoresData1";
  test.code = code;
  test.initial = std::vector<u32>(2, 0);
  test.expected = {0x40800000u, 0x40800000u}; // min(4, 9) = 4, max(4, 1) = 4
  test.opcodes = {O::V_MOV_B32,  O::DS_WRITE_B32, O::DS_MIN_F32,
                  O::DS_MAX_F32, O::DS_READ_B32,  O::BUFFER_STORE_DWORD,
                  O::S_ENDPGM};
  test.compute_info.threads_num[0] = 1;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.has_compute_info = true;
  return test;
}

TestCase MWave1T234DsMinMaxLdsClasses() {
  using O = ShaderOpcode;
  // Upstream e85279ea table. Rows memory, columns source: -inf, -normal, -denorm, -0, +0, +denorm, +normal, +inf,
  // qNaN, sNaN. O/N select old/new; Q/R quiet them.
  constexpr const char *minimum[] = {
      "OOOOOOOOOR", "NNOOOOOOOR", "NNNNOOOOOR", "NNNOOOOOOR", "NNNNOOOOOR",
      "NNNNNNOOOR", "NNNNNNOOOR", "NNNNNNNOOR", "NNNNNNNNOR", "QQQQQQQQQQ"};
  constexpr const char *maximum[] = {
      "ONNNNNNNOR", "OONNNNNNOR", "OOOONNNNOR", "OOOONNNNOR", "OOOOONNNOR",
      "OOOOOONNOR", "OOOOOONNOR", "OOOOOOOOOR", "NNNNNNNNOR", "QQQQQQQQQQ"};
  constexpr u32 old_values[] = {
      0xff800000u, 0xc0000000u, 0x80000100u, 0x80000000u, 0u,
      0x00000100u, 0x40000000u, 0x7f800000u, 0x7fc12345u, 0x7f812345u};
  constexpr u32 sources[] = {
      0xff800000u, 0xc0400000u, 0x80000001u, 0x80000000u, 0u,
      0x00000001u, 0x40400000u, 0x7f800000u, 0xffc54321u, 0xff854321u};
  const auto select = [](char choice, u32 old, u32 source) {
    const u32 bits = choice == 'O' || choice == 'Q' ? old : source;
    return choice == 'Q' || choice == 'R' ? bits | 0x00400000u : bits;
  };
  TestCase test;
  test.name = "MW1T234DsMinMaxLdsClasses";
  for (u32 row = 0; row < 10u; ++row) {
    for (u32 column = 0; column < 10u; ++column) {
      const auto old = old_values[row];
      const auto source = sources[column];
      test.initial.insert(test.initial.end(), {old, source, 0u, 0u});
      test.expected.insert(test.expected.end(),
                           {old, source, select(minimum[row][column], old, source),
                            select(maximum[row][column], old, source)});
    }
  }
  // Reversing positive denorm magnitudes still selects source for min and old for max.
  test.initial.insert(test.initial.end(), {1u, 0x100u, 0u, 0u});
  test.expected.insert(test.expected.end(), {1u, 0x100u, 0x100u, 1u});
  const auto count = static_cast<u32>(test.initial.size() / 4u);
  auto &code = test.code;
  code.push_back(EncodeVop2(0x1a, 1, InlineU32(3), 0)); // v1 = tid << 3 (LDS address)
  code.push_back(EncodeVop2(0x1a, 8, InlineU32(4), 0)); // v8 = tid << 4 (buffer offset)
  code.push_back(EncodeMubuf0(0x0d));                   // buffer_load_dwordx2 v[2:3] = old, source
  code.push_back(EncodeMubuf1(2, 0, 8));
  for (u32 offset : {0u, 4u}) {
    code.push_back(EncodeDs0(0x0d, offset));
    code.push_back(EncodeDs1(0, 2, 1));
  }
  code.push_back(EncodeDs0(0x12, 0));
  code.push_back(EncodeDs1Ex(0, 250, 3, 1)); // DATA1 is unused and uninitialized.
  code.push_back(EncodeDs0(0x13, 4));
  code.push_back(EncodeDs1Ex(0, 251, 3, 1));
  for (u32 component = 0; component < 2u; ++component) {
    code.push_back(EncodeDs0(0x36, component * 4u));
    code.push_back(EncodeDs1(4u + component, 0, 1));
  }
  code.push_back(EncodeMubuf0(0x1d, 8)); // buffer_store_dwordx2 v[4:5] at tid * 16 + 8
  code.push_back(EncodeMubuf1(4, 0, 8));
  AppendEnd(&code);
  test.compute_info.threads_num[0] = count;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.compute_info.thread_ids_num = 1;
  test.compute_info.lds_size_dwords = count * 2u;
  test.has_compute_info = true;
  test.opcodes = {O::V_LSHLREV_B32, O::BUFFER_LOAD_DWORDX2, O::DS_WRITE_B32, O::DS_MIN_F32,
                  O::DS_MAX_F32, O::DS_READ_B32, O::BUFFER_STORE_DWORDX2, O::S_ENDPGM};
  return test;
}

TestCase MWave1T233LegacyMadRoundsProduct() {
  using O = ShaderOpcode;
  // a = b = 1 + 2^-12: a * b = 1 + 2^-11 + 2^-24 rounds (tie to even) to 1 + 2^-11 = -c; legacy MAD = 0, fused = 2^-24.
  constexpr u32 a = 0x3f800800u;
  constexpr u32 c = 0xbf801000u;
  std::vector<u32> code;
  AppendVMovLiteral(&code, 0, a);
  AppendVMovLiteral(&code, 1, a);
  AppendVMovLiteral(&code, 2, c);
  AppendVop3(&code, 0x141, 10, Vgpr(0), Vgpr(1), Vgpr(2)); // v_mad_f32 v10, v0, v1, v2
  AppendVMovLiteral(&code, 11, c);
  code.push_back(EncodeVop2(0x1f, 11, Vgpr(0), 1));       // v_mac_f32 v11, v0, v1
  code.push_back(EncodeVop2(0x20, 12, Vgpr(0), 2));       // v_madmk_f32 v12, v0, K = a, v2
  code.push_back(a);
  code.push_back(EncodeVop2(0x21, 13, Vgpr(0), 1));       // v_madak_f32 v13, v0, v1, K = c
  code.push_back(c);
  AppendVMovLiteral(&code, 14, c);
  AppendVop3(&code, 0x11f, 14, Vgpr(0), Vgpr(1), 0);      // v_mac_f32 (VOP3) v14, v0, v1
  AppendVMovLiteral(&code, 15, c);
  code.push_back(EncodeVop2(0x2b, 15, Vgpr(0), 1));       // v_fmac_f32 v15, v0, v1 (fused control)
  AppendVop3(&code, 0x14b, 16, Vgpr(0), Vgpr(1), Vgpr(2)); // v_fma_f32 v16, v0, v1, v2 (fused control)
  for (u32 i = 0; i < 7u; i++) {
    AppendStoreVgpr(&code, 10u + i, i);
  }
  AppendEnd(&code);
  TestCase test;
  test.name = "MW1T233LegacyMadRoundsProduct";
  test.code = code;
  test.expected = {0u, 0u, 0u, 0u, 0u, 0x33800000u, 0x33800000u};
  test.opcodes = {O::V_MOV_B32, O::V_MAD_F32, O::V_MAC_F32, O::V_MADMK_F32, O::V_MADAK_F32, O::V_FMA_F32,
                  O::BUFFER_STORE_DWORD, O::S_ENDPGM};
  return test;
}

TestCase MWave1T203AlignByteTwoBitOffset() {
  using O = ShaderOpcode;
  std::vector<u32> code;
  AppendVMovLiteral(&code, 0, 0x11223344u);
  AppendVMovLiteral(&code, 1, 0x55667788u);
  const std::vector<u32> offsets = {0, 1, 2, 3, 4, 5, 7, 8, 31, 32, 0xffffffffu};
  for (u32 i = 0; i < static_cast<u32>(offsets.size()); i++) {
    AppendVMovU32(&code, 2, i * sizeof(u32));
    AppendBufferLoadDword(&code, 2, 2); // the offset is not a constant of the program
    AppendVop3(&code, 0x14f, 10u + i, Vgpr(0), Vgpr(1), Vgpr(2));
    AppendStoreVgpr(&code, 10u + i, i);
  }
  AppendEnd(&code);
  TestCase test;
  test.name = "MW1T203AlignByteTwoBitOffset";
  test.code = code;
  test.initial = offsets;
  test.expected = {0x55667788u, 0x44556677u, 0x33445566u, 0x22334455u, 0x55667788u, 0x44556677u,
                   0x22334455u, 0x55667788u, 0x22334455u, 0x55667788u, 0x22334455u};
  test.opcodes = {O::V_MOV_B32, O::BUFFER_LOAD_DWORD, O::V_ALIGNBYTE_B32, O::BUFFER_STORE_DWORD,
                  O::S_ENDPGM};
  return test;
}

TestCase MWave1T306SampleOffsetsFourNeighbors() {
  using O = ShaderOpcode;
  TestCase test;
  test.name = "MW1T306SampleOffsetsFourNeighbors";
  // Upstream 984cfceb: +1 X, -1 X, -1 Y, +1 Y on image_sample_lz_o (0x37), _lz_o, _l_o (0x34), _d_o (0x32).
  constexpr std::array<u32, 4> offsets{0x01u, 0x3fu, 0x3f00u, 0x0100u};
  constexpr std::array<u32, 4> opcodes{0x37u, 0x37u, 0x34u, 0x32u};
  for (u32 sample = 0; sample < offsets.size(); ++sample) {
    AppendVMovLiteral(&test.code, 20, offsets[sample]);
    u32 coordinate = 21;
    if (opcodes[sample] == 0x32u) {
      for (float gradient : {0.25f, 0.f, 0.f, 0.25f}) {
        AppendVMovLiteral(&test.code, coordinate++, std::bit_cast<u32>(gradient));
      }
    }
    // All instructions address the center of texel (2, 1) before applying the offset.
    AppendVMovLiteral(&test.code, coordinate, std::bit_cast<u32>(0.625f));
    AppendVMovLiteral(&test.code, coordinate + 1, std::bit_cast<u32>(0.375f));
    if (opcodes[sample] == 0x34u) {
      AppendVMovU32(&test.code, coordinate + 2, 0);
    }
    test.code.push_back(EncodeMimg0(opcodes[sample], 0x1));
    test.code.push_back(EncodeMimg1(sample, 20));
    AppendStoreVgpr(&test.code, sample, sample);
  }
  AppendEnd(&test.code);
  test.sampled_image_rgba = MakeRgbaImage(4, 4);
  SetRgbaPixel(&test.sampled_image_rgba, 4, 2, 1, std::bit_cast<u32>(16.f), 0, 0, 0);
  constexpr std::array<std::array<u32, 2>, 4> neighbors{{{3, 1}, {1, 1}, {2, 0}, {2, 2}}};
  for (u32 sample = 0; sample < neighbors.size(); ++sample) {
    const auto value = std::bit_cast<u32>(float(sample + 1));
    SetRgbaPixel(&test.sampled_image_rgba, 4, neighbors[sample][0], neighbors[sample][1], value, 0, 0, 0);
    test.expected.push_back(value);
  }
  test.opcodes = {O::V_MOV_B32, O::IMAGE_SAMPLE, O::BUFFER_STORE_DWORD, O::S_ENDPGM};
  return test;
}

TestCase MWave1T032Snorm16XyzwSkinning() {
  using O = ShaderOpcode;
  // Upstream c66d977c: normal and tangent of a character skinning dispatch.
  constexpr std::array<u32, 8> values = {0x3d98f7c5u, 0xbedae712u, 0xbf66a19eu, 0x3f800000u,
                                         0x3f7e6baeu, 0xbd339a7du, 0x3dd0a2e2u, 0xbf800000u};
  std::vector<u32> code;
  for (u32 record = 0; record < 2; record++) {
    for (u32 component = 0; component < 4; component++) {
      AppendVMovLiteral(&code, component, values[record * 4 + component]);
    }
    AppendVMovU32(&code, 20, record);
    code.push_back(EncodeMubuf0(0x07u, 0, true, false));
    code.push_back(EncodeMubuf1(0, 0, 20));
  }
  AppendEnd(&code);
  TestCase test;
  test.name = "MW1T032Snorm16XyzwSkinning";
  test.code = std::move(code);
  test.initial = std::vector<u32>(4, 0xdeadbeefu);
  test.expected = {0xc947098fu, 0x7fff8cb0u, 0xfa637f35u, 0x80010d0au};
  test.user_data =
      MakeStructuredStorageBufferData(8, 2, false, BufferFormat(Prospero::BufferFormat::k16_16_16_16SNorm));
  test.has_user_data = true;
  test.opcodes = {O::V_MOV_B32, O::BUFFER_STORE_FORMAT_XYZW, O::S_ENDPGM};
  return test;
}

TestCase MWave1T032Snorm16XClampRound() {
  using O = ShaderOpcode;
  constexpr std::array<float, 9> values = {-2.0f, -1.0f, -0.75f, -0.25f, 0.0f, 0.25f, 0.75f, 1.0f, 2.0f};
  std::vector<u32> code;
  for (u32 i = 0; i < values.size(); i++) {
    AppendVMovLiteral(&code, 0, std::bit_cast<u32>(values[i]));
    AppendVMovU32(&code, 20, i * 2 + 2);
    code.push_back(EncodeMubuf0(0x04u));
    code.push_back(EncodeMubuf1(0, 0, 20));
  }
  AppendEnd(&code);
  TestCase test;
  test.name = "MW1T032Snorm16XClampRound";
  test.code = std::move(code);
  test.initial = std::vector<u32>(6, 0xdeadbeefu);
  test.expected = {0x8001beefu, 0xa0018001u, 0x0000e000u, 0x5fff2000u, 0x7fff7fffu, 0xdeadbeefu};
  test.user_data = MakeStructuredStorageBufferData(0, 24, false, BufferFormat(Prospero::BufferFormat::k16SNorm));
  test.has_user_data = true;
  test.opcodes = {O::V_MOV_B32, O::BUFFER_STORE_FORMAT_X, O::S_ENDPGM};
  return test;
}

TestCase MWave1T032Float16Xyzw() {
  using O = ShaderOpcode;
  // Upstream a6248c7c: this finite F32 has low bits 0x7e63, which form an F16 NaN if truncated.
  constexpr std::array<float, 8> values = {std::bit_cast<float>(0x3f807e63u), -2.0f, 0.5f, 0.25f,
                                           -4.0f, 3.0f, 0.0f, 2.0f};
  std::vector<u32> code;
  for (u32 record = 0; record < 2; record++) {
    for (u32 component = 0; component < 4; component++) {
      AppendVMovLiteral(&code, component, std::bit_cast<u32>(values[record * 4 + component]));
    }
    AppendVMovU32(&code, 20, record);
    code.push_back(EncodeMubuf0(0x07u, 0, true, false));
    code.push_back(EncodeMubuf1(0, 0, 20));
  }
  AppendEnd(&code);
  TestCase test;
  test.name = "MW1T032Float16Xyzw";
  test.code = std::move(code);
  test.initial = std::vector<u32>(4, 0xdeadbeefu);
  test.expected = {0xc0003c04u, 0x34003800u, 0x4200c400u, 0x40000000u};
  test.user_data =
      MakeStructuredStorageBufferData(8, 2, false, BufferFormat(Prospero::BufferFormat::k16_16_16_16Float));
  test.has_user_data = true;
  test.opcodes = {O::V_MOV_B32, O::BUFFER_STORE_FORMAT_XYZW, O::S_ENDPGM};
  return test;
}

std::vector<TestCase> MWave1T032ConversionCases() {
  using F = Prospero::BufferFormat;
  using O = ShaderOpcode;
  struct ConversionCase {
    const char *name[2];
    F format;
    u32 components;
    std::array<float, 4> values;
    u32 expected;
  };
  constexpr float nan = std::bit_cast<float>(0x7fc12345u);
  constexpr float inf = std::bit_cast<float>(0x7f800000u);
  // Upstream de9c15fa, except the four non-packed partial cases (ZeroFill X / Xy / Xyz of 8- and 16-bit formats):
  // here the components without a VGPR keep the memory (the transfer rule of our emitter; upstream zero-fills them,
  // [I]); packed bit-field formats write their one word whole with the missing fields zero (as upstream).
  constexpr ConversionCase inputs[] = {
      {{"MW1T032Snorm8Range", "MW1T032TSnorm8Range"}, F::k8_8_8_8SNorm, 4, {-2.0f, 0.25f, 0.75f, 2.0f}, 0x7f5f2081u},
      {{"MW1T032Snorm8Ties", "MW1T032TSnorm8Ties"}, F::k8_8SNorm, 2, {0.5f, -0.5f}, 0xffffc040u},
      {{"MW1T032SnormPackedAlpha", "MW1T032TSnormPackedAlpha"}, F::k10_10_10_2SNorm, 4,
       {-1.0f, -0.5f, 0.5f, 1.0f}, 0xd00c0201u},
      {{"MW1T032SnormPackedFirstChannel", "MW1T032TSnormPackedFirstChannel"}, F::k2_10_10_10SNorm, 4,
       {1.0f, -1.0f, 0.5f, -0.5f}, 0xc0100807u},
      {{"MW1T032SnormPackedZeroFillX", "MW1T032TSnormPackedZeroFillX"}, F::k10_10_10_2SNorm, 1, {-1.0f},
       0x00000201u},
      {{"MW1T032SnormPackedZeroFillXy", "MW1T032TSnormPackedZeroFillXy"}, F::k10_10_10_2SNorm, 2, {-1.0f, 1.0f},
       0x0007fe01u},
      {{"MW1T032SnormPackedZeroFillXyz", "MW1T032TSnormPackedZeroFillXyz"}, F::k10_10_10_2SNorm, 3,
       {-1.0f, 1.0f, -1.0f}, 0x2017fe01u},
      {{"MW1T032Snorm8PartialX", "MW1T032TSnorm8PartialX"}, F::k8_8_8_8SNorm, 1, {-1.0f}, 0xffffff81u},
      {{"MW1T032Snorm16PartialX", "MW1T032TSnorm16PartialX"}, F::k16_16SNorm, 1, {-1.0f}, 0xffff8001u},
      {{"MW1T032UscaledPartialXy", "MW1T032TUscaledPartialXy"}, F::k8_8_8_8UScaled, 2, {42.0f, 99.0f}, 0xffff632au},
      {{"MW1T032SscaledPartialXyz", "MW1T032TSscaledPartialXyz"}, F::k8_8_8_8SScaled, 3, {-42.0f, 127.0f, -128.0f},
       0xff807fd6u},
      {{"MW1T032Uscaled8Fraction", "MW1T032TUscaled8Fraction"}, F::k8UScaled, 1, {42.875f}, 0xffffff2au},
      {{"MW1T032Sscaled8Fraction", "MW1T032TSscaled8Fraction"}, F::k8SScaled, 1, {-42.875f}, 0xffffffd6u},
      {{"MW1T032Uscaled8Range", "MW1T032TUscaled8Range"}, F::k8_8_8_8UScaled, 4, {-1.0f, 255.875f, 256.0f, 0.0f},
       0x00ffff00u},
      {{"MW1T032Sscaled8Range", "MW1T032TSscaled8Range"}, F::k8_8_8_8SScaled, 4,
       {-129.0f, -128.75f, 127.875f, 128.0f}, 0x7f7f8080u},
      {{"MW1T032Uscaled16Range", "MW1T032TUscaled16Range"}, F::k16_16UScaled, 2, {65536.0f, 42.875f}, 0x002affffu},
      {{"MW1T032Sscaled16Range", "MW1T032TSscaled16Range"}, F::k16_16SScaled, 2, {-32769.0f, 32768.0f},
       0x7fff8000u},
      {{"MW1T032UscaledPacked", "MW1T032TUscaledPacked"}, F::k10_10_10_2UScaled, 4, {1024.0f, 3.875f, -1.0f, 4.0f},
       0xc0000fffu},
      {{"MW1T032SscaledPackedAlpha", "MW1T032TSscaledPackedAlpha"}, F::k10_10_10_2SScaled, 4,
       {-512.75f, 511.875f, -3.875f, 3.875f}, 0xffd7fe00u},
      {{"MW1T032SscaledPackedFirstChannel", "MW1T032TSscaledPackedFirstChannel"}, F::k2_10_10_10SScaled, 4,
       {3.0f, -512.0f, 511.0f, -1.0f}, 0xffdff803u},
      {{"MW1T032Snorm8SpecialValues", "MW1T032TSnorm8SpecialValues"}, F::k8_8_8_8SNorm, 4, {nan, inf, -inf, -0.0f},
       0x00817f00u},
      {{"MW1T032Uscaled8SpecialValues", "MW1T032TUscaled8SpecialValues"}, F::k8_8_8_8UScaled, 4,
       {nan, inf, -inf, -0.0f}, 0x0000ff00u},
      {{"MW1T032Sscaled8SpecialValues", "MW1T032TSscaled8SpecialValues"}, F::k8_8_8_8SScaled, 4,
       {nan, inf, -inf, -0.0f}, 0x00807f00u},
  };
  constexpr O store_opcodes[2][4] = {
      {O::BUFFER_STORE_FORMAT_X, O::BUFFER_STORE_FORMAT_XY, O::BUFFER_STORE_FORMAT_XYZ, O::BUFFER_STORE_FORMAT_XYZW},
      {O::TBUFFER_STORE_FORMAT_X, O::TBUFFER_STORE_FORMAT_XY, O::TBUFFER_STORE_FORMAT_XYZ,
       O::TBUFFER_STORE_FORMAT_XYZW},
  };
  std::vector<TestCase> cases;
  for (const auto &input : inputs) {
    for (const bool typed : {false, true}) {
      TestCase test;
      test.name = input.name[typed ? 1 : 0];
      for (u32 component = 0; component < input.components; ++component) {
        AppendVMovLiteral(&test.code, component, std::bit_cast<u32>(input.values[component]));
      }
      AppendVMovU32(&test.code, 20, 4);
      const u32 opcode = 3 + input.components;
      if (typed) {
        const u32 format = BufferFormat(input.format);
        test.code.push_back(EncodeMtbuf0(opcode, format & 0xfu, format >> 4u));
        test.code.push_back(EncodeMtbuf1(opcode, 0, 0, 20));
      } else {
        test.code.push_back(EncodeMubuf0(opcode));
        test.code.push_back(EncodeMubuf1(0, 0, 20));
      }
      AppendEnd(&test.code);
      test.initial = {0xdeadbeefu, 0xffffffffu, 0xcafef00du};
      test.expected = {0xdeadbeefu, input.expected, 0xcafef00du};
      test.user_data = MakeStructuredStorageBufferData(0, 12, false, BufferFormat(input.format));
      test.has_user_data = true;
      test.opcodes = {O::V_MOV_B32, store_opcodes[typed ? 1 : 0][input.components - 1], O::S_ENDPGM};
      cases.push_back(std::move(test));
    }
  }
  return cases;
}

std::vector<TestCase> MWave1Cases() {
  std::vector<TestCase> cases;
  cases.push_back(MWave1T234DsMinMaxIgnoresData1());
  cases.push_back(MWave1T234DsMinMaxLdsClasses());
  cases.push_back(MWave1T233LegacyMadRoundsProduct());
  cases.push_back(MWave1T203AlignByteTwoBitOffset());
  cases.push_back(MWave1T306SampleOffsetsFourNeighbors());
  cases.push_back(MWave1T032Snorm16XyzwSkinning());
  cases.push_back(MWave1T032Snorm16XClampRound());
  cases.push_back(MWave1T032Float16Xyzw());
  for (auto &test : MWave1T032ConversionCases()) {
    cases.push_back(std::move(test));
  }
  return cases;
}

} // namespace
} // namespace Libs::Graphics
'''

edit(CMP,
     '} // namespace\n'
     '} // namespace Libs::Graphics\n',
     MW1_CASES.lstrip('\n'))

edit(CMP,
     '  std::setvbuf(stdout, nullptr, _IONBF, 0);\n'
     '  EnsureConfigInitialized();\n'
     '  CheckLeastRecentlyUsedCacheOrdering();\n',
     '  std::setvbuf(stdout, nullptr, _IONBF, 0);\n'
     '  EnsureConfigInitialized();\n'
     '  CheckLeastRecentlyUsedCacheOrdering();\n'
     '  if (argc == 2 && std::strcmp(argv[1], "--m-wave1-list") == 0) {\n'
     '    // Track M, M2a (HPP-838): the names of the GPU gate cases of wave 1.\n'
     '    for (const auto &test : MWave1Cases()) {\n'
     '      std::printf("%s\\n", test.name);\n'
     '    }\n'
     '    return 0;\n'
     '  }\n'
     '  if (argc == 3 && std::strcmp(argv[1], "--m-wave1-case") == 0) {\n'
     '    // Track M, M2a (HPP-838, ROADMAP s122 item 756(v)(1)(i)): one GPU gate case at the knob values of this process.\n'
     '    std::printf("[mw1] mask=0x%02x case=%s\\n", ShaderRecompiler::Decoder::MThemeMask(), argv[2]);\n'
     '    for (const auto &test : MWave1Cases()) {\n'
     '      if (std::strcmp(test.name, argv[2]) == 0) {\n'
     '        VulkanHarness vulkan;\n'
     '        RunCase(&vulkan, test);\n'
     '        std::printf("ALL OK\\n");\n'
     '        return 0;\n'
     '      }\n'
     '    }\n'
     '    std::printf("[mw1] no case %s\\n", argv[2]);\n'
     '    return 2;\n'
     '  }\n'
     '  if (argc == 2 && std::strcmp(argv[1], "--m-wave1-cache") == 0) {\n'
     '    // Track M, M2a (HPP-838): ":mw1_<mask>" is the last token of the signature and "_mw1_<mask>" of the directory\n'
     '    // exactly when a theme is on; every theme off adds nothing.\n'
     '    const auto token = ShaderRecompiler::Decoder::MWave1SignatureToken();\n'
     '    const ShaderTranslationCache cache("PPSA21564");\n'
     '    const auto directory = Common::PathToString(cache.Directory());\n'
     '    std::string signature = cache.Signature();\n'
     '    while (!signature.empty() && (signature.back() == \'\\n\' || signature.back() == \'\\r\')) {\n'
     '      signature.pop_back();\n'
     '    }\n'
     '    std::string folder_token = token;\n'
     '    std::replace(folder_token.begin(), folder_token.end(), \':\', \'_\');\n'
     '    const bool sig_ok = token.empty() ? signature.find(":mw1_") == std::string::npos\n'
     '                                      : signature.size() >= token.size() &&\n'
     '                                            signature.compare(signature.size() - token.size(), token.size(),\n'
     '                                                              token) == 0;\n'
     '    const bool dir_ok = token.empty() ? directory.find("mw1_") == std::string::npos\n'
     '                                      : directory.size() >= folder_token.size() &&\n'
     '                                            directory.compare(directory.size() - folder_token.size(),\n'
     '                                                              folder_token.size(), folder_token) == 0;\n'
     '    std::printf("[mw1] mask=0x%02x token=%s\\n[mw1] cache signature=%s\\n[mw1] cache dir=%s sig_ok=%d dir_ok=%d\\n",\n'
     '                ShaderRecompiler::Decoder::MThemeMask(), token.c_str(), signature.c_str(), directory.c_str(),\n'
     '                sig_ok ? 1 : 0, dir_ok ? 1 : 0);\n'
     '    Require("MWave1Cache", "translation cache key", cache.Enabled() && sig_ok && dir_ok,\n'
     '            "mw1 token of the signature or directory does not follow the knobs");\n'
     '    std::printf("ALL OK\\n");\n'
     '    return 0;\n'
     '  }\n')


def main():
    files = {}
    for path, anchor, new in edits:
        full = os.path.join(ROOT, path)
        if full not in files:
            raw = open(full, 'rb').read()
            crlf = b'\r\n' in raw
            files[full] = [raw.decode('utf-8').replace('\r\n', '\n'), crlf]
        text = files[full][0]
        n = text.count(anchor)
        if n != 1:
            print('ANCHOR COUNT %d in %s: %r' % (n, path, anchor[:90]))
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
