# F18a (HPP-535): prepares a copy of a sweep jsonl for git (general rule 28): every match of a pattern of the privacy
# list (one regular expression per line) is replaced by <masked> - the context lines of the old logs carry the user
# path of the former emulator folder.  Idempotent.  Usage: python mask_f18a.py <in.jsonl> <out.jsonl> <privacy list>
import re, sys

src, dst = sys.argv[1], sys.argv[2]
PRIV = [re.compile(l.strip()) for l in open(sys.argv[3], encoding='utf-8') if l.strip()]
out = []
masked = 0
for l in open(src, encoding='utf-8'):
    if not l.startswith('{'):
        continue
    s = l.rstrip(chr(10))
    for p in PRIV:
        s, n = p.subn('<masked>', s)
        masked += n
    out.append(s)
open(dst, 'wb').write((chr(10).join(out) + chr(10)).encode('ascii'))
left = sum(1 for s in out for p in PRIV if p.search(s))
print('lines', len(out), '; privacy matches replaced', masked, '; lines with <masked>', sum(1 for s in out if '<masked>' in s),
      '; matches left', left)
sys.exit(1 if left else 0)
