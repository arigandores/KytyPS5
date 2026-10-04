"""F16k (HPP-583, ROADMAP s122 item 492(v), (g)): patch of src/graphics/host_gpu/renderer/diagF5.cpp.

    python p_diag_cpp.py <repo root>

LF in, LF out (a CR in the file is an error). Every anchor is a whole line (or whole lines) and must occur once.
"""
import sys

ROOT = sys.argv[1]
PATH = ROOT + "/src/graphics/host_gpu/renderer/diagF5.cpp"


def sub_once(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit("anchor count %d for %r" % (n, old[:80]))
    return text.replace(old, new)


data = open(PATH, "rb").read()
if b"\r" in data:
    raise SystemExit("CR in " + PATH)
t = data.decode("utf-8")

t = sub_once(t, r'''#include "graphics/host_gpu/renderer/debug.h"

#include <fmt/format.h>

#include <chrono>
#include <cstdlib>
#include <mutex>
''', r'''#include "graphics/host_gpu/renderer/debug.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"

#include <fmt/format.h>

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <deque>
#include <map>
#include <mutex>
#include <string_view>
''')

t = sub_once(t, r'''    "zero_disp",
};
static_assert(std::size(F5Names) == static_cast<size_t>(DiagF5::Counter::Count));
''', r'''    "zero_disp",
    "f5cmu_kept",
    "f5cmu_kept_applied",
    "f5cmu_exact_stale",
    "f5cmu_fallback",
    "dcc_stale_bucket_only",
    "dcc_stale_fallback",
    "cmask_rt_bucket_only",
};
static_assert(std::size(F5Names) == static_cast<size_t>(DiagF5::Counter::Count));
''')

# The F16k part of the anonymous namespace: the recent lines and the state of KYTY_DIAG_F5ID.
t = sub_once(t, r'''static_assert(std::size(F6Names) == static_cast<size_t>(DiagF6::Counter::Count));

} // namespace
''', r'''static_assert(std::size(F6Names) == static_cast<size_t>(DiagF6::Counter::Count));

// ---- Track F, F16k (HPP-583, ROADMAP s122 item 492): the lines of KYTY_FIX_F5CMU / KYTY_DIAG_F5ID go to the log and to a
// list the test site reads (the last 4096).
std::mutex              g_recent_mutex;
std::deque<std::string> g_recent;

void EmitLine(const std::string& line) {
	LOGF("%s\n", line.c_str());
	std::scoped_lock lock {g_recent_mutex};
	g_recent.push_back(line);
	if (g_recent.size() > 4096) {
		g_recent.pop_front();
	}
}

// The state of KYTY_DIAG_F5ID (item 492(g)): one mutex, a leaf (only EmitLine - the logger - is called under it).
namespace Id = DiagF5Id;

constexpr const char* IdNames[] = {
    "fce",          "r0",          "r1",           "r2",           "r3",              "r4",
    "r5",           "r6",          "r7",           "cs",           "img_clear",       "meta_clear",
    "tracked",      "tracked_other", "exec_nofill", "exec_fill_clear", "exec_fill_other", "changed",
    "changed_na",   "marks_set",   "marks_dropped", "marks_overflow", "stale_apply",   "next_texture",
    "next_target",  "next_none",   "next_exit",    "next_cleared", "next_bufreads",   "next_merged",
    "next_overflow", "keys_fce",   "keys_cs",      "overflow_fce", "overflow_cs",
};
enum IdCounter : uint32_t {
	kFce,
	kR0,
	kR1,
	kR2,
	kR3,
	kR4,
	kR5,
	kR6,
	kR7,
	kCs,
	kImgClear,
	kMetaClear,
	kTracked,
	kTrackedOther,
	kExecNoFill,
	kExecFillClear,
	kExecFillOther,
	kChanged,
	kChangedNa,
	kMarksSet,
	kMarksDropped,
	kMarksOverflow,
	kStaleApply,
	kNextTexture,
	kNextTarget,
	kNextNone,
	kNextExit,
	kNextCleared,
	kNextBufReads,
	kNextMerged,
	kNextOverflow,
	kKeysFce,
	kKeysCs,
	kOverflowFce,
	kOverflowCs,
	kIdCount
};
static_assert(std::size(IdNames) == kIdCount);

constexpr uint32_t kKeysPerSite    = 256;
constexpr uint32_t kLinesPerKey    = 4;
constexpr uint32_t kOpenMax        = 64;
constexpr uint32_t kMarksMax       = 4096;
constexpr uint32_t kStaleLines     = 64;
constexpr uint32_t kNoneFrames     = 600;
constexpr uint32_t kSumFrames      = 600;

struct IdFceKey {
	uint64_t base     = 0;
	uint64_t dcc      = 0;
	Id::Miss why      = Id::Miss::None;
	uint64_t n        = 0;
	uint64_t texture  = 0;
	uint64_t target   = 0;
	uint64_t none     = 0;
	uint64_t exit     = 0;
	uint64_t cleared  = 0;
	uint64_t bufreads = 0;
	bool     dirty    = false;
};
struct IdCsKey {
	uint64_t     shader      = 0;
	uint64_t     addr        = 0;
	Id::CsClass  cls         = Id::CsClass::Exec;
	uint64_t     n           = 0;
	uint64_t     stale_apply = 0;
	bool         dirty       = false;
};
struct IdOpen {
	uint64_t              base       = 0;
	uint64_t              surface    = 0;
	int                   key        = -1;
	bool                  printed    = false;
	uint32_t              open_frame = 0;
	uint64_t              merged     = 0;
	bool                  bound      = false;
	Id::BindKind          kind       = Id::BindKind::Texture;
	uint32_t              bind_frame = 0;
	ImageMetadataKind     meta_kind  = ImageMetadataKind::None;
	uint64_t              meta_addr  = 0;
	bool                  cleared    = false;
	uint64_t              buf_reads  = 0;
};
struct IdMark {
	uint64_t    shader = 0;
	Id::CsClass cls    = Id::CsClass::Exec;
	uint32_t    frame  = 0;
	int         key    = -1;
};
struct IdState {
	std::mutex                      mutex;
	std::array<uint64_t, kIdCount>  cnt {};
	std::vector<IdFceKey>           fce_keys;
	std::vector<IdCsKey>            cs_keys;
	std::vector<IdOpen>             open;
	std::map<uint64_t, IdMark>      marks;
	std::map<uint64_t, uint64_t>    fill_seq;
	uint64_t                        stale_lines = 0;
	bool                            printed     = false;
	uint32_t                        last_frame  = 0;
	uint64_t                        last_total  = 0;
	std::atomic<uint32_t>           open_count {0};
	std::atomic<uint32_t>           mark_count {0};
};

IdState& IdS() {
	static IdState state;
	return state;
}

const char* MissName(Id::Miss why) {
	switch (why) {
		case Id::Miss::None: return "r0";
		case Id::Miss::R1: return "r1";
		case Id::Miss::R2: return "r2";
		case Id::Miss::R3: return "r3";
		case Id::Miss::R4: return "r4";
		case Id::Miss::R5: return "r5";
		case Id::Miss::R6: return "r6";
		case Id::Miss::R7: return "r7";
	}
	return "r0";
}

const char* WrAfterName(Id::WrAfter wr) {
	switch (wr) {
		case Id::WrAfter::None: return "none";
		case Id::WrAfter::Exact: return "exact";
		case Id::WrAfter::Fallback: return "fallback";
		case Id::WrAfter::Na: return "na";
	}
	return "na";
}

const char* CsClassName(Id::CsClass cls) {
	switch (cls) {
		case Id::CsClass::ImgClear: return "img_clear";
		case Id::CsClass::MetaClear: return "meta_clear";
		case Id::CsClass::Tracked: return "tracked";
		case Id::CsClass::TrackedOther: return "tracked_other";
		case Id::CsClass::Exec: return "exec";
	}
	return "exec";
}

const char* BindKindName(Id::BindKind kind) {
	return kind == Id::BindKind::Texture ? "texture" : "target";
}

const char* ApplySiteName(Id::ApplySite site) {
	switch (site) {
		case Id::ApplySite::DccRt: return "dcc_rt";
		case Id::ApplySite::CmaskRt: return "cmask_rt";
		case Id::ApplySite::Mat: return "mat";
		case Id::ApplySite::Fce: return "fce";
	}
	return "mat";
}

std::string MetaKindAt(ImageMetadataKind kind, uint64_t address) {
	switch (kind) {
		case ImageMetadataKind::None: return "None";
		case ImageMetadataKind::Htile: return fmt::format("Htile@0x{:x}", address);
		case ImageMetadataKind::Dcc: return fmt::format("Dcc@0x{:x}", address);
		case ImageMetadataKind::Cmask: return fmt::format("Cmask@0x{:x}", address);
	}
	return "None";
}

bool SameSnap(const Id::MetaSnap& a, const Id::MetaSnap& b) {
	return a.type == b.type && a.clear_mask == b.clear_mask && a.fill_value == b.fill_value &&
	       a.fill_size == b.fill_size && a.fill_seq == b.fill_seq;
}

// Caller holds IdS().mutex. Closes record `i` (kind name) and erases it.
void IdClose(IdState& s, size_t i, const char* kind, uint32_t frame) {
	const auto rec = s.open[i];
	s.open.erase(s.open.begin() + static_cast<std::ptrdiff_t>(i));
	IdFceKey* key = rec.key >= 0 ? &s.fce_keys[static_cast<size_t>(rec.key)] : nullptr;
	const bool texture = rec.bound && rec.kind == Id::BindKind::Texture;
	const bool target  = rec.bound && rec.kind == Id::BindKind::Target;
	const bool none    = !rec.bound && std::string_view {kind} == "none";
	s.cnt[texture ? kNextTexture : target ? kNextTarget : none ? kNextNone : kNextExit]++;
	if (rec.cleared) {
		s.cnt[kNextCleared]++;
	}
	if (rec.buf_reads > 0) {
		s.cnt[kNextBufReads]++;
	}
	if (key != nullptr) {
		(texture ? key->texture : target ? key->target : none ? key->none : key->exit)++;
		key->cleared += rec.cleared ? 1 : 0;
		key->bufreads += rec.buf_reads > 0 ? 1 : 0;
		key->dirty = true;
	}
	if (rec.printed) {
		const auto end_frame = rec.bound ? rec.bind_frame : frame;
		EmitLine(fmt::format("DiagF5Id: fce_next base=0x{:016x} kind={} dframes={} meta={} cleared={} buf_reads={} "
		                     "merged={}",
		                     rec.base, kind, end_frame - rec.open_frame,
		                     rec.bound ? MetaKindAt(rec.meta_kind, rec.meta_addr) : std::string {"-"},
		                     rec.cleared ? 1 : 0,
		                     rec.surface == 0 ? std::string {"na"} : std::to_string(rec.buf_reads), rec.merged));
	}
}

} // namespace
''')

# The DiagF5 F16k functions, at the end of namespace DiagF5.
t = sub_once(t, r'''void NoteDmaRefusal(uint8_t refusal, uint32_t value) {
	if (refusal == RefusalDcc) {
		Add(DccFillClassOf(value) == FillClass::Clear ? Counter::MetaDmaUntracked : Counter::MetaDmaNoClear);
	} else if (refusal == RefusalCmask) {
		Add(value == 0 ? Counter::MetaDmaUntracked : Counter::MetaDmaNoClear);
	}
}

} // namespace DiagF5
''', r'''void NoteDmaRefusal(uint8_t refusal, uint32_t value) {
	if (refusal == RefusalDcc) {
		Add(DccFillClassOf(value) == FillClass::Clear ? Counter::MetaDmaUntracked : Counter::MetaDmaNoClear);
	} else if (refusal == RefusalCmask) {
		Add(value == 0 ? Counter::MetaDmaUntracked : Counter::MetaDmaNoClear);
	}
}

// ---- Track F, F16k (HPP-583, ROADMAP s122 item 492(v)): KYTY_FIX_F5CMU.
bool FixCmuOn() {
	static const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_F5CMU"));
	return on;
}

bool LogFixCmuMode() {
	static std::atomic<bool> logged {false};
	if (!FixCmuOn() || logged.exchange(true, std::memory_order_relaxed)) {
		return false;
	}
	EmitLine("FixF5Cmu: mode=1");
	return true;
}

bool ExactRingOn() {
	static const bool on = FixCmuOn() || DiagF5Id::On();
	return on;
}

const char* CmuFixName(CmuFix fix) {
	switch (fix) {
		case CmuFix::Off: return "off";
		case CmuFix::Fresh: return "fresh";
		case CmuFix::ExactStale: return "exact_stale";
		case CmuFix::Kept: return "kept";
		case CmuFix::KeptApplied: return "kept_applied";
		case CmuFix::Fallback: return "fallback";
	}
	return "off";
}

const char* CmuWhyName(CmuWhy why) {
	switch (why) {
		case CmuWhy::None: return "none";
		case CmuWhy::Value: return "value";
		case CmuWhy::Mask: return "mask";
		case CmuWhy::Range: return "range";
		case CmuWhy::Partial: return "partial";
		case CmuWhy::Decode: return "decode";
		case CmuWhy::Layers: return "layers";
		case CmuWhy::NoLayer: return "nolayer";
	}
	return "none";
}

void NoteDccStaleProbe(const StaleProbe& probe) {
	if (!probe.bucket_stale || probe.exact_stale) {
		return;
	}
	Add(probe.fallback ? Counter::DccStaleFallback : Counter::DccStaleBucketOnly);
}

namespace {
std::atomic<uint32_t> g_present {0};
std::atomic<uint64_t> g_cmu_events {0};
} // namespace

void NotePresent(uint32_t present) {
	g_present.store(present, std::memory_order_relaxed);
}

uint32_t Present() {
	return g_present.load(std::memory_order_relaxed);
}

std::string FormatCmuEvent(uint64_t n, const CmuEventLine& line) {
	auto text = fmt::format("DiagF5Ev: cmask_fce n={} present={} gpu={} image=0x{:016x} cmask=0x{:016x} extent={}x{} "
	                        "applied={} fix={}",
	                        n, line.present, line.gpu, line.image, line.cmask, line.width, line.height,
	                        line.applied ? 1 : 0, CmuFixName(line.event.fix));
	if (line.event.why != CmuWhy::None) {
		text += fmt::format(" why={}", CmuWhyName(line.event.why));
	}
	return text;
}

bool NoteCmuEvent(const CmuEventLine& line) {
	const auto n = g_cmu_events.fetch_add(1, std::memory_order_relaxed) + 1;
	if (n > 64) {
		return false;
	}
	EmitLine(FormatCmuEvent(n, line));
	return true;
}

std::vector<std::string> RecentLines() {
	std::scoped_lock lock {g_recent_mutex};
	return {g_recent.begin(), g_recent.end()};
}

void ClearRecentLines() {
	std::scoped_lock lock {g_recent_mutex};
	g_recent.clear();
}

} // namespace DiagF5

// ---- Track F, F16k (HPP-583, ROADMAP s122 item 492(g)): KYTY_DIAG_F5ID - see diagF5.h.
namespace DiagF5Id {

bool Knob() {
	static const bool on = Common::EnvValueOn(std::getenv("KYTY_DIAG_F5ID"));
	return on;
}

bool On() {
	static const bool on = Knob() && DiagF5::On();
	return on;
}

bool LogMode() {
	static std::atomic<bool> logged {false};
	if (!Knob() || logged.exchange(true, std::memory_order_relaxed)) {
		return false;
	}
	EmitLine(On() ? "DiagF5Id: mode=1" : "DiagF5Id: mode=0 needs=KYTY_DIAG_F5");
	return true;
}

const char* MetaTypeName(MetaType type) {
	switch (type) {
		case MetaType::Absent: return "absent";
		case MetaType::PendingDcc: return "PendingDcc";
		case MetaType::CMask: return "CMask";
		case MetaType::FMask: return "FMask";
		case MetaType::HTile: return "HTile";
		case MetaType::Dcc: return "Dcc";
	}
	return "absent";
}

DccMiss ScanReason(uint32_t candidates, bool dcc_other, uint64_t dcc_other_address, int other_kind) {
	if (candidates > 1) {
		return {Miss::R4, candidates};
	}
	if (dcc_other) {
		return {Miss::R2, dcc_other_address};
	}
	if (other_kind >= 0) {
		return {Miss::R3, static_cast<uint64_t>(other_kind)};
	}
	return {Miss::R1, 0};
}

void NoteFce(const FceEvent& e) {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	s.cnt[kFce]++;
	s.cnt[kR0 + static_cast<uint32_t>(e.miss.why)]++;
	int key = -1;
	for (size_t i = 0; i < s.fce_keys.size(); i++) {
		const auto& k = s.fce_keys[i];
		if (k.base == e.base && k.dcc == e.dcc && k.why == e.miss.why) {
			key = static_cast<int>(i);
			break;
		}
	}
	if (key < 0) {
		if (s.fce_keys.size() < kKeysPerSite) {
			s.fce_keys.push_back({.base = e.base, .dcc = e.dcc, .why = e.miss.why});
			key = static_cast<int>(s.fce_keys.size() - 1);
			s.cnt[kKeysFce]++;
		} else {
			s.cnt[kOverflowFce]++;
		}
	}
	bool printed = false;
	if (key >= 0) {
		auto& k = s.fce_keys[static_cast<size_t>(key)];
		printed = k.n < kLinesPerKey;
		k.n++;
		k.dirty = true;
		if (printed) {
			EmitLine(fmt::format(
			    "DiagF5Id: fce frame={} present={} slot={} base=0x{:016x} dcc=0x{:016x} fmt={} nfmt={} extent={}x{} "
			    "pitch={} size=0x{:x} dcc_size=0x{:x} clear={:08x}/{:08x} dcc_en={} key_en={} reason={} info=0x{:x} "
			    "entry={} clear_mask=0x{:08x} fill=0x{:08x} fill_size=0x{:x} fill_seq={} after={} after_mask=0x{:08x} "
			    "wr_after={} cpu_mod={} key_n={}",
			    e.frame, e.present, e.slot, e.base, e.dcc, e.fmt, e.nfmt, e.width, e.height, e.pitch, e.surface_size,
			    e.dcc_size, e.clear0, e.clear1, e.dcc_en ? 1 : 0, e.key_en ? 1 : 0, MissName(e.miss.why), e.miss.info,
			    MetaTypeName(e.before.type), e.before.clear_mask, e.before.fill_value, e.before.fill_size,
			    e.before.fill_seq, MetaTypeName(e.after.type), e.after.clear_mask, WrAfterName(e.wr_after),
			    e.cpu_mod < 0 ? std::string {"na"} : std::to_string(e.cpu_mod), k.n));
		}
	}
	for (auto& rec: s.open) {
		if (rec.base == e.base && !rec.bound) {
			rec.merged++;
			s.cnt[kNextMerged]++;
			return;
		}
	}
	if (s.open.size() >= kOpenMax) {
		s.cnt[kNextOverflow]++;
		return;
	}
	s.open.push_back({.base = e.base, .surface = e.surface_size, .key = key, .printed = printed,
	                  .open_frame = e.frame});
	s.open_count.store(static_cast<uint32_t>(s.open.size()), std::memory_order_relaxed);
}

void NoteBind(uint64_t image_address, BindKind kind, ImageMetadataKind meta_kind, uint64_t meta_address,
              uint32_t frame) {
	auto& s = IdS();
	if (s.open_count.load(std::memory_order_relaxed) == 0) {
		return;
	}
	std::scoped_lock lock {s.mutex};
	for (auto& rec: s.open) {
		if (rec.base == image_address && !rec.bound) {
			rec.bound      = true;
			rec.kind       = kind;
			rec.bind_frame = frame;
			rec.meta_kind  = meta_kind;
			rec.meta_addr  = meta_address;
		}
	}
}

void NoteBufferAccess(uint64_t address, uint64_t size) {
	auto& s = IdS();
	if (s.open_count.load(std::memory_order_relaxed) == 0) {
		return;
	}
	std::scoped_lock lock {s.mutex};
	for (auto& rec: s.open) {
		if (!rec.bound && rec.surface != 0 && address < rec.base + rec.surface && rec.base < address + size) {
			rec.buf_reads++;
		}
	}
}

void Emit(CsDispatch& d, const DiagF5::CsRefusals& refusals) {
	if (d.emitted || !d.classed) {
		return;
	}
	d.emitted = true;
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	for (uint32_t i = 0; i < refusals.count && i < DiagF5::CsRefusals::Max; i++) {
		const auto addr = refusals.addresses[i];
		const auto cls  = d.outcome != CsClass::Exec ? d.outcome
		                  : d.tracked == 0           ? CsClass::Exec
		                  : addr == d.tracked        ? CsClass::Tracked
		                                             : CsClass::TrackedOther;
		const auto& before = d.before[i];
		const auto  sub    = cls == CsClass::Exec ? d.sub : CsSub::None;
		const bool  vclear = sub == CsSub::FillShape &&
		                    (before.type == MetaType::CMask
		                         ? d.value == 0
		                         : DiagF5::DccFillClassOf(d.value) == DiagF5::FillClass::Clear);
		s.cnt[kCs]++;
		switch (cls) {
			case CsClass::ImgClear: s.cnt[kImgClear]++; break;
			case CsClass::MetaClear: s.cnt[kMetaClear]++; break;
			case CsClass::Tracked: s.cnt[kTracked]++; break;
			case CsClass::TrackedOther: s.cnt[kTrackedOther]++; break;
			case CsClass::Exec:
				s.cnt[sub == CsSub::FillShape ? (vclear ? kExecFillClear : kExecFillOther) : kExecNoFill]++;
				break;
		}
		const bool ran     = cls == CsClass::Exec || cls == CsClass::Tracked || cls == CsClass::TrackedOther;
		std::string changed = "-";
		if (ran) {
			if (d.has_after) {
				const bool c = !SameSnap(before, d.after[i]);
				changed      = c ? "1" : "0";
				if (c) {
					s.cnt[kChanged]++;
				}
			} else {
				changed = "na";
				s.cnt[kChangedNa]++;
			}
		}
		int key = -1;
		for (size_t k = 0; k < s.cs_keys.size(); k++) {
			const auto& ck = s.cs_keys[k];
			if (ck.shader == d.shader && ck.addr == addr && ck.cls == cls) {
				key = static_cast<int>(k);
				break;
			}
		}
		if (key < 0) {
			if (s.cs_keys.size() < kKeysPerSite) {
				s.cs_keys.push_back({.shader = d.shader, .addr = addr, .cls = cls});
				key = static_cast<int>(s.cs_keys.size() - 1);
				s.cnt[kKeysCs]++;
			} else {
				s.cnt[kOverflowCs]++;
			}
		}
		// Marks (item 492(g)(3), RC8): a clear mask left on the entry by a dispatch that ran as it is (exec, tracked_other;
		// PendingDcc, Dcc, CMask) or by an image clear (img_clear; PendingDcc).
		const bool known = before.type == MetaType::PendingDcc || before.type == MetaType::Dcc ||
		                   before.type == MetaType::CMask;
		const bool mark  = before.clear_mask != 0 &&
		                  (((cls == CsClass::Exec || cls == CsClass::TrackedOther) && known) ||
		                   (cls == CsClass::ImgClear && before.type == MetaType::PendingDcc));
		if (mark) {
			if (s.marks.size() < kMarksMax || s.marks.contains(addr)) {
				s.marks[addr] = {.shader = d.shader, .cls = cls, .frame = d.frame, .key = key};
				s.cnt[kMarksSet]++;
			} else {
				s.cnt[kMarksOverflow]++;
			}
			s.mark_count.store(static_cast<uint32_t>(s.marks.size()), std::memory_order_relaxed);
		}
		if (key >= 0) {
			auto& ck = s.cs_keys[static_cast<size_t>(key)];
			const bool print = ck.n < kLinesPerKey;
			ck.n++;
			ck.dirty = true;
			if (print) {
				EmitLine(fmt::format(
				    "DiagF5Id: cs frame={} present={} shader=0x{:016x} addr=0x{:016x} size=0x{:x} read={} class={} sub={} "
				    "value=0x{:08x} vclass={} entry={} clear_mask=0x{:08x} fill=0x{:08x} fill_size=0x{:x} changed={} "
				    "mark={} key_n={}",
				    d.frame, DiagF5::Present(), d.shader, addr, d.sizes[i], d.reads[i] ? 1 : 0, CsClassName(cls),
				    sub == CsSub::NoFill ? "nofill" : sub == CsSub::FillShape ? "fill_shape" : "-", d.value,
				    sub == CsSub::FillShape ? (vclear ? "clear" : "other") : "-", MetaTypeName(before.type),
				    before.clear_mask, before.fill_value, before.fill_size, changed, mark ? 1 : 0, ck.n));
			}
		}
	}
}

void NoteClearApplied(ApplySite site, uint64_t meta_address, uint64_t image_address, uint32_t frame) {
	auto& s = IdS();
	if (s.open_count.load(std::memory_order_relaxed) == 0 && s.mark_count.load(std::memory_order_relaxed) == 0) {
		return;
	}
	std::scoped_lock lock {s.mutex};
	if (const auto found = s.marks.find(meta_address); found != s.marks.end()) {
		const auto mark = found->second;
		s.marks.erase(found);
		s.mark_count.store(static_cast<uint32_t>(s.marks.size()), std::memory_order_relaxed);
		s.cnt[kStaleApply]++;
		if (mark.key >= 0) {
			s.cs_keys[static_cast<size_t>(mark.key)].stale_apply++;
			s.cs_keys[static_cast<size_t>(mark.key)].dirty = true;
		}
		if (s.stale_lines++ < kStaleLines) {
			EmitLine(fmt::format("DiagF5Id: stale_apply site={} addr=0x{:016x} image=0x{:016x} shader=0x{:016x} class={} "
			                     "dframes={}",
			                     ApplySiteName(site), meta_address, image_address, mark.shader, CsClassName(mark.cls),
			                     frame - mark.frame));
		}
	}
	if (site != ApplySite::CmaskRt) {
		for (auto& rec: s.open) {
			if (rec.base == image_address) {
				rec.cleared = true;
			}
		}
	}
}

void NoteFill(uint64_t address) {
	auto& s = IdS();
	if (s.mark_count.load(std::memory_order_relaxed) == 0) {
		return;
	}
	std::scoped_lock lock {s.mutex};
	if (s.marks.erase(address) != 0) {
		s.cnt[kMarksDropped]++;
		s.mark_count.store(static_cast<uint32_t>(s.marks.size()), std::memory_order_relaxed);
	}
}

void NoteFillSeq(uint64_t address, uint64_t seq) {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	s.fill_seq[address] = seq;
}

uint64_t FillSeq(uint64_t address) {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	const auto       found = s.fill_seq.find(address);
	return found == s.fill_seq.end() ? 0 : found->second;
}

bool Service(bool exit) {
	if (!On()) {
		return false;
	}
	return ServiceAt(GpuTimeProfiler::Frame(), exit);
}

bool ServiceAt(uint32_t frame, bool exit) {
	if (!On()) {
		return false;
	}
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	for (size_t i = 0; i < s.open.size();) {
		const auto& rec = s.open[i];
		if (rec.bound) {
			IdClose(s, i, BindKindName(rec.kind), frame);
		} else if (exit) {
			IdClose(s, i, "exit", frame);
		} else if (frame - rec.open_frame >= kNoneFrames) {
			IdClose(s, i, "none", frame);
		} else {
			i++;
		}
	}
	s.open_count.store(static_cast<uint32_t>(s.open.size()), std::memory_order_relaxed);
	// One pass: the counters of this module (under its mutex, written by the sites on this thread) and the DiagF5
	// counters of the identities (their sites run on this thread too; no window is open at the loop top).
	const auto cnt              = s.cnt;
	const auto dcc_fce_no_image = DiagF5::Get(DiagF5::Counter::DccFceNoImage);
	const auto cs_untracked     = DiagF5::Get(DiagF5::Counter::MetaCsUntracked);
	const auto cs_tracked       = DiagF5::Get(DiagF5::Counter::MetaCsTracked);
	uint64_t   total            = 0;
	for (const auto value: cnt) {
		total += value;
	}
	if (!exit && (total == s.last_total || (s.printed && frame - s.last_frame < kSumFrames))) {
		return false;
	}
	uint64_t reasons = 0;
	for (uint32_t r = kR1; r <= kR7; r++) {
		reasons += cnt[r];
	}
	const bool id_fce = reasons == dcc_fce_no_image && cnt[kFce] == reasons && cnt[kR0] == 0;
	const bool id_cs  = cnt[kImgClear] + cnt[kMetaClear] + cnt[kTrackedOther] + cnt[kExecNoFill] + cnt[kExecFillClear] +
	                           cnt[kExecFillOther] ==
	                       cs_untracked &&
	                   cnt[kTracked] == cs_tracked;
	std::string line = fmt::format("DiagF5Id: sum frame={} exit={}", frame, exit ? 1 : 0);
	for (uint32_t i = 0; i < kIdCount; i++) {
		line += fmt::format(" {}={}", IdNames[i], cnt[i]);
	}
	line += fmt::format(" marks={} open={} dcc_fce_no_image={} meta_cs_untracked={} meta_cs_tracked={} id_fce={} id_cs={}",
	                    s.marks.size(), s.open.size(), dcc_fce_no_image, cs_untracked, cs_tracked,
	                    id_fce ? "ok" : "bad", id_cs ? "ok" : "bad");
	EmitLine(line);
	for (auto& k: s.fce_keys) {
		if (k.dirty) {
			k.dirty = false;
			EmitLine(fmt::format("DiagF5Id: key site=fce base=0x{:016x} dcc=0x{:016x} reason={} n={} texture={} target={} "
			                     "none={} exit={} cleared={} bufreads={}",
			                     k.base, k.dcc, MissName(k.why), k.n, k.texture, k.target, k.none, k.exit, k.cleared,
			                     k.bufreads));
		}
	}
	for (auto& k: s.cs_keys) {
		if (k.dirty) {
			k.dirty = false;
			EmitLine(fmt::format("DiagF5Id: key site=cs shader=0x{:016x} addr=0x{:016x} class={} n={} stale_apply={}",
			                     k.shader, k.addr, CsClassName(k.cls), k.n, k.stale_apply));
		}
	}
	s.printed    = true;
	s.last_frame = frame;
	s.last_total = total;
	return true;
}

uint64_t Count(const char* name) {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	for (uint32_t i = 0; i < kIdCount; i++) {
		if (std::string_view {IdNames[i]} == name) {
			return s.cnt[i];
		}
	}
	return UINT64_MAX;
}

uint32_t OpenRecords() {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	return static_cast<uint32_t>(s.open.size());
}

uint32_t Marks() {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	return static_cast<uint32_t>(s.marks.size());
}

void ResetForTest() {
	auto&            s = IdS();
	std::scoped_lock lock {s.mutex};
	s.cnt = {};
	s.fce_keys.clear();
	s.cs_keys.clear();
	s.open.clear();
	s.marks.clear();
	s.fill_seq.clear();
	s.stale_lines = 0;
	s.printed     = false;
	s.last_frame  = 0;
	s.last_total  = 0;
	s.open_count.store(0, std::memory_order_relaxed);
	s.mark_count.store(0, std::memory_order_relaxed);
}

} // namespace DiagF5Id
''')

open(PATH, "wb").write(t.encode("utf-8"))
print("patched", PATH)
