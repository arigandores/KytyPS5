# F11d (HPP-466, ROADMAP s122 item 376(g)(3)): part A of the test patch - the S_TRAP case and the SPIR-V
# dump mode --diag-dump-spirv <dir> (B1b BVH cases and S_TRAP cases). Uses only code that exists before the
# diagnostics, so the same text is applied to the base tree (the build without the diagnostics) and to the
# diagnostics tree: python patch_f11d_tests_a.py <root>.
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

CASES = r"""// Track F, F11d (HPP-466, ROADMAP p.376(g)(2)-(3)): S_TRAP with exec = 0 in every wave of `groups`
// workgroups (one wave each). The trap is a scalar instruction and runs whatever exec holds; at
// KYTY_DIAG_BVHNODES=1 it counts the subgroups (traps) and no lanes (trap_lanes). `all_lanes` adds a second
// trap after exec is restored. The stores keep the program observable.
TestCase DiagTrapCase(const char *name, u32 wave_size, u32 groups, bool all_lanes) {
  using O = ShaderOpcode;
  std::vector<u32> code;
  if (wave_size == 64u) {
    code.push_back(EncodeSop1(0x04, 126, InlineU32(0))); // s_mov_b64 exec, 0
  } else {
    code.push_back(EncodeSMovB32(126, InlineU32(0))); // s_mov_b32 exec_lo, 0
  }
  code.push_back(EncodeSopp(0x12, 1)); // s_trap 1
  if (wave_size == 64u) {
    code.push_back(EncodeSop1(0x04, 126, 193u)); // s_mov_b64 exec, -1
  } else {
    code.push_back(EncodeSMovB32(126, 193u)); // s_mov_b32 exec_lo, -1
  }
  if (all_lanes) {
    code.push_back(EncodeSopp(0x12, 1)); // s_trap 1
  }
  AppendVMovU32(&code, 1, 7);
  AppendStoreVgprAtLaneDwordOffset(&code, 1, 0, 0);
  AppendEnd(&code);

  TestCase test;
  test.name = name;
  test.code = std::move(code);
  test.initial.assign(wave_size, 0u);
  test.expected.assign(wave_size, 7u);
  test.bda_mappings = {{0, 0}};
  test.opcodes = {O::S_MOV_B32, O::S_MOV_B64, O::S_TRAP, O::V_MOV_B32, O::V_LSHLREV_B32,
                  O::BUFFER_STORE_DWORD, O::S_ENDPGM};
  test.compute_info.threads_num[0] = wave_size;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.compute_info.wave_size = wave_size;
  test.compute_info.thread_ids_num = 1;
  test.has_compute_info = true;
  test.dispatch_x = groups;
  return test;
}

// Track F, F11d (ROADMAP p.376(g)(3)): the SPIR-V of the four B1b BVH cases and of the S_TRAP cases,
// one file <dir>/<case>.spv each, translated for a 32-wide host subgroup (no Vulkan device). Run at
// KYTY_BVH_NATIVE=0 and 1 on the build without the diagnostics and at KYTY_DIAG_BVHNODES=0 on the build
// with them; the files are compared byte for byte.
int RunDiagDumpSpirv(const char *dir) {
  const std::vector<TestCase> cases{
      B1bBvhCase("B1bBvhNodeAddress", false, B1bWord1High, B1bTrueChildren),
      B1bBvhCase("B1bBvhPaddingBitsIgnored", false, B1bWord1High | 0x0000ab00u, B1bTrueChildren),
      B1bBvhCase("B1bBvhFieldBit32", false, B1bWord1High | 0x00000001u, B1bNullChildren),
      B1bBvhCase("B1bBvh64NodePointer", true, B1bWord1High | 0x00000001u, B1bTrueChildren),
      DiagTrapCase("DiagTrapExec0Wave32", 32u, 3u, false),
      DiagTrapCase("DiagTrapExecAllWave32", 32u, 3u, true),
      DiagTrapCase("DiagTrapExec0Wave64", 64u, 3u, false),
  };
  for (const auto &test : cases) {
    const auto compiled = CompileCase(test, 32u);
    const std::string path = std::string(dir) + "/" + test.name + ".spv";
    FILE *file = std::fopen(path.c_str(), "wb");
    Require(test.name, "SPIR-V dump", file != nullptr, "cannot open " + path);
    const auto written =
        std::fwrite(compiled.spirv.data(), sizeof(u32), compiled.spirv.size(), file);
    std::fclose(file);
    Require(test.name, "SPIR-V dump", written == compiled.spirv.size(), "short write " + path);
    std::printf("[diag-dump] %-28s words=%zu\n", test.name, compiled.spirv.size());
  }
  std::printf("ALL OK\n");
  return 0;
}

"""

at = find_seq(lines, ["TestCase VectorVop3CompareEqI64OnGpu() {"])
lines[at:at] = CASES.split("\n")[:-1]

HOOK = r"""  if (argc == 3 && std::strcmp(argv[1], "--diag-dump-spirv") == 0) {
    // Track F, F11d (HPP-466): SPIR-V of the B1b and S_TRAP cases for the =0 byte compare.
    return RunDiagDumpSpirv(argv[2]);
  }"""
at = find_seq(lines, ["  if (argc == 3 && std::strcmp(argv[1], \"--b26-pass\") == 0) {"])
lines[at:at] = HOOK.split("\n")

text = "\n".join(lines)
if crlf:
    text = text.replace("\n", "\r\n")
(ROOT / REL).write_bytes(text.encode("utf-8"))
print("patched", REL)
print("ALL OK")
