"""lvl_recount.py - S9r (HPP-432, Red Team): own recount of the T2 and U lists of seal 05b (item 355 (d), (e); item 362 (g)).
Every file under C:/kyty with mtime >= T0 (2026-09-30 23:41:52Z), ANY size and ANY extension except media / binaries /
archives, is read in binary chunks; every occurrence of b'Level has started: ' gives the name up to the end of the line;
every occurrence of b'ShaderSeed: compatibility=' gives the compatibility string.  Checks the lock and STOP between files.
Output: one TSV row per file with a hit, then a summary for the 10 T2 names, the pool-(A) names before them and the U names.
    python lvl_recount.py <out.tsv>
"""
import datetime
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
T0 = datetime.datetime(2026, 9, 30, 23, 41, 52, tzinfo=datetime.timezone.utc).timestamp()
SKIP_DIRS = ('C:/kyty/KytyPS5/ps5 em/games', 'C:/kyty/build', 'C:/kyty/KytyPS5/.git', 'C:/kyty/s288/s9r')
SKIP_EXT = ('.mp4', '.exe', '.dll', '.pdb', '.png', '.jpg', '.jpeg', '.bin', '.rdc', '.xz', '.zip', '.7z', '.obj', '.lib',
            '.pack', '.idx', '.sqlite', '.etl', '.nv12', '.spv', '.raw', '.pyc', '.ilk', '.exp', '.gz', '.mkv', '.avi',
            '.wav', '.dds', '.ktx', '.gnf', '.gnfp', '.pkg', '.sprx', '.prx', '.elf', '.self', '.at9', '.bk2', '.pkl', '.npy')
K_LVL = b'Level has started: '
K_CMP = b'ShaderSeed: compatibility='
CH = 64 << 20


def hits(path):
    names = {}
    cmp_ = set()
    with open(path, 'rb') as f:
        tail = b''
        while True:
            b = f.read(CH)
            if not b:
                break
            buf = tail + b
            for key, kind in ((K_LVL, 'l'), (K_CMP, 'c')):
                i = buf.find(key)
                while i >= 0:
                    j = buf.find(b'\n', i)
                    if j < 0:
                        break      # the line is completed in the next chunk (the tail keeps it)
                    v = buf[i + len(key):j].strip().decode('latin1')
                    if kind == 'l':
                        names[v] = names.get(v, 0) + 1
                    else:
                        cmp_.add(v)
                    i = buf.find(key, j)
            # keep the last 4 KiB that may hold an unfinished line; avoid double counting: cut at the last newline
            k = buf.rfind(b'\n')
            tail = buf[k + 1:] if k >= 0 else buf
            if len(tail) > (1 << 20):
                tail = tail[-4096:]
    return names, cmp_


def main():
    out = sys.argv[1]
    big = ('C:/kyty/s146', 'C:/kyty/s145', 'C:/kyty/p283', 'C:/kyty/f287', 'C:/kyty/s144')
    roots = sys.argv[2:] or ['C:/kyty']
    skip = SKIP_DIRS
    if roots == ['REST']:
        roots, skip = ['C:/kyty'], SKIP_DIRS + big
    rows = []
    nfiles = 0
    nbytes = 0
    for root, dirs, files in (w for rt in roots for w in os.walk(rt)):
        r = root.replace(os.sep, '/')
        if any(r == d or r.startswith(d + '/') for d in skip):
            dirs[:] = []
            continue
        for fn in files:
            if os.path.exists(LOCK) or os.path.exists(STOP):
                print('ABORT: lock or stop at file %d' % nfiles)
                return 5
            if fn.lower().endswith(SKIP_EXT):
                continue
            p = r + '/' + fn
            try:
                st = os.stat(p)
            except OSError:
                continue
            if st.st_mtime < T0 or st.st_size == 0:
                continue
            try:
                names, cmp_ = hits(p)
            except OSError as e:
                rows.append((p, st.st_size, 'UNREADABLE %s' % e, ''))
                continue
            nfiles += 1
            nbytes += st.st_size
            if names or cmp_:
                rows.append((p, st.st_size, ';'.join('%s=%d' % kv for kv in sorted(names.items())), '|'.join(sorted(cmp_))))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# files scanned %d bytes %d\n' % (nfiles, nbytes))
        for x in rows:
            f.write('%s\t%d\t%s\t%s\n' % x)
    print('files scanned %d, %.1f GB, files with a hit %d' % (nfiles, nbytes / 1e9, len(rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
