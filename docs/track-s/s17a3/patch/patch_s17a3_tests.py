"""S17a3 (HPP-620, ROADMAP s122 item 537(g)(1), (3)): tests of the role classifier of S-replay.
Adds TestShaderReplayWalkBits to tests/shaderCfgTests.cpp and its RUN line. Anchors are whole lines; LF in, LF out.
Usage: python patch_s17a3_tests.py <repository root>"""
import sys

root = sys.argv[1].rstrip('/\\')
path = root + '/tests/shaderCfgTests.cpp'
data = open(path, 'rb').read()
crlf = b'\r\n' in data
text = data.decode('utf-8').replace('\r\n', '\n')
lines = text.split('\n')


def find_line(anchor, start=0):
    hits = [i for i in range(start, len(lines)) if lines[i] == anchor]
    if len(hits) != 1:
        sys.exit('anchor %r: %d hits' % (anchor, len(hits)))
    return hits[0]


ANCHOR_PROBE = '// Track S, S16d (HPP-608, ROADMAP s122 item 516(v)): probe P-S16 of S-replay (tests/S16dProbe.inc).'
ANCHOR_RUN = '  RUN(TestShaderReplayCanonicalPath);'
if any(l == '  RUN(TestShaderReplayWalkBits);' for l in lines):
    sys.exit('already applied')

