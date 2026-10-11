# F42b (HPP-780, Red Team): copy of the F42a run_tests_f42a.py with f42a->f42b in ALL lines (own build).
"""F42b (HPP-779, ROADMAP s122 item 694(g)(2)): shader_cfg_tests of the F42b worktree build (copy of the cfg part of
the F38a run_tests_f38a.py): KYTY_TESTS_CONTINUE=1, KYTY_TESTS_VERBOSE=1, every other KYTY_* removed, at KYTY_FIX_F20 unset
and =1 -> tests/cfg_log_<v>.txt; compared with the FS12a log of the FS12 build (docs/track-f/fs12a/tests/fs12/log.txt):
rc, the number of "[test] " lines and the multiset of the lines with the word "failed". Prints ALL OK / FAIL.
Rule 27: lock and STOP before every process."""
import collections
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/f42b/build'
OUT = 'C:/kyty/f287/f42b/tests'
REF = 'C:/kyty/KytyPS5/docs/track-f/fs12a/tests/fs12'


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def env_base():
    return {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}


def run(exe, env, out, args=()):
    guard()
    with open(out, 'wb') as f:
        rc = subprocess.run([exe] + list(args), stdout=f, stderr=subprocess.STDOUT, cwd=B, env=env,
                            timeout=530).returncode
    return rc


def failed_lines(text):
    return collections.Counter(l.strip() for l in text.split('\n') if 'failed' in l)


def main():
    os.makedirs(OUT, exist_ok=True)
    ok = True
    for v in (None, '1'):
        env = env_base()
        if v is not None:
            env['KYTY_FIX_F20'] = v
        name = 'unset' if v is None else v
        env['KYTY_TESTS_CONTINUE'] = '1'
        env['KYTY_TESTS_VERBOSE'] = '1'
        out = os.path.join(OUT, 'cfg_log_%s.txt' % name)
        rc = run(B + '/shader_cfg_tests.exe', env, out)
        open(os.path.join(OUT, 'cfg_rc_%s.txt' % name), 'w').write('%d\n' % rc)
        text = open(out, 'rb').read().decode('utf-8', 'replace')
        ref = open(REF + '/log.txt', 'rb').read().decode('utf-8', 'replace')
        ref_rc = int(open(REF + '/rc.txt').read().strip())
        n, rn = text.count('[test] '), ref.count('[test] ')
        f, rf = failed_lines(text), failed_lines(ref)
        vname = name
        for name, a, b in (('rc', rc, ref_rc), ('[test] lines', n, rn), ('failed lines', sum(f.values()), sum(rf.values())),
                           ('failed multiset equal', f == rf, True)):
            good = a == b
            ok &= good
            print('%s shader_cfg_tests KYTY_FIX_F20=%s %s: f42b %s fs12 %s' % ('OK  ' if good else 'FAIL', vname, name, a, b))
        for l in sorted(f):
            print('  failed: %s' % l[:150])
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
