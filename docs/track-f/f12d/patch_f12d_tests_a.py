# F12d (HPP-477, ROADMAP s122 item 391(v), (g)(2)-(3)): part A of the test patch - the F10 cases (F12a section 7.1:
# triangle node types 0-3 hit and miss, types 6 and 7; the RC4 mix case of F12b) and the SPIR-V dump mode
# --f10-dump-spirv <dir> (B1b BVH cases and F10 cases). Uses only code that exists before the fix, so the same
# text is applied to the base tree (the build without the fix) and to the fix tree: python patch_f12d_tests_a.py <root>.
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

CASES = r"""// Track F, F12d (HPP-477, ROADMAP p.391(v), (g)(2)): IMAGE_BVH_INTERSECT_RAY on triangle node types 0-3 and on
// types 6, 7 under KYTY_FIX_F10 (F12a section 7.1, docs/track-f/f12a/ref_f12a.py). One 64-byte node at X + 0x100
// (X = B1bBvhBase; mapped at X and at X >> 8, so the node address is the same at both KYTY_FIX_B1B values) holds
// five vertices V0 = (0, -8, 1), V1 = (8, 0, 2), V2 = (0, 0, 0), V3 = (0, 8, 3), V4 = (-8, 0, 4) (dwords 0..14) and the
// triangle ID field 0x09040209 (dword 15). The hardware answer (GPURT b89f22aa software path, RRA): type 0 =
// (V0, V1, V2), 1 = (V1, V3, V2), 2 = (V2, V3, V4), 3 = (V2, V4, V0); 6 and 7 = 0xffffffff x4. Before the fix the
// emulator answers 0xffffffff x4 on types 2-3. The ray of a lane is origin (x, y, -4), direction (0, 0, 1); all
// coordinates are small integers, so every product and sum is exact in float32 (FMA contraction and the order of
// additions do not change a bit; t_denom = -64 makes the reciprocal exact). Expected words: ref_f12a.out.txt
// (words 2-3 follow GPURT RT IP 1.1; their applicability to PS5 is [I], RC2 of F12b). Every lane reads its node
// pointer and origin.xy from a per-lane table and stores the 4 result dwords at 16 * lane; the result area starts
// filled with the marker 0xa5a5a5a5, so a lane that must not store (inactive) keeps it.
constexpr u32 F10ResultMarker = 0xa5a5a5a5u;
constexpr u32 F10TableByte = 0x1000u;
constexpr u32 F10NodeBacking = 0x2000u;
constexpr u32 F10BufferBytes = 0x2200u;
constexpr u32 F10NodePointer = 0x100u >> 3u; // node pointer of X + 0x100 without the type (bits [31:3] = 64-byte unit 4)
constexpr u32 F10PlusTwo = 0x40000000u;  // 2.0
constexpr u32 F10MinusTwo = 0xc0000000u; // -2.0
constexpr u32 F10Ffff = 0xffffffffu;

struct F10Ray {
  const char *name;
  u32 type;
  u32 origin_x;
  u32 origin_y;
  std::array<u32, 4> fixed;   // KYTY_FIX_F10=1: the first source (F12a section 1.2)
  std::array<u32, 4> current; // KYTY_FIX_F10=0: the emulator before the fix
};

// ref_f12a.out.txt, rows "type case origin =1 =0".
const std::array<F10Ray, 10> &F10Rays() {
  static const std::array<F10Ray, 10> rays{{
      {"F10Type0Hit", 0u, F10PlusTwo, F10MinusTwo,
       {0xc3980000u, 0xc2800000u, 0xc1800000u, 0xc2000000u},
       {0xc3980000u, 0xc2800000u, 0xc1800000u, 0xc2000000u}},
      {"F10Type0Miss", 0u, F10MinusTwo, F10PlusTwo,
       {0x7f800000u, 0x3f800000u, 0x41800000u, 0xc2c00000u},
       {0x7f800000u, 0x3f800000u, 0x41800000u, 0xc2c00000u}},
      {"F10Type1Hit", 1u, F10PlusTwo, F10PlusTwo,
       {0xc3a80000u, 0xc2800000u, 0xc2000000u, 0xc1800000u},
       {0xc3a80000u, 0xc2800000u, 0xc2000000u, 0xc1800000u}},
      {"F10Type1Miss", 1u, F10MinusTwo, F10MinusTwo,
       {0x7f800000u, 0x3f800000u, 0xc2c00000u, 0x42a20000u},
       {0x7f800000u, 0x3f800000u, 0xc2c00000u, 0x42a20000u}},
      {"F10Type2Hit", 2u, F10MinusTwo, F10PlusTwo,
       {0xc3b80000u, 0xc2800000u, 0xc2000000u, 0xc1800000u},
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff}},
      {"F10Type2Miss", 2u, F10PlusTwo, F10MinusTwo,
       {0x7f800000u, 0x3f800000u, 0xc1f80000u, 0x41800000u},
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff}},
      {"F10Type3Hit", 3u, F10MinusTwo, F10MinusTwo,
       {0xc3a80000u, 0xc2800000u, 0xc1800000u, 0xc1800000u},
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff}},
      {"F10Type3Miss", 3u, F10PlusTwo, F10PlusTwo,
       {0x7f800000u, 0x3f800000u, 0x41800000u, 0x41800000u},
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff}},
      {"F10Type6", 6u, F10PlusTwo, F10MinusTwo,
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff},
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff}},
      {"F10Type7", 7u, F10PlusTwo, F10MinusTwo,
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff},
       {F10Ffff, F10Ffff, F10Ffff, F10Ffff}},
  }};
  return rays;
}

struct F10Lane {
  u32 pointer;
  u32 origin_x;
  u32 origin_y;
};

std::vector<u32> F10Memory(const std::vector<F10Lane> &lanes) {
  std::vector<u32> memory(F10BufferBytes / 4u, 0u);
  for (size_t lane = 0; lane < lanes.size(); lane++) {
    for (u32 word = 0; word < 4u; word++) {
      memory[lane * 4u + word] = F10ResultMarker;
    }
    const size_t at = F10TableByte / 4u + lane * 4u;
    memory[at + 0u] = lanes[lane].pointer;
    memory[at + 1u] = lanes[lane].origin_x;
    memory[at + 2u] = lanes[lane].origin_y;
  }
  static constexpr std::array<u32, 16> node{
      0x00000000u, 0xc1000000u, 0x3f800000u, // V0 = (0, -8, 1)
      0x41000000u, 0x00000000u, 0x40000000u, // V1 = (8, 0, 2)
      0x00000000u, 0x00000000u, 0x00000000u, // V2 = (0, 0, 0)
      0x00000000u, 0x41000000u, 0x40400000u, // V3 = (0, 8, 3)
      0xc1000000u, 0x00000000u, 0x40800000u, // V4 = (-8, 0, 4)
      0x09040209u};                          // triangle ID: I/J bytes of types 0..3
  for (u32 word = 0; word < 16u; word++) {
    memory[(F10NodeBacking + 0x100u) / 4u + word] = node[word];
  }
  return memory;
}

// exec_mask: 0 = all lanes; otherwise exec_lo (and exec_hi for wave64) = exec_mask before the first vector
// instruction, so inactive lanes neither load, nor intersect, nor store.
TestCase F10BvhCase(const char *name, u32 wave_size, u32 exec_mask, const std::vector<F10Lane> &lanes,
                    std::vector<u32> expected) {
  using O = ShaderOpcode;
  std::vector<u32> code;
  AppendSMovLiteral(&code, 16, static_cast<u32>(B1bBvhBase >> 8u)); // dword0 = X >> 8
  AppendSMovLiteral(&code, 17, B1bWord1High);
  AppendSMovLiteral(&code, 18, 0xffffffffu); // size
  AppendSMovLiteral(&code, 19, 0x81000000u); // type 8, triangle_return_mode 1 (as the game)
  if (exec_mask != 0u) {
    AppendSMovLiteral(&code, 126, exec_mask); // exec_lo
    if (wave_size == 64u) {
      AppendSMovLiteral(&code, 127, exec_mask); // exec_hi
    }
  }
  code.push_back(EncodeVop2(0x1a, 31, InlineU32(4), 0)); // v_lshlrev_b32 v31, 4, v0: result byte offset
  AppendVMovU32(&code, 30, F10TableByte);
  code.push_back(EncodeVop2(0x25, 30, Vgpr(31), 30)); // v_add_nc_u32 v30, v31, v30: table entry
  AppendBufferLoadDword(&code, 4, 30);                 // v4 = node pointer
  code.push_back(EncodeVop2(0x25, 30, InlineU32(4), 30));
  AppendBufferLoadDword(&code, 6, 30); // v6 = origin.x
  code.push_back(EncodeVop2(0x25, 30, InlineU32(4), 30));
  AppendBufferLoadDword(&code, 7, 30);     // v7 = origin.y
  AppendVMovU32(&code, 5, 0x7149f2cau);    // ray extent 1e30
  AppendVMovU32(&code, 8, 0xc0800000u);    // origin.z = -4
  AppendVMovU32(&code, 9, 0u);             // direction (0, 0, 1)
  AppendVMovU32(&code, 10, 0u);
  AppendVMovU32(&code, 11, 0x3f800000u);
  for (u32 i = 12; i < 15u; i++) {
    AppendVMovU32(&code, i, 0x3f800000u); // inverse direction (not used by triangle nodes)
  }
  code.push_back(EncodeMimg0(0xe6u, 0xf, 0, false, 0, true));
  code.push_back(EncodeMimg1(0, 4, 16u / 4u));
  for (u32 i = 0; i < 4u; i++) {
    if (i != 0u) {
      code.push_back(EncodeVop2(0x25, 31, InlineU32(4), 31)); // next result dword
    }
    AppendBufferStoreDword(&code, i, 31);
  }
  AppendEnd(&code);

  TestCase test;
  test.name = name;
  test.code = std::move(code);
  test.initial = F10Memory(lanes);
  test.expected = std::move(expected);
  test.bda_mappings = {{0, 0}, {B1bBvhBase, F10NodeBacking}, {B1bBvhBase >> 8u, F10NodeBacking}};
  test.opcodes = {O::S_MOV_B32, O::V_MOV_B32, O::V_ADD_NC_U32, O::V_LSHLREV_B32,
                  O::IMAGE_BVH_INTERSECT_RAY, O::BUFFER_LOAD_DWORD, O::BUFFER_STORE_DWORD,
                  O::S_ENDPGM};
  test.compute_info.threads_num[0] = wave_size;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.compute_info.wave_size = wave_size;
  test.compute_info.thread_ids_num = 1;
  test.has_compute_info = true;
  return test;
}

// The 10 cases of F12a section 7.1 (wave32, every lane the same ray) and the mix case (RC4 of F12b): one wave64,
// lane L has type (L >> 1) & 3 and the hit ray of its type, odd lanes are inactive (exec 0x5555555555555555) and
// carry a type-2 hit ray that would overwrite the marker if they stored; active lanes: 8 of each type 0..3.
std::vector<TestCase> F10Cases(bool fix_on) {
  std::vector<TestCase> cases;
  for (const auto &ray : F10Rays()) {
    const std::vector<F10Lane> lanes(32u, F10Lane{F10NodePointer | ray.type, ray.origin_x, ray.origin_y});
    std::vector<u32> expected;
    for (u32 lane = 0; lane < 32u; lane++) {
      const auto &words = fix_on ? ray.fixed : ray.current;
      expected.insert(expected.end(), words.begin(), words.end());
    }
    cases.push_back(F10BvhCase(ray.name, 32u, 0u, lanes, std::move(expected)));
  }
  const auto &rays = F10Rays();
  const std::array<const F10Ray *, 4> hit_of_type{&rays[0], &rays[2], &rays[4], &rays[6]};
  std::vector<F10Lane> lanes;
  std::vector<u32> expected;
  for (u32 lane = 0; lane < 64u; lane++) {
    if ((lane & 1u) == 0u) {
      const F10Ray &ray = *hit_of_type[(lane >> 1u) & 3u];
      lanes.push_back(F10Lane{F10NodePointer | ray.type, ray.origin_x, ray.origin_y});
      const auto &words = fix_on ? ray.fixed : ray.current;
      expected.insert(expected.end(), words.begin(), words.end());
    } else {
      const F10Ray &ray = rays[4];
      lanes.push_back(F10Lane{F10NodePointer | ray.type, ray.origin_x, ray.origin_y});
      expected.insert(expected.end(), 4u, F10ResultMarker);
    }
  }
  cases.push_back(F10BvhCase("F10MixWave64", 64u, 0x55555555u, lanes, std::move(expected)));
  return cases;
}

// Track F, F12d (ROADMAP p.391(g)(3)): the SPIR-V of the four B1b BVH cases and of the 11 F10 cases, one file
// <dir>/<case>.spv each, translated for a 32-wide host subgroup (no Vulkan device). Run at KYTY_BVH_NATIVE=0 and 1
// on the build without the fix and at KYTY_FIX_F10 unset / 0 / 1 on the build with it; the files are compared
// byte for byte.
int RunF10DumpSpirv(const char *dir) {
  std::vector<TestCase> cases{
      B1bBvhCase("B1bBvhNodeAddress", false, B1bWord1High, B1bTrueChildren),
      B1bBvhCase("B1bBvhPaddingBitsIgnored", false, B1bWord1High | 0x0000ab00u, B1bTrueChildren),
      B1bBvhCase("B1bBvhFieldBit32", false, B1bWord1High | 0x00000001u, B1bNullChildren),
      B1bBvhCase("B1bBvh64NodePointer", true, B1bWord1High | 0x00000001u, B1bTrueChildren),
  };
  for (auto &test : F10Cases(false)) {
    cases.push_back(std::move(test));
  }
  for (const auto &test : cases) {
    const auto compiled = CompileCase(test, 32u);
    const std::string path = std::string(dir) + "/" + test.name + ".spv";
    FILE *file = std::fopen(path.c_str(), "wb");
    Require(test.name, "SPIR-V dump", file != nullptr, "cannot open " + path);
    const auto written =
        std::fwrite(compiled.spirv.data(), sizeof(u32), compiled.spirv.size(), file);
    std::fclose(file);
    Require(test.name, "SPIR-V dump", written == compiled.spirv.size(), "short write " + path);
    std::printf("[f10-dump] %-28s words=%zu\n", test.name, compiled.spirv.size());
  }
  std::printf("ALL OK\n");
  return 0;
}

"""

at = find_seq(lines, ["TestCase VectorVop3CompareEqI64OnGpu() {"])
lines[at:at] = CASES.split("\n")[:-1]

HOOK = r"""  if (argc == 3 && std::strcmp(argv[1], "--f10-dump-spirv") == 0) {
    // Track F, F12d (HPP-477): SPIR-V of the B1b and F10 cases for the =0 byte compare.
    return RunF10DumpSpirv(argv[2]);
  }"""
at = find_seq(lines, ["  if (argc == 3 && std::strcmp(argv[1], \"--b26-pass\") == 0) {"])
lines[at:at] = HOOK.split("\n")

text = "\n".join(lines)
if crlf:
    text = text.replace("\n", "\r\n")
(ROOT / REL).write_bytes(text.encode("utf-8"))
print("patched", REL)
print("ALL OK")
