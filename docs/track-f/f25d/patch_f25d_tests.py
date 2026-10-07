# F25d (HPP-667; ROADMAP s122 items 596(v), 599(b)(8), (v) RC9): tests of the F25 fix without the game.
# RC9: the cases tied to the old constants count their records / threads from the constants (kWaitRing + 904,
# kWLinesCap + 17, and by the same rule kMustCap + 4 / kOthersCap + 6), expectations of the old form.
# New cases (F25a s2.3, s11.3(a)-(v); item 599(b)(8)): E1 / E2, 150 mandatory threads, windows 6.6 s / 21 s, 20 000
# wait records, the -x tail and its identity over 3 windows, the CloseWindow time. The cases that need the F25 fields
# or Test::CloseWindowBench are inside #ifdef KYTY_DIAG_B32_F25 - the F20j4 control build compiles without them.
# Usage: python patch_f25d_tests.py <worktree root>
import sys

ROOT = sys.argv[1].rstrip('/\\')
T = 'tests/DiagB32Tests.cpp'
t = open(ROOT + '/' + T, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def sub(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor count %d != %d: %r' % (n, count, old[:120]))
    return text.replace(old, new)


t = sub(t, '// (RC2), a contended lock inside H:qlock / H:present (RC4).\n',
        '// (RC2), a contended lock inside H:qlock / H:present (RC4).\n'
        '// F25d (HPP-667; ROADMAP s122 items 596(v), 599(b)(8), (v)): RC9 - the cases tied to the old constants count from the\n'
        '// constants; plus E1 / E2 of F25a s11.1, 150 mandatory threads, windows 6.6 s / 21 s, 20 000 wait records, the -x\n'
        '// tail (hist_exh, hist_exh_w, w_cut_w, others_cut_w) and its identity over 3 windows, cover_us / flip_ns, the\n'
        '// CloseWindow time (printed; <= 20 ms at 2 000 and <= 100 ms at 20 000 records). Cases needing the F25 fields are\n'
        '// under KYTY_DIAG_B32_F25 (absent in the F20j4 control build).\n')

# RC9: TestRing - kWaitRing + 904 records
t = sub(t, '\tfor (uint32_t i = 0; i < 5000; i++) {\n\t\tWaitRec r;\n\t\tr.start_ns = i;\n',
        '\tconstexpr uint32_t kN = kWaitRing + 904; // F25d RC9: was 5000 at kWaitRing 4096\n'
        '\tfor (uint32_t i = 0; i < kN; i++) {\n\t\tWaitRec r;\n\t\tr.start_ns = i;\n')
t = sub(t, '\tCHECK(drop == 5000 - kWaitRing);\n', '\tCHECK(drop == kN - kWaitRing);\n')
t = sub(t, '\tCHECK(out.back().start_ns == 4999 && out.back().waker1 == 2',
        '\tCHECK(out.back().start_ns == kN - 1 && out.back().waker1 == 2')

# RC9 rule: kMustCap + 4 mandatory, kOthersCap + 6 idle
t = sub(t, '\t\t// 100 threads with R >= 10 % -> mandatory; cap 96 -> lines_cut 4; 30 idle -> others_cut 6\n'
           '\t\tReport r = MakeReport();\n\t\tr.threads.clear();\n\t\tr.waits.clear();\n'
           '\t\tfor (int i = 0; i < 130; i++) {\n',
        '\t\t// kMustCap + 4 threads with R >= 10 % -> mandatory; lines_cut 4; kOthersCap + 6 idle -> others_cut 6\n'
        '\t\t// (F25d RC9 rule: was 100 / 30 at the caps 96 / 24)\n'
        '\t\tconstexpr int kMust = static_cast<int>(kMustCap) + 4;\n'
        '\t\tconstexpr int kAll  = kMust + static_cast<int>(kOthersCap) + 6;\n'
        '\t\tReport r = MakeReport();\n\t\tr.threads.clear();\n\t\tr.waits.clear();\n'
        '\t\tfor (int i = 0; i < kAll; i++) {\n')
t = sub(t, '\t\t\t\trow.agg.Add(Code(i < 100 && k < 4 ? State::R : State::S, 0));\n',
        '\t\t\t\trow.agg.Add(Code(i < kMust && k < 4 ? State::R : State::S, 0));\n')
t = sub(t, '\t\tCHECK(n_t == 96 + 24);\n', '\t\tCHECK(n_t == static_cast<int>(kMustCap + kOthersCap));\n')

# the -x tail (gap3p, ring_hold) without the line end; the F25 tail checked separately
t = sub(t, '\t\tCHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0\\n") != std::string::npos);\n',
        '\t\tCHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0") != std::string::npos);\n'
        '#ifdef KYTY_DIAG_B32_F25\n'
        '\t\t// F25d: then hist_exh, hist_exh_w, w_cut_w, others_cut_w; others_cut_w last\n'
        '\t\tCHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0 hist_exh=0 hist_exh_w=0 w_cut_w=0 others_cut_w=0\\n") !=\n'
        '\t\t      std::string::npos);\n'
        '#endif\n')
# RC9: -w cap - kWLinesCap + 17 records in all
t = sub(t, '\t\t// -w cap 64: the chain records are never cut, the rest by overlap\n'
           '\t\tReport r = MakeReport();\n\t\tfor (int i = 0; i < 80; i++) {\n',
        '\t\t// -w cap kWLinesCap: the chain records are never cut, the rest by overlap (F25d RC9: kWLinesCap + 17 records in\n'
        '\t\t// all - one of MakeReport and kWLinesCap + 16 here; was 80 at the cap 64)\n'
        '\t\tReport r = MakeReport();\n\t\tfor (int i = 0; i < static_cast<int>(kWLinesCap) + 16; i++) {\n')
t = sub(t, '\t\tCHECK(c.w_cut == 81 - kWLinesCap);\n', '\t\tCHECK(c.w_cut == (kWLinesCap + 17) - kWLinesCap);\n')
t = sub(t, '\tCHECK(text.find(" gap3p=0 ring_hold=8 ring_hold_w=3\\n") != std::string::npos); // at the end of the -x line\n',
        '\tCHECK(text.find(" gap3p=0 ring_hold=8 ring_hold_w=3") != std::string::npos); // after gap3p\n'
        '#ifdef KYTY_DIAG_B32_F25\n'
        '\tCHECK(text.find(" ring_hold_w=3 hist_exh=0 hist_exh_w=0 w_cut_w=0 others_cut_w=0\\n") != std::string::npos);\n'
        '#endif\n')

t = sub(t, '#include <vector>\n\nusing namespace Common::DiagB32;\n',
        '#include <vector>\n\n#ifdef _WIN32\n#ifndef NOMINMAX\n#define NOMINMAX\n#endif\n#include <windows.h> // F25d: the thread priority of the CloseWindow time case\n#endif\n\n'
        'using namespace Common::DiagB32;\n')

NEW = r'''
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
'''
t = sub(t, '\nint main() {\n', NEW + '\nint main() {\n')
t = sub(t, '\tTestM5Charge();\n\tTestWaitLoopRuntime(); // runtime cases last: g_on stays on\n',
        '\tTestM5Charge();\n'
        '\tTestF25EdgesE1E2();\n'
        '\tTestF25Mandatory150();\n'
        '\tTestF25Windows();\n'
        '\tTestF25Ring20000();\n'
        '#ifdef KYTY_DIAG_B32_F25\n'
        '\tTestF25XIdentity();\n'
        '\tTestF25BenchWindows();\n'
        '\tTestF25CloseTime();\n'
        '#endif\n'
        '\tTestWaitLoopRuntime(); // runtime cases last: g_on stays on\n')
open(ROOT + '/' + T, 'wb').write(t.encode('utf-8'))
print('TESTS PATCH OK')
