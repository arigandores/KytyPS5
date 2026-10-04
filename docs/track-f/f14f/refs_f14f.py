"""F14f (HPP-506): rule 24(1) - every <commit>:<path>:<line> reference of docs/track-f/f14f-review.md, by anchor and +1.
Usage: python refs_f14f.py   (run in C:/kyty/KytyPS5; prints one line per reference and ALL OK)"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
RM = 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
REFS = [
    ('082d1612', RM, 34, 'bool FixF19Enabled() {', 'static const bool enabled = Common::EnvFlagOn("KYTY_FIX_F19");'),
    ('082d1612', RM, 39, 'bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor) {',
     'return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;'),
    ('082d1612', RM, 43, 'void FixF19MergeIndirectTables(std::vector<ResourceSpecialization::Image>& images) {',
     'for (uint32_t root = 0; root < images.size(); root++) {'),
    ('082d1612', RM, 599, 'if (FixF19Enabled()) {',
     '// Track F, F14e (ROADMAP s122 item 409(v)): native for every format the renderer views as'),
    ('082d1612', RM, 605, 'image.manual_depth_compare = !NullImageDescriptor(descriptor) &&',
     'format != Prospero::BufferFormat::k32Float;'),
    ('082d1612', RM, 724, 'if (FixF19Enabled()) {',
     '// Track F, F14e (ROADMAP s122 item 415(b), variant O1): an indirect table with a shader-compared'),
    ('082d1612', RM, 1207, 'for (bool changed = true; changed;) {', 'changed = false;'),
    ('082d1612', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 587,
     '(ShaderRecompiler::IR::FixF19Enabled() ? ":fixf19" : "");', 'if (!variant.empty()) {'),
    ('082d1612', 'CMakeLists.txt', 155, '-D SHADER_SOURCE_DIR=${KYTY_SOURCE_DIR}/graphics/shader',
     '-D SHADER_CACHE_EXTRA_FILES=${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/guest_gpu/gpu_format.h$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/guest_gpu/gpu_defs.h'),
    ('082d1612', 'src/graphics/host_gpu/renderer/image/imageInfo.h', 193,
     'inline constexpr std::array<DepthFormatPolicy, 2> DEPTH_FORMAT_POLICIES {{', '{Prospero::DepthFormat::kZ16,'),
    ('082d1612', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 3073, 'if (resource.depth_compare) {',
     'if (const auto* depth_format = FindGuestDepthFormatPolicy(format)) {'),
    ('082d1612', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 3383,
     'if (!program.info.samplers[index].depth_compare) {', 'descriptor.fields[0] &= ~(0x7u << 12u);'),
    ('082d1612', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 1336,
     'const bool native_compare = binding == TextureCache::BindingType::Texture &&',
     'resource.depth_compare && !resource.manual_depth_compare;'),
    ('082d1612', 'src/graphics/host_gpu/renderer/cache/samplerCache.cpp', 160,
     'sampler_info.compareEnable           = (r.DepthCompareFunc() != 0 ? VK_TRUE : VK_FALSE);',
     'sampler_info.compareOp               = static_cast<vk::CompareOp>(r.DepthCompareFunc());'),
    ('082d1612', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 1584,
     'for (const bool flag: {i.read, i.written, i.atomic, i.depth_compare, i.cube, i.r128,', 'i.manual_depth_compare}) {'),
    ('082d1612', 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp', 683,
     'const bool  manual_dref    = dref && image.manual_depth_compare;', 'const bool  native_dref    = dref && !manual_dref;'),
    ('082d1612', 'tests/shaderCfgTests.cpp', 14775, 'if (const char *f19 = std::getenv("KYTY_RECOMPILE_F19_FORMAT");',
     'f19 != nullptr && ShaderRecompiler::IR::FixF19Enabled()) {'),
    ('082d1612', 'tests/ShaderRecompilerComputeTests.cpp', 10069, 'Require(name, "comparison path",',
     'compiled.program.info.images.size() == 1 &&'),
    ('f18022a5', 'docs/track-f/f14e/bin_f14e.sha256.txt', 2,
     '4833a35ffa91e77609e68afe949ca5e8ffc50bdc1ae76d9ef1470d2522d35eda *fix_shader_cfg_tests.exe',
     'e575f0fca9d9e1be372d8fa7ff358407da940c21d9c92775449fd6df12f427bc *base/shader_cfg_tests.exe'),
    ('f18022a5', 'docs/track-f/f14e/bin_f14e.sha256.txt', 4,
     '9b254b77c82952bc38ecb274da561eb8c55ba9be6e16e89da166b7ee8d071165 *build/shader_recompiler_compute_tests.exe',
     '4833a35ffa91e77609e68afe949ca5e8ffc50bdc1ae76d9ef1470d2522d35eda *build/shader_cfg_tests.exe'),
]


def main():
    ok = True
    for c, p, n, anchor, plus1 in REFS:
        text = subprocess.run([G, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout.decode('utf-8')
        lines = text.replace('\r\n', '\n').split('\n')
        a = lines[n - 1].strip() == anchor
        b = lines[n].strip() == plus1
        ok &= a and b
        print('%s %s:%s:%d anchor %s +1 %s' % ('ok ' if a and b else 'BAD', c, p, n, a, b))
    print('refs %d' % len(REFS))
    print('ALL OK' if ok else 'NOT OK')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
