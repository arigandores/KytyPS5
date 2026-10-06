"""S18c (HPP-644): check of the seal - every line 'seal: <sha256> <path>' of pred/s18c_seal.md equals the file on disk, and the seal is byte
for byte the git copy docs/track-s/s18c.md.  Prints one line per file and 'SEAL: PASS' / 'SEAL: FAIL'.  Port of checkseal_s17c2.py.
ASCII only.
usage: python checkseal_s18c.py [<seal>]"""
import hashlib
import os
import sys

SEAL = 'C:/kyty/s288/s18c/pred/s18c_seal.md'
GIT = 'C:/kyty/KytyPS5/docs/track-s/s18c.md'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main(argv):
    seal = argv[0] if argv else SEAL
    ok = True
    n = 0
    for line in open(seal, 'rb').read().decode('utf-8').splitlines():
        s = line.strip().lstrip('-').strip().strip('`')
        if not s.startswith('seal: '):
            continue
        parts = s.split(' ', 2)
        if len(parts) != 3:
            continue
        n += 1
        want, path = parts[1], parts[2].strip()
        got = sha(path) if os.path.isfile(path) else None
        print('%s %s %s' % ('ok  ' if got == want else 'FAIL', want[:16], path))
        ok = ok and got == want
    same = os.path.isfile(GIT) and open(GIT, 'rb').read() == open(seal, 'rb').read()
    print('%s seal = %s byte for byte' % ('ok  ' if same else 'FAIL', GIT))
    ok = ok and same and n > 0
    print('seal lines %d' % n)
    print('SEAL: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
