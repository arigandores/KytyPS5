import subprocess, sys

REPO = 'C:/kyty/KytyPS5'
# (id, commit, path, anchor substring) - the line is found by the anchor; printed with the +1 line
REFS = [
    ('A1', '810909e3', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'if (size > (16u << 20)) {'),
    ('A2', '810909e3', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'BufferCache::ExactWriteSeq BufferCache::LastGpuWriteSeqExact('),
    ('A3', '810909e3', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'if (ring->second.count > ExactRing::K && oldest > since) {'),
    ('A4', '810909e3', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'if (DiagF5::ExactRingOn()) [[unlikely]] {'),
    ('A5', '810909e3', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', '		NoteGpuWrite(vaddr, size);'),
    ('A6', '810909e3', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 'DiagF5Id::NoteBufferAccess(vaddr, size);'),
    ('B1', '810909e3', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'const auto since = std::max(before.fill_seq, DiagF5Id::FillSeq(e.dcc));'),
    ('B2', '810909e3', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'const auto exact = buffers.LastGpuWriteSeqExact(e.dcc, e.dcc_size, since);'),
    ('B3', '810909e3', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'e.cpu_mod        = buffers.IsRegionCpuModified(e.dcc, e.dcc_size) ? 1 : 0;'),
    ('B4', '810909e3', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'DiagF5::On() ? &f5_cmu : nullptr); // Track F, F16k'),
    ('B5', '810909e3', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'F5IdNoteFceMiss(cache, m_context.GetBufferCache(), slot, rt, f5id_before, f5id_miss);'),
    ('C1', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'm_f5id_stamp_address = address;'),
    ('C2', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'if (m_f5id_stamp_address != 0) [[unlikely]] {'),
    ('C3', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', '	const bool cpu_written = m_buffer_cache.IsRegionCpuModified(address, meta.fill_size);'),
    ('C4', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', '		if (cpu_written) {'),
    ('C5', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {'),
    ('C6', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'F5CmuScope(bool fce, DiagF5::CmuEvent* out)'),
    ('C7', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'PrepareCmaskClear(id, desc, fce_materialize, f5cmu); // Track F, F16k'),
    ('C8', '810909e3', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'void TextureCache::F5IdMetaSnap(uint64_t address, DiagF5Id::MetaSnap* out) {'),
    ('D1', '810909e3', 'src/graphics/host_gpu/renderer/renderCompute.cpp', 'cache.TrackDccFill(descriptor.Base48(), size, packed_clear);'),
    ('D2', '810909e3', 'src/graphics/host_gpu/renderer/renderCompute.cpp', 'f5id.Class(DiagF5Id::CsClass::Exec, f5_tracked);'),
    ('D3', '810909e3', 'src/graphics/host_gpu/renderer/renderCompute.cpp', 'DiagF5::Add(DiagF5::Counter::ZeroDisp); // Track F, F16d'),
    ('D4', '810909e3', 'src/graphics/host_gpu/renderer/renderCompute.cpp', 'Common::FrameStats::Add(Common::FrameStats::Counter::BindFloorSkipDrop, 1);'),
    ('D5', '810909e3', 'src/graphics/host_gpu/renderer/renderCompute.cpp', '		m_context.GetTextureCache().StampPendingDccFill();'),
    ('E1', '810909e3', 'src/graphics/host_gpu/memoryTracker.h', '[[nodiscard]] uint64_t RangeWriteEpoch(uint64_t vaddr, uint64_t size) noexcept {'),
    ('E2', '810909e3', 'tests/ShaderRecompilerComputeTests.cpp', 'The test memory was written by the CPU (memset): a read acquisition uploads it'),
    ('E3', '810909e3', 'src/graphics/host_gpu/renderer/diagF5.cpp', 'const bool id_cs  = cnt[kImgClear] + cnt[kMetaClear]'),
    ('E4', '810909e3', 'src/graphics/host_gpu/renderer/diagF5.cpp', '    "f5cmu_kept",'),
    ('E5', '810909e3', 'src/graphics/host_gpu/renderer/diagF5.cpp', 'static const bool on = FixCmuOn() || DiagF5Id::On();'),
    ('E6', '810909e3', 'CMakeLists.txt', '-D SHADER_CACHE_EXTRA_FILES='),
    ('R1', 'c0789a34', 'docs/ROADMAP.md', '(д) **Правило чтения тегов `f5id_*`'),
    ('R2', 'c0789a34', 'docs/ROADMAP.md', '(е) **Пара свидетеля ветви 1'),
    ('R3', 'b6858d6d', 'docs/ROADMAP.md', '495. **Звено F16k трека F'),
    ('R4', '470c54cf', 'docs/track-f/f16k.md', '- `m_f5id_stamp_address` / `m_f5id_stamp_size`'),
]

bad = 0
for rid, commit, path, anchor in REFS:
    text = subprocess.run(['git', '-C', REPO, 'show', f'{commit}:{path}'], capture_output=True).stdout.decode('utf-8')
    lines = text.split('\n')
    hits = [i for i, l in enumerate(lines) if anchor in l]
    if len(hits) != 1:
        print(f'{rid} BAD hits={len(hits)} {commit}:{path} [{anchor}]')
        bad += 1
        continue
    i = hits[0]
    nxt = lines[i + 1].strip() if i + 1 < len(lines) else '<eof>'
    print(f'{rid} {commit}:{path}:{i + 1} | {lines[i].strip()[:110]} | +1: {nxt[:90]}')
print('ALL OK' if bad == 0 else f'BAD {bad}')
