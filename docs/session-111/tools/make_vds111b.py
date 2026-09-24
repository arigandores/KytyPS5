"""Session 111: vds111b.py / test_vds111b.py from vds111.py / test_vds111.py (ROADMAP §0.1 "СЕССИЯ 111" item 4): the
gate file replaces the base's `smemocheck=0` IN PLACE (the loader takes the first assignment) and appends ` daslot=2`;
the GATES term follows that form.  Byte-reproducible."""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')


def derive(src, dst, pairs):
    s = (STAGE / src).read_bytes().decode('utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (src, a[:70], s.count(a))
        s = s.replace(a, b)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('vds111.py', 'vds111b.py', [
    ('"""Session 111, pred/02_vds111.md: the verify run', '"""Session 111, pred/02b_vds111b.md (from vds111.py by make_vds111b.py): the verify run'),
    ("    python C:/kyty/s111/vds111.py", "    python C:/kyty/s111/vds111b.py"),
    ("TAG = 'vds111'", "TAG = 'vds111b'"),
    ("PRED = 'C:/kyty/s111/pred/02_vds111.md'", "PRED = 'C:/kyty/s111/pred/02b_vds111b.md'"),
    ("TAIL = ' daslot=2 smemocheck=1'", "TAIL = ' daslot=2'  # smemocheck=1 replaces the base's smemocheck=0 in place"),
    ("    if not gates.endswith(TAIL) or gates.count(' daslot=') != 1 or gates.count(' smemocheck=') != 1:",
     "    if (not gates.endswith(TAIL) or gates.count(' daslot=') != 1 or gates.count(' smemocheck=') != 1\n"
     "            or ' smemocheck=1 ' not in gates + ' '):"),
])
derive('test_vds111.py', 'test_vds111b.py', [
    ('"""Session 111: fixtures for vds111.py', '"""Session 111: fixtures for vds111b.py (from test_vds111.py by make_vds111b.py)'),
    ("BASE = Path('C:/kyty/s106_stage/fx_vds111')", "BASE = Path('C:/kyty/s106_stage/fx_vds111b')"),
    ("spec = importlib.util.spec_from_file_location('vds111', SRC)", "spec = importlib.util.spec_from_file_location('vds111b', SRC)"),
    ("seal.write_bytes(b'fixture seal 111 vds')", "seal.write_bytes(b'fixture seal 111 vdsb')"),
    ("GATES = 'dawalk=1 dabatch=8 fslean=0'", "GATES = 'dawalk=1 smemocheck=1 dabatch=8 fslean=0'\nGATES0 = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'"),
    ("""    ('GATES_missing', dict(gates=GATES), 'NOT_ADMITTED', ['GATES']),
    ('GATES_no_check', dict(gates=GATES + ' daslot=2'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_mode1', dict(gates=GATES + ' daslot=1 smemocheck=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_twice', dict(gates=GATES + ' daslot=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),
    ('GATES_order', dict(gates=GATES + ' smemocheck=1 daslot=2'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_chk_twice', dict(gates=GATES + ' smemocheck=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),""",
     """    ('GATES_missing', dict(gates=GATES), 'NOT_ADMITTED', ['GATES']),
    ('GATES_check_off', dict(gates=GATES0 + ' daslot=2'), 'NOT_ADMITTED', ['GATES']),          # the vds111 defect
    ('GATES_appended', dict(gates=GATES0 + ' daslot=2 smemocheck=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_mode1', dict(gates=GATES + ' daslot=1'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_twice', dict(gates=GATES + ' daslot=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),
    ('GATES_order', dict(gates='dawalk=1 smemocheck=1 daslot=2 dabatch=8 fslean=0'), 'NOT_ADMITTED', ['GATES']),
    ('GATES_chk_twice', dict(gates=GATES + ' smemocheck=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),
    ('GATES_chk_none', dict(gates='dawalk=1 dabatch=8 fslean=0' + mod.TAIL), 'NOT_ADMITTED', ['GATES']),"""),
])
