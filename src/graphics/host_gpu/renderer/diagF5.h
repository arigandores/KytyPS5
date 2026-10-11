#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF5_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF5_H_

// Track F, F16d (HPP-521, ROADMAP s122 items 421(g), 427, 433(v)): the diagnostic counters KYTY_DIAG_F5 (row F5,
// members 1-6: the colour metadata branches where a clear the guest expects is not performed, and the reference
// counters of members 3-6) and KYTY_DIAG_F6 (row F6: the colour slots of a host draw against the guest registers and
// the MRT exports of its pixel program). MEASUREMENT ONLY, default 0: each knob is read once (unset or "" = OFF,
// otherwise Common::EnvValueOn); a counter is a relaxed std::atomic<uint64_t> incremented under `if (On())`; the sites
// read only values already in their scope - no cache call, no lock, no write into guest or host state - so with the
// knob off not even an atomic operation runs. Outside the translation cache signature set (the shader tree,
// shaderTranslationCache.cpp, gpu_format.h, gpu_defs.h): the signature and the variant directory do not change.
// The line "DiagF5: mode=1" / "DiagF6: mode=1" is printed once at device creation; "DiagF5: frame=<n> <name>=<value> ..."
// (all counters) when a counter grew since the last line and >= 2 s passed (item 427(e)). Track F, F16d2 (HPP-569,
// item 470(v)(1), form (a)): the flip tick (PresentThread) only publishes a request (frame, clock) and reads no counter;
// the counters are copied once and the line is printed by Service() on the GuestGpu thread at the top of the
// GuestGpu::ThreadRun loop, where no window "parent added, children not yet" of a site is open (graphicsRun.cpp) - the
// line is one consistent snapshot.
// Track F, F16k (HPP-583, ROADMAP s122 item 492(v), (g)): two more knobs, default 0, read once, independent of each other:
// KYTY_FIX_F5CMU - the exact check of a pending CMASK fill decides the stale question at the fast-clear-eliminate
// acquisition only (TextureCache::PrepareCmaskClear with `fce`); its counters f5cmu_* and the event line DiagF5Ev (under
// KYTY_DIAG_F5). KYTY_DIAG_F5ID - measurement only of the branches dcc_fce_no_image and meta_cs_untracked (namespace
// DiagF5Id below) and the F26 counters; effective only together with KYTY_DIAG_F5 (its identities are sums of DiagF5
// counters). The new counter names are the last rows of the table.
// Track F, F16o (HPP-595, ROADMAP s122 item 504(e)): KYTY_FIX_F26 - default 0, read once: the exact check decides the
// stale question of a pending DCC fill at PrepareDccClear and AdoptPendingDccForTexture (row F26); the FCE acquisition and
// every other PrepareCmaskClear do not read it. Its counters f26_* and the event line DiagF5Ev dcc_stale (KYTY_DIAG_F5).
// Track F, F46a (HPP-798, ROADMAP s122 item 702(e)): the mark M1 of a kept fill keyed by the metadata address (the line
// dcc_stale_apply), the line f26_first_exec (KYTY_DIAG_F5ID) and the synthetic positive control KYTY_F26_TINT /
// KYTY_F26_TINT_DCC (default 0; NOT a measurement when set - the picture changes) - DccApplyLine, FirstExecLine,
// F26TintAt below.

#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/host_gpu/renderer/image/imageInfo.h"

#include <array>
#include <atomic>
#include <cstdint>
#include <string>
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

