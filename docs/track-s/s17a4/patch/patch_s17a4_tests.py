# S17a4 (HPP-622, ROADMAP s122 item 541(c)(5)): fixtures of TestShaderReplayWalkBits - branch addr (culprit=30:role2),
# branch exact, the residual counter by prefix and the own limit of residual lines. Anchors are whole lines; CRLF kept.
import sys

PATH = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
NL = chr(10)

data = open(PATH, 'rb').read().decode('utf-8')
crlf = chr(13) + NL in data
text = data.replace(chr(13), '')


def replace_block(text, old_lines, new_lines, what):
    old = NL.join(old_lines) + NL
    new = NL.join(new_lines) + NL
    n = text.count(old)
    if n != 1:
        print('ANCHOR FAIL', what, n)
        sys.exit(1)
    i = text.find(old)
    if i != 0 and text[i - 1] != NL:
        print('ANCHOR NOT LINE START', what)
        sys.exit(1)
    return text.replace(old, new)


SHADER_A = [
    '    const uint32_t shader[] = {',
    '        EncodeSmem0(0x02, 4, 14), (125u << 25u) | 0x50u, // s_load_dwordx4 s[4:7], s[28:29], 0x50 (V# C)',
    '        EncodeSopc(0x06, 0, 128),                         // s_cmp_eq_u32 s0, 0 (s0 = 1: the block is not taken)',
    '        EncodeSopp(0x04, 4),                              // s_cbranch_scc0 +4',
    '        EncodeSmem0(0x0a, 8, 2), 12u << 25u,              // s_buffer_load_dwordx4 s[8:11], s[4:7], s12 (V# D)',
    '        EncodeMubuf0(0x0c), EncodeMubuf1(1, 2, 0),        // buffer_load_dword v1, v0, s[8:11]',
    '        EncodeExp0(0x00, 0x1), EncodeExp1(1, 0, 0, 0),',
    '        EncodeSopp(0x01),',
    '    };',
]

text = replace_block(text, [
    '    Check(!canonical && why == "residual",',
    '          "replay walk address: an address word kept as read did not fail the residual check");',
    '  }',
], [
    '    // S17a4 (item 541(c)(1), (5)): the reject names the branch addr, the culprit s28 (word 2 + 28) with the role of the',
    '    // classifier (PTR_LO) and the count; the raw value of the word is not printed.',
    '    char raw_hex[16];',
    '    std::snprintf(raw_hex, sizeof(raw_hex), "%08x", user_data[28]);',
    '    Check(!canonical && why.starts_with("residual branch=addr culprit=30:role2 ") && Common::ContainsStr(why, " n=") &&',
    '              !Common::ContainsStr(why, raw_hex),',
    '          "replay walk address: no residual reject of branch addr naming culprit 30:role2 without the raw value");',
    '  }',
    '  // (b2) S17a4, item 541(c)(5): the exact branch of the residual check. The shader of (a) with W (num_records of the',
    '  // V# C) equal to the lower word of the address of the reads of D (C base + 0x200). W is INERT for the classifier (bits',
    '  // 8 and 0 keep the reads of D in bounds), its canonical 0x100 | (W & 0xF) skips them, so W is kept as read with',
    '  // kept_address 0 (not an address role); the exact-value comparison finds it among the requests: residual',
    '  // branch=exact culprit=<W>:role0 n=1, the raw value not printed.',
    '  {',
] + SHADER_A + [
    '    std::vector<uint32_t> memory(0x20000u / 4u + 0x100u, 0u);',
    '    auto address = (reinterpret_cast<uint64_t>(memory.data()) + 15u) & ~uint64_t{15u};',
    '    if (static_cast<uint32_t>(address + 0x300u) < 0x10000u) {',
    '      address += 0x10000u;',
    '    }',
    '    auto *table = reinterpret_cast<uint32_t *>(address);',
    '    const auto w = static_cast<uint32_t>(address + 0x300u);',
    '    table[0x50u / 4u] = static_cast<uint32_t>(address + 0x100u);',
    '    table[0x50u / 4u + 1u] = static_cast<uint32_t>((address + 0x100u) >> 32u) & 0xffffu;',
    '    table[0x50u / 4u + 2u] = w;',
    '    table[0x300u / 4u] = 0x2000u;',
    '    table[0x300u / 4u + 2u] = 4u;',
    '    std::array<uint32_t, 32> user_data{};',
    '    user_data[0] = 1u;',
    '    user_data[12] = 0x200u;',
    '    user_data[28] = static_cast<uint32_t>(address);',
    '    user_data[29] = static_cast<uint32_t>(address >> 32u);',
    '    auto options = MakeCompileOptions(ShaderType::Pixel);',
    '    options.dump_ir = false;',
    '    options.user_data = user_data;',
    '    auto translated = ShaderRecompiler::TranslateProgram(shader, options);',
    '    const auto plan = IR::ExtractResourcePlan(translated.program);',
    '    const IR::SrtRuntime live{.user_data = options.user_data,',
    '                              .shader_base = reinterpret_cast<uint64_t>(shader),',
    '                              .read_memory = ReadHostTestMemory,',
    '                              .userdata = nullptr,',
    '                              .read_specialization_memory = ReadHostTestMemory};',
    '    SR::Trace trace;',
    '    IR::ResourceSpecialization live_specialization;',
    '    Check(ReplayRecord(plan, live, trace, live_specialization), "replay walk exact: recording failed");',
    '    size_t w_index = 0;',
    '    bool d_read = false;',
    '    for (size_t r = 0; r < trace.reads.size(); r++) {',
    '      if (trace.reads[r].address == address + 0x58u && trace.reads[r].value == w) {',
    '        w_index = 2 + trace.user_data.size() + r;',
    '      }',
    '      d_read = d_read || static_cast<uint32_t>(trace.reads[r].address) == w;',
    '    }',
    '    Check(w_index != 0 && d_read, "replay walk exact: W or the read of D not on the path");',
    '    std::vector<SR::Word> words;',
    '    size_t user_words = 0;',
    '    std::string why;',
    '    const bool canonical = SR::Canonicalize(plan, trace, live_specialization, words, user_words, why, false);',
    '    const std::string expected = "residual branch=exact culprit=" + std::to_string(w_index) + ":role0 n=1";',
    '    char raw_hex[16];',
    '    std::snprintf(raw_hex, sizeof(raw_hex), "%08x", w);',
    '    std::fprintf(stderr, "[replay] walk exact: reads=%zu w=%zu canonical=%d why=%s\\n", trace.reads.size(), w_index,',
    '                 canonical ? 1 : 0, why.c_str());',
    '    Check(!canonical && why == expected && !Common::ContainsStr(why, raw_hex),',
    '          "replay walk exact: no residual reject of branch exact naming W as role0, n=1, without the raw value");',
    '  }',
], 'b check')

