# F16e2 (HPP-570, Red Team; ROADMAP s122 item 470(d)): compare two PE files section by section (raw bytes) and print
# the differing ranges of non-.text sections with the printable strings around them (cause of a sha256 difference).
# Usage: pecmp.py <a.exe> <b.exe>
import hashlib
import struct
import sys


def sections(path):
    b = open(path, 'rb').read()
    pe = struct.unpack_from('<I', b, 0x3C)[0]
    nsec = struct.unpack_from('<H', b, pe + 6)[0]
    opt = struct.unpack_from('<H', b, pe + 20)[0]
    ts = struct.unpack_from('<I', b, pe + 8)[0]
    off = pe + 24 + opt
    out = {}
    for i in range(nsec):
        name = b[off:off + 8].rstrip(b'\0').decode('ascii', 'replace')
        vsize, va, rsize, rptr = struct.unpack_from('<IIII', b, off + 8)
        out[name] = b[rptr:rptr + rsize]
        off += 40
    return b, out, ts


def strings_near(data, pos, span=80):
    lo, hi = max(0, pos - span), min(len(data), pos + span)
    s = data[lo:hi]
    return ''.join(chr(c) if 32 <= c < 127 else '.' for c in s)


def main():
    a, sa, ta = sections(sys.argv[1])
    b, sb, tb = sections(sys.argv[2])
    print('size', len(a), len(b), 'sha256', hashlib.sha256(a).hexdigest()[:16], hashlib.sha256(b).hexdigest()[:16])
    print('COFF timestamp', ta, tb)
    for name in sorted(set(sa) | set(sb)):
        x, y = sa.get(name, b''), sb.get(name, b'')
        diff = [i for i in range(min(len(x), len(y))) if x[i] != y[i]] if len(x) == len(y) else None
        if diff is None:
            print('%-8s size %d vs %d DIFFERENT SIZE' % (name, len(x), len(y)))
            continue
        print('%-8s size %d sha %s %s diff bytes %d' % (name, len(x), hashlib.sha256(x).hexdigest()[:16],
                                                        hashlib.sha256(y).hexdigest()[:16], len(diff)))
        if diff and name != '.text':
            runs = []
            for i in diff:
                if runs and i - runs[-1][1] <= 16:
                    runs[-1][1] = i
                else:
                    runs.append([i, i])
            for lo, hi in runs[:12]:
                print('   @%#x..%#x' % (lo, hi))
                print('     a:', strings_near(x, lo))
                print('     b:', strings_near(y, lo))
    whole = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    print('whole-file differing bytes', len(whole), 'first', [hex(i) for i in whole[:8]])


main()
