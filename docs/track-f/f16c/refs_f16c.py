# F16c (HPP-520): every code reference of the review - anchor on the line and the +1 line, at 887825c7.
import subprocess, sys
C = '887825c7'
R = 'src/graphics/host_gpu/renderer/'
refs = [
 (R+'colorRenderTarget.cpp', 113, 'if (FastRenderMemoEnabled() && !graphics_debug_dump_enabled() &&'),
 (R+'colorRenderTarget.cpp', 133, 'if (memo_slot->valid && memo_slot->extra == memo_extra && memo_slot->regs == memo_regs) {'),
 (R+'colorRenderTarget.cpp', 164, 'return;'),
 (R+'colorRenderTarget.cpp', 431, 'const bool has_dcc        = rt.info.dcc_compression_enable && rt.dcc_addr.addr != 0;'),
 (R+'colorRenderTarget.cpp', 434, '(void)TileGetDccSize('),
 (R+'colorRenderTarget.cpp', 441, '} else if (rt.info.cmask_fast_clear_enable && rt.cmask.addr != 0 && samples == 1 &&'),
 (R+'debug.cpp', 210, 'if (rt.info.fmask_compression_enable) {'),
 (R+'debug.cpp', 223, 'if (rt.info.cmask_fast_clear_enable || rt.info.dcc_compression_enable) {'),
 (R+'debug.cpp', 856, 'const auto  rt_slot = render_target_first_bound_slot(buffer);'),
 (R+'debug.cpp', 879, 'RtCheck(rt);'),
 (R+'renderDraw.cpp', 2887, 'ResolveRenderColorTarget(buffer, state.color_info[state.color_count],'),
 (R+'renderDraw.cpp', 5008, 'if (ConsumeMetadataColorOperation(buffer)) {'),
 (R+'renderDraw.cpp', 5072, 'hw_check(buffer);'),
 (R+'renderDraw.cpp', 5295, 'hw_check(buffer);'),
 (R+'renderDraw.cpp', 5390, 'ResolveRenderColorTarget(buffer, src, render_target_slice_offset, 0, true, true);'),
 (R+'pipeline/descriptors.cpp', 3541, 'if (code == 0x20) {'),
 (R+'pipeline/descriptors.cpp', 3578, 'if (!decoded) {'),
 (R+'pipeline/descriptors.cpp', 3596, 'const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, 0,'),
 (R+'pipeline/descriptors.cpp', 3665, 'FixB42Hit FixB42Probe(TextureCache& cache, const HW::RenderTarget& rt, const RenderColorInfo& color) {'),
 (R+'pipeline/descriptors.cpp', 3688, 'if (fill.b42_draw_seq > fill.b42_fill_seq) {'),
 (R+'pipeline/descriptors.cpp', 3769, 'ResolveRenderColorTarget(buffer, color, 0, slot, true, true);'),
 (R+'pipeline/descriptors.cpp', 3772, 'if (b42.kind == FixB42Kind::Hit && FixB42Enabled()) {'),
 (R+'pipeline/descriptors.cpp', 3810, 'if (!id) {'),
 (R+'pipeline/descriptors.cpp', 6498, 'MaterializeDeferredDccClear(buffer, descriptors.images[i].image_id, image);'),
 (R+'cache/textureCache.cpp', 1893, 'if (PendingDccFillStale(desc.info.metadata.range.address, metadata,'),
 (R+'cache/textureCache.cpp', 1898, '} else if (metadata.type != MetaDataInfo::Type::Dcc) {'),
 (R+'cache/textureCache.cpp', 1916, 'if (metadata.clear_mask == 0 || image.info.resources.levels != 1 ||'),
 (R+'cache/textureCache.cpp', 1924, 'if (!DecodeDccClearFill(desc, metadata.fill_value, clear.color)) {'),
 (R+'cache/textureCache.cpp', 1936, 'if (first >= 32 || count > 32 - first) {'),
 (R+'cache/textureCache.cpp', 2002, 'if (metadata.fill_value != 0 || metadata.clear_mask == 0 ||'),
 (R+'cache/textureCache.cpp', 2005, 'if (!DecodePackedColorClear(image.backing.format, desc.info.metadata.cmask_clear_words[0],'),
 (R+'cache/textureCache.cpp', 2008, 'if (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 - view.base_layer) return;'),
 (R+'cache/textureCache.cpp', 2297, 'PrepareDccClear(id, desc);'),
 (R+'cache/textureCache.cpp', 2420, 'PrepareDccClear(id, desc);'),
 (R+'cache/textureCache.cpp', 3184, 'bool TextureCache::ClearMeta(uint64_t address) {'),
 (R+'cache/textureCache.cpp', 3188, 'found->second.type == MetaDataInfo::Type::Dcc || found->second.type == MetaDataInfo::Type::CMask) {'),
 (R+'cache/textureCache.cpp', 3204, 'void TextureCache::TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value) {'),
 (R+'cache/textureCache.cpp', 3227, 'const auto found = m_surface_metas.try_emplace(address).first;'),
 (R+'cache/textureCache.h', 188, 'Type     type       = Type::PendingDcc;'),
 (R+'cache/textureCache.h', 312, 'TrackingSpinLock                                  m_lock;'),
 (R+'renderCompute.cpp', 85, 'if ((!resource.written || resource.read) && cache.IsMeta(descriptor.Base48())) {'),
 (R+'renderCompute.cpp', 103, 'if (cache.ClearMeta(descriptor.Base48())) {'),
 (R+'renderCompute.cpp', 114, 'other_writes = true;'),
 (R+'renderCompute.cpp', 245, 'cache.TrackDccFill(descriptor.Base48(), size, packed_clear);'),
 (R+'renderCompute.cpp', 248, '"GraphicsRenderDispatchDirect: metadata fill shader=0x%016" PRIx64'),
 (R+'renderCompute.cpp', 551, 'if (!indirect && !floor_clear_skip && TryConsumeComputeMetaClear(input_info, buffer)) {'),
 (R+'renderCompute.cpp', 560, 'TryConsumeComputeImageClear(input_info, buffer, thread_group_x, thread_group_y,'),
 (R+'renderCompute.cpp', 936, 'if (!indirect && (thread_group_x == 0 || thread_group_y == 0 || thread_group_z == 0)) {'),
 (R+'cache/bufferCache.cpp', 2262, '(void)m_texture_cache.ClearMeta(vaddr);'),
 (R+'depthRenderTarget.cpp', 355, 'if (attachment_unbound) {'),
 ('src/graphics/host_gpu/regionManager.h', 38, 'EXIT("recursive region tracking lock\\n");'),
 ('src/graphics/guest_gpu/command_processor/pm4Handlers.cpp', 4014, 'g_hw_uc_indirect_func[Pm4::GE_STEREO_CNTL] = [](KYTY_HW_UC_INDIRECT_ARGS) {'),
 ('src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 599, 'image.fmask             = Prospero::IsFmaskTextureFormat(format);'),
 ('src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp', 1197, 'if (specialization.images[memory.resource].fmask) {'),
 ('src/generate_version.cmake', 43, 'set(KYTY_SHADER_SOURCE_HASH "unknown")'),
 ('CMakeLists.txt', 156, '-D SHADER_CACHE_EXTRA_FILES='),
]
ok = True
cache = {}
for path, line, anchor in refs:
    if path not in cache:
        txt = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', C + ':' + path], capture_output=True).stdout
        cache[path] = txt.decode('utf-8', 'replace').replace('\r', '').split('\n')
    L = cache[path]
    a = L[line - 1].strip() if line - 1 < len(L) else ''
    b = L[line].strip() if line < len(L) else ''
    good = anchor.strip() in a
    ok &= good
    print(('OK  ' if good else 'BAD ') + C + ':' + path + ':' + str(line) + ' | ' + a[:110] + ' | +1: ' + b[:90])
print('refs', len(refs))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
