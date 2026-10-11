# Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(2)-(5)): the measurement code of the F46 pair on top of the
# KYTY_FIX_F26 chain (F16d .. F16o2): the mark M1 by metadata address (RC5 of F45b), the line f26_first_exec
# (KYTY_DIAG_F5ID, RC2(a)), the synthetic positive control KYTY_F26_TINT / KYTY_F26_TINT_DCC (M2, RC3), the test site.
# Every new knob defaults to 0. Usage: python p_f46a.py <repo root> [--check]
# Anchors are whole lines; each must occur exactly once (else the script stops before writing anything). CRLF files keep
# CRLF; the script writes LF otherwise. Refuses to touch the translation signature set (src/graphics/shader/**,
# shaderTranslationCache.cpp, gpu_format.h, gpu_defs.h, imageInfo.h).
import os
import sys

ROOT = sys.argv[1]
CHECK = '--check' in sys.argv

SIGNATURE = ('src/graphics/shader/', 'shaderTranslationCache.cpp', 'gpu_format.h', 'gpu_defs.h', 'imageInfo.h')

EDITS = {}


def edit(path, old, new):
    EDITS.setdefault(path, []).append((old, new))


# ---------------------------------------------------------------------------------------------------------------- diagF5.h
H = 'src/graphics/host_gpu/renderer/diagF5.h'
edit(H, '''// stale question of a pending DCC fill at PrepareDccClear and AdoptPendingDccForTexture (row F26); the FCE acquisition and
// every other PrepareCmaskClear do not read it. Its counters f26_* and the event line DiagF5Ev dcc_stale (KYTY_DIAG_F5).
''', '''// stale question of a pending DCC fill at PrepareDccClear and AdoptPendingDccForTexture (row F26); the FCE acquisition and
// every other PrepareCmaskClear do not read it. Its counters f26_* and the event line DiagF5Ev dcc_stale (KYTY_DIAG_F5).
// Track F, F46a (HPP-798, ROADMAP s122 item 702(e)): the mark M1 of a kept fill keyed by the metadata address (the line
// dcc_stale_apply), the line f26_first_exec (KYTY_DIAG_F5ID) and the synthetic positive control KYTY_F26_TINT /
// KYTY_F26_TINT_DCC (default 0; NOT a measurement when set - the picture changes) - DccApplyLine, FirstExecLine,
// F26TintAt below.
''')
edit(H, '''	F26DeferredDeclined,
	Count
};
''', '''	F26DeferredDeclined,
	// Track F, F46a (HPP-798, item 702(e)(2), (4)): the mark is keyed by the metadata address and a declined mark stays
	// (a later clear of the address takes it): f26_kept_applied <= f26_kept and f26_deferred_declined <= f26_kept (the sum
	// may exceed f26_kept). KYTY_F26_TINT: the DCC fill executions at the key address KYTY_F26_TINT_DCC whose clear value
	// was replaced by (1, 0, 1, 1) (f26_tint_applied) or would have been, the view format having no such encoding
	// (f26_tint_skip). Both 0 with KYTY_F26_TINT = 0.
	F26TintApplied,
	F26TintSkip,
	Count
};
''')
edit(H, '''// ---- Track F, F16o2 (HPP-599, RC1 of F16p, ROADMAP s122 item 507(b)): the deferred clear of an adoption (the
// one-shot mark the event fix=kept why=deferred of AdoptPendingDccForTexture leaves on the image -
// TextureCache::F26Deferred, under m_lock).
// The outcome line of RenderExecutor::MaterializeDeferredDccClear on an image with the mark (the call takes the mark
// whatever its outcome), KYTY_DIAG_F5=1: "DiagF5Ev: dcc_stale_apply n=<n> present=<n> gpu=<n> image=0x... dcc=0x...
// result=<cleared|declined> layers=0x<mask>"; n, image, dcc - of the adopt's dcc_stale line; present / gpu - at the
// outcome (sources as dcc_stale); cleared - >= 1 layer cleared; declined - any return without a clear; layers - the
// pending layer mask the call read (0 when it returned before reading it). The limit of dcc_stale: printed when
// n <= 256 (the adopt's own line was printed). Counting (f26_kept_applied / f26_deferred_declined) is the caller's.
struct DccApplyLine {
	uint64_t n       = 0;
	uint32_t present = 0;
	uint32_t gpu     = 0;
	uint64_t image   = 0;
	uint64_t dcc     = 0;
	bool     cleared = false;
	uint32_t layers  = 0;
};
[[nodiscard]] std::string FormatDccStaleApply(const DccApplyLine& line);
bool                      NoteDccStaleApply(const DccApplyLine& line);
''', '''// ---- Track F, F16o2 (HPP-599, RC1 of F16p, ROADMAP s122 item 507(b)): the deferred clear of a kept fill.
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
''')

