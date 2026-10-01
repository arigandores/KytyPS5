# F4a2 (HPP-346, ROADMAP s122 p.262(b)): KYTY_FIX_DUALSRC=1 - pipelines with SRC1 blend factors get a fragment
# module variant with Location 1 -> Location 0 Index 1 (dualSrcBlend.h). Files outside the translation signature set.
# Anchors are whole lines; each must occur exactly once; CR stripped before search and restored after.
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/KytyPS5'
NL = chr(10)


def patch(rel, edits):
    p = ROOT + '/' + rel
    raw = open(p, 'rb').read().decode('utf-8')
    crlf = (chr(13) + NL) in raw
    s = raw.replace(chr(13), '')
    for anchor, new, where in edits:
        a = NL.join(anchor) + NL
        n = s.count(NL + a)
        if n != 1:
            print('ANCHOR COUNT', n, rel, repr(anchor[0]))
            sys.exit(1)
        b = NL.join(new) + NL
        if where == 'after':
            s = s.replace(NL + a, NL + a + b, 1)
        elif where == 'before':
            s = s.replace(NL + a, NL + b + a, 1)
        else:
            s = s.replace(NL + a, NL + b, 1)
    if crlf:
        s = s.replace(NL, chr(13) + NL)
    open(p, 'wb').write(s.encode('utf-8'))
    print('patched', rel, 'crlf' if crlf else 'lf')


# 1. GraphicContext: the device state the pipeline creation reads.
patch('src/graphics/host_gpu/graphicContext.h', [
    (['\tbool                               provoking_vertex_last_enabled         = false;'],
     ['\t// Track F, F4a2 (HPP-346, ROADMAP s122 p.262(b)): dualSrcBlend enabled on the device (KYTY_FIX_DUALSRC=1 and',
      '\t// supported) and its limit; CreatePipelineInternal builds the Location 0 Index 1 variant of the pixel module.',
      '\tbool                               dual_src_blend_enabled                = false;',
      '\tuint32_t                           max_fragment_dual_src_attachments     = 0;'],
     'after'),
])

# 2. vulkanWindow.cpp: publish the switch and the limit (the log line of F4a stays byte-equal).
patch('src/graphics/presentation/window/vulkanWindow.cpp', [
    (['\t\tLOGF("DualSrcBlend: supported=%d enabled=%d\\n", dual_src_supported ? 1 : 0,',
      '\t\t     dual_src_enabled ? 1 : 0);'],
     ['\t\t// F4a2 (HPP-346, p.262(b)): read by CreatePipelineInternal for the Location 0 Index 1 variant.',
      '\t\tgraphics.dual_src_blend_enabled            = dual_src_enabled;',
      '\t\tgraphics.max_fragment_dual_src_attachments = properties2.properties.limits.maxFragmentDualSrcAttachments;'],
     'after'),
])

# 3. ShaderProgram: a view of the permutation's SPIR-V.
patch('src/graphics/host_gpu/renderer/pipeline/pipelineCache.h', [
    (['struct ShaderProgram {',
      '\tuint64_t         id     = 0;',
      '\tvk::ShaderModule module = nullptr;'],
     ['struct ShaderProgram {',
      '\tuint64_t         id     = 0;',
      '\tvk::ShaderModule module = nullptr;',
      '\t// Track F, F4a2 (HPP-346): the SPIR-V the module was created from (Permutation::spirv; empty when the',
      '\t// translation cache is off), read only by CreatePipelineInternal under KYTY_FIX_DUALSRC=1.',
      '\tconst std::vector<uint32_t>* spirv = nullptr;'],
     'replace'),
])

