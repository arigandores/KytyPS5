"""M5b: count PS programs exporting MRTZ with Z enabled (EXP tgt 8, en bit0) - T109 case (v). Read-only."""
import os, sys, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc_tr_m5b.py'), encoding='utf-8').read()
src = src[:src.index('progs = sorted(')]
ns = {}
exec(compile(src, 'rc_tr_m5b', 'exec'), ns)
import csv
t1 = collections.defaultdict(set)
for r in csv.DictReader(open('C:/kyty/m657/m2a/corpus/corpus_m2a.tsv', encoding='utf-8'), delimiter='\t'):
    t1[r['hash16']].add(r['stage'])
D = 'C:/kyty/f287/f23a/eboot_text/'
hits = collections.Counter(); progs = set(); en_hist = collections.Counter()
for fn in sorted(os.listdir(D)):
    b = open(D + fn, 'rb').read()
    words = [int.from_bytes(b[i:i + 4], 'little') for i in range(0, len(b) // 4 * 4, 4)]
    for pc, fam, w, w1, size, info in ns['walk'](words):
        if fam == 'EXP':
            tgt = (w >> 4) & 0x3f; en = w & 0xf
            if tgt == 8:
                en_hist[en] += 1
                if en & 1:
                    progs.add(fn[:16])
print('MRTZ exports by en mask', dict(sorted(en_hist.items())))
print('programs exporting Z (en bit0)', len(progs), 'in T1', sum(1 for p in progs if p in t1), sorted(p + ':' + ','.join(sorted(t1.get(p, ['-']))) for p in progs)[:40])
print('ALL DONE')
