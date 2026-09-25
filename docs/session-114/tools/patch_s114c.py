"""Session 114, ROADMAP 0.1 "СЕССИЯ 114" items 9 and 10 (recorded first): titleasync defaults to 1 (seal 02b SHIP);
measurement-only KYTY_PREPARE_HOLD_MS (WindowPrepareShaders keeps presenting from the main thread for >= N ms) and the
PresentOverlap detector (a second thread entering Presenter::Present while another is inside: counter present_overlap,
PresentOverlap: lines).  Whole-line anchors, asserted.

    python C:/kyty/s106_stage/patch_s114c.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/gates.cpp'] = [
    ("""    // Session 114: UpdateTitle posts the title to the SDL main thread without waiting (1) instead of waiting under
    // VideoOutConfig::mutex (0). Read on every UpdateTitle call, so it CAN be a schedule arm.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_TITLE_ASYNC", "titleasync", 0, 1},
""",
     """    // Session 114: UpdateTitle posts the title to the SDL main thread without waiting (1) instead of waiting under
    // VideoOutConfig::mutex (0). Read on every UpdateTitle call, so it CAN be a schedule arm. Default 1 since the
    // sealed ABBA pred/02b_ttl114b.md (SHIP: d mean dt -43.5 us, 2SE 73.2; control pred/01_ctl114.md PASS; video clean).
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_TITLE_ASYNC", "titleasync", 1, 1},
"""),
]

EDITS['src/common/gates.h'] = [
    ("""	// then stops the flip path).  Read on every UpdateTitle call, so it CAN be a schedule arm; safe at any moment.
""",
     """	// then stops the flip path).  Read on every UpdateTitle call, so it CAN be a schedule arm; safe at any moment.
	// Default 1 since session 114 (seal 02b SHIP); the async path starts only once the SDL main loop runs.
"""),
]

EDITS['src/common/frameStats.h'] = [
    ("""	MainTaskN,               // mt_n
	Count
""",
     """	MainTaskN,               // mt_n
	// Session 114 (item 10): a thread entered Presenter::Present while another was inside (must stay 0).  Raw count.
	PresentOverlap,          // present_overlap
	Count
"""),
]

EDITS['src/graphics/presentation/videoOut.cpp'] = [
    ("""				    {"mt_n", FS::Counter::MainTaskN, false},
""",
     """				    {"mt_n", FS::Counter::MainTaskN, false},
				    {"present_overlap", FS::Counter::PresentOverlap, false},
"""),
]

EDITS['src/graphics/presentation/window/swapchain.cpp'] = [
    ("""#include <algorithm>
#include <deque>
""",
     """#include <algorithm>
#include <atomic>
#include <deque>
#include <functional>
#include <thread>
"""),
    ("""void Presenter::Present(Frame& frame, bool reuse) {
	KYTY_PROFILER_FUNCTION();
""",
     """void Presenter::Present(Frame& frame, bool reuse) {
	KYTY_PROFILER_FUNCTION();
	// Session 114 (ROADMAP item 10): the PresentOverlap detector - presenting is single-threaded by design (the
	// startup park, review C1); a second thread entering while another is inside is counted and logged.
	static std::atomic<int> present_inside {0};
	struct PresentInside {
		PresentInside() {
			if (present_inside.fetch_add(1, std::memory_order_acq_rel) != 0) {
				Common::FrameStats::Add(Common::FrameStats::Counter::PresentOverlap, 1);
				static std::atomic<uint32_t> overlap_logged {0};
				if (overlap_logged.fetch_add(1, std::memory_order_relaxed) < 8) {
					LOGF("PresentOverlap: thread=%llu\\n", static_cast<unsigned long long>(
					                                           std::hash<std::thread::id> {}(std::this_thread::get_id())));
				}
			}
		}
		~PresentInside() { present_inside.fetch_sub(1, std::memory_order_acq_rel); }
		KYTY_CLASS_NO_COPY(PresentInside);
	} present_inside_guard;
"""),
]

EDITS['src/graphics/presentation/window/window.cpp'] = [
    ("""	const auto started = SDL_GetTicks64();
	uint64_t last_log = 0;
	while (true) {
		const auto status = cache.GetPreparationStatus();
		if (!status.active) break;
""",
     """	const auto started = SDL_GetTicks64();
	// Session 114 (ROADMAP item 10, MEASUREMENT ONLY): KYTY_PREPARE_HOLD_MS keeps presenting the preparation screen from
	// the main thread for at least N ms after the wait started - the stress for the startup park (review C1).
	static const uint64_t hold_ms = [] {
		const char* value = std::getenv("KYTY_PREPARE_HOLD_MS");
		return value != nullptr ? static_cast<uint64_t>(std::strtoull(value, nullptr, 10)) : uint64_t {0};
	}();
	if (hold_ms != 0) {
		LOGF("PrepareHold: ms=%llu\\n", static_cast<unsigned long long>(hold_ms));
	}
	uint64_t last_log = 0;
	while (true) {
		const auto status = cache.GetPreparationStatus();
		if (!status.active && SDL_GetTicks64() - started >= hold_ms) break;
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
