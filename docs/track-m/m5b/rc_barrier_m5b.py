"""M5b: offline count of the pattern buffer store -> s_barrier -> buffer/flat load in program order (linear over the
reachable walk; loops ignored) - side observation of M5a s2.1 (EmitBarrier without UniformMemory). Read-only."""
import os, sys, collections, csv
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc_tr_m5b.py'), encoding='utf-8').read()
src = src[:src.index('progs = sorted(')]
ns = {}
exec(compile(src, 'rc_tr_m5b', 'exec'), ns)
t1 = collections.defaultdict(set)
for r in csv.DictReader(open('C:/kyty/m657/m2a/corpus/corpus_m2a.tsv', encoding='utf-8'), delimiter='\t'):
    t1[r['hash16']].add(r['stage'])
D = 'C:/kyty/f287/f23a/eboot_text/'
# MUBUF GFX10: stores 0x04-0x07 (format), 0x18-0x1f; loads 0x00-0x03, 0x08-0x0f, 0x20-0x27 (d16); atomics >= 0x30
hits = []
for fn in sorted(os.listdir(D)):
    b = open(D + fn, 'rb').read()
    words = [int.from_bytes(b[i:i + 4], 'little') for i in range(0, len(b) // 4 * 4, 4)]
    st = 0; ex = None
    for pc, fam, w, w1, size, info in ns['walk'](words):
        if fam == 'MUBUF':
            op = info['op']
            if 0x04 <= op <= 0x07 or 0x18 <= op <= 0x1f:
                st = max(st, 1)
            elif (op <= 0x03 or 0x08 <= op <= 0x0f or 0x20 <= op <= 0x27) and st == 2:
                ex = pc; break
        if fam == 'MTBUF':
            op = ((w >> 16) & 7) | (((w1 >> 21) & 1) << 3)
            if op >= 4:
                st = max(st, 1)
            elif st == 2:
                ex = pc; break
        if fam == 'FLAT':
            op = (w >> 18) & 0x7f
            if 0x18 <= op <= 0x1f:
                st = max(st, 1)
            elif 0x08 <= op <= 0x0f and st == 2:
                ex = pc; break
        if fam == 'SOPP' and info['op'] == 0x0a and st == 1:
            st = 2
    if ex is not None:
        hits.append((fn[:16], ex))
print('programs with store -> s_barrier -> load (any resource, linear)', len(hits), 'in T1', sum(1 for h, _ in hits if h in t1))
print(sorted(h + ':' + ','.join(sorted(t1.get(h, ['-']))) + '@' + str(p) for h, p in hits)[:60])
print('ALL DONE')
