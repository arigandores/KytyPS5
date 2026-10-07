"""Track F link F24c (HPP-662): the one conflict of the cherry-pick of 21f8ca76 onto 0005e11f + 1570d110 - the include
block of regionManager.h (S18 has no "common/diagB32.h" include, F20j3 2cde5ef2 is not in S18). Resolution: the S18 side
(no diagB32 include) plus the include the fix adds ("common/envFlag.h"). Exactly one conflict block is allowed.

    python resolve_wtB_f24c.py <worktree>
"""
import sys

path = sys.argv[1].rstrip('/\\') + '/src/graphics/host_gpu/regionManager.h'
L = open(path, 'rb').read().decode('utf-8').split('\n')
starts = [i for i, l in enumerate(L) if l.startswith('<<<<<<< ')]
if len(starts) != 1:
    sys.exit('conflict blocks: %d' % len(starts))
s = starts[0]
e = next(i for i in range(s, len(L)) if L[i].startswith('>>>>>>> '))
block = L[s:e + 1]
mid = next(i for i, l in enumerate(block) if l == '=======')
base = next(i for i, l in enumerate(block) if l.startswith('||||||| '))
ours, theirs = block[1:base], block[mid + 1:-1]
want_theirs = ['#include "common/diagB32.h" // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))', '#include "common/envFlag.h"']
if ours != [] or theirs != want_theirs:
    sys.exit('unexpected conflict: ours %r theirs %r' % (ours, theirs))
L[s:e + 1] = ['#include "common/envFlag.h"']
open(path, 'wb').write('\n'.join(L).encode('utf-8'))
print('resolved', path)
