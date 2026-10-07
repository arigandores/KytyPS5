# F24d (HPP-663, Red Team): references of f24d-review.md - <commit>:<path>:<line> with the anchor (the whole line,
# stripped) and the +1 control (the next whole line, stripped), read with git show (general rule 24(1)).
# Usage: python refs_f24d.py gen   -> writes refs_f24d.tsv from the list below (anchors read from git)
#        python refs_f24d.py check [file.md] -> re-reads every row of refs_f24d.tsv; if a .md is given, also requires
#        that every "<commit>:<path>:<line>" in it is a row of the tsv; prints ALL OK or FAILED.
#        python refs_f24d.py negctl -> the check on a copy of the tsv with one anchor changed; must print FAILED.
import subprocess, sys, re

REPO = 'C:/kyty/KytyPS5'
G = 'C:/Program Files/Git/cmd/git.exe'
TSV = 'C:/kyty/f287/f24d/refs_f24d.tsv'
LIST = [
    ('21f8ca76', 'src/graphics/host_gpu/regionManager.h', [51, 52, 246, 257, 262, 266, 275, 278, 291, 305]),
    ('21f8ca76', 'src/graphics/host_gpu/memoryTracker.cpp', [18]),
    ('21f8ca76', 'src/graphics/host_gpu/memoryTracker.h', [30]),
    ('21f8ca76', 'src/graphics/host_gpu/regionDefinitions.h', [28, 48, 51]),
    ('21f8ca76', 'src/graphics/host_gpu/regionManager.h', [172, 496]),
    ('21f8ca76', 'tests/B13EpochStand.cpp', [162, 163, 168, 169, 173, 174, 178, 181, 185]),
    ('707e0d7d', 'src/graphics/host_gpu/renderer/renderContext.cpp', [330, 333, 399]),
    ('707e0d7d', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', [3506, 3507, 3530, 3532, 3539, 3571]),
    ('fbae3a68', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', [3448, 3472, 3474]),
    ('707e0d7d', 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp', [1798, 1863, 2911]),
    ('707e0d7d', 'src/graphics/host_gpu/memoryTracker.cpp', [250]),
    ('fbae3a68', 'src/generate_version.cmake', [45]),
]
cache = {}


def lines(c, p):
    if (c, p) not in cache:
        cache[(c, p)] = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode(
            'utf-8').replace('\r\n', '\n').split('\n')
    return cache[(c, p)]


def check(rows):
    bad = 0
    for c, p, n, a, b in rows:
        L = lines(c, p)
        ok = L[n - 1].strip() == a and L[n].strip() == b
        if not ok:
            bad += 1
            print('MISMATCH %s:%s:%d' % (c, p, n))
    return bad


mode = sys.argv[1]
if mode == 'gen':
    out = []
    for c, p, ns in LIST:
        for n in ns:
            L = lines(c, p)
            out.append('\t'.join([c, p, str(n), L[n - 1].strip(), L[n].strip()]))
    open(TSV, 'wb').write(('\n'.join(out) + '\n').encode('utf-8'))
    print('rows', len(out))
else:
    rows = []
    for l in open(TSV, 'rb').read().decode('utf-8').split('\n'):
        if l:
            c, p, n, a, b = l.split('\t')
            rows.append((c, p, int(n), a, b))
    if mode == 'negctl':
        c, p, n, a, b = rows[0]
        rows[0] = (c, p, n, a + ' X', b)
    bad = check(rows)
    miss = 0
    if mode == 'check' and len(sys.argv) > 2:
        keys = {'%s:%s:%d' % (c, p, n) for c, p, n, a, b in rows}
        md = open(sys.argv[2], 'rb').read().decode('utf-8')
        for m in re.findall(r'`([0-9a-f]{8}:[A-Za-z0-9_./-]+:\d+)`', md):
            if m not in keys:
                miss += 1
                print('NOT IN TSV', m)
    print('REFS %d, mismatches %d, not in tsv %d' % (len(rows), bad, miss))
    print('ALL OK' if bad == 0 and miss == 0 else 'FAILED')
