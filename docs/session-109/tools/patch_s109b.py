"""Session 109: knob "cspfree" - the walker's compute prefetch without PipelineCache::m_mutex on a
(source entry, specialization) hit.  ROADMAP §0.1 "СЕССИЯ 109" items 4-5 (20e7b31); design C:/kyty/s109/design109.md."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/src')


def patch(rel, pairs):
    p = ROOT / rel
    s = p.read_bytes().decode('utf-8')
    assert '\r\n' not in s, rel
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80])
        s = s.replace(a, b)
    p.write_bytes(s.encode('utf-8'))
    print('patched', rel)


patch('common/gates.h', [
    ("""	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchFamily, // KYTY_CS_PREFETCH_FAMILY, file name "cspfam" (0 off, K = streak before skipping)
	Count,""", """	CsPrefetchFamily, // KYTY_CS_PREFETCH_FAMILY, file name "cspfam" (0 off, K = streak before skipping)
	// Session 109: PipelineCache::PrefetchComputePipeline without the lock when a per-thread memo knows the
	// (source entry, materialized specialization) - the exact permutation predicate of ProgramCache::Get -
	// and a pipeline for it; the materialization runs unlocked on a source whose compiled SRT was seen
	// published under the lock.  0 = off; 1 = skip on a hit; 2 = verify (the locked path still runs; ids
	// that differ at equal specializations are counted bad).  Read once per prefetch call.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchFree,   // KYTY_CS_PREFETCH_FREE,   file name "cspfree" (0 off, 1 skip on hit, 2 verify)
	Count,"""),
])
patch('common/gates.cpp', [
    ("""    // off failed its rule (cs_sync_new 6 vs 3 + 2): rolled back to 0 (ROADMAP 0.1, session 108 item 8).
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CS_PREFETCH_FAMILY", "cspfam", 0, 1024},
}};""", """    // off failed its rule (cs_sync_new 6 vs 3 + 2): rolled back to 0 (ROADMAP 0.1, session 108 item 8).
    {"KYTY_CS_PREFETCH_FAMILY", "cspfam", 0, 1024},
    // Session 109: the compute prefetch without the lock on a (source, specialization) hit; 0 = off
    // (today).  Read once per prefetch call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CS_PREFETCH_FREE", "cspfree", 0, 2},
}};"""),
])
patch('common/frameStats.h', [
    ("""	CspFamClear,             // cspfam_clr
	Count""", """	CspFamClear,             // cspfam_clr
	// Session 109, knob "cspfree": prefetch calls that built the key (knob != 0), that found the source,
	// that found the specialization (a skip at knob 1), source unknown, specialization unknown, unlocked
	// materialization failed, memo cleared (stamp moved or full), entries stored, knob 2 disagreements at
	// equal specializations (bad) and at different ones (memory moved between the two reads).  Raw counts.
	CspFreeLook,             // cspfree_look
	CspFreeHit,              // cspfree_hit
	CspFreeSrcMiss,          // cspfree_src_miss
	CspFreeSpecMiss,         // cspfree_spec_miss
	CspFreeMatFail,          // cspfree_mat_fail
	CspFreeClear,            // cspfree_clr
	CspFreeStore,            // cspfree_store
	CspFreeBad,              // cspfree_bad
	CspFreeMoved,            // cspfree_moved
	Count"""),
])
patch('graphics/presentation/videoOut.cpp', [
    ("""				    {"cspfam_clr", FS::Counter::CspFamClear, false},
""", """				    {"cspfam_clr", FS::Counter::CspFamClear, false},
				    // Session 109: knob "cspfree".  Raw counts.
				    {"cspfree_look", FS::Counter::CspFreeLook, false},
				    {"cspfree_hit", FS::Counter::CspFreeHit, false},
				    {"cspfree_src_miss", FS::Counter::CspFreeSrcMiss, false},
				    {"cspfree_spec_miss", FS::Counter::CspFreeSpecMiss, false},
				    {"cspfree_mat_fail", FS::Counter::CspFreeMatFail, false},
				    {"cspfree_clr", FS::Counter::CspFreeClear, false},
				    {"cspfree_store", FS::Counter::CspFreeStore, false},
				    {"cspfree_bad", FS::Counter::CspFreeBad, false},
				    {"cspfree_moved", FS::Counter::CspFreeMoved, false},
