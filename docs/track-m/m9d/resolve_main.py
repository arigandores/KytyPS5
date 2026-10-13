"""M9d: resolve the cherry-pick conflicts of d490f648 on main - every conflict block keeps HEAD's lines, then the commit's
lines (the base section must be empty: both sides only inserted). Usage: python resolve_main.py <file>. Prints the
number of blocks and ALL OK."""
import os
import re
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
p = sys.argv[1]
t = open(p, 'rb').read().decode('utf-8')
pat = re.compile(r'<<<<<<< HEAD\n(.*?)\|\|\|\|\|\|\| [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n', re.S)
blocks = pat.findall(t)
assert blocks, 'no blocks'
for ours, base, theirs in blocks:
    assert base == '', 'non-empty base section'
t2 = pat.sub(lambda m: m.group(1) + m.group(3), t)
assert '<<<<<<<' not in t2 and '>>>>>>>' not in t2 and '|||||||' not in t2
open(p, 'wb').write(t2.encode('utf-8'))
print('blocks', len(blocks))
print('ALL OK')