NEW = r'''// Track S, S17a3 (HPP-620, ROADMAP s122 item 537(g)): the role classifier of S-replay against a walk that depends on
// bits of a word outside the two perturbations (bit 8, bit 0) - the form of the canon_self rejects of the s17c_c2 tag.
namespace Libs::Graphics {
namespace {

// The raw path of a trace (all words ROLE_KEEP), the form Canonicalize builds.
std::vector<ShaderReplay::Word> ReplayRawPath(const ShaderReplay::Trace &trace) {
  namespace SR = ShaderReplay;
  std::vector<SR::Word> raw;
  raw.push_back({static_cast<uint32_t>(trace.shader_base), SR::ROLE_KEEP, SR::WORD_BASE | SR::WORD_OK});
  raw.push_back({static_cast<uint32_t>(trace.shader_base >> 32u), SR::ROLE_KEEP, SR::WORD_BASE | SR::WORD_OK});
  for (const auto value : trace.user_data) {
    raw.push_back({value, SR::ROLE_KEEP, SR::WORD_USER | SR::WORD_OK});
  }
  for (const auto &read : trace.reads) {
    raw.push_back({read.value, SR::ROLE_KEEP,
                   static_cast<uint8_t>((read.clean != 0 ? SR::WORD_CLEAN : 0) | (read.ok != 0 ? SR::WORD_OK : 0))});
  }
  return raw;
}

bool ReplayRecord(const ShaderRecompiler::IR::ResourcePlan &plan, const ShaderRecompiler::IR::SrtRuntime &live,
                  ShaderReplay::Trace &trace, ShaderRecompiler::IR::ResourceSpecialization &specialization) {
  trace = {};
  ShaderReplay::Recorder recorder{.inner = &live, .trace = &trace};
  ShaderRecompiler::IR::ResourceSnapshot snapshot;
  return ShaderRecompiler::IR::MaterializeResources(plan, recorder.Runtime(), snapshot, specialization);
}

void ReplayPrintRoles(const char *what, const std::vector<ShaderReplay::Word> &words) {
  std::string line;
  for (size_t i = 0; i < words.size(); i++) {
    if (words[i].role != ShaderReplay::ROLE_KEEP && words[i].role != ShaderReplay::ROLE_INERT) {
      line += fmt::format(" {}:{}:{:x}", i, words[i].role, words[i].value);
    }
  }
  std::fprintf(stderr, "[replay] %s: address roles%s\n", what, line.c_str());
}

void TestShaderReplayWalkBits() {
  namespace SR = ShaderReplay;
  namespace IR = ShaderRecompiler::IR;
  // (a) Item 537(g)(1): the compiled walk evaluates every node, a bounds-checked scalar buffer read
  // (s_buffer_load) included, and skips the read (no reader call) when its offset is past the V# size; a read with a
  // register offset is not a flat slot, and the source it feeds is under a branch the draw does not take, so the walk
  // still succeeds (ok=1). The V# C of the table (offset 0x50) holds num_records = W; the V# D is read from C at the
  // offset s12 = 0x200 (4 reads in bounds while W >= 0x210). W = 0x45f, 0x55f (bit 8), 0x45e (bit 0): the same reads -
  // the classifier sees W as INERT; W = 0x10f (the INERT canonical form 0x100 | (W & 0xF), bits 4, 6, 8, 10 flipped):
  // the 4 reads of D are skipped and the recorded path is not consumed - before S17a3 the self-check rejects the record
  // (self ok=1 complete=0, culprit=<W>:role1:0000045f->0000010f, the form of the s17c_c2 rejects); after S17a3 W is
  // kept as read (ROLE_KEEP).
  [&] {
    const uint32_t shader[] = {
        EncodeSmem0(0x02, 4, 14), (125u << 25u) | 0x50u, // s_load_dwordx4 s[4:7], s[28:29], 0x50 (V# C)
        EncodeSopc(0x06, 0, 128),                         // s_cmp_eq_u32 s0, 0 (s0 = 1: the block is not taken)
        EncodeSopp(0x04, 4),                              // s_cbranch_scc0 +4
        EncodeSmem0(0x0a, 8, 2), 12u << 25u,              // s_buffer_load_dwordx4 s[8:11], s[4:7], s12 (V# D)
        EncodeMubuf0(0x0c), EncodeMubuf1(1, 2, 0),        // buffer_load_dword v1, v0, s[8:11]
        EncodeExp0(0x00, 0x1), EncodeExp1(1, 0, 0, 0),
        EncodeSopp(0x01),
    };
    std::array<uint32_t, 0xd0> table{};
    const auto address = reinterpret_cast<uint64_t>(table.data());
    table[0x50u / 4u] = static_cast<uint32_t>(address + 0x100u);
    table[0x50u / 4u + 1u] = static_cast<uint32_t>((address + 0x100u) >> 32u) & 0xffffu;
    table[0x50u / 4u + 2u] = 0x45fu;
    table[0x300u / 4u] = 0x2000u;
    table[0x300u / 4u + 2u] = 4u;
    std::array<uint32_t, 32> user_data{};
    user_data[0] = 1u;
    user_data[12] = 0x200u;
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
    SR::Trace trace;
    IR::ResourceSpecialization live_specialization;
    Check(ReplayRecord(plan, live, trace, live_specialization), "replay walk bits: recording failed");
    const auto raw = ReplayRawPath(trace);
    size_t w_index = raw.size();
    for (size_t r = 0; r < trace.reads.size(); r++) {
      if (trace.reads[r].address == address + 0x58u) {
        w_index = 2 + trace.user_data.size() + r;
      }
    }
    Check(w_index < raw.size() && raw[w_index].value == 0x45fu, "replay walk bits: W not on the path");
    if (w_index >= raw.size()) {
      return;
    }
    // The premise of the reproduction: the recorded walk is complete with W = 0x45f, 0x55f, 0x45e and not with 0x10f.
    const uint32_t values[4] = {0x45fu, 0x55fu, 0x45eu, 0x10fu};
    bool complete[4] = {};
    for (int k = 0; k < 4; k++) {
      SR::Catalogue::Spec spec;
      spec.header.user_words = static_cast<uint32_t>(trace.user_data.size());
      spec.words = raw;
      spec.words[w_index].value = values[k];
      IR::ResourceSpecialization again;
      complete[k] = SR::Specialize(plan, spec, again) && again == live_specialization;
    }
    std::fprintf(stderr, "[replay] walk bits: reads=%zu w=%zu complete 45f=%d 55f=%d 45e=%d 10f=%d\n",
                 trace.reads.size(), w_index, complete[0] ? 1 : 0, complete[1] ? 1 : 0, complete[2] ? 1 : 0,
                 complete[3] ? 1 : 0);
    Check(complete[0] && complete[1] && complete[2] && !complete[3],
          "replay walk bits: premise (complete at 0x45f, 0x55f, 0x45e, not at 0x10f) does not hold");
    std::vector<SR::Word> words;
    size_t user_words = 0;
    std::string why;
    const bool canonical = SR::Canonicalize(plan, trace, live_specialization, words, user_words, why, false);
    std::fprintf(stderr, "[replay] walk bits: canonical=%d why=%s\n", canonical ? 1 : 0, why.c_str());
    Check(canonical, "replay walk bits: the record is rejected (canon_self of s17c_c2 reproduced)");
    if (!canonical) {
      return;
    }
    ReplayPrintRoles("walk bits", words);
    Check(words[w_index].role == SR::ROLE_KEEP && words[w_index].value == 0x45fu,
          "replay walk bits: W is not kept as read");
    Check(words[2 + 28].role == SR::ROLE_PTR_LO && words[2 + 29].role == SR::ROLE_PTR_HI &&
              words[2 + 28].value != user_data[28],
          "replay walk bits: the pointer words lost their roles");
    Check(std::ranges::all_of(words, [](const SR::Word &w) { return SR::WordCanonical(w); }),
          "replay walk bits: a non-canonical address word");
    SR::Catalogue::Spec record;
    record.header.user_words = static_cast<uint32_t>(user_words);
    record.words = words;
    IR::ResourceSpecialization again;
    Check(SR::Specialize(plan, record, again) && again == live_specialization,
          "replay walk bits: the canonical path did not give the live specialization");
    // (d) Item 537(g)(3): the rule of the offline scanner R_ADDR (WordCanonical) on this record - 0 non-canonical
    // words on the canonical path (R_ADDR = 0); the record with every value as read (the addr stand of HandleSpec,
    // roles kept) has the pointer words non-canonical (stand addr > 0).
    auto stand = words;
    for (size_t i = 0; i < stand.size(); i++) {
      stand[i].value = raw[i].value;
    }
    const auto r_addr = std::ranges::count_if(words, [](const SR::Word &w) { return !SR::WordCanonical(w); });
    const auto r_stand = std::ranges::count_if(stand, [](const SR::Word &w) { return !SR::WordCanonical(w); });
    std::fprintf(stderr, "[replay] walk bits: r_addr=%td stand_addr=%td\n", r_addr, r_stand);
    Check(r_addr == 0 && r_stand > 0, "replay walk bits: scanner rule (R_ADDR 0, stand addr > 0) does not hold");
  }();
  // (b) Item 537(g)(3): an address word whose canonical substitution changes the walk must not reach the catalogue as
  // read. The V# C is built from the user data pointer: base s[28:29] and num_records = s28 (the pointer low word);
  // the V# D is read from C at offset 0x200 under a branch not taken. Bits 8 and 0 of s28 move the requests by 0x100
  // and 1 (an address role), the canonical 0x100 | (v & 0xF) makes the reads of D past the size and skips them. No
  // request is at offset 0 (the exact-value residual check alone does not see s28); after S17a3 the record is rejected
  // as residual, before S17a3 it is rejected by the self-check.
  {
    const uint32_t shader[] = {
        EncodeSMovB32(4, 28),                            // s_mov_b32 s4, s28 (C base low)
        EncodeSMovB32(5, 29),                            // s_mov_b32 s5, s29 (C base high, stride 0)
        EncodeSMovB32(6, 28),                            // s_mov_b32 s6, s28 (C num_records = the pointer low word)
        EncodeSMovB32(7, 128),                           // s_mov_b32 s7, 0
        EncodeSopc(0x06, 0, 128),                        // s_cmp_eq_u32 s0, 0 (s0 = 1: the block is not taken)
        EncodeSopp(0x04, 4),                             // s_cbranch_scc0 +4
        EncodeSmem0(0x0a, 8, 2), (125u << 25u) | 0x200u, // s_buffer_load_dwordx4 s[8:11], s[4:7], 0x200 (V# D)
        EncodeMubuf0(0x0c), EncodeMubuf1(1, 2, 0),       // buffer_load_dword v1, v0, s[8:11]
        EncodeExp0(0x00, 0x1), EncodeExp1(1, 0, 0, 0),
        EncodeSopp(0x01),
    };
    std::vector<uint32_t> memory(0x20000u / 4u + 0x100u, 0u);
    auto address = (reinterpret_cast<uint64_t>(memory.data()) + 15u) & ~uint64_t{15u};
    if (static_cast<uint32_t>(address) < 0x10000u) {
      address += 0x10000u;
    }
    auto *table = reinterpret_cast<uint32_t *>(address);
    table[0x200u / 4u] = 0x2000u;
    table[0x200u / 4u + 2u] = 4u;
    std::array<uint32_t, 32> user_data{};
    user_data[0] = 1u;
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
    SR::Trace trace;
    IR::ResourceSpecialization live_specialization;
    Check(ReplayRecord(plan, live, trace, live_specialization), "replay walk address: recording failed");
    bool exact = false;
    for (const auto &read : trace.reads) {
      exact = exact || static_cast<uint32_t>(read.address) == user_data[28];
    }
    std::vector<SR::Word> words;
    size_t user_words = 0;
    std::string why;
    const bool canonical = SR::Canonicalize(plan, trace, live_specialization, words, user_words, why, false);
    std::fprintf(stderr, "[replay] walk address: reads=%zu low=%08x exact=%d canonical=%d why=%s\n",
                 trace.reads.size(), user_data[28], exact ? 1 : 0, canonical ? 1 : 0, why.c_str());
    Check(trace.reads.size() == 4u && !exact, "replay walk address: the fixture does not read D only");
    Check(!canonical && why == "residual",
          "replay walk address: an address word kept as read did not fail the residual check");
  }
  // (c) Item 537(g)(3), item 536(b): the canon stand still spoils a T# base word (ROLE_T_LO, value 1 -> 0) and the
  // self-check rejects the record naming it: culprit=<i>:role6:<raw>->00000000. The shader of TestShaderReplayCanonicalPath
  // (1) with the T# s[0:7] of an integer format: a null T# specializes as Float, the live one as an integer class.
  {
    const uint32_t shader[] = {
        EncodeMubuf0(0x0c),
        EncodeMubuf1(0, 0, 1), // buffer load s[0:3]
        EncodeMubuf0(0x0c),
        EncodeMubuf1(1, 0, 1), // same buffer
        EncodeMubuf0(0x1d),
        EncodeMubuf1(0, 1, 1), // keep both loads live in s[4:7]
        EncodeMimg0(0x20, 0xf),
        EncodeMimg1(8, 0, 2, 1), // sampled image s[0:7], sampler s[8:11]
        EncodeMimg0(0x08, 0xf),
        EncodeMimg1(8, 0, 0, 1), // keep sample live in storage view
        EncodeSopp(0x01),
    };
    auto user_data = ImageTestUserData();
    user_data[7] = 0;
    SetImageTestFormat(&user_data, 0, Prospero::BufferFormat::k32UInt);
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
    SR::Trace trace;
    IR::ResourceSpecialization live_specialization;
    Check(ReplayRecord(plan, live, trace, live_specialization), "replay canon stand: recording failed");
    std::vector<SR::Word> words;
    size_t user_words = 0;
    std::string why;
    const bool clean = SR::Canonicalize(plan, trace, live_specialization, words, user_words, why, false);
    std::fprintf(stderr, "[replay] canon stand: unspoiled canonical=%d why=%s\n", clean ? 1 : 0, why.c_str());
    if (clean) {
      ReplayPrintRoles("canon stand", words);
    }
    Check(clean, "replay canon stand: the unspoiled record is rejected");
    why.clear();
    const bool spoiled = SR::Canonicalize(plan, trace, live_specialization, words, user_words, why, true);
    std::fprintf(stderr, "[replay] canon stand: spoiled canonical=%d why=%s\n", spoiled ? 1 : 0, why.c_str());
    Check(!spoiled && why.starts_with("self ") && Common::ContainsStr(why, ":role6:") &&
              Common::ContainsStr(why, "->00000000"),
          "replay canon stand: no self reject naming culprit role6 ->00000000");
  }
}

} // namespace
} // namespace Libs::Graphics

'''

i = find_line(ANCHOR_PROBE)
lines[i:i] = NEW.split('\n')[:-1]
j = find_line(ANCHOR_RUN)
lines.insert(j + 1, '  RUN(TestShaderReplayWalkBits);')
out = '\n'.join(lines)
if crlf:
    out = out.replace('\n', '\r\n')
open(path, 'wb').write(out.encode('utf-8'))
print('patched', path, 'probe anchor line', i + 1, 'run line', j + 2)