# -------------------------------------------------------------------------------------------------------------- diagF5.cpp
C = 'src/graphics/host_gpu/renderer/diagF5.cpp'
edit(C, '''#include "common/logging/log.h"
#include "graphics/host_gpu/renderer/debug.h"
''', '''#include "common/logging/log.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h" // Track F, F46a: DccFixedClearSupported (F26TintAt)
#include "graphics/host_gpu/renderer/debug.h"
''')
edit(C, '''#include <string_view>
''', '''#include <string_view>

#include <vulkan/vulkan_format_traits.hpp> // Track F, F46a: vk::componentCount (F26TintAt)
''')
edit(C, '''    "f26_deferred_declined", // Track F, F16o2 (item 507(b)(3))
};
''', '''    "f26_deferred_declined", // Track F, F16o2 (item 507(b)(3))
    "f26_tint_applied",      // Track F, F46a (item 702(e)(4))
    "f26_tint_skip",
};
''')
edit(C, '''// ---- Track F, F16o2 (HPP-599, ROADMAP s122 item 507(b)(3)): the line dcc_stale_apply.
std::string FormatDccStaleApply(const DccApplyLine& line) {
	return fmt::format("DiagF5Ev: dcc_stale_apply n={} present={} gpu={} image=0x{:016x} dcc=0x{:016x} result={} "
	                   "layers=0x{:08x}",
	                   line.n, line.present, line.gpu, line.image, line.dcc, line.cleared ? "cleared" : "declined",
	                   line.layers);
}
''', '''// ---- Track F, F16o2 (HPP-599, ROADMAP s122 item 507(b)(3)): the line dcc_stale_apply. Track F, F46a (HPP-798, item
// 702(e)(2)): the result dropped and the field site.
const char* DccApplyResultName(DccApplyResult result) {
	switch (result) {
		case DccApplyResult::Cleared: return "cleared";
		case DccApplyResult::Declined: return "declined";
		case DccApplyResult::Dropped: return "dropped";
	}
	return "cleared";
}

const char* F26SiteName(F26Site site) {
	switch (site) {
		case F26Site::Prepare: return "prepare";
		case F26Site::Mat: return "mat";
		case F26Site::Fill: return "fill";
		case F26Site::Unmap: return "unmap";
		case F26Site::Delete: return "delete";
		case F26Site::Retype: return "retype";
		case F26Site::Remark: return "remark";
	}
	return "prepare";
}

std::string FormatDccStaleApply(const DccApplyLine& line) {
	return fmt::format("DiagF5Ev: dcc_stale_apply n={} present={} gpu={} image=0x{:016x} dcc=0x{:016x} result={} "
	                   "layers=0x{:08x} site={}",
	                   line.n, line.present, line.gpu, line.image, line.dcc, DccApplyResultName(line.result),
	                   line.layers, F26SiteName(line.site));
}
''')
edit(C, '''std::vector<std::string> RecentLines() {
	std::scoped_lock lock {g_recent_mutex};
''', '''// ---- Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(3)): the line f26_first_exec.
std::string FormatFirstExec(const FirstExecLine& line) {
	return fmt::format("DiagF5Ev: f26_first_exec n={} present={} dcc=0x{:016x} image=0x{:016x} site={}", line.n,
	                   line.present, line.dcc, line.image, F26SiteName(line.site));
}

bool NoteFirstExec(const FirstExecLine& line) {
	if (line.n == 0 || line.n > 256) { // the limit of dcc_stale
		return false;
	}
	EmitLine(FormatFirstExec(line));
	return true;
}

// ---- Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(4)): KYTY_F26_TINT / KYTY_F26_TINT_DCC.
namespace {
uint32_t ParseTintMode(const char* value) {
	if (value == nullptr) {
		return 0;
	}
	const std::string_view text(value);
	return text == "1" ? 1u : text == "2" ? 2u : 0u;
}

uint64_t ParseTintDcc(const char* value) {
	if (value == nullptr || value[0] == 0) {
		return 0;
	}
	char*      end    = nullptr;
	const auto parsed = std::strtoull(value, &end, 16);
	return end != nullptr && *end == 0 ? static_cast<uint64_t>(parsed) : 0;
}
} // namespace

uint32_t F26TintMode() {
	static const uint32_t mode = ParseTintMode(std::getenv("KYTY_F26_TINT"));
	return mode;
}

uint64_t F26TintDcc() {
	static const uint64_t key = ParseTintDcc(std::getenv("KYTY_F26_TINT_DCC"));
	return key;
}

bool LogF26TintMode() {
	static std::atomic<bool> logged {false};
	if (F26TintMode() == 0 || logged.exchange(true, std::memory_order_relaxed)) {
		return false;
	}
	EmitLine(fmt::format("F26Tint: mode={} dcc=0x{:016x}", F26TintMode(), F26TintDcc()));
	return true;
}

bool F26TintKey(uint64_t address) {
	return F26TintMode() != 0 && address == F26TintDcc();
}

TintResult F26TintAt(uint32_t mode, uint64_t key, uint64_t address, bool removes_mark, vk::Format format,
                     vk::ClearColorValue& clear) {
	if ((mode != 1 && mode != 2) || address != key || (mode == 1 && !removes_mark)) {
		return TintResult::None;
	}
	if (!DccFixedClearSupported(format) || vk::componentCount(format) < 3) {
		return TintResult::Skip;
	}
	clear.float32 = std::array<float, 4> {1.0f, 0.0f, 1.0f, 1.0f};
	return TintResult::Applied;
}

TintResult F26Tint(uint64_t address, bool removes_mark, vk::Format format, vk::ClearColorValue& clear) {
	const auto result = F26TintAt(F26TintMode(), F26TintDcc(), address, removes_mark, format, clear);
	if (result == TintResult::Applied) {
		Add(Counter::F26TintApplied);
	} else if (result == TintResult::Skip) {
		Add(Counter::F26TintSkip);
	}
	return result;
}

std::vector<std::string> RecentLines() {
	std::scoped_lock lock {g_recent_mutex};
''')

