# F11d (HPP-466, ROADMAP s122 item 376(g)(2), RC2 of F11b): part B of the test patch - the stand carries
# and reads back the fault-buffer tail, and the GPU gate --diag-bvh-only (every case of item 376(g)(2), each
# number compared for exact equality). Needs the src part and part A: python patch_f11d_tests_b.py <root>.
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


def block(text):
    if text.startswith("\n"):
        text = text[1:]
    return text.split("\n")


def insert_after(anchor, text):
    anchor = anchor if isinstance(anchor, list) else [anchor]
    at = find_seq(lines, anchor) + len(anchor)
    lines[at:at] = block(text)


def insert_before(anchor, text):
    anchor = anchor if isinstance(anchor, list) else [anchor]
    at = find_seq(lines, anchor)
    lines[at:at] = block(text)


def replace(old, text):
    old = old if isinstance(old, list) else [old]
    at = find_seq(lines, old)
    lines[at:at + len(old)] = block(text)


replace("    options.printf_direction = Config::LogDirection::Silent;", r"""    // Track F, F11d: KYTY_TEST_LOG_CONSOLE=1 writes the emulator log (LOGF) to stdout - the gate counts the
    // DiagBvhNodes lines there. Unset (the default): silent, as before.
    const char *log_console = std::getenv("KYTY_TEST_LOG_CONSOLE");
    options.printf_direction = log_console != nullptr && log_console[0] == '1'
                                   ? Config::LogDirection::Console
                                   : Config::LogDirection::Silent;""")

insert_after("#include \"graphics/host_gpu/renderer/cache/bufferCache.h\"",
             "#include \"graphics/host_gpu/renderer/cache/faultManager.h\"")

insert_after("  u32 expected_storage_mip_descriptors = 0;", r"""  // Track F, F11d (KYTY_DIAG_BVHNODES gate): the fault-buffer tail is filled with 0xa5a5a5a5, then zeroed
  // over FaultManager::TailOffset/TailBytes as ClearLoopTripTail does (diag_skip_clear: not zeroed), and
  // read back after the dispatch: the loop-cap and the diagnostic words, compared with expected_tail.
  bool diag_tail = false;
  bool diag_skip_clear = false;
  std::vector<u32> expected_tail;
  uint64_t shader_hash = 0;""")

insert_after(["  options.input_info.compute = &compute_info;", "  options.user_data = user_data;"], r"""  if (test.shader_hash != 0) {
    options.shader_hash = test.shader_hash;
  }""")

replace(["    m_fault_buffer = CreateDeviceBuffer(",
         "        shader_name, BufferCache::CACHING_NUMPAGES / 8, usage);"], r"""    // Track F, F11d (RC2 of F11b): the stand carries the counter tail of the emulator's fault buffer
    // (FaultManager::TailBytes: loop-cap words, and the diagnostic words at KYTY_DIAG_BVHNODES=1) and
    // can be copied out.
    m_fault_buffer = CreateDeviceBuffer(
        shader_name, FaultManager::TailOffset() + FaultManager::TailBytes(),
        usage | vk::BufferUsageFlagBits::eTransferSrc);""")

insert_before("  [[nodiscard]] GraphicContext &RuntimeContext() {", r"""  // Track F, F11d: the fault-buffer tail of the last Dispatch of a diag_tail case (empty otherwise).
  [[nodiscard]] const std::vector<u32> &LastTail() const { return m_last_tail; }""")

insert_after("  Buffer m_fault_buffer;", "  std::vector<u32> m_last_tail;")

replace("      cmd.fillBuffer(m_fault_buffer.buffer, 0, m_fault_buffer.size, 0);", r"""      if (test.diag_tail) {
        // Track F, F11d (RC1 of F11b): garbage in the tail, then the emulator's zeroing range.
        cmd.fillBuffer(m_fault_buffer.buffer, 0, FaultManager::TailOffset(), 0);
        cmd.fillBuffer(m_fault_buffer.buffer, FaultManager::TailOffset(),
                       FaultManager::TailBytes(), 0xa5a5a5a5u);
        if (!test.diag_skip_clear) {
          vk::BufferMemoryBarrier fill_barrier{};
          fill_barrier.sType = vk::StructureType::eBufferMemoryBarrier;
          fill_barrier.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
          fill_barrier.dstAccessMask = vk::AccessFlagBits::eTransferWrite;
          fill_barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
          fill_barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
          fill_barrier.buffer = m_fault_buffer.buffer;
          fill_barrier.offset = 0;
          fill_barrier.size = m_fault_buffer.size;
          cmd.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
                              vk::PipelineStageFlagBits::eTransfer, {}, 0, nullptr, 1,
                              &fill_barrier, 0, nullptr);
          cmd.fillBuffer(m_fault_buffer.buffer, FaultManager::TailOffset(),
                         FaultManager::TailBytes(), 0);
        }
      } else {
        cmd.fillBuffer(m_fault_buffer.buffer, 0, m_fault_buffer.size, 0);
      }""")

