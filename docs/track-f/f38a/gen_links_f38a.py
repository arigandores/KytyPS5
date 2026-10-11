"""F38a (HPP-763): generates links_f38a.py - the list of references <commit>:<path>:<line> of docs/track-f/f38a.md with
the anchor (first 90 characters of the line) and the +1 control (first 90 characters of the next line), read from
git show of the commit by the real git. Usage: gen_links_f38a.py <out links_f38a.py>"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = '730ed40a'
WANT = {
    'src/kernel/fileSystem.cpp': [110, 402, 406, 762, 764, 765, 775, 776, 777, 782, 826, 837, 850, 852, 854, 867, 941,
                                  977, 989, 990, 991, 1000, 1002, 1004, 1010],
    'src/libs/libKernel.cpp': [235, 262, 1418, 1435, 1436, 1930, 2148, 2224, 2968, 2993, 2995, 2996, 3141, 3144,
                               3146, 3248, 3369, 3395, 3430, 3431, 3441],
    'src/libs/errno.h': [20, 24, 61, 182, 192],
    'src/common/file.cpp': [163, 170],
    'src/common/platform/sysWindowsFileIO.cpp': [267],
    'tests/KernelFileSystemTests.cpp': [158],
}
# The F38a code commit (main): the places of the new state.
C2 = 'e9dd8604'
WANT2 = {
    'src/kernel/fileSystem.cpp': [127, 128, 133, 135, 427, 786, 787, 803, 804, 863, 864, 867, 868, 869, 870, 891, 892,
                                  893, 1028, 1033, 1034, 1035, 1037, 1053, 1054, 1055],
}


def main():
    refs = []
    for c, want in ((C, WANT), (C2, WANT2)):
        for path, lines in want.items():
            text = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, path)], capture_output=True).stdout
            rows = text.decode('utf-8').split('\n')
            for n in lines:
                refs.append((c, path, n, rows[n - 1].rstrip('\r')[:90], rows[n].rstrip('\r')[:90]))
    body = []
    body.append('"""F38a (HPP-763): check of the references <commit>:<path>:<line> of docs/track-f/f38a.md - the line '
                'starts with the anchor\nand the next line starts with the +1 text (git show of the commit, real git). '
                'Generated once by gen_links_f38a.py.\nPrints one line per reference and ALL OK / FAIL."""')
    body.append('import subprocess\n')
    body.append("G = 'C:/Program Files/Git/cmd/git.exe'")
    body.append("REPO = 'C:/kyty/KytyPS5'")
    body.append('REFS = [')
    for r in refs:
        body.append('    %r,' % (r,))
    body.append(']\n')
    body.append('''
def main():
    ok = True
    cache = {}
    for c, path, n, anchor, nxt in REFS:
        key = (c, path)
        if key not in cache:
            out = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % key], capture_output=True).stdout
            cache[key] = [x.rstrip('\\r') for x in out.decode('utf-8').split('\\n')]
        rows = cache[key]
        good = len(rows) > n and rows[n - 1].startswith(anchor) and rows[n].startswith(nxt)
        ok &= good
        print('%s %s:%s:%d' % ('OK  ' if good else 'FAIL', c, path, n))
    print('refs %d' % len(REFS))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
''')
    open(sys.argv[1], 'wb').write('\n'.join(body).encode('utf-8'))
    for r in refs:
        print('%s:%s:%d | %s | %s' % (r[1].split('/')[-1], '', r[2], r[3], r[4]))


if __name__ == '__main__':
    main()