# -------------------------------------------------------------------------------------------------------- textureCache.h
TH = 'src/graphics/host_gpu/renderer/cache/textureCache.h'
edit(TH, '''namespace DiagF5 {
struct CmuEvent;   // Track F, F16k (diagF5.h)
struct StaleProbe; // Track F, F16k (diagF5.h)
} // namespace DiagF5
''', '''namespace DiagF5 {
struct CmuEvent;   // Track F, F16k (diagF5.h)
struct StaleProbe; // Track F, F16k (diagF5.h)
enum class F26Site : uint8_t; // Track F, F46a (diagF5.h)
} // namespace DiagF5
''')
edit(TH, '''	// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(2)-(3)): the one-shot deferred mark of an
	// image. NoteF26DeferredLocked - caller holds m_lock (the F26Scope of AdoptPendingDccForTexture, event fix=kept
	// why=deferred); a second such event on the image overwrites the mark. TakeF26Deferred - takes m_lock itself (as
	// MetaClearMask; RenderExecutor::MaterializeDeferredDccClear holds no texture cache lock), removes and returns the
	// mark; false without one (and without taking the lock while no image has a mark). DeleteImage drops a mark without
	// a line. No mark exists with KYTY_FIX_F26 = 0.
	struct F26Deferred {
		uint64_t n     = 0; // the event number of the adopt's dcc_stale line
		uint64_t image = 0; // image / dcc of that line
		uint64_t dcc   = 0;
	};
	void               NoteF26DeferredLocked(ImageId id, const F26Deferred& mark);
	[[nodiscard]] bool TakeF26Deferred(ImageId id, F26Deferred* mark);
''', '''	// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(2)-(3)) and Track F, F46a (HPP-798, item
	// 702(e)(2)-(3), RC5 of F45b): the mark M1 of a kept fill keyed by the METADATA ADDRESS (diagF5.h, DccApplyLine) -
	// set under m_lock by the reporting F26Scope (F26MarkLocked), removed by the execution of the fill at that address
	// by any image (F26ExecLocked / F26Exec), reported once on a MaterializeDeferredDccClear of the address that clears
	// nothing (F26Declined), dropped by a new fill, an erase or a retype of the entry (F26DropLocked); and the armed
	// events of the line f26_first_exec (F26ArmFirstExecLocked; KYTY_DIAG_F5ID), fired by the same execution hook.
	// *Locked - the caller holds m_lock; F26Exec / F26Declined / F26HasMark take it themselves (as MetaClearMask;
	// RenderExecutor::MaterializeDeferredDccClear holds no texture cache lock), and not at all while nothing is stored
	// (the counts). No mark exists with KYTY_FIX_F26 = 0 or KYTY_DIAG_F5 = 0; no armed event without KYTY_DIAG_F5ID.
	struct F26Deferred {
		uint64_t n        = 0; // the event number of the dcc_stale line that set the mark
		uint64_t image    = 0; // image / dcc of that line
		uint64_t dcc      = 0;
		bool     declined = false; // Track F, F46a: the declined line of this mark was printed
	};
	void F26MarkLocked(uint64_t address, const F26Deferred& mark);
	void F26ArmFirstExecLocked(uint64_t address, uint64_t n);
	// `layers` - the clear-mask bits of `address` the execution took 1 -> 0 (called only when != 0).
	void F26ExecLocked(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers);
	void F26Exec(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers);
	void F26Declined(uint64_t address, uint64_t image_address, uint32_t layers);
	void F26DropLocked(uint64_t address, DiagF5::F26Site site, uint32_t layers);
	[[nodiscard]] bool F26HasMarkLocked(uint64_t address) const;
	[[nodiscard]] bool F26HasMark(uint64_t address);
''')
edit(TH, '''	// Track F, F16o2 (item 507(b)(2)): the deferred marks, under m_lock; their number - written under m_lock, read
	// without it by TakeF26Deferred (0: the lock is not taken).
	std::unordered_map<ImageId, F26Deferred>          m_f26_deferred;
	std::atomic<uint32_t>                             m_f26_deferred_count {0};
''', '''	// Track F, F46a (item 702(e)(2)-(3)): the marks M1 by metadata address and the armed f26_first_exec events (event
	// numbers by metadata address), under m_lock; their numbers - written under m_lock, read without it by the fast
	// paths (0: the lock is not taken).
	std::unordered_map<uint64_t, F26Deferred>         m_f26_marks;
	std::atomic<uint32_t>                             m_f26_marks_count {0};
	std::unordered_map<uint64_t, std::vector<uint64_t>> m_f26_first;
	std::atomic<uint32_t>                             m_f26_first_count {0};
''')

