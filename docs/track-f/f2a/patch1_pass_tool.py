# F2a (HPP-307) patch 1: test-only tool "--b26-pass <eboot.bin>" in ShaderRecompilerComputeTests.cpp
# (ROADMAP p.237(g)(2), RC7 F1b): full decoder pass over the 5 B26b shaders BEFORE the fix.
import sys
sys.path.insert(0, 'C:/kyty/f287/f2a')
import patchlib

T = 'C:/kyty/KytyPS5/tests/ShaderRecompilerComputeTests.cpp'

FUNC = r'''// Track F, F2a (HPP-307, ROADMAP p.237(g)(2), RC7 of the F1b review): the full decoder pass over the
// five B26b compute shaders, read from eboot.bin by offset (docs/track-f/f1a/b26_shaders.tsv). It
// lists EVERY UNSUPPORTED instruction - the CFG stops at the first one - and then translates each
// shader the way CsPretranslate does (computePretranslation.h: zero user data, fatal interceptor,
// translation budget) for the wave sizes 32 and 64. The registration info of the real shaders
// (threads, user SGPR count) is not in the logs: threads 64x1x1 and 16 user SGPRs are assumptions,
// so the translation verdict is a prediction, the UNSUPPORTED list is not.
static int RunB26DecodePass(const char *eboot_path) {
  namespace SR = Libs::Graphics::ShaderRecompiler;
  struct Blob {
    uint64_t hash;
    uint64_t offset;
    uint32_t words;
  };
  const Blob blobs[] = {
      {0x57c4d5848e02ecdcull, 0x901f640ull, 4420},
      {0x433e4cede34ca4c3ull, 0x9033540ull, 136},
      {0x4468d53059c03cbaull, 0x9034140ull, 344},
      {0x7bb50479b3a32c7cull, 0x9034740ull, 380},
      {0xf8e350383290ff7bull, 0x9033840ull, 152},
  };
  std::FILE *file = std::fopen(eboot_path, "rb");
  if (file == nullptr) {
    std::fprintf(stderr, "B26Pass: cannot open %s\n", eboot_path);
    return 2;
  }
  int failures = 0;
  size_t unsupported_total = 0;
  for (const auto &blob : blobs) {
    std::vector<uint32_t> code(blob.words);
    if (_fseeki64(file, static_cast<long long>(blob.offset), SEEK_SET) != 0 ||
        std::fread(code.data(), sizeof(uint32_t), code.size(), file) != code.size()) {
      std::printf("B26Pass: hash=%016llx read failed\n",
                  static_cast<unsigned long long>(blob.hash));
      failures++;
      continue;
    }
    const auto xxh = XXH3_64bits(code.data(), code.size() * sizeof(uint32_t));
    SR::Decoder::Program program;
    std::string decode_error;
    try {
      Common::ScopedFatalInterceptor recover(
          [](const char *where, int line, std::string_view text) {
            throw std::runtime_error(std::string(where) + ":" +
                                     std::to_string(line) + " " +
                                     std::string(text));
          });
      SR::Decoder::DecodeProgram(code, program);
    } catch (const std::exception &error) {
      decode_error = error.what();
    }
    size_t unsupported = 0;
    for (const auto &inst : program.instructions) {
      unsupported += inst.opcode == SR::Decoder::Opcode::UNSUPPORTED ? 1u : 0u;
    }
    unsupported_total += unsupported;
    std::printf("B26Pass: hash=%016llx words=%u xxh3=%016llx match=%d "
                "instructions=%zu unsupported=%zu decode_error=%s\n",
                static_cast<unsigned long long>(blob.hash), blob.words,
                static_cast<unsigned long long>(xxh), xxh == blob.hash ? 1 : 0,
                program.instructions.size(), unsupported,
                decode_error.empty() ? "none" : decode_error.c_str());
    if (xxh != blob.hash || !decode_error.empty()) {
      failures++;
    }
    for (const auto &inst : program.instructions) {
      if (inst.opcode != SR::Decoder::Opcode::UNSUPPORTED) {
        continue;
      }
      // A one-word UNSUPPORTED record whose source field selects the literal (255) leaves the
      // literal word to be decoded as the next instruction: mark it so the list can be read.
      const auto word = inst.raw[0];
      bool literal_follows = false;
      switch (inst.family) {
      case SR::Decoder::Family::SOP1:
        literal_follows = (word & 0xffu) == 0xffu;
        break;
      case SR::Decoder::Family::SOP2:
      case SR::Decoder::Family::SOPC:
        literal_follows = (word & 0xffu) == 0xffu || ((word >> 8u) & 0xffu) == 0xffu;
        break;
      case SR::Decoder::Family::VOPC:
        literal_follows = (word & 0x1ffu) == 0xffu;
        break;
      default:
        break;
      }
      std::printf("B26Pass:   %s literal_follows=%d\n",
                  SR::Decoder::InstructionToString(inst).c_str(),
                  literal_follows ? 1 : 0);
    }
    for (const uint32_t wave : {32u, 64u}) {
      Libs::Graphics::ShaderComputeInputInfo info{};
      info.lds_size_dwords = 1024;
      info.threads_num[0] = 64;
      info.threads_num[1] = 1;
      info.threads_num[2] = 1;
      info.thread_ids_num = 1;
      info.wave_size = wave;
      info.host_subgroup_size = 32;
      std::array<uint32_t, 32> user_data{};
      SR::CompileOptions options;
      options.stage = Libs::Graphics::ShaderType::Compute;
      options.shader_hash = blob.hash;
      options.wave_size = wave;
      options.input_info.compute = &info;
      options.user_data = std::span(user_data).first(16);
      std::string verdict = "ready";
      try {
        Common::ScopedFatalInterceptor recover(
            [](const char *where, int line, std::string_view text) {
              throw std::runtime_error(std::string(where) + ":" +
                                       std::to_string(line) + " " +
                                       std::string(text));
            });
        SR::TranslationBudget budget;
        SR::TranslationBudget::current = &budget;
        auto result = SR::TranslateProgram(code, options);
        SR::TranslationBudget::current = nullptr;
      } catch (const std::exception &error) {
        SR::TranslationBudget::current = nullptr;
        verdict = std::string("skipped reason=") + error.what();
      }
      std::printf("B26Pass: translate hash=%016llx wave=%u %s\n",
                  static_cast<unsigned long long>(blob.hash), wave,
                  verdict.c_str());
    }
  }
  std::fclose(file);
  std::printf("B26Pass: shaders=5 unsupported_total=%zu failures=%d\n",
              unsupported_total, failures);
  if (failures == 0) {
    std::printf("ALL OK\n");
  }
  return failures == 0 ? 0 : 1;
}
'''.split('\n')

patchlib.apply(T, [
    (['#include "graphics/shader/recompiler/ShaderRecompiler.h"'],
     ['#include "graphics/shader/recompiler/TranslationBudget.h"'], 'after'),
    (['#include <algorithm>'], ['#include <xxhash.h>'], 'before'),
    (['int main(int argc, char **argv) {'], FUNC, 'before'),
    (['  CheckLeastRecentlyUsedCacheOrdering();'],
     ['  if (argc == 3 && std::strcmp(argv[1], "--b26-pass") == 0) {',
      '    return RunB26DecodePass(argv[2]);',
      '  }'], 'after'),
])
