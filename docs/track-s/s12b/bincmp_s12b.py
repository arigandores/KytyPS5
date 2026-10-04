# S12b (HPP-495, Red Team): S12 adb0c82f against FS5 631ff987 (base 0e72bc19) and the S12a worktree install.
# Port of my FS5b bincmp_fs5b.py: section table, .text differing runs, .rdata/.data string multisets.
# Expected: the only source change is SPcwMode (c1732d1a); differing .text must sit in one region (+ displacements).
import re, struct, collections, hashlib, sys

S12 = 'C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe'
WT = 'C:/kyty/s288/s12a/build/install/kyty_emulator.exe'
FS5 = 'C:/kyty/f287/bin/kyty_emulator_631ff987.exe'
FS5OWN = 'C:/kyty/f287/fs5/fs5b/build/install/kyty_emulator.exe'
ok = True
D = {}
for p in (S12, WT, FS5, FS5OWN):
    try:
        D[p] = open(p, 'rb').read()
    except OSError as e:
        print('MISSING', p, e)
        D[p] = None
        continue
    print('sha256', hashlib.sha256(D[p]).hexdigest(), len(D[p]), p)
ok &= D[S12] is not None and hashlib.sha256(D[S12]).hexdigest().startswith('adb0c82f1a752805')
if D[WT] is not None:
    print('copy == worktree install:', D[S12] == D[WT])
    ok &= D[S12] == D[WT]


def secs(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    ts = struct.unpack_from('<I', d, pe + 8)[0]
    opt = struct.unpack_from('<H', d, pe + 20)[0]
    o = pe + 24 + opt
    r = collections.OrderedDict()
    for _ in range(n):
        name = d[o:o + 8].rstrip(b'\0').decode()
        vs, vaddr, rs, rp = struct.unpack_from('<IIII', d, o + 8)
        r[name] = (vs, vaddr, rs, rp)
        o += 40
    return ts, r


def strs(d, sec):
    vs, va, rs, rp = sec
    return collections.Counter(re.findall(rb'[\x20-\x7e]{8,}', d[rp:rp + min(vs, rs)]))


for B_PATH in (FS5, FS5OWN):
    A, B = D[S12], D[B_PATH]
    if B is None:
        continue
    print('=== A = S12 adb0c82f, B =', B_PATH)
    ta, ra = secs(A)
    tb, rb = secs(B)
    for s in ra:
        print('  %-8s vsize A %10d B %10d %s' % (s, ra[s][0], rb[s][0], 'equal' if ra[s][0] == rb[s][0] else 'DIFF'))
    for s in ('.rdata', '.data'):
        ca, cb = strs(A, ra[s]), strs(B, rb[s])
        oa, ob = ca - cb, cb - ca
        print('  %s strings>=8 only A %d only B %d' % (s, sum(oa.values()), sum(ob.values())))
        for k in list(oa)[:10]:
            print('    A only', k[:120])
        for k in list(ob)[:10]:
            print('    B only', k[:120])
    vs, va, rs, rp = ra['.text']
    vsb, vab, rsb, rpb = rb['.text']
    n = min(vs, vsb)
    ta_ = A[rp:rp + n]
    tb_ = B[rpb:rpb + n]
    runs = []
    i = 0
    # fast scan in 4 KiB blocks
    blk = 4096
    for off in range(0, n, blk):
        if ta_[off:off + blk] == tb_[off:off + blk]:
            continue
        j = off
        end = min(off + blk, n)
        while j < end:
            if ta_[j] != tb_[j]:
                k = j
                while k < n and ta_[k] != tb_[k]:
                    k += 1
                runs.append((j, k - j))
                j = k
            else:
                j += 1
    nbytes = sum(l for _, l in runs)
    print('  .text differing runs %d bytes %d' % (len(runs), nbytes))
    if runs:
        print('  first run RVA 0x%x len %d; last run RVA 0x%x len %d' % (va + runs[0][0], runs[0][1], va + runs[-1][0], runs[-1][1]))
        hist = collections.Counter(min(l, 9) for _, l in runs)
        print('  run length histogram (9 = >=9)', sorted(hist.items()))
        big = [(va + o, l) for o, l in runs if l > 4]
        print('  runs > 4 bytes: %d' % len(big), ['0x%x:%d' % x for x in big[:20]])
        # span of runs > 4 bytes
        if big:
            print('  span of runs > 4 bytes: 0x%x .. 0x%x (%d bytes)' % (big[0][0], big[-1][0] + big[-1][1], big[-1][0] + big[-1][1] - big[0][0]))
print('KYTY_GIT_REVISION 4d9e8ab7 in S12:', len(re.findall(rb'4d9e8ab709b4911a935e76cd90303562b2ecf174', D[S12])))
print('SDL_REVISION in S12:', re.findall(rb'SDL-KytyPS5-[0-9a-z\-]+', D[S12]))
print('signature 26ce5fc7 in S12:', len(re.findall(rb'26ce5fc78ea3b20be537c7696be041f5e97d9e58', D[S12])))
print('S-pcw format string in S12:', len(re.findall(rb'S-pcw: KYTY_S_PCW=%d KYTY_S_PCW_FORCE_MS=%u', D[S12])))
print('ALL OK' if ok else 'CHECK FAILED')
