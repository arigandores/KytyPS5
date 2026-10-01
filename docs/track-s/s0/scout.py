# scout.py - vocabulary of "Word:" prefixes in one log, streaming, binary (S0, HPP-294)
import re, sys, collections
path = sys.argv[1]
rx = re.compile(rb'(?:^|[\s\]])([A-Z][A-Za-z0-9]+(?:-[a-z0-9]+)?): ')
cnt = collections.Counter(); samp = {}
n = 0
with open(path, 'rb') as f:
    for line in f:
        n += 1
        m = rx.search(line[:160])
        if m:
            k = m.group(1)
            cnt[k] += 1
            if cnt[k] <= 2:
                samp.setdefault(k, []).append((n, line[:300].rstrip()))
print('lines', n)
for k, c in cnt.most_common(150):
    print(c, k.decode())
    for ln, s in samp[k]:
        print('    ', ln, s.decode('latin1'))
