"""F16k (HPP-583, ROADMAP s122 item 492(v), (g)): patch of src/graphics/host_gpu/renderer/diagF5.h.

    python p_diag_h.py <repo root>

LF in, LF out (a CR in the file is an error). Every anchor is a whole line and must occur exactly once.
"""
import sys

ROOT = sys.argv[1]
PATH = ROOT + "/src/graphics/host_gpu/renderer/diagF5.h"


def sub_once(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit("anchor count %d for %r" % (n, old[:80]))
    return text.replace(old, new)


data = open(PATH, "rb").read()
if b"\r" in data:
    raise SystemExit("CR in " + PATH)
t = data.decode("utf-8")

# (1) header comment
t = sub_once(t, r'''// line is one consistent snapshot.

#include "graphics/guest_gpu/hardwareContext.h"
''', r'''// line is one consistent snapshot.
// Track F, F16k (HPP-583, ROADMAP s122 item 492(v), (g)): two more knobs, default 0, read once, independent of each other:
// KYTY_FIX_F5CMU - the exact check of a pending CMASK fill decides the stale question at the fast-clear-eliminate
// acquisition only (TextureCache::PrepareCmaskClear with `fce`); its counters f5cmu_* and the event line DiagF5Ev (under
// KYTY_DIAG_F5). KYTY_DIAG_F5ID - measurement only of the branches dcc_fce_no_image and meta_cs_untracked (namespace
// DiagF5Id below) and the F26 counters; effective only together with KYTY_DIAG_F5 (its identities are sums of DiagF5
// counters). The new counter names are the last rows of the table.

#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/host_gpu/renderer/image/imageInfo.h"
''')

t = sub_once(t, r'''#include <string>

namespace Libs::Graphics::DiagF5 {
''', r'''#include <string>
#include <vector>

namespace Libs::Graphics::DiagF5Id {

// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)): a copy of a metadata entry of TextureCache (MetaDataInfo) taken under its
// lock - Absent, or the type (TextureCache::MetaDataInfo::Type + 1) and the fill fields.
enum class MetaType : uint8_t { Absent, PendingDcc, CMask, FMask, HTile, Dcc };
struct MetaSnap {
	MetaType type       = MetaType::Absent;
	uint32_t clear_mask = 0;
	uint32_t fill_value = 0xffffffffu;
	uint64_t fill_size  = 0;
	uint64_t fill_seq   = 0;
};

} // namespace Libs::Graphics::DiagF5Id

namespace Libs::Graphics::DiagF5 {
''')

# (2) the counters
t = sub_once(t, r'''	ZeroDisp,
	Count
};
''', r'''	ZeroDisp,
	// Track F, F16k (item 492(v)(5), (g)(5)): KYTY_FIX_F5CMU at the FCE acquisition - the bucket check said stale and the
	// exact one did not (kept; kept_applied - and the same call cleared >= 1 layer; kept_applied <= kept), stale by the
	// exact check too, the ring could not answer (fallback). KYTY_DIAG_F5ID (F26, counted only - no decision changes):
	// at PrepareDccClear / AdoptPendingDccForTexture the bucket check said stale and the exact one did not, or the ring
	// fell back; at a PrepareCmaskClear that is not the FCE acquisition the bucket check said stale and the exact one did
	// not.
	F5CmuKept,
	F5CmuKeptApplied,
	F5CmuExactStale,
	F5CmuFallback,
	DccStaleBucketOnly,
	DccStaleFallback,
	CmaskRtBucketOnly,
	Count
};
''')

# (4) the F16k API of DiagF5, before the end of the namespace
t = sub_once(t, r'''void NoteDmaRefusal(uint8_t refusal, uint32_t value);

} // namespace Libs::Graphics::DiagF5
''', r'''void NoteDmaRefusal(uint8_t refusal, uint32_t value);

// ---- Track F, F16k (HPP-583, ROADMAP s122 item 492(v)): KYTY_FIX_F5CMU.
// The knob (default 0, read once: unset or "" = OFF, otherwise Common::EnvValueOn).
[[nodiscard]] bool FixCmuOn();
// "FixF5Cmu: mode=1" once per process when FixCmuOn() (device creation); true when this call printed it.
bool LogFixCmuMode();
// BufferCache writes its exact write journal (the ring of item 492(v)(3)) while this holds: FixCmuOn() or
// DiagF5Id::On(). Both are read once, so the journal holds every write since the process start or none.
[[nodiscard]] bool ExactRingOn();

// The decision of one PrepareCmaskClear call for the event line (item 492(v)(4)): Off - KYTY_FIX_F5CMU is 0 or the call
// was not the FCE acquisition; Fresh - the bucket check did not say stale (or was not reached); ExactStale - stale by
// the exact check as well (or a CPU write); Kept - the bucket check said stale, the exact one did not, the fill was kept
// and the call returned without ClearImage (`why`); KeptApplied - kept, and the call cleared >= 1 layer; Fallback - the
// ring could not answer, the bucket answer (stale) stood.
enum class CmuFix : uint8_t { Off, Fresh, ExactStale, Kept, KeptApplied, Fallback };
// Why a kept call returned without ClearImage, in the order of PrepareCmaskClear's returns: the fill value is not 0,
// the clear mask is 0, the metadata range is empty, the fill is shorter than the range, DecodePackedColorClear failed,
// the view is not representable in the mask, no bit of the view layers was set (the loop cleared nothing).
enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer };
[[nodiscard]] const char* CmuFixName(CmuFix fix);
[[nodiscard]] const char* CmuWhyName(CmuWhy why);
struct CmuEvent {
	CmuFix fix = CmuFix::Off;
	CmuWhy why = CmuWhy::None;
};

// The probe of TextureCache::PendingDccFillStale (nullptr = the old call). In: `exact_decides` - the exact answer is
// the answer (KYTY_FIX_F5CMU at the FCE acquisition). Out, written only when the old check reached its comparison:
// `bucket_stale` - the old answer was stale (a newer GPU write in a 64 KB bucket of the fill, or a CPU write);
// `exact_stale` - a newer GPU write that crosses [address, address + fill_size), or a CPU write; `fallback` - not
// exact_stale and the ring of a bucket had no room for the writes since the fill (all K entries newer).
struct StaleProbe {
	bool exact_decides = false;
	bool bucket_stale  = false;
	bool exact_stale   = false;
	bool fallback      = false;
};
[[nodiscard]] inline bool StaleBucketOnly(const StaleProbe& probe) {
	return probe.bucket_stale && !probe.exact_stale && !probe.fallback;
}
// F26 at the DCC sites (KYTY_DIAG_F5ID): dcc_stale_bucket_only / dcc_stale_fallback by the probe.
void NoteDccStaleProbe(const StaleProbe& probe);

// The present number the video index (.idx, the second column) is written with: ScreenshotGrabber::PollScreenshot
// publishes its m_presents here when On(); a site reads the last one published (the frame of the site is shown at a
// later present).
void                   NotePresent(uint32_t present);
[[nodiscard]] uint32_t Present();

// The event line (item 492(v)(4)), KYTY_DIAG_F5=1, one per B42 hit of the FCE scan:
// "DiagF5Ev: cmask_fce n=<k> present=<n> gpu=<n> image=0x... cmask=0x... extent=<w>x<h> applied=<0|1> fix=<..>
// [why=<..>]"; printed for the first 64 events (k = 1..64), counted after (the hits are cmask_fce_b42 +
// cmask_fce_unapplied).
struct CmuEventLine {
	uint32_t present = 0;
	uint32_t gpu     = 0;
	uint64_t image   = 0;
	uint64_t cmask   = 0;
	uint32_t width   = 0;
	uint32_t height  = 0;
	bool     applied = false;
	CmuEvent event;
};
[[nodiscard]] std::string FormatCmuEvent(uint64_t n, const CmuEventLine& line);
bool                      NoteCmuEvent(const CmuEventLine& line);

// Test site: the F16k lines printed so far (DiagF5Ev, FixF5Cmu, DiagF5Id; at most the last 4096) and a reset of that
// list.
[[nodiscard]] std::vector<std::string> RecentLines();
void                                   ClearRecentLines();

} // namespace Libs::Graphics::DiagF5

namespace Libs::Graphics::DiagF5Id {

// ---- Track F, F16k (HPP-583, ROADMAP s122 item 492(g)): KYTY_DIAG_F5ID - measurement only. Nothing here changes the
// state of the guest, the host or a cache; the cache reads of the sites (a MetaSnap under TextureCache::m_lock) are made
// only with On(), at the events of the two branches. The state below lives under one mutex of this module, a leaf: no
// cache call and no other lock of the emulator is taken while it is held (the log line only).
// The knob (default 0, read once) and the effective switch: Knob() && DiagF5::On().
[[nodiscard]] bool Knob();
[[nodiscard]] bool On();
// "DiagF5Id: mode=1" once per process when On(); "DiagF5Id: mode=0 needs=KYTY_DIAG_F5" when the knob is set without
// KYTY_DIAG_F5. True when this call printed.
bool LogMode();
[[nodiscard]] const char* MetaTypeName(MetaType type);

// Branch 2 (dcc_fce_no_image): the reason FindDccSurfaceImage found no image, in the order of its code: R1 - no usable
// colour image starts at the base; R2 - an image with DCC metadata at another address; R3 - an image with another kind
// of metadata; R4 - more than one image without metadata; R5 - the lone candidate, no entry at the DCC address; R6 - an
// entry that is not PendingDcc; R7 - the pending fill is stale (the entry is erased). `info`: R2 - the other DCC
// address, R3 - ImageMetadataKind, R4 - the candidates, R6 - MetaType.
enum class Miss : uint8_t { None, R1, R2, R3, R4, R5, R6, R7 };
struct DccMiss {
	Miss     why  = Miss::None;
	uint64_t info = 0;
};
// The scan's own reasons when there is no owner and not exactly one candidate: `dcc_other` - an image with DCC metadata
// at another address was seen (`dcc_other_address`), `other_kind` - ImageMetadataKind of an image with another kind
// (-1: none).
[[nodiscard]] DccMiss ScanReason(uint32_t candidates, bool dcc_other, uint64_t dcc_other_address, int other_kind);

enum class WrAfter : uint8_t { None, Exact, Fallback, Na };
struct FceEvent {
	uint32_t frame        = 0;
	uint32_t present      = 0;
	uint32_t slot         = 0;
	uint64_t base         = 0;
	uint64_t dcc          = 0;
	uint32_t fmt          = 0;
	uint32_t nfmt         = 0;
	uint32_t width        = 0;
	uint32_t height       = 0;
	uint32_t pitch        = 0;
	uint64_t surface_size = 0; // 0 - not computable from the registers (buf_reads=na)
	uint64_t dcc_size     = 0; // 0 - not known (wr_after=na, cpu_mod=na)
	uint32_t clear0       = 0;
	uint32_t clear1       = 0;
	bool     dcc_en       = false;
	bool     key_en       = false;
	DccMiss  miss;
	MetaSnap before;
	MetaSnap after;
	WrAfter  wr_after = WrAfter::Na;
	int      cpu_mod  = -1; // -1 - na
};
// One event of branch 2: counts its reason, prints its line for the first 4 events of its key (base, dcc, reason) (at
// most 256 keys; later keys only counted, overflow), and opens the next-access record of `base` (at most 64 open, one
// per base: a later event of an open base is merged into it).
void NoteFce(const FceEvent& event);

// The next access of an open base: the first binding of an image whose data starts there marks the record (texture -
// the per-image loop of CommitBindings, target - RenderExecutor::BindRenderTarget); the record is closed by the next
// Service (the GuestGpu loop top: every clear of that draw has run) with `cleared` - a DCC clear of an image at the
// base after the event (PrepareDccClear, MaterializeDeferredDccClear); 600 frames without a binding - kind=none; at
// exit - kind=exit. `buf_reads`: buffer acquisitions (ObtainBuffer, read or read-write) crossing [base, base +
// surface_size) between the event and the binding.
enum class BindKind : uint8_t { Texture, Target };
void NoteBind(uint64_t image_address, BindKind kind, ImageMetadataKind meta_kind, uint64_t meta_address, uint32_t frame);
void NoteBufferAccess(uint64_t address, uint64_t size);

// Branch 3 (meta_cs_untracked and its neighbours): the class of each address ClearMeta refused in one dispatch, by the
// dispatch's outcome: ImgClear - TryConsumeComputeImageClear took it as an image clear; MetaClear - consumed by the
// metadata shortcut (only with KYTY_META_CLEAR_ALL_WRITES=0); Tracked - the fill this dispatch tracked is at that address
// (meta_cs_tracked); TrackedOther - it tracked a fill at another address; Exec - it runs as it is (sub NoFill: no uniform
// fill; FillShape: a uniform fill whose shape was refused - `value`, its class: DccFillClassOf for DCC entries, 0 for
// CMASK, is Clear or Other). Identity: ImgClear + MetaClear + TrackedOther + Exec = meta_cs_untracked; Tracked =
// meta_cs_tracked.
enum class CsClass : uint8_t { ImgClear, MetaClear, Tracked, TrackedOther, Exec };
enum class CsSub : uint8_t { None, NoFill, FillShape };
// The KYTY_DIAG_F5ID side of one dispatch, built by DispatchDirect only with On() (std::optional there; nothing at 0):
// per refused address (the index of DiagF5::CsRefusals) the size of the written buffer (GetSize), its read flag and
// the entry ClearMeta refused (taken in its refusal branch, under its lock); after the outcome the class fields; after
// the write of the dispatch is recorded the entries again (`after`; changed=0|1), or none when DispatchDirect returns
// before it (changed=na). Emit prints and counts once (the destructor of DispatchDirect's holder calls it if needed).
struct CsDispatch {
	bool                                          emitted   = false;
	bool                                          classed   = false;
	bool                                          has_after = false;
	uint64_t                                      shader    = 0;
	uint32_t                                      frame     = 0;
	CsClass                                       outcome   = CsClass::Exec; // ImgClear / MetaClear / Exec
	uint64_t                                      tracked   = 0;
	CsSub                                         sub       = CsSub::None;
	uint32_t                                      value     = 0;
	std::array<uint64_t, DiagF5::CsRefusals::Max> sizes {};
	std::array<bool, DiagF5::CsRefusals::Max>     reads {};
	std::array<MetaSnap, DiagF5::CsRefusals::Max> before {};
	std::array<MetaSnap, DiagF5::CsRefusals::Max> after {};
};
void Emit(CsDispatch& dispatch, const DiagF5::CsRefusals& refusals);

// A clear of pending metadata state executed at `meta_address` (image `image_address`): a stale-apply line when a mark
// of branch 3 is there (then the mark is dropped), and `cleared` for an open record of branch 2 at the image (DCC
// sites).
enum class ApplySite : uint8_t { DccRt, CmaskRt, Mat, Fce };
void NoteClearApplied(ApplySite site, uint64_t meta_address, uint64_t image_address, uint32_t frame);
// TrackDccFill at `address`: a new fill drops the mark there.
void NoteFill(uint64_t address);
// The fill's GPU write sequence (StampPendingDccFill's answer for any entry type), for wr_after.
void     NoteFillSeq(uint64_t address, uint64_t seq);
[[nodiscard]] uint64_t FillSeq(uint64_t address);

// The sum line "DiagF5Id: sum frame=<n> ..." (with the DiagF5 counters dcc_fce_no_image, meta_cs_untracked,
// meta_cs_tracked copied in the same pass, and the identities id_fce / id_cs) and the key lines of the keys that
// changed: called on the GuestGpu thread at the loop top (graphicsRun.cpp) - closes the records of branch 2 that were
// bound or are 600 frames old, prints when a counter grew and >= 600 frames passed since the last sum line (the first:
// at once). `exit`: at the end of the GuestGpu loop - closes every record (kind=exit) and prints. Service reads the
// frame (GpuTimeProfiler::Frame); ServiceAt takes it as an argument (test site). True when a sum line was printed.
bool Service(bool exit = false);
bool ServiceAt(uint32_t frame, bool exit);

// Test site: the counters of the sum line by name ("r1".."r7", "fce", "cs", "img_clear", ...), the open records and
// marks, and a reset of the whole state (between scenarios).
[[nodiscard]] uint64_t Count(const char* name);
[[nodiscard]] uint32_t OpenRecords();
[[nodiscard]] uint32_t Marks();
void                   ResetForTest();

} // namespace Libs::Graphics::DiagF5Id
''')

open(PATH, "wb").write(t.encode("utf-8"))
print("patched", PATH)
