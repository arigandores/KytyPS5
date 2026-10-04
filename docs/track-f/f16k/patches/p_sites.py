"""F16k (HPP-583, ROADMAP s122 item 492(v), (g)): the sites of KYTY_FIX_F5CMU / KYTY_DIAG_F5ID.

    python p_sites.py <repo root>

Files: cache/bufferCache.h/.cpp, cache/textureCache.h/.cpp, pipeline/descriptors.cpp, renderCompute.cpp, render.h,
guest_gpu/graphicsRun.cpp, presentation/window/vulkanWindow.cpp, presentation/window/screenshot.cpp. LF in, LF out (a CR
is an error). Every anchor is whole lines and must occur exactly once. No file of the translation signature set
(CMakeLists.txt:156: src/graphics/shader/**, shaderTranslationCache.cpp, gpu_format.h, gpu_defs.h, imageInfo.h) is
touched - checked at the end.
"""
import sys

ROOT = sys.argv[1]
R = ROOT + "/src/graphics/host_gpu/renderer/"
FILES = {}


def load(path):
    if path not in FILES:
        data = open(path, "rb").read()
        if b"\r" in data:
            raise SystemExit("CR in " + path)
        FILES[path] = data.decode("utf-8")
    return FILES[path]


def sub(path, old, new):
    t = load(path)
    n = t.count(old)
    if n != 1:
        raise SystemExit("anchor count %d in %s for %r" % (n, path, old[:100]))
    FILES[path] = t.replace(old, new)


SIGNATURE = ("/src/graphics/shader/", "shaderTranslationCache.cpp", "gpu_format.h", "gpu_defs.h", "imageInfo.h")

# ---------------------------------------------------------------- bufferCache.h
P = R + "cache/bufferCache.h"
sub(P, r'''	uint64_t                                m_gpu_write_seq   = 0;
	uint64_t                                m_large_write_seq = 0;
	void                   NoteGpuWrite(uint64_t vaddr, uint64_t size);
''', r'''	uint64_t                                m_gpu_write_seq   = 0;
	uint64_t                                m_large_write_seq = 0;
	// Track F, F16k (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID, ROADMAP s122 item 492(v)(3)): the exact write journal - the last K
	// GPU writes {lo, hi, seq} of each 64 KB bucket, beside m_bucket_write_seq and written by NoteGpuWrite in the same
	// place (the GuestGpu thread), only while DiagF5::ExactRingOn() (read once: the journal holds every write of the
	// process or none). A write larger than 16 MB touches no bucket and no ring, as before. Read only by
	// LastGpuWriteSeqExact; no decision of the cache reads it.
	struct ExactWrite {
		uint64_t lo  = 0;
		uint64_t hi  = 0;
		uint64_t seq = 0;
	};
	struct ExactRing {
		static constexpr uint32_t K = 8;
		std::array<ExactWrite, K> writes {};
		uint64_t                  count = 0; // writes recorded in this bucket; writes[(count - 1) % K] is the last
	};
	std::unordered_map<uint64_t, ExactRing> m_bucket_write_ring;
	void                   NoteGpuWrite(uint64_t vaddr, uint64_t size);
''')
sub(P, r'''	[[nodiscard]] uint64_t LastGpuWriteSeq(uint64_t vaddr, uint64_t size, bool include_large = true) const;
''', r'''	[[nodiscard]] uint64_t LastGpuWriteSeq(uint64_t vaddr, uint64_t size, bool include_large = true) const;
	// Track F, F16k (item 492(v)(3)): the exact form of LastGpuWriteSeq(vaddr, size, false) after `since`. `seq` - the
	// newest recorded write with seq > since that crosses [vaddr, vaddr + size) (0 - none). `fallback` - a bucket of the
	// range has a write newer than `since` while its ring holds K writes all newer than `since` and older ones were
	// dropped (the history since `since` may be incomplete): only the bucket answer is safe there. Needs
	// DiagF5::ExactRingOn(); a bucket without a ring (not possible then) is a fallback.
	struct ExactWriteSeq {
		uint64_t seq      = 0;
		bool     fallback = false;
	};
	[[nodiscard]] ExactWriteSeq LastGpuWriteSeqExact(uint64_t vaddr, uint64_t size, uint64_t since) const;
''')

# ---------------------------------------------------------------- bufferCache.cpp
P = R + "cache/bufferCache.cpp"
sub(P, r'''	const auto first = vaddr >> HotBucketBits;
	const auto last  = (vaddr + size - 1) >> HotBucketBits;
	for (auto bucket = first; bucket <= last; bucket++) {
		m_bucket_write_seq[bucket] = seq;
	}
}
''', r'''	const auto first = vaddr >> HotBucketBits;
	const auto last  = (vaddr + size - 1) >> HotBucketBits;
	for (auto bucket = first; bucket <= last; bucket++) {
		m_bucket_write_seq[bucket] = seq;
	}
	// Track F, F16k (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID, item 492(v)(3)): the exact journal of the same buckets.
	if (DiagF5::ExactRingOn()) [[unlikely]] {
		for (auto bucket = first; bucket <= last; bucket++) {
			auto& ring                              = m_bucket_write_ring[bucket];
			ring.writes[ring.count % ExactRing::K] = {vaddr, vaddr + size, seq};
			ring.count++;
		}
	}
}

BufferCache::ExactWriteSeq BufferCache::LastGpuWriteSeqExact(uint64_t vaddr, uint64_t size, uint64_t since) const {
	ExactWriteSeq answer {};
	const auto    first = vaddr >> HotBucketBits;
	const auto    last  = (vaddr + size - 1) >> HotBucketBits;
	const auto    end   = vaddr + size;
	for (auto bucket = first; bucket <= last; bucket++) {
		const auto it = m_bucket_write_seq.find(bucket);
		if (it == m_bucket_write_seq.end() || it->second <= since) {
			continue; // no write of this bucket after `since` - the bucket answer and the exact one agree
		}
		const auto ring = m_bucket_write_ring.find(bucket);
		if (ring == m_bucket_write_ring.end()) {
			answer.fallback = true;
			continue;
		}
		const auto kept   = std::min<uint64_t>(ring->second.count, ExactRing::K);
		uint64_t   oldest = UINT64_MAX;
		for (uint64_t i = 0; i < kept; i++) {
			const auto& write = ring->second.writes[i];
			oldest            = std::min(oldest, write.seq);
			if (write.seq > since && write.lo < end && vaddr < write.hi) {
				answer.seq = std::max(answer.seq, write.seq);
			}
		}
		if (ring->second.count > ExactRing::K && oldest > since) {
			answer.fallback = true;
		}
	}
	return answer;
}
''')
sub(P, r'''	Common::FrameStats::Add(Common::FrameStats::Counter::ObtainBufs, 1);
''', r'''	Common::FrameStats::Add(Common::FrameStats::Counter::ObtainBufs, 1);
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)): buf_reads of an open fce_next record (any buffer acquisition).
	if (DiagF5Id::On()) [[unlikely]] {
		DiagF5Id::NoteBufferAccess(vaddr, size);
	}
''')

