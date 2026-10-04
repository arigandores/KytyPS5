# F16e2 (HPP-570, Red Team; ROADMAP s122 item 470(d)): stronger form of disp.py. Every differing .text run must be one
# rel32 field whose targets in A and B are outside .text; among the candidate windows (start s, immediate 0/1/4 after
# the field) the one with the smallest |shift| is taken. Then the map target_A -> target_B over ALL windows must be
#   (1) single-valued   - one target_A never maps to two target_B (a swapped reference breaks this),
#   (2) injective       - two target_A never map to one target_B,
#   (3) monotone        - target_A order = target_B order (data moved as blocks, nothing reordered).
# Also the unchanged rel32 fields are NOT checked (they are equal by definition); a code change that lands on a field
# with equal bytes in A and B is invisible to any byte compare. Usage: disp2.py <a.exe> <b.exe> [negctl|swap]
#   negctl - 16 bytes of B's .text changed in the middle (a code change);
#   swap   - two differing rel32 fields of B with different targets swapped (a "wrong global" change; keeps every run 4 bytes).
import struct
import sys

a = open(sys.argv[1], 'rb').read()
b = bytearray(open(sys.argv[2], 'rb').read())
assert len(a) == len(b)
pe = struct.unpack_from('<I', a, 0x3c)[0]
nsec = struct.unpack_from('<H', a, pe + 6)[0]
osz = struct.unpack_from('<H', a, pe + 20)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + osz + 40 * i
    name = a[o:o + 8].rstrip(b'\0').decode()
    vsz, va, rsz, rp = struct.unpack_from('<IIII', a, o + 8)
    secs.append((name, va, vsz, rp, rsz))
T = [s for s in secs if s[0] == '.text'][0]
t0, tl = T[3], T[4]
mode = sys.argv[3] if len(sys.argv) > 3 else ''
if mode == 'negctl':
    off = t0 + tl // 2
    for k in range(16):
        b[off + k] ^= 0x5A
    print('negctl: 16 bytes of .text changed at', off)


def rva_sec(rva):
    for n, va, vsz, rp, rsz in secs:
        if va <= rva < va + max(vsz, rsz):
            return n
    return None


def analyse(bb):
    diff = [i for i in range(t0, t0 + tl) if a[i] != bb[i]]
    merged = []
    for i in diff:
        if merged and i - merged[-1][0] < 4:
            merged[-1][1] = i
        else:
            merged.append([i, i])
    bad = []
    pairs = []
    for lo, hi in merged:
        best = None
        if hi - lo + 1 <= 4:
            for s in range(hi - 3, lo + 1):
                da = struct.unpack_from('<i', a, s)[0]
                db = struct.unpack_from('<i', bb, s)[0]
                for imm in (0, 1, 4):
                    nxt = T[1] + (s - t0) + 4 + imm
                    ta, tb = nxt + da, nxt + db
                    sa, sb = rva_sec(ta), rva_sec(tb)
                    if sa and sa == sb and sa != '.text':
                        if best is None or abs(tb - ta) < abs(best[2] - best[1]):
                            best = (s, ta, tb, sa)
        if best is None:
            bad.append((lo, hi))
        else:
            pairs.append(best)
    return diff, merged, bad, pairs


diff, merged, bad, pairs = analyse(bytes(b))
if mode == 'swap':
    # swap the rel32 fields of two windows with different targets (recomputed for B's own next-ip)
    p1 = pairs[len(pairs) // 3]
    p2 = next(p for p in pairs[len(pairs) // 3 + 1:] if p[2] != p1[2])
    for (s, ta, tb, sec), tnew in ((p1, p2[2]), (p2, p1[2])):
        nxt_b = struct.unpack_from('<i', b, s)[0]
        nxt = tb - nxt_b
        struct.pack_into('<i', b, s, tnew - nxt)
    print('swap: fields at', hex(p1[0]), hex(p2[0]))
    diff, merged, bad, pairs = analyse(bytes(b))
fwd = {}
rev = {}
multi = 0
inj = 0
for s, ta, tb, sec in pairs:
    if ta in fwd and fwd[ta] != tb:
        multi += 1
    fwd.setdefault(ta, tb)
    if tb in rev and rev[tb] != ta:
        inj += 1
    rev.setdefault(tb, ta)
items = sorted(fwd.items())
nonmono = sum(1 for (xa, xb), (ya, yb) in zip(items, items[1:]) if not xb < yb)
print('.text differing bytes', len(diff), 'windows', len(merged), 'without a rel32 window', len(bad))
print('distinct targets A', len(fwd), 'single-valued violations', multi, 'injective violations', inj,
      'monotone violations', nonmono)
shifts = sorted(set(tb - ta for ta, tb in items))
print('distinct shifts', len(shifts), [hex(x) if x >= 0 else '-' + hex(-x) for x in shifts[:16]])
ok = not bad and multi == 0 and inj == 0 and nonmono == 0
print('VERDICT', 'LAYOUT-SHIFT-ONLY' if ok else 'NOT-LAYOUT-SHIFT-ONLY')
