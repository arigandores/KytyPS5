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
// F20j4 (HPP-652; ROADMAP s122 item 581(v), (d)): plus the kind partition by who clears the wait (RC5), the M5 refresh
// charged to the window it ran in (RC3, model and the run ring), a writer waiting for readers and an own-slot peer
// (RC2), a contended lock inside H:qlock / H:present (RC4).
// F25d (HPP-667; ROADMAP s122 items 596(v), 599(b)(8), (v)): RC9 - the cases tied to the old constants count from the
// constants; plus E1 / E2 of F25a s11.1, 150 mandatory threads, windows 6.6 s / 21 s, 20 000 wait records, the -x
// tail (hist_exh, hist_exh_w, w_cut_w, others_cut_w) and its identity over 3 windows, cover_us / flip_ns, the
// CloseWindow time (printed; <= 20 ms at 2 000 and <= 100 ms at 20 000 records). Cases needing the F25 fields are
// under KYTY_DIAG_B32_F25 (absent in the F20j4 control build).

#include "common/diagB32.h"
#include "common/threads.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <random>
#include <mutex>
#include <shared_mutex>
#include <string>
#include <thread>
#include <vector>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // F25d: the thread priority of the CloseWindow time case
#endif

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
	constexpr uint32_t kN = kWaitRing + 904; // F25d RC9: was 5000 at kWaitRing 4096
	for (uint32_t i = 0; i < kN; i++) {
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
	CHECK(drop == kN - kWaitRing);
	CHECK(torn == 0);
	CHECK(out.back().start_ns == kN - 1 && out.back().waker1 == 2 && out.back().kind == static_cast<uint8_t>(Wait::Cond));
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
		// kMustCap + 4 threads with R >= 10 % -> mandatory; lines_cut 4; kOthersCap + 6 idle -> others_cut 6
		// (F25d RC9 rule: was 100 / 30 at the caps 96 / 24)
		constexpr int kMust = static_cast<int>(kMustCap) + 4;
		constexpr int kAll  = kMust + static_cast<int>(kOthersCap) + 6;
		Report r = MakeReport();
		r.threads.clear();
		r.waits.clear();
		for (int i = 0; i < kAll; i++) {
			ThreadRow row;
			row.slot1 = 10 + i;
			row.name  = "t";
			row.role  = "guest";
			for (int k = 0; k < 36; k++) {
				row.agg.Add(Code(i < kMust && k < 4 ? State::R : State::S, 0));
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
		CHECK(n_t == static_cast<int>(kMustCap + kOthersCap));
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
		CHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0") != std::string::npos);
#ifdef KYTY_DIAG_B32_F25
		// F25d: then hist_exh, hist_exh_w, w_cut_w, others_cut_w; others_cut_w last
		CHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0 hist_exh=0 hist_exh_w=0 w_cut_w=0 others_cut_w=0\n") !=
		      std::string::npos);
#endif
	}
	{
		// -w cap kWLinesCap: the chain records are never cut, the rest by overlap (F25d RC9: kWLinesCap + 17 records in
		// all - one of MakeReport and kWLinesCap + 16 here; was 80 at the cap 64)
		Report r = MakeReport();
		for (int i = 0; i < static_cast<int>(kWLinesCap) + 16; i++) {
			WaitRec w;
			w.start_ns = r.win_start_ns + 1000000 * static_cast<uint64_t>(i);
			w.end_ns   = r.win_end_ns;
			w.slot1    = 5;
			w.kind     = static_cast<uint8_t>(Wait::Sleep);
			r.waits.push_back(w);
		}
		Counters   c;
		const auto text = Format(&r, &c);
		CHECK(c.w_cut == (kWLinesCap + 17) - kWLinesCap);
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
	// F20j4 (item 581(v)(5)): emu_join appended after rwlock; join keeps its number and name (PthreadJoin only).
	CHECK(static_cast<uint8_t>(Wait::EmuJoin) == static_cast<uint8_t>(Wait::Rwlock) + 1);
	CHECK(static_cast<uint8_t>(Wait::Count) == static_cast<uint8_t>(Wait::EmuJoin) + 1);
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::EmuJoin))) == "emu_join");
	CHECK(std::string(WaitName(static_cast<uint8_t>(Wait::Join))) == "join");
	// F20j4 (item 581(v)(5)): EMU_WAIT - EmuMutex .. Av and vblank, audio, aio, net, emu_join; GUEST_SLEEP - the rest.
	const std::vector<std::string> emu_hle = {"vblank", "audio", "aio", "net", "emu_join"};
	const std::vector<std::string> guest   = {"cond", "mutex", "sem",   "psem", "evf",   "eq",  "sleep", "gpu_idle",
	                                          "gpu_regmem", "once", "join", "addr", "fiber", "ult", "rwlock"};
	uint32_t n_emu = 0;
	for (uint8_t k = 1; k < static_cast<uint8_t>(Wait::Count); k++) {
		const std::string n   = WaitName(k);
		const bool        emu = (k >= static_cast<uint8_t>(Wait::EmuMutex) && k <= static_cast<uint8_t>(Wait::Av)) ||
		                 std::find(emu_hle.begin(), emu_hle.end(), n) != emu_hle.end();
		CHECK(IsEmuWait(k) == emu);
		CHECK(emu != (std::find(guest.begin(), guest.end(), n) != guest.end())); // each kind in exactly one class
		n_emu += emu ? 1 : 0;
	}
	CHECK(n_emu == 25 + 5);
	CHECK(!IsEmuWait(static_cast<uint8_t>(Wait::Cond)) && !IsEmuWait(static_cast<uint8_t>(Wait::Join)));
	CHECK(IsEmuWait(static_cast<uint8_t>(Wait::Vblank)) && IsEmuWait(static_cast<uint8_t>(Wait::EmuJoin)));
	CHECK(!IsEmuWait(0) && !IsEmuWait(static_cast<uint8_t>(Wait::Count)));
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
	CHECK(text.find(" gap3p=0 ring_hold=8 ring_hold_w=3") != std::string::npos); // after gap3p
