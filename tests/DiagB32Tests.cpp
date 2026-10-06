// Track F, F20j (HPP-629; ROADMAP s122 item 550(z)(4)): unit tests of the KYTY_DIAG_B32 core without the game -
// the sample partition H > W > R > r > Sr > Sw > S (exactly one), I1, I2', I3, the window selection and instr_us, the
// printed lines (RC13 form), the counters slot_full / torn / ring_drop / sgap_bad / lines_cut / gap3p, mandatory -t
// lines (RC2). Target diag_b32_tests (not in ctest); prints one line per case and "ALL OK".
// F20j2 (HPP-633; ROADMAP s122 item 552(v), (d)): plus the kernel query schedule (RC1), the nearest snapshot, the
// per-window zero invariants _w (RC3), the drain with a preempted writer (RC4), the async submitter's line (RC5).
// F20j3 (HPP-646; ROADMAP s122 item 574(g)): plus the wait kinds, ring_hold (Z1), the record's peer in -w, the M5
// refresh off the sampler thread (an 80 ms refresh - model), a wait loop with short wakeups under one mark (W share,
// one record, waker and peer) and the contended Common::Mutex / TrackedMutex (W:emu_mutex, peer = owner). The two
// runtime cases run last: Test::InitRuntime turns g_on on for the rest of the process.

#include "common/diagB32.h"
#include "common/threads.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <random>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

using namespace Common::DiagB32;
using namespace Common::DiagB32::Core;

static int g_fail  = 0;
static int g_cases = 0;

#define CHECK(cond)                                                                                                    \
	do {                                                                                                               \
		if (!(cond)) {                                                                                                 \
			std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #cond);                                                 \
			g_fail++;                                                                                                  \
		}                                                                                                              \
	} while (false)

static void Case(const char* name) {
	g_cases++;
	std::printf("[case] %s\n", name);
}

// ---------------------------------------------------------------------------------------------------------------------
static State Expected(uint32_t mark, uint64_t cpu, uint64_t interval, bool kq, uint32_t ks) {
	const auto ms = static_cast<State>(mark >> 8u);
	if (ms == State::H) {
		return State::H;
	}
	if (ms == State::W) {
		return State::W;
	}
	if (interval > 0 && cpu * 2 >= interval) {
		return State::R;
	}
	if (cpu > 0) {
		return State::Rr;
	}
	if (kq && KernelReady(ks)) {
		return State::Sr;
	}
	if (kq && KernelWaiting(ks)) {
		return State::Sw;
	}
	return State::S;
}

static void TestPartition() {
	Case("partition H > W > R > r > Sr > Sw > S, exactly one");
	const uint32_t marks[] = {0, MarkWord(State::H, static_cast<uint8_t>(Call::Present)),
	                          MarkWord(State::H, static_cast<uint8_t>(Call::Fault)),
	                          MarkWord(State::W, static_cast<uint8_t>(Wait::Cond)),
	                          MarkWord(State::W, static_cast<uint8_t>(Wait::GpuRegmem))};
	const uint64_t interval = 5000000;
	const uint64_t cpus[]   = {0, 1, 2499999, 2500000, 5000000, 9000000};
	uint32_t       n        = 0;
	for (auto m: marks) {
		for (auto c: cpus) {
			for (int kq = 0; kq < 2; kq++) {
				for (uint32_t ks = 0; ks < 10; ks++) {
					for (uint32_t kr: {0u, 6u, 77u}) {
						const auto code = Classify(m, c, interval, kq != 0, ks, kr);
						const auto st   = CodeState(code);
						CHECK(static_cast<size_t>(st) < static_cast<size_t>(State::Count));
						CHECK(st != State::X);
						CHECK(st == Expected(m, c, interval, kq != 0, ks));
						if (st == State::H || st == State::W) {
							CHECK(CodeKind(code) == (m & 0xffu));
						}
						if (st == State::Sw) {
							CHECK(CodeKind(code) == std::min<uint32_t>(kr, 63));
						}
						// exactly one: one Agg slot grows by one
						Agg a;
						a.Add(code);
						CHECK(a.Total() == 1);
						n++;
					}
				}
			}
		}
	}
	// explicit precedence points
	CHECK(CodeState(Classify(MarkWord(State::H, 1), 5000000, interval, true, 5, 0)) == State::H); // H beats R and Sw
	CHECK(CodeState(Classify(MarkWord(State::W, 1), 5000000, interval, true, 1, 0)) == State::W); // W beats R and Sr
	CHECK(CodeState(Classify(0, 2500000, interval, true, 1, 0)) == State::R);                     // R: >= 50 %
	CHECK(CodeState(Classify(0, 2499999, interval, true, 1, 0)) == State::Rr);                    // r: > 0, < 50 %
	CHECK(CodeState(Classify(0, 0, interval, true, 1, 0)) == State::Sr);                          // ready
	CHECK(CodeState(Classify(0, 0, interval, true, 5, 6)) == State::Sw);                          // waiting
	CHECK(CodeState(Classify(0, 0, interval, false, 5, 6)) == State::S);                          // no kernel state
	CHECK(CodeState(Classify(0, 0, interval, true, 4, 0)) == State::S);                           // terminated
	std::printf("  combinations %u\n", n);
}

static void TestI1() {
	Case("I1: X + R + r + Sr + Sw + S + W + H = samples");
	std::mt19937 rng(20);
	for (int round = 0; round < 200; round++) {
		Agg      a;
		uint32_t samples = 1 + rng() % 400;
		for (uint32_t i = 0; i < samples; i++) {
			const auto s    = static_cast<State>(rng() % static_cast<uint32_t>(State::Count));
			uint8_t    kind = 0;
			if (s == State::H) {
				kind = static_cast<uint8_t>(1 + rng() % (static_cast<uint32_t>(Call::Count) - 1));
			} else if (s == State::W) {
				kind = static_cast<uint8_t>(1 + rng() % (static_cast<uint32_t>(Wait::Count) - 1));
			} else if (s == State::Sw) {
				kind = static_cast<uint8_t>(rng() % 80);
			}
			a.Add(Code(s, kind));
		}
		CHECK(a.Total() == samples);
	}
}

