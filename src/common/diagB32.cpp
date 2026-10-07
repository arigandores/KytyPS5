#include "common/diagB32.h"

#include "common/common.h"
#include "common/frameStats.h"
#include "common/logging/log.h"

#include <algorithm>
#include <random>
#include <chrono>
#include <cinttypes>
#include <cstdarg>
#include <cstddef>
#include <cstdio>
#include <condition_variable>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
// clang-format off
#include <tlhelp32.h>
// clang-format on
#endif

// Track F, F20j (HPP-629): see diagB32.h. Sites and the record table - docs/track-f/f20j.md.

namespace Common::DiagB32 {

bool g_on            = false;
bool g_test_on       = false;
bool g_test_gpusleep = false;
bool g_present_site  = false;

namespace {

// Stand KYTY_TEST_B32 (read once by Init).
bool                  g_test_present = false;
double                g_test_delay_s = 0.0;
uint32_t              g_test_ms      = 0;
std::atomic<bool>     g_test_armed {false};
std::atomic<uint64_t> g_test_fire_ns {0};
std::atomic<bool>     g_test_done {false};
bool                  g_config_invalid = false;
char                  g_config_text[64] {};
char                  g_test_text[64] {};

} // namespace

const char* CallName(uint8_t call) {
	static constexpr const char* names[] = {"-", "present", "acquire", "qsubmit", "qlock", "drain", "semwait", "protect", "fault"};
	return call < sizeof(names) / sizeof(names[0]) ? names[call] : "?";
}

const char* WaitName(uint8_t kind) {
	static constexpr const char* names[] = {"-", "cond", "mutex", "sem", "psem", "evf", "eq", "sleep", "gpu_idle", "gpu_regmem",
	                                        // F20j3 (item 574(g)(1)): emulator waits, in the order of enum Wait
	                                        "emu_mutex", "gpu_wait", "gpu_cmd", "flip_slot", "flip_done", "flip_cancel",
	                                        "flip_req", "vo_pace", "relay", "frame_pool", "rec_wait", "rec_idle",
	                                        "asub_idle", "asub_drain", "ops_wait", "ops_idle", "pipe_wait", "pcopy",
	                                        "pm_drain", "vma_flush", "rec_queue", "main_task", "main_idle", "spin", "av",
	                                        "vblank", "once", "join", "addr", "aio", "fiber", "audio", "ult", "net", "rwlock",
	                                        // F20j4 (item 581(v)(5)): Common::Thread::Join
	                                        "emu_join"};
	static_assert(sizeof(names) / sizeof(names[0]) == static_cast<size_t>(Wait::Count));
	return kind < sizeof(names) / sizeof(names[0]) ? names[kind] : "?";
}

const char* StateName(State state) {
	static constexpr const char* names[] = {"X", "H", "W", "R", "r", "Sr", "Sw", "S"};
	const auto                   i       = static_cast<size_t>(state);
	return i < sizeof(names) / sizeof(names[0]) ? names[i] : "?";
}

// =====================================================================================================================
// Core
// =====================================================================================================================
namespace Core {

bool KernelReady(uint32_t thread_state) {
	return thread_state == 1 || thread_state == 2 || thread_state == 3 || thread_state == 6 || thread_state == 7;
}

bool KernelWaiting(uint32_t thread_state) {
	return thread_state == 5 || thread_state == 8 || thread_state == 9;
}

uint16_t Classify(uint32_t mark, uint64_t cpu_ns, uint64_t interval_ns, bool kq, uint32_t kthread_state,
                  uint32_t kwait_reason) {
	const auto mark_state = static_cast<State>(mark >> 8u);
	const auto mark_kind  = static_cast<uint8_t>(mark & 0xffu);
	if (mark_state == State::H) {
		return Code(State::H, mark_kind);
	}
	if (mark_state == State::W) {
		return Code(State::W, mark_kind);
	}
	if (interval_ns > 0 && cpu_ns * 2 >= interval_ns) {
		return Code(State::R, 0);
	}
	if (cpu_ns > 0) {
		return Code(State::Rr, 0);
	}
	if (kq) {
		if (KernelReady(kthread_state)) {
			return Code(State::Sr, 0);
		}
		if (KernelWaiting(kthread_state)) {
			return Code(State::Sw, static_cast<uint8_t>(std::min<uint32_t>(kwait_reason, 63)));
		}
	}
	return Code(State::S, 0);
}

void Agg::Add(uint16_t code) {
	const auto state = CodeState(code);
	const auto kind  = CodeKind(code);
	const auto si    = static_cast<size_t>(state);
	if (si >= static_cast<size_t>(State::Count)) {
		st[static_cast<size_t>(State::S)]++;
		return;
	}
	if (state == State::H) {
		h[kind < static_cast<uint8_t>(Call::Count) ? kind : 0]++;
	} else if (state == State::W) {
		w[kind < static_cast<uint8_t>(Wait::Count) ? kind : 0]++;
	} else if (state == State::Sw) {
		swr[std::min<uint32_t>(kind, 63)]++;
	} else {
		st[si]++;
	}
}

uint32_t Agg::SumH() const {
	uint32_t s = 0;
	for (auto v: h) {
		s += v;
	}
	return s;
}

uint32_t Agg::SumW() const {
	uint32_t s = 0;
	for (auto v: w) {
		s += v;
	}
	return s;
}

uint32_t Agg::SumSw() const {
	uint32_t s = 0;
	for (auto v: swr) {
		s += v;
	}
	return s;
}

uint32_t Agg::Total() const {
	return st[static_cast<size_t>(State::X)] + st[static_cast<size_t>(State::R)] + st[static_cast<size_t>(State::Rr)] +
	       st[static_cast<size_t>(State::Sr)] + st[static_cast<size_t>(State::S)] + SumSw() + SumW() + SumH();
}

GapStats Gaps(const uint64_t* t, size_t n, uint64_t win_start, uint64_t win_end, uint64_t period_ns) {
	GapStats g;
	g.samples      = static_cast<uint32_t>(n);
	uint64_t prev  = win_start;
	const auto gap = [&](uint64_t a, uint64_t b) {
		if (b < a) {
			g.monotonic = false;
			return;
		}
		const auto d  = b - a;
		g.sgap_max_ns = std::max(g.sgap_max_ns, d);
		if (d > 3 * period_ns) {
			g.gap3p++;
		}
	};
	for (size_t i = 0; i < n; i++) {
		gap(prev, t[i]);
		prev = t[i];
	}
	gap(prev, win_end);
	const uint64_t window = win_end > win_start ? win_end - win_start : 0;
	g.i2_ok               = period_ns > 0 && static_cast<uint64_t>(n) >= window / (2 * period_ns);
	return g;
}

bool KqSchedule::Due(uint64_t now_ns) const {
	if (win_start == 0 || now_ns < win_start + kKernelAfterNs) {
		return false;
	}
	return (win_kq_ns + last_kq_ns) * kKqBudgetDiv <= now_ns - win_start;
}

void KqSchedule::Done(uint64_t cost_ns) {
	win_kq_ns += cost_ns;
	last_kq_ns = cost_ns;
}

void KqSchedule::NewWindow(uint64_t flip_ns, uint64_t carried_kq_ns) {
	win_start = flip_ns;
	win_kq_ns = carried_kq_ns;
}

uint64_t NextBegin(uint64_t begin_ns, uint64_t now_ns) {
	return std::max(begin_ns + kPeriodNs, now_ns);
}

void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,
                     int32_t* out) {
	// F25d (item 599(b)(8), RC8 of F25c): the inner loop runs over the samples with a snapshot only, in the same order
	// (the same nearest one and the same tie - the earlier) - n x snapshots instead of n x n.
	std::vector<size_t> snaps;
	for (size_t j = 0; j < n; j++) {
		if (kq[j] != 0) {
			snaps.push_back(j);
		}
	}
	for (size_t i = 0; i < n; i++) {
		if (kq[i] != 0) {
			out[i] = static_cast<int32_t>(i);
			continue;
		}
		int32_t  best   = -1;
		uint64_t best_d = 0;
		for (const size_t j: snaps) {
			const auto d = t[i] > kq_t[j] ? t[i] - kq_t[j] : kq_t[j] - t[i];
			if (d <= max_ns && (best < 0 || d < best_d)) {
				best   = static_cast<int32_t>(j);
				best_d = d;
			}
		}
		out[i] = best;
	}
}

void WindowSamples(const uint64_t* t, const uint64_t* cost, const uint8_t* kq, uint64_t hpos, uint32_t hist,
                   uint64_t start, uint64_t end, uint64_t extra_ns, std::vector<uint64_t>* idx, uint64_t* instr_ns,
                   uint32_t* kq_n, bool* exhausted) {
	idx->clear();
	*instr_ns     = extra_ns;
	*kq_n         = 0;
	bool found_le = false;
	for (uint64_t k = 0; k < hist && k < hpos; k++) {
		const auto h  = hpos - 1 - k;
		const auto th = t[h % hist];
		if (th <= start) {
			found_le = true;
			break;
		}
		if (th <= end) {
			idx->push_back(h);
		}
	}
	*exhausted = !found_le && hpos >= hist;
	std::reverse(idx->begin(), idx->end());
	for (auto h: *idx) {
		*instr_ns += cost[h % hist];
		*kq_n += kq[h % hist];
	}
}

int64_t OtherUs(uint64_t sys_busy_us, uint64_t proc_us) {
	return static_cast<int64_t>(sys_busy_us) - static_cast<int64_t>(proc_us);
}

std::string SafeName(const char* name) {
	std::string out;
	if (name != nullptr) {
		for (size_t i = 0; name[i] != '\0' && out.size() < 31; i++) {
			const char c  = name[i];
			const bool ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' ||
			                c == '.' || c == '-';
			out.push_back(ok ? c : '_');
		}
	}
	if (out.empty()) {
		out = "-";
	}
	return out;
}

int32_t Registry::Allocate(uint32_t os_tid, void* handle, const char* role, const char* name, int32_t gid) {
	const auto idx = count.fetch_add(1, std::memory_order_acq_rel);
	if (idx >= kSlots) {
		count.fetch_sub(1, std::memory_order_acq_rel);
		slot_full.fetch_add(1, std::memory_order_relaxed);
		return -1;
	}
	auto& s  = slots[idx];
	s.os_tid = os_tid;
	s.handle = handle;
	std::snprintf(s.role, sizeof(s.role), "%s", role != nullptr ? role : "emu");
	std::snprintf(s.name, sizeof(s.name), "%s", name != nullptr ? name : s.role);
	s.gid.store(gid, std::memory_order_relaxed);
	s.live.store(1, std::memory_order_release);
	return static_cast<int32_t>(idx);
}

void Registry::WriteMark(int32_t idx, uint32_t mark, uint64_t obj, uint64_t since, int32_t peer) {
	auto&      s   = slots[idx];
	const auto seq = s.seq.load(std::memory_order_relaxed);
	s.seq.store(seq + 1, std::memory_order_relaxed);
	std::atomic_thread_fence(std::memory_order_release);
	s.mark.store(mark, std::memory_order_relaxed);
	s.obj.store(obj, std::memory_order_relaxed);
	s.since.store(since, std::memory_order_relaxed);
	s.peer.store(peer, std::memory_order_relaxed);
	s.seq.store(seq + 2, std::memory_order_release);
}

bool Registry::ReadMark(int32_t idx, MarkSnap* out) {
	auto& s = slots[idx];
	for (int attempt = 0; attempt < 3; attempt++) {
		const auto s1 = s.seq.load(std::memory_order_acquire);
		if ((s1 & 1u) != 0) {
			continue;
		}
		MarkSnap v;
		v.mark  = s.mark.load(std::memory_order_relaxed);
		v.obj   = s.obj.load(std::memory_order_relaxed);
		v.since = s.since.load(std::memory_order_relaxed);
		v.peer  = s.peer.load(std::memory_order_relaxed);
		std::atomic_thread_fence(std::memory_order_acquire);
		const auto s2 = s.seq.load(std::memory_order_relaxed);
		if (s1 == s2) {
			*out = v;
			return true;
		}
	}
	torn.fetch_add(1, std::memory_order_relaxed);
	return false;
}

void WaitRing::Push(const WaitRec& rec) {
	Write(Reserve(), rec);
}

uint64_t WaitRing::Reserve() {
	return wpos.fetch_add(1, std::memory_order_acq_rel);
}

void WaitRing::Write(uint64_t i, const WaitRec& rec) {
	auto& x = e[i % kWaitRing];
	x.seq.store(2 * i + 1, std::memory_order_relaxed);
	std::atomic_thread_fence(std::memory_order_release);
	x.start.store(rec.start_ns, std::memory_order_relaxed);
	x.end.store(rec.end_ns, std::memory_order_relaxed);
	x.obj.store(rec.obj, std::memory_order_relaxed);
	x.req.store(rec.req_us, std::memory_order_relaxed);
	x.who.store(static_cast<uint64_t>(static_cast<uint32_t>(rec.slot1) & 0xfffffu) |
	                (static_cast<uint64_t>(static_cast<uint32_t>(rec.waker1) & 0xfffffu) << 20u) |
	                (static_cast<uint64_t>(rec.kind) << 40u) | (static_cast<uint64_t>(rec.timed_out) << 48u),
	            std::memory_order_relaxed);
	x.peer.store(static_cast<uint32_t>(rec.peer1), std::memory_order_relaxed);
	x.seq.store(2 * i + 2, std::memory_order_release);
}

void WaitRing::Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn, uint64_t* held) {
	const auto w = wpos.load(std::memory_order_acquire);
	if (w > rpos + kWaitRing) {
		*drop += w - kWaitRing - rpos;
		rpos = w - kWaitRing;
	}
	while (rpos < w) {
		auto&      x    = e[rpos % kWaitRing];
		const auto want = 2 * rpos + 2;
		const auto s1   = x.seq.load(std::memory_order_acquire);
		if (s1 < want) {
			// F20j2 (RC4): the write of this position has not finished - not started (an older lap's word) or in progress
			// (2 * rpos + 1; the writer may be preempted between Reserve and the final word). Stop here; the next drain
			// (the next flip) continues from this position. F20j3 (Z1): the positions left behind - ring_hold.
			if (held != nullptr) {
				*held += w - rpos;
			}
			break;
		}
		if (s1 == want) {
			WaitRec r;
			r.start_ns     = x.start.load(std::memory_order_relaxed);
			r.end_ns       = x.end.load(std::memory_order_relaxed);
			r.obj          = x.obj.load(std::memory_order_relaxed);
			r.req_us       = x.req.load(std::memory_order_relaxed);
			r.peer1        = static_cast<int32_t>(x.peer.load(std::memory_order_relaxed));
			const auto who = x.who.load(std::memory_order_relaxed);
			std::atomic_thread_fence(std::memory_order_acquire);
			if (x.seq.load(std::memory_order_relaxed) == s1) {
				r.slot1     = static_cast<int32_t>(who & 0xfffffu);
				r.waker1    = static_cast<int32_t>((who >> 20u) & 0xfffffu);
				r.kind      = static_cast<uint8_t>((who >> 40u) & 0xffu);
				r.timed_out = static_cast<uint8_t>((who >> 48u) & 0xffu);
				out->push_back(r);
				rpos++;
				continue;
			}
		}
		// Overwritten by a later lap before or while it was read: the record is lost (F20j2 RC4 - only this is torn).
		(*torn)++;
		rpos++;
	}
}

