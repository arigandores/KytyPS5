"""Session 145 link 1b rework 1 (HPP-379; ROADMAP s122 item 301 (v)): one mutant run of the frozen harness v4.1
under a wall cap; stops the run at once when its log shows 'workers: FORCED TO 1' (item 301 (v)(1)).
usage: python rm1b2.py gate|sc <cap seconds>
Prints ASCII only: 'RM1B2 <which> rc <rc> wall <s> forced <0|1> capped <0|1>'.
"""
import os
import subprocess
import sys
import time

HARN = 'C:/kyty/KytyPS5/docs/session-116/mutlib_v41/' + 'mut' + 'lib.py'
S = 'C:/kyty/s145'
RUNS = {
    'gate': (['--scorer', S + '/step2/gate145.py', '--test', S + '/step2/test_gate145.py', '--mutants', S + '/step2/mut_gate145.py',
              '--only', 'g_pred,g_refseal,g_minfree,g_disk,g_rx,g_wab_none,g_wab_noline,g_f4,g_f4_nojson,g_wb_none,g_wb,'
              'g_ref_cmp,g_ref_none,g_free_cmp,g_early',
              '--workers', '18', '--work-dir', S + '/mutwork_1b2g', '--cache-dir', S + '/mutcache_1b2g'],
             S + '/step1b/mut_only1b_gate2.log', S + '/step1b/mut_only1b_gate2.txt'),
    'sc': (['--scorer', S + '/sc145.py', '--test', S + '/test_sc145.py', '--mutants', S + '/mut_sc145.py',
            '--only', 'e_rg_ok_lim,e_rg_lim_ctrl,rg_mok,rg_nhok,rg_nh,rg_exp,rg_res,rg_wt',
            '--workers', '11', '--work-dir', S + '/mutwork_1b3', '--cache-dir', S + '/mutcache_1b3'],
           S + '/step1b/mut_only1b_sc3.log', S + '/step1b/mut_only1b_sc3.txt'),
}


def main():
    which, cap = sys.argv[1], float(sys.argv[2])
    args, log, out = RUNS[which]
    cmd = [sys.executable, HARN] + args + ['--control', '--no-memo', '--out', out]
    t0 = time.time()
    forced = capped = 0
    with open(log, 'wb') as lf:
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
        while p.poll() is None:
            time.sleep(1)
            try:
                with open(log, 'rb') as f:
                    if b'FORCED TO 1' in f.read():
                        forced = 1
            except OSError:
                pass
            if forced or time.time() - t0 > cap:
                capped = 0 if forced else 1
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], capture_output=True)
                p.wait()
                break
    print('RM1B2 %s rc %s wall %.1f forced %d capped %d' % (which, p.returncode, time.time() - t0, forced, capped))
    return 0


if __name__ == '__main__':
    sys.exit(main())