static void TestGaps() {
	Case("I2' and gap3p, sgap_max over (previous flip, flip]");
	const uint64_t P = kPeriodNs;
	{
		std::vector<uint64_t> t;
		for (uint64_t x = 5; x <= 100; x += 5) {
			t.push_back(x * 1000000);
		}
		const auto g = Gaps(t.data(), t.size(), 0, 100000000, P);
		CHECK(g.samples == 20);
		CHECK(g.i2_ok);
		CHECK(g.gap3p == 0);
		CHECK(g.sgap_max_ns == 5000000);
		CHECK(g.monotonic);
	}
	{
		// 9 samples in 100 ms: floor(100 / 10) = 10 -> I2' fails
		std::vector<uint64_t> t;
		for (uint64_t x = 10; x <= 90; x += 10) {
			t.push_back(x * 1000000);
		}
		const auto g = Gaps(t.data(), t.size(), 0, 100000000, P);
		CHECK(g.samples == 9);
		CHECK(!g.i2_ok);
		// exactly 10 samples -> ok
		t.push_back(95000000);
		CHECK(Gaps(t.data(), t.size(), 0, 100000000, P).i2_ok);
	}
	{
		// HOST_FREEZE: samples every 5 ms up to 35 ms, nothing until 112 ms, flip at 113 ms (RC1 scenario).
		std::vector<uint64_t> t = {5000000, 10000000, 15000000, 20000000, 25000000, 30000000, 35000000, 112000000};
		const auto            g = Gaps(t.data(), t.size(), 0, 113000000, P);
		CHECK(g.sgap_max_ns == 77000000);
		CHECK(g.gap3p == 1);
		CHECK(!g.i2_ok); // 8 < floor(113 / 10) = 11
	}
	{
		// gap exactly 3 P is not > 3 P; 3 P + 1 is
		std::vector<uint64_t> t = {15000000, 30000001};
		const auto            g = Gaps(t.data(), t.size(), 0, 35000000, P);
		CHECK(g.gap3p == 1);
	}
	{
		std::vector<uint64_t> t = {10000000, 9000000};
		CHECK(!Gaps(t.data(), t.size(), 0, 20000000, P).monotonic);
	}
}

static void TestI3() {
	Case("I3: other_us = sys_busy_us - proc_us (signed)");
	CHECK(OtherUs(1000, 300) == 700);
	CHECK(OtherUs(100, 300) == -200);
	CHECK(OtherUs(0, 0) == 0);
}

static void TestWindowSamples() {
	Case("window (previous flip, flip] from the history ring; instr_us");
	constexpr uint32_t H = 8;
	uint64_t           t[H] {};
	uint64_t           cost[H] {};
	uint8_t            kq[H] {};
	// 12 samples taken, every 10 ms from 10 ms; cost 100 us each; kq from 60 ms
	for (uint64_t h = 0; h < 12; h++) {
		t[h % H]    = (h + 1) * 10000000;
		cost[h % H] = 100000;
		kq[h % H]   = (h + 1) * 10 >= 60 ? 1 : 0;
	}
	std::vector<uint64_t> idx;
	uint64_t              instr = 0;
	uint32_t              kqn   = 0;
	bool                  ex    = false;
	WindowSamples(t, cost, kq, 12, H, 75000000, 115000000, 250000, &idx, &instr, &kqn, &ex);
	// samples 80, 90, 100, 110 ms
	CHECK(idx.size() == 4);
	CHECK(idx.front() == 7 && idx.back() == 10);
	CHECK(instr == 250000 + 4 * 100000);
	CHECK(kqn == 4);
	CHECK(!ex);
	// a window older than the ring holds -> exhausted (ring_drop)
	WindowSamples(t, cost, kq, 12, H, 5000000, 115000000, 0, &idx, &instr, &kqn, &ex);
	CHECK(ex);
	CHECK(idx.size() == H - 1 || idx.size() == H);
	// a sample exactly at the window start belongs to the previous window; exactly at the flip - to this one
	WindowSamples(t, cost, kq, 12, H, 80000000, 100000000, 0, &idx, &instr, &kqn, &ex);
	CHECK(idx.size() == 2); // 90, 100
}

static void TestRegistry() {
	Case("slot_full and torn (registry)");
	auto* r = new Registry;
	for (uint32_t i = 0; i < kSlots; i++) {
		CHECK(r->Allocate(1000 + i, nullptr, "guest", "x", static_cast<int32_t>(i)) == static_cast<int32_t>(i));
	}
	CHECK(r->slot_full.load() == 0);
	CHECK(r->Allocate(9999, nullptr, "guest", "y", 0) == -1);
	CHECK(r->slot_full.load() == 1);
	CHECK(r->count.load() == kSlots);
	r->WriteMark(3, MarkWord(State::W, static_cast<uint8_t>(Wait::Mutex)), 0x1234, 777, 9);
	MarkSnap s;
	CHECK(r->ReadMark(3, &s));
	CHECK(s.mark == MarkWord(State::W, static_cast<uint8_t>(Wait::Mutex)) && s.obj == 0x1234 && s.since == 777 && s.peer == 9);
	CHECK(r->torn.load() == 0);
	// a writer that never finishes (odd seqlock word) -> 3 attempts, then torn + 1
	r->slots[4].seq.store(7);
	CHECK(!r->ReadMark(4, &s));
	CHECK(r->torn.load() == 1);
	delete r;
}

static void TestRing() {
	Case("ring_drop and torn (wait ring)");
	auto*   w    = new WaitRing;
	uint64_t drop = 0;
	uint64_t torn = 0;
	for (uint32_t i = 0; i < 5000; i++) {
		WaitRec r;
		r.start_ns = i;
		r.end_ns   = i + 10000000;
		r.slot1    = 1 + static_cast<int32_t>(i % 200);
		r.waker1   = 2;
		r.kind     = static_cast<uint8_t>(Wait::Cond);
		w->Push(r);
	}
	std::vector<WaitRec> out;
	w->Drain(&out, &drop, &torn);
	CHECK(out.size() == kWaitRing);
	CHECK(drop == 5000 - kWaitRing);
	CHECK(torn == 0);
	CHECK(out.back().start_ns == 4999 && out.back().waker1 == 2 && out.back().kind == static_cast<uint8_t>(Wait::Cond));
	// nothing new -> nothing
	out.clear();
	w->Drain(&out, &drop, &torn);
	CHECK(out.empty());
	// a record whose write is in progress (odd word for its index): F20j2 RC4 - the drain stops there and does not count
	// it torn (F20j counted torn here); once the write is finished the next drain takes it
	WaitRec r;
	r.start_ns = 77;
	w->Push(r);
	const auto i = w->wpos.load() - 1;
	w->e[i % kWaitRing].seq.store(2 * i + 1);
	w->Drain(&out, &drop, &torn);
	CHECK(out.empty());
	CHECK(torn == 0);
	CHECK(w->rpos == i);
	w->e[i % kWaitRing].seq.store(2 * i + 2);
	w->Drain(&out, &drop, &torn);
	CHECK(out.size() == 1 && out[0].start_ns == 77);
	CHECK(torn == 0);
	delete w;
}

