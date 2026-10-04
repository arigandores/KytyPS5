# Track F, F16d (HPP-521, ROADMAP s122 items 421(g), 427, 433(v)): KYTY_DIAG_F5 / KYTY_DIAG_F6 (default 0, measurement only).
# Applies the source edits to a tree: python patch_f16d_src.py <repo root> [--check]
# Anchors are whole lines (a block = consecutive whole lines); each must occur exactly once. CRLF files are handled
# (\r stripped before the search and restored); output is written with write_bytes. New files come from ./new/.
import os
import shutil
import sys

ROOT = sys.argv[1]
CHECK = "--check" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
R = "src/graphics/host_gpu/renderer/"
INC = '#include "graphics/host_gpu/renderer/diagF5.h"'

EDITS = []  # (path, kind, anchor lines, new lines); kind: after | replace


def after(path, anchor, new):
    EDITS.append((path, "after", anchor if isinstance(anchor, list) else [anchor], new))


def replace(path, old, new):
    EDITS.append((path, "replace", old if isinstance(old, list) else [old], new))


# ---------------------------------------------------------------- textureCache.h
replace(R + "cache/textureCache.h", "\t[[nodiscard]] bool ClearMeta(uint64_t address);", [
    "\t// Track F, F16d (KYTY_DIAG_F5): `f5_refusal` (optional) receives the kind of a refusal of a PendingDcc / Dcc / CMask",
    "\t// address (DiagF5::RefusalDcc / RefusalCmask), only with the knob on; the answer does not depend on it.",
    "\t[[nodiscard]] bool ClearMeta(uint64_t address, uint8_t* f5_refusal = nullptr);",
])

