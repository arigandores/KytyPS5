# scan_f45a.py - track F, link F45a (HPP-795): DCC stale resets around the level start of a Sky Garden log (read only).
# Usage: python scan_f45a.py <log> [<log> ...]. Per log: lines "stale pending DCC fill ignored" before / after the line
# "GuestOut: Level has started: underwater_aerial_garden", the (image, dcc, fill) of those after, and "skipped draw" lines.
import re, sys
RX = re.compile(rb"image=(0x[0-9a-f]+) dcc=(0x[0-9a-f]+) fill=(0x[0-9a-f]+) size=(0x[0-9a-f]+)")
for path in sys.argv[1:]:
    before = after = skipped = 0
    lvl = None
    keys = []
    with open(path, "rb") as f:
        for n, line in enumerate(f, 1):
            if b"skipped draw" in line:
                skipped += 1
            elif b"Level has started: underwater_aerial_garden" in line and lvl is None:
                lvl = n
            elif b"stale pending DCC fill ignored" in line:
                if lvl is None:
                    before += 1
                else:
                    after += 1
                    m = RX.search(line)
                    keys.append(b"/".join(m.groups()).decode() if m else "?")
    print("%s level_line=%s stale_before=%d stale_after=%d skipped_draw=%d" % (path, lvl, before, after, skipped))
    for k in keys:
        print("  after " + k)
