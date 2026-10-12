"""M2c (HPP-840): MEASUREMENT-ONLY patch of tests/ShaderRecompilerComputeTests.cpp in an M2c worktree (never committed).
Fail() throws instead of abort(); every top-level Check*/vulkan.Check* statement of the Windows default path of main()
and every RunCase/RunGraphicsCase of the case loops is wrapped so that one failure does not stop the run; each prints
"[m2c] PASS <label>" / "[m2c] FAIL <label>". Applied identically to the FS15 tree (wt15) and the main tree (wt) so the
two lists compare like with like. Anchors are whole lines, each counted. Usage: python patch_meas.py <worktree>."""
import re
import sys

path = sys.argv[1] + '/tests/ShaderRecompilerComputeTests.cpp'
raw = open(path, 'rb').read()
assert b'\r' not in raw
text = raw.decode('utf-8')
lines = text.split('\n')

fail_head = '[[noreturn]] void Fail(const char *shader_name, const char *stage,'
idx = [i for i, l in enumerate(lines) if l == fail_head]
assert len(idx) == 1, idx
i = idx[0]
assert lines[i + 1] == '                       const std::string &message) {'
assert lines[i + 2] == '  std::fprintf(stderr, "ShaderRecompilerComputeTests: %s failed at %s: %s\\n",'
assert lines[i + 3] == '               shader_name, stage, message.c_str());'
assert lines[i + 4] == '  std::abort();'
assert lines[i + 5] == '}'
lines[i + 4] = '  throw M2cFailure{};'
macro = ('#define M2C_TRY(label, stmt) do { try { stmt; std::fprintf(stderr, "[m2c] PASS %s\\n", label); } '
         'catch (const M2cFailure &) { std::fprintf(stderr, "[m2c] FAIL %s\\n", label); } '
         'catch (const std::exception &e) { std::fprintf(stderr, "[m2c] EXC %s %s\\n", label, e.what()); } } while (0)')
lines[i:i] = ['struct M2cFailure {};', macro]

start = [k for k, l in enumerate(lines) if l == '  VulkanHarness vulkan;']
end = [k for k, l in enumerate(lines) if l == '  std::printf("ShaderRecompilerComputeTests: all cases passed\\n");']
assert len(end) == 1, end
end = end[0]
win = [k for k in start if k < end and lines[k + 1] == '  CheckRenderTargetFormatContract();']
assert len(win) == 1, win
pat = re.compile(r'^  ((?:vulkan\.)?Check\w+\(.*\));$')
wrapped = 0
for k in range(win[0] + 1, end):
    l = lines[k]
    m = pat.match(l)
    if m:
        stmt = m.group(1)
        label = stmt.replace('"', "'")
        lines[k] = '  M2C_TRY("%s", %s);' % (label, stmt)
        wrapped += 1
    elif l == '    RunCase(&vulkan, test);':
        lines[k] = '    M2C_TRY(test.name, RunCase(&vulkan, test));'
        wrapped += 1
    elif l == '    RunGraphicsCase(&vulkan, test);':
        lines[k] = '    M2C_TRY(test.name, RunGraphicsCase(&vulkan, test));'
        wrapped += 1
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('wrapped', wrapped, 'ALL OK')