# ---------------------------------------------------------------- textureCache.cpp
T = R + "cache/textureCache.cpp"
after(T, '#include "graphics/host_gpu/renderer/commandScheduler.h"', [INC])
replace(T, [
    "\t\tif (PendingDccFillStale(desc.info.metadata.range.address, metadata,",
    "\t\t                        image.info.data.address)) {",
    "\t\t\tmetadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};",
    "\t\t}",
    "\t\tmetadata.type = MetaDataInfo::Type::Dcc;",
], [
    "\t\tif (PendingDccFillStale(desc.info.metadata.range.address, metadata,",
    "\t\t                        image.info.data.address)) {",
    "\t\t\tmetadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};",
    "\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\tDiagF5::Add(DiagF5::Counter::DccResetStale); // Track F, F16d: the pending fill is dropped (RC6(7))",
    "\t\t\t}",
    "\t\t} else if (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::NoteDccFill(metadata.fill_value); // Track F, F16d: PendingDcc -> Dcc by the stored code (RC3)",
    "\t\t}",
    "\t\tmetadata.type = MetaDataInfo::Type::Dcc;",
])
after(T, "\t\tmetadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};", [
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccResetType); // Track F, F16d: an entry of another type is reset (RC6(7))",
    "\t\t}",
])
replace(T, [
    "\tif (metadata.clear_mask == 0 || image.info.resources.levels != 1 ||",
    "\t    desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) {",
    "\t\treturn;",
    "\t}",
], [
    "\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC4): the render-target path only, and only when the clear mask has a bit",
    "\t// in the layers of this view (first / count as computed for the loop below); each return below is one child of",
    "\t// dcc_rt_pending. Reads locals only.",
    "\tconst bool f5_pend = DiagF5::On() && desc.type == BindingType::RenderTarget && [&] {",
    "\t\tconst bool f5_volume = image.info.IsVolume() && desc.view_info.type == vk::ImageViewType::e3D;",
    "\t\tconst auto f5_first  = f5_volume ? 0u : desc.view_info.base_layer;",
    "\t\tconst auto f5_count  = f5_volume ? std::max(image.info.extent.depth >> desc.view_info.base_level, 1u)",
    "\t\t                                 : desc.view_info.layer_count;",
    "\t\treturn (metadata.clear_mask & DiagF5::ViewLayerBits(f5_first, f5_count)) != 0;",
    "\t}();",
    "\tif (f5_pend) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::DccRtPending);",
    "\t}",
    "\tif (metadata.clear_mask == 0 || image.info.resources.levels != 1 ||",
    "\t    desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) {",
    "\t\tif (f5_pend) [[unlikely]] {",
    "\t\t\tDiagF5::Add(image.info.resources.levels != 1 ? DiagF5::Counter::DccRtSkipLevels",
    "\t\t\t                                             : DiagF5::Counter::DccRtSkipPartial);",
    "\t\t}",
    "\t\treturn;",
    "\t}",
])
replace(T, [
    "\tif (!DecodeDccClearFill(desc, metadata.fill_value, clear.color)) {",
    "\t\treturn;",
    "\t}",
], [
    "\tif (!DecodeDccClearFill(desc, metadata.fill_value, clear.color)) {",
    "\t\tif (f5_pend) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccRtSkipDecode);",
    "\t\t}",
    "\t\treturn;",
    "\t}",
])
replace(T, [
    "\tif (first >= 32 || count > 32 - first) {",
    "\t\treturn;",
    "\t}",
    "\t// The metadata fill covers the complete allocation. Consume each layer only after its",
], [
    "\tif (first >= 32 || count > 32 - first) {",
    "\t\tif (f5_pend) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccRtSkipLayers);",
    "\t\t}",
    "\t\treturn;",
    "\t}",
    "\tif (f5_pend) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::DccRtCleared); // a bit of the view layers is set: the loop below clears it",
    "\t}",
    "\t// The metadata fill covers the complete allocation. Consume each layer only after its",
])
replace(T, [
    "\tif (metadata.fill_value != 0 || metadata.clear_mask == 0 ||",
    "\t    desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) return;",
    "\tvk::ClearValue clear {};",
    "\tif (!DecodePackedColorClear(image.backing.format, desc.info.metadata.cmask_clear_words[0],",
    "\t                           desc.info.metadata.cmask_clear_words[1], clear.color)) return;",
    "\tconst auto& view = desc.view_info;",
    "\tif (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 - view.base_layer) return;",
], [
    "\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC6(1)): a clear-mask bit in the layers of the view; each return below is",
    "\t// one child of cmask_rt_pending. Reads locals only.",
    "\tconst bool f5_pend = DiagF5::On() &&",
    "\t                     (metadata.clear_mask &",
    "\t                      DiagF5::ViewLayerBits(desc.view_info.base_layer, desc.view_info.layer_count)) != 0;",
    "\tif (f5_pend) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::CmaskRtPending);",
    "\t}",
    "\tif (metadata.fill_value != 0 || metadata.clear_mask == 0 ||",
    "\t    desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) {",
    "\t\tif (f5_pend) [[unlikely]] {",
    "\t\t\tDiagF5::Add(metadata.fill_value != 0 ? DiagF5::Counter::CmaskRtSkipValue",
    "\t\t\t                                      : DiagF5::Counter::CmaskRtSkipPartial);",
    "\t\t}",
    "\t\treturn;",
    "\t}",
    "\tvk::ClearValue clear {};",
    "\tif (!DecodePackedColorClear(image.backing.format, desc.info.metadata.cmask_clear_words[0],",
    "\t                           desc.info.metadata.cmask_clear_words[1], clear.color)) {",
    "\t\tif (f5_pend) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::CmaskRtSkipDecode);",
    "\t\t}",
    "\t\treturn;",
    "\t}",
    "\tconst auto& view = desc.view_info;",
    "\tif (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 - view.base_layer) {",
    "\t\tif (f5_pend) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::CmaskRtSkipLayers);",
    "\t\t}",
    "\t\treturn;",
    "\t}",
    "\tif (f5_pend) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::CmaskRtCleared); // a bit of the view layers is set: the loop below clears it",
    "\t}",
])
replace(T, "bool TextureCache::ClearMeta(uint64_t address) {", ["bool TextureCache::ClearMeta(uint64_t address, uint8_t* f5_refusal) {"])
after(T, "\t\t// for FMask/HTile; an arbitrary write must not imply a color fast clear.", [
    "\t\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC2): a refusal of a known metadata address - the parent of the",
    "\t\t// caller's meta_cs_* / meta_dma_*; the kind goes to the caller's local.",
    "\t\tif (DiagF5::On() && found != m_surface_metas.end()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::MetaRefusedKnown);",
    "\t\t\tif (f5_refusal != nullptr) {",
    "\t\t\t\t*f5_refusal = found->second.type == MetaDataInfo::Type::CMask ? DiagF5::RefusalCmask : DiagF5::RefusalDcc;",
    "\t\t\t}",
    "\t\t}",
])
after(T, [
    "\tif (!GuestRange {address, size}.Valid()) {",
    "\t\tEXIT(\"TextureCache: invalid DCC fill range\\n\");",
    "\t}",
], [
    "\tif (DiagF5::On()) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::DccFillAll); // Track F, F16d: every call (line_mismatch_fill, RC3)",
    "\t}",
])
after(T, [
    "\tif (found->second.type == MetaDataInfo::Type::PendingDcc ||",
    "\t    found->second.type == MetaDataInfo::Type::Dcc || found->second.type == MetaDataInfo::Type::CMask) {",
], [
    "\t\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC3): a fill on confirmed DCC, by its code.",
    "\t\tif (DiagF5::On() && found->second.type == MetaDataInfo::Type::Dcc) [[unlikely]] {",
    "\t\t\tDiagF5::NoteDccFill(fill_value);",
    "\t\t}",
])
replace(T, [
    "\t\tm_surface_metas.erase(found);",
    "\t\tBumpMetaEpoch();",
    "\t\treturn false;",
], [
    "\t\tm_surface_metas.erase(found);",
    "\t\tBumpMetaEpoch();",
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccResetStale); // Track F, F16d: the pending fill is dropped (RC6(7))",
    "\t\t}",
    "\t\treturn false;",
])
after(T, "\tfound->second.type                 = MetaDataInfo::Type::Dcc;", [
    "\tif (DiagF5::On()) [[unlikely]] {",
    "\t\tDiagF5::NoteDccFill(found->second.fill_value); // Track F, F16d: PendingDcc -> Dcc by the stored code (RC3)",
    "\t}",
])

