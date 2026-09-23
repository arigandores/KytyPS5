"""Session 110: derive test_stl110.py from the session-109 test_ent109b.py: CsStall lines per stall, the duration
verdict branches, STALL_SYNC fixtures.  Byte-reproducible."""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC_SHA = '4b97143d43257ff91aebd2d1b5690421d6909f33e53b15dc1eb732f7c36f4545'
src = (STAGE / 'test_ent109b.py').read_bytes()
assert hashlib.sha256(src).hexdigest() == SRC_SHA, 'test_ent109b.py moved'
s = src.decode('utf-8')
n_tag = s.count("'ent109b_")
pairs = [
    ('"""Session 109: fixtures for ent109b.py (derived by make_ent109b.py).',
     '"""Session 110: fixtures for stl110.py (derived from test_ent109b.py by make_test_stl110.py).'),
    ("BASE = Path('C:/kyty/s106_stage/fx_ent109b')", "BASE = Path('C:/kyty/s106_stage/fx_stl110')"),
    ("spec = importlib.util.spec_from_file_location('ent109b', SRC)",
     "spec = importlib.util.spec_from_file_location('stl110', SRC)"),
    ("seal.write_bytes(b'fixture seal 109 entb')", "seal.write_bytes(b'fixture seal 110 stl')"),
    ("""                  'cspfree_look=%d cspfree_hit=%d cspfree_bad=%d') % (sn, sw, 1 if arm == 'B' else 0, look, skip,""",
     """                  'cspfree_look=%d cspfree_hit=%d cspfree_bad=%d cs_sync_new_us=0 cs_sync_wait_us=0') % (
                      sn, sw, 1 if arm == 'B' else 0, look, skip,"""),
    ("""    if 'marker' in bad:
        lines.append(bad['marker'])""", """    if 'marker' in bad:
        lines.append(bad['marker'])
    # Session 110: one CsStall line per stall (count = s unless overridden), 5 000 us each unless overridden
    for k in range(bad.get('stall_lines', s)):
        us = bad.get('stall_first_us', 5000) if k == 0 else 5000
        lines.append('CsStall: kind=%s us=%d id=%d hash=0x%016x' % ('new' if k % 2 == 0 else 'wait', us, 100 + k, k))"""),
    ("'ent109b_", "'stl110_"),
    ("""    ('PASS', dict(), 'PASS', []),
    ('PASS_edge', dict(sa=(1, 1, 0, 0), sb=(1, 1, 1, 1)), 'PASS', []),          # S_B = S_A + 2
    ('FAIL', dict(sa=(1, 1, 0, 0), sb=(2, 1, 1, 1)), 'FAIL', []),               # S_B = S_A + 3
    ('NO_POWER', dict(sa=(0, 0, 0, 0), sb=(0, 0, 0, 0)), 'NO_POWER', []),
    ('NO_POWER_b', dict(sa=(0, 0, 0, 0), sb=(3, 0, 0, 0)), 'NO_POWER', []),     # B alone cannot give power""",
     """    ('PASS', dict(), 'PASS', []),                                               # D_A 20 000, D_B 20 000
    ('PASS_D_edge', dict(sb=(3, 2, 2, 2)), 'PASS', []),                         # D_B 45 000 = 1.25 * 20 000 + 20 000
    ('FAIL_D', dict(sb=(3, 3, 2, 2)), 'FAIL', []),                              # D_B 50 000
    ('FAIL_D_just', dict(sb=(3, 2, 2, 2), per={1: {'stall_first_us': 5001}}), 'FAIL', []),  # D_B 45 001
    ('FAIL_M_first', dict(sb=(2, 1, 1, 1), per={1: {'stall_first_us': 15001}}), 'FAIL', []),  # max is not the last line
    ('PASS_M_edge', dict(per={1: {'stall_first_us': 15000}}), 'PASS', []),      # M_B = M_A + 10 000
    ('FAIL_M', dict(per={1: {'stall_first_us': 15001}}), 'FAIL', []),           # only M exceeds (D_B 30 001)
    ('PASS_more_events', dict(sa=(3, 3, 3, 3), sb=(4, 4, 4, 4)), 'PASS', []),   # 16 vs 12 events, D 80 000 <= 95 000
    ('NO_POWER', dict(sa=(0, 0, 0, 0), sb=(0, 0, 0, 0)), 'NO_POWER', []),
    ('NO_POWER_b', dict(sa=(0, 0, 0, 0), sb=(3, 0, 0, 0)), 'NO_POWER', []),     # B alone cannot give power
    ('SYNC_inflight', dict(per={1: {'stall_lines': 0}}), 'PASS', []),          # one stall in flight at exit is allowed
    ('SYNC_missing', dict(sb=(2, 1, 1, 1), per={1: {'stall_lines': 0}}), 'NOT_ADMITTED', ['stl110_2:STALL_SYNC']),
    ('SYNC_extra', dict(per={0: {'stall_lines': 2}}), 'NOT_ADMITTED', ['stl110_1:STALL_SYNC']),"""),
    # session-109 audit survivors (AUDIT109 MINOR-5)
    ("""    if not bad.get('no_log'):""", """    if 'stdout_marker' in bad:
        (d / ('stdout_%s.txt' % tag)).write_bytes((bad['stdout_marker'] + NL).encode('utf-8'))
    if 'pin_extra' in bad:
        lines.insert(1, bad['pin_extra'])
    if 'precache_first' in bad:
        lines.insert(1, bad['precache_first'])
    if not bad.get('no_log'):"""),
    ("""    ('ARM_B_bad', dict(per={B0: {'free_bad': 1}}), 'NOT_ADMITTED', ['stl110_2:ARM_B_ARMED']),
""", """    ('ARM_B_bad', dict(per={B0: {'free_bad': 1}}), 'NOT_ADMITTED', ['stl110_2:ARM_B_ARMED']),
    ('PIN_mode2', dict(per={0: {'pin_extra': 'GpuClockPin: mode 2'}}), 'NOT_ADMITTED', ['stl110_1:PIN_ONCE']),
    ('MARK_fatal', dict(per={B0: {'marker': '--- Fatal Error ---'}}), 'NOT_ADMITTED', ['stl110_2:NO_MARKER']),
    ('MARK_stdout', dict(per={3: {'stdout_marker': 'Unhandled exception: 0xC0000005'}}), 'NOT_ADMITTED',
     ['stl110_4:NO_MARKER']),
    ('GATES_notail', dict(per={B0: {'gates': 'cspfree=1 ' + GATES}}), 'NOT_ADMITTED', ['stl110_2:GATES_ARM']),
    ('ATT_hold_edge', dict(per={0: {'att': {'hold_s': 140.0}}}), 'NOT_ADMITTED', ['stl110_1:ATTEMPT']),
    ('ORDER_dupe', dict(per={1: {'launched': '2026-09-24T10:10:00'}}), 'NOT_ADMITTED', ['ORDER']),
    ('PRECACHE_first', dict(per={0: {'precache_first': 'PipelinePrecache: 641 recipes -> 520 graphics + 121 compute '
                                                       'pipelines queued, 0 skipped'}}), 'NOT_ADMITTED',
     ['stl110_1:PRECACHE_OFF']),
"""),
]
for a, b in pairs:
    want = n_tag if a == "'ent109b_" else 1
    assert s.count(a) == want, (a[:60], s.count(a))
    s = s.replace(a, b)
(STAGE / 'test_stl110.py').write_bytes(s.encode('utf-8'))
print('test_stl110.py', hashlib.sha256(s.encode('utf-8')).hexdigest())