static uint64_t Overlap(const WaitRec& w, uint64_t a, uint64_t b) {
	const auto s = std::max(w.start_ns, a);
	const auto e = std::min(w.end_ns, b);
	return e > s ? e - s : 0;
}

// F25d (item 599(b)(8), RC8 of F25c): slot + 1 -> the position of the FIRST thread row with it, built once per call -
// the answer of the linear search of F20j4 (RowOf, GidOf) by construction. Rows with slot1 <= 0 are not indexed:
// RowOf never returns them, GidOf searches them linearly (none in the sampler's reports).
class RowIndex {
public:
	explicit RowIndex(const Report& r) {
		for (size_t i = 0; i < r.threads.size(); i++) {
			const auto s = r.threads[i].slot1;
			if (s <= 0) {
				m_nonpos = true;
				continue;
			}
			if (static_cast<size_t>(s) >= m_pos.size()) {
				m_pos.resize(static_cast<size_t>(s) + 1, -1);
			}
			if (m_pos[static_cast<size_t>(s)] < 0) {
				m_pos[static_cast<size_t>(s)] = static_cast<int32_t>(i);
			}
		}
	}
	[[nodiscard]] int32_t Pos(int32_t slot1) const {
		return slot1 > 0 && static_cast<size_t>(slot1) < m_pos.size() ? m_pos[static_cast<size_t>(slot1)] : -1;
	}
	[[nodiscard]] bool NonPositive() const { return m_nonpos; }

private:
	std::vector<int32_t> m_pos;
	bool                 m_nonpos = false;
};

static ThreadRow* RowOf(Report* r, const RowIndex& index, int32_t slot1) {
	const auto p = index.Pos(slot1);
	return p >= 0 ? &r->threads[static_cast<size_t>(p)] : nullptr;
}

// The -w records printed: the closure (3 steps) of the chain participants first (the present thread, GuestGpu,
// flip_slot, threads with R >= 10 %), then the rest by overlap with the window up to kWLinesCap in all. F20j3 (item
// 574(d)): the closure follows the waker and the peer of a record.
static std::vector<size_t> PickWaits(const Report& r, size_t* cut) {
	std::vector<int32_t> set;
	const auto           add = [&](int32_t s) {
        if (s > 0 && std::find(set.begin(), set.end(), s) == set.end()) {
            set.push_back(s);
        }
	};
	add(r.vo_slot1);
	add(r.gpu_slot1);
	add(r.flip_slot1);
	const auto samples = r.gaps.samples;
	for (const auto& t: r.threads) {
		if (samples > 0 && t.agg.st[static_cast<size_t>(State::R)] * 10 >= samples) {
			add(t.slot1);
		}
	}
	std::vector<size_t> must;
	// F25d (item 599(b)(8), RC8 of F25c): a record's membership in `must` - a flag per record, not std::find over must.
	std::vector<char> in_must(r.waits.size(), 0);
	for (int step = 0; step < 3; step++) {
		const auto before = set.size();
		for (size_t i = 0; i < r.waits.size(); i++) {
			if (in_must[i] == 0 && std::find(set.begin(), set.end(), r.waits[i].slot1) != set.end()) {
				in_must[i] = 1;
				must.push_back(i);
				add(r.waits[i].waker1);
				add(r.waits[i].peer1);
			}
		}
		if (set.size() == before) {
			break;
		}
	}
	std::vector<size_t> rest;
	for (size_t i = 0; i < r.waits.size(); i++) {
		if (in_must[i] == 0) {
			rest.push_back(i);
		}
	}
	std::sort(rest.begin(), rest.end(), [&](size_t a, size_t b) {
		return Overlap(r.waits[a], r.win_start_ns, r.win_end_ns) > Overlap(r.waits[b], r.win_start_ns, r.win_end_ns);
	});
	std::vector<size_t> out = must;
	*cut                    = 0;
	for (auto i: rest) {
		if (out.size() < kWLinesCap) {
			out.push_back(i);
		} else {
			(*cut)++;
		}
	}
	return out;
}

void MarkMandatory(Report* report) {
	auto&      r       = *report;
	const auto samples = r.gaps.samples;
	for (auto& t: r.threads) {
		// F20j2 RC5: the async submitter in a window where it waited for / held graphics.queue_mutex.
		const bool asub = t.role == "ASubmit" &&
		                  t.agg.h[static_cast<size_t>(Call::QLock)] + t.agg.h[static_cast<size_t>(Call::QSubmit)] > 0;
		t.must = t.slot1 == r.vo_slot1 || t.slot1 == r.gpu_slot1 || t.slot1 == r.flip_slot1 ||
		         (samples > 0 && t.agg.st[static_cast<size_t>(State::R)] * 10 >= samples) || asub;
	}
	size_t         cut  = 0;
	const auto     pick = PickWaits(r, &cut);
	const RowIndex index(r); // F25d (item 599(b)(8))
	for (auto i: pick) {
		if (auto* t = RowOf(&r, index, r.waits[i].waker1); t != nullptr) {
			t->must = true;
		}
		if (auto* t = RowOf(&r, index, r.waits[i].peer1); t != nullptr) { // F20j3 (RC2: every waker / peer of the -w records)
			t->must = true;
		}
	}
	for (auto& t: r.threads) {
		if (t.last.mark != 0 && t.last.peer > 0) {
			if (auto* p = RowOf(&r, index, t.last.peer); p != nullptr && t.must) {
				p->must = true;
			}
		}
	}
}

static std::string KindList(const uint32_t* v, size_t n, const char* (*name)(uint8_t)) {
	std::string out;
	for (size_t i = 1; i < n; i++) {
		if (v[i] == 0) {
			continue;
		}
		char buf[48];
		std::snprintf(buf, sizeof(buf), "%s%s:%u", out.empty() ? "" : ",", name(static_cast<uint8_t>(i)), v[i]);
		out += buf;
	}
	if (v[0] != 0) {
		char buf[24];
		std::snprintf(buf, sizeof(buf), "%s?:%u", out.empty() ? "" : ",", v[0]);
		out += buf;
	}
	return out.empty() ? "-" : out;
}

static std::string ReasonList(const uint32_t* v) {
	std::string out;
	for (size_t i = 0; i < 64; i++) {
		if (v[i] == 0) {
			continue;
		}
		char buf[32];
		std::snprintf(buf, sizeof(buf), "%s%zu:%u", out.empty() ? "" : ",", i, v[i]);
		out += buf;
	}
	return out.empty() ? "-" : out;
}

static int32_t SlotIndex(int32_t slot1) {
	return slot1 > 0 ? slot1 - 1 : -1;
}

static void Append(std::string* out, const char* fmt, ...) {
	char    buf[1024];
	va_list args;
	va_start(args, fmt);
	const int len = std::vsnprintf(buf, sizeof(buf), fmt, args);
	va_end(args);
	if (len > 0) {
		out->append(buf, std::min<size_t>(static_cast<size_t>(len), sizeof(buf) - 1));
	}
}

static int32_t GidOf(const Report& r, const RowIndex& index, int32_t slot1) {
	if (slot1 > 0) {
		const auto p = index.Pos(slot1);
		return p >= 0 ? r.threads[static_cast<size_t>(p)].gid : 0;
	}
	if (!index.NonPositive()) {
		return 0;
	}
	for (const auto& t: r.threads) {
		if (t.slot1 == slot1) {
			return t.gid;
		}
	}
	return 0;
}