# ---------------------------------------------------------------- colorRenderTarget.cpp
C = R + "colorRenderTarget.cpp"
after(C, '#include "graphics/host_gpu/renderer/debug.h"', [INC])
after(C, "\tconst bool has_dcc        = rt.info.dcc_compression_enable && rt.dcc_addr.addr != 0;", [
    "\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t// Track F, F16d (KYTY_DIAG_F5, item 427(d)): a full resolution (memo miss) of an active slot; of those with DCC.",
    "\t\tDiagF5::Add(DiagF5::Counter::RtResolves);",
    "\t\tif (has_dcc) {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccRt);",
    "\t\t}",
    "\t}",
])

# ---------------------------------------------------------------- descriptors.cpp
D = R + "pipeline/descriptors.cpp"
after(D, '#include "graphics/host_gpu/renderer/renderContext.h"', [INC])
replace(D, [
    "\tif (mask == 0) {",
    "\t\treturn;",
    "\t}",
    "\tif (t_sp_dcc_armed) {",
], [
    "\tif (mask == 0) {",
    "\t\treturn;",
    "\t}",
    "\tif (DiagF5::On()) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::DccMatPending); // Track F, F16d (item 427(b), RC4): a pending layer mask",
    "\t}",
    "\tif (t_sp_dcc_armed) {",
])
replace(D, [
    "\tif (!decoded) {",
    "\t\treturn;",
    "\t}",
    "\tCommon::DrawStat::Mark(Common::DrawStat::ImgUp | Common::DrawStat::Meta);",
], [
    "\tif (!decoded) {",
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccMatUndecoded); // Track F, F16d: the clear is not performed (B)",
    "\t\t}",
    "\t\treturn;",
    "\t}",
    "\tif (DiagF5::On()) [[unlikely]] {",
    "\t\tDiagF5::Add(DiagF5::Counter::DccMatCleared);",
    "\t}",
    "\tCommon::DrawStat::Mark(Common::DrawStat::ImgUp | Common::DrawStat::Meta);",
])
after(D, [
    "\t\tif (rt.base.addr != 0 && rt.cmask.addr != 0 && rt.info.cmask_fast_clear_enable &&",
    "\t\t    !rt.info.dcc_compression_enable) {",
], [
    "\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\tDiagF5::Add(DiagF5::Counter::CmaskFce); // Track F, F16d (item 427(b), RC5): FCE on a CMASK target",
    "\t\t\t}",
])
replace(D, [
    "\t\t\t\tFixB42Note(b42, applied, color.desc.info.extent.width, color.desc.info.extent.height, rt.cmask.addr,",
    "\t\t\t\t           rt.clear_word0.word0, rt.clear_word1.word1);",
    "\t\t\t}",
    "\t\t\tcontinue;",
], [
    "\t\t\t\tFixB42Note(b42, applied, color.desc.info.extent.width, color.desc.info.extent.height, rt.cmask.addr,",
    "\t\t\t\t           rt.clear_word0.word0, rt.clear_word1.word1);",
    "\t\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\t\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC5): after FixB42Note, by the computed b42 / applied.",
    "\t\t\t\t\tDiagF5::Add(b42.kind == FixB42Kind::Drawn ? DiagF5::Counter::CmaskFceDrawn",
    "\t\t\t\t\t            : applied                      ? DiagF5::Counter::CmaskFceB42",
    "\t\t\t\t\t                                           : DiagF5::Counter::CmaskFceUnapplied);",
    "\t\t\t\t}",
    "\t\t\t} else if (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\t// Track F, F16d: FixB42Probe answered None - the first of its tests that holds, in its order (the descriptor",
    "\t\t\t\t// is not modified on this path); none of them - no tracked covering fill of 0 at the CMASK address.",
    "\t\t\t\tconst auto& f5_info = color.desc.info;",
    "\t\t\t\tDiagF5::Add(!color.image_id                                      ? DiagF5::Counter::CmaskFceNoImage",
    "\t\t\t\t            : f5_info.metadata.kind != ImageMetadataKind::None ? DiagF5::Counter::CmaskFceMeta",
    "\t\t\t\t            : f5_info.samples != 1                             ? DiagF5::Counter::CmaskFceMsaa",
    "\t\t\t\t            : (f5_info.resources.levels != 1 || f5_info.IsVolume() ||",
    "\t\t\t\t               (f5_info.extent.width % 1024u == 0 && f5_info.extent.height % 1024u == 0))",
    "\t\t\t\t                ? DiagF5::Counter::CmaskFceLayout",
    "\t\t\t\t                : DiagF5::Counter::CmaskFceNoFill);",
    "\t\t\t}",
    "\t\t\tcontinue;",
])
replace(D, [
    "\t\tif (rt.base.addr == 0 || rt.dcc_addr.addr == 0) {",
    "\t\t\tcontinue;",
    "\t\t}",
    "\t\tconst auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr);",
    "\t\tif (!id) {",
], [
    "\t\tif (rt.base.addr == 0 || rt.dcc_addr.addr == 0) {",
    "\t\t\tcontinue;",
    "\t\t}",
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccFce); // Track F, F16d (item 427(b), RC6(4)): FCE on a DCC slot",
    "\t\t}",
    "\t\tconst auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr);",
    "\t\tif (!id) {",
    "\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\tDiagF5::Add(DiagF5::Counter::DccFceNoImage);",
    "\t\t\t}",
])
replace(D, [
    "\t\tMaterializeDeferredDccClear(buffer, id);",
    "\t}",
    "}",
], [
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DccFceImage);",
    "\t\t}",
    "\t\tMaterializeDeferredDccClear(buffer, id);",
    "\t}",
    "}",
])

