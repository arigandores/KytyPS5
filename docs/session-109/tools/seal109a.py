"""Session 109: place ent109 files in C:/kyty/s109, seal pred/01_ent109.md, pin the scorer, write SEALS109.txt."""
import hashlib
import shutil
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
DST = Path('C:/kyty/s109')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


seal = DST / 'pred' / '01_ent109.md'
assert not seal.exists(), 'seal exists already'
assert sha('C:/kyty/build/install/kyty_emulator.exe').startswith('e90f55438d95'), 'build changed'
for name in ('gates_fam0.txt', 'gates_fam4.txt'):
    assert (DST / name).is_file(), name
for name in ('ent109.py', 'test_ent109.py', 'go109.sh', 'mut_ent109.py'):
    assert not (DST / name).exists(), name
    (DST / name).write_bytes((STAGE / name).read_bytes().replace(b'\r\n', b'\n'))
shutil.copy2('C:/kyty/build/install/kyty_emulator.exe', DST / 'kyty_emulator_e90f5543.exe')
(DST / 'pred').mkdir(exist_ok=True)
seal.write_bytes((STAGE / '01_ent109.md').read_bytes().replace(b'\r\n', b'\n'))
seal_sha, seal_bytes = sha(seal), seal.stat().st_size
s = (DST / 'ent109.py').read_bytes().decode('utf-8')
a = "PRED_SHA = None          # filled by the executor when pred/01 is sealed"
b = "PRED_BYTES = None        # filled by the executor when pred/01 is sealed"
assert s.count(a) == 1 and s.count(b) == 1
s = s.replace(a, "PRED_SHA = '%s'   # pred/01 sealed" % seal_sha)
s = s.replace(b, "PRED_BYTES = %d       # pred/01 sealed" % seal_bytes)
(DST / 'ent109.py').write_bytes(s.encode('utf-8'))
seals = ''.join('%s *%s\n' % (sha(DST / p), p) for p in ('pred/01_ent109.md', 'ent109.py', 'test_ent109.py',
                                                          'go109.sh', 'gates_fam0.txt', 'gates_fam4.txt'))
(DST / 'SEALS109.txt').write_bytes(seals.encode('ascii'))
print(seals, end='')
print('seal bytes', seal_bytes)
