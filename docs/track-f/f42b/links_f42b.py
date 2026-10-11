# F42b (HPP-780, Red Team): copy of the F42a links_f42a.py with f42a->f42b in ALL lines.
"""F42b (HPP-779): map of the references <commit>:<path>:<line> of docs/track-f/f42b.md (form of links_f38a.py).

    python links_f42b.py gen   <md> <tsv>   - every reference of the text (the full form `<commit>:<path>:<line>` and the
                                              short form `:<line>` / `<file>` :<line> after a full one is NOT mapped -
                                              only the full form) -> tsv rows commit, path, line, anchor (line text, first
                                              90 characters), next (line + 1, first 90 characters), from git show;
    python links_f42b.py check <md> <tsv>   - every full reference of the text is a tsv row, and every tsv row: the line
                                              starts with the anchor and the next line with the +1 text; ALL OK / FAIL.
Real git (C:/Program Files/Git/cmd/git.exe), repository C:/kyty/KytyPS5.
"""
import re
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REF = re.compile(r'`([0-9a-f]{8}):([A-Za-z0-9_./-]+):(\d+)`')


def lines_of(cache, c, path):
    key = (c, path)
    if key not in cache:
        out = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % key], capture_output=True).stdout
        cache[key] = [x.rstrip('\r') for x in out.decode('utf-8').split('\n')]
    return cache[key]


def refs_of(md):
    text = open(md, encoding='utf-8').read()
    seen = []
    for m in REF.finditer(text):
        r = (m.group(1), m.group(2), int(m.group(3)))
        if r not in seen:
            seen.append(r)
    return seen


def esc(s):
    return s.replace('\\', '\\\\').replace('\t', '\\t')


def unesc(s):
    out = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            out.append('\t' if s[i + 1] == 't' else s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def main():
    mode, md, tsv = sys.argv[1:4]
    cache = {}
    if mode == 'gen':
        rows = []
        for c, path, n in refs_of(md):
            ls = lines_of(cache, c, path)
            anchor = ls[n - 1][:90] if len(ls) >= n else ''
            nxt = ls[n][:90] if len(ls) > n else ''
            rows.append('%s\t%s\t%d\t%s\t%s' % (c, path, n, esc(anchor), esc(nxt)))
            print('%s:%s:%d  %s' % (c, path, n, anchor.strip()[:80]))
        open(tsv, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
        print('generated %d' % len(rows))
        return 0
    table = {}
    for line in open(tsv, encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) == 5:
            table[(f[0], f[1], int(f[2]))] = (unesc(f[3]), unesc(f[4]))
    ok = True
    refs = refs_of(md)
    for r in refs:
        if r not in table:
            ok = False
            print('MISSING %s:%s:%d' % r)
    for (c, path, n), (anchor, nxt) in table.items():
        ls = lines_of(cache, c, path)
        good = len(ls) > n and ls[n - 1].startswith(anchor) and ls[n].startswith(nxt) and anchor != ''
        ok &= good
        print('%s %s:%s:%d' % ('OK  ' if good else 'FAIL', c, path, n))
    print('text refs %d map rows %d' % (len(refs), len(table)))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
