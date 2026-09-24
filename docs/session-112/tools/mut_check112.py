"""Session 112: mutants of check112.py - each must be killed by test_check112.py."""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC = (STAGE / 'check112.py').read_text(encoding='utf-8')
MUTANTS = [
    ('frames', 'MIN_FRAMES = 3000', 'MIN_FRAMES = 2999'),
    ('rows', 'MIN_ROWS = 1000', 'MIN_ROWS = 999'),
    ('pin_count', 'pins == 1 and pin1 == 1', 'pin1 >= 1'),
    ('pin_mode', "pin1 += int(line.startswith(b'GpuClockPin: mode 1'))", 'pin1 += 1'),
    ('pin_env', "env.get('KYTY_GPU_CLOCK_PIN') == '1' and ", ''),
    ('rec', "recorded=bool(env.get('KYTY_REC')),", 'recorded=True,'),
    ('sched', "no_schedule='KYTY_GATE_SCHEDULE' not in env,", 'no_schedule=True,'),
    ('ckpt', "no_checkpoints='KYTY_GPU_CHECKPOINTS' not in env,", 'no_checkpoints=True,'),
    ('att_len', 'len(atts) == 1 and ', ''),
    ('def_daslot', "' daslot=' not in gates and ", ''),
    ('def_daguard', "' daguard=' not in gates and ", ''),
    ('def_cspfree', " and ' cspfree=' not in gates,", ','),
    ('glitch', "int(mg.group(1)) == 0", "int(mg.group(1)) <= 1"),
    ('missing', 'rows >= MIN_ROWS and missing == 0', 'rows >= MIN_ROWS'),
    ('free', "tot['da_q_free'] > 0 and ", ''),
    ('noguard', " and tot['da_q_noguard'] == 0,", ','),
    ('slot_bad', "slot_no_bad=tot['da_slot_bad'] == 0,", 'slot_no_bad=True,'),
    ('hit', "tot['cspfree_hit'] > 0 and ", ''),
    ('free_bad', " and tot['cspfree_bad'] == 0,", ','),
    ('guard', "guard=tot['cs_sync_new'] == 0,", 'guard=True,'),
    ('stdout', "    if so.is_file():", "    if False:"),
    ('stable', 'int(m.group(1)) >= stable', 'int(m.group(1)) >= 0'),
    ('marker_fatal', "b'fatal', ", ''),
    ('installed', 'installed_now=installed_sha == BUILD_SHA,', 'installed_now=True,'),
]
killed = 0
for name, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print('%-14s ANCHOR x%d' % (name, SRC.count(old)))
        continue
    path = STAGE / ('mut_check112_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, str(STAGE / 'test_check112.py'), str(path)], capture_output=True, text=True)
    killed += r.returncode != 0
    print('%-14s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))