#ifdef KYTY_DIAG_B32_F25
	CHECK(text.find(" ring_hold_w=3 hist_exh=0 hist_exh_w=0 w_cut_w=0 others_cut_w=0\n") != std::string::npos);
#endif
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

// ---------------------------------------------------------------------------------------------------------------------
// F20j4 (HPP-652; ROADMAP s122 item 581(v))
// ---------------------------------------------------------------------------------------------------------------------
struct RunProbe {
	std::atomic<bool> in_work {false};
	std::atomic<bool> release {false};
};

static void ProbeWork(void* user) {
	auto* p = static_cast<RunProbe*>(user);
	p->in_work.store(true);
	while (!p->release.load()) {
		std::this_thread::yield();
	}
}

static void TestM5Charge() {
	Case("F20j4 (3), RC3 of F20k3: the M5 refresh time is charged to the window it ran in (model; the run ring)");
	const uint64_t ms = 1000000;
	// The RC3 scenario: window k = (1000, 1150] ms (a 150 ms frame), k+1 = (1150, 1270] ms; a 76.7 ms refresh.
	const uint64_t s0 = 1000 * ms;
	const uint64_t f1 = 1150 * ms;
	const uint64_t f2 = 1270 * ms;
	{
		M5Charge c; // a run entirely inside k, taken at the flip of k: m5r(k) = its cost, m5r(k+1) = 0
		c.Add({{s0 + 40 * ms, s0 + 40 * ms + 76700000}}, 0);
		CHECK(c.Window(s0, f1) == 76700000);
		c.Prune(f1);
		c.Add({}, 0);
		CHECK(c.Window(f1, f2) == 0 && c.Pending() == 0);
	}
	{
		M5Charge c; // a run across the flip of k, finished before the take: split by the overlap
		c.Add({{f1 - 30 * ms, f1 + 50 * ms}}, 0);
		CHECK(c.Window(s0, f1) == 30 * ms);
		c.Prune(f1);
		CHECK(c.Pending() == 1);
		c.Add({}, 0);
		CHECK(c.Window(f1, f2) == 50 * ms);
		c.Prune(f2);
		CHECK(c.Pending() == 0);
	}
	{
		M5Charge       c; // a run in progress at the take of k, finished before the take of k+1: k gets its part only once
		const uint64_t b = f1 - 30 * ms;
		c.Add({}, b);
		CHECK(c.Window(s0, f1) == 30 * ms);
		c.Prune(f1);
		c.Add({{b, f1 + 50 * ms}}, 0);
		CHECK(c.Window(f1, f2) == 50 * ms);
	}
	{
		M5Charge       c; // the run seen in progress finished before the take: counted once
		const uint64_t b = s0 + 20 * ms;
		c.Add({{b, b + 10 * ms}}, b);
		CHECK(c.Window(s0, f1) == 10 * ms);
	}
	{
		M5Charge c; // two windows closed at one take (a batch): a run over both and a later one
		c.Add({{s0 + 100 * ms, f1 + 20 * ms}, {f1 + 60 * ms, f1 + 70 * ms}}, 0);
		CHECK(c.Window(s0, f1) == 50 * ms);
		CHECK(c.Window(f1, f2) == 30 * ms);
		c.Prune(f2);
		CHECK(c.Pending() == 0);
	}
	// The run ring of AsyncRefresh: CurrentBegin while a run is in progress, the run with [begin, end] after it.
	RunProbe     probe;
	AsyncRefresh ar;
	ar.Start(&ProbeWork, &probe, 1000000000ull);
	while (!probe.in_work.load()) {
		std::this_thread::yield();
	}
	const auto                     cur = ar.CurrentBegin();
	std::vector<AsyncRefresh::Run> runs;
	ar.TakeRuns(&runs);
	CHECK(cur != 0 && runs.empty());
	std::this_thread::sleep_for(std::chrono::milliseconds(5));
	probe.release.store(true);
	while (ar.Runs() < 1) {
		std::this_thread::yield();
	}
	ar.TakeRuns(&runs);
	CHECK(runs.size() == 1 && runs[0].begin_ns == cur && runs[0].end_ns >= cur + 4 * ms);
	CHECK(ar.CurrentBegin() == 0);
	ar.Stop();
	AsyncRefresh lap; // more than kRuns runs before a take: the oldest are counted as lost
	for (uint64_t i = 0; i < AsyncRefresh::kRuns + 6; i++) {
		lap.PushRun(i * 10 + 1, i * 10 + 5);
	}
	std::vector<AsyncRefresh::Run> got;
	lap.TakeRuns(&got);
	CHECK(got.size() == AsyncRefresh::kRuns && lap.LostRuns() == 6 && !got.empty() && got[0].begin_ns == 61);
	std::printf("  m5 charge: run in progress begin=%llu, taken runs=%zu, ring lost=%llu\n", static_cast<unsigned long long>(cur),
	            runs.size(), static_cast<unsigned long long>(lap.LostRuns()));
}

