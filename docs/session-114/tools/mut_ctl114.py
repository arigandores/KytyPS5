"""Session 114: mutants of ctl114.py - each must be killed by test_ctl114.py.  Run through mutlib v2 (the frozen copy
docs/session-113/mutlib/v2/mutlib.py) --control --no-memo on the SEALED copy."""
import subprocess
import sys
from pathlib import Path

SRC = Path('C:/kyty/s114/ctl114.py').read_text(encoding='utf-8')
MUTANTS = [
    ('freeze_up', 'FREEZE_US = 2500000', 'FREEZE_US = 2500001'),
    ('freeze_down', 'FREEZE_US = 2500000', 'FREEZE_US = 2499999'),
    ('calm_up', 'CALM_US = 500000', 'CALM_US = 500001'),
    ('calm_down', 'CALM_US = 500000', 'CALM_US = 499999'),
    ('window_2', 'WINDOW = 3', 'WINDOW = 2'),
    ('window_4', 'WINDOW = 3', 'WINDOW = 4'),
    ('rows_down', 'MIN_ROWS = 1000', 'MIN_ROWS = 999'),
    ('rows_up', 'MIN_ROWS = 1000', 'MIN_ROWS = 1001'),
    ('hold', '0.95 * HOLD_S', '0.9 * HOLD_S'),
    ('gpu_util', 'MAX_GPU_UTIL = 10.0', 'MAX_GPU_UTIL = 10.2'),
    ('stall_frame', 'STALL_FRAME = 3000', 'STALL_FRAME = 1'),
    ('stall_env', "STALL_ENV = '3000:3000'", "STALL_ENV = '3000:2000'"),
    ('binary_off', "if meta.get('binary_sha256') != BINARY_SHA:", 'if False:'),
    ('prereg_off', "if pre.get('sha256') != PRED_SHA or pre.get('bytes') != PRED_BYTES:", 'if False:'),
    ('pin_env_off', "if env.get('KYTY_GPU_CLOCK_PIN') != '1':", 'if False:'),
    ('stall_env_off', "if env.get('KYTY_MAIN_STALL_TEST') != STALL_ENV:", 'if False:'),
    ('forbid_sched', "FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', ", 'FORBIDDEN_ENV = ('),
    ('forbid_ckpt', "'KYTY_GPU_CHECKPOINTS', 'KYTY_REC'", "'KYTY_REC'"),
    ('forbid_rec', "'KYTY_REC', 'KYTY_PIPELINE_PRECACHE',", "'KYTY_PIPELINE_PRECACHE',"),
    ('forbid_precache', "'KYTY_PIPELINE_PRECACHE',\n", "\n"),
    ('forbid_shift', "'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB', 'KYTY_TITLE_ASYNC')", "'KYTY_TITLE_ASYNC')"),
    ('forbid_title', ", 'KYTY_TITLE_ASYNC')", ')'),
    ('gates_value', "gates.endswith(' titleasync=%d' % ASYNC[tag])", "gates.endswith(' titleasync=%d' % 0)"),
    ('gates_count', " or gates.count(' titleasync=') != 1:", ':'),
    ('async_swapped', "ASYNC = {'ctl114a': 0, 'ctl114b': 1}", "ASYNC = {'ctl114a': 1, 'ctl114b': 0}"),
    ('att_len', 'if len(att) != 1 or len(ok_att) != 1 or ', 'if len(ok_att) != 1 or '),
    ('att_ok', 'if len(att) != 1 or len(ok_att) != 1 or ', 'if len(att) != 1 or '),
    ('pre_run_missing_ok', "if not isinstance(pr.get('gpu_util_median'), (int, float)) or ",
     "if isinstance(pr.get('gpu_util_median'), (int, float)) and "),
    ('pin_count', 'if pins != 1 or pin1 != 1:', 'if pin1 < 1:'),
    ('pin_mode', "pin1 += int(line.startswith(b'GpuClockPin: mode 1'))", 'pin1 += 1'),
    ('marker_off', '    if markers:\n', '    if False:\n'),
    ('marker_fatal', "b'abort()', b'fatal', ", "b'abort()', "),
    ('marker_lost', "b'errordevicelost', ", ''),
    ('marker_hang', "MARKERS = (b'gpuhangabort', ", 'MARKERS = ('),
    ('marker_slow_added', "b'--- error ---', b'asyncpipelines: skipped draw')",
     "b'--- error ---', b'asyncpipelines: skipped draw', b'gpuwaitslow')"),
    ('stdout_off', '    if so.is_file():', '    if False:'),
    ('rows_off', 'if rows < MIN_ROWS:', 'if False:'),
    ('trigger_count', 'if triggers != 1 or queued != 1:', 'if triggers < 1 or queued < 1:'),
    ('trigger_only', 'if triggers != 1 or queued != 1:', 'if queued != 1:'),
    ('queued_only', 'if triggers != 1 or queued != 1:', 'if triggers != 1:'),
    ('stall_rows_off', 'if len(window) < WINDOW:', 'if False:'),
    ('window_any', 'if after_queued and len(window) < WINDOW:', 'if len(window) < WINDOW:'),
    ('queued_flag_off', '                after_queued = True\n', '                pass\n'),
    ('wait_any_frame', 'stall_waits = [us for us, frame in waits if frame == STALL_FRAME]',
     'stall_waits = [us for us, frame in waits]'),
    ('late_off', '                lates.append(int(m.group(1)))', '                pass'),
    ('slow_off', '                slow += 1', '                pass'),
    ('a_froze_gt', "a_froze=a['max_dt'] >= FREEZE_US", "a_froze=a['max_dt'] > FREEZE_US"),
    ('a_froze_off', "a_froze=a['max_dt'] >= FREEZE_US", 'a_froze=True'),
    ('a_wait_gt', "a_waited_main=a['main_wait_max_us'] >= FREEZE_US", "a_waited_main=a['main_wait_max_us'] > FREEZE_US"),
    ('a_wait_off', "a_waited_main=a['main_wait_max_us'] >= FREEZE_US", 'a_waited_main=True'),
    ('b_calm_lt', "b_calm=b['max_dt'] <= CALM_US", "b_calm=b['max_dt'] < CALM_US"),
    ('b_calm_off', "b_calm=b['max_dt'] <= CALM_US", 'b_calm=True'),
    ('b_slow_off', "b_no_slow=b['gpuwaitslow'] == 0", 'b_no_slow=True'),
    ('b_slept_gt', "b_main_slept=b['main_late_max_us'] >= FREEZE_US", "b_main_slept=b['main_late_max_us'] > FREEZE_US"),
    ('b_slept_off', "b_main_slept=b['main_late_max_us'] >= FREEZE_US", 'b_main_slept=True'),
    ('verdict_any', "res['verdict'] = 'PASS' if all(checks.values()) else 'FAIL'",
     "res['verdict'] = 'PASS' if any(checks.values()) else 'FAIL'"),
    ('admission_run_off', "if errors or any(r['errors'] for r in runs.values()):", 'if errors:'),
    ('identity_off', 'if installed_sha != BINARY_SHA:', 'if False:'),
    ('draft_off', "    if PRED_SHA is None or PRED_BYTES is None:\n        errors.append('DRAFT')\n    elif ",
     "    if "),
]
killed = 0
for name, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print('%-18s ANCHOR x%d' % (name, SRC.count(old)))
        continue
    path = Path('C:/kyty/s106_stage/mut_ctl114_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, 'C:/kyty/s114/test_ctl114.py', str(path)], capture_output=True, text=True)
    killed += r.returncode != 0
    print('%-18s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))
