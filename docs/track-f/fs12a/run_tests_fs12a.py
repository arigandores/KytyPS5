# FS12a (HPP-750): port of docs/track-f/fs11a/run_tests_fs11a.py (fs11a -> fs12a, mode fs11 -> fs12, base FS11 ee9632be). Was:
# FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): tests of the FS12 worktree build (C:/kyty/f287/fs12a/wt ->
# C:/kyty/f287/fs12a/build) without the game; the form of fs11a/run_tests_fs11a.py (t3, t4) plus memory_tracker_tests.
"""Usage:
  python run_tests_fs12a.py base   - shader_cfg_tests and memory_tracker_tests of the base FS11 ee9632be (same worktree
                                     before the cherry-picks), all KYTY_* removed -> tests/base/
  python run_tests_fs12a.py fs12   - the same after the cherry-picks and the FS12a commit -> tests/fs12/, then:
  (t2) memory_tracker_tests: rc, the number of lines with the word "failed" and the multiset of those lines, the
       "MemoryTrackerTests:" summary line = base; the "FixB12:" / "FixB13:" lines printed (reference; the base has no
       FixB12 code).
  (t3) shader_cfg_tests: rc, the number of "[test] " lines, the number of "ShaderCfgTests: failed:" and the multiset of
       lines with the word "failed" = base.
  (t4) the SPIR-V files written by (t3) (KYTY_TESTS_SPV_DIR) = base byte for byte (file names and sha256).
Rule 27: lock and STOP before every process. Prints ALL OK only if t2, t3, t4 hold.
"""
import collections
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/fs12a/build'
OUT = 'C:/kyty/f287/fs12a/tests'


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


def run_mt(out):
    os.makedirs(out, exist_ok=True)
    guard()
    r = subprocess.run([B + '/memory_tracker_tests.exe'], capture_output=True, text=True, cwd=B, env=clean_env(),
                       errors='replace')
    log = r.stdout + r.stderr
    open(out + '/mt_log.txt', 'w', encoding='utf-8', newline='\n').write(log)
    open(out + '/mt_rc.txt', 'w', encoding='utf-8', newline='\n').write('%d\n' % r.returncode)
    open(out + '/mt_exe_sha256.txt', 'w', encoding='utf-8', newline='\n').write(sha(B + '/memory_tracker_tests.exe') + '\n')
    return r.returncode, log


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


def mt_summary(rc, log):
    lines = log.splitlines()
    return (rc, collections.Counter(l for l in lines if 'failed' in l),
            [l for l in lines if l.startswith('MemoryTrackerTests:')],
            [l for l in lines if l.startswith('FixB12:') or l.startswith('FixB13:')])


mode = sys.argv[1] if len(sys.argv) > 1 else ''
if mode == 'base':
    rc, log = run_mt(OUT + '/base')
    m = mt_summary(rc, log)
    print('base memory_tracker_tests rc=%d lines_with_failed=%d summary=%s fix=%s' % (m[0], sum(m[1].values()), m[2], m[3]))
    rc, log = cfg_tests(OUT + '/base')
    s = summary(rc, log)
    print('base shader_cfg_tests rc=%d tests=%d failed_lines=%d lines_with_failed=%d spv=%d' % (
        s[0], s[1], s[2], sum(s[3].values()), len(os.listdir(OUT + '/base/spv'))))
    sys.exit(0)
if mode != 'fs12':
    print(__doc__)
    sys.exit(2)

ok = True
rc, log = run_mt(OUT + '/fs12')
m = mt_summary(rc, log)
bl = open(OUT + '/base/mt_log.txt', encoding='utf-8', errors='replace').read()
brc = int(open(OUT + '/base/mt_rc.txt').read())
bm = mt_summary(brc, bl)
t2 = m[0] == bm[0] and m[1] == bm[1] and m[2] == bm[2] and len(m[2]) > 0
print('t2 memory_tracker_tests fs12 rc=%d lines_with_failed=%d summary=%s fix=%s | base rc=%d lines_with_failed=%d summary=%s fix=%s -> %s' % (
    m[0], sum(m[1].values()), m[2], m[3], bm[0], sum(bm[1].values()), bm[2], bm[3], 'ok' if t2 else 'FAIL'))
ok &= t2

rc, log = cfg_tests(OUT + '/fs12')
s = summary(rc, log)
bl = open(OUT + '/base/log.txt', encoding='utf-8', errors='replace').read()
brc = int(open(OUT + '/base/rc.txt').read())
bs = summary(brc, bl)
t3 = s[0] == bs[0] and s[1] == bs[1] and s[2] == bs[2] and s[3] == bs[3] and s[1] > 0
print('t3 shader_cfg_tests fs12 rc=%d tests=%d failed_lines=%d lines_with_failed=%d | base rc=%d tests=%d failed_lines=%d lines_with_failed=%d; multiset equal %s -> %s' % (
    s[0], s[1], s[2], sum(s[3].values()), bs[0], bs[1], bs[2], sum(bs[3].values()), s[3] == bs[3], 'ok' if t3 else 'FAIL'))
ok &= t3

mine = sorted(os.listdir(OUT + '/fs12/spv'))
ref = sorted(os.listdir(OUT + '/base/spv'))
diff = [f for f in sorted(set(mine) | set(ref)) if f not in mine or f not in ref or sha(OUT + '/fs12/spv/' + f) != sha(OUT + '/base/spv/' + f)]
agg_m = hashlib.sha256(''.join(sha(OUT + '/fs12/spv/' + f) for f in mine).encode()).hexdigest()
agg_r = hashlib.sha256(''.join(sha(OUT + '/base/spv/' + f) for f in ref).encode()).hexdigest()
t4 = len(mine) > 0 and not diff
print('t4 SPIR-V fs12 %d base %d differing %d aggregate %s / %s -> %s' % (len(mine), len(ref), len(diff), agg_m[:8], agg_r[:8],
                                                                     'ok' if t4 else 'FAIL'))
for f in diff[:20]:
    print('   differs:', f)
ok &= t4
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
