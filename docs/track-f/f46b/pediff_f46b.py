"""Track F, F46b (HPP-799): why two kyty_emulator.exe builds of the same tree differ. Prints the PE header fields that differ
(TimeDateStamp), the section table of both (virtual / raw size), and the printable strings (>= 6 bytes) whose counts differ
between the two files (the multiset difference) - the named reason for "sha256 != copy".

    python pediff_f46b.py <A.exe> <B.exe>
"""
import collections
import re
import struct
import sys


def pe(data):
    off = struct.unpack_from('<I', data, 0x3c)[0]
    nsec = struct.unpack_from('<H', data, off + 6)[0]
    stamp = struct.unpack_from('<I', data, off + 8)[0]
    optsz = struct.unpack_from('<H', data, off + 20)[0]
    sec = off + 24 + optsz
    out = []
    for i in range(nsec):
        s = sec + 40 * i
        name = data[s:s + 8].rstrip(b'\0').decode('ascii', 'replace')
        vsize, vaddr, rsize, rptr = struct.unpack_from('<IIII', data, s + 8)
        out.append((name, vsize, vaddr, rsize, rptr))
    return stamp, out


def strings(data):
    return collections.Counter(m.group(0) for m in re.finditer(rb'[\x20-\x7e]{6,}', data))


def main():
    a = open(sys.argv[1], 'rb').read()
    b = open(sys.argv[2], 'rb').read()
    sa, ta = pe(a)
    sb, tb = pe(b)
    print('A %s len %d TimeDateStamp 0x%08x' % (sys.argv[1], len(a), sa))
    print('B %s len %d TimeDateStamp 0x%08x' % (sys.argv[2], len(b), sb))
    print('section  A(vsize rsize)  B(vsize rsize)  text-equal')
    for x, y in zip(ta, tb):
        same = ''
        if x[0] == y[0]:
            same = a[x[4]:x[4] + x[3]] == b[y[4]:y[4] + y[3]]
        print('%-8s %10d %10d  %10d %10d  %s' % (x[0], x[1], x[3], y[1], y[3], same))
    ca, cb = strings(a), strings(b)
    only_a = ca - cb
    only_b = cb - ca
    print('strings with a different count: A-only %d, B-only %d' % (sum(only_a.values()), sum(only_b.values())))
    for s, n in sorted(only_a.items())[:40]:
        print('  A x%d %r' % (n, s[:160]))
    for s, n in sorted(only_b.items())[:40]:
        print('  B x%d %r' % (n, s[:160]))


main()
