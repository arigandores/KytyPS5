"""M2c (HPP-840): MEASUREMENT-ONLY patch, step 4 (after patch_meas3.py; never committed). M2C_SKIP=<i>,<j>,... - the cases
with these indices are not run (no "[m2c] IDX" line). Reason: case 224 FlatVirtualAddressRebasesGuestAllocation loses
the Vulkan device (ErrorDeviceLost) -> Windows GPU driver reset (TDR), the user's screen freezes (user complaint in
HPP-840, 2026-10-12). run_cases.py refuses an exe without the string M2C_SKIP. Usage: python patch_meas4.py <worktree>."""
import sys

path = sys.argv[1] + '/tests/ShaderRecompilerComputeTests.cpp'
text = open(path, 'rb').read().decode('utf-8')
assert '\r' not in text and 'm2c_from' in text and 'm2c_skip' not in text
lines = text.split('\n')
decl = '  const int m2c_from = std::getenv("M2C_FROM") != nullptr ? std::atoi(std::getenv("M2C_FROM")) : 0;'
k = [i for i, l in enumerate(lines) if l == decl]
assert len(k) == 1
lines.insert(k[0] + 1, '  const std::string m2c_skip = std::getenv("M2C_SKIP") != nullptr ? "," + std::string(std::getenv("M2C_SKIP")) + "," : std::string();')
n = 0
for i, l in enumerate(lines):
    if l.startswith('    if (m2c_index++ >= m2c_from) {'):
        lines[i] = l.replace('if (m2c_index++ >= m2c_from) {',
                             'if (m2c_index++ >= m2c_from && m2c_skip.find("," + std::to_string(m2c_index - 1) + ",") == std::string::npos) {', 1)
        n += 1
assert n == 2, n
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('loops', n, 'ALL OK')
