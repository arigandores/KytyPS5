"""Session 114, ROADMAP 0.1 "СЕССИЯ 114" item 15 (recorded first): titleasync back to default 0 - the sealed consequence
of pred/03 (the boot check was not admitted twice); re-ship in session 115 after the presentation-ring fix and a boot
check.  Whole-line anchors, asserted.

    python C:/kyty/s106_stage/patch_s114e.py [--dry]
"""
import sys
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
DRY = '--dry' in sys.argv
EDITS = {}

EDITS['src/common/gates.cpp'] = [
    ("""    // VideoOutConfig::mutex (0). Read on every UpdateTitle call, so it CAN be a schedule arm. Default 1 since the
    // sealed ABBA pred/02b_ttl114b.md (SHIP: d mean dt -43.5 us, 2SE 73.2; control pred/01_ctl114.md PASS; video clean).
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_TITLE_ASYNC", "titleasync", 1, 1},
""",
     """    // VideoOutConfig::mutex (0). Read on every UpdateTitle call, so it CAN be a schedule arm. The sealed ABBA
    // pred/02b_ttl114b.md said SHIP (d mean dt -43.5 us, 2SE 73.2), but the boot check of pred/03 was not admitted
    // twice (a knob-independent startup crash, commandRecorder.cpp:326), so the default stays 0 until session 115.
    // LAST row, matching the LAST enum entry before Knob::Count.
    {"KYTY_TITLE_ASYNC", "titleasync", 0, 1},
"""),
]

EDITS['src/common/gates.h'] = [
    ("""	// Default 1 since session 114 (seal 02b SHIP); the async path starts only once the SDL main loop runs.
""",
     """	// Default 0 (session 114 item 15, re-ship pending); the async path starts only once the SDL main loop runs.
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