insert_after("    cmd.dispatch(test.dispatch_x, test.dispatch_y, test.dispatch_z);", r"""    Buffer tail_readback;
    if (uses_bda && test.diag_tail) {
      // Track F, F11d: the tail goes to a host buffer for the comparison in RunCase.
      tail_readback = CreateHostBuffer(test.name, FaultManager::TailBytes(),
                                       vk::BufferUsageFlagBits::eTransferDst, {});
      vk::BufferMemoryBarrier to_copy{};
      to_copy.sType = vk::StructureType::eBufferMemoryBarrier;
      to_copy.srcAccessMask = vk::AccessFlagBits::eShaderWrite;
      to_copy.dstAccessMask = vk::AccessFlagBits::eTransferRead;
      to_copy.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
      to_copy.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
      to_copy.buffer = m_fault_buffer.buffer;
      to_copy.offset = 0;
      to_copy.size = m_fault_buffer.size;
      cmd.pipelineBarrier(vk::PipelineStageFlagBits::eComputeShader,
                          vk::PipelineStageFlagBits::eTransfer, {}, 0, nullptr, 1, &to_copy, 0,
                          nullptr);
      const vk::BufferCopy region{FaultManager::TailOffset(), 0, FaultManager::TailBytes()};
      cmd.copyBuffer(m_fault_buffer.buffer, tail_readback.buffer, 1, &region);
      vk::BufferMemoryBarrier to_host{};
      to_host.sType = vk::StructureType::eBufferMemoryBarrier;
      to_host.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
      to_host.dstAccessMask = vk::AccessFlagBits::eHostRead;
      to_host.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
      to_host.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
      to_host.buffer = tail_readback.buffer;
      to_host.offset = 0;
      to_host.size = tail_readback.size;
      cmd.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer, vk::PipelineStageFlagBits::eHost,
                          {}, 0, nullptr, 1, &to_host, 0, nullptr);
    }""")

replace(["    EndSubmitAndFree(test.name, \"dispatch\", cmd);",
         "    if (flattened_buffer.buffer != nullptr) {"], r"""    EndSubmitAndFree(test.name, "dispatch", cmd);
    m_last_tail.clear();
    if (tail_readback.buffer != nullptr) {
      m_last_tail = ReadBuffer(test.name, tail_readback,
                               static_cast<size_t>(FaultManager::TailBytes() / sizeof(u32)));
      DestroyBuffer(&tail_readback);
    }
    if (flattened_buffer.buffer != nullptr) {""")

insert_after("  auto actual = vulkan->ReadBuffer(test.name, buffer, test.expected.size());", r"""  if (test.diag_tail) {
    // Track F, F11d: every word of the tail - loop-cap words (never written here) and diagnostic words.
    CompareWords(test, "fault-buffer tail readback", test.expected_tail, vulkan->LastTail());
    std::printf("[diag]    %-28s tail", test.name);
    for (size_t index = 0; index < vulkan->LastTail().size(); index++) {
      if (vulkan->LastTail()[index] != 0u) {
        std::printf(" [%zu]=0x%x", index, vulkan->LastTail()[index]);
      }
    }
    std::printf("\n");
  }""")

