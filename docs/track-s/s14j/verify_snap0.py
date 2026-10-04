"""S14j (HPP-533): the snap0 manifest check before and after the dump (ROADMAP s122 item 430(g)(1)): sha256 of
C:/kyty/s288/snap0/MANIFEST.txt must be d8ca8c8e...; every listed file (path size sha256) must have the listed size and
sha256; no file of snap0 outside the list (MANIFEST.txt itself excepted). Read-only.

    python verify_snap0.py [snap0 dir]   -> last line 'MANIFEST MATCH <n>/<n> extra=0' or 'MANIFEST MISMATCH ...'
"""
import hashlib
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/snap0'
MAN = os.path.join(ROOT, 'MANIFEST.txt')
EXPECT_MAN = 'd8ca8c8e'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


man_sha = sha(MAN)
print('MANIFEST.txt sha256 %s (expected prefix %s): %s' % (man_sha, EXPECT_MAN, 'ok' if man_sha.startswith(EXPECT_MAN) else 'BAD'))
rows = []
with open(MAN, 'rb') as f:
    for line in f.read().decode('utf-8').splitlines():
        if line.strip():
            rel, size, digest = line.rsplit(' ', 2)
            rows.append((rel, int(size), digest))
bad = []
for rel, size, digest in rows:
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        bad.append(('missing', rel))
    elif os.path.getsize(p) != size:
        bad.append(('size', rel))
    elif sha(p) != digest:
        bad.append(('sha256', rel))
listed = {r[0].replace('\\', '/') for r in rows}
extra = []
for d, _, fs in os.walk(ROOT):
    for name in fs:
        rel = os.path.relpath(os.path.join(d, name), ROOT).replace('\\', '/')
        if rel != 'MANIFEST.txt' and rel not in listed:
            extra.append(rel)
for b in bad[:20]:
    print('BAD', *b)
for e in extra[:20]:
    print('EXTRA', e)
ok = man_sha.startswith(EXPECT_MAN) and not bad and not extra
n = len(rows)
print(('MANIFEST MATCH %d/%d extra=0' % (n, n)) if ok else
      ('MANIFEST MISMATCH ok=%d/%d bad=%d extra=%d' % (n - len(bad), n, len(bad), len(extra))))
sys.exit(0 if ok else 1)