std::string Format(Report* report, Counters* counters) {
	auto& r = *report;
	MarkMandatory(&r);
	if (!r.gaps.i2_ok || !r.gaps.monotonic) {
		counters->sgap_bad++;
	}
	// -t: mandatory first (slot order), then the others by activity (R + r + W + H), cap kOthersCap.
	std::vector<const ThreadRow*> must;
	std::vector<const ThreadRow*> others;
	for (const auto& t: r.threads) {
		(t.must ? must : others).push_back(&t);
	}
	std::sort(must.begin(), must.end(), [](const ThreadRow* a, const ThreadRow* b) { return a->slot1 < b->slot1; });
	const auto act = [](const ThreadRow* t) {
		return t->agg.st[static_cast<size_t>(State::R)] + t->agg.st[static_cast<size_t>(State::Rr)] + t->agg.SumW() +
		       t->agg.SumH();
	};
	std::stable_sort(others.begin(), others.end(), [&](const ThreadRow* a, const ThreadRow* b) { return act(a) > act(b); });
	if (must.size() > kMustCap) {
		counters->lines_cut += must.size() - kMustCap;
		must.resize(kMustCap);
	}
	if (others.size() > kOthersCap) {
		counters->others_cut += others.size() - kOthersCap;
		others.resize(kOthersCap);
	}
	size_t     w_cut = 0;
	const auto picks = PickWaits(r, &w_cut);
	counters->w_cut += w_cut;
	std::vector<const CpuRow*> cpu;
	for (const auto& c: r.cpu) {
		cpu.push_back(&c);
	}
	std::sort(cpu.begin(), cpu.end(), [](const CpuRow* a, const CpuRow* b) { return a->cpu_us > b->cpu_us; });
	if (cpu.size() > kCLines) {
		cpu.resize(kCLines);
	}

	std::string out;
	out.reserve(16384);
	const auto n = static_cast<unsigned long long>(r.n);
	Append(&out,
	       "DiagB32: n=%llu dt_us=%llu instr_us=%llu samples=%u sgap_max_us=%llu gap3p=%u i2=%d kstate=%u kq=%u"
	       " kq_n=%u kq_us=%llu m5r_us=%llu"
	       " proc_us=%llu sys_busy_us=%llu sys_idle_us=%llu other_us=%lld ncpu=%u snap_ok=%u snap_lag_us=%llu"
	       " flip_slot=%d flip_tid=%d flip_src=%s lat_us=%llu vo_slot=%d gpu_slot=%d t_lines=%zu w_lines=%zu c_lines=%zu"
	       " cover_us=%llu flip_ns=%llu\n", // F25d (items 596(v) C4, 599(b)(11) C6): flip_ns - the FrameStats::NowNs scale, last
	       n, static_cast<unsigned long long>(r.dt_us), static_cast<unsigned long long>(r.instr_us), r.gaps.samples,
	       static_cast<unsigned long long>(r.gaps.sgap_max_ns / 1000u), r.gaps.gap3p, r.gaps.i2_ok && r.gaps.monotonic ? 1 : 0,
	       r.kstate, r.kq, r.kq_n, static_cast<unsigned long long>(r.kq_us), static_cast<unsigned long long>(r.m5r_us),
	       static_cast<unsigned long long>(r.proc_us), static_cast<unsigned long long>(r.sys_busy_us),
	       static_cast<unsigned long long>(r.sys_idle_us), static_cast<long long>(OtherUs(r.sys_busy_us, r.proc_us)), r.ncpu,
	       r.snap_ok, static_cast<unsigned long long>(r.snap_lag_us), SlotIndex(r.flip_slot1), r.flip_gid,
	       r.flip_src == 1 ? "cpu" : (r.flip_src == 2 ? "gpu" : "-"), static_cast<unsigned long long>(r.lat_us),
	       SlotIndex(r.vo_slot1), SlotIndex(r.gpu_slot1), must.size() + others.size(), picks.size(), cpu.size(),
	       static_cast<unsigned long long>(r.cover_us), static_cast<unsigned long long>(r.win_end_ns));
	const auto line_t = [&](const ThreadRow* t) {
		const auto& a   = t->agg;
		std::string top = "-";
		uint32_t    best = 0;
		for (size_t i = 1; i < static_cast<size_t>(Wait::Count); i++) {
			if (a.w[i] > best) {
				best = a.w[i];
				top  = std::string("W:") + WaitName(static_cast<uint8_t>(i));
			}
		}
		for (size_t i = 1; i < static_cast<size_t>(Call::Count); i++) {
			if (a.h[i] > best) {
				best = a.h[i];
				top  = std::string("H:") + CallName(static_cast<uint8_t>(i));
			}
		}
		std::string last = "-";
		if (t->last.mark != 0) {
			const bool h = (t->last.mark >> 8u) == static_cast<uint32_t>(State::H);
			last         = std::string(h ? "H:" : "W:") +
			       (h ? CallName(static_cast<uint8_t>(t->last.mark & 0xffu)) : WaitName(static_cast<uint8_t>(t->last.mark & 0xffu)));
		}
		const long long since_us = t->last.mark != 0 ? (static_cast<long long>(t->last.since) -
		                                                 static_cast<long long>(r.win_start_ns)) /
		                                                    1000
		                                              : 0;
		Append(&out,
		       "DiagB32-t: n=%llu slot=%d tid=%d os_tid=%u name=%s role=%s must=%d X=%u R=%u r=%u Sr=%u Sw=%u S=%u W=%s H=%s"
		       " SwR=%s cpu_us=%lld top=%s last=%s obj=0x%llx since_us=%lld peer=%d\n",
		       n, SlotIndex(t->slot1), t->gid, t->os_tid, t->name.c_str(), t->role.c_str(), t->must ? 1 : 0,
		       a.st[static_cast<size_t>(State::X)], a.st[static_cast<size_t>(State::R)], a.st[static_cast<size_t>(State::Rr)],
		       a.st[static_cast<size_t>(State::Sr)], a.SumSw(), a.st[static_cast<size_t>(State::S)],
		       KindList(a.w, static_cast<size_t>(Wait::Count), WaitName).c_str(),
		       KindList(a.h, static_cast<size_t>(Call::Count), CallName).c_str(), ReasonList(a.swr).c_str(),
		       static_cast<long long>(t->cpu_us), top.c_str(), last.c_str(), static_cast<unsigned long long>(t->last.obj),
		       since_us, SlotIndex(t->last.peer));
	};
	for (const auto* t: must) {
		line_t(t);
	}
	for (const auto* t: others) {
		line_t(t);
	}
	const RowIndex index(r); // F25d (item 599(b)(8))
	for (auto i: picks) {
		const auto& w = r.waits[i];
		// F20j3 (item 574(d)): the record's peer (slot) and its guest id at the end of the line.
		Append(&out,
		       "DiagB32-w: n=%llu slot=%d tid=%d kind=%s obj=0x%llx start_us=%lld wait_us=%llu overlap_us=%llu waker=%d"
		       " waker_tid=%d req_us=%llu to=%u open=%u peer=%d peer_tid=%d\n",
		       n, SlotIndex(w.slot1), GidOf(r, index, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),
		       (static_cast<long long>(w.start_ns) - static_cast<long long>(r.win_start_ns)) / 1000,
		       static_cast<unsigned long long>((w.end_ns - w.start_ns) / 1000u),
		       static_cast<unsigned long long>(Overlap(w, r.win_start_ns, r.win_end_ns) / 1000u), SlotIndex(w.waker1),
		       GidOf(r, index, w.waker1), static_cast<unsigned long long>(w.req_us), w.timed_out, w.open, SlotIndex(w.peer1),
		       GidOf(r, index, w.peer1));
	}
	for (const auto* c: cpu) {
		Append(&out, "DiagB32-c: n=%llu os_tid=%u slot=%d name=%s cpu_us=%llu\n", n, c->os_tid, SlotIndex(c->slot1),
		       c->name.c_str(), static_cast<unsigned long long>(c->cpu_us));
	}
	// F20j2 (item 552(v)(3), RC3 of F20k): every zero invariant cumulative and its increment over this window (_w).
	const auto& b  = counters->base;
	const auto  dw = [](uint64_t v, uint64_t base) { return static_cast<unsigned long long>(v >= base ? v - base : 0); };
	// F20j3 (item 554(v)(1), Z1): ring_hold / ring_hold_w at the end of the line. F25d (items 596(v), 599(b)(9)): then
	// hist_exh / hist_exh_w (C3), w_cut_w (C5v), others_cut_w (C5g) - others_cut_w is the last field.
	Append(&out,
	       "DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu torn=%llu torn_w=%llu ring_drop=%llu ring_drop_w=%llu"
	       " sgap_bad=%llu sgap_bad_w=%llu lines_cut=%llu lines_cut_w=%llu req_miss=%llu req_miss_w=%llu sub_miss=%llu"
	       " sub_miss_w=%llu short_stalls=%llu others_cut=%llu w_cut=%llu rep_drop=%llu kq_fail=%llu print_us=%llu gap3p=%u"
	       " ring_hold=%llu ring_hold_w=%llu hist_exh=%llu hist_exh_w=%llu w_cut_w=%llu others_cut_w=%llu\n",
	       n, static_cast<unsigned long long>(counters->slots), static_cast<unsigned long long>(counters->slot_full),
	       dw(counters->slot_full, b.slot_full), static_cast<unsigned long long>(counters->torn), dw(counters->torn, b.torn),
	       static_cast<unsigned long long>(counters->ring_drop), dw(counters->ring_drop, b.ring_drop),
	       static_cast<unsigned long long>(counters->sgap_bad), dw(counters->sgap_bad, b.sgap_bad),
	       static_cast<unsigned long long>(counters->lines_cut), dw(counters->lines_cut, b.lines_cut),
	       static_cast<unsigned long long>(counters->req_miss), dw(counters->req_miss, b.req_miss),
	       static_cast<unsigned long long>(counters->sub_miss), dw(counters->sub_miss, b.sub_miss),
	       static_cast<unsigned long long>(counters->short_stalls), static_cast<unsigned long long>(counters->others_cut),
	       static_cast<unsigned long long>(counters->w_cut), static_cast<unsigned long long>(counters->rep_drop),
	       static_cast<unsigned long long>(counters->kq_fail), static_cast<unsigned long long>(counters->print_us),
	       r.gaps.gap3p, static_cast<unsigned long long>(counters->ring_hold), dw(counters->ring_hold, b.ring_hold),
	       static_cast<unsigned long long>(counters->hist_exh), dw(counters->hist_exh, b.hist_exh),
	       dw(counters->w_cut, b.w_cut), dw(counters->others_cut, b.others_cut));
	return out;
}

void Counters::Rebase() {
	base.slot_full = slot_full;
	base.torn      = torn;
	base.ring_drop = ring_drop;
	base.sgap_bad  = sgap_bad;
	base.lines_cut = lines_cut;
	base.req_miss  = req_miss;
	base.sub_miss  = sub_miss;
	base.ring_hold = ring_hold;
	base.hist_exh  = hist_exh;   // F25d C3
	base.w_cut     = w_cut;      // F25d C5v
	base.others_cut = others_cut; // F25d C5g
}

std::string HeaderLine(uint32_t ncpu, uint32_t kstate, uint64_t kq_us) {
	char buf[320];
	std::snprintf(buf, sizeof(buf),
	              "DiagB32: mode=1 period_us=%llu print_us=%llu wait_rec_us=%llu kernel_after_us=%llu slots=%u hist=%u"
	              " wring=%u ncpu=%u kstate=%u kq_us=%llu kq_budget_div=%llu kq_near_us=%llu\n",
	              static_cast<unsigned long long>(kPeriodNs / 1000u), static_cast<unsigned long long>(kPrintNs / 1000u),
	              static_cast<unsigned long long>(kWaitRecNs / 1000u), static_cast<unsigned long long>(kKernelAfterNs / 1000u),
	              kSlots, kHist, kWaitRing, ncpu, kstate, static_cast<unsigned long long>(kq_us),
	              static_cast<unsigned long long>(kKqBudgetDiv), static_cast<unsigned long long>(kKqNearNs / 1000u));
	return buf;
}

// F20j3 (item 574(g)(4)): the refresher thread. A condition variable only to stop it (tests); the work runs unlocked.
struct AsyncRefresh::Impl {
	std::mutex              mutex;
	std::condition_variable cv;
	bool                    stop = false;
	std::thread             thread;
};

AsyncRefresh::~AsyncRefresh() {
	Stop();
}

void AsyncRefresh::Start(Fn work, void* user, uint64_t period_ns) {
	if (m_impl != nullptr) {
		return;
	}
	m_impl         = new Impl;
	auto* impl     = m_impl;
	impl->thread   = std::thread([this, impl, work, user, period_ns] {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
        using SetThreadDescriptionFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
        if (HMODULE k32 = GetModuleHandleW(L"kernel32.dll"); k32 != nullptr) {
            if (auto set_fn = reinterpret_cast<SetThreadDescriptionFn>(
                    reinterpret_cast<void*>(GetProcAddress(k32, "SetThreadDescription")));
                set_fn != nullptr) {
                set_fn(GetCurrentThread(), L"DiagB32M5"); // the refresh's CPU is visible in the -c lines
            }
        }
#endif
        for (;;) {
            const auto t0 = FrameStats::NowNs();
            m_cur_begin.store(t0, std::memory_order_release); // F20j4 (RC3 of F20k3): the run in progress
            work(user);
            const auto t1 = FrameStats::NowNs();
            m_work_ns.fetch_add(t1 - t0, std::memory_order_acq_rel);
            PushRun(t0, t1);
            m_cur_begin.store(0, std::memory_order_release);
            m_runs.fetch_add(1, std::memory_order_acq_rel);
            std::unique_lock lock(impl->mutex);
            if (impl->cv.wait_for(lock, std::chrono::nanoseconds(period_ns), [impl] { return impl->stop; })) {
                return;
            }
        }
    });
}

void AsyncRefresh::Stop() {
	if (m_impl == nullptr) {
		return;
	}
	{
		std::lock_guard lock(m_impl->mutex);
		m_impl->stop = true;
	}
	m_impl->cv.notify_all();
	if (m_impl->thread.joinable()) {
		m_impl->thread.join();
	}
	delete m_impl;
	m_impl = nullptr;
}

uint64_t AsyncRefresh::TakeWorkNs() {
	return m_work_ns.exchange(0, std::memory_order_acq_rel);
}

// F20j4 (item 581(v)(3), RC3 of F20k3): one writer (the refresher thread) - a per-entry sequence word, as WaitRing.
void AsyncRefresh::PushRun(uint64_t begin_ns, uint64_t end_ns) {
	const auto i = m_wpos.load(std::memory_order_relaxed);
	auto&      e = m_ring[i % kRuns];
	e.seq.store(2 * i + 1, std::memory_order_release);
	e.begin.store(begin_ns, std::memory_order_relaxed);
	e.end.store(end_ns, std::memory_order_relaxed);
	e.seq.store(2 * i + 2, std::memory_order_release);
	m_wpos.store(i + 1, std::memory_order_release);
}

