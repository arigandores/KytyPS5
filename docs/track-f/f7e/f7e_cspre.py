# F7e (HPP-444, lead): CsPretranslate skipped profile in log_f7a_1.txt and use of those hashes outside the speculative thread
import re, collections, hashlib, sys
p = 'C:/kyty/f287/f7a/log_f7a_1.txt'
lines = open(p, 'rb').read().split(b'\n')
sk = set(); fam = collections.Counter()
for l in lines:
    if b'CsPretranslate: skipped' in l:
        sk.add(re.search(rb'hash=([0-9a-f]+)', l).group(1))
        m = re.search(rb'family=(\w+) opcode=(0x[0-9a-f]+)', l)
        fam[(m.group(1) + b' ' + m.group(2)).decode() if m else ('budget' if b'budget' in l else 'resource' if b'resource' in l else 'other')] += 1
outside = 0; outside_dispatcher = 0
for l in lines:
    if b'CsPretranslate: skipped' in l or b'CsPretranslate phase' in l:
        continue
    if any(h in sk for h in re.findall(rb'[0-9a-f]{16}', l)):
        if b'CsPretranslate CFG dispatcher fallback' in l:
            outside_dispatcher += 1
        else:
            outside += 1
cfg_out = sum(1 for l in lines if b'shader CFG build failed' in l and b'CsPretranslate' not in l)
print('log sha256', hashlib.sha256(open(p, 'rb').read()).hexdigest())
print('skipped hashes', len(sk))
print('profile', dict(sorted(fam.items())))
print('lines with these hashes outside the speculative thread', outside, '(+ dispatcher fallback of the same thread', outside_dispatcher, ')')
print('shader CFG build failed outside CsPretranslate', cfg_out)
ok = outside == 0 and cfg_out == 0
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
