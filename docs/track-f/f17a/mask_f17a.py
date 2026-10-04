# F17a (HPP-525): prepares sweep.jsonl for git (general rule 28).  Replaces the names of foreign applications in the 'wo'
# texts by <app> and every match of a pattern of the privacy list (one regular expression per line) by <masked> - one
# stray log directory of s146 carries a mangled user path in its name.  Idempotent.
# Usage: python mask_f17a.py <sweep.jsonl> <privacy list>
import json, re, sys

APP = re.compile(r'VK_LAYER_\w+_HOOK|C:\\ProgramData\\[^)\s]+')
src = sys.argv[1]
PRIV = [re.compile(l.strip()) for l in open(sys.argv[2], encoding='utf-8') if l.strip()]
out = []
masked = 0
for l in open(src, encoding='utf-8'):
    if not l.startswith('{'):
        continue
    r = json.loads(l)
    wo = {}
    for k, n in r['wo'].items():
        k2 = APP.sub('<app>', k)
        wo[k2] = wo.get(k2, 0) + n
    r['wo'] = wo
    s = json.dumps(r, ensure_ascii=True, sort_keys=True)
    for p in PRIV:
        s, n = p.subn('<masked>', s)
        masked += n
    out.append(s)
open(src, 'wb').write((chr(10).join(out) + chr(10)).encode('ascii'))
print('lines', len(out), '; lines with <app>', sum(1 for l in out if '<app>' in l), '; privacy matches replaced now', masked,
      '; lines with <masked>', sum(1 for l in out if '<masked>' in l))
