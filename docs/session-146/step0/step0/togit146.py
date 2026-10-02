"""togit146.py - session 146 step 0 (HPP-386): copy the step 0 files into C:/kyty/KytyPS5/docs/session-146/step0/ (byte copies) after
a privacy scan of every file by the expressions of C:/kyty/scrub/ (the list stays out of git; its expressions are never printed, only
their numbers).  A file with a hit is not copied and is named.  step0/times.txt is copied with the process names of its foreign-CPU
rows masked as <app> (general rule 28; FACTS 0.7(1)) - its copy sha differs from the local file and both are printed.  launch_run.py
stays local (as in s145).  ASCII output.  usage: togit146.py <out.txt>"""
import hashlib
import os
import re
import shutil
import sys

SRC = 'C:/kyty/s146/'
DST = 'C:/kyty/KytyPS5/docs/session-146/step0/'
ROOT_FILES = ('go146i.sh', 'i146_read.py', 'test_i146.py', 'go146a.sh', 'sc146.py', 'test_sc146.py', 'mut_sc146.py', 'mut_sc146.txt',
              'test_go146a.py', 'fgcpu146.py', 'test_fgcpu146.py', 'cachemf146.py', 'lockcheck146.py', 'test_tools146.py',
              'tiles146.py', 'enter_scene.py', 'procload.py', 'idle142.py', 'run_safety99.py', 'gates_default.txt', 'sheet142.py',
              'sheetpair_f3d.py', 'shalist_f2c.py', 'score_i146_v.txt', 'tiles_i146_v.txt', 'FACTS.md')
STEP2 = ('next_one.sh', 'call_one.sh', 'wait_one.sh', 'pre_one.sh', 'apichk146.py', 'gate146.py', 'test_gate146.py')
STEP0 = ('setup146.py', 'setup146.out.txt', 'lvl146.py', 'lvl146.out.txt', 'port_sc146.py', 'port_tools146.py', 'port_gate146.py',
         'port_tests146.py', 'port_testgo146.py', 'partf146.py.txt', 'gen_test146.py', 'mk_mut146.py', 'mk_seal146.py',
         'mk_seal_i146.py', 'fix_pf.py', 'fix_pf2.py', 'fix_pt.py', 'fix_ptg.py', 'fix_run1.py', 'tilereg146.py',
         'tilereg146_1.out.txt', 'tilereg146_2.out.txt', 'regress145.out.txt', 'calib146.out.txt', 'check1b146.out.txt',
         'jsonsrc145.py', 'jsonsrc145.out.txt', 'test_sc146.out.txt', 'test_gate146.out.txt', 'test_go146a.out.txt',
         'test_fgcpu146.out.txt', 'test_tools146.out.txt', 'test_i146.out.txt', 'mut_screen1.txt', 'mut_screen1.log',
         'mut_screen2.txt', 'mut_screen2.log', 'mut_screen3.txt', 'mut_screen3.log', 'mut_run.log', 'mut_full.sh',
         'run1/mut_sc146.run1.txt', 'run1/mut_run.run1.log', 'checkseal146.out.txt', 'dry146.out.txt', 'summary146_empty.txt',
         'next_i146.sh', 'wait_i146.sh', 'togit146.py')
RX_NAME = re.compile(rb'(?<![<\w])([A-Za-z][\w.\-]*):(\d+):(\d+\.\d{3})')


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


def mask_times(data):
    out = []
    n = 0
    for line in data.split(b'\n'):
        if b'foreign cpu' in line:
            line, k = RX_NAME.subn(rb'<app>:\2:\3', line)
            n += k
        out.append(line)
    return b'\n'.join(out), n


def main():
    xs = exprs()
    lines = ['togit146: %d expressions (exprs.txt + checks.txt of C:/kyty/scrub; %d not compilable as Python regex)' % (
        len(xs), sum(1 for x in xs if x is None))]
    pairs = [(SRC + f, DST + f) for f in ROOT_FILES] + [(SRC + 'step2/' + f, DST + 'step2/' + f) for f in STEP2] + \
        [(SRC + 'step0/' + f, DST + 'step0/' + f) for f in STEP0] + \
        [(SRC + 'pred/00_i146.md', DST + 'pred/00_i146.md'), (SRC + 'pred/01_sc146.md', DST + 'pred/01_sc146.md'),
         (SRC + 'step0/times.txt', DST + 'step0/times.txt')]
    copied = hits = 0
    for a, b in pairs:
        data = open(a, 'rb').read()
        note = ''
        if a.endswith('step0/times.txt'):
            new, n = mask_times(data)
            note = ' (local sha256 %s; %d process names masked as <app>)' % (hashlib.sha256(data).hexdigest()[:16], n)
            data = new
        bad = [i + 1 for i, x in enumerate(xs) if x is not None and x.search(data)]
        if bad:
            hits += 1
            lines.append('HIT expr %s in %s - not copied (stays local)' % (','.join('#%d' % i for i in bad), a[len(SRC):]))
            continue
        os.makedirs(os.path.dirname(b), exist_ok=True)
        open(b, 'wb').write(data)
        copied += 1
        lines.append('copied %s sha256 %s%s' % (a[len(SRC):], hashlib.sha256(data).hexdigest()[:16], note))
    lines.append('togit146: copied %d, not copied by a hit %d, of %d' % (copied, hits, len(pairs)))
    open(sys.argv[1], 'w', encoding='ascii', newline='\n').write('\n'.join(lines) + '\n')
    print(lines[0])
    print('\n'.join(x for x in lines if x.startswith('HIT') or 'masked' in x))
    print(lines[-1])


if __name__ == '__main__':
    main()
