#include "common/diagB32.h"

#include "common/common.h"
#include "common/frameStats.h"
#include "common/logging/log.h"

#include <algorithm>
#include <chrono>
#include <cinttypes>
#include <cstdarg>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
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
	static constexpr const char* names[] = {"-", "cond", "mutex", "sem", "psem", "evf", "eq", "sleep", "gpu_idle", "gpu_regmem"};
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
	const auto i = wpos.fetch_add(1, std::memory_order_acq_rel);
	auto&      x = e[i % kWaitRing];
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
	x.seq.store(2 * i + 2, std::memory_order_release);
}

void WaitRing::Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn) {
	const auto w = wpos.load(std::memory_order_acquire);
	if (w > rpos + kWaitRing) {
		*drop += w - kWaitRing - rpos;
		rpos = w - kWaitRing;
	}
	for (; rpos < w; rpos++) {
		auto& x  = e[rpos % kWaitRing];
		bool  ok = false;
		for (int attempt = 0; attempt < 3 && !ok; attempt++) {
			const auto s1 = x.seq.load(std::memory_order_acquire);
			if (s1 != 2 * rpos + 2) {
				if (s1 > 2 * rpos + 2) {
					break; // overwritten by a later lap
				}
				continue;
			}
			WaitRec r;
			r.start_ns     = x.start.load(std::memory_order_relaxed);
			r.end_ns       = x.end.load(std::memory_order_relaxed);
			r.obj          = x.obj.load(std::memory_order_relaxed);
			r.req_us       = x.req.load(std::memory_order_relaxed);
			const auto who = x.who.load(std::memory_order_relaxed);
			std::atomic_thread_fence(std::memory_order_acquire);
			if (x.seq.load(std::memory_order_relaxed) != s1) {
				continue;
			}
			r.slot1     = static_cast<int32_t>(who & 0xfffffu);
			r.waker1    = static_cast<int32_t>((who >> 20u) & 0xfffffu);
			r.kind      = static_cast<uint8_t>((who >> 40u) & 0xffu);
			r.timed_out = static_cast<uint8_t>((who >> 48u) & 0xffu);
			out->push_back(r);
			ok = true;
		}
		if (!ok) {
			const auto s1 = x.seq.load(std::memory_order_acquire);
			if (s1 > 2 * rpos + 2) {
				(*drop)++;
			} else {
				(*torn)++;
			}
		}
	}
}

static uint64_t Overlap(const WaitRec& w, uint64_t a, uint64_t b) {
	const auto s = std::max(w.start_ns, a);
	const auto e = std::min(w.end_ns, b);
	return e > s ? e - s : 0;
}

static ThreadRow* RowOf(Report* r, int32_t slot1) {
	if (slot1 <= 0) {
		return nullptr;
	}
	for (auto& t: r->threads) {
		if (t.slot1 == slot1) {
			return &t;
		}
	}
	return nullptr;
}

