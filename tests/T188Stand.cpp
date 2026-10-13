// Track M, M9d (HPP-869, ROADMAP s122 item 785(d)): stand without the game and without the GPU of KYTY_DIAG_T188 stage 1
// and of DiagT109 (src/libs/diagT188.cpp; the emulator sources of this build are linked, not copied). Every case resets
// the counters, runs the Note functions on synthetic images and compares EVERY counter of T188Stat (and the class
// counters it names) with exact expected values - a counter the case does not name must stay 0.
// Separate CMake target t188_stand (EXCLUDE_FROM_ALL, no add_test); the driver C:/kyty/m657/m9d/run_stand_m9d.py runs it.
//
// Usage: t188_stand <log file>. Lines:
//   T188Stand: case=<name> field=<f> got=<g> want=<w> match=0      (only mismatches)
//   T188Stand: case=<name> match=<0|1>
//   T188Stand: total=<n> match=<m> END
// Exit 0 unless the arguments are bad (2).

#define SDL_MAIN_HANDLED
#include "common/common.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "libs/diagT188.h"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>
#include <vulkan/vulkan_core.h>

namespace T = Libs::DiagT188;
namespace T109 = Libs::DiagT109;

namespace {

int g_total = 0;
int g_match = 0;

constexpr uint64_t A = 0x10000000ull;

// Three levels: L0 [0, 0x4000), L1 [0x4000, 0x5000), L2 [0x5000, 0x5400).
const T::Mip kMips[3] = {{0, 0x4000}, {0x4000, 0x1000}, {0x5000, 0x400}};

T::Geometry Geo(uint64_t source_size = 0x5400, bool volume = false, uint32_t layers = 1) {
	T::Geometry g;
	g.address     = A;
	g.data_size   = 0x5400;
	g.source_size = source_size;
	g.levels      = 3;
	g.layers      = layers;
	g.volume      = volume;
	g.mips        = kMips;
	return g;
}

T::ClassFields Fields(uint32_t usage = 1) {
	T::ClassFields f;
	f.fmt     = VK_FORMAT_R8G8B8A8_UNORM;
	f.tile    = 2;
	f.w       = 64;
	f.h       = 64;
	f.levels  = 3;
	f.layers  = 1;
	f.samples = 1;
	f.usage   = usage;
	return f;
}

const char* kNames[] = {
    "part", "part_st", "part_fill", "part_copy", "part_unk", "part_off", "part_synced", "part_dlmem", "reopen", "ep_new",
    "ep_prop", "prop_merge", "w_mipal", "w_inmip", "w_other", "w_bytes", "img_bytes", "img_bytes_unsync",
    "img_full_unsync", "in_pass", "in_pass_unsync", "cl_smp", "cl_rt", "cl_rtclr", "cl_dt", "cl_sto", "cl_clrop",
    "cl_oth", "cl_vo", "cl_cover", "cl_cmp", "cl_msaa", "cl_free", "cl_commit", "cl_copydst", "cl_skip", "cl_none",
    "open", "ep_pend", "pend_done", "pend_drop", "pend_free", "pend_open", "lost_bytes", "lost_pend_bytes", "w_ovf",
    "sync_full", "sync_part", "dl_mem", "ep_bad", "lock_bad", "tint_ep", "tint_mips", "tint_bytes", "tint_part_mips",
    "tint_skip_fmt", "tint_skip_vol", "tint_skip_cls", "tint_skip_cpu", "tint_skip_ovf", "tint_bad", "tint_rb_req",
    "tint_rb0_ok", "tint_rb0_bad", "tint_rb0_none", "tint_rb0_nofmt", "tint_rb1_ok", "tint_rb1_over", "tint_rb1_bad",
    "tint_rb1_none"};
static_assert(std::size(kNames) == static_cast<size_t>(T::C::Count));

using Want = std::map<std::string, uint64_t>;

// Compares every T188Stat counter (absent - 0) and the named extra values ("x:<name>").
void Check(const char* name, const Want& want, const Want& extra_got = {}) {
	bool ok = true;
	for (uint32_t i = 0; i < static_cast<uint32_t>(T::C::Count); i++) {
		const auto     found = want.find(kNames[i]);
		const uint64_t w     = found == want.end() ? 0 : found->second;
		const uint64_t g     = T::Read(static_cast<T::C>(i));
		if (g != w) {
			ok = false;
			std::printf("T188Stand: case=%s field=%s got=%llu want=%llu match=0\n", name, kNames[i],
			            static_cast<unsigned long long>(g), static_cast<unsigned long long>(w));
		}
	}
	for (const auto& [k, w]: want) {
		if (k.rfind("x:", 0) != 0) {
			bool known = false;
			for (const char* n: kNames) {
				known = known || k == n;
			}
			if (!known) {
				ok = false;
				std::printf("T188Stand: case=%s field=%s unknown match=0\n", name, k.c_str());
			}
			continue;
		}
		const auto     found = extra_got.find(k);
		const uint64_t g     = found == extra_got.end() ? UINT64_MAX : found->second;
		if (g != w) {
			ok = false;
			std::printf("T188Stand: case=%s field=%s got=%llu want=%llu match=0\n", name, k.c_str(),
			            static_cast<unsigned long long>(g), static_cast<unsigned long long>(w));
		}
	}
	g_total++;
	g_match += ok ? 1 : 0;
	std::printf("T188Stand: case=%s match=%d\n", name, ok ? 1 : 0);
}

void Reset(int mode) {
	T::ResetForStand();
	T109::ResetForStand();
	T::g_mode = mode;
}

uint64_t Cls(uint64_t key, T::CC cc) {
	return T::ReadClass(key, cc);
}

// An image with an open episode whose union is [A + b, A + e).
void Open(T::ImageState& s, const T::Geometry& g, uint64_t b, uint64_t e, T::Writer writer = T::Writer::St) {
	(void)T::NoteInvalidate(s, g, Fields(), true, writer, A + b, e - b, false, true);
}

void CasesS2() {
	{ // m1: coverage of SourceRange(), not of info.data.size
		Reset(1);
		T::ImageState s;
		const auto    ev = T::NoteInvalidate(s, Geo(0x5000), Fields(), true, T::Writer::St, A, 0x5000, false, true);
		Check("cover_src", {{"x:ev", static_cast<uint64_t>(T::Ev::None)}}, {{"x:ev", static_cast<uint64_t>(ev)}});
	}
	{ // a write without IsGpuModified and no episode: nothing
		Reset(1);
		T::ImageState s;
		const auto    ev = T::NoteInvalidate(s, Geo(), Fields(), false, T::Writer::St, A + 0x100, 0x100, false, true);
		Check("not_gpu", {{"x:ev", static_cast<uint64_t>(T::Ev::None)}}, {{"x:ev", static_cast<uint64_t>(ev)}});
	}
	T::ImageState s;
	{ // a new episode: write of level 1 exactly (not at the base), by a storage write, inside a pass
		Reset(1);
		const auto ev = T::NoteInvalidate(s, Geo(), Fields(), true, T::Writer::St, A + 0x4000, 0x1000, true, true);
		const auto key = T::ClassKey(Fields());
		Check("part_new",
		      {{"part", 1}, {"part_st", 1}, {"part_off", 1}, {"w_mipal", 1}, {"w_bytes", 0x1000}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"in_pass", 1}, {"in_pass_unsync", 1},
		       {"ep_new", 1}, {"open", 1}, {"x:ev", static_cast<uint64_t>(T::Ev::New)}, {"x:cls_ev", 1}, {"x:cls_ev_st", 1},
		       {"x:cls_ev_off", 1}, {"x:cls_ep_new", 1}, {"x:cls_img_bytes", 0x5400}, {"x:open_flag", 1},
		       {"x:writer", 1}},
		      {{"x:ev", static_cast<uint64_t>(ev)}, {"x:cls_ev", Cls(key, T::CC::ev)},
		       {"x:cls_ev_st", Cls(key, T::CC::ev_st)}, {"x:cls_ev_off", Cls(key, T::CC::ev_off)},
		       {"x:cls_ep_new", Cls(key, T::CC::ep_new)}, {"x:cls_img_bytes", Cls(key, T::CC::img_bytes)},
		       {"x:open_flag", s.open ? 1u : 0u}, {"x:writer", s.writer}});
	}
	{ // m2: a second partial write of the open episode is a reopen (fill, inside level 0, at the base)
		const auto ev = T::NoteInvalidate(s, Geo(), Fields(), true, T::Writer::Fill, A, 0x100, false, true);
		Check("reopen",
		      {{"part", 2}, {"part_st", 1}, {"part_fill", 1}, {"part_off", 1}, {"w_mipal", 1}, {"w_inmip", 1},
		       {"w_bytes", 0x1100}, {"img_bytes", 0xa800}, {"img_bytes_unsync", 0xa800}, {"img_full_unsync", 0xa800},
		       {"in_pass", 1}, {"in_pass_unsync", 1}, {"ep_new", 1}, {"reopen", 1}, {"open", 1},
		       {"x:ev", static_cast<uint64_t>(T::Ev::Reopen)}, {"x:spans", 2}},
		      {{"x:ev", static_cast<uint64_t>(ev)}, {"x:spans", s.n}});
	}
	{ // decision 1: an open episode, a partial write without IsGpuModified joins the union (no counter)
		const auto ev = T::NoteInvalidate(s, Geo(), Fields(), false, T::Writer::Copy, A + 0x100, 0x100, false, true);
		Check("join",
		      {{"part", 2}, {"part_st", 1}, {"part_fill", 1}, {"part_off", 1}, {"w_mipal", 1}, {"w_inmip", 1},
		       {"w_bytes", 0x1100}, {"img_bytes", 0xa800}, {"img_bytes_unsync", 0xa800}, {"img_full_unsync", 0xa800},
		       {"in_pass", 1}, {"in_pass_unsync", 1}, {"ep_new", 1}, {"reopen", 1}, {"open", 1},
		       {"x:ev", static_cast<uint64_t>(T::Ev::Join)}, {"x:spans", 2}, {"x:span0_e", A + 0x200}},
		      {{"x:ev", static_cast<uint64_t>(ev)}, {"x:spans", s.n}, {"x:span0_e", s.w[0].e}});
	}
	{ // a covering write closes the episode (cl_cover)
		const auto ev = T::NoteInvalidate(s, Geo(), Fields(), false, T::Writer::Copy, A, 0x5400, false, true);
		Check("close_cover",
		      {{"part", 2}, {"part_st", 1}, {"part_fill", 1}, {"part_off", 1}, {"w_mipal", 1}, {"w_inmip", 1},
		       {"w_bytes", 0x1100}, {"img_bytes", 0xa800}, {"img_bytes_unsync", 0xa800}, {"img_full_unsync", 0xa800},
		       {"in_pass", 1}, {"in_pass_unsync", 1}, {"ep_new", 1}, {"reopen", 1}, {"cl_cover", 1},
		       {"x:ev", static_cast<uint64_t>(T::Ev::Cover)}, {"x:open_flag", 0}},
		      {{"x:ev", static_cast<uint64_t>(ev)}, {"x:open_flag", s.open ? 1u : 0u}});
	}
	{ // a full synchronization: the next partial write is part_synced (no episode, no unsync bytes)
		Reset(1);
		T::ImageState t;
		T::NoteGpuWrite(t);
		T::NoteSync(t, true, true);
		const auto ev  = T::NoteInvalidate(t, Geo(), Fields(), true, T::Writer::St, A, 0x100, false, true);
		const auto key = T::ClassKey(Fields());
		Check("synced",
		      {{"part", 1}, {"part_st", 1}, {"w_inmip", 1}, {"w_bytes", 0x100}, {"img_bytes", 0x5400}, {"part_synced", 1},
		       {"sync_full", 1}, {"x:ev", static_cast<uint64_t>(T::Ev::Synced)}, {"x:cls_synced", 1}},
		      {{"x:ev", static_cast<uint64_t>(ev)}, {"x:cls_synced", Cls(key, T::CC::ev_synced)}});
	}
	{ // m7: a write after the synchronization moves wseq - the event opens an episode
		Reset(1);
		T::ImageState t;
		T::NoteGpuWrite(t);
		T::NoteSync(t, true, true);
		T::NoteGpuWrite(t);
		const auto ev = T::NoteInvalidate(t, Geo(), Fields(), true, T::Writer::St, A, 0x100, false, true);
		Check("sync_then_write",
		      {{"part", 1}, {"part_st", 1}, {"w_inmip", 1}, {"w_bytes", 0x100}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"open", 1}, {"sync_full", 1},
		       {"x:ev", static_cast<uint64_t>(T::Ev::New)}},
		      {{"x:ev", static_cast<uint64_t>(ev)}});
	}
	{ // m6: a partial synchronization stamps nothing
		Reset(1);
		T::ImageState t;
		T::NoteGpuWrite(t);
		T::NoteSync(t, false, true);
		const auto ev = T::NoteInvalidate(t, Geo(), Fields(), true, T::Writer::St, A, 0x100, false, true);
		Check("sync_part",
		      {{"part", 1}, {"part_st", 1}, {"w_inmip", 1}, {"w_bytes", 0x100}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"open", 1}, {"sync_part", 1},
		       {"x:ev", static_cast<uint64_t>(T::Ev::New)}},
		      {{"x:ev", static_cast<uint64_t>(ev)}});
	}
	{ // a download to guest memory: part_dlmem
		Reset(1);
		T::ImageState t;
		T::NoteGpuWrite(t);
		T::NoteDownload(t, true);
		const auto ev = T::NoteInvalidate(t, Geo(), Fields(), true, T::Writer::Copy, A + 0x10, 0x100, true, true);
		Check("dlmem",
		      {{"part", 1}, {"part_copy", 1}, {"part_off", 1}, {"w_inmip", 1}, {"w_bytes", 0x100}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"in_pass", 1}, {"in_pass_unsync", 1},
		       {"part_dlmem", 1}, {"dl_mem", 1}, {"x:ev", static_cast<uint64_t>(T::Ev::Dlmem)}},
		      {{"x:ev", static_cast<uint64_t>(ev)}});
	}
	{ // writer Unk (invariant 0 in the game) and a write across two levels (w_other)
		Reset(1);
		T::ImageState t;
		(void)T::NoteInvalidate(t, Geo(), Fields(), true, T::Writer::Unk, A + 0x3000, 0x1800, false, true);
		Check("unk_other",
		      {{"part", 1}, {"part_unk", 1}, {"part_off", 1}, {"w_other", 1}, {"w_bytes", 0x1800}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"open", 1}});
	}
	{ // m11: a volume write aligned to a level is w_other
		Reset(1);
		T::ImageState t;
		(void)T::NoteInvalidate(t, Geo(0x5400, true), Fields(), true, T::Writer::St, A + 0x4000, 0x1000, false, true);
		Check("vol_other",
		      {{"part", 1}, {"part_st", 1}, {"part_off", 1}, {"w_other", 1}, {"w_bytes", 0x1000}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"open", 1}});
	}
	{ // m10: a site without m_lock does no work and counts lock_bad - every site function
		Reset(2);
		T::ImageState t;
		const auto    g = Geo();
		(void)T::NoteInvalidate(t, g, Fields(), true, T::Writer::St, A, 0x100, false, false);
		(void)T::CloseUpload(t, g, Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, false);
		(void)T::PendDone(t, g, 0, 3, false);
		T::PendDrop(t, false);
		T::CloseNoUpload(t, T::Close::Commit, false);
		T::NoteFree(t, false);
		T::Propagate(t, t, g, Fields(), false);
		T::NoteSync(t, true, false);
		T::NoteDownload(t, false);
		Check("lock_bad", {{"lock_bad", 9}, {"x:sseq", UINT64_MAX}, {"x:dseq", UINT64_MAX}},
		      {{"x:sseq", t.sseq.load()}, {"x:dseq", t.dseq.load()}});
	}
	{ // w_ovf: the 9th disjoint interval does not enter the union
		Reset(1);
		T::ImageState t;
		for (uint64_t i = 0; i < 9; i++) {
			(void)T::NoteInvalidate(t, Geo(), Fields(), i == 0, T::Writer::St, A + i * 0x200, 0x10, false, true);
		}
		Check("ovf",
		      {{"part", 1}, {"part_st", 1}, {"w_inmip", 1}, {"w_bytes", 0x10}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"open", 1}, {"w_ovf", 1},
		       {"x:spans", 8}},
		      {{"x:spans", t.n}});
		T::g_mode = 2;
		(void)T::CloseUpload(t, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, true);
		Check("ovf_skip",
		      {{"part", 1}, {"part_st", 1}, {"w_inmip", 1}, {"w_bytes", 0x10}, {"img_bytes", 0x5400},
		       {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"w_ovf", 1}, {"cl_smp", 1},
		       {"lost_bytes", 0x5400 - 8 * 0x10}, {"tint_skip_ovf", 1}});
	}
}