# ------------------------------------------------------------------------------------------------------ textureCache.cpp
T = 'src/graphics/host_gpu/renderer/cache/textureCache.cpp'
edit(T, '''	// Track F, F16o2 (item 507(b)(2)): the deferred mark of a deleted image is dropped without a line.
	if (m_f26_deferred_count.load(std::memory_order_relaxed) != 0 && m_f26_deferred.erase(id) != 0) [[unlikely]] {
		m_f26_deferred_count.fetch_sub(1, std::memory_order_relaxed);
	}
''', '')
edit(T, '''			// A later binding may have reused this address for another metadata type.
			m_surface_metas.erase(metadata);
''', '''			// A later binding may have reused this address for another metadata type.
			// Track F, F46a (item 702(e)(2)): the erase drops the mark M1 of the address (site=delete).
			if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) [[unlikely]] {
				F26DropLocked(metadata->first, DiagF5::F26Site::Delete, metadata->second.clear_mask);
			}
			m_surface_metas.erase(metadata);
''')
edit(T, '''// AdoptPendingDccForTexture. Arm() - the probe of the call: passed when the ring is written and KYTY_DIAG_F5 or
''', '''// AdoptPendingDccForTexture. Track F, F46a (HPP-798, item 702(e)(2)-(3)): `cache` - the TextureCache of the site (its
// m_lock is held by the site call). Arm() - the probe of the call: passed when the ring is written and KYTY_DIAG_F5 or
''')
edit(T, '''	explicit F26Scope(DiagF5::DccSite site): m_site(site) {}
''', '''	F26Scope(DiagF5::DccSite site, TextureCache* cache): m_site(site), m_cache(cache) {}
''')
edit(T, '''	// Track F, F16o2 (RC1 of F16p, item 507(b)(1)-(2)): AdoptPendingDccForTexture adopted the kept fill with a clear the
	// call does not apply (RenderExecutor::MaterializeDeferredDccClear clears it later or declines): kept why=deferred;
	// when Report() reports it as kept (KYTY_FIX_F26, KYTY_DIAG_F5), the mark of `id` in `cache` with the line's n (the
	// scope is declared after cache->m_lock is taken and leaves before it is released).
	void Deferred(TextureCache* cache, ImageId id) {
		m_why         = DiagF5::CmuWhy::Deferred;
		m_applied     = false;
		m_defer_cache = cache;
		m_defer_id    = id;
	}
''', '''	// Track F, F16o2 (RC1 of F16p, item 507(b)(1)-(2)): AdoptPendingDccForTexture adopted the kept fill with a clear the
	// call does not apply (RenderExecutor::MaterializeDeferredDccClear clears it later or declines): kept why=deferred.
	// Track F, F46a: the mark of Report() is keyed by the metadata address (the line's dcc).
	void Deferred() {
		m_why     = DiagF5::CmuWhy::Deferred;
		m_applied = false;
	}
	// Track F, F46a (item 702(e)(4), KYTY_F26_TINT=1): this call kept a fill the bucket check called stale (KYTY_FIX_F26,
	// the exact check fresh) - its in-call clear (kept_applied) executes the F26 decision of the call.
	[[nodiscard]] bool KeptNow() const {
		return m_fix && m_probe.bucket_stale && !m_probe.exact_stale && !m_probe.fallback;
	}
''')
edit(T, '''		uint64_t n = 0;
		(void)DiagF5::NoteDccStale(m_line, &n);
		if (m_fix && e.fix == F::Kept && e.why == DiagF5::CmuWhy::Deferred && m_defer_cache != nullptr) {
			m_defer_cache->NoteF26DeferredLocked(m_defer_id, {.n = n, .image = m_line.image, .dcc = m_line.dcc});
		}
	}
''', '''		uint64_t n = 0;
		(void)DiagF5::NoteDccStale(m_line, &n);
		// Track F, F16o2 / F46a (item 702(e)(2), RC5 of F45b): the mark M1 of a kept fill this call did not apply - adopt
		// why=deferred, prepare why=decode - keyed by the metadata address.
		if (m_fix && e.fix == F::Kept &&
		    (e.why == DiagF5::CmuWhy::Deferred || e.why == DiagF5::CmuWhy::Decode)) {
			m_cache->F26MarkLocked(m_line.dcc, {.n = n, .image = m_line.image, .dcc = m_line.dcc});
		}
		// Track F, F46a (item 702(e)(3)): the event arms its f26_first_exec line (both arms, KYTY_DIAG_F5ID) here, when the
		// site call leaves - after any in-call clear, which is not "after the event".
		if (DiagF5Id::On() && n <= 256) [[unlikely]] {
			m_cache->F26ArmFirstExecLocked(m_line.dcc, n);
		}
	}
''')
edit(T, '''	TextureCache*        m_defer_cache = nullptr; // Track F, F16o2: Deferred()
	ImageId              m_defer_id {};
''', '''	TextureCache*        m_cache; // Track F, F46a: the site's cache (marks, armed events)
''')
edit(T, '''	F26Scope f26 {DiagF5::DccSite::Prepare};
''', '''	F26Scope f26 {DiagF5::DccSite::Prepare, this};
''')
edit(T, '''	const uint32_t f5id_mask0 = metadata.clear_mask; // Track F, F16k (KYTY_DIAG_F5ID): NoteClearApplied below
''', '''	const uint32_t f5id_mask0 = metadata.clear_mask; // Track F, F16k (KYTY_DIAG_F5ID): NoteClearApplied below
	// Track F, F46a (item 702(e)(4)): KYTY_F26_TINT - decided once, before the first ClearImage of this call.
	bool f26_tint_decided = false;
''')
edit(T, '''		ClearImage(m_scheduler.Current(), id, view.format,
		           {vk::ImageAspectFlagBits::eColor, view.base_level, view.level_count, start,
''', '''		if (!f26_tint_decided) {
			f26_tint_decided = true;
			if (DiagF5::F26TintKey(desc.info.metadata.range.address)) [[unlikely]] {
				(void)DiagF5::F26Tint(desc.info.metadata.range.address,
				                      f26.KeptNow() || F26HasMarkLocked(desc.info.metadata.range.address), view.format,
				                      clear.color);
			}
		}
		ClearImage(m_scheduler.Current(), id, view.format,
		           {vk::ImageAspectFlagBits::eColor, view.base_level, view.level_count, start,
''')
edit(T, '''	f26.Applied(metadata.clear_mask != f5id_mask0, DiagF5::CmuWhy::NoLayer);
''', '''	f26.Applied(metadata.clear_mask != f5id_mask0, DiagF5::CmuWhy::NoLayer);
	// Track F, F46a (item 702(e)(2)-(3)): the clear-mask bits of this address went 1 -> 0 here - the mark M1 of the address
	// (whichever image set it) and its armed f26_first_exec events are resolved by this image.
	if (metadata.clear_mask != f5id_mask0 && (m_f26_marks_count.load(std::memory_order_relaxed) != 0 ||
	                                          m_f26_first_count.load(std::memory_order_relaxed) != 0)) [[unlikely]] {
		F26ExecLocked(desc.info.metadata.range.address, image.info.data.address, DiagF5::F26Site::Prepare,
		              f5id_mask0 & ~metadata.clear_mask);
	}
''')
edit(T, '''	} else if (metadata.type != MetaDataInfo::Type::CMask) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
		metadata = MetaDataInfo {.type = MetaDataInfo::Type::CMask};
''', '''	} else if (metadata.type != MetaDataInfo::Type::CMask) {
		Common::DrawStat::Mark(Common::DrawStat::Meta);
		BumpMetaEpoch();
		// Track F, F46a (item 702(e)(2)): a retype drops the mark M1 of the address (site=retype).
		if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) [[unlikely]] {
			F26DropLocked(desc.info.metadata.range.address, DiagF5::F26Site::Retype, metadata.clear_mask);
		}
		metadata = MetaDataInfo {.type = MetaDataInfo::Type::CMask};
''')
edit(T, '''			metadata->second = {.type       = MetaDataInfo::Type::HTile,
			                    .clear_mask = image.info.htile_clear_mask};
''', '''			// Track F, F46a (item 702(e)(2)): a retype drops the mark M1 of the address (site=retype).
			if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) [[unlikely]] {
				F26DropLocked(metadata->first, DiagF5::F26Site::Retype, metadata->second.clear_mask);
			}
			metadata->second = {.type       = MetaDataInfo::Type::HTile,
			                    .clear_mask = image.info.htile_clear_mask};
''')
edit(T, '''		found->second.clear_mask = found->second.type == MetaDataInfo::Type::CMask
''', '''		// Track F, F46a (item 702(e)(2)): a new fill of the address drops its mark M1 (site=fill; P1 of F45a).
		if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) [[unlikely]] {
			F26DropLocked(address, DiagF5::F26Site::Fill, found->second.clear_mask);
		}
		found->second.clear_mask = found->second.type == MetaDataInfo::Type::CMask
''')
edit(T, '''	F26Scope   f26 {DiagF5::DccSite::Adopt};
''', '''	F26Scope   f26 {DiagF5::DccSite::Adopt, this};
''')
edit(T, '''		f26.Deferred(this, id);
''', '''		f26.Deferred();
''')
edit(T, '''// Track F, F16o2 (KYTY_FIX_F26, item 507(b)(2)): caller holds m_lock.
void TextureCache::NoteF26DeferredLocked(ImageId id, const F26Deferred& mark) {
	if (m_f26_deferred.insert_or_assign(id, mark).second) {
		m_f26_deferred_count.fetch_add(1, std::memory_order_relaxed);
	}
}

// Track F, F16o2 (item 507(b)(3)): takes m_lock itself, as MetaClearMask; while no image has a mark the lock is not
// taken (the count is written under m_lock by the same GPU thread that calls this [I]).
bool TextureCache::TakeF26Deferred(ImageId id, F26Deferred* mark) {
	if (m_f26_deferred_count.load(std::memory_order_relaxed) == 0) {
		return false;
	}
	std::scoped_lock lock {m_lock};
	const auto       found = m_f26_deferred.find(id);
	if (found == m_f26_deferred.end()) {
		return false;
	}
	*mark = found->second;
	m_f26_deferred.erase(found);
	m_f26_deferred_count.fetch_sub(1, std::memory_order_relaxed);
	return true;
}
''', '''// Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(2)-(3)): the mark M1 by metadata address and the armed f26_first_exec
// events (textureCache.h). *Locked - the caller holds m_lock. The counts are written under m_lock and read without it
// only as "is anything stored" by the same GPU thread [I, as F16o2].
void TextureCache::F26MarkLocked(uint64_t address, const F26Deferred& mark) {
	if (m_f26_marks.contains(address)) [[unlikely]] {
		F26DropLocked(address, DiagF5::F26Site::Remark, 0);
	}
	m_f26_marks.emplace(address, mark);
	m_f26_marks_count.fetch_add(1, std::memory_order_relaxed);
}

void TextureCache::F26ArmFirstExecLocked(uint64_t address, uint64_t n) {
	m_f26_first[address].push_back(n);
	m_f26_first_count.fetch_add(1, std::memory_order_relaxed);
}

void TextureCache::F26ExecLocked(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers) {
	if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) {
		if (const auto found = m_f26_marks.find(address); found != m_f26_marks.end()) {
			DiagF5::Add(DiagF5::Counter::F26KeptApplied);
			(void)DiagF5::NoteDccStaleApply({.n       = found->second.n,
			                                 .present = DiagF5::Present(),
			                                 .gpu     = GpuTimeProfiler::Frame(),
			                                 .image   = image_address,
			                                 .dcc     = found->second.dcc,
			                                 .result  = DiagF5::DccApplyResult::Cleared,
			                                 .layers  = layers,
			                                 .site    = site});
			m_f26_marks.erase(found);
			m_f26_marks_count.fetch_sub(1, std::memory_order_relaxed);
		}
	}
	if (m_f26_first_count.load(std::memory_order_relaxed) != 0) {
		if (const auto found = m_f26_first.find(address); found != m_f26_first.end()) {
			for (const auto n: found->second) {
				(void)DiagF5::NoteFirstExec(
				    {.n = n, .present = DiagF5::Present(), .dcc = address, .image = image_address, .site = site});
			}
			m_f26_first_count.fetch_sub(static_cast<uint32_t>(found->second.size()), std::memory_order_relaxed);
			m_f26_first.erase(found);
		}
	}
}

void TextureCache::F26Exec(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers) {
	if (m_f26_marks_count.load(std::memory_order_relaxed) == 0 &&
	    m_f26_first_count.load(std::memory_order_relaxed) == 0) {
		return;
	}
	std::scoped_lock lock {m_lock};
	F26ExecLocked(address, image_address, site, layers);
}

void TextureCache::F26Declined(uint64_t address, uint64_t image_address, uint32_t layers) {
	if (m_f26_marks_count.load(std::memory_order_relaxed) == 0) {
		return;
	}
	std::scoped_lock lock {m_lock};
	const auto       found = m_f26_marks.find(address);
	if (found == m_f26_marks.end() || found->second.declined) {
		return;
	}
	found->second.declined = true;
	DiagF5::Add(DiagF5::Counter::F26DeferredDeclined);
	(void)DiagF5::NoteDccStaleApply({.n       = found->second.n,
	                                 .present = DiagF5::Present(),
	                                 .gpu     = GpuTimeProfiler::Frame(),
	                                 .image   = image_address,
	                                 .dcc     = found->second.dcc,
	                                 .result  = DiagF5::DccApplyResult::Declined,
	                                 .layers  = layers,
	                                 .site    = DiagF5::F26Site::Mat});
}

void TextureCache::F26DropLocked(uint64_t address, DiagF5::F26Site site, uint32_t layers) {
	const auto found = m_f26_marks.find(address);
	if (found == m_f26_marks.end()) {
		return;
	}
	(void)DiagF5::NoteDccStaleApply({.n       = found->second.n,
	                                 .present = DiagF5::Present(),
	                                 .gpu     = GpuTimeProfiler::Frame(),
	                                 .image   = found->second.image,
	                                 .dcc     = found->second.dcc,
	                                 .result  = DiagF5::DccApplyResult::Dropped,
	                                 .layers  = layers,
	                                 .site    = site});
	m_f26_marks.erase(found);
	m_f26_marks_count.fetch_sub(1, std::memory_order_relaxed);
}

bool TextureCache::F26HasMarkLocked(uint64_t address) const {
	return m_f26_marks_count.load(std::memory_order_relaxed) != 0 && m_f26_marks.contains(address);
}

bool TextureCache::F26HasMark(uint64_t address) {
	if (m_f26_marks_count.load(std::memory_order_relaxed) == 0) {
		return false;
	}
	std::scoped_lock lock {m_lock};
	return m_f26_marks.contains(address);
}
''')
edit(T, '''		metadata = m_surface_metas.erase(metadata);
''', '''		// Track F, F46a (item 702(e)(2)): the erase drops the mark M1 of the address (site=unmap; C4 of F45a).
		if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) [[unlikely]] {
			F26DropLocked(metadata->first, DiagF5::F26Site::Unmap, metadata->second.clear_mask);
		}
		metadata = m_surface_metas.erase(metadata);
''')

