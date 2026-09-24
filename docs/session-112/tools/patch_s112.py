"""Session 112 (ROADMAP 0.1, the executor's decision after session 111, items 1 and 3): knob "daguard", the
walker's GuardSlot yield, the ahead_threads size race, and the comments the session-111 audit named.

Knob "daguard" (KYTY_DRAW_AHEAD_GUARD, 0..1, default 1, LAST knob row).  0: at daslot = 0 the M1 queue - holding
PipelineCache::m_mutex (taken by QueueDrawAhead) and ahead_queue_mutex (taken by QueueAhead) - skips the slot
guards and reads hints directly.  Safe by construction: the only other guard takers are QueueAheadSource of another
QueueAhead call (serialised by ahead_queue_mutex) and AheadTake (only inside ProgramCache::Get, whose every caller
holds m_mutex); workers only CAS the state; every hint writer (AheadNote) holds m_mutex.  The decision is one read
of both knobs per QueueDrawAhead call, passed down, so a flip at any moment is safe.  Counters: da_q_noguard (calls
in that mode, the arming proof of the arm), da_guard_yield (walker guard waits that yielded to the OS).

    python C:/kyty/s106_stage/patch_s112.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv

EDITS = {}

EDITS['src/common/gates.h'] = [
    ("""	// Session 111: which lock PipelineCache::QueueDrawAhead (the M1 queue of the draw walker) takes: 0 = m_mutex
	// (today), 1 = only the new ahead_queue_mutex (the slots are guarded per slot either way), 2 = 1 plus a check of
	// the slot key under its guard at every take (da_slot_bad, DaSlotVerify: MISMATCH).  Read once per queue call
	// and once per take, so it CAN be a schedule arm; the per-slot protocol is unconditional, so a flip is safe.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	DrawAheadSlot,    // KYTY_DRAW_AHEAD_SLOT,    file name "daslot" (0 m_mutex, 1 own lock, 2 own lock + verify)
""",
     """	// Session 111: which lock PipelineCache::QueueDrawAhead (the M1 queue of the draw walker) takes: 0 = m_mutex
	// (the pre-session lock - but with the session-111 slot protocol inside the hold unless daguard = 0, so NOT the
	// session-110 code), 1 = only the new ahead_queue_mutex (the slots are guarded per slot), 2 = 1 plus a check of
	// the slot key under its guard at every take (da_slot_bad, DaSlotVerify: MISMATCH).  Read once per queue call
	// and once per take, so it CAN be a schedule arm; a flip is safe.
	DrawAheadSlot,    // KYTY_DRAW_AHEAD_SLOT,    file name "daslot" (0 m_mutex, 1 own lock, 2 own lock + verify)
	// Session 112: at daslot = 0 the M1 queue, which then holds m_mutex and ahead_queue_mutex, skips the slot guards
	// and reads the hints directly (0) - the session-110 walker hold, the arm the session-111 audit asked for; 1 =
	// the guards always (session 111).  No effect at daslot != 0.  Read once per queue call (with daslot), so it
	// CAN be a schedule arm; safe to flip at any moment (every other guard taker is serialised by one of the locks).
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	DrawAheadGuard,   // KYTY_DRAW_AHEAD_GUARD,   file name "daguard" (0 no guards at daslot 0, 1 guards)
"""),
]

EDITS['src/common/gates.cpp'] = [
    ("""    // Session 111: the M1 queue off PipelineCache::m_mutex (per-slot guards are unconditional); 0 = m_mutex.
    // Read once per queue call and once per take, so it CAN be a schedule arm. Session 111: default 1 after
    // the verify run (pred/02b_vds111b.md: GO, 60.8 M checks, 0 bad) and the sealed ship ABBA
    // (pred/03_shp111.md: d mean dt -230.7 us on frames 10-89, 2SE 81.8; video clean).
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_DRAW_AHEAD_SLOT", "daslot", 1, 2},
""",
     """    // Session 111: the M1 queue off PipelineCache::m_mutex; 0 = m_mutex (with the slot protocol inside the
    // hold unless daguard = 0). Read once per queue call and once per take, so it CAN be a schedule arm.
    // Session 111: default 1 after the verify run (pred/02b_vds111b.md: GO, 60.8 M checks, 0 bad) and the
    // sealed ship ABBA (pred/03_shp111.md: d mean dt -230.7 us on frames 10-89, 2SE 81.8; video clean) -
    // against daslot = 0 of the same build, not against session 110 (audit pred/04_audit111.md).
    {"KYTY_DRAW_AHEAD_SLOT", "daslot", 1, 2},
    // Session 112: at daslot = 0, 0 = the M1 queue skips the slot guards and reads hints directly (the
    // session-110 walker hold); 1 = guards always. Read once per queue call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_DRAW_AHEAD_GUARD", "daguard", 1, 1},
