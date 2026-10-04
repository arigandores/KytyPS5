# F15c (HPP-514, item 412(g)(3)): (1) kernel_file_system_tests --filesystem-only (the file system part without the socket
# part, which aborts in base and fix alike: 'guest PEEK and WAITALL preserve the wake bytes') for base/fix x none/0/1;
# (2) comparison of the 'failed:' lines of every run of tests_f15c.py and of (1): base vs fix at the same knob value.
import os, re, subprocess, sys
for st in ('base', 'fix'):
    for fx in ('none', '0', '1'):
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            print('HALT'); sys.exit(3)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
        if fx != 'none':
            env['KYTY_FIX_B4'] = fx
        p = subprocess.run([os.path.abspath(st + '/kernel_file_system_tests.exe'), '--filesystem-only'], cwd=os.path.abspath(st),
                           env=env, capture_output=True, timeout=300)
        out = (p.stdout + p.stderr).decode('utf-8', 'replace')
        open('runs/tests/%s_kfsonly_%s.txt' % (st, fx), 'w', encoding='utf-8', newline='\n').write(out)
        last = [l for l in out.splitlines() if l.strip()]
        print('%s kernel_file_system_tests --filesystem-only fix=%s rc=%s last=[%s]' % (st, fx, p.returncode, last[-1] if last else ''))


def failed(path):
    t = open(path, encoding='utf-8').read()
    return [l for l in t.splitlines() if 'failed:' in l]


ok = True
for exe in ('kernel_file_system_tests', 'shader_cfg_tests', 'kfsonly'):
    for fx in ('none', '0', '1'):
        b = failed('runs/tests/base_%s_%s.txt' % (exe, fx))
        f = failed('runs/tests/fix_%s_%s.txt' % (exe, fx))
        same = b == f
        ok &= same
        print('%s fix=%s failed-lines base %d fix %d equal %s %s' % (exe, fx, len(b), len(f), same, sorted(set(b))[:3]))
print('ALL OK' if ok else 'DIFF')