// Opening counters of Open(s, Geo(), b, e) with a storage write not at the base and not covering a level: the fields
// every S3 case below starts from.
Want Opened(uint64_t b, uint64_t e, const char* shape) {
	Want w = {{"part", 1}, {"part_st", 1}, {shape, 1}, {"w_bytes", e - b}, {"img_bytes", 0x5400},
	          {"img_bytes_unsync", 0x5400}, {"img_full_unsync", 0x5400}, {"ep_new", 1}, {"open", 1}};
	if (b != 0) {
		w["part_off"] = 1;
	}
	return w;
}

void CasesS3() {
	const auto key = T::ClassKey(Fields());
	{ // mode 1: closure by a sampled upload; lost = L0 + L2 (the union covers L1 exactly)
		Reset(1);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		const auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, true);
		auto       w    = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w["cl_smp"]          = 1;
		w["lost_bytes"]      = 0x4400;
		w["x:mask"]          = 0;
		w["x:cls_lost"]      = 0x4400;
		w["x:cls_cl_smp"]    = 1;
		Check("s3_mode1", w,
		      {{"x:mask", plan.mask}, {"x:cls_lost", Cls(key, T::CC::lost_bytes)}, {"x:cls_cl_smp", Cls(key, T::CC::cl_smp)}});
	}
	{ // mode 2: L0 and L2 are lost without an intersection - tinted; L1 covered - not
		Reset(2);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		const auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::Rt, 0, 3, 0, 0, true, false, true);
		auto       w    = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w["cl_rt"]       = 1;
		w["lost_bytes"]  = 0x4400;
		w["tint_ep"]     = 1;
		w["tint_mips"]   = 2;
		w["tint_bytes"]  = 0x4400;
		w["tint_rb_req"] = 2;
		w["x:mask"]      = 0b101;
		w["x:rb_mask"]   = 0b101;
		w["x:cls_tint_ep"] = 1;
		w["x:cls_tint_bytes"] = 0x4400;
		Check("s3_mode2", w,
		      {{"x:mask", plan.mask}, {"x:rb_mask", plan.rb_mask}, {"x:cls_tint_ep", Cls(key, T::CC::tint_ep)},
		       {"x:cls_tint_bytes", Cls(key, T::CC::tint_bytes)}});
	}
	{ // m4: mode 2, the union covers half of L0 - L0 is part (not tinted), L1 and L2 tinted
		Reset(2);
		T::ImageState s;
		Open(s, Geo(), 0x2000, 0x4000);
		const auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::RtClr, 0, 3, 0, 0, true, false, true);
		auto       w    = Opened(0x2000, 0x4000, "w_inmip");
		w.erase("open");
		w["cl_rtclr"]       = 1;
		w["lost_bytes"]     = 0x2000 + 0x1000 + 0x400;
		w["tint_ep"]        = 1;
		w["tint_mips"]      = 2;
		w["tint_bytes"]     = 0x1400;
		w["tint_part_mips"] = 1;
		w["tint_rb_req"]    = 2;
		w["x:mask"]         = 0b110;
		Check("s3_part", w, {{"x:mask", plan.mask}});
	}
	{ // mode 3: every uploaded level of the episode, the covered one too
		Reset(3);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		const auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::Dt, 0, 3, 0, 0, true, false, true);
		auto       w    = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w["cl_dt"]       = 1;
		w["lost_bytes"]  = 0x4400;
		w["tint_ep"]     = 1;
		w["tint_mips"]   = 3;
		w["tint_bytes"]  = 0x5400;
		w["tint_rb_req"] = 3;
		w["x:mask"]      = 0b111;
		Check("s3_mode3", w, {{"x:mask", plan.mask}});
	}
	{ // K: the fifth level of a class is not read back (two episodes of 3 levels at mode 3: 3 + 1)
		Reset(3);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Dt, 0, 3, 0, 0, true, false, true);
		Open(s, Geo(), 0x4000, 0x5000);
		const auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::Dt, 0, 3, 0, 0, true, false, true);
		Want w = {{"part", 2}, {"part_st", 2}, {"part_off", 2}, {"w_mipal", 2}, {"w_bytes", 0x2000}, {"img_bytes", 0xa800},
		          {"img_bytes_unsync", 0xa800}, {"img_full_unsync", 0xa800}, {"ep_new", 2}, {"cl_dt", 2},
		          {"lost_bytes", 0x8800}, {"tint_ep", 2}, {"tint_mips", 6}, {"tint_bytes", 0xa800}, {"tint_rb_req", 4},
		          {"x:rb_mask", 0b001}};
		Check("rb_quota", w, {{"x:rb_mask", plan.rb_mask}});
	}
	{ // m5: deferred levels L0, L1 - S3 uploads L2 only (covered: nothing to tint), S3b tints L0 and L1
		Reset(2);
		T::ImageState s;
		Open(s, Geo(), 0x5000, 0x5400);
		const auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 2, 3, 0, 2, true, false, true);
		auto       w    = Opened(0x5000, 0x5400, "w_mipal");
		w.erase("open");
		w["cl_smp"]          = 1;
		w["lost_bytes"]      = 0;
		w["lost_pend_bytes"] = 0x5000;
		w["ep_pend"]         = 1;
		w["pend_open"]       = 1;
		w["x:mask"]          = 0;
		w["x:wait"]          = 1;
		Check("s3_deferred", w, {{"x:mask", plan.mask}, {"x:wait", s.wait ? 1u : 0u}});
		const auto pend = T::PendDone(s, Geo(), 0, 2, true);
		w.erase("pend_open");
		w["pend_done"]   = 1;
		w["tint_ep"]     = 1;
		w["tint_mips"]   = 2;
		w["tint_bytes"]  = 0x5000;
		w["tint_rb_req"] = 2;
		w["x:mask"]      = 0b011;
		w["x:wait"]      = 0;
		Check("s3b_done", w, {{"x:mask", pend.mask}, {"x:wait", s.wait ? 1u : 0u}});
	}
	{ // the deferred part dropped (S3c), freed (S5) and replaced by a new upload (decision 4)
		Reset(1);
		T::ImageState s;
		Open(s, Geo(), 0x5000, 0x5400);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 2, 3, 0, 2, true, false, true);
		T::PendDrop(s, true);
		Open(s, Geo(), 0x5000, 0x5400);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 2, 3, 0, 2, true, false, true);
		T::NoteFree(s, true);
		Open(s, Geo(), 0x5000, 0x5400);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 2, 3, 0, 2, true, false, true);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, true);
		Want w = {{"part", 3}, {"part_st", 3}, {"part_off", 3}, {"w_mipal", 3}, {"w_bytes", 0xc00}, {"img_bytes", 0xfc00},
		          {"img_bytes_unsync", 0xfc00}, {"img_full_unsync", 0xfc00}, {"ep_new", 3}, {"cl_smp", 3},
		          {"cl_none", 2}, {"lost_pend_bytes", 0xf000}, {"ep_pend", 3}, {"pend_drop", 2}, {"pend_free", 1}};
		Check("pend_outcomes", w);
	}
	{ // the skip reasons at mode 2 (cls is tested by the driver with KYTY_DIAG_T188_CLS): vol, fmt, cpu
		Reset(2);
		T::ImageState s;
		Open(s, Geo(0x5400, true), 0x4000, 0x5000);
		(void)T::CloseUpload(s, Geo(0x5400, true), Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, true);
		Open(s, Geo(), 0x4000, 0x5000);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, false, false, true);
		Open(s, Geo(), 0x4000, 0x5000);
		(void)T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, true, true, true);
		Want w = {{"part", 3}, {"part_st", 3}, {"part_off", 3}, {"w_mipal", 2}, {"w_other", 1}, {"w_bytes", 0x3000},
		          {"img_bytes", 0xfc00}, {"img_bytes_unsync", 0xfc00}, {"img_full_unsync", 0xfc00}, {"ep_new", 3},
		          {"cl_smp", 3}, {"lost_bytes", 3 * 0x4400}, {"tint_skip_vol", 1}, {"tint_skip_fmt", 1},
		          {"tint_skip_cpu", 1}, {"x:cls_skip", 3}};
		Check("skips", w, {{"x:cls_skip", Cls(key, T::CC::tint_skip)}});
	}
	{ // m12: the class is fixed at S2 - a closure after the usage changed adds to the class of the opening
		Reset(1);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		(void)T::CloseUpload(s, Geo(), Fields(4), T::Close::Rt, 0, 3, 0, 0, true, false, true);
		const auto other = T::ClassKey(Fields(4));
		auto       w     = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w["cl_rt"]           = 1;
		w["lost_bytes"]      = 0x4400;
		w["x:cls_open_rt"]   = 1;
		w["x:cls_open_lost"] = 0x4400;
		w["x:cls_other_rt"]  = 0;
		Check("class_at_s2", w,
		      {{"x:cls_open_rt", Cls(key, T::CC::cl_rt)}, {"x:cls_open_lost", Cls(key, T::CC::lost_bytes)},
		       {"x:cls_other_rt", Cls(other, T::CC::cl_rt)}});
	}
}