# ------------------------------------------------------------------------------------------------------- descriptors.cpp
D = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
edit(D, '''// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(3)): one MaterializeDeferredDccClear call on an
// image that carries the deferred mark of AdoptPendingDccForTexture (event fix=kept why=deferred). The constructor
// takes the mark (TextureCache::TakeF26Deferred - m_lock taken inside, as MetaClearMask; the call holds no cache
// lock), so it is removed whatever the outcome; the destructor (every return of the call) reports it: cleared (>= 1
// layer cleared) - f26_kept_applied, declined (any return without a clear) - f26_deferred_declined, and the line
// DiagF5Ev dcc_stale_apply. Without KYTY_FIX_F26 nothing is taken (no mark exists) and nothing is reported.
class F26ApplyScope {
public:
	F26ApplyScope(TextureCache& cache, ImageId id) {
		if (DiagF5::FixF26On()) [[unlikely]] {
			m_armed = cache.TakeF26Deferred(id, &m_mark);
		}
	}
	~F26ApplyScope() {
		if (m_armed) [[unlikely]] {
			DiagF5::Add(m_cleared ? DiagF5::Counter::F26KeptApplied : DiagF5::Counter::F26DeferredDeclined);
			(void)DiagF5::NoteDccStaleApply({.n       = m_mark.n,
			                                   .present = DiagF5::Present(),
			                                   .gpu     = GpuTimeProfiler::Frame(),
			                                   .image   = m_mark.image,
			                                   .dcc     = m_mark.dcc,
			                                   .cleared = m_cleared,
			                                   .layers  = m_layers});
		}
	}
	F26ApplyScope(const F26ApplyScope&)            = delete;
	F26ApplyScope& operator=(const F26ApplyScope&) = delete;

	// The pending layer mask the call read.
	void Layers(uint32_t mask) { m_layers = mask; }
	// Every layer of that mask was cleared.
	void Cleared() { m_cleared = true; }

private:
	TextureCache::F26Deferred m_mark {};
	bool                      m_armed   = false;
	bool                      m_cleared = false;
	uint32_t                  m_layers  = 0;
};
''', '''// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(3)); Track F, F46a (HPP-798, item 702(e)(2), RC5
// of F45b): one MaterializeDeferredDccClear call of an image with DCC metadata. The mark M1 is keyed by the metadata
// address: a call whose layer loop clears takes it (TextureCache::F26Exec after the loop, whichever image set it -
// dcc_stale_apply result=cleared site=mat, f26_kept_applied); a call that returns without a clear does not remove it -
// the destructor reports the first such return per mark (TextureCache::F26Declined - m_lock taken inside, the call
// holds no cache lock: dcc_stale_apply result=declined site=mat, f26_deferred_declined). Without KYTY_FIX_F26 nothing
// is reported (no mark exists).
class F26ApplyScope {
public:
	F26ApplyScope(TextureCache& cache, const Image& image)
	    : m_cache(cache), m_on(DiagF5::FixF26On() && image.info.metadata.kind == ImageMetadataKind::Dcc),
	      m_address(image.info.metadata.range.address), m_image(image.info.data.address) {}
	~F26ApplyScope() {
		if (m_on && !m_cleared) [[unlikely]] {
			m_cache.F26Declined(m_address, m_image, m_layers);
		}
	}
	F26ApplyScope(const F26ApplyScope&)            = delete;
	F26ApplyScope& operator=(const F26ApplyScope&) = delete;

	// The pending layer mask the call read.
	void Layers(uint32_t mask) { m_layers = mask; }
	// Every layer of that mask was cleared.
	void Cleared() { m_cleared = true; }

private:
	TextureCache& m_cache;
	bool          m_on;
	uint64_t      m_address;
	uint64_t      m_image;
	bool          m_cleared = false;
	uint32_t      m_layers  = 0;
};
''')
edit(D, '''	// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(3)): the deferred mark of an adoption is
	// taken here, before any return; the outcome (dcc_stale_apply) is reported when the call returns. Nothing without
	// the knob.
	F26ApplyScope f26_apply {cache, id};
''', '''	// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(3)); Track F, F46a (item 702(e)(2)): a return
	// without a clear reports the mark of the metadata address as declined (it stays). Nothing without the knob.
	F26ApplyScope f26_apply {cache, image};
''')
edit(D, '''		DiagF5::Add(DiagF5::Counter::DccMatCleared);
	}
''', '''		DiagF5::Add(DiagF5::Counter::DccMatCleared);
	}
	// Track F, F46a (item 702(e)(4)): KYTY_F26_TINT at the key address (mode 1 - the address carries an F26 mark the clear
	// below removes).
	if (DiagF5::F26TintKey(address)) [[unlikely]] {
		(void)DiagF5::F26Tint(address, cache.F26HasMark(address), clear_format, clear);
	}
''')
edit(D, '''	f26_apply.Cleared(); // Track F, F16o2: every layer of the mask was cleared above
''', '''	f26_apply.Cleared(); // Track F, F16o2: every layer of the mask was cleared above
	// Track F, F46a (item 702(e)(2)-(3)): the clear-mask bits of `address` went 1 -> 0 in the loop above (TouchMeta) - the
	// mark M1 of the address (whichever image set it) and its armed f26_first_exec events are resolved by this image.
	cache.F26Exec(address, image.info.data.address, DiagF5::F26Site::Mat, mask);
''')

