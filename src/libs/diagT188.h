#pragma once

// Track M, M9d (HPP-869, ROADMAP s122 item 785; design docs/track-m/m9a2/design_m9a2.md edition 2 with the decisions
// 785(b)-(v)): KYTY_DIAG_T188 - stage 1 of T188, the image range that a partial GPU write of the guest memory
// invalidates (TextureCache::InvalidateMemoryFromGPU drops IsGpuModified and marks the image buffer-modified, so the next
// upload refreshes the whole SourceRange() from the buffer, which does not hold what the GPU rendered).
//   0 (default) - nothing; one "T188: mode=0 cls=all k=4" line per process.
//   1 - counting only (MEASUREMENT ONLY: no decision of the emulator changes), with the T109 counters (DiagT109).
//   2 - counting + tint of the LOST levels (uploaded by the closing upload, not intersecting the union of the episode's
//       writes) magenta (1, 0, 1, 1) with readback control; changes the picture - no measurement, not for shipping.
//   3 - counting + tint of EVERY level uploaded by the closing upload of an episode image (positive control K-P).
// KYTY_DIAG_T188_CLS - comma separated class keys (16 hex digits); limits only the tint (2, 3); empty - all classes.
// Lines: "T188Stat: when=<periodic|exit>", "T188Img: when=exit key=...", "T109Stat: when=<periodic|exit>" (mode >= 1).
// Every site function below takes `locked` - TrackingSpinLock::HeldByCurrentThread() of TextureCache::m_lock at the site;
// false counts lock_bad (invariant 0) and the site does no work. The counters are relaxed atomics; the class table and
// the readback registry are guarded by a mutex of this file, taken only after m_lock (callbacks take only that mutex).
// Outside the translation signature set (src/graphics/shader/**, imageInfo.h, gpu_format.h, gpu_defs.h not touched).

#include <atomic>
#include <cstdint>

struct VkViewport;
struct VkRect2D;

