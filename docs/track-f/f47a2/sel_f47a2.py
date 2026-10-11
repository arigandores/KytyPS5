# F47a2 (HPP-807, ROADMAP s122 item 708(b)(11)): select the recordings for the detector of F47a section 1.3 - ALL recordings
# of underwater_aerial_garden (Sky Garden), big_hand_pirate_island, timestop_casino and pot_treasure_cave of the map
# (map_f47a.py output; rows after the FS8 install 2026-10-05T11:39:58Z plus the four early EXTRA rows of map_f47a.py, which
# are kept and marked 'pre-FS8'). Writes <out>_main.tsv (window LO 600 HI 950) and <out>_ts.tsv (timestop_casino,
# window LO 600 HI 1700 - F47a batch_ts form), rows: tag mp4 log; and <out>_meta.tsv: tag level mtime sha8 era new.
# 'new' = the mp4 path is absent from the F47a map (docs/track-f/f47a/map.tsv), i.e. recorded after the F47a listing.
# sha8 - the last column of the map row (map_f47a.py now prints 10 columns, the F47a map.tsv 9).
# Usage: python sel_f47a2.py <map.tsv now> <F47a map.tsv> <out prefix>
import sys

LEVELS = ('underwater_aerial_garden', 'big_hand_pirate_island', 'timestop_casino', 'pot_treasure_cave')
FS8 = '2026-10-05T11:39:58Z'


def rows(p):
    out = []
    for ln in open(p, encoding='utf-8'):
        r = ln.rstrip('\n').split('\t')
        if len(r) >= 9 and r[0] != 'mtime' and not ln.startswith('watch:'):
            out.append(r)
    return out


now, old, pre = sys.argv[1], sys.argv[2], sys.argv[3]
old_mp4 = {r[1] for r in rows(old)}
sel = [r for r in rows(now) if r[5] in LEVELS]
with open(pre + '_main.tsv', 'w', encoding='utf-8', newline='\n') as m, \
        open(pre + '_ts.tsv', 'w', encoding='utf-8', newline='\n') as t, \
        open(pre + '_meta.tsv', 'w', encoding='utf-8', newline='\n') as meta:
    meta.write('tag\tlevel\tmtime\tsha8\tera\tnew\tmp4\n')
    n = {}
    for r in sel:
        mtime, mp4, idx, tag, logp, lvl, sha8 = r[0], r[1], r[2], r[3], r[4], r[5], r[-1]
        if idx != '1' or not logp:
            meta.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\tSKIP_no_idx_or_log\n' % (tag, lvl, mtime, sha8, '', '', mp4))
            continue
        era = 'FS8+' if mtime >= FS8 else 'pre-FS8'
        new = 'new' if mp4 not in old_mp4 else ''
        (t if lvl == 'timestop_casino' else m).write('%s\t%s\t%s\n' % (tag, mp4, logp))
        meta.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (tag, lvl, mtime, sha8, era, new, mp4))
        n[(lvl, era)] = n.get((lvl, era), 0) + 1
for k in sorted(n):
    print(k[0], k[1], n[k])
