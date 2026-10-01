# F5a2 (HPP-366): string census of the F5c binary (ROADMAP p.280(d)) against abce7916 (F5a) and the installed 9235a7ac.
# Usage: python accept_f5a.py   -> prints a table and "ACCEPT ALL OK" when the worktree binary has the required rows.
import hashlib

BINS = [
    ('wt 6f495a65 (4fc501f4 + F5a + F5a2)', 'C:/kyty/f287/bin/kyty_emulator_6f495a65.exe'),
    ('wt abce7916 (4fc501f4 + F5a)', 'C:/kyty/f287/bin/kyty_emulator_abce7916.exe'),
    ('installed 9235a7ac', 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'),
]
# string, required count in the worktree binary (None - data only)
ROWS = [
    ('699c1e4b7db359067b461e029b913c4b6e78dc90', 1),
    ('KYTY_FIX_MINIMIZE', 1),
    ('FixMinimize: on', 1),
    ('SwapchainZeroExtent: begin', 1),
    ('SwapchainZeroExtent: end frames_dropped=', 1),
    ('KYTY_TEST_MINIMIZE', 1),
    ('TestMinimize: minimize', 1),
    ('TestMinimize: restore', 1),
    ('TestMinimize: armed', 1),
    ('TestMinimize: config', 1),
    ('Level has started: ', None),
    ('KYTY_FIX_B1B', 0),
    ('KYTY_FIX_B26', 0),
    ('KYTY_FIX_DUALSRC', 0),
    ('KYTY_S_PCW', 0),
]

data = []
for name, path in BINS:
    b = open(path, 'rb').read()
    data.append((name, b))
    print('%-32s sha256 %s bytes %d' % (name, hashlib.sha256(b).hexdigest(), len(b)))
print()
print('%-44s %s' % ('string', ' | '.join(n for n, _ in BINS)))
ok = True
for s, req in ROWS:
    counts = [b.count(s.encode()) for _, b in data]
    mark = ''
    if req is not None:
        good = counts[0] == req
        ok &= good
        mark = '  required %d %s' % (req, 'OK' if good else 'FAIL')
    print('%-44s %s%s' % (s, ' | '.join(str(c) for c in counts), mark))
print()
print('ACCEPT ALL OK' if ok else 'ACCEPT FAIL')
