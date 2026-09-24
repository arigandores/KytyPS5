"""Session 113: mutants of vbn113.py - each must be killed by test_vbn113.py."""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC = (STAGE / 'vbn113.py').read_text(encoding='utf-8')
MUTANTS = [
    ('rows', 'MIN_ROWS = 5000', 'MIN_ROWS = 4999'),
    ('regime', 'REGIME_OLD = 500 ', 'REGIME_OLD = 501 '),
    ('regime2', 'REGIME_OLD = 500 ', 'REGIME_OLD = 499 '),
    ('would', 'MIN_WOULD = 1000 ', 'MIN_WOULD = 999 '),
    ('would2', 'MIN_WOULD = 1000 ', 'MIN_WOULD = 1001 '),
    ('hold', '0.95 * HOLD_S', '0.9 * HOLD_S'),
    ('tail', "TAIL = ' bdanarrow=2'", "TAIL = ' bdanarrow=1'"),
    ('gates_count', " or gates.count(' bdanarrow=') != 1", ''),
    ('tags', "TAGS = ('vbn113', 'vbn113b')", "TAGS = ('vbn113', 'vbn113b', 'vbn113c')"),
    ('pin_count', 'if pins != 1 or pin1 != 1:', 'if pin1 < 1:'),
    ('pin_mode', "pin1 += int(line.startswith(b'GpuClockPin: mode 1'))", 'pin1 += 1'),
    ('stdout', "    if so.is_file():", "    if False:"),
    ('marker_fatal', "b'fatal', ", ''),
    ('marker_lost', "b'errordevicelost',", ''),
    ('marker_slow', "b'gpuwaitslow', ", ''),
    ('env_sched', "FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', ", 'FORBIDDEN_ENV = ('),
    ('env_precache', ", 'KYTY_PIPELINE_PRECACHE')", ')'),
    ('armed_ginv', "tot['bda_ginv_reg'] <= 0 or ", ''),
    ('armed_nskip', " or tot['bda_nskip'] != 0", ''),
    ('defaults_slot', "tot['da_q_free'] <= 0 or ", ''),
    ('defaults_bad', " or tot['cspfree_bad'] != 0", ''),
    ('bad_miss', "bad = tot['bda_nmiss'] + tot['bda_nxthr']", "bad = tot['bda_nxthr']"),
    ('bad_xthr', "bad = tot['bda_nmiss'] + tot['bda_nxthr']", "bad = tot['bda_nmiss']"),
    ('stable', 'if m and int(m.group(1)) >= stable:', 'if m:'),
    ('missing', 'if rows < MIN_ROWS or missing:', 'if rows < MIN_ROWS:'),
    ('att_len', 'if len(att) != 1 or len(ok_att) != 1 or ', 'if len(ok_att) != 1 or '),
    ('b2', "lambda r: r['level']['bda_scan'], 800, 1400)", "lambda r: r['level']['bda_scan'], 800, 1500)"),
    ('b3', "lambda r: r['per_row']['bda_ginv_reg'], 0.5, 3.0)", "lambda r: r['per_row']['bda_ginv_reg'], 0.4, 3.0)"),
    ('b4', "lambda r: r['per_row']['bda_nwould'], 800, 1400)", "lambda r: r['per_row']['bda_nwould'], 700, 1400)"),
    ('b5', "lambda r: r['per_row']['bgc_evict'], 0.5, 3.0)", "lambda r: r['per_row']['bgc_evict'], 0.5, 4.0)"),
    ('evaluable', "elif not regime_old:", "elif False:"),
]
killed = 0
for name, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print('%-14s ANCHOR x%d' % (name, SRC.count(old)))
        continue
    path = STAGE / ('mut_vbn113_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, str(STAGE / 'test_vbn113.py'), str(path)], capture_output=True, text=True)
    killed += r.returncode != 0
    print('%-14s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))
