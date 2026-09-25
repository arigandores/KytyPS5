"""Session 114: mutants of bootctl114.py - each must be killed by test_bootctl114.py; run through mutlib v2 (frozen copy)
--control --no-memo on the sealed copy."""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
SRC = Path('C:/kyty/s114/bootctl114.py').read_text(encoding='utf-8')
MUTANTS = [
    ('binary', "binary=meta.get('binary_sha256') == BUILD_SHA,", 'binary=True,'),
    ('hold_env', "hold_env=env.get('KYTY_PREPARE_HOLD_MS') == '10000',", 'hold_env=True,'),
    ('hold_env_any', "env.get('KYTY_PREPARE_HOLD_MS') == '10000'", "'KYTY_PREPARE_HOLD_MS' in env"),
    ('pinned', "pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1',", 'pinned=True,'),
    ('sched', "no_schedule='KYTY_GATE_SCHEDULE' not in env,", 'no_schedule=True,'),
    ('ckpt', "no_checkpoints='KYTY_GPU_CHECKPOINTS' not in env,", 'no_checkpoints=True,'),
    ('knob', '                 knob=knob)', '                 knob=True)'),
    ('knob_c_env', "env.get('KYTY_TITLE_ASYNC') == '0' and ", ''),
    ('knob_c_gate', " and ' titleasync=0 ' in gates", ''),
    ('knob_c_gate_sp', "' titleasync=0 ' in gates", "' titleasync=0' in gates"),
    ('knob_b_env', "'KYTY_TITLE_ASYNC' not in env and ", ''),
    ('knob_b_gate', " and ' titleasync=' not in gates", ''),
    ('knob_branch', "if tag.endswith('c'):", "if tag.endswith('b'):"),
    ('holds_one', 'len(holds) == 1 and ', 'len(holds) >= 1 and '),
    ('holds_any', 'len(holds) == 1 and ', ''),
    ('after_hold', '                if holds:', '                if True:'),
    ('fatal_flag', ' and fatal_after_hold and ', ' and '),
    ('waits', ' and waits == 0', ''),
    ('hold_line', "HOLD_LINE = b'PrepareHold: ms=10000'", "HOLD_LINE = b'PrepareHold: ms='"),
    ('fatal_site', "FATAL_SITE = b'commandRecorder.cpp:326'", "FATAL_SITE = b'commandRecorder.cpp'"),
    ('fatal_prefix', 'if FATAL_SITE in line:', 'if line.startswith(FATAL_SITE):'),
    ('setup_all', "if not all(t['setup_ok'] for t in res['tags'].values()):", 'if False:'),
    ('setup_any', "if not all(t['setup_ok'] for t in res['tags'].values()):",
     "if not any(t['setup_ok'] for t in res['tags'].values()):"),
    ('same_any', "elif all(t['outcome'] == 'SAME_FATAL' for t in res['tags'].values()):",
     "elif any(t['outcome'] == 'SAME_FATAL' for t in res['tags'].values()):"),
    ('tags', "TAGS = ('boot114b', 'boot114c')", "TAGS = ('boot114b', 'boot114b')"),
]
killed = 0
for name, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print('%-14s ANCHOR x%d' % (name, SRC.count(old)))
        continue
    path = STAGE / ('mut_bootctl114_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, 'C:/kyty/s114/test_bootctl114.py', str(path)], capture_output=True, text=True)
    killed += r.returncode != 0
    print('%-14s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))
