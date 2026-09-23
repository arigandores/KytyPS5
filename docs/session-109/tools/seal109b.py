"""Session 109: place the cspfree scorers in C:/kyty/s109, write gates_free{0,1,2}.txt, seal pred/01b, 02, 03,
pin PRED_SHA/PRED_BYTES in vfy109.py, ent109b.py, frf109.py, append SEALS109.txt.  One-shot."""
import hashlib
import re
import shutil
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
DST = Path('C:/kyty/s109')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


assert sha('C:/kyty/build/install/kyty_emulator.exe').startswith('2f5932296d56'), 'build changed'
seals = {'pred/01b_vfy109.md': '01b_vfy109.md', 'pred/02_ent109b.md': '02_ent109b.md',
         'pred/03_frf109.md': '03_frf109.md'}
for dst in seals:
    assert not (DST / dst).exists(), dst
files = {'vfy109.py': 'vfy109.py', 'test_vfy109.py': 'test_vfy109.py', 'ent109b.py': 'ent109b.py',
         'make_ent109b.py': 'make_ent109b.py', 'test_ent109b.py': 'test_ent109b.py', 'mut_ent109b.py': 'mut_ent109b.py',
         'frf109.py': 'frf109/frf109.py', 'make_frf109.py': 'frf109/make_frf109.py',
         'test_frf109.py': 'frf109/test_frf109.py', 'mut_frf109.py': 'frf109/mut_frf109.py', 'go109b.sh': 'go109b.sh'}
for dst, src in files.items():
    assert not (DST / dst).exists(), dst
    (DST / dst).write_bytes((STAGE / src).read_bytes().replace(b'\r\n', b'\n'))
shutil.copy2('C:/kyty/build/install/kyty_emulator.exe', DST / 'kyty_emulator_2f593229.exe')
base = (DST / 'gates_base.txt').read_bytes()
assert base.endswith(b'\r\n') and base.count(b'\n') == 1
for v in (0, 1, 2):
    (DST / ('gates_free%d.txt' % v)).write_bytes(base[:-2] + (' cspfree=%d\r\n' % v).encode())
for dst, src in seals.items():
    (DST / dst).write_bytes((STAGE / src).read_bytes().replace(b'\r\n', b'\n'))
pins = {'vfy109.py': 'pred/01b_vfy109.md', 'ent109b.py': 'pred/02_ent109b.md', 'frf109.py': 'pred/03_frf109.md'}
for scorer, seal in pins.items():
    p = DST / scorer
    s = p.read_bytes().decode('utf-8')
    a = re.search(r'^PRED_SHA = None .*$', s, re.M)
    b = re.search(r'^PRED_BYTES = None .*$', s, re.M)
    assert a and b and len(re.findall(r'^PRED_SHA = None', s, re.M)) == 1, scorer
    s = s.replace(a.group(0), "PRED_SHA = '%s'   # %s sealed" % (sha(DST / seal), seal))
    s = s.replace(b.group(0), "PRED_BYTES = %d       # %s sealed" % ((DST / seal).stat().st_size, seal))
    p.write_bytes(s.encode('utf-8'))
listed = ['pred/01b_vfy109.md', 'pred/02_ent109b.md', 'pred/03_frf109.md', 'vfy109.py', 'test_vfy109.py', 'ent109b.py',
          'make_ent109b.py', 'test_ent109b.py', 'frf109.py', 'make_frf109.py', 'test_frf109.py', 'go109b.sh',
          'gates_free0.txt', 'gates_free1.txt', 'gates_free2.txt']
text = ''.join('%s *%s\n' % (sha(DST / p), p) for p in listed)
with open(DST / 'SEALS109.txt', 'ab') as f:
    f.write(text.encode('ascii'))
print(text, end='')
