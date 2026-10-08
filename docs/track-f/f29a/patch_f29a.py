"""F29a (HPP-699): add the CMake target b12_bdastamp_stand (EXCLUDE_FROM_ALL) after the b27_daslot_stand block and copy the
stand source into tests/. Whole-line anchors; keeps the file's line endings; writes bytes.

    python patch_f29a.py <repo> <stand source>
"""
import shutil
import sys

repo, stand = sys.argv[1], sys.argv[2]
path = repo + '/CMakeLists.txt'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
anchor = 'target_include_directories(b27_daslot_stand PRIVATE ${inc_headers})'
idx = [i for i, l in enumerate(lines) if l == anchor]
if len(idx) != 1:
    sys.exit('anchor count %d' % len(idx))
if any('b12_bdastamp_stand' in l for l in lines):
    sys.exit('already patched')
block = [
    '',
    '# Track F, F29a (HPP-699, ROADMAP s122 item 638(g)(2)): the B12 "bdastamp" stand (tests/B12BdaStampStand.cpp) - the real',
    '# MemoryTracker and RangeSet, a model of the BDA scan of RenderContext::PrepareBda. Run by',
    '# docs/track-f/f29a/run_stand_f29a.py, not by ctest.',
    'add_executable(b12_bdastamp_stand EXCLUDE_FROM_ALL',
    '\t"${KYTY_TESTS_DIR}/B12BdaStampStand.cpp"',
    '\t"${KYTY_SOURCE_DIR}/graphics/host_gpu/pageManager.cpp"',
    '\t"${KYTY_SOURCE_DIR}/graphics/host_gpu/memoryTracker.cpp"',
    ')',
    'target_link_libraries(b12_bdastamp_stand fmt::fmt common)',
    'target_include_directories(b12_bdastamp_stand PRIVATE ${inc_headers})',
]
lines[idx[0] + 1:idx[0] + 1] = block
text = '\n'.join(lines)
if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
shutil.copyfile(stand, repo + '/tests/B12BdaStampStand.cpp')
print('patched', path, 'crlf' if crlf else 'lf', 'at line', idx[0] + 2)
