# F19c2 (HPP-559): copy of the F19c tests_f19c.py, run in C:/kyty/f287/f19c2 (worktree wt = main 20d97cd8 + F19c2 patches). Was:
# F19c (HPP-547; form of the F18c tests_f18c.py): shader_cfg_tests of the F19c worktree build (52d2f546 = 4d9e8ab7 +
# cherry-pick 9c726d74) at KYTY_FIX_B24 unset / 1; every KYTY_* removed from the child environment, then
# KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1. Output per run: runs/tests/<exe>_<fix>.txt; one summary line per run: rc,
# wall, the last line, the [test] count and the "failed" lines. Halts on the lock or STOP. Form of the F15c tests_f15c.py.
# Usage (cwd C:/kyty/f287/f19c): python tests_f19c.py
import os, subprocess, sys, time
os.makedirs('runs/tests', exist_ok=True)
for exe in ('shader_cfg_tests',):
    for fx in ('none', '1'):
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            print('HALT')
            sys.exit(3)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
        if fx != 'none':
            env['KYTY_FIX_B24'] = fx
        env['KYTY_TESTS_CONTINUE'] = '1'
        env['KYTY_TESTS_VERBOSE'] = '1'
        t0 = time.time()
        p = subprocess.run([os.path.abspath('build/' + exe + '.exe')], cwd=os.path.abspath('build'), env=env,
                           capture_output=True, timeout=500)
        out = (p.stdout + p.stderr).decode('utf-8', 'replace').replace('\r\n', '\n')
        open('runs/tests/%s_%s.txt' % (exe, fx), 'w', encoding='utf-8', newline='\n').write(out)
        lines = [l for l in out.split('\n') if l.strip()]
        tests = sum(1 for l in lines if l.startswith('[test]'))
        fails = [l for l in lines if 'fail' in l.lower()]
        print('%s fix=%s rc=%s wall=%.1f s tests=%d last=[%s] fail_lines=%d %s' % (
            exe, fx, p.returncode, time.time() - t0, tests, lines[-1][:120] if lines else '', len(fails),
            ' | '.join(f[:100] for f in fails[:4])))
