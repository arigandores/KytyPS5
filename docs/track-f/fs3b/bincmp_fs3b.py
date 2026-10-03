# FS3b (HPP-448, Red Team): independent rebuild check of the FS3 binary 540c035a (ROADMAP s122 item 367(g)(2)); a port of
# my FS2b bincmp_fs2b.py with paths fs2b -> fs3/fs3b, fs2a -> fs3/fs3a. Was:
# FS2b (HPP-382, Red Team): independent rebuild check of the FS2 binary by ROADMAP p.286(b) (i)-(iii).
# A = own build C:/kyty/f287/fs2b/build/install/kyty_emulator.exe (worktree fs2b/wt at 9c9d86ae, LF);
# B = the FS2a copy C:/kyty/f287/bin/kyty_emulator_bbad499c.exe (FS2a code is not imported; a port of FSb
# bincmp_fsb.py + textcmp_fsb.py with the worktree path fs2b -> fs2a).
# (i)  KYTY_SHADER_SOURCE_HASH and kytyGitVersion.h without comments equal (both build trees);
# (ii) section table: every section of one length, except .data/.reloc allowed to differ;
# (iii) .text: every differing byte run is <= 4 bytes and sits inside a 32-bit little-endian displacement
#      (the smallest |delta| over the 4-byte windows covering the run is reported); .rdata/.data printable strings
#      (>= 8 chars) equal as multisets after mapping the worktree path and masking ?A0x######## anonymous-namespace
#      hashes, except the PDB record.
import re, struct, collections, hashlib, io

A_PATH = 'C:/kyty/f287/fs3/fs3b/build/install/kyty_emulator.exe'
B_PATH = 'C:/kyty/f287/bin/kyty_emulator_540c035a.exe'
B_SHA = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'
A = open(A_PATH, 'rb').read()
B = open(B_PATH, 'rb').read()
BS = bytes([92])
ok = True

ha, hb = hashlib.sha256(A).hexdigest(), hashlib.sha256(B).hexdigest()
print('A', A_PATH, ha, len(A))
print('B', B_PATH, hb, len(B))
print('B sha256 == FS3a report', hb == B_SHA)
ok &= hb == B_SHA


def gv(path):
    t = io.open(path, encoding='utf-8').read().split('\n')
    return [l for l in t if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*') and not l.strip().startswith('*')]


va = gv('C:/kyty/f287/fs3/fs3b/build/kytyGitVersion.h')
vb = gv('C:/kyty/f287/fs3/fs3a/build/kytyGitVersion.h')
print('(i) kytyGitVersion.h without comments equal:', va == vb, 'lines', len(va), len(vb))
if va != vb:
    for x, y in zip(va, vb):
        if x != y:
            print('   A', x)
            print('   B', y)
ok &= va == vb
sig = [l for l in va if 'KYTY_SHADER_SOURCE_HASH' in l]
print('    signature line:', sig)
for nm, d in (('A', A), ('B', B)):
    m = re.findall(rb'56189185f9e9f9a0ea5174f3f85206e6d099db3d', d)
    print('    %s: signature 56189185f9e9... occurrences in exe %d' % (nm, len(m)))
    ok &= len(m) == 1
ok &= len(sig) == 1 and '56189185f9e9f9a0ea5174f3f85206e6d099db3d' in sig[0]


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


ta, ra = secs(A)
tb, rb = secs(B)
print('(ii) PE timestamp A %08x B %08x' % (ta, tb))
print('     sections A', list(ra.keys()))
print('     sections B', list(rb.keys()))
ok &= list(ra.keys()) == list(rb.keys())
for s in ra:
    same = ra[s][0] == rb[s][0]
    print('     %-8s vsize A %10d B %10d %s' % (s, ra[s][0], rb[s][0], 'equal' if same else 'DIFF'))
    if not same and s not in ('.data', '.reloc'):
        ok = False

# (iii) strings
na = A.replace(b'fs3' + BS + b'fs3b', b'fs3' + BS + b'fs3a').replace(b'fs3/fs3b', b'fs3/fs3a')
anon = re.compile(rb'\?A0x[0-9A-Fa-f]{1,8}')


def strs(d):
    return collections.Counter(anon.sub(b'?A0xXXXXXXXX', m.group()) for m in re.finditer(rb'[\x20-\x7e]{8,}', d))


for sec in ('.rdata', '.data'):
    xa = na[ra[sec][3]:ra[sec][3] + ra[sec][2]]
    xb = B[rb[sec][3]:rb[sec][3] + rb[sec][2]]
    a, b = strs(xa), strs(xb)
    oa, ob = a - b, b - a
    print('(iii) %s strings>=8 A %d B %d only A %d only B %d' % (sec, sum(a.values()), sum(b.values()), sum(oa.values()), sum(ob.values())))
    for s in list(oa)[:6]:
        print('      A only', s[:200])
    for s in list(ob)[:6]:
        print('      B only', s[:200])
    # the PDB record: lld writes the debug directory entry as "<1 byte>LLD PDB." + GUID/age (first run FAILED on
    # this filter: it looked for ".pdb" only; the record has no file name in .rdata)
    rest = [s for s in list(oa) + list(ob) if not (b'.pdb' in s.lower() or s.startswith(b'RSDS') or b'LLD PDB.' in s)]
    if rest:
        print('      non-PDB differences', len(rest))
        ok = False

xa = A[ra['.text'][3]:ra['.text'][3] + ra['.text'][0]]
xb = B[rb['.text'][3]:rb['.text'][3] + rb['.text'][0]]
if len(xa) != len(xb):
    print('(iii) .text lengths differ')
    ok = False
else:
    runs = []
    i, n = 0, len(xa)
    while i < n:
        if xa[i] != xb[i]:
            j = i
            while j < n and xa[j] != xb[j]:
                j += 1
            runs.append((i, j - i))
            i = j
        else:
            i += 1
    lens = collections.Counter(l for _, l in runs)
    print('(iii) .text bytes %d differing runs %d differing bytes %d' % (n, len(runs), sum(l for _, l in runs)))
    print('      run length histogram', sorted(lens.items()))
    deltas = collections.Counter()
    for s, l in runs:
        if l > 4:
            deltas['run>4'] += 1
            ok = False
            continue
        best = None
        for st in range(s + l - 4, s + 1):
            if st < 0:
                continue
            dlt = struct.unpack_from('<i', xa, st)[0] - struct.unpack_from('<i', xb, st)[0]
            if best is None or abs(dlt) < abs(best):
                best = dlt
        deltas[best] += 1
    print('      displacement deltas (top 10)', deltas.most_common(10))
    print('      distinct deltas', len(deltas))
print('BINCMP', 'ALL OK' if ok else 'FAILED')
