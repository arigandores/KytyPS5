"""S18a (HPP-642): executor variant of the resolution of the cherry-pick 283a6ef9 onto FS8a 302347b4.
Each file has one conflict (diff3 form: ours 302347b4 / base 283a6ef9^ / theirs 283a6ef9). The base side is the context
of main commits absent from FS8a (F16d 381aa80a DiagF5 block; S16d 1d8d9aa6 S16dProbe include). Resolution: ours (empty)
+ the lines 283a6ef9 ADDS to the base side, i.e. theirs with the base block removed. Checked: the base side is a prefix
(pipelineCache.cpp) or a suffix (shaderCfgTests.cpp) of theirs, ours side is empty - otherwise exit 1.
Usage: python resolve1.py <in file> <out file> <prefix|suffix|auto> (auto: prefix if the base is a prefix of theirs, else suffix)
"""
import sys

src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, 'rb').read().decode('utf-8').split('\n')
out = []
i = 0
n_conf = 0
while i < len(lines):
    if lines[i].startswith('<<<<<<< '):
        j = i + 1
        ours = []
        while not lines[j].startswith('||||||| '):
            ours.append(lines[j]); j += 1
        j += 1
        base = []
        while lines[j] != '=======':
            base.append(lines[j]); j += 1
        j += 1
        theirs = []
        while not lines[j].startswith('>>>>>>> '):
            theirs.append(lines[j]); j += 1
        if ours:
            print('ours side not empty'); sys.exit(1)
        m = mode
        if m == 'auto':
            m = 'prefix' if theirs[:len(base)] == base else 'suffix'
        if m == 'prefix':
            if theirs[:len(base)] != base:
                print('base is not a prefix of theirs'); sys.exit(1)
            added = theirs[len(base):]
        else:
            if theirs[len(theirs) - len(base):] != base:
                print('base is not a suffix of theirs'); sys.exit(1)
            added = theirs[:len(theirs) - len(base)]
        print('mode', m)
        print('conflict at line %d: ours %d, base %d, theirs %d, kept (added by 283a6ef9) %d' % (i + 1, len(ours), len(base), len(theirs), len(added)))
        for a in added:
            print('  + ' + a)
        out.extend(added)
        n_conf += 1
        i = j + 1
        continue
    out.append(lines[i])
    i += 1
if n_conf < 1:
    print('conflicts', n_conf); sys.exit(1)
open(dst, 'wb').write('\n'.join(out).encode('utf-8'))
print('resolved', dst)