static void TestPeerSelfRuntime() {
	Case("F20j4 (2), RC2 of F20k3: a writer waiting for two readers - peer 0; an own-slot peer is stored as 0");
	Test::InitRuntime();
	TrackedMutex<std::shared_mutex> sm;
	std::atomic<int32_t>            x_slot {0};
	std::atomic<int32_t>            self_peer {-1};
	std::atomic<int>                readers {0};
	std::atomic<bool>               x_first {false};
	std::atomic<bool>               writer_waits {false};
	std::thread                     x([&] {
		RegisterRole("TestX");
		x_slot.store(SelfSlotIfRegistered());
		sm.lock(); // X is the last exclusive holder; before F20j4 its slot stayed in the owner field after the unlock
		sm.unlock();
		x_first.store(true);
		while (readers.load() < 2) {
			std::this_thread::yield();
		}
		writer_waits.store(true);
		sm.lock(); // waits for the two readers (lock_shared does not set the owner)
		sm.unlock();
		Mark self; // a mark given the thread's own slot as the peer
		self.BeginWReg(Wait::GpuWait, &sm, SelfSlotIfRegistered(), 0);
		MarkSnap s;
		if (Test::ReadSlotMark(SelfSlotIfRegistered(), &s)) {
			self_peer.store(s.peer);
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(20));
		self.End(0, false);
	});
	const auto reader = [&](const char* role) {
		RegisterRole(role);
		while (!x_first.load()) {
			std::this_thread::yield();
		}
		sm.lock_shared();
		readers.fetch_add(1);
		while (!writer_waits.load()) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		sm.unlock_shared();
	};
	std::thread r1([&] { reader("TestR1"); });
	std::thread r2([&] { reader("TestR2"); });
	x.join();
	r1.join();
	r2.join();
	const auto recs = RecordsOf(x_slot.load());
	std::printf("  peer: records=%zu self_peer=%d\n", recs.size(), self_peer.load());
	CHECK(self_peer.load() == 0);
	CHECK(recs.size() == 2);
	if (recs.size() == 2) {
		CHECK(recs[0].kind == static_cast<uint8_t>(Wait::EmuMutex) && recs[0].obj == reinterpret_cast<uint64_t>(&sm));
		CHECK(recs[0].peer1 == 0 && recs[0].waker1 == 0);
		CHECK(recs[0].end_ns - recs[0].start_ns >= 20000000);
		CHECK(recs[1].kind == static_cast<uint8_t>(Wait::GpuWait) && recs[1].peer1 == 0);
	}
	for (const auto& r: recs) {
		CHECK(r.peer1 != x_slot.load() && r.waker1 != x_slot.load()); // no record names the waiter itself
	}
}