// The order is the order of the line. Families (parent = sum of the children; checked by the test site and the reader):
// DccRtPending (PrepareDccClear on the render-target path, a clear-mask bit in the view layers) = DccRtCleared +
// DccRtSkip{Levels,Partial,Decode,Layers}; DccMatPending (MaterializeDeferredDccClear, a non-zero layer mask) =
// DccMatCleared + DccMatUndecoded; DccFce (fast-clear-eliminate scan, DCC slot) = DccFceImage + DccFceNoImage;
// DccFillMeta (a fill on confirmed DCC: TrackDccFill on a Dcc entry, or a PendingDcc -> Dcc adoption by the stored
// code) = DccFillClear + DccFillUncompressed + DccFillUnknown; MetaRefusedKnown (ClearMeta refuses a PendingDcc / Dcc /
// CMask address) = MetaCsTracked + MetaCsUntracked + MetaDmaUntracked + MetaDmaNoClear; CmaskRtPending
// (PrepareCmaskClear, a clear-mask bit in the view layers) = CmaskRtCleared + CmaskRtSkip{Value,Partial,Decode,Layers};
// CmaskFce (fast-clear-eliminate scan, CMASK slot) = CmaskFce{NoImage,Meta,Msaa,Layout,NoFill,Drawn,B42,Unapplied}.
enum class Counter : uint32_t {
	RtResolves,
	DccRt,
	RtcheckMeta,
	DccRtPending,
	DccRtCleared,
	DccRtSkipLevels,
	DccRtSkipPartial,
	DccRtSkipDecode,
	DccRtSkipLayers,
	DccMatPending,
	DccMatCleared,
	DccMatUndecoded,
	DccFce,
	DccFceImage,
	DccFceNoImage,
	DccFillAll,
	DccFillMeta,
	DccFillClear,
	DccFillUncompressed,
	DccFillUnknown,
	DccResetStale,
	DccResetType,
	MetaRefusedKnown,
	MetaCsTracked,
	MetaCsUntracked,
	MetaDmaUntracked,
	MetaDmaNoClear,
	CmaskRtPending,
	CmaskRtCleared,
	CmaskRtSkipValue,
	CmaskRtSkipPartial,
	CmaskRtSkipDecode,
	CmaskRtSkipLayers,
	CmaskFce,
	CmaskFceNoImage,
	CmaskFceMeta,
	CmaskFceMsaa,
	CmaskFceLayout,
	CmaskFceNoFill,
	CmaskFceDrawn,
	CmaskFceB42,
	CmaskFceUnapplied,
	FmaskRead,
	RoundUnorm,
	RoundFloat,
	RoundOther,
	DsUnbound,
	DsUnboundClear,
	StereoWrites,
	StereoNonzero,
	ZeroDisp,
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
	// Track F, F16k2 (RC4, ROADMAP s122 item 496(b)(4)): the f5cmu_exact_stale decisions set by a CPU-modified page of the
	// fill (PendingDccFillStale's cpu_written; the event line says why=cpu): f5cmu_exact_cpu <= f5cmu_exact_stale.
	F5CmuExactCpu,
	// Track F, F16o (item 504(e)(4)): KYTY_FIX_F26 at PrepareDccClear / AdoptPendingDccForTexture, where the bucket check
	// said stale - kept (the exact check did not; kept_applied - and the fill was applied: >= 1 layer cleared by the call
	// at prepare; at adopt (Track F, F16o2) >= 1 layer cleared by the MaterializeDeferredDccClear that took the deferred
	// mark; kept_applied <= kept), stale by the exact check too, the ring could
	// not answer (fallback). With KYTY_DIAG_F5ID: f26_kept = dcc_stale_bucket_only, f26_fallback = dcc_stale_fallback.
	F26Kept,
	F26KeptApplied,
	F26ExactStale,
	F26Fallback,
	// Track F, F16o2 (RC1 of F16p, item 507(b)(3)-(4)): a deferred clear of an adoption (fix=kept why=deferred) that
	// RenderExecutor::MaterializeDeferredDccClear took and did not clear (result=declined); one it cleared counts
	// f26_kept_applied. f26_kept_applied + f26_deferred_declined <= f26_kept.
	F26DeferredDeclined,
	// Track F, F46a (HPP-798, item 702(e)(2), (4)): the mark is keyed by the metadata address and a declined mark stays
	// (a later clear of the address takes it): f26_kept_applied <= f26_kept and f26_deferred_declined <= f26_kept (the sum
	// may exceed f26_kept). KYTY_F26_TINT: the DCC fill executions at the key address KYTY_F26_TINT_DCC whose clear value
	// was replaced by (1, 0, 1, 1) (f26_tint_applied) or would have been, the view format having no such encoding
	// (f26_tint_skip). Both 0 with KYTY_F26_TINT = 0.
	F26TintApplied,
	F26TintSkip,
	Count
};