void CasesClosures() {
	struct Site {
		const char* name;
		T::Close    site;
		const char* field;
	};
	const Site sites[] = {{"close_cmp", T::Close::Cmp, "cl_cmp"},       {"close_msaa", T::Close::Msaa, "cl_msaa"},
	                      {"close_commit", T::Close::Commit, "cl_commit"}, {"close_copydst", T::Close::CopyDst, "cl_copydst"},
	                      {"close_skip", T::Close::Skip, "cl_skip"}};
	for (const auto& x: sites) { // m8 (S7) and the other closures without an upload; m3 - the second call is cl_none
		Reset(1);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		T::CloseNoUpload(s, x.site, true);
		T::CloseNoUpload(s, x.site, true);
		auto w = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w[x.field]   = 1;
		w["cl_none"] = 1;
		Check(x.name, w);
	}
	{ // S5 with an open episode, then on a closed one
		Reset(1);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		T::NoteFree(s, true);
		T::NoteFree(s, true);
		auto w = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w["cl_free"] = 1;
		w["cl_none"] = 1;
		Check("close_free", w);
	}
	{ // m9: S8 opens the destination's episode with the source's union; a second carry merges
		Reset(1);
		T::ImageState src;
		T::ImageState dst;
		Open(src, Geo(), 0x4000, 0x5000);
		T::Propagate(dst, src, Geo(), Fields(2), true);
		T::Propagate(dst, src, Geo(), Fields(2), true);
		auto w = Opened(0x4000, 0x5000, "w_mipal");
		w["open"]       = 2;
		w["ep_prop"]    = 1;
		w["prop_merge"] = 1;
		w["x:dst_open"] = 1;
		w["x:dst_span"] = A + 0x5000;
		w["x:cls_prop"] = 1;
		Check("propagate", w,
		      {{"x:dst_open", dst.open ? 1u : 0u}, {"x:dst_span", dst.w[0].e},
		       {"x:cls_prop", Cls(T::ClassKey(Fields(2)), T::CC::ep_prop)}});
	}
	{ // ep_bad (b): a closure sees the open flag while no episode is counted; (v): the exit scan
		Reset(1);
		T::ImageState s;
		s.open = true;
		T::CloseNoUpload(s, T::Close::Commit, true);
		T::ExitScan(1, 0);
		Check("ep_bad", {{"cl_commit", 1}, {"ep_bad", 2}, {"open", UINT64_MAX}});
	}
}

