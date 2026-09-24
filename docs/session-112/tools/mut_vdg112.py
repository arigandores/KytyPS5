"""Session 112: mutants of vdg112.py - each must be killed by test_vdg112.py.
    python mut_vdg112.py
"""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC = (STAGE / 'vdg112.py').read_text(encoding='utf-8')
MUTANTS = [
    ('rows_min', 'MIN_ROWS = 5000', 'MIN_ROWS = 4999'),
    ('blocks_min', 'MIN_BLOCKS = 40 ', 'MIN_BLOCKS = 39 '),
    ('arm_rows_min', 'MIN_MAIN_ROWS = 1000', 'MIN_MAIN_ROWS = 0'),
    ('ratio', 'CHECK_RATIO = 0.99 ', 'CHECK_RATIO = 0.98 '),
    ('main_lo', 'MAIN = (10, 89)', 'MAIN = (9, 89)'),
    ('main_hi', 'MAIN = (10, 89)', 'MAIN = (10, 90)'),
    ('main_lo2', 'MAIN = (10, 89)', 'MAIN = (11, 89)'),
    ('hold', '0.95 * HOLD_S', '0.9 * HOLD_S'),
    ('pin_once', 'if pins != 1 or pin1 != 1:', 'if pin1 < 1:'),
    ('pin_mode', "pin1 += int(line.startswith(b'GpuClockPin: mode 1'))", "pin1 += 1"),
    ('marker_stdout', "    markers += scan_markers(Path(root) / ('stdout_%s.txt' % TAG))\n", ''),
    ('marker_fatal', "b'fatal', ", ''),
    ('marker_skipped', "           b'asyncpipelines: skipped draw')", "           b'--none--')"),
    ('env_ckpt', "FORBIDDEN_ENV = ('KYTY_GPU_CHECKPOINTS', ", "FORBIDDEN_ENV = ("),
    ('env_precache', ", 'KYTY_PIPELINE_PRECACHE')", ")"),
    ('sched_abba', " or env.get('KYTY_GATE_SCHEDULE_ABBA') != '1'", ''),
    ('gates_daslot', "or ' daslot=' in gates\n", "or False\n"),
    ('gates_daguard', "            or ' daguard=' in gates):", "            or False):"),
    ('gates_count', "gates.count(' smemocheck=') != 1 or ", ''),
    ('arm_text', "or g.group(7).decode('utf-8', 'replace').strip() != ARM_TEXT[arm]", ''),
    ('arm_abba', " or g.group(6) != b'1'", ''),
    ('arm_period', " or int(g.group(5)) != PERIOD", ''),
    ('arm_arms', " or g.group(2) != b'2'", ''),
    ('armed0_dark', " or sum(per[0]['da_q_free']) != 0", ''),
    ('armed1_dark', " or sum(per[1]['da_q_noguard']) != 0", ''),
    ('armed0_level', "if level[0]['da_q_noguard'] < 1", "if level[0]['da_q_noguard'] < 0"),
    ('armed1_level', "if level[1]['da_q_free'] < 1", "if level[1]['da_q_free'] < 0"),
    ('bad_slot', "bad = tot['da_slot_bad'] + ", 'bad = '),
    ('bad_chk', " + tot['da_chk_bad'] + sum(mismatch.values())", ' + sum(mismatch.values())'),
    ('bad_lines', " + sum(mismatch.values())\n", '\n'),
    ('defaults_bad', " or tot['cspfree_bad'] != 0", ''),
    ('missing', 'if rows < MIN_ROWS or missing:', 'if rows < MIN_ROWS:'),
    ('attempts_two', 'len(att) != 1 or ', ''),
    ('pre_seen', "        if not scheduled or arm == 1", "        if not scheduled or arm == 1"),  # placeholder, removed below
    ('scheduled_only', "                if scheduled:\n", "                if True:\n"),
    ('d4_band', "lambda r: r['total']['da_guard_yield'], None, 100)", "lambda r: r['total']['da_guard_yield'], None, 101)"),
    ('d2_value', "lambda r: r['level'][1]['da_q_free'], 800, 1400)", "lambda r: r['level'][0]['da_q_free'], 800, 1400)"),
]
MUTANTS = [m for m in MUTANTS if m[0] != 'pre_seen']
killed = 0
for name, old, new in MUTANTS:
    n = SRC.count(old)
    if n != 1:
        print('%-16s ANCHOR x%d' % (name, n))
        continue
    path = STAGE / ('mut_vdg112_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, str(STAGE / 'test_vdg112.py'), str(path)], capture_output=True, text=True)
    dead = r.returncode != 0
    killed += dead
    print('%-16s %s' % (name, 'killed' if dead else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))