# ---------------------------------------------------------------- textureCache.h
P = R + "cache/textureCache.h"
sub(P, r'''
struct TextureCacheTestAccess;
''', r'''
struct TextureCacheTestAccess;
namespace DiagF5 {
struct CmuEvent;   // Track F, F16k (diagF5.h)
struct StaleProbe; // Track F, F16k (diagF5.h)
} // namespace DiagF5
namespace DiagF5Id {
struct MetaSnap; // Track F, F16k (diagF5.h)
struct DccMiss;  // Track F, F16k (diagF5.h)
} // namespace DiagF5Id
''')
sub(P, r'''	[[nodiscard]] vk::ImageView FindRenderTarget(ImageId id, const ImageDesc& desc,
	                                             uint32_t guest_clear_regs = 0,
	                                             bool     fce_materialize  = false);
''', r'''	// Track F, F16k (KYTY_FIX_F5CMU, ROADMAP s122 item 492(v)): `fce_materialize` also tells PrepareCmaskClear that this is
	// the FCE acquisition (the only one where KYTY_FIX_F5CMU decides); `f5cmu` (non-null only with KYTY_DIAG_F5, from
	// the FCE scan) receives that call's decision for the event line.
	[[nodiscard]] vk::ImageView FindRenderTarget(ImageId id, const ImageDesc& desc,
	                                             uint32_t guest_clear_regs = 0,
	                                             bool     fce_materialize  = false,
	                                             DiagF5::CmuEvent* f5cmu   = nullptr);
''')
sub(P, r'''	[[nodiscard]] bool ClearMeta(uint64_t address, uint8_t* f5_refusal = nullptr);
''', r'''	// Track F, F16k (KYTY_DIAG_F5ID): `f5id_snap` (optional) receives the refused entry in the same branch, under m_lock.
	[[nodiscard]] bool ClearMeta(uint64_t address, uint8_t* f5_refusal = nullptr,
	                             DiagF5Id::MetaSnap* f5id_snap = nullptr);
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)): a read-only copy of the entry at `address` taken under m_lock (Absent
	// when there is none); nothing is inserted, bumped or consumed.
	void F5IdMetaSnap(uint64_t address, DiagF5Id::MetaSnap* out);
''')
sub(P, r'''	[[nodiscard]] bool AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address);
''', r'''	// Track F, F16k (KYTY_DIAG_F5ID): `f5id_miss` (optional) receives the reason of a false answer (DiagF5Id::Miss).
	[[nodiscard]] bool AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address,
	                                             DiagF5Id::DccMiss* f5id_miss = nullptr);
''')
sub(P, r'''	[[nodiscard]] ImageId FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address);
''', r'''	// Track F, F16k (KYTY_DIAG_F5ID): `f5id_miss` (optional) receives the reason of an empty answer (DiagF5Id::Miss).
	[[nodiscard]] ImageId FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address,
	                                          DiagF5Id::DccMiss* f5id_miss = nullptr);
''')
sub(P, r'''	void                        PrepareCmaskClear(ImageId id, const ImageDesc& desc);
''', r'''	// Track F, F16k (item 492(v)): `fce` - the FCE acquisition (FindRenderTarget's fce_materialize); `f5cmu` - see
	// FindRenderTarget.
	void                        PrepareCmaskClear(ImageId id, const ImageDesc& desc, bool fce = false,
	                                              DiagF5::CmuEvent* f5cmu = nullptr);
''')
sub(P, r'''	[[nodiscard]] bool          PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
	                                                uint64_t image_address);
''', r'''	// Track F, F16k (item 492(v)(2)): `f5_probe` (nullptr - the old call exactly) - see DiagF5::StaleProbe; the answer
	// changes only with f5_probe->exact_decides (KYTY_FIX_F5CMU at the FCE acquisition).
	[[nodiscard]] bool          PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
	                                                uint64_t image_address, DiagF5::StaleProbe* f5_probe = nullptr);
''')
sub(P, r'''	uint64_t                                          m_fill_stamp_size    = 0;
''', r'''	uint64_t                                          m_fill_stamp_size    = 0;
	// Track F, F16k (KYTY_DIAG_F5ID): the last fill of any entry type, stamped for DiagF5Id::NoteFillSeq (wr_after).
	uint64_t                                          m_f5id_stamp_address = 0;
	uint64_t                                          m_f5id_stamp_size    = 0;
''')

