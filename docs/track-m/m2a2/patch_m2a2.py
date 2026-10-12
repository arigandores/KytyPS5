"""M2a2 (HPP-843, ROADMAP s122 item 761(v); RC-T306-1 of M2c HPP-840): add the shader_cfg_tests test
TestMWave1T306OffsetWriteMask to tests/shaderCfgTests.cpp of a tree (test only, outside the translator source hash set).
Anchors are whole lines; the file is LF; written with write_bytes. Usage: python patch_m2a2.py <tree>
Edition 2: lane masks from compares with user-data SGPRs (VGPRs and the entry EXEC of a full compute wave are
constants in this test and fold); the full-mask form is a printed probe without a Check (finding of M2a2, see report)."""
import sys

path = sys.argv[1].rstrip('/') + '/tests/shaderCfgTests.cpp'
data = open(path, 'rb').read()
assert b'\r' not in data, 'CR in file'
text = data.decode('utf-8')
lines = text.split('\n')

TEST = r'''// Track M, M2a2 (HPP-843, ROADMAP s122 item 761(v); RC-T306-1 of M2c HPP-840): T306 passes the offset of
// image_sample_*_o as ConstOffset only when the offset VGPR was written under the lane mask of the sample
// (MResolveSampleOffset). The offset 0x0101 (+1 X, +1 Y) is written by v_mov_b32. Lane masks come from compares with
// user-data SGPRs (in this test VGPRs and the entry EXEC of a full compute wave are constants and fold away).
// Program "same": A = s8 > v0 (s_and_saveexec_b64); the offset is written and sampled under A - ConstOffset at
// KYTY_M_T306=1. Program "other": the offset is written under A & (s9 > v0), exec is restored to A before the sample -
// lanes of A outside the write mask keep their old offset, so the previous path (no ConstOffset, an MTexOffset line).
// At 0 neither program has ConstOffset. A guard that ignores the write mask gives "other" a ConstOffset (mutant
// t306_mask of C:/kyty/m657/m2c/mut_m2c.py). Program "full" (printed probe, no Check): the offset is written under A
// and exec is restored to the entry EXEC, the constant true of a full compute wave - SelectU32(true, offset, 0) folds
// and the write under A is taken for the T306 wrapper (finding of M2a2, decision of the lead).
void TestMWave1T306OffsetWriteMask() {
  namespace D = ShaderRecompiler::Decoder;
  const bool on = D::MThemeEnabled(D::MTheme::T306);
  uint32_t const_offset[3] = {};
  uint32_t samples[3] = {};
  for (uint32_t form = 0; form < 3u; form++) {
    std::vector<uint32_t> shader = {
        EncodeVopc(0xc4, 8, 0),   // v_cmp_gt_u32 vcc, s8, v0
        EncodeSop1(0x24, 40, 106), // s_and_saveexec_b64 s[40:41], vcc (exec = A)
    };
    if (form == 1u) {
      shader.push_back(EncodeVopc(0xc4, 9, 0));    // v_cmp_gt_u32 vcc, s9, v0
      shader.push_back(EncodeSop1(0x24, 42, 106)); // s_and_saveexec_b64 s[42:43], vcc (exec = A & B)
    }
    shader.push_back(EncodeVop1(0x01, 20, 255)); // v_mov_b32 v20, 0x0101 (offset +1 X, +1 Y)
    shader.push_back(0x0101u);
    if (form == 1u) {
      shader.push_back(EncodeSop1(0x04, 126, 42)); // s_mov_b64 exec, s[42:43] (exec = A)
    } else if (form == 2u) {
      shader.push_back(EncodeSop1(0x04, 126, 40)); // s_mov_b64 exec, s[40:41] (exec = entry EXEC)
    }
    shader.push_back(EncodeMimg0(0x37, 0x1)); // image_sample_lz_o v4, v[20:22]
    shader.push_back(EncodeMimg1(4, 0, 0, 20));
    shader.push_back(EncodeMimg0(0x08, 0x1)); // image_store v4, v[0:1] (keeps the sample live)
    shader.push_back(EncodeMimg1(4, 0, 0, 0));
    shader.push_back(0xbf810000u);
    auto user_data = ImageTestUserData();
    auto options = MakeCompileOptions(ShaderType::Compute);
    options.user_data = user_data;
    auto result = RecompileForTest(shader, options);
    CheckSpirvBinaryValidates(result.spirv);
    const auto source = DisassembleSpirvBinary(result.spirv);
    const_offset[form] = CountSourceOccurrences(source, "ConstOffset");
    samples[form] = CountSourceOccurrences(source, "OpImageSample");
  }
  std::fprintf(stderr,
               "[mw1] T306 knob=%d write-mask same: OpImageSample=%u ConstOffset=%u other: OpImageSample=%u "
               "ConstOffset=%u reference=same %s, other 0\n",
               on ? 1 : 0, samples[0], const_offset[0], samples[1], const_offset[1], on ? ">=1" : "0");
  std::fprintf(stderr, "[mw1] T306 knob=%d probe full-mask (no check): OpImageSample=%u ConstOffset=%u\n", on ? 1 : 0,
               samples[2], const_offset[2]);
  Check(samples[0] >= 1u && samples[1] >= 1u, "T306: offset write-mask test lost its sample");
  Check(on ? const_offset[0] >= 1u : const_offset[0] == 0u,
        "T306: offset written under the mask of the sample does not follow KYTY_M_T306");
  Check(const_offset[1] == 0u, "T306: offset written under another lane mask became a ConstOffset");
}
'''

ANCHOR = 'void TestNewShaderRecompilerCfgStraightLine() {'
RUN_ANCHOR = '  RUN(TestMWave1Translator);'
assert lines.count(ANCHOR) == 1 and lines.count(RUN_ANCHOR) == 1
assert 'TestMWave1T306OffsetWriteMask' not in text
i = lines.index(ANCHOR)
lines[i:i] = TEST.split('\n')
j = lines.index(RUN_ANCHOR)
lines.insert(j + 1, '  RUN(TestMWave1T306OffsetWriteMask);')
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('patched', path)
