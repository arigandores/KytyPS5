"""M2a2 (HPP-843): apply / restore ONLY the mutant t306_mask of Red Team's C:/kyty/m657/m2c/mut_m2c.py (its EDITS,
HELPER and INCLUDE, read from that file unchanged) on the M2a2 worktree. The mutant is active at M2C_MUT=t306_mask;
unset - main behaviour. Usage: python mut_t306.py patch|restore"""
import hashlib
import subprocess
import sys

SRC = 'C:/kyty/m657/m2c/mut_m2c.py'
WT = 'C:/kyty/m657/m2a2/wt/'
GIT = 'C:/Program Files/Git/cmd/git.exe'
FILE = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp'

raw = open(SRC, 'rb').read()
print('mut_m2c.py sha256', hashlib.sha256(raw).hexdigest())
head = raw.decode('utf-8').split('\ndef patch():')[0]
ns = {}
exec(compile(head, SRC, 'exec'), ns)
anchor, edits = ns['EDITS'][FILE]
edits = [(o, n) for o, n in edits if 'M2cMut("t306_mask")' in n]
assert len(edits) == 1

if sys.argv[1] == 'patch':
    data = open(WT + FILE, 'rb').read()
    assert b'\r' not in data
    lines = data.decode('utf-8').split('\n')
    for old, new in edits:
        idx = [i for i, l in enumerate(lines) if l == old]
        assert len(idx) == 1, (old, idx)
        lines[idx[0]] = new
        print('mutant line:', new.strip())
    idx = [i for i, l in enumerate(lines) if l == anchor]
    assert len(idx) == 1, (anchor, idx)
    lines.insert(idx[0], ns['HELPER'])
    lines.insert(0, ns['INCLUDE'])
    open(WT + FILE, 'wb').write('\n'.join(lines).encode('utf-8'))
    print('patched', FILE)
else:
    subprocess.check_call([GIT, '-C', WT, 'checkout', '--', FILE])
    print(subprocess.check_output([GIT, '-C', WT, 'status', '--short']).decode())
