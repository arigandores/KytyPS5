# F46a (HPP-798): copy of the F44a run_tests_f44a.py, executable lines f44a -> f46a (paths); only the mode cfg is used.
# F44a (HPP-791): copy of the F40a2 run_tests_f40a2.py, executable lines f40a2 -> f44a (paths, names). Was:
# F44a (HPP-791): copy of the F40a run_tests_f40a.py, executable lines f40a -> f44a (paths, names). Was:
"""F44a (HPP-791): tests of the F40a2 worktree build without the game.
  python run_tests_f46a.py kfs   - kernel_file_system_tests at KYTY_FIX_F25 unset / 0 / 1 (all other KYTY_* removed),
                                   --filesystem-only (rc 0, all cases passed) and full (only the known socket failure
                                   'guest PEEK and WAITALL', the same on the base - F15c, F15d) -> tests/kfs_<form>_<v>.txt
  python run_tests_f46a.py cfg   - shader_cfg_tests (KYTY_TESTS_CONTINUE=1, KYTY_TESTS_VERBOSE=1, all other KYTY_*
                                   removed) -> tests/cfg_log.txt; compared with the FS12a log of the FS12 build
                                   (docs/track-f/fs12a/tests/fs12/log.txt): rc, the number of "[test] " lines and the
                                   multiset of the lines with the word "failed". Prints ALL OK / FAIL.
Rule 27: lock and STOP before every process."""
import collections
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/f46a/build'
OUT = 'C:/kyty/f287/f46a/tests'
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


KNOWN_SOCKET = 'KernelFileSystemTests: failed: guest PEEK and WAITALL preserve the wake bytes'


def failed_lines(text):
    return collections.Counter(l.strip() for l in text.split('\n') if 'failed' in l)


def main():
    os.makedirs(OUT, exist_ok=True)
    ok = True
    if sys.argv[1] == 'kfs':
        for v in (None, '0', '1'):
            env = env_base()
            if v is not None:
                env['KYTY_FIX_F25'] = v
            name = 'unset' if v is None else v
            for form, args in (('fsonly', ['--filesystem-only']), ('full', [])):
                out = os.path.join(OUT, 'kfs_%s_%s.txt' % (form, name))
                rc = run(B + '/kernel_file_system_tests.exe', env, out, args)
                text = open(out, 'rb').read().decode('utf-8', 'replace')
                fl = failed_lines(text)
                if form == 'fsonly':
                    # the file part: all cases pass
                    good = rc == 0 and sum(fl.values()) == 0 and 'KernelFileSystemTests: all cases passed' in text
                else:
                    # the full set: only the known socket failure (F15c, F15d: the same on the base, not a file read)
                    good = set(fl) == {KNOWN_SOCKET}
                ok &= good
                print('%s kernel_file_system_tests %s KYTY_FIX_F25=%s rc %d failed-lines %s' % (
                    'OK  ' if good else 'FAIL', form, name, rc, dict(fl)))
    else:
        env = env_base()
        env['KYTY_TESTS_CONTINUE'] = '1'
        env['KYTY_TESTS_VERBOSE'] = '1'
        out = os.path.join(OUT, 'cfg_log.txt')
        rc = run(B + '/shader_cfg_tests.exe', env, out)
        open(os.path.join(OUT, 'cfg_rc.txt'), 'w').write('%d\n' % rc)
        text = open(out, 'rb').read().decode('utf-8', 'replace')
        ref = open(REF + '/log.txt', 'rb').read().decode('utf-8', 'replace')
        ref_rc = int(open(REF + '/rc.txt').read().strip())
        n, rn = text.count('[test] '), ref.count('[test] ')
        f, rf = failed_lines(text), failed_lines(ref)
        for name, a, b in (('rc', rc, ref_rc), ('[test] lines', n, rn), ('failed lines', sum(f.values()), sum(rf.values())),
                           ('failed multiset equal', f == rf, True)):
            good = a == b
            ok &= good
            print('%s shader_cfg_tests %s: f46a %s fs12 %s' % ('OK  ' if good else 'FAIL', name, a, b))
        for l in sorted(f):
            print('  failed: %s' % l[:150])
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
