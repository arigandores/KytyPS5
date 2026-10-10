"""F37a (HPP-761): writes links_f37a.py - the references <commit>:<path>:<line> of docs/track-f/f37a.md with the anchor (the
line, up to 90 characters) and the +1 text (the next line, up to 90 characters), taken once from git show of the commit.
Usage: gen_links_f37a.py <out links_f37a.py>"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = 'ee9632be'
SITES = [
    ('src/kernel/fileSystem.cpp', [762, 764, 765, 775, 776, 777, 782, 828, 829, 852, 854, 867, 941, 979, 980, 989, 990, 991, 1002, 1004, 1010]),
    ('src/common/file.cpp', [163, 201, 207]),
    ('src/common/platform/sysWindowsFileIO.cpp', [68, 76]),
    ('src/libs/libKernel.cpp', [1418, 1436, 1930, 2993, 2995, 2996, 2224, 3144, 3146, 3369, 3430, 3431, 3441]),
    ('src/libs/errno.h', [20, 24, 182, 192, 61]),
    ('src/common/assert.h', [53]),
    ('src/common/assert.cpp', [22, 116]),
]


def main():
    out = []
    for path, lines in SITES:
        t = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (C, path)], capture_output=True, check=True).stdout.decode('utf-8').split('\n')
        for n in lines:
            out.append((C, path, n, t[n - 1][:90], t[n][:90]))
    body = []
    body.append('"""F37a (HPP-761): check of the references <commit>:<path>:<line> of docs/track-f/f37a.md - the line starts with the anchor')
    body.append('and the next line starts with the +1 text (git show of the commit, real git). Generated once by gen_links_f37a.py.')
    body.append('Prints one line per reference and ALL OK / FAIL."""')
    body.append('import subprocess')
    body.append('')
    body.append("G = 'C:/Program Files/Git/cmd/git.exe'")
    body.append("REPO = 'C:/kyty/KytyPS5'")
    body.append('REFS = [')
    for r in out:
        body.append('    %r,' % (r,))
    body.append(']')
    body.append('')
    body.append('')
    body.append('def main():')
    body.append('    ok = True')
    body.append('    for c, p, n, a, b in REFS:')
    body.append("        t = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split(chr(10))")
    body.append("        la, lb = t[n - 1] if n - 1 < len(t) else '', t[n] if n < len(t) else ''")
    body.append('        good = la.startswith(a) and lb.startswith(b)')
    body.append('        ok &= good')
    body.append("        print('%s:%s:%d anchor %s +1 %s' % (c, p, n, 'OK' if la.startswith(a) else 'FAIL', 'OK' if lb.startswith(b) else 'FAIL'))")
    body.append("    print('ALL OK' if ok else 'FAIL')")
    body.append('')
    body.append('')
    body.append("if __name__ == '__main__':")
    body.append('    main()')
    body.append('')
    open(sys.argv[1], 'wb').write(chr(10).join(body).encode('utf-8'))
    for r in out:
        print('%s:%s:%d | %s | +1 %s' % (r[1].split('/')[-1], r[0], r[2], r[3].strip(), r[4].strip()))


if __name__ == '__main__':
    main()
