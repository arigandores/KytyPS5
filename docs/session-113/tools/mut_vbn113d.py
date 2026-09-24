"""Session 113: mutants of vbn113d.py (from mut_vbn113c.py by make_vbn113d.py) - each must be killed by test_vbn113d.py.
Run through mutlib on the SEALED copy (items 7, 13, 14).
"""
import hashlib
import subprocess
import sys
from pathlib import Path

TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113d.py')
TEST = Path('C:/kyty/s106_stage/test_vbn113d.py')
WORK = Path('C:/kyty/s106_stage')
SRC = TARGET.read_text(encoding='utf-8')
print('target %s sha256 %s' % (TARGET, hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
MUTANTS = [
    ('rows', 'MIN_ROWS = 5000', 'MIN_ROWS = 4999'),
    ('regime_up', 'REGIME_OLD = 500 ', 'REGIME_OLD = 501 '),
    ('regime_down', 'REGIME_OLD = 500 ', 'REGIME_OLD = 499 '),
    ('would_down', 'MIN_WOULD = 1000 ', 'MIN_WOULD = 999 '),
    ('would_up', 'MIN_WOULD = 1000 ', 'MIN_WOULD = 1001 '),
    ('gpu_util_up', 'MAX_GPU_UTIL = 10.0 ', 'MAX_GPU_UTIL = 10.2 '),
    ('gpu_util_down', 'MAX_GPU_UTIL = 10.0 ', 'MAX_GPU_UTIL = 9.9 '),
    ('pre_run_missing_ok', "if not isinstance(pr.get('gpu_util_median'), (int, float)) or ",
     "if isinstance(pr.get('gpu_util_median'), (int, float)) and "),
    ('hold', '0.95 * HOLD_S', '0.9 * HOLD_S'),
    ('tail', "TAIL = ' bdanarrow=2'", "TAIL = ' bdanarrow=1'"),
    ('gates_count', " or gates.count(' bdanarrow=') != 1", ''),
    ('tags', "TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')", "TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j', 'vbn113k')"),
    ('tags_drop', "TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')", "TAGS = ('vbn113g', 'vbn113h', 'vbn113i')"),
    ('race_blocks', "    elif bad == 0:\n        out['verdict'] = 'GO'", "    elif bad == 0 and tot['bda_nrace'] == 0:\n        out['verdict'] = 'GO'"),
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
    ('bad_race', "bad = tot['bda_nmiss'] + tot['bda_nxthr']", "bad = tot['bda_nmiss'] + tot['bda_nxthr'] + tot['bda_nrace']"),
    ('investigate', "    elif tot['bda_nmiss'] == 0:\n        out['verdict'] = 'INVESTIGATE'\n", ''),
    ('stable', 'if m and int(m.group(1)) >= stable:', 'if m:'),
    ('scene_stable', 'if int(m.group(1)) >= stable:\n                    for k in scene:',
     'if True:\n                    for k in scene:'),
    ('missing', 'if rows < MIN_ROWS or missing:', 'if rows < MIN_ROWS:'),
    ('streams_gap', "any(b - a != 1 for a, b in zip(xns, xns[1:])) or ", ''),
    ('streams_main', " or abs(rows - main_rows) > 1):", "):"),
    ('streams_tol', "abs(rows - main_rows) > 1", "abs(rows - main_rows) > 2"),
    ('att_len', 'if len(att) != 1 or len(ok_att) != 1 or ', 'if len(ok_att) != 1 or '),
    ('b2', "lambda r: r['level']['bda_scan'], 800, 1400)", "lambda r: r['level']['bda_scan'], 800, 1500)"),
    ('b3', "lambda r: r['level']['bda_ginv_reg'], 0.5, 3.0)", "lambda r: r['per_row']['bda_ginv_reg'], 0.5, 3.0)"),
    ('b4', "lambda r: r['level']['bda_nwould'], 800, 1400)", "lambda r: r['level']['bda_nwould'], 700, 1400)"),
    ('b5', "lambda r: r['level']['bgc_evict'], 0.5, 3.0)", "lambda r: r['per_row']['bgc_evict'], 0.5, 3.0)"),
    ('b6', "lambda r: r['total']['bda_nrace'], None, 40)", "lambda r: r['total']['bda_nrace'], None, 41)"),
    ('evaluable', "elif not regime_old:", "elif False:"),
]
killed = 0
for name, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print('%-18s ANCHOR x%d' % (name, SRC.count(old)))
        continue
    path = WORK / ('mut_vbn113d_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, str(TEST), str(path)], capture_output=True, text=True)
    killed += r.returncode != 0
    print('%-18s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))