"""),
]

EDITS['src/common/frameStats.h'] = [
    ("""	DaCheckOk,               // da_chk_ok
	DaCheckBad,              // da_chk_bad
	Count
};
""",
     """	DaCheckOk,               // da_chk_ok
	DaCheckBad,              // da_chk_bad
	// Session 112, knob "daguard": QueueDrawAhead calls at daslot = 0 that skipped the slot guards (the arming
	// proof of the arm), and walker guard waits (GuardSlot) that spun out and yielded to the OS.  Raw counts.
	DaQueueNoGuard,          // da_q_noguard
	DaGuardYield,            // da_guard_yield
	Count
};
"""),
]

EDITS['src/graphics/presentation/videoOut.cpp'] = [
    ("""				    {"da_chk_bad", FS::Counter::DaCheckBad, false},
				};
""",
     """				    {"da_chk_bad", FS::Counter::DaCheckBad, false},
				    {"da_q_noguard", FS::Counter::DaQueueNoGuard, false},
				    {"da_guard_yield", FS::Counter::DaGuardYield, false},
				};
"""),
]

PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
EDITS[PC] = [
    # comments the audit named (MINOR-8)
    ("""		// ShaderTranslationCache::PlanFingerprint of the plan (| 1, 0 = not computed yet); only
		// the holder of PipelineCache::m_mutex computes and reads it.
		mutable uint64_t                   plan_fingerprint = 0;
		// Canonical class of the plan (ClassOf), same ownership as plan_fingerprint.
""",
     """		// ShaderTranslationCache::PlanFingerprint of the plan (| 1, 0 = not computed yet); computed only by the
		// holder of PipelineCache::m_mutex.  Session 111 ("daslot"): the M1 queue reads it WITHOUT m_mutex - safe only
		// because AheadNote computes it (and plan_class) before the hint that publishes the source, and neither is
		// ever reset.  A path that lets a source reach the queue before AheadNote would be a data race.
		mutable uint64_t                   plan_fingerprint = 0;
		// Canonical class of the plan (ClassOf), same ownership and publication as plan_fingerprint.
"""),
    ("""	// Ownership: the key fields are written only by the holder of PipelineCache::m_mutex while no
	// worker can touch the slot (state Empty, Ready or Failed). A worker claims a Queued slot with a
	// compare-exchange, writes only the result fields and publishes Ready or Failed; after that it
	// never touches the slot again, so the holder of m_mutex reads the result without a lock.
""",
     """	// Ownership (session 111): the key fields are written only by a producer (QueueAheadSource, serialised by
	// ahead_queue_mutex) under the slot guard while no worker can touch the slot (state Empty, Ready or Failed).
	// A worker claims a Queued slot with a compare-exchange, writes only the result fields and publishes Ready or
	// Failed; after that it never touches the slot again, so the draw (holder of m_mutex) reads the result after
	// moving the slot to Taking under the guard.  Session 112 (knob "daguard" 0 at daslot 0): the producer then
	// holds m_mutex too and skips the guards - the draw, the only other guard taker, cannot run.
"""),
    ("""		// Holder of m_mutex only (workers never read them): a draw took this result (da_unused counts
		// results that went without), and the stage it was queued for.
""",
     """		// Under the slot guard, or by the draw while the slot is Taking (workers never read them): a draw took
		// this result (da_unused counts results that went without), and the stage it was queued for.
"""),
    ("""		// key (holder of m_mutex); `source` is one entry with this plan, for the worker
""",
     """		// key (producer, under the slot guard); `source` is one entry with this plan, for the worker
"""),
    # GuardSlot yield (MINOR-6)
    ("""	static void GuardSlot(AheadSlot& slot) {
		while (slot.guard.load(std::memory_order_relaxed) != 0 || slot.guard.exchange(1, std::memory_order_acquire) != 0) {
			YieldProcessor();
		}
	}
""",
     """	// Session 112: the producer spins, and after 256 spins gives its quantum away (the guard holder - a draw - may
	// have been preempted inside its few-instruction window); da_guard_yield counts those.
	static void GuardSlot(AheadSlot& slot) {
		uint32_t spin = 0;
		while (slot.guard.load(std::memory_order_relaxed) != 0 || slot.guard.exchange(1, std::memory_order_acquire) != 0) {
			if (++spin < 256) {
				YieldProcessor();
			} else {
				spin = 0;
				Common::FrameStats::Add(Common::FrameStats::Counter::DaGuardYield, 1);
				SwitchToThread();
			}
		}
	}
"""),
    # ReadHintLocked
    ("""	// Slot guards: the draw gives up after a bounded spin (a miss); the producer waits.