static Report MakeReport() {
	Report r;
	r.n            = 3193;
	r.dt_us        = 180215;
	r.win_start_ns = 1000000000;
	r.win_end_ns   = 1180215000;
	r.instr_us     = 4321;
	std::vector<uint64_t> t;
	for (uint64_t x = 1; x <= 36; x++) {
		t.push_back(r.win_start_ns + x * 5000000);
	}
	r.gaps        = Gaps(t.data(), t.size(), r.win_start_ns, r.win_end_ns, kPeriodNs);
	r.kstate      = 1;
	r.kq          = 28;
	r.proc_us     = 515625;
	r.sys_busy_us = 900000;
	r.sys_idle_us = 1900000;
	r.ncpu        = 16;
	r.flip_slot1  = 3;
	r.flip_gid    = 23;
	r.flip_src    = 2;
	r.lat_us      = 157043;
	r.vo_slot1    = 1;
	r.gpu_slot1   = 2;
	const char* names[] = {"Present", "Gpu", "DrawThread", "Physics_ATQT", "%evil", "Vulkan pipeline cache: saved", "BvhLoopCapTrip:"};
	for (int i = 0; i < 7; i++) {
		ThreadRow row;
		row.slot1  = i + 1;
		row.gid    = i >= 2 ? 20 + i : 0;
		row.os_tid = 4000 + static_cast<uint32_t>(i);
		row.name   = SafeName(names[i]);
		row.role   = i == 0 ? "Present" : (i == 1 ? "Gpu" : "guest");
		for (int k = 0; k < 36; k++) {
			if (i == 0) {
				row.agg.Add(Code(State::H, static_cast<uint8_t>(Call::Present)));
			} else if (i == 2) {
				row.agg.Add(Code(State::W, static_cast<uint8_t>(Wait::Cond)));
			} else {
				row.agg.Add(Code(k % 2 == 0 ? State::Sw : State::S, 6));
			}
		}
		row.cpu_us = 1000 * i;
		r.threads.push_back(row);
	}
	WaitRec w;
	w.start_ns = r.win_start_ns + 20000000;
	w.end_ns   = r.win_end_ns - 1000000;
	w.slot1    = 3;
	w.waker1   = 4;
	w.kind     = static_cast<uint8_t>(Wait::Cond);
	r.waits.push_back(w);
	CpuRow c;
	c.os_tid = 4001;
	c.slot1  = 2;
	c.name   = "Gpu";
	c.cpu_us = 42602;
	r.cpu.push_back(c);
	return r;
}

static bool StartsWith(const std::string& s, const char* p) {
	return s.compare(0, std::strlen(p), p) == 0;
}

static std::vector<std::string> Lines(const std::string& text) {
	std::vector<std::string> out;
	size_t                   a = 0;
	while (a < text.size()) {
		const auto b = text.find('\n', a);
		out.push_back(text.substr(a, (b == std::string::npos ? text.size() : b) - a));
		a = b == std::string::npos ? text.size() : b + 1;
	}
	return out;
}