// The -w records printed: the closure (3 steps) of the chain participants first (the present thread, GuestGpu,
// flip_slot, threads with R >= 10 %), then the rest by overlap with the window up to kWLinesCap in all.
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
	for (int step = 0; step < 3; step++) {
		const auto before = set.size();
		for (size_t i = 0; i < r.waits.size(); i++) {
			if (std::find(set.begin(), set.end(), r.waits[i].slot1) != set.end() &&
			    std::find(must.begin(), must.end(), i) == must.end()) {
				must.push_back(i);
				add(r.waits[i].waker1);
			}
		}
		if (set.size() == before) {
			break;
		}
	}
	std::vector<size_t> rest;
	for (size_t i = 0; i < r.waits.size(); i++) {
		if (std::find(must.begin(), must.end(), i) == must.end()) {
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
		t.must = t.slot1 == r.vo_slot1 || t.slot1 == r.gpu_slot1 || t.slot1 == r.flip_slot1 ||
		         (samples > 0 && t.agg.st[static_cast<size_t>(State::R)] * 10 >= samples);
	}
	size_t     cut  = 0;
	const auto pick = PickWaits(r, &cut);
	for (auto i: pick) {
		if (auto* t = RowOf(&r, r.waits[i].waker1); t != nullptr) {
			t->must = true;
		}
	}
	for (auto& t: r.threads) {
		if (t.last.mark != 0 && t.last.peer > 0) {
			if (auto* p = RowOf(&r, t.last.peer); p != nullptr && t.must) {
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

static int32_t GidOf(const Report& r, int32_t slot1) {
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
	       " proc_us=%llu sys_busy_us=%llu sys_idle_us=%llu other_us=%lld ncpu=%u snap_ok=%u snap_lag_us=%llu"
	       " flip_slot=%d flip_tid=%d flip_src=%s lat_us=%llu vo_slot=%d gpu_slot=%d t_lines=%zu w_lines=%zu c_lines=%zu\n",
	       n, static_cast<unsigned long long>(r.dt_us), static_cast<unsigned long long>(r.instr_us), r.gaps.samples,
	       static_cast<unsigned long long>(r.gaps.sgap_max_ns / 1000u), r.gaps.gap3p, r.gaps.i2_ok && r.gaps.monotonic ? 1 : 0,
	       r.kstate, r.kq, static_cast<unsigned long long>(r.proc_us), static_cast<unsigned long long>(r.sys_busy_us),
	       static_cast<unsigned long long>(r.sys_idle_us), static_cast<long long>(OtherUs(r.sys_busy_us, r.proc_us)), r.ncpu,
	       r.snap_ok, static_cast<unsigned long long>(r.snap_lag_us), SlotIndex(r.flip_slot1), r.flip_gid,
	       r.flip_src == 1 ? "cpu" : (r.flip_src == 2 ? "gpu" : "-"), static_cast<unsigned long long>(r.lat_us),
	       SlotIndex(r.vo_slot1), SlotIndex(r.gpu_slot1), must.size() + others.size(), picks.size(), cpu.size());
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
	for (auto i: picks) {
		const auto& w = r.waits[i];
		Append(&out,
		       "DiagB32-w: n=%llu slot=%d tid=%d kind=%s obj=0x%llx start_us=%lld wait_us=%llu overlap_us=%llu waker=%d"
		       " waker_tid=%d req_us=%llu to=%u open=%u\n",
		       n, SlotIndex(w.slot1), GidOf(r, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),
		       (static_cast<long long>(w.start_ns) - static_cast<long long>(r.win_start_ns)) / 1000,
		       static_cast<unsigned long long>((w.end_ns - w.start_ns) / 1000u),
		       static_cast<unsigned long long>(Overlap(w, r.win_start_ns, r.win_end_ns) / 1000u), SlotIndex(w.waker1),
		       GidOf(r, w.waker1), static_cast<unsigned long long>(w.req_us), w.timed_out, w.open);
	}
	for (const auto* c: cpu) {
		Append(&out, "DiagB32-c: n=%llu os_tid=%u slot=%d name=%s cpu_us=%llu\n", n, c->os_tid, SlotIndex(c->slot1),
		       c->name.c_str(), static_cast<unsigned long long>(c->cpu_us));
	}
	Append(&out,
	       "DiagB32-x: n=%llu slots=%llu slot_full=%llu torn=%llu ring_drop=%llu sgap_bad=%llu lines_cut=%llu"
	       " short_stalls=%llu others_cut=%llu w_cut=%llu rep_drop=%llu kq_fail=%llu print_us=%llu gap3p=%u\n",
	       n, static_cast<unsigned long long>(counters->slots), static_cast<unsigned long long>(counters->slot_full),
	       static_cast<unsigned long long>(counters->torn), static_cast<unsigned long long>(counters->ring_drop),
	       static_cast<unsigned long long>(counters->sgap_bad), static_cast<unsigned long long>(counters->lines_cut),
	       static_cast<unsigned long long>(counters->short_stalls), static_cast<unsigned long long>(counters->others_cut),
	       static_cast<unsigned long long>(counters->w_cut), static_cast<unsigned long long>(counters->rep_drop),
	       static_cast<unsigned long long>(counters->kq_fail), static_cast<unsigned long long>(counters->print_us),
	       r.gaps.gap3p);
	return out;
}

std::string HeaderLine(uint32_t ncpu, uint32_t kstate) {
	char buf[256];
	std::snprintf(buf, sizeof(buf),
	              "DiagB32: mode=1 period_us=%llu print_us=%llu wait_rec_us=%llu kernel_after_us=%llu slots=%u hist=%u"
	              " wring=%u ncpu=%u kstate=%u\n",
	              static_cast<unsigned long long>(kPeriodNs / 1000u), static_cast<unsigned long long>(kPrintNs / 1000u),
	              static_cast<unsigned long long>(kWaitRecNs / 1000u), static_cast<unsigned long long>(kKernelAfterNs / 1000u),
	              kSlots, kHist, kWaitRing, ncpu, kstate);
	return buf;
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
};
constexpr uint32_t    kFlipRing = 16;
FlipEnt               g_flip[kFlipRing];
std::atomic<uint64_t> g_flip_pub {0};
std::atomic<int32_t>  g_vo_slot1 {0};
std::atomic<int32_t>  g_gpu_slot1 {0};

// Reports: the sampler formats, the present thread prints at its next flip site.
struct RepSlot {
	std::atomic<uint32_t> state {0}; // 0 free, 1 ready
	uint64_t              n = 0;
	std::string           text;
};
RepSlot               g_rep[4];
std::atomic<uint64_t> g_print_us {0};

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
	}
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
	m_peer       = peer_slot1;
	m_req_us     = req_us;
	g_reg->WriteMark(m_slot, m_mark, m_obj, m_since, m_peer);
	m_active = true;
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
	}
	const auto k = g_flip_pub.load(std::memory_order_relaxed);
	auto&      e = g_flip[k % kFlipRing];
	e.n.store(n, std::memory_order_relaxed);
	e.ns.store(now, std::memory_order_relaxed);
	e.lat_us.store(reserve_host_ns != 0 && now > reserve_host_ns ? (now - reserve_host_ns) / 1000u : 0,
	               std::memory_order_relaxed);
	e.slot1.store(slot1, std::memory_order_relaxed);
	e.src.store(src, std::memory_order_relaxed);
	g_flip_pub.store(k + 1, std::memory_order_release);
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	SetEvent(g_flip_event);
#endif
	// Print the reports the sampler has closed (each one once, in the order of n).
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
		g_print_us.store((FrameStats::NowNs() - t0) / 1000u, std::memory_order_relaxed);
	}
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

