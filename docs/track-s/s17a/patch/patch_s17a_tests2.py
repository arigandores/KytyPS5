"""S17a (HPP-611): shader_cfg_tests - TestShaderReplayCanonicalPath: recording, canonicalization with self-check and the
synthetic runtime of the rebuild on two shaders of this file (descriptors inline in user data; a pointer in user data to a
host table holding a V#). LF in, LF out."""
P = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
t = open(P, 'rb').read().decode('utf-8')
assert '\r' not in t

anchor = '''  // The knob is off by default (the test runs without KYTY_S_REPLAY).
  if (std::getenv("KYTY_S_REPLAY") == nullptr) {
    Check(SR::Mode() == 0 && !SR::CaptureOn() && !SR::RebuildOn(), "replay knob default 0");
  }
}
'''
assert t.count(anchor) == 1
block = r'''
// One read path: record it through `live`, canonicalize it, check every word is canonical, replay the canonical path
// through the synthetic runtime of the rebuild (same specialization), and check a shortened path diverges.
std::vector<ShaderReplay::Word> ReplayRoundTrip(const ShaderRecompiler::IR::ResourcePlan &plan,
                                                const ShaderRecompiler::IR::SrtRuntime &live, size_t &user_words,
                                                const char *what) {
  namespace SR = ShaderReplay;
  SR::Trace trace;
  SR::Recorder recorder{.inner = &live, .trace = &trace};
  ShaderRecompiler::IR::ResourceSnapshot snapshot;
  ShaderRecompiler::IR::ResourceSpecialization live_specialization;
  Check(ShaderRecompiler::IR::MaterializeResources(plan, recorder.Runtime(), snapshot, live_specialization),
        "replay recording materialization failed");
  std::vector<SR::Word> words;
  std::string why;
  const bool canonical = SR::Canonicalize(plan, trace, live_specialization, words, user_words, why, false);
  std::fprintf(stderr, "[replay] %s: words=%zu user=%zu reads=%zu canonical=%d why=%s\n", what, words.size(),
               user_words, trace.reads.size(), canonical ? 1 : 0, why.c_str());
  Check(canonical, "replay canonicalization failed");
  Check(std::ranges::all_of(words, [](const SR::Word &w) { return SR::WordCanonical(w); }),
        "replay canonical path holds a non-canonical address word");
  SR::Catalogue::Spec record;
  record.header.user_words = static_cast<uint32_t>(user_words);
  record.words = words;
  ShaderRecompiler::IR::ResourceSpecialization again;
  Check(SR::Specialize(plan, record, again) && again == live_specialization,
        "replay of the canonical path did not give the live specialization");
  if (record.words.size() > 2u + user_words) {
    auto shorter = record;
    shorter.words.pop_back();
    Check(!SR::Specialize(plan, shorter, again), "replay of a shortened path did not diverge");
  }
  return words;
}

void TestShaderReplayCanonicalPath() {
  namespace SR = ShaderReplay;
  namespace IR = ShaderRecompiler::IR;
  // (1) Descriptors inline in user data (ImageTestUserData: T# bases 0x1000 + 0x100 * start), memory reads answer 0.
  {
    const uint32_t shader[] = {
        EncodeSmem0(0x00, 0, 4), 0u,                    // s_load_dword s0
        EncodeSmem0(0x08, 1, 4), 0u,                    // s_buffer_load_dword s1
        EncodeMubuf0(0x0c, 4),   EncodeMubuf1(0, 0, 1), // buffer_load_dword v0
        EncodeMimg0(0x00, 0xf),  EncodeMimg1(4, 0, 0, 1), // image_load v4
        EncodeMimg0(0x20, 0xf),  EncodeMimg1(3, 0, 0, 1), // image_sample v3
        0xbf810000u,
    };
    auto user_data = ImageTestUserData();
    auto options = MakeCompileOptions(ShaderType::Compute);
    options.dump_ir = false;
    options.user_data = user_data;
    auto translated = ShaderRecompiler::TranslateProgram(shader, options);
    const auto plan = IR::ExtractResourcePlan(translated.program);
    const IR::SrtRuntime live{.user_data = options.user_data,
                              .shader_base = reinterpret_cast<uint64_t>(shader),
                              .read_memory = ReadZeroTestMemory,
                              .userdata = nullptr,
                              .read_specialization_memory = ReadZeroTestMemory};
    size_t user_words = 0;
    const auto words = ReplayRoundTrip(plan, live, user_words, "inline descriptors");
    const auto count = [&words](uint8_t role) {
      return std::ranges::count_if(words, [role](const SR::Word &w) { return w.role == role; });
    };
    Check(count(SR::ROLE_T_LO) >= 1 && count(SR::ROLE_T_HI) >= 1, "replay found no T# base word in user data");
    for (size_t i = 0; i < user_words; i++) {
      const auto &w = words[2 + i];
      if (w.role == SR::ROLE_T_LO) {
        Check(w.value == 1u && user_data[i] != 0u, "replay T# base not canonical (non-null -> 1)");
      }
    }
  }
  // (2) A pointer in user data (s[28:29]) to a host table holding a V# at 0x50 (base 0x2000) and one at 0x60.
  {
    const uint32_t shader[] = {
        EncodeSmem0(0x02, 32, 14), (125u << 25u) | 0x60u,
        EncodeSopc(0x06, 0, 128),
        EncodeSopp(0x04, 10),
        EncodeSmem0(0x02, 32, 14), (125u << 25u) | 0x50u,
        EncodeSopc(0x06, 1, 128),
        EncodeSopp(0x04, 6),
        EncodeSmem0(0x08, 56, 16), 125u << 25u,
        EncodeVop1(0x01, 0, 56),
        EncodeExp0(0x00, 0x1), EncodeExp1(0, 0, 0, 0),
        EncodeSopp(0x01),
        EncodeSopp(0x01),
    };
    std::array<uint32_t, 28> table{};
    table[0x50u / 4u] = 0x2000u;
    table[0x50u / 4u + 2u] = 4u;
    table[0x60u / 4u] = 0x3000u;
    table[0x60u / 4u + 2u] = 4u;
    std::array<uint32_t, 32> user_data{};
    const auto address = reinterpret_cast<uint64_t>(table.data());
    user_data[28] = static_cast<uint32_t>(address);
    user_data[29] = static_cast<uint32_t>(address >> 32u);
    auto options = MakeCompileOptions(ShaderType::Pixel);
    options.dump_ir = false;
    options.user_data = user_data;
    auto translated = ShaderRecompiler::TranslateProgram(shader, options);
    const auto plan = IR::ExtractResourcePlan(translated.program);
    const IR::SrtRuntime live{.user_data = options.user_data,
                              .shader_base = reinterpret_cast<uint64_t>(shader),
                              .read_memory = ReadHostTestMemory,
                              .userdata = nullptr,
                              .read_specialization_memory = ReadHostTestMemory};
    size_t user_words = 0;
    const auto words = ReplayRoundTrip(plan, live, user_words, "pointer to a V# table");
    Check(user_words == user_data.size() && words[2 + 28].role == SR::ROLE_PTR_LO &&
              words[2 + 29].role == SR::ROLE_PTR_HI,
          "replay did not classify the user data pointer as PTR_LO / PTR_HI");
    Check(std::ranges::none_of(words, [address](const SR::Word &w) {
            return w.value == static_cast<uint32_t>(address) || w.value == 0x2000u;
          }),
          "replay kept a host address or a V# base");
    Check(std::ranges::count_if(words, [](const SR::Word &w) { return w.role == SR::ROLE_V_LO; }) >= 1,
          "replay found no V# base word in the table");
  }
}
'''
t = t.replace(anchor, anchor + block)
run = '  RUN(TestShaderReplayFormat);\n'
assert t.count(run) == 1
t = t.replace(run, run + '  RUN(TestShaderReplayCanonicalPath);\n')
open(P, 'wb').write(t.encode('utf-8'))
print('tests2 patched OK')
