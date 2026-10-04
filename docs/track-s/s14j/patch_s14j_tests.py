"""S14j (HPP-533, ROADMAP s122 item 430(g)(1)): add the KYTY_TEST_SPECDUMP_* mode and the TestSpecDumpRoundTrip fixture to
tests/shaderCfgTests.cpp. Usage: python patch_s14j_tests.py <repo root> <dir with block_specdump.cpp, block_hook.cpp>.
Anchors are whole lines; each must occur exactly once. CRLF is kept if the file has it; the result is written with
write_bytes."""
import sys
from pathlib import Path

root = Path(sys.argv[1])
blocks = Path(sys.argv[2])
path = root / 'tests' / 'shaderCfgTests.cpp'
raw = path.read_bytes()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
lines = text.split('\n')
block_dump = blocks.joinpath('block_specdump.cpp').read_bytes().decode('utf-8').replace('\r\n', '\n')
block_hook = blocks.joinpath('block_hook.cpp').read_bytes().decode('utf-8').replace('\r\n', '\n')
if 'SpecDumpMain' in text:
    sys.exit('already patched')


def index_of(line):
    hits = [i for i, l in enumerate(lines) if l == line]
    if len(hits) != 1:
        sys.exit('anchor %r: %d hits' % (line, len(hits)))
    return hits[0]


# 1. includes: after the whole line '#include <deque>'.
i = index_of('#include <deque>')
lines[i + 1:i + 1] = ['#include <filesystem>', '#include <fstream>', '#include <map>', '#include <set>']
i = index_of('#include <algorithm>')
lines[i:i] = ['#include <fmt/format.h>', '']
# 2. the dump block before the RUN macro comment.
i = index_of('// KYTY_TESTS_VERBOSE=1 prints the name of every test before it runs;')
lines[i:i] = block_dump.rstrip('\n').split('\n') + ['']
# 3. the mode hook: before the KYTY_RECOMPILE mode in main.
i = index_of('  if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {')
if lines[i - 1] != '  EnsureConfigInitialized();':
    sys.exit('hook anchor: previous line is %r' % lines[i - 1])
lines[i:i] = block_hook.rstrip('\n').split('\n')
# 4. the fixture: last RUN of the suite.
i = index_of('  RUN(TestNewShaderRecompilerUnsupportedMemoryDecode);')
if lines[i + 1] != '' or lines[i + 2] != '  return 0;':
    sys.exit('RUN anchor: next lines %r' % lines[i + 1:i + 3])
lines[i + 1:i + 1] = ['  RUN(TestSpecDumpRoundTrip);']

out = '\n'.join(lines)
if crlf:
    out = out.replace('\n', '\r\n')
path.write_bytes(out.encode('utf-8'))
print('patched %s (crlf=%s)' % (path, crlf))