static void TestLockUnderHRuntime() {
	Case("F20j4 (4), RC4 of F20k3: a contended lock inside H:qlock / H:present keeps the H mark; without H - W:emu_mutex");
	Test::InitRuntime();
	Common::Mutex            m;
	TrackedMutex<std::mutex> tm;
	// B: 1 - waits for m inside H:qlock, 2 - waits for tm inside H:present, 3 - waits for m without an H mark, 4 - done.
	std::atomic<int>     stage {0};
	std::atomic<bool>    a_holds {false};
	std::atomic<bool>    b_mid {false};
	std::atomic<bool>    a_again {false};
	std::atomic<int32_t> a_slot {0};
	std::atomic<int32_t> b_slot {0};
	std::thread          a([&] {
		RegisterRole("TestHA");
		a_slot.store(SelfSlotIfRegistered());
		m.Lock();
		tm.lock();
		a_holds.store(true);
		while (stage.load() < 1) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		m.Unlock();
		while (stage.load() < 2) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		tm.unlock();
		while (!b_mid.load()) {
			std::this_thread::yield();
		}
		m.Lock();
		a_again.store(true);
		while (stage.load() < 3) {
			std::this_thread::yield();
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(40));
		m.Unlock();
	});
	std::thread b([&] {
		RegisterRole("TestHB");
		b_slot.store(SelfSlotIfRegistered());
		while (!a_holds.load()) {
			std::this_thread::yield();
		}
		{
			Mark h;
			h.BeginH(Call::QLock);
			stage.store(1);
			m.Lock();
			m.Unlock();
			h.End(0, false);
		}
		{
			Mark h;
			h.BeginH(Call::Present);
			stage.store(2);
			tm.lock();
			tm.unlock();
			h.End(0, false);
		}
		b_mid.store(true);
		while (!a_again.load()) {
			std::this_thread::yield();
		}
		stage.store(3);
		m.Lock();
		m.Unlock();
		stage.store(4);
	});
	// Samples of B's slot every 1 ms by the clock; a sample counts only if the stage did not change around it.
	uint32_t h_ok[4] {};
	uint32_t w_n[4] {};
	uint32_t w_emu[4] {};
	while (b_slot.load() == 0 || stage.load() == 0) {
		std::this_thread::yield();
	}
	auto next = std::chrono::steady_clock::now();
	while (stage.load() != 4) {
		const int s0 = stage.load();
		MarkSnap  snap;
		const bool got = Test::ReadSlotMark(b_slot.load(), &snap);
		const int s1 = stage.load();
		if (got && s0 == s1 && s0 >= 1 && s0 <= 3) {
			const auto st   = static_cast<State>(snap.mark >> 8u);
			const auto kind = static_cast<uint8_t>(snap.mark & 0xffu);
			const auto want = s0 == 1 ? static_cast<uint8_t>(Call::QLock) : static_cast<uint8_t>(Call::Present);
			h_ok[s0] += st == State::H && kind == want ? 1 : 0;
			w_n[s0] += st == State::W ? 1 : 0;
			w_emu[s0] += st == State::W && kind == static_cast<uint8_t>(Wait::EmuMutex) ? 1 : 0;
		}
		next += std::chrono::milliseconds(1);
		while (std::chrono::steady_clock::now() < next && stage.load() != 4) {
			std::this_thread::yield();
		}
	}
	a.join();
	b.join();
	const auto recs = RecordsOf(b_slot.load());
	std::printf("  under H: qlock H=%u W=%u; present H=%u W=%u; no H W:emu_mutex=%u W=%u; records=%zu\n", h_ok[1], w_n[1],
	            h_ok[2], w_n[2], w_emu[3], w_n[3], recs.size());
	CHECK(h_ok[1] >= 10 && w_n[1] == 0); // inside H:qlock the samples stay H:qlock
	CHECK(h_ok[2] >= 10 && w_n[2] == 0); // inside H:present the samples stay H:present
	CHECK(w_emu[3] >= 10);               // the control without an H mark: W:emu_mutex
	CHECK(recs.size() == 1);             // only the wait without an H mark is a record
	if (recs.size() == 1) {
		CHECK(recs[0].kind == static_cast<uint8_t>(Wait::EmuMutex) && recs[0].obj == reinterpret_cast<uint64_t>(&m));
		CHECK(recs[0].peer1 == a_slot.load() && recs[0].waker1 == a_slot.load());
		CHECK(recs[0].end_ns - recs[0].start_ns >= 20000000);
	}
}

// ---------------------------------------------------------------------------------------------------------------------
// F25d (HPP-667; ROADMAP s122 items 596(v), 599(b)(8), (v)): the F25 fix. Negative control - the F20j4 code (f2307b02):
// E1 / E2, 150 mandatory, window 6.6 s and 20 000 records fail there (F25a s2.3, s11.3).

static std::vector<std::string> LinesWith(const std::string& text, const char* prefix) {
	std::vector<std::string> out;
	for (const auto& l: Lines(text)) {
		if (StartsWith(l, prefix)) {
			out.push_back(l);
		}
	}
	return out;
}

