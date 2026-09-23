"""Session 106: KYTY_GPU_WALL=1 (measurement only) - wall time of the GuestGpu thread by region.
ROADMAP.md, "СЕССИЯ 106 — ЗАПИСИ ДО ДЕЙСТВИЙ", item 2 (commit 276437f).  Idempotent anchors, CRLF-safe.
    python C:/kyty/s105/patch_gwall106.py [--dry]
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
            raise SystemExit('%s: anchor found %d times: %r' % (rel, text.count(old), old[:80]))
        text = text.replace(old, new)
    if crlf:
        text = text.replace(NL, '\r\n')
    if not DRY:
        open(path, 'wb').write(text.encode('utf-8'))
    print('ok', rel, 'crlf' if crlf else 'lf')


patch('common/frameStats.h', [
    ('''	CtxRecordBlock,          // ctx_rec_block
	Count
};''', '''	CtxRecordBlock,          // ctx_rec_block
	// Session 106, KYTY_GPU_WALL=1 (measurement only, read once per process): the wall of the
	// GuestGpu thread by region - waiting for work in ThreadRun (gw_idle), all queues blocked
	// (gw_blk), one GuestGpu::Process call (gw_proc), one queued command (gw_cmd), and inside
	// Process the R_WAIT_FLIP_DONE wait in FlipQueue::Wait (gw_flip).  Raw ns / counts, live in
	// KYTY_FRAME_TRACE=lite; all read 0 without the variable.  dt - cpu_net splits into
	// idle + blk (outside Process) + flip + lock waits + the rest (other waits, preemption).
	GpuWallIdleNs,           // gw_idle_ns
	GpuWallIdleN,            // gw_idle_n
	GpuWallBlockedNs,        // gw_blk_ns
	GpuWallBlockedN,         // gw_blk_n
	GpuWallFlipNs,           // gw_flip_ns
	GpuWallFlipN,            // gw_flip_n
	GpuWallProcNs,           // gw_proc_ns
	GpuWallProcN,            // gw_proc_n
	GpuWallCmdNs,            // gw_cmd_ns
	GpuWallCmdN,             // gw_cmd_n
	Count
};'''),
    ('''// Session 96, gate "pathlap": HoldLap's shape with its OWN thread-local cursor, so a chain''',
     '''// Session 106, KYTY_GPU_WALL=1 (measurement only): read once per process; logs "GpuWall: mode 1"
// the first time it is asked and finds the variable on.
[[nodiscard]] bool GpuWallOn();

// Session 106: the wall of one GuestGpu-thread region (counters GpuWall*), timestamped under
// Enabled() so it reads in KYTY_FRAME_TRACE=lite.  `on` is the caller's extra condition (the
// thread role for the flip wait).  Off, it costs the static read in GpuWallOn().
class WallSpan {
public:
	WallSpan(bool on, Counter ns, Counter n): m_ns(ns), m_t0(on && GpuWallOn() && Enabled() ? NowNs() : 0) {
		if (m_t0 != 0) {
			Add(n, 1);
		}
	}
	~WallSpan() {
		if (m_t0 != 0) {
			Add(m_ns, NowNs() - m_t0);
		}
	}
	WallSpan(const WallSpan&)            = delete;
	WallSpan& operator=(const WallSpan&) = delete;

private:
	Counter  m_ns;
	uint64_t m_t0;
};

// Session 96, gate "pathlap": HoldLap's shape with its OWN thread-local cursor, so a chain'''),
])

patch('common/frameStats.cpp', [
    ('''uint64_t ThreadCpuNs(ThreadRole role) {''', '''bool GpuWallOn() {
	static const bool on = [] {
		const bool value = Common::EnvFlagOn("KYTY_GPU_WALL");
		if (value) {
			LOGF("GpuWall: mode 1" "\\n");
		}
		return value;
	}();
	return on;
}

uint64_t ThreadCpuNs(ThreadRole role) {'''),
])

patch('graphics/presentation/videoOut.cpp', [
    ('''				    {"ctx_rec_block", FS::Counter::CtxRecordBlock, false},
				};''', '''				    {"ctx_rec_block", FS::Counter::CtxRecordBlock, false},
				    // Session 106, KYTY_GPU_WALL=1: the GuestGpu thread's wall by region.  Raw ns/counts.
				    {"gw_idle_ns", FS::Counter::GpuWallIdleNs, false},
				    {"gw_idle_n", FS::Counter::GpuWallIdleN, false},
				    {"gw_blk_ns", FS::Counter::GpuWallBlockedNs, false},
				    {"gw_blk_n", FS::Counter::GpuWallBlockedN, false},
				    {"gw_flip_ns", FS::Counter::GpuWallFlipNs, false},
				    {"gw_flip_n", FS::Counter::GpuWallFlipN, false},
				    {"gw_proc_ns", FS::Counter::GpuWallProcNs, false},
				    {"gw_proc_n", FS::Counter::GpuWallProcN, false},
				    {"gw_cmd_ns", FS::Counter::GpuWallCmdNs, false},
				    {"gw_cmd_n", FS::Counter::GpuWallCmdN, false},
				};'''),
    ('''	EXIT_NOT_IMPLEMENTED(!IsValidBufferIndex(index));
	m_impl->GetFlipQueue().Wait(*ctx, index);
}''', '''	EXIT_NOT_IMPLEMENTED(!IsValidBufferIndex(index));
	// Session 106, KYTY_GPU_WALL=1: R_WAIT_FLIP_DONE on the GuestGpu thread (gw_flip).
	Common::FrameStats::WallSpan wall(
	    Common::FrameStats::CurrentRole() == Common::FrameStats::ThreadRole::Gpu,
	    Common::FrameStats::Counter::GpuWallFlipNs, Common::FrameStats::Counter::GpuWallFlipN);
	m_impl->GetFlipQueue().Wait(*ctx, index);
}'''),
])

patch('graphics/guest_gpu/graphicsRun.cpp', [
    ('''				{
					Common::FrameStats::Scope idle_scope(Common::FrameStats::Counter::GpuThreadIdleNs);
					gpu->m_work_available.Wait(&gpu->m_queue_mutex);
				}''', '''				{
					Common::FrameStats::Scope idle_scope(Common::FrameStats::Counter::GpuThreadIdleNs);
					Common::FrameStats::WallSpan wall(true, Common::FrameStats::Counter::GpuWallIdleNs,
					                                  Common::FrameStats::Counter::GpuWallIdleN);
					gpu->m_work_available.Wait(&gpu->m_queue_mutex);
				}'''),
    ('''					{
						Common::FrameStats::Scope blocked_scope(Common::FrameStats::Counter::GpuThreadBlockedNs);
						gpu->m_work_available.WaitFor(&gpu->m_queue_mutex, 100);
					}''', '''					{
						Common::FrameStats::Scope blocked_scope(Common::FrameStats::Counter::GpuThreadBlockedNs);
						Common::FrameStats::WallSpan wall(true, Common::FrameStats::Counter::GpuWallBlockedNs,
						                                  Common::FrameStats::Counter::GpuWallBlockedN);
						gpu->m_work_available.WaitFor(&gpu->m_queue_mutex, 100);
					}'''),
    ('''			{
				Common::FrameStats::Scope process_scope(Common::FrameStats::Counter::GpuThreadProcessNs);
				command();
			}''', '''			{
				Common::FrameStats::Scope process_scope(Common::FrameStats::Counter::GpuThreadProcessNs);
				Common::FrameStats::WallSpan wall(true, Common::FrameStats::Counter::GpuWallCmdNs,
				                                  Common::FrameStats::Counter::GpuWallCmdN);
				command();
			}'''),
    ('''			Common::FrameStats::Scope process_scope(Common::FrameStats::Counter::GpuThreadProcessNs);
			// Session 98 (patch_s98a): the latch sees this submission's seq, queue and flip state
			// for the whole slice; a resumed slice keeps its after_flip and bf_mixed bits.''',
     '''			Common::FrameStats::Scope process_scope(Common::FrameStats::Counter::GpuThreadProcessNs);
			Common::FrameStats::WallSpan wall(true, Common::FrameStats::Counter::GpuWallProcNs,
			                                  Common::FrameStats::Counter::GpuWallProcN);
			// Session 98 (patch_s98a): the latch sees this submission's seq, queue and flip state
			// for the whole slice; a resumed slice keeps its after_flip and bf_mixed bits.'''),
])
