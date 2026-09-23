"""Session 110: place stl110 files in C:/kyty/s110, seal pred/01_stl110.md, pin the scorer, write SEALS110.txt."""
import hashlib
import re
import shutil
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
DST = Path('C:/kyty/s110')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


assert sha('C:/kyty/build/install/kyty_emulator.exe').startswith('b3f7a2c957dd'), 'build changed'
seal = DST / 'pred' / '01_stl110.md'
assert not seal.exists()
for g in ('gates_free0.txt', 'gates_free1.txt', 'gates_base.txt'):
    assert (DST / g).is_file(), g
for name in ('stl110.py', 'make_stl110.py', 'test_stl110.py', 'make_test_stl110.py', 'mut_stl110.py', 'go110.sh'):
    assert not (DST / name).exists(), name
    (DST / name).write_bytes((STAGE / name).read_bytes().replace(b'\r\n', b'\n'))
shutil.copy2('C:/kyty/build/install/kyty_emulator.exe', DST / 'kyty_emulator_b3f7a2c9.exe')
(DST / 'pred').mkdir(exist_ok=True)
seal.write_bytes((STAGE / '01_stl110.md').read_bytes().replace(b'\r\n', b'\n'))
p = DST / 'stl110.py'
s = p.read_bytes().decode('utf-8')
a = re.search(r'^PRED_SHA = None .*$', s, re.M)
b = re.search(r'^PRED_BYTES = None .*$', s, re.M)
assert a and b
s = s.replace(a.group(0), "PRED_SHA = '%s'   # pred/01_stl110.md sealed" % sha(seal))
s = s.replace(b.group(0), "PRED_BYTES = %d       # pred/01_stl110.md sealed" % seal.stat().st_size)
p.write_bytes(s.encode('utf-8'))
listed = ['pred/01_stl110.md', 'stl110.py', 'make_stl110.py', 'test_stl110.py', 'make_test_stl110.py', 'mut_stl110.py',
          'go110.sh', 'gates_free0.txt', 'gates_free1.txt']
text = ''.join('%s *%s\n' % (sha(DST / x), x) for x in listed)
(DST / 'SEALS110.txt').write_bytes(text.encode('ascii'))
print(text, end='')
