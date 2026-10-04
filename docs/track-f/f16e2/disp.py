# F16e2 (HPP-570, Red Team; ROADMAP s122 item 470(d)): are the differing .text bytes of two equal-size PE builds only
# rel32 displacement fields (data moved, code not)? For every run of differing .text bytes: the run must fit in one
# 4-byte window [s, s+4); among the windows covering it the one is chosen whose rel32 target (VA(s+4) + disp, i.e. the
# displacement is the last field; also tried with a 1-byte and a 4-byte immediate after it) lands outside .text in both
# files. Printed: runs, runs longer than 4 bytes, runs without such a window, the histogram of target shifts
# (target_b - target_a), the sections of targets. A real code change gives long runs / no window / random shifts.
# Usage: disp.py <a.exe> <b.exe> [negctl]
import collections
import struct
import sys

a = open(sys.argv[1], 'rb').read()
b = bytearray(open(sys.argv[2], 'rb').read())
assert len(a) == len(b)
pe = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, pe + 6)[0]
osz = struct.unpack_from('<H', a, pe + 20)[0]
base = struct.unpack_from('<Q', a, pe + 24 + 24)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + osz + 40 * i
    name = a[o:o + 8].rstrip(b'\0').decode()
    vsz, va, rsz, rp = struct.unpack_from('<IIII', a, o + 8)
    secs.append((name, va, vsz, rp, rsz))
T = [s for s in secs if s[0] == '.text'][0]
if len(sys.argv) > 3 and sys.argv[3] == 'negctl':
    # negative control: overwrite 16 consecutive bytes in the middle of .text (a code change, not a displacement)
    off = T[3] + T[4] // 2
    for k in range(16):
        b[off + k] ^= 0x5A
    print('negctl: 16 bytes of .text changed at', off)
b = bytes(b)


def rva_sec(rva):
    for n, va, vsz, rp, rsz in secs:
        if va <= rva < va + max(vsz, rsz):
            return n
    return None


t0, tl = T[3], T[4]
diff = [i for i in range(t0, t0 + tl) if a[i] != b[i]]
runs = []
for i in diff:
    if runs and i == runs[-1][1] + 1:
        runs[-1][1] = i
    else:
        runs.append([i, i])
# merge runs that are within one 4-byte window
merged = []
for r in runs:
    if merged and r[1] - merged[-1][0] < 4:
        merged[-1][1] = r[1]
    else:
        merged.append(list(r))
longr = [r for r in merged if r[1] - r[0] + 1 > 4]
shifts = collections.Counter()
tsec = collections.Counter()
nowin = []
for lo, hi in merged:
    if hi - lo + 1 > 4:
        continue
    found = None
    for s in range(hi - 3, lo + 1):
        da = struct.unpack_from('<i', a, s)[0]
        db = struct.unpack_from('<i', b, s)[0]
        for imm in (0, 1, 4):
            rva_next = T[1] + (s - t0) + 4 + imm
            ta, tb = rva_next + da, rva_next + db
            sa, sb = rva_sec(ta), rva_sec(tb)
            if sa and sa == sb and sa != '.text':
                found = (tb - ta, sa)
                break
        if found:
            break
    if found:
        shifts[found[0]] += 1
        tsec[found[1]] += 1
    else:
        nowin.append((lo, hi))
print('.text differing bytes', len(diff), 'runs (4-byte windows)', len(merged))
print('runs longer than 4 bytes', len(longr), [(hex(x), y - x + 1) for x, y in longr[:8]])
print('runs without a rel32 window into a non-.text section', len(nowin))
for lo, hi in nowin[:10]:
    print('   0x%08x..0x%08x a=%s b=%s' % (lo, hi, a[lo - 4:hi + 5].hex(), b[lo - 4:hi + 5].hex()))
print('target sections', dict(tsec))
print('distinct target shifts', len(shifts), 'top', [(hex(k) if k >= 0 else '-' + hex(-k), v) for k, v in shifts.most_common(12)])
print('VERDICT', 'DISPLACEMENT-ONLY' if not longr and not nowin else 'NOT-DISPLACEMENT-ONLY')
