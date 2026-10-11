# F47a2 (HPP-807, item 708(b)(11)): summary of the F47a detector over all selected recordings.
# Per row of batch_main.tsv / batch_ts.tsv (batch_f47a.py output) joined with sel_meta.tsv (level, mtime, sha8, era, new):
#   blocks   - at least one black run (K >= 150 in the title band) in the window;
#   s555     - the F47a series: a black run of 5 video frames at v, a white run of 5 at v + 7, a black run of 5 at v + 15
#              (video frame numbers; the structure of F47a section 1.3);
#   dn555    - dn of the first black run of the s555 series ('-' if none);
#   len4     - pot_treasure_cave form (F47a section 1.3): at least one black run of exactly 4 video frames;
#   dn1      - dn of the first black run (F47a section 1.2; '?' if a present of the run is missing in .idx);
#   d<0      - the recording lost video frames (B38): dn is not quoted (F47a section 1.2).
# Output: table rows (tsv) and the counts per level and era, 'N of N with blocks'.
# Usage: python sum_f47a2.py sel_meta.tsv batch_main.tsv batch_ts.tsv > sum.tsv
import sys

meta = {}
for ln in open(sys.argv[1], encoding='utf-8'):
    r = ln.rstrip('\n').split('\t')
    if r[0] == 'tag' or len(r) < 7:
        continue
    meta.setdefault(r[0], []).append(r)
rows = []
for p in sys.argv[2:]:
    for ln in open(p, encoding='utf-8'):
        if ln.startswith('#') or ln.startswith('tag\t'):
            continue
        rows.append(ln.rstrip('\n').split('\t'))


def runs(field):
    out = []
    if field in ('', '-', None):
        return out
    for item in field.split(' '):
        vf, pr, dn = item.split(';')
        a, b = vf.split('-')
        out.append((int(a), int(b), dn.split('-')[0]))
    return out


used = {}
print('tag\tlevel\tera\tsha8\tnew\td\tblack_runs\twhite_runs\tblocks\ts555\tdn1\tdn555\tlen4')
cnt = {}
for r in rows:
    tag, lvl = r[0], r[1]
    k = used.get(tag, 0)
    used[tag] = k + 1
    m = meta[tag][k]
    era, sha8, new = m[4], m[3], m[5]
    if r[8] == 'NO_START':
        blocks, s555, dn1, d, dn555, len4 = 'NO_START', '-', '-', '-', '-', '-'
        bl, wh = [], []
    else:
        d = int(r[5])
        bl, wh = runs(r[8]), runs(r[9])
        blocks = 'yes' if bl else 'no'
        s555, dn555 = 'no', '-'
        len4 = 'yes' if any(b - a == 3 for a, b, _ in bl) else 'no'
        for a, b, dnx in bl:
            if b - a == 4 and any(x == a + 7 and y - x == 4 for x, y, _ in wh) and \
                    any(x == a + 15 and y - x == 4 for x, y, _ in bl):
                s555, dn555 = 'yes', dnx
                break
        dn1 = bl[0][2] if bl else '-'
        if d < 0:
            dn1 = dn555 = 'd<0'
    key = (m[1], era)
    c = cnt.setdefault(key, [0, 0, 0, 0])
    c[0] += 1
    c[1] += blocks == 'yes'
    c[2] += s555 == 'yes'
    c[3] += len4 == 'yes'
    print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (tag, m[1], era, sha8, new, d,
                                                          ' '.join('%d-%d' % (a, b) for a, b, _ in bl) or '-',
                                                          ' '.join('%d-%d' % (a, b) for a, b, _ in wh) or '-',
                                                          blocks, s555, dn1, dn555, len4))
print('#')
print('# level\tera\trecordings\twith_blocks\twith_s555\twith_len4')
for k in sorted(cnt):
    c = cnt[k]
    print('# %s\t%s\t%d\t%d\t%d\t%d' % (k[0], k[1], c[0], c[1], c[2], c[3]))
