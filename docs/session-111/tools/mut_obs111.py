"""Session 111: single-term mutants of obs111.py; every one must be killed by test_obs111.py.  Each mutant replaces
exactly one anchored text (asserted to occur once); it is killed when the fixture run does not end in 'ALL OK'
('fixtures' = a fixture assertion failed, 'crash' = the scorer raised).  Mutants run 8 at a time, each with its own
fixture directory (<dir>/fx/<mutant stem>), all removed at the end.
    python mut_obs111.py [<obs111.py> [<test_obs111.py>]]
"""
import concurrent.futures
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCORER = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'obs111.py'
TEST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'test_obs111.py'
MUT_DIR = HERE / 'mutants'
src = SCORER.read_bytes().decode('utf-8')

PLK = "if [t for t in tokens if t.startswith('plkstat=')] != ['plkstat=1']:"
KNOBS = "DEFAULT_KNOBS = ('cspfree=', 'cspmemo=', 'cspfam=')"
ROWS = "if nrow < MIN_ROWS or missing:"
ARMED = "if not (tot['pl_cont_n'] > 0 or tot['pl_wq_hold_n'] > 0):"
RULE = "elif r['tag1_us'] >= RULE_US:"
STEADY = "steady = [d for n, d in rows if n >= START]"
US = "return x / nrow / 1000.0 if nrow else None"
SPIN = "spin_share=tot['pl_cont_cpu_ns'] / wall if wall else None,"
M = {
    # the seal, identity and inputs
    'DRAFT': ("errors.append('DRAFT')", "pass"),
    'DRAFT_bytes_pin': ("if PRED_SHA is None or PRED_BYTES is None:", "if PRED_SHA is None:"),
    'SEAL': ("errors.append('SEAL')", "pass"),
    'SEAL_sha': ("sha_file(PRED) != PRED_SHA or ", ""),
    'SEAL_size': (" or Path(PRED).stat().st_size != PRED_BYTES:", ":"),
    'IDENTITY': ("errors.append('IDENTITY')", "pass"),
    'INPUTS_log': ("if meta_p.is_file() and log_p.is_file():", "if meta_p.is_file():"),
    'INPUTS_json': ("        except ValueError:", "        except KeyError:"),
    'INPUTS_dict': ("if not isinstance(meta, dict):", "if meta is None:"),
    'BINARY': ("errors.append('BINARY')", "pass"),
    'BINARY_const': ("BINARY_SHA = '072861c8", "BINARY_SHA = '172861c8"),
    'PREREG': ("errors.append('PREREG')", "pass"),
    'PREREG_bytes': (" or pre.get('bytes') != PRED_BYTES:", ":"),
    'PREREG_unpinned': ("if PRED_SHA is None or pre.get('sha256')", "if pre.get('sha256')"),
    # environment
    'ENV_PIN': ("errors.append('ENV_PIN')", "pass"),
    'ENV_PIN_present': ("env.get('KYTY_GPU_CLOCK_PIN') != '1'", "'KYTY_GPU_CLOCK_PIN' not in env"),
    'ENV_FORBIDDEN': ("errors.append('ENV_FORBIDDEN')", "pass"),
    'ENV_no_sched': ("FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', ", "FORBIDDEN_ENV = ("),
    'ENV_no_ckpt': ("'KYTY_GPU_CHECKPOINTS', 'KYTY_REC')", "'KYTY_REC')"),
    'ENV_no_rec': (", 'KYTY_REC')", ")"),
    'ENV_truthy': ("if any(k in env for k in FORBIDDEN_ENV):", "if any(env.get(k) for k in FORBIDDEN_ENV):"),
    # gate text
    'GATES_PLKSTAT': ("errors.append('GATES_PLKSTAT')", "pass"),
    'GATES_plk_atleast': (PLK, "if 'plkstat=1' not in tokens:"),
    'GATES_plk_substring': (PLK, "if (' ' + (meta.get('gates') or '') + ' ').count(' plkstat=1') != 1:"),
    'GATES_DEFAULTS': ("errors.append('GATES_DEFAULTS')", "pass"),
    'GATES_no_cspfree': (KNOBS, "DEFAULT_KNOBS = ('cspmemo=', 'cspfam=')"),
    'GATES_no_cspmemo': (KNOBS, "DEFAULT_KNOBS = ('cspfree=', 'cspfam=')"),
    'GATES_no_cspfam': (KNOBS, "DEFAULT_KNOBS = ('cspfree=', 'cspmemo=')"),
    # the attempt
    'ATTEMPT': ("errors.append('ATTEMPT')", "pass"),
    'ATT_n': ("if (len(att) != 1 or ", "if (len(att) < 1 or "),
    'ATT_outcome': ("att[0].get('outcome') != 'ok' or ", ""),
    'ATT_exit': ("att[0].get('hold_exit') is not None", "False"),
    'ATT_exit_truthy': ("att[0].get('hold_exit') is not None", "att[0].get('hold_exit')"),
    'ATT_hold': ("or (att[0].get('hold_s') or 0) < MIN_HOLD_S", "or False"),
    'ATT_hold_const': ("MIN_HOLD_S = 285.0", "MIN_HOLD_S = 280.0"),
    'ATT_hold_edge': ("or 0) < MIN_HOLD_S", "or 0) <= MIN_HOLD_S"),
    # the clock pin line
    'PIN_ONCE': ("errors.append('PIN_ONCE')", "pass"),
    'PIN_count_off': ("if pins != 1 or pin1 != 1:", "if pin1 != 1:"),
    'PIN_mode_off': ("if pins != 1 or pin1 != 1:", "if pins != 1:"),
    'PIN_prefix': ("pin1 += int(m is not None and m.group(1) == b'1')",
                   "pin1 += int(line.startswith(b'GpuClockPin: mode 1'))"),
    # failure markers
    'NO_MARKER': ("errors.append('NO_MARKER')", "pass"),
    'MARK_hang': ("(b'gpuhangabort', ", "("),
    'MARK_fatal': ("b'abort()', b'fatal', ", "b'abort()', "),
    'MARK_error': (" b'--- error ---',", ""),
    'MARK_skipped': ("b'asyncpipelines: skipped draw')", ")"),
    'MARK_case': ("low = line.lower()", "low = line"),
    'MARK_stdout': ("    if stdout_p.is_file():", "    if False:"),
    # rows
    'ROWS': ("errors.append('ROWS')", "pass"),
    'ROWS_min': (ROWS, "if nrow < 4000 or missing:"),
    'ROWS_edge': (ROWS, "if nrow <= MIN_ROWS or missing:"),
    'ROWS_missing_off': (ROWS, "if nrow < MIN_ROWS:"),
    'ROWS_count_all': (ROWS, "if len(rows) < MIN_ROWS or missing:"),
    'ROWS_missing_all': ("missing = sum(1 for d in steady if", "missing = sum(1 for n, d in rows if"),
    # arming
    'PLKSTAT_ARMED': ("errors.append('PLKSTAT_ARMED')", "pass"),
    'PLK_cont_only': (ARMED, "if not tot['pl_cont_n'] > 0:"),
    'PLK_wq_only': (ARMED, "if not tot['pl_wq_hold_n'] > 0:"),
    'PLK_all_rows': (ARMED, "if not (sum(d.get('pl_cont_n', 0) for n, d in rows) > 0 "
                            "or sum(d.get('pl_wq_hold_n', 0) for n, d in rows) > 0):"),
    'CSPFREE_ARMED': ("errors.append('CSPFREE_ARMED')", "pass"),
    'FREE_all_rows': ("if tot['cspfree_hit'] <= 0:", "if sum(d.get('cspfree_hit', 0) for n, d in rows) <= 0:"),
    'CSPFREE_BAD': ("errors.append('CSPFREE_BAD')", "pass"),
    'FREE_bad_steady': ("bad_all = sum(d.get('cspfree_bad', 0) for n, d in rows)",
                        "bad_all = sum(d.get('cspfree_bad', 0) for d in steady)"),
    # the rule and its edge
    'RULE_const_hi': ("RULE_US = 100.0", "RULE_US = 100.001"),
    'RULE_const_lo': ("RULE_US = 100.0", "RULE_US = 99.9999"),
    'RULE_edge': (RULE, "elif r['tag1_us'] > RULE_US:"),
    'RULE_hi': (RULE, "elif r['tag1_us'] >= RULE_US + 0.001:"),
    'RULE_lo': (RULE, "elif r['tag1_us'] >= RULE_US - 0.0001:"),
    'RULE_on_wall': (RULE, "elif r['cont_wall_us'] >= RULE_US:"),
    'RULE_on_tag2': (RULE, "elif r['tag2_us'] >= RULE_US:"),
    # tag mapping
    'TAG1_is_h2': ("tag1_us=us(tot['pl_cont_h1_ns']),", "tag1_us=us(tot['pl_cont_h2_ns']),"),
    'TAG2_is_h3': ("tag2_us=us(tot['pl_cont_h2_ns']),", "tag2_us=us(tot['pl_cont_h3_ns']),"),
    'TAG03_is_h02': ("tag03_us=us(tot['pl_cont_h0_ns'] + tot['pl_cont_h3_ns']),",
                     "tag03_us=us(tot['pl_cont_h0_ns'] + tot['pl_cont_h2_ns']),"),
    'TAG1_share_h2': ("tag1_share=tot['pl_cont_h1_ns'] / wall", "tag1_share=tot['pl_cont_h2_ns'] / wall"),
    'TAG1_n_h2': ("'1': per(tot['pl_cont_h1_n'])", "'1': per(tot['pl_cont_h2_n'])"),
    # the window (steady filter)
    'STEADY_gt': (STEADY, "steady = [d for n, d in rows if n > START]"),
    'STEADY_2099': (STEADY, "steady = [d for n, d in rows if n >= START - 1]"),
    'STEADY_off': (STEADY, "steady = [d for n, d in rows]"),
    'START_const': ("START = 2100", "START = 1800"),
    # per-flip division and ratios
    'DIV_us_all_rows': (US, "return x / len(rows) / 1000.0 if nrow else None"),
    'DIV_us_scale': (US, "return x / nrow / 1000000.0 if nrow else None"),
    'DIV_per_all_rows': ("return x / nrow if nrow else None", "return x / len(rows) if nrow else None"),
    'SPIN_inverted': (SPIN, "spin_share=wall / tot['pl_cont_cpu_ns'] if wall else None,"),
    'SPIN_mean_of_ratios': (SPIN, "spin_share=sum(d['pl_cont_cpu_ns'] / d['pl_cont_wall_ns'] for d in steady) / nrow "
                                  "if wall else None,"),
    'WQ_call_per_flip': ("wq_call_us=tot['pl_wq_hold_ns'] / tot['pl_wq_hold_n'] / 1000.0",
                         "wq_call_us=tot['pl_wq_hold_ns'] / nrow / 1000.0"),
    'WP_uses_n': ("wp_hold_us=us(tot['pl_wp_hold_ns']),", "wp_hold_us=us(tot['pl_wp_hold_n']),"),
    'HIT_is_have': ("cspfree_hit=per(tot['cspfree_hit']),", "cspfree_hit=per(tot['cspf_have']),"),
    # prediction bands (never deciding, but printed)
    'P1_band': ("r['tag2_us'], None, 20.0)", "r['tag2_us'], None, 20.001)"),
    'P2_band': ("r['tag1_share'], 0.85, None)", "r['tag1_share'], 0.8499, None)"),
    'P3_lo': ("r['cont_wall_us'], 150.0, 320.0)", "r['cont_wall_us'], 149.9999, 320.0)"),
    'P3_hi': ("r['cont_wall_us'], 150.0, 320.0)", "r['cont_wall_us'], 150.0, 320.0001)"),
    'P4_band': ("r['wp_hold_us'], None, 20.0)", "r['wp_hold_us'], None, 20.001)"),
    'P_lo_strict': ("(lo is None or value >= lo)", "(lo is None or value > lo)"),
}


