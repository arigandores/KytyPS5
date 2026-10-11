// Track F, F42a (HPP-779, ROADMAP s122 item 694(g)(1), (v)(6); RC5 of F41b): the GPU stand of row F20 (--f20-stand).
// A guest program translated by the real translator (the null-page BDA mode of the game: one FLAT load of a page that
// is not in the page table, the fault written by RecordBdaFault on the return of main) is dispatched R times per arm;
// after every dispatch the whole fault bitmap (m_fault_buffer, zeroed by Dispatch before the dispatch) is read back
// (ReadFaultBuffer) and compared with the bitmap computed on the CPU from the page formula of the arm - one bit per
// invocation, gid = (group_y * 32768 + group_x) * 64 + local_x, page = F20PageBase + rel(gid):
//   W - the 32 lanes of one subgroup write 32 different bits of one word        rel = gid
//   X - 32 subgroups write one word, every lane of a subgroup the same bit      rel = gid >> 5
//   S - one lane per word                                                       rel = gid << 5 | gid & 31
//   N - the module of W with every OpName / OpMemberName removed (detector of a fault buffer without its name).
// At KYTY_FIX_F20=1 (Common::EnvFlagOn - the parse of FixF20::Mode) the module of every arm goes through
// Libs::Graphics::FixF20::RewriteFaultOr - the function the emulator calls (fixF20.h) - with the FaultBuffer binding of
// the compiled program; at 0 the translator's words are dispatched (the statistics are computed for the form line
// only). Form (item 694(v)(6)): wave 32 on a 32-lane host subgroup (lane_count 1 by the rule of SpirvEmitter.cpp -
// no other_half), LocalSize 64, the triples = OpReturn of main. Every module is written to <out>.<arm>.spv.
// KYTY_TEST_F20STAND_OUT=<tsv> (required), KYTY_TEST_F20STAND_R (default 200), KYTY_TEST_F20STAND_SEED (default 1:
// the order of the four arms in every round).
constexpr u32 F20PageBase = 0x44000u; // guest address 0x110000000, word 8704 of the bitmap
constexpr u32 F20Words = 4096u;

enum class F20Arm : u32 { W, X, S, N };

const char *F20ArmName(F20Arm arm) {
  switch (arm) {
  case F20Arm::W: return "W";
  case F20Arm::X: return "X";
  case F20Arm::S: return "S";
  case F20Arm::N: return "N";
  }
  return "?";
}

u32 F20Invocations(F20Arm arm) {
  return arm == F20Arm::X ? F20Words * 32u * 32u : arm == F20Arm::S ? F20Words : F20Words * 32u;
}

u32 F20RelativePage(F20Arm arm, u32 gid) {
  switch (arm) {
  case F20Arm::X: return gid >> 5u;
  case F20Arm::S: return (gid << 5u) | (gid & 31u);
  default: return gid;
  }
}

