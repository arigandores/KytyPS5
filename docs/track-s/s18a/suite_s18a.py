"""S18a (HPP-642, ROADMAP s122 item 569(d)(1)(3)): shader_cfg_tests of the S18a worktree, form of suite_fs8a.py run 'fu'
(one process, all KYTY_* removed, KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR=<run>/spv).
Readings: rc 0 and 0 lines 'ShaderCfgTests: failed:' (the known-failure list of HANDOFF s4 is compared by name: the FS8a
suite C:/kyty/f287/fs8a/suite/fu had 0 such lines on 130 tests); test names of FS8a fu all present in S18a; information:
SPIR-V files of S18a vs FS8a fu by name and sha256 (the test numbering of files may shift with the new tests - not a gate).
Usage: python suite_s18a.py <shader_cfg_tests.exe> <out>. Rule 27: lock and STOP before the process.
"""
import hashlib
import os
import re
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
FS8A = 'C:/kyty/f287/fs8a/suite/fu'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def summary(d):
    text = open(d + '/suite.log', 'rb').read().decode('latin1').replace(chr(13), '')
    rc = int(open(d + '/rc.txt').read())
    tests, fails, cur = [], [], None
    for line in text.split(chr(10)):
        m = re.match(r'^\[test\] (\S+)$', line)
        if m:
            cur = m.group(1)
            tests.append(cur)
        elif 'ShaderCfgTests: failed: ' in line:
            fails.append((cur, line.split('ShaderCfgTests: failed: ', 1)[1]))
    spv = sorted((f for f in os.listdir(d + '/spv') if f.endswith('.spv')), key=lambda f: int(f[:-4]))
    return {'rc': rc, 'tests': tests, 'fails': fails, 'spv': {f: sha('%s/spv/%s' % (d, f)) for f in spv},
            'replay_lines': text.count('ShaderReplay')}


def main():
    exe, out = sys.argv[1:3]
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(5)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)
    d = out + '/fu'
    os.makedirs(d + '/spv', exist_ok=True)
    for f in os.listdir(d + '/spv'):
        os.remove(d + '/spv/' + f)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update({'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_VERBOSE': '1', 'KYTY_TESTS_SPV_DIR': d + '/spv'})
    t0 = time.time()
    p = subprocess.run([exe], cwd=d, env=env, capture_output=True, timeout=900)
    open(d + '/suite.log', 'wb').write(p.stdout + b'\n==== stderr ====\n' + p.stderr)
    open(d + '/rc.txt', 'w').write('%d\n' % p.returncode)
    print('fu rc=%s wall=%.1f s exe=%s' % (p.returncode, time.time() - t0, sha(exe)[:8]))
    s, f = summary(d), summary(FS8A)
    ok = s['rc'] == 0 and not s['fails']
    print('S18a: rc %d, tests %d, failed lines %d %s, spv %d, lines with ShaderReplay %d' % (
        s['rc'], len(s['tests']), len(s['fails']), s['fails'][:5], len(s['spv']), s['replay_lines']))
    print('FS8a: rc %d, tests %d, failed lines %d, spv %d' % (f['rc'], len(f['tests']), len(f['fails']), len(f['spv'])))
    missing = [t for t in f['tests'] if t not in s['tests']]
    new = [t for t in s['tests'] if t not in f['tests']]
    print('FS8a tests missing in S18a: %d %s' % (len(missing), missing[:10]))
    print('tests new in S18a: %d %s' % (len(new), ' '.join(new)))
    ok &= not missing
    same_name = [n for n in f['spv'] if n in s['spv']]
    eq = [n for n in same_name if f['spv'][n] == s['spv'][n]]
    fs = sorted(f['spv'].values())
    ss = sorted(s['spv'].values())
    import collections
    cf, cs = collections.Counter(fs), collections.Counter(ss)
    print('information: SPIR-V same name %d, byte-equal by name %d; FS8a SPIR-V contents found in S18a %d of %d' % (
        len(same_name), len(eq), sum((cf & cs).values()), len(fs)))
    print('exe', exe, sha(exe))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