"""),
])
patch('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    # ProgramCache: the memo type and the two helpers, right after PermutationRef/by_id
    ("""	std::unordered_map<uint64_t, PermutationRef> by_id;
""", """	std::unordered_map<uint64_t, PermutationRef> by_id;

	// Session 109, knob "cspfree": the per-thread memo of the compute prefetch.  A source enters it only
	// from FreeSourceFor (under PipelineCache::m_mutex, compiled SRT published); source entries are never
	// freed and their permutations only appended, so (source, specialization) -> id stays what Get's
	// find_if returns for push-data cursor 0 until a stamp moves (a dropped entry moves programs_epoch).
	struct PrefetchFree {
		struct Known {
			ShaderRecompiler::IR::ResourceSpecialization specialization;
			uint64_t                                     id = 0;
		};
		struct Source {
			const SourceEntry* source = nullptr;
			std::vector<Known> known;
		};
		static constexpr size_t                          Capacity = 8192;
		std::unordered_map<ProgramKey, Source, ProgramKeyHash> sources;
		size_t                                           known_count   = 0;
		uint64_t                                         epoch         = UINT64_MAX;
		uint64_t                                         registrations = UINT64_MAX;
		ProgramKey                                       key; // this call's key (scratch)

		// true when the memo was cleared
		bool Restamp(uint64_t now_epoch, uint64_t now_registrations) {
			if (now_epoch != epoch || now_registrations != registrations || known_count >= Capacity ||
			    sources.size() >= Capacity) {
				sources.clear();
				known_count   = 0;
				epoch         = now_epoch;
				registrations = now_registrations;
				return true;
			}
			return false;
		}
	};
	static PrefetchFree& ThreadPrefetchFree() {
		thread_local PrefetchFree memo;
		return memo;
	}

	// Holder of PipelineCache::m_mutex: the source entry of a compute key and the specialization of its
	// permutation `id`; nullptr when absent or its compiled SRT is not published yet.
	const SourceEntry* FreeSourceFor(const ProgramKey& key, uint64_t id,
	                                 ShaderRecompiler::IR::ResourceSpecialization& specialization) const {
		const auto entry = programs.find(key);
		if (entry == programs.end() || entry->second.resource_plan.srt_compiled == nullptr) {
			return nullptr;
		}
		for (const auto& permutation: entry->second.permutations) {
			if (permutation.handle.id == id) {
				specialization = permutation.specialization;
				return &entry->second;
			}
		}
		return nullptr;
	}

	// Any thread, NO lock: the materialization Get runs for this source (same runtime), on a source that
	// FreeSourceFor returned (its plan is immutable apart from the once-published compiled SRT).
	static bool MaterializeUnlocked(const SourceEntry& source, const ShaderParams& params,
	                                ShaderRecompiler::IR::ResourceSnapshot&       resources,
	                                ShaderRecompiler::IR::ResourceSpecialization& specialization) {
		ShaderReadCache                        read_cache;
		const ShaderRecompiler::IR::SrtRuntime runtime {
		    .user_data                  = params.user_data,
		    .shader_base                = params.Base(),
		    .read_memory                = ReadShaderLiveMemory,
		    .userdata                   = &read_cache,
		    .read_specialization_memory = ReadShaderGuestMemory,
		};
		return ShaderRecompiler::IR::MaterializeResources(source.resource_plan, runtime, resources,
		                                                  specialization);
	}
