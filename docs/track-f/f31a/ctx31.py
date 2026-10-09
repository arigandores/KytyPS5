# F31a: context around the B25 assert in a log (binary read, no full decode)
import sys, re
path = sys.argv[1]
out = sys.argv[2]
before = int(sys.argv[3]) if len(sys.argv) > 3 else 400
after = int(sys.argv[4]) if len(sys.argv) > 4 else 150
SIG = [b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'pc=0x00000009004a020e']
ring = []
hits = []
n = 0
post = None
res = []
with open(path, 'rb') as f:
    for line in f:
        n += 1
        if post is not None:
            res.append((n, line))
            post -= 1
            if post == 0:
                break
            continue
        ring.append((n, line))
        if len(ring) > before:
            ring.pop(0)
        if any(s in line for s in SIG):
            hits.append(n)
            res = list(ring)
            post = after
with open(out, 'wb') as o:
    o.write(('hits_first_at %s total_lines_read %d\n' % (hits[:1], n)).encode())
    for k, l in res:
        o.write(b'%d\t' % k + l.rstrip(b'\r\n')[:600] + b'\n')
print('first hit', hits[:1], 'lines read', n)
