"""F14f (HPP-506, ROADMAP s122 items 409(g)(2), 415(g)): Red Team's own shader_cfg_tests runs and reader.

Runs (one process each in <out>/<name>, all KYTY_* removed, KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1,
KYTY_TESTS_SPV_DIR=<out>/<name>/spv): base (base exe, knob unset), f0 (fix exe, =0), fu (fix exe, unset), f1 (fix exe, =1).
Reader: tests = lines '[test] <name>'; failures = lines with 'ShaderCfgTests: failed'; SPIR-V files of f0 and fu == base
byte for byte; f1 - list of differing files; the [f19] probe lines.
Expected (item 409(g)(2), 415(b)): 0 failures in all four; f0, fu == base; f1 differs only in the F14e probes; probe lines
f1: k16 dref=1 manual=0; tables k16+k8 manual, k16+k32 dref, k32+k8 manual; f0: k16 manual, tables k16+k8 manual,
k16+k32 manual, k32+k8 dref.
Usage: python f14f_suite.py run <base exe> <fix exe> <out> [names] | python f14f_suite.py read <out> [--mutant]
"""
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(base, fix, out, names):
    cfg = {'base': (base, None), 'f0': (fix, '0'), 'fu': (fix, None), 'f1': (fix, '1')}
    for n in names:
        if os.path.exists(LOCK):
            print('HALT lock')
            sys.exit(5)
        if os.path.exists(STOP):
            print('HALT stop')
            sys.exit(4)
        exe, f19 = cfg[n]
        d = os.path.join(out, n)
        os.makedirs(d + '/spv', exist_ok=True)
        for f in os.listdir(d + '/spv'):
            os.remove(d + '/spv/' + f)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env.update({'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_VERBOSE': '1', 'KYTY_TESTS_SPV_DIR': d + '/spv'})
        if f19 is not None:
            env['KYTY_FIX_F19'] = f19
        p = subprocess.run([exe], cwd=d, env=env, capture_output=True, timeout=900)
        open(d + '/suite.log', 'wb').write(p.stdout + b'\n==== stderr ====\n' + p.stderr)
        open(d + '/rc.txt', 'w').write(str(p.returncode) + '\n')
        print('%s rc=%d exe=%s' % (n, p.returncode, sha(exe)[:8]))


def summary(out, n):
    d = os.path.join(out, n)
    text = open(d + '/suite.log', 'rb').read().decode('latin1').replace('\r', '')
    tests = re.findall(r'(?m)^\[test\] (\S+)$', text)
    fails = [l for l in text.split('\n') if 'ShaderCfgTests: failed' in l]
    f19 = [l for l in text.split('\n') if l.startswith('[f19]')]
    spv = {f: sha(d + '/spv/' + f) for f in os.listdir(d + '/spv') if f.endswith('.spv')}
    return tests, fails, f19, spv


def read(out):
    ok = True
    s = {n: summary(out, n) for n in ('base', 'f0', 'fu', 'f1') if os.path.exists(os.path.join(out, n, 'suite.log'))}
    for n, (tests, fails, f19, spv) in s.items():
        print('%s: tests %d, failure lines %d, spv %d' % (n, len(tests), len(fails), len(spv)))
        for l in fails[:5]:
            print('    FAIL', l[:200])
        for l in f19:
            print('   ', l)
        ok &= not fails and len(tests) > 0
    b = s['base'][3]
    for n in ('f0', 'fu', 'f1'):
        spv = s[n][3]
        diff = sorted(f for f in set(b) | set(spv) if b.get(f) != spv.get(f))
        print('%s: SPIR-V differing from base %d: %s' % (n, len(diff), ' '.join(diff)))
        if n != 'f1':
            ok &= not diff
        else:
            ok &= len(diff) == 4
    exp1 = ['C dref=1 manual=0, C_LZ dref=1 manual=0', 'k16UNorm+k8UNorm KYTY_FIX_F19=1: images=2 members=2 dref=0 manual=1',
            'k16UNorm+k32Float KYTY_FIX_F19=1: images=2 members=2 dref=2 manual=0',
            'k32Float+k8UNorm KYTY_FIX_F19=1: images=2 members=2 dref=0 manual=1']
    exp0 = ['C dref=0 manual=1, C_LZ dref=0 manual=1', 'k16UNorm+k8UNorm KYTY_FIX_F19=0: images=2 members=2 dref=0 manual=1',
            'k16UNorm+k32Float KYTY_FIX_F19=0: images=2 members=2 dref=0 manual=1',
            'k32Float+k8UNorm KYTY_FIX_F19=0: images=2 members=2 dref=2 manual=0']
    for n, exp in (('f1', exp1), ('f0', exp0), ('fu', exp0)):
        j = '\n'.join(s[n][2])
        got = [e in j for e in exp]
        print('%s probe lines as expected: %s' % (n, got))
        ok &= all(got)
    print('ALL OK' if ok else 'NOT OK')
    return ok


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:] or ['base', 'f0', 'fu', 'f1'])
    else:
        sys.exit(0 if read(sys.argv[2]) else 1)
