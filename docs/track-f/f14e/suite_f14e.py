"""F14e (HPP-505, ROADMAP s122 item 409(g)(2)): full shader_cfg_tests runs and the SPIR-V of the probes.

Runs (one process each, all KYTY_* removed, KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR=<run>/spv):
  base   base exe (parent of the code commit + test part A), KYTY_FIX_F19 unset
  f0     fix exe, KYTY_FIX_F19=0
  fu     fix exe, KYTY_FIX_F19 unset
  f1     fix exe, KYTY_FIX_F19=1
Readings: every run - number of tests, failing tests (ShaderCfgTests: failed:), the [f19] lines; SPIR-V files
(RecompileForTest dumps them in call order) of f0 and fu == base byte for byte (same names, same bytes); f1 - the list of
files that differ from base (expected: only the probes of F14e). Usage: python suite_f14e.py <base exe> <fix exe> <out>
[run names]. Rule 27: the lock and STOP are checked before every process (exit 5 / 4).
"""
import hashlib
import os
import re
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(name, exe, f19, out):
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(5)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)
    d = '%s/%s' % (out, name)
    os.makedirs(d + '/spv', exist_ok=True)
    for f in os.listdir(d + '/spv'):
        os.remove(d + '/spv/' + f)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update({'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_VERBOSE': '1', 'KYTY_TESTS_SPV_DIR': d + '/spv'})
    if f19 is not None:
        env['KYTY_FIX_F19'] = f19
    t0 = time.time()
    p = subprocess.run([exe], cwd=d, env=env, capture_output=True, timeout=900)
    log = p.stdout + b'\n==== stderr ====\n' + p.stderr
    open(d + '/suite.log', 'wb').write(log)
    print('%s rc=%s wall=%.1f s exe=%s' % (name, p.returncode, time.time() - t0, sha(exe)[:8]))


def summary(name, out):
    d = '%s/%s' % (out, name)
    text = open(d + '/suite.log', 'rb').read().decode('latin1').replace('\r', '')
    tests, fails, cur, f19 = [], {}, None, []
    for line in text.split('\n'):
        m = re.match(r'^\[test\] (\S+)$', line)
        if m:
            cur = m.group(1)
            tests.append(cur)
        elif 'ShaderCfgTests: failed: ' in line:
            fails.setdefault(cur, []).append(line.split('ShaderCfgTests: failed: ', 1)[1])
        elif line.startswith('[f19]'):
            f19.append(line)
    spv = sorted(f for f in os.listdir(d + '/spv') if f.endswith('.spv'))
    print('%s: tests %d, failing %d %s' % (name, len(tests), len(fails), list(fails.items())[:3]))
    for line in f19:
        print('   ', line)
    return len(tests), fails, spv


def main():
    base_exe, fix_exe, out = sys.argv[1:4]
    names = sys.argv[4:] or ['base', 'f0', 'fu', 'f1']
    cfg = {'base': (base_exe, None), 'f0': (fix_exe, '0'), 'fu': (fix_exe, None), 'f1': (fix_exe, '1')}
    for n in names:
        run(n, cfg[n][0], cfg[n][1], out)
    ok = True
    res = {}
    for n in ['base', 'f0', 'fu', 'f1']:
        if os.path.exists('%s/%s/suite.log' % (out, n)):
            res[n] = summary(n, out)
            ok &= not res[n][1]
    if 'base' in res:
        bspv = res['base'][2]
        for n in ('f0', 'fu', 'f1'):
            if n not in res:
                continue
            nspv = res[n][2]
            diff = [f for f in sorted(set(bspv) | set(nspv))
                    if f not in bspv or f not in nspv or
                    sha('%s/base/spv/%s' % (out, f)) != sha('%s/%s/spv/%s' % (out, n, f))]
            print('%s: SPIR-V files %d (base %d), differing from base %d: %s' % (n, len(nspv), len(bspv), len(diff),
                                                                               ' '.join(diff[:20])))
            if n in ('f0', 'fu'):
                ok &= not diff and len(nspv) == len(bspv)
    print('base exe', base_exe, sha(base_exe))
    print('fix exe ', fix_exe, sha(fix_exe))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
