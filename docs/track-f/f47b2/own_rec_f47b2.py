# F47b2 (HPP-808, Red Team): own recount of (b)(11) data of F47a2 on a sample of records, independent of
# det_f47a.py / batch_f47a.py: full 960x540 frames, band y < 162 (top 30 %), black = all channels <= 8,
# white = all channels >= 247; a frame is "black" when the band holds >= MINPX = 1000 such pixels, "white" when >= MINW = 4000
# (edition 1 of this script used 1000 for white too - too loose: other white UI in the band; 4000 at 960x540 = 1000 at 480x270).
# Window: [b0 - 60; b0 + 60] video frames, b0 = start of the sum.tsv black run followed by a white run at +7 (else the
# first black run) - location only, not the verdict.
# Output: per record own black / white runs, own s555 (black 5 at a, white 5 at a + 7, black 5 at a + 15) or
# len4 (pot_treasure_cave: black run of exactly 4), and equality with sum.tsv runs.
import csv, subprocess, sys
import numpy as np

SUM, SELS, OUT = sys.argv[1], sys.argv[2].split(','), sys.argv[3]
W, H, BH, MINPX, MINW, HALF = 960, 540, 162, 1000, 4000, 60

rows = {r['tag']: r for r in csv.DictReader(open(SUM, encoding='utf-8'), delimiter='\t')}
mp4 = {}
for s in SELS:
    for line in open(s, encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) >= 2:
            mp4[f[0]] = f[1]

# sample: records NOT the first of their binary in sum.tsv order (F47a ran one per binary), plus the two records
# after the F47a list, plus one of each other level
seen, sample = set(), []
for tag, r in rows.items():
    if r['level'] != 'underwater_aerial_garden' or r['era'] == 'pre-FS8':
        continue
    if r['sha8'] in seen and len(sample) < 10:
        sample.append(tag)
    seen.add(r['sha8'])
for t in ('fs13_z', 'f24_n1'):
    if t in rows and t not in sample:
        sample.append(t)
for lvl in ('pot_treasure_cave', 'big_hand_pirate_island', 'timestop_casino'):
    for tag, r in rows.items():
        if r['level'] == lvl and r['era'] != 'pre-FS8':
            sample.append(tag)
            break


def runs(flags, base):
    out, i = [], 0
    while i < len(flags):
        if flags[i]:
            j = i
            while j + 1 < len(flags) and flags[j + 1]:
                j += 1
            out.append((base + i, base + j))
            i = j + 1
        else:
            i += 1
    return out


def fmt(rs):
    return ' '.join('%d-%d' % r for r in rs)


ok_all = True
with open(OUT, 'w', encoding='utf-8') as o:
    o.write('tag\tlevel\tsha8\tb0\town_black\town_white\town_form\tsum_black\tsum_white\tsum_form\tsame\n')
    for tag in sample:
        r = rows[tag]
        bl = [int(x.split('-')[0]) for x in r['black_runs'].split() if x[:1].isdigit()]
        wl = [int(x.split('-')[0]) for x in r['white_runs'].split() if x[:1].isdigit()]
        b0 = next((s for s in bl if s + 7 in wl), bl[0])
        a, b = max(0, b0 - HALF), b0 + HALF
        sel = "select='between(n%s%d%s%d)'" % (chr(92) + ',', a, chr(92) + ',', b)
        p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp4[tag], '-vf', sel, '-vsync', '0', '-f', 'rawvideo',
                            '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        arr = np.frombuffer(p.stdout, dtype=np.uint8)
        n = arr.size // (W * H * 3)
        arr = arr[:n * W * H * 3].reshape(n, H, W, 3)[:, :BH]
        blk = [(f.max(axis=2) <= 8).sum() >= MINPX for f in arr]
        wht = [(f.min(axis=2) >= 247).sum() >= MINW for f in arr]
        br, wr = runs(blk, a), runs(wht, a)
        if r['level'] == 'pot_treasure_cave':
            form = 'len4' if any(e - s + 1 == 4 for s, e in br) else 'no'
            sform = 'len4' if r['len4'] == 'yes' else 'no'
        else:
            bs = {s: e - s + 1 for s, e in br}
            ws = {s: e - s + 1 for s, e in wr}
            form = 'no'
            for s, ln in bs.items():
                if ln == 5 and ws.get(s + 7) == 5 and bs.get(s + 15) == 5:
                    form = 's555@%d' % s
                    break
            sform = 's555' if r['s555'] == 'yes' else 'no'
        # own runs inside the window vs sum.tsv runs inside the window
        sb = [x for x in r['black_runs'].split() if x[:1].isdigit() and a <= int(x.split('-')[0]) <= b]
        sw = [x for x in r['white_runs'].split() if x[:1].isdigit() and a <= int(x.split('-')[0]) <= b]
        same = (fmt(br).split() == sb and fmt(wr).split() == sw and form.split('@')[0] == sform)
        ok_all &= same
        o.write('\t'.join([tag, r['level'], r['sha8'], str(b0), fmt(br), fmt(wr), form, ' '.join(sb), ' '.join(sw), sform,
                           'yes' if same else 'NO']) + '\n')
        o.flush()
    o.write('records %d all_same %s\n' % (len(sample), 'yes' if ok_all else 'NO'))
print(open(OUT, encoding='utf-8').read())
