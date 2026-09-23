"""Session 108: knob cspfam (compute-prefetch skip per shader family) + always-live sync-compile guard counters.
ROADMAP "СЕССИЯ 108 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 1 (commit 3cc53a2).  Anchored, CRLF-safe.
    python C:/kyty/s106_stage/patch_s108.py [--dry]
"""
import sys

ROOT = 'C:/kyty/KytyPS5/src/'
DRY = '--dry' in sys.argv
NL = chr(10)


def patch(rel, edits):
    path = ROOT + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', NL)
    for old, new in edits:
        if text.count(old) != 1:
            raise SystemExit('%s: anchor found %d times: %r' % (rel, text.count(old), old[:90]))
        text = text.replace(old, new)
    if crlf:
        text = text.replace(NL, '\r\n')
    if not DRY:
        open(path, 'wb').write(text.encode('utf-8'))
    print('ok', rel)


patch('common/gates.h', [
    ('''	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchMemo,   // KYTY_CS_PREFETCH_MEMO,   file name "cspmemo" (0 off, 1 shadow, 2 skip, 3 skip + verify)
	Count,''', '''	CsPrefetchMemo,   // KYTY_CS_PREFETCH_MEMO,   file name "cspmemo" (0 off, 1 shadow, 2 skip, 3 skip + verify)
	// Session 108: skip PipelineCache::PrefetchComputePipeline per shader FAMILY (code hash and base plus
	// the stage static key, no user SGPRs) once the family's last K locked prefetches all found a built
	// pipeline and neither the programs epoch nor the shader registrations moved.  0 = off; K = the
	// streak.  A new permutation of a skipped family is then compiled on the dispatch - counted by
	// cs_sync_new, the guard of every run.  Read once per prefetch call.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchFamily, // KYTY_CS_PREFETCH_FAMILY, file name "cspfam" (0 off, K = streak before skipping)
	Count,'''),
])
patch('common/gates.cpp', [
    ('''    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CS_PREFETCH_MEMO", "cspmemo", 0, 3},
}};''', '''    {"KYTY_CS_PREFETCH_MEMO", "cspmemo", 0, 3},
    // Session 108: compute-prefetch skip per shader family after K "already built"; 0 = off (today).
    // Read once per prefetch call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_CS_PREFETCH_FAMILY", "cspfam", 0, 1024},
}};'''),
])
patch('common/frameStats.h', [
    ('''	CspPrefNew,              // cspf_new: ... that queued a new pipeline
	Count
};''', '''	CspPrefNew,              // cspf_new: ... that queued a new pipeline
	// Session 108, knob "cspfam": prefetch calls that looked the family up / returned before the lock.
	CspFamLook,              // cspfam_look
	CspFamSkip,              // cspfam_skip
	// Session 108, the guard of every run (no gate): GetComputePipeline found no pipeline and compiled it
	// synchronously on the dispatch (cs_sync_new), or found one the prefetch queued still compiling and
	// waited for it (cs_sync_wait).  Raw counts.
	CsSyncNew,               // cs_sync_new
	CsSyncWait,              // cs_sync_wait
	Count
};'''),
])
patch('graphics/presentation/videoOut.cpp', [
    ('''				    {"cspf_new", FS::Counter::CspPrefNew, false},
				};''', '''				    {"cspf_new", FS::Counter::CspPrefNew, false},
				    // Session 108: knob "cspfam" and the dispatch-time compile guard.  Raw counts.
				    {"cspfam_look", FS::Counter::CspFamLook, false},
				    {"cspfam_skip", FS::Counter::CspFamSkip, false},
				    {"cs_sync_new", FS::Counter::CsSyncNew, false},
				    {"cs_sync_wait", FS::Counter::CsSyncWait, false},
				};'''),
])
patch('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ('''CsPrefetchMemo& ThreadCsPrefetchMemo() {
	thread_local CsPrefetchMemo memo;
	return memo;
}
''', '''CsPrefetchMemo& ThreadCsPrefetchMemo() {
	thread_local CsPrefetchMemo memo;
	return memo;
}

// Session 108, knob "cspfam": per-thread streaks of "the locked prefetch found a built pipeline" per
// shader family; same stamps and capacity rule as CsPrefetchMemo.
struct CsPrefetchFamilies {
	static constexpr size_t Capacity = 4096;
	std::unordered_map<uint64_t, uint32_t> streak;
	uint64_t                               epoch = UINT64_MAX;
	uint64_t                               registrations = UINT64_MAX;
	std::vector<uint32_t>                  key_words;

	void Restamp(uint64_t now_epoch, uint64_t now_registrations) {
		if (now_epoch != epoch || now_registrations != registrations || streak.size() >= Capacity) {
			streak.clear();
			epoch         = now_epoch;
			registrations = now_registrations;
		}
	}
};

CsPrefetchFamilies& ThreadCsPrefetchFamilies() {
	thread_local CsPrefetchFamilies families;
	return families;
}
'''),
    ('''	const auto params             = PrepareProgram(regs, sh, input_info);
	// Session 107, knob "cspmemo": look the prefetch up before taking the lock.''',
     '''	const auto params             = PrepareProgram(regs, sh, input_info);
	// Session 108, knob "cspfam": skip the whole prefetch for a family whose last K locked prefetches all
	// found a built pipeline (stamps unchanged).
	const auto fam_k   = Common::Gates::Value(Common::Gates::Knob::CsPrefetchFamily);
	uint64_t   fam_key = 0;
	if (fam_k != 0) {
		auto& fam = ThreadCsPrefetchFamilies();
		fam.Restamp(g_programs_epoch_mirror.load(std::memory_order_acquire), ShaderRegistrations());
		fam.key_words.clear();
		BuildStageStaticKey(input_info, fam.key_words);
		fam_key = XXH3_64bits_withSeed(fam.key_words.data(), fam.key_words.size() * sizeof(uint32_t),
		                               params.hash ^ params.Base() ^ 0x63737066616d00ULL);
		Common::FrameStats::Add(Common::FrameStats::Counter::CspFamLook, 1);
		if (const auto it = fam.streak.find(fam_key); it != fam.streak.end() && it->second >= fam_k) {
			Common::FrameStats::Add(Common::FrameStats::Counter::CspFamSkip, 1);
			return;
		}
	}
	const auto fam_note = [&](bool have) {
		if (fam_k == 0) {
			return;
		}
		auto& streak = ThreadCsPrefetchFamilies().streak[fam_key];
		streak       = have ? streak + 1 : 0;
	};
	// Session 107, knob "cspmemo": look the prefetch up before taking the lock.'''),
    ('''	if (m_compute_pipelines.contains(program.id)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefHave, 1);
		memo_store(program.id);
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefNew, 1);''',
     '''	if (m_compute_pipelines.contains(program.id)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefHave, 1);
		memo_store(program.id);
		fam_note(true);
		return;
	}
	Common::FrameStats::Add(Common::FrameStats::Counter::CspPrefNew, 1);
	fam_note(false);'''),
    ('''			pending = iter->second.get(); // queued by the lookahead, still compiling
		} else {
			LibKernel::KernelTimeFreezeScope freeze_scope;
''', '''			pending = iter->second.get(); // queued by the lookahead, still compiling
			Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncWait, 1);
		} else {
			// Session 108: the guard of the "cspfam" knob - a compute pipeline compiled on the dispatch.
			Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncNew, 1);
			LibKernel::KernelTimeFreezeScope freeze_scope;
'''),
])
