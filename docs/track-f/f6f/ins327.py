"""F6f (HPP-378): insert the lead point into ROADMAP.md (number = last + 1), register section 23, mirror docs/track-f/f6f/. LF, write_bytes; aborts on lock."""
import os, pathlib, re, shutil, subprocess, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
S = pathlib.Path(os.environ['PAPERCLIP_RUN_SCRATCH_DIR'])
R = pathlib.Path('C:/kyty/KytyPS5')
TIME = subprocess.check_output(['date', '-u', '+%Y-%m-%d %H:%M:%S']).decode().strip()
rm = R / 'docs/ROADMAP.md'
t = rm.read_bytes().decode('utf-8')
assert '\r\n' not in t
nums = [int(m.group(1)) for m in re.finditer(r'(?m)^(\d+)\. \*\*', t)]
N = max(nums)
assert N >= 326, N
assert 'Звено F6f трека F (`HPP-378`' not in t
p = (S / 'p327.md').read_bytes().decode('utf-8').replace('{N}', str(N + 1)).replace('{TIME}', TIME)
t = t.rstrip('\n') + '\n' + p.rstrip('\n') + '\n'
rm.write_bytes(t.encode('utf-8'))
rg = R / 'docs/track-f/register.md'
g = rg.read_bytes().decode('utf-8')
assert '## 23.' not in g and '## 22.' in g
g = g.rstrip('\n') + '\n' + (S / 'reg327.md').read_bytes().decode('utf-8').replace('{N}', str(N + 1)).rstrip('\n') + '\n'
rg.write_bytes(g.encode('utf-8'))
M = R / 'docs/track-f/f6f'
M.mkdir(exist_ok=True)
for src in ['C:/kyty/f287/lead/f6f_chk.py', 'C:/kyty/f287/lead/f6f_chk.out.txt', str(S / 'p327.md'), str(S / 'reg327.md'), str(S / 'ins327.py')]:
    shutil.copyfile(src, M / pathlib.Path(src).name)
print('point', N + 1, 'time', TIME)
