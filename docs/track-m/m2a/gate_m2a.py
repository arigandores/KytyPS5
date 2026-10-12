"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(i), (iv)): GPU test gate of the translator themes of wave 1.
Each case of shader_recompiler_compute_tests --m-wave1-list runs in its own process, every KYTY_* variable removed:
  z  - all knobs unset (the FS15 answer of the theme)        -> must DIFFER from the reference (reproduction)
  o  - KYTY_M_<theme of the case>=1, the other knobs unset   -> must EQUAL the reference (rc 0 and "ALL OK")
and --m-wave1-cache at unset and at each knob = 1 (token rule). Member: every case z rc != 0 and o rc 0.
Usage: python gate_m2a.py <exe> <out dir> [--only-o] [--label L]. Lock and STOP are checked before every process.
Prints a table and ALL OK / FAIL; writes <out>/gate.tsv and the logs."""
import argparse
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def run(exe, args, extra, log):
    guard()
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(extra)
    try:
        p = subprocess.run([exe] + args, capture_output=True, timeout=180, env=env, cwd=os.path.dirname(exe))
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out = 'timeout', (e.stdout or b'') + (e.stderr or b'')
    open(log, 'wb').write(out)
    return rc, out.decode('utf-8', 'replace')


def first_fail(text):
    for line in text.split('\n'):
        if 'FAIL' in line or 'mismatch' in line or 'expected' in line:
            return line.strip()[:160]
    return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('exe')
    ap.add_argument('out')
    ap.add_argument('--only-o', action='store_true')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    exe = os.path.abspath(args.exe)
    print('exe', exe, hashlib.sha256(open(exe, 'rb').read()).hexdigest())
    rc, text = run(exe, ['--m-wave1-list'], {}, args.out + '/list.txt')
    names = [l.strip() for l in text.split('\n') if l.strip().startswith('MW1')]
    print('cases', len(names))
    ok = True
    rows = []
    for name in names:
        theme = re.match(r'MW1(T\d{3})', name).group(1)
        r = [name, theme]
        if not args.only_o:
            rc0, t0 = run(exe, ['--m-wave1-case', name], {}, '%s/%s_z.txt' % (args.out, name))
            ok0 = rc0 != 0 and 'ALL OK' not in t0
            r += [str(rc0), 'DIFFERS' if ok0 else 'EQUAL', first_fail(t0)]
            ok &= ok0
        rc1, t1 = run(exe, ['--m-wave1-case', name], {'KYTY_M_' + theme: '1'}, '%s/%s_o.txt' % (args.out, name))
        ok1 = rc1 == 0 and 'ALL OK' in t1
        r += [str(rc1), 'EQUAL' if ok1 else 'DIFFERS', first_fail(t1)]
        ok &= ok1
        rows.append(r)
        print('\t'.join(r))
    for setting in [None] + THEMES:
        extra = {} if setting is None else {'KYTY_M_' + setting: '1'}
        rc, t = run(exe, ['--m-wave1-cache'], extra, '%s/cache_%s.txt' % (args.out, setting or 'unset'))
        good = rc == 0 and 'ALL OK' in t
        ok &= good
        lines = [l for l in t.split('\n') if l.startswith('[mw1]')]
        print('cache', setting or 'unset', 'rc', rc, 'OK' if good else 'FAIL', ' | '.join(lines)[:400])
    hdr = ['case', 'theme'] + ([] if args.only_o else ['rc_z', 'z_vs_ref', 'z_fail']) + ['rc_o', 'o_vs_ref', 'o_fail']
    with open(args.out + '/gate.tsv', 'w', newline='\n') as f:
        f.write('\t'.join(hdr) + '\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
