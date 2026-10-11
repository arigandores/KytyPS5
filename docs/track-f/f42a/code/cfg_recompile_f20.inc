    if (const char *f20 = std::getenv("KYTY_RECOMPILE_F20"); f20 != nullptr && f20[0] != 0) {
      // Track F, F42a (HPP-779, ROADMAP s122 item 694(g)(4)): KYTY_RECOMPILE_F20=<file> - the module of KYTY_FIX_F20=1
      // (Libs::Graphics::FixF20::RewriteFaultOr with the FaultBuffer binding of the compiled program, the function the
      // emulator calls; the words unchanged when nothing is rewritten) and one line "recompile-f20: ...".
      const bool bound = std::ranges::any_of(compiled.program.bindings.descriptors, [](const auto &b) {
        return b.kind == ShaderRecompiler::IR::DescriptorBindingKind::FaultBuffer;
      });
      std::vector<uint32_t> fixed;
      const auto stats = Libs::Graphics::FixF20::RewriteFaultOr(compiled.spirv, bound, fixed);
      const auto &words = stats.rewritten != 0 ? fixed : compiled.spirv;
      FILE *f20_out = std::fopen(f20, "wb");
      if (f20_out == nullptr) {
        std::fprintf(stderr, "recompile: cannot write %s\n", f20);
        return 1;
      }
      std::fwrite(words.data(), sizeof(uint32_t), words.size(), f20_out);
      std::fclose(f20_out);
      std::printf("recompile-f20: bound=%d named=%u sites=%u rewritten=%u unmatched=%u malformed=%d words=%zu -> %s\n",
                  bound ? 1 : 0, stats.named, stats.sites, stats.rewritten, stats.unmatched, stats.malformed ? 1 : 0,
                  words.size(), f20);
    }
