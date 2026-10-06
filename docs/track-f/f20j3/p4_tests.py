# F20j3 (HPP-646): part 4 of patch_f20j3.py - unit tests (tests/DiagB32Tests.cpp, target diag_b32_tests).
T = 'tests/DiagB32Tests.cpp'

edit(T, '''// F20j2 (HPP-633; ROADMAP s122 item 552(v), (d)): plus the kernel query schedule (RC1), the nearest snapshot, the
// per-window zero invariants _w (RC3), the drain with a preempted writer (RC4), the async submitter's line (RC5).

#include "common/diagB32.h"

#include <cstdio>
''', '''// F20j2 (HPP-633; ROADMAP s122 item 552(v), (d)): plus the kernel query schedule (RC1), the nearest snapshot, the
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
''')

edit(T, '''#include <string>
#include <vector>

using namespace Common::DiagB32;
''', '''#include <mutex>
#include <string>
#include <thread>
#include <vector>

using namespace Common::DiagB32;
''')

edit(T, '''		CHECK(text.find(" gap3p=2 ") != std::string::npos);
		CHECK(text.find(" gap3p=2\\n") != std::string::npos);
''', '''		CHECK(text.find(" gap3p=2 ") != std::string::npos);
		// F20j3 (Z1): the -x line now ends with ring_hold / ring_hold_w after gap3p
		CHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0\\n") != std::string::npos);
''')

edit(T, '''int main() {
	TestPartition();
''', '''// ---------------------------------------------------------------------------------------------------------------------
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
	CHECK(text.find(" gap3p=0 ring_hold=8 ring_hold_w=3\\n") != std::string::npos); // at the end of the -x line
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
	std::printf("  m5 model: async sgap_max_us=%llu samples=%u runs=%llu work_us=%llu; inline sgap_max_us=%llu samples=%u\\n",
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
		std::printf("  loop per_call=%d: samples=%u W=%u wakeups=%u records=%zu\\n", per_call, n, w, wakeups.load(), recs.size());
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
	std::printf("  emu_mutex: records=%zu\\n", recs.size());
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
''')

edit(T, '''	TestDrainPreempted();
	TestASubmit();
	std::printf("cases %d, failures %d\\n", g_cases, g_fail);
''', '''	TestDrainPreempted();
	TestASubmit();
	TestKinds();
	TestRingHold();
	TestPeerFields();
	TestM5Async();
	TestWaitLoopRuntime(); // runtime cases last: g_on stays on
	TestEmuMutexRuntime();
	std::printf("cases %d, failures %d\\n", g_cases, g_fail);
''')