[[nodiscard]] bool        On();
void                      Add(Counter counter);
[[nodiscard]] uint64_t    Get(Counter counter);
[[nodiscard]] const char* Name(Counter counter);
// "DiagF5: mode=1" once per process when On(); true when this call printed it.
bool LogMode();
// The flip tick (PresentThread): when On(), publishes the request for a line - the frame and the clock - and reads no
// counter; true when published (a newer request replaces one not served yet). TickAt takes the clock as an argument
// (test site); Tick reads it.
bool Tick(uint32_t frame);
bool TickAt(uint32_t frame, uint64_t now_ms);
// Track F, F16d2: the line. Called on the GuestGpu thread outside every window (GuestGpu::ThreadRun, graphicsRun.cpp):
// takes the pending request, copies all counters once and prints the line from the copy when On(), a counter grew
// since the last line and >= 2000 ms (request clock) passed since it (the first line: at the first request with a
// growth); true when it printed.
bool Service();
[[nodiscard]] std::string FormatLine(uint32_t frame);
// Test site: the number of lines Service printed and the last of them.
[[nodiscard]] uint64_t    Lines();
[[nodiscard]] std::string LastLine();
// Test site only (nullptr in the emulator): called on the site's thread right after each counter increment of Add
// (`set` 5) and of DiagF6::NoteDraw (`set` 6) - inside a window of the site.
using WindowHook = void (*)(uint32_t set, uint32_t counter);
void SetWindowHook(WindowHook hook);

// The layer bits of a view [first, first + count) inside the 32-bit clear mask; UINT32_MAX when the range is not
// representable there (first >= 32 or count > 32 - first: the code returns without a clear, every mask bit counts).
[[nodiscard]] uint32_t ViewLayerBits(uint32_t first, uint32_t count);

// TrackDccFill's classification of a stored fill value (textureCache.cpp: a repeated byte, codes 00/20/40/80/c0 clear).
enum class FillClass : uint8_t { Clear, Uncompressed, Unknown };
[[nodiscard]] FillClass DccFillClassOf(uint32_t fill_value);
void                    NoteDccFill(uint32_t fill_value); // DccFillMeta + its child

// ClearMeta's refusal kind for its callers (the optional out argument): 0 - none (accepted, or an address that is not
// PendingDcc / Dcc / CMask), 1 - PendingDcc or Dcc, 2 - CMask.
inline constexpr uint8_t RefusalNone  = 0;
inline constexpr uint8_t RefusalDcc   = 1;
inline constexpr uint8_t RefusalCmask = 2;

// The written buffers of one compute dispatch that ClearMeta refused as known metadata (TryConsumeComputeMetaClear).
struct CsRefusals {
	static constexpr uint32_t   Max = 32; // ShaderInfo::MaxBuffers
	uint32_t                    count = 0;
	std::array<uint64_t, Max>   addresses; // only [0, count) is read; not zeroed per dispatch
};
// Per refused address: MetaCsTracked when the same dispatch tracked a fill at that address (TrackDccFill of
// TryConsumeComputeImageClear; `tracked_address` 0 - none), otherwise MetaCsUntracked.
void NoteCsRefusals(const CsRefusals& refusals, uint64_t tracked_address);
// A DMA fill refused as known metadata: MetaDmaUntracked when the value is a clear for the entry kind (DCC: a clear
// code of DccFillClassOf; CMASK: 0), otherwise MetaDmaNoClear.
void NoteDmaRefusal(uint8_t refusal, uint32_t value);