static bool IsHex(char c) {
	return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

static void TestFormat() {
	Case("print: DiagB32 lines (RC13: prefix at column 0, no leading %, no hexadecimal first field)");
	auto     r = MakeReport();
	Counters c;
	const auto text  = Format(&r, &c);
	const auto lines = Lines(text);
	std::printf("%s", text.c_str());
	CHECK(!lines.empty());
	int n_main = 0;
	int n_t    = 0;
	int n_w    = 0;
	int n_c    = 0;
	int n_x    = 0;
	for (const auto& l: lines) {
		CHECK(StartsWith(l, "DiagB32"));
		CHECK(l[0] != '%' && l[0] != ' ');
		const auto colon = l.find(": ");
		CHECK(colon != std::string::npos && colon <= 10);
		const auto first = l.substr(colon + 2);
		CHECK(StartsWith(first, "n=") || StartsWith(first, "mode="));
		CHECK(!(IsHex(first[0]) && first.size() > 1 && first[1] == ':'));
		CHECK(l.find("Vulkan pipeline cache: saved") == std::string::npos);
		CHECK(l.find("BvhLoopCapTrip:") == std::string::npos);
		n_main += StartsWith(l, "DiagB32: ") ? 1 : 0;
		n_t += StartsWith(l, "DiagB32-t: ") ? 1 : 0;
		n_w += StartsWith(l, "DiagB32-w: ") ? 1 : 0;
		n_c += StartsWith(l, "DiagB32-c: ") ? 1 : 0;
		n_x += StartsWith(l, "DiagB32-x: ") ? 1 : 0;
	}
	CHECK(n_main == 1 && n_t == 7 && n_w == 1 && n_c == 1 && n_x == 1);
	CHECK(text.find(" instr_us=4321 ") != std::string::npos);
	CHECK(text.find(" other_us=384375 ") != std::string::npos); // I3: 900000 - 515625
	CHECK(text.find(" flip_slot=2 flip_tid=23 flip_src=gpu ") != std::string::npos);
	CHECK(text.find("name=_evil") != std::string::npos);
	// I1 on every printed -t line
	for (const auto& l: lines) {
		if (!StartsWith(l, "DiagB32-t: ")) {
			continue;
		}
		const auto num = [&](const char* key) {
			const auto p = l.find(std::string(" ") + key + "=");
			return p == std::string::npos ? -1L : std::strtol(l.c_str() + p + std::strlen(key) + 2, nullptr, 10);
		};
		const auto list = [&](const char* key) {
			const auto p = l.find(std::string(" ") + key + "=");
			long       s = 0;
			if (p == std::string::npos) {
				return -1L;
			}
			auto       q   = p + std::strlen(key) + 2;
			const auto end = l.find(' ', q);
			const auto v   = l.substr(q, end - q);
			if (v == "-") {
				return 0L;
			}
			size_t a = 0;
			while (a < v.size()) {
				const auto colon = v.find(':', a);
				const auto comma = v.find(',', a);
				s += std::strtol(v.c_str() + colon + 1, nullptr, 10);
				a = comma == std::string::npos ? v.size() : comma + 1;
			}
			return s;
		};
		const long sum = num("X") + num("R") + num("r") + num("Sr") + num("Sw") + num("S") + list("W") + list("H");
		CHECK(sum == 36);
		CHECK(list("SwR") == num("Sw"));
	}
	// header line form
	const auto h = HeaderLine(16, 1, 10739);
	CHECK(StartsWith(h, "DiagB32: mode=1 period_us=5000 print_us=100000 "));
	CHECK(h.find(" kstate=1 kq_us=10739 kq_budget_div=10 kq_near_us=60000\n") != std::string::npos);
	// F20j2: the main line carries kq_n, kq_us, m5r_us
	CHECK(text.find(" kq=28 kq_n=0 kq_us=0 m5r_us=0 ") != std::string::npos);
}

static void TestMandatoryAndCuts() {
	Case("RC2: mandatory -t lines, lines_cut, others_cut, sgap_bad");
	{
		auto r = MakeReport();
		MarkMandatory(&r);
		CHECK(r.threads[0].must);  // present thread
		CHECK(r.threads[1].must);  // GuestGpu
		CHECK(r.threads[2].must);  // flip_slot
		CHECK(r.threads[3].must);  // waker of the flip thread's -w record
		CHECK(!r.threads[4].must); // nobody
		Counters c;
		(void)Format(&r, &c);
		CHECK(c.lines_cut == 0 && c.others_cut == 0 && c.sgap_bad == 0 && c.w_cut == 0);
	}
	{
		// 100 threads with R >= 10 % -> mandatory; cap 96 -> lines_cut 4; 30 idle -> others_cut 6
		Report r = MakeReport();
		r.threads.clear();
		r.waits.clear();
		for (int i = 0; i < 130; i++) {
			ThreadRow row;
			row.slot1 = 10 + i;
			row.name  = "t";
			row.role  = "guest";
			for (int k = 0; k < 36; k++) {
				row.agg.Add(Code(i < 100 && k < 4 ? State::R : State::S, 0));
			}
			r.threads.push_back(row);
		}
		Counters c;
		const auto text = Format(&r, &c);
		CHECK(c.lines_cut == 4);
		CHECK(c.others_cut == 6);
		int n_t = 0;
		for (const auto& l: Lines(text)) {
			n_t += StartsWith(l, "DiagB32-t: ") ? 1 : 0;
		}
		CHECK(n_t == 96 + 24);
	}
	{
		// I2' broken -> sgap_bad + 1; non-monotonic -> + 1
		Report r = MakeReport();
		r.gaps.i2_ok = false;
		Counters c;
		(void)Format(&r, &c);
		CHECK(c.sgap_bad == 1);
		r.gaps.i2_ok     = true;
		r.gaps.monotonic = false;
		(void)Format(&r, &c);
		CHECK(c.sgap_bad == 2);
	}
	{
		// gap3p printed in the DiagB32: and -x lines
		Report                r = MakeReport();
		std::vector<uint64_t> t = {r.win_start_ns + 5000000, r.win_start_ns + 100000000};
		r.gaps                  = Gaps(t.data(), t.size(), r.win_start_ns, r.win_end_ns, kPeriodNs);
		Counters   c;
		const auto text = Format(&r, &c);
		CHECK(r.gaps.gap3p == 2);
		CHECK(text.find(" gap3p=2 ") != std::string::npos);
		// F20j3 (Z1): the -x line now ends with ring_hold / ring_hold_w after gap3p
		CHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0\n") != std::string::npos);
	}
	{
		// -w cap 64: the chain records are never cut, the rest by overlap
		Report r = MakeReport();
		for (int i = 0; i < 80; i++) {
			WaitRec w;
			w.start_ns = r.win_start_ns + 1000000 * static_cast<uint64_t>(i);
			w.end_ns   = r.win_end_ns;
			w.slot1    = 5;
			w.kind     = static_cast<uint8_t>(Wait::Sleep);
			r.waits.push_back(w);
		}
		Counters   c;
		const auto text = Format(&r, &c);
		CHECK(c.w_cut == 81 - kWLinesCap);
		CHECK(text.find("slot=2 tid=22 kind=cond") != std::string::npos); // the flip thread's record kept
	}
}

// ---------------------------------------------------------------------------------------------------------------------
// F20j2 (item 552(v)(1)): the sampler loop with the real schedule (KqSchedule, NextBegin) and a cost model - a sample
// costs kBase, with the kernel query kBase + K; the sample time is after the query (RC2); flips every dt from start0,
// processed before the next sample begins (the flip event wakes the sampler; a flip during a sample - after it).
// windows_before = 0: the measured window is the first one with a query (last cost unknown); 3: steady state.
struct SimOut {
	uint32_t samples  = 0;
	uint32_t need     = 0;
	uint32_t kq_n     = 0;
	uint64_t instr_ns = 0;
	bool     i2       = false;
	int64_t  dt_minus = 0; // dt - instr_us, ns
};

static SimOut SimWindow(uint64_t dt_ns, uint64_t k_ns, int windows_before, uint64_t phase_ns) {
	constexpr uint64_t kBase  = 50000; // a sample without the kernel query, 0.05 ms [I] (= f20k_model.py BASE)
	const uint64_t     start0 = 1000000000;
	const int          nwin   = windows_before + 1;
	struct Smp {
		uint64_t ts;
		uint64_t cost;
		uint64_t q;
	};
	std::vector<Smp> all;
	KqSchedule       s;
	s.NewWindow(start0, 0);
	int            next_flip = 1;
	uint64_t       begin     = start0 + phase_ns;
	const uint64_t last      = start0 + static_cast<uint64_t>(nwin) * dt_ns;
	while (begin < last + 50000000) {
		while (next_flip <= nwin && start0 + static_cast<uint64_t>(next_flip) * dt_ns <= begin) {
			const uint64_t f       = start0 + static_cast<uint64_t>(next_flip) * dt_ns;
			uint64_t       carried = 0;
			for (auto it = all.rbegin(); it != all.rend() && it->ts > f; ++it) {
				carried += it->q;
			}
			s.NewWindow(f, carried);
			next_flip++;
		}
		uint64_t q = 0;
		if (s.Due(begin)) {
			q = k_ns;
			s.Done(q);
		}
		all.push_back({begin + q, kBase + q, q});
		begin = NextBegin(begin, begin + kBase + q);
	}
	const uint64_t        ws = last - dt_ns;
	std::vector<uint64_t> t;
	SimOut                o;
	for (const auto& x: all) {
		if (x.ts > ws && x.ts <= last) {
			t.push_back(x.ts);
			o.instr_ns += x.cost;
			o.kq_n += x.q != 0 ? 1 : 0;
		}
	}
	const auto g = Gaps(t.data(), t.size(), ws, last, kPeriodNs);
	o.samples    = g.samples;
	o.need       = static_cast<uint32_t>(dt_ns / (2 * kPeriodNs));
	o.i2         = g.i2_ok && g.monotonic;
	o.dt_minus   = static_cast<int64_t>(dt_ns) - static_cast<int64_t>(o.instr_ns);
	return o;
}

static void TestSchedule() {
	Case("F20j2 RC1: kernel query schedule (>= 40 ms, <= 10 % of the window, absolute period), item 552(v)(1)");
	// KqSchedule letter: >= 40 ms; (window queries + last cost) * 10 <= time since the flip; first query - at 40 ms.
	KqSchedule s;
	CHECK(!s.Due(500000000)); // no flip yet
	s.NewWindow(1000000000, 0);
	CHECK(!s.Due(1039999999));
	CHECK(s.Due(1040000000)); // first query of the process: last cost unknown
	s.Done(10000000);
	CHECK(!s.Due(1199999999)); // (10 + 10) * 10 = 200 ms
	CHECK(s.Due(1200000000));
	s.NewWindow(1300000000, 0);
	CHECK(!s.Due(1399999999)); // (0 + 10) * 10 = 100 ms
	CHECK(s.Due(1400000000));
	s.NewWindow(1500000000, 3000000); // a query of 3 ms already after the flip
	CHECK(!s.Due(1629999999));        // (3 + 10) * 10 = 130 ms
	CHECK(s.Due(1630000000));
	// absolute period: P after the begin; a long sample is followed at once
	CHECK(NextBegin(1000000000, 1000050000) == 1005000000);
	CHECK(NextBegin(1000000000, 1010050000) == 1010050000);
	// item 552(v)(1): window 120 ms at K = 10 ms - dt - instr >= 100 ms and I2'; window 200 ms - I2' at 10 and 20 ms,
	// >= 1 query at 10 ms. Both regimes, two sample phases.
	for (uint64_t phase: {500000ull, 4500000ull}) {
		for (int before: {0, 3}) {
			const auto a = SimWindow(120000000, 10000000, before, phase);
			CHECK(a.dt_minus >= 100000000);
			CHECK(a.i2);
			const auto b = SimWindow(200000000, 10000000, before, phase);
			CHECK(b.i2);
			CHECK(b.kq_n >= 1);
			const auto c = SimWindow(200000000, 20000000, before, phase);
			CHECK(c.i2);
		}
	}
	// the table of the report f20j2.md (model, phase 2.5 ms): instr_us for windows 100..240 ms at K 3.2 / 10.7 / 13.3 / 20 ms
	for (uint64_t k: {3200000ull, 10700000ull, 13300000ull, 20000000ull}) {
		for (uint64_t dt: {100000000ull, 115000000ull, 120000000ull, 150000000ull, 200000000ull, 240000000ull}) {
			for (int before: {0, 3}) {
				const auto o = SimWindow(dt, k, before, 2500000);
				std::printf("  sched K_ms=%.1f dt_ms=%llu regime=%s samples=%u need=%u i2=%d kq_n=%u instr_us=%llu"
				            " dt_minus_instr_us=%lld instr_made=%d\n",
				            static_cast<double>(k) / 1e6, static_cast<unsigned long long>(dt / 1000000u),
				            before == 0 ? "first" : "steady", o.samples, o.need, o.i2 ? 1 : 0, o.kq_n,
				            static_cast<unsigned long long>(o.instr_ns / 1000u), static_cast<long long>(o.dt_minus / 1000),
				            o.dt_minus < 100000000 ? 1 : 0);
				// item 552(d) F20k2: at K <= 13.3 ms INSTR_MADE only for windows <= 115 ms
				if (k <= 13300000 && dt > 115000000) {
					CHECK(o.dt_minus >= 100000000);
				}
			}
		}
	}
}

static void TestNearest() {
	Case("F20j2: S split by the nearest snapshot of the same window <= 60 ms");
	// samples every 5 ms from 5 to 150 ms; snapshots at sample 8 (t 45, snapshot 44) and 18 (t 95, snapshot 94)
	std::vector<uint64_t> t;
	std::vector<uint8_t>  kq;
	std::vector<uint64_t> kt;
	for (uint64_t x = 1; x <= 30; x++) {
		t.push_back(x * 5000000);
		kq.push_back(x == 9 || x == 19 ? 1 : 0);
		kt.push_back(x == 9 ? 44000000 : (x == 19 ? 94000000 : 0));
	}
	std::vector<int32_t> out(t.size(), -2);
	NearestSnapshot(t.data(), kq.data(), kt.data(), t.size(), kKqNearNs, out.data());
	CHECK(out[8] == 8 && out[18] == 18); // own snapshot
	CHECK(out[0] == 8);                  // t 5: |5 - 44| = 39
	CHECK(out[13] == 18);                // t 70: 26 vs 24
	CHECK(out[12] == 8);                 // t 65: 21 vs 29
	CHECK(out[29] == 18);                // t 150: 56 <= 60
	std::vector<uint64_t> t2 = {5000000, 10000000, 80000000};
	std::vector<uint8_t>  q2 = {0, 1, 0};
	std::vector<uint64_t> k2 = {0, 9000000, 0};
	std::vector<int32_t>  o2(3, -2);
	NearestSnapshot(t2.data(), q2.data(), k2.data(), 3, kKqNearNs, o2.data());
	CHECK(o2[0] == 1 && o2[1] == 1);
	CHECK(o2[2] == -1); // 71 ms > 60
	// equal distance - the earlier snapshot
	std::vector<uint64_t> t3 = {10000000, 20000000, 30000000};
	std::vector<uint8_t>  q3 = {1, 0, 1};
	std::vector<uint64_t> k3 = {10000000, 0, 30000000};
	std::vector<int32_t>  o3(3, -2);
	NearestSnapshot(t3.data(), q3.data(), k3.data(), 3, kKqNearNs, o3.data());
	CHECK(o3[1] == 0);
}

static std::string Field(const std::string& text, const char* key) {
	const auto p = text.find(std::string(" ") + key + "=");
	if (p == std::string::npos) {
		return "?";
	}
	const auto a = p + std::strlen(key) + 2;
	const auto b = text.find_first_of(" \n", a);
	return text.substr(a, b - a);
}

static void TestWindowDelta() {
	Case("F20j2 RC3: zero invariants per window (_w) - an event in window k, a clean window k+1");
	Counters c;
	// window k: one torn read, one ring drop, one request miss, I2' broken (sgap_bad)
	auto r = MakeReport();
	r.gaps.i2_ok = false;
	c.torn       = 1;
	c.ring_drop  = 1;
	c.req_miss   = 1;
	const auto k = Format(&r, &c);
	c.Rebase();
	CHECK(Field(k, "torn") == "1" && Field(k, "torn_w") == "1");
	CHECK(Field(k, "ring_drop") == "1" && Field(k, "ring_drop_w") == "1");
	CHECK(Field(k, "sgap_bad") == "1" && Field(k, "sgap_bad_w") == "1");
	CHECK(Field(k, "req_miss") == "1" && Field(k, "req_miss_w") == "1");
	CHECK(Field(k, "sub_miss_w") == "0" && Field(k, "slot_full_w") == "0" && Field(k, "lines_cut_w") == "0");
	// window k+1: nothing new - the cumulative values stay, every _w is 0
	auto r2 = MakeReport();
	r2.n    = 3194;
	const auto k1 = Format(&r2, &c);
	c.Rebase();
	CHECK(Field(k1, "torn") == "1" && Field(k1, "torn_w") == "0");
	CHECK(Field(k1, "ring_drop") == "1" && Field(k1, "ring_drop_w") == "0");
	CHECK(Field(k1, "sgap_bad") == "1" && Field(k1, "sgap_bad_w") == "0");
	CHECK(Field(k1, "req_miss") == "1" && Field(k1, "req_miss_w") == "0");
	CHECK(Field(k1, "slot_full_w") == "0" && Field(k1, "lines_cut_w") == "0" && Field(k1, "sub_miss_w") == "0");
	// a short window between (not printed, rebased by the sampler): its event is not in the next printed window's _w
	c.sub_miss = 2;
	c.Rebase();
	auto       r3 = MakeReport();
	const auto k2 = Format(&r3, &c);
	CHECK(Field(k2, "sub_miss") == "2" && Field(k2, "sub_miss_w") == "0");
}

static void TestDrainPreempted() {
	Case("F20j2 RC4: drain with a writer preempted between Reserve and the final word");
	auto*    w    = new WaitRing;
	uint64_t drop = 0;
	uint64_t torn = 0;
	const auto rec = [](uint64_t start) {
		WaitRec r;
		r.start_ns = start;
		r.end_ns   = start + 20000000;
		r.slot1    = 5;
		r.waker1   = 3;
		r.kind     = static_cast<uint8_t>(Wait::Cond);
		return r;
	};
	w->Push(rec(0));
	w->Push(rec(1));
	const auto i = w->Reserve(); // preempted writer: the position is taken, nothing written yet
	w->Push(rec(3));
	std::vector<WaitRec> out;
	w->Drain(&out, &drop, &torn);
	CHECK(out.size() == 2 && out[0].start_ns == 0 && out[1].start_ns == 1);
	CHECK(torn == 0 && drop == 0 && w->rpos == i);
	// the writer resumed and wrote its first word only (in progress) - still waiting, nothing lost
	w->e[i % kWaitRing].seq.store(2 * i + 1);
	out.clear();
	w->Drain(&out, &drop, &torn);
	CHECK(out.empty() && torn == 0 && w->rpos == i);
	// the write finishes - the next drain takes it and the record behind it, in order
	w->Write(i, rec(2));
	out.clear();
	w->Drain(&out, &drop, &torn);
	CHECK(out.size() == 2 && out[0].start_ns == 2 && out[1].start_ns == 3 && out[0].waker1 == 3);
	CHECK(torn == 0 && drop == 0);
	// a position overwritten by a later lap after the drain read wpos (word of index + kWaitRing) - torn, the drain goes on
	const auto j = w->Reserve();
	w->Push(rec(5));
	w->e[j % kWaitRing].seq.store(2 * (j + kWaitRing) + 1);
	out.clear();
	w->Drain(&out, &drop, &torn);
	CHECK(torn == 1);
	CHECK(out.size() == 1 && out[0].start_ns == 5);
	CHECK(w->rpos == w->wpos.load());
	delete w;
}

static void TestASubmit() {
	Case("F20j2 RC5: the async submitter's -t line is mandatory in a window with H:qlock / H:qsubmit");
	auto      r = MakeReport();
	ThreadRow a;
	a.slot1  = 20;
	a.os_tid = 5000;
	a.name   = "ASubmit";
	a.role   = "ASubmit";
	for (int k = 0; k < 36; k++) {
		a.agg.Add(Code(State::S, 0));
	}
	r.threads.push_back(a);
	MarkMandatory(&r);
	CHECK(!r.threads.back().must); // no qlock / qsubmit sample
	auto b = MakeReport();
	a.agg  = Agg {};
	for (int k = 0; k < 36; k++) {
		a.agg.Add(k == 7 ? Code(State::H, static_cast<uint8_t>(Call::QSubmit)) : Code(State::S, 0));
	}
	b.threads.push_back(a);
	MarkMandatory(&b);
	CHECK(b.threads.back().must);
	auto c = MakeReport();
	a.agg  = Agg {};
	for (int k = 0; k < 36; k++) {
		a.agg.Add(k == 3 ? Code(State::H, static_cast<uint8_t>(Call::QLock)) : Code(State::S, 0));
	}
	c.threads.push_back(a);
	Counters   cn;
	const auto text = Format(&c, &cn);
	CHECK(text.find("name=ASubmit role=ASubmit must=1 ") != std::string::npos);
	CHECK(text.find("H=qlock:1 ") != std::string::npos);
}

static void TestSig() {
	Case("waker word: SigWaker against the wait start");
	const uint64_t t      = 123456789000ull;
	const uint64_t packed = ((t >> 10u) << 16u) | 7u;
	CHECK(SigWaker(packed, t - 5000000) == 7);   // signal after the wait began
	CHECK(SigWaker(packed, t + 50000000) == 0);  // signal older than the wait
	CHECK(SigWaker(0, 1) == 0);
}

// ---------------------------------------------------------------------------------------------------------------------
// F20j3 (HPP-646; ROADMAP s122 item 574(g))
// ---------------------------------------------------------------------------------------------------------------------
static void TestKinds() {
	Case("F20j3 wait kinds: names unique, older numbers kept, EMU_WAIT / guest HLE partition, mutex-like");
	std::vector<std::string> names;
	for (uint8_t k = 1; k < static_cast<uint8_t>(Wait::Count); k++) {
		const std::string n = WaitName(k);
		CHECK(n != "?" && n != "-");
		CHECK(std::find(names.begin(), names.end(), n) == names.end());
		names.push_back(n);
	}
	CHECK(static_cast<uint8_t>(Wait::GpuRegmem) == 9 && std::string(WaitName(9)) == "gpu_regmem");
	CHECK(static_cast<uint8_t>(Wait::EmuMutex) == 10 && std::string(WaitName(10)) == "emu_mutex");
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::GpuWait))) == "gpu_wait");
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::FlipReq))) == "flip_req");
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::Rwlock))) == "rwlock");
	for (uint8_t k = 1; k < static_cast<uint8_t>(Wait::Count); k++) {
		const bool emu = k >= static_cast<uint8_t>(Wait::EmuMutex) && k <= static_cast<uint8_t>(Wait::Av);
		CHECK(IsEmuWait(k) == emu);
	}
	CHECK(!IsEmuWait(static_cast<uint8_t>(Wait::Vblank)) && !IsEmuWait(static_cast<uint8_t>(Wait::Cond)));
	CHECK(MutexLike(static_cast<uint8_t>(Wait::Mutex)) && MutexLike(static_cast<uint8_t>(Wait::EmuMutex)));
	CHECK(MutexLike(static_cast<uint8_t>(Wait::Spin)) && !MutexLike(static_cast<uint8_t>(Wait::GpuWait)));
	CHECK(!MutexLike(static_cast<uint8_t>(Wait::Cond)) && !MutexLike(static_cast<uint8_t>(Wait::FlipDone)));
}

