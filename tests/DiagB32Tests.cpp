// Track F, F20j (HPP-629; ROADMAP s122 item 550(z)(4)): unit tests of the KYTY_DIAG_B32 core without the game -
// the sample partition H > W > R > r > Sr > Sw > S (exactly one), I1, I2', I3, the window selection and instr_us, the
// printed lines (RC13 form), the counters slot_full / torn / ring_drop / sgap_bad / lines_cut / gap3p, mandatory -t
// lines (RC2). Target diag_b32_tests (not in ctest); prints one line per case and "ALL OK".

#include "common/diagB32.h"

#include <cstdio>
#include <cstring>
#include <random>
#include <string>
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
	// a record whose write is in progress (odd word for its index) -> torn
	WaitRec r;
	w->Push(r);
	const auto i = w->wpos.load() - 1;
	w->e[i % kWaitRing].seq.store(2 * i + 1);
	w->Drain(&out, &drop, &torn);
	CHECK(out.empty());
	CHECK(torn == 1);
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
	const auto h = HeaderLine(16, 1);
	CHECK(StartsWith(h, "DiagB32: mode=1 period_us=5000 print_us=100000 "));
	CHECK(h.find(" kstate=1") != std::string::npos);
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
		CHECK(text.find(" gap3p=2\n") != std::string::npos);
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

static void TestSig() {
	Case("waker word: SigWaker against the wait start");
	const uint64_t t      = 123456789000ull;
	const uint64_t packed = ((t >> 10u) << 16u) | 7u;
	CHECK(SigWaker(packed, t - 5000000) == 7);   // signal after the wait began
	CHECK(SigWaker(packed, t + 50000000) == 0);  // signal older than the wait
	CHECK(SigWaker(0, 1) == 0);
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
	std::printf("cases %d, failures %d\n", g_cases, g_fail);
	std::printf("%s\n", g_fail == 0 ? "ALL OK" : "FAILED");
	return g_fail == 0 ? 0 : 1;
}