// ---- Track F, F16k (HPP-583, ROADMAP s122 item 492(v)): KYTY_FIX_F5CMU.
// The knob (default 0, read once: unset or "" = OFF, otherwise Common::EnvValueOn).
[[nodiscard]] bool FixCmuOn();
// "FixF5Cmu: mode=1" once per process when FixCmuOn() (device creation); true when this call printed it.
bool LogFixCmuMode();
// BufferCache writes its exact write journal (the ring of item 492(v)(3)) while this holds: FixCmuOn(), FixF26On()
// (Track F, F16o) or DiagF5Id::On(). All are read once, so the journal holds every write since the process start or
// none.
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
// Track F, F16k2 (RC4, item 496(b)(4)): Cpu - an ExactStale decision set by a CPU write (a CPU-modified page of the
// fill), not by a crossing GPU write.
// Track F, F16o (item 504(e)(3)): Levels - PrepareDccClear's return on an image with more than one level (the line
// dcc_stale only). Track F, F16o2 (item 507(b)(1)): Deferred - AdoptPendingDccForTexture adopted the fill with a clear
// the call does not apply (the line dcc_stale only; the outcome - the line dcc_stale_apply of the same n).
enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu, Levels, Deferred };
[[nodiscard]] const char* CmuFixName(CmuFix fix);
[[nodiscard]] const char* CmuWhyName(CmuWhy why);
struct CmuEvent {
	CmuFix fix = CmuFix::Off;
	CmuWhy why = CmuWhy::None;
};