void CasesPure() {
	{ // the magenta codes of design s.5.3 and a non-magenta texel
		bool       ok = true;
		uint8_t    code[16];
		uint32_t   bytes = 0;
		const struct {
			uint32_t fmt;
			uint32_t bytes;
			uint8_t  b[16];
		} rows[] = {
		    {VK_FORMAT_R8_UNORM, 1, {255}},
		    {VK_FORMAT_R8G8_UNORM, 2, {255, 0}},
		    {VK_FORMAT_R8G8B8A8_UNORM, 4, {255, 0, 255, 255}},
		    {VK_FORMAT_B8G8R8A8_SRGB, 4, {255, 0, 255, 255}},
		    {VK_FORMAT_R16_SFLOAT, 2, {0x00, 0x3c}},
		    {VK_FORMAT_R16G16B16A16_SFLOAT, 8, {0x00, 0x3c, 0, 0, 0x00, 0x3c, 0x00, 0x3c}},
		    {VK_FORMAT_R32G32_SFLOAT, 8, {0, 0, 0x80, 0x3f, 0, 0, 0, 0}},
		    {VK_FORMAT_A2B10G10R10_UNORM_PACK32, 4, {0xff, 0x03, 0xf0, 0xff}},
		    {VK_FORMAT_B10G11R11_UFLOAT_PACK32, 4, {0xc0, 0x03, 0x00, 0x78}},
		    {VK_FORMAT_R16G16B16A16_UNORM, 8, {0xff, 0xff, 0, 0, 0xff, 0xff, 0xff, 0xff}},
		};
		for (const auto& r: rows) {
			ok = ok && T::MagentaCode(r.fmt, code, &bytes) && bytes == r.bytes && std::memcmp(code, r.b, r.bytes) == 0 &&
			     T::TexelIsMagenta(r.fmt, r.b);
		}
		const uint8_t green[4] = {0, 255, 0, 255};
		ok = ok && !T::TexelIsMagenta(VK_FORMAT_R8G8B8A8_UNORM, green) && !T::MagentaCode(VK_FORMAT_R8G8B8A8_UINT, code, &bytes);
		Reset(1);
		Check("magenta", {{"x:ok", 1}}, {{"x:ok", ok ? 1u : 0u}});
	}
	{ // the class key: FNV-1a 64 of the fields (independent recomputation)
		const auto f = Fields(3);
		uint64_t   h = 0xcbf29ce484222325ull;
		for (const uint32_t v: {f.fmt, f.tile, f.w, f.h, f.levels, f.layers, f.cmp, f.samples, f.usage, f.vol}) {
			for (uint32_t i = 0; i < 8; i++) {
				h ^= (static_cast<uint64_t>(v) >> (8 * i)) & 0xffu;
				h *= 0x100000001b3ull;
			}
		}
		Reset(1);
		Check("class_key", {{"x:eq", 1}, {"x:diff", 1}},
		      {{"x:eq", T::ClassKey(f) == h ? 1u : 0u}, {"x:diff", T::ClassKey(f) != T::ClassKey(Fields(1)) ? 1u : 0u}});
	}
	{ // VerifyTintPlan: a bit outside [first, end) and (mode 2) an intersecting level count tint_bad
		Reset(2);
		const T::Span w[1] = {{A + 0x4000, A + 0x4100}};
		const auto    m    = T::VerifyTintPlan(Geo(), 0b111, 1, 3, w, 1);
		Check("verify", {{"tint_bad", 2}, {"x:mask", 0b100}}, {{"x:mask", m}});
	}
}