TestCase F20StandCase(F20Arm arm) {
  using O = ShaderOpcode;
  const bool x = arm == F20Arm::X;
  const bool s = arm == F20Arm::S;
  std::vector<u32> code;
  code.push_back(EncodeVop1(0x01, 1, 4));                // v1 = s4 (group x)
  code.push_back(EncodeVop1(0x01, 6, 5));                // v6 = s5 (group y)
  code.push_back(EncodeVop2(0x1a, 6, InlineU32(15), 6)); // v6 = v6 << 15
  code.push_back(EncodeVop2(0x25, 1, Vgpr(6), 1));       // v1 = group x + group y * 32768
  code.push_back(EncodeVop2(0x1a, 1, InlineU32(6), 1));  // v1 = v1 << 6
  code.push_back(EncodeVop2(0x25, 1, Vgpr(0), 1));       // v1 = gid
  if (x) {
    code.push_back(EncodeVop2(0x16, 2, InlineU32(5), 1)); // v2 = gid >> 5
  } else if (s) {
    code.push_back(EncodeVop2(0x1b, 3, InlineU32(31), 1)); // v3 = gid & 31
    code.push_back(EncodeVop2(0x1a, 2, InlineU32(5), 1));  // v2 = gid << 5
    code.push_back(EncodeVop2(0x1c, 2, Vgpr(3), 2));       // v2 = v2 | v3
  } else {
    code.push_back(EncodeVop1(0x01, 2, Vgpr(1))); // v2 = gid
  }
  AppendVMovLiteral(&code, 4, F20PageBase);
  code.push_back(EncodeVop2(0x25, 2, Vgpr(4), 2));       // v2 = page
  code.push_back(EncodeVop2(0x1a, 20, InlineU32(14), 2)); // v20 = page << 14 (address, low dword)
  code.push_back(EncodeVop2(0x16, 21, InlineU32(18), 2)); // v21 = page >> 18 (address, high dword)
  code.push_back(EncodeFlat0(0x0c, 0, 0));               // FLAT_LOAD_DWORD v5, v[20:21]
  code.push_back(EncodeFlat1(5, 0x7d, 0, 20));
  AppendStoreVgprAtLaneDwordOffset(&code, 5, 0, 0); // out[local x] = v5 (the null page: 0)
  AppendEnd(&code);

  TestCase test;
  test.name = arm == F20Arm::X ? "F20StandX" : arm == F20Arm::S ? "F20StandS" : arm == F20Arm::N ? "F20StandN" : "F20StandW";
  test.code = std::move(code);
  test.initial = std::vector<u32>(64, 0u);
  test.expected = std::vector<u32>(64, 0u);
  test.bda_mappings = {{0, 0}};
  test.opcodes = {O::V_MOV_B32, O::V_LSHLREV_B32, O::V_ADD_NC_U32, O::FLAT_LOAD_DWORD, O::BUFFER_STORE_DWORD,
                  O::S_ENDPGM};
  if (s) {
    test.opcodes.push_back(O::V_AND_B32);
    test.opcodes.push_back(O::V_OR_B32);
  }
  test.opcodes.push_back(O::V_LSHRREV_B32);
  test.compute_info.threads_num[0] = 64;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.compute_info.group_id[0] = true;
  test.compute_info.group_id[1] = true;
  test.compute_info.wave_size = 32;
  test.compute_info.thread_ids_num = 1;
  test.compute_info.workgroup_register = 4;
  test.has_compute_info = true;
  const u32 groups = F20Invocations(arm) / 64u;
  test.dispatch_x = x ? 32768u : groups;
  test.dispatch_y = x ? groups / 32768u : 1u;
  return test;
}

std::vector<u32> F20StripNames(const std::vector<u32> &in) {
  std::vector<u32> out(in.begin(), in.begin() + 5);
  for (size_t i = 5; i < in.size();) {
    const u32 count = in[i] >> 16u;
    const u32 op = in[i] & 0xffffu;
    Require("F20Stand", "strip names", count != 0 && count <= in.size() - i, "malformed SPIR-V");
    if (op != 5u && op != 6u) {
      out.insert(out.end(), in.begin() + static_cast<std::ptrdiff_t>(i),
                 in.begin() + static_cast<std::ptrdiff_t>(i + count));
    }
    i += count;
  }
  return out;
}

struct F20Form {
  u32 local_x = 0;
  u32 local_y = 0;
  u32 local_z = 0;
  u32 returns_main = 0;
  u32 functions = 0;
};

// LocalSize of the entry point and the OpReturn of its function (main).
F20Form F20ReadForm(const std::vector<u32> &w) {
  F20Form form;
  u32 entry = 0;
  u32 current = 0;
  for (size_t i = 5; i < w.size();) {
    const u32 count = w[i] >> 16u;
    const u32 op = w[i] & 0xffffu;
    Require("F20Stand", "form", count != 0 && count <= w.size() - i, "malformed SPIR-V");
    if (op == 15u && count >= 3) { // OpEntryPoint
      entry = w[i + 2];
    } else if (op == 16u && count >= 6 && w[i + 2] == 17u) { // OpExecutionMode LocalSize
      form.local_x = w[i + 3];
      form.local_y = w[i + 4];
      form.local_z = w[i + 5];
    } else if (op == 54u && count >= 3) { // OpFunction
      current = w[i + 2];
      form.functions++;
    } else if (op == 253u && current == entry && entry != 0) { // OpReturn in main
      form.returns_main++;
    }
    i += count;
  }
  return form;
}

