# F2a (HPP-307) patch 3: tests of B26b (ROADMAP p.237(g)(3), RC6 of the F1b review) in
# tests/ShaderRecompilerComputeTests.cpp: GPU cases for S_BREV_B64 and V_CMP_LE_U64 (wave32, wave64),
# decoder checks for KYTY_FIX_B26=1 and =0, mode --fix-b26-only, and the knob line of --b26-pass.
import sys
sys.path.insert(0, 'C:/kyty/f287/f2a')
import patchlib

T = 'C:/kyty/KytyPS5/tests/ShaderRecompilerComputeTests.cpp'

CASES = r'''// Track F, F2a (HPP-307, ROADMAP p.237(g)(3)): S_BREV_B64 (SOP1 0x0c) with the RC6 edges of the F1b
// review - the literal of the game shader 57c4d5848e02ecdc (s11 = 0x00016204), a literal with bit 31
// (unsigned 64-bit source, zero extended: ISA RDNA2 6.2.1), a register pair with different halves, the
// same pair in place, the inline constant -1 (sign extended, all ones) and SCC left untouched.
TestCase B26ScalarBrevB64() {
  using O = ShaderOpcode;
  std::vector<u32> code;
  auto set_scc = [&](bool value) {
    code.push_back(EncodeSopc(0x06, InlineU32(1), InlineU32(value ? 1u : 0u)));
  };
  auto capture_scc = [&](u32 dst_sgpr) {
    code.push_back(EncodeSop2(0x0a, dst_sgpr, InlineU32(1), InlineU32(0)));
  };
  code.push_back(EncodeSop1(0x0c, 10, 255u)); // s_brev_b64 s[10:11], 0x20468000
  code.push_back(0x20468000u);
  code.push_back(EncodeSop1(0x0c, 12, 255u)); // s_brev_b64 s[12:13], 0x80000001
  code.push_back(0x80000001u);
  AppendSMovLiteral(&code, 4, 0x00000001u);
  AppendSMovLiteral(&code, 5, 0x12345678u);
  code.push_back(EncodeSop1(0x0c, 14, 4)); // s_brev_b64 s[14:15], s[4:5]
  code.push_back(EncodeSop1(0x0c, 4, 4));  // s_brev_b64 s[4:5], s[4:5]
  set_scc(false);
  code.push_back(EncodeSop1(0x0c, 16, 193u)); // s_brev_b64 s[16:17], -1
  capture_scc(18);
  set_scc(true);
  code.push_back(EncodeSop1(0x0c, 20, InlineU32(0))); // s_brev_b64 s[20:21], 0
  capture_scc(22);
  const u32 stored[] = {10, 11, 12, 13, 14, 15, 4, 5, 16, 17, 18, 20, 21, 22};
  for (u32 i = 0; i < std::size(stored); i++) {
    AppendStoreSgpr(&code, stored[i], i);
  }
  AppendEnd(&code);

  TestCase test{"B26ScalarBrevB64",
                code,
                {},
                {0x00000000u, 0x00016204u, 0x00000000u, 0x80000001u, 0x1e6a2c48u,
                 0x80000000u, 0x1e6a2c48u, 0x80000000u, 0xffffffffu, 0xffffffffu,
                 0u, 0u, 0u, 1u},
                {O::S_BREV_B64, O::S_MOV_B32, O::S_CMP_EQ_U32, O::S_CSELECT_B32,
                 O::V_MOV_B32, O::BUFFER_STORE_DWORD, O::S_ENDPGM}};
  test.decoded_counts = {{"S_BREV_B64", 6}};
  return test;
}

// Track F, F2a: V_CMP_LE_U64 (VOPC 0xe3 and its VOP3 form) with the RC6 edges - equal, less and
// greater in one compare (lanes 31 / 30 / 32 against 31), the high half deciding both ways, the
// unsigned extremes (-1 is the largest value, not below 0), a zero-extended literal, lanes off in EXEC
// writing 0, and the VOP3 form with an SGPR destination. Results are per lane, so the same program
// checks wave32 (VCC_LO) and wave64.
TestCase B26VectorCmpLeU64(u32 wave_size) {
  using O = ShaderOpcode;
  std::vector<u32> code;
  AppendVMovU32(&code, 1, 1);
  code.push_back(EncodeVop1(0x01, 2, Vgpr(0))); // v[2:3] = lane
  AppendVMovU32(&code, 3, 0);
  AppendVMovU32(&code, 4, 0); // v[4:5] = 0x00000001_00000000
  AppendVMovU32(&code, 5, 1);
  AppendVMovU32(&code, 6, 0xffffffffu); // v[6:7] = 0x00000000_ffffffff
  AppendVMovU32(&code, 7, 0);
  AppendVMovU32(&code, 8, 0); // v[8:9] = 0
  AppendVMovU32(&code, 9, 0);
  AppendVMovU32(&code, 10, 0xffffffffu); // v[10:11] = 0xffffffff_ffffffff
  AppendVMovU32(&code, 11, 0xffffffffu);
  AppendVMovU32(&code, 12, 0x80000000u); // v[12:13] = 0x00000000_80000000
  AppendVMovU32(&code, 13, 0);
  auto store_vcc_lanes = [&](u32 result_vgpr, u32 slot) {
    code.push_back(EncodeVop2(0x01, result_vgpr, InlineU32(0), 1)); // vcc ? 1 : 0
    AppendStoreVgprAtLaneDwordOffset(&code, result_vgpr, 0, slot * 64u);
  };
  AppendSMovLiteral(&code, 4, 31);
  AppendSMovLiteral(&code, 5, 0);
  code.push_back(EncodeVopc(0xe3, 4, 2)); // 0: 31 <= lane
  store_vcc_lanes(14, 0);
  AppendSMovLiteral(&code, 6, 0xffffffffu);
  AppendSMovLiteral(&code, 7, 0);
  code.push_back(EncodeVopc(0xe3, 6, 4)); // 1: 0x0_ffffffff <= 0x1_00000000
  store_vcc_lanes(15, 1);
  AppendSMovLiteral(&code, 8, 0);
  AppendSMovLiteral(&code, 9, 1);
  code.push_back(EncodeVopc(0xe3, 8, 6)); // 2: 0x1_00000000 <= 0x0_ffffffff
  store_vcc_lanes(16, 2);
  code.push_back(EncodeVopc(0xe3, 193u, 8)); // 3: -1 <= 0
  store_vcc_lanes(17, 3);
  code.push_back(EncodeVopc(0xe3, InlineU32(0), 10)); // 4: 0 <= 0xffffffff_ffffffff
  store_vcc_lanes(18, 4);
  code.push_back(EncodeVopc(0xe3, 255u, 12)); // 5: 0x80000000 (literal) <= 0x0_80000000
  code.push_back(0x80000000u);
  store_vcc_lanes(19, 5);
  AppendSMovLiteral(&code, 24, 0x0000ffffu);
  AppendSMovLiteral(&code, 25, 0x0000ffffu);
  code.push_back(EncodeSop1(0x04, 126, 24));          // s_mov_b64 exec, s[24:25]
  code.push_back(EncodeVopc(0xe3, InlineU32(0), 2));  // 6: 0 <= lane on the active lanes
  code.push_back(EncodeSop1(0x04, 126, 193u));        // s_mov_b64 exec, -1
  store_vcc_lanes(20, 6);
  AppendVop3(&code, 0x0e3, 22, 4, Vgpr(2)); // 7: v_cmp_le_u64 s[22:23], s[4:5], v[2:3]
  AppendVop3(&code, 0x101, 21, InlineU32(0), InlineU32(1), 22);
  AppendStoreVgprAtLaneDwordOffset(&code, 21, 0, 7u * 64u);
  AppendEnd(&code);

  TestCase test;
  test.name = wave_size == 32u ? "B26VectorCmpLeU64Wave32" : "B26VectorCmpLeU64Wave64";
  test.code = std::move(code);
  test.initial.assign(8u * 64u, 0xdeadbeefu);
  test.expected.assign(8u * 64u, 0u);
  for (u32 lane = 0; lane < 64; lane++) {
    test.expected[0 * 64 + lane] = lane >= 31u ? 1u : 0u;
    test.expected[1 * 64 + lane] = 1u;
    test.expected[2 * 64 + lane] = 0u;
    test.expected[3 * 64 + lane] = 0u;
    test.expected[4 * 64 + lane] = 1u;
    test.expected[5 * 64 + lane] = 1u;
    test.expected[6 * 64 + lane] = (lane % 32u) < 16u ? 1u : 0u;
    test.expected[7 * 64 + lane] = lane >= 31u ? 1u : 0u;
  }
  test.opcodes = {O::V_MOV_B32, O::S_MOV_B32, O::S_MOV_B64, O::V_CMP_LE_U64,
                  O::V_CNDMASK_B32, O::V_LSHLREV_B32, O::V_ADD_NC_U32,
                  O::BUFFER_STORE_DWORD, O::S_ENDPGM};
  test.decoded_counts = {{"V_CMP_LE_U64", 8}};
  test.compute_info.threads_num[0] = 64;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.compute_info.wave_size = wave_size;
  test.compute_info.thread_ids_num = 1;
  test.has_compute_info = true;
  return test;
}

TestCase B26VectorCmpLeU64Wave32() { return B26VectorCmpLeU64(32); }

TestCase B26VectorCmpLeU64Wave64() { return B26VectorCmpLeU64(64); }

std::string B26Decoded(const std::vector<u32> &words) {
  ShaderRecompiler::Decoder::Instruction inst;
  ShaderRecompiler::Decoder::DecodeInstruction(words, 0, inst);
  return ShaderRecompiler::Decoder::InstructionToString(inst) +
         " words=" + std::to_string(inst.word_count);
}

std::string B26Replace(std::string text, const std::string &from, const std::string &to) {
  const auto at = text.find(from);
  if (at != std::string::npos) {
    text.replace(at, from.size(), to);
  }
  return text;
}

// Track F, F2a: the decoder side of KYTY_FIX_B26. At 0 the three encodings of B26b decode exactly as
// before the fix: SOP1 0x0c and VOPC 0xe3 to the strings the pre-fix decoder printed in
// C:/kyty/s142/log_v142.txt (lines 305203 and 306334), the VOP3 form like its unsupported neighbour
// 0x0e0 (V_CMP_F_U64, not in the table in either build). At 1 they decode to the two opcodes.
void CheckB26Decode(bool fix_on) {
  const char *name = "B26Decode";
  const auto sop1 = B26Decoded({0xbe8a0cffu, 0x20468000u});
  const auto vopc = B26Decoded({0x7dc60004u});
  const auto vop3 = B26Decoded({EncodeVop3Word0(0x0e3, 22), EncodeVop3Word1(4, Vgpr(2))});
  if (!fix_on) {
    Require(name, "SOP1 0x0c at 0",
            sop1 == "0x00000000: unsupported family=SOP1 opcode=0x0c raw=[0xbe8a0cff] "
                    "reason=SOP1 opcode is not implemented words=1",
            sop1);
    Require(name, "VOPC 0xe3 at 0",
            vopc == "0x00000000: unsupported family=VOPC opcode=0xe3 raw=[0x7dc60004] "
                    "reason=VOPC opcode is not implemented words=1",
            vopc);
    const auto f_u64 = B26Decoded({EncodeVop3Word0(0x0e0, 22), EncodeVop3Word1(4, Vgpr(2))});
    const auto expected = B26Replace(
        B26Replace(f_u64, "opcode=0xe0", "opcode=0xe3"),
        "0x" + Hex(EncodeVop3Word0(0x0e0, 22)).substr(2),
        "0x" + Hex(EncodeVop3Word0(0x0e3, 22)).substr(2));
    Require(name, "VOP3 0x0e3 at 0",
            vop3 == expected && vop3.find("unsupported family=VOP3") != std::string::npos,
            vop3 + " | expected " + expected);
  } else {
    Require(name, "SOP1 0x0c at 1",
            sop1.find("S_BREV_B64") != std::string::npos && sop1.find("words=2") != std::string::npos &&
                sop1.find("unsupported") == std::string::npos,
            sop1);
    Require(name, "VOPC 0xe3 at 1",
            vopc.find("V_CMP_LE_U64") != std::string::npos &&
                vopc.find("unsupported") == std::string::npos,
            vopc);
    Require(name, "VOP3 0x0e3 at 1",
            vop3.find("V_CMP_LE_U64") != std::string::npos &&
                vop3.find("unsupported") == std::string::npos,
            vop3);
  }
  std::printf("[b26]     %s fix=%d\n      %s\n      %s\n      %s\n", name, fix_on ? 1 : 0,
              sop1.c_str(), vopc.c_str(), vop3.c_str());
}

'''.split('\n')

