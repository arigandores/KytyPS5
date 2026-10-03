"""F10a (HPP-445): extract the definition of ValidateShaderSpirv byte for byte from the git blob.

Writes sval_body.inc (the exact bytes of the definition, from the line 'bool ValidateShaderSpirv('
through the first following line that is exactly '}'), checks the region is the same at 8f6b6be2 (the
commit cited by ROADMAP item 366) and at HEAD, re-reads the written file and compares it with the blob
region. ASCII output only.
"""
import hashlib
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
PATH = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
OUT = 'C:/kyty/f287/f10a/sval_body.inc'


def region(rev):
    blob = subprocess.run(['git', '-C', REPO, 'show', rev + ':' + PATH], capture_output=True, check=True).stdout
    lines = blob.split(b'\n')
    starts = [i for i, l in enumerate(lines) if l.startswith(b'bool ValidateShaderSpirv(')]
    assert len(starts) == 1, starts
    a = starts[0]
    b = a
    while lines[b] != b'}':
        b += 1
    # anonymous namespace bounds: the definition must be inside 'namespace {' .. '} // namespace'
    opens = [i for i, l in enumerate(lines[:a]) if l == b'namespace {']
    closes = [i for i, l in enumerate(lines[:a]) if l == b'} // namespace']
    return a + 1, b + 1, b'\n'.join(lines[a:b + 1]) + b'\n', (opens[-1] + 1 if opens else None,
                                                             closes[-1] + 1 if closes else None)


ok = True
head = subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD'], capture_output=True, check=True).stdout.decode().strip()
r_old = region('8f6b6be2')
r_head = region('HEAD')
for name, r in (('8f6b6be2', r_old), ('HEAD ' + head[:8], r_head)):
    print('%s: lines %d-%d, %d bytes, sha256 %s, last "namespace {" before it at line %s, last "} // namespace" before it at line %s'
          % (name, r[0], r[1], len(r[2]), hashlib.sha256(r[2]).hexdigest(), r[3][0], r[3][1]))
ok &= r_old[2] == r_head[2]
print('region 8f6b6be2 == HEAD:', r_old[2] == r_head[2])
# inside an anonymous namespace: the last 'namespace {' precedes it and no '} // namespace' after that
ok &= r_head[3][0] is not None and (r_head[3][1] is None or r_head[3][1] < r_head[3][0])
open(OUT, 'wb').write(r_head[2])
back = open(OUT, 'rb').read()
print('sval_body.inc sha256', hashlib.sha256(back).hexdigest(), 'equal to blob region:', back == r_head[2])
ok &= back == r_head[2]
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
