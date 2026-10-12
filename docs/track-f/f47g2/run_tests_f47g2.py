"""F47g2 (HPP-828, ROADMAP s122 item 742(v)): copy of run_tests_f47g.py - the F47g2 worktree build (8bdc069a) against the
F47g run of the F47g build 1f9b5b77 (C:/kyty/f287/f47g/tests/f47g, itself = FS15a). Was:
F47g (HPP-824, ROADMAP s122 item 740(v)(1)): copy of run_tests_fs15a.py - the F47g worktree build (4aab9750) against the
FS15a run of the FS15 build 6beb3b73 (C:/kyty/f287/fs15a/tests/fs15). Was:
FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): shader_cfg_tests of the FS15 worktree build (6beb3b73) without the game.
Port of run_tests_fs14a_f29.py (FS14a): KYTY_TESTS_CONTINUE=1, KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR, all other KYTY_*
removed -> tests/fs15/; compared with the FS14a run of the FS14 build eb7e8b91 (C:/kyty/f287/fs15a/tests/fs15, the base
of FS15): rc, the number of "[test] " lines, "ShaderCfgTests: failed:" lines and the multiset of the lines with the word
"failed" (t3); the SPIR-V files byte for byte (t4, reference).
Rule 27: lock and STOP before the process. Prints ALL OK / FAIL."""
import collections
import hashlib
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/f47g/build'
OUT = 'C:/kyty/f287/f47g2/tests'
REF = 'C:/kyty/f287/f47g/tests/f47g'


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def failed_lines(text):
    return collections.Counter(l.strip() for l in text.split('\n') if 'failed' in l)


def main():
    ok = True
    o = os.path.join(OUT, 'f47g2')
    os.makedirs(o + '/spv', exist_ok=True)
    for f in os.listdir(o + '/spv'):
        os.remove(o + '/spv/' + f)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_TESTS_CONTINUE'] = '1'
    env['KYTY_TESTS_VERBOSE'] = '1'
    env['KYTY_TESTS_SPV_DIR'] = o + '/spv'
    out = os.path.join(o, 'log.txt')
    guard()
    with open(out, 'wb') as f:
        rc = subprocess.run([B + '/shader_cfg_tests.exe'], stdout=f, stderr=subprocess.STDOUT, cwd=B, env=env,
                            timeout=530).returncode
    open(os.path.join(o, 'rc.txt'), 'w', newline='\n').write('%d\n' % rc)
    open(os.path.join(o, 'exe_sha256.txt'), 'w', newline='\n').write(sha(B + '/shader_cfg_tests.exe') + '\n')
    text = open(out, 'rb').read().decode('utf-8', 'replace')
    ref = open(REF + '/log.txt', 'rb').read().decode('utf-8', 'replace')
    ref_rc = int(open(REF + '/rc.txt').read().strip())
    n, rn = text.count('[test] '), ref.count('[test] ')
    f, rf = failed_lines(text), failed_lines(ref)
    fl, rfl = text.count('ShaderCfgTests: failed:'), ref.count('ShaderCfgTests: failed:')
    for name, a, b in (('rc', rc, ref_rc), ('[test] lines', n, rn), ('ShaderCfgTests: failed: lines', fl, rfl),
                       ('lines with failed', sum(f.values()), sum(rf.values())),
                       ('failed multiset equal', f == rf, True)):
        good = a == b
        ok &= good
        print('%s t3 shader_cfg_tests %s: f47g2 %s f47g %s' % ('OK  ' if good else 'FAIL', name, a, b))
    ok &= n > 0
    mine = sorted(os.listdir(o + '/spv'))
    refs = sorted(os.listdir(REF + '/spv'))
    diff = [x for x in sorted(set(mine) | set(refs)) if x not in mine or x not in refs or
            sha(o + '/spv/' + x) != sha(REF + '/spv/' + x)]
    agg_m = hashlib.sha256(''.join(sha(o + '/spv/' + x) for x in mine).encode()).hexdigest()
    agg_r = hashlib.sha256(''.join(sha(REF + '/spv/' + x) for x in refs).encode()).hexdigest()
    t4 = len(mine) > 0 and not diff
    ok &= t4
    print('%s t4 SPIR-V f47g2 %d f47g %d differing %d aggregate %s / %s' % (
        'OK  ' if t4 else 'FAIL', len(mine), len(refs), len(diff), agg_m[:8], agg_r[:8]))
    for x in diff[:20]:
        print('   differs:', x)
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
