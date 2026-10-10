# F32d (HPP-742, ROADMAP p.673(z)(3)(1)): the loglist of the 36 emulator logs outside the F32a mask (F32b scope,
# docs/track-f/f32b/outglob.txt) in the format of sweep_f32a.py (path, size, mtime, kind, orig_size, status, note), so that
# sweep_f32a.py / wit_f32a.py run on them unchanged with F32A_OUT=<out>.  Every row is SWEEP (the F0 rule FIX and the
# manifest shortcut are not applied: the list is fixed by F32b).  .xz rows get orig_size 0 (read whole as one task).
# Usage: python list_f32d.py <outglob.txt> <out_dir>   -> <out_dir>/loglist_f32a.tsv
import os, sys
TAB = chr(9)
NL = chr(10)
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
if os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(4)
src, out = sys.argv[1], sys.argv[2]
rows = []
for l in open(src, encoding='utf-8'):
    p = l.strip()
    if not p:
        continue
    st = os.stat(p)
    kind = 'xz' if p.endswith('.xz') else 'txt'
    rows.append((p, st.st_size, int(st.st_mtime), kind, 0 if kind == 'xz' else st.st_size, 'SWEEP', 'F32b out-of-mask'))
rows.sort()
with open(out + '/loglist_f32a.tsv', 'w', encoding='utf-8', newline=NL) as o:
    for r in rows:
        o.write(TAB.join(str(x) for x in r) + NL)
print('rows', len(rows), 'txt', sum(1 for r in rows if r[3] == 'txt'), 'xz', sum(1 for r in rows if r[3] == 'xz'),
      'bytes', sum(r[1] for r in rows))
