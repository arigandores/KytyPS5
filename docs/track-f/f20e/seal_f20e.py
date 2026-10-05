"""F20e (HPP-624): diffs of the f20e harness against seal 2 of F20c, the seal lines, the anchor check of the seal refs.  ASCII only."""
import difflib
import hashlib
import os
import subprocess
import sys

S = 'C:/kyty/f287/f20c'
D = 'C:/kyty/f287/f20e'
PAIRS = [('pred/f20c_seal.md', 'pred/f20e_seal.md'), ('f20c_read.py', 'f20e_read.py'), ('test_f20c_read.py', 'test_f20e_read.py'),
         ('sens_f20c.py', 'sens_f20e.py'), ('test_tools_f20c.py', 'test_tools_f20e.py'), ('go_f20c.sh', 'go_f20e.sh'),
         ('launch_f20c.sh', 'launch_f20e.sh'), ('wait_f20c.sh', 'wait_f20e.sh'), ('post_f20c.sh', 'post_f20e.sh'),
         ('queue_f20c.py', 'queue_f20e.py'), ('watch_f20c.py', 'watch_f20e.py'), ('enter_scene.py', 'enter_scene.py'),
         ('procload.py', 'procload.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
         ('manifest_fs4c.py', 'manifest_fs4c.py'), ('sheet142.py', 'sheet142.py'), ('run_safety99.py', 'run_safety99.py'),
         ('gates_default.txt', 'gates_default.txt'), ('guard_f20c.py', 'guard_f20e.py'), ('test_guard_f20c.py', 'test_guard_f20e.py')]
EXTRA = ['C:/kyty/scripts/s51_vidglitch.py', D + '/test_f20e_read.out.txt', D + '/sens_f20e.out.txt', D + '/test_tools_f20e.out.txt',
         D + '/test_guard_f20e.out.txt', D + '/regress_f20e.txt']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    os.makedirs(D + '/seal_diff', exist_ok=True)
    seal = []
    summ = []
    for a, b in PAIRS:
        pa, pb = S + '/' + a, D + '/' + b
        la = open(pa, 'rb').read().decode('utf-8').splitlines(True)
        lb = open(pb, 'rb').read().decode('utf-8').splitlines(True)
        diff = list(difflib.unified_diff(la, lb, 'f20c/' + a, 'f20e/' + b, n=1))
        name = os.path.basename(b) + '.diff'
        with open(D + '/seal_diff/' + name, 'wb') as f:
            f.write(''.join(diff).encode('utf-8'))
        add = sum(1 for x in diff if x.startswith('+') and not x.startswith('+++'))
        rem = sum(1 for x in diff if x.startswith('-') and not x.startswith('---'))
        summ.append('%s -> %s: %s +%d -%d' % (a, b, 'SAME' if not diff else 'diff', add, rem))
        seal.append('seal: %s %s' % (sha(pb), pb))
    for p in EXTRA:
        seal.append('seal: %s %s' % (sha(p), p))
    with open(D + '/SEAL_LINES.txt', 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(seal) + '\n')
    with open(D + '/seal_diff/SUMMARY.txt', 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(summ) + '\n')
    print('\n'.join(summ))
    # anchors of the seal (rule 24(1)) at b5cec16e
    L = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', 'b5cec16e:docs/ROADMAP.md'],
                       capture_output=True).stdout.decode('utf-8').split('\n')
    A = [(23155, '543. **', '   (\u0430) **'), (23161, '   (\u0435) **', '   (\u0436) **'), (23159, '   (\u0433) **', '   (\u0434) **'),
         (23090, '   (\u0432) **', '      (1) '), (23178, '545. **', '   (\u0430) **'), (23194, '547. **', '   (\u0430) **')]
    ok = True
    for n, a, b in A:
        g = L[n - 1].startswith(a) and L[n].startswith(b)
        ok &= g
        print('anchor %d %s' % (n, 'ok' if g else 'MISMATCH'))
    print('ANCHORS %s' % ('ALL OK' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