void AsyncRefresh::TakeRuns(std::vector<Run>* out) {
	const auto w = m_wpos.load(std::memory_order_acquire);
	if (w - m_rpos > kRuns) {
		m_lost += w - m_rpos - kRuns;
		m_rpos = w - kRuns;
	}
	for (; m_rpos < w; m_rpos++) {
		auto&      e  = m_ring[m_rpos % kRuns];
		const auto s0 = e.seq.load(std::memory_order_acquire);
		Run        r;
		r.begin_ns = e.begin.load(std::memory_order_relaxed);
		r.end_ns   = e.end.load(std::memory_order_relaxed);
		std::atomic_thread_fence(std::memory_order_acquire);
		const auto s1 = e.seq.load(std::memory_order_relaxed);
		if (s0 != 2 * m_rpos + 2 || s1 != s0) {
			m_lost++; // overwritten by a later lap before or while it was read
			continue;
		}
		out->push_back(r);
	}
}

void M5Charge::Add(const std::vector<AsyncRefresh::Run>& runs, uint64_t cur_begin) {
	m_cur = cur_begin;
	for (const auto& r: runs) {
		if (cur_begin != 0 && r.begin_ns == cur_begin) {
			m_cur = 0; // the run seen in progress finished before the take - the same run
		}
		m_runs.push_back(r);
	}
}

uint64_t M5Charge::Window(uint64_t start, uint64_t end) const {
	uint64_t sum = 0;
	for (const auto& r: m_runs) {
		const auto b = std::max(r.begin_ns, start);
		const auto e = std::min(r.end_ns, end);
		sum += e > b ? e - b : 0;
	}
	if (m_cur != 0) {
		const auto b = std::max(m_cur, start);
		sum += end > b ? end - b : 0;
	}
	return sum;
}

void M5Charge::Prune(uint64_t from) {
	m_runs.erase(std::remove_if(m_runs.begin(), m_runs.end(), [from](const AsyncRefresh::Run& r) { return r.end_ns <= from; }),
	             m_runs.end());
}

} // namespace Core

// =====================================================================================================================
// Runtime
// =====================================================================================================================
namespace {

Core::Registry* g_reg  = nullptr; // allocated by Init only at KYTY_DIAG_B32=1
Core::WaitRing* g_ring = nullptr;

thread_local int32_t t_slot1 = 0; // 0 - not yet, -1 - the registry is full

// The last guest submission (GuestGpu::Enqueue) and the submission the GuestGpu thread processes now.
std::atomic<uint64_t> g_last_submit {0}; // PackSig of the submitter
std::atomic<uint64_t> g_cur_submit_seq {0};
struct SubmitEnt {
	std::atomic<uint64_t> seq {0};
	std::atomic<int32_t>  slot1 {0};
};
SubmitEnt g_submit[1024];

// Flip requests by request id (ReserveFlipRequest) and the flips published to the sampler (OnFlip).
struct ReqEnt {
	std::atomic<uint64_t> id {0};
	std::atomic<int32_t>  slot1 {0};
	std::atomic<uint32_t> src {0};
};
ReqEnt g_req[64];

struct FlipEnt {
	std::atomic<uint64_t> n {0};
	std::atomic<uint64_t> ns {0};
	std::atomic<uint64_t> lat_us {0};
	std::atomic<int32_t>  slot1 {0};
	std::atomic<uint32_t> src {0};
	std::atomic<uint64_t> print_ns {0}; // F20j2 RC6: the report print of the previous OnFlip - inside the window this flip closes
};
constexpr uint32_t    kFlipRing = 16;
FlipEnt               g_flip[kFlipRing];
std::atomic<uint64_t> g_flip_pub {0};
std::atomic<int32_t>  g_vo_slot1 {0};
std::atomic<int32_t>  g_gpu_slot1 {0};
// F20j3 (item 574(g)(2)): the slot + 1 of every peer role (RegisterRole).
std::atomic<int32_t>  g_peer_slot1[static_cast<size_t>(Peer::Count)] {};

// F20j3 (item 574(g)(1)): the last signaller side table (std::condition_variable waits). The word: PackSig with the
// 12-bit tag of the object's address in bits 52..63 (the time field (NowNs >> 10) stays below 2^36 for 19 hours of
// process time and bits 52..63 of PackSig are zero; a longer run only loses the tag check - the waker is then unknown
// to the reading at most once per 2^12 objects [I]).
constexpr uint32_t    kSigTab = 4096;
std::atomic<uint64_t> g_sigtab[kSigTab] {};

uint32_t SigBucket(const void* obj) {
	const auto a = reinterpret_cast<uintptr_t>(obj);
	return static_cast<uint32_t>(((a >> 4u) ^ (a >> 16u)) % kSigTab);
}

uint64_t SigTag(const void* obj) {
	const auto a = reinterpret_cast<uintptr_t>(obj);
	return static_cast<uint64_t>(((a >> 3u) ^ (a >> 15u) ^ (a >> 27u)) & 0xfffu);
}

// Reports: the sampler formats, the present thread prints at its next flip site.
struct RepSlot {
	std::atomic<uint32_t> state {0}; // 0 free, 1 ready
	uint64_t              n = 0;
	std::string           text;
};
RepSlot               g_rep[4];
std::atomic<uint64_t> g_print_us {0};
uint64_t              g_print_prev_ns = 0; // present thread only (OnFlip): the print time of its previous call (F20j2 RC6)
std::atomic<uint64_t> g_req_miss {0};      // F20j2 RC7: OnFlip found the request entry overwritten
std::atomic<uint64_t> g_sub_miss {0};      // F20j2 RC7: NoteFlipRequest found the submission entry overwritten
std::atomic<uint64_t> g_kq_first_us {0};   // F20j2 (item 552(v)(1)): the cost of the first kernel query (start probe)

uint32_t              g_ncpu = 0;
std::atomic<uint32_t> g_kstate {0};
std::atomic<bool>     g_sampler_ready {false};

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
HANDLE g_flip_event = nullptr;
#endif

const char* RoleName() {
	switch (FrameStats::CurrentRole()) {
		case FrameStats::ThreadRole::Main: return "Main";
		case FrameStats::ThreadRole::Gpu: return "Gpu";
		case FrameStats::ThreadRole::Present: return "Present";
		case FrameStats::ThreadRole::Record: return "Record";
		default: return "emu";
	}
}

int32_t RegisterSelf(const char* role, const char* name, int32_t gid) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	const auto tid    = static_cast<uint32_t>(GetCurrentThreadId());
	HANDLE     handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, tid);
	const auto idx    = g_reg->Allocate(tid, handle, role, name, gid);
	if (idx < 0 && handle != nullptr) {
		CloseHandle(handle);
	}
	t_slot1 = idx >= 0 ? idx + 1 : -1;
	return t_slot1 > 0 ? t_slot1 : 0;
#else
	(void)role;
	(void)name;
	(void)gid;
	t_slot1 = -1;
	return 0;
#endif
}

} // namespace

int32_t SelfSlot() {
	if (t_slot1 != 0) {
		return t_slot1 > 0 ? t_slot1 : 0;
	}
	if (g_reg == nullptr) {
		return 0;
	}
	return RegisterSelf(RoleName(), nullptr, 0);
}

void RegisterRole(const char* role) {
	if (g_reg == nullptr) {
		return;
	}
	int32_t slot1 = t_slot1 > 0 ? t_slot1 : 0;
	if (t_slot1 == 0) {
		slot1 = RegisterSelf(role, role, 0);
	}
	if (slot1 > 0) {
		auto& s = g_reg->slots[slot1 - 1];
		std::snprintf(s.role, sizeof(s.role), "%s", role);
		if (std::strcmp(role, "Present") == 0) {
			g_vo_slot1.store(slot1, std::memory_order_release);
		} else if (std::strcmp(role, "Gpu") == 0) {
			g_gpu_slot1.store(slot1, std::memory_order_release);
		}
		// F20j3 (item 574(g)(2)): the peer roles.
		static constexpr const char* peers[] = {"Present", "Gpu", "ASubmit", "POps", "Relay", "Main", "Record"};
		static_assert(sizeof(peers) / sizeof(peers[0]) == static_cast<size_t>(Peer::Count));
		for (size_t i = 0; i < sizeof(peers) / sizeof(peers[0]); i++) {
			if (std::strcmp(role, peers[i]) == 0) {
				g_peer_slot1[i].store(slot1, std::memory_order_release);
			}
		}
	}
}

int32_t PeerSlot(Peer peer) {
	const auto i = static_cast<size_t>(peer);
	return i < static_cast<size_t>(Peer::Count) ? g_peer_slot1[i].load(std::memory_order_acquire) : 0;
}

int32_t SelfSlotIfRegistered() {
	return t_slot1 > 0 ? t_slot1 : 0;
}

int32_t SlotOfOsTid(uint32_t os_tid) {
	if (g_reg == nullptr || os_tid == 0) {
		return 0;
	}
	const auto n = std::min<uint32_t>(g_reg->count.load(std::memory_order_acquire), kSlots);
	for (uint32_t i = 0; i < n; i++) {
		const auto& s = g_reg->slots[i];
		if (s.live.load(std::memory_order_acquire) == 1 && s.os_tid == os_tid) {
			return static_cast<int32_t>(i) + 1;
		}
	}
	return 0;
}

int32_t RegisterGuest(int32_t gid, const char* name) {
	if (g_reg == nullptr) {
		return 0;
	}
	int32_t slot1 = t_slot1 > 0 ? t_slot1 : 0;
	if (t_slot1 == 0) {
		slot1 = RegisterSelf("guest", name, gid);
	}
	if (slot1 > 0) {
		auto& s = g_reg->slots[slot1 - 1];
		std::snprintf(s.name, sizeof(s.name), "%s", name != nullptr ? name : "guest");
		s.gid.store(gid, std::memory_order_release);
	}
	return slot1;
}

void Unregister() {
	if (g_reg != nullptr && t_slot1 > 0) {
		g_reg->slots[t_slot1 - 1].live.store(2, std::memory_order_release);
	}
}

uint64_t PackSig() {
	const auto slot1 = SelfSlot();
	return ((FrameStats::NowNs() >> 10u) << 16u) | (static_cast<uint64_t>(slot1) & 0xffffu);
}

uint64_t PackSigIfRegistered() {
	return ((FrameStats::NowNs() >> 10u) << 16u) | (static_cast<uint64_t>(SelfSlotIfRegistered()) & 0xffffu);
}

void NoteSignalSlow(const void* obj) {
	g_sigtab[SigBucket(obj)].store((PackSigIfRegistered() & ((uint64_t {1} << 52u) - 1u)) | (SigTag(obj) << 52u),
	                               std::memory_order_relaxed);
}

uint64_t SignalOf(const void* obj) {
	const auto v = g_sigtab[SigBucket(obj)].load(std::memory_order_relaxed);
	if (v == 0 || (v >> 52u) != SigTag(obj)) {
		return 0;
	}
	return v & ((uint64_t {1} << 52u) - 1u);
}

int32_t SigWaker(uint64_t packed, uint64_t since_ns) {
	if (packed == 0) {
		return 0;
	}
	const auto t = (packed >> 16u) << 10u;
	if (t + 1024u < since_ns) {
		return 0;
	}
	return static_cast<int32_t>(packed & 0xffffu);
}

void Mark::BeginH(Call call) {
	const auto slot1 = SelfSlot();
	if (slot1 <= 0) {
		return;
	}
	auto& s      = g_reg->slots[slot1 - 1];
	m_slot       = slot1 - 1;
	m_prev_mark  = s.mark.load(std::memory_order_relaxed);
	m_prev_obj   = s.obj.load(std::memory_order_relaxed);
	m_prev_since = s.since.load(std::memory_order_relaxed);
	m_prev_peer  = s.peer.load(std::memory_order_relaxed);
	m_mark       = Core::MarkWord(State::H, static_cast<uint8_t>(call));
	m_obj        = 0;
	m_since      = FrameStats::NowNs();
	m_peer       = 0;
	m_req_us     = 0;
	g_reg->WriteMark(m_slot, m_mark, 0, m_since, 0);
	m_active = true;
}