class Sampler {
public:
	void Run();

private:
	void     Sample(uint64_t t0);
	void     ProcessFlips();
	void     KernelQuery();
	bool     KernelLookup(uint32_t tid, uint32_t* state, uint32_t* reason) const;
	void     M5Refresh(uint64_t now);
	void     M5Snapshot();
	void     M1Snapshot(uint64_t* proc_us, uint64_t* busy_us, uint64_t* idle_us);
	void     CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
	                     uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us);
	[[nodiscard]] uint64_t CyclesToNs(uint64_t cycles) const {
		return m_cpn > 0.0 ? static_cast<uint64_t>(static_cast<double>(cycles) / m_cpn) : 0;
	}

	double                    m_cpn = 0.0;
	std::vector<uint16_t>     m_codes = std::vector<uint16_t>(static_cast<size_t>(kSlots) * kHist, 0);
	uint64_t                  m_t[kHist] {};
	uint64_t                  m_cost[kHist] {};
	uint8_t                   m_kq[kHist] {};
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
	uint64_t                  m_m5_next = 0;
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

void Sampler::Sample(uint64_t t0) {
	const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;
	bool           kq       = false;
	if (m_kq_ok && m_win_start != 0 && t0 >= m_win_start + kKernelAfterNs) {
		KernelQuery();
		kq = !m_kmap.empty();
	}
	const auto n   = std::min<uint32_t>(g_reg->count.load(std::memory_order_acquire), kSlots);
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
			if (ms.mark != 0) {
				m_last_mark[i]     = ms;
				m_last_mark_pos[i] = m_hpos;
			}
		}
		m_codes[static_cast<size_t>(i) * kHist + pos] = code;
	}
	m_t[pos]    = t0;
	m_kq[pos]   = kq ? 1 : 0;
	m_last_t    = t0;
	m_cost[pos] = FrameStats::NowNs() - t0;
	m_hpos++;
}

