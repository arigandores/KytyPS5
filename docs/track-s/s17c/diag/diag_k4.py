"""Diagnostics (not a member, outside the seal): why rb_hit < live_perms in s17c_r3 - classes of the rebuilt keys not live and of the live
keys not rebuilt.  ASCII only.  usage: python diag_k4.py <tag>"""
import collections
import sys

sys.path.insert(0, 'C:/kyty/s288/s17c')
import s17c_read as R  # noqa: E402
import tc_s17c  # noqa: E402

tag = sys.argv[1] if len(sys.argv) > 1 else 's17c_r3'
G = 'C:/kyty/s288/s17c'
live, _ = tc_s17c.read_folder(G + '/state/s17c_n0/f19')
rb, _ = tc_s17c.read_folder(G + '/state/%s/f19' % tag)
sig, rows, _ = R.read_manifest(G + '/state/%s/replay/rebuild_manifest.tsv' % tag)
lk = {}
for n, f in live.items():
    for p in f['perms']:
        lk[(n, p['spec'], p['start'])] = p['spirv_xxh3']
rk = {}
for (n, i, _sh, st, x) in rows:
    p = rb[n]['perms'][i]
    rk[(n, p['spec'], p['start'])] = p['spirv_xxh3']
dead = [k for k in rk if k not in lk]
miss = [k for k in lk if k not in rk]
print('live files %d perms %d; rebuilt files %d keys %d; manifest rows %d' % (len(live), len(lk), len(rb), len(rk), len(rows)))
print('files only live %d, only rebuilt %d, both %d' % (len(set(live) - set(rb)), len(set(rb) - set(live)), len(set(live) & set(rb))))
c = collections.Counter()
for k in dead:
    n, spec, st = k
    same_file = [q for q in lk if q[0] == n]
    if not same_file:
        c['dead: file not live'] += 1
        continue
    if any(q[1] == spec for q in same_file):
        c['dead: same file+spec, other push start'] += 1
    elif any(lk[q] == rk[k] for q in same_file):
        c['dead: same file+SPIR-V, other spec bytes'] += 1
    elif any(q[2] == st for q in same_file):
        c['dead: same file+start, other spec and SPIR-V'] += 1
    else:
        c['dead: other'] += 1
for k in miss:
    n, spec, st = k
    same_file = [q for q in rk if q[0] == n]
    c['live-miss: %s' % ('file not rebuilt' if not same_file else 'file rebuilt, key differs')] += 1
for k, v in sorted(c.items()):
    print('%-50s %d' % (k, v))
# spec bytes difference pattern for same file+SPIR-V
diffpos = collections.Counter()
lens = collections.Counter()
nshown = 0
for k in dead:
    n, spec, st = k
    for q in lk:
        if q[0] == n and lk[q] == rk[k] and q[1] != spec:
            lens['len rb %d live %d' % (len(spec), len(q[1]))] += 1
            if len(spec) == len(q[1]):
                d = [i for i in range(len(spec)) if spec[i] != q[1][i]]
                diffpos[(d[0] if d else -1, len(d))] += 1
            break
print('spec length pairs (same file+SPIR-V):', dict(lens.most_common(8)))
print('first differing byte offset, count of differing bytes:', diffpos.most_common(12))
