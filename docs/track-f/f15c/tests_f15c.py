# F15c (HPP-514, ROADMAP s122 item 412(g)(3)): kernel_file_system_tests and shader_cfg_tests of the base (4d9e8ab7, base/)
# and of the fix (5c2c5e52, fix/) at KYTY_FIX_B4 unset / 0 / 1; every KYTY_* removed from the child environment, then
# KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 for shader_cfg_tests. Output per run: runs/tests/<set>_<exe>_<fix>.txt; one
# summary line per run: rc, wall, the last line, failure lines count. Halts on the lock or STOP.
import os, subprocess, sys, time
os.makedirs('runs/tests', exist_ok=True)
for exe in ('kernel_file_system_tests', 'shader_cfg_tests'):
    for st in ('base', 'fix'):
        for fx in ('none', '0', '1'):
            if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
                print('HALT'); sys.exit(3)
            env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
            if fx != 'none':
                env['KYTY_FIX_B4'] = fx
            if exe == 'shader_cfg_tests':
                env['KYTY_TESTS_CONTINUE'] = '1'
                env['KYTY_TESTS_VERBOSE'] = '1'
            t0 = time.time()
            p = subprocess.run([os.path.abspath(st + '/' + exe + '.exe')], cwd=os.path.abspath(st), env=env,
                               capture_output=True, timeout=500)
            out = (p.stdout + p.stderr).decode('utf-8', 'replace')
            open('runs/tests/%s_%s_%s.txt' % (st, exe, fx), 'w', encoding='utf-8', newline='\n').write(out)
            lines = [l for l in out.splitlines() if l.strip()]
            fails = [l for l in lines if 'FAIL' in l.upper() and 'failed: 0' not in l.lower()]
            print('%s %s fix=%s rc=%s wall=%.1f s last=[%s] fail_lines=%d' % (st, exe, fx, p.returncode, time.time() - t0,
                  lines[-1][:120] if lines else '', len(fails)))
