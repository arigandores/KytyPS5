"""Session 145 step 0b (HPP-350, ROADMAP s122 item 288): copy the step 0b files into
C:/kyty/KytyPS5/docs/session-145/step0b/ (byte copies) after a privacy scan of every file by the expressions of C:/kyty/scrub/
(the list stays out of git; its expressions are never printed, only their numbers).  A file with a hit is not copied and is
named.  ASCII output.  usage: togit145b.py <out.txt>"""
import hashlib
import os
import re
import sys

SRC = 'C:/kyty/s145/'
DST = 'C:/kyty/KytyPS5/docs/session-145/step0b/'
FILES = ['sc145.py', 'go145a.sh', 'test_sc145.py', 'test_go145a.py', 'mut_sc145.py', 'FACTS.md', 'pred/02_sc145.md',
         'step2/gate145.py', 'step2/test_gate145.py', 'step2/call_one.sh'] + ['step0b/' + f for f in (
    'times.txt', 'priv0b.out.txt', 'pg0b.py', 'pt0b.py', 'pp0b.py', 'facts0b.py', 'togit145b.py', 'test_sc145.out.txt',
    'test_go145a.out.txt', 'test_go145a.try1_env.txt', 'test_gate145.out.txt', 'test_gate145.try1.txt', 'mut_only0b.txt',
    'mut_only0b.log', 'regress144.out.txt', 'start_dry0b.out.txt', 'recheck144_dry.out.txt', 'checkseal145.out.txt',
    'dry145.out.txt', 'seal_template02.md', 'mkseal145b.out.txt', 'priv0b.py', 'mkseal145b.py')]


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
            if s.startswith('regex:') and '==>' in s:
                s = s[len('regex:'):s.rindex('==>')]
            try:
                out.append(re.compile(s.encode('utf-8')))
            except re.error:
                out.append(None)
    return out


def main():
    xs = exprs()
    lines = ['togit145b: %d expressions (exprs.txt without "regex:" and "==>..." + checks.txt of C:/kyty/scrub; %d not '
             'compilable as Python regex)' % (len(xs), sum(1 for x in xs if x is None))]
    copied = hits = 0
    for f in FILES:
        a, b = SRC + f, DST + f
        data = open(a, 'rb').read()
        bad = [i + 1 for i, x in enumerate(xs) if x is not None and x.search(data)]
        if bad:
            hits += 1
            lines.append('HIT expr %s in %s - not copied (stays local)' % (','.join('#%d' % i for i in bad), f))
            continue
        os.makedirs(os.path.dirname(b), exist_ok=True)
        open(b, 'wb').write(data)
        copied += 1
        lines.append('copied %s sha256 %s' % (f, hashlib.sha256(data).hexdigest()[:16]))
    lines.append('togit145b: copied %d, not copied by a hit %d, of %d' % (copied, hits, len(FILES)))
    open(sys.argv[1], 'w', encoding='ascii', newline='\n').write('\n'.join(lines) + '\n')
    print(lines[0])
    print('\n'.join(x for x in lines if x.startswith('HIT')))
    print(lines[-1])


if __name__ == '__main__':
    main()
