import re, sys, collections
# F2c (HPP-310): sample line forms around B26 in one s142 log (read-only, ASCII output)
f = sys.argv[1]
H5 = [b'57c4d5848e02ecdc']
for l in open('C:/kyty/f287/f1a/b26_shaders.tsv', 'rb').read().splitlines()[1:]:
    p = l.split(b'\t')
    if p[2] in (b'0xe3',):
        H5.append(p[0])
print('h5', [h.decode() for h in H5])
pats = [rb'opcode is not implemented', rb'Shader translation cache:', rb'CsPretranslate: (ready|skipped|miss|hit)', rb'shader CFG build failed',
        rb'Level has started', rb'unsupported decoded instruction']
seen = collections.Counter()
n = 0
with open(f, 'rb') as fh:
    for i, line in enumerate(fh):
        for p in pats:
            if re.search(p, line):
                k = p[:30]
                seen[k] += 1
                hit5 = any(h in line for h in H5)
                if seen[k] <= 3 or (hit5 and seen[k] <= 400 and n < 40):
                    if hit5:
                        n += 1
                    print(i + 1, ('H5 ' if hit5 else '   ') + line[:300].decode('latin1').rstrip().encode('ascii', 'replace').decode())
print(dict((k.decode(), v) for k, v in seen.items()))
