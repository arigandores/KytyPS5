"""Session 121 seal 02: fill PRED_SHA / PRED_BYTES / VFY_SCORER_SHA of shp121.py (pred/02_shp121.md; the sealed
vfy121.py) and append the seal-02 shas to SEALS121.txt.  LF out.  Run once, after the last edit of the pred."""
import hashlib
from pathlib import Path

R = Path('C:/kyty/s121')
pred = (R / 'pred/02_shp121.md').read_bytes()
sha, size = hashlib.sha256(pred).hexdigest(), len(pred)
vsha = hashlib.sha256((R / 'vfy121.py').read_bytes()).hexdigest()
assert vsha.startswith('43359b14'), vsha
p = R / 'shp121.py'
s = p.read_bytes().decode('utf-8')
A = 'PRED_SHA = None          # filled by the executor when C:/kyty/s121/pred/02_shp121.md is sealed'
B = 'PRED_BYTES = None        # filled by the executor when C:/kyty/s121/pred/02_shp121.md is sealed'
V = 'VFY_SCORER_SHA = None          # filled by the executor at seal 02'
assert s.count(A) == 1 and s.count(B) == 1 and s.count(V) == 1
s = s.replace(A, "PRED_SHA = '%s'  # pred/02_shp121.md, sealed (session 121 seal 02)" % sha)
s = s.replace(B, 'PRED_BYTES = %d        # pred/02_shp121.md, sealed' % size)
s = s.replace(V, "VFY_SCORER_SHA = '%s'  # vfy121.py, sealed at seal 01" % vsha)
p.write_bytes(s.encode('utf-8'))
files = ['pred/02_shp121.md', 'shp121.py', 'test_shp121.py', 'mut_shp121.py', 'chk_vfy121.py', 'go121a.sh',
         'runs121/vfy121.score.json', 'vfy121.py']
lines = ['', '# Session 121 seal 02 (shp121) - sha256 of every sealed file; written by seal121_02.py', '']
for f in files:
    lines.append('%s  %s' % (hashlib.sha256((R / f).read_bytes()).hexdigest(), f))
with open(R / 'SEALS121.txt', 'ab') as fh:
    fh.write(('\n'.join(lines) + '\n').encode('utf-8'))
print(sha, size, vsha)