# ---------------------------------------------------------------- textureCache.cpp
P = R + "cache/textureCache.cpp"
sub(P, r'''void TextureCache::PrepareDccClear(ImageId id, const ImageDesc& desc) {
''', r'''namespace {

// Track F, F16k (KYTY_DIAG_F5ID): a MetaDataInfo as DiagF5Id::MetaSnap (MetaType = Type + 1; checked in F5IdMetaSnap).
template <typename Meta>
DiagF5Id::MetaSnap F5IdSnapOf(const Meta& meta) {
	return {.type       = static_cast<DiagF5Id::MetaType>(static_cast<uint8_t>(meta.type) + 1u),
	        .clear_mask = meta.clear_mask,
	        .fill_value = meta.fill_value,
	        .fill_size  = meta.fill_size,
	        .fill_seq   = meta.fill_seq};
}

// Track F, F16k (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID, ROADMAP s122 item 492(v), (g)(5)): one PrepareCmaskClear call.
// `decide` - KYTY_FIX_F5CMU at the FCE acquisition: the probe's exact answer is the answer (PendingDccFillStale);
// `rt_count` - KYTY_DIAG_F5ID at any other acquisition: the probe only counts cmask_rt_bucket_only. Neither: Probe() is
// nullptr (the old call). The destructor (every return of the call) counts f5cmu_* (KYTY_DIAG_F5 on, `decide`) and
// writes the decision into `out` (when non-null): fix and, for a kept fill, why the call returned without ClearImage.
class F5CmuScope {
public:
	F5CmuScope(bool fce, DiagF5::CmuEvent* out)
	    : m_out(out), m_decide(fce && DiagF5::FixCmuOn()), m_rt_count(!fce && DiagF5Id::On()) {
		m_probe.exact_decides = m_decide;
		m_fix                 = m_decide ? DiagF5::CmuFix::Fresh : DiagF5::CmuFix::Off;
	}
	~F5CmuScope() {
		auto fix = m_fix;
		if (fix == DiagF5::CmuFix::Kept && m_cleared) {
			fix = DiagF5::CmuFix::KeptApplied;
		}
		if (m_decide && DiagF5::On()) [[unlikely]] {
			switch (fix) {
				case DiagF5::CmuFix::Kept: DiagF5::Add(DiagF5::Counter::F5CmuKept); break;
				case DiagF5::CmuFix::KeptApplied:
					DiagF5::Add(DiagF5::Counter::F5CmuKept);
					DiagF5::Add(DiagF5::Counter::F5CmuKeptApplied);
					break;
				case DiagF5::CmuFix::ExactStale: DiagF5::Add(DiagF5::Counter::F5CmuExactStale); break;
				case DiagF5::CmuFix::Fallback: DiagF5::Add(DiagF5::Counter::F5CmuFallback); break;
				default: break;
			}
		}
		if (m_out != nullptr) [[unlikely]] {
			m_out->fix = fix;
			m_out->why = fix == DiagF5::CmuFix::Kept
			                 ? (m_why != DiagF5::CmuWhy::None ? m_why : DiagF5::CmuWhy::NoLayer)
			                 : DiagF5::CmuWhy::None;
		}
	}
	F5CmuScope(const F5CmuScope&)            = delete;
	F5CmuScope& operator=(const F5CmuScope&) = delete;

	[[nodiscard]] DiagF5::StaleProbe* Probe() { return m_decide || m_rt_count ? &m_probe : nullptr; }
	// After PendingDccFillStale (the PendingDcc branch only).
	void Decided() {
		if (m_rt_count && DiagF5::StaleBucketOnly(m_probe)) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::CmaskRtBucketOnly);
		}
		if (m_decide && m_probe.bucket_stale) [[unlikely]] {
			m_fix = m_probe.exact_stale ? DiagF5::CmuFix::ExactStale
			        : m_probe.fallback  ? DiagF5::CmuFix::Fallback
			                            : DiagF5::CmuFix::Kept;
		}
	}
	void               Why(DiagF5::CmuWhy why) { m_why = why; }
	void               Cleared() { m_cleared = true; }
	[[nodiscard]] bool AnyCleared() const { return m_cleared; }

private:
	DiagF5::CmuEvent*  m_out;
	bool               m_decide;
	bool               m_rt_count;
	DiagF5::StaleProbe m_probe {};
	DiagF5::CmuFix     m_fix     = DiagF5::CmuFix::Off;
	DiagF5::CmuWhy     m_why     = DiagF5::CmuWhy::None;
	bool               m_cleared = false;
};

} // namespace

void TextureCache::PrepareDccClear(ImageId id, const ImageDesc& desc) {
''')
sub(P, r'''		if (PendingDccFillStale(desc.info.metadata.range.address, metadata,
		                        image.info.data.address)) {
			metadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};
			if (DiagF5::On()) [[unlikely]] {
				DiagF5::Add(DiagF5::Counter::DccResetStale); // Track F, F16d: the pending fill is dropped (RC6(7))
			}
		} else if (DiagF5::On()) [[unlikely]] {
			DiagF5::NoteDccFill(metadata.fill_value); // Track F, F16d: PendingDcc -> Dcc by the stored code (RC3)
		}
		metadata.type = MetaDataInfo::Type::Dcc;
''', r'''		// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(5), F26): the probe only counts - the decision is the old one.
		DiagF5::StaleProbe f5_probe {};
		const bool         f5id = DiagF5Id::On();
		if (PendingDccFillStale(desc.info.metadata.range.address, metadata,
		                        image.info.data.address, f5id ? &f5_probe : nullptr)) {
			metadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};
			if (DiagF5::On()) [[unlikely]] {
				DiagF5::Add(DiagF5::Counter::DccResetStale); // Track F, F16d: the pending fill is dropped (RC6(7))
			}
		} else if (DiagF5::On()) [[unlikely]] {
			DiagF5::NoteDccFill(metadata.fill_value); // Track F, F16d: PendingDcc -> Dcc by the stored code (RC3)
		}
		if (f5id) [[unlikely]] {
			DiagF5::NoteDccStaleProbe(f5_probe);
		}
		metadata.type = MetaDataInfo::Type::Dcc;
''')
sub(P, r'''	// The metadata fill covers the complete allocation. Consume each layer only after its
	// native image contents exist; already materialized layers may have been rendered since.
''', r'''	const uint32_t f5id_mask0 = metadata.clear_mask; // Track F, F16k (KYTY_DIAG_F5ID): NoteClearApplied below
	// The metadata fill covers the complete allocation. Consume each layer only after its
	// native image contents exist; already materialized layers may have been rendered since.
''')
sub(P, r'''		metadata.clear_mask &= ~mask;
		BumpMetaEpoch();
	}
}

void TextureCache::PrepareCmaskClear(ImageId id, const ImageDesc& desc) {
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_CMASK_CLEAR");
		return value == nullptr || value[0] != '0';
	}();
	if (!enabled || desc.info.metadata.kind != ImageMetadataKind::Cmask ||
''', r'''		metadata.clear_mask &= ~mask;
		BumpMetaEpoch();
	}
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)-(3)): a clear ran here - a stale mark, `cleared` of an open record.
	if (DiagF5Id::On() && metadata.clear_mask != f5id_mask0) [[unlikely]] {
		DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::DccRt, desc.info.metadata.range.address,
		                           image.info.data.address, GpuTimeProfiler::Frame());
	}
}

void TextureCache::PrepareCmaskClear(ImageId id, const ImageDesc& desc, bool fce, DiagF5::CmuEvent* f5cmu) {
	static const bool enabled = [] {
		const auto* value = std::getenv("KYTY_CMASK_CLEAR");
		return value == nullptr || value[0] != '0';
	}();
	// Track F, F16k (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID, ROADMAP s122 item 492(v), (g)(5)): this call's stale probe, its
	// decision for the event line and its counters (F5CmuScope). Both knobs off: no probe is passed, nothing is counted,
	// and `f5cmu` (non-null only with KYTY_DIAG_F5) only receives fix=off.
	F5CmuScope f5 {fce, f5cmu};
	if (!enabled || desc.info.metadata.kind != ImageMetadataKind::Cmask ||
''')
sub(P, r'''		if (PendingDccFillStale(desc.info.metadata.range.address, metadata, image.info.data.address)) {
			metadata = MetaDataInfo {};
		}
		metadata.type = MetaDataInfo::Type::CMask;
''', r'''		if (PendingDccFillStale(desc.info.metadata.range.address, metadata, image.info.data.address, f5.Probe())) {
			metadata = MetaDataInfo {};
		}
		f5.Decided(); // Track F, F16k: fix / cmask_rt_bucket_only by the probe
		metadata.type = MetaDataInfo::Type::CMask;
''')
sub(P, r'''			DiagF5::Add(metadata.fill_value != 0 ? DiagF5::Counter::CmaskRtSkipValue
			                                      : DiagF5::Counter::CmaskRtSkipPartial);
		}
		return;
	}
	vk::ClearValue clear {};
	if (!DecodePackedColorClear(image.backing.format, desc.info.metadata.cmask_clear_words[0],
	                           desc.info.metadata.cmask_clear_words[1], clear.color)) {
		if (f5_pend) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::CmaskRtSkipDecode);
		}
		return;
	}
	const auto& view = desc.view_info;
	if (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 - view.base_layer) {
		if (f5_pend) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::CmaskRtSkipLayers);
		}
		return;
	}
''', r'''			DiagF5::Add(metadata.fill_value != 0 ? DiagF5::Counter::CmaskRtSkipValue
			                                      : DiagF5::Counter::CmaskRtSkipPartial);
		}
		f5.Why(metadata.fill_value != 0              ? DiagF5::CmuWhy::Value
		       : metadata.clear_mask == 0             ? DiagF5::CmuWhy::Mask
		       : desc.info.metadata.range.size == 0   ? DiagF5::CmuWhy::Range
		                                              : DiagF5::CmuWhy::Partial);
		return;
	}
	vk::ClearValue clear {};
	if (!DecodePackedColorClear(image.backing.format, desc.info.metadata.cmask_clear_words[0],
	                           desc.info.metadata.cmask_clear_words[1], clear.color)) {
		if (f5_pend) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::CmaskRtSkipDecode);
		}
		f5.Why(DiagF5::CmuWhy::Decode);
		return;
	}
	const auto& view = desc.view_info;
	if (view.base_level != 0 || view.base_layer >= 32 || view.layer_count > 32 - view.base_layer) {
		if (f5_pend) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::CmaskRtSkipLayers);
		}
		f5.Why(DiagF5::CmuWhy::Layers);
		return;
	}
''')
sub(P, r'''		ClearImage(m_scheduler.Current(), id, image.backing.format,
		           {vk::ImageAspectFlagBits::eColor, 0, 1, layer, 1}, clear);
		metadata.clear_mask &= ~(1u << layer);
		BumpMetaEpoch();
''', r'''		ClearImage(m_scheduler.Current(), id, image.backing.format,
		           {vk::ImageAspectFlagBits::eColor, 0, 1, layer, 1}, clear);
		metadata.clear_mask &= ~(1u << layer);
		BumpMetaEpoch();
		f5.Cleared(); // Track F, F16k: kept_applied
''')
sub(P, r'''		               desc.info.metadata.range.address, layer, desc.info.metadata.cmask_clear_words[0],
		               desc.info.metadata.cmask_clear_words[1]);
	}
}
''', r'''		               desc.info.metadata.range.address, layer, desc.info.metadata.cmask_clear_words[0],
		               desc.info.metadata.cmask_clear_words[1]);
	}
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(3)): a clear ran here - a stale mark of branch 3.
	if (DiagF5Id::On() && f5.AnyCleared()) [[unlikely]] {
		DiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::CmaskRt, desc.info.metadata.range.address,
		                           image.info.data.address, GpuTimeProfiler::Frame());
	}
}
''')
sub(P, r'''vk::ImageView TextureCache::FindRenderTarget(ImageId id, const ImageDesc& desc,
                                             uint32_t guest_clear_regs, bool fce_materialize) {
''', r'''vk::ImageView TextureCache::FindRenderTarget(ImageId id, const ImageDesc& desc,
                                             uint32_t guest_clear_regs, bool fce_materialize,
                                             DiagF5::CmuEvent* f5cmu) {
''')
sub(P, r'''		PrepareCmaskClear(id, desc);
''', r'''		PrepareCmaskClear(id, desc, fce_materialize, f5cmu); // Track F, F16k: the FCE acquisition and its decision
''')
sub(P, r'''bool TextureCache::ClearMeta(uint64_t address, uint8_t* f5_refusal) {
''', r'''bool TextureCache::ClearMeta(uint64_t address, uint8_t* f5_refusal, DiagF5Id::MetaSnap* f5id_snap) {
''')
sub(P, r'''				*f5_refusal = found->second.type == MetaDataInfo::Type::CMask ? DiagF5::RefusalCmask : DiagF5::RefusalDcc;
			}
''', r'''				*f5_refusal = found->second.type == MetaDataInfo::Type::CMask ? DiagF5::RefusalCmask : DiagF5::RefusalDcc;
			}
			if (f5id_snap != nullptr) {
				*f5id_snap = F5IdSnapOf(found->second); // Track F, F16k (KYTY_DIAG_F5ID): the refused entry
			}
''')
sub(P, r'''void TextureCache::TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value) {
''', r'''void TextureCache::F5IdMetaSnap(uint64_t address, DiagF5Id::MetaSnap* out) {
	static_assert(static_cast<uint8_t>(MetaDataInfo::Type::PendingDcc) + 1u ==
	                  static_cast<uint8_t>(DiagF5Id::MetaType::PendingDcc) &&
	              static_cast<uint8_t>(MetaDataInfo::Type::CMask) + 1u == static_cast<uint8_t>(DiagF5Id::MetaType::CMask) &&
	              static_cast<uint8_t>(MetaDataInfo::Type::FMask) + 1u == static_cast<uint8_t>(DiagF5Id::MetaType::FMask) &&
	              static_cast<uint8_t>(MetaDataInfo::Type::HTile) + 1u == static_cast<uint8_t>(DiagF5Id::MetaType::HTile) &&
	              static_cast<uint8_t>(MetaDataInfo::Type::Dcc) + 1u == static_cast<uint8_t>(DiagF5Id::MetaType::Dcc));
	std::scoped_lock lock {m_lock};
	const auto       found = m_surface_metas.find(address);
	*out                   = found == m_surface_metas.end() ? DiagF5Id::MetaSnap {} : F5IdSnapOf(found->second);
}

void TextureCache::TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value) {
''')
sub(P, r'''		if (found->second.type == MetaDataInfo::Type::PendingDcc) {
			found->second.fill_seq = 0;
			m_fill_stamp_address   = address;
			m_fill_stamp_size      = size;
		}
	}
''', r'''		if (found->second.type == MetaDataInfo::Type::PendingDcc) {
			found->second.fill_seq = 0;
			m_fill_stamp_address   = address;
			m_fill_stamp_size      = size;
		}
		// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)-(3)): a new fill drops the stale mark at this address and is
		// stamped for wr_after (StampPendingDccFill).
		if (DiagF5Id::On()) [[unlikely]] {
			DiagF5Id::NoteFill(address);
			m_f5id_stamp_address = address;
			m_f5id_stamp_size    = size;
		}
	}
''')
sub(P, r'''void TextureCache::StampPendingDccFill() {
	std::scoped_lock lock {m_lock};
	if (m_fill_stamp_address == 0) {
''', r'''void TextureCache::StampPendingDccFill() {
	std::scoped_lock lock {m_lock};
	// Track F, F16k (KYTY_DIAG_F5ID): the write sequence of the last fill of any entry type (wr_after); 0 with the knob
	// off (only TrackDccFill sets the address, under the knob).
	if (m_f5id_stamp_address != 0) [[unlikely]] {
		DiagF5Id::NoteFillSeq(m_f5id_stamp_address,
		                      m_buffer_cache.LastGpuWriteSeq(m_f5id_stamp_address, m_f5id_stamp_size, false));
		m_f5id_stamp_address = 0;
		m_f5id_stamp_size    = 0;
	}
	if (m_fill_stamp_address == 0) {
''')
sub(P, r'''bool TextureCache::PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
                                       uint64_t image_address) {
''', r'''bool TextureCache::PendingDccFillStale(uint64_t address, const MetaDataInfo& meta,
                                       uint64_t image_address, DiagF5::StaleProbe* f5_probe) {
''')
sub(P, r'''	if (last_seq <= meta.fill_seq && !cpu_written) {
		return false;
	}
	static std::atomic<uint32_t> stale_count = 0;
''', r'''	if (last_seq <= meta.fill_seq && !cpu_written) {
		return false;
	}
	// Track F, F16k (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID, ROADMAP s122 item 492(v)(2)-(3)): the bucket answer is stale; the
	// exact one asks whether a newer GPU write crosses [address, address + fill_size) (a CPU write stays stale, as
	// before). Only `exact_decides` changes the answer: kept - false, without the stale line.
	if (f5_probe != nullptr) [[unlikely]] {
		f5_probe->bucket_stale = true;
		if (cpu_written) {
			f5_probe->exact_stale = true;
		} else {
			const auto exact      = m_buffer_cache.LastGpuWriteSeqExact(address, meta.fill_size, meta.fill_seq);
			f5_probe->exact_stale = exact.seq != 0;
			f5_probe->fallback    = !f5_probe->exact_stale && exact.fallback;
		}
		if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {
			return false;
		}
	}
	static std::atomic<uint32_t> stale_count = 0;
''')
sub(P, r'''ImageId TextureCache::FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address) {
	if (data_address == 0 || metadata_address == 0) {
		return {};
	}
	ImageId  owner {};
	ImageId  candidate {};
	uint32_t candidates = 0;
''', r'''ImageId TextureCache::FindDccSurfaceImage(uint64_t data_address, uint64_t metadata_address,
                                          DiagF5Id::DccMiss* f5id_miss) {
	if (data_address == 0 || metadata_address == 0) {
		if (f5id_miss != nullptr) [[unlikely]] {
			*f5id_miss = {DiagF5Id::Miss::R1, 0};
		}
		return {};
	}
	ImageId  owner {};
	ImageId  candidate {};
	uint32_t candidates = 0;
	// Track F, F16k (KYTY_DIAG_F5ID): what the scan saw besides the candidates (read only for `f5id_miss`).
	bool     f5id_dcc_other         = false;
	uint64_t f5id_dcc_other_address = 0;
	int      f5id_other_kind        = -1;
''')
sub(P, r'''			if (image->info.metadata.kind == ImageMetadataKind::Dcc) {
				if (image->info.metadata.range.address == metadata_address) {
					owner = id;
					break;
				}
				continue;
			}
			if (image->info.metadata.kind == ImageMetadataKind::None) {
				candidate = id;
				candidates++;
			}
		}
	}
	if (owner) {
		return owner;
	}
	if (candidates == 1 && AdoptPendingDccForTexture(candidate, metadata_address)) {
		return candidate;
	}
	return {};
}
''', r'''			if (image->info.metadata.kind == ImageMetadataKind::Dcc) {
				if (image->info.metadata.range.address == metadata_address) {
					owner = id;
					break;
				}
				f5id_dcc_other         = true;
				f5id_dcc_other_address = image->info.metadata.range.address;
				continue;
			}
			if (image->info.metadata.kind == ImageMetadataKind::None) {
				candidate = id;
				candidates++;
			} else {
				f5id_other_kind = static_cast<int>(image->info.metadata.kind);
			}
		}
	}
	if (owner) {
		return owner;
	}
	if (candidates == 1 && AdoptPendingDccForTexture(candidate, metadata_address, f5id_miss)) {
		return candidate;
	}
	if (f5id_miss != nullptr && candidates != 1) [[unlikely]] {
		*f5id_miss = DiagF5Id::ScanReason(candidates, f5id_dcc_other, f5id_dcc_other_address, f5id_other_kind);
	}
	return {};
}
''')
sub(P, r'''bool TextureCache::AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address) {
	std::scoped_lock lock {m_lock};
	auto*            image = m_slot_images.try_get(id);
	if (image == nullptr || !image->registered || image->info.data.Empty() ||
	    image->info.IsDepth() || image->depth_id || metadata_address == 0) {
		return false;
	}
	if (image->info.metadata.kind == ImageMetadataKind::Dcc) {
		return image->info.metadata.range.address == metadata_address;
	}
	if (image->info.metadata.kind != ImageMetadataKind::None) {
		return false;
	}
	const auto found = m_surface_metas.find(metadata_address);
	if (found == m_surface_metas.end() || found->second.type != MetaDataInfo::Type::PendingDcc) {
		// Only a fill observed through TrackDccFill proves the address is DCC metadata;
		// never classify an untouched address from a T# alone.
		return false;
	}
	if (PendingDccFillStale(metadata_address, found->second, image->info.data.address)) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		m_surface_metas.erase(found);
		BumpMetaEpoch();
		if (DiagF5::On()) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::DccResetStale); // Track F, F16d: the pending fill is dropped (RC6(7))
		}
		return false;
	}
''', r'''bool TextureCache::AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address, DiagF5Id::DccMiss* f5id_miss) {
	std::scoped_lock lock {m_lock};
	auto*            image = m_slot_images.try_get(id);
	if (image == nullptr || !image->registered || image->info.data.Empty() ||
	    image->info.IsDepth() || image->depth_id || metadata_address == 0) {
		if (f5id_miss != nullptr) [[unlikely]] {
			*f5id_miss = {DiagF5Id::Miss::R1, 0}; // Track F, F16k: no usable colour image
		}
		return false;
	}
	if (image->info.metadata.kind == ImageMetadataKind::Dcc) {
		if (f5id_miss != nullptr && image->info.metadata.range.address != metadata_address) [[unlikely]] {
			*f5id_miss = {DiagF5Id::Miss::R2, image->info.metadata.range.address};
		}
		return image->info.metadata.range.address == metadata_address;
	}
	if (image->info.metadata.kind != ImageMetadataKind::None) {
		if (f5id_miss != nullptr) [[unlikely]] {
			*f5id_miss = {DiagF5Id::Miss::R3, static_cast<uint64_t>(image->info.metadata.kind)};
		}
		return false;
	}
	const auto found = m_surface_metas.find(metadata_address);
	if (found == m_surface_metas.end() || found->second.type != MetaDataInfo::Type::PendingDcc) {
		// Only a fill observed through TrackDccFill proves the address is DCC metadata;
		// never classify an untouched address from a T# alone.
		if (f5id_miss != nullptr) [[unlikely]] {
			*f5id_miss = found == m_surface_metas.end()
			                 ? DiagF5Id::DccMiss {DiagF5Id::Miss::R5, 0}
			                 : DiagF5Id::DccMiss {DiagF5Id::Miss::R6, static_cast<uint64_t>(found->second.type) + 1u};
		}
		return false;
	}
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(5), F26): the probe only counts - the decision is the old one.
	DiagF5::StaleProbe f5_probe {};
	const bool         f5id     = DiagF5Id::On();
	const bool         f5_stale = PendingDccFillStale(metadata_address, found->second, image->info.data.address,
	                                                  f5id ? &f5_probe : nullptr);
	if (f5id) [[unlikely]] {
		DiagF5::NoteDccStaleProbe(f5_probe);
	}
	if (f5_stale) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		m_surface_metas.erase(found);
		BumpMetaEpoch();
		if (DiagF5::On()) [[unlikely]] {
			DiagF5::Add(DiagF5::Counter::DccResetStale); // Track F, F16d: the pending fill is dropped (RC6(7))
		}
		if (f5id_miss != nullptr) [[unlikely]] {
			*f5id_miss = {DiagF5Id::Miss::R7, 0};
		}
		return false;
	}
''')