static void TestRingHold() {
	Case("F20j3 Z1: ring_hold - the positions a drain left at an unfinished write; -x ring_hold / ring_hold_w");
	auto*   w = new WaitRing;
	WaitRec rec;
	rec.start_ns = 1;
	rec.end_ns   = 20000001;
	rec.slot1    = 1;
	rec.peer1    = 3;
	rec.kind     = static_cast<uint8_t>(Wait::GpuWait);
	w->Push(rec);
	const auto pending = w->Reserve(); // a writer preempted after Reserve
	w->Push(rec);
	w->Push(rec);
	std::vector<WaitRec> out;
	uint64_t             drop = 0;
	uint64_t             torn = 0;
	uint64_t             held = 0;
	w->Drain(&out, &drop, &torn, &held);
	CHECK(out.size() == 1 && held == 3); // the unfinished position and the two after it
	CHECK(!out.empty() && out[0].peer1 == 3 && out[0].kind == static_cast<uint8_t>(Wait::GpuWait));
	w->Write(pending, rec);
	out.clear();
	w->Drain(&out, &drop, &torn, &held);
	CHECK(out.size() == 3 && held == 3 && torn == 0 && drop == 0);
	delete w;
	Counters c;
	c.ring_hold = 5;
	c.Rebase();
	c.ring_hold = 8;
	auto       r    = MakeReport();
	const auto text = Format(&r, &c);
	CHECK(Field(text, "ring_hold") == "8" && Field(text, "ring_hold_w") == "3");
	CHECK(text.find(" gap3p=0 ring_hold=8 ring_hold_w=3\n") != std::string::npos); // at the end of the -x line
}

