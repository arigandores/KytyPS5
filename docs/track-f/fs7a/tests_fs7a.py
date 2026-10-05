# FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1)): shader_cfg_tests and audio_propagation_tests of the base (FS6a
# 3904522d: C:/kyty/f287/fs6a/build - the FS6a worktree build, audio_propagation_tests built there as an extra target) and
# of FS7 (fix/) at the defaults - every KYTY_* removed from the child environment, then KYTY_TESTS_CONTINUE=1
# KYTY_TESTS_VERBOSE=1. Output: runs/tests/<set>_<exe>.txt; comparison of the 'failed:' lines base vs FS7, the [test]
# count and the last line. Halts on the lock or STOP. Copy of the FS6a tests_fs6a.py with the F18c test set.
import os, re, subprocess, sys, time
os.makedirs('runs/tests', exist_ok=True)
SETS = {'base': 'C:/kyty/f287/fs6a/build', 'fs7': 'C:/kyty/f287/fs7a/fix'}
RUNS = (('scfg', 'shader_cfg_tests', []), ('aprop', 'audio_propagation_tests', []))
only = sys.argv[1:]
for tag, exe, args in RUNS:
    for st, d in SETS.items():
        if only and tag not in only:
            continue
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            print('HALT'); sys.exit(3)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
        env['KYTY_TESTS_CONTINUE'] = '1'
        env['KYTY_TESTS_VERBOSE'] = '1'
        t0 = time.time()
        p = subprocess.run([d + '/' + exe + '.exe'] + args, cwd=d, env=env, capture_output=True, timeout=500)
        out = (p.stdout + p.stderr).decode('utf-8', 'replace').replace('\r\n', '\n')
        open('runs/tests/%s_%s.txt' % (st, tag), 'w', encoding='utf-8', newline='\n').write(out)
        lines = [l for l in out.splitlines() if l.strip()]
        print('%s %s rc=%s wall=%.1f s tests=%d last=[%s]' % (st, exe, p.returncode, time.time() - t0,
              sum(1 for l in lines if l.startswith('[test]')), lines[-1][:140] if lines else ''))


def failed(path):
    return [l for l in open(path, encoding='utf-8').read().splitlines() if 'failed:' in l]


def norm(path):
    t = open(path, encoding='utf-8').read()
    return re.sub(r'elapsed_ms=\d+', 'elapsed_ms=N', t)


ok = True
for tag, exe, args in RUNS:
    pb, pf = 'runs/tests/base_%s.txt' % tag, 'runs/tests/fs7_%s.txt' % tag
    if not (os.path.exists(pb) and os.path.exists(pf)):
        print('%s missing' % tag)
        ok = False
        continue
    b, f = failed(pb), failed(pf)
    same = b == f
    ok &= same
    tb = sum(1 for l in open(pb, encoding='utf-8') if l.startswith('[test]'))
    tf = sum(1 for l in open(pf, encoding='utf-8') if l.startswith('[test]'))
    ok &= tb == tf
    print('%s failed-lines base %d fs7 %d equal %s; [test] base %d fs7 %d; text equal (elapsed_ms masked) %s' %
          (tag, len(b), len(f), same, tb, tf, norm(pb) == norm(pf)))
    for l in sorted(set(f)):
        print('   ', l[:160])
print('ALL OK' if ok else 'DIFF')
