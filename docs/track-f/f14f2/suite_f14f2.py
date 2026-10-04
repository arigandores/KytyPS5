"""F14f2 (HPP-546, ROADMAP s122 item 443(g)): own repeat of item 443(v)(3) - full shader_cfg_tests runs and SPIR-V
of the set, written independently of suite_f14e2.py (no import, own readings).

Mode 'suite' (6 runs, every KYTY_* removed, KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 KYTY_TESTS_SPV_DIR=<run>/spv):
  bu base exe unset, b0 base =0, b1 base =1, fu link unset, f0 link =0, f1 link =1.
  Readings: (s1) 0 'ShaderCfgTests: failed:' lines in every run, rc 0; (s2) link has exactly one [test] more than base,
  the new one is TestF19NullComparisonImage and it is the last; (s3) N = number of base dumps; bu = b0 byte for byte
  (unset = 0 on the base); fu and f0: dumps 0..N-1 = bu byte for byte; f1: dumps 0..N-1 = b1 byte for byte;
  (s4) link runs have N+4 dumps; (s5) [f19] null lines: f1 alone native=1 manual_images=0 dref=1 manual=0 (C, C_LZ),
  shared native=2 manual_images=0 dref=2 manual=0; f0/fu alone the same, shared native=0 manual_images=2 dref=0 manual=2;
  (s6) alone dumps (N, N+2) f1 = f0 = fu byte for byte; shared dumps (N+1, N+3) f0 = fu, f1 != f0.
Mode 'mut <name> <exe> <expect>': 3 runs (=1, =0, unset) of a mutant exe; prints failing lines per run;
  expect is e.g. '1:fail,0:pass,u:pass' and the mode prints CAUGHT/NOT CAUGHT by that expectation.
Rule 27: lock and STOP before every process.
"""
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
OUT = 'C:/kyty/f287/f14f2/suite'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(name, exe, f19):
    if os.path.exists(LOCK):
        print('HALT lock'); sys.exit(3)
    if os.path.exists(STOP):
        print('HALT stop'); sys.exit(4)
    d = OUT + '/' + name
    os.makedirs(d + '/spv', exist_ok=True)
    for f in os.listdir(d + '/spv'):
        os.remove(d + '/spv/' + f)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update({'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_VERBOSE': '1', 'KYTY_TESTS_SPV_DIR': d + '/spv'})
    if f19 is not None:
        env['KYTY_FIX_F19'] = f19
    p = subprocess.run([exe], cwd=d, env=env, capture_output=True, timeout=600)
    open(d + '/suite.log', 'wb').write(p.stdout + b'\n==== stderr ====\n' + p.stderr)
    txt = (p.stdout + p.stderr).decode('utf-8', 'replace').replace(chr(13), '')  # stdout of the exe is CRLF
    tests = re.findall(r'^\[test\] (\S+)', txt, re.M)
    failed = re.findall(r'^ShaderCfgTests: failed: (.*)$', txt, re.M)
    null = re.findall(r'^\[f19\] null T#.*$', txt, re.M)
    spv = sorted([f for f in os.listdir(d + '/spv') if f.endswith('.spv')], key=lambda s: int(s.split('.')[0]))
    print('%s rc=%d exe=%s KYTY_FIX_F19=%s tests=%d failed=%d spv=%d' % (
        name, p.returncode, sha(exe)[:8], 'unset' if f19 is None else f19, len(tests), len(failed), len(spv)))
    for f in failed:
        print('   failed:', f)
    for l in null:
        print('   ' + l)
    return {'rc': p.returncode, 'tests': tests, 'failed': failed, 'null': null, 'spv': spv, 'dir': d + '/spv'}


def blob(r, i):
    return open('%s/%d.spv' % (r['dir'], i), 'rb').read()


