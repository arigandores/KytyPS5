# F47a2 (HPP-807, item 708(b)(11)): resumable driver of the F47a detector (docs/track-f/f47a/batch_f47a.py, unchanged) -
# one call per recording, output rows/<list>_<i>.tsv; a row already written is skipped, so a run killed by the watchdog
# (foreign lock) is continued by calling the driver again. At the end the per-row files are joined into <out>.tsv
# (header of batch_f47a.py once, rows in list order).
# Usage: python drive_f47a2.py <list.tsv: tag mp4 log> <out.tsv> [batch args, e.g. --hi 1700]
import os, subprocess, sys

BATCH = 'C:/kyty/KytyPS5/docs/track-f/f47a/batch_f47a.py'
lst, outp, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
base = os.path.splitext(os.path.basename(lst))[0]
rd = os.path.join(os.path.dirname(os.path.abspath(outp)), 'rows')
os.makedirs(rd, exist_ok=True)
rows = [l for l in open(lst, encoding='utf-8') if l.strip() and not l.startswith('#')]
for i, row in enumerate(rows):
    one = os.path.join(rd, '%s_%03d.tsv' % (base, i))
    if os.path.exists(one) and open(one, encoding='utf-8').read().count('\n') >= 3:
        continue
    li = os.path.join(rd, '%s_%03d.list' % (base, i))
    open(li, 'w', encoding='utf-8', newline='\n').write(row)
    tmp = one + '.part'
    subprocess.run([sys.executable, BATCH, li, tmp] + extra, check=True)
    os.replace(tmp, one)
hdr, body = None, []
for i in range(len(rows)):
    ls = open(os.path.join(rd, '%s_%03d.tsv' % (base, i)), encoding='utf-8').read().splitlines()
    hdr = hdr or ls[:2]
    body.extend(ls[2:])
with open(outp, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(hdr + body) + '\n')
print('joined', len(body), 'rows ->', outp)
