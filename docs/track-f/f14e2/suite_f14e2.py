"""F14e2 (HPP-545, ROADMAP s122 item 443(v)(3)): full shader_cfg_tests runs and the SPIR-V of the set.
Copy of the F14e suite_f14e.py (HPP-505) with the reading of item 443(v)(3).

Runs (one process each, all KYTY_* removed, KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR=<run>/spv):
  base   base exe (HEAD main before the link, no RC3 probes), KYTY_FIX_F19 unset
  b1     base exe, KYTY_FIX_F19=1 (reference of f1 for the files of the base set)
  f0     link exe, KYTY_FIX_F19=0
  fu     link exe, KYTY_FIX_F19 unset
  f1     link exe, KYTY_FIX_F19=1
RecompileForTest names the dumps by a process counter; the RC3 test runs last, so the files 0..N-1 (N = base count)
are the set of the base and N.. are the new probes (4: C alone, C shared, C_LZ alone, C_LZ shared).
Readings (ALL OK only if every one holds):
  (r1) every run: 0 failing tests (lines 'ShaderCfgTests: failed:'); link runs have one test more than base.
  (r2) f0 and fu: files 0..N-1 byte for byte = base; f1: files 0..N-1 byte for byte = b1.
  (r3) f0 and fu have exactly N+4 files, the 4 new ones byte for byte f0 = fu.
  (r4) f1: the 'alone' probes byte for byte = f0 (null T# native at any value); the 'shared' probes differ from f0.
  (r5) [f19] null lines: f1 - alone native=1 dref=1 manual=0, shared native=2 dref=2 manual=0;
       f0/fu - alone the same, shared manual_images=2 dref=0 manual=2.
Usage: python suite_f14e2.py <base exe> <link exe> <out> [run names]. Rule 27: lock and STOP before every process.
"""
import hashlib
import os
import re
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
NEW = 4


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
    print('%s rc=%s wall=%.1f s exe=%s KYTY_FIX_F19=%s' % (name, p.returncode, time.time() - t0, sha(exe)[:8],
                                                          'unset' if f19 is None else f19))


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
    spv = sorted((f for f in os.listdir(d + '/spv') if f.endswith('.spv')), key=lambda f: int(f[:-4]))
    print('%s: tests %d, failing %d %s, spv %d' % (name, len(tests), len(fails), list(fails.items())[:3], len(spv)))
    for line in f19:
        print('   ', line)
    return {'tests': len(tests), 'fails': fails, 'spv': spv, 'f19': f19}


def same(out, a, b, f):
    pa, pb = '%s/%s/spv/%s' % (out, a, f), '%s/%s/spv/%s' % (out, b, f)
    return os.path.exists(pa) and os.path.exists(pb) and sha(pa) == sha(pb)


def main():
    base_exe, fix_exe, out = sys.argv[1:4]
    names = sys.argv[4:] or ['base', 'b1', 'f0', 'fu', 'f1']
    cfg = {'base': (base_exe, None), 'b1': (base_exe, '1'), 'f0': (fix_exe, '0'), 'fu': (fix_exe, None),
           'f1': (fix_exe, '1')}
    for n in names:
        run(n, cfg[n][0], cfg[n][1], out)
    ok = True
    res = {n: summary(n, out) for n in ['base', 'b1', 'f0', 'fu', 'f1']}
    # (r1)
    for n, r in res.items():
        ok &= not r['fails']
    for n in ('f0', 'fu', 'f1'):
        good = res[n]['tests'] == res['base']['tests'] + 1
        print('(r1) %s tests %d = base %d + 1: %s' % (n, res[n]['tests'], res['base']['tests'], good))
        ok &= good
    nb = len(res['base']['spv'])
    good = len(res['b1']['spv']) == nb
    print('(r1) b1 spv %d = base %d: %s' % (len(res['b1']['spv']), nb, good))
    ok &= good
    old = ['%d.spv' % i for i in range(nb)]
    new = ['%d.spv' % i for i in range(nb, nb + NEW)]
    # (r2)
    for n, ref in (('f0', 'base'), ('fu', 'base'), ('f1', 'b1')):
        diff = [f for f in old if not same(out, ref, n, f)]
        print('(r2) %s: files 0..%d vs %s - differing %d %s' % (n, nb - 1, ref, len(diff), ' '.join(diff[:10])))
        ok &= not diff
    # (r3)
    for n in ('f0', 'fu', 'f1'):
        good = len(res[n]['spv']) == nb + NEW
        print('(r3) %s: spv %d = %d + %d: %s' % (n, len(res[n]['spv']), nb, NEW, good))
        ok &= good
    diff = [f for f in new if not same(out, 'f0', 'fu', f)]
    print('(r3) new files f0 vs fu - differing %d %s' % (len(diff), ' '.join(diff)))
    ok &= not diff
    # (r4): order of the test - C alone, C shared, C_LZ alone, C_LZ shared
    kinds = ['alone', 'shared', 'alone', 'shared']
    for f, k in zip(new, kinds):
        eq = same(out, 'f0', 'f1', f)
        good = eq if k == 'alone' else not eq
        print('(r4) %s (%s): f1 %s f0: %s' % (f, k, '==' if eq else '!=', good))
        ok &= good
    # (r5)
    want = {
        'f1': ['alone C KYTY_FIX_F19=1: images=1 native=1 manual_images=0 dref=1 manual=0',
               'shared sampler C KYTY_FIX_F19=1: images=2 native=2 manual_images=0 dref=2 manual=0',
               'alone C_LZ KYTY_FIX_F19=1: images=1 native=1 manual_images=0 dref=1 manual=0',
               'shared sampler C_LZ KYTY_FIX_F19=1: images=2 native=2 manual_images=0 dref=2 manual=0'],
    }
    for n in ('f0', 'fu'):
        want[n] = ['alone C KYTY_FIX_F19=0: images=1 native=1 manual_images=0 dref=1 manual=0',
                   'shared sampler C KYTY_FIX_F19=0: images=2 native=0 manual_images=2 dref=0 manual=2',
                   'alone C_LZ KYTY_FIX_F19=0: images=1 native=1 manual_images=0 dref=1 manual=0',
                   'shared sampler C_LZ KYTY_FIX_F19=0: images=2 native=0 manual_images=2 dref=0 manual=2']
    for n, lines in want.items():
        got = [l for l in res[n]['f19'] if l.startswith('[f19] null T#')]
        good = len(got) == 4 and all(g.endswith(w) for g, w in zip(got, lines))
        print('(r5) %s null lines %d, as expected: %s' % (n, len(got), good))
        ok &= good
    print('base exe', base_exe, sha(base_exe))
    print('link exe', fix_exe, sha(fix_exe))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