bool F20Validate(const std::vector<u32> &spirv, std::string *messages) {
  spvtools::SpirvTools tools(SPV_ENV_VULKAN_1_2);
  tools.SetMessageConsumer([messages](spv_message_level_t, const char *, const spv_position_t &,
                                      const char *message) { *messages += message; });
  return tools.Validate(spirv);
}

int F20StandMain() {
  const char *out_path = std::getenv("KYTY_TEST_F20STAND_OUT");
  if (out_path == nullptr || out_path[0] == 0) {
    std::fprintf(stderr, "--f20-stand needs KYTY_TEST_F20STAND_OUT=<tsv>\n");
    return 2;
  }
  const bool fix = Common::EnvFlagOn("KYTY_FIX_F20");
  const char *r_text = std::getenv("KYTY_TEST_F20STAND_R");
  const char *seed_text = std::getenv("KYTY_TEST_F20STAND_SEED");
  const u32 rounds = r_text != nullptr ? static_cast<u32>(std::strtoul(r_text, nullptr, 10)) : 200u;
  const u32 seed = seed_text != nullptr ? static_cast<u32>(std::strtoul(seed_text, nullptr, 10)) : 1u;
  VulkanHarness vulkan;
  const u32 subgroup = vulkan.SubgroupSize();

  struct ArmData {
    F20Arm arm = F20Arm::W;
    TestCase test;
    CompiledShader compiled;
    Libs::Graphics::FixF20::RewriteStats stats;
    bool bound = false;
    bool valid = false;
    std::string val_messages;
    F20Form form;
    std::vector<u32> expected;
    uint64_t expected_bits = 0;
    uint64_t lost = 0;
    uint64_t extra = 0;
    uint64_t words_lost = 0;
    uint64_t out_nonzero = 0;
    u32 rounds_with_loss = 0;
  };
  std::array<ArmData, 4> arms;
  for (u32 a = 0; a < 4u; a++) {
    auto &d = arms[a];
    d.arm = static_cast<F20Arm>(a);
    d.test = F20StandCase(d.arm);
    d.compiled = CompileCase(d.test, subgroup);
    auto words = d.compiled.spirv;
    if (d.arm == F20Arm::N) {
      words = F20StripNames(words);
    }
    d.bound = std::ranges::any_of(d.compiled.program.bindings.descriptors, [](const auto &b) {
      return b.kind == ShaderRecompiler::IR::DescriptorBindingKind::FaultBuffer;
    });
    std::vector<u32> fixed;
    d.stats = Libs::Graphics::FixF20::RewriteFaultOr(words, d.bound, fixed);
    if (fix && d.stats.rewritten != 0) {
      words = fixed;
    }
    d.form = F20ReadForm(words);
    d.valid = F20Validate(words, &d.val_messages);
    const auto spv_path = std::string(out_path) + "." + F20ArmName(d.arm) + ".spv";
    if (FILE *file = std::fopen(spv_path.c_str(), "wb"); file != nullptr) {
      std::fwrite(words.data(), sizeof(u32), words.size(), file);
      std::fclose(file);
    }
    d.compiled.spirv = std::move(words);
    d.expected.assign(F20Words, 0u);
    for (u32 gid = 0; gid < F20Invocations(d.arm); gid++) {
      const u32 rel = F20RelativePage(d.arm, gid);
      d.expected[rel >> 5u] |= 1u << (rel & 31u);
    }
    for (const u32 word : d.expected) {
      d.expected_bits += static_cast<uint64_t>(std::popcount(word));
    }
    const u32 lane_count = d.compiled.program.wave_size == 64u && subgroup == 32u ? 2u : 1u;
    std::printf("F20Stand: form mode=%d arm=%s wave=%u subgroup=%u lane_count=%u local=%ux%ux%u functions=%u "
                "returns_main=%u bound=%d named=%u sites=%u rewritten=%u unmatched=%u malformed=%d valid=%d "
                "groups=%ux%u invocations=%u expected_bits=%llu words=%zu\n",
                fix ? 1 : 0, F20ArmName(d.arm), d.compiled.program.wave_size, subgroup, lane_count, d.form.local_x,
                d.form.local_y, d.form.local_z, d.form.functions, d.form.returns_main, d.bound ? 1 : 0,
                d.stats.named, d.stats.sites, d.stats.rewritten, d.stats.unmatched, d.stats.malformed ? 1 : 0,
                d.valid ? 1 : 0, d.test.dispatch_x, d.test.dispatch_y, F20Invocations(d.arm),
                static_cast<unsigned long long>(d.expected_bits), d.compiled.spirv.size());
    if (!d.valid) {
      std::printf("F20Stand: validation arm=%s %s\n", F20ArmName(d.arm), d.val_messages.c_str());
    }
  }

  FILE *tsv = std::fopen(out_path, "wb");
  if (tsv == nullptr) {
    std::fprintf(stderr, "F20Stand: cannot write %s\n", out_path);
    return 2;
  }
  std::fprintf(tsv, "mode\tseed\tround\tposition\tarm\texpected_bits\tseen_bits\tlost\textra\twords_lost\tout_nonzero\n");
  uint32_t state = seed * 2654435761u + 1u;
  const auto next = [&state]() {
    state ^= state << 13u;
    state ^= state >> 17u;
    state ^= state << 5u;
    return state;
  };
  constexpr u32 base_word = F20PageBase / 32u;
  for (u32 r = 0; r < rounds; r++) {
    std::array<u32, 4> order{0, 1, 2, 3};
    for (u32 i = 3; i > 0; i--) {
      std::swap(order[i], order[next() % (i + 1u)]);
    }
    for (u32 position = 0; position < 4u; position++) {
      auto &d = arms[order[position]];
      auto buffer = vulkan.CreateStorageBuffer(d.test.name, d.test.initial, 64u, true);
      vulkan.Dispatch(d.test, d.compiled, buffer);
      const auto out = vulkan.ReadBuffer(d.test.name, buffer, 64u);
      vulkan.DestroyBuffer(&buffer);
      const auto map = vulkan.ReadFaultBuffer(d.test.name);
      uint64_t seen = 0;
      uint64_t extra = 0;
      uint64_t words_lost = 0;
      for (size_t i = 0; i < map.size(); i++) {
        const u32 expected = i >= base_word && i < base_word + F20Words ? d.expected[i - base_word] : 0u;
        seen += static_cast<uint64_t>(std::popcount(map[i] & expected));
        extra += static_cast<uint64_t>(std::popcount(map[i] & ~expected));
        words_lost += (expected & ~map[i]) != 0u ? 1u : 0u;
      }
      const uint64_t out_nonzero = static_cast<uint64_t>(std::ranges::count_if(out, [](u32 v) { return v != 0u; }));
      const uint64_t lost = d.expected_bits - seen;
      d.lost += lost;
      d.extra += extra;
      d.words_lost += words_lost;
      d.out_nonzero += out_nonzero;
      d.rounds_with_loss += lost != 0 ? 1u : 0u;
      std::fprintf(tsv, "%d\t%u\t%u\t%u\t%s\t%llu\t%llu\t%llu\t%llu\t%llu\t%llu\n", fix ? 1 : 0, seed, r, position,
                   F20ArmName(d.arm), static_cast<unsigned long long>(d.expected_bits),
                   static_cast<unsigned long long>(seen), static_cast<unsigned long long>(lost),
                   static_cast<unsigned long long>(extra), static_cast<unsigned long long>(words_lost),
                   static_cast<unsigned long long>(out_nonzero));
    }
  }
  std::fclose(tsv);
  for (const auto &d : arms) {
    std::printf("F20Stand: sum mode=%d seed=%u arm=%s rounds=%u expected_bits=%llu lost=%llu rounds_with_loss=%u "
                "extra=%llu words_lost=%llu out_nonzero=%llu\n",
                fix ? 1 : 0, seed, F20ArmName(d.arm), rounds,
                static_cast<unsigned long long>(d.expected_bits * rounds), static_cast<unsigned long long>(d.lost),
                d.rounds_with_loss, static_cast<unsigned long long>(d.extra),
                static_cast<unsigned long long>(d.words_lost), static_cast<unsigned long long>(d.out_nonzero));
  }
  std::printf("F20Stand: done\n");
  return 0;
}