# ---------------------------------------------------------------- render.h
H = R + "render.h"
after(H, "struct RenderExecutorTestAccess;", [
    "namespace DiagF5 {",
    "struct CsRefusals; // Track F, F16d (diagF5.h)",
    "} // namespace DiagF5",
])
replace(H, [
    "\t[[nodiscard]] bool        TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,",
    "\t                                                     const CommandBuffer&          buffer);",
    "\t[[nodiscard]] bool TryConsumeComputeImageClear(const ShaderComputeInputInfo& input,",
    "\t                                              CommandBuffer& command, uint32_t group_x,",
    "\t                                              uint32_t group_y, uint32_t group_z, uint32_t mode);",
], [
    "\t// Track F, F16d (KYTY_DIAG_F5): `f5_refusals` / `f5_tracked` - non-null only with the knob on (renderCompute.cpp).",
    "\t[[nodiscard]] bool        TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,",
    "\t                                                     const CommandBuffer&          buffer,",
    "\t                                                     DiagF5::CsRefusals*           f5_refusals = nullptr);",
    "\t[[nodiscard]] bool TryConsumeComputeImageClear(const ShaderComputeInputInfo& input,",
    "\t                                              CommandBuffer& command, uint32_t group_x,",
    "\t                                              uint32_t group_y, uint32_t group_z, uint32_t mode,",
    "\t                                              uint64_t* f5_tracked = nullptr);",
])