"""),
    # PrefetchComputePipeline: the unlocked lookup before the lock ...
    ("""	Common::LockGuard lock(m_mutex);
	PipeLockHolder    holder(m_lock_holder, 2, Common::FrameStats::Counter::PipeLockWalkPrefHoldNs,
	                         Common::FrameStats::Counter::PipeLockWalkPrefHoldN);
	uint32_t          push_data_cursor = 0;
	const auto        program = m_program_cache->Get(params, input_info, push_data_cursor, true);""",
     """	// Session 109, knob "cspfree": the unlocked lookup of (source entry, specialization).
	const auto free_mode = Common::Gates::Value(Common::Gates::Knob::CsPrefetchFree);
	bool       free_hit  = false;
	uint64_t   free_id   = 0;
	ShaderRecompiler::IR::ResourceSpecialization free_specialization;
	if (free_mode != 0) {
		auto& memo = ProgramCache::ThreadPrefetchFree();
		if (memo.Restamp(g_programs_epoch_mirror.load(std::memory_order_acquire), ShaderRegistrations())) {
			Common::FrameStats::Add(Common::FrameStats::Counter::CspFreeClear, 1);
		}
		memo.key.stage           = ShaderType::Compute;
		memo.key.hash            = params.hash;
		memo.key.user_data_count = static_cast<uint32_t>(params.user_data.size());
		memo.key.code_size       = static_cast<uint32_t>(params.code.size());
		memo.key.static_state.clear();
		BuildStageStaticKey(input_info, memo.key.static_state);
		Common::FrameStats::Add(Common::FrameStats::Counter::CspFreeLook, 1);
		if (const auto it = memo.sources.find(memo.key); it != memo.sources.end()) {
			ShaderRecompiler::IR::ResourceSnapshot resources;
			if (ProgramCache::MaterializeUnlocked(*it->second.source, params, resources, free_specialization)) {
				for (const auto& known: it->second.known) {
					if (known.specialization == free_specialization) {
						free_hit = true;
						free_id  = known.id;
						break;
					}
				}
				Common::FrameStats::Add(free_hit ? Common::FrameStats::Counter::CspFreeHit
				                                 : Common::FrameStats::Counter::CspFreeSpecMiss,
				                        1);
				if (free_hit && free_mode == 1) {
					return;
				}
			} else {
				Common::FrameStats::Add(Common::FrameStats::Counter::CspFreeMatFail, 1);
			}
		} else {
			Common::FrameStats::Add(Common::FrameStats::Counter::CspFreeSrcMiss, 1);
		}
	}
	Common::LockGuard lock(m_mutex);
	PipeLockHolder    holder(m_lock_holder, 2, Common::FrameStats::Counter::PipeLockWalkPrefHoldNs,
	                         Common::FrameStats::Counter::PipeLockWalkPrefHoldN);
	uint32_t          push_data_cursor = 0;
	const auto        program = m_program_cache->Get(params, input_info, push_data_cursor, true);
	// Session 109, knob "cspfree": under the lock, record (source, specialization) -> id once the id has a
	// pipeline; at knob 2 compare with the unlocked hit first.
	const auto free_store = [&](uint64_t id) {
		if (free_mode == 0) {
			return;
		}
		auto&                                        memo = ProgramCache::ThreadPrefetchFree();
		ShaderRecompiler::IR::ResourceSpecialization locked_specialization;
		const auto* source = m_program_cache->FreeSourceFor(memo.key, id, locked_specialization);
		if (free_mode == 2 && free_hit && free_id != id) {
			const bool same = source != nullptr && locked_specialization == free_specialization;
			Common::FrameStats::Add(same ? Common::FrameStats::Counter::CspFreeBad
			                             : Common::FrameStats::Counter::CspFreeMoved,
			                        1);
			static std::atomic<uint32_t> bad_log {0};
			if (same && bad_log.fetch_add(1, std::memory_order_relaxed) < 40) {
				LOGF("CspFreeVerify: MISMATCH hash=0x%016" PRIx64 " memo_id=%" PRIu64 " id=%" PRIu64 "\\n",
				     params.hash, free_id, id);
			}
		}
		if (source == nullptr) {
			return;
		}
		auto& entry = memo.sources[memo.key];
		if (entry.source != source) {
			memo.known_count -= std::min(memo.known_count, entry.known.size());
			entry.known.clear();
			entry.source = source;
		}
		for (const auto& known: entry.known) {
			if (known.id == id) {
				return;
			}
		}
		entry.known.push_back({std::move(locked_specialization), id});
		memo.known_count++;
		Common::FrameStats::Add(Common::FrameStats::Counter::CspFreeStore, 1);
	};"""),
    # ... and the two store points on the locked path
    ("""	if (m_compute_pipelines.contains(program.id)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefHave, 1);
		memo_store(program.id);
		fam_note(true);
		return;
	}""", """	if (m_compute_pipelines.contains(program.id)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefHave, 1);
		memo_store(program.id);
		fam_note(true);
		free_store(program.id);
		return;
	}"""),
    ("""	g_compute_creations.fetch_add(1, std::memory_order_release);
	memo_store(program.id);
	m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);""", """	g_compute_creations.fetch_add(1, std::memory_order_release);
	memo_store(program.id);
	free_store(program.id);
	m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);"""),
])
