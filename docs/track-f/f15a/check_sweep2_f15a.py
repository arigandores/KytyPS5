# F15a: positive control of sweep2_f15a.py - the block search and a plain line scan on the same files must agree;
# the witness log C:/kyty/s131/log_dds131.txt.xz (Б4 after 'Event: quit') must be found by the block search.
# Usage: python check_sweep2_f15a.py <file> [<file> ...]
import re, subprocess, sys

QUIT = (b'Event: quit', b'Event: terminate')
NUL = b'm_files[index] == nullptr'
FAT = b'--- Fatal Error ---'
BLOCK = 64 << 20
OVER = 4096


def opener(p):
    if p.endswith('.xz'):
        proc = subprocess.Popen(['xz', '-dc', p], stdout=subprocess.PIPE)
        return proc.stdout, proc
    return open(p, 'rb'), None


def line_scan(p):
    src, proc = opener(p)
    q = False
    r = [0, 0, 0, 0, False]
    for raw in src:
        if not q and (QUIT[0] in raw or QUIT[1] in raw):
            q = True
        if NUL in raw:
            r[0] += 1
            r[1] += q
        if FAT in raw:
            r[2] += 1
            r[3] += q
    r[4] = q
    src.close()
    if proc:
        proc.wait()
    return r


def positions(buf, pat, limit):
    res = []
    i = buf.find(pat)
    while i != -1 and i < limit:
        res.append(i)
        i = buf.find(pat, i + 1)
    return res


def block_scan(p, block):
    src, proc = opener(p)
    quit_off = -1
    r = [0, 0, 0, 0, False]
    base = 0
    buf = b''
    while True:
        data = src.read(block)
        eof = not data
        buf += data
        limit = len(buf) if eof else max(0, len(buf) - OVER)
        if quit_off < 0:
            q = [x for pat in QUIT for x in positions(buf, pat, limit)]
            if q:
                quit_off = base + min(q)
        for i in positions(buf, NUL, limit):
            r[0] += 1
            r[1] += 0 <= quit_off <= base + i
        for i in positions(buf, FAT, limit):
            r[2] += 1
            r[3] += 0 <= quit_off <= base + i
        if eof:
            break
        base += limit
        buf = buf[limit:]
    src.close()
    if proc:
        proc.wait()
    r[4] = quit_off >= 0
    return r


ok = True
for p in sys.argv[1:]:
    a = line_scan(p)
    b = block_scan(p, BLOCK)
    c = block_scan(p, 1 << 16)  # small blocks: markers cross block borders many times
    same = a == b == c
    ok &= same
    print(p, 'line', a, 'block64M', b, 'block64K', c, 'OK' if same else 'MISMATCH')
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