# ---------------------------------------------------------------- renderCompute.cpp
P = R + "renderCompute.cpp"
after(P, '#include "graphics/host_gpu/renderer/commandRecorder.h"', [INC])
replace(P, [
    "bool RenderExecutor::TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,",
    "                                                const CommandBuffer&          buffer) {",
], [
    "bool RenderExecutor::TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,",
    "                                                const CommandBuffer&          buffer,",
    "                                                DiagF5::CsRefusals*           f5_refusals) {",
])
replace(P, "\t\t\t\tif (cache.ClearMeta(descriptor.Base48())) {", [
    "\t\t\t\tuint8_t f5_refusal = DiagF5::RefusalNone; // Track F, F16d: written by ClearMeta only with KYTY_DIAG_F5 on",
    "\t\t\t\tif (cache.ClearMeta(descriptor.Base48(), f5_refusals != nullptr ? &f5_refusal : nullptr)) {",
])
replace(P, [
    "\t\t\t\t} else {",
    "\t\t\t\t\tother_writes = true;",
    "\t\t\t\t}",
], [
    "\t\t\t\t} else {",
    "\t\t\t\t\tother_writes = true;",
    "\t\t\t\t\tif (f5_refusal != DiagF5::RefusalNone && f5_refusals->count < DiagF5::CsRefusals::Max) [[unlikely]] {",
    "\t\t\t\t\t\tf5_refusals->addresses[f5_refusals->count++] = descriptor.Base48();",
    "\t\t\t\t\t}",
    "\t\t\t\t}",
])
replace(P, [
    "bool RenderExecutor::TryConsumeComputeImageClear(const ShaderComputeInputInfo& input,",
    "                                                CommandBuffer& command, uint32_t group_x,",
    "                                                uint32_t group_y, uint32_t group_z, uint32_t mode) {",
], [
    "bool RenderExecutor::TryConsumeComputeImageClear(const ShaderComputeInputInfo& input,",
    "                                                CommandBuffer& command, uint32_t group_x,",
    "                                                uint32_t group_y, uint32_t group_z, uint32_t mode,",
    "                                                uint64_t* f5_tracked) {",
])
after(P, "\t\tcache.TrackDccFill(descriptor.Base48(), size, packed_clear);", [
    "\t\tif (f5_tracked != nullptr) [[unlikely]] {",
    "\t\t\t*f5_tracked = descriptor.Base48(); // Track F, F16d: the fill tracked at this address (meta_cs_tracked)",
    "\t\t}",
])
replace(P, [
    "\tif (!indirect && !floor_clear_skip && TryConsumeComputeMetaClear(input_info, buffer)) {",
    "\t\t// Session 100, the L3 debt of session 98 (ROADMAP.md:1406): bf_clr_skip is a shape",
    "\t\t// census of ELIGIBLE dispatches and over-counts.  This counts the consumed ones, in",
    "\t\t// BOTH arms and behind no gate, so the base arm has a real denominator at last.",
    "\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::ClearShortcutMeta, 1);",
    "\t\tResetBindings();",
    "\t\treturn;",
    "\t}",
    "\tif (!indirect && !floor_clear_skip &&",
    "\t    TryConsumeComputeImageClear(input_info, buffer, thread_group_x, thread_group_y,",
    "\t                                thread_group_z, mode)) {",
    "\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::ClearShortcutImage, 1);",
    "\t\tResetBindings();",
    "\t\treturn;",
    "\t}",
], [
    "\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC2): the written buffers ClearMeta refused as known metadata, and the",
    "\t// address TryConsumeComputeImageClear tracked a fill at - non-null pointers only with the knob on; a refused",
    "\t// address without that fill in this dispatch is meta_cs_untracked.",
    "\tconst bool         f5_on = DiagF5::On();",
    "\tDiagF5::CsRefusals f5_refusals;",
    "\tuint64_t           f5_tracked = 0;",
    "\tif (!indirect && !floor_clear_skip &&",
    "\t    TryConsumeComputeMetaClear(input_info, buffer, f5_on ? &f5_refusals : nullptr)) {",
    "\t\tif (f5_on) [[unlikely]] {",
    "\t\t\tDiagF5::NoteCsRefusals(f5_refusals, 0);",
    "\t\t}",
    "\t\t// Session 100, the L3 debt of session 98 (ROADMAP.md:1406): bf_clr_skip is a shape",
    "\t\t// census of ELIGIBLE dispatches and over-counts.  This counts the consumed ones, in",
    "\t\t// BOTH arms and behind no gate, so the base arm has a real denominator at last.",
    "\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::ClearShortcutMeta, 1);",
    "\t\tResetBindings();",
    "\t\treturn;",
    "\t}",
    "\tif (!indirect && !floor_clear_skip &&",
    "\t    TryConsumeComputeImageClear(input_info, buffer, thread_group_x, thread_group_y,",
    "\t                                thread_group_z, mode, f5_on ? &f5_tracked : nullptr)) {",
    "\t\tif (f5_on) [[unlikely]] {",
    "\t\t\tDiagF5::NoteCsRefusals(f5_refusals, 0);",
    "\t\t}",
    "\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::ClearShortcutImage, 1);",
    "\t\tResetBindings();",
    "\t\treturn;",
    "\t}",
    "\tif (f5_on) [[unlikely]] {",
    "\t\tDiagF5::NoteCsRefusals(f5_refusals, f5_tracked);",
    "\t}",
])
after(P, "\tif (!indirect && (thread_group_x == 0 || thread_group_y == 0 || thread_group_z == 0)) {", [
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::ZeroDisp); // Track F, F16d (member 6, reference)",
    "\t\t}",
])

