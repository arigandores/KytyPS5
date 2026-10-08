# FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): tests of the FS10 worktree build (C:/kyty/f287/fs10a/wt ->
# C:/kyty/f287/fs10a/build) without the game; the form of f25k2/run_tests_f25k2.py and fs9a/run_tests_fs9a.py.
"""Usage:
  python run_tests_fs10a.py base   - shader_cfg_tests of the base FS9 11164d72 (same worktree before the cherry-picks),
                                     all KYTY_* removed -> tests/base/ (log.txt, spv/)
  python run_tests_fs10a.py fs10   - after the cherry-picks and the FS10a commit:
  (t1) log_async_tests (the FS10 source): rc 0 and the last line ALL OK; in it seq0_0 (KYTY_FIX_B36=0) - the file equals the
       expected bytes; seq0_u (variable unset) - "LogAsync: mode=1" first, full_waits=0, without the LogAsync: lines = the
       expected bytes (the default ON of FS10a); seq0_1 (=1) - the same.
  (t1b) =0 byte for byte with the code before F25k: the reference executable of F25k (f25k/ref/log_async_tests_ref.exe,
       its sha256 printed) writes the fixed sequence; sha256 = that of seq0_0.txt (=0). Negative controls: seq0_1.txt (=1)
       and seq0_u.txt (unset) must differ from it.
  (t1c) the "mode" line of each seq0 file: =0 - no "LogAsync:" line; unset and =1 - "LogAsync: mode=1".
  (t3) shader_cfg_tests, all KYTY_* removed: rc, the number of "[test] " lines, the number of "ShaderCfgTests: failed:" and
       the multiset of lines with the word "failed" = base.
  (t4) the SPIR-V files written by (t3) (KYTY_TESTS_SPV_DIR) = base byte for byte (file names and sha256).
Rule 27: lock and STOP before every process. Prints ALL OK only if t1, t1b, t1c, t3, t4 hold.
"""
import collections
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/fs10a/build'
OUT = 'C:/kyty/f287/fs10a/tests'
REFEXE = 'C:/kyty/f287/f25k/ref/log_async_tests_ref.exe'


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


def cfg_tests(out):
    os.makedirs(out + '/spv', exist_ok=True)
    for f in os.listdir(out + '/spv'):
        os.remove(out + '/spv/' + f)
    guard()
    env = clean_env()
    env['KYTY_TESTS_CONTINUE'] = '1'
    env['KYTY_TESTS_VERBOSE'] = '1'
    env['KYTY_TESTS_SPV_DIR'] = out + '/spv'
    r = subprocess.run([B + '/shader_cfg_tests.exe'], capture_output=True, text=True, cwd=B, env=env, errors='replace')
    log = r.stdout + r.stderr
    open(out + '/log.txt', 'w', encoding='utf-8', newline='\n').write(log)
    open(out + '/rc.txt', 'w', encoding='utf-8', newline='\n').write('%d\n' % r.returncode)
    open(out + '/exe_sha256.txt', 'w', encoding='utf-8', newline='\n').write(sha(B + '/shader_cfg_tests.exe') + '\n')
    return r.returncode, log


def summary(rc, log):
    return (rc, len(re.findall(r'^\[test\] ', log, re.M)), len(re.findall(r'ShaderCfgTests: failed:', log)),
            collections.Counter(l for l in log.splitlines() if 'failed' in l))


mode = sys.argv[1] if len(sys.argv) > 1 else ''
if mode == 'base':
    rc, log = cfg_tests(OUT + '/base')
    s = summary(rc, log)
    print('base shader_cfg_tests rc=%d tests=%d failed_lines=%d lines_with_failed=%d spv=%d' % (
        s[0], s[1], s[2], sum(s[3].values()), len(os.listdir(OUT + '/base/spv'))))
    sys.exit(0)
if mode != 'fs10':
    print(__doc__)
    sys.exit(2)

ok = True
os.makedirs(OUT + '/fs10', exist_ok=True)
LA = OUT + '/fs10/la'
os.makedirs(LA, exist_ok=True)
for f in os.listdir(LA):
    if os.path.isfile(LA + '/' + f):
        os.remove(LA + '/' + f)

