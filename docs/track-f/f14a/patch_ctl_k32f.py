"""F14a (HPP-487): control patch of the WORKTREE test file only (C:/kyty/f287/f14a/wt/tests/shaderCfgTests.cpp).

In TestNewShaderRecompilerPixelImageSampleLodSelection, right after the first whole line
'    auto user_data = ImageTestUserData();' that follows the function header, insert one line that - only when the
environment variable F14A_K32F is set - rewrites the format of descriptor srsrc 0 to k32Float (SetImageTestFormat,
the helper already in the file). Without F14A_K32F the test is byte-for-byte the original behaviour.
--apply writes the file (LF, as in git); --revert is done by git checkout of the file. Not committed anywhere.
"""
import sys

PATH = 'C:/kyty/f287/f14a/wt/tests/shaderCfgTests.cpp'
HEADER = 'void TestNewShaderRecompilerPixelImageSampleLodSelection() {'
ANCHOR = '    auto user_data = ImageTestUserData();'
INSERT = ('    if (std::getenv("F14A_K32F") != nullptr) {'
          ' SetImageTestFormat(&user_data, 0, Prospero::BufferFormat::k32Float); }')

data = open(PATH, 'rb').read()
assert b'\r' not in data, 'CR in worktree file'
lines = data.decode('utf-8').split('\n')
h = [i for i, l in enumerate(lines) if l == HEADER]
assert len(h) == 1, h
a = None
for i in range(h[0] + 1, len(lines)):
    if lines[i] == ANCHOR:
        a = i
        break
    if lines[i].startswith('void '):
        break
assert a is not None, 'anchor not found inside the function'
assert INSERT not in lines, 'already applied'
print('header line', h[0] + 1, 'anchor line', a + 1)
if '--apply' in sys.argv:
    lines.insert(a + 1, INSERT)
    open(PATH, 'wb').write('\n'.join(lines).encode('utf-8'))
    print('applied: inserted line', a + 2)
