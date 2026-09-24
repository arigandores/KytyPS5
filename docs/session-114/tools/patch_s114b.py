"""Session 114, ROADMAP 0.1 "СЕССИЯ 114" item 4 (recorded first): the review fixes of `titleasync`.
C1: the async title path only once the SDL main loop runs (WindowContext::main_loop_running, set in Run() before the
first DrainMainThreadTasks) - before that the waiting path keeps parking the present thread while WindowPrepareShaders
presents from the main thread.  C2: pres_title_* and MainThreadWait: only after the loop started.  F1: the hold of
VideoOutConfig::mutex in FlipQueue::Flip by phase (flip_hold_ns/_n, FlipHold: lines > 50 ms) and the queue-to-run age
of main-thread tasks (mt_age_ns/mt_n, MainTaskLate: lines > 50 ms).  Whole-line anchors, asserted; LF kept as found.

    python C:/kyty/s106_stage/patch_s114b.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/frameStats.h'] = [
    ("""	FlipReserveWaitN,        // flip_rsv_wait_n
	Count
""",
     """	FlipReserveWaitN,        // flip_rsv_wait_n
	// Session 114 (item 4): flip_hold_ns / flip_hold_n - the hold of VideoOutConfig::mutex in FlipQueue::Flip (lands in
	// the next FrameTrace row: the snapshot is taken inside the hold); mt_age_ns / mt_n - the queue-to-run age of the
	// SDL main thread's tasks (RunOnMainThread and PostToMainThread).  Raw ns / counts.
	FlipHoldNs,              // flip_hold_ns
	FlipHoldN,               // flip_hold_n
	MainTaskAgeNs,           // mt_age_ns
	MainTaskN,               // mt_n
	Count
"""),
]

VO = 'src/graphics/presentation/videoOut.cpp'
EDITS[VO] = [
    ("""				    {"flip_rsv_wait_n", FS::Counter::FlipReserveWaitN, false},
""",
     """				    {"flip_rsv_wait_n", FS::Counter::FlipReserveWaitN, false},
				    {"flip_hold_ns", FS::Counter::FlipHoldNs, false},
				    {"flip_hold_n", FS::Counter::FlipHoldN, false},
				    {"mt_age_ns", FS::Counter::MainTaskAgeNs, false},
				    {"mt_n", FS::Counter::MainTaskN, false},
"""),
    ("""	r.cfg->mutex.Lock();
	if (!IsFlipDueLocked(*r.cfg, r.generation)) {
""",
     """	r.cfg->mutex.Lock();
	// Session 114 (ROADMAP item 4): the hold of VideoOutConfig::mutex by phase - GuestGpu's ReserveFlipRequest waits on it.
	const uint64_t hold_t0    = Common::FrameStats::NowNs();
	uint64_t       present_ns = 0;
	uint64_t       poll_ns    = 0;
	if (!IsFlipDueLocked(*r.cfg, r.generation)) {
"""),
    ("""	} else {
		m_presenter.Present(*r.frame);
	}
""",
     """	} else {
		const uint64_t present_t0 = Common::FrameStats::NowNs();
		m_presenter.Present(*r.frame);
		present_ns = Common::FrameStats::NowNs() - present_t0;
	}
"""),
    ("""	Common::Gates::Poll(static_cast<uint32_t>(r.cfg->flip_status.count));
""",
     """	const uint64_t poll_t0 = Common::FrameStats::NowNs();
	Common::Gates::Poll(static_cast<uint32_t>(r.cfg->flip_status.count));
	poll_ns = Common::FrameStats::NowNs() - poll_t0;
"""),
    ("""	m_mutex.Unlock();
	r.cfg->mutex.Unlock();

	Graphics::RenderDocOnGuestFlip(m_presenter.Renderer());
""",
     """	m_mutex.Unlock();
	{
		const uint64_t hold_ns = Common::FrameStats::NowNs() - hold_t0;
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipHoldNs, hold_ns);
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipHoldN, 1);
		if (hold_ns >= 50000000ull) {
			static std::atomic<uint32_t> hold_logged {0};
			if (hold_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
				const uint64_t named = present_ns + poll_ns;
				LOGF("FlipHold: us=%llu present_us=%llu poll_us=%llu other_us=%llu flip=%llu\\n",
				     static_cast<unsigned long long>(hold_ns / 1000), static_cast<unsigned long long>(present_ns / 1000),
				     static_cast<unsigned long long>(poll_ns / 1000),
				     static_cast<unsigned long long>((hold_ns > named ? hold_ns - named : 0) / 1000),
				     static_cast<unsigned long long>(r.cfg->flip_status.count));
			}
		}
	}
	r.cfg->mutex.Unlock();

	Graphics::RenderDocOnGuestFlip(m_presenter.Renderer());