void CasesReadback() {
	{ // rb0 magenta -> rb1 due in a later frame; written after the tint -> over; not written -> ok / bad
		Reset(2);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		auto plan = T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, true);
		const auto first = T::RbBegin(s, plan, Geo(), 64, 64, VK_FORMAT_R8G8B8A8_UNORM, 10);
		T::RbDone0(first, true);
		T::RbDone0(first + 1, true);
		T::RbInfo infos[4];
		const auto same_frame = T::RbWant1(s, 10, infos, 4);
		T::NoteGpuWrite(s); // a write after the tint
		const auto n = T::RbWant1(s, 11, infos, 4);
		T::RbDone1(infos[0].id, false);
		T::RbDone1(infos[1].id, true);
		auto w = Opened(0x4000, 0x5000, "w_mipal");
		w.erase("open");
		w["cl_smp"]        = 1;
		w["lost_bytes"]    = 0x4400;
		w["tint_ep"]       = 1;
		w["tint_mips"]     = 2;
		w["tint_bytes"]    = 0x4400;
		w["tint_rb_req"]   = 2;
		w["tint_rb0_ok"]   = 2;
		w["tint_rb1_over"] = 1;
		w["tint_rb1_ok"]   = 1;
		w["x:same_frame"]  = 0;
		w["x:n"]           = 2;
		w["x:x0"]          = 32;
		w["x:x2"]          = 8;
		w["x:pend"]        = 0;
		Check("rb_over", w,
		      {{"x:same_frame", same_frame}, {"x:n", n}, {"x:x0", infos[0].x}, {"x:x2", infos[1].x},
		       {"x:pend", s.rb_pend.load()}});
	}
	{ // rb1 not magenta and no write after the tint -> rb1_bad; rb0 not magenta -> rb0_bad; abandon and exit -> none
		Reset(2);
		T::ImageState s;
		Open(s, Geo(), 0x4000, 0x5000);
		auto       plan  = T::CloseUpload(s, Geo(), Fields(), T::Close::Smp, 0, 3, 0, 0, true, false, true);
		const auto first = T::RbBegin(s, plan, Geo(), 64, 64, VK_FORMAT_R8G8B8A8_UNORM, 10);
		T::RbDone0(first, true);
		T::RbDone0(first + 1, false);
		T::RbInfo infos[4];
		const auto n = T::RbWant1(s, 11, infos, 4);
		T::RbDone1(infos[0].id, false);
		// a second image: rb0 in flight when it is freed, then the exit
		T::ImageState t;
		Open(t, Geo(), 0x4000, 0x5000);
		auto plan2 = T::CloseUpload(t, Geo(), T::ClassFields {}, T::Close::Smp, 0, 3, 0, 0, true, false, true);
		(void)T::RbBegin(t, plan2, Geo(), 64, 64, VK_FORMAT_R8G8B8A8_UNORM, 10);
		T::NoteFree(t, true);
		T::PrintExit();
		Want w = {{"part", 2}, {"part_st", 2}, {"part_off", 2}, {"w_mipal", 2}, {"w_bytes", 0x2000}, {"img_bytes", 0xa800},
		          {"img_bytes_unsync", 0xa800}, {"img_full_unsync", 0xa800}, {"ep_new", 2}, {"cl_smp", 2},
		          {"cl_none", 1}, {"lost_bytes", 0x8800}, {"tint_ep", 2}, {"tint_mips", 4}, {"tint_bytes", 0x8800},
		          {"tint_rb_req", 4}, {"tint_rb0_ok", 1}, {"tint_rb0_bad", 1}, {"tint_rb1_bad", 1}, {"tint_rb0_none", 2},
		          {"x:n", 1}};
		Check("rb_bad_none", w, {{"x:n", n}});
	}
}

