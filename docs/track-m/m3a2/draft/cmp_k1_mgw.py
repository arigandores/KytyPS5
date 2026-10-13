import os, hashlib, sys
G = 'C:/kyty/m657/m3a2'
def rows(p):
    d = {}
    for l in open(p, encoding='utf-8', errors='replace'):
        t = l.rstrip('\n').split('\t')
        if len(t) == 4:
            d[(t[0], t[1])] = (t[2], t[3])
    return d
k1 = rows(G + '/k1/k1.tsv')
run = rows(G + '/runs/m3w2_mg_w/manifest_run.tsv')
# _ShaderCache of the run state from k1.new
r = G + '/k1.new/_ShaderCache'
for dp, dn, fn in os.walk(r):
    for f in fn:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, r).replace(os.sep, '/')
        run[('_ShaderCache', rel)] = (str(os.path.getsize(p)), hashlib.sha256(open(p, 'rb').read()).hexdigest())
dirs = sorted(set(k for k, _ in k1) | set(k for k, _ in run))
for d in dirs:
    a = {k: v for k, v in k1.items() if k[0] == d}
    b = {k: v for k, v in run.items() if k[0] == d}
    oa = set(a) - set(b); ob = set(b) - set(a); ch = [k for k in set(a) & set(b) if a[k] != b[k]]
    print(d, 'k1', len(a), 'run', len(b), 'only_k1', len(oa), 'only_run', len(ob), 'changed', len(ch))
    for k in sorted(ch)[:6]: print('  CH', k[1], a[k][0], '->', b[k][0])
    for k in sorted(ob)[:6]: print('  NEW', k[1], b[k][0])
    for k in sorted(oa)[:6]: print('  GONE', k[1], a[k][0])