# ---------------------------------------------------------------- render.h
P = R + "render.h"
sub(P, r'''namespace DiagF5 {
struct CsRefusals; // Track F, F16d (diagF5.h)
} // namespace DiagF5
''', r'''namespace DiagF5 {
struct CsRefusals; // Track F, F16d (diagF5.h)
} // namespace DiagF5
namespace DiagF5Id {
struct CsDispatch; // Track F, F16k (diagF5.h)
} // namespace DiagF5Id
''')
sub(P, r'''	// Track F, F16d (KYTY_DIAG_F5): `f5_refusals` / `f5_tracked` - non-null only with the knob on (renderCompute.cpp).
	[[nodiscard]] bool        TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,
	                                                     const CommandBuffer&          buffer,
	                                                     DiagF5::CsRefusals*           f5_refusals = nullptr);
''', r'''	// Track F, F16d (KYTY_DIAG_F5): `f5_refusals` / `f5_tracked` - non-null only with the knob on (renderCompute.cpp).
	// Track F, F16k (KYTY_DIAG_F5ID): `f5id` - non-null only with DiagF5Id::On(); its entries follow `f5_refusals`.
	[[nodiscard]] bool        TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,
	                                                     const CommandBuffer&          buffer,
	                                                     DiagF5::CsRefusals*           f5_refusals = nullptr,
	                                                     DiagF5Id::CsDispatch*         f5id        = nullptr);
''')

