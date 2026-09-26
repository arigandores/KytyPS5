"""Session 121 seal 01: fill PRED_SHA / PRED_BYTES of vfy121.py from the final pred/01_vfy121.md and write SEALS121.txt
(sha256 of every sealed file).  LF out.  Run once, after the last edit of the pred."""
import hashlib
from pathlib import Path

R = Path('C:/kyty/s121')
pred = (R / 'pred/01_vfy121.md').read_bytes()
sha, size = hashlib.sha256(pred).hexdigest(), len(pred)
p = R / 'vfy121.py'
s = p.read_bytes().decode('utf-8')
A = 'PRED_SHA = None          # filled by the executor when pred/01_vfy121.md is sealed'
B = 'PRED_BYTES = None        # filled by the executor when pred/01_vfy121.md is sealed'
assert s.count(A) == 1 and s.count(B) == 1
s = s.replace(A, "PRED_SHA = '%s'  # pred/01_vfy121.md, sealed (session 121 seal 01)" % sha)
s = s.replace(B, 'PRED_BYTES = %d        # pred/01_vfy121.md, sealed' % size)
p.write_bytes(s.encode('utf-8'))
files = ['pred/01_vfy121.md', 'design/design121.md', 'vfy121.py', 'test_vfy121.py', 'mut_vfy121.py', 'gates_base.txt',
         'go121a.sh', 'enter_scene.py', 'procload.py', 'kyty_emulator_0bd21ec2.exe', 'chk_vfy121.py']
lines = ['# Session 121 seal 01 (vfy121) - sha256 of every sealed file; written by seal121_01.py', '']
for f in files:
    lines.append('%s  %s' % (hashlib.sha256((R / f).read_bytes()).hexdigest(), f))
lines += ['', 'mutlib v4.1 (docs/session-116/mutlib_v41/mutlib.py db82ef4b) FULL run on the sealed copy: see below', '']
(R / 'SEALS121.txt').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
print(sha, size)
