"""Session 110: single-term mutants of stl110.py; every one must be killed by test_stl110.py."""
import subprocess
import sys
from pathlib import Path

SCORER = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/stl110.py')
TEST = Path(sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s106_stage/test_stl110.py')
src = SCORER.read_bytes().decode('utf-8')
V = "elif db <= D_FACTOR * da + D_SLACK_US and mb <= ma + M_SLACK_US:"
M = {
    'BINARY': ("fails.append('BINARY')", "pass"), 'PREREG': ("fails.append('PREREG')", "pass"),
    'ENV_PRECACHE': ("fails.append('ENV_PRECACHE')", "pass"), 'ENV_PIN': ("fails.append('ENV_PIN')", "pass"),
    'ENV_FORBIDDEN': ("fails.append('ENV_FORBIDDEN')", "pass"), 'GATES_ARM': ("fails.append('GATES_ARM')", "pass"),
    'GATES_other': ("or (' ' + other) in (' ' + gates + ' ')", ""),
    'GATES_contains': ("not gates.endswith(' ' + TOKEN[arm])", "(' ' + TOKEN[arm]) not in (' ' + gates)"),
    'ATTEMPT_hold': ("or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S", ""),
    'ATTEMPT_hold80': ("< 0.95 * HOLD_S", "< 0.80 * HOLD_S"), 'ATTEMPT_n': ("len(att) != 1 or ", ""),
    'PIN_ONCE': ("if pins != 1 or pin1 != 1:", "if pin1 < 1:"),
    'PIN_mode1_only': ("if pins != 1 or pin1 != 1:", "if pin1 != 1:"),
    'PRECACHE_OFF': ("fails.append('PRECACHE_OFF')", "pass"),
    'PRECACHE_last': ("if m and queued is None:", "if m:"),
    'NO_MARKER': ("fails.append('NO_MARKER')", "pass"),
    'MARKER_no_fatal': ("b'abort()', b'fatal', ", "b'abort()', "),
    'MARKER_no_stdout': ("    if stdout_p.is_file():", "    if False:"),
    'ROWS_min': ("rows < MIN_ROWS or ", ""), 'ROWS_missing': ("or missing:", "or False:"),
    'ARM_A_look': ("(tot['cspfree_hit'] or tot['cspfree_look'])", "tot['cspfree_hit']"),
    'ARM_B': ("fails.append('ARM_B_ARMED')", "pass"),
    'ARM_B_bad': ("(tot['cspfree_hit'] <= 0 or tot['cspfree_bad'])", "tot['cspfree_hit'] <= 0"),
    'IDENTITY': ("errors.append('IDENTITY')", "pass"), 'ORDER': ("errors.append('ORDER')", "pass"),
    'ORDER_dupes': (" or len(set(stamps)) != len(stamps)", ""),
    'DRAFT': ("errors.append('DRAFT')", "pass"), 'SEAL': ("errors.append('SEAL')", "pass"),
    'STALL_SYNC': ("fails.append('STALL_SYNC')", "pass"),
    'STALL_SYNC_low': ("if not 0 <= s - stall_n <= 1:", "if not s - stall_n <= 1:"),
    'STALL_SYNC_high': ("if not 0 <= s - stall_n <= 1:", "if not 0 <= s - stall_n <= 2:"),
    'STALL_max': ("stall_m = max(stall_m, us)", "stall_m = us"),
    'STALL_kind': ("rb'^CsStall: kind=(new|wait) us=", "rb'^CsStall: kind=(new) us="),
    'POWER': ("elif na == 0:", "elif False:"),
    'D_FACTOR': (V, V.replace('D_FACTOR * da', '1.3 * da')),
    'D_SLACK': (V, V.replace('D_SLACK_US and', 'D_SLACK_US + 1 and')),
    'D_off': (V, "elif mb <= ma + M_SLACK_US:"), 'M_off': (V, "elif db <= D_FACTOR * da + D_SLACK_US:"),
    'M_SLACK': (V, V.replace('ma + M_SLACK_US:', 'ma + M_SLACK_US + 1:')),
    'D_edge': (V, V.replace('db <=', 'db <')), 'M_edge': (V, V.replace('mb <=', 'mb <')),
}
alive = []
for name, (a, b) in M.items():
    assert src.count(a) == 1, name
    m = SCORER.with_name('mut_stl110_%s.py' % name)
    m.write_bytes(src.replace(a, b).encode('utf-8'))
    r = subprocess.run([sys.executable, str(TEST), str(m)], capture_output=True, text=True)
    killed = 'FIXTURE FAILURES' in r.stdout
    print('%-18s %s' % (name, 'killed' if killed else 'ALIVE'))
    if not killed:
        alive.append(name)
    m.unlink()
print('mutants %d  %s' % (len(M), 'ALL KILLED' if not alive else 'ALIVE: %s' % alive))
