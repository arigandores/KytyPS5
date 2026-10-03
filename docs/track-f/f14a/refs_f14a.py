"""F14a (HPP-487): rule 24(1) - every <commit>:<path>:<line> reference of docs/track-f/f14a.md is checked against the git blob:
the anchor text must be on the line, the control text on line + 1. Prints one line per reference and ALL OK / FAIL."""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
C = 'ded0daf2'
R = 'c5bff245'
REFS = [
    (R, 'docs/ROADMAP.md', 21285, '(г) **Следующая итерация очереди F — F14 = Б11 (+Ф3)**', 'остался отзыв — F14 идёт параллельно'),
    (R, 'docs/ROADMAP.md', 21294, '**Правило вывода (решено сейчас):** Б11 — (а) выход', 'транслятора соответствует ISA, ошибается ожидание теста'),
    (C, 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 570,
     'image.manual_depth_compare = !NullImageDescriptor(descriptor) &&', 'format != Prospero::BufferFormat::k32Float;'),
    (C, 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 128,
     'bool RequiresPointSampler(const ImageResource& image) {', 'return image.numeric_class == Prospero::TextureNumericClass::Sint ||'),
    (C, 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 1171,
     'if (images[pair.image].manual_depth_compare && samplers[pair.sampler].depth_compare) {', 'samplers[pair.sampler].depth_compare = false;'),
    (C, 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp', 72,
     'if (HasFlag(mem, Decoder::ImageSampleFlagCompare)) layout.dref = cursor++;', 'if (HasFlag(mem, Decoder::ImageSampleFlagDerivative)) {'),
    (C, 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp', 106,
     'uint32_t ManualDepthCompare(EmitterState& state, uint32_t texel, uint32_t ref, uint32_t op) {', 'const auto depth = state.builder.AllocateId();'),
    (C, 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp', 683,
     'const bool  manual_dref    = dref && image.manual_depth_compare;', 'const bool  native_dref    = dref && !manual_dref;'),
    (C, 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp', 766,
     'opcode = native_dref ? spv::OpImageSampleDrefExplicitLod : spv::OpImageSampleExplicitLod;', '} else if (native_dref) {'),
    (C, 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp', 823,
     'result = ManualDepthCompare(state, result, dref_value, image.depth_compare_op);', '}'),
    (C, 'src/graphics/shader/recompiler/frontend/decode/ImageOps.cpp', 300,
     'if ((flags & ImageSampleFlagCompare) != 0u && index == cursor) return 32u;', 'return 16u;'),
    (C, 'src/graphics/host_gpu/renderer/cache/samplerCache.cpp', 147,
     'sampler_info.magFilter = to_vk_filter(mag_filter);', 'sampler_info.minFilter = to_vk_filter(min_filter);'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 3383,
     'if (!program.info.samplers[index].depth_compare) {', 'descriptor.fields[0] &= ~(0x7u << 12u);'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 3073,
     'if (resource.depth_compare) {', 'if (const auto* depth_format = FindGuestDepthFormatPolicy(format)) {'),
    (C, 'src/graphics/host_gpu/renderer/image/imageInfo.h', 194, '{Prospero::DepthFormat::kZ16,', 'Prospero::BufferFormat::k16UNorm,'),
    (C, 'tests/shaderCfgTests.cpp', 1429, 'data[start + 1u] = static_cast<uint32_t>(Prospero::BufferFormat::k8UNorm)', '<< 20u;'),
    (C, 'tests/shaderCfgTests.cpp', 5382, 'const auto result = compile(0x28, 0x1); // image_sample_c', 'Check(SpirvInstructionOpcodeCount(result.spirv,'),
    (C, 'tests/shaderCfgTests.cpp', 5391, 'const auto result = compile(0x2f, 0x1); // image_sample_c_lz', 'Check(SpirvInstructionOpcodeCount(result.spirv,'),
    (C, 'tests/shaderCfgTests.cpp', 14675, 'RUN(TestNewShaderRecompilerPixelImageSampleLodSelection);', 'RUN(TestNewShaderRecompilerBranchConditionForms);'),
    (C, 'tests/ResourceMaterializationTests.cpp', 311,
     'Check(specialization.images[0].manual_depth_compare == (format != Prospero::BufferFormat::k32Float) &&',
     'specialization.images[0].depth_compare_op == 3u,'),
    (C, 'tests/ShaderRecompilerComputeTests.cpp', 9777, 'test.required_spirv = {"OpImageSampleDrefExplicitLod"};', 'std::vector<uint32_t> promoted_expected;'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', 116, 'CsPretranslate: hit hash=', 'hash, job->translate_us, stats.hits);'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', 130, 'CsPretranslate: miss hash=', 'return std::nullopt;'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', 232, 'CsPretranslate: skipped hash=', '} catch (...) {'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', 226,
     'options.user_data = std::span(user_data).first(job->key.user_data_count);', 'options.dump_ir = job->dump_ir;'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 3991,
     'prepared = pretranslation.Take(params.code, params.hash, input_info,', 'static_cast<uint32_t>(params.user_data.size()));'),
    (C, 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 2230,
     'if (!translation_cache.Load(CacheKey(key), cached)) {', 'return false;'),
    (C, 'src/graphics/shader/recompiler/frontend/cfg/ShaderCFG.cpp', 44, 'EXIT("shader CFG build failed: %s", message.c_str());', 'std::abort();'),
    (C, 'docs/agent/HANDOFF.md', 6457, 'теперь R16-теневые карты (2-байтный формат) остаются ручными', '`OpImageSampleDref*`. Проверка без игры'),
    (C, 'docs/agent/HANDOFF.md', 7269, 'Полная эмуляция PCF для цвета не добавлялась.', '**600 с обычной Vulkan-валидации без фильтров'),
    (C, 'docs/agent/HANDOFF.md', 7287, 'ComparisonDepthTexture (ожидание native Dref для D16)', 'из 03b9643'),
    (C, 'docs/agent/HANDOFF.md', 7731, 'нет PCF в manual depth compare.', '`DumpDraw touches=PS`'),
    (C, 'docs/agent/HANDOFF.md', 7714, 'эталон `shader_cfg_tests` — 0 падений', '`PixelImageSampleLodSelection` починен'),
    ('2f1dafec', 'docs/track-f/register.md', 165, '| Б11 | K4 | наблюдение (проявления нет) |', '| Б14 | K4 | наблюдение (проявления нет) |'),
    ('2f1dafec', 'docs/track-f/register.md', 157, '| Ф3 | K4 | наблюдение по букве п. 228(б)', '| Ф7 | K4 | наблюдение |'),
    (C, 'docs/track-f/register.md', 323, 'Б26г', ''),
]
ok = True
for commit, path, line, anchor, nxt in REFS:
    blob = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', REPO, 'show', commit + ':' + path],
                          capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    a = line - 1 < len(blob) and anchor in blob[line - 1]
    b = line < len(blob) and nxt in blob[line]
    ok &= a and b
    print('%s %s:%s:%d anchor %s +1 %s' % ('OK ' if a and b else 'BAD', commit, path, line, a, b))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
