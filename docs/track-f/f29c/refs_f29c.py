"""Track F link F29c (HPP-702): copy of refs_f29a.py with the names changed. Was: Track F link F29a (HPP-699): copy of refs_f24a.py with the names changed. Was: Track F link F24a (HPP-658): check every '<commit>:<path>:<line>' reference of f29a.md (general rule 24(1)): the
reference must have a row in refs_f29a.tsv (written by gen_refs_f29a.py from anchors), the line holds the anchor and the
next line holds the +1 anchor (stripped; an empty +1 anchor means the next line is empty). Copy of refs_f25a.py with
the report scan added. ASCII code, UTF-8 data.

    python refs_f29a.py <f29a.md> [--tsv refs_f29a.tsv] [--out refs_f29a.out.txt]
"""
import os
import re
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REF = re.compile(r'`([0-9a-f]{8}):([A-Za-z0-9_./-]+):([0-9]+)`')


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    report = argv[0]
    tsv = argv[argv.index('--tsv') + 1] if '--tsv' in argv else os.path.join(here, 'refs_f29c.tsv')
    rows = {}
    for raw in open(tsv, encoding='utf-8'):
        raw = raw.rstrip('\n')
        if raw.strip():
            c, p, ln, a, b = (raw.split('\t') + ['', '', '', '', ''])[:5]
            rows[(c, p, ln)] = (a, b)
    refs = sorted(set(REF.findall(open(report, encoding='utf-8').read())))
    out = []
    ok = True
    cache = {}
    for c, p, ln in refs:
        if (c, p, ln) not in rows:
            ok = False
            out.append('FAIL %s:%s:%s no anchor row' % (c, p, ln))
            continue
        a, b = rows[(c, p, ln)]
        if (c, p) not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True)
            cache[(c, p)] = r.stdout.decode('utf-8', 'replace').split('\n') if r.returncode == 0 else None
        lines = cache[(c, p)]
        i = int(ln)
        if lines is None or i < 1 or i >= len(lines):
            good, why = False, 'missing'
        else:
            g0 = a.strip() in lines[i - 1].strip()
            l1 = lines[i].strip()
            g1 = (l1 == '') if b.strip() == '' else (b.strip() in l1)
            good = g0 and g1
            why = 'anchor %s, +1 %s' % ('ok' if g0 else 'NO', 'ok' if g1 else 'NO')
        ok &= good
        out.append('%s %s:%s:%s %s' % ('ok' if good else 'FAIL', c, p, ln, why))
    out.append('REFS %d, %s' % (len(refs), 'ALL OK' if ok and refs else 'FAILED'))
    txt = '\n'.join(out) + '\n'
    if '--out' in argv:
        open(argv[argv.index('--out') + 1], 'w', encoding='ascii', newline='\n').write(txt)
    sys.stdout.write(txt)
    return 0 if ok and refs else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
