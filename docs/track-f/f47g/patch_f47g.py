"""F47g (HPP-824, ROADMAP s122 item 740(v)(1)): KYTY_DIAG_F47DT hooks. Usage: python patch_f47g.py <worktree> <draft dir>
Copies src/graphics/host_gpu/renderer/diagF47Dt.{h,cpp} from the draft and inserts the hooks; anchors are whole lines,
each must occur exactly once. CR is stripped before the search and restored when the file had CRLF. Writes LF bytes."""
import os
import shutil
import sys

WT = sys.argv[1]
DRAFT = sys.argv[2]
INC = '#include "graphics/host_gpu/renderer/diagF47Dt.h" // Track F, F47g (KYTY_DIAG_F47DT)\n'


def edit(rel, pairs):
    path = os.path.join(WT, rel)
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            sys.exit('ANCHOR %s: %d occurrences of %r' % (rel, n, old[:80]))
        text = text.replace(old, new)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(path, 'wb').write(text.encode('utf-8'))
    print('patched', rel)


for name in ('diagF47Dt.h', 'diagF47Dt.cpp'):
    rel = 'src/graphics/host_gpu/renderer/' + name
    shutil.copyfile(os.path.join(DRAFT, rel), os.path.join(WT, rel))
    print('copied', rel)

# 1. renderDraw.cpp - the draw (after the pipeline lookup, both outcomes; after its timing marks).
edit('src/graphics/host_gpu/renderer/renderDraw.cpp', [
    ('#include "graphics/host_gpu/renderer/debug.h"\n',
     '#include "graphics/host_gpu/renderer/debug.h"\n' + INC),
    ('\tCommon::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmPipeNs);\n'
     '\tif (pipeline_ptr == nullptr) {\n',
     '\tCommon::FrameStats::PathLap::Mark(Common::FrameStats::Counter::PathEmPipeNs);\n'
     '\t// Track F, F47g (HPP-824, ROADMAP s122 item 740(v)(1)): KYTY_DIAG_F47DT - measurement only, default 0; at 0\n'
     '\t// one test of a flag read once per process. Reads the prepared bindings and the registers, records nothing\n'
     '\t// the draw uses.\n'
     '\tif (DiagF47Dt::On()) {\n'
     '\t\tDiagF47Dt::DrawArgs f47dt;\n'
     '\t\tf47dt.submit_id      = submit_id;\n'
     '\t\tf47dt.draw_name      = draw.Name();\n'
     '\t\tf47dt.index_count    = draw.index_count;\n'
     '\t\tf47dt.instance_count = draw.instance_count;\n'
     '\t\tf47dt.guest_frame    = m_context.GetGpu().GetFrameNum();\n'
     '\t\tf47dt.vs             = &state.vertex_info[0].stage;\n'
     '\t\tf47dt.ps             = state.ps_active ? &state.ps_input_info.stage : nullptr;\n'
     '\t\tf47dt.pixel          = bindings.pixel.has_value() ? &*bindings.pixel : nullptr;\n'
     '\t\tf47dt.colors         = state.color_info;\n'
     '\t\tf47dt.color_count    = state.color_count;\n'
     '\t\tf47dt.depth          = &state.depth_info;\n'
     '\t\tf47dt.pipeline_ready = pipeline_ptr != nullptr;\n'
     '\t\tDiagF47Dt::OnDraw(m_context, buffer, f47dt);\n'
     '\t}\n'
     '\tif (pipeline_ptr == nullptr) {\n'),
])

# 2. pipelineCache.cpp - the finished key of the draw (before the memo / map lookups).
edit('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ('#include "graphics/host_gpu/renderer/pipeline/fixF20.h" // Track F, F42a (KYTY_FIX_F20)\n',
     '#include "graphics/host_gpu/renderer/pipeline/fixF20.h" // Track F, F42a (KYTY_FIX_F20)\n' + INC),
    ('\t// Session 60, B3 (gate "progmemo"): most draws build the key of the previous draw\'s\n'
     '\t// pipeline; entries are never erased, so the pointer found then still names it.\n',
     '\t// Track F, F47g (HPP-824): KYTY_DIAG_F47DT - a thread-local copy of the finished key (measurement only).\n'
     '\tif (DiagF47Dt::On()) {\n'
     '\t\tDiagF47Dt::NoteGraphicsKey(key.static_params, key.rendering);\n'
     '\t}\n'
     '\t// Session 60, B3 (gate "progmemo"): most draws build the key of the previous draw\'s\n'
     '\t// pipeline; entries are never erased, so the pointer found then still names it.\n'),
])

