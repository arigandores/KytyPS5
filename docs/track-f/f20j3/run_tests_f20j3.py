# F20j3 (HPP-646, ROADMAP s122 item 574(g)(6)): copy of f20j2/run_tests_f20j2.py, names changed (f20j2 -> f20j3).
# F20j2 (HPP-633, ROADMAP s122 item 552(d)): copy of the F20j run_tests_f20j.py, names changed (f20j -> f20j2).
"""F20j (HPP-629, ROADMAP s122 item 550(z)(4)-(5)): tests of the F20j3 worktree build without the game.

  (t1) diag_b32_tests: rc 0 and the line ALL OK (the core of KYTY_DIAG_B32: partition, I1, I2', I3, window, lines,
       counters).
  (t2) shader_cfg_tests with all KYTY_* removed (form fu of suite_fs8a.py): 0 lines 'ShaderCfgTests: failed:', rc 0,
       the test count = FS8a fu (130).
  (t3) the SPIR-V of (t2) = FS8a fu (C:/kyty/f287/fs8a/suite/fu/spv) byte for byte, every file (the translator is not
       touched; the signature 9177b426 is the FS8 one).
Usage: python run_tests_f20j3.py. Rule 27: lock and STOP before every process. Prints ALL OK only if t1-t3 hold.
"""
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/f20j3/build'
OUT = 'C:/kyty/f287/f20j3/tests_out'
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


ok = True
os.makedirs(OUT + '/fu/spv', exist_ok=True)
for f in os.listdir(OUT + '/fu/spv'):
    os.remove(OUT + '/fu/spv/' + f)

guard()
r = subprocess.run([B + '/diag_b32_tests.exe'], capture_output=True, text=True)
open(OUT + '/diag_b32_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
t1 = r.returncode == 0 and 'ALL OK' in r.stdout.splitlines()[-1:]
print('t1 diag_b32_tests rc=%d last=%r -> %s' % (r.returncode, r.stdout.splitlines()[-1] if r.stdout else '', 'ok' if t1 else 'FAIL'))
ok &= t1

guard()
env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
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
t2 = r.returncode == 0 and n_failed == 0 and n_tests > 0 and (ref_tests == 0 or n_tests == ref_tests)
print('t2 shader_cfg_tests rc=%d tests=%d (FS8a fu %d) failed_lines=%d -> %s' % (r.returncode, n_tests, ref_tests, n_failed,
                                                                                  'ok' if t2 else 'FAIL'))
ok &= t2

mine = sorted(os.listdir(OUT + '/fu/spv'))
ref = sorted(os.listdir(REF + '/spv'))
diff = [f for f in sorted(set(mine) | set(ref)) if f not in mine or f not in ref or sha(OUT + '/fu/spv/' + f) != sha(REF + '/spv/' + f)]
agg_m = hashlib.sha256(''.join(sha(OUT + '/fu/spv/' + f) for f in mine).encode()).hexdigest()
agg_r = hashlib.sha256(''.join(sha(REF + '/spv/' + f) for f in ref).encode()).hexdigest()
t3 = len(mine) > 0 and not diff
print('t3 SPIR-V files mine %d ref %d differing %d aggregate %s / %s -> %s' % (len(mine), len(ref), len(diff), agg_m[:8],
                                                                              agg_r[:8], 'ok' if t3 else 'FAIL'))
for f in diff[:20]:
    print('   differs:', f)
ok &= t3
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
