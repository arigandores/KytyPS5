"""Session 109: cspfam v2 - a process-wide count of compute-pipeline creations joins the family table's stamps.
ROADMAP §0.1 "СЕССИЯ 109" item 1 (bd52f86).  Files are LF; patched as bytes-preserving text."""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5/src')


def patch(rel, pairs):
    p = ROOT / rel
    s = p.read_bytes().decode('utf-8')
    assert '\r\n' not in s, rel
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:70])
        s = s.replace(a, b)
    p.write_bytes(s.encode('utf-8'))
    print('patched', rel)


patch('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ("""std::atomic<uint64_t> g_programs_epoch_mirror {0};
""", """std::atomic<uint64_t> g_programs_epoch_mirror {0};

// Session 109, knob "cspfam" v2: bumped wherever m_compute_pipelines gains an entry (the walker's
// prefetch, GetComputePipeline's synchronous path, the startup precache); a stamp of the family table,
// so any creation clears every streak and the skip re-arms only after K rounds with no creation.
std::atomic<uint64_t> g_compute_creations {0};
"""),
    ("""	uint64_t                               epoch = UINT64_MAX;
	uint64_t                               registrations = UINT64_MAX;
	std::vector<uint32_t>                  key_words;

	void Restamp(uint64_t now_epoch, uint64_t now_registrations) {
		if (now_epoch != epoch || now_registrations != registrations || streak.size() >= Capacity) {
			streak.clear();
			epoch         = now_epoch;
			registrations = now_registrations;
		}
	}
};""", """	uint64_t                               epoch = UINT64_MAX;
	uint64_t                               registrations = UINT64_MAX;
	uint64_t                               creations = UINT64_MAX; // session 109, v2
	std::vector<uint32_t>                  key_words;

	// true when the table was cleared
	bool Restamp(uint64_t now_epoch, uint64_t now_registrations, uint64_t now_creations) {
		if (now_epoch != epoch || now_registrations != registrations || now_creations != creations ||
		    streak.size() >= Capacity) {
			streak.clear();
			epoch         = now_epoch;
			registrations = now_registrations;
			creations     = now_creations;
			return true;
		}
		return false;
	}
};"""),
    ("""		fam.Restamp(g_programs_epoch_mirror.load(std::memory_order_acquire), ShaderRegistrations());
""", """		if (fam.Restamp(g_programs_epoch_mirror.load(std::memory_order_acquire), ShaderRegistrations(),
		                g_compute_creations.load(std::memory_order_acquire))) {
			Common::FrameStats::Add(Common::FrameStats::Counter::CspFamClear, 1);
		}
"""),
    ("""	m_compute_pipelines.emplace(program.id, std::move(entry));
	memo_store(program.id);
""", """	m_compute_pipelines.emplace(program.id, std::move(entry));
	g_compute_creations.fetch_add(1, std::memory_order_release);
	memo_store(program.id);
"""),
    ("""			    m_compute_pipelines.emplace(compute_program.id, std::move(cached));
			EXIT_IF(!inserted);
""", """			    m_compute_pipelines.emplace(compute_program.id, std::move(cached));
			EXIT_IF(!inserted);
			g_compute_creations.fetch_add(1, std::memory_order_release);
"""),
    ("""				m_compute_pipelines.emplace(program.id, std::move(entry));
				m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);
			}""", """				m_compute_pipelines.emplace(program.id, std::move(entry));
				g_compute_creations.fetch_add(1, std::memory_order_release);
				m_pending_pipelines.fetch_add(1, std::memory_order_relaxed);
			}"""),
])
patch('common/frameStats.h', [
    ("""	CsSyncNew,               // cs_sync_new
	CsSyncWait,              // cs_sync_wait
	Count""", """	CsSyncNew,               // cs_sync_new
	CsSyncWait,              // cs_sync_wait
	// Session 109, knob "cspfam" v2: family-table clears on the prefetching thread (a stamp moved:
	// programs epoch, shader registrations, a compute-pipeline creation anywhere, or capacity).
	CspFamClear,             // cspfam_clr
	Count"""),
])
patch('graphics/presentation/videoOut.cpp', [
    ("""				    {"cs_sync_wait", FS::Counter::CsSyncWait, false},
""", """				    {"cs_sync_wait", FS::Counter::CsSyncWait, false},
				    // Session 109: knob "cspfam" v2, family-table clears.  Raw count.
				    {"cspfam_clr", FS::Counter::CspFamClear, false},
"""),
])
patch('common/gates.h', [
    ("""	// Session 108: skip PipelineCache::PrefetchComputePipeline per shader FAMILY (code hash and base plus
	// the stage static key, no user SGPRs) once the family's last K locked prefetches all found a built
	// pipeline and neither the programs epoch nor the shader registrations moved.""",
     """	// Session 108: skip PipelineCache::PrefetchComputePipeline per shader FAMILY (code hash and base plus
	// the stage static key, no user SGPRs) once the family's last K locked prefetches all found a built
	// pipeline and neither the programs epoch nor the shader registrations moved.  Session 109 (v2): nor
	// the count of compute-pipeline creations anywhere (any creation clears every streak)."""),
])