guard()
r = subprocess.run([B + '/log_async_tests.exe', LA], capture_output=True, text=True, env=clean_env(), errors='replace')
open(OUT + '/fs10/log_async_tests.log', 'w', encoding='utf-8', newline='\n').write(r.stdout + r.stderr)
last = r.stdout.splitlines()[-1] if r.stdout else ''
cases = re.findall(r'cases=(\d+) failures=(\d+)', r.stdout)
t1 = r.returncode == 0 and last == 'ALL OK'
print('t1 log_async_tests rc=%d last=%r cases=%s -> %s' % (r.returncode, last, cases, 'ok' if t1 else 'FAIL'))
ok &= t1

guard()
ref_txt = LA + '/seq0_ref.txt'
r = subprocess.run([REFEXE, '--child', 'seq0', ref_txt], capture_output=True, text=True, env=clean_env())
h_ref = sha(ref_txt) if os.path.exists(ref_txt) else '-'
h0, hu, h1 = sha(LA + '/seq0_0.txt'), sha(LA + '/seq0_u.txt'), sha(LA + '/seq0_1.txt')
t1b = r.returncode == 0 and h_ref == h0 and h1 != h0 and hu != h0
print('t1b =0 vs the code before F25k: ref exe %s; ref %s =0 %s -> equal %s; negative controls =1 %s differs %s, unset %s differs %s -> %s' % (
    sha(REFEXE)[:16], h_ref[:16], h0[:16], h_ref == h0, h1[:16], h1 != h0, hu[:16], hu != h0, 'ok' if t1b else 'FAIL'))
ok &= t1b


def first_async(p):
    for l in open(p, 'rb').read().decode('utf-8', 'replace').split('\n'):
        if l.startswith('LogAsync:'):
            return l
    return ''


m0, mu, m1 = first_async(LA + '/seq0_0.txt'), first_async(LA + '/seq0_u.txt'), first_async(LA + '/seq0_1.txt')
t1c = m0 == '' and mu.startswith('LogAsync: mode=1 ') and m1.startswith('LogAsync: mode=1 ')
print('t1c first LogAsync line: =0 %r; unset %r; =1 %r -> %s' % (m0, mu[:40], m1[:40], 'ok' if t1c else 'FAIL'))
ok &= t1c

rc, log = cfg_tests(OUT + '/fs10')
s = summary(rc, log)
bl = open(OUT + '/base/log.txt', encoding='utf-8', errors='replace').read()
brc = int(open(OUT + '/base/rc.txt').read())
bs = summary(brc, bl)
t3 = s[0] == bs[0] and s[1] == bs[1] and s[2] == bs[2] and s[3] == bs[3] and s[1] > 0
print('t3 shader_cfg_tests fs10 rc=%d tests=%d failed_lines=%d lines_with_failed=%d | base rc=%d tests=%d failed_lines=%d lines_with_failed=%d; multiset equal %s -> %s' % (
    s[0], s[1], s[2], sum(s[3].values()), bs[0], bs[1], bs[2], sum(bs[3].values()), s[3] == bs[3], 'ok' if t3 else 'FAIL'))
ok &= t3

mine = sorted(os.listdir(OUT + '/fs10/spv'))
ref = sorted(os.listdir(OUT + '/base/spv'))
diff = [f for f in sorted(set(mine) | set(ref)) if f not in mine or f not in ref or sha(OUT + '/fs10/spv/' + f) != sha(OUT + '/base/spv/' + f)]
agg_m = hashlib.sha256(''.join(sha(OUT + '/fs10/spv/' + f) for f in mine).encode()).hexdigest()
agg_r = hashlib.sha256(''.join(sha(OUT + '/base/spv/' + f) for f in ref).encode()).hexdigest()
t4 = len(mine) > 0 and not diff
print('t4 SPIR-V fs10 %d base %d differing %d aggregate %s / %s -> %s' % (len(mine), len(ref), len(diff), agg_m[:8], agg_r[:8],
                                                                     'ok' if t4 else 'FAIL'))
for f in diff[:20]:
    print('   differs:', f)
ok &= t4
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