static void TestF25EdgesE1E2() {
	Case("F25 C5a (F25a s11.1, s11.3(a)): 3 000 records - the 4th chain thread (E1) and the -t partner (E2) are printed, w_cut 0");
	Report r = MakeReport();
	r.threads.clear();
	r.waits.clear();
	// slots: 1 Present, 2 Gpu, 3 flip (holder), 10 A, 11 B, 12 C, 20 tpeer, 30..79 fillers
	const int ids[] = {1, 2, 3, 10, 11, 12, 20};
	for (int id: ids) {
		ThreadRow row;
		row.slot1 = id;
		row.name  = "t";
		row.role  = id == 1 ? "Present" : (id == 2 ? "Gpu" : "guest");
		for (int k = 0; k < 36; k++) {
			row.agg.Add(Code(State::W, static_cast<uint8_t>(Wait::Cond)));
		}
		if (id == 3) {
			row.last.mark = MarkWord(State::W, static_cast<uint8_t>(Wait::Mutex));
			row.last.peer = 20; // the holder's -t partner (tpeer): mandatory by -t, not in the -w closure
		}
		r.threads.push_back(row);
	}
	for (int id = 30; id < 80; id++) {
		ThreadRow row;
		row.slot1 = id;
		row.name  = "f";
		row.role  = "guest";
		for (int k = 0; k < 36; k++) {
			row.agg.Add(Code(State::S, 0));
		}
		r.threads.push_back(row);
	}
	const auto rec = [&](int slot, int waker, uint64_t obj, uint64_t overlap_ns) {
		WaitRec w;
		w.start_ns = r.win_end_ns - overlap_ns;
		w.end_ns   = r.win_end_ns;
		w.slot1    = slot;
		w.waker1   = waker;
		w.obj      = obj;
		w.kind     = static_cast<uint8_t>(Wait::Cond);
		r.waits.push_back(w);
	};
	// The chain in reverse order: one closure pass adds one thread, so C's record (checked before B's in the pass that
	// adds C) stays outside the 3 passes (E1); in the forward order a pass would reach it after B's record.
	rec(12, 13, 0xc0ffee, 11000000); // C (step 3, outside the 3-step closure) - small overlap
	rec(11, 12, 0xa003, 150000000); // B waits for C
	rec(10, 11, 0xa002, 150000000); // A waits for B
	rec(3, 10, 0xa001, 150000000);  // holder waits for A
	rec(20, 0, 0xbeef, 11000000);    // tpeer's own record - small overlap
	for (int i = 0; i < 2995; i++) {
		rec(30 + i % 50, 0, 0x100000 + static_cast<uint64_t>(i), 100000000 + static_cast<uint64_t>(i));
	}
	CHECK(r.waits.size() == 3000);
	Counters   c;
	const auto text = Format(&r, &c);
	CHECK(c.w_cut == 0);
	CHECK(text.find(" obj=0xc0ffee ") != std::string::npos); // E1
	CHECK(text.find(" obj=0xbeef ") != std::string::npos);   // E2
	CHECK(LinesWith(text, "DiagB32-w: ").size() == 3000);
	std::printf("  w_cut=%llu w_lines=%zu\n", static_cast<unsigned long long>(c.w_cut), LinesWith(text, "DiagB32-w: ").size());
}

static void TestF25Mandatory150() {
	Case("F25 C5b (F25a s11.3(b)): 150 mandatory threads - lines_cut 0, 150 -t lines");
	Report r = MakeReport();
	r.threads.clear();
	r.waits.clear();
	for (int i = 0; i < 150; i++) {
		ThreadRow row;
		row.slot1 = 10 + i;
		row.name  = "t";
		row.role  = "guest";
		for (int k = 0; k < 36; k++) {
			row.agg.Add(Code(k < 4 ? State::R : State::S, 0));
		}
		r.threads.push_back(row);
	}
	Counters   c;
	const auto text = Format(&r, &c);
	CHECK(c.lines_cut == 0);
	CHECK(LinesWith(text, "DiagB32-t: ").size() == 150);
	std::printf("  lines_cut=%llu t_lines=%zu\n", static_cast<unsigned long long>(c.lines_cut), LinesWith(text, "DiagB32-t: ").size());
}

// The history ring of kHist samples P apart: before samples up to the window start (the last one at it), n after it.
static void HistWindow(uint32_t before, uint32_t n, bool* exhausted, size_t* got, GapStats* g) {
	std::vector<uint64_t> t(kHist);
	std::vector<uint64_t> cost(kHist, 1000);
	std::vector<uint8_t>  kq(kHist, 0);
	const uint64_t        start = 1000000000000ull;
	const uint64_t        total = static_cast<uint64_t>(before) + n;
	for (uint64_t h = 0; h < total; h++) {
		t[h % kHist] = h < before ? start - (before - 1 - h) * kPeriodNs : start + (h - before + 1) * kPeriodNs;
	}
	const uint64_t        flip = start + static_cast<uint64_t>(n) * kPeriodNs;
	std::vector<uint64_t> idx;
	uint64_t              instr = 0;
	uint32_t              kqn   = 0;
	WindowSamples(t.data(), cost.data(), kq.data(), total, kHist, start, flip, 0, &idx, &instr, &kqn, exhausted);
	std::vector<uint64_t> times;
	for (auto h: idx) {
		times.push_back(t[h % kHist]);
	}
	*got = idx.size();
	*g   = Gaps(times.data(), times.size(), start, flip, kPeriodNs);
}

