# F12d (HPP-477, ROADMAP s122 item 391(g)(2)): part B of the test patch - the GPU gate mode --fix-f10-only: the
# translation cache tokens follow KYTY_FIX_F10, the 11 F10 cases (part A) with the expectation of the knob value of
# this process, and the four B1b cases with their previous expectations. Applied to the fix tree only (it calls
# Decoder::FixF10Enabled): python patch_f12d_tests_b.py <root>.
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
REL = "tests/ShaderRecompilerComputeTests.cpp"


def find_seq(lines, seq):
    hits = [i for i in range(len(lines) - len(seq) + 1) if lines[i:i + len(seq)] == seq]
    if len(hits) != 1:
        raise SystemExit("ANCHOR %s matches %d times" % (seq[0][:80], len(hits)))
    return hits[0]


raw = (ROOT / REL).read_bytes().decode("utf-8")
crlf = "\r\n" in raw
lines = raw.replace("\r\n", "\n").split("\n")

HOOK = r"""  if (argc == 2 && std::strcmp(argv[1], "--fix-f10-only") == 0) {
    // Track F, F12d (HPP-477, ROADMAP p.391(g)(2)): the GPU gate of KYTY_FIX_F10 at the knob values of this
    // process (KYTY_FIX_F10, KYTY_BVH_NATIVE, KYTY_FIX_B1B; all read once per process): the F10 cases of F12a
    // section 7.1 and the RC4 mix case, every word exact; the B1b cases with their previous expectations.
    const bool fix_on = ShaderRecompiler::Decoder::FixF10Enabled();
    const bool fix_b1b = ShaderRecompiler::Decoder::FixB1BEnabled();
    const char *raw_f10 = std::getenv("KYTY_FIX_F10");
    const char *native = std::getenv("KYTY_BVH_NATIVE");
    std::printf("[f10] KYTY_FIX_F10=%s effective=%d KYTY_FIX_B1B effective=%d KYTY_BVH_NATIVE=%s\n",
                raw_f10 != nullptr ? raw_f10 : "(unset)", fix_on ? 1 : 0, fix_b1b ? 1 : 0,
                native != nullptr ? native : "(unset)");
    {
      // =0 and =1 never share a signature or a directory; the token is the last one of the variant.
      const ShaderTranslationCache cache("PPSA21564");
      const auto directory = Common::PathToString(cache.Directory());
      std::string signature = cache.Signature();
      while (!signature.empty() && (signature.back() == '\n' || signature.back() == '\r')) {
        signature.pop_back();
      }
      const bool f10_sig = signature.find(":fixf10") != std::string::npos;
      const bool f10_dir = directory.find("fixf10") != std::string::npos;
      const bool f10_last_sig = f10_sig && signature.size() >= 7u &&
                                signature.compare(signature.size() - 7u, 7u, ":fixf10") == 0;
      const bool f10_last_dir = f10_dir && directory.size() >= 7u &&
                                directory.compare(directory.size() - 7u, 7u, "_fixf10") == 0;
      std::printf("[f10]     cache signature=%s\n", signature.c_str());
      std::printf("[f10]     cache dir=%s fixf10_in_signature=%d fixf10_in_dir=%d last_sig=%d last_dir=%d\n",
                  directory.c_str(), f10_sig ? 1 : 0, f10_dir ? 1 : 0, f10_last_sig ? 1 : 0,
                  f10_last_dir ? 1 : 0);
      Require("F10Cache", "translation cache key",
              cache.Enabled() && f10_sig == fix_on && f10_dir == fix_on && f10_last_sig == fix_on &&
                  f10_last_dir == fix_on,
              "fixf10 token of the signature or directory does not follow the knob");
    }
    VulkanHarness vulkan;
    for (const auto &test : F10Cases(fix_on)) {
      RunCase(&vulkan, test);
    }
    RunB1bCases(&vulkan, fix_b1b);
    std::printf("ALL OK\n");
    return 0;
  }"""
at = find_seq(lines, ["  if (argc == 3 && std::strcmp(argv[1], \"--f10-dump-spirv\") == 0) {"])
lines[at:at] = HOOK.split("\n")

text = "\n".join(lines)
if crlf:
    text = text.replace("\n", "\r\n")
(ROOT / REL).write_bytes(text.encode("utf-8"))
print("patched", REL)
print("ALL OK")