# 2b. pipelineCache.cpp - the PS runtime of the draw (ProgramCache::Get, pixel stage).
edit('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ('\t\t    .read_specialization_memory = ReadShaderGuestMemory,\n'
     '\t\t};\n'
     '\t\tpg_mark(Common::FrameStats::Counter::ProgLapLocalNs);\n',
     '\t\t    .read_specialization_memory = ReadShaderGuestMemory,\n'
     '\t\t};\n'
     '\t\t// Track F, F47g (HPP-824): KYTY_DIAG_F47DT - the plan, base and user data of the PS (measurement only).\n'
     '\t\tif (DiagF47Dt::On() && stage == ShaderType::Pixel) {\n'
     '\t\t\tDiagF47Dt::NotePsRuntime(entry != programs.end() ? &entry->second.resource_plan : nullptr,\n'
     '\t\t\t                         params.Base(), params.user_data.data(), params.user_data.size());\n'
     '\t\t}\n'
     '\t\tpg_mark(Common::FrameStats::Counter::ProgLapLocalNs);\n'),
])

# 3. shaders.cpp - the two conversions of the pipeline creation, for the diagnostic (not called by the pipeline).
edit('src/graphics/host_gpu/renderer/pipeline/shaders.cpp', [
    ('\t\tdefault: EXIT("unknown op: %u\\n", op);\n'
     '\t}\n'
     '\treturn vk::BlendOp::eAdd;\n'
     '}\n',
     '\t\tdefault: EXIT("unknown op: %u\\n", op);\n'
     '\t}\n'
     '\treturn vk::BlendOp::eAdd;\n'
     '}\n'
     '\n'
     '// Track F, F47g (HPP-824, ROADMAP s122 item 740(v)(1)): GetBlendFactor / GetBlendOp for KYTY_DIAG_F47DT\n'
     '// (diagF47Dt.cpp prints the Vulkan blend state of a draw with the conversions the pipeline uses).\n'
     'vk::BlendFactor DiagF47DtBlendFactor(uint32_t factor) {\n'
     '\treturn GetBlendFactor(factor);\n'
     '}\n'
     '\n'
     'vk::BlendOp DiagF47DtBlendOp(uint32_t op) {\n'
     '\treturn GetBlendOp(op);\n'
     '}\n'),
])

# 4. bufferCache.cpp - the source of an image upload, on the branch ObtainBufferForImage returns from.
NOTE = '\t\t\tif (DiagF47Dt::On()) {{ // Track F, F47g\n' \
       '\t\t\t\tDiagF47Dt::NoteImageSource(DiagF47Dt::SrcKind::{k}, vaddr, size, nullptr, nullptr, nullptr, 0);\n' \
       '\t\t\t}}\n'
edit('src/graphics/host_gpu/renderer/cache/bufferCache.cpp', [
    ('#include "graphics/host_gpu/renderer/cache/bufferCache.h"\n',
     '#include "graphics/host_gpu/renderer/cache/bufferCache.h"\n' + INC),
    ('\t\t\tTraceImageUpload(vaddr, size, "owner");\n',
     '\t\t\tTraceImageUpload(vaddr, size, "owner");\n' + NOTE.format(k='Owner')),
    ('\t\tTraceImageUpload(vaddr, size, "gpu-buffer");\n',
     '\t\tTraceImageUpload(vaddr, size, "gpu-buffer");\n' + NOTE.format(k='Gpu').replace('\t\t\t', '\t\t')),
    ('\t\t\tTraceImageUpload(vaddr, size, "import:no-owner");\n',
     '\t\t\tTraceImageUpload(vaddr, size, "import:no-owner");\n' + NOTE.format(k='Import')),
    ('\t\t\tCommon::WaitAsyncCopies(); // Commit flushes the range\n'
     '\t\t}\n'
     '\t}\n'
     '\tm_staging_buffer.Commit();\n',
     '\t\t\tCommon::WaitAsyncCopies(); // Commit flushes the range\n'
     '\t\t}\n'
     '\t\t// Track F, F47g (HPP-824): KYTY_DIAG_F47DT - the staging bytes; a pooled copy on coherent memory is still in\n'
     '\t\t// flight here and is hashed later (never waited for), otherwise the bytes have landed.\n'
     '\t\tif (DiagF47Dt::On()) {\n'
     '\t\t\tDiagF47Dt::NoteImageSource(\n'
     '\t\t\t    pooled && m_staging_buffer.IsCoherent() ? DiagF47Dt::SrcKind::StagingAsync : DiagF47Dt::SrcKind::Staging,\n'
     '\t\t\t    vaddr, size, staging, &m_staging_buffer,\n'
     '\t\t\t    [](const void* ring) { return static_cast<const StreamBuffer*>(ring)->Generation(); },\n'
     '\t\t\t    m_staging_buffer.Generation());\n'
     '\t\t}\n'
     '\t}\n'
     '\tm_staging_buffer.Commit();\n'),
])

