"""F23f (HPP-592, ROADMAP s122 item 498(g)(2)(g)): what the 17 S12 modules write - per storage-buffer variable the OpStore /
OpAtomic* whose pointer comes (through access chains) from it, OpImageWrite count, OpKill / demote count. Offline, no GPU.
Output: wbuf_f23f.out.txt."""
import collections
import json
import sys

sys.path.insert(0, 'C:/kyty/f287/f23f')
import refs_f23f as R  # noqa: E402

D = 'C:/kyty/f287/f23f/'
S = json.load(open(D + 'sites_f23f.json'))
out = []
for h, v in sorted(S.items(), key=lambda x: (x[1]['stage'], x[0])):
    ins = R.instrs(R.words_of(open(D + 's12spv/' + v['spv'], 'rb').read()))
    names, sc, base = {}, {}, {}
    for x in ins:
        op = x[0] & 0xffff
        if op == 5:
            names[x[1]] = bytes(b for w in x[2:] for b in w.to_bytes(4, 'little')).split(bytes(1))[0].decode()
        if op == 59:
            sc[x[2]] = x[3]
        if op in (65, 66, 67, 70) and len(x) > 3:
            base[x[2]] = base.get(x[3], x[3])
    cnt = collections.Counter()
    for x in ins:
        op = x[0] & 0xffff
        if op == 62:
            b = base.get(x[1], x[1])
            cnt['store:' + names.get(b, '%%%d' % b)] += 1
        if 227 <= op <= 242:
            b = base.get(x[3], x[3])
            cnt['atomic:' + names.get(b, '%%%d' % b)] += 1
        if op == 99:
            cnt['OpImageWrite'] += 1
        if op == 252:
            cnt['OpKill'] += 1
    sbuf = [names.get(k, k) for k, s in sc.items() if s == 12]
    keep = {k: c for k, c in cnt.items() if not (k.startswith('store:') and (k[6:].startswith('%') or k[6:].startswith('out_') or k[6:].startswith('gl_')))}
    out.append('%s %s storage-buffer variables %s | %s' % (v['stage'], h, sbuf, dict(sorted(keep.items()))))
open(D + 'wbuf_f23f.out.txt', 'w', encoding='utf-8', newline=chr(10)).write(chr(10).join(out) + chr(10))
print(chr(10).join(out))