# ---------------------------------------------------------------- renderCompute.cpp
P = R + "renderCompute.cpp"
sub(P, r'''bool RenderExecutor::TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,
                                                const CommandBuffer&          buffer,
                                                DiagF5::CsRefusals*           f5_refusals) {
''', r'''// Track F, F16k (KYTY_DIAG_F5ID, ROADMAP s122 item 492(g)(3)): the holder of one dispatch's DiagF5Id::CsDispatch in
// DispatchDirect - empty unless Arm ran (the knob on); emitted once: at once for img_clear / meta_clear, after the
// recorded write for the other classes (After, at StampPendingDccFill), or by the destructor on any other return
// (changed=na). Holds a reference to DispatchDirect's DiagF5::CsRefusals (declared before it, destroyed after it).
class F5IdCsHolder {
public:
	explicit F5IdCsHolder(const DiagF5::CsRefusals& refusals): m_refusals(refusals) {}
	~F5IdCsHolder() {
		if (m_d) [[unlikely]] {
			DiagF5Id::Emit(*m_d, m_refusals);
		}
	}
	F5IdCsHolder(const F5IdCsHolder&)            = delete;
	F5IdCsHolder& operator=(const F5IdCsHolder&) = delete;

	void Arm(const ShaderComputeInputInfo& input) {
		m_d.emplace();
		m_d->shader      = input.stage.program->shader_hash;
		m_d->frame       = GpuTimeProfiler::Frame();
		const auto& fill = input.stage.resources.uniform_fill;
		m_d->sub   = fill.kind == ShaderRecompiler::IR::UniformFillKind::None ? DiagF5Id::CsSub::NoFill
		                                                                     : DiagF5Id::CsSub::FillShape;
		m_d->value = fill.value;
	}
	[[nodiscard]] DiagF5Id::CsDispatch* Get() { return m_d ? &*m_d : nullptr; }
	void                                Class(DiagF5Id::CsClass outcome, uint64_t tracked) {
		if (!m_d) [[likely]] {
			return;
		}
		m_d->classed = true;
		m_d->outcome = outcome;
		m_d->tracked = tracked;
		if (outcome != DiagF5Id::CsClass::Exec) {
			DiagF5Id::Emit(*m_d, m_refusals);
		}
	}
	void After(TextureCache& cache) {
		if (!m_d || !m_d->classed || m_d->emitted) [[likely]] {
			return;
		}
		for (uint32_t i = 0; i < m_refusals.count && i < DiagF5::CsRefusals::Max; i++) {
			cache.F5IdMetaSnap(m_refusals.addresses[i], &m_d->after[i]);
		}
		m_d->has_after = true;
		DiagF5Id::Emit(*m_d, m_refusals);
	}

private:
	const DiagF5::CsRefusals&           m_refusals;
	std::optional<DiagF5Id::CsDispatch> m_d;
};

bool RenderExecutor::TryConsumeComputeMetaClear(const ShaderComputeInputInfo& input,
                                                const CommandBuffer&          buffer,
                                                DiagF5::CsRefusals*           f5_refusals,
                                                DiagF5Id::CsDispatch*         f5id) {
''')
sub(P, r'''				uint8_t f5_refusal = DiagF5::RefusalNone; // Track F, F16d: written by ClearMeta only with KYTY_DIAG_F5 on
				if (cache.ClearMeta(descriptor.Base48(), f5_refusals != nullptr ? &f5_refusal : nullptr)) {
''', r'''				uint8_t f5_refusal = DiagF5::RefusalNone; // Track F, F16d: written by ClearMeta only with KYTY_DIAG_F5 on
				// Track F, F16k (KYTY_DIAG_F5ID): the refused entry goes straight into the slot of this refusal.
				auto* const f5id_snap = f5id != nullptr && f5_refusals != nullptr &&
				                                f5_refusals->count < DiagF5::CsRefusals::Max
				                            ? &f5id->before[f5_refusals->count]
				                            : nullptr;
				if (cache.ClearMeta(descriptor.Base48(), f5_refusals != nullptr ? &f5_refusal : nullptr, f5id_snap)) {
''')
sub(P, r'''					if (f5_refusal != DiagF5::RefusalNone && f5_refusals->count < DiagF5::CsRefusals::Max) [[unlikely]] {
						f5_refusals->addresses[f5_refusals->count++] = descriptor.Base48();
					}
''', r'''					if (f5_refusal != DiagF5::RefusalNone && f5_refusals->count < DiagF5::CsRefusals::Max) [[unlikely]] {
						if (f5id != nullptr) {
							f5id->sizes[f5_refusals->count] = descriptor.GetSize(); // Track F, F16k
							f5id->reads[f5_refusals->count] = resource.read;
						}
						f5_refusals->addresses[f5_refusals->count++] = descriptor.Base48();
					}
''')
sub(P, r'''	const bool         f5_on = DiagF5::On();
	DiagF5::CsRefusals f5_refusals;
	uint64_t           f5_tracked = 0;
	if (!indirect && !floor_clear_skip &&
	    TryConsumeComputeMetaClear(input_info, buffer, f5_on ? &f5_refusals : nullptr)) {
		if (f5_on) [[unlikely]] {
			DiagF5::NoteCsRefusals(f5_refusals, 0);
		}
''', r'''	const bool         f5_on = DiagF5::On();
	DiagF5::CsRefusals f5_refusals;
	uint64_t           f5_tracked = 0;
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(3)): the per-address side of the refusals and their class by this
	// dispatch's outcome (F5IdCsHolder); nothing is built with the knob off.
	F5IdCsHolder f5id {f5_refusals};
	if (DiagF5Id::On()) [[unlikely]] {
		f5id.Arm(input_info);
	}
	if (!indirect && !floor_clear_skip &&
	    TryConsumeComputeMetaClear(input_info, buffer, f5_on ? &f5_refusals : nullptr, f5id.Get())) {
		if (f5_on) [[unlikely]] {
			DiagF5::NoteCsRefusals(f5_refusals, 0);
		}
		f5id.Class(DiagF5Id::CsClass::MetaClear, 0);
''')
sub(P, r'''	                                thread_group_z, mode, f5_on ? &f5_tracked : nullptr)) {
		if (f5_on) [[unlikely]] {
			DiagF5::NoteCsRefusals(f5_refusals, 0);
		}
''', r'''	                                thread_group_z, mode, f5_on ? &f5_tracked : nullptr)) {
		if (f5_on) [[unlikely]] {
			DiagF5::NoteCsRefusals(f5_refusals, 0);
		}
		f5id.Class(DiagF5Id::CsClass::ImgClear, 0);
''')
sub(P, r'''	if (f5_on) [[unlikely]] {
		DiagF5::NoteCsRefusals(f5_refusals, f5_tracked);
	}
''', r'''	if (f5_on) [[unlikely]] {
		DiagF5::NoteCsRefusals(f5_refusals, f5_tracked);
	}
	f5id.Class(DiagF5Id::CsClass::Exec, f5_tracked);
''')
sub(P, r'''		tail.Commit(true);
		m_context.GetTextureCache().StampPendingDccFill();
''', r'''		tail.Commit(true);
		m_context.GetTextureCache().StampPendingDccFill();
		f5id.After(m_context.GetTextureCache()); // Track F, F16k (KYTY_DIAG_F5ID): the entries after the write
''')
sub(P, r'''	                           indirect ? 1u : 0u);
	m_context.GetTextureCache().StampPendingDccFill();
''', r'''	                           indirect ? 1u : 0u);
	m_context.GetTextureCache().StampPendingDccFill();
	f5id.After(m_context.GetTextureCache()); // Track F, F16k (KYTY_DIAG_F5ID): the entries after the write
''')
t = load(P)
if "#include <optional>" not in t:
    sub(P, r'''namespace Libs::Graphics {
static bool FillSourcesDisjoint(''', r'''#include <optional> // Track F, F16k (F5IdCsHolder)

namespace Libs::Graphics {
static bool FillSourcesDisjoint(''')