static void TestPeerFields() {
	Case("F20j3 (2), (d): the -w line carries the record's peer; the peer's -t line is mandatory");
	auto r           = MakeReport();
	r.waits[0].peer1 = 5; // slot index 4, "%evil" (gid 24): neither R nor a waker - mandatory only as the peer
	Counters   c;
	const auto text = Format(&r, &c);
	std::string wline;
	for (const auto& l: Lines(text)) {
		if (StartsWith(l, "DiagB32-w: ")) {
			wline = l;
		}
	}
	CHECK(wline.find(" open=0 peer=4 peer_tid=24") != std::string::npos);
	CHECK(text.find("slot=4 tid=24 os_tid=4004 name=_evil role=guest must=1 ") != std::string::npos);
	auto       r0    = MakeReport(); // without a peer the same row is not mandatory
	Counters   c0;
	const auto text0 = Format(&r0, &c0);
	CHECK(text0.find("slot=4 tid=24 os_tid=4004 name=_evil role=guest must=0 ") != std::string::npos);
	CHECK(text0.find(" peer=-1 peer_tid=0") != std::string::npos);
}

// The sampler model of item 574(g)(4): a loop with the absolute period P (Core::NextBegin) for 400 ms; "inline" - an
// 80 ms refresh on the loop thread every 100 ms (the F20j2 form); "async" - the same refresh on Core::AsyncRefresh.
static GapStats M5Model(bool async_mode, uint64_t* work_ns, uint64_t* runs) {
	using Clock     = std::chrono::steady_clock;
	const auto ns   = [] { return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count()); };
	const auto work = [](void*) { std::this_thread::sleep_for(std::chrono::milliseconds(80)); };
	AsyncRefresh refresh;
	if (async_mode) {
		refresh.Start(+work, nullptr, 20000000);
	}
	std::vector<uint64_t> t;
	const uint64_t        start = ns();
	uint64_t              next_refresh = start + 100000000;
	uint64_t              begin        = start;
	for (;;) {
		const auto now = ns();
		if (now >= start + 400000000) {
			break;
		}
		if (now >= begin) {
			t.push_back(now);
			if (!async_mode && now >= next_refresh) {
				work(nullptr);
				next_refresh = now + 100000000;
			}
			begin = NextBegin(now, ns());
		}
		std::this_thread::sleep_for(std::chrono::microseconds(500));
	}
	const uint64_t end = ns();
	if (async_mode) {
		refresh.Stop();
	}
	*work_ns = refresh.TakeWorkNs();
	*runs    = refresh.Runs();
	return Gaps(t.data(), t.size(), start, end, kPeriodNs);
}

