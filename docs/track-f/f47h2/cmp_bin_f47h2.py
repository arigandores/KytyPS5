"""cmp_bin_f47h2.py - F47h2 (HPP-829): copy of cmp_bin_f47h.py; own build of 8bdc069a (worktree f47h) against the F47g2 binary 86e42e36 (worktree f47g). Was: F47h (HPP-825): own clean build of 1f9b5b77 against the F47g binary e1c50d15.

    python cmp_bin_f47h.py <F47g exe> <own exe>

Prints both sha256, then swaps the worktree name f47h -> f47g (same length) in the own binary and classifies every
remaining differing byte: PE header, the SDL revision string, the debug directory (timestamp / PDB GUID), the 8-hex
anonymous-namespace hashes "?A0x........" (clang-cl derives them from the source path), other; and per PE section.
"""
import hashlib
import re
import struct
import sys
from collections import Counter

a = open(sys.argv[1], 'rb').read()
b0 = open(sys.argv[2], 'rb').read()
print('F47g', hashlib.sha256(a).hexdigest(), len(a))
print('own ', hashlib.sha256(b0).hexdigest(), len(b0))
print('path strings: f47g in F47g', a.count(b'f47g'), '; f47h in own', b0.count(b'f47h'))
b = b0.replace(b'f47h', b'f47g')
print('own with f47h->f47g sha256', hashlib.sha256(b).hexdigest(), 'equal' if a == b else 'differs')
assert len(a) == len(b)
pe = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, pe + 6)[0]
opt = struct.unpack_from('<H', a, pe + 20)[0]
secs = []
for k in range(nsec):
    o = pe + 24 + opt + 40 * k
    name = a[o:o + 8].rstrip(b'\0').decode()
    _, _, rs, rp = struct.unpack_from('<IIII', a, o + 8)
    secs.append((name, rp, rs))


def sec(i):
    for n, rp, rs in secs:
        if rp <= i < rp + rs:
            return n
    return 'hdr'


d = [i for i in range(len(a)) if a[i] != b[i]]
cls = Counter()
for i in d:
    if b'?A0x' in a[max(0, i - 12):i + 9]:
        cls['anon-namespace hash ?A0x (path)'] += 1
    elif re.search(rb'KytyPS5-2026-09-15-6a2987a-\d+-g', a[max(0, i - 40):i + 1]):
        cls['SDL revision string'] += 1
    elif i < 0x400:
        cls['PE header timestamp'] += 1
    elif b'RSDS' in a[i - 40:i + 8] or b'\x00\x00\x00\x00\x02\x00\x00\x00' in a[i - 16:i + 16]:
        cls['debug directory (timestamp / PDB GUID)'] += 1
    else:
        cls['other'] += 1
print('differing bytes', len(d))
for k, v in sorted(cls.items()):
    print('  %-42s %d' % (k, v))
print('by section', dict(Counter(sec(i) for i in d)))
print('.text differing bytes', sum(1 for i in d if sec(i) == '.text'))
for x, nm in ((a, 'F47g'), (b0, 'own ')):
    print(nm, 'version strings', sorted(set(m.group(0).decode() for m in re.finditer(rb'KytyPS5-2026-09-15-6a2987a-\d+-g[0-9a-f]+', x))))
