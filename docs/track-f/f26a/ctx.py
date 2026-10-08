import sys, subprocess, collections
# usage: ctx.py <xz path> <out prefix> <before lines> <after lines>
path, outp, before, after = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
pats = [b'too many objects', b'Unhandled host exception', b'--- Error ---', b'4a020e']
p = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE, bufsize=1 << 20)
ring = collections.deque(maxlen=before)
hits = []
n = 0
tail_left = 0
out = None
for line in p.stdout:
    n += 1
    if tail_left > 0:
        out.write(b'%d: ' % n + line)
        tail_left -= 1
        if tail_left == 0:
            out.close(); out = None
    hit = any(x in line for x in pats)
    if hit:
        hits.append((n, line[:300]))
        if out is None and len(hits) == 1 or (out is None and b'too many objects' in line):
            out = open('%s_%d.txt' % (outp, n), 'wb')
            for (k, l) in ring:
                out.write(b'%d: ' % k + l)
            out.write(b'%d: ' % n + line)
            tail_left = after
    ring.append((n, line))
p.wait()
if out: out.close()
with open(outp + '_hits.txt', 'wb') as f:
    f.write(b'total_lines %d\n' % n)
    for k, l in hits:
        f.write(b'%d: ' % k + l.rstrip() + b'\n')
print('lines', n, 'hits', len(hits))
