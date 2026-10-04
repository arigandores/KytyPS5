"""F14e (HPP-505, ROADMAP s122 items 409(g)(2), 415(b)): shader_cfg_tests probes of KYTY_FIX_F19 - part A.

Part A builds against the sources without the fix too (the base of the =0 byte compare): the probes read the knob
themselves (Common::EnvFlagOn, the reading of FixF19Enabled) and call nothing of the fix.
  1. TestNewShaderRecompilerPixelImageSampleLodSelection: IMAGE_SAMPLE_C / _C_LZ on a k16UNorm T# - =0 manual, =1 Dref.
  2. TestF19IndirectComparisonTable: an indirect image table (material/heap pattern of TryMakeIndirectImage,
     materialized from host memory) with IMAGE_SAMPLE_C_LZ for k16UNorm + k8UNorm, k16UNorm + k32Float,
     k32Float + k8UNorm; =1 (O1): manual / Dref / manual for the whole table; =0: manual / manual / Dref.
Usage: python patch_f14e_tests_a.py <repo root>.
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')
NL = chr(10)


def patch(rel, edits):
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r', '')
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit('anchor count %d in %s: %r' % (n, rel, old[:120]))
        text = text.replace(old, new)
    out = text.encode('utf-8')
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    open(path, 'wb').write(out)
    print('patched', rel, 'edits', len(edits), 'crlf', crlf)


def L(*lines):
    return NL.join(lines) + NL


INC_OLD = L('#include "common/emulatorConfig.h"')
INC_NEW = L('#include "common/emulatorConfig.h"', '#include "common/envFlag.h"')

LOD_OLD = L(
    '    Check(SpirvManualDepthCompareCount(result.spirv,',
    '                                       OpImageSampleExplicitLod) == 1,',
    '          "manual pixel IMAGE_SAMPLE_C_LZ must compare the texel and select");',
    '  }',
    '}',
    '',
    'void TestNewShaderRecompilerImageViewDimensions() {',
)
LOD_NEW = L(
    '    Check(SpirvManualDepthCompareCount(result.spirv,',
    '                                       OpImageSampleExplicitLod) == 1,',
    '          "manual pixel IMAGE_SAMPLE_C_LZ must compare the texel and select");',
    '  }',
    '  {',
    '    // Track F, F14e (HPP-505, ROADMAP s122 item 409(g)(2)): a k16UNorm T# - the shader (manual) comparison at',
    '    // KYTY_FIX_F19=0 (the rule before the fix), native OpImageSampleDref* at =1 (the renderer views k16UNorm as',
    '    // D16_UNORM). The knob is read as FixF19Enabled reads it, once per process.',
    '    const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");',
    '    const auto c = compile(0x28, 0x1, Prospero::BufferFormat::k16UNorm);',
    '    const auto c_lz = compile(0x2f, 0x1, Prospero::BufferFormat::k16UNorm);',
    '    const auto dref = [](const std::vector<uint32_t> &spirv) {',
    '      return SpirvInstructionOpcodeCount(spirv, OpImageSampleDrefImplicitLod) +',
    '             SpirvInstructionOpcodeCount(spirv, OpImageSampleDrefExplicitLod);',
    '    };',
    '    const auto c_manual =',
    '        SpirvManualDepthCompareCount(c.spirv, OpImageSampleImplicitLod);',
    '    const auto c_lz_manual =',
    '        SpirvManualDepthCompareCount(c_lz.spirv, OpImageSampleExplicitLod);',
    '    std::printf("[f19] k16UNorm KYTY_FIX_F19=%d: C dref=%u manual=%u, C_LZ dref=%u manual=%u\\n",',
    '                fix_f19 ? 1 : 0, dref(c.spirv), c_manual, dref(c_lz.spirv), c_lz_manual);',
    '    if (fix_f19) {',
    '      Check(SpirvInstructionOpcodeCount(c.spirv,',
    '                                        OpImageSampleDrefImplicitLod) == 1 &&',
    '                dref(c.spirv) == 1 && c_manual == 0,',
    '            "k16UNorm IMAGE_SAMPLE_C must be native Dref at KYTY_FIX_F19=1");',
    '      Check(SpirvInstructionOpcodeCount(c_lz.spirv,',
    '                                        OpImageSampleDrefExplicitLod) == 1 &&',
    '                dref(c_lz.spirv) == 1 && c_lz_manual == 0,',
    '            "k16UNorm IMAGE_SAMPLE_C_LZ must be native Dref at KYTY_FIX_F19=1");',
    '    } else {',
    '      Check(dref(c.spirv) == 0 && c_manual == 1,',
    '            "k16UNorm IMAGE_SAMPLE_C must be the manual compare at KYTY_FIX_F19=0");',
    '      Check(dref(c_lz.spirv) == 0 && c_lz_manual == 1 &&',
    '                SpirvExplicitLodZeroCount(c_lz.spirv) == 1,',
    '            "k16UNorm IMAGE_SAMPLE_C_LZ must be the manual compare at KYTY_FIX_F19=0");',
    '    }',
    '  }',
    '}',
    '',
    '// Track F, F14e (HPP-505, ROADMAP s122 items 409(g)(2), 415(b)): an indirect image table sampled with',
    '// IMAGE_SAMPLE_C_LZ. The pixel shader reads its T# through the material/heap pattern TryMakeIndirectImage',
    '// (ResourceTracking.cpp) plans: v_readfirstlane_b32 -> s_mul_i32 by the record stride -> s_buffer_load_dword',
    '// key -> s_lshl_b32 5 -> s_buffer_load_dwordx8 from the heap. MaterializeResources enumerates the keys of the',
    '// material table in host memory (record 0 -> key 0, record 1 -> key 1), so the table has a root (heap entry 0)',
    '// and one candidate (heap entry 1). Returns the image resource count, the member count of the root table, and',
    '// the Dref / manual-compare sample counts of the SPIR-V.',
    'struct F19IndirectProbe {',
    '  size_t images = 0;',
    '  size_t members = 0;',
    '  uint32_t dref = 0;',
    '  uint32_t manual = 0;',
    '  uint32_t plain = 0;',
    '};',
    '',
    'F19IndirectProbe CompileF19IndirectTable(Prospero::BufferFormat root_format,',
    '                                         Prospero::BufferFormat candidate_format) {',
    '  constexpr uint32_t OpImageSampleExplicitLod = 88;',
    '  constexpr uint32_t OpImageSampleDrefImplicitLod = 89;',
    '  constexpr uint32_t OpImageSampleDrefExplicitLod = 90;',
    '  constexpr uint32_t record_stride = 224;',
    '  alignas(256) static std::array<uint32_t, 256> material{};',
    '  alignas(256) static std::array<uint32_t, 64> heap{};',
    '  material.fill(0u);',
    '  heap.fill(0u);',
    '  material[record_stride / 4u] = 1u;',
    '  const auto set_descriptor = [&](uint32_t key, Prospero::BufferFormat format) {',
    '    uint32_t *d = &heap[key * 8u];',
    '    d[0] = 0x20u + key;',
    '    d[1] = (static_cast<uint32_t>(format) << 20u) | (3u << 30u); // width 4',
    '    d[2] = 3u << 14u;                                               // height 4',
    '    d[3] = DstSel(4, 5, 6, 7) |',
    '           (static_cast<uint32_t>(Prospero::ImageType::kColor2D) << 28u);',
    '  };',
    '  set_descriptor(0u, root_format);',
    '  set_descriptor(1u, candidate_format);',
    '  const auto material_address = reinterpret_cast<uint64_t>(material.data());',
    '  const auto heap_address = reinterpret_cast<uint64_t>(heap.data());',
    '  std::array<uint32_t, 64> user_data{};',
    '  user_data[0] = static_cast<uint32_t>(material_address);',
    '  user_data[1] = static_cast<uint32_t>((material_address >> 32u) & 0xffffu) |',
    '                 (record_stride << 16u);',
    '  user_data[2] = 2u; // two records',
    '  user_data[4] = static_cast<uint32_t>(heap_address);',
    '  user_data[5] = static_cast<uint32_t>((heap_address >> 32u) & 0xffffu) | (16u << 16u);',
    '  user_data[6] = 4u; // 64 bytes: two T#',
    '  user_data[8] = 3u << 12u; // S# s[8:11]: depth compare LESS_EQUAL',
    '  const uint32_t shader[] = {',
    '      EncodeVop1(0x02, 16, 256u + 4u),        // v_readfirstlane_b32 s16, v4',
    '      EncodeSop2(0x26, 17, 16, 255), record_stride, // s_mul_i32 s17, s16, 224',
    '      EncodeSmem0(0x08, 18, 0), 17u << 25u,   // s_buffer_load_dword s18, s[0:3], s17',
    '      EncodeSop2(0x1e, 19, 18, 128u + 5u),    // s_lshl_b32 s19, s18, 5',
    '      EncodeSmem0(0x0b, 20, 2), 19u << 25u,   // s_buffer_load_dwordx8 s[20:27], s[4:7], s19',
    '      EncodeMimg0(0x2f, 0x1),',
    '      EncodeMimg1(0, 5, 2, 4),                // image_sample_c_lz v0, v[4:6], s[20:27], s[8:11]',
    '      EncodeExp0(0x00, 0xf, true, false, true),',
    '      EncodeExp1(0, 1, 2, 3),',
    '      0xbf810000u,',
    '  };',
    '  auto ps_info = RegressionPixelInputInfo();',
    '  auto options = MakeCompileOptions(ShaderType::Pixel);',
    '  options.input_info.pixel = &ps_info;',
    '  options.dump_ir = true;',
    '  options.user_data = user_data;',
    '  auto result = RecompileForTest(shader, options);',
    '  CheckSpirvBinaryValidates(result.spirv);',
    '  F19IndirectProbe probe;',
    '  probe.images = result.program.info.images.size();',
    '  probe.members = probe.images != 0u',
    '                      ? result.program.info.images[0].indirect_resources.size()',
    '                      : 0u;',
    '  probe.dref = SpirvInstructionOpcodeCount(result.spirv, OpImageSampleDrefImplicitLod) +',
    '               SpirvInstructionOpcodeCount(result.spirv, OpImageSampleDrefExplicitLod);',
    '  probe.manual = SpirvManualDepthCompareCount(result.spirv, OpImageSampleExplicitLod);',
    '  probe.plain = SpirvInstructionOpcodeCount(result.spirv, OpImageSampleExplicitLod);',
    '  return probe;',
    '}',
    '',
    'void TestF19IndirectComparisonTable() {',
    '  using Format = Prospero::BufferFormat;',
    '  const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");',
    '  struct Row {',
    '    Format root;',
    '    Format candidate;',
    '    bool manual_at_1; // variant O1: the "or" of the =1 rule over the table',
    '    bool manual_at_0; // the rule before the fix: the root decides',
    '    const char *name;',
    '  };',
    '  const Row rows[] = {',
    '      {Format::k16UNorm, Format::k8UNorm, true, true, "k16UNorm+k8UNorm"},',
    '      {Format::k16UNorm, Format::k32Float, false, true, "k16UNorm+k32Float"},',
    '      {Format::k32Float, Format::k8UNorm, true, false, "k32Float+k8UNorm"},',
    '  };',
    '  for (const auto &row : rows) {',
    '    const auto probe = CompileF19IndirectTable(row.root, row.candidate);',
    '    std::printf("[f19] indirect %s KYTY_FIX_F19=%d: images=%zu members=%zu dref=%u manual=%u "',
    '                "plain_explicit=%u\\n",',
    '                row.name, fix_f19 ? 1 : 0, probe.images, probe.members, probe.dref,',
    '                probe.manual, probe.plain);',
    '    Check(probe.images == 2u && probe.members == 2u,',
    '          "indirect comparison table did not materialize as a root and one candidate");',
    '    const bool manual = fix_f19 ? row.manual_at_1 : row.manual_at_0;',
    '    if (manual) {',
    '      Check(probe.dref == 0u && probe.manual == probe.members,',
    '            "indirect comparison table must be the manual compare for every member");',
    '    } else {',
    '      Check(probe.dref == probe.members && probe.manual == 0u,',
    '            "indirect comparison table must be native Dref for every member");',
    '    }',
    '  }',
    '}',
    '',
    'void TestNewShaderRecompilerImageViewDimensions() {',
)

RUN_OLD = L('  RUN(TestNewShaderRecompilerPixelImageSampleLodSelection);')
RUN_NEW = L('  RUN(TestNewShaderRecompilerPixelImageSampleLodSelection);', '  RUN(TestF19IndirectComparisonTable);')

patch('tests/shaderCfgTests.cpp', [(INC_OLD, INC_NEW), (LOD_OLD, LOD_NEW), (RUN_OLD, RUN_NEW)])
print('ALL OK')
