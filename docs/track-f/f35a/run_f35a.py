# F35a (HPP-755, ROADMAP s122 item 685(v)(2)): shader_cfg_tests runs of the F35a builds without the game; the form of
# C:/kyty/f287/fs11a/run_tests_fs11a.py (all KYTY_* removed, then KYTY_TESTS_CONTINUE=1, KYTY_TESTS_VERBOSE=1 and the
# value of KYTY_FIX_F19 under test).
"""Usage:
  python run_f35a.py full <label> <exe> <0|1>   - the full set -> tests/<label>_f19<v>/{log.txt,rc.txt,exe_sha256.txt}
  python run_f35a.py filt <label> <exe> <0|1>   - KYTY_TESTS_FILTER=TestF22 -> tests/<label>_filt_f19<v>/...
  python run_f35a.py cmp <base> <label>          - for v in 0, 1: rc, "[test] " lines (label = base + 1), the
                                                   multiset of lines with the word "failed" (label = base, 0 new);
                                                   prints ALL OK only if both values hold.
Rule 27: lock and STOP before every process.
"""
import collections
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
OUT = 'C:/kyty/f287/f35a/tests'


def guard():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(5)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(out, exe, f19, filt):
    os.makedirs(out, exist_ok=True)
    guard()
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_TESTS_CONTINUE'] = '1'
    env['KYTY_TESTS_VERBOSE'] = '1'
    env['KYTY_FIX_F19'] = f19
    if filt:
        env['KYTY_TESTS_FILTER'] = 'TestF22'
    r = subprocess.run([exe], capture_output=True, text=True, cwd=os.path.dirname(exe), env=env, errors='replace')
    log = r.stdout + r.stderr
    open(out + '/log.txt', 'w', encoding='utf-8', newline='\n').write(log)
    open(out + '/rc.txt', 'w', encoding='utf-8', newline='\n').write('%d\n' % r.returncode)
    open(out + '/exe_sha256.txt', 'w', encoding='utf-8', newline='\n').write(sha(exe) + '\n')
    s = summary(out)
    print(out, 'rc', s[0], 'tests', s[1], 'failed-lines', sum(s[2].values()))
    for line in log.splitlines():
        if line.startswith('[f22]') or 'failed' in line:
            print('  ', line)


def summary(out):
    log = open(out + '/log.txt', encoding='utf-8').read()
    rc = int(open(out + '/rc.txt').read())
    return (rc, len(re.findall(r'^\[test\] ', log, re.M)),
            collections.Counter(l for l in log.splitlines() if 'failed' in l))


def cmp(base, label):
    ok = True
    for v in ('0', '1'):
        b = summary('%s/%s_f19%s' % (OUT, base, v))
        t = summary('%s/%s_f19%s' % (OUT, label, v))
        new = t[2] - b[2]
        gone = b[2] - t[2]
        print('KYTY_FIX_F19=%s base rc=%d tests=%d failed-lines=%d | %s rc=%d tests=%d failed-lines=%d | new=%d gone=%d'
              % (v, b[0], b[1], sum(b[2].values()), label, t[0], t[1], sum(t[2].values()), sum(new.values()),
                 sum(gone.values())))
        for l in sorted(new):
            print('  NEW', l)
        for l in sorted(gone):
            print('  GONE', l)
        ok &= (t[0] == b[0] and t[1] == b[1] + 1 and not new and not gone)
    print('ALL OK' if ok else 'NOT OK')
    return ok


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode in ('full', 'filt'):
        label, exe, f19 = sys.argv[2], sys.argv[3], sys.argv[4]
        assert f19 in ('0', '1')
        out = '%s/%s_%sf19%s' % (OUT, label, 'filt_' if mode == 'filt' else '', f19)
        run(out, exe, f19, mode == 'filt')
    elif mode == 'cmp':
        sys.exit(0 if cmp(sys.argv[2], sys.argv[3]) else 1)
