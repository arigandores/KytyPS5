# F47a (HPP-802): comparison sheet of the title-card blocks across binaries. For every row of batch.tsv named on the command
# line: the middle frame (start + 2) of the first black run, of the white run and of the second black run, the top 40 % of
# the 960x540 frame scaled to 400 px wide; one row per recording, labelled "tag level sha8 vf".
# Usage: python cmp_f47a.py <batch.tsv> <list.tsv (tag mp4 log)> <out.png> <tag> [<tag> ...]
import hashlib, subprocess, sys
from PIL import Image, ImageDraw

batch, lst, outp, tags = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
SHA = {}
for ln in open('C:/kyty/f287/f47a/map.tsv', encoding='utf-8'):
    p = ln.rstrip('\n').split('\t')
    if len(p) > 9 and p[0].startswith('2026'):
        SHA[p[1]] = p[-1]
mp4s = {l.split('\t')[0]: l.split('\t')[1] for l in open(lst, encoding='utf-8') if l.strip()}
rows = {}
for ln in open(batch, encoding='utf-8'):
    p = ln.rstrip('\n').split('\t')
    if len(p) > 10 and not ln.startswith('#') and p[0] != 'tag':
        rows[p[0]] = p
TW, CH = 400, 0.40
cells = []
for tag in tags:
    p = rows[tag]
    def long_runs(field):
        # runs of >= 4 frames only (a 1-2 frame black run is a cut or a fade, not a block - u_12 913-918 sheet)
        out = []
        for r in field.split():
            if r == '-':
                continue
            a, b = (int(x) for x in r.split(';')[0].split('-'))
            if b - a + 1 >= 4:
                out.append('%d-%d' % (a, b))
        return out

    k = long_runs(p[8])
    w = long_runs(p[9])
    picks = []
    if k:
        picks.append(int(k[0].split('-')[0]) + 2)
    if w:
        picks.append(int(w[0].split('-')[0]) + 2)
    if len(k) > 1:
        picks.append(int(k[1].split('-')[0]) + 2)
    imgs = []
    for vf in picks:
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp4s[tag], '-vf', "select='eq(n%s%d)'" % (chr(92) + ',', vf),
                              '-vsync', '0', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             capture_output=True, check=True).stdout
        im = Image.frombytes('RGB', (960, 540), raw).crop((0, 0, 960, int(540 * CH))).resize((TW, int(TW * 540 * CH / 960)))
        imgs.append((vf, im))
    cells.append((tag, p[1], SHA.get(mp4s[tag], ''), imgs))
ih = int(TW * 540 * CH / 960)
LAB = 16
out = Image.new('RGB', (TW * 3, (ih + LAB) * len(cells)), (40, 40, 40))
d = ImageDraw.Draw(out)
for r, (tag, lvl, sha, imgs) in enumerate(cells):
    y = r * (ih + LAB)
    d.text((4, y + 2), '%s  %s  %s  vf %s' % (tag, lvl, sha, ' / '.join(str(v) for v, _ in imgs)), fill=(255, 255, 0))
    for c, (vf, im) in enumerate(imgs):
        out.paste(im, (c * TW, y + LAB))
out.save(outp)
print(outp, len(cells), 'rows sha256', hashlib.sha256(open(outp, 'rb').read()).hexdigest())