# ---------------------------------------------------------------- bufferCache.cpp
B = R + "cache/bufferCache.cpp"
after(B, '#include "graphics/host_gpu/renderer/commandScheduler.h"', [INC])
replace(B, "\t(void)m_texture_cache.ClearMeta(vaddr);", [
    "\t// Track F, F16d (KYTY_DIAG_F5, item 427(b), RC2): a DMA fill never tracks a fill - a refusal of known metadata with a",
    "\t// clear value is meta_dma_untracked. `f5_refusal` stays RefusalNone with the knob off.",
    "\tuint8_t f5_refusal = DiagF5::RefusalNone;",
    "\t(void)m_texture_cache.ClearMeta(vaddr, DiagF5::On() ? &f5_refusal : nullptr);",
    "\tif (f5_refusal != DiagF5::RefusalNone) [[unlikely]] {",
    "\t\tDiagF5::NoteDmaRefusal(f5_refusal, value);",
    "\t}",
])

# ---------------------------------------------------------------- debug.cpp
G = R + "debug.cpp"
after(G, '#include "graphics/guest_gpu/hardwareContext.h"', [INC])
after(G, "\t\tif (rt.info.cmask_fast_clear_enable || rt.info.dcc_compression_enable) {", [
    "\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\tDiagF5::Add(DiagF5::Counter::RtcheckMeta); // Track F, F16d (RC8): the condition of the line below",
    "\t\t\t}",
])
after(G, "\t\tif (rt.info.round_mode) {", [
    "\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\t// Track F, F16d (member 3, reference): the targets with ROUND_MODE by channel type.",
    "\t\t\t\tDiagF5::Add(rt.info.channel_type == Prospero::ChannelType::kUNorm   ? DiagF5::Counter::RoundUnorm",
    "\t\t\t\t            : rt.info.channel_type == Prospero::ChannelType::kFloat ? DiagF5::Counter::RoundFloat",
    "\t\t\t\t                                                                    : DiagF5::Counter::RoundOther);",
    "\t\t\t}",
])

