"""togit1b.py - session 146 link 1b (HPP-395): copy the files of link 1b into C:/kyty/KytyPS5/docs/session-146/step1b/ (byte copies)
after a privacy scan of every file by the expressions of C:/kyty/scrub/ (never printed, only their numbers).  A file with a hit is not
copied and is named.  The port of step0/togit146.py (no times.txt masking: step1b/times.txt names no foreign process).  ASCII output.
usage: togit1b.py <out.txt>"""
import hashlib
import os
import re
import sys

SRC = 'C:/kyty/s146/'
DST = 'C:/kyty/KytyPS5/docs/session-146/step1b/'
FILES = ('sc146.py', 'go146a.sh', 'test_sc146.py', 'test_go146a.py', 'mut_sc146.py', 'FACTS.md', 'pred/02_sc146.md',
         'step2/gate146.py', 'step2/call_one.sh', 'step2/test_gate146.py',
         'step1b/p1b_sc.py', 'step1b/p1b_path.py', 'step1b/p1b_tsc.py', 'step1b/p1b_mut.py', 'step1b/mk_seal146_02.py',
         'step1b/skipfx1b.py', 'step1b/skipfx1b.out.txt', 'step1b/test_sc146.out.txt', 'step1b/test_gate146.out.txt',
         'step1b/test_go146a.out.txt', 'step1b/test_fgcpu146.out.txt', 'step1b/test_tools146.out.txt',
         'step1b/regress145.out.txt', 'step1b/calib146.out.txt', 'step1b/check1b146.out.txt', 'step1b/checkseal146.out.txt',
         'step1b/mut_only1b.txt', 'step1b/mut_only1b.log', 'step1b/facts1b.md', 'step1b/times.txt', 'step1b/togit1b.py')


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
    lines = ['togit1b: %d expressions (exprs.txt + checks.txt of C:/kyty/scrub; %d not compilable as Python regex)' % (
        len(xs), sum(1 for x in xs if x is None))]
    copied = hits = 0
    for f in FILES:
        data = open(SRC + f, 'rb').read()
        bad = [i + 1 for i, x in enumerate(xs) if x is not None and x.search(data)]
        if bad:
            hits += 1
            lines.append('HIT expr %s in %s - not copied (stays local)' % (','.join('#%d' % i for i in bad), f))
            continue
        b = DST + f
        os.makedirs(os.path.dirname(b), exist_ok=True)
        open(b, 'wb').write(data)
        copied += 1
        lines.append('copied %s sha256 %s' % (f, hashlib.sha256(data).hexdigest()[:16]))
    lines.append('togit1b: copied %d, not copied by a hit %d, of %d' % (copied, hits, len(FILES)))
    open(sys.argv[1], 'w', encoding='ascii', newline='\n').write('\n'.join(lines) + '\n')
    print(lines[0])
    print('\n'.join(x for x in lines if x.startswith('HIT')))
    print(lines[-1])


if __name__ == '__main__':
    main()