void Mark::BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {
	const auto slot1 = SelfSlot();
	if (slot1 <= 0) {
		return;
	}
	auto& s      = g_reg->slots[slot1 - 1];
	m_slot       = slot1 - 1;
	m_prev_mark  = s.mark.load(std::memory_order_relaxed);
	m_prev_obj   = s.obj.load(std::memory_order_relaxed);
	m_prev_since = s.since.load(std::memory_order_relaxed);
	m_prev_peer  = s.peer.load(std::memory_order_relaxed);
	m_mark       = Core::MarkWord(State::W, static_cast<uint8_t>(kind));
	m_obj        = reinterpret_cast<uint64_t>(obj);
	m_since      = FrameStats::NowNs();
	m_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself
	m_req_us     = req_us;
	g_reg->WriteMark(m_slot, m_mark, m_obj, m_since, m_peer);
	m_active = true;
}

void Mark::BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {
	const auto slot1 = SelfSlotIfRegistered();
	if (slot1 <= 0 || g_reg == nullptr) {
		return;
	}
	auto& s      = g_reg->slots[slot1 - 1];
	m_slot       = slot1 - 1;
	m_prev_mark  = s.mark.load(std::memory_order_relaxed);
	m_prev_obj   = s.obj.load(std::memory_order_relaxed);
	m_prev_since = s.since.load(std::memory_order_relaxed);
	m_prev_peer  = s.peer.load(std::memory_order_relaxed);
	m_mark       = Core::MarkWord(State::W, static_cast<uint8_t>(kind));
	m_obj        = reinterpret_cast<uint64_t>(obj);
	m_since      = FrameStats::NowNs();
	m_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself
	m_req_us     = req_us;
	g_reg->WriteMark(m_slot, m_mark, m_obj, m_since, m_peer);
	m_active = true;
}

// F20j4 (item 581(v)(4), RC4 of F20k3): the slot's mark is written only by this thread - the load is exact.
void Mark::BeginWLock(Wait kind, const void* obj, int32_t peer_slot1) {
	const auto slot1 = SelfSlotIfRegistered();
	if (slot1 <= 0 || g_reg == nullptr) {
		return;
	}
	if ((g_reg->slots[slot1 - 1].mark.load(std::memory_order_relaxed) >> 8u) == static_cast<uint32_t>(State::H)) {
		return;
	}
	BeginWReg(kind, obj, peer_slot1, 0);
}

void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {
	if (!m_active) {
		return;
	}
	m_active = false;
	g_reg->WriteMark(m_slot, m_prev_mark, m_prev_obj, m_prev_since, m_prev_peer);
	if ((m_mark >> 8u) != static_cast<uint32_t>(State::W)) {
		return;
	}
	const auto now = FrameStats::NowNs();
	if (now < m_since || now - m_since < kWaitRecNs) {
		return;
	}
	Core::WaitRec rec;
	rec.start_ns  = m_since;
	rec.end_ns    = now;
	rec.obj       = m_obj;
	rec.req_us    = m_req_us;
	rec.slot1     = m_slot + 1;
	rec.waker1    = waker_slot1;
	rec.peer1     = m_peer; // F20j3 (item 574(g)(2))
	rec.kind      = static_cast<uint8_t>(m_mark & 0xffu);
	rec.timed_out = timed_out ? 1 : 0;
	g_ring->Push(rec);
}

void NoteSubmit(uint64_t seq) {
	const auto packed = PackSig();
	g_last_submit.store(packed, std::memory_order_relaxed);
	auto& e = g_submit[seq % 1024];
	e.slot1.store(static_cast<int32_t>(packed & 0xffffu), std::memory_order_relaxed);
	e.seq.store(seq, std::memory_order_release);
}

void NoteCurrentSubmission(uint64_t seq) {
	g_cur_submit_seq.store(seq, std::memory_order_release);
}

int32_t LastSubmitWaker(uint64_t since_ns) {
	return SigWaker(g_last_submit.load(std::memory_order_relaxed), since_ns);
}

void NoteFlipRequest(uint64_t request_id, bool cpu_source) {
	int32_t slot1 = 0;
	if (cpu_source) {
		slot1 = SelfSlot();
	} else {
		const auto seq = g_cur_submit_seq.load(std::memory_order_acquire);
		auto&      e   = g_submit[seq % 1024];
		if (e.seq.load(std::memory_order_acquire) == seq) {
			slot1 = e.slot1.load(std::memory_order_relaxed);
		} else {
			g_sub_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten
		}
	}
	auto& r = g_req[request_id % 64];
	r.slot1.store(slot1, std::memory_order_relaxed);
	r.src.store(cpu_source ? 1u : 2u, std::memory_order_relaxed);
	r.id.store(request_id, std::memory_order_release);
}

void OnFlip(uint64_t n, uint64_t request_id, uint64_t reserve_host_ns) {
	const auto now   = FrameStats::NowNs();
	int32_t    slot1 = 0;
	uint32_t   src   = 0;
	auto&      r     = g_req[request_id % 64];
	if (r.id.load(std::memory_order_acquire) == request_id) {
		slot1 = r.slot1.load(std::memory_order_relaxed);
		src   = r.src.load(std::memory_order_relaxed);
	} else {
		g_req_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten
	}
	const auto k = g_flip_pub.load(std::memory_order_relaxed);
	auto&      e = g_flip[k % kFlipRing];
	e.n.store(n, std::memory_order_relaxed);
	e.ns.store(now, std::memory_order_relaxed);
	e.lat_us.store(reserve_host_ns != 0 && now > reserve_host_ns ? (now - reserve_host_ns) / 1000u : 0,
	               std::memory_order_relaxed);
	e.slot1.store(slot1, std::memory_order_relaxed);
	e.src.store(src, std::memory_order_relaxed);
	e.print_ns.store(g_print_prev_ns, std::memory_order_relaxed);
	g_flip_pub.store(k + 1, std::memory_order_release);
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	SetEvent(g_flip_event);
#endif
	// Print the reports the sampler has closed (each one once, in the order of n). F20j2 RC6: this runs under
	// FlipQueue::m_mutex and VideoOutConfig::mutex (videoOut.cpp); the whole print time of this call lies after this
	// flip, so it is published with the next flip and added to instr_us of the window that flip closes.
	uint64_t print_ns = 0;
	for (;;) {
		RepSlot* best = nullptr;
		for (auto& slot: g_rep) {
			if (slot.state.load(std::memory_order_acquire) == 1 && (best == nullptr || slot.n < best->n)) {
				best = &slot;
			}
		}
		if (best == nullptr) {
			break;
		}
		const auto t0 = FrameStats::NowNs();
		if (!::Log::IsSilent()) {
			::Log::Write(best->text);
		}
		best->state.store(0, std::memory_order_release);
		const auto took = FrameStats::NowNs() - t0;
		print_ns += took;
		g_print_us.store(took / 1000u, std::memory_order_relaxed);
	}
	g_print_prev_ns = print_ns;
}

// ---- stand ----
void TestArm() {
	if (!g_test_on || g_test_armed.exchange(true, std::memory_order_acq_rel)) {
		return;
	}
	const auto now = FrameStats::NowNs();
	g_test_fire_ns.store(now + static_cast<uint64_t>(g_test_delay_s * 1e9), std::memory_order_release);
	LOGF("TestB32: armed t_ms=%llu fire_after_s=%.3f mode=%s ms=%u\n", static_cast<unsigned long long>(now / 1000000u),
	     g_test_delay_s, g_test_present ? "present" : "gpusleep", g_test_ms);
}

static void TestSleepNow(const char* mode) {
	const auto fire = g_test_fire_ns.load(std::memory_order_acquire);
	if (fire == 0 || g_test_done.load(std::memory_order_relaxed) || FrameStats::NowNs() < fire ||
	    g_test_done.exchange(true, std::memory_order_acq_rel)) {
		return;
	}
	LOGF("TestB32: fire mode=%s ms=%u\n", mode, g_test_ms);
	const auto t0 = FrameStats::NowNs();
	std::this_thread::sleep_for(std::chrono::milliseconds(g_test_ms));
	LOGF("TestB32: done mode=%s slept_us=%llu\n", mode, static_cast<unsigned long long>((FrameStats::NowNs() - t0) / 1000u));
}

void TestPresentPoint() {
	if (g_test_present) {
		TestSleepNow("present");
	}
}

void TestGpuSleepPoint() {
	if (g_test_gpusleep) {
		TestSleepNow("gpusleep");
	}
}

// ---- sampler ----
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
namespace {

using NtQuerySystemInformationFn = LONG(NTAPI*)(ULONG, PVOID, ULONG, PULONG);
using GetThreadDescriptionFn     = HRESULT(WINAPI*)(HANDLE, PWSTR*);

// SYSTEM_PROCESS_INFORMATION / SYSTEM_THREAD_INFORMATION (x64 layout, documented offsets: UniqueProcessId 0x50,
// the thread array right after the 0x100-byte process record, 0x50 bytes per thread).
struct SysThread {
	LARGE_INTEGER KernelTime;
	LARGE_INTEGER UserTime;
	LARGE_INTEGER CreateTime;
	ULONG         WaitTime;
	PVOID         StartAddress;
	HANDLE        UniqueProcess;
	HANDLE        UniqueThread;
	LONG          Priority;
	LONG          BasePriority;
	ULONG         ContextSwitches;
	ULONG         ThreadState;
	ULONG         WaitReason;
};
static_assert(sizeof(SysThread) == 0x50);

struct SysProcess {
	ULONG  NextEntryOffset;
	ULONG  NumberOfThreads;
	BYTE   Reserved1[48];
	USHORT NameLength;
	USHORT NameMaximumLength;
	PWSTR  NameBuffer;
	LONG   BasePriority;
	HANDLE UniqueProcessId;
	BYTE   Rest[0x100 - 0x58];
};
static_assert(sizeof(SysProcess) == 0x100);
static_assert(offsetof(SysProcess, UniqueProcessId) == 0x50);

struct M5Ent {
	uint32_t    os_tid  = 0;
	HANDLE      handle  = nullptr;
	std::string name;
	uint64_t    cyc     = 0;
	bool        have    = false;
	uint64_t    last_ns = 0;
	bool        valid   = false;
	bool        seen    = false;
};

// F20j3 (item 574(g)(4)): the thread list built by the refresher thread (CreateToolhelp32Snapshot, OpenThread, names).
// It owns the handles: a vanished thread's handle goes to the graveyard with the generation of the list that dropped
// it and is closed once the sampler adopted a later generation (the sampler uses only handles of the list it adopted).
struct M5Pub {
	uint32_t    os_tid = 0;
	HANDLE      handle = nullptr;
	std::string name;
};

struct M5Shared {
	std::mutex                                  mutex;    // the published list (the sampler only try_locks it)
	std::vector<M5Pub>                          pub;
	uint64_t                                    pub_gen = 0;
	std::atomic<uint64_t>                       adopted {0}; // the generation the sampler uses
	// refresher thread only:
	std::vector<M5Pub>                          own;
	std::vector<std::pair<uint64_t, HANDLE>>    graveyard;
	uint64_t                                    gen = 0;
	uint32_t                                    pid = 0;
	GetThreadDescriptionFn                      gtd = nullptr;
};

class Sampler {
public:
	void Run();

	friend Test::BenchOut Test::CloseWindowBench(const Test::BenchIn& in); // F25d (item 599(b)(8))

private:
	void     Sample(uint64_t begin);
	void     ProcessFlips();
	void     KernelQuery();
	bool     KernelLookup(uint32_t tid, uint32_t* state, uint32_t* reason) const;
	static void M5RefreshWork(void* user); // F20j3: runs on the refresher thread (Core::AsyncRefresh)
	void     M5Adopt();                     // F20j3: the sampler takes the last published list (try_lock only)
	void     M5Snapshot();
	void     M1Snapshot(uint64_t* proc_us, uint64_t* busy_us, uint64_t* idle_us);
	void     CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
	                     uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us, uint64_t print_ns);
	void     RefreshCounters();
	[[nodiscard]] uint64_t CyclesToNs(uint64_t cycles) const {
		return m_cpn > 0.0 ? static_cast<uint64_t>(static_cast<double>(cycles) / m_cpn) : 0;
	}

