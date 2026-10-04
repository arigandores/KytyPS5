# S14a: prefix histogram of one S10 log, before / after the level entry line (binary stream)
import sys, os, collections, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
tag, lv = sys.argv[1], sys.argv[2]
p = 'C:/kyty/s288/s10/log_%s.txt' % tag
h = hashlib.sha256()
ent = None
c = [collections.Counter(), collections.Counter()]
with open(p, 'rb') as f:
    for n, l in enumerate(f, 1):
        h.update(l)
        if ent is None and l.startswith(b'GuestOut: Level has started: ' + lv.encode()):
            ent = n
        k = l[:60].split(b':', 1)[0][:40] if b':' in l[:60] else b'<none>'
        if k == b'AvTrace':
            k = b'AvTrace: ' + b' '.join(l[9:60].split(b' ')[:2])
        c[1 if ent else 0][k] += 1
print(tag, 'lines', n, 'entry', ent, 'sha256', h.hexdigest()[:16])
for i, name in ((0, 'before'), (1, 'after')):
    print('==', name)
    for k, v in c[i].most_common(70):
        print('  %8d %s' % (v, k.decode('latin1')))