static void TestM5Async() {
	Case("F20j3 (4): an 80 ms M5 refresh off the sampler thread makes no gap of samples (model; control - inline)");
	uint64_t   work_a = 0;
	uint64_t   runs_a = 0;
	uint64_t   work_i = 0;
	uint64_t   runs_i = 0;
	const auto ga     = M5Model(true, &work_a, &runs_a);
	const auto gi     = M5Model(false, &work_i, &runs_i);
	std::printf("  m5 model: async sgap_max_us=%llu samples=%u runs=%llu work_us=%llu; inline sgap_max_us=%llu samples=%u\n",
	            static_cast<unsigned long long>(ga.sgap_max_ns / 1000u), ga.samples, static_cast<unsigned long long>(runs_a),
	            static_cast<unsigned long long>(work_a / 1000u), static_cast<unsigned long long>(gi.sgap_max_ns / 1000u),
	            gi.samples);
	CHECK(ga.sgap_max_ns < 40000000);  // the 80 ms refresh does not show in the gaps (half its cost as the bound)
	CHECK(gi.sgap_max_ns >= 80000000); // control: the same refresh on the sampler thread is a gap >= its cost
	CHECK(runs_a >= 2 && work_a >= runs_a * 75000000); // the refresh did run, its time is taken for instr_us (RC9)
	CHECK(ga.monotonic && gi.monotonic);
}

static std::vector<WaitRec> RecordsOf(int32_t slot1) {
	std::vector<WaitRec> all;
	Test::DrainWaits(&all);
	std::vector<WaitRec> out;
	for (const auto& w: all) {
		if (w.slot1 == slot1) {
			out.push_back(w);
		}
	}
	return out;
}