# 5. textureCache.cpp / .h - the upload of an image range; a read-only image accessor (GetImage touches the LRU).
edit('src/graphics/host_gpu/renderer/cache/textureCache.cpp', [
    ('#include "graphics/host_gpu/renderer/cache/textureCache.h"\n',
     '#include "graphics/host_gpu/renderer/cache/textureCache.h"\n' + INC),
    ('\t\timage.pending_bytes  = image.pending_levels != 0 ? image.SourceRange().size - std::min(image.SourceRange().size, uploaded) : 0;\n',
     '\t\timage.pending_bytes  = image.pending_levels != 0 ? image.SourceRange().size - std::min(image.SourceRange().size, uploaded) : 0;\n'
     '\t\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, the upload of this range\n'
     '\t\t\tDiagF47Dt::NoteImageUpload(id.index, image.SourceRange().address, image.SourceRange().size, first_level,\n'
     '\t\t\t                           image.info.resources.levels - first_level, image.pending_levels, false);\n'
     '\t\t}\n'),
    ('\tm_frame_pending_bytes += uploaded;\n'
     '\timage.pending_bytes = 0;\n',
     '\tm_frame_pending_bytes += uploaded;\n'
     '\timage.pending_bytes = 0;\n'
     '\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, the completion of a deferred upload\n'
     '\t\tDiagF47Dt::NoteImageUpload(UINT32_MAX, image.SourceRange().address, image.SourceRange().size,\n'
     '\t\t                           image.source_first_level, levels - image.source_first_level, 0, true);\n'
     '\t}\n'),
])
edit('src/graphics/host_gpu/renderer/cache/textureCache.h', [
    ('\t[[nodiscard]] Image&        GetImage(ImageId id) {\n'
     '\t\tauto& image = m_slot_images[id];\n'
     '\t\tTouchImage(image);\n'
     '\t\treturn image;\n'
     '\t}\n',
     '\t[[nodiscard]] Image&        GetImage(ImageId id) {\n'
     '\t\tauto& image = m_slot_images[id];\n'
     '\t\tTouchImage(image);\n'
     '\t\treturn image;\n'
     '\t}\n'
     '\t// Track F, F47g (HPP-824): the image without the LRU touch of GetImage (KYTY_DIAG_F47DT reads only).\n'
     '\t[[nodiscard]] const Image& PeekImage(ImageId id) const { return m_slot_images[id]; }\n'),
])

# 6. pm4Handlers.cpp - raw context register words.
CXEXIT = ('\t\t\tEXIT("unknown cx reg at %05" PRIx32 ": 0x%" PRIx32 "' + chr(92) + 'n", num_dw - dw, cmd_offset);\n'
          '\t\t}\n'
          '\n')
edit('src/graphics/guest_gpu/command_processor/pm4Handlers.cpp', [
    ('#include "graphics/host_gpu/renderer/render.h"\n',
     '#include "graphics/host_gpu/renderer/render.h"\n' + INC),
    ('\t\tif (handled) {\n'
     '\t\t\tfor (uint32_t i = 0; i < num_values; i++) {\n'
     '\t\t\t\tg_hw_ctx_indirect_func[(cmd_offset + i) & (Pm4::CX_NUM - 1)](cp, cmd_offset + i,\n'
     '\t\t\t\t                                                             buffer[1 + i]);\n'
     '\t\t\t}\n'
     '\t\t\treturn num_values + 1u;\n',
     '\t\tif (handled) {\n'
     '\t\t\tfor (uint32_t i = 0; i < num_values; i++) {\n'
     '\t\t\t\tg_hw_ctx_indirect_func[(cmd_offset + i) & (Pm4::CX_NUM - 1)](cp, cmd_offset + i,\n'
     '\t\t\t\t                                                             buffer[1 + i]);\n'
     '\t\t\t}\n'
     '\t\t\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, raw register words\n'
     '\t\t\t\tDiagF47Dt::NoteCtxWrite(&cp.GetCtx(), cmd_offset, buffer + 1, num_values, 1);\n'
     '\t\t\t}\n'
     '\t\t\treturn num_values + 1u;\n'),
    ('\tauto s = pfunc(cp, cmd_id, cmd_offset, buffer + 1, dw);\n'
     '\n'
     '\tEXIT_IF(s == 0);\n'
     '\n'
     '\treturn s + 1;\n',
     '\tauto s = pfunc(cp, cmd_id, cmd_offset, buffer + 1, dw);\n'
     '\n'
     '\tEXIT_IF(s == 0);\n'
     '\n'
     '\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, raw register words\n'
     '\t\tDiagF47Dt::NoteCtxWrite(&cp.GetCtx(), cmd_offset, buffer + 1, s, 0);\n'
     '\t}\n'
     '\n'
     '\treturn s + 1;\n'),
    (CXEXIT +
     '\t\tpfunc(cp, cmd_offset, value);\n'
     '\t}\n'
     '\n'
     '\treturn KYTY_PM4_LEN(cmd_id) - 1u;\n',
     CXEXIT +
     '\t\tpfunc(cp, cmd_offset, value);\n'
     '\t\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, raw register words\n'
     '\t\t\tDiagF47Dt::NoteCtxWrite(&cp.GetCtx(), cmd_offset, &value, 1, 2);\n'
     '\t\t}\n'
     '\t}\n'
     '\n'
     '\treturn KYTY_PM4_LEN(cmd_id) - 1u;\n'),
])

