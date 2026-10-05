"""S17a (HPP-611): shader_cfg_tests - TestShaderReplayFormat (layout line for the R_ADDR scanner fixture, RC7; canonical
forms; form K round trips; generation parse, corruption and compatibility). LF in, LF out."""
P = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
t = open(P, 'rb').read().decode('utf-8')
assert '\r' not in t


def once(anchor):
    assert t.count(anchor) == 1, anchor[:60]


inc = '#include "graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h"\n'
once(inc)
t = t.replace(inc, inc + '#include "graphics/host_gpu/renderer/pipeline/shaderReplay.h"\n')

anchor = '// Track S, S16d (HPP-608, ROADMAP s122 item 516(v)): probe P-S16 of S-replay (tests/S16dProbe.inc).\n'
once(anchor)
block = r'''// Track S, S17a (HPP-611, ROADMAP s122 item 524(z) K3, RC7 of the S16b review): the catalogue format of S-replay.
namespace Libs::Graphics {
namespace {

void TestShaderReplayFormat() {
  namespace SR = ShaderReplay;
  // The fixture line of the offline scanner (docs/track-s/s17a/r_addr.py reads every offset from it).
  std::fprintf(stderr, "%s\n", SR::LayoutLine().c_str());
  // Canonical forms by role.
  Check(SR::WordCanonical({0x105u, SR::ROLE_PTR_LO, 0}) && !SR::WordCanonical({0x2345u, SR::ROLE_PTR_LO, 0}) &&
            !SR::WordCanonical({0u, SR::ROLE_PTR_LO, 0}),
        "replay canonical PTR_LO");
  Check(SR::WordCanonical({0x12340000u, SR::ROLE_PTR_HI, 0}) && !SR::WordCanonical({0x2u, SR::ROLE_PTR_HI, 0}),
        "replay canonical PTR_HI");
  Check(SR::WordCanonical({0u, SR::ROLE_V_LO, 0}) && SR::WordCanonical({0x10Fu, SR::ROLE_V_LO, 0}) &&
            !SR::WordCanonical({0x80001000u, SR::ROLE_V_LO, 0}),
        "replay canonical V_LO");
  Check(SR::WordCanonical({0x00200000u, SR::ROLE_V_HI, 0}) && !SR::WordCanonical({0x00200001u, SR::ROLE_V_HI, 0}),
        "replay canonical V_HI");
  Check(SR::WordCanonical({1u, SR::ROLE_T_LO, 0}) && !SR::WordCanonical({0x40000u, SR::ROLE_T_LO, 0}),
        "replay canonical T_LO");
  Check(SR::WordCanonical({0x09000000u, SR::ROLE_T_HI, 0}) && !SR::WordCanonical({0x09000003u, SR::ROLE_T_HI, 0}),
        "replay canonical T_HI");
  Check(SR::WordCanonical({0x00FFFFFFu, SR::ROLE_T_META6, 0}) &&
            !SR::WordCanonical({0x01000000u, SR::ROLE_T_META6, 0}) && SR::WordCanonical({0u, SR::ROLE_T_META7, 0}) &&
            !SR::WordCanonical({1u, SR::ROLE_T_META7, 0}),
        "replay canonical T_META");
  Check(SR::WordCanonical({0x12345678u, SR::ROLE_KEEP, 0}) && !SR::WordCanonical({0x12345678u, SR::ROLE_INERT, 0}) &&
            !SR::WordCanonical({0u, SR::ROLE_COUNT, 0}),
        "replay canonical KEEP/INERT/unknown");
  // Form K: input -> key -> input -> key gives the same key (vertex with clip, mesh and two resources; pixel; compute).
  {
    ShaderVertexInputInfo vertex {};
    vertex.fetch_embedded = true;
    vertex.fetch_attrib_reg = 4;
    vertex.fetch_buffer_reg = 6;
    vertex.resources_num = 2;
    vertex.pa_cl_vs_out_cntl = 0x3fu;
    vertex.clip_space.enabled = true;
    vertex.clip_space.scale[0] = 0.5f;
    vertex.mesh.threads_num[0] = 64;
    vertex.mesh.wave_size = 32;
    vertex.mesh.max_vertices = 128;
    for (int r = 0; r < 2; r++) {
      vertex.resources_dst[r].register_start = 4 + r * 4;
      vertex.resources_dst[r].registers_num = 3 + r;
      vertex.resources_dst[r].attr_id = r;
      vertex.resources[r].fields[0] = 0x12345000u; // an address: not in the key, not in the rebuilt input
      vertex.resources[r].fields[1] = (static_cast<uint32_t>(12 + 4 * r) << 16u) | 0x7u;
      vertex.resources[r].fields[3] = 4u | (5u << 3u) | (6u << 6u) | (7u << 9u) | (13u << 12u) | (1u << 28u);
    }
    std::vector<uint32_t> key;
    BuildStageStaticKey(vertex, key);
    ShaderVertexInputInfo rebuilt {};
    std::string why;
    Check(SR::VertexFromKey(key, ShaderType::Mesh, rebuilt, why), "replay VertexFromKey");
    std::vector<uint32_t> again;
    BuildStageStaticKey(rebuilt, again);
    Check(again == key && rebuilt.resources[0].fields[0] == 0 && rebuilt.logical_stage == ShaderType::Mesh,
          "replay vertex key round trip without address");
    Check(!SR::VertexFromKey(std::span(key).first(key.size() - 1), ShaderType::Vertex, rebuilt, why),
          "replay VertexFromKey rejects a short key");
    ShaderPixelInputInfo pixel {};
    pixel.input_num = 3;
    pixel.wave_size = 32;
    pixel.ps_pos_z = true;
    pixel.interpolator_settings[2] = 0x21u;
    pixel.target_output_mode[1] = 4;
    BuildStageStaticKey(pixel, key);
    ShaderPixelInputInfo pixel2 {};
    Check(SR::PixelFromKey(key, pixel2, why), "replay PixelFromKey");
    BuildStageStaticKey(pixel2, again);
    Check(again == key, "replay pixel key round trip");
    ShaderComputeInputInfo compute {};
    compute.threads_num[0] = 64;
    compute.threads_num[1] = compute.threads_num[2] = 1;
    compute.group_id[1] = true;
    compute.workgroup_register = 12;
    compute.tg_size_en = true;
    BuildStageStaticKey(compute, key);
    ShaderComputeInputInfo compute2 {};
    Check(SR::ComputeFromKey(key, compute2, why), "replay ComputeFromKey");
    BuildStageStaticKey(compute2, again);
    Check(again == key, "replay compute key round trip");
  }
  // Generations: serialize / parse, corruption, compatibility.
  {
    SR::Catalogue catalogue;
    SR::Catalogue::Source source;
    source.header.src_id = 11;
    source.header.stage = static_cast<uint32_t>(ShaderType::Pixel);
    source.header.code_size = 2;
    source.header.code_words = 2;
    source.code = {0xbf810000u, 0u};
    catalogue.sources.push_back(source);
    SR::Catalogue::Spec spec;
    spec.header.spec_id = 22;
    spec.header.src_id = 11;
    spec.header.user_words = 1;
    spec.header.reads = 1;
    spec.header.words = 4;
    spec.words = {{0x100u, SR::ROLE_PTR_LO, SR::WORD_BASE | SR::WORD_OK},
                  {0u, SR::ROLE_PTR_HI, SR::WORD_BASE | SR::WORD_OK},
                  {7u, SR::ROLE_KEEP, SR::WORD_USER | SR::WORD_OK},
                  {1u, SR::ROLE_T_LO, SR::WORD_OK}};
    catalogue.specs.push_back(spec);
    SR::Catalogue::Pipe pipe;
    pipe.header.pipe_id = 33;
    pipe.header.spec[0] = 22;
    pipe.header.kind = 2;
    catalogue.pipes.push_back(pipe);
    const auto bytes = SR::Store::Serialize(catalogue, "compat-a", 5);
    SR::Catalogue read;
    uint64_t generation = 0;
    std::string state;
    Check(SR::Store::Parse(bytes, "compat-a", read, generation, state) && state == "ok" && generation == 5 &&
              read.sources.size() == 1 && read.specs.size() == 1 && read.pipes.size() == 1 &&
              read.FindSpec(22) != nullptr && read.FindSpec(22)->words[3].value == 1u &&
              read.FindSource(11)->code == source.code,
          "replay generation round trip");
    Check(SR::Store::Parse(bytes, "compat-b", read, generation, state) && state == "mismatch",
          "replay generation compat mismatch");
    auto spoiled = bytes;
    spoiled.back() ^= 0xFFu;
    Check(!SR::Store::Parse(spoiled, "compat-a", read, generation, state) && state == "corrupt",
          "replay generation corrupt");
    auto truncated = bytes;
    truncated.resize(truncated.size() - 3);
    Check(!SR::Store::Parse(truncated, "compat-a", read, generation, state) && state == "corrupt",
          "replay generation truncated");
    Check(SR::SourceId(1, 2, 3, 4, std::vector<uint32_t> {5u}) != SR::SourceId(1, 2, 3, 4, std::vector<uint32_t> {6u}),
          "replay source id keys the static state");
  }
  // The knob is off by default (the test runs without KYTY_S_REPLAY).
  if (std::getenv("KYTY_S_REPLAY") == nullptr) {
    Check(SR::Mode() == 0 && !SR::CaptureOn() && !SR::RebuildOn(), "replay knob default 0");
  }
}

} // namespace
} // namespace Libs::Graphics

'''
t = t.replace(anchor, block + anchor)

run = '  RUN(TestF19NullComparisonImage);\n'
once(run)
t = t.replace(run, run + '  RUN(TestShaderReplayFormat);\n')
open(P, 'wb').write(t.encode('utf-8'))
print('tests patched OK')
