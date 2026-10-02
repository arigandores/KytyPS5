"""S7: byte difference between each duplicate compute recipe and its first record (snap0 pipelines.bin).
cs record = u8 kind, key, u32 index, ShaderComputeInputInfo (CS bytes, size from the recipe signature).
ASCII output only. Usage: python recdiff_s7.py <pipelines.bin> <rcp tsv>"""
import collections
import re
import struct
import sys

sys.path.insert(0, 'C:/kyty/s288/s7')
from recipes_s7 import stored_key, MAGIC  # noqa: E402


def records(path):
    d = open(path, 'rb').read()
    assert d[:8] == MAGIC
    (ss,) = struct.unpack_from('<I', d, 8)
    sig = d[12:12 + ss]
    VS, PS, CS, REN, VIN, STA = (int(x) for x in re.search(rb'(\d+):(\d+):(\d+):(\d+):(\d+):(\d+)$', sig).groups())
    p = 12 + ss + 4
    (count,) = struct.unpack_from('<I', d, 12 + ss)
    out = {}
    for i in range(count):
        kind = d[p]
        p += 1
        if kind == 1:
            _, p = stored_key(d, p)
            p += 4
            act = d[p] != 0
            p += 1
            if act:
                _, p = stored_key(d, p)
                p += 4
            p += REN + VIN + STA + VS + (PS if act else 0)
        else:
            _, p = stored_key(d, p)
            p += 4
            out[i] = d[p:p + CS]
            p += CS
    return out, CS


def main():
    recs, cs = records(sys.argv[1])
    print('cs info size', cs)
    offs = collections.Counter()
    n = 0
    for line in open(sys.argv[2], encoding='ascii').read().splitlines()[1:]:
        f = line.split('\t')
        dup = int(f[0])
        first = int(f[3].split()[-1])
        a, b = recs[first], recs[dup]
        diff = [k for k in range(cs) if a[k] != b[k]]
        offs[tuple(diff)] += 1
        n += 1
        if n <= 6:
            print('dup %d first %d differing byte offsets %s' % (dup, first, diff))
            for k in sorted(set(x - x % 4 for x in diff))[:8]:
                print('   off %4d first %08x dup %08x' % (k, struct.unpack_from('<I', a, k)[0], struct.unpack_from('<I', b, k)[0]))
    print('pairs', n)
    for k, v in offs.most_common(10):
        print('  offsets', list(k), 'pairs', v)


if __name__ == '__main__':
    main()
