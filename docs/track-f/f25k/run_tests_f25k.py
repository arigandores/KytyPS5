# F25k (HPP-678, ROADMAP s122 item 613(g)(1)): tests of the binary-T worktree build without the game; t2-t4 - form of
# f25d/run_tests_f25d.py (paths f25d -> f25k).
"""Tests of the F25k worktree build (C:/kyty/f287/f25k/wt -> C:/kyty/f287/f25k/build) without the game.

  (t1) log_async_tests: rc 0 and the last line ALL OK (KYTY_FIX_B36: order, wait on overflow, the drain on 7 death paths,
       the negative controls latency_0 and die_kill, =0 / =1 / unset on a fixed sequence).
  (t1b) =0 byte for byte with the OLD code: the reference executable ref/log_async_tests_ref.exe (the same test file built
       on the worktree base 929b6073 before the F25k patch, without KYTY_LOG_ASYNC_TESTS) writes the fixed sequence; its
       sha256 = that of seq0_0.txt (=0) and of seq0_u.txt (unset) of t1; negative control - seq0_1.txt (=1, with the
       "LogAsync:" lines) must differ.
  (t2) diag_b32_tests: rc 0 and ALL OK (KYTY_DIAG_B32 of the 6 picked commits, unchanged by F25k).
  (t3) shader_cfg_tests with all KYTY_* removed: 0 lines 'ShaderCfgTests: failed:', rc 0, the test count = FS8a fu.
  (t4) the SPIR-V of (t3) = FS8a fu byte for byte (F25k does not touch the translator).
Usage: python run_tests_f25k.py. Rule 27: lock and STOP before every process. Prints ALL OK only if t1-t4 hold.
"""
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/f25k/build'
OUT = 'C:/kyty/f287/f25k/tests_out'
REFEXE = 'C:/kyty/f287/f25k/ref/log_async_tests_ref.exe'
REF = 'C:/kyty/f287/fs8a/suite/fu'


def guard():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(5)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}


ok = True
os.makedirs(OUT + '/fu/spv', exist_ok=True)
for f in os.listdir(OUT + '/fu/spv'):
    os.remove(OUT + '/fu/spv/' + f)

guard()
r = subprocess.run([B + '/log_async_tests.exe', OUT], capture_output=True, text=True, env=clean_env(), errors='replace')
open(OUT + '/log_async_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
last = r.stdout.splitlines()[-1] if r.stdout else ''
t1 = r.returncode == 0 and last == 'ALL OK'
print('t1 log_async_tests rc=%d last=%r cases=%s -> %s' % (r.returncode, last,
      re.findall(r'cases=(\d+) failures=(\d+)', r.stdout), 'ok' if t1 else 'FAIL'))
ok &= t1

guard()
ref_txt = OUT + '/seq0_ref.txt'
if os.path.exists(ref_txt):
    os.remove(ref_txt)
r = subprocess.run([REFEXE, '--child', 'seq0', ref_txt], capture_output=True, text=True, env=clean_env())
h_ref = sha(ref_txt) if os.path.exists(ref_txt) else '-'
h0 = sha(OUT + '/seq0_0.txt')
hu = sha(OUT + '/seq0_u.txt')
h1 = sha(OUT + '/seq0_1.txt')
t1b = r.returncode == 0 and h_ref == h0 == hu and h1 != h0
print('t1b =0 vs old code: ref %s =0 %s unset %s; negative control =1 %s differs=%s -> %s' % (
    h_ref[:16], h0[:16], hu[:16], h1[:16], h1 != h0, 'ok' if t1b else 'FAIL'))
ok &= t1b

guard()
r = subprocess.run([B + '/diag_b32_tests.exe'], capture_output=True, text=True, errors='replace')
open(OUT + '/diag_b32_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
t2 = r.returncode == 0 and 'ALL OK' in r.stdout.splitlines()[-1:]
print('t2 diag_b32_tests rc=%d last=%r -> %s' % (r.returncode, r.stdout.splitlines()[-1] if r.stdout else '', 'ok' if t2 else 'FAIL'))
ok &= t2

guard()
env = clean_env()
env['KYTY_TESTS_CONTINUE'] = '1'
env['KYTY_TESTS_VERBOSE'] = '1'
env['KYTY_TESTS_SPV_DIR'] = OUT + '/fu/spv'
r = subprocess.run([B + '/shader_cfg_tests.exe'], capture_output=True, text=True, cwd=B, env=env, errors='replace')
log = r.stdout + r.stderr
open(OUT + '/fu/log.txt', 'w', encoding='utf-8', newline='\n').write(log)
n_tests = len(re.findall(r'^\[test\] ', log, re.M))
n_failed = len(re.findall(r'ShaderCfgTests: failed:', log))
ref_log = open(REF + '/log.txt', encoding='utf-8', errors='replace').read() if os.path.exists(REF + '/log.txt') else ''
ref_tests = len(re.findall(r'^\[test\] ', ref_log, re.M))
t3 = r.returncode == 0 and n_failed == 0 and n_tests > 0 and (ref_tests == 0 or n_tests == ref_tests)
print('t3 shader_cfg_tests rc=%d tests=%d (FS8a fu %d) failed_lines=%d -> %s' % (r.returncode, n_tests, ref_tests, n_failed,
                                                                                  'ok' if t3 else 'FAIL'))
ok &= t3

mine = sorted(os.listdir(OUT + '/fu/spv'))
ref = sorted(os.listdir(REF + '/spv'))
diff = [f for f in sorted(set(mine) | set(ref)) if f not in mine or f not in ref or sha(OUT + '/fu/spv/' + f) != sha(REF + '/spv/' + f)]
agg_m = hashlib.sha256(''.join(sha(OUT + '/fu/spv/' + f) for f in mine).encode()).hexdigest()
agg_r = hashlib.sha256(''.join(sha(REF + '/spv/' + f) for f in ref).encode()).hexdigest()
t4 = len(mine) > 0 and not diff
print('t4 SPIR-V files mine %d ref %d differing %d aggregate %s / %s -> %s' % (len(mine), len(ref), len(diff), agg_m[:8],
                                                                              agg_r[:8], 'ok' if t4 else 'FAIL'))
for f in diff[:20]:
    print('   differs:', f)
ok &= t4
print('ALL OK' if ok else 'FAILED')