namespace Libs::DiagT188 {

// KYTY_DIAG_T188, read by the static initialization of diagT188.cpp (getenv only): unset, "", 0/false/off/no - 0;
// "1", "2", "3" - that value; anything else - 0.
extern int g_mode;
[[nodiscard]] inline int Mode() noexcept {
	return g_mode;
}
// "T188: mode=<0..3> cls=<all|n> k=<K>" once per process (TextureCache's constructor and the stands).
void PrintModeLine();

constexpr uint32_t K         = 4;   // readbacks per class (ROADMAP s122 item 785(v)(1))
constexpr uint32_t kSpans    = 8;   // intervals of the union of the writes of an episode
constexpr uint32_t kImgLines = 256; // T188Img lines, then key=other
constexpr uint32_t kLevels   = 32;  // bit masks of levels

enum class Writer : uint8_t { Unk = 0, St = 1, Fill = 2, Copy = 3 };
// The closures, in the order of the cl_* fields.
enum class Close : uint8_t { Smp, Rt, RtClr, Dt, Sto, ClrOp, Oth, Vo, Cover, Cmp, Msaa, Free, Commit, CopyDst, Skip, Count };

struct Span {
	uint64_t b = 0; // [b, e) of guest addresses
	uint64_t e = 0;
};

// Image::t188. Everything but the atomics only under TextureCache::m_lock.
struct ImageState {
	bool     open        = false; // episode open (S2 / S8 .. a closure)
	bool     wait        = false; // a closing upload left deferred levels (S3 .. S3b / S3c / S5 / a new S3)
	bool     ovf         = false; // the union of the episode overflowed kSpans
	bool     pend_ovf    = false;
	bool     pend_skip   = false; // the tint of the deferred part is skipped (decided at S3)
	bool     pend_tinted = false; // S3 tinted >= 1 level of the episode whose deferred part waits
	uint8_t  writer      = 0;     // Writer of the opening write
	uint8_t  n           = 0;     // intervals in w
	uint8_t  pend_n      = 0;
	uint64_t key         = 0;     // class key, fixed at the opening (S2 / S8)
	uint64_t pend_key    = 0;
	Span     w[kSpans] {};
	Span     pend_w[kSpans] {};
	uint32_t rb_first    = 0;     // readback group of the last tint (registry ids [rb_first, rb_first + rb_count))
	uint32_t rb_count    = 0;
	uint32_t rb_frame    = 0;     // GpuTimeProfiler::Frame() of that tint
	// Any thread.
	std::atomic<uint64_t> wseq {0};          // moves at every MarkGpuModified (mode >= 1)
	std::atomic<uint64_t> sseq {UINT64_MAX}; // wseq at the last full SynchronizeBufferFromImage
	std::atomic<uint64_t> dseq {UINT64_MAX}; // wseq at the last DownloadImageMemory
	std::atomic<uint8_t>  rb_pend {0};       // a readback group waits for its rb1
	std::atomic<uint8_t>  rb_wr {0};         // the image was written after its tint (while rb_pend)
};

// Sw: the first statement of Image::MarkGpuModified (RC13(a)); unconditional at mode >= 1 (RC13(b)).
inline void NoteGpuWrite(ImageState& s) noexcept {
	s.wseq.fetch_add(1, std::memory_order_acq_rel);
	if (s.rb_pend.load(std::memory_order_acquire) != 0) {
		s.rb_wr.store(1, std::memory_order_release);
	}
}
// A write of the image that is not a MarkGpuModified (uploads, clears, copies; RC12): only the readback flag.
inline void NoteImageWrite(ImageState& s) noexcept {
	if (s.rb_pend.load(std::memory_order_acquire) != 0) {
		s.rb_wr.store(1, std::memory_order_release);
	}
}

struct ClassFields {
	uint32_t fmt     = 0; // info.pixel_format (vk::Format)
	uint32_t tile    = 0; // info.tile_mode
	uint32_t w       = 0;
	uint32_t h       = 0;
	uint32_t levels  = 0;
	uint32_t layers  = 0;
	uint32_t cmp     = 0; // bit 0 IsBlock(), bit 1 metadata.compression != Uncompressed
	uint32_t samples = 0;
	uint32_t usage   = 0; // ImageUsage at S2: 1 texture, 2 storage, 4 render_target, 8 depth_target, 16 video_out
	uint32_t vol     = 0;
};
// FNV-1a 64 over the 8 little-endian bytes of every field in the order above.
[[nodiscard]] uint64_t ClassKey(const ClassFields& f) noexcept;
// True if the class is listed in KYTY_DIAG_T188_CLS (or the list is empty).
[[nodiscard]] bool ClassListed(uint64_t key) noexcept;

struct Mip {
	uint64_t offset = 0; // from the image's base address
	uint64_t size   = 0; // every layer of the level
};
struct Geometry {
	uint64_t   address     = 0; // info.data.address
	uint64_t   data_size   = 0; // info.data.size
	uint64_t   source_size = 0; // SourceRange().size
	uint32_t   levels      = 0;
	uint32_t   layers      = 0;
	bool       volume      = false;
	const Mip* mips        = nullptr; // `levels` entries
};

// Pure helpers (stand).
[[nodiscard]] bool     CoversSource(const Geometry& g, uint64_t address, uint64_t size) noexcept;
enum class Shape : uint8_t { MipAligned, InMip, Other };
[[nodiscard]] Shape    WShape(const Geometry& g, uint64_t address, uint64_t size) noexcept;
[[nodiscard]] uint64_t IntersectLen(uint64_t b, uint64_t e, const Span* w, uint32_t n) noexcept;
// Magenta (1, 0, 1, 1) as the texel bytes of vk_format; false - no row in the table of design s.5.3.
[[nodiscard]] bool MagentaCode(uint32_t vk_format, uint8_t code[16], uint32_t* bytes) noexcept;
[[nodiscard]] bool TexelIsMagenta(uint32_t vk_format, const uint8_t* texel) noexcept;

// What the site has to tint and read back after a closing upload / a deferred upload.
struct TintPlan {
	uint32_t mask    = 0; // levels to clear magenta
	uint32_t rb_mask = 0; // of them, the levels to read back (<= K per class)
	uint64_t key     = 0;
};

enum class Ev : uint8_t { None, Cover, Join, Synced, Dlmem, Reopen, New };
// S2: one (call, image) pair of InvalidateMemoryFromGPU before ClearGpuModified. cf - the class fields now.
Ev NoteInvalidate(ImageState& s, const Geometry& g, const ClassFields& cf, bool gpu_modified, Writer writer,
                  uint64_t address, uint64_t size, bool in_pass, bool locked);
// S3: a closing upload of levels [first, end); deferred levels [pend_first, pend_end) stay (pend_end <= pend_first:
// none). cf_now - the class fields at the closure (the episode keeps its S2 class; the argument exists so that the
// mutant "class taken at the closure" can be written). fmt_ok - T188Gpu::TintFormatOk; cpu_dirty - IsCpuDirty().
TintPlan CloseUpload(ImageState& s, const Geometry& g, const ClassFields& cf_now, Close site, uint32_t first,
                     uint32_t end, uint32_t pend_first, uint32_t pend_end, bool fmt_ok, bool cpu_dirty, bool locked);
// S3b: the deferred levels [first, end) uploaded now.
TintPlan PendDone(ImageState& s, const Geometry& g, uint32_t first, uint32_t end, bool locked);
// S3c: the deferred levels dropped without an upload.
void PendDrop(ImageState& s, bool locked);
// S4, S7, S7b, S7c: a closure without an upload.
void CloseNoUpload(ImageState& s, Close site, bool locked);
// S5: FreeImage (the readback group of the image is abandoned).
void NoteFree(ImageState& s, bool locked);
// S8: CopyImage carries the buffer-modified mark of the source to the destination of the same data range.
void Propagate(ImageState& dst, const ImageState& src, const Geometry& gdst, const ClassFields& cf_dst, bool locked);
// Ss: SynchronizeBufferFromImage returned true; full - every level (a volume - always whole).
void NoteSync(ImageState& s, bool full, bool locked);
// Sd: DownloadImageMemory returned true.
void NoteDownload(ImageState& s, bool locked);
// The independent check of a plan: bits outside [first, end), of an empty level or (mode 2) of a level that intersects
// the union count tint_bad and are removed.
[[nodiscard]] uint32_t VerifyTintPlan(const Geometry& g, uint32_t mask, uint32_t first, uint32_t end, const Span* w,
                                      uint32_t n);

// Readback registry (mode >= 2). The site records the reads, then registers them.
struct RbInfo {
	uint32_t id         = 0;
	uint32_t level      = 0;
	uint32_t x          = 0;
	uint32_t y          = 0;
	uint32_t last_layer = 0; // 0 - only layer 0 is read
	uint32_t fmt        = 0;
};
// The readbacks rb0 of the levels of plan.rb_mask, recorded right after their clears: count entries, ids
// [first, first + count). An older group of the image is abandoned (its pending rb1 count tint_rb1_none).
uint32_t RbBegin(ImageState& s, const TintPlan& plan, const Geometry& g, uint32_t width, uint32_t height,
                 uint32_t vk_format, uint32_t frame);
// The site could not record the readbacks of a plan (no mapping): they count tint_rb0_none.
void RbNotRecorded(const TintPlan& plan);
// rb0 result (callback of the completed tick).
void RbDone0(uint32_t id, bool magenta);
// A visit of the image (S2-S8, Svo) in a frame after the tint: the entries whose rb0 was magenta and whose rb1 is due;
// rb_wr is snapshotted into them and they go "in flight". At most `max`. When nothing of the group is left, rb_pend = 0.
uint32_t RbWant1(ImageState& s, uint32_t frame, RbInfo* out, uint32_t max);
// The visit could not record the rb1 reads of `ids`: they count tint_rb1_none.
void RbNotRecorded1(const RbInfo* infos, uint32_t count);
// rb1 result (callback).
void RbDone1(uint32_t id, bool magenta);
// Readbacks in flight (rb0 or rb1 recorded, result not in).
[[nodiscard]] uint32_t RbInFlight();

// S6: the exit scan of the images (sums of the flags) - ep_bad when they differ from the counters of open episodes and
// waiting deferred parts.
void ExitScan(uint64_t open_flags, uint64_t wait_flags);
// The exit hook of the texture cache (S6: m_lock, scan, then PrintExit). Set by the TextureCache at mode >= 1;
// SetExitHook(nullptr, context) clears it only if `context` is the one set.
using ExitHook = void (*)(void* context);
void SetExitHook(ExitHook hook, void* context);
// Finalizes the readbacks (not completed - *_none) and prints T188Stat / T188Img / T109Stat when=exit.
void PrintExit();
// Both exits of Execute (emulator.cpp): mode >= 1 - the hook (or PrintExit without one); 0 - nothing.
void PrintExitStat();
// One queued AudioOut2 push (libAudio2.cpp, mode >= 1): the periodic T188Stat / T109Stat every 4096.
void NoteAudioPush();
void PrintStat(const char* when);

// Counters for the stand (index order = the order of the T188Stat fields).
enum class C : uint32_t {
	part, part_st, part_fill, part_copy, part_unk, part_off, part_synced, part_dlmem, reopen, ep_new, ep_prop, prop_merge,
	w_mipal, w_inmip, w_other, w_bytes, img_bytes, img_bytes_unsync, img_full_unsync, in_pass, in_pass_unsync,
	cl_smp, cl_rt, cl_rtclr, cl_dt, cl_sto, cl_clrop, cl_oth, cl_vo, cl_cover, cl_cmp, cl_msaa, cl_free, cl_commit,
	cl_copydst, cl_skip, cl_none, open, ep_pend, pend_done, pend_drop, pend_free, pend_open, lost_bytes,
	lost_pend_bytes, w_ovf, sync_full, sync_part, dl_mem, ep_bad, lock_bad, tint_ep, tint_mips, tint_bytes,
	tint_part_mips, tint_skip_fmt, tint_skip_vol, tint_skip_cls, tint_skip_cpu, tint_skip_ovf, tint_bad, tint_rb_req,
	tint_rb0_ok, tint_rb0_bad, tint_rb0_none, tint_rb0_nofmt, tint_rb1_ok, tint_rb1_over, tint_rb1_bad, tint_rb1_none,
	Count
};
[[nodiscard]] uint64_t Read(C counter) noexcept;
// Class counters (T188Img), index order = the order of its fields.
enum class CC : uint32_t {
	ev, ev_st, ev_fill, ev_copy, ev_off, ev_synced, ev_dlmem, ep_new, ep_prop, cl_smp, cl_rt, cl_rtclr, cl_vo, cl_commit,
	cl_free, lost_bytes, lost_pend_bytes, img_bytes, tint_ep, tint_mips, tint_bytes, tint_skip, tint_rb0_ok,
	tint_rb0_bad, tint_rb1_ok, tint_rb1_over, tint_rb1_bad, Count
};
[[nodiscard]] uint64_t ReadClass(uint64_t key, CC counter);
// Stand only: every counter, the class table and the registry back to zero.
void ResetForStand();

} // namespace Libs::DiagT188

