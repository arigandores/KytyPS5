import sys
sys.path.insert(0, '.')
from diag_k4b_lib import fields
import s17c_read as R, tc_s17c
G = 'C:/kyty/s288/s17c'
for tag in sys.argv[1:]:
    live, _ = tc_s17c.read_folder(G + '/state/s17c_n0/f19'); rb, _ = tc_s17c.read_folder(G + '/state/%s/f19' % tag)
    sig, rows, _ = R.read_manifest(G + '/state/%s/replay/rebuild_manifest.tsv' % tag)
    fk = lambda n, p: (n, tuple(sorted(fields(p['spec']).items())), p['start'])
    lk = {}
    dup = 0
    for n, f in live.items():
        for p in f['perms']:
            k = fk(n, p); dup += k in lk; lk[k] = p['spirv_xxh3']
    rk = {}
    for (n, i, _s, st, x) in rows:
        p = rb[n]['perms'][i]; rk[fk(n, p)] = p['spirv_xxh3']
    hit = [k for k in lk if k in rk]; mism = [k for k in hit if lk[k] != rk[k]]
    print('%s field key (variant, reference): live_perms %d (dup %d) rebuilt %d rb_hit %d rb_dead %d rb_live_mismatch %d share %.4f' % (
        tag, len(lk), dup, len(rk), len(hit), len([k for k in rk if k not in lk]), len(mism), len(hit) / len(lk)))
