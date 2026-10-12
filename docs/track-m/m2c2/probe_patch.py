"""M2c2 (HPP-844): Red Team's own probe of the M2a2 finding (ROADMAP s122 item 762(d)(2)) - NOT committed.
Inserts TestM2c2T306Probe into the M2c worktree test file (after main's test, before the CFG straight-line test) and a
RUN line. Each form is selected by M2C2_FORM=<n> (one process per form, a translator EXIT kills only that form).
Forms (offset 0x0101 = (+1,+1) written under A = s8 > v0; old offset 0x0202 written under the entry exec first):
  0 full_old  compute: old 0x0202, write 0x0101 under A, exec := s[40:41] (entry EXEC, constant true), sample
  1 lit       compute: write 0x0101 under A, s_mov_b64 exec, -1 (inline constant), sample
  2 pix_lit   pixel:   as 1
  3 pix_entry pixel:   as 0 (exec := saved entry EXEC, helper==0 - not a constant)
  4 ctl_same  compute: old 0x0202, write 0x0101 under A, sample under A (positive control: ConstOffset is right)
  5 ctl_other compute: old 0x0202, write 0x0101 under A&B (B = s9 > v0), exec := A, sample (negative control)
Prints '[m2c2] form=<n> knob=<k> OpImageSample=<s> ConstOffset=<c>'. LF file, whole-line anchors."""
import sys

F = 'C:/kyty/m657/m2c/wt/tests/shaderCfgTests.cpp'
ANCHOR_FN = 'void TestNewShaderRecompilerCfgStraightLine() {'
ANCHOR_RUN = '  RUN(TestMWave1T306OffsetWriteMask);'
NL = chr(10)

FN = r'''// M2c2 (HPP-844) probe, never committed.
void TestM2c2T306Probe() {
  namespace D = ShaderRecompiler::Decoder;
  const bool on = D::MThemeEnabled(D::MTheme::T306);
  const char *sel = std::getenv("M2C2_FORM");
  if (sel == nullptr) {
    return;
  }
  const uint32_t form = static_cast<uint32_t>(std::strtoul(sel, nullptr, 0));
  const bool pixel = form == 2u || form == 3u;
  const bool old = form == 0u || form == 3u || form == 4u || form == 5u;
  std::vector<uint32_t> shader;
  if (old) {
    shader.push_back(EncodeVop1(0x01, 20, 255)); // v_mov_b32 v20, 0x0202 (old offset, entry exec)
    shader.push_back(0x0202u);
  }
  shader.push_back(EncodeVopc(0xc4, 8, 0));   // v_cmp_gt_u32 vcc, s8, v0
  shader.push_back(EncodeSop1(0x24, 40, 106)); // s_and_saveexec_b64 s[40:41], vcc (exec = A)
  if (form == 5u) {
    shader.push_back(EncodeVopc(0xc4, 9, 0));    // v_cmp_gt_u32 vcc, s9, v0
    shader.push_back(EncodeSop1(0x24, 42, 106)); // s_and_saveexec_b64 s[42:43], vcc (exec = A & B)
  }
  shader.push_back(EncodeVop1(0x01, 20, 255)); // v_mov_b32 v20, 0x0101
  shader.push_back(0x0101u);
  if (form == 0u || form == 3u) {
    shader.push_back(EncodeSop1(0x04, 126, 40)); // s_mov_b64 exec, s[40:41] (entry exec)
  } else if (form == 1u || form == 2u) {
    shader.push_back(EncodeSop1(0x04, 126, 193)); // s_mov_b64 exec, -1
  } else if (form == 5u) {
    shader.push_back(EncodeSop1(0x04, 126, 42)); // s_mov_b64 exec, s[42:43] (exec = A)
  }
  shader.push_back(EncodeMimg0(0x37, 0x1)); // image_sample_lz_o v4, v[20:22]
  shader.push_back(EncodeMimg1(4, 0, 0, 20));
  shader.push_back(EncodeMimg0(0x08, 0x1)); // image_store v4, v[0:1]
  shader.push_back(EncodeMimg1(4, 0, 0, 0));
  shader.push_back(0xbf810000u);
  auto user_data = ImageTestUserData();
  ShaderPixelInputInfo ps_info{};
  ps_info.ps_system_input_base = 9;
  ps_info.ps_pos_x = true;
  auto options = MakeCompileOptions(pixel ? ShaderType::Pixel : ShaderType::Compute);
  options.user_data = user_data;
  if (pixel) {
    options.input_info.pixel = &ps_info;
  }
  auto result = RecompileForTest(shader, options);
  CheckSpirvBinaryValidates(result.spirv);
  const auto source = DisassembleSpirvBinary(result.spirv);
  std::fprintf(stderr, "[m2c2] form=%u knob=%d OpImageSample=%u ConstOffset=%u\n", form, on ? 1 : 0,
               static_cast<unsigned>(CountSourceOccurrences(source, "OpImageSample")),
               static_cast<unsigned>(CountSourceOccurrences(source, "ConstOffset")));
}
'''

lines = open(F, 'rb').read().decode('utf-8').split(NL)
assert '\r' not in NL.join(lines)
i = [k for k, l in enumerate(lines) if l == ANCHOR_FN]
assert len(i) == 1, i
lines[i[0]:i[0]] = FN.split(NL)
j = [k for k, l in enumerate(lines) if l == ANCHOR_RUN]
assert len(j) == 1, j
lines.insert(j[0] + 1, '  RUN(TestM2c2T306Probe);')
open(F, 'wb').write(NL.join(lines).encode('utf-8'))
print('patched probe')