void CasesT109() {
	struct Draw {
		const char* name;
		uint32_t    fmt;
		bool        test;
		bool        write;
		bool        zx;
		bool        bias;
		float       min0, max0, min1, max1;
		uint32_t    count;
		T109::Totals want;
	};
	const Draw draws[] = {
	    // not D32 (t3: bias without the D32 condition)
	    {"t109_d24", VK_FORMAT_D24_UNORM_S8_UINT, true, true, true, true, 0.0f, 0.5f, 0.0f, 1.0f, 1, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}},
	    // D32, no test and no write
	    {"t109_off", VK_FORMAT_D32_SFLOAT, false, false, true, true, 0.0f, 0.5f, 0.0f, 1.0f, 1, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}},
	    // D32, full range (t2: the strict comparisons at 0 and 1)
	    {"t109_full", VK_FORMAT_D32_SFLOAT, true, false, true, true, 0.0f, 1.0f, 0.0f, 1.0f, 2, {1, 1, 0, 1, 0, 0, 0, 0, 0, 0}},
	    // D32S8, maxDepth < 1 on viewport 0
	    {"t109_max", VK_FORMAT_D32_SFLOAT_S8_UINT, false, true, true, false, 0.0f, 0.5f, 0.0f, 1.0f, 1, {1, 1, 1, 0, 0, 0, 0, 0, 0, 0}},
	    // D32, minDepth > 0 only on viewport 1 of 2 (t1: only viewport 0); M9d3: count 2 - bias_narrow_vi (t7, t9)
	    {"t109_vp1", VK_FORMAT_D32_SFLOAT, true, true, false, true, 0.0f, 1.0f, 0.25f, 1.0f, 2, {1, 0, 0, 1, 1, 0, 0, 0, 1, 0}},
	    // D32, narrow, no Z export (t4: zx_narrow without zx_d32)
	    {"t109_nozx", VK_FORMAT_D32_SFLOAT, true, true, false, false, 0.0f, 0.5f, 0.0f, 1.0f, 1, {1, 0, 0, 0, 0, 0, 0, 0, 0, 0}},
	};
	for (const auto& d: draws) {
		Reset(1);
		VkViewport vp[2] = {};
		vp[0].minDepth   = d.min0;
		vp[0].maxDepth   = d.max0;
		vp[1].minDepth   = d.min1;
		vp[1].maxDepth   = d.max1;
		VkRect2D sc[2]   = {};
		sc[0].extent     = {64, 64}; // M9d2: both slots rasterize
		sc[1].extent     = {64, 64};
		T109::NoteDraw(d.fmt, d.test, d.write, d.zx, d.bias, vp, sc, d.count, false);
		const auto t = T109::Read();
		Check(d.name,
		      {{"x:d32", d.want.d32}, {"x:zx_d32", d.want.zx_d32}, {"x:zx_narrow", d.want.zx_narrow},
		       {"x:bias_d32", d.want.bias_d32}, {"x:bias_narrow", d.want.bias_narrow},
		       {"x:zx_narrow_vi", d.want.zx_narrow_vi}, {"x:bias_narrow_vi", d.want.bias_narrow_vi},
		       {"x:narrow_cd", d.want.narrow_cd}},
		      {{"x:d32", t.d32}, {"x:zx_d32", t.zx_d32}, {"x:zx_narrow", t.zx_narrow}, {"x:bias_d32", t.bias_d32},
		       {"x:bias_narrow", t.bias_narrow}, {"x:zx_narrow_vi", t.zx_narrow_vi},
		       {"x:bias_narrow_vi", t.bias_narrow_vi}, {"x:narrow_cd", t.narrow_cd}});
	}
	// M9d2 (RC1 of M9e, ROADMAP s122 item 788(b)(4)): rasterized slots only (scissor area > 0) and the [min, max] range.
	// D32, test, write, Z export and bias on; an empty slot is minDepth = maxDepth = 0, width 1, scissor {0, 0} (as
	// SetGraphicsDynamicParams leaves it); the active slot has a 64x64 scissor. want = zx_narrow = bias_narrow.
	// M9d3 (RC1 of M9e2, item 789(v)(3)): want_vi = zx_narrow_vi = bias_narrow_vi, want_cd = narrow_cd; with cd
	// (clip_disable) every slot is 16384 x 16384 and has the 64x64 scissor (vport_scissor_enable 0), the slots other
	// than the active one keep minDepth = maxDepth = 0.
	struct Slots {
		const char* name;
		uint32_t    count;
		uint32_t    active;
		float       min_a, max_a;
		uint64_t    want;
		uint64_t    want_vi;
		uint64_t    want_cd;
		bool        cd;
	};
	const Slots slots[] = {
	    // 16 slots, slot 0 full, slots 1-15 empty 0/0 (t5: every slot without the scissor test)
	    {"t109_vi16", 16, 0, 0.0f, 1.0f, 0, 0, 0, false},
	    // inverted full range [1, 0] (t6: raw minDepth / maxDepth without min/max)
	    {"t109_inv", 1, 0, 1.0f, 0.0f, 0, 0, 0, false},
	    // inverted narrow range [1, 0.5] - positive control of min/max
	    {"t109_inv_n", 1, 0, 1.0f, 0.5f, 1, 0, 0, false},
	    // 16 slots, active slot 3 [0, 0.5], the rest empty (t1: only slot 0); M9d3: multi-slot narrow (t7, t9)
	    {"t109_vi16n", 16, 3, 0.0f, 0.5f, 1, 1, 0, false},
	    // M9d3: 16 slots, clip_disable, slot 0 [0, 1], slots 1-15 0/0 with 64x64 scissors - the false narrow of RC1 of
	    // M9e2 is seen in zx_narrow_vi / bias_narrow_vi and narrow_cd (once per draw) (t7, t9)
	    {"t109_cd16", 16, 0, 0.0f, 1.0f, 1, 1, 1, true},
	    // M9d3: 1 slot [0, 0.5], clip_disable - positive control of the split by count (t8)
	    {"t109_cd1", 1, 0, 0.0f, 0.5f, 1, 0, 0, true},
	};
	for (const auto& s: slots) {
		Reset(1);
		VkViewport vp[16] = {};
		VkRect2D   sc[16] = {};
		for (uint32_t i = 0; i < 16; i++) {
			vp[i].width  = s.cd ? 16384.0f : 1.0f;
			vp[i].height = s.cd ? 16384.0f : 1.0f;
			if (s.cd) {
				sc[i].extent = {64, 64};
			}
		}
		if (!s.cd) {
			vp[s.active].width  = 64.0f;
			vp[s.active].height = 64.0f;
		}
		vp[s.active].minDepth = s.min_a;
		vp[s.active].maxDepth = s.max_a;
		sc[s.active].extent   = {64, 64};
		T109::NoteDraw(VK_FORMAT_D32_SFLOAT, true, true, true, true, vp, sc, s.count, s.cd);
		const auto t = T109::Read();
		Check(s.name,
		      {{"x:d32", 1}, {"x:zx_d32", 1}, {"x:zx_narrow", s.want}, {"x:bias_d32", 1}, {"x:bias_narrow", s.want},
		       {"x:zx_narrow_vi", s.want_vi}, {"x:bias_narrow_vi", s.want_vi}, {"x:narrow_cd", s.want_cd}},
		      {{"x:d32", t.d32}, {"x:zx_d32", t.zx_d32}, {"x:zx_narrow", t.zx_narrow}, {"x:bias_d32", t.bias_d32},
		       {"x:bias_narrow", t.bias_narrow}, {"x:zx_narrow_vi", t.zx_narrow_vi},
		       {"x:bias_narrow_vi", t.bias_narrow_vi}, {"x:narrow_cd", t.narrow_cd}});
	}
	{
		Reset(1);
		T109::NoteRenderOverride(0x20000000u);
		T109::NoteRenderOverride(0x00010000u);
		const auto t = T109::Read();
		Check("t109_ovr",
		      {{"x:ovr_w", 2}, {"x:ovr_vpc", 1}, {"x:zx_narrow_vi", 0}, {"x:bias_narrow_vi", 0}, {"x:narrow_cd", 0}},
		      {{"x:ovr_w", t.ovr_w}, {"x:ovr_vpc", t.ovr_vpc}, {"x:zx_narrow_vi", t.zx_narrow_vi},
		       {"x:bias_narrow_vi", t.bias_narrow_vi}, {"x:narrow_cd", t.narrow_cd}});
	}
}

} // namespace

