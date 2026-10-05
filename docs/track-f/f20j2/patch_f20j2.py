"""F20j2 (HPP-633, ROADMAP s122 item 552(v)(1)-(7), (d)): the KYTY_DIAG_B32 changes by the review F20k (RC1-RC7).

Usage: python patch_f20j2.py <tree root> [--check]
Every edit replaces a block of WHOLE lines that must occur exactly once in its file (anchors are whole lines; a block
that is not found, or found twice, stops the script before anything is written). Files are read in binary, CR is
removed before the search and put back if the file had CRLF; output is written with write_bytes. Prints ALL OK.
--check: only reports whether every edit is already applied (the new block present, the old one absent).
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')
CHECK = '--check' in sys.argv[2:]

EDITS = []  # (relative path, old block, new block)


def edit(path, old, new):
    EDITS.append((path, old, new))


# =====================================================================================================================
# src/common/diagB32.h
# =====================================================================================================================
H = 'src/common/diagB32.h'

edit(H, r'''constexpr uint64_t kKernelAfterNs = 40000000;  // RC3: kernel thread state only in samples >= 40 ms after the previous flip
''', r'''constexpr uint64_t kKernelAfterNs = 40000000;  // RC3: kernel thread state only in samples >= 40 ms after the previous flip
// F20j2 (HPP-633; ROADMAP s122 item 552(v)(1), RC1 of F20k): the kernel query schedule - a query of the open window only
// if (its kernel-query time + the last query's cost) <= window / kKqBudgetDiv; an S sample without its own query is
// split by the nearest snapshot of the same window not farther than kKqNearNs (at the window close).
constexpr uint64_t kKqBudgetDiv   = 10;
constexpr uint64_t kKqNearNs      = 60000000;
''')

edit(H, r'''// t - the sample times inside (win_start, win_end], in the order they were taken.
[[nodiscard]] GapStats Gaps(const uint64_t* t, size_t n, uint64_t win_start, uint64_t win_end, uint64_t period_ns);
''', r'''// t - the sample times inside (win_start, win_end], in the order they were taken.
[[nodiscard]] GapStats Gaps(const uint64_t* t, size_t n, uint64_t win_start, uint64_t win_end, uint64_t period_ns);

// F20j2 (item 552(v)(1), RC1 of F20k): the kernel query schedule of the sampler. A sample queries the kernel thread
// state only if >= kKernelAfterNs passed since the previous flip and (the kernel-query time of the open window + the
// cost of the last query) <= (time since the previous flip) / kKqBudgetDiv. The first query of the process (no last
// cost yet) - at the first sample >= kKernelAfterNs. The start probe of Run (kstate) does not enter the schedule.
struct KqSchedule {
	uint64_t win_start  = 0; // the previous flip (0 - no flip yet: no query)
	uint64_t win_kq_ns  = 0; // kernel-query time inside the open window
	uint64_t last_kq_ns = 0; // the cost of the last query (0 - none yet)
	[[nodiscard]] bool Due(uint64_t now_ns) const;
	void               Done(uint64_t cost_ns);
	// The window closed at flip_ns; carried_kq_ns - kernel-query time of samples already after flip_ns.
	void NewWindow(uint64_t flip_ns, uint64_t carried_kq_ns);
};

// F20j2 (item 552(v)(1), RC1(b) of F20k): the absolute sample period. The next sample begins P after the BEGIN of the
// previous one; a sample (with the boundary work after it) longer than P is followed at once - no catch-up of the
// missed periods, the kernel query does not stretch the step.
[[nodiscard]] uint64_t NextBegin(uint64_t begin_ns, uint64_t now_ns);

// F20j2 (item 552(v)(1)): for the n samples of one window (t - sample times, oldest first; kq[i] - sample i has its own
// kernel snapshot taken at kq_t[i]) out[i] = i for a sample with its own snapshot; otherwise the index of the sample
// whose snapshot is nearest in time to t[i] and not farther than max_ns (ties - the earlier one), or -1.
void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,
                     int32_t* out);
''')

edit(H, r'''class WaitRing {
public:
	void Push(const WaitRec& rec);
	// Moves every record written since the previous call into out; records overwritten before this call are counted in
	// drop, records whose write did not settle after 3 attempts in torn.
	void Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn);
''', r'''class WaitRing {
public:
	void Push(const WaitRec& rec); // = Write(Reserve(), rec)
	// F20j2 (RC4 of F20k): the two halves of Push - the position, then the record (a writer can be preempted between).
	uint64_t Reserve();
	void     Write(uint64_t i, const WaitRec& rec);
	// Moves every record written since the previous call into out, oldest first. Positions the reader no longer holds
	// (more than kWaitRing behind) are counted in drop. F20j2 (item 552(v)(4), RC4 of F20k): the drain stops at a
	// position whose write has not finished (not started, or in progress) and continues there on the next call; torn
	// counts only a position overwritten by a later lap (before or while it is read).
	void Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn);
''')

edit(H, r'''	uint64_t kq_fail      = 0;
	uint64_t print_us     = 0; // wall of the previous report's print on the present thread (reference)
};
''', r'''	uint64_t kq_fail      = 0;
	uint64_t print_us     = 0; // wall of the previous report's print on the present thread (reference)
	// F20j2 (item 552(v)(7), RC7 of F20k): a flip whose request entry (ring of 64) / submission entry (ring of 1024) was
	// overwritten before it was read.
	uint64_t req_miss     = 0;
	uint64_t sub_miss     = 0;
	// F20j2 (item 552(v)(3), RC3 of F20k): the zero invariants at the previous window close; Format prints
	// <name>_w = value - base (the increment over the window) next to the cumulative value. Rebase at every close.
	struct Base {
		uint64_t slot_full = 0;
		uint64_t torn      = 0;
		uint64_t ring_drop = 0;
		uint64_t sgap_bad  = 0;
		uint64_t lines_cut = 0;
		uint64_t req_miss  = 0;
		uint64_t sub_miss  = 0;
	} base;
	void Rebase();
};
''')

edit(H, r'''	uint32_t kq           = 0; // samples of the window with the kernel state
''', r'''	uint32_t kq           = 0; // samples of the window with the kernel state
	uint32_t kq_n         = 0; // F20j2 (item 552(v)(1)): kernel queries in the window
	uint64_t kq_us        = 0; // F20j2: their time (inside instr_us too)
	uint64_t m5r_us       = 0; // F20j2 (item 552(e)(3)): the thread-list refresh (CreateToolhelp32Snapshot) in the window (inside instr_us)
''')

edit(H, r'''// Mandatory -t lines (RC2): the present thread, GuestGpu, flip_slot, every waiting thread / waker / peer of the
// window's -w records, every thread with R >= 10 % of the window samples. Sets ThreadRow::must.
''', r'''// Mandatory -t lines (RC2): the present thread, GuestGpu, flip_slot, every waiting thread / waker / peer of the
// window's -w records, every thread with R >= 10 % of the window samples; F20j2 (item 552(v)(5), RC5 of F20k): the async
// submitter (role ASubmit) in a window where it has at least one H:qlock / H:qsubmit sample. Sets ThreadRow::must.
''')

edit(H, r'''[[nodiscard]] std::string HeaderLine(uint32_t ncpu, uint32_t kstate);
''', r'''// kq_us - the cost of the first kernel query of the process (the start probe of the sampler; F20j2, item 552(v)(1)).
[[nodiscard]] std::string HeaderLine(uint32_t ncpu, uint32_t kstate, uint64_t kq_us);
''')

# =====================================================================================================================
# src/common/diagB32.cpp
# =====================================================================================================================
C = 'src/common/diagB32.cpp'

edit(C, r'''	const uint64_t window = win_end > win_start ? win_end - win_start : 0;
	g.i2_ok               = period_ns > 0 && static_cast<uint64_t>(n) >= window / (2 * period_ns);
	return g;
}
''', r'''	const uint64_t window = win_end > win_start ? win_end - win_start : 0;
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
	for (size_t i = 0; i < n; i++) {
		if (kq[i] != 0) {
			out[i] = static_cast<int32_t>(i);
			continue;
		}
		int32_t  best   = -1;
		uint64_t best_d = 0;
		for (size_t j = 0; j < n; j++) {
			if (kq[j] == 0) {
				continue;
			}
			const auto d = t[i] > kq_t[j] ? t[i] - kq_t[j] : kq_t[j] - t[i];
			if (d <= max_ns && (best < 0 || d < best_d)) {
				best   = static_cast<int32_t>(j);
				best_d = d;
			}
		}
		out[i] = best;
	}
}
''')

edit(C, r'''void WaitRing::Push(const WaitRec& rec) {
	const auto i = wpos.fetch_add(1, std::memory_order_acq_rel);
	auto&      x = e[i % kWaitRing];
''', r'''void WaitRing::Push(const WaitRec& rec) {
	Write(Reserve(), rec);
}

uint64_t WaitRing::Reserve() {
	return wpos.fetch_add(1, std::memory_order_acq_rel);
}

void WaitRing::Write(uint64_t i, const WaitRec& rec) {
	auto& x = e[i % kWaitRing];
''')

edit(C, r'''	for (; rpos < w; rpos++) {
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
''', r'''	while (rpos < w) {
		auto&      x    = e[rpos % kWaitRing];
		const auto want = 2 * rpos + 2;
		const auto s1   = x.seq.load(std::memory_order_acquire);
		if (s1 < want) {
			// F20j2 (RC4): the write of this position has not finished - not started (an older lap's word) or in progress
			// (2 * rpos + 1; the writer may be preempted between Reserve and the final word). Stop here; the next drain
			// (the next flip) continues from this position.
			break;
		}
		if (s1 == want) {
			WaitRec r;
			r.start_ns     = x.start.load(std::memory_order_relaxed);
			r.end_ns       = x.end.load(std::memory_order_relaxed);
			r.obj          = x.obj.load(std::memory_order_relaxed);
			r.req_us       = x.req.load(std::memory_order_relaxed);
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
''')

edit(C, r'''	for (auto& t: r.threads) {
		t.must = t.slot1 == r.vo_slot1 || t.slot1 == r.gpu_slot1 || t.slot1 == r.flip_slot1 ||
		         (samples > 0 && t.agg.st[static_cast<size_t>(State::R)] * 10 >= samples);
	}
''', r'''	for (auto& t: r.threads) {
		// F20j2 RC5: the async submitter in a window where it waited for / held graphics.queue_mutex.
		const bool asub = t.role == "ASubmit" &&
		                  t.agg.h[static_cast<size_t>(Call::QLock)] + t.agg.h[static_cast<size_t>(Call::QSubmit)] > 0;
		t.must = t.slot1 == r.vo_slot1 || t.slot1 == r.gpu_slot1 || t.slot1 == r.flip_slot1 ||
		         (samples > 0 && t.agg.st[static_cast<size_t>(State::R)] * 10 >= samples) || asub;
	}
''')

edit(C, r'''	Append(&out,
	       "DiagB32: n=%llu dt_us=%llu instr_us=%llu samples=%u sgap_max_us=%llu gap3p=%u i2=%d kstate=%u kq=%u"
	       " proc_us=%llu sys_busy_us=%llu sys_idle_us=%llu other_us=%lld ncpu=%u snap_ok=%u snap_lag_us=%llu"
	       " flip_slot=%d flip_tid=%d flip_src=%s lat_us=%llu vo_slot=%d gpu_slot=%d t_lines=%zu w_lines=%zu c_lines=%zu\n",
	       n, static_cast<unsigned long long>(r.dt_us), static_cast<unsigned long long>(r.instr_us), r.gaps.samples,
	       static_cast<unsigned long long>(r.gaps.sgap_max_ns / 1000u), r.gaps.gap3p, r.gaps.i2_ok && r.gaps.monotonic ? 1 : 0,
	       r.kstate, r.kq, static_cast<unsigned long long>(r.proc_us), static_cast<unsigned long long>(r.sys_busy_us),
''', r'''	Append(&out,
	       "DiagB32: n=%llu dt_us=%llu instr_us=%llu samples=%u sgap_max_us=%llu gap3p=%u i2=%d kstate=%u kq=%u"
	       " kq_n=%u kq_us=%llu m5r_us=%llu"
	       " proc_us=%llu sys_busy_us=%llu sys_idle_us=%llu other_us=%lld ncpu=%u snap_ok=%u snap_lag_us=%llu"
	       " flip_slot=%d flip_tid=%d flip_src=%s lat_us=%llu vo_slot=%d gpu_slot=%d t_lines=%zu w_lines=%zu c_lines=%zu\n",
	       n, static_cast<unsigned long long>(r.dt_us), static_cast<unsigned long long>(r.instr_us), r.gaps.samples,
	       static_cast<unsigned long long>(r.gaps.sgap_max_ns / 1000u), r.gaps.gap3p, r.gaps.i2_ok && r.gaps.monotonic ? 1 : 0,
	       r.kstate, r.kq, r.kq_n, static_cast<unsigned long long>(r.kq_us), static_cast<unsigned long long>(r.m5r_us),
	       static_cast<unsigned long long>(r.proc_us), static_cast<unsigned long long>(r.sys_busy_us),
''')

edit(C, r'''	Append(&out,
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
''', r'''	// F20j2 (item 552(v)(3), RC3 of F20k): every zero invariant cumulative and its increment over this window (_w).
	const auto& b  = counters->base;
	const auto  dw = [](uint64_t v, uint64_t base) { return static_cast<unsigned long long>(v >= base ? v - base : 0); };
	Append(&out,
	       "DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu torn=%llu torn_w=%llu ring_drop=%llu ring_drop_w=%llu"
	       " sgap_bad=%llu sgap_bad_w=%llu lines_cut=%llu lines_cut_w=%llu req_miss=%llu req_miss_w=%llu sub_miss=%llu"
	       " sub_miss_w=%llu short_stalls=%llu others_cut=%llu w_cut=%llu rep_drop=%llu kq_fail=%llu print_us=%llu gap3p=%u\n",
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
	       r.gaps.gap3p);
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
}
''')

edit(C, r'''std::string HeaderLine(uint32_t ncpu, uint32_t kstate) {
	char buf[256];
	std::snprintf(buf, sizeof(buf),
	              "DiagB32: mode=1 period_us=%llu print_us=%llu wait_rec_us=%llu kernel_after_us=%llu slots=%u hist=%u"
	              " wring=%u ncpu=%u kstate=%u\n",
	              static_cast<unsigned long long>(kPeriodNs / 1000u), static_cast<unsigned long long>(kPrintNs / 1000u),
	              static_cast<unsigned long long>(kWaitRecNs / 1000u), static_cast<unsigned long long>(kKernelAfterNs / 1000u),
	              kSlots, kHist, kWaitRing, ncpu, kstate);
	return buf;
}
''', r'''std::string HeaderLine(uint32_t ncpu, uint32_t kstate, uint64_t kq_us) {
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
''')

edit(C, r'''struct FlipEnt {
	std::atomic<uint64_t> n {0};
	std::atomic<uint64_t> ns {0};
	std::atomic<uint64_t> lat_us {0};
	std::atomic<int32_t>  slot1 {0};
	std::atomic<uint32_t> src {0};
};
''', r'''struct FlipEnt {
	std::atomic<uint64_t> n {0};
	std::atomic<uint64_t> ns {0};
	std::atomic<uint64_t> lat_us {0};
	std::atomic<int32_t>  slot1 {0};
	std::atomic<uint32_t> src {0};
	std::atomic<uint64_t> print_ns {0}; // F20j2 RC6: the report print of the previous OnFlip - inside the window this flip closes
};
''')

edit(C, r'''RepSlot               g_rep[4];
std::atomic<uint64_t> g_print_us {0};
''', r'''RepSlot               g_rep[4];
std::atomic<uint64_t> g_print_us {0};
uint64_t              g_print_prev_ns = 0; // present thread only (OnFlip): the print time of its previous call (F20j2 RC6)
std::atomic<uint64_t> g_req_miss {0};      // F20j2 RC7: OnFlip found the request entry overwritten
std::atomic<uint64_t> g_sub_miss {0};      // F20j2 RC7: NoteFlipRequest found the submission entry overwritten
std::atomic<uint64_t> g_kq_first_us {0};   // F20j2 (item 552(v)(1)): the cost of the first kernel query (start probe)
''')

edit(C, r'''		auto&      e   = g_submit[seq % 1024];
		if (e.seq.load(std::memory_order_acquire) == seq) {
			slot1 = e.slot1.load(std::memory_order_relaxed);
		}
	}
''', r'''		auto&      e   = g_submit[seq % 1024];
		if (e.seq.load(std::memory_order_acquire) == seq) {
			slot1 = e.slot1.load(std::memory_order_relaxed);
		} else {
			g_sub_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten
		}
	}
''')

edit(C, r'''	if (r.id.load(std::memory_order_acquire) == request_id) {
		slot1 = r.slot1.load(std::memory_order_relaxed);
		src   = r.src.load(std::memory_order_relaxed);
	}
	const auto k = g_flip_pub.load(std::memory_order_relaxed);
''', r'''	if (r.id.load(std::memory_order_acquire) == request_id) {
		slot1 = r.slot1.load(std::memory_order_relaxed);
		src   = r.src.load(std::memory_order_relaxed);
	} else {
		g_req_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten
	}
	const auto k = g_flip_pub.load(std::memory_order_relaxed);
''')

edit(C, r'''	e.slot1.store(slot1, std::memory_order_relaxed);
	e.src.store(src, std::memory_order_relaxed);
	g_flip_pub.store(k + 1, std::memory_order_release);
''', r'''	e.slot1.store(slot1, std::memory_order_relaxed);
	e.src.store(src, std::memory_order_relaxed);
	e.print_ns.store(g_print_prev_ns, std::memory_order_relaxed);
	g_flip_pub.store(k + 1, std::memory_order_release);
''')

edit(C, r'''	// Print the reports the sampler has closed (each one once, in the order of n).
	for (;;) {
''', r'''	// Print the reports the sampler has closed (each one once, in the order of n). F20j2 RC6: this runs under
	// FlipQueue::m_mutex and VideoOutConfig::mutex (videoOut.cpp); the whole print time of this call lies after this
	// flip, so it is published with the next flip and added to instr_us of the window that flip closes.
	uint64_t print_ns = 0;
	for (;;) {
''')

edit(C, r'''		best->state.store(0, std::memory_order_release);
		g_print_us.store((FrameStats::NowNs() - t0) / 1000u, std::memory_order_relaxed);
	}
}
''', r'''		best->state.store(0, std::memory_order_release);
		const auto took = FrameStats::NowNs() - t0;
		print_ns += took;
		g_print_us.store(took / 1000u, std::memory_order_relaxed);
	}
	g_print_prev_ns = print_ns;
}
''')

edit(C, r'''	void     Sample(uint64_t t0);
''', r'''	void     Sample(uint64_t begin);
''')

edit(C, r'''	void     CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
	                     uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us);
''', r'''	void     CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
	                     uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us, uint64_t print_ns);
	void     RefreshCounters();
''')

edit(C, r'''	uint64_t                  m_cost[kHist] {};
	uint8_t                   m_kq[kHist] {};
''', r'''	uint64_t                  m_cost[kHist] {};
	uint8_t                   m_kq[kHist] {};
	uint64_t                  m_kqt[kHist] {};  // F20j2 RC2: the kernel snapshot time of the sample (own field)
	uint64_t                  m_kqc[kHist] {};  // F20j2 RC1: the kernel-query time of the sample (0 - no query)
	// F20j2 (item 552(v)(1)): per slot, the kernel-only class (Sr / Sw:<reason> / S) at the samples with a snapshot.
	std::vector<uint16_t>     m_kcodes = std::vector<uint16_t>(static_cast<size_t>(kSlots) * kHist, 0);
	Core::KqSchedule          m_sched;
	uint64_t                  m_win_m5r_ns = 0;
''')

edit(C, r'''void Sampler::Sample(uint64_t t0) {
	const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;
	bool           kq       = false;
	if (m_kq_ok && m_win_start != 0 && t0 >= m_win_start + kKernelAfterNs) {
		KernelQuery();
		kq = !m_kmap.empty();
	}
	const auto n   = std::min<uint32_t>(g_reg->count.load(std::memory_order_acquire), kSlots);
''', r'''void Sampler::Sample(uint64_t begin) {
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
''')

edit(C, r'''			uint32_t ks = 0;
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
''', r'''			uint32_t ks = 0;
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
''')

edit(C, r'''void Sampler::CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
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
''', r'''void Sampler::RefreshCounters() {
	m_c.slot_full = g_reg->slot_full.load(std::memory_order_relaxed);
	m_c.torn      = g_reg->torn.load(std::memory_order_relaxed) + m_ring_torn;
	m_c.req_miss  = g_req_miss.load(std::memory_order_relaxed);
	m_c.sub_miss  = g_sub_miss.load(std::memory_order_relaxed);
}

void Sampler::CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,
                          uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us, uint64_t print_ns) {
	const uint64_t start = m_win_start;
	const uint64_t extra = m_win_extra_ns + print_ns; // F20j2 RC6: the report print inside this window
	const uint64_t m5r   = m_win_m5r_ns;
	m_win_start          = flip_ns;
	m_win_extra_ns       = 0;
	m_win_m5r_ns         = 0;
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
''')

edit(C, r'''	std::vector<uint64_t> times;
	for (auto h: idx) {
		times.push_back(m_t[h % kHist]);
	}
	Core::Report r;
''', r'''	std::vector<uint64_t> times;
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
''')

edit(C, r'''	r.kstate       = g_kstate.load(std::memory_order_relaxed);
	r.kq           = kq;
''', r'''	r.kstate       = g_kstate.load(std::memory_order_relaxed);
	r.kq           = kq;
	r.kq_n         = kq_n;
	r.kq_us        = kq_ns / 1000u;
	r.m5r_us       = m5r / 1000u;
''')

edit(C, r'''		Core::ThreadRow row;
		for (auto h: idx) {
			row.agg.Add(m_codes[static_cast<size_t>(i) * kHist + h % kHist]);
		}
''', r'''		Core::ThreadRow row;
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
''')

edit(C, r'''	m_c.slots     = nslots;
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
''', r'''	m_c.slots    = nslots;
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
''')

edit(C, r'''	if (t0 >= m_m5_next) {
		M5Refresh(t0);
	}
''', r'''	uint64_t m5r = 0;
	if (t0 >= m_m5_next) {
		M5Refresh(t0);
		m5r = FrameStats::NowNs() - t0; // F20j2 (item 552(e)(3)): the refresh's share of the boundary work
	}
''')

edit(C, r'''		const auto src     = e.src.load(std::memory_order_relaxed);
		const bool last    = k + 1 == pub;
		const auto lag_us  = t0 > ns ? (t0 - ns) / 1000u : 0;
		CloseWindow(n, ns, lat, slot1, src, last && !batch, proc_us, busy_us, idle_us, lag_us);
	}
''', r'''		const auto src     = e.src.load(std::memory_order_relaxed);
		const auto prn     = e.print_ns.load(std::memory_order_relaxed);
		const bool last    = k + 1 == pub;
		const auto lag_us  = t0 > ns ? (t0 - ns) / 1000u : 0;
		CloseWindow(n, ns, lat, slot1, src, last && !batch, proc_us, busy_us, idle_us, lag_us, prn);
	}
''')

edit(C, r'''	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us).
	m_win_extra_ns += FrameStats::NowNs() - t0;
}
''', r'''	// The boundary work runs after the flip: it is sampler time inside the new window (RC9 instr_us).
	m_win_extra_ns += FrameStats::NowNs() - t0;
	m_win_m5r_ns += m5r;
}
''')

edit(C, r'''	m_kmap.reserve(1024);
	if (m_ntq != nullptr) {
		KernelQuery();
		m_kq_ok = !m_kmap.empty();
	}
''', r'''	m_kmap.reserve(1024);
	if (m_ntq != nullptr) {
		const auto q0 = FrameStats::NowNs();
		KernelQuery();
		g_kq_first_us.store((FrameStats::NowNs() - q0) / 1000u, std::memory_order_relaxed); // F20j2: kq_us of mode=1
		m_kq_ok = !m_kmap.empty();
	}
''')

edit(C, r'''	SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);
	for (;;) {
		const DWORD r = WaitForMultipleObjects(2, handles, FALSE, 1000);
		if (r == WAIT_OBJECT_0) {
			Sample(FrameStats::NowNs());
			SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);
		}
		ProcessFlips();
	}
}
''', r'''	SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);
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
''')

edit(C, r'''	const auto text = Core::HeaderLine(g_ncpu, g_kstate.load(std::memory_order_relaxed));
''', r'''	const auto text = Core::HeaderLine(g_ncpu, g_kstate.load(std::memory_order_relaxed),
	                                   g_kq_first_us.load(std::memory_order_relaxed));
''')

# =====================================================================================================================
# sites (RC5, RC6)
# =====================================================================================================================
S1 = 'src/graphics/host_gpu/renderer/commandScheduler.cpp'
edit(S1, r'''	void Loop() {
		for (;;) {
			Record record;
''', r'''	void Loop() {
		// Track F, F20j2 (KYTY_DIAG_B32, RC5 of F20k): the async submitter's own slot and role (mandatory -t line in a
		// window where it waited for or held graphics.queue_mutex).
		if (Common::DiagB32::g_on) [[unlikely]] {
			Common::DiagB32::RegisterRole("ASubmit");
		}
		for (;;) {
			Record record;
''')
edit(S1, r'''			uint64_t   locked_ns = 0;
			{
				Common::LockGuard lock(graphics.queue_mutex);
				locked_ns    = Common::FrameStats::NowNs();
''', r'''			uint64_t   locked_ns = 0;
			{
				Common::DiagB32::Mark b32_q; // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock / H:qsubmit, RC5 of F20k)
				if (Common::DiagB32::g_on) [[unlikely]] {
					b32_q.BeginH(Common::DiagB32::Call::QLock);
				}
				Common::LockGuard lock(graphics.queue_mutex);
				b32_q.End(0, false);
				locked_ns    = Common::FrameStats::NowNs();
''')
edit(S1, r'''				RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, false,
				                    vk::Result::eNotReady);
				result = graphics.queue.submit(1, &submit_info, nullptr);
				RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, true, result);
''', r'''				RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, false,
				                    vk::Result::eNotReady);
				if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qsubmit, RC5 of F20k)
					b32_q.BeginH(Common::DiagB32::Call::QSubmit);
				}
				result = graphics.queue.submit(1, &submit_info, nullptr);
				b32_q.End(0, false);
				RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, true, result);
''')

S2 = 'src/graphics/presentation/window/swapchain.cpp'
edit(S2, r'''	vk::Result result;
	{
		Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);
		result = m_window.graphic_ctx.queue.presentKHR(&present);
	}
''', r'''	vk::Result result;
	{
		// Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock, RC5 of F20k): nested in H:present - a sample shows the innermost mark,
		// End restores H:present.
		Common::DiagB32::Mark b32_q;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32_q.BeginH(Common::DiagB32::Call::QLock);
		}
		Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);
		b32_q.End(0, false);
		result = m_window.graphic_ctx.queue.presentKHR(&present);
	}
''')

S3 = 'src/graphics/presentation/systemOverlay.cpp'
edit(S3, r'''#include "common/assert.h"
#include "common/frameStats.h"
#include "common/stringUtils.h"
''', r'''#include "common/assert.h"
#include "common/diagB32.h"
#include "common/frameStats.h"
#include "common/stringUtils.h"
''')
edit(S3, r'''		{
			Common::LockGuard queue_lock(graphics.queue_mutex);
			ImGui_ImplVulkan_RenderDrawData(ImGui::GetDrawData(),
			                                static_cast<VkCommandBuffer>(command));
		}
''', r'''		{
			Common::DiagB32::Mark b32_q; // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock, RC5 of F20k)
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32_q.BeginH(Common::DiagB32::Call::QLock);
			}
			Common::LockGuard queue_lock(graphics.queue_mutex);
			b32_q.End(0, false);
			ImGui_ImplVulkan_RenderDrawData(ImGui::GetDrawData(),
			                                static_cast<VkCommandBuffer>(command));
		}
''')

S4 = 'src/graphics/presentation/videoOut.cpp'
edit(S4, r'''	// Track F, F20j (KYTY_DIAG_B32): the window boundary for the B32 sampler (n = FrameTrace: n= of this flip); the
	// reports the sampler has closed are printed here, outside m_mutex.
''', r'''	// Track F, F20j (KYTY_DIAG_B32): the window boundary for the B32 sampler (n = FrameTrace: n= of this flip); the
	// reports the sampler has closed are printed here, under FlipQueue::m_mutex and VideoOutConfig::mutex (F20j2, RC6 of
	// F20k: the print time goes into instr_us of the window open during the print).
''')


# =====================================================================================================================
# tests/DiagB32Tests.cpp
# =====================================================================================================================
T = 'tests/DiagB32Tests.cpp'
edit(T, r'''// lines (RC2). Target diag_b32_tests (not in ctest); prints one line per case and "ALL OK".
''', r'''// lines (RC2). Target diag_b32_tests (not in ctest); prints one line per case and "ALL OK".
// F20j2 (HPP-633; ROADMAP s122 item 552(v), (d)): plus the kernel query schedule (RC1), the nearest snapshot, the
// per-window zero invariants _w (RC3), the drain with a preempted writer (RC4), the async submitter's line (RC5).
''')
edit(T, r'''	// a record whose write is in progress (odd word for its index) -> torn
	WaitRec r;
	w->Push(r);
	const auto i = w->wpos.load() - 1;
	w->e[i % kWaitRing].seq.store(2 * i + 1);
	w->Drain(&out, &drop, &torn);
	CHECK(out.empty());
	CHECK(torn == 1);
	delete w;
}
''', r'''	// a record whose write is in progress (odd word for its index): F20j2 RC4 - the drain stops there and does not count
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
''')
edit(T, r'''	const auto h = HeaderLine(16, 1);
	CHECK(StartsWith(h, "DiagB32: mode=1 period_us=5000 print_us=100000 "));
	CHECK(h.find(" kstate=1") != std::string::npos);
''', r'''	const auto h = HeaderLine(16, 1, 10739);
	CHECK(StartsWith(h, "DiagB32: mode=1 period_us=5000 print_us=100000 "));
	CHECK(h.find(" kstate=1 kq_us=10739 kq_budget_div=10 kq_near_us=60000\n") != std::string::npos);
	// F20j2: the main line carries kq_n, kq_us, m5r_us
	CHECK(text.find(" kq=28 kq_n=0 kq_us=0 m5r_us=0 ") != std::string::npos);
''')
edit(T, r'''static void TestSig() {
''', r'''// ---------------------------------------------------------------------------------------------------------------------
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
''')
edit(T, r'''	TestMandatoryAndCuts();
	TestSig();
	std::printf("cases %d, failures %d\n", g_cases, g_fail);
''', r'''	TestMandatoryAndCuts();
	TestSig();
	TestSchedule();
	TestNearest();
	TestWindowDelta();
	TestDrainPreempted();
	TestASubmit();
	std::printf("cases %d, failures %d\n", g_cases, g_fail);
''')


def load(path):
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    return raw.replace(b'\r\n', b'\n').decode('utf-8'), crlf


def main():
    files = {}
    for path, old, new in EDITS:
        if path not in files:
            files[path] = load(ROOT + '/' + path)
    if CHECK:
        bad = 0
        for path, old, new in EDITS:
            text = files[path][0]
            ok = text.count(new) == 1 and (old in new or text.count(old) == 0)
            if not ok:
                bad += 1
                print('NOT APPLIED %s: %s' % (path, old.splitlines()[0][:80]))
        print('edits %d not applied %d' % (len(EDITS), bad))
        print('ALL OK' if bad == 0 else 'FAILED')
        sys.exit(0 if bad == 0 else 1)
    for path, old, new in EDITS:
        text, crlf = files[path]
        if not old.endswith('\n') or not new.endswith('\n'):
            print('STOP block without final newline in %s' % path)
            sys.exit(2)
        n = text.count(old)
        # whole-line anchor: the block must start at a line start
        starts = 0
        i = text.find(old)
        while i >= 0:
            if i == 0 or text[i - 1] == '\n':
                starts += 1
            i = text.find(old, i + 1)
        if n != 1 or starts != 1:
            print('STOP %s: block found %d times (%d at a line start): %s' % (path, n, starts, old.splitlines()[0][:80]))
            sys.exit(2)
        files[path] = (text.replace(old, new), crlf)
    for path, (text, crlf) in files.items():
        out = text.replace('\n', '\r\n') if crlf else text
        open(ROOT + '/' + path, 'wb').write(out.encode('utf-8'))
        print('patched %s (%s)' % (path, 'CRLF' if crlf else 'LF'))
    print('edits %d' % len(EDITS))
    print('ALL OK')


main()