def suite(base_exe, link_exe):
    R = {}
    R['bu'] = run('bu', base_exe, None)
    R['b0'] = run('b0', base_exe, '0')
    R['b1'] = run('b1', base_exe, '1')
    R['fu'] = run('fu', link_exe, None)
    R['f0'] = run('f0', link_exe, '0')
    R['f1'] = run('f1', link_exe, '1')
    ok = True
    s1 = all(R[k]['rc'] == 0 and not R[k]['failed'] for k in R)
    print('(s1) rc 0 and 0 failing lines in 6 runs:', s1); ok &= s1
    s2 = all(R[k]['tests'] == R['bu']['tests'] + ['TestF19NullComparisonImage'] for k in ('fu', 'f0', 'f1')) and \
        all(R[k]['tests'] == R['bu']['tests'] for k in ('b0', 'b1'))
    print('(s2) link tests = base tests + TestF19NullComparisonImage last:', s2, len(R['bu']['tests']),
          len(R['f1']['tests'])); ok &= s2
    N = len(R['bu']['spv'])
    s3 = True
    for k in ('b0',):
        s3 &= len(R[k]['spv']) == N and all(blob(R[k], i) == blob(R['bu'], i) for i in range(N))
    for k in ('fu', 'f0'):
        s3 &= all(blob(R[k], i) == blob(R['bu'], i) for i in range(N))
    s3 &= len(R['b1']['spv']) == N and all(blob(R['f1'], i) == blob(R['b1'], i) for i in range(N))
    nd1 = sum(blob(R['b1'], i) != blob(R['bu'], i) for i in range(N))
    print('(s3) N=%d; b0=bu, fu/f0 0..N-1 = bu, f1 0..N-1 = b1:' % N, s3, '| b1 vs bu differing files', nd1); ok &= s3
    s4 = all(len(R[k]['spv']) == N + 4 for k in ('fu', 'f0', 'f1'))
    print('(s4) link runs N+4 dumps:', s4); ok &= s4
    A1 = 'images=1 native=1 manual_images=0 dref=1 manual=0'
    S1 = 'images=2 native=2 manual_images=0 dref=2 manual=0'
    S0 = 'images=2 native=0 manual_images=2 dref=0 manual=2'
    def nl(k, v):
        return ['[f19] null T# alone C KYTY_FIX_F19=%s: %s' % (v, A1),
                '[f19] null T# + k16UNorm shared sampler C KYTY_FIX_F19=%s: %s' % (v, S1 if v == '1' else S0),
                '[f19] null T# alone C_LZ KYTY_FIX_F19=%s: %s' % (v, A1),
                '[f19] null T# + k16UNorm shared sampler C_LZ KYTY_FIX_F19=%s: %s' % (v, S1 if v == '1' else S0)]
    s5 = R['f1']['null'] == nl('f1', '1') and R['f0']['null'] == nl('f0', '0') and R['fu']['null'] == nl('fu', '0')
    print('(s5) null probe lines as decided p.443(b):', s5); ok &= s5
    s6 = all(blob(R['f1'], N + j) == blob(R['f0'], N + j) == blob(R['fu'], N + j) for j in (0, 2)) and \
        all(blob(R['f0'], N + j) == blob(R['fu'], N + j) and blob(R['f1'], N + j) != blob(R['f0'], N + j) for j in (1, 3))
    print('(s6) alone dumps f1=f0=fu, shared f0=fu and f1!=f0:', s6); ok &= s6
    print('ALL OK' if ok else 'FAIL')
    return ok


def mut(name, exe, expect):
    exp = dict(x.split(':') for x in expect.split(','))
    res = {}
    for v, f19 in (('1', '1'), ('0', '0'), ('u', None)):
        r = run('%s_%s' % (name, v), exe, f19)
        res[v] = 'fail' if (r['failed'] or r['rc'] != 0) else 'pass'
    caught = all(res[v] == exp[v] for v in exp)
    print('%s result %s expect %s -> %s' % (name, ','.join('%s:%s' % kv for kv in res.items()), expect,
                                           'CAUGHT' if caught else 'NOT CAUGHT'))
    return caught


if __name__ == '__main__':
    if sys.argv[1] == 'suite':
        sys.exit(0 if suite(sys.argv[2], sys.argv[3]) else 1)
    if sys.argv[1] == 'mut':
        sys.exit(0 if mut(sys.argv[2], sys.argv[3], sys.argv[4]) else 1)