# ---------------------------------------------------------------- depthRenderTarget.cpp
Z = R + "depthRenderTarget.cpp"
after(Z, '#include "graphics/host_gpu/renderer/debug.h"', [INC])
after(Z, "\tif (attachment_unbound) {", [
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::DsUnbound); // Track F, F16d (member 4, reference)",
    "\t\t\tif (rc.depth_clear_enable || rc.stencil_clear_enable) {",
    "\t\t\t\tDiagF5::Add(DiagF5::Counter::DsUnboundClear);",
    "\t\t\t}",
    "\t\t}",
])

# ---------------------------------------------------------------- pm4Handlers.cpp
M = "src/graphics/guest_gpu/command_processor/pm4Handlers.cpp"
after(M, '#include "graphics/host_gpu/lodStats.h"', [INC])
after(M, "\tg_hw_uc_indirect_func[Pm4::GE_STEREO_CNTL] = [](KYTY_HW_UC_INDIRECT_ARGS) {", [
    "\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\tDiagF5::Add(DiagF5::Counter::StereoWrites); // Track F, F16d (member 5, reference)",
    "\t\t\tif (value != 0) {",
    "\t\t\t\tDiagF5::Add(DiagF5::Counter::StereoNonzero);",
    "\t\t\t}",
    "\t\t}",
])

# ---------------------------------------------------------------- pipelineCache.cpp
Q = R + "pipeline/pipelineCache.cpp"
after(Q, '#include "graphics/host_gpu/renderer/renderContext.h"', [INC])
after(Q, "\t\t\t\tpg_mark(Common::FrameStats::Counter::ProgLapPermFindNs);", [
    "\t\t\t\tif (DiagF5::On()) [[unlikely]] {",
    "\t\t\t\t\t// Track F, F16d (KYTY_DIAG_F5, item 427(v), reference): a permutation found by specialization whose",
    "\t\t\t\t\t// images include an FMASK image (read as the identity fragment map). Memo hits do not reach here.",
    "\t\t\t\t\tif (std::ranges::any_of(permutation->specialization.images,",
    "\t\t\t\t\t                        [](const auto& image) { return image.fmask; })) {",
    "\t\t\t\t\t\tDiagF5::Add(DiagF5::Counter::FmaskRead);",
    "\t\t\t\t\t}",
    "\t\t\t\t}",
])

# ---------------------------------------------------------------- renderDraw.cpp
W = R + "renderDraw.cpp"
after(W, '#include "graphics/host_gpu/renderer/renderMemo.h"', [INC])
after(W, [
    "\tuint64_t prog_memo_serial = 0;",
    "};",
], [
    "",
    "// Track F, F16d (KYTY_DIAG_F6, ROADMAP s122 item 433(v)): one host draw at a recording site after the",
    "// PrepareDrawRenderState / RtsPlaceA fork - the guest slots of the host attachments and the MRT exports of the pixel",
    "// program by guest index (ShaderInfo::outputs, kind Mrt; the dual-source variant keeps the guest index). Reads only.",
    "static void DiagF6NoteDraw(const CommandBuffer& buffer, const DrawRenderState& state, bool mesh, bool indirect,",
    "                           bool indexed) {",
    "\tstd::array<uint32_t, RENDER_COLOR_ATTACHMENTS_MAX> host_slots {};",
    "\tconst uint32_t host_count = std::min<uint32_t>(state.color_count, RENDER_COLOR_ATTACHMENTS_MAX);",
    "\tfor (uint32_t i = 0; i < host_count; i++) {",
    "\t\thost_slots[i] = state.color_info[i].target_slot;",
    "\t}",
    "\tconst auto&              ps        = state.ps_input_info.stage;",
    "\tconst bool               ps_on     = state.ps_active && ps;",
    "\tstd::array<uint32_t, 16> mrt       = {};",
    "\tuint32_t                 mrt_count = 0;",
    "\tif (ps_on) {",
    "\t\tfor (const auto& output: ps.program->info.outputs) {",
    "\t\t\tif (output.kind == ShaderRecompiler::IR::StageOutputKind::Mrt && mrt_count < mrt.size()) {",
    "\t\t\t\tmrt[mrt_count++] = output.index;",
    "\t\t\t}",
    "\t\t}",
    "\t}",
    "\tconst auto kind = mesh       ? DiagF6::DrawKind::Mesh",
    "\t                 : indirect ? DiagF6::DrawKind::Indirect",
    "\t                 : indexed  ? DiagF6::DrawKind::Indexed",
    "\t                            : DiagF6::DrawKind::Auto;",
    "\tDiagF6::NoteDraw(buffer.GetRegisters(), host_slots.data(), host_count, ps_on, mrt.data(), mrt_count, kind);",
    "}",
])
after(W, "\t\tGpuMarkerTop(tail, gpu_marker);", [
    "\t\tif (DiagF6::On()) [[unlikely]] {",
    "\t\t\tDiagF6NoteDraw(buffer, state, mesh_active, emit_info.indirect_buffer != nullptr, draw.IsIndexed()); // F16d",
    "\t\t}",
])
after(W, "\tGpuMarkerTop(vk_buffer, gpu_marker);", [
    "\tif (DiagF6::On()) [[unlikely]] {",
    "\t\tDiagF6NoteDraw(buffer, state, mesh_active, emit_info.indirect_buffer != nullptr, draw.IsIndexed()); // F16d",
    "\t}",
])