void Sampler::M5Refresh(uint64_t now) {
	HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
	m_m5_next   = now + 1000000000ull;
	if (snap == INVALID_HANDLE_VALUE) {
		return;
	}
	for (auto& e: m_m5) {
		e.seen = false;
	}
	THREADENTRY32 te {};
	te.dwSize = sizeof(te);
	for (BOOL ok = Thread32First(snap, &te); ok != FALSE; ok = Thread32Next(snap, &te)) {
		if (te.th32OwnerProcessID != m_pid) {
			continue;
		}
		auto it = std::find_if(m_m5.begin(), m_m5.end(), [&](const M5Ent& e) { return e.os_tid == te.th32ThreadID; });
		if (it != m_m5.end()) {
			it->seen = true;
			continue;
		}
		M5Ent e;
		e.os_tid = te.th32ThreadID;
		e.handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, te.th32ThreadID);
		e.seen   = true;
		if (e.handle == nullptr) {
			continue;
		}
		if (m_gtd != nullptr) {
			PWSTR desc = nullptr;
			if (SUCCEEDED(m_gtd(e.handle, &desc)) && desc != nullptr) {
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
		m_m5.push_back(std::move(e));
	}
	CloseHandle(snap);
	for (auto& e: m_m5) {
		if (!e.seen && e.handle != nullptr) {
			CloseHandle(e.handle);
			e.handle = nullptr;
		}
	}
	m_m5.erase(std::remove_if(m_m5.begin(), m_m5.end(), [](const M5Ent& e) { return e.handle == nullptr; }), m_m5.end());
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

void Sampler::CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
                          uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us) {
	const uint64_t start = m_win_start;
	const uint64_t extra = m_win_extra_ns;
	m_win_start          = flip_ns;
	m_win_extra_ns       = 0;
	if (start == 0 || flip_ns <= start) {
		return;
	}
	const uint64_t dt = flip_ns - start;
	if (dt < kPrintNs) {
		if (dt >= kShortNs) {
			m_c.short_stalls++;
		}
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
	}
	std::vector<uint64_t> times;
	for (auto h: idx) {
		times.push_back(m_t[h % kHist]);
	}
	Core::Report r;
	r.n            = n;
	r.dt_us        = dt / 1000u;
	r.win_start_ns = start;
	r.win_end_ns   = flip_ns;
	r.instr_us     = instr / 1000u;
	r.gaps         = Core::Gaps(times.data(), times.size(), start, flip_ns, kPeriodNs);
	r.kstate       = g_kstate.load(std::memory_order_relaxed);
	r.kq           = kq;
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
		for (auto h: idx) {
			row.agg.Add(m_codes[static_cast<size_t>(i) * kHist + h % kHist]);
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
			w.waker1   = (m_last_mark[i].mark & 0xffu) == static_cast<uint32_t>(Wait::Mutex) ? m_last_mark[i].peer : 0;
			w.kind     = static_cast<uint8_t>(m_last_mark[i].mark & 0xffu);
			w.open     = 1;
			r.waits.push_back(w);
		}
		r.threads.push_back(std::move(row));
	}
	for (const auto& w: m_recent) {
		if (w.end_ns > start && w.start_ns < flip_ns) {
			// The same wait seen open in the last sample and closed (in the ring) before the flip: keep the closed record.
			r.waits.erase(std::remove_if(r.waits.begin(), r.waits.end(),
			                             [&](const Core::WaitRec& o) {
				                             return o.open != 0 && o.slot1 == w.slot1 && o.start_ns == w.start_ns;
			                             }),
			              r.waits.end());
			r.waits.push_back(w);
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
	m_c.slots     = nslots;
	m_c.slot_full = g_reg->slot_full.load(std::memory_order_relaxed);
	m_c.torn      = g_reg->torn.load(std::memory_order_relaxed) + m_ring_torn;
	m_c.print_us  = g_print_us.load(std::memory_order_relaxed);
	auto text     = Core::Format(&r, &m_c);
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
	if (t0 >= m_m5_next) {
		M5Refresh(t0);
	}
	M5Snapshot();
	uint64_t proc_us = 0;
	uint64_t busy_us = 0;
	uint64_t idle_us = 0;
	M1Snapshot(&proc_us, &busy_us, &idle_us);
	m_ring_tmp.clear();
	g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn);
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
		const bool last    = k + 1 == pub;
		const auto lag_us  = t0 > ns ? (t0 - ns) / 1000u : 0;
		CloseWindow(n, ns, lat, slot1, src, last && !batch, proc_us, busy_us, idle_us, lag_us);
	}
	m_seen_flips = pub;
	// Wait records older than 3 s before the current window start are no longer needed.
	const auto keep_from = m_win_start > 3000000000ull ? m_win_start - 3000000000ull : 0;
	m_recent.erase(std::remove_if(m_recent.begin(), m_recent.end(), [&](const Core::WaitRec& w) { return w.end_ns < keep_from; }),
	               m_recent.end());
	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us).
	m_win_extra_ns += FrameStats::NowNs() - t0;
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
	if (m_ntq != nullptr) {
		KernelQuery();
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
		if (r == WAIT_OBJECT_0) {
			Sample(FrameStats::NowNs());
			SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);
		}
		ProcessFlips();
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
	const auto text = Core::HeaderLine(g_ncpu, g_kstate.load(std::memory_order_relaxed));
	if (!::Log::IsSilent()) {
		::Log::Write(text);
	}
}

} // namespace Common::DiagB32
