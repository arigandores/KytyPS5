# F25d (HPP-667; ROADMAP s122 items 596(v), 599(b)(8), (9), (11), (v)): the F25 fix of KYTY_DIAG_B32 - C1 kHist 4096,
# C2 kWaitRing 65536, C3 hist_exh / hist_exh_w, C4 cover_us, C5a kWLinesCap 4096, C5b kMustCap 256, C5v w_cut_w,
# C5g kOthersCap 256 + others_cut_w, C6 flip_ns; the test hook Test::CloseWindowBench (RC8 timing member).
# Usage: python patch_f25d.py <worktree root>. Anchors are whole lines; files are read with CR removed and written LF.
import sys

ROOT = sys.argv[1].rstrip('/\\')


def load(rel):
    return open(ROOT + '/' + rel, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def save(rel, text):
    open(ROOT + '/' + rel, 'wb').write(text.encode('utf-8'))


def sub(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor count %d != %d: %r' % (n, count, old[:120]))
    return text.replace(old, new)


# ---------------------------------------------------------------- diagB32.h
H = 'src/common/diagB32.h'
h = load(H)
h = sub(h, 'constexpr uint32_t kHist          = 512;       // per-slot history ring: 512 samples x 5 ms = 2.56 s (RC1: >= 2 s)\n'
           'constexpr uint32_t kWaitRing      = 4096;\n'
           'constexpr uint32_t kOthersCap     = 24;        // RC2: the cap applies only to the non-mandatory -t lines\n'
           'constexpr uint32_t kMustCap       = 96;        // a mandatory -t line beyond this is cut and counted in lines_cut\n'
           'constexpr uint32_t kWLinesCap     = 64;\n',
        '// F25d (HPP-667; ROADMAP s122 items 596(v), 599(b)(9)): C1 kHist 512 -> 4096 (20.48 s at P = 5 ms: a window up to\n'
        '// (kHist - 1) x P = 20.475 s keeps its start), C2 kWaitRing 4096 -> 65536, C5a kWLinesCap 64 -> 4096, C5b kMustCap\n'
        '// 96 -> 256 (= kSlots: lines_cut stays 0 by construction), C5g kOthersCap 24 -> 256 (= kSlots: others_cut stays 0).\n'
        'constexpr uint32_t kHist          = 4096;      // per-slot history ring: 4096 samples x 5 ms = 20.48 s (F25 C1)\n'
        'constexpr uint32_t kWaitRing      = 65536;     // F25 C2\n'
        'constexpr uint32_t kOthersCap     = 256;       // RC2: the cap applies only to the non-mandatory -t lines (F25 C5g)\n'
        'constexpr uint32_t kMustCap       = 256;       // a mandatory -t line beyond this is cut and counted in lines_cut (F25 C5b)\n'
        'constexpr uint32_t kWLinesCap     = 4096;      // F25 C5a\n')
h = sub(h, '#include <cstddef>\n#include <cstdint>\n#include <string>\n#include <vector>\n',
        '#include <cstddef>\n#include <cstdint>\n#include <string>\n#include <vector>\n\n'
        '// F25d (HPP-667): the F25 fields (hist_exh, cover_us, flip_ns, w_cut_w, others_cut_w) and Test::CloseWindowBench exist.\n'
        '#define KYTY_DIAG_B32_F25 1\n')
h = sub(h, '\t// F20j3 (item 554(v)(1), Z1 of F20k2): wait-ring positions a drain left behind (an unfinished write stopped it).\n'
           '\tuint64_t ring_hold    = 0;\n',
        '\t// F20j3 (item 554(v)(1), Z1 of F20k2): wait-ring positions a drain left behind (an unfinished write stopped it).\n'
        '\tuint64_t ring_hold    = 0;\n'
        '\t// F25d (item 596(v), C3): windows whose start the history ring no longer held (each also counts in ring_drop).\n'
        '\tuint64_t hist_exh     = 0;\n')
h = sub(h, '\t\tuint64_t ring_hold = 0;\n\t} base;\n',
        '\t\tuint64_t ring_hold = 0;\n'
        '\t\tuint64_t hist_exh  = 0; // F25d C3\n'
        '\t\tuint64_t w_cut     = 0; // F25d C5v: w_cut_w\n'
        '\t\tuint64_t others_cut = 0; // F25d C5g: others_cut_w\n'
        '\t} base;\n')
h = sub(h, '\tint32_t  gpu_slot1    = 0;\n\tstd::vector<ThreadRow> threads;\n',
        '\tint32_t  gpu_slot1    = 0;\n'
        '\t// F25d (item 596(v), C4): the flip minus the time of the oldest sample of the window (0 - no sample), us.\n'
        '\tuint64_t cover_us     = 0;\n'
        '\tstd::vector<ThreadRow> threads;\n')
h = sub(h, 'void DrainWaits(std::vector<Core::WaitRec>* out);\n} // namespace Test\n',
        'void DrainWaits(std::vector<Core::WaitRec>* out);\n'
        '// F25d (HPP-667; ROADMAP s122 item 599(b)(8), RC8 of F25c): one window of a sampler built in memory, closed once by\n'
        '// Sampler::CloseWindow and timed. nslots registered slots (a registry of its own, swapped in for the call), before\n'
        '// samples at or before the window start and nsamples samples period_ns apart after it (the last one at the flip),\n'
        '// random codes; nwaits closed wait records inside the window (the slots in turn, random wakers), open W marks on\n'
        '// nopen slots. The report text is taken out of the report slot. Tests only (not called by the emulator).\n'
        'struct BenchIn {\n'
        '\tuint32_t nslots    = 90;\n'
        '\tuint32_t before    = 1;\n'
        '\tuint32_t nsamples  = 4096;\n'
        '\tuint32_t nwaits    = 0;\n'
        '\tuint32_t nopen     = 0;\n'
        '\tuint32_t nmatch    = 0; // the first nmatch closed records repeat an open record\'s slot and start (dropped open)\n'
        '\tuint32_t kq_every  = 0; // every kq_every-th sample has its own kernel snapshot (0 - none)\n'
        '\tuint64_t period_ns = kPeriodNs;\n'
        '\tuint32_t seed      = 1;\n'
        '};\n'
        'struct BenchOut {\n'
        '\tuint64_t    close_ns = 0; // the wall of CloseWindow\n'
        '\tuint64_t    start_ns = 0; // the window start (the previous flip)\n'
        '\tuint64_t    flip_ns  = 0;\n'
        '\tstd::string text;\n'
        '};\n'
        'BenchOut CloseWindowBench(const BenchIn& in);\n'
        '} // namespace Test\n')
save(H, h)

# ---------------------------------------------------------------- diagB32.cpp
C = 'src/common/diagB32.cpp'
c = load(C)
# C4, C6: cover_us and flip_ns at the end of the DiagB32: line
c = sub(c, '\t       " flip_slot=%d flip_tid=%d flip_src=%s lat_us=%llu vo_slot=%d gpu_slot=%d t_lines=%zu w_lines=%zu c_lines=%zu\\n",\n',
        '\t       " flip_slot=%d flip_tid=%d flip_src=%s lat_us=%llu vo_slot=%d gpu_slot=%d t_lines=%zu w_lines=%zu c_lines=%zu"\n'
        '\t       " cover_us=%llu flip_ns=%llu\\n", // F25d (items 596(v) C4, 599(b)(11) C6): flip_ns - the FrameStats::NowNs scale, last\n')
c = sub(c, '\t       SlotIndex(r.vo_slot1), SlotIndex(r.gpu_slot1), must.size() + others.size(), picks.size(), cpu.size());\n',
        '\t       SlotIndex(r.vo_slot1), SlotIndex(r.gpu_slot1), must.size() + others.size(), picks.size(), cpu.size(),\n'
        '\t       static_cast<unsigned long long>(r.cover_us), static_cast<unsigned long long>(r.win_end_ns));\n')
# C3, C5v, C5g: the -x tail
c = sub(c, '\t// F20j3 (item 554(v)(1), Z1): ring_hold / ring_hold_w at the end of the line.\n',
        '\t// F20j3 (item 554(v)(1), Z1): ring_hold / ring_hold_w at the end of the line. F25d (items 596(v), 599(b)(9)): then\n'
        '\t// hist_exh / hist_exh_w (C3), w_cut_w (C5v), others_cut_w (C5g) - others_cut_w is the last field.\n')
c = sub(c, '\t       " ring_hold=%llu ring_hold_w=%llu\\n",\n',
        '\t       " ring_hold=%llu ring_hold_w=%llu hist_exh=%llu hist_exh_w=%llu w_cut_w=%llu others_cut_w=%llu\\n",\n')
c = sub(c, '\t       r.gaps.gap3p, static_cast<unsigned long long>(counters->ring_hold), dw(counters->ring_hold, b.ring_hold));\n\treturn out;\n',
        '\t       r.gaps.gap3p, static_cast<unsigned long long>(counters->ring_hold), dw(counters->ring_hold, b.ring_hold),\n'
        '\t       static_cast<unsigned long long>(counters->hist_exh), dw(counters->hist_exh, b.hist_exh),\n'
        '\t       dw(counters->w_cut, b.w_cut), dw(counters->others_cut, b.others_cut));\n'
        '\treturn out;\n')
c = sub(c, '\tbase.ring_hold = ring_hold;\n}\n',
        '\tbase.ring_hold = ring_hold;\n'
        '\tbase.hist_exh  = hist_exh;   // F25d C3\n'
        '\tbase.w_cut     = w_cut;      // F25d C5v\n'
        '\tbase.others_cut = others_cut; // F25d C5g\n'
        '}\n')
# C3: the history ring no longer holds the window start
c = sub(c, '\tif (exhausted) {\n\t\tm_c.ring_drop++; // the history ring no longer holds the start of this window\n\t}\n',
        '\tif (exhausted) {\n'
        '\t\tm_c.ring_drop++; // the history ring no longer holds the start of this window\n'
        '\t\tm_c.hist_exh++;  // F25d (item 596(v), C3): the same event, its own counter\n'
        '\t}\n')
# C4: cover_us
c = sub(c, '\tr.gaps         = Core::Gaps(times.data(), times.size(), start, flip_ns, kPeriodNs);\n',
        '\tr.gaps         = Core::Gaps(times.data(), times.size(), start, flip_ns, kPeriodNs);\n'
        '\tr.cover_us     = times.empty() ? 0 : (flip_ns - times.front()) / 1000u; // F25d (item 596(v), C4)\n')
# the bench is a friend of the sampler
c = sub(c, 'class Sampler {\npublic:\n\tvoid Run();\n\nprivate:\n',
        'class Sampler {\npublic:\n\tvoid Run();\n\n'
        '\tfriend Test::BenchOut Test::CloseWindowBench(const Test::BenchIn& in); // F25d (item 599(b)(8))\n\n'
        'private:\n')
BENCH = r'''
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
'''
c = sub(c, '\t\tg_ring->Drain(out, &drop, &torn);\n\t}\n}\n\n} // namespace Test\n',
        '\t\tg_ring->Drain(out, &drop, &torn);\n\t}\n}\n' + BENCH + '\n} // namespace Test\n')
if '#include <random>' not in c:
    c = sub(c, '#include <algorithm>\n', '#include <algorithm>\n#include <random>\n')
if '#include <chrono>' not in c:
    c = sub(c, '#include <algorithm>\n', '#include <algorithm>\n#include <chrono>\n')
save(C, c)
print('PATCH OK')