# ---------------------------------------------------------------- videoOut.cpp
V = "src/graphics/presentation/videoOut.cpp"
after(V, '#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"', [INC])
after(V, "\tGraphics::GpuTimeProfiler::SetFrame(static_cast<uint32_t>(r.cfg->flip_status.count));", [
    "\t// Track F, F16d (KYTY_DIAG_F5 / KYTY_DIAG_F6, item 427(e)): the flip tick - a line on growth, at most every 2 s.",
    "\tGraphics::DiagF5::Tick(static_cast<uint32_t>(r.cfg->flip_status.count));",
    "\tGraphics::DiagF6::Tick(static_cast<uint32_t>(r.cfg->flip_status.count));",
])

# ---------------------------------------------------------------- vulkanWindow.cpp
K = "src/graphics/presentation/window/vulkanWindow.cpp"
after(K, '#include "graphics/host_gpu/vulkanCommon.h"', [INC])
after(K, [
    "\t\tgraphics.max_fragment_dual_src_attachments = properties2.properties.limits.maxFragmentDualSrcAttachments;",
    "\t}",
], [
    "\t// Track F, F16d (ROADMAP s122 items 421(g), 433(v)): \"DiagF5: mode=1\" / \"DiagF6: mode=1\" once, before the guest runs.",
    "\t(void)DiagF5::LogMode();",
    "\t(void)DiagF6::LogMode();",
])

NEW_FILES = [("diagF5.h", R + "diagF5.h"), ("diagF5.cpp", R + "diagF5.cpp")]


def find_block(lines, block):
    hits = []
    n = len(block)
    for i in range(len(lines) - n + 1):
        if lines[i:i + n] == block:
            hits.append(i)
    return hits


def main():
    by_file = {}
    for e in EDITS:
        by_file.setdefault(e[0], []).append(e)
    ok = True
    for path, edits in by_file.items():
        full = os.path.join(ROOT, path)
        raw = open(full, "rb").read()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8").replace("\r\n", "\n")
        lines = text.split("\n")
        for (_, kind, anchor, new) in edits:
            hits = find_block(lines, anchor)
            if len(hits) != 1:
                print("ANCHOR %s x%d: %s | %r" % (kind, len(hits), path, anchor[0][:90]))
                ok = False
                continue
            i = hits[0]
            if kind == "after":
                lines[i + len(anchor):i + len(anchor)] = new
            else:
                lines[i:i + len(anchor)] = new
        out = "\n".join(lines)
        if crlf:
            out = out.replace("\n", "\r\n")
        if not CHECK:
            open(full, "wb").write(out.encode("utf-8"))
        print("%s %s (%d edits)" % ("checked" if CHECK else "patched", path, len(edits)))
    for src, dst in NEW_FILES:
        full = os.path.join(ROOT, dst)
        if os.path.exists(full):
            print("EXISTS %s" % dst)
            ok = False
            continue
        if not CHECK:
            open(full, "wb").write(open(os.path.join(HERE, "new", src), "rb").read().replace(b"\r\n", b"\n"))
        print("%s %s" % ("would add" if CHECK else "added", dst))
    print("PATCH OK" if ok else "PATCH FAILED")
    return 0 if ok else 1


sys.exit(main())
