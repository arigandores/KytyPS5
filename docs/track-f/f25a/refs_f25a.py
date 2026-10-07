"""Track F link F25a (HPP-660): check every '<commit>:<path>:<line>' reference of f25a.md (rule 24(1)): the line holds the anchor and
the next line holds the +1 anchor (stripped of leading blanks; an empty +1 anchor means the next line is empty).  ASCII code, UTF-8 data.

    python refs_f25a.py [--tsv refs_f25a.tsv] [--out refs_f25a.txt]
"""
import os
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    tsv = argv[argv.index('--tsv') + 1] if '--tsv' in argv else os.path.join(here, 'refs_f25a.tsv')
    out = []
    ok = True
    n = 0
    cache = {}
    for raw in open(tsv, encoding='utf-8'):
        raw = raw.rstrip('\n')
        if not raw.strip():
            continue
        c, p, ln, a, b = (raw.split('\t') + ['', '', '', '', ''])[:5]
        n += 1
        key = (c, p)
        if key not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True)
            cache[key] = r.stdout.decode('utf-8', 'replace').split('\n') if r.returncode == 0 else None
        lines = cache[key]
        i = int(ln)
        if lines is None or i < 1 or i >= len(lines):
            good = False
            why = 'missing'
        else:
            l0 = lines[i - 1].strip()
            l1 = lines[i].strip()
            g0 = a.strip() in l0
            g1 = (l1 == '') if b.strip() == '' else (b.strip() in l1)
            good = g0 and g1
            why = 'anchor %s, +1 %s' % ('ok' if g0 else 'NO', 'ok' if g1 else 'NO')
        ok &= good
        out.append('%s %s:%s:%s %s' % ('ok' if good else 'FAIL', c, p, ln, why))
    out.append('REFS %d, %s' % (n, 'ALL OK' if ok and n else 'FAILED'))
    txt = '\n'.join(out) + '\n'
    if '--out' in argv:
        open(argv[argv.index('--out') + 1], 'w', encoding='ascii', newline='\n').write(txt)
    sys.stdout.write(txt)
    return 0 if ok and n else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