"""),
]

EDITS['src/graphics/presentation/window/windowInternal.h'] = [
    ("""	uint64_t                           main_tasks_run    = 0; // guarded by main_task_mutex
""",
     """	uint64_t                           main_tasks_run    = 0; // guarded by main_task_mutex
	// Session 114 (item 4): the enqueue time of each main-thread task, parallel to main_tasks (guarded by
	// main_task_mutex); DrainMainThreadTasks reports the queue-to-run age (mt_age_ns, MainTaskLate: lines).
	std::vector<uint64_t>              main_task_enqueue_ns;
	// Session 114 (item 4, review C1): set by Run() before its first DrainMainThreadTasks.  Until then UpdateTitle keeps
	// the waiting path, which parks the present thread while WindowPrepareShaders presents from the main thread.
	std::atomic<bool>                  main_loop_running {false};
"""),
]

EDITS['src/graphics/presentation/window/window.cpp'] = [
    ("""		main_tasks.push_back(std::move(task));
		ticket = ++main_tasks_queued;
""",
     """		main_tasks.push_back(std::move(task));
		main_task_enqueue_ns.push_back(Common::FrameStats::NowNs());
		ticket = ++main_tasks_queued;
"""),
    ("""		main_tasks.push_back(std::move(task));
		++main_tasks_queued;
""",
     """		main_tasks.push_back(std::move(task));
		main_task_enqueue_ns.push_back(Common::FrameStats::NowNs());
		++main_tasks_queued;
"""),
    ("""	std::vector<std::function<void()>> tasks;
	{
		Common::LockGuard lock(main_task_mutex);
		tasks.swap(main_tasks);
	}
	if (tasks.empty()) {
		return;
	}
	for (auto& task: tasks) {
		task();
	}
""",
     """	std::vector<std::function<void()>> tasks;
	std::vector<uint64_t>              enqueued;
	{
		Common::LockGuard lock(main_task_mutex);
		tasks.swap(main_tasks);
		enqueued.swap(main_task_enqueue_ns);
	}
	if (tasks.empty()) {
		return;
	}
	for (size_t i = 0; i < tasks.size(); i++) {
		// Session 114 (ROADMAP item 4): the queue-to-run age - a busy main thread stays visible at titleasync 1.
		if (i < enqueued.size()) {
			const auto age = Common::FrameStats::NowNs() - enqueued[i];
			Common::FrameStats::Add(Common::FrameStats::Counter::MainTaskAgeNs, age);
			Common::FrameStats::Add(Common::FrameStats::Counter::MainTaskN, 1);
			if (age >= 50000000ull) {
				static std::atomic<uint32_t> late_logged {0};
				if (late_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
					LOGF("MainTaskLate: us=%llu\\n", static_cast<unsigned long long>(age / 1000));
				}
			}
		}
		tasks[i]();
	}
"""),
    ("""	loop.paused.store(false, std::memory_order_release);

	while (!loop.need_exit) {
""",
     """	loop.paused.store(false, std::memory_order_release);
	// Session 114 (ROADMAP item 4, review C1): from here on UpdateTitle may take the async title path.
	main_loop_running.store(true, std::memory_order_release);

	while (!loop.need_exit) {
"""),
    ("""	const bool title_async = Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;
""",
     """	// Session 114 (ROADMAP item 4, review C1): the async path only once the SDL main loop runs - before WindowRun the
	// waiting path parks the present thread, which keeps it out of Present while WindowPrepareShaders presents.
	const bool loop_running = main_loop_running.load(std::memory_order_acquire);
	const bool title_async  = loop_running && Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;
"""),
    ("""	Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleNs, title_ns);
	Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleN, 1);
	if (title_ns >= 50000000ull) {
""",
     """	if (loop_running) {
		Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleNs, title_ns);
		Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleN, 1);
	}
	if (loop_running && title_ns >= 50000000ull) {
"""),
]


def main():
    for rel, pairs in EDITS.items():
        path = ROOT / rel
        raw = path.read_bytes().decode('utf-8')
        crlf = '\r\n' in raw
        text = raw.replace('\r\n', '\n')
        for old, new in pairs:
            assert old.endswith('\n') and (text.startswith(old) or ('\n' + old) in text), (rel, 'anchor not whole lines')
            n = text.count(old)
            assert n == 1, (rel, n, old[:90])
            text = text.replace(old, new)
        if crlf:
            print('note: %s was CRLF in the working tree; written as LF (the repository form)' % rel)
        if not DRY:
            path.write_bytes(text.encode('utf-8'))
        print(('checked ' if DRY else 'patched ') + rel)


if __name__ == '__main__':
    main()
