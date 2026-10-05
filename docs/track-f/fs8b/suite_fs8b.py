# FS8b (HPP-572, Red Team, item 471(g)(2) own run of (g)(1)(v)): copy of the FS8a suite_fs8a.py, logic unchanged.
"""FS8a (HPP-571, ROADMAP s122 item 471(g)(1)(v), reading of item 523(g)): shader_cfg_tests of the FS8 worktree.
Form of the F14e2 suite_f14e2.py (HPP-545), runs and readings of member (v) only.

Runs (one process each, all KYTY_* removed, KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR=<run>/spv):
  fu  KYTY_FIX_F19 unset
  f0  KYTY_FIX_F19=0
  f1  KYTY_FIX_F19=1
Readings (ALL OK only if every one holds):
  (v1) every run: 0 lines 'ShaderCfgTests: failed:' and rc 0; the three runs have the same test count (> 0).
  (v2) fu and f1: the same set of SPIR-V files, byte for byte equal (sha256 per file); count > 0.
  (v3) information: f0 vs fu - number of differing SPIR-V files (the =0 path differs where F19 acts; not a gate).
Usage: python suite_fs8a.py <shader_cfg_tests.exe> <out> [run names]. Rule 27: lock and STOP before every process.
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
    open(d + '/rc.txt', 'w').write('%d\n' % p.returncode)
    print('%s rc=%s wall=%.1f s exe=%s KYTY_FIX_F19=%s' % (name, p.returncode, time.time() - t0, sha(exe)[:8],
                                                          'unset' if f19 is None else f19))


def summary(name, out):
    d = '%s/%s' % (out, name)
    text = open(d + '/suite.log', 'rb').read().decode('latin1').replace('\r', '')
    rc = int(open(d + '/rc.txt').read())
    tests, fails, cur = [], [], None
    for line in text.split('\n'):
        m = re.match(r'^\[test\] (\S+)$', line)
        if m:
            cur = m.group(1)
            tests.append(cur)
        elif 'ShaderCfgTests: failed: ' in line:
            fails.append((cur, line.split('ShaderCfgTests: failed: ', 1)[1]))
    spv = sorted((f for f in os.listdir(d + '/spv') if f.endswith('.spv')), key=lambda f: int(f[:-4]))
    print('%s: rc %d, tests %d, failed lines %d %s, spv %d' % (name, rc, len(tests), len(fails), fails[:3], len(spv)))
    return {'rc': rc, 'tests': len(tests), 'fails': fails, 'spv': spv,
            'sha': {f: sha('%s/spv/%s' % (d, f)) for f in spv}}


def main():
    exe, out = sys.argv[1:3]
    names = sys.argv[3:] or ['fu', 'f0', 'f1']
    cfg = {'fu': None, 'f0': '0', 'f1': '1'}
    for n in names:
        run(n, exe, cfg[n], out)
    res = {n: summary(n, out) for n in ['fu', 'f0', 'f1']}
    ok = True
    # (v1)
    for n, r in res.items():
        good = not r['fails'] and r['rc'] == 0
        print('(v1) %s: failed lines %d, rc %d: %s' % (n, len(r['fails']), r['rc'], good))
        ok &= good
    counts = {r['tests'] for r in res.values()}
    good = len(counts) == 1 and min(counts) > 0
    print('(v1) test count equal in the three runs %s: %s' % (sorted(counts), good))
    ok &= good
    # (v2)
    fu, f1 = res['fu'], res['f1']
    good = fu['spv'] == f1['spv'] and len(fu['spv']) > 0
    diff = [f for f in fu['spv'] if fu['sha'].get(f) != f1['sha'].get(f)]
    print('(v2) fu spv %d, f1 spv %d, same names %s, differing %d %s' % (
        len(fu['spv']), len(f1['spv']), fu['spv'] == f1['spv'], len(diff), ' '.join(diff[:10])))
    ok &= good and not diff
    agg = hashlib.sha256(''.join('%s %s\n' % (f, fu['sha'][f]) for f in fu['spv']).encode()).hexdigest()
    print('(v2) aggregate sha256 of the fu set (name sha lines): %s' % agg)
    # (v3)
    f0 = res['f0']
    d0 = [f for f in fu['spv'] if fu['sha'].get(f) != f0['sha'].get(f)]
    print('(v3) information: f0 spv %d, differing from fu %d %s' % (len(f0['spv']), len(d0), ' '.join(d0[:20])))
    print('exe', exe, sha(exe))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