	double                    m_cpn = 0.0;
	std::vector<uint16_t>     m_codes = std::vector<uint16_t>(static_cast<size_t>(kSlots) * kHist, 0);
	uint64_t                  m_t[kHist] {};
	uint64_t                  m_cost[kHist] {};
	uint8_t                   m_kq[kHist] {};
	uint64_t                  m_kqt[kHist] {};  // F20j2 RC2: the kernel snapshot time of the sample (own field)
	uint64_t                  m_kqc[kHist] {};  // F20j2 RC1: the kernel-query time of the sample (0 - no query)
	// F20j2 (item 552(v)(1)): per slot, the kernel-only class (Sr / Sw:<reason> / S) at the samples with a snapshot.
	std::vector<uint16_t>     m_kcodes = std::vector<uint16_t>(static_cast<size_t>(kSlots) * kHist, 0);
	Core::KqSchedule          m_sched;
	Core::M5Charge            m_m5c;          // F20j4 (item 581(v)(3), RC3 of F20k3)
	std::vector<Core::AsyncRefresh::Run> m_m5_runs;
	uint64_t                  m_hpos   = 0;
	uint64_t                  m_last_t = 0;
	uint64_t                  m_prev_cyc[kSlots] {};
	bool                      m_have_cyc[kSlots] {};
	Core::MarkSnap            m_last_mark[kSlots] {};
	uint64_t                  m_last_mark_pos[kSlots] {};
	uint64_t                  m_seen_flips    = 0;
	uint64_t                  m_win_start     = 0;
	uint64_t                  m_win_extra_ns  = 0;
	bool                      m_kq_ok         = false;
	NtQuerySystemInformationFn m_ntq          = nullptr;
	GetThreadDescriptionFn    m_gtd           = nullptr;
	std::vector<uint8_t>      m_kbuf          = std::vector<uint8_t>(static_cast<size_t>(2) << 20u);
	std::vector<std::pair<uint32_t, uint64_t>> m_kmap;
	std::vector<M5Ent>        m_m5;
	M5Shared                  m_m5s;          // F20j3 (item 574(g)(4))
	Core::AsyncRefresh        m_m5r;
	uint64_t                  m_m5_gen = 0;   // the generation of m_m5
	uint64_t                  m_ring_hold = 0; // F20j3 (Z1)
	uint64_t                  m_m1_proc = 0;
	uint64_t                  m_m1_kernel = 0;
	uint64_t                  m_m1_user = 0;
	uint64_t                  m_m1_idle = 0;
	bool                      m_m1_have = false;
	std::vector<Core::WaitRec> m_recent;
	std::vector<Core::WaitRec> m_ring_tmp;
	uint64_t                  m_ring_torn = 0;
	Core::Counters            m_c;
	uint32_t                  m_pid = 0;
};

uint64_t FileTime(const FILETIME& t) {
	return (static_cast<uint64_t>(t.dwHighDateTime) << 32u) | t.dwLowDateTime;
}

void Sampler::KernelQuery() {
	m_kmap.clear();
	if (m_ntq == nullptr) {
		return;
	}
	ULONG need   = 0;
	LONG  status = m_ntq(5 /* SystemProcessInformation */, m_kbuf.data(), static_cast<ULONG>(m_kbuf.size()), &need);
	if (status == static_cast<LONG>(0xC0000004L) /* STATUS_INFO_LENGTH_MISMATCH */) {
		m_kbuf.resize(static_cast<size_t>(need) + (static_cast<size_t>(256) << 10u));
		status = m_ntq(5, m_kbuf.data(), static_cast<ULONG>(m_kbuf.size()), &need);
	}
	if (status < 0) {
		m_c.kq_fail++;
		return;
	}
	size_t off = 0;
	for (;;) {
		if (off + sizeof(SysProcess) > m_kbuf.size()) {
			break;
		}
		const auto* p = reinterpret_cast<const SysProcess*>(m_kbuf.data() + off);
		if (static_cast<uint32_t>(reinterpret_cast<uintptr_t>(p->UniqueProcessId)) == m_pid) {
			const auto* th = reinterpret_cast<const SysThread*>(p + 1);
			for (ULONG i = 0; i < p->NumberOfThreads; i++) {
				if (reinterpret_cast<const uint8_t*>(th + i + 1) > m_kbuf.data() + m_kbuf.size()) {
					break;
				}
				m_kmap.emplace_back(static_cast<uint32_t>(reinterpret_cast<uintptr_t>(th[i].UniqueThread)),
				                    static_cast<uint64_t>(th[i].ThreadState) | (static_cast<uint64_t>(th[i].WaitReason) << 32u));
			}
			std::sort(m_kmap.begin(), m_kmap.end());
			return;
		}
		if (p->NextEntryOffset == 0) {
			break;
		}
		off += p->NextEntryOffset;
	}
	m_c.kq_fail++;
}

bool Sampler::KernelLookup(uint32_t tid, uint32_t* state, uint32_t* reason) const {
	const auto it = std::lower_bound(m_kmap.begin(), m_kmap.end(), std::make_pair(tid, uint64_t {0}));
	if (it == m_kmap.end() || it->first != tid) {
		return false;
	}
	*state  = static_cast<uint32_t>(it->second & 0xffffffffu);
	*reason = static_cast<uint32_t>(it->second >> 32u);
	return true;
}

void Sampler::Sample(uint64_t begin) {
	// F20j2 (item 552(v)(1), RC1 of F20k): the kernel query only by the schedule (>= 40 ms and <= 10 % of the window).
	bool     kq    = false;
	uint64_t kq_ns = 0;
	uint64_t kq_t  = 0;
	if (m_kq_ok && m_sched.Due(begin)) {
		KernelQuery();
		const auto q1 = FrameStats::NowNs();
		kq_ns         = q1 > begin ? q1 - begin : 0;
		kq_t          = begin + kq_ns / 2; // the snapshot moment lies inside the call [I]: its middle
		kq            = !m_kmap.empty();
		m_sched.Done(kq_ns);
	}
	// F20j2 (item 552(v)(2), RC2 of F20k): the sample time is the moment the slots are read - after the kernel query;
	// the interval for R is between such moments.
	const uint64_t t0       = FrameStats::NowNs();
	const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;
	const auto     n        = std::min<uint32_t>(g_reg->count.load(std::memory_order_acquire), kSlots);
	const auto pos = static_cast<size_t>(m_hpos % kHist);
	for (uint32_t i = 0; i < n; i++) {
		auto&    s    = g_reg->slots[i];
		uint16_t code = Core::Code(State::X, 0);
		if (s.live.load(std::memory_order_acquire) == 1 && s.handle != nullptr) {
			Core::MarkSnap ms;
			if (!g_reg->ReadMark(static_cast<int32_t>(i), &ms)) {
				ms = Core::MarkSnap {};
			}
			ULONG64  cyc    = 0;
			uint64_t cpu_ns = 0;
			if (QueryThreadCycleTime(static_cast<HANDLE>(s.handle), &cyc) != 0) {
				if (m_have_cyc[i] && cyc >= m_prev_cyc[i]) {
					cpu_ns = CyclesToNs(cyc - m_prev_cyc[i]);
				}
				m_prev_cyc[i] = cyc;
				m_have_cyc[i] = true;
			}
			uint32_t ks = 0;
			uint32_t kr = 0;
			const bool known = kq && KernelLookup(s.os_tid, &ks, &kr);
			code             = Core::Classify(ms.mark, cpu_ns, interval, known, ks, kr);
			if (known) {
				m_kcodes[static_cast<size_t>(i) * kHist + pos] = Core::Classify(0, 0, interval, true, ks, kr);
			} else if (kq) {
				m_kcodes[static_cast<size_t>(i) * kHist + pos] = Core::Code(State::S, 0);
			}
			if (ms.mark != 0) {
				m_last_mark[i]     = ms;
				m_last_mark_pos[i] = m_hpos;
			}
		} else if (kq) {
			m_kcodes[static_cast<size_t>(i) * kHist + pos] = Core::Code(State::S, 0);
		}
		m_codes[static_cast<size_t>(i) * kHist + pos] = code;
	}
	m_t[pos]    = t0;
	m_kq[pos]   = kq ? 1 : 0;
	m_kqt[pos]  = kq_t;
	m_kqc[pos]  = kq_ns;
	m_last_t    = t0;
	m_cost[pos] = FrameStats::NowNs() - begin; // RC9: the whole sample, the kernel query included
	m_hpos++;
}

// F20j3 (item 574(g)(4)): was Sampler::M5Refresh on the sampler thread (76.7 ms in b32_pp frame 1798 = the gap of
// samples, item 574(a)(6)); now the same enumeration on the refresher thread, published for M5Adopt.
void Sampler::M5RefreshWork(void* user) {
	auto&  m    = *static_cast<M5Shared*>(user);
	HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
	if (snap == INVALID_HANDLE_VALUE) {
		return;
	}
	std::vector<uint32_t> seen;
	THREADENTRY32         te {};
	te.dwSize = sizeof(te);
	for (BOOL ok = Thread32First(snap, &te); ok != FALSE; ok = Thread32Next(snap, &te)) {
		if (te.th32OwnerProcessID != m.pid) {
			continue;
		}
		seen.push_back(te.th32ThreadID);
		auto it = std::find_if(m.own.begin(), m.own.end(), [&](const M5Pub& e) { return e.os_tid == te.th32ThreadID; });
		if (it != m.own.end()) {
			continue;
		}
		M5Pub e;
		e.os_tid = te.th32ThreadID;
		e.handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, te.th32ThreadID);
		if (e.handle == nullptr) {
			continue;
		}
		if (m.gtd != nullptr) {
			PWSTR desc = nullptr;
			if (SUCCEEDED(m.gtd(e.handle, &desc)) && desc != nullptr) {
				char buf[64] {};
				for (size_t i = 0; desc[i] != 0 && i + 1 < sizeof(buf); i++) {
					buf[i] = desc[i] < 128 ? static_cast<char>(desc[i]) : '_';
				}
				e.name = Core::SafeName(buf);
				LocalFree(desc);
			}
		}
		if (e.name.empty() || e.name == "-") {
			e.name = "t" + std::to_string(e.os_tid);
		}
		m.own.push_back(std::move(e));
	}
	CloseHandle(snap);
	m.gen++;
	for (auto& e: m.own) {
		if (std::find(seen.begin(), seen.end(), e.os_tid) == seen.end()) {
			m.graveyard.emplace_back(m.gen, e.handle); // the sampler may still use it until it adopts gen
			e.handle = nullptr;
		}
	}
	m.own.erase(std::remove_if(m.own.begin(), m.own.end(), [](const M5Pub& e) { return e.handle == nullptr; }), m.own.end());
	{
		std::lock_guard lock(m.mutex);
		m.pub     = m.own;
		m.pub_gen = m.gen;
	}
	const auto adopted = m.adopted.load(std::memory_order_acquire);
	m.graveyard.erase(std::remove_if(m.graveyard.begin(), m.graveyard.end(),
	                                 [&](const std::pair<uint64_t, HANDLE>& g) {
		                                 if (g.first <= adopted) {
			                                 CloseHandle(g.second);
			                                 return true;
		                                 }
		                                 return false;
	                                 }),
	                  m.graveyard.end());
}

void Sampler::M5Adopt() {
	std::unique_lock lock(m_m5s.mutex, std::try_to_lock);
	if (!lock.owns_lock() || m_m5s.pub_gen == m_m5_gen) {
		return;
	}
	std::vector<M5Ent> next;
	next.reserve(m_m5s.pub.size());
	for (const auto& p: m_m5s.pub) {
		M5Ent e;
		e.os_tid = p.os_tid;
		e.handle = p.handle;
		e.name   = p.name;
		auto it  = std::find_if(m_m5.begin(), m_m5.end(), [&](const M5Ent& o) { return o.os_tid == p.os_tid; });
		if (it != m_m5.end()) { // the cycle state continues
			e.cyc     = it->cyc;
			e.have    = it->have;
			e.last_ns = it->last_ns;
			e.valid   = it->valid;
		}
		next.push_back(std::move(e));
	}
	m_m5_gen = m_m5s.pub_gen;
	lock.unlock();
	m_m5 = std::move(next);
	m_m5s.adopted.store(m_m5_gen, std::memory_order_release);
}

void Sampler::M5Snapshot() {
	for (auto& e: m_m5) {
		ULONG64 cyc = 0;
		e.valid     = false;
		if (QueryThreadCycleTime(e.handle, &cyc) == 0) {
			continue;
		}
		if (e.have && cyc >= e.cyc) {
			e.last_ns = CyclesToNs(cyc - e.cyc);
			e.valid   = true;
		}
		e.cyc  = cyc;
		e.have = true;
	}
}

