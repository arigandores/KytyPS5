"""Session 145 step 0 (HPP-350): copy the step 0 files into C:/kyty/KytyPS5/docs/session-145/step0/ (byte copies) after a
privacy scan of every file by the expressions of C:/kyty/scrub/ (the list stays out of git; its expressions are never printed,
only their numbers).  A file with a hit is not copied and is named.  ASCII output.  usage: togit145.py <out.txt>"""
import hashlib
import os
import re
import shutil
import sys

SRC = 'C:/kyty/s145/'
DST = 'C:/kyty/KytyPS5/docs/session-145/step0/'
ROOT_FILES = ('go145a.sh', 'sc145.py', 'test_sc145.py', 'mut_sc145.py', 'test_go145a.py', 'fgcpu145.py', 'test_fgcpu145.py',
              'cachemf145.py', 'lockcheck145.py', 'test_tools145.py', 'enter_scene.py', 'procload.py', 'idle142.py',
              'run_safety99.py', 'launch_run.py', 'gates_default.txt', 'sheet142.py', 'mut_sc145.txt', 'mut_run.log',
              'FACTS.md')
STEP2 = ('next_one.sh', 'call_one.sh', 'wait_one.sh', 'pre_one.sh', 'apichk145.py', 'gate145.py', 'test_gate145.py',
         'table145.py')
STEP0 = ('times.txt', 'f6scan145.py', 'f6scan145.out.txt', 'vuid145.py', 'vuid145.out.txt', 'livecache145.out.txt',
         'mk_sc145.py', 'mk_test_sc145.py', 'partE.py.txt', 'mk_go145a.py', 'mk_wrap145.py', 'mk_mut145.py', 'mkseal145.py',
         'mkseal145.out.txt', 'seal_template.md', 'mut_screen1.txt', 'mut_screen1.log', 'mut_screen2.txt', 'mut_screen2.log',
         'mut_run_aborted1.log', 'test_sc145.out.txt', 'test_go145a.out.txt', 'test_fgcpu145.out.txt', 'test_tools145.out.txt',
         'test_gate145.out.txt', 'regress144.out.txt', 'regress143.out.txt', 'regress142.out.txt', 'calib145.out.txt',
         'check1b145.out.txt', 'checkseal145.out.txt', 'summary145_empty.txt', 'dry145.out.txt', 'togit145.py')


def exprs():
    out = []
    for name in ('exprs.txt', 'checks.txt'):
        p = 'C:/kyty/scrub/' + name
        if not os.path.isfile(p):
            continue
        for line in open(p, encoding='utf-8'):
            s = line.rstrip('\r\n')
            if not s or s.startswith('#'):
                continue
            try:
                out.append(re.compile(s.encode('utf-8')))
            except re.error:
                out.append(None)
    return out


def main():
    xs = exprs()
    lines = ['togit145: %d expressions (exprs.txt + checks.txt of C:/kyty/scrub; %d not compilable as Python regex)' % (
        len(xs), sum(1 for x in xs if x is None))]
    pairs = [(SRC + f, DST + f) for f in ROOT_FILES] + [(SRC + 'step2/' + f, DST + 'step2/' + f) for f in STEP2] + \
        [(SRC + 'step0/' + f, DST + 'step0/' + f) for f in STEP0] + [(SRC + 'pred/01_sc145.md', DST + 'pred/01_sc145.md')]
    copied = hits = 0
    for a, b in pairs:
        data = open(a, 'rb').read()
        bad = [i + 1 for i, x in enumerate(xs) if x is not None and x.search(data)]
        if bad:
            hits += 1
            lines.append('HIT expr %s in %s - not copied (stays local)' % (','.join('#%d' % i for i in bad), a[len(SRC):]))
            continue
        os.makedirs(os.path.dirname(b), exist_ok=True)
        shutil.copyfile(a, b)
        copied += 1
        lines.append('copied %s sha256 %s' % (a[len(SRC):], hashlib.sha256(data).hexdigest()[:16]))
    lines.append('togit145: copied %d, not copied by a hit %d, of %d' % (copied, hits, len(pairs)))
    open(sys.argv[1], 'w', encoding='ascii', newline='\n').write('\n'.join(lines) + '\n')
    print(lines[0])
    print('\n'.join(x for x in lines if x.startswith('HIT')))
    print(lines[-1])


if __name__ == '__main__':
    main()
