"""Session 110: stall duration on the dispatch - counters cs_sync_new_us / cs_sync_wait_us and a CsStall line per
stall (ROADMAP §0.1 "СЕССИЯ 110" item 1).  Measurement only.  LF files, bytes-preserving."""
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


patch('common/frameStats.h', [
    ("""	CspFreeMoved,            // cspfree_moved
	Count""", """	CspFreeMoved,            // cspfree_moved
	// Session 110: wall on the dispatching thread inside GetComputePipeline's synchronous compile (from the
	// "not found" branch, lock held, to the return) and inside the wait for a pending entry.  Raw us.
	CsSyncNewUs,             // cs_sync_new_us
	CsSyncWaitUs,            // cs_sync_wait_us
	Count"""),
])
patch('graphics/presentation/videoOut.cpp', [
    ("""				    {"cspfree_moved", FS::Counter::CspFreeMoved, false},
""", """				    {"cspfree_moved", FS::Counter::CspFreeMoved, false},
				    // Session 110: stall duration on the dispatch.  Raw us.
				    {"cs_sync_new_us", FS::Counter::CsSyncNewUs, false},
				    {"cs_sync_wait_us", FS::Counter::CsSyncWaitUs, false},
"""),
])
patch('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    ("""	ComputePipelineEntry* pending = nullptr;
	{
		Common::LockGuard lock(m_mutex);

		if (auto iter = m_compute_pipelines.find(compute_program.id);""",
     """	ComputePipelineEntry* pending = nullptr;
	// Session 110: one line per dispatch-time stall (always on, capped), the duration guard's input.
	const auto note_stall = [&](const char* kind, uint64_t us) {
		static std::atomic<uint32_t> stall_lines {0};
		if (stall_lines.fetch_add(1, std::memory_order_relaxed) < 4096) {
			LOGF("CsStall: kind=%s us=%" PRIu64 " id=%" PRIu64 " hash=0x%016" PRIx64 "\\n", kind, us,
			     compute_program.id, input_info.stage.program->shader_hash);
		}
	};
	{
		Common::LockGuard lock(m_mutex);

		if (auto iter = m_compute_pipelines.find(compute_program.id);"""),
    ("""			// Session 108: the guard of the "cspfam" knob - a compute pipeline compiled on the dispatch.
			Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncNew, 1);
			LibKernel::KernelTimeFreezeScope freeze_scope;
""", """			// Session 108: the guard of the "cspfam" knob - a compute pipeline compiled on the dispatch.
			Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncNew, 1);
			const auto                       stall_begin = HostMicros();
			LibKernel::KernelTimeFreezeScope freeze_scope;
"""),
    ("""			    m_compute_pipelines.emplace(compute_program.id, std::move(cached));
			EXIT_IF(!inserted);
			g_compute_creations.fetch_add(1, std::memory_order_release);
			return *place->second;""", """			    m_compute_pipelines.emplace(compute_program.id, std::move(cached));
			EXIT_IF(!inserted);
			g_compute_creations.fetch_add(1, std::memory_order_release);
			const auto stall_us = HostMicros() - stall_begin;
			Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncNewUs, stall_us);
			note_stall("new", stall_us);
			return *place->second;"""),
    ("""		m_ready_cv.wait(lock, [pending] { return pending->ready.load(std::memory_order_acquire); });
	}
	if (AvTraceEnabled()) {""", """		m_ready_cv.wait(lock, [pending] { return pending->ready.load(std::memory_order_acquire); });
	}
	{
		const auto stall_us = HostMicros() - wait_begin;
		Common::FrameStats::Add(Common::FrameStats::Counter::CsSyncWaitUs, stall_us);
		note_stall("wait", stall_us);
	}
	if (AvTraceEnabled()) {"""),
])