# ---------------------------------------------------------------- descriptors.cpp
P = R + "pipeline/descriptors.cpp"
sub(P, r'''thread_local vk::Format g_dcc_clear_view_format = vk::Format::eUndefined;
''', r'''thread_local vk::Format g_dcc_clear_view_format = vk::Format::eUndefined;

// Track F, F16k (KYTY_DIAG_F5ID, ROADMAP s122 item 492(g)(3)): set by the FCE scan around its MaterializeDeferredDccClear
// call (stale_apply site=fce; site=mat otherwise). Only with the knob on; restored on scope exit.
thread_local bool t_f5id_fce_site = false;

class F5IdFceSite {
public:
	F5IdFceSite() noexcept: m_saved(t_f5id_fce_site), m_on(DiagF5Id::On()) {
		if (m_on) [[unlikely]] {
			t_f5id_fce_site = true;
		}
	}
	~F5IdFceSite() {
		if (m_on) [[unlikely]] {
			t_f5id_fce_site = m_saved;
		}
	}
	F5IdFceSite(const F5IdFceSite&)            = delete;
	F5IdFceSite& operator=(const F5IdFceSite&) = delete;

private:
	bool m_saved;
	bool m_on;
};
''')
sub(P, r'''	const SkcCensus::SubScope skc3_sub(SkcCensus::Sub {0, UINT32_MAX, 0, 0, mask, 1});
	cache.MarkGpuWritten(id);
}
''', r'''	const SkcCensus::SubScope skc3_sub(SkcCensus::Sub {0, UINT32_MAX, 0, 0, mask, 1});
	cache.MarkGpuWritten(id);
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)-(3)): the clear ran - a stale mark at `address`, `cleared` of an open
	// record at the image.
	if (DiagF5Id::On()) [[unlikely]] {
		DiagF5Id::NoteClearApplied(t_f5id_fce_site ? DiagF5Id::ApplySite::Fce : DiagF5Id::ApplySite::Mat, address,
		                           image.info.data.address, GpuTimeProfiler::Frame());
	}
}
''')
sub(P, r'''} // namespace

// A fast-clear-eliminate / DCC-decompress draw (CB_COLOR_CONTROL.MODE 2/6) binds the surface as
''', r'''// Track F, F16k (KYTY_DIAG_F5ID, ROADMAP s122 item 492(g)(2)): the sizes of a DCC colour slot from its registers, for
// the measurement only - wr_after / cpu_mod over [dcc, dcc + dcc) and buf_reads over [base, base + surface). Never
// EXITs: an element size the table does not know is taken as 16 bytes (the largest DCC and surface - an over-estimate
// of both ranges); a surface that is not a single-level render-target-tiled or linear one is 0 (buf_reads=na); a DCC
// layout TileGetDccSize refuses is 0 (the entry's fill size is used, else wr_after=na).
struct F5IdSlotSizes {
	uint32_t width   = 0;
	uint32_t height  = 0;
	uint32_t pitch   = 0;
	uint64_t surface = 0;
	uint64_t dcc     = 0;
};

uint32_t F5IdBytesPerElement(Prospero::ChannelLayout layout) {
	using L = Prospero::ChannelLayout;
	switch (layout) {
		case L::k8: return 1;
		case L::k16:
		case L::k8_8:
		case L::k5_6_5:
		case L::k5_5_5_1:
		case L::k1_5_5_5:
		case L::k4_4_4_4: return 2;
		case L::k32:
		case L::k16_16:
		case L::k11_11_10:
		case L::k10_11_11:
		case L::k2_10_10_10:
		case L::k10_10_10_2:
		case L::k8_8_8_8:
		case L::k10_10_10_2Float:
		case L::k9_9_9_5: return 4;
		case L::k32_32:
		case L::k16_16_16_16: return 8;
		default: return 16;
	}
}

F5IdSlotSizes F5IdSlotSizesOf(const HW::RenderTarget& rt) {
	F5IdSlotSizes s {};
	s.width               = rt.attrib2.width + 1u;
	s.height              = rt.attrib2.height + 1u;
	const uint32_t levels = rt.attrib2.num_mip_levels + 1u;
	const bool     volume = rt.attrib3.dimension == 2;
	const uint32_t layers = volume ? rt.attrib3.depth + 1u : rt.view.last_array_slice_index + 1u;
	const uint32_t bpe    = F5IdBytesPerElement(rt.info.format);
	const uint32_t frags  = rt.attrib.num_fragments;
	TileSizeAlign  dcc {};
	if (TileGetDccSize(s.width, s.height, layers, bpe, levels, rt.attrib3.tile_mode, dcc, frags)) {
		s.dcc = dcc.size;
	}
	if (levels == 1 && rt.attrib3.tile_mode == Prospero::TileMode::kRenderTarget) {
		s.pitch = TileGetRenderTargetPitch(s.width, bpe, frags);
		TileSizeAlign total {};
		if (s.pitch != 0 && TileGetRenderTargetSize(s.width, s.height, s.pitch, bpe, total, frags)) {
			s.surface = static_cast<uint64_t>(total.size) * layers;
		}
	} else if (levels == 1 && rt.attrib3.tile_mode == Prospero::TileMode::kLinear) {
		s.pitch   = (s.width + 255u) & ~255u;
		s.surface = static_cast<uint64_t>(s.pitch) * s.height * bpe * (uint64_t {1} << frags) * layers;
	}
	return s;
}

// The event of branch 2 (dcc_fce_no_image): the slot registers, the entry before (`before`, taken before
// FindDccSurfaceImage) and after, the reason, wr_after / cpu_mod over the DCC range since the last fill there.
void F5IdNoteFceMiss(TextureCache& cache, BufferCache& buffers, uint32_t slot, const HW::RenderTarget& rt,
                     const DiagF5Id::MetaSnap& before, const DiagF5Id::DccMiss& miss) {
	DiagF5Id::FceEvent e {};
	e.frame            = GpuTimeProfiler::Frame();
	e.present          = DiagF5::Present();
	e.slot             = slot;
	e.base             = rt.base.addr;
	e.dcc              = rt.dcc_addr.addr;
	e.fmt              = static_cast<uint32_t>(rt.info.format);
	e.nfmt             = static_cast<uint32_t>(rt.info.channel_type);
	const auto sizes   = F5IdSlotSizesOf(rt);
	e.width            = sizes.width;
	e.height           = sizes.height;
	e.pitch            = sizes.pitch;
	e.surface_size     = sizes.surface;
	e.dcc_size         = sizes.dcc != 0 ? sizes.dcc : before.fill_size;
	e.clear0           = rt.clear_word0.word0;
	e.clear1           = rt.clear_word1.word1;
	e.dcc_en           = rt.info.dcc_compression_enable;
	e.key_en           = rt.dcc.dcc_clear_key_enable;
	e.miss             = miss;
	e.before           = before;
	cache.F5IdMetaSnap(rt.dcc_addr.addr, &e.after);
	if (e.dcc_size != 0) {
		const auto since = std::max(before.fill_seq, DiagF5Id::FillSeq(e.dcc));
		const auto exact = buffers.LastGpuWriteSeqExact(e.dcc, e.dcc_size, since);
		e.wr_after       = exact.seq != 0    ? DiagF5Id::WrAfter::Exact
		                   : exact.fallback ? DiagF5Id::WrAfter::Fallback
		                                    : DiagF5Id::WrAfter::None;
		e.cpu_mod        = buffers.IsRegionCpuModified(e.dcc, e.dcc_size) ? 1 : 0;
	}
	DiagF5Id::NoteFce(e);
}

} // namespace

// A fast-clear-eliminate / DCC-decompress draw (CB_COLOR_CONTROL.MODE 2/6) binds the surface as
''')
sub(P, r'''			if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {
''', r'''			// Track F, F16k (KYTY_FIX_F5CMU, item 492(v)(4)): the decision of the FCE acquisition below (KYTY_DIAG_F5).
			DiagF5::CmuEvent f5_cmu {};
			if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {
''')
sub(P, r'''				        (rt.dcc.dcc_clear_key_enable ? TextureCache::kRegColorDccKey : 0u),
				    true); // Track F, F9e2b (B42): the FCE acquisition - no draw stamp
''', r'''				        (rt.dcc.dcc_clear_key_enable ? TextureCache::kRegColorDccKey : 0u),
				    true, // Track F, F9e2b (B42): the FCE acquisition - no draw stamp
				    DiagF5::On() ? &f5_cmu : nullptr); // Track F, F16k: its decision for the event line
''')
sub(P, r'''					DiagF5::Add(b42.kind == FixB42Kind::Drawn ? DiagF5::Counter::CmaskFceDrawn
					            : applied                      ? DiagF5::Counter::CmaskFceB42
					                                           : DiagF5::Counter::CmaskFceUnapplied);
				}
''', r'''					DiagF5::Add(b42.kind == FixB42Kind::Drawn ? DiagF5::Counter::CmaskFceDrawn
					            : applied                      ? DiagF5::Counter::CmaskFceB42
					                                           : DiagF5::Counter::CmaskFceUnapplied);
				}
				if (DiagF5::On() && b42.kind == FixB42Kind::Hit) [[unlikely]] {
					// Track F, F16k (item 492(v)(4)): the event line of a B42 hit - the last present number of the video
					// index, the GPU frame, `applied` as above and the decision of the acquisition (fix=off without
					// KYTY_FIX_F5CMU, or without the acquisition: KYTY_FIX_B42=0).
					(void)DiagF5::NoteCmuEvent({.present = DiagF5::Present(),
					                            .gpu     = GpuTimeProfiler::Frame(),
					                            .image   = color.desc.info.data.address,
					                            .cmask   = rt.cmask.addr,
					                            .width   = color.desc.info.extent.width,
					                            .height  = color.desc.info.extent.height,
					                            .applied = applied,
					                            .event   = f5_cmu});
				}
''')
sub(P, r'''		const auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr);
		if (!id) {
			if (DiagF5::On()) [[unlikely]] {
				DiagF5::Add(DiagF5::Counter::DccFceNoImage);
			}
''', r'''		// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)): the entry at the DCC address before the call and the reason of
		// a miss; nothing is read with the knob off.
		const bool         f5id = DiagF5Id::On();
		DiagF5Id::MetaSnap f5id_before {};
		DiagF5Id::DccMiss  f5id_miss {};
		if (f5id) [[unlikely]] {
			cache.F5IdMetaSnap(rt.dcc_addr.addr, &f5id_before);
		}
		const auto id = cache.FindDccSurfaceImage(rt.base.addr, rt.dcc_addr.addr, f5id ? &f5id_miss : nullptr);
		if (!id) {
			if (DiagF5::On()) [[unlikely]] {
				DiagF5::Add(DiagF5::Counter::DccFceNoImage);
			}
			if (f5id) [[unlikely]] {
				F5IdNoteFceMiss(cache, m_context.GetBufferCache(), slot, rt, f5id_before, f5id_miss);
			}
''')
sub(P, r'''		MaterializeDeferredDccClear(buffer, id);
	}
}

void RenderExecutor::BindRenderTarget(ImageId id) {
	auto& image             = m_context.GetTextureCache().GetImage(id);
	image.binding.is_target = true;
	m_bound_images.push_back(id);
}
''', r'''		{
			const F5IdFceSite f5id_site; // Track F, F16k (KYTY_DIAG_F5ID): a clear of this call is the FCE site's
			MaterializeDeferredDccClear(buffer, id);
		}
	}
}

void RenderExecutor::BindRenderTarget(ImageId id) {
	auto& image             = m_context.GetTextureCache().GetImage(id);
	image.binding.is_target = true;
	m_bound_images.push_back(id);
	// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)): a target binding of an image whose data starts at an open base.
	if (DiagF5Id::On()) [[unlikely]] {
		DiagF5Id::NoteBind(image.info.data.address, DiagF5Id::BindKind::Target, image.info.metadata.kind,
		                   image.info.metadata.range.address, GpuTimeProfiler::Frame());
	}
}
''')
sub(P, r'''				const DccClearViewFormat clear_view {descriptors.images[i].desc.view_info.format};
				MaterializeDeferredDccClear(buffer, descriptors.images[i].image_id, image);
			}
''', r'''				const DccClearViewFormat clear_view {descriptors.images[i].desc.view_info.format};
				MaterializeDeferredDccClear(buffer, descriptors.images[i].image_id, image);
			}
			// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)): a shader binding of an image whose data starts at an open base.
			if (DiagF5Id::On()) [[unlikely]] {
				DiagF5Id::NoteBind(image.info.data.address, DiagF5Id::BindKind::Texture, image.info.metadata.kind,
				                   image.info.metadata.range.address, GpuTimeProfiler::Frame());
			}
''')

