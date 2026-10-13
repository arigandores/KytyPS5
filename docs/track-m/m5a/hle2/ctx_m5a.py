import os, re, sys, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present, exit'); sys.exit(3)
# usage: ctx_m5a.py <log> <regex-bytes> <before> <after> <maxhits>
path = sys.argv[1]
rx = re.compile(sys.argv[2].encode())
B = int(sys.argv[3]); A = int(sys.argv[4]); M = int(sys.argv[5])
ring = collections.deque(maxlen=B)
hits = 0
after = 0
n = 0
with open(path, 'rb') as f:
    for line in f:
        n += 1
        if after > 0:
            print('   +%d: %r' % (n, line[:220]))
            after -= 1
            if after == 0:
                print('-----')
            ring.append((n, line))
            continue
        if rx.search(line):
            hits += 1
            if hits <= M:
                for (k, l) in ring:
                    print('   -%d: %r' % (k, l[:220]))
                print('>> %d: %r' % (n, line[:220]))
                after = A
                if A == 0:
                    print('-----')
        ring.append((n, line))
print('TOTAL hits', hits, 'lines', n)
