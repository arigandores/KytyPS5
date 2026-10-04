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
// (all counters) on a flip tick when a counter grew since the last line and >= 2 s passed (item 427(e)).

#include "graphics/guest_gpu/hardwareContext.h"

#include <array>
#include <atomic>
#include <cstdint>
#include <string>

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
	Count
};

[[nodiscard]] bool        On();
void                      Add(Counter counter);
[[nodiscard]] uint64_t    Get(Counter counter);
[[nodiscard]] const char* Name(Counter counter);
// "DiagF5: mode=1" once per process when On(); true when this call printed it.
bool LogMode();
// The flip tick: prints the line when On(), a counter grew since the last line and >= 2000 ms passed since it (the
// first line: at the first tick with a growth). TickAt takes the clock as an argument (test site); Tick reads it.
bool Tick(uint32_t frame);
bool TickAt(uint32_t frame, uint64_t now_ms);
[[nodiscard]] std::string FormatLine(uint32_t frame);

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

} // namespace Libs::Graphics::DiagF5

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
[[nodiscard]] std::string FormatLine(uint32_t frame);

// `host_slots` - the guest slots of the host colour attachments of the draw (RenderColorInfo::target_slot of
// state.color_info[0, host_count)); `mrt` - the guest MRT indices the pixel program exports (only with `ps`).
void NoteDraw(const HW::Context& hw, const uint32_t* host_slots, uint32_t host_count, bool ps, const uint32_t* mrt,
              uint32_t mrt_count, DrawKind kind);

} // namespace Libs::Graphics::DiagF6

#endif /* EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF5_H_ */