""",
     """	// Session 112 ("daguard" 0 at daslot 0): the caller holds PipelineCache::m_mutex, which every hint writer
	// (AheadNote) holds, so the hint cannot change under it: a plain copy.
	void ReadHintLocked(size_t index, AheadHintView& view) const {
		const auto& hint = ahead_hints[index];
		for (size_t i = 0; i < view.sources.size(); i++) {
			view.sources[i] = hint.sources[i].load(std::memory_order_relaxed);
		}
		view.base       = hint.base.load(std::memory_order_relaxed);
		view.generation = hint.generation.load(std::memory_order_relaxed);
		view.count      = hint.count.load(std::memory_order_relaxed);
		view.stage      = hint.stage.load(std::memory_order_relaxed);
	}
	// Slot guards: the draw gives up after a bounded spin (a miss); the producer waits.
"""),
    # ahead_threads size race (MINOR-9)
    ("""	std::vector<std::thread>              ahead_threads;
""",
     """	std::vector<std::thread>              ahead_threads; // ahead_queue_mutex (AheadStartThreads) / shutdown
	// Session 112: ahead_threads.size() for the workers, which read it under ahead_mutex, not under the lock the
	// vector is resized under (a data race the session-111 audit found, MINOR-9).
	std::atomic<uint32_t>                 ahead_thread_count {0};
"""),
    ("""			ahead_threads.emplace_back([this, index] {
				SetThreadDescription(GetCurrentThread(), L"DrawAhead");
				AheadWorker(index);
			});
		}
""",
     """			ahead_threads.emplace_back([this, index] {
				SetThreadDescription(GetCurrentThread(), L"DrawAhead");
				AheadWorker(index);
			});
			ahead_thread_count.store(static_cast<uint32_t>(ahead_threads.size()), std::memory_order_relaxed);
		}
"""),
    ("""		ahead_threads.clear();
	}
""",
     """		ahead_threads.clear();
		ahead_thread_count.store(0, std::memory_order_relaxed);
	}
"""),
    ("""				wake_all =
				    ahead_threads.size() > Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
""",
     """				wake_all = ahead_thread_count.load(std::memory_order_relaxed) >
				           Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
