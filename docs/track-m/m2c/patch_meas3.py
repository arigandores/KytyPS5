"""M2c (HPP-840): MEASUREMENT-ONLY patch, step 3 (after patch_meas2.py; never committed). The case loops count cases
from 0 over MakeCases then MakeGraphicsCases; with M2C_FROM=<n> the cases before n are skipped; before each run case the
line "[m2c] IDX <n> <name>" is printed. The driver restarts the process after a device loss or a fatal exit from the
next index, so one lost device does not fail every later case. Usage: python patch_meas3.py <worktree>."""
import sys

path = sys.argv[1] + '/tests/ShaderRecompilerComputeTests.cpp'
text = open(path, 'rb').read().decode('utf-8')
assert '\r' not in text and 'm2c_from' not in text
lines = text.split('\n')
decl = '  const bool m2c_cases_only = std::getenv("M2C_CASES_ONLY") != nullptr;'
k = [i for i, l in enumerate(lines) if l == decl]
assert len(k) == 1
lines.insert(k[0] + 1, '  int m2c_index = 0;')
lines.insert(k[0] + 2, '  const int m2c_from = std::getenv("M2C_FROM") != nullptr ? std::atoi(std::getenv("M2C_FROM")) : 0;')
n = 0
for i, l in enumerate(lines):
    for call in ('RunCase(&vulkan, test)', 'RunGraphicsCase(&vulkan, test)'):
        if l == '    M2C_TRY(test.name, %s);' % call:
            lines[i] = ('    if (m2c_index++ >= m2c_from) { std::fprintf(stderr, "[m2c] IDX %%d %%s\\n", m2c_index - 1, test.name); '
                        'M2C_TRY(test.name, %s); }' % call)
            n += 1
assert n == 2, n
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('loops', n, 'ALL OK')
