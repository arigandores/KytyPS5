"""F14c (HPP-489) negative control of the B11 test fix: the two new manual-path probes get the format k32Float (native Dref path),
so every check of the manual probes must fail (6 failures: C - dref, sample form, compare; C_LZ - dref, sample form, compare; the
Lod-0 check of C_LZ counts OpImageSampleExplicitLod and must also fail -> 7). Applied on top of patch_test_b11.py in the worktree only;
reverted by re-applying the fixed file (git checkout + patch_test_b11.py). Anchors are whole lines; CR stripped and restored.
Usage: python patch_ctl_b11.py <repo root>.
"""
import sys

root = sys.argv[1]
path = root + '/tests/shaderCfgTests.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
NL = chr(10)


def rep(old, new):
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, old[:80]))
    text = text.replace(old, new)


rep('    const auto result = compile(0x28, 0x1); // image_sample_c, k8UNorm' + NL,
    '    const auto result = compile(0x28, 0x1, Prospero::BufferFormat::k32Float); // CTL' + NL)
rep('    const auto result = compile(0x2f, 0x1); // image_sample_c_lz, k8UNorm' + NL,
    '    const auto result = compile(0x2f, 0x1, Prospero::BufferFormat::k32Float); // CTL' + NL)
out = text.replace('\n', '\r\n') if crlf else text
open(path, 'wb').write(out.encode('utf-8'))
print('control patched', path)