// The cls arm (driver: KYTY_DIAG_T188=2, KYTY_DIAG_T188_CLS="<ClassKey(Fields())>,zz,1"): the list is read once by the
// static initialization; the class of Fields() is listed, that of Fields(4) is not - its closure counts tint_skip_cls.
int ArmCls() {
	const bool listed = T::ClassListed(T::ClassKey(Fields()));
	const bool other  = T::ClassListed(T::ClassKey(Fields(4)));
	Reset(2);
	T::ImageState s;
	(void)T::NoteInvalidate(s, Geo(), Fields(4), true, T::Writer::St, A + 0x4000, 0x1000, false, true);
	const auto plan = T::CloseUpload(s, Geo(), Fields(4), T::Close::Smp, 0, 3, 0, 0, true, false, true);
	const bool ok = T::g_mode == 2 && listed && !other && T::Read(T::C::tint_skip_cls) == 1 && plan.mask == 0;
	std::printf("T188Stand: cls listed=%d other=%d skip_cls=%llu mask=%u ok=%d\n", listed ? 1 : 0, other ? 1 : 0,
	            static_cast<unsigned long long>(T::Read(T::C::tint_skip_cls)), plan.mask, ok ? 1 : 0);
	return 0;
}

int main(int argc, char** argv) {
	if (argc != 2 && !(argc == 3 && std::strcmp(argv[2], "cls") == 0)) {
		std::fprintf(stderr, "usage: t188_stand <log file> [cls]\n");
		return 2;
	}
	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction   = Config::LogDirection::File;
	options.printf_output_file = argv[1];
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();
	const int env_mode = T::g_mode;
	T::PrintModeLine();
	if (argc == 3) {
		(void)ArmCls();
		std::fflush(stdout);
		Log::Flush();
		Log::DrainForExit();
		std::_Exit(0);
	}
	std::printf("T188Stand: env_mode=%d cls_listed_zero=%d\n", env_mode, T::ClassListed(0) ? 1 : 0);
	CasesS2();
	CasesS3();
	CasesClosures();
	CasesPure();
	CasesReadback();
	CasesT109();
	std::printf("T188Stand: total=%d match=%d END\n", g_total, g_match);
	std::fflush(stdout);
	Log::Flush();
	Log::DrainForExit();
	std::_Exit(0);
}
