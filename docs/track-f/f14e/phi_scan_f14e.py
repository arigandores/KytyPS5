# F14e member (g)(0)(b): indirect image tables with depth compare in T1 corpus A rows.
# An indirect image sample is emitted as OpSwitch + OpPhi over per-candidate samples
# (spirvEmitterImage.cpp:893-917). Count OpPhi whose incoming values are image-sample results.
import csv, struct, sys, os, collections
S7 = 'C:/kyty/s288/s7'
SAMPLE = {87: 'Implicit', 88: 'Explicit', 89: 'DrefImplicit', 90: 'DrefExplicit', 96: 'Gather', 97: 'DrefGather'}
rows = list(csv.DictReader(open(S7 + '/t1_base.tsv', encoding='ascii'), delimiter='\t'))
out = []
tot = collections.Counter()
for r in rows:
    if os.path.exists('C:/kyty/SEALED_RUN.lock'):
        print('HALT lock'); sys.exit(3)
    if r['row'] != 'A' or r['outcome'] != 'OK':
        continue
    rid = '%s_%s_%s' % (r['hash16'], r['key16'], r['perm'])
    p = '%s/work/A/A_%s/out.spv' % (S7, rid)
    if not os.path.exists(p):
        continue
    b = open(p, 'rb').read()
    w = struct.unpack('<%dI' % (len(b) // 4), b)
    i = 5
    defop = {}
    phis = []
    uses_extract = collections.defaultdict(list)
    while i < len(w):
        op = w[i] & 0xffff; n = w[i] >> 16
        if n == 0: break
        ins = w[i:i + n]
        if op in SAMPLE:
            defop[ins[2]] = op
        elif op == 245:  # OpPhi
            phis.append(ins)
        i += n
    tot['rows'] += 1
    tot['samples'] += len(defop)
    tot['phis'] += len(phis)
    tot['switch'] += sum(1 for _ in [0])*0
    for ph in phis:
        inc = [ph[k] for k in range(3, len(ph), 2)]
        kinds = set(SAMPLE[defop[v]] for v in inc if v in defop)
        if kinds:
            tot['phi_sample'] += 1
            dref = any('Dref' in k for k in kinds)
            out.append((rid, len(inc), ','.join(sorted(kinds)), dref))
print('rows scanned', tot['rows'], 'image sample results', tot['samples'], 'OpPhi total', tot['phis'], 'phi over image samples', tot['phi_sample'])
c = collections.Counter((k, d) for _, _, k, d in out)
for k, v in sorted(c.items()): print('  kinds=%s dref=%s : %d' % (k[0], k[1], v))
rows_with = sorted(set(x[0] for x in out))
print('rows with phi-of-sample', len(rows_with))
open('phi_scan_f14e.tsv', 'w', encoding='ascii').write(''.join('%s\t%d\t%s\t%d\n' % (a, n, k, d) for a, n, k, d in out))
print('ALL OK')
