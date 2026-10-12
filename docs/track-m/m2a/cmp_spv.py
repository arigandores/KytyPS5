"""M2a (HPP-838): compare the SPIR-V dumps (KYTY_TESTS_SPV_DIR) of two shader_cfg_tests runs byte for byte.
Usage: python cmp_spv.py <dir a> <dir b> [label]. Prints the number of files, differing names and EQUAL / DIFFER."""
import hashlib
import os
import sys


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


a, b = sys.argv[1], sys.argv[2]
label = sys.argv[3] if len(sys.argv) > 3 else ''
A = sorted(x for x in os.listdir(a) if x.endswith('.spv'))
B = sorted(x for x in os.listdir(b) if x.endswith('.spv'))
diff = [x for x in sorted(set(A) | set(B)) if x not in A or x not in B or sha(a + '/' + x) != sha(b + '/' + x)]
print('%s spv %d / %d differing %d %s' % (label, len(A), len(B), len(diff), 'EQUAL' if not diff and A else 'DIFFER'))
for x in diff[:40]:
    print('   differs:', x)