# ---------------------------------------------------------------- graphicsRun.cpp
P = ROOT + "/src/graphics/guest_gpu/graphicsRun.cpp"
sub(P, r'''		if (diag_f56) [[unlikely]] {
			(void)DiagF5::Service();
			(void)DiagF6::Service();
		}
''', r'''		if (diag_f56) [[unlikely]] {
			(void)DiagF5::Service();
			(void)DiagF6::Service();
			(void)DiagF5Id::Service(); // Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(1)): the sum line, same point
		}
''')
sub(P, r'''		if (should_stop) {
			gpu->m_gfx_cp->BufferWait();
''', r'''		if (should_stop) {
			if (diag_f56) [[unlikely]] {
				(void)DiagF5Id::Service(true); // Track F, F16k (KYTY_DIAG_F5ID): the line at exit (records kind=exit)
			}
			gpu->m_gfx_cp->BufferWait();
''')

# ---------------------------------------------------------------- vulkanWindow.cpp
P = ROOT + "/src/graphics/presentation/window/vulkanWindow.cpp"
sub(P, r'''	(void)DiagF5::LogMode();
	(void)DiagF6::LogMode();
''', r'''	(void)DiagF5::LogMode();
	(void)DiagF6::LogMode();
	// Track F, F16k (ROADMAP s122 item 492(v)(1), (g)(1)): "FixF5Cmu: mode=1" / "DiagF5Id: mode=1" once, same point.
	(void)DiagF5::LogFixCmuMode();
	(void)DiagF5Id::LogMode();
''')

# ---------------------------------------------------------------- screenshot.cpp
P = ROOT + "/src/graphics/presentation/window/screenshot.cpp"
sub(P, r'''#include "graphics/host_gpu/renderer/commandScheduler.h"
''', r'''#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/diagF5.h"
''')
sub(P, r'''bool ScreenshotGrabber::PollScreenshot() {
	m_presents++;
''', r'''bool ScreenshotGrabber::PollScreenshot() {
	m_presents++;
	// Track F, F16k (KYTY_DIAG_F5, ROADMAP s122 item 492(v)(4)): the present number the video index writes (.idx, the
	// second column: slot.present = m_presents of this present) for the event lines.
	if (DiagF5::On()) [[unlikely]] {
		DiagF5::NotePresent(m_presents);
	}
''')

for path, text in FILES.items():
    norm = path.replace("\\", "/")
    if any(s in norm for s in SIGNATURE):
        raise SystemExit("signature set file touched: " + path)
    open(path, "wb").write(text.encode("utf-8"))
    print("patched", path)