void Sampler::M1Snapshot(uint64_t* proc_us, uint64_t* busy_us, uint64_t* idle_us) {
	FILETIME idle {};
	FILETIME kernel {};
	FILETIME user {};
	FILETIME creation {};
	FILETIME exit {};
	FILETIME pk {};
	FILETIME pu {};
	*proc_us = *busy_us = *idle_us = 0;
	if (GetSystemTimes(&idle, &kernel, &user) == 0 ||
	    GetProcessTimes(GetCurrentProcess(), &creation, &exit, &pk, &pu) == 0) {
		return;
	}
	const auto i = FileTime(idle);
	const auto k = FileTime(kernel);
	const auto u = FileTime(user);
	const auto p = FileTime(pk) + FileTime(pu);
	if (m_m1_have) {
		const auto di = i - m_m1_idle;
		const auto dk = k - m_m1_kernel; // includes idle
		const auto du = u - m_m1_user;
		*idle_us      = di / 10u;
		*busy_us      = (dk + du > di ? dk + du - di : 0) / 10u;
		*proc_us      = (p - m_m1_proc) / 10u;
	}
	m_m1_idle   = i;
	m_m1_kernel = k;
	m_m1_user   = u;
	m_m1_proc   = p;
	m_m1_have   = true;
}

void Sampler::RefreshCounters() {
	m_c.slot_full = g_reg->slot_full.load(std::memory_order_relaxed);
	m_c.torn      = g_reg->torn.load(std::memory_order_relaxed) + m_ring_torn;
	m_c.req_miss  = g_req_miss.load(std::memory_order_relaxed);
	m_c.sub_miss  = g_sub_miss.load(std::memory_order_relaxed);
	m_c.ring_hold = m_ring_hold; // F20j3 (Z1)
}

void Sampler::CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
                          uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us, uint64_t print_ns) {
	const uint64_t start = m_win_start;
	// F20j4 (item 581(v)(3), RC3 of F20k3): the M5 refresh time inside (start, flip_ns] - this window's own (RC9).
	const uint64_t m5r   = m_m5c.Window(start, flip_ns);
	const uint64_t extra = m_win_extra_ns + print_ns + m5r; // F20j2 RC6: the report print inside this window
	m_win_start          = flip_ns;
	m_win_extra_ns       = 0;
	// F20j2 (item 552(v)(1)): the schedule's new window; queries of samples already after the flip belong to it.
	{
		uint64_t carried = 0;
		for (uint64_t k = 0; k < kHist && k < m_hpos; k++) {
			const auto h = m_hpos - 1 - k;
			if (m_t[h % kHist] <= flip_ns) {
				break;
			}
			carried += m_kqc[h % kHist];
		}
		m_sched.NewWindow(flip_ns, carried);
	}
	// F20j2 (item 552(v)(3)): the zero invariants are rebased at every window close - _w is the increment of one window.
	RefreshCounters();
	if (start == 0 || flip_ns <= start) {
		m_c.Rebase();
		return;
	}
	const uint64_t dt = flip_ns - start;
	if (dt < kPrintNs) {
		if (dt >= kShortNs) {
			m_c.short_stalls++;
		}
		m_c.Rebase();
		return;
	}
	// The samples of (start, flip_ns], oldest first.
	std::vector<uint64_t> idx;
	uint64_t              instr     = 0;
	uint32_t              kq        = 0;
	bool                  exhausted = false;
	Core::WindowSamples(m_t, m_cost, m_kq, m_hpos, kHist, start, flip_ns, extra, &idx, &instr, &kq, &exhausted);
	if (exhausted) {
		m_c.ring_drop++; // the history ring no longer holds the start of this window
		m_c.hist_exh++;  // F25d (item 596(v), C3): the same event, its own counter
	}
	std::vector<uint64_t> times;
	std::vector<uint8_t>  wkq;
	std::vector<uint64_t> wkqt;
	uint32_t              kq_n  = 0;
	uint64_t              kq_ns = 0;
	for (auto h: idx) {
		times.push_back(m_t[h % kHist]);
		wkq.push_back(m_kq[h % kHist]);
		wkqt.push_back(m_kqt[h % kHist]);
		kq_n += m_kqc[h % kHist] != 0 ? 1 : 0;
		kq_ns += m_kqc[h % kHist];
	}
	// F20j2 (item 552(v)(1)): an S sample without its own snapshot is split by the nearest snapshot of this window <= 60 ms.
	std::vector<int32_t> nearest(idx.size(), -1);
	Core::NearestSnapshot(times.data(), wkq.data(), wkqt.data(), idx.size(), kKqNearNs, nearest.data());
	Core::Report r;
	r.n            = n;
	r.dt_us        = dt / 1000u;
	r.win_start_ns = start;
	r.win_end_ns   = flip_ns;
	r.instr_us     = instr / 1000u;
	r.gaps         = Core::Gaps(times.data(), times.size(), start, flip_ns, kPeriodNs);
	r.cover_us     = times.empty() ? 0 : (flip_ns - times.front()) / 1000u; // F25d (item 596(v), C4)
	r.kstate       = g_kstate.load(std::memory_order_relaxed);
	r.kq           = kq;
	r.kq_n         = kq_n;
	r.kq_us        = kq_ns / 1000u;
	r.m5r_us       = m5r / 1000u;
	r.proc_us      = proc_us;
	r.sys_busy_us  = busy_us;
	r.sys_idle_us  = idle_us;
	r.ncpu         = g_ncpu;
	r.snap_ok      = snap ? 1 : 0;
	r.snap_lag_us  = lag_us;
	r.flip_slot1   = flip_slot1;
	r.flip_src     = src;
	r.lat_us       = lat_us;
	r.vo_slot1     = g_vo_slot1.load(std::memory_order_acquire);
	r.gpu_slot1    = g_gpu_slot1.load(std::memory_order_acquire);
	const auto nslots = std::min<uint32_t>(g_reg->count.load(std::memory_order_acquire), kSlots);
	for (uint32_t i = 0; i < nslots; i++) {
		Core::ThreadRow row;
		for (size_t j = 0; j < idx.size(); j++) {
			auto code = m_codes[static_cast<size_t>(i) * kHist + idx[j] % kHist];
			if (Core::CodeState(code) == State::S && wkq[j] == 0 && nearest[j] >= 0) {
				const auto kc = m_kcodes[static_cast<size_t>(i) * kHist + idx[static_cast<size_t>(nearest[j])] % kHist];
				if (Core::CodeState(kc) == State::Sr || Core::CodeState(kc) == State::Sw) {
					code = kc;
				}
			}
			row.agg.Add(code);
		}
		if (row.agg.st[static_cast<size_t>(State::X)] == idx.size()) {
			continue;
		}
		auto& s    = g_reg->slots[i];
		row.slot1  = static_cast<int32_t>(i) + 1;
		row.gid    = s.gid.load(std::memory_order_acquire);
		row.os_tid = s.os_tid;
		row.name   = Core::SafeName(s.name);
		row.role   = Core::SafeName(s.role);
		if (!idx.empty() && m_last_mark_pos[i] >= idx.front() && m_last_mark_pos[i] <= idx.back()) {
			row.last = m_last_mark[i];
		}
		if (snap) {
			for (const auto& e: m_m5) {
				if (e.os_tid == s.os_tid && e.valid) {
					row.cpu_us = static_cast<int64_t>(e.last_ns / 1000u);
				}
			}
		}
		if (row.slot1 == flip_slot1) {
			r.flip_gid = row.gid;
		}
		// An open wait: the slot's mark in the last sample of the window is W and started >= 10 ms before the flip.
		if (!idx.empty() && m_last_mark_pos[i] == idx.back() &&
		    (m_last_mark[i].mark >> 8u) == static_cast<uint32_t>(State::W) && m_last_mark[i].since + kWaitRecNs <= flip_ns) {
			Core::WaitRec w;
			w.start_ns = m_last_mark[i].since;
			w.end_ns   = flip_ns;
			w.obj      = m_last_mark[i].obj;
			w.slot1    = row.slot1;
			// F20j3 (item 574(d)): mutex-like kinds (mutex, emu_mutex, spin) - the waker is the peer; every record - its peer.
			w.waker1   = MutexLike(static_cast<uint8_t>(m_last_mark[i].mark & 0xffu)) ? m_last_mark[i].peer : 0;
			w.peer1    = m_last_mark[i].peer;
			w.kind     = static_cast<uint8_t>(m_last_mark[i].mark & 0xffu);
			w.open     = 1;
			r.waits.push_back(w);
		}
		r.threads.push_back(std::move(row));
	}
	// The same wait seen open in the last sample and closed (in the ring) before the flip: keep the closed record.
	// F25d (item 599(b)(8), RC8 of F25c): one pass - an open record is dropped iff a closed record of the window has its
	// slot and start (sorted keys, binary search); the kept open records stay first in their order, the closed ones follow
	// in the m_recent order - the list of the per-record erase of F20j4 (r.waits holds only open records here).
	{
		std::vector<std::pair<int32_t, uint64_t>> keys;
		for (const auto& w: m_recent) {
			if (w.end_ns > start && w.start_ns < flip_ns) {
				keys.emplace_back(w.slot1, w.start_ns);
			}
		}
		std::sort(keys.begin(), keys.end());
		r.waits.erase(std::remove_if(r.waits.begin(), r.waits.end(),
		                             [&](const Core::WaitRec& o) {
			                             return o.open != 0 &&
			                                    std::binary_search(keys.begin(), keys.end(), std::make_pair(o.slot1, o.start_ns));
		                             }),
		              r.waits.end());
		for (const auto& w: m_recent) {
			if (w.end_ns > start && w.start_ns < flip_ns) {
				r.waits.push_back(w);
			}
		}
	}
	if (snap) {
		for (const auto& e: m_m5) {
			if (!e.valid) {
				continue;
			}
			Core::CpuRow c;
			c.os_tid = e.os_tid;
			c.name   = e.name;
			c.cpu_us = e.last_ns / 1000u;
			for (uint32_t i = 0; i < nslots; i++) {
				if (g_reg->slots[i].os_tid == e.os_tid) {
					c.slot1 = static_cast<int32_t>(i) + 1;
				}
			}
			r.cpu.push_back(std::move(c));
		}
	}
	m_c.slots    = nslots;
	m_c.print_us = g_print_us.load(std::memory_order_relaxed);
	auto text    = Core::Format(&r, &m_c);
	m_c.Rebase();
	for (auto& slot: g_rep) {
		if (slot.state.load(std::memory_order_acquire) == 0) {
			slot.n    = n;
			slot.text = std::move(text);
			slot.state.store(1, std::memory_order_release);
			return;
		}
	}
	m_c.rep_drop++;
}

void Sampler::ProcessFlips() {
	const auto pub = g_flip_pub.load(std::memory_order_acquire);
	if (pub == m_seen_flips) {
		return;
	}
	const auto t0 = FrameStats::NowNs();
	if (pub - m_seen_flips > kFlipRing) {
		m_c.ring_drop += pub - m_seen_flips - kFlipRing;
		m_seen_flips = pub - kFlipRing;
	}
	// F20j3 (item 574(g)(4)): the refresh runs on the refresher thread (no gap of samples). F20j4 (item 581(v)(3), RC3 of
	// F20k3): its runs are charged to the windows they ran in - the begin of the run in progress first, then the finished
	// runs; CloseWindow takes the overlap with its own window.
	const uint64_t m5_cur = m_m5r.CurrentBegin();
	m_m5_runs.clear();
	m_m5r.TakeRuns(&m_m5_runs);
	m_m5c.Add(m_m5_runs, m5_cur);
	M5Adopt();
	M5Snapshot();
	uint64_t proc_us = 0;
	uint64_t busy_us = 0;
	uint64_t idle_us = 0;
	M1Snapshot(&proc_us, &busy_us, &idle_us);
	m_ring_tmp.clear();
	g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn, &m_ring_hold);
	for (auto& w: m_ring_tmp) {
		m_recent.push_back(w);
	}
	const bool batch = pub - m_seen_flips > 1;
	for (auto k = m_seen_flips; k < pub; k++) {
		auto&      e       = g_flip[k % kFlipRing];
		const auto n       = e.n.load(std::memory_order_relaxed);
		const auto ns      = e.ns.load(std::memory_order_relaxed);
		const auto lat     = e.lat_us.load(std::memory_order_relaxed);
		const auto slot1   = e.slot1.load(std::memory_order_relaxed);
		const auto src     = e.src.load(std::memory_order_relaxed);
		const auto prn     = e.print_ns.load(std::memory_order_relaxed);
		const bool last    = k + 1 == pub;
		const auto lag_us  = t0 > ns ? (t0 - ns) / 1000u : 0;
		CloseWindow(n, ns, lat, slot1, src, last && !batch, proc_us, busy_us, idle_us, lag_us, prn);
	}
	m_seen_flips = pub;
	// Wait records older than 3 s before the current window start are no longer needed.
	const auto keep_from = m_win_start > 3000000000ull ? m_win_start - 3000000000ull : 0;
	m_recent.erase(std::remove_if(m_recent.begin(), m_recent.end(), [&](const Core::WaitRec& w) { return w.end_ns < keep_from; }),
	               m_recent.end());
	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us). F20j4: the M5
	// refresh time is charged by CloseWindow; the finished runs that end before the open window are dropped.
	m_win_extra_ns += FrameStats::NowNs() - t0;
	m_m5c.Prune(m_win_start);
}

