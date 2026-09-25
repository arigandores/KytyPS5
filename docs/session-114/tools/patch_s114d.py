"""Session 114, ROADMAP 0.1 "СЕССИЯ 114" item 11 (recorded first): the PresentOverlap detector covers the swapchain work
only - it is left before UpdateTitle, where the present thread parks at startup (the park is inside Present).
Whole-line anchors, asserted.

    python C:/kyty/s106_stage/patch_s114d.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/graphics/presentation/window/swapchain.cpp'] = [
    ("""	// Session 114 (ROADMAP item 10): the PresentOverlap detector - presenting is single-threaded by design (the
	// startup park, review C1); a second thread entering while another is inside is counted and logged.
	static std::atomic<int> present_inside {0};
	struct PresentInside {
		PresentInside() {
""",
     """	// Session 114 (ROADMAP items 10, 11): the PresentOverlap detector - the swapchain work is single-threaded by design
	// (the startup park, review C1); a second thread entering while another is inside is counted and logged.  The zone
	// ends before UpdateTitle (Leave), because the startup park itself happens inside UpdateTitle.
	static std::atomic<int> present_inside {0};
	struct PresentInside {
		bool inside = true;
		PresentInside() {
"""),
    ("""		~PresentInside() { present_inside.fetch_sub(1, std::memory_order_acq_rel); }
""",
     """		void Leave() {
			if (inside) {
				inside = false;
				present_inside.fetch_sub(1, std::memory_order_acq_rel);
			}
		}
		~PresentInside() { Leave(); }
"""),
    ("""		if (!preparing) m_impl->window.UpdateTitle();
""",
     """		present_inside_guard.Leave();
		if (!preparing) m_impl->window.UpdateTitle();
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
