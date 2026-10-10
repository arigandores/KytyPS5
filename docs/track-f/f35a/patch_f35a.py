# F35a (HPP-755, ROADMAP s122 item 685(v)(1)): adds TestF22IndirectNullComparison to tests/shaderCfgTests.cpp.
# Usage: python patch_f35a.py <repo root> <block file>. Anchors are whole lines; CRLF is kept if the file has it.
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
root, block_path = sys.argv[1], sys.argv[2]
path = os.path.join(root, 'tests', 'shaderCfgTests.cpp')
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
block = open(block_path, 'rb').read().decode('utf-8').replace('\r\n', '\n')
lines = text.split('\n')

anchor_fn = 'void TestNewShaderRecompilerImageViewDimensions() {'
anchor_run = '  RUN(TestF19NullComparisonImage);'
assert 'TestF22IndirectNullComparison' not in text, 'already patched'
assert lines.count(anchor_fn) == 1, anchor_fn
assert lines.count(anchor_run) == 1, anchor_run
i = lines.index(anchor_fn)
lines[i:i] = block.rstrip('\n').split('\n') + ['']
j = lines.index(anchor_run)
lines.insert(j + 1, '  RUN(TestF22IndirectNullComparison);')
out = '\n'.join(lines)
if crlf:
    out = out.replace('\n', '\r\n')
open(path, 'wb').write(out.encode('utf-8'))
print('patched', path, 'crlf' if crlf else 'lf')