MODE = r'''  if (argc == 2 && std::strcmp(argv[1], "--fix-b26-only") == 0) {
    // Track F, F2a (HPP-307): the B26b cases at the knob value of this process.
    const bool fix_on = ShaderRecompiler::Decoder::FixB26Enabled();
    std::printf("[b26] KYTY_FIX_B26 effective=%d\n", fix_on ? 1 : 0);
    CheckB26Decode(fix_on);
    if (fix_on) {
      VulkanHarness vulkan;
      RunCase(&vulkan, B26ScalarBrevB64());
      RunCase(&vulkan, B26VectorCmpLeU64Wave32());
      RunCase(&vulkan, B26VectorCmpLeU64Wave64());
    }
    std::printf("ALL OK\n");
    return 0;
  }'''.split('\n')

patchlib.apply(T, [
    (['TestCase VectorVop3CompareEqI64OnGpu() {'], CASES, 'before'),
    (['  AddCase(VectorVopcCompareLtU64OnGpu);'],
     ['  if (ShaderRecompiler::Decoder::FixB26Enabled()) {',
      '    AddCase(B26ScalarBrevB64);',
      '    AddCase(B26VectorCmpLeU64Wave32);',
      '    AddCase(B26VectorCmpLeU64Wave64);',
      '  }'], 'after'),
    (['  if (argc == 3 && std::strcmp(argv[1], "--b26-pass") == 0) {'], MODE, 'before'),
    (['  int failures = 0;', '  size_t unsupported_total = 0;'],
     ['  std::printf("B26Pass: fix_b26=%d\\n",',
      '              Libs::Graphics::ShaderRecompiler::Decoder::FixB26Enabled() ? 1 : 0);',
      '  int failures = 0;', '  size_t unsupported_total = 0;'], 'replace'),
])
