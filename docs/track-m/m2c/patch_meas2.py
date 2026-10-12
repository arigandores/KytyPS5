"""M2c (HPP-840): MEASUREMENT-ONLY patch, step 2 (after patch_meas.py; never committed). With M2C_CASES_ONLY set in the
environment the wrapped top-level host checks of main() are skipped - only CheckOpcodeCoverage and the case loops
(MakeCases / MakeGraphicsCases through RunCase / RunGraphicsCase) run. Unset: as patch_meas.py.
Usage: python patch_meas2.py <worktree>."""
import sys

path = sys.argv[1] + '/tests/ShaderRecompilerComputeTests.cpp'
text = open(path, 'rb').read().decode('utf-8')
assert '\r' not in text and 'm2c_cases_only' not in text
lines = text.split('\n')
anchor = [k for k, l in enumerate(lines) if l == '  VulkanHarness vulkan;' and lines[k + 1] == '  M2C_TRY("CheckRenderTargetFormatContract()", CheckRenderTargetFormatContract());']
assert len(anchor) == 1, anchor
n = 0
for k in range(anchor[0] + 1, len(lines)):
    l = lines[k]
    if l == '  std::printf("ShaderRecompilerComputeTests: all cases passed\\n");':
        break
    if l.startswith('  M2C_TRY("') and 'CheckOpcodeCoverage' not in l:
        lines[k] = '  if (!m2c_cases_only) ' + l[2:]
        n += 1
lines.insert(anchor[0] + 1, '  const bool m2c_cases_only = std::getenv("M2C_CASES_ONLY") != nullptr;')
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('gated', n, 'ALL OK')