static void TestWaitLoopRuntime() {
	Case("F20j3 (3): a wait loop with short wakeups under one mark - W >= 50 % of samples, one -w record, waker, peer");
	Test::InitRuntime();
	for (int per_call = 0; per_call < 2; per_call++) {
		Common::Mutex         m;
		Common::CondVar       cv;
		bool                  flag = false;
		std::atomic<int32_t>  w_slot {0};
		std::atomic<int32_t>  s_slot {0};
		std::atomic<bool>     waiting {false};
		std::atomic<bool>     done {false};
		std::atomic<uint32_t> wakeups {0};
		// The signaller wakes the waiter every 2 ms for 60 ms without the condition (short wakeups; timed by the clock,
		// not by sleep - the Windows sleep granularity is 15.6 ms), then sets it. It is the last signaller and the peer.
		std::thread           sig([&] {
            RegisterRole("TestS");
            s_slot.store(SelfSlotIfRegistered());
            while (!waiting.load()) {
                std::this_thread::yield();
            }
            const auto t0 = std::chrono::steady_clock::now();
            auto       next = t0;
            while (std::chrono::steady_clock::now() - t0 < std::chrono::milliseconds(60)) {
                next += std::chrono::milliseconds(2);
                while (std::chrono::steady_clock::now() < next) {
                    std::this_thread::yield();
                }
                Common::LockGuard lock(m);
                cv.Signal();
            }
            Common::LockGuard lock(m);
            flag = true;
            cv.Signal();
        });
		std::thread           wt([&] {
            RegisterRole("TestW");
            w_slot.store(SelfSlotIfRegistered());
            while (s_slot.load() == 0) {
                std::this_thread::yield();
            }
            Common::LockGuard lock(m);
            Mark              loop;
            if (per_call == 0) { // the F20j3 form: one mark over the loop
                loop.BeginWReg(Wait::GpuWait, &cv, s_slot.load(), 0);
            }
            waiting.store(true);
            while (!flag) {
                Mark call; // the control: a mark per short wait
                if (per_call == 1) {
                    call.BeginWReg(Wait::GpuWait, &cv, s_slot.load(), 0);
                }
                cv.Wait(&m); // woken every 2 ms (as by the 10 ms poll of CondVar::Wait in the game)
                if (call.Active()) {
                    call.End(cv.B32Waker(call.SinceNs()), false);
                }
                wakeups.fetch_add(1);
            }
            if (loop.Active()) {
                loop.End(cv.B32Waker(loop.SinceNs()), false);
            }
            done.store(true);
        });
		uint32_t n = 0;
		uint32_t w = 0;
		while (!waiting.load()) {
			std::this_thread::yield();
		}
		auto next = std::chrono::steady_clock::now();
		while (!done.load()) {
			MarkSnap s;
			if (Test::ReadSlotMark(w_slot.load(), &s)) {
				n++; // a short wakeup gives r (cpu > 0) - the mark wins: H > W > R > r
				w += CodeState(Classify(s.mark, 200000, 1000000, false, 0, 0)) == State::W ? 1 : 0;
			}
			next += std::chrono::milliseconds(1); // a sample every 1 ms by the clock
			while (std::chrono::steady_clock::now() < next && !done.load()) {
				std::this_thread::yield();
			}
		}
		sig.join();
		wt.join();
		const auto recs = RecordsOf(w_slot.load());
		std::printf("  loop per_call=%d: samples=%u W=%u wakeups=%u records=%zu\n", per_call, n, w, wakeups.load(), recs.size());
		CHECK(wakeups.load() >= 10);
		if (per_call == 0) {
			CHECK(n >= 10 && w * 2 >= n);
			CHECK(recs.size() == 1);
			if (recs.size() == 1) {
				CHECK(recs[0].kind == static_cast<uint8_t>(Wait::GpuWait));
				CHECK(recs[0].waker1 == s_slot.load() && recs[0].peer1 == s_slot.load());
				CHECK(recs[0].end_ns - recs[0].start_ns >= 50000000);
			}
		} else {
			CHECK(recs.empty()); // control: 2 ms waits are below the 10 ms record threshold - the loop is lost
		}
	}
}

static void TestEmuMutexRuntime() {
	Case("F20j3 (1): contended Common::Mutex and TrackedMutex - W:emu_mutex, waker and peer = the owner");
	Test::InitRuntime();
	Common::Mutex             m;
	TrackedMutex<std::mutex>  tm;
	std::atomic<int>          phase {0};
	std::atomic<int32_t>      a_slot {0};
	std::atomic<int32_t>      b_slot {0};
	std::thread               a([&] {
        RegisterRole("TestA");
        a_slot.store(SelfSlotIfRegistered());
        m.Lock();
        tm.lock();
        phase.store(1);
        std::this_thread::sleep_for(std::chrono::milliseconds(40));
        tm.unlock();
        std::this_thread::sleep_for(std::chrono::milliseconds(40));
        m.Unlock();
    });
	std::thread               b([&] {
        RegisterRole("TestB");
        b_slot.store(SelfSlotIfRegistered());
        while (phase.load() == 0) {
            std::this_thread::yield();
        }
        tm.lock();
        tm.unlock();
        m.Lock();
        m.Unlock();
    });
	a.join();
	b.join();
	const auto recs = RecordsOf(b_slot.load());
	std::printf("  emu_mutex: records=%zu\n", recs.size());
	CHECK(recs.size() == 2);
	for (const auto& r: recs) {
		CHECK(r.kind == static_cast<uint8_t>(Wait::EmuMutex));
		CHECK(r.peer1 == a_slot.load() && r.waker1 == a_slot.load());
		CHECK(r.end_ns - r.start_ns >= 20000000);
	}
	CHECK(recs.size() == 2 && recs[0].obj == reinterpret_cast<uint64_t>(&tm) && recs[1].obj == reinterpret_cast<uint64_t>(&m));
}

int main() {
	TestPartition();
	TestI1();
	TestGaps();
	TestI3();
	TestWindowSamples();
	TestRegistry();
	TestRing();
	TestFormat();
	TestMandatoryAndCuts();
	TestSig();
	TestSchedule();
	TestNearest();
	TestWindowDelta();
	TestDrainPreempted();
	TestASubmit();
	TestKinds();
	TestRingHold();
	TestPeerFields();
	TestM5Async();
	TestWaitLoopRuntime(); // runtime cases last: g_on stays on
	TestEmuMutexRuntime();
	std::printf("cases %d, failures %d\n", g_cases, g_fail);
	std::printf("%s\n", g_fail == 0 ? "ALL OK" : "FAILED");
	return g_fail == 0 ? 0 : 1;
}
