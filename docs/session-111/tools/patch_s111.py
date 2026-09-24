"""Session 111: knob "daslot" - the M1 queue (QueueDrawAhead) off PipelineCache::m_mutex: per-slot guards, the Taking
state, publish-once hints (seqlock), atomic variants / memo_generation / slot-table pointer, ahead_queue_mutex.
ROADMAP §0.1 "СЕССИЯ 111" item 2 (1f488f7); design C:/kyty/s109/design109.md §A.  LF files, bytes-preserving."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/src')


def patch(rel, pairs):
    p = ROOT / rel
    s = p.read_bytes().decode('utf-8')
    assert '\r\n' not in s, rel
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:90])
        s = s.replace(a, b)
    p.write_bytes(s.encode('utf-8'))
    print('patched', rel)


patch('common/gates.h', [
    ("""	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchFree,   // KYTY_CS_PREFETCH_FREE,   file name "cspfree" (0 off, 1 skip on hit, 2 verify)
	Count,""", """	CsPrefetchFree,   // KYTY_CS_PREFETCH_FREE,   file name "cspfree" (0 off, 1 skip on hit, 2 verify)
	// Session 111: which lock PipelineCache::QueueDrawAhead (the M1 queue of the draw walker) takes: 0 = m_mutex
	// (today), 1 = only the new ahead_queue_mutex (the slots are guarded per slot either way), 2 = 1 plus a check of
	// the slot key under its guard at every take (da_slot_bad, DaSlotVerify: MISMATCH).  Read once per queue call
	// and once per take, so it CAN be a schedule arm; the per-slot protocol is unconditional, so a flip is safe.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	DrawAheadSlot,    // KYTY_DRAW_AHEAD_SLOT,    file name "daslot" (0 m_mutex, 1 own lock, 2 own lock + verify)
	Count,"""),
])
patch('common/gates.cpp', [
    ("""    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CS_PREFETCH_FREE", "cspfree", 1, 2},
}};""", """    {"KYTY_CS_PREFETCH_FREE", "cspfree", 1, 2},
    // Session 111: the M1 queue off PipelineCache::m_mutex (per-slot guards are unconditional); 0 = m_mutex
    // (today).  Read once per queue call and once per take, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_DRAW_AHEAD_SLOT", "daslot", 0, 2},
}};"""),
])
patch('common/frameStats.h', [
    ("""	CsSyncWaitUs,            // cs_sync_wait_us
	Count""", """	CsSyncWaitUs,            // cs_sync_wait_us
	// Session 111, knob "daslot": a take gave up on a busy slot guard (a miss), the walker met a slot being taken
	// (skipped), AheadNote deferred a source whose compiled SRT is not published yet, the walker's hint read raced
	// a write (treated as no hint), and the knob-2 check of a slot key failed.  Raw counts.
	DaGuardBusy,             // da_guard_busy
	DaQueueTaking,           // da_q_taking
	DaHintDefer,             // da_hint_defer
	DaHintTorn,              // da_hint_torn
	DaSlotBad,               // da_slot_bad
	Count"""),
])
patch('graphics/presentation/videoOut.cpp', [
    ("""				    {"cs_sync_wait_us", FS::Counter::CsSyncWaitUs, false},
""", """				    {"cs_sync_wait_us", FS::Counter::CsSyncWaitUs, false},
				    // Session 111: knob "daslot".  Raw counts.
				    {"da_guard_busy", FS::Counter::DaGuardBusy, false},
				    {"da_q_taking", FS::Counter::DaQueueTaking, false},
				    {"da_hint_defer", FS::Counter::DaHintDefer, false},
				    {"da_hint_torn", FS::Counter::DaHintTorn, false},
				    {"da_slot_bad", FS::Counter::DaSlotBad, false},