void Sampler::Run() {
	SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST);
	m_cpn = FrameStats::CpuCyclesPerNs();
	m_pid = static_cast<uint32_t>(GetCurrentProcessId());
	if (HMODULE ntdll = GetModuleHandleW(L"ntdll.dll"); ntdll != nullptr) {
		m_ntq = reinterpret_cast<NtQuerySystemInformationFn>(
		    reinterpret_cast<void*>(GetProcAddress(ntdll, "NtQuerySystemInformation")));
	}
	if (HMODULE k32 = GetModuleHandleW(L"kernel32.dll"); k32 != nullptr) {
		m_gtd = reinterpret_cast<GetThreadDescriptionFn>(reinterpret_cast<void*>(GetProcAddress(k32, "GetThreadDescription")));
		using SetThreadDescriptionFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
		if (auto set_fn = reinterpret_cast<SetThreadDescriptionFn>(
		        reinterpret_cast<void*>(GetProcAddress(k32, "SetThreadDescription")));
		    set_fn != nullptr) {
			set_fn(GetCurrentThread(), L"DiagB32"); // the instrument's own CPU is visible in the -c lines
		}
	}
	m_kmap.reserve(1024);
	// F20j3 (item 574(g)(4)): the thread list is refreshed every 1 s on its own thread (was: on this thread).
	m_m5s.pid = m_pid;
	m_m5s.gtd = m_gtd;
	m_m5r.Start(&Sampler::M5RefreshWork, &m_m5s, 1000000000ull);
	if (m_ntq != nullptr) {
		const auto q0 = FrameStats::NowNs();
		KernelQuery();
		g_kq_first_us.store((FrameStats::NowNs() - q0) / 1000u, std::memory_order_relaxed); // F20j2: kq_us of mode=1
		m_kq_ok = !m_kmap.empty();
	}
	g_kstate.store(m_kq_ok ? 1 : 0, std::memory_order_relaxed);
	g_sampler_ready.store(true, std::memory_order_release);
	HANDLE timer = CreateWaitableTimerExW(nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);
	if (timer == nullptr) {
		timer = CreateWaitableTimerW(nullptr, TRUE, nullptr);
	}
	if (timer == nullptr) {
		return;
	}
	HANDLE        handles[2] = {timer, g_flip_event};
	LARGE_INTEGER due {};
	due.QuadPart = -static_cast<LONGLONG>(kPeriodNs / 100u);
	SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);
	for (;;) {
		const DWORD r = WaitForMultipleObjects(2, handles, FALSE, 1000);
		if (r != WAIT_OBJECT_0) {
			ProcessFlips();
			continue;
		}
		// F20j2 (item 552(v)(1), RC1(b) of F20k): the absolute period - the next sample is due P after the BEGIN of this
		// one (Core::NextBegin); when the sample and the flips after it took P or longer, the next sample runs at once.
		// A flip published together with the timer is taken first, so the schedule sees the current window start.
		for (;;) {
			ProcessFlips();
			const auto begin = FrameStats::NowNs();
			Sample(begin);
			ProcessFlips();
			const auto now  = FrameStats::NowNs();
			const auto next = Core::NextBegin(begin, now);
			if (next >= now + 100) {
				due.QuadPart = -static_cast<LONGLONG>((next - now) / 100u);
				SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);
				break;
			}
		}
	}
}

} // namespace
#endif

void Init() {
	static bool done = false;
	if (done) {
		return;
	}
	done = true;
	if (const char* v = std::getenv("KYTY_DIAG_B32"); v != nullptr && v[0] != '\0') {
		if (std::strcmp(v, "1") == 0) {
			g_on = true;
		} else if (std::strcmp(v, "0") != 0) {
			g_config_invalid = true;
			std::snprintf(g_config_text, sizeof(g_config_text), "%s", v);
		}
	}
	if (const char* v = std::getenv("KYTY_TEST_B32"); v != nullptr && v[0] != '\0') {
		std::snprintf(g_test_text, sizeof(g_test_text), "%s", v);
		char*        end   = nullptr;
		const double delay = std::strtod(v, &end);
		bool         ok    = end != v && end != nullptr && *end == ':' && delay >= 0.0;
		bool         pres  = false;
		bool         gpu   = false;
		uint32_t     ms    = 0;
		if (ok) {
			const char* mode = end + 1;
			if (std::strncmp(mode, "present:", 8) == 0) {
				pres = true;
				mode += 8;
			} else if (std::strncmp(mode, "gpusleep:", 9) == 0) {
				gpu = true;
				mode += 9;
			} else {
				ok = false;
			}
			if (ok) {
				char*      end2 = nullptr;
				const auto val  = std::strtoul(mode, &end2, 10);
				ok              = end2 != mode && end2 != nullptr && *end2 == '\0' && val > 0 && val <= 60000;
				ms              = static_cast<uint32_t>(val);
			}
		}
		if (ok) {
			g_test_on       = true;
			g_test_present  = pres;
			g_test_gpusleep = gpu;
			g_test_delay_s  = delay;
			g_test_ms       = ms;
		}
	}
	g_present_site = g_on || g_test_present;
	if (!g_on) {
		return;
	}
	g_reg  = new Core::Registry;
	g_ring = new Core::WaitRing;
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	g_ncpu       = static_cast<uint32_t>(GetActiveProcessorCount(ALL_PROCESSOR_GROUPS));
	g_flip_event = CreateEventW(nullptr, FALSE, FALSE, nullptr);
	std::thread([] {
		auto* sampler = new Sampler;
		sampler->Run();
	}).detach();
#endif
}

namespace Test {

void InitRuntime() {
	if (g_reg == nullptr) {
		g_reg  = new Core::Registry;
		g_ring = new Core::WaitRing;
	}
	g_on = true;
}

bool ReadSlotMark(int32_t slot1, Core::MarkSnap* out) {
	return g_reg != nullptr && slot1 > 0 && g_reg->ReadMark(slot1 - 1, out);
}

void DrainWaits(std::vector<Core::WaitRec>* out) {
	uint64_t drop = 0;
	uint64_t torn = 0;
	if (g_ring != nullptr) {
		g_ring->Drain(out, &drop, &torn);
	}
}

BenchOut CloseWindowBench(const BenchIn& in) {
	BenchOut out;
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	auto*    reg     = new Core::Registry;
	auto*    old_reg = g_reg;
	const auto old_vo  = g_vo_slot1.load();
	const auto old_gpu = g_gpu_slot1.load();
	g_reg              = reg;
	const uint32_t nslots = std::min(in.nslots, kSlots);
	for (uint32_t i = 0; i < nslots; i++) {
		(void)reg->Allocate(5000 + i, nullptr, i == 0 ? "Present" : (i == 1 ? "Gpu" : "guest"), "bench", static_cast<int32_t>(i));
	}
	g_vo_slot1.store(nslots > 0 ? 1 : 0);
	g_gpu_slot1.store(nslots > 1 ? 2 : 0);
	auto*          s     = new Sampler;
	std::mt19937   rng(in.seed);
	const uint64_t P     = in.period_ns;
	const uint64_t start = 1000000000000ull;
	const uint64_t total = static_cast<uint64_t>(in.before) + in.nsamples;
	// sample h (absolute number): h < before - at or before the start, the last of them exactly at the start
	for (uint64_t h = 0; h < total; h++) {
		const uint64_t th  = h < in.before ? start - (in.before - 1 - h) * P : start + (h - in.before + 1) * P;
		const auto     pos = static_cast<size_t>(h % kHist);
		s->m_t[pos]        = th;
		s->m_cost[pos]     = 50000;
		const bool     snap = in.kq_every > 0 && h % in.kq_every == 0;
		s->m_kq[pos]       = snap ? 1 : 0;
		s->m_kqt[pos]      = snap ? th - P / 4 : 0;
		s->m_kqc[pos]      = snap ? 200000 : 0;
		for (uint32_t i = 0; i < nslots; i++) {
			const auto kk = rng() % 3u;
			s->m_kcodes[static_cast<size_t>(i) * kHist + pos] =
			    kk == 0 ? Core::Code(State::Sr, 0) : (kk == 1 ? Core::Code(State::Sw, static_cast<uint8_t>(rng() % 40u)) : Core::Code(State::S, 0));
		}
		for (uint32_t i = 0; i < nslots; i++) {
			const auto k = rng() % 8u;
			uint16_t   code;
			if (k < 2) {
				code = Core::Code(State::R, 0);
			} else if (k < 4) {
				code = Core::Code(State::W, static_cast<uint8_t>(1 + rng() % (static_cast<uint32_t>(Wait::Count) - 1)));
			} else if (k == 4) {
				code = Core::Code(State::H, static_cast<uint8_t>(1 + rng() % (static_cast<uint32_t>(Call::Count) - 1)));
			} else {
				code = Core::Code(State::S, 0);
			}
			s->m_codes[static_cast<size_t>(i) * kHist + pos] = code;
		}
	}
	s->m_hpos         = total;
	const uint64_t flip = start + static_cast<uint64_t>(in.nsamples) * P;
	for (uint32_t i = 0; i < nslots && i < in.nopen; i++) {
		s->m_last_mark[i].mark  = Core::MarkWord(State::W, static_cast<uint8_t>(Wait::Cond));
		s->m_last_mark[i].since = start + P;
		s->m_last_mark[i].peer  = static_cast<int32_t>(1 + (i + 1) % nslots);
		s->m_last_mark_pos[i]   = total - 1;
	}
	const uint64_t span = flip > start ? flip - start : 1;
	for (uint32_t k = 0; k < in.nwaits; k++) {
		Core::WaitRec w;
		w.start_ns = start + rng() % span;
		w.end_ns   = std::min(flip, w.start_ns + kWaitRecNs + rng() % 40000000u);
		w.obj      = 0x10000u + k;
		w.slot1    = nslots > 0 ? static_cast<int32_t>(1 + k % nslots) : 0;
		w.waker1   = nslots > 0 ? static_cast<int32_t>(1 + rng() % nslots) : 0;
		w.peer1    = 0;
		w.kind     = static_cast<uint8_t>(Wait::Cond);
		if (k < in.nmatch && k < in.nopen && k < nslots) { // the open record of slot k + 1 closed before the flip
			w.slot1    = static_cast<int32_t>(1 + k);
			w.start_ns = start + P;
			w.end_ns   = start + P + kWaitRecNs + 1000000;
		}
		s->m_recent.push_back(w);
	}
	s->m_win_start = start;
	const auto t0  = std::chrono::steady_clock::now();
	s->CloseWindow(7, flip, 0, 3, 2, false, 0, 0, 0, 0, 0);
	const auto t1  = std::chrono::steady_clock::now();
	out.close_ns   = static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count());
	out.start_ns   = start;
	out.flip_ns    = flip;
	for (auto& slot: g_rep) {
		if (slot.state.load(std::memory_order_acquire) == 1 && slot.n == 7) {
			out.text = std::move(slot.text);
			slot.text.clear();
			slot.state.store(0, std::memory_order_release);
			break;
		}
	}
	delete s;
	g_reg = old_reg;
	g_vo_slot1.store(old_vo);
	g_gpu_slot1.store(old_gpu);
	delete reg;
#else
	(void)in;
#endif
	return out;
}

} // namespace Test

void LogHeader() {
	if (g_config_invalid) {
		LOGF("DiagB32: config invalid value=%s (off)\n", Core::SafeName(g_config_text).c_str());
	}
	if (g_test_text[0] != '\0') {
		LOGF("TestB32: config %s value=%s\n", g_test_on ? "on" : "invalid", Core::SafeName(g_test_text).c_str());
	}
	if (!g_on) {
		return;
	}
	// kstate is known once the sampler made its first kernel query; the header waits for it up to 1 s (start only).
	for (int i = 0; i < 200 && !g_sampler_ready.load(std::memory_order_acquire); i++) {
		std::this_thread::sleep_for(std::chrono::milliseconds(5));
	}
	const auto text = Core::HeaderLine(g_ncpu, g_kstate.load(std::memory_order_relaxed),
	                                   g_kq_first_us.load(std::memory_order_relaxed));
	if (!::Log::IsSilent()) {
		::Log::Write(text);
	}
}

} // namespace Common::DiagB32
