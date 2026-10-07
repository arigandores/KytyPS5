# F24d (HPP-663, Red Team): own check that the KYTY_FIX_B13=0 branch of 21f8ca76 is the parent text verbatim: code
# lines with one extra leading tab, preprocessor lines (column 0) unchanged. Inputs: rm_parent.h = git show
# 21f8ca76^:src/graphics/host_gpu/regionManager.h, rm_fix.h = git show 21f8ca76:src/graphics/host_gpu/regionManager.h.
# Usage: python else_check_f24d.py <dir with rm_parent.h and rm_fix.h>
import sys

D = sys.argv[1].rstrip('/') + '/'
P = open(D + 'rm_parent.h', 'rb').read().decode().split('\n')
F = open(D + 'rm_fix.h', 'rb').read().decode().split('\n')
T = chr(9)
s = P.index(T * 3 + '// Called with the region lock held, after the bits and before the pages become')
e = next(i for i in range(s, len(P)) if 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);' in P[i])
par = P[s:e + 1]
fi = next(i for i, x in enumerate(F) if x.strip() == 'if (FixB13Enabled()) {')
fe = next(i for i in range(fi, len(F)) if F[i] == T * 3 + '} else {')
fs = fe + 3
fend = next(i for i in range(fs, len(F)) if 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);' in F[i])
new = F[fs:fend + 1]
print('if at', fi + 1, 'else at', fe + 1, '; F24c comment lines:', fe + 2, fe + 3)
print('parent block lines', len(par), '(%d-%d)' % (s + 1, e + 1), 'else block lines', len(new), '(%d-%d)' % (fs + 1, fend + 1))


def norm(x):
    if x.startswith('#'):
        return x
    return x[1:] if x.startswith(T) else 'NO_TAB:' + x


bad = [(i, a, b) for i, (a, b) in enumerate(zip(par, map(norm, new))) if a != b]
print('mismatches', len(bad) + abs(len(par) - len(new)), bad[:3])
print('closing:', repr(F[fend + 1]), '(closes else) next', repr(F[fend + 2]))
print('ELSE VERBATIM OK' if not bad and len(par) == len(new) else 'ELSE DIFFERS')
