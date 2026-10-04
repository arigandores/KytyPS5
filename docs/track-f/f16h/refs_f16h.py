#!/usr/bin/env python3
# F16h (HPP-580): every code reference of docs/track-f/f16h.md - the line of `git show <commit>:<path>` holds the anchor.
# Log references: the 0-based line of the log holds the anchor (read as a stream, stops at the largest line asked).
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = 'cc096dbf'
R = 'src/graphics/host_gpu/renderer/'
CODE = [
    (R + 'renderCompute.cpp', 73, 'bool RenderExecutor::TryConsumeComputeMetaClear('),
    (R + 'renderCompute.cpp', 87, 'if ((!resource.written || resource.read) && cache.IsMeta(descriptor.Base48()))'),
    (R + 'renderCompute.cpp', 92, 'if (!program.info.has_bitwise_xor) {'),
    (R + 'renderCompute.cpp', 106, 'if (cache.ClearMeta(descriptor.Base48()'),
    (R + 'renderCompute.cpp', 117, 'other_writes = true;'),
    (R + 'renderCompute.cpp', 126, 'return cleared_metadata && !other_writes;'),
    (R + 'renderCompute.cpp', 128, 'return false;'),
    (R + 'renderCompute.cpp', 131, 'bool ResolveComputeBufferFill('),
    (R + 'renderCompute.cpp', 229, 'if (!ResolveComputeBufferFill('),
    (R + 'renderCompute.cpp', 252, 'cache.TrackDccFill(descriptor.Base48(), size, packed_clear);'),
    (R + 'renderCompute.cpp', 579, 'if (!indirect && !floor_clear_skip &&'),
    (R + 'renderCompute.cpp', 583, 'DiagF5::NoteCsRefusals(f5_refusals, 0);'),
    (R + 'renderCompute.cpp', 586, 'ResetBindings();'),
    (R + 'renderCompute.cpp', 1191, 'm_context.GetTextureCache().StampPendingDccFill();'),
    (R + 'renderCompute.cpp', 1217, 'm_context.GetTextureCache().StampPendingDccFill();'),
    (R + 'renderDraw.cpp', 5044, 'MaterializeBoundTargetDccClears(buffer);'),
    (R + 'renderDraw.cpp', 5271, 'MaterializeBoundTargetDccClears(buffer);'),
    (R + 'diagF5.cpp', 311, 'void NoteCsRefusals(const CsRefusals& refusals, uint64_t tracked_address) {'),
    (R + 'pipeline/descriptors.cpp', 3142, 'if (descriptor.MetaCompress() && descriptor.MetaAddr() != 0) {'),
    (R + 'pipeline/descriptors.cpp', 3143, 'AdoptPendingDccForTexture(id, descriptor.MetaAddr() << 8u);'),
    (R + 'pipeline/descriptors.cpp', 3269, 'AdoptPendingDccForTexture(memo_slot.image_id, meta_address);'),
    (R + 'pipeline/descriptors.cpp', 3500, 'image.info.metadata.kind != ImageMetadataKind::Dcc) {'),
    (R + 'pipeline/descriptors.cpp', 3509, 'mask                  = cache.MetaClearMask(address, &fill) & layer_mask;'),
    (R + 'pipeline/descriptors.cpp', 3517, 'if (mask == 0) {'),
    (R + 'pipeline/descriptors.cpp', 3675, 'FixB42Hit FixB42Probe(TextureCache& cache, const HW::RenderTarget& rt, const RenderColorInfo& color) {'),
    (R + 'pipeline/descriptors.cpp', 3771, 'void RenderExecutor::MaterializeBoundTargetDccClears(CommandBuffer& buffer) {'),
    (R + 'pipeline/descriptors.cpp', 3776, 'if (rt.base.addr != 0 && rt.cmask.addr != 0 && rt.info.cmask_fast_clear_enable &&'),
    (R + 'pipeline/descriptors.cpp', 3785, 'if (b42.kind == FixB42Kind::Hit && FixB42Enabled()) {'),
    (R + 'pipeline/descriptors.cpp', 3811, 'applied = after.found && after.cmask && after.fill_value == 0 &&'),
    (R + 'pipeline/descriptors.cpp', 3818, 'DiagF5::Add(b42.kind == FixB42Kind::Drawn ? DiagF5::Counter::CmaskFceDrawn'),
    (R + 'pipeline/descriptors.cpp', 3836, 'if (rt.base.addr == 0 || rt.dcc_addr.addr == 0) {'),
    (R + 'pipeline/descriptors.cpp', 3842, 'const auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr);'),
    (R + 'pipeline/descriptors.cpp', 3843, 'if (!id) {'),
    (R + 'pipeline/descriptors.cpp', 3859, 'MaterializeDeferredDccClear(buffer, id);'),
    (R + 'pipeline/descriptors.cpp', 6537, 'MaterializeDeferredDccClear(buffer, descriptors.images[i].image_id, image);'),
    (R + 'cache/textureCache.cpp', 1869, 'void TextureCache::PrepareDccClear(ImageId id, const ImageDesc& desc) {'),
    (R + 'cache/textureCache.cpp', 1894, 'if (PendingDccFillStale(desc.info.metadata.range.address, metadata,'),
    (R + 'cache/textureCache.cpp', 1976, 'for (uint32_t layer = first; layer < first + count;) {'),
    (R + 'cache/textureCache.cpp', 1995, 'void TextureCache::PrepareCmaskClear(ImageId id, const ImageDesc& desc) {'),
    (R + 'cache/textureCache.cpp', 2023, 'if (PendingDccFillStale(desc.info.metadata.range.address, metadata, image.info.data.address)) {'),
    (R + 'cache/textureCache.cpp', 2024, 'metadata = MetaDataInfo {};'),
    (R + 'cache/textureCache.cpp', 2026, 'metadata.type = MetaDataInfo::Type::CMask;'),
    (R + 'cache/textureCache.cpp', 2045, 'if (metadata.fill_value != 0 || metadata.clear_mask == 0 ||'),
    (R + 'cache/textureCache.cpp', 2071, 'for (uint32_t layer = view.base_layer; layer < view.base_layer + view.layer_count; ++layer) {'),
    (R + 'cache/textureCache.cpp', 2624, 'bool TextureCache::ClearImageFromBuffer(CommandBuffer& command, uint64_t address, uint64_t size,'),
    (R + 'cache/textureCache.cpp', 3194, 'bool TextureCache::IsMeta(uint64_t address) {'),
    (R + 'cache/textureCache.cpp', 3201, 'TextureCache::MetaFillQuery TextureCache::QueryMetaFill(uint64_t address, ImageId image) {'),
    (R + 'cache/textureCache.cpp', 3249, 'if (found == m_surface_metas.end() || found->second.type == MetaDataInfo::Type::PendingDcc ||'),
    (R + 'cache/textureCache.cpp', 3300, 'const auto found = m_surface_metas.try_emplace(address).first;'),
    (R + 'cache/textureCache.cpp', 3307, 'found->second.clear_mask = found->second.type == MetaDataInfo::Type::CMask'),
    (R + 'cache/textureCache.cpp', 3328, 'void TextureCache::StampPendingDccFill() {'),
    (R + 'cache/textureCache.cpp', 3343, 'bool TextureCache::PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,'),
    (R + 'cache/textureCache.cpp', 3352, 'if (!stale_check || meta.type != MetaDataInfo::Type::PendingDcc || meta.fill_seq == 0) {'),
    (R + 'cache/textureCache.cpp', 3355, 'const auto last_seq    = m_buffer_cache.LastGpuWriteSeq(address, meta.fill_size, false);'),
    (R + 'cache/textureCache.cpp', 3356, 'const bool cpu_written = m_buffer_cache.IsRegionCpuModified(address, meta.fill_size);'),
    (R + 'cache/textureCache.cpp', 3372, 'ImageId TextureCache::FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address) {'),
    (R + 'cache/textureCache.cpp', 3404, 'if (candidates == 1 && AdoptPendingDccForTexture(candidate, metadata_address)) {'),
    (R + 'cache/textureCache.cpp', 3410, 'bool TextureCache::AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address) {'),
    (R + 'cache/textureCache.cpp', 3424, 'if (found == m_surface_metas.end() || found->second.type != MetaDataInfo::Type::PendingDcc) {'),
    (R + 'cache/textureCache.cpp', 3429, 'if (PendingDccFillStale(metadata_address, found->second, image->info.data.address)) {'),
    (R + 'cache/bufferCache.cpp', 1735, 'NoteGpuWrite(vaddr, size);'),
    (R + 'cache/bufferCache.cpp', 2849, 'void BufferCache::NoteGpuWrite(uint64_t vaddr, uint64_t size) {'),
    (R + 'cache/bufferCache.cpp', 2863, 'uint64_t BufferCache::LastGpuWriteSeq(uint64_t vaddr, uint64_t size, bool include_large) const {'),
    (R + 'cache/bufferCache.h', 453, 'static constexpr uint32_t HotBucketBits = 16;'),
    (R + 'cache/bufferCache.h', 455, 'm_bucket_write_seq;'),
]
L = 'C:/kyty/f287/f16f/log_f5_ef.txt'
LOG = [
    (16366, b'metadata fill shader=0xa572ee17a880e71c addr=0x000000056d898000'),
    (16370, b'metadata fill shader=0xa572ee17a880e71c addr=0x000000056c058000 size=0x0000000000006000 value=0x00000000'),
    (16372, b'addr=0x000000056d8ac000 size=0x000000000000c000'),
    (16388, b'addr=0x000000056c05e000 size=0x0000000000002000'),
    (16390, b'addr=0x00000005637f0000 size=0x0000000000008000 value=0x00000000'),
    (16508, b'Push marker: Resolve Cmask for lighting'),
    (16511, b'no image for slot=0 base=0x0000000510d10000 dcc=0x000000056d898000'),
    (16514, b'RenderColorTarget: slot=0 addr=0x0512570000'),
    (16516, b'dcc=0x000000056c058000 fill=0x00000000 size=0x6000 seq=5 last=11'),
    (16518, b'extent=1920x1080 cmask=0x56c058000 clear=70e270e2/00000000'),
    (16688, b'addr=0x0510d10000 type=9 fmt=71 extent=1920x1080'),
    (16691, b'image=0x0000000510d10000 dcc=0x000000056d898000 fill=0x20202020 size=0x14000 seq=3 last=6'),
    (17076, b'MaterializeDeferredDccClear: image=0x0000000510d10000 dcc=0x000000056d898000 code=0x20'),
    (17078, b'hit=2 applied=1 drawn=0 rearm=1'),
    (19590, b'dcc=0x000000057075c000 fill=0x00000000 size=0x9000 seq=188 last=189'),
    (19592, b'extent=2432x1368 cmask=0x57075c000'),
    (27701, b'dcc=0x0000000570b1b000 fill=0x00000000 size=0x9000 seq=452 last=453'),
    (40610, b'dcc=0x0000000570ff6000 fill=0x00000000 size=0x10000 seq=715 last=716'),
    (220376, b'Level has started: enemy_final'),
    (297370, b'stale pending DCC fill ignored'),
]
ok = True
cache = {}
for path, line, anchor in CODE:
    if path not in cache:
        cache[path] = subprocess.run([GIT, '-C', REPO, 'show', C + ':' + path], capture_output=True, check=True).stdout.decode('utf-8', 'replace').split('\n')
    text = cache[path][line - 1]
    good = anchor in text
    ok &= good
    print(('OK  ' if good else 'BAD ') + C + ':' + path + ':' + str(line))
want = {n: a for n, a in LOG}
last = max(want)
with open(L, 'rb') as f:
    for n, row in enumerate(f):
        if n in want:
            good = want[n] in row
            ok &= good
            print(('OK  ' if good else 'BAD ') + 'log_f5_ef.txt[0-based ' + str(n) + ']')
        if n >= last:
            break
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