// The probe of TextureCache::PendingDccFillStale (nullptr = the old call). In: `exact_decides` - the exact answer is
// the answer (KYTY_FIX_F5CMU at the FCE acquisition; Track F, F16o: KYTY_FIX_F26 at PrepareDccClear and
// AdoptPendingDccForTexture). Out, written only when the old check reached its comparison:
// `bucket_stale` - the old answer was stale (a newer GPU write in a 64 KB bucket of the fill, or a CPU write);
// `exact_stale` - a newer GPU write that crosses [address, address + fill_size), or a CPU write; `fallback` - not
// exact_stale and the ring of a bucket had no room for the writes since the fill (all K entries newer).
struct StaleProbe {
	bool exact_decides = false;
	bool bucket_stale  = false;
	bool exact_stale   = false;
	bool fallback      = false;
	// Track F, F16k2 (RC4): exact_stale was set by cpu_written (a CPU-modified page of the fill), not by a GPU write.
	bool cpu           = false;
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
// [why=<..>]"; printed for the first 1024 events (k = 1..1024; Track F, F16o, item 504(e)(5): was 64), counted after
// (the hits are cmask_fce_b42 + cmask_fce_unapplied).
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
// Track F, F16k2 (RC5, ROADMAP s122 item 496(b)(5)): the event line of a decision of the FCE acquisition that has no
// cmask_fce line (no B42 hit: the target carried CMASK metadata already - FixB42Probe answered None - or a drawn
// fill), KYTY_DIAG_F5=1 and fix not off / fresh: "DiagF5Ev: cmask_fce_nohit n=<k> b42=<none|drawn> present=<n>
// gpu=<n> image=0x... cmask=0x... extent=<w>x<h> fix=<..> [why=<..>]" (`applied` is not printed); its own limit -
// the first 64 (k = 1..64), counted after.
[[nodiscard]] std::string FormatCmuNoHit(uint64_t n, const CmuEventLine& line, bool drawn);
bool                      NoteCmuNoHit(const CmuEventLine& line, bool drawn);

// ---- Track F, F16o (HPP-595, ROADMAP s122 item 504(e)): KYTY_FIX_F26.
// The knob (default 0, read once: unset or "" = OFF, otherwise Common::EnvValueOn).
[[nodiscard]] bool FixF26On();
// "FixF26: mode=1" once per process when FixF26On() (device creation); true when this call printed it.
bool LogFixF26Mode();
// The event line (item 504(e)(3)), KYTY_DIAG_F5=1, one per decision of PrepareDccClear / AdoptPendingDccForTexture
// where the bucket check said stale: "DiagF5Ev: dcc_stale site=<prepare|adopt> n=<k> present=<n> gpu=<n> image=0x...
// dcc=0x... extent=<w>x<h> exact=<stale|fresh|fallback|na> fix=<off|exact_stale|kept|kept_applied|fallback>
// [why=<..>]"; `exact` - the ring's answer (na: the ring is not written); `fix` - off: KYTY_FIX_F26 is 0; kept: kept
// and not applied in the same call (`why`); kept_applied: kept and applied in the same call; `present` - as cmask_fce
// (Present()); printed for the first 256 (k = 1..256), counted after.
enum class DccSite : uint8_t { Prepare, Adopt };
enum class DccExact : uint8_t { Na, Stale, Fresh, Fallback };
[[nodiscard]] const char* DccSiteName(DccSite site);
[[nodiscard]] const char* DccExactName(DccExact exact);
struct DccStaleLine {
	DccSite  site    = DccSite::Prepare;
	uint32_t present = 0;
	uint32_t gpu     = 0;
	uint64_t image   = 0;
	uint64_t dcc     = 0;
	uint32_t width   = 0;
	uint32_t height  = 0;
	DccExact exact   = DccExact::Na;
	CmuEvent event;
};
[[nodiscard]] std::string FormatDccStale(uint64_t n, const DccStaleLine& line);
// Track F, F16o2: `n_out` (optional) receives the event number k (past the limit too).
bool                      NoteDccStale(const DccStaleLine& line, uint64_t* n_out = nullptr);

// ---- Track F, F16o2 (HPP-599, RC1 of F16p, ROADMAP s122 item 507(b)): the deferred clear of a kept fill.
// Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(2), RC5 of F45b): the mark M1 is keyed by the METADATA ADDRESS
// (TextureCache::F26Deferred in m_f26_marks, under m_lock), not by the image. It is set, with KYTY_FIX_F26 and
// KYTY_DIAG_F5, by the event fix=kept why=deferred of AdoptPendingDccForTexture and by the event fix=kept why=decode of
// PrepareDccClear; it is removed where the clear-mask bits of that address go 1 -> 0 - the layer loop of
// PrepareDccClear (site=prepare) or of RenderExecutor::MaterializeDeferredDccClear (TouchMeta(..., false), site=mat) -
// whichever image executes the fill (result=cleared, f26_kept_applied); a MaterializeDeferredDccClear of the address
// that clears nothing does not remove it (result=declined, the first one per mark, f26_deferred_declined); a new fill
// of the address (TrackDccFill, site=fill), the erase of its entry (UnmapMemory - site=unmap, DeleteImage -
// site=delete), a retype of the entry (PrepareCmaskClear, the HTile binding - site=retype) or a second mark at the
// address (site=remark; not reachable while the entry is Dcc) drop it (result=dropped, no counter).
// The line, KYTY_DIAG_F5=1: "DiagF5Ev: dcc_stale_apply n=<n> present=<n> gpu=<n> image=0x... dcc=0x...
// result=<cleared|declined|dropped> layers=0x<mask> site=<prepare|mat|fill|unmap|delete|retype|remark>"; n, dcc - of
// the event's dcc_stale line; image - the executing image (cleared, declined) or the event's (dropped); present / gpu -
// at the outcome; layers - cleared: the bits that went 1 -> 0, declined: the pending layer mask the call read (0 when
// it returned before reading it), dropped: the clear mask of the entry at the drop. The limit of dcc_stale: printed
// when n <= 256 (the event's own line was printed). Counting is the caller's.
enum class DccApplyResult : uint8_t { Cleared, Declined, Dropped };
enum class F26Site : uint8_t { Prepare, Mat, Fill, Unmap, Delete, Retype, Remark };
[[nodiscard]] const char* DccApplyResultName(DccApplyResult result);
[[nodiscard]] const char* F26SiteName(F26Site site);
struct DccApplyLine {
	uint64_t       n       = 0;
	uint32_t       present = 0;
	uint32_t       gpu     = 0;
	uint64_t       image   = 0;
	uint64_t       dcc     = 0;
	DccApplyResult result  = DccApplyResult::Cleared;
	uint32_t       layers  = 0;
	F26Site        site    = F26Site::Prepare;
};
[[nodiscard]] std::string FormatDccStaleApply(const DccApplyLine& line);
bool                      NoteDccStaleApply(const DccApplyLine& line);

// ---- Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(3), RC2(a) of F45b): the first execution of a fill of an address
// that had a dcc_stale event in this process, after the event. KYTY_DIAG_F5ID=1, both arms of KYTY_FIX_F26: the event
// is armed at TextureCache::m_f26_first by its reporting F26Scope - when the site call leaves, so the in-call clear of a
// kept_applied event is not "after the event"; the first PrepareDccClear (site=prepare) or MaterializeDeferredDccClear
// (site=mat) whose layer loop takes a clear-mask bit of the address 1 -> 0 prints one line per armed event and disarms
// it: "DiagF5Ev: f26_first_exec n=<n> present=<n> dcc=0x... image=0x... site=<prepare|mat>" (n - the event's,
// image - the executing image). The limit of dcc_stale: only events n <= 256 are armed.
struct FirstExecLine {
	uint64_t n       = 0;
	uint32_t present = 0;
	uint64_t dcc     = 0;
	uint64_t image   = 0;
	F26Site  site    = F26Site::Prepare;
};
[[nodiscard]] std::string FormatFirstExec(const FirstExecLine& line);
bool                      NoteFirstExec(const FirstExecLine& line); // printed when n is 1..256

// ---- Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(4), RC3 of F45b): the synthetic positive control M2 - NOT a
// measurement: with a mode != 0 the clear value of the chosen executions is replaced and the picture changes.
// KYTY_F26_TINT: 0 (default; any value other than "1" / "2"), 1 - an execution that removes an F26 mark of the key
// address (the mark M1, or the in-call clear of a kept_applied event of PrepareDccClear - the F26 decision of that very
// call), 2 - every execution of a DCC fill (PrepareDccClear, MaterializeDeferredDccClear) at the key address.
// KYTY_F26_TINT_DCC: the key, a metadata address in hex ("0x" optional; unset or not fully parsed - 0). Both read once
// per process. The colour (1, 0, 1, 1) is written as float in the format the clear is written through; a format without
// that encoding (not DccFixedClearSupported, or fewer than 3 components) keeps the decoded value (f26_tint_skip).
[[nodiscard]] uint32_t F26TintMode();
[[nodiscard]] uint64_t F26TintDcc();
// "F26Tint: mode=<m> dcc=0x<key>" once per process when F26TintMode() != 0 (device creation); true when this call
// printed it.
bool LogF26TintMode();
// The sites' cheap check: a mode is set and `address` is the key.
[[nodiscard]] bool F26TintKey(uint64_t address);
enum class TintResult : uint8_t { None, Applied, Skip };
// The pure decision (test site): `mode` / `key` as given; `removes_mark` - the execution removes an F26 mark of
// `address` (read by mode 1 only). Applied: `clear` is set to (1, 0, 1, 1); None / Skip: `clear` is unchanged.
[[nodiscard]] TintResult F26TintAt(uint32_t mode, uint64_t key, uint64_t address, bool removes_mark, vk::Format format,
                                   vk::ClearColorValue& clear);
// The sites' call: F26TintAt with the process knobs, counting f26_tint_applied / f26_tint_skip.
TintResult F26Tint(uint64_t address, bool removes_mark, vk::Format format, vk::ClearColorValue& clear);

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

// Track F, F16k2 (RC1, item 496(b)(1)): Large - no recorded bucket write crosses the range after `since`, but a GPU
// write larger than 16 MB (no bucket, no ring, any address) is newer than `since`.
enum class WrAfter : uint8_t { None, Exact, Fallback, Na, Large };
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
// The fill's GPU write sequence (StampPendingDccFill's answer for any entry type), for wr_after; Track F, F16k2 (RC2,
// item 496(b)(2)): with the CPU write epoch of the fill range at the stamp (MemoryTracker::RangeWriteEpoch; 0 - not
// tracked), for cpu_mod. FillCpuEpoch: false - no fill was stamped at `address`.
void     NoteFillSeq(uint64_t address, uint64_t seq, uint64_t cpu_epoch);
[[nodiscard]] uint64_t FillSeq(uint64_t address);
[[nodiscard]] bool     FillCpuEpoch(uint64_t address, uint64_t* cpu_epoch);
// Track F, F16k2 (RC3, item 496(b)(3)): a fill stamp its dispatch left untaken (TextureCache::F5IdNoteStampLate at the
// end of DispatchDirect, or TrackDccFill over it) - the counter stamp_late of the sum line, once per stamp.
void NoteStampLate();

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

namespace Libs::Graphics::DiagF6 {

// One host draw at a recording site after the PrepareDrawRenderState / RtsPlaceA fork (renderDraw.cpp). Slot class by
// (mask != 0, base != 0, raw CB_COLORn_INFO.FORMAT != 0); an export is an MRT output of the pixel program by its guest
// index (ShaderInfo::outputs, kind Mrt). Identities: SBound + SAddr0Fmt + SAddr0NoFmt + SMask0Addr + SEmpty ==
// 8 * Draws; HBound == SBound - BoundMissing + BoundExtra; WTotal == WBound + WMask0 + WAddr0Fmt + WAddr0NoFmt + WGe8;
// DrawsIdx + DrawsAuto + DrawsInd + DrawsMesh == Draws; PsDraws <= Draws.
enum class Counter : uint32_t {
	Draws,
	DrawsIdx,
	DrawsAuto,
	DrawsInd,
	DrawsMesh,
	PsDraws,
	SBound,
	SAddr0Fmt,
	SAddr0NoFmt,
	SMask0Addr,
	SEmpty,
	HBound,
	BoundMissing,
	BoundExtra,
	WTotal,
	WBound,
	WMask0,
	WAddr0Fmt,
	WAddr0NoFmt,
	WGe8,
	Count
};

enum class DrawKind : uint8_t { Indexed, Auto, Indirect, Mesh };

[[nodiscard]] bool        On();
[[nodiscard]] uint64_t    Get(Counter counter);
[[nodiscard]] const char* Name(Counter counter);
bool                      LogMode();
bool                      Tick(uint32_t frame);
bool                      TickAt(uint32_t frame, uint64_t now_ms);
bool                      Service(); // Track F, F16d2: as DiagF5::Service
[[nodiscard]] std::string FormatLine(uint32_t frame);
[[nodiscard]] uint64_t    Lines();
[[nodiscard]] std::string LastLine();

// `host_slots` - the guest slots of the host colour attachments of the draw (RenderColorInfo::target_slot of
// state.color_info[0, host_count)); `mrt` - the guest MRT indices the pixel program exports (only with `ps`).
void NoteDraw(const HW::Context& hw, const uint32_t* host_slots, uint32_t host_count, bool ps, const uint32_t* mrt,
              uint32_t mrt_count, DrawKind kind);

} // namespace Libs::Graphics::DiagF6

#endif /* EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF5_H_ */
