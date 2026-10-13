import os, sys, struct, collections, importlib.util, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# T133: do ASTRO BOT programs address 1D images at all? MIMG dword0 DIM = bits [5:3] (RDNA2/GFX10 encoding [I]):
# 0 1D, 1 2D, 2 3D, 3 CUBE, 4 1D_ARRAY, 5 2D_ARRAY, 6 2D_MSAA, 7 2D_MSAA_ARRAY. op = bits [24:18].
# Walk = gcn_f23a.walk (unchanged), programs C:/kyty/f287/f23a/eboot_text (5 698).
G = 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py'
spec = importlib.util.spec_from_file_location('g', G)
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
print('decoder sha256', hashlib.sha256(open(G, 'rb').read()).hexdigest())
D = 'C:/kyty/f287/f23a/eboot_text/'
DIM = ['1D', '2D', '3D', 'CUBE', '1D_ARRAY', '2D_ARRAY', '2D_MSAA', '2D_MSAA_ARRAY']
inst = collections.Counter(); progs = collections.Counter(); status = collections.Counter()
ex1d = collections.defaultdict(list)
files = sorted(os.listdir(D))
for fn in files:
    b = open(D + fn, 'rb').read()
    words = list(struct.unpack_from('<%dI' % (len(b) // 4), b, 0))
    out, st = g.walk(words)
    status[st.split('@')[0]] += 1
    seen = set()
    for pc, fam, op, size, ex in out:
        if fam != 'MIMG':
            continue
        w = words[pc]
        dim = DIM[(w >> 3) & 7]
        mop = (w >> 18) & 0x7f
        inst[dim] += 1
        seen.add(dim)
        if dim in ('1D', '1D_ARRAY') and len(ex1d[dim]) < 8:
            ex1d[dim].append('%s pc=%d op=0x%02x' % (fn[:-4], pc, mop))
    for d in seen:
        progs[d] += 1
print('programs', len(files), 'walk status', dict(status))
for d in DIM:
    print('  dim %-14s instructions %7d programs %5d' % (d, inst[d], progs[d]))
for d, l in ex1d.items():
    print('  examples', d, l)
print('DONE')
