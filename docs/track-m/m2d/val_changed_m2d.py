# M2d (HPP-841): copy of m657/m2a/val_changed.py with CONFIGS = z, d, e of corpus_m2d.py. Was:
"""M2a (HPP-838): spirv-val (options of ValidateShaderSpirv at KYTY_FIX_SVAL=1: --target-env vulkan1.3
--uniform-buffer-standard-layout) of every module of a theme config that differs from base, and of its base module
(control). Usage: python val_changed.py <corpus dir> [<supplement run dir>]. Prints per config: changed, valid, invalid
(and invalid among the base controls). Lock and STOP checked."""
import collections
import hashlib
import os
import subprocess
import sys

VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
OPTS = ['--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout']
CONFIGS = ['z', 'd', 'e']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def valid(p):
    return subprocess.run([VAL] + OPTS + [p], capture_output=True).returncode == 0


def main():
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
        print('LOCK or STOP')
        return 3
    ok = True
    for root in sys.argv[1:]:
        rows = sorted(os.listdir(root + '/base'))
        stats = collections.defaultdict(lambda: [0, 0, 0, 0])
        base_valid = {}
        for rid in rows:
            b = '%s/base/%s/out.spv' % (root, rid)
            if not os.path.exists(b):
                continue
            for c in CONFIGS:
                p = '%s/%s/%s/out.spv' % (root, c, rid)
                if not os.path.exists(p) or sha(p) == sha(b):
                    continue
                if rid not in base_valid:
                    base_valid[rid] = valid(b)
                v = valid(p)
                s = stats[c]
                s[0] += 1
                s[1] += int(v)
                s[2] += int(not base_valid[rid])
                s[3] += int(not v and base_valid[rid])
        for c in CONFIGS:
            s = stats[c]
            print('%s %s changed %d valid %d base-invalid %d new-invalid %d' % (root, c, s[0], s[1], s[2], s[3]))
            ok &= s[3] == 0
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