# 4. pipelineCache.cpp: set the view at the three sites where a permutation enters `permutations`.
patch('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    (['\tstatic void AdoptDmaLayout(Permutation& permutation) {',
      '\t\tif (DmaLayoutMode()) [[unlikely]] {',
      '\t\t\tpermutation.dma_layout = DmaLayoutInject(permutation.program);',
      '\t\t}',
      '\t}'],
     ['',
      '\t// Track F, F4a2 (HPP-346, ROADMAP s122 p.262(b)): the handle points at the permutation\'s own SPIR-V, set',
      '\t// at the same three sites as AdoptDmaLayout, right after the push_back and before the handle is indexed or',
      '\t// handed out. The element never moves: deque::push_back does not relocate elements, and moving the',
      '\t// SourceEntry (try_emplace of a local source) moves the deque, which keeps pointers to its elements',
      '\t// (LWG 2321); retired sources are never freed. `spirv` is not written again after this point.',
      '\tstatic void AdoptSpirvView(Permutation& permutation) {',
      '\t\tpermutation.handle.spirv = &permutation.spirv;',
      '\t}'],
     'after'),
    (['\t\t\tAdoptDmaLayout(source.permutations.back()); // session 102, KYTY_DMA_LAYOUT',
      '\t\t}',
      '\t\tsource.from_cache = true;',
      '\t\tentry             = programs.try_emplace(key, std::move(source)).first;'],
     ['\t\t\tAdoptDmaLayout(source.permutations.back()); // session 102, KYTY_DMA_LAYOUT',
      '\t\t\tAdoptSpirvView(source.permutations.back()); // track F, F4a2',
      '\t\t}',
      '\t\tsource.from_cache = true;',
      '\t\tentry             = programs.try_emplace(key, std::move(source)).first;'],
     'replace'),
    (['\t\tAdoptDmaLayout(entry->second.permutations.back()); // session 102, KYTY_DMA_LAYOUT'],
     ['\t\tAdoptSpirvView(entry->second.permutations.back()); // track F, F4a2'],
     'after'),
    (['\t\t\t\tAdoptDmaLayout(source.permutations.back()); // session 102, KYTY_DMA_LAYOUT'],
     ['\t\t\t\tAdoptSpirvView(source.permutations.back()); // track F, F4a2'],
     'after'),
])

