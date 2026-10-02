"""shalist_f2c.py - the content list of one cache directory for F2c (HPP-310; ROADMAP p.228(v), F2b RC4): every file under
the directory (recursive), its path relative to the directory ('/'), size and sha256; sorted by path.  One ASCII line:
"files N bytes B listsha <sha256 of the list>" - the list sha does not depend on mtime, so a copy and its return compare
equal byte for byte.  READ ONLY.  --out <file> also writes the list (one "rel<TAB>size<TAB>sha256" line per file).

    python shalist_f2c.py <dir> [--out <list.txt>]

rc 0 - line printed (a missing directory prints "files 0 bytes 0 absent listsha <sha of the empty list>"); rc 2 - usage.
"""
import hashlib
import os
import sys

CHUNK = 1 << 22


def listing(root):
    rows = []
    if not os.path.isdir(root):
        return rows, False
    for d, _, fs in os.walk(root):
        for n in fs:
            p = os.path.join(d, n)
            h = hashlib.sha256()
            with open(p, 'rb') as f:
                while True:
                    b = f.read(CHUNK)
                    if not b:
                        break
                    h.update(b)
            rows.append((os.path.relpath(p, root).replace('\\', '/'), os.path.getsize(p), h.hexdigest()))
    rows.sort()
    return rows, True


def text_of(rows):
    return ''.join('%s\t%d\t%s\n' % r for r in rows)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0].startswith('--'):
        print('usage: shalist_f2c.py <dir> [--out <list.txt>]')
        return 2
    rows, present = listing(a[0])
    t = text_of(rows)
    if '--out' in a:
        with open(a[a.index('--out') + 1], 'w', encoding='utf-8', newline='\n') as f:
            f.write(t)
    print('files %d bytes %d%s listsha %s' % (len(rows), sum(r[1] for r in rows), '' if present else ' absent',
                                             hashlib.sha256(t.encode('utf-8')).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