"""),
])

P = 'graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
patch(P, [
    # memo_generation atomic (the walker reads it without m_mutex under daslot)
    ("""	// Bumped when a source entry is dropped: the stored permutation pointers belong to one.
	uint64_t memo_generation = 1;""", """	// Bumped when a source entry is dropped: the stored permutation pointers belong to one.  Session 111
	// ("daslot"): atomic - the M1 queue reads it without PipelineCache::m_mutex.
	std::atomic<uint64_t> memo_generation {1};"""),
    # slot: guard byte, Taking state
    ("""	enum AheadState : uint8_t { AheadEmpty, AheadQueued, AheadRunning, AheadReady, AheadFailed };

	struct AheadSlot {
		std::atomic<uint8_t> state {AheadEmpty};""", """	// Session 111 (knob "daslot"): the key, walk, uses, taken, pixel and every state transition of the producer and
	// of the draw are read and written only under the slot's `guard` (a spin byte), so the M1 queue can run without
	// PipelineCache::m_mutex. AheadTaking: a draw took a Ready slot under the guard and verifies/copies its result
	// without it; nobody else touches such a slot until the draw publishes Ready or Empty. Workers still only CAS
	// Queued -> Running and publish Ready/Failed; they never take the guard.
	enum AheadState : uint8_t { AheadEmpty, AheadQueued, AheadRunning, AheadReady, AheadFailed, AheadTaking };

	struct AheadSlot {
		std::atomic<uint8_t> state {AheadEmpty};
		std::atomic<uint8_t> guard {0};"""),
    # hints and variants: atomic fields, seqlock
    ("""	struct AheadHint {
		std::array<const SourceEntry*, 4> sources {}; // static variants seen, replaced in turn
		uint64_t                          base       = 0;
		uint64_t                          generation = 0;
		uint32_t                          count      = 0;
		uint32_t                          next       = 0; // variant slot replaced next
		ShaderType                        stage      = ShaderType::Unknown;
	};""", """	// Session 111 ("daslot"): written only by AheadNote (holder of m_mutex) under a sequence counter, read by the M1
	// queue without m_mutex as a consistent copy (ReadHint). A source enters a hint only with its compiled SRT
	// published and its fingerprint and class computed, so the queue never writes to a source entry.
	struct AheadHint {
		std::atomic<uint32_t>                          seq {0};
		std::array<std::atomic<const SourceEntry*>, 4> sources {}; // static variants seen, replaced in turn
		std::atomic<uint64_t>                          base {0};
		std::atomic<uint64_t>                          generation {0};
		std::atomic<uint32_t>                          count {0};
		std::atomic<uint32_t>                          next {0}; // variant slot replaced next
		std::atomic<ShaderType>                        stage {ShaderType::Unknown};
	};
	struct AheadHintView {
		std::array<const SourceEntry*, 4> sources {};
		uint64_t                          base       = 0;
		uint64_t                          generation = 0;
		uint32_t                          count      = 0;
		ShaderType                        stage      = ShaderType::Unknown;
	};
	// The M1 queue's copy of a hint; false (no hint) when the write in progress did not settle.
	bool ReadHint(size_t index, AheadHintView& view) const {
		const auto& hint = ahead_hints[index];
		for (int attempt = 0; attempt < 4; attempt++) {
			const auto begin = hint.seq.load(std::memory_order_acquire);
			if ((begin & 1u) != 0) {
				YieldProcessor();
				continue;
			}
			for (size_t i = 0; i < view.sources.size(); i++) {
				view.sources[i] = hint.sources[i].load(std::memory_order_relaxed);
			}
			view.base       = hint.base.load(std::memory_order_relaxed);
			view.generation = hint.generation.load(std::memory_order_relaxed);
			view.count      = hint.count.load(std::memory_order_relaxed);
			view.stage      = hint.stage.load(std::memory_order_relaxed);
			std::atomic_thread_fence(std::memory_order_acquire);
			if (hint.seq.load(std::memory_order_relaxed) == begin) {
				return true;
			}
		}
		Common::FrameStats::Add(Common::FrameStats::Counter::DaHintTorn, 1);
		return false;
	}
	// Slot guards: the draw gives up after a bounded spin (a miss); the producer waits.
	static bool TryGuardSlot(AheadSlot& slot) {
		for (int spin = 0; spin < 64; spin++) {
			if (slot.guard.load(std::memory_order_relaxed) == 0 &&
			    slot.guard.exchange(1, std::memory_order_acquire) == 0) {
				return true;
			}
			YieldProcessor();
		}
		return false;
	}
	static void GuardSlot(AheadSlot& slot) {
		while (slot.guard.load(std::memory_order_relaxed) != 0 || slot.guard.exchange(1, std::memory_order_acquire) != 0) {
			YieldProcessor();
		}
	}
	static void UnguardSlot(AheadSlot& slot) {
		slot.guard.store(0, std::memory_order_release);
	}"""),
    ("""	std::unique_ptr<AheadSlot[]>          ahead_slots; // allocated by the first queued walk
	std::array<AheadHint, AheadHintCount> ahead_hints {};""", """	std::unique_ptr<AheadSlot[]>          ahead_slots; // allocated by the first queued walk (ahead_queue_mutex)
	std::atomic<AheadSlot*>               ahead_slots_ptr {nullptr}; // the same, published for the draw
	std::array<AheadHint, AheadHintCount> ahead_hints {};"""),
    ("""	struct AheadVariant {
		uint64_t           key    = 0;
		const SourceEntry* source = nullptr;
	};""", """	struct AheadVariant { // session 111 ("daslot"): atomic, read by the M1 queue without m_mutex
		std::atomic<uint64_t>           key {0};
		std::atomic<const SourceEntry*> source {nullptr};
	};"""),
    ("""	std::mutex                            ahead_mutex;
	std::condition_variable               ahead_cv;""", """	std::mutex                            ahead_mutex;
	std::condition_variable               ahead_cv;
	// Session 111 ("daslot"): serialises every QueueAhead call (the walker and GuestGpu's own walks) and the
	// allocation of the slot table; taken after PipelineCache::m_mutex when that is held too (daslot = 0).
	std::mutex                            ahead_queue_mutex;"""),
    # AheadNote: publish once, seqlock writes
    ("""	void AheadNote(ShaderType stage, uint64_t base, std::span<const uint32_t> user_data,
	               const SourceEntry* source) {
		const auto count = static_cast<uint32_t>(user_data.size());
		auto&      hint  = ahead_hints[AheadHintIndex(stage, base, count)];
		if (hint.sources[1] != nullptr && hint.base == base && hint.count == count &&
			!Common::Gates::Enabled(Common::Gates::Gate::DrawAheadClass) &&
		    hint.stage == stage && hint.generation == memo_generation) {
			const auto key = AheadVariantKey(stage, base, UserDataHash(user_data));
			ahead_variants[key % AheadVariantCount] = {key, source};
		}
		if (hint.base != base || hint.count != count || hint.stage != stage ||
		    hint.generation != memo_generation) {
			hint            = {};
			hint.sources[0] = source;
			hint.base       = base;
			hint.generation = memo_generation;
			hint.count      = count;
			hint.next       = 1;
			hint.stage      = stage;
			return;
		}
		if (std::find(hint.sources.begin(), hint.sources.end(), source) != hint.sources.end()) {
			return;
		}
		// Another static variant of the same program.
		Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadHintFlip, 1);
		hint.sources[hint.next % hint.sources.size()] = source;
		hint.next++;
	}""", """	void AheadNote(ShaderType stage, uint64_t base, std::span<const uint32_t> user_data,
	               const SourceEntry* source) {
		// Session 111 ("daslot"): publish once - the M1 queue reads hints without m_mutex, so a source enters one
		// only with its compiled SRT published and its fingerprint and class already computed (the next draw of
		// the program notes it; the queue would have skipped it as no_plan anyway).
		if (source->resource_plan.srt_compiled == nullptr) {
			Common::FrameStats::Add(Common::FrameStats::Counter::DaHintDefer, 1);
			return;
		}
		Fingerprint(*source);
		ClassOf(*source);
		const auto count      = static_cast<uint32_t>(user_data.size());
		const auto generation = memo_generation.load(std::memory_order_relaxed);
		auto&      hint       = ahead_hints[AheadHintIndex(stage, base, count)];
		// This thread is the only writer: relaxed reads of its own fields.
		const auto hint_base  = hint.base.load(std::memory_order_relaxed);
		const auto hint_count = hint.count.load(std::memory_order_relaxed);
		const auto hint_stage = hint.stage.load(std::memory_order_relaxed);
		const auto hint_gen   = hint.generation.load(std::memory_order_relaxed);
		const auto write      = [&hint](const auto& body) {
			const auto seq = hint.seq.load(std::memory_order_relaxed);
			hint.seq.store(seq + 1, std::memory_order_relaxed);
			std::atomic_thread_fence(std::memory_order_release);
			body();
			hint.seq.store(seq + 2, std::memory_order_release);
		};
		if (hint.sources[1].load(std::memory_order_relaxed) != nullptr && hint_base == base && hint_count == count &&
			!Common::Gates::Enabled(Common::Gates::Gate::DrawAheadClass) &&
		    hint_stage == stage && hint_gen == generation) {
			const auto key     = AheadVariantKey(stage, base, UserDataHash(user_data));
			auto&      variant = ahead_variants[key % AheadVariantCount];
			variant.source.store(source, std::memory_order_release);
			variant.key.store(key, std::memory_order_release);
		}
		if (hint_base != base || hint_count != count || hint_stage != stage || hint_gen != generation) {
			write([&] {
				hint.sources[0].store(source, std::memory_order_relaxed);
				for (size_t i = 1; i < hint.sources.size(); i++) {
					hint.sources[i].store(nullptr, std::memory_order_relaxed);
				}
				hint.base.store(base, std::memory_order_relaxed);
				hint.generation.store(generation, std::memory_order_relaxed);
				hint.count.store(count, std::memory_order_relaxed);
				hint.next.store(1, std::memory_order_relaxed);
				hint.stage.store(stage, std::memory_order_relaxed);
			});
			return;
		}
		for (const auto& held: hint.sources) {
			if (held.load(std::memory_order_relaxed) == source) {
				return;
			}
		}
		// Another static variant of the same program.
		Common::FrameStats::Add(Common::FrameStats::Counter::DrawAheadHintFlip, 1);
		const auto next = hint.next.load(std::memory_order_relaxed);
		write([&] {
			hint.sources[next % hint.sources.size()].store(source, std::memory_order_relaxed);
			hint.next.store(next + 1, std::memory_order_relaxed);
		});
	}"""),
    # QueueAheadSource: guards on both probes; Taking is busy
    ("""		const auto fingerprint = plan_class != nullptr ? plan_class->hash : Fingerprint(*source);
		const std::span<const uint32_t> user_data(request.user_data.data(), request.count);
		const auto hash        = AheadHash(fingerprint, request.base, request.user_hash);
		AheadSlot* victim      = nullptr;
		uint32_t   victim_rank = UINT32_MAX;
		for (size_t probe = 0; probe < 2; probe++) {
			stats.probes++;
			auto&      slot  = ahead_slots[(hash + probe) & (AheadSlotCount - 1)];
			const auto state = slot.state.load(std::memory_order_acquire);
			if (state != AheadEmpty && slot.Matches(fingerprint, plan_class, request.base, memo_generation, user_data)) {""",
     """		const auto fingerprint = plan_class != nullptr ? plan_class->hash : Fingerprint(*source);
		const std::span<const uint32_t> user_data(request.user_data.data(), request.count);
		const auto hash        = AheadHash(fingerprint, request.base, request.user_hash);
		const auto generation  = memo_generation.load(std::memory_order_relaxed);
		AheadSlot* victim      = nullptr;
		uint32_t   victim_rank = UINT32_MAX;
		// Session 111 ("daslot"): both probe slots guarded for the whole decision, lower index first.
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
		for (size_t probe = 0; probe < 2; probe++) {
			stats.probes++;
			auto&      slot  = ahead_slots[(hash + probe) & (AheadSlotCount - 1)];
			const auto state = slot.state.load(std::memory_order_acquire);
			if (state == AheadTaking) {
				// A draw is taking this slot's result right now: neither a match to update nor a victim.
				if (slot.Matches(fingerprint, plan_class, request.base, generation, user_data)) {
					Common::FrameStats::Add(Common::FrameStats::Counter::DaQueueTaking, 1);
					stats.busy++;
					return;
				}
				continue;
			}
			if (state != AheadEmpty && slot.Matches(fingerprint, plan_class, request.base, generation, user_data)) {"""),
    ("""		victim->generation  = memo_generation;
		victim->walk        = ahead_walk;""", """		victim->generation  = generation;
		victim->walk        = ahead_walk;"""),
    ("""	// Holder of m_mutex.
	void QueueAhead(std::span<const PipelineCache::DrawAheadRequest> requests, uint64_t walk) {
		namespace FS     = Common::FrameStats;
		const auto wanted = Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
		if (wanted == 0) {
			return;
		}""", """	// Session 111 ("daslot"): under ahead_queue_mutex (taken here), with or without PipelineCache::m_mutex.
	void QueueAhead(std::span<const PipelineCache::DrawAheadRequest> requests, uint64_t walk) {
		namespace FS     = Common::FrameStats;
		const auto wanted = Common::Gates::Value(Common::Gates::Knob::DrawAheadThreads);
		if (wanted == 0) {
			return;
		}
		std::lock_guard<std::mutex> queue_lock(ahead_queue_mutex);
		const auto                  generation = memo_generation.load(std::memory_order_relaxed);"""),
    ("""			ahead_slots = std::make_unique<AheadSlot[]>(AheadSlotCount);
			ahead_queue = std::make_unique<uint32_t[]>(AheadQueueSize);
		}""", """			ahead_slots = std::make_unique<AheadSlot[]>(AheadSlotCount);
			ahead_queue = std::make_unique<uint32_t[]>(AheadQueueSize);
			ahead_slots_ptr.store(ahead_slots.get(), std::memory_order_release);
		}"""),
    ("""		auto prefetch_request = [&](const PipelineCache::DrawAheadRequest& ahead) {
			const auto  ahead_stage = ahead.pixel ? ShaderType::Pixel : ShaderType::Vertex;
			const auto& ahead_hint  = ahead_hints[AheadHintIndex(ahead_stage, ahead.base, ahead.count)];
			if (ahead.count > HW::UserSgprInfo::SGPRS_MAX || ahead_hint.sources[0] == nullptr ||
			    ahead_hint.stage != ahead_stage || ahead_hint.base != ahead.base ||
			    ahead_hint.count != ahead.count || ahead_hint.generation != memo_generation) {
				return;
			}""", """		auto prefetch_request = [&](const PipelineCache::DrawAheadRequest& ahead) {
			const auto    ahead_stage = ahead.pixel ? ShaderType::Pixel : ShaderType::Vertex;
			AheadHintView ahead_hint;
			if (ahead.count > HW::UserSgprInfo::SGPRS_MAX ||
			    !ReadHint(AheadHintIndex(ahead_stage, ahead.base, ahead.count), ahead_hint) ||
			    ahead_hint.sources[0] == nullptr || ahead_hint.stage != ahead_stage || ahead_hint.base != ahead.base ||
			    ahead_hint.count != ahead.count || ahead_hint.generation != generation) {
				return;
			}"""),
    ("""			const auto  stage = request.pixel ? ShaderType::Pixel : ShaderType::Vertex;
			const auto& hint  = ahead_hints[AheadHintIndex(stage, request.base, request.count)];
			if (request.count > HW::UserSgprInfo::SGPRS_MAX || hint.sources[0] == nullptr ||
			    hint.stage != stage || hint.base != request.base || hint.count != request.count ||
			    hint.generation != memo_generation) {""", """			const auto    stage = request.pixel ? ShaderType::Pixel : ShaderType::Vertex;
			AheadHintView hint;
			if (request.count > HW::UserSgprInfo::SGPRS_MAX ||
			    !ReadHint(AheadHintIndex(stage, request.base, request.count), hint) || hint.sources[0] == nullptr ||
			    hint.stage != stage || hint.base != request.base || hint.count != request.count ||
			    hint.generation != generation) {"""),
    ("""				if (class_mode || counting) {
					const auto* plan_class = ClassOf(*source);""", """				if (class_mode || counting) {
					// Session 111 ("daslot"): computed by AheadNote before the source was published.
					const auto* plan_class = source->plan_class;"""),
    ("""				const auto& predicted = ahead_variants[key % AheadVariantCount];
				if (predicted.key == key &&
				    std::find(hint.sources.begin(), hint.sources.end(), predicted.source) !=
				        hint.sources.end()) {
					QueueAheadSource(predicted.source, nullptr, request, stats, batch);""", """				const auto& predicted        = ahead_variants[key % AheadVariantCount];
				const auto  predicted_key    = predicted.key.load(std::memory_order_acquire);
				const auto* predicted_source = predicted.source.load(std::memory_order_acquire);
				if (predicted_key == key && predicted_source != nullptr &&
				    std::find(hint.sources.begin(), hint.sources.end(), predicted_source) !=
				        hint.sources.end()) {
					QueueAheadSource(predicted_source, nullptr, request, stats, batch);"""),
    # AheadTake: published pointer, guards, Taking
    ("""		if (params.user_data.size() > HW::UserSgprInfo::SGPRS_MAX || ahead_slots == nullptr) {
			return false;
		}""", """		auto* const slots = ahead_slots_ptr.load(std::memory_order_acquire);
		if (params.user_data.size() > HW::UserSgprInfo::SGPRS_MAX || slots == nullptr) {
			return false;
		}
		const auto slot_mode = Common::Gates::Value(Common::Gates::Knob::DrawAheadSlot);"""),
    ("""		for (size_t probe = 0; probe < 2; probe++) {
			auto& slot = ahead_slots[(hash + probe) & (AheadSlotCount - 1)];
			if (!slot.Matches(fingerprint, plan_class, params.Base(), memo_generation, params.user_data)) {
				continue;
			}
			probes     = probe + 1;
			auto state = slot.state.load(std::memory_order_acquire);
			if (state == AheadQueued) {
				if (slot.uses > 1) {
					slot.uses--; // later draws of this walk still want it
				} else {
					// Nobody will need it after this draw: let the workers skip it.
					auto expected = static_cast<uint8_t>(AheadQueued);
					slot.state.compare_exchange_strong(expected, AheadEmpty, std::memory_order_acq_rel);
				}
				FS::Add(FS::Counter::DrawAheadLate, 1);
				return false;
			}
			if (state == AheadRunning) {
				slot.uses -= slot.uses != 0 ? 1u : 0u;
				FS::Add(FS::Counter::DrawAheadLate, 1);
				return false;
			}
			if (state != AheadReady) {
				break;
			}""", """		const auto generation = memo_generation.load(std::memory_order_relaxed);
		for (size_t probe = 0; probe < 2; probe++) {
			auto& slot = slots[(hash + probe) & (AheadSlotCount - 1)];
			// Session 111 ("daslot"): the key and the state transition under the slot's guard; a busy guard is a
			// miss rather than a wait.
			if (!TryGuardSlot(slot)) {
				FS::Add(FS::Counter::DaGuardBusy, 1);
				continue;
			}
			if (!slot.Matches(fingerprint, plan_class, params.Base(), generation, params.user_data)) {
				UnguardSlot(slot);
				continue;
			}
			probes     = probe + 1;
			auto state = slot.state.load(std::memory_order_acquire);
			if (state == AheadQueued) {
				if (slot.uses > 1) {
					slot.uses--; // later draws of this walk still want it
				} else {
					// Nobody will need it after this draw: let the workers skip it.
					auto expected = static_cast<uint8_t>(AheadQueued);
					slot.state.compare_exchange_strong(expected, AheadEmpty, std::memory_order_acq_rel);
				}
				UnguardSlot(slot);
				FS::Add(FS::Counter::DrawAheadLate, 1);
				return false;
			}
			if (state == AheadRunning) {
				slot.uses -= slot.uses != 0 ? 1u : 0u;
				UnguardSlot(slot);
				FS::Add(FS::Counter::DrawAheadLate, 1);
				return false;
			}
			if (state != AheadReady) {
				UnguardSlot(slot);
				break;
			}
			if (slot_mode == 2) {
				// Knob "daslot" = 2: the key the producer wrote must still describe the source it named.
				const bool key_ok = slot.source != nullptr &&
				                    (slot.plan_class != nullptr
				                         ? ClassOf(*slot.source) == slot.plan_class && slot.plan_class->hash == slot.fingerprint
				                         : Fingerprint(*slot.source) == slot.fingerprint);
				if (!key_ok) {
					FS::Add(FS::Counter::DaSlotBad, 1);
					static std::atomic<uint32_t> bad_log {0};
					if (bad_log.fetch_add(1, std::memory_order_relaxed) < 40) {
						LOGF("DaSlotVerify: MISMATCH slot=%" PRIu64 " fingerprint=0x%016" PRIx64 "\\n",
						     static_cast<uint64_t>(&slot - slots), slot.fingerprint);
					}
				}
			}
			slot.state.store(AheadTaking, std::memory_order_relaxed);
			UnguardSlot(slot);"""),
    ("""				Common::DrawStat::Mark(Common::DrawStat::M1);
				// Guest words moved since the worker read them: no later draw can use it either.
				slot.uses = 0;
				slot.state.store(AheadEmpty, std::memory_order_release);
				return false;""", """				Common::DrawStat::Mark(Common::DrawStat::M1);
				// Guest words moved since the worker read them: no later draw can use it either.
				slot.uses = 0;
				slot.state.store(AheadEmpty, std::memory_order_release); // publishes the Taking slot
				return false;"""),
    ("""			if (slot.uses > 1) {
				slot.uses--;
				CopyAheadResult(slot, resources, specialization, kept, false);
			} else {""", """			if (slot.uses > 1) {
				slot.uses--;
				CopyAheadResult(slot, resources, specialization, kept, false);
				slot.taken = 1;
				slot.state.store(AheadReady, std::memory_order_release); // publishes the Taking slot
			} else {"""),
    ("""				slot.uses = 0;
				slot.state.store(AheadEmpty, std::memory_order_release);
				FS::Add(FS::Counter::DrawAheadMoves, 1);
			}
			take_mark(Common::FrameStats::Counter::TakeLapTakeNs);
			slot.taken = 1;""", """				slot.uses  = 0;
				slot.taken = 1;
				slot.state.store(AheadEmpty, std::memory_order_release); // publishes the Taking slot
				FS::Add(FS::Counter::DrawAheadMoves, 1);
			}
			take_mark(Common::FrameStats::Counter::TakeLapTakeNs);"""),
    # QueueDrawAhead: the knob picks the lock
    ("""	const bool        timed       = Common::FrameStats::Enabled();
	const auto        queue_begin = timed ? Common::FrameStats::NowNs() : 0;
	Common::LockGuard lock(m_mutex);
	PipeLockHolder    holder(m_lock_holder, 1, Common::FrameStats::Counter::PipeLockWalkQueueHoldNs,
	                         Common::FrameStats::Counter::PipeLockWalkQueueHoldN);
	m_program_cache->QueueAhead(requests, walk);""", """	const bool        timed       = Common::FrameStats::Enabled();
	const auto        queue_begin = timed ? Common::FrameStats::NowNs() : 0;
	// Session 111, knob "daslot": 0 = under m_mutex (today); 1/2 = only ahead_queue_mutex (taken in QueueAhead) -
	// the slots are guarded one by one and the hints are read as consistent copies, so GuestGpu's draws do not
	// wait for the walker here.
	if (Common::Gates::Value(Common::Gates::Knob::DrawAheadSlot) == 0) {
		Common::LockGuard lock(m_mutex);
		PipeLockHolder    holder(m_lock_holder, 1, Common::FrameStats::Counter::PipeLockWalkQueueHoldNs,
		                         Common::FrameStats::Counter::PipeLockWalkQueueHoldN);
		m_program_cache->QueueAhead(requests, walk);
	} else {
		m_program_cache->QueueAhead(requests, walk);
	}"""),
])
