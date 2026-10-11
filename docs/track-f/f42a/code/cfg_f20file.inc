  if (const char *f20file = std::getenv("KYTY_TEST_F20FILE"); f20file != nullptr && f20file[0] != 0) {
    // Track F, F42a (HPP-779, ROADMAP s122 item 694(g)(3)): KYTY_TEST_F20FILE="<in.spv>;<out.spv>;<bound 0|1>" - the
    // module of KYTY_FIX_F20=1 for the replay arms a / a' (Libs::Graphics::FixF20::RewriteFaultOr, the function the
    // emulator calls); <out> = the rewritten words, or a copy of <in> when nothing is rewritten; one line "f20file: ...".
    std::string list = f20file;
    const auto first = list.find(';');
    const auto second = first == std::string::npos ? std::string::npos : list.find(';', first + 1);
    if (second == std::string::npos) {
      std::fprintf(stderr, "KYTY_TEST_F20FILE=<in.spv>;<out.spv>;<bound 0|1>\n");
      return 1;
    }
    const auto in_path = list.substr(0, first);
    const auto out_path = list.substr(first + 1, second - first - 1);
    const bool bound = list.substr(second + 1) == "1";
    std::vector<uint32_t> words;
    if (FILE *file = std::fopen(in_path.c_str(), "rb"); file != nullptr) {
      uint32_t word = 0;
      while (std::fread(&word, sizeof(word), 1, file) == 1) {
        words.push_back(word);
      }
      std::fclose(file);
    } else {
      std::fprintf(stderr, "f20file: cannot open %s\n", in_path.c_str());
      return 1;
    }
    std::vector<uint32_t> fixed;
    const auto stats = Libs::Graphics::FixF20::RewriteFaultOr(words, bound, fixed);
    const auto &result = stats.rewritten != 0 ? fixed : words;
    FILE *out = std::fopen(out_path.c_str(), "wb");
    if (out == nullptr) {
      std::fprintf(stderr, "f20file: cannot write %s\n", out_path.c_str());
      return 1;
    }
    std::fwrite(result.data(), sizeof(uint32_t), result.size(), out);
    std::fclose(out);
    std::printf("f20file: bound=%d named=%u sites=%u rewritten=%u unmatched=%u malformed=%d words_in=%zu words_out=%zu\n",
                bound ? 1 : 0, stats.named, stats.sites, stats.rewritten, stats.unmatched, stats.malformed ? 1 : 0,
                words.size(), result.size());
    return 0;
  }
