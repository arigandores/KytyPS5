# FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): kernel_file_system_tests --filesystem-only and shader_cfg_tests of the base
# (S12a 4d9e8ab7: C:/kyty/f287/f15c/base/, built by F15c from the base worktree) and of FS6 (3904522d: fix/) at the defaults -
# every KYTY_* removed from the child environment, then KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 for shader_cfg_tests.
# Output: runs/tests/<set>_<exe>.txt; comparison of the 'failed:' lines base vs FS6 and the shader_cfg_tests count line.
# Halts on the lock or STOP. Copy of the F15c tests_f15c.py / tests2_f15c.py reduced to the defaults.
import os, re, subprocess, sys, time
os.makedirs('runs/tests', exist_ok=True)
SETS = {'base': 'C:/kyty/f287/f15c/base', 'fs6': 'C:/kyty/f287/fs6a/fix'}
RUNS = (('kfsonly', 'kernel_file_system_tests', ['--filesystem-only']), ('scfg', 'shader_cfg_tests', []))
for tag, exe, args in RUNS:
    for st, d in SETS.items():
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            print('HALT'); sys.exit(3)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
        if exe == 'shader_cfg_tests':
            env['KYTY_TESTS_CONTINUE'] = '1'
            env['KYTY_TESTS_VERBOSE'] = '1'
        t0 = time.time()
        p = subprocess.run([d + '/' + exe + '.exe'] + args, cwd=d, env=env, capture_output=True, timeout=500)
        out = (p.stdout + p.stderr).decode('utf-8', 'replace')
        open('runs/tests/%s_%s.txt' % (st, tag), 'w', encoding='utf-8', newline='\n').write(out)
        lines = [l for l in out.splitlines() if l.strip()]
        print('%s %s %s rc=%s wall=%.1f s last=[%s]' % (st, exe, ' '.join(args), p.returncode, time.time() - t0,
              lines[-1][:140] if lines else ''))


def failed(path):
    return [l for l in open(path, encoding='utf-8').read().splitlines() if 'failed:' in l]


def count_line(path):
    t = open(path, encoding='utf-8').read()
    return re.findall(r'^.*\b\d+\s*/\s*\d+.*$|^.*tests?.*(?:passed|failed).*$', t, re.M)[-3:]


ok = True
for tag, exe, args in RUNS:
    b = failed('runs/tests/base_%s.txt' % tag)
    f = failed('runs/tests/fs6_%s.txt' % tag)
    same = b == f
    ok &= same
    print('%s failed-lines base %d fs6 %d equal %s' % (tag, len(b), len(f), same))
    for l in sorted(set(f)):
        print('   ', l[:160])
for st in SETS:
    print(st, 'scfg tail:', count_line('runs/tests/%s_scfg.txt' % st))
print('ALL OK' if ok else 'DIFF')