"""),
    # QueueAheadSource: unguarded
    ("""	// Holder of m_mutex: queue one request for one source entry, or find it already queued.
	void QueueAheadSource(const SourceEntry* source, const PlanClass* plan_class,
						  const PipelineCache::DrawAheadRequest& request,
	                      AheadQueueStats& stats, std::vector<uint32_t>& batch) {
""",
     """	// Under ahead_queue_mutex: queue one request for one source entry, or find it already queued.  `unguarded`
	// (session 112, "daguard" 0 at daslot 0): the caller holds PipelineCache::m_mutex too, so no draw can take a
	// guard and the slot guards are skipped.
	void QueueAheadSource(const SourceEntry* source, const PlanClass* plan_class,
						  const PipelineCache::DrawAheadRequest& request,
	                      AheadQueueStats& stats, std::vector<uint32_t>& batch, bool unguarded) {
"""),
    ("""		// Session 111 ("daslot"): both probe slots guarded for the whole decision, lower index first.
		struct PairGuard {
			AheadSlot& low;
			AheadSlot& high;
			PairGuard(AheadSlot& a, AheadSlot& b): low(&a < &b ? a : b), high(&a < &b ? b : a) {
				GuardSlot(low);
				GuardSlot(high);
			}
			~PairGuard() {
				UnguardSlot(high);
				UnguardSlot(low);
			}
		} pair_guard(ahead_slots[hash & (AheadSlotCount - 1)], ahead_slots[(hash + 1) & (AheadSlotCount - 1)]);
""",
     """		// Session 111 ("daslot"): both probe slots guarded for the whole decision, lower index first (session 112:
		// not when `unguarded`).
		struct PairGuard {
			AheadSlot& low;
			AheadSlot& high;
			bool       on;
			PairGuard(AheadSlot& a, AheadSlot& b, bool guard)
			    : low(&a < &b ? a : b), high(&a < &b ? b : a), on(guard) {
				if (on) {
					GuardSlot(low);
					GuardSlot(high);
				}
			}
			~PairGuard() {
				if (on) {
					UnguardSlot(high);
					UnguardSlot(low);
				}
			}
		} pair_guard(ahead_slots[hash & (AheadSlotCount - 1)], ahead_slots[(hash + 1) & (AheadSlotCount - 1)],
		             !unguarded);
"""),
    ("""	// Session 111 ("daslot"): under ahead_queue_mutex (taken here), with or without PipelineCache::m_mutex.
	void QueueAhead(std::span<const PipelineCache::DrawAheadRequest> requests, uint64_t walk) {
""",
     """	// Session 111 ("daslot"): under ahead_queue_mutex (taken here), with or without PipelineCache::m_mutex.
	// Session 112: `unguarded` only when the caller holds m_mutex ("daguard" 0 at daslot 0).
	void QueueAhead(std::span<const PipelineCache::DrawAheadRequest> requests, uint64_t walk, bool unguarded) {
"""),
    ("""		AheadQueueStats                    stats;
		thread_local std::vector<uint32_t> batch;
""",
     """		AheadQueueStats                    stats;
		thread_local std::vector<uint32_t> batch;
		auto read_hint = [&](size_t index, AheadHintView& view) {
			if (unguarded) {
				ReadHintLocked(index, view);
				return true;
			}
			return ReadHint(index, view);
		};
"""),
    ("""			    !ReadHint(AheadHintIndex(ahead_stage, ahead.base, ahead.count), ahead_hint) ||
""",
     """			    !read_hint(AheadHintIndex(ahead_stage, ahead.base, ahead.count), ahead_hint) ||
"""),
    ("""			    !ReadHint(AheadHintIndex(stage, request.base, request.count), hint) || hint.sources[0] == nullptr ||
""",
     """			    !read_hint(AheadHintIndex(stage, request.base, request.count), hint) || hint.sources[0] == nullptr ||
"""),
    ("""					QueueAheadSource(class_sources[index], classes[index], request, stats, batch);
""",
     """					QueueAheadSource(class_sources[index], classes[index], request, stats, batch, unguarded);
"""),
    ("""					QueueAheadSource(predicted_source, nullptr, request, stats, batch);
""",
     """					QueueAheadSource(predicted_source, nullptr, request, stats, batch, unguarded);
"""),
    ("""					QueueAheadSource(source, nullptr, request, stats, batch);
""",
     """					QueueAheadSource(source, nullptr, request, stats, batch, unguarded);
"""),
    # QueueDrawAhead
    ("""	// Session 111, knob "daslot": 0 = under m_mutex (today); 1/2 = only ahead_queue_mutex (taken in QueueAhead) -
	// the slots are guarded one by one and the hints are read as consistent copies, so GuestGpu's draws do not
	// wait for the walker here.
	if (Common::Gates::Value(Common::Gates::Knob::DrawAheadSlot) == 0) {
		Common::LockGuard lock(m_mutex);
		PipeLockHolder    holder(m_lock_holder, 1, Common::FrameStats::Counter::PipeLockWalkQueueHoldNs,
		                         Common::FrameStats::Counter::PipeLockWalkQueueHoldN);
		m_program_cache->QueueAhead(requests, walk);
	} else {
		m_program_cache->QueueAhead(requests, walk);
		Common::FrameStats::Add(Common::FrameStats::Counter::DaQueueFree, 1);
	}
""",
     """	// Session 111, knob "daslot": 0 = under m_mutex; 1/2 = only ahead_queue_mutex (taken in QueueAhead) - the
	// slots are guarded one by one and the hints are read as consistent copies, so GuestGpu's draws do not wait
	// for the walker here.  Session 112, knob "daguard": at daslot 0, 0 = no slot guards and direct hint reads
	// inside the m_mutex hold (the session-110 hold); both knobs are read once here and the decision passed down.
	if (Common::Gates::Value(Common::Gates::Knob::DrawAheadSlot) == 0) {
		const bool        unguarded = Common::Gates::Value(Common::Gates::Knob::DrawAheadGuard) == 0;
		Common::LockGuard lock(m_mutex);
		PipeLockHolder    holder(m_lock_holder, 1, Common::FrameStats::Counter::PipeLockWalkQueueHoldNs,
		                         Common::FrameStats::Counter::PipeLockWalkQueueHoldN);
		m_program_cache->QueueAhead(requests, walk, unguarded);
		if (unguarded) {
			Common::FrameStats::Add(Common::FrameStats::Counter::DaQueueNoGuard, 1);
		}
	} else {
		m_program_cache->QueueAhead(requests, walk, false);
		Common::FrameStats::Add(Common::FrameStats::Counter::DaQueueFree, 1);
	}
"""),
]


def main():
    for rel, pairs in EDITS.items():
        path = ROOT / rel
        raw = path.read_bytes().decode('utf-8')
        crlf = '\r\n' in raw
        text = raw.replace('\r\n', '\n')
        for old, new in pairs:
            n = text.count(old)
            assert n == 1, (rel, n, old[:90])
            text = text.replace(old, new)
        if crlf:
            text = text.replace('\n', '\r\n')
        if not DRY:
            path.write_bytes(text.encode('utf-8'))
        print(('checked ' if DRY else 'patched ') + rel)


if __name__ == '__main__':
    main()
