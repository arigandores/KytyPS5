"""M9d2 (HPP-874): forward declaration of VkRect2D in diagT188.h next to VkViewport (the header does not include Vulkan).
Whole-line anchor, found exactly once; LF out. Usage: python patch_m9d2b.py <worktree root>. Lock: exit 3."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
p = os.path.join(sys.argv[1], 'src/libs/diagT188.h')
raw = open(p, 'rb').read().decode('utf-8')
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
old = 'struct VkViewport;\n'
if s.count(old) != 1:
    print('ANCHOR count=%d' % s.count(old))
    print('FAIL')
    sys.exit(1)
s = s.replace(old, 'struct VkViewport;\nstruct VkRect2D;\n')
if crlf:
    s = s.replace('\n', '\r\n')
open(p, 'wb').write(s.encode('utf-8'))
print('ALL OK')