GATE = r"""// Track F, F11d (HPP-466, ROADMAP p.376(g)(2), RC2/RC5/RC7 of F11b): the GPU gate of the KYTY_DIAG_BVHNODES
// counters. Every case reads the whole fault-buffer tail after the emulator's zeroing range was applied to
// 0xa5a5a5a5 garbage, and compares every word with an expectation written by hand: the 16 loop-cap words 0,
// the diagnostic words as listed, all others 0. The BVH programs read nodes of the B1b memory (base
// X = 0x110000000, KYTY_FIX_B1B=1) through a per-lane pointer table at byte DiagTableByte; the results are
// stored back over the table and not compared - the gate is the count. Descriptor size field 100 (64-byte
// units) unless named. Host subgroup: the device's (32 on the stand of this link).
namespace DiagE = ShaderRecompiler::Spirv::Emitter;
constexpr u32 DiagTableByte = 0x8200u;
constexpr u32 DiagSize = 100u;

using DiagWordsArray = std::array<u32, DiagE::DiagWords>;

std::vector<u32> DiagExpectedTail(const DiagWordsArray &diag) {
  std::vector<u32> tail(DiagE::LoopTripWords, 0u);
  tail.insert(tail.end(), diag.begin(), diag.end());
  return tail;
}

TestCase DiagBvhCase(const char *name, u32 wave_size, const std::vector<u32> &pointers, u32 size_lo,
                     u32 size_hi, u32 exec_lo, u32 calls, bool node64, const DiagWordsArray &diag) {
  using O = ShaderOpcode;
  std::vector<u32> code;
  AppendSMovLiteral(&code, 16, static_cast<u32>(B1bBvhBase >> 8u)); // dword0 = X >> 8
  AppendSMovLiteral(&code, 17, B1bWord1High);
  AppendSMovLiteral(&code, 18, size_lo);                // size[31:0]
  AppendSMovLiteral(&code, 19, 0x81000000u | size_hi);  // size[41:32], type 8, triangle_return_mode 1
  AppendVMovU32(&code, 31, DiagTableByte / 4u);
  code.push_back(EncodeVop2(0x25, 31, Vgpr(0), 31));      // v_add_nc_u32 v31, v0, v31
  code.push_back(EncodeVop2(0x1a, 31, InlineU32(2), 31)); // v_lshlrev_b32 v31, 2, v31
  AppendBufferLoadDword(&code, 4, 31);                    // v4 = pointer of this lane
  u32 vgpr = 5;
  if (node64) {
    AppendVMovU32(&code, 30, 0u);
    AppendBufferLoadDword(&code, vgpr++, 30); // high pointer dword: dword 0 of the buffer (0), runtime
  }
  AppendVMovU32(&code, vgpr++, 0x7149f2cau); // ray extent 1e30
  for (u32 i = 0; i < 3u; i++) {
    AppendVMovU32(&code, vgpr++, 0u); // origin
  }
  for (u32 i = 0; i < 6u; i++) {
    AppendVMovU32(&code, vgpr++, 0x3f800000u); // direction, inverse direction
  }
  if (exec_lo != 0u) {
    AppendSMovLiteral(&code, 126, exec_lo); // s_mov_b32 exec_lo (wave32)
  }
  for (u32 call = 0; call < calls; call++) {
    code.push_back(EncodeMimg0(node64 ? 0xe7u : 0xe6u, 0xf, 0, false, 0, true));
    code.push_back(EncodeMimg1(0, 4, 16u / 4u));
  }
  if (exec_lo != 0u) {
    code.push_back(EncodeSMovB32(126, 193u)); // s_mov_b32 exec_lo, -1
  }
  AppendBufferStoreDword(&code, 0, 31);
  AppendEnd(&code);

  TestCase test;
  test.name = name;
  test.code = std::move(code);
  test.initial = B1bMemory();
  test.initial.resize(DiagTableByte / 4u + 64u, 0u);
  for (size_t lane = 0; lane < pointers.size(); lane++) {
    test.initial[DiagTableByte / 4u + lane] = pointers[lane];
  }
  test.bda_mappings = {{0, 0},
                       {B1bBvhBase, B1bTrueBacking},
                       {B1bBvhBase >> 8u, B1bDecoyBacking}};
  test.opcodes = {O::S_MOV_B32, O::V_MOV_B32, O::V_ADD_NC_U32, O::V_LSHLREV_B32,
                  node64 ? O::IMAGE_BVH64_INTERSECT_RAY : O::IMAGE_BVH_INTERSECT_RAY,
                  O::BUFFER_LOAD_DWORD, O::BUFFER_STORE_DWORD, O::S_ENDPGM};
  test.compute_info.threads_num[0] = wave_size;
  test.compute_info.threads_num[1] = 1;
  test.compute_info.threads_num[2] = 1;
  test.compute_info.wave_size = wave_size;
  test.compute_info.thread_ids_num = 1;
  test.has_compute_info = true;
  test.diag_tail = true;
  test.expected_tail = DiagExpectedTail(diag);
  return test;
}

u32 DiagPointer(u32 idx, u32 type) { return (idx << 3u) | type; }

void RunDiagBvhCases(VulkanHarness *vulkan) {
  constexpr u32 Other = DiagE::DiagLanes + DiagE::DiagSlotCount;
  // Each node type alone, two executions of the instruction: t_k = 2 x 32 lanes.
  static const char *const type_names[8] = {"DiagBvhType0", "DiagBvhType1", "DiagBvhType2",
                                            "DiagBvhType3", "DiagBvhType4", "DiagBvhType5",
                                            "DiagBvhType6", "DiagBvhType7"};
  for (u32 type = 0; type < 8u; type++) {
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + type] = 64;
    diag[Other] = 64;
    diag[DiagE::DiagGroups] = 2;
    RunCase(vulkan, DiagBvhCase(type_names[type], 32, std::vector<u32>(32, DiagPointer(4, type)),
                                DiagSize, 0, 0, 2, false, diag));
  }
  {
    // Mixed types in one subgroup, pointers from a VGPR: lane L has type L & 7 -> 4 lanes each.
    std::vector<u32> pointers;
    for (u32 lane = 0; lane < 32u; lane++) {
      pointers.push_back(DiagPointer(4 + lane, lane & 7u));
    }
    DiagWordsArray diag{};
    for (u32 type = 0; type < 8u; type++) {
      diag[DiagE::DiagT0 + type] = 4;
    }
    diag[Other] = 32;
    diag[DiagE::DiagGroups] = 1;
    RunCase(vulkan, DiagBvhCase("DiagBvhMixedTypes", 32, pointers, DiagSize, 0, 0, 1, false, diag));
  }
  {
    // Partial exec: lanes 0..15 active with type 0, lanes 16..31 inactive with type 2 - not counted.
    std::vector<u32> pointers;
    for (u32 lane = 0; lane < 32u; lane++) {
      pointers.push_back(DiagPointer(5, lane < 16u ? 0u : 2u));
    }
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + 0] = 16;
    diag[Other] = 16;
    diag[DiagE::DiagGroups] = 1;
    RunCase(vulkan,
            DiagBvhCase("DiagBvhPartialExec", 32, pointers, DiagSize, 0, 0x0000ffffu, 1, false, diag));
  }
  {
    // Wave64: lanes 0..31 type 1, lanes 32..63 type 3 - both halves counted, one host subgroup.
    std::vector<u32> pointers;
    for (u32 lane = 0; lane < 64u; lane++) {
      pointers.push_back(DiagPointer(4 + (lane & 31u), lane < 32u ? 1u : 3u));
    }
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + 1] = 32;
    diag[DiagE::DiagT0 + 3] = 32;
    diag[Other] = 64;
    diag[DiagE::DiagGroups] = 1;
    RunCase(vulkan, DiagBvhCase("DiagBvhWave64", 64, pointers, DiagSize, 0, 0, 1, false, diag));
  }
  {
    // The size field (100): idx = 100 is not a violation; 101 is (excess 1, bucket 0); 116 (excess 16,
    // bucket 1); 117 (excess 17, bucket 2); 201 = 2 x 100 + 1 (excess 101, bucket 2 - inside the doubled
    // unit); 202 (bucket 3, idx > 2 x size + 1) for a triangle and for a box; type 7 and type 6 apart.
    std::vector<u32> pointers{DiagPointer(100, 0), DiagPointer(101, 0), DiagPointer(116, 1),
                              DiagPointer(117, 0), DiagPointer(201, 1), DiagPointer(202, 0),
                              DiagPointer(202, 4), DiagPointer(101, 7), DiagPointer(117, 6)};
    pointers.resize(32, DiagPointer(4, 0));
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + 0] = 27;
    diag[DiagE::DiagT0 + 1] = 2;
    diag[DiagE::DiagT0 + 4] = 1;
    diag[DiagE::DiagT0 + 6] = 1;
    diag[DiagE::DiagT0 + 7] = 1;
    diag[DiagE::DiagSizeViol] = 8;
    diag[DiagE::DiagOverMax] = 102;
    diag[DiagE::DiagBuckets + 0] = 1; // triangle, excess 1
    diag[DiagE::DiagBuckets + 1] = 1; // triangle, excess 2..16
    diag[DiagE::DiagBuckets + 2] = 2; // triangle, excess 17.. (117 and 201)
    diag[DiagE::DiagBuckets + 3] = 1; // triangle, idx > 2 x size + 1
    diag[DiagE::DiagBuckets + 6] = 1; // box (type 6), excess 17..
    diag[DiagE::DiagBuckets + 7] = 1; // box (type 4), idx > 2 x size + 1
    diag[DiagE::DiagBuckets + 8] = 1; // type 7, excess 1
    diag[Other] = 32;
    diag[DiagE::DiagGroups] = 1;
    RunCase(vulkan, DiagBvhCase("DiagBvhSizeBuckets", 32, pointers, DiagSize, 0, 0, 1, false, diag));
  }
  {
    // size64 = 2^42 - 1 (all ones): counted as size_off, never a violation.
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + 5] = 32;
    diag[DiagE::DiagSizeOff] = 32;
    diag[Other] = 32;
    diag[DiagE::DiagGroups] = 1;
    RunCase(vulkan, DiagBvhCase("DiagBvhSizeOff", 32, std::vector<u32>(32, DiagPointer(202, 5)),
                                0xffffffffu, 0x3ffu, 0, 1, false, diag));
  }
  {
    // 64-bit node pointer (runtime high dword): node64, never in size_viol although idx > size.
    const u32 pointer = static_cast<u32>(((B1bBvhBase + 0x100u) >> 3u) | 5u);
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + 5] = 32;
    diag[DiagE::DiagNode64] = 32;
    diag[Other] = 32;
    diag[DiagE::DiagGroups] = 1;
    RunCase(vulkan, DiagBvhCase("DiagBvhNode64", 32, std::vector<u32>(32, pointer), DiagSize, 0, 0, 1,
                                true, diag));
  }
  {
    // Program slot: the program hash 380bb9d636390bae is slot 4 of the table, other stays 0.
    const u32 slot = DiagE::DiagBvhSlot(0x380bb9d636390baeull);
    Require("DiagBvhSlot380b", "slot table", slot == 4u &&
                                                 DiagE::DiagBvhSlotHash(slot) == 0x380bb9d636390baeull &&
                                                 DiagE::DiagBvhSlot(0) == DiagE::DiagSlotCount,
            "slot of 380bb9d636390bae is not 4");
    DiagWordsArray diag{};
    diag[DiagE::DiagT0 + 5] = 32;
    diag[DiagE::DiagLanes + slot] = 32;
    diag[DiagE::DiagGroups] = 1;
    auto test = DiagBvhCase("DiagBvhSlot380b", 32, std::vector<u32>(32, DiagPointer(4, 5)), DiagSize, 0,
                            0, 1, false, diag);
    test.shader_hash = 0x380bb9d636390baeull;
    RunCase(vulkan, test);
  }
  {
    // Negative control of the zeroing (RC1): without it the 0xa5a5a5a5 garbage stays and the counts add on.
    DiagWordsArray diag{};
    diag.fill(0xa5a5a5a5u);
    diag[DiagE::DiagT0 + 0] += 32;
    diag[Other] += 32;
    diag[DiagE::DiagGroups] += 1;
    auto test = DiagBvhCase("DiagBvhNoClearControl", 32, std::vector<u32>(32, DiagPointer(4, 0)),
                            DiagSize, 0, 0, 1, false, diag);
    test.diag_skip_clear = true;
    test.expected_tail.assign(DiagE::LoopTripWords, 0xa5a5a5a5u);
    test.expected_tail.insert(test.expected_tail.end(), diag.begin(), diag.end());
    RunCase(vulkan, test);
  }
  {
    // S_TRAP (RC7): with exec = 0 every subgroup counts (3 workgroups, one wave each), no lane does; a
    // second trap with all lanes adds 3 subgroups and 3 x 32 lanes; wave64 is one host subgroup.
    struct TrapCase {
      const char *name;
      u32 wave;
      bool all;
      u32 traps;
      u32 lanes;
    };
    for (const auto &item : {TrapCase{"DiagTrapExec0Wave32", 32u, false, 3u, 0u},
                             TrapCase{"DiagTrapExecAllWave32", 32u, true, 6u, 96u},
                             TrapCase{"DiagTrapExec0Wave64", 64u, false, 3u, 0u}}) {
      DiagWordsArray diag{};
      diag[DiagE::DiagTraps] = item.traps;
      diag[DiagE::DiagTrapLanes] = item.lanes;
      auto test = DiagTrapCase(item.name, item.wave, 3u, item.all);
      test.diag_tail = true;
      test.expected_tail = DiagExpectedTail(diag);
      RunCase(vulkan, test);
    }
  }
}

"""
insert_before("TestCase VectorVop3CompareEqI64OnGpu() {", GATE)

