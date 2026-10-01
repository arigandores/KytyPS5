# F5a2: raw bytes of every GuestOut line with "Level has started" in the named logs (mmap scan).
import mmap, sys
for p in sys.argv[1:]:
    with open(p, 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        pos = 0
        while True:
            i = m.find(b'Level has started', pos)
            if i < 0: break
            a = m.rfind(b'\n', 0, i) + 1; b = m.find(b'\n', i)
            print(p.split('/')[-1], a, repr(m[a:b + 1]))
            pos = i + 1