text = replace_block(text, [
    '          "replay canon stand: no self reject naming culprit role6 ->00000000");',
    '  }',
    '}',
], [
    '          "replay canon stand: no self reject naming culprit role6 ->00000000");',
    '  }',
    '  // (e) S17a4, item 541(c)(2)-(3): CountReject - a residual reject with its suffix counts in canon_residual (not in',
    '  // canon_big) and in canon_mismatch; residual reject lines have their own limit of 20, the other kinds theirs.',
    '  {',
    '    SR::CaptureStats stats;',
    '    int printed_residual = 0;',
    '    for (int k = 0; k < 25; k++) {',
    '      printed_residual += SR::CountReject(stats, "residual branch=addr culprit=30:role2 n=1") ? 1 : 0;',
    '    }',
    '    const bool self_printed = SR::CountReject(stats, "self ok=1 complete=0");',
    '    const bool exact_printed = SR::CountReject(stats, "residual branch=exact culprit=36:role0 n=2");',
    '    const bool base_printed = SR::CountReject(stats, "base");',
    '    const bool big_printed = SR::CountReject(stats, "big");',
    '    std::fprintf(stderr,',
    '                 "[replay] count reject: residual=%u self=%u base=%u big=%u mismatch=%u printed_residual=%d "',
    '                 "self=%d exact=%d base=%d big=%d\\n",',
    '                 stats.canon_residual, stats.canon_self, stats.canon_base, stats.canon_big, stats.canon_mismatch,',
    '                 printed_residual, self_printed ? 1 : 0, exact_printed ? 1 : 0, base_printed ? 1 : 0,',
    '                 big_printed ? 1 : 0);',
    '    Check(stats.canon_residual == 26u && stats.canon_self == 1u && stats.canon_base == 1u && stats.canon_big == 1u &&',
    '              stats.canon_mismatch == 27u,',
    '          "replay count reject: a residual reject with a suffix is not counted in canon_residual");',
    '    Check(printed_residual == 20 && !exact_printed && self_printed && base_printed && big_printed,',
    '          "replay count reject: the limits of 20 reject lines are not independent");',
    '  }',
    '}',
], 'c end')

if crlf:
    text = text.replace(NL, chr(13) + NL)
open(PATH, 'wb').write(text.encode('utf-8'))
print('PATCH TESTS OK')