static void TestF25Windows() {
	Case("F25 C1 (F25a s2.3): window 6.6 s - the ring holds its start (hist_exh 0), sgap <= 2P, i2; window 21 s - exhausted");
	bool     ex  = true;
	size_t   got = 0;
	GapStats g;
	HistWindow(100, 1320, &ex, &got, &g); // 1320 x 5 ms = 6.6 s
	CHECK(!ex);
	CHECK(got == 1320);
	CHECK(g.sgap_max_ns <= 2 * kPeriodNs && g.i2_ok && g.monotonic);
	std::printf("  6.6 s: exhausted=%d samples=%zu sgap_max_us=%llu\n", ex ? 1 : 0, got,
	            static_cast<unsigned long long>(g.sgap_max_ns / 1000u));
	HistWindow(100, 4200, &ex, &got, &g); // 21 s
	CHECK(ex);
	std::printf("  21 s: exhausted=%d samples=%zu\n", ex ? 1 : 0, got);
}

static void TestF25Ring20000() {
	Case("F25 C2 (F25a s2.3): 20 000 wait records in one window - ring_drop 0");
	auto*    w    = new WaitRing;
	uint64_t drop = 0;
	uint64_t torn = 0;
	for (uint32_t i = 0; i < 20000; i++) {
		WaitRec rec;
		rec.start_ns = 1000000 + i;
		rec.end_ns   = rec.start_ns + 10000000;
		rec.slot1    = 1 + static_cast<int32_t>(i % 90);
		rec.kind     = static_cast<uint8_t>(Wait::Cond);
		w->Push(rec);
	}
	std::vector<WaitRec> out;
	w->Drain(&out, &drop, &torn);
	CHECK(drop == 0 && torn == 0);
	CHECK(out.size() == 20000);
	std::printf("  drained=%zu ring_drop=%llu\n", out.size(), static_cast<unsigned long long>(drop));
	delete w;
}

#ifdef KYTY_DIAG_B32_F25
static void TestF25XIdentity() {
	Case("F25 C3, C5v, C5g (F25a s11.3(v)): -x tail after ring_hold_w; w_cut_w / others_cut_w = increments on 3 windows");
	Counters    c;
	uint64_t    prev_w = 0;
	uint64_t    prev_o = 0;
	const int   cut[3] = {1, 0, 1}; // window 2 clean
	for (int k = 0; k < 3; k++) {
		Report r = MakeReport();
		r.n      = 3193 + static_cast<uint64_t>(k);
		if (cut[k] != 0) {
			for (int i = 0; i < static_cast<int>(kWLinesCap) + 16; i++) { // the -w cap of RC9: 17 cut
				WaitRec w;
				w.start_ns = r.win_start_ns + 1000 * static_cast<uint64_t>(i);
				w.end_ns   = r.win_end_ns;
				w.slot1    = 5;
				w.kind     = static_cast<uint8_t>(Wait::Sleep);
				r.waits.push_back(w);
			}
			for (int i = 0; i < static_cast<int>(kOthersCap) + 6; i++) { // idle non-mandatory threads
				ThreadRow row;
				row.slot1 = 100 + i;
				row.name  = "idle";
				row.role  = "guest";
				for (int q = 0; q < 36; q++) {
					row.agg.Add(Code(State::S, 0));
				}
				r.threads.push_back(row);
			}
		}
		const auto text = Format(&r, &c);
		c.Rebase();
		const auto x = LinesWith(text, "DiagB32-x: ");
		CHECK(x.size() == 1);
		if (x.size() != 1) {
			continue;
		}
		const auto& l = x[0];
		const auto  p = l.find(" ring_hold_w=");
		const auto  q = l.find(" hist_exh=");
		const auto  s = l.find(" hist_exh_w=");
		const auto  u = l.find(" w_cut_w=");
		const auto  v = l.find(" others_cut_w=");
		CHECK(p != std::string::npos && q != std::string::npos && s != std::string::npos && u != std::string::npos &&
		      v != std::string::npos);
		CHECK(p < q && q < s && s < u && u < v);
		CHECK(l.find(' ', v + 1) == std::string::npos); // others_cut_w is the last field
		const auto w_cut  = std::strtoull(Field(text, "w_cut").c_str(), nullptr, 10);
		const auto o_cut  = std::strtoull(Field(text, "others_cut").c_str(), nullptr, 10);
		const auto w_cutw = std::strtoull(Field(text, "w_cut_w").c_str(), nullptr, 10);
		const auto o_cutw = std::strtoull(Field(text, "others_cut_w").c_str(), nullptr, 10);
		CHECK(w_cutw == w_cut - prev_w);
		CHECK(o_cutw == o_cut - prev_o);
		CHECK(Field(text, "hist_exh") == "0" && Field(text, "hist_exh_w") == "0");
		// cut windows: 17 -w records (RC9 form); others - slots 5..7 of MakeReport + kOthersCap + 6 idle = cap + 9
		CHECK(cut[k] == 0 ? (w_cutw == 0 && o_cutw == 0) : (w_cutw == 17 && o_cutw == 9));
		std::printf("  window %d: w_cut=%llu w_cut_w=%llu others_cut=%llu others_cut_w=%llu\n", k + 1,
		            static_cast<unsigned long long>(w_cut), static_cast<unsigned long long>(w_cutw),
		            static_cast<unsigned long long>(o_cut), static_cast<unsigned long long>(o_cutw));
		prev_w = w_cut;
		prev_o = o_cut;
	}
}