# 5. shaders.cpp: the variant in CreatePipelineInternal (the one function of the game path and of precache).
patch('src/graphics/host_gpu/renderer/pipeline/shaders.cpp', [
    (['#include "graphics/host_gpu/renderer/debug.h"'],
     ['#include "graphics/host_gpu/renderer/pipeline/dualSrcBlend.h"'],
     'after'),
    (['#include <limits>'],
     ['#include <mutex>'],
     'after'),
    (['#include <string>'],
     ['#include <unordered_set>'],
     'after'),
    (['// NOLINTNEXTLINE(readability-function-cognitive-complexity)',
      'void CreatePipelineInternal(GraphicContext& graphics, PipelineCache::Pipeline& pipeline,',
      '                            const PipelineRenderingState&          rendering,'],
     ['// Track F, F4a2 (HPP-346, ROADMAP s122 p.262(b)): the blend factors that read the second source.',
      'static bool IsSecondSourceFactor(vk::BlendFactor factor) {',
      '\treturn factor == vk::BlendFactor::eSrc1Color || factor == vk::BlendFactor::eOneMinusSrc1Color ||',
      '\t       factor == vk::BlendFactor::eSrc1Alpha || factor == vk::BlendFactor::eOneMinusSrc1Alpha;',
      '}',
      '',
      '// One "patched" and one "skip" line per PS hash for the whole run (pipelines are created on the draw,',
      '// worker and precache threads).',
      'static bool DualSourceFirstLine(uint64_t ps_hash, bool patched) {',
      '\tstatic std::mutex                   mutex;',
      '\tstatic std::unordered_set<uint64_t> seen[2];',
      '\tstd::lock_guard                     lock(mutex);',
      '\treturn seen[patched ? 1 : 0].insert(ps_hash).second;',
      '}',
      '',
      '// KYTY_FIX_DUALSRC=1 and a blended attachment with a SRC1 factor: the fragment module of this pipeline only,',
      '// with the output at Location 1 rewritten to Location 0 Index 1 (DualSrcBlend::RewriteLocation1ToIndex1).',
      '// nullptr: the pipeline keeps the translated module (skip line with the reason). The caller destroys the',
      '// returned module after vkCreateGraphicsPipelines. Not salted by KYTY_PIPELINE_SALT.',
      'static vk::ShaderModule CreateDualSourceVariant(GraphicContext& graphics, const ShaderProgram& pixel_program,',
      '                                                uint64_t ps_hash, uint32_t color_count) {',
      '\tstd::vector<uint32_t> words;',
      '\tconst char*           reason = nullptr;',
      '\tif (color_count > graphics.max_fragment_dual_src_attachments) {',
      '\t\treason = "attachments";',
      '\t} else if (pixel_program.spirv == nullptr || pixel_program.spirv->empty()) {',
      '\t\treason = "no_spirv";',
      '\t} else if (const auto outcome = DualSrcBlend::RewriteLocation1ToIndex1(*pixel_program.spirv, words);',
      '\t           outcome != DualSrcBlend::Outcome::Patched) {',
      '\t\treason = DualSrcBlend::OutcomeName(outcome);',
      '\t}',
      '\tif (reason != nullptr) {',
      '\t\tif (DualSourceFirstLine(ps_hash, false)) {',
      '\t\t\tLOGF("DualSrcBlend: skip ps=%016" PRIx64 " reason=%s\\n", ps_hash, reason);',
      '\t\t}',
      '\t\treturn nullptr;',
      '\t}',
      '\tconst auto module = CompileSPV(words, graphics.device);',
      '\tif (DualSourceFirstLine(ps_hash, true)) {',
      '\t\tLOGF("DualSrcBlend: patched ps=%016" PRIx64 "\\n", ps_hash);',
      '\t}',
      '\treturn module;',
      '}',
      ''],
     'before'),
    (['\tif (ps_active) {',
      '\t\tshader_stages[shader_stage_count++] = {.stage  = vk::ShaderStageFlagBits::eFragment,'],
     ['\tconst uint32_t ps_stage_index = shader_stage_count; // F4a2: the fragment stage, when ps_active'],
     'before'),
    (['\tvk::Bool32 color_write_enable[RENDER_COLOR_ATTACHMENTS_MAX] = {};'],
     ['\t// Track F, F4a2 (HPP-346, ROADMAP s122 p.262(b)): the game path and precache both create here.',
      '\tvk::ShaderModule dual_src_module = nullptr;',
      '\tif (graphics.dual_src_blend_enabled && ps_active) {',
      '\t\tbool second_source = false;',
      '\t\tfor (uint32_t i = 0; i < rendering.color_count; i++) {',
      '\t\t\tconst auto& a = color_blend_attachment[i];',
      '\t\t\tsecond_source |= a.blendEnable == VK_TRUE &&',
      '\t\t\t                 (IsSecondSourceFactor(a.srcColorBlendFactor) ||',
      '\t\t\t                  IsSecondSourceFactor(a.dstColorBlendFactor) ||',
      '\t\t\t                  IsSecondSourceFactor(a.srcAlphaBlendFactor) ||',
      '\t\t\t                  IsSecondSourceFactor(a.dstAlphaBlendFactor));',
      '\t\t}',
      '\t\tif (second_source) {',
      '\t\t\tdual_src_module = CreateDualSourceVariant(graphics, pixel_program,',
      '\t\t\t                                          ps_input_info->stage.program->shader_hash,',
      '\t\t\t                                          rendering.color_count);',
      '\t\t\tif (dual_src_module != nullptr) {',
      '\t\t\t\tshader_stages[ps_stage_index].module = dual_src_module;',
      '\t\t\t}',
      '\t\t}',
      '\t}',
      ''],
     'before'),
    (['\tif (tess_eval_shader_module != nullptr) {',
      '\t\tgraphics.device.destroyShaderModule(tess_eval_shader_module, nullptr);',
      '\t}',
      '}'],
     ['\tif (tess_eval_shader_module != nullptr) {',
      '\t\tgraphics.device.destroyShaderModule(tess_eval_shader_module, nullptr);',
      '\t}',
      '\tif (dual_src_module != nullptr) {',
      '\t\tgraphics.device.destroyShaderModule(dual_src_module, nullptr);',
      '\t}',
      '}'],
     'replace'),
])
print('ALL PATCHED')