# ------------------------------------------------------------------------------------------------------- vulkanWindow.cpp
W = 'src/graphics/presentation/window/vulkanWindow.cpp'
edit(W, '''	(void)DiagF5::LogFixF26Mode(); // Track F, F16o (item 504(e)(1)): "FixF26: mode=1" once, same point
''', '''	(void)DiagF5::LogFixF26Mode(); // Track F, F16o (item 504(e)(1)): "FixF26: mode=1" once, same point
	(void)DiagF5::LogF26TintMode(); // Track F, F46a (item 702(e)(4)): "F26Tint: mode= dcc=" once when KYTY_F26_TINT is set
''')


def main():
    for path in EDITS:
        norm = path.replace('\\', '/')
        if any(s in norm for s in SIGNATURE):
            print('REFUSED: signature set', path)
            sys.exit(2)
    out = {}
    for path, edits in EDITS.items():
        full = os.path.join(ROOT, path)
        raw = open(full, 'rb').read()
        crlf = b'\r\n' in raw
        text = raw.decode('utf-8').replace('\r\n', '\n')
        for old, new in edits:
            n = text.count(old)
            if n != 1:
                print('ANCHOR %s count %d: %r' % (path, n, old[:100]))
                sys.exit(3)
            text = text.replace(old, new)
        if crlf:
            text = text.replace('\n', '\r\n')
        out[full] = text.encode('utf-8')
    if CHECK:
        print('CHECK OK', len(EDITS), 'files', sum(len(e) for e in EDITS.values()), 'edits')
        return
    for full, data in out.items():
        open(full, 'wb').write(data)
    print('PATCHED', len(EDITS), 'files', sum(len(e) for e in EDITS.values()), 'edits')


if __name__ == '__main__':
    main()
