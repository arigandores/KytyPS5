import subprocess
import sys
from pathlib import Path

src = Path('C:/kyty/s106_stage/ent109b.py').read_bytes().decode('utf-8')
MUTANTS = {
    'BINARY': ("fails.append('BINARY')", "pass"),
    'PREREG': ("fails.append('PREREG')", "pass"),
    'ENV_PRECACHE': ("fails.append('ENV_PRECACHE')", "pass"),
    'ENV_PIN': ("fails.append('ENV_PIN')", "pass"),
    'ENV_FORBIDDEN': ("fails.append('ENV_FORBIDDEN')", "pass"),
    'GATES_ARM': ("fails.append('GATES_ARM')", "pass"),
    'GATES_other': ("or (' ' + other) in (' ' + gates + ' ')", ""),
    'ATTEMPT_hold': ("or (att[0].get('hold_s') or 0) < 0.95 * HOLD_S", ""),
    'ATTEMPT_n': ("len(att) != 1 or ", ""),
    'PIN_ONCE': ("if pins != 1:", "if pins < 1:"),
    'PRECACHE_OFF': ("fails.append('PRECACHE_OFF')", "pass"),
    'NO_MARKER': ("fails.append('NO_MARKER')", "pass"),
    'ROWS_min': ("rows < MIN_ROWS or ", ""),
    'ROWS_missing': ("or missing:", "or False:"),
    'ARM_A_look': ("(tot['cspfree_hit'] or tot['cspfree_look'])", "tot['cspfree_hit']"),
    'ARM_B_bad': ("(tot['cspfree_hit'] <= 0 or tot['cspfree_bad'])", "tot['cspfree_hit'] <= 0"),
    'ARM_B': ("fails.append('ARM_B_ARMED')", "pass"),
    'IDENTITY': ("errors.append('IDENTITY')", "pass"),
    'ORDER': ("errors.append('ORDER')", "pass"),
    'DRAFT': ("errors.append('DRAFT')", "pass"),
    'SEAL': ("errors.append('SEAL')", "pass"),
    'SLACK': ("elif sb <= sa + SLACK:", "elif sb <= sa + SLACK + 1:"),
    'POWER': ("elif sa == 0:", "elif False:"),
    'S_wait': ("s=tot['cs_sync_new'] + tot['cs_sync_wait']", "s=tot['cs_sync_new']"),
}
alive = []
for name, (a, b) in MUTANTS.items():
    assert src.count(a) == 1, name
    m = Path('C:/kyty/s106_stage/mut_ent109b_%s.py' % name)
    m.write_bytes(src.replace(a, b).encode('utf-8'))
    r = subprocess.run([sys.executable, 'C:/kyty/s106_stage/test_ent109b.py', str(m)], capture_output=True, text=True)
    killed = 'FIXTURE FAILURES' in r.stdout
    fails = [l.split()[0] for l in r.stdout.splitlines() if l.endswith('FAIL')]
    print('%-14s %s %s' % (name, 'killed' if killed else 'ALIVE', fails))
    if not killed:
        alive.append(name)
    m.unlink()
print('ALL KILLED' if not alive else 'ALIVE: %s' % alive)