HOOK = r"""  if (argc == 2 && std::strcmp(argv[1], "--diag-bvh-only") == 0) {
    // Track F, F11d (HPP-466, ROADMAP p.376(g)(2)): the KYTY_DIAG_BVHNODES gate at the knob values of this
    // process (KYTY_DIAG_BVHNODES, KYTY_BVH_NATIVE; both read once per process).
    const bool diag_on = ShaderRecompiler::Decoder::DiagBvhNodesEnabled();
    const char *native = std::getenv("KYTY_BVH_NATIVE");
    const auto tail_offset = FaultManager::TailOffset();
    const auto tail_bytes = FaultManager::TailBytes();
    std::printf("[diag] KYTY_DIAG_BVHNODES effective=%d KYTY_BVH_NATIVE=%s tail_offset=%llu "
                "tail_bytes=%llu\n",
                diag_on ? 1 : 0, native != nullptr ? native : "(unset)",
                static_cast<unsigned long long>(tail_offset),
                static_cast<unsigned long long>(tail_bytes));
    Require("DiagTail", "fault-buffer tail",
            tail_offset == BufferCache::CACHING_NUMPAGES / 8 &&
                tail_bytes == (diag_on ? 64u + 256u : 64u),
            "the tail is not the loop-cap words (+ 64 diagnostic words at =1)");
    {
      // =1 and =0 never share a signature or a directory.
      const ShaderTranslationCache cache("PPSA21564");
      const auto directory = Common::PathToString(cache.Directory());
      std::string signature = cache.Signature();
      while (!signature.empty() && (signature.back() == '\n' || signature.back() == '\r')) {
        signature.pop_back();
      }
      const bool diag_sig = signature.find(":diagbvh") != std::string::npos;
      const bool diag_dir = directory.find("diagbvh") != std::string::npos;
      std::printf("[diag]     cache signature=%s\n", signature.c_str());
      std::printf("[diag]     cache dir=%s diagbvh_in_signature=%d diagbvh_in_dir=%d\n",
                  directory.c_str(), diag_sig ? 1 : 0, diag_dir ? 1 : 0);
      Require("DiagCache", "translation cache key",
              cache.Enabled() && diag_sig == diag_on && diag_dir == diag_on,
              "diagbvh token of the signature or directory does not follow the knob");
    }
    VulkanHarness vulkan;
    {
      // The emulator's own FaultManager (runtime renderer of the harness): its fault buffer is the
      // bitmap plus the tail - at =0 the size it had before the diagnostics.
      const auto *fault = vulkan.RuntimeRenderer().GetBufferCache().GetFaultBuffer();
      std::printf("[diag]     emulator fault buffer bytes=%llu\n",
                  static_cast<unsigned long long>(fault->Size()));
      Require("DiagTail", "emulator fault buffer", fault->Size() == tail_offset + tail_bytes,
              "the FaultManager buffer is not bitmap + tail");
    }
    if (diag_on) {
      RunDiagBvhCases(&vulkan);
    }
    std::printf("ALL OK\n");
    return 0;
  }"""
insert_before("  if (argc == 3 && std::strcmp(argv[1], \"--diag-dump-spirv\") == 0) {", HOOK)

text = "\n".join(lines)
if crlf:
    text = text.replace("\n", "\r\n")
(ROOT / REL).write_bytes(text.encode("utf-8"))
print("patched", REL)
print("ALL OK")
