"""Session 114, ROADMAP 0.1 "СЕССИЯ 114" item 2 (recorded first): knob `titleasync` (the title update no longer waits
for the SDL main thread while the present thread holds VideoOutConfig::mutex), the instrument (pres_title_ns/_n,
MainThreadWait: lines, flip_rsv_wait_ns/_n) and the positive control KYTY_MAIN_STALL_TEST=<frame>:<ms> (measurement
only).  Whole-line anchors, asserted.

    python C:/kyty/s106_stage/patch_s114a.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/gates.h'] = [
    ("""	// bda_nmiss).  Read once per PrepareBda call, so it CAN be a schedule arm; a switch is safe at any moment.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	BdaNarrowStamps,  // KYTY_BDA_NARROW_STAMPS,  file name "bdanarrow" (0 global, 1 per buffer, 2 global + check)
""",
     """	// bda_nmiss).  Read once per PrepareBda call, so it CAN be a schedule arm; a switch is safe at any moment.
	BdaNarrowStamps,  // KYTY_BDA_NARROW_STAMPS,  file name "bdanarrow" (0 global, 1 per buffer, 2 global + check)
	// Session 114: WindowContext::UpdateTitle hands the window title to the SDL main thread without waiting (1)
	// instead of waiting for it while the present thread holds VideoOutConfig::mutex (0, today: a busy main thread
	// then stops the flip path).  Read on every UpdateTitle call, so it CAN be a schedule arm; safe at any moment.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	TitleAsync,       // KYTY_TITLE_ASYNC,        file name "titleasync" (0 wait for the main thread, 1 post)
"""),
]

EDITS['src/common/gates.cpp'] = [
    ("""    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_BDA_NARROW_STAMPS", "bdanarrow", 0, 2},
""",
     """    {"KYTY_BDA_NARROW_STAMPS", "bdanarrow", 0, 2},
    // Session 114: UpdateTitle posts the title to the SDL main thread without waiting (1) instead of waiting under
    // VideoOutConfig::mutex (0). Read on every UpdateTitle call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_TITLE_ASYNC", "titleasync", 0, 1},
"""),
]

EDITS['src/common/frameStats.h'] = [
    ("""	GpuIdlePrio,             // gw_idle_prio
	Count
""",
     """	GpuIdlePrio,             // gw_idle_prio
	// Session 114 (item 2): pres_title_ns / pres_title_n - the wall of WindowContext::UpdateTitle on the present thread,
	// including the wait for the SDL main thread at titleasync 0; flip_rsv_wait_ns / flip_rsv_wait_n - blocking waits
	// for VideoOutConfig::mutex in ReserveFlipRequest after a failed TryLock.  Raw ns / counts.
	PresTitleNs,             // pres_title_ns
	PresTitleN,              // pres_title_n
	FlipReserveWaitNs,       // flip_rsv_wait_ns
	FlipReserveWaitN,        // flip_rsv_wait_n
	Count
"""),
]

EDITS['src/graphics/presentation/videoOut.cpp'] = [
    ("""				    {"gw_idle_prio", FS::Counter::GpuIdlePrio, false},
""",
     """				    {"gw_idle_prio", FS::Counter::GpuIdlePrio, false},
				    {"pres_title_ns", FS::Counter::PresTitleNs, false},
				    {"pres_title_n", FS::Counter::PresTitleN, false},
				    {"flip_rsv_wait_ns", FS::Counter::FlipReserveWaitNs, false},
				    {"flip_rsv_wait_n", FS::Counter::FlipReserveWaitN, false},