namespace Libs::DiagT109 {

// SetGraphicsDynamicParams, one call per draw (mode >= 1): depth_format - the depth target's view format (VkFormat;
// VK_FORMAT_UNDEFINED without a target), test / write - depth_test_enable / depth_write_enable, z_export -
// db_shader_control.shader_z_export_enable, bias - depth_bias_enable, viewports / scissors / count - the computed
// VkViewport and VkRect2D arrays passed to vkCmdSetViewportWithCount / vkCmdSetScissorWithCount (after minDepth /
// maxDepth and the empty-slot rule). Track M, M9d2 (RC1 of M9e, ROADMAP s122 item 788(b)): a slot counts only when
// its scissor has area > 0 (it rasterizes); its clamp range is [min(minDepth, maxDepth), max(minDepth, maxDepth)].
void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,
              const VkRect2D* scissors, uint32_t count);
// HwCtxSetDepthMetadataRegister, the DB_RENDER_OVERRIDE branch (every path of the register): one write.
void NoteRenderOverride(uint32_t value);

struct Totals {
	uint64_t d32;
	uint64_t zx_d32;
	uint64_t zx_narrow;
	uint64_t bias_d32;
	uint64_t bias_narrow;
	uint64_t ovr_w;
	uint64_t ovr_vpc;
};
[[nodiscard]] Totals Read();
void                 PrintStat(const char* when);
void                 ResetForStand();

} // namespace Libs::DiagT109
