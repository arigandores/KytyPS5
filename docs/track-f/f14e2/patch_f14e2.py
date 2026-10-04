"""F14e2 (HPP-545, ROADMAP s122 item 443(b)): RC1 and RC3 of the F14f review.

RC1 - CMakeLists.txt: imageInfo.h (DEPTH_FORMAT_POLICIES, read by FixF19ManualDepthCompare) joins
      SHADER_CACHE_EXTRA_FILES, the file set of KYTY_SHADER_SOURCE_HASH (the translation cache signature).
RC3 - tests/shaderCfgTests.cpp: probes of a null T# with a comparison sample (alone; on one sampler with a k16UNorm
      T#); the test runs LAST (RUN after TestSpecDumpRoundTrip), so the SPIR-V files of the set keep their numbers
      and the new ones are appended.
Anchors are whole lines; CR is stripped before the search and restored on write (LF files stay LF).
Usage: python patch_f14e2.py <worktree root>
"""
import sys

ROOT = sys.argv[1].rstrip('/')


def patch(rel, edits):
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    for anchor, mode, new in edits:
        hits = [i for i, l in enumerate(lines) if l == anchor]
        if len(hits) != 1:
            print('ANCHOR %s hits %d: %r' % (rel, len(hits), anchor[:90]))
            sys.exit(1)
        i = hits[0]
        if mode == 'replace':
            lines[i:i + 1] = new
        elif mode == 'before':
            lines[i:i] = new
        elif mode == 'after':
            lines[i + 1:i + 1] = new
        print('%s:%d %s (%d lines)' % (rel, i + 1, mode, len(new)))
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    open(path, 'wb').write(out.encode('utf-8'))
    print('%s written, crlf %s' % (rel, crlf))


CMAKE_OLD = ('\t\t-D SHADER_CACHE_EXTRA_FILES=${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
             '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/guest_gpu/gpu_format.h'
             '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/guest_gpu/gpu_defs.h')
CMAKE_NEW = CMAKE_OLD + '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/image/imageInfo.h'

