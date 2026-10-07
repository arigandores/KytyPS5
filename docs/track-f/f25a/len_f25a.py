"""F25a RC1: the 1024-byte line buffer of Append (f2307b02:src/common/diagB32.cpp:539) - the longest DiagB32 line of each kind and
the lines without their last field (truncated), over the given logs."""
import sys
tails = {b'DiagB32: n=': b'c_lines=', b'DiagB32-t: ': b'peer=', b'DiagB32-w: ': b'peer_tid=', b'DiagB32-c: ': b'cpu_us=', b'DiagB32-x: ': b'ring_hold_w='}
mx = dict((k, 0) for k in tails)
bad = dict((k, 0) for k in tails)
n = dict((k, 0) for k in tails)
for p in sys.argv[1:]:
    with open(p, 'rb') as f:
        for line in f:
            i = line.find(b'DiagB32')
            if i < 0:
                continue
            s = line[i:].rstrip(b'\r\n')
            for k, t in tails.items():
                if s.startswith(k):
                    n[k] += 1
                    mx[k] = max(mx[k], len(s))
                    if t not in s:
                        bad[k] += 1
for k in tails:
    print('%-12s lines %6d  max length %4d  without the last field %d' % (k.decode().strip(), n[k], mx[k], bad[k]))
print('ALL OK' if sum(bad.values()) == 0 else 'TRUNCATED LINES FOUND')