static uint64_t Num(const std::string& text, const char* key) {
	return std::strtoull(Field(text, key).c_str(), nullptr, 10);
}

static void TestF25BenchWindows() {
	Case("F25 C1, C3, C4, C6 through Sampler::CloseWindow: 6.6 s - hist_exh_w 0, cover_us, flip_ns last; 21 s - hist_exh_w 1");
	{
		Test::BenchIn in;
		in.nslots   = 90;
		in.before   = 100;
		in.nsamples = 1320;
		in.nwaits   = 200;
		const auto o    = Test::CloseWindowBench(in);
		const auto main = LinesWith(o.text, "DiagB32: ");
		CHECK(main.size() == 1);
		const auto dt    = Num(o.text, "dt_us");
		const auto cover = Num(o.text, "cover_us");
		const auto sgap  = Num(o.text, "sgap_max_us");
		CHECK(dt == 6600000);
		CHECK(Field(o.text, "hist_exh_w") == "0" && Field(o.text, "ring_drop_w") == "0");
		CHECK(cover == dt - kPeriodNs / 1000u);  // the oldest sample is P after the start
		CHECK(dt - cover <= sgap + 1);           // item 599(b)(1): the agreement invariant
		CHECK(Num(o.text, "flip_ns") == o.flip_ns);
		CHECK(!main.empty() && main[0].find(" cover_us=") < main[0].find(" flip_ns=") &&
		      main[0].find(' ', main[0].find(" flip_ns=") + 1) == std::string::npos); // flip_ns last, after cover_us
		CHECK(Field(o.text, "w_cut_w") == "0" && Field(o.text, "others_cut_w") == "0" && Field(o.text, "lines_cut_w") == "0");
		std::printf("  6.6 s: dt_us=%llu cover_us=%llu sgap_max_us=%llu hist_exh_w=%s flip_ns=%s close_us=%llu\n",
		            static_cast<unsigned long long>(dt), static_cast<unsigned long long>(cover),
		            static_cast<unsigned long long>(sgap), Field(o.text, "hist_exh_w").c_str(), Field(o.text, "flip_ns").c_str(),
		            static_cast<unsigned long long>(o.close_ns / 1000u));
	}
	{
		Test::BenchIn in;
		in.nslots   = 90;
		in.before   = 100;
		in.nsamples = 4200;
		const auto o = Test::CloseWindowBench(in);
		CHECK(Field(o.text, "hist_exh_w") == "1" && Field(o.text, "ring_drop_w") == "1");
		CHECK(Num(o.text, "cover_us") < Num(o.text, "dt_us"));
		std::printf("  21 s: dt_us=%s cover_us=%s hist_exh_w=%s ring_drop_w=%s\n", Field(o.text, "dt_us").c_str(),
		            Field(o.text, "cover_us").c_str(), Field(o.text, "hist_exh_w").c_str(), Field(o.text, "ring_drop_w").c_str());
	}
}

static void TestF25CloseTime() {
	Case("F25 RC8 (item 599(b)(8)): CloseWindow time, 4 096 samples x 90 slots; <= 20 ms at 2 000, <= 100 ms at 20 000 records");
	// The sampler thread runs at THREAD_PRIORITY_HIGHEST; the test thread too, so that a preemption by another process of
	// the machine is not read as the cost. The member is the median of 5 runs; every run and the worst are printed.
#ifdef _WIN32
	const int old_prio = GetThreadPriority(GetCurrentThread());
	SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST);
#endif
	const uint32_t limits_ms[2] = {20, 100};
	const uint32_t waits[2]     = {2000, 20000};
	for (int k = 0; k < 2; k++) {
		uint64_t              worst = 0;
		size_t                wl    = 0;
		std::vector<uint64_t> runs;
		for (uint32_t rep = 0; rep < 5; rep++) {
			Test::BenchIn in;
			in.nslots   = 90;
			in.before   = 1;
			in.nsamples = kHist - 1; // 4 096 samples in the ring, the window start held
			in.nwaits   = waits[k];
			in.nopen    = 90;
			in.seed     = 11 + rep;
			const auto o = Test::CloseWindowBench(in);
			worst        = std::max(worst, o.close_ns);
			runs.push_back(o.close_ns);
			wl           = LinesWith(o.text, "DiagB32-w: ").size();
			std::printf("  records=%u rep=%u close_ms=%.3f w_lines=%zu text_bytes=%zu\n", waits[k], rep,
			            static_cast<double>(o.close_ns) / 1e6, wl, o.text.size());
		}
		std::sort(runs.begin(), runs.end());
		const uint64_t median = runs[runs.size() / 2];
		std::printf("  records=%u median_ms=%.3f worst_ms=%.3f limit_ms=%u\n", waits[k], static_cast<double>(median) / 1e6,
		            static_cast<double>(worst) / 1e6, limits_ms[k]);
		CHECK(median <= static_cast<uint64_t>(limits_ms[k]) * 1000000u);
	}
