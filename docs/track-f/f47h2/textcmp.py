"""textcmp.py - F47h2: differing bytes per PE section of two builds of one worktree (rebuild after the mutants).
    python textcmp.py <a.exe> <b.exe>"""
import struct
import sys

a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
print('len', len(a), len(b))
pe = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, pe + 6)[0]
opt = struct.unpack_from('<H', a, pe + 20)[0]
secs = []
for k in range(nsec):
    o = pe + 24 + opt + 40 * k
    name = a[o:o + 8].rstrip(b'\0').decode()
    rs, rp = struct.unpack_from('<II', a, o + 16)
    secs.append((name, rp, rp + rs))
cnt = {}
for i in range(min(len(a), len(b))):
    if a[i] != b[i]:
        sec = next((s[0] for s in secs if s[1] <= i < s[2]), 'hdr/other')
        cnt[sec] = cnt.get(sec, 0) + 1
print('differing bytes by section', cnt, '; .text', cnt.get('.text', 0))