# 7. graphicsRun.cpp - context clear / push / pop and the processor reset.
edit('src/graphics/guest_gpu/graphicsRun.cpp', [
    ('#include "graphics/guest_gpu/graphicsRun.h"\n',
     '#include "graphics/guest_gpu/graphicsRun.h"\n' + INC),
    ('void CommandProcessor::Reset() {\n'
     '\tm_sh_ctx.Reset();\n',
     'void CommandProcessor::Reset() {\n'
     '\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, the register shadow follows the context\n'
     '\t\tDiagF47Dt::NoteCtxOp(&m_ctx, &m_saved_ctx, DiagF47Dt::CtxOp::Reset);\n'
     '\t}\n'
     '\tm_sh_ctx.Reset();\n'),
    ('void CommandProcessor::ApplyContextStateOperation(ContextStateOperation operation) {\n'
     '\tswitch (operation) {\n',
     'void CommandProcessor::ApplyContextStateOperation(ContextStateOperation operation) {\n'
     '\tif (DiagF47Dt::On()) { // Track F, F47g (HPP-824): KYTY_DIAG_F47DT, the register shadow follows the context\n'
     '\t\tDiagF47Dt::NoteCtxOp(&m_ctx, &m_saved_ctx,\n'
     '\t\t                     operation == ContextStateOperation::Clear  ? DiagF47Dt::CtxOp::Clear\n'
     '\t\t                     : operation == ContextStateOperation::Push ? DiagF47Dt::CtxOp::Push\n'
     '\t\t                     : operation == ContextStateOperation::Pop  ? DiagF47Dt::CtxOp::Pop\n'
     '\t\t                                                                 : DiagF47Dt::CtxOp::PushClear);\n'
     '\t}\n'
     '\tswitch (operation) {\n'),
])

# 8. emulator.cpp - the exit line beside FixF20Stat.
X20 = '\tLibs::Graphics::FixF20::PrintExitStat(); // Track F, F42a: "FixF20Stat: when=exit" (KYTY_FIX_F20=1 only)\n'
X47 = '\tLibs::Graphics::DiagF47Dt::PrintExitStat(); // Track F, F47g: "F47dtStat: when=exit" (KYTY_DIAG_F47DT=1 only)\n'
edit('src/emulator.cpp', [
    ('#include "emulator.h"\n', '#include "emulator.h"\n' + INC),
    ('\t' + X20 + '\t\tstd::quick_exit(0);\n', '\t' + X20 + '\t' + X47 + '\t\tstd::quick_exit(0);\n'),
    ('\tLibs::Graphics::WindowRun();\n' + X20, '\tLibs::Graphics::WindowRun();\n' + X20 + X47),
])
# 9. The stand (tests/F47DtStand.cpp) and its target.
shutil.copyfile(os.path.join(DRAFT, 'tests/F47DtStand.cpp'), os.path.join(WT, 'tests/F47DtStand.cpp'))
print('copied tests/F47DtStand.cpp')
edit('CMakeLists.txt', [
    ('add_kyty_full_emulator_test(f29_fault_stand\n'
     '\t"${KYTY_TESTS_DIR}/F29FaultStand.cpp")\n'
     '\n',
     'add_kyty_full_emulator_test(f29_fault_stand\n'
     '\t"${KYTY_TESTS_DIR}/F29FaultStand.cpp")\n'
     '\n' + open(os.path.join(DRAFT, 'cmake_add.txt'), encoding='utf-8').read()),
])
print('ALL PATCHED')
