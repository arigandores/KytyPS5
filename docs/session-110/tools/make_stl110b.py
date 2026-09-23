"""Session 110: stl110b.py / test_stl110b.py from stl110.py / test_stl110.py (ROADMAP §0.1 "СЕССИЯ 110" item 4):
STALL_SYNC compares only the CsStall lines logged after the first FrameTrace-x row (startup stalls before it are
never counted by any row); D and M still take every line.  Byte-reproducible."""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')


def derive(src, src_sha, dst, pairs, counts=None):
    b = (STAGE / src).read_bytes()
    assert hashlib.sha256(b).hexdigest() == src_sha, src + ' moved'
    s = b.decode('utf-8')
    for a, r in pairs:
        want = (counts or {}).get(a, 1)
        assert (s.count(a) >= 1) if want is None else (s.count(a) == want), (src, a[:70], s.count(a))
        s = s.replace(a, r)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('stl110.py', 'bb475bb4a4f5c4499905126240fcb46da50db538626a069c255bf8dffb9d6f0d', 'stl110b.py', [
    ('"""Session 110, pred/01_stl110.md: the powered guard of knob `cspfree` by stall DURATION, an ABBA of ENTRIES (derived\nfrom ent109b.py by make_stl110.py).',
     '"""Session 110, pred/02_stl110b.md: the powered guard of knob `cspfree` by stall DURATION, an ABBA of ENTRIES (from\nstl110.py by make_stl110b.py: STALL_SYNC counts only CsStall lines after the first FrameTrace-x row).'),
    ("              its FrameTrace-x sum(cs_sync_new + cs_sync_wait), allowing one stall in flight at exit)",
     "              its FrameTrace-x sum(cs_sync_new + cs_sync_wait) after the first row, one stall in flight allowed)"),
    ("python C:/kyty/s110/stl110.py", "python C:/kyty/s110/stl110b.py"),
    ("PRED = 'C:/kyty/s110/pred/01_stl110.md'", "PRED = 'C:/kyty/s110/pred/02_stl110b.md'"),
    ("TAGS = ['stl110_%d' % (i + 1) for i in range(len(ORDER))]", "TAGS = ['stl110b_%d' % (i + 1) for i in range(len(ORDER))]"),
    ("    stall_n = stall_d = stall_m = 0\n", "    stall_n = stall_d = stall_m = stall_after = 0\n"),
    ("                stall_n += 1\n", "                stall_n += 1\n                stall_after += int(rows > 0)  # startup stalls precede every counted row\n"),
    ("    if not 0 <= s - stall_n <= 1:", "    if not 0 <= s - stall_after <= 1:"),
    ("fails=fails, s=s, stall_n=stall_n,", "fails=fails, s=s, stall_n=stall_n, stall_after=stall_after,"),
])

derive('test_stl110.py', 'e48b06acff06f9741211a3caf0a382f58472c0c72e6d4c5498dd5c8f4ca6d0cf', 'test_stl110b.py', [
    ('"""Session 110: fixtures for stl110.py (derived from test_ent109b.py by make_test_stl110.py).',
     '"""Session 110: fixtures for stl110b.py (from test_stl110.py by make_stl110b.py).'),
    ("BASE = Path('C:/kyty/s106_stage/fx_stl110')", "BASE = Path('C:/kyty/s106_stage/fx_stl110b')"),
    ("spec = importlib.util.spec_from_file_location('stl110', SRC)",
     "spec = importlib.util.spec_from_file_location('stl110b', SRC)"),
    ("seal.write_bytes(b'fixture seal 110 stl')", "seal.write_bytes(b'fixture seal 110 stlb')"),
    ("""    # Session 110: one CsStall line per stall (count = s unless overridden), 5 000 us each unless overridden
    for k in range(bad.get('stall_lines', s)):
        us = bad.get('stall_first_us', 5000) if k == 0 else 5000
        lines.append('CsStall: kind=%s us=%d id=%d hash=0x%016x' % ('new' if k % 2 == 0 else 'wait', us, 100 + k, k))
    rows = bad.get('rows', 1100)""", """    # Session 110b: the counted stalls' lines go right after the first FrameTrace-x row; 'startup_stalls' lines
    # precede every row (as the real startup stalls do) and count in D and M only
    stall_block = []
    for k in range(bad.get('stall_lines', s)):
        us = bad.get('stall_first_us', 5000) if k == 0 else 5000
        stall_block.append('CsStall: kind=%s us=%d id=%d hash=0x%016x' % ('new' if k % 2 == 0 else 'wait', us, 100 + k, k))
    for k, us in enumerate(bad.get('startup_stalls', ())):
        lines.append('CsStall: kind=wait us=%d id=%d hash=0x%016x' % (us, 900 + k, k))
    rows = bad.get('rows', 1100)
    first_row = len(lines)"""),
    ("""    assert new_left <= 0 and wait_left <= 0, 'fixture too short for s'
""", """    assert new_left <= 0 and wait_left <= 0, 'fixture too short for s'
    lines[first_row + 1:first_row + 1] = stall_block
"""),
    ("'stl110_", "'stl110b_"),
    ("""    ('SYNC_extra', dict(per={0: {'stall_lines': 2}}), 'NOT_ADMITTED', ['stl110b_1:STALL_SYNC']),""",
     """    ('SYNC_extra', dict(per={0: {'stall_lines': 2}}), 'NOT_ADMITTED', ['stl110b_1:STALL_SYNC']),
    ('STARTUP_ok', dict(per={0: {'startup_stalls': (12000,)}, 1: {'startup_stalls': (12000,)}}), 'PASS', []),
    ('STARTUP_only', dict(sa=(0, 0, 0, 0), sb=(0, 0, 0, 0), per={0: {'startup_stalls': (3000,)}}), 'PASS', []),
    ('STARTUP_in_M', dict(per={1: {'startup_stalls': (15001,)}}), 'FAIL', []),
    ('STARTUP_in_D', dict(per={1: {'startup_stalls': (5000, 5000, 5000, 5000, 5000, 5001)}}), 'FAIL', []),"""),
], counts={"'stl110_": None})