TEST_FN = r'''// Track F, F14e2 (HPP-545, ROADMAP s122 item 443(b), RC3 of the F14f review): a null T# with a comparison sample.
// The rule before the fix and the =1 rule (FixF19ManualDepthCompare) both keep a null T# native, so the renderer
// binds the D32 placeholder of NullTextureDesc (descriptors.cpp: depth_compare && !manual_depth_compare).
// (1) alone - native OpImageSampleDref* at any KYTY_FIX_F19; (2) on one sampler with a k16UNorm T# - at =1 both
// native (neither is manual, the shared-sampler pass of ApplyResourceSpecialization has nothing to spread), at =0
// both manual (k16UNorm by the rule before the fix, the null image through the shared sampler). A =1 rule that makes
// the null T# manual (mutant M5 of F14f: no !null_descriptor) fails (1) and (2) at =1.
struct F19NullProbe {
  size_t images = 0;
  uint32_t native_images = 0; // depth_compare && !manual_depth_compare after specialization
  uint32_t manual_images = 0; // depth_compare && manual_depth_compare after specialization
  uint32_t dref = 0;
  uint32_t manual = 0;
};

F19NullProbe CompileF19NullComparison(uint32_t opcode, bool with_k16) {
  constexpr uint32_t OpImageSampleImplicitLod = 87;
  constexpr uint32_t OpImageSampleExplicitLod = 88;
  constexpr uint32_t OpImageSampleDrefImplicitLod = 89;
  constexpr uint32_t OpImageSampleDrefExplicitLod = 90;
  auto user_data = ImageTestUserData();
  for (uint32_t i = 0; i < 8u; i++) {
    user_data[i] = 0u; // T# s[0:7]: null (all zero)
  }
  SetImageTestFormat(&user_data, 2, Prospero::BufferFormat::k16UNorm); // T# s[8:15]
  user_data[16] = 3u << 12u; // S# s[16:19]: depth compare LESS_EQUAL
  user_data[17] = 0u;
  user_data[18] = 0u;
  user_data[19] = 0u;
  std::vector<uint32_t> shader = {
      EncodeMimg0(opcode, 0x1),
      EncodeMimg1(0, 0, 4, 4), // v0, v[4:6], T# s[0:7] (null), S# s[16:19]
  };
  if (with_k16) {
    shader.push_back(EncodeMimg0(opcode, 0x1));
    shader.push_back(EncodeMimg1(1, 2, 4, 4)); // v1, v[4:6], T# s[8:15] (k16UNorm), S# s[16:19]
  }
  shader.push_back(EncodeExp0(0x00, 0xf, true, false, true));
  shader.push_back(EncodeExp1(0, 1, 2, 3));
  shader.push_back(0xbf810000u);
  auto ps_info = RegressionPixelInputInfo();
  auto options = MakeCompileOptions(ShaderType::Pixel);
  options.input_info.pixel = &ps_info;
  options.dump_ir = true;
  options.user_data = user_data;
  auto result = RecompileForTest(shader, options);
  CheckSpirvBinaryValidates(result.spirv);
  F19NullProbe probe;
  probe.images = result.program.info.images.size();
  for (const auto &image : result.program.info.images) {
    if (image.depth_compare) {
      (image.manual_depth_compare ? probe.manual_images : probe.native_images)++;
    }
  }
  probe.dref = SpirvInstructionOpcodeCount(result.spirv, OpImageSampleDrefImplicitLod) +
               SpirvInstructionOpcodeCount(result.spirv, OpImageSampleDrefExplicitLod);
  probe.manual = SpirvManualDepthCompareCount(
      result.spirv, opcode == 0x28u ? OpImageSampleImplicitLod : OpImageSampleExplicitLod);
  return probe;
}

void TestF19NullComparisonImage() {
  const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");
  for (const uint32_t opcode : {0x28u, 0x2fu}) { // image_sample_c, image_sample_c_lz
    const char *name = opcode == 0x28u ? "C" : "C_LZ";
    const auto alone = CompileF19NullComparison(opcode, false);
    std::printf("[f19] null T# alone %s KYTY_FIX_F19=%d: images=%zu native=%u manual_images=%u dref=%u "
                "manual=%u\n",
                name, fix_f19 ? 1 : 0, alone.images, alone.native_images, alone.manual_images, alone.dref,
                alone.manual);
    Check(alone.images == 1u && alone.native_images == 1u && alone.manual_images == 0u &&
              alone.dref == 1u && alone.manual == 0u,
          "null comparison T# must be native Dref (D32 placeholder) at any KYTY_FIX_F19");
    const auto shared = CompileF19NullComparison(opcode, true);
    std::printf("[f19] null T# + k16UNorm shared sampler %s KYTY_FIX_F19=%d: images=%zu native=%u "
                "manual_images=%u dref=%u manual=%u\n",
                name, fix_f19 ? 1 : 0, shared.images, shared.native_images, shared.manual_images,
                shared.dref, shared.manual);
    Check(shared.images == 2u, "null T# + k16UNorm on one sampler did not materialize as two images");
    if (fix_f19) {
      Check(shared.native_images == 2u && shared.manual_images == 0u && shared.dref == 2u &&
                shared.manual == 0u,
            "null T# + k16UNorm on one sampler must both be native Dref at KYTY_FIX_F19=1");
    } else {
      Check(shared.native_images == 0u && shared.manual_images == 2u && shared.dref == 0u &&
                shared.manual == 2u,
            "null T# + k16UNorm on one sampler must both be the manual compare at KYTY_FIX_F19=0");
    }
  }
}
'''

patch('CMakeLists.txt', [(CMAKE_OLD, 'replace', [CMAKE_NEW])])
patch('tests/shaderCfgTests.cpp', [
    ('void TestNewShaderRecompilerImageViewDimensions() {', 'before', TEST_FN.split('\n')),
    ('  RUN(TestSpecDumpRoundTrip);', 'after', ['  RUN(TestF19NullComparisonImage);']),
])
print('PATCH OK')