#ifdef _WIN32
	SetThreadPriority(GetCurrentThread(), old_prio);
#endif
}
#endif

#ifdef KYTY_DIAG_B32_F25
// F25d (item 599(b)(8)): the report texts of fixed bench inputs, one file per input (equivalence of the index fix).
static int DumpBench(const char* dir) {
	struct In {
		const char* name;
		uint32_t    before, nsamples, nwaits, nopen, nmatch, kq_every, seed;
	};
	const In ins[] = {{"w6600", 100, 1320, 200, 0, 0, 0, 1},
	                  {"w21000", 100, 4200, 0, 0, 0, 0, 1},
	                  {"r2000_s11", 1, kHist - 1, 2000, 90, 0, 0, 11},
	                  {"r2000_s12", 1, kHist - 1, 2000, 90, 0, 0, 12},
	                  {"r20000_s11", 1, kHist - 1, 20000, 90, 0, 0, 11},
	                  {"r20000_s15", 1, kHist - 1, 20000, 90, 0, 0, 15},
	                  {"r20000_open0", 1, kHist - 1, 20000, 0, 0, 0, 21},
	                  {"r500_s3", 1, 800, 500, 40, 0, 0, 3},
	                  {"m2000_kq9", 1, kHist - 1, 2000, 90, 45, 9, 31},
	                  {"m20000_kq13", 1, kHist - 1, 20000, 90, 90, 13, 32},
	                  {"m300_kq1", 50, 1500, 300, 60, 30, 1, 33},
	                  {"m300_kq40", 50, 1500, 300, 60, 60, 40, 34}};
	for (const auto& x: ins) {
		Test::BenchIn in;
		in.nslots   = 90;
		in.before   = x.before;
		in.nsamples = x.nsamples;
		in.nwaits   = x.nwaits;
		in.nopen    = x.nopen;
		in.nmatch   = x.nmatch;
		in.kq_every = x.kq_every;
		in.seed     = x.seed;
		const auto  o    = Test::CloseWindowBench(in);
		std::string path = std::string(dir) + "/" + x.name + ".txt";
		FILE*       f    = std::fopen(path.c_str(), "wb");
		if (f == nullptr) {
			std::printf("cannot write %s\n", path.c_str());
			return 1;
		}
		std::fwrite(o.text.data(), 1, o.text.size(), f);
		std::fclose(f);
		size_t open_lines = 0;
		for (size_t p = o.text.find(" open=1 "); p != std::string::npos; p = o.text.find(" open=1 ", p + 1)) {
			open_lines++;
		}
		size_t sw_t = 0; // -t lines with Sr or Sw samples (the nearest-snapshot split in use)
		for (const auto& l: Lines(o.text)) {
			if (StartsWith(l, "DiagB32-t: ") && (l.find(" Sr=0 ") == std::string::npos || l.find(" Sw=0 ") == std::string::npos)) {
				sw_t++;
			}
		}
		std::printf("%s bytes=%zu close_ms=%.3f open_w_lines=%zu t_lines_with_Sr_or_Sw=%zu\n", x.name, o.text.size(),
		            static_cast<double>(o.close_ns) / 1e6, open_lines, sw_t);
	}
	return 0;
}
#endif

int main(int argc, char** argv) {
#ifdef KYTY_DIAG_B32_F25
	if (argc == 3 && std::strcmp(argv[1], "--dump-bench") == 0) {
		return DumpBench(argv[2]);
	}
#else
	(void)argc;
	(void)argv;
#endif
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
	TestM5Charge();
	TestF25EdgesE1E2();
	TestF25Mandatory150();
	TestF25Windows();
	TestF25Ring20000();
#ifdef KYTY_DIAG_B32_F25
	TestF25XIdentity();
	TestF25BenchWindows();
	TestF25CloseTime();
#endif
	TestWaitLoopRuntime(); // runtime cases last: g_on stays on
	TestEmuMutexRuntime();
	TestPeerSelfRuntime();
	TestLockUnderHRuntime();
	std::printf("cases %d, failures %d\n", g_cases, g_fail);
	std::printf("%s\n", g_fail == 0 ? "ALL OK" : "FAILED");
	return g_fail == 0 ? 0 : 1;
}
