import collections, struct, sys
sys.path.insert(0, 'C:/kyty/s288/s17c')
import s17c_read as R, tc_s17c
G = 'C:/kyty/s288/s17c'; tag = sys.argv[1]
IMG = ['numeric_class','dimension','mip_count','conversion_format','shader_swizzle','indirect_root','indirect_mapping_offset','indirect_search_iterations']
def fields(spec):
    nb = struct.unpack_from('<I', spec, 0)[0]; out = {}
    for i in range(nb):
        w = struct.unpack_from('<3I', spec, 4 + 12 * i)
        for j, n in enumerate(['packed_stride','descriptor_format','descriptor_swizzle']): out['buf%d.%s' % (i, n)] = w[j]
    o = 4 + 12 * nb; ni = struct.unpack_from('<I', spec, o)[0]; o += 4
    for i in range(ni):
        b = spec[o + 44 * i: o + 44 * (i + 1)]
        w = struct.unpack_from('<8I', b, 0)
        for j, n in enumerate(IMG): out['img%d.%s' % (i, n)] = w[j]
        out['img%d.cube' % i] = b[32]; out['img%d.manual_depth_compare' % i] = b[33]
        out['img%d.depth_compare_op' % i] = struct.unpack_from('<I', b, 36)[0]; out['img%d.fmask' % i] = b[40]
    return out
live, _ = tc_s17c.read_folder(G + '/state/s17c_n0/f19'); rb, _ = tc_s17c.read_folder(G + '/state/%s/f19' % tag)
sig, rows, _ = R.read_manifest(G + '/state/%s/replay/rebuild_manifest.tsv' % tag)
lk = {}
for n, f in live.items():
    for p in f['perms']: lk[(n, p['spec'], p['start'])] = p['spirv_xxh3']
c = collections.Counter(); ex = []
for (n, i, _s, st, x) in rows:
    p = rb[n]['perms'][i]; k = (n, p['spec'], p['start'])
    if k in lk: continue
    cands = [q for q in lk if q[0] == n and lk[q] == p['spirv_xxh3']]
    if not cands: c['no same-SPIR-V live perm'] += 1; continue
    fa, fb = fields(p['spec']), fields(cands[0][1])
    d = sorted(set(k2.split('.', 1)[1] for k2 in set(fa) | set(fb) if fa.get(k2) != fb.get(k2)))
    c[' + '.join(d)] += 1
    if len(ex) < 4: ex.append((n, [(k2, fb.get(k2), fa.get(k2)) for k2 in sorted(set(fa) | set(fb)) if fa.get(k2) != fb.get(k2)][:4]))
for k, v in c.most_common(): print('%4d  differs: %s' % (v, k))
for e in ex: print('example', e[0], 'live -> rebuilt', e[1])
