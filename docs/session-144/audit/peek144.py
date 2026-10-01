# peek144.py - Session Auditor s144 step 3 (HPP-333): print the lines of a log around the byte positions of a key (read only, mmap).
# Usage: python peek144.py <log> <key> [before_lines] [after_lines] [max_hits]
import sys, mmap

path, key = sys.argv[1], sys.argv[2].encode()
nb = int(sys.argv[3]) if len(sys.argv) > 3 else 3
na = int(sys.argv[4]) if len(sys.argv) > 4 else 3
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 5
with open(path, 'rb') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    p = mm.find(key)
    hits = 0
    while p != -1 and hits < mx:
        hits += 1
        a = p
        for _ in range(nb + 1):
            a = mm.rfind(b'\n', 0, a)
            if a == -1:
                a = 0
                break
        e = p
        for _ in range(na + 1):
            e2 = mm.find(b'\n', e + 1)
            if e2 == -1:
                e = len(mm)
                break
            e = e2
        print('=== hit %d at byte %d (size %d)' % (hits, p, len(mm)))
        q = a + 1 if a else 0
        for ln in mm[q:e].split(b'\n'):
            print('%12d | %s' % (q, ln[:260].decode('ascii', 'replace').rstrip('\r')))
            q += len(ln) + 1
        p = mm.find(key, p + 1)
    print('hits shown %d' % hits)
    mm.close()