"""),
    ("""	Common::LockGuard lock(video_out->mutex);
	if (video_out->closing ||
	    (!IsSpecialBufferIndex(index) && !video_out->buffers[index].Occupied())) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}
	if (!driver.GetFlipQueue().Reserve(*video_out, index, flip_arg, source, request_id)) {
""",
     """	// Session 114 (ROADMAP item 2): the present thread holds this mutex for a whole present; time a blocking wait.
	if (!video_out->mutex.TryLock()) {
		const auto wait_t0 = Common::FrameStats::NowNs();
		video_out->mutex.Lock();
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipReserveWaitNs, Common::FrameStats::NowNs() - wait_t0);
		Common::FrameStats::Add(Common::FrameStats::Counter::FlipReserveWaitN, 1);
	}
	struct ReserveUnlock {
		Common::Mutex& mutex;
		~ReserveUnlock() { mutex.Unlock(); }
	} lock {video_out->mutex};
	if (video_out->closing ||
	    (!IsSpecialBufferIndex(index) && !video_out->buffers[index].Occupied())) {
		return VIDEO_OUT_ERROR_INVALID_INDEX;
	}
	if (!driver.GetFlipQueue().Reserve(*video_out, index, flip_arg, source, request_id)) {
"""),
]

EDITS['src/graphics/presentation/window/windowInternal.h'] = [
    ("""#include <memory>
#include <vector>
""",
     """#include <memory>
#include <string>
#include <vector>
"""),
    ("""	void RunOnMainThread(std::function<void()> task);
""",
     """	void RunOnMainThread(std::function<void()> task);
	// Session 114 (knob "titleasync"): queue a task for the main thread and return without waiting for it.
	void PostToMainThread(std::function<void()> task);
"""),
    ("""	uint64_t                           main_tasks_run    = 0; // guarded by main_task_mutex
""",
     """	uint64_t                           main_tasks_run    = 0; // guarded by main_task_mutex
	// Session 114 (knob "titleasync" 1): the latest title text and whether a title task is queued; the main thread
	// applies the latest text, so at most one title task waits in main_tasks.  Guarded by title_mutex.
	Common::Mutex title_mutex;
	std::string   title_text;
	bool          title_queued = false;
"""),
]

EDITS['src/graphics/presentation/window/window.cpp'] = [
    ("""#include "common/file.h"
""",
     """#include "common/file.h"
#include "common/frameStats.h"
#include "common/gates.h"
"""),
    ("""#include <cstdlib>
""",
     """#include <atomic>
#include <chrono>
#include <cstdlib>
#include <thread>
#include <utility>
"""),
    ("""void WindowContext::DrainMainThreadTasks() {
""",
     """void WindowContext::PostToMainThread(std::function<void()> task) {
	{
		Common::LockGuard lock(main_task_mutex);
		main_tasks.push_back(std::move(task));
		++main_tasks_queued;
	}
	// Wake the main loop in case it is blocked in SDL_WaitEvent.
	SDL_Event event {};
	event.type = SDL_USEREVENT;
	SDL_PushEvent(&event);
}

void WindowContext::DrainMainThreadTasks() {
"""),
    ("""	RunOnMainThread([this, text = std::move(text)] { SDL_SetWindowTitle(window, text.c_str()); });
""",
     """	// Session 114 (ROADMAP §0.1 "СЕССИЯ 114" item 2): the present thread holds VideoOutConfig::mutex here, so waiting
	// for the SDL main thread (titleasync 0) stops the flip path while the main thread is busy.  KYTY_MAIN_STALL_TEST=
	// <frame>:<ms> (measurement only, read once) queues a sleep on the main thread at one frame: the positive control.
	static const std::pair<uint64_t, uint32_t> stall_test = [] {
		std::pair<uint64_t, uint32_t> v {0, 0};
		if (const char* s = std::getenv("KYTY_MAIN_STALL_TEST"); s != nullptr) {
			char* end = nullptr;
			v.first   = std::strtoull(s, &end, 10);
			if (end != nullptr && *end == ':') {
				v.second = static_cast<uint32_t>(std::strtoul(end + 1, nullptr, 10));
			}
			LOGF("MainStallTest: frame=%llu ms=%u\\n", static_cast<unsigned long long>(v.first), v.second);
		}
		return v;
	}();
	if (stall_test.second != 0 && frame_num == stall_test.first) {
		const auto ms = stall_test.second;
		LOGF("MainStallTest: queued frame=%llu ms=%u\\n", static_cast<unsigned long long>(frame_num), ms);
		PostToMainThread([ms] { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); });
	}
	const bool title_async = Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;
	const auto title_t0    = Common::FrameStats::NowNs();
	if (title_async) {
		bool post = false;
		{
			Common::LockGuard lock(title_mutex);
			title_text   = std::move(text);
			post         = !title_queued;
			title_queued = true;
		}
		if (post) {
			PostToMainThread([this] {
				std::string latest;
				{
					Common::LockGuard lock(title_mutex);
					latest       = title_text;
					title_queued = false;
				}
				SDL_SetWindowTitle(window, latest.c_str());
			});
		}
	} else {
		RunOnMainThread([this, text = std::move(text)] { SDL_SetWindowTitle(window, text.c_str()); });
	}
	const auto title_ns = Common::FrameStats::NowNs() - title_t0;
	Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleNs, title_ns);
	Common::FrameStats::Add(Common::FrameStats::Counter::PresTitleN, 1);
	if (title_ns >= 50000000ull) {
		static std::atomic<uint32_t> wait_logged {0};
		if (wait_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
			LOGF("MainThreadWait: us=%llu frame=%llu titleasync=%d\\n",
			     static_cast<unsigned long long>(title_ns / 1000), static_cast<unsigned long long>(frame_num),
			     title_async ? 1 : 0);
		}
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
            assert old.endswith('\n') and (text.startswith(old) or ('\n' + old) in text), (rel, 'anchor not whole lines')
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
