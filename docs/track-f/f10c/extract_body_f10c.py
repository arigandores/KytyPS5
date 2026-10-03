"""Track F, link F10c (HPP-451), ROADMAP s122 item 369(v)(1): extract the code under test byte for byte from the git blob.

Copy of the F10a extract_body.py idea on the F10c commit. The region is contiguous in pipelineCache.cpp: from the line
'bool FixSvalEnabled() {' through the closing '}' of 'bool ValidateShaderSpirv(' - it holds FixSvalEnabled (the
KYTY_FIX_SVAL read), g_fix_sval_ubo_std_layout and ValidateShaderSpirv. Checks: one start, inside the anonymous namespace,
the region holds exactly these three definitions, the written sval_body_f10c.inc equals the blob region; and the part of
ValidateShaderSpirv outside the F10c hunk equals the F10a body (sval_body.inc of F10a, the 9e60a8a5-era definition).
Usage: python extract_body_f10c.py <commit>.  ASCII output only, ends with ALL OK.
"""
import difflib
import hashlib
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
PATH = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
OUT = 'C:/kyty/f287/f10c/sval_body_f10c.inc'
F10A_BODY = 'C:/kyty/f287/f10a/sval_body.inc'
REV = sys.argv[1]

ok = True
blob = subprocess.run(['git', '-C', REPO, 'show', REV + ':' + PATH], capture_output=True, check=True).stdout
assert b'\r' not in blob
lines = blob.split(b'\n')
starts = [i for i, l in enumerate(lines) if l == b'bool FixSvalEnabled() {']
vstarts = [i for i, l in enumerate(lines) if l.startswith(b'bool ValidateShaderSpirv(')]
print('starts FixSvalEnabled', [s + 1 for s in starts], 'ValidateShaderSpirv', [s + 1 for s in vstarts])
ok &= len(starts) == 1 and len(vstarts) == 1
a = starts[0]
v = vstarts[0]
b = v
while lines[b] != b'}':
    b += 1
region = b'\n'.join(lines[a:b + 1]) + b'\n'
opens = [i for i, l in enumerate(lines[:a]) if l == b'namespace {']
closes = [i for i, l in enumerate(lines[:a]) if l == b'} // namespace']
in_anon = bool(opens) and (not closes or closes[-1] < opens[-1])
print('%s: region lines %d-%d (%d bytes, sha256 %s); ValidateShaderSpirv lines %d-%d; inside anonymous namespace: %s'
      % (REV, a + 1, b + 1, len(region), hashlib.sha256(region).hexdigest(), v + 1, b + 1, in_anon))
ok &= in_anon
top = [l for l in lines[a:b + 1] if l and not l.startswith((b'\t', b' ', b'}', b'//'))]
print('top-level lines in the region:')
for l in top:
    print('  ' + l.decode())
ok &= top == [b'bool FixSvalEnabled() {', b'std::atomic<bool> g_fix_sval_ubo_std_layout {false};',
              b'bool ValidateShaderSpirv(const char* label, uint64_t shader_hash,']
open(OUT, 'wb').write(region)
back = open(OUT, 'rb').read()
print('sval_body_f10c.inc sha256', hashlib.sha256(back).hexdigest(), 'equal to blob region:', back == region)
ok &= back == region
# ValidateShaderSpirv of this commit against the F10a body: the only change is the F10c hunk.
old = open(F10A_BODY, 'rb').read().decode().split('\n')
new = b'\n'.join(lines[v:b + 1]).decode().split('\n') + ['']
diff = [d for d in difflib.unified_diff(old, new, 'f10a/sval_body.inc', REV + ' ValidateShaderSpirv', n=0, lineterm='')]
print('diff of ValidateShaderSpirv vs the F10a body (%d lines):' % len(diff))
for d in diff:
    print('  ' + d)
removed = [d for d in diff if d.startswith('-') and not d.startswith('---')]
ok &= removed == ['-\tif (tools.Validate(spirv)) {']
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
