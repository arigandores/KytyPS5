"""FS13a (HPP-787, ROADMAP s122 item 697(g)(1)): tests of the FS13 worktree build without the game. Port of the F38a
run_tests_f38a.py (paths fs13a; t4 SPIR-V and the FixF25 line added).
  python run_tests_fs13a.py kfs  - kernel_file_system_tests at KYTY_FIX_F25 unset / 0 / 1 (all other KYTY_* removed):
                                   --filesystem-only - rc 0, 0 lines with "failed", "KernelFileSystemTests: all cases
                                   passed" (the member); full - only the known socket failure 'guest PEEK and WAITALL'
                                   (reference, the same on FS12 - F15c, F15d, F38a) -> tests/kfs_<form>_<v>.txt
  python run_tests_fs13a.py cfg  - shader_cfg_tests (KYTY_TESTS_CONTINUE=1, KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR, all
                                   other KYTY_* removed) -> tests/fs13/; compared with the FS12a run of the FS12 build
                                   730ed40a (C:/kyty/f287/fs12a/tests/fs12, the base of FS13): rc, the number of "[test] "
                                   lines, "ShaderCfgTests: failed:" lines and the multiset of the lines with the word
                                   "failed" (t3); the SPIR-V files byte for byte (t4).
Rule 27: lock and STOP before every process. Prints ALL OK / FAIL."""
import collections
import hashlib
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
B = 'C:/kyty/f287/fs13a/build'
OUT = 'C:/kyty/f287/fs13a/tests'
REF = 'C:/kyty/f287/fs12a/tests/fs12'


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


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
        open(os.path.join(OUT, 'kfs_exe_sha256.txt'), 'w', newline='\n').write(
            sha(B + '/kernel_file_system_tests.exe') + '\n')
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
                    good = rc == 0 and sum(fl.values()) == 0 and 'KernelFileSystemTests: all cases passed' in text
                else:
                    good = set(fl) == {KNOWN_SOCKET}
                ok &= good
                print('%s kernel_file_system_tests %s KYTY_FIX_F25=%s rc %d failed-lines %s; FixF25 lines %s' % (
                    'OK  ' if good else 'FAIL', form, name, rc, dict(fl),
                    sorted(set(l.strip() for l in text.split('\n') if l.startswith('FixF25: mode=')))))
    else:
        o = os.path.join(OUT, 'fs13')
        os.makedirs(o + '/spv', exist_ok=True)
        for f in os.listdir(o + '/spv'):
            os.remove(o + '/spv/' + f)
        env = env_base()
        env['KYTY_TESTS_CONTINUE'] = '1'
        env['KYTY_TESTS_VERBOSE'] = '1'
        env['KYTY_TESTS_SPV_DIR'] = o + '/spv'
        out = os.path.join(o, 'log.txt')
        rc = run(B + '/shader_cfg_tests.exe', env, out)
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
            print('%s t3 shader_cfg_tests %s: fs13 %s fs12 %s' % ('OK  ' if good else 'FAIL', name, a, b))
        ok &= n > 0
        mine = sorted(os.listdir(o + '/spv'))
        refs = sorted(os.listdir(REF + '/spv'))
        diff = [x for x in sorted(set(mine) | set(refs)) if x not in mine or x not in refs or
                sha(o + '/spv/' + x) != sha(REF + '/spv/' + x)]
        agg_m = hashlib.sha256(''.join(sha(o + '/spv/' + x) for x in mine).encode()).hexdigest()
        agg_r = hashlib.sha256(''.join(sha(REF + '/spv/' + x) for x in refs).encode()).hexdigest()
        t4 = len(mine) > 0 and not diff
        ok &= t4
        print('%s t4 SPIR-V fs13 %d fs12 %d differing %d aggregate %s / %s' % (
            'OK  ' if t4 else 'FAIL', len(mine), len(refs), len(diff), agg_m[:8], agg_r[:8]))
        for x in diff[:20]:
            print('   differs:', x)
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
