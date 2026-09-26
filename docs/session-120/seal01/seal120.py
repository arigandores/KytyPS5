"""Session 120 seal 01: fill PRED_SHA / PRED_BYTES of rpk120.py and spc120.py from the final pred/01_cen120.md and
write SEALS120.txt (sha256 of every sealed file).  LF out.  Run once, after the last edit of the pred."""
import hashlib
from pathlib import Path

R = Path('C:/kyty/s120')
pred = (R / 'pred/01_cen120.md').read_bytes()
sha, size = hashlib.sha256(pred).hexdigest(), len(pred)
A = 'PRED_SHA = None          # filled by the executor when pred/01_cen120.md is sealed'
B = 'PRED_BYTES = None        # filled by the executor when pred/01_cen120.md is sealed'
for name in ('rpk120.py', 'spc120.py'):
    p = R / name
    s = p.read_bytes().decode('utf-8')
    assert s.count(A) == 1 and s.count(B) == 1, name
    s = s.replace(A, "PRED_SHA = '%s'  # pred/01_cen120.md, sealed (session 120 seal 01)" % sha)
    s = s.replace(B, 'PRED_BYTES = %d        # pred/01_cen120.md, sealed' % size)
    p.write_bytes(s.encode('utf-8'))
files = ['pred/01_cen120.md', 'design/design120.md', 'rpk120.py', 'test_rpk120.py', 'mut_rpk120.py', 'spc120.py',
         'test_spc120.py', 'mut_spc120.py', 'gates_base.txt', 'go120a.sh', 'enter_scene.py', 'procload.py',
         'kyty_emulator_15cdbfc6.exe', 'smoke120.py']
lines = ['# Session 120 seal 01 (cen120) - sha256 of every sealed file; written by seal120.py', '']
for f in files:
    lines.append('%s  %s' % (hashlib.sha256((R / f).read_bytes()).hexdigest(), f))
lines += ['', 'mutlib v4.1 (docs/session-116/mutlib_v41/mutlib.py db82ef4b) FULL runs on the sealed copies: see below', '']
(R / 'SEALS120.txt').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
print(sha, size)
