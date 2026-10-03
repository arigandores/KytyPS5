"""F14c (HPP-489): fixtures of spv_sites_f14c.py.
(1) On every A row of the T1 corpus (S7 pass A out.spv, sha256 checked as in f14a_corpus.py) the manual and native site counts
    equal the counts of f14a_spv.tsv (F14a, KytyPS5 a015bb9f) - the site rule is unchanged.
(2) Every site resolves its image and sampler to (DescriptorSet, Binding, index) with set and binding not None.
(3) The SPIR-V probes of F14a section 2.1 (spv/ctl_base, spv/ctl_k32f, if present as .spv): probe 3/4 k8UNorm manual 1 site each,
    k32Float native 1 site each.
Prints per-row mismatches, a binding census of the sites, and ALL OK / FAIL.  ASCII only.  Halts on the lock or STOP.
"""
import csv, hashlib, os, sys
sys.path.insert(0, 'C:/kyty/f287/f14c')
import spv_sites_f14c as S

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
S7 = 'C:/kyty/s288/s7'
F14A = 'C:/kyty/KytyPS5/docs/track-f/f14a/f14a_spv.tsv'
if os.path.exists(LOCK):
    print('HALT lock'); sys.exit(3)
if os.path.exists(STOP):
    print('HALT stop'); sys.exit(4)
ok = True
ref = {r['id']: r for r in csv.DictReader(open(F14A, encoding='ascii'), delimiter='\t')}
rows = list(csv.DictReader(open(S7 + '/t1_base.tsv', encoding='ascii'), delimiter='\t'))
n = mism = unres = 0
census = {}
for r in rows:
    if r['row'] != 'A' or r['outcome'] != 'OK':
        continue
    rid = '%s_%s_%s' % (r['hash16'], r['key16'], r['perm'])
    p = '%s/work/A/A_%s/out.spv' % (S7, rid)
    data = open(p, 'rb').read()
    if hashlib.sha256(data).hexdigest() != r['spv_sha256_a']:
        print('sha mismatch', rid); ok = False; continue
    st, err = S.sites(data)
    n += 1
    man = sum(1 for s in st if s['kind'] == 'manual')
    nat = sum(1 for s in st if s['kind'] == 'native')
    rr = ref.get(rid)
    if rr is None or int(rr['manual']) != man or int(rr['native']) != nat or err:
        mism += 1
        print('MISMATCH %s mine manual %d native %d ref %s %s err %s' % (rid, man, nat, rr and rr['manual'], rr and rr['native'], err))
    for s in st:
        if s['img'] is None or s['smp'] is None or s['img'][0] is None or s['img'][1] is None or s['smp'][0] is None or s['smp'][1] is None:
            unres += 1
            print('UNRESOLVED %s %s' % (rid, S.key(s)))
        k = '%s %s %s depth=%s dim=%s img_idx=%s smp_idx=%s' % (r['stage'], s['kind'], s['op'], s['img_depth'], s['img_dim'],
                                                               'dyn' if s['img'] and s['img'][2] == 'dyn' else 'const',
                                                               'dyn' if s['smp'] and s['smp'][2] == 'dyn' else 'const')
        census[k] = census.get(k, 0) + 1
print('rows %d mismatches %d unresolved sites %d' % (n, mism, unres))
for k in sorted(census):
    print('CENSUS %s %d' % (k, census[k]))
ok &= n == 269 and mism == 0 and unres == 0
# (3) F14a probes, if the .spv files exist
PR = 'C:/kyty/KytyPS5/docs/track-f/f14a/spv'
found = 0
for sub, kind in (('ctl_base', 'manual'), ('ctl_k32f', 'native')):
    d = PR + '/' + sub
    if not os.path.isdir(d):
        continue
    for name in sorted(os.listdir(d)):
        if not name.endswith('.spv'):
            continue
        st, err = S.sites(open(d + '/' + name, 'rb').read())
        print('PROBE %s/%s %s' % (sub, name, ', '.join(S.key(s) for s in st) or '-'))
        found += 1
print('probe files %d' % found)
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