def run_one(item):
    name, (a, b) = item
    path = MUT_DIR / ('mut_obs111_%s.py' % name)
    path.write_bytes(src.replace(a, b).encode('utf-8'))
    try:
        r = subprocess.run([sys.executable, '-B', str(TEST), str(path)], capture_output=True, text=True, timeout=600)
        lines = r.stdout.strip().splitlines()
        if r.returncode == 0 and lines and lines[-1] == 'ALL OK':
            kind = 'ALIVE'
        elif 'Traceback' in r.stderr:
            kind = 'killed (crash: %s)' % (r.stderr.strip().splitlines() or ['?'])[-1][:60]
        else:
            failed = [ln.split()[0] for ln in lines if ' FAIL ' in ln + ' ' or ln.endswith(' FAIL')]
            kind = 'killed (fixtures: %s)' % ','.join(failed[:6])
    finally:
        path.unlink()
        shutil.rmtree(HERE / 'fx' / path.stem, ignore_errors=True)
    return name, kind


def main():
    for name, (a, b) in M.items():
        assert src.count(a) == 1, (name, a, src.count(a))
        assert a != b, name
    print('scorer %s %s' % (SCORER.name, hashlib.sha256(SCORER.read_bytes()).hexdigest()))
    print('test   %s %s' % (TEST.name, hashlib.sha256(TEST.read_bytes()).hexdigest()))
    r = subprocess.run([sys.executable, '-B', str(TEST), str(SCORER)], capture_output=True, text=True, timeout=600)
    base_ok = r.returncode == 0 and r.stdout.strip().splitlines()[-1] == 'ALL OK'
    print('%-22s %s' % ('(unmutated)', 'ALL OK' if base_ok else 'FIXTURE FAILURES - mutant run meaningless'))
    if not base_ok:
        return 1
    if MUT_DIR.exists():
        shutil.rmtree(MUT_DIR)
    MUT_DIR.mkdir()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            res = dict(ex.map(run_one, M.items()))
    finally:
        shutil.rmtree(MUT_DIR, ignore_errors=True)
        try:
            (HERE / 'fx').rmdir()
        except OSError:
            pass
    alive = [n for n in M if res[n] == 'ALIVE']
    for n in M:
        print('%-22s %s' % (n, res[n]))
    print('mutants %d  %s' % (len(M), 'ALL KILLED' if not alive else 'ALIVE: %s' % alive))
    return 0 if not alive else 1


if __name__ == '__main__':
    sys.exit(main())
