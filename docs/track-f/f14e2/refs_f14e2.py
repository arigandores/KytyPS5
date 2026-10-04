"""F14e2 (HPP-545): every <commit>:<path>:<line> reference of docs/track-f/f14e2.md - the line holds the anchor and
line+1 holds the +1 text (an empty +1 means an empty line). Rule 24(1). Prints ALL OK or FAILED.
Usage: python refs_f14e2.py (run in C:/kyty/KytyPS5)."""
import subprocess
import sys

REFS = [
    ('19f7b753', 'docs/ROADMAP.md', 22407,
     '443. **Звено F14f трека F (`HPP-506`, Red Team; приёмка лида на стадии review): F14f ПРИНЯТО',
     '(а) **Приёмка строкой: F14f ✓**'),
    ('e975327c', 'docs/track-f/f14f-review.md', 124, '**RC1. `imageInfo.h` не входит в подпись трансляции',
     '- **Что не так.** `FixF19ManualDepthCompare` берёт таблицу'),
    ('e975327c', 'docs/track-f/f14f-review.md', 137,
     '**RC3. Пустой T# при `=1` не покрыт ни одним тестом (мутант M5 выжил).**',
     '- **Сценарий отказа.** Правка, которая уберёт член `!null_descriptor`'),
    ('082d1612', 'CMakeLists.txt', 155, '-D SHADER_SOURCE_DIR=${KYTY_SOURCE_DIR}/graphics/shader',
     '-D SHADER_CACHE_EXTRA_FILES='),
    ('f98e842c', 'CMakeLists.txt', 156, '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/image/imageInfo.h',
     '-P ${KYTY_SOURCE_DIR}/generate_version.cmake'),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 5757, 'F19NullProbe CompileF19NullComparison(uint32_t opcode, bool with_k16) {',
     'constexpr uint32_t OpImageSampleImplicitLod = 87;'),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 5803, 'void TestF19NullComparisonImage() {',
     'const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");'),
    ('f98e842c', 'tests/shaderCfgTests.cpp', 15702, 'RUN(TestF19NullComparisonImage);', ''),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 39,
     'bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor) {',
     'return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 603,
     'FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));', '} else {'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 605,
     'image.manual_depth_compare = !NullImageDescriptor(descriptor) &&', 'format != Prospero::BufferFormat::k32Float;'),
    ('f98e842c', 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 1207,
     'for (bool changed = true; changed;) {', 'changed = false;'),
    ('f98e842c', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 1336,
     'const bool native_compare = binding == TextureCache::BindingType::Texture &&',
     'resource.depth_compare && !resource.manual_depth_compare;'),
    ('f98e842c', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 1339,
     'desc.info.pixel_format = vk::Format::eD32Sfloat;', '}'),
    ('a015bb9f', 'docs/track-f/f14a.md', 69, '| GPU-тест | `shader_recompiler_compute_tests.exe` (`d3f81bdc…`, та же сборка)', ''),
    ('f18022a5', 'docs/track-f/f14e.md', 191, '| `c0` `=0 --fix-f19-comparison-depth` |', ''),
    ('f18022a5', 'docs/track-f/f14e.md', 193, '## 6. Член (г)(2) — `=0` байт в байт, `=1` только места `k16UNorm` [c]', ''),
    ('f18022a5', 'docs/track-f/f14e/bin_f14e.sha256.txt', 2, '4833a35ffa91e776', 'e575f0fca9d9e1be'),
]

ok = True
for commit, path, line, anchor, plus in REFS:
    text = subprocess.run(['git', 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.decode('utf-8')
    lines = text.replace('\r\n', '\n').split('\n')
    a = lines[line - 1] if line - 1 < len(lines) else None
    b = lines[line] if line < len(lines) else None
    good_a = a is not None and anchor in a
    good_b = b is not None and (b.strip() == '' if plus == '' else plus in b)
    print('%s %s:%s:%d anchor %s +1 %s' % ('OK  ' if good_a and good_b else 'FAIL', commit, path, line, good_a, good_b))
    ok &= good_a and good_b
print('%d refs' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
