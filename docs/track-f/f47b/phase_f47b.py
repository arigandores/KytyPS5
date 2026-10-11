# F47b own check: for each recording in batch.tsv with a black run, phase of the first black run in guest frames (dn)
# and in seconds: (a) sum dt_us of FrameTrace n_start+1..n_block, (b) host seconds of .idx between present(n_start)+d and
# the block present. Also own d check: cross-correlation of .idx present deltas with FrameTrace dt_us near the block.
import re, sys, statistics
B = 'C:/kyty/KytyPS5/docs/track-f/f47a/'
RX = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) ')
lst = {}
for l in open(B + 'batch_list.tsv', encoding='utf-8'):
    if l.startswith('#') or not l.strip():
        continue
    p = l.rstrip('\n').split('\t')
    lst[p[0]] = p
rows = []
for l in open(B + 'batch.tsv', encoding='utf-8'):
    if l.startswith('#') or l.startswith('tag') or not l.strip():
        continue
    p = l.rstrip('\n').split('\t')
    rows.append(p)
only = sys.argv[1] if len(sys.argv) > 1 else None
out = []
for p in rows:
    tag, lvl, n0, d = p[0], p[1], int(p[2]), int(p[5])
    if only and lvl != only:
        continue
    br = p[8].split()
    if not br or br[0] == '-' or d < 0:
        continue
    vf, pr, dn = br[0].split(';')
    pres = int(pr.split('-')[0]); dn0 = int(dn.split('-')[0])
    ent = lst.get(tag)
    if not ent:
        print('nolist', tag); continue
    log = [x for x in ent if x.endswith('.txt')][0]
    mp4 = [x for x in ent if x.endswith('.mp4')][0]
    dt = {}
    with open(log, 'rb') as f:
        for line in f:
            m = RX.match(line)
            if m:
                dt[int(m.group(1))] = int(m.group(2))
    nb = n0 + dn0
    s_ft = sum(dt.get(k, 0) for k in range(n0 + 1, nb + 1)) / 1e6
    idx = {}
    for l in open(mp4 + '.idx'):
        a = l.split()
        if len(a) >= 3:
            idx[int(a[1])] = float(a[2])
    p0 = n0 + d
    s_idx = idx.get(pres, float('nan')) - idx.get(p0, float('nan'))
    # own d: best offset o in [d-40, d+40] matching idx deltas to dt_us over presents pres-300..pres+50
    best = None
    for o in range(d - 40, d + 41):
        err = 0; cnt = 0
        for q in range(pres - 300, pres + 50):
            if q in idx and q - 1 in idx and (q - o) in dt:
                err += abs((idx[q] - idx[q - 1]) * 1e6 - dt[q - o]); cnt += 1
        if cnt > 200:
            e = err / cnt
            if best is None or e < best[1]:
                best = (o, e, cnt)
    out.append((tag, lvl, n0, d, dn0, s_ft, s_idx, best))
    print(tag, lvl, 'n0', n0, 'd', d, 'dn', dn0, 's_ft %.2f' % s_ft, 's_idx %.2f' % s_idx,
          'd_xcorr', best[0] if best else None, 'err_us %.0f' % (best[1] if best else -1))
for lv in sorted(set(o[1] for o in out)):
    v = [o for o in out if o[1] == lv]
    if len(v) < 3:
        continue
    dns = [o[4] for o in v]; sft = [o[5] for o in v]
    print('LEVEL', lv, 'N', len(v), 'dn min/max/cv %d %d %.4f' % (min(dns), max(dns), statistics.pstdev(dns) / statistics.mean(dns)),
          's_ft min/max/cv %.2f %.2f %.4f' % (min(sft), max(sft), statistics.pstdev(sft) / statistics.mean(sft)))
