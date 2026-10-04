# F17a (HPP-525): check of the references of f17a.md (general rule 24(1)): <commit>:<path>:<line> with an anchor and the
# +1 control line.  Usage: python refs_f17a.py <code_commit>   (prints 'N of N' and 'ALL OK')
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
CODE = sys.argv[1]
DOC = '74a87005'
G = 'src/graphics/'
R = G + 'host_gpu/renderer/'
P = G + 'guest_gpu/command_processor/pm4Handlers.cpp'
REFS = [
    (DOC, 'docs/ROADMAP.md', 22160, '(е) **Следующая итерация очереди F — F17 = Ф6, офлайн, без игры и без замка**',
     '(`ShaderInfoCollection.cpp:379`), для которого нет привязанной цели)'),
    (DOC, 'docs/ROADMAP.md', 22166, 'пайплайн, `Location`), идентификаторы сообщений; срабатывали ли пути (1)',
     'сейчас):** (а) эмулятор привязывает каждый слот гостя'),
    (DOC, 'docs/ROADMAP.md', 15093, 'строка `Undefined-Value-ShaderOutputNotConsumed-DynamicRendering` (смещение `0xd05a98`) стоит за форматом',
     '«there is no VkRenderingInfo::pColorAttachments['),
    (DOC, 'docs/track-f/register.md', 162, '| Ф6 | K4 | наблюдение |', '| Б30 | K4 |'),
    (DOC, 'docs/track-f/register.md', 781, '| Ф6 (поправка к §4) | K4 | наблюдение |', ''),
    # guest state
    (CODE, P, 3278, 'g_hw_ctx_indirect_func[Pm4::CB_TARGET_MASK] = [](KYTY_HW_CTX_INDIRECT_ARGS) {', 'cp.GetCtx().SetRenderTargetMask(value);'),
    (CODE, P, 3272, 'g_hw_ctx_indirect_func[Pm4::CB_SHADER_MASK] = [](KYTY_HW_CTX_INDIRECT_ARGS) {', 'cp.GetCtx().SetShaderMask(value);'),
    (CODE, P, 2755, 'base.addr |= static_cast<uint64_t>(value) << 8u;', 'cp.GetCtx().SetColorBase(slot, base);'),
    (CODE, P, 569, 'static_cast<Prospero::ChannelLayout>(KYTY_PM4_GET(buffer[0], CB_COLOR0_INFO, FORMAT));', ''),
    (CODE, R + 'debug.cpp', 19, 'uint32_t render_target_mask_slot(uint32_t mask, uint32_t slot) {', 'return (mask >> (slot * 4u)) & 0x0fu;'),
    # the attachment set of a draw
    (CODE, R + 'renderDraw.cpp', 2878, 'if (ResolveColorTargets(buffer, render_target_slice_offset)) {', 'return false;'),
    (CODE, R + 'renderDraw.cpp', 2884, 'for (uint32_t slot = 0; slot < RENDER_COLOR_ATTACHMENTS_MAX; slot++) {',
     'if (slot == 0 || (render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0 &&'),
    (CODE, R + 'renderDraw.cpp', 2892, 'if (state.color_info[state.color_count].image_id) {', 'state.color_count++;'),
    (CODE, R + 'renderDraw.cpp', 2906, 'if (state.color_count == 0 && !state.depth_info.image_id && !state.ps_active) {', 'LogFramebufferSkip('),
    (CODE, R + 'renderDraw.cpp', 152, 'if (!graphics_debug_dump_enabled()) {', 'return;'),
    (CODE, R + 'renderDraw.cpp', 186, 'LOGF("MrtState[%u]: %s rt_mask=0x%08" PRIx32 " cb_shader_mask=0x%08" PRIx32', ''),
    (CODE, R + 'renderDraw.cpp', 2520, 'const bool  has_color_output = (ctx.GetRenderTargetMask() & sh_regs.m_cbShaderMask) != 0;', ''),
    (CODE, R + 'colorRenderTarget.cpp', 106, 'auto        mask    = render_target_mask_slot(hw.GetRenderTargetMask(), rt_slot);',
     'if (ignore_target_mask && rt.base.addr != 0 && mask == 0) {'),
    (CODE, R + 'colorRenderTarget.cpp', 113, 'if (FastRenderMemoEnabled() && !graphics_debug_dump_enabled() &&', '(rt.base.addr == 0 || mask == 0)) {'),
    (CODE, R + 'colorRenderTarget.cpp', 184, 'if (rt.base.addr == 0 || mask == 0) {', 'if (graphics_debug_dump_enabled()) {'),
    (CODE, R + 'colorRenderTarget.cpp', 189, 'LOGF("RenderColorTarget: no color output slot=%" PRIu32 " base=0x%010" PRIx64', ''),
    (CODE, R + 'colorRenderTarget.cpp', 201, 'if (samples == 0 || rt.attrib.num_samples != rt.attrib.num_fragments) {',
     'EXIT("unsupported render-target sample configuration'),
    (CODE, R + 'colorRenderTarget.cpp', 300, 'const auto target_format =', 'TextureGetRenderTargetFormat(rt.info.format, rt.info.channel_type, rt.info.channel_order);'),
    (CODE, R + 'colorRenderTarget.cpp', 303, 'if (bytes_per_element == 0) {', 'EXIT("render-target format has no valid element size'),
    (CODE, R + 'colorRenderTarget.cpp', 392, 'if (size == 0 || (!volume && size > UINT64_MAX / view.image_layers)) {',
     'EXIT("render-target memory footprint is invalid'),
    (CODE, R + 'colorRenderTarget.cpp', 493, 'r.image_id                 = texture_cache.FindImage(r.desc, exact_format);',
     'r.export_mapping           = target_format.export_mapping;'),
    (CODE, R + 'image/textureCommon.cpp', 137, 'EXIT("unsupported render-target format combination: layout=%u type=%u order=%u', ''),
    (CODE, R + 'cache/textureCache.cpp', 2105, 'if (desc.info.data.Empty()) {', ''),
    (CODE, R + 'cache/textureCache.cpp', 2107, 'return GetNullImage(desc);', ''),
    (CODE, R + 'renderMemo.h', 21, 'inline bool FastRenderMemoEnabled() noexcept {', ''),
    # the host pass and the pipeline
    (CODE, R + 'renderDraw.cpp', 2065, 'EXIT_IF(!target.image_id || target.target_slot >= RENDER_COLOR_ATTACHMENTS_MAX);', ''),
    (CODE, R + 'renderDraw.cpp', 2068, 'state.num_color_attachments = std::max(state.num_color_attachments, target.target_slot + 1);', ''),
    (CODE, R + 'renderDraw.cpp', 2092, 'target.image_id = cache.FindImage(target.desc);', 'BindRenderTarget(target.image_id);'),
    (CODE, R + 'renderDraw.cpp', 2125, 'EXIT_IF(image.backing.samples != target.desc.info.samples || image_view == nullptr);', ''),
    (CODE, R + 'renderDraw.cpp', 2162, 'auto& attachment        = state.color_attachments[target.target_slot];', 'attachment.image_view   = image_view;'),
    (CODE, R + 'context.cpp', 442, 'rendering.colorAttachmentCount = state.num_color_attachments;', 'rendering.pColorAttachments    = colors.data();'),
    (CODE, R + 'pipeline/pipelineCache.cpp', 5330, 'rendering.color_count = std::max(rendering.color_count, slot + 1);',
     'static_params.color_mask[slot] = colors[i].export_mapping.ApplyMask('),
    (CODE, R + 'pipeline/pipelineCache.cpp', 5333, 'rendering.color_formats[slot] = colors[i].desc.view_info.format;', ''),
    (CODE, R + 'pipeline/shaders.cpp', 550, 'color_blend_attachment[i].colorWriteMask =', 'vk::ColorComponentFlags {static_params.color_mask[i]};'),
    (CODE, R + 'pipeline/shaders.cpp', 583, 'dual_src_module = CreateDualSourceVariant(graphics, pixel_program,', ''),
    (CODE, R + 'pipeline/shaders.cpp', 696, 'rendering_info.colorAttachmentCount    = rendering.color_count;',
     'rendering_info.pColorAttachmentFormats = rendering.color_formats.data();'),
    (CODE, R + 'renderDraw.cpp', 535, 'enable[slot] = render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0', ''),
    (CODE, G + 'guest_gpu/gpu_defs.h', 122, '[[nodiscard]] constexpr uint32_t ApplyMask(uint32_t logical_mask) const {', ''),
    # the PS exports
    (CODE, G + 'shader/recompiler/ir/passes/ShaderInfoCollection.cpp', 336, 'if (export_info.en == 0) {', 'continue;'),
    (CODE, G + 'shader/recompiler/ir/passes/ShaderInfoCollection.cpp', 378, 'AddOutput(info, StageOutputKind::Mrt, export_info.index, export_info.index,',
     'fmt::format("out_mrt_{}", export_info.index));'),
    (CODE, G + 'shader/recompiler/backend/spirv/spirvEmitterFlow.cpp', 532,
     'const auto mapping = state.input_info.pixel->target_export_mapping[exp.index];', ''),
    (CODE, G + 'shader/shader.cpp', 330, 'static void ps_check(const HW::PsStageRegisters& ps, const HW::ShaderRegisters& sh) {', ''),
    (CODE, G + 'shader/shader.cpp', 414, 'temporary: ignoring extra CB_SHADER_MASK MRT bits: 0x%08" PRIx32', ''),
    (CODE, G + 'shader/shader.cpp', 833, 'ps_info.target_export_mapping[i] = sh.target_output_mode[i] != 0', ''),
    (CODE, R + 'renderDraw.cpp', 2948, 'for (uint32_t i = 0; i < state.color_count; i++) {',
     'target_export_mapping[state.color_info[i].target_slot] = state.color_info[i].export_mapping;'),
    # rtskip
    (CODE, R + 'renderDraw.cpp', 1462, 'uint32_t RtsRelSkip(uint32_t mask) {', ''),
    (CODE, R + 'renderDraw.cpp', 1572, 'LOGF("RtSkipVerify: MISMATCH frame=%d bits=0x%03x', ''),
    (CODE, R + 'renderDraw.cpp', 3461, '} else if (t_rts != 3 && t_rts_reg) {', 'why = C::RtsXaReg;'),
    (CODE, R + 'renderDraw.cpp', 3484, 'if (t_rts == 1 && t_rts_pa) {', ''),
    (CODE, R + 'renderDraw.cpp', 3490, 'state.color_count = rec->color_count;', 'state.depth_info  = rec->pre_depth;'),
    (CODE, 'src/common/gates.cpp', 436, '{"KYTY_RT_SKIP", "rtskip", 1, 3},', ''),
    # whole-draw exits
    (CODE, R + 'renderDraw.cpp', 5008, 'if (ConsumeMetadataColorOperation(buffer)) {', 'MaterializeBoundTargetDccClears(buffer);'),
    (CODE, R + 'renderDraw.cpp', 5378, 'if (hw.GetColorControl().mode != 3) {', 'return false;'),
    (CODE, R + 'renderDraw.cpp', 3936, 'LOGF("SkipDrawDiagnostic: ps=%016" PRIx64 " after_frame=%d', ''),
    # the sites of the diagnostic
    (CODE, R + 'renderDraw.cpp', 5126, 'const bool prepared  = t_rts == 0 ? PrepareDrawRenderState(buffer, draw, args.render_target_slice_offset, state)',
     ': RtsPlaceA(buffer, draw, args.render_target_slice_offset, state);'),
    (CODE, R + 'renderDraw.cpp', 5142, 'RefreshShaders(buffer, draw, state);', ''),
    (CODE, R + 'renderDraw.cpp', 5314, 'const bool prepared  = t_rts == 0 ? PrepareDrawRenderState(buffer, draw, args.render_target_slice_offset, state)',
     ': RtsPlaceA(buffer, draw, args.render_target_slice_offset, state);'),
    # the layer callback
    (CODE, G + 'presentation/window/vulkanWindow.cpp', 865, 'if (r.enable_validation_layers) {', ''),
    (CODE, G + 'presentation/window/vulkanWindow.cpp', 874, 'LOGF("VK_LAYER_KHRONOS_validation available extension: %s, version = %u', ''),
    (CODE, G + 'presentation/window/vulkanWindow.cpp', 938, 'LOGF_COLOR(severity_style, "[Vulkan][%s][%u]: %s', 'static_cast<uint32_t>(message_types), callback_data->pMessage);'),
]
cache = {}
ok = 0
for commit, path, line, anchor, plus1 in REFS:
    key = (commit, path)
    if key not in cache:
        o = subprocess.run([GIT, '-C', REPO, 'show', commit + ':' + path], capture_output=True)
        cache[key] = o.stdout.decode('utf-8', 'replace').split('\n')
    L = cache[key]
    a = L[line - 1] if line - 1 < len(L) else ''
    b = L[line] if line < len(L) else ''
    good = anchor in a and (plus1 == '' or plus1 in b)
    ok += good
    if not good:
        print('FAIL %s:%s:%d' % (commit, path, line))
        print('   line: ' + a.strip()[:160])
        print('   +1  : ' + b.strip()[:160])
print('%d of %d' % (ok, len(REFS)))
print('ALL OK' if ok == len(REFS) else 'FAILED')
