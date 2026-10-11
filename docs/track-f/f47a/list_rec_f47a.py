# F47a (HPP-802): list of video recordings under C:/kyty (mtime UTC, size, .idx present).
# Usage: python list_rec_f47a.py > out.tsv
import os, sys, time

ROOT = 'C:/kyty'
SKIP = ('KytyPS5', '_cleanup401')

rows = []
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if f.endswith('.mp4'):
            p = os.path.join(root, f).replace(os.sep, '/')
            st = os.stat(p)
            rows.append((st.st_mtime, p, st.st_size, os.path.exists(p + '.idx')))
rows.sort()
for m, p, s, i in rows:
    print('%s\t%d\t%d\t%s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(m)), s, int(i), p))
