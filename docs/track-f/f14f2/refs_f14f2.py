# F14f2 (HPP-546): references of docs/track-f/f14f2-review.md - <commit>:<path>:<line>, anchor (substring of the line) and
# control +1 (substring of the next line; '' = empty line). Rule 24(1).
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
R = [
    ('f98e842c', 'CMakeLists.txt', 156, '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/image/imageInfo.h',
     '-P ${KYTY_SOURCE_DIR}/generate_version.cmake'),
    ('f98e842c', 'src/generate_version.cmake', 51, 'if(EXISTS "${SHADER_SOURCE}")', 'file(SHA1 "${SHADER_SOURCE}" SHADER_DIGEST)'),
    ('f98e842c', 'src/graphics/host_gpu/renderer/image/imageInfo.h', 193,
     'inline constexpr std::array<DepthFormatPolicy, 2> DEPTH_FORMAT_POLICIES {{', '{Prospero::DepthFormat::kZ16,'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 40,
     'return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;', '}'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 123,
     'return descriptor.dwords[0] == 0 && (descriptor.dwords[1] & 0xffu) == 0;', '}'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 603,
     'FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));', '} else {'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 1213,
     'if (images[pair.image].manual_depth_compare && samplers[pair.sampler].depth_compare) {',
     'samplers[pair.sampler].depth_compare = false;'),
    ('f98e842c', 'src/graphics/shader/shaderBindings.h', 101, 'IsNull() const { return Base40() == 0; }',
     'Prospero::BufferFormat Format() const {'),
    ('f98e842c', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 1336,
     'const bool native_compare = binding == TextureCache::BindingType::Texture &&',
     'resource.depth_compare && !resource.manual_depth_compare;'),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 5803, 'void TestF19NullComparisonImage() {',
     'const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");'),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 15702, 'RUN(TestF19NullComparisonImage);', ''),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 15399, 'ShaderRecompiler::IR::FixF19ManualDepthCompare(format, false);',
     '(image.manual_depth_compare ? kept_manual : to_native)++;'),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 1522, 'for (uint32_t start = 0; start + 3u < data.size(); start += 4u) {',
     'data[start] = 0x1000u + start * 0x100u;'),
    ('574bf7ff', 'docs/track-f/f14e2.md', 130, '## 6. Поправки к `f14e.md` (п. 443(б); отчёт F14e не переписывается)', ''),
    ('f18022a5', 'docs/track-f/f14e.md', 191, '| `c0` `=0 --fix-f19-comparison-depth` |', ''),
]
ok = True
for c, p, n, a, b in R:
    t = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8')
    L = t.split('\n')
    la = L[n - 1] if n - 1 < len(L) else None
    lb = L[n] if n < len(L) else None
    oa = la is not None and a in la
    ob = lb is not None and (lb.strip() == '' if b == '' else b in lb)
    print('%s:%s:%d anchor %s +1 %s' % (c, p, n, 'OK' if oa else 'BAD', 'OK' if ob else 'BAD'))
    ok &= oa and ob
print('%d refs' % len(R))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
