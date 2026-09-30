import json, struct, collections, sys, mmap
sys.path.insert(0, 'C:/kyty/f287/f1a')
from rdis import dis
idx = json.load(open('C:/kyty/f287/f1a/code/index.json'))
rows = []
tgt_src = collections.Counter()
ncalls = collections.Counter()
sizes = collections.Counter()
other_unknown = collections.Counter()
for it in idx:
    words = list(struct.unpack('<%dI' % it['words'], open('C:/kyty/f287/f1a/code/%s.bin' % it['hash'], 'rb').read()))
    ins = dis(words)
    calls = []
    for k, (pc, ws, text) in enumerate(ins):
        if text.startswith('s_swappc_b64') or text.startswith('s_setpc_b64') or text.startswith('s_getpc_b64') or text.startswith('s_call_b64'):
            # find last writers of s14, s15 before
            src = {}
            for j in range(k - 1, max(-1, k - 40), -1):
                t = ins[j][2]
                for r in ('s14', 's15'):
                    if r not in src and (t.startswith('s_') and (' %s,' % r) in t[:t.find(',') + 1]):
                        src[r] = t
                if len(src) == 2:
                    break
            calls.append((pc, text, src.get('s14', '?'), src.get('s15', '?')))
    if it['op'] == '0x21':
        ncalls[len([c for c in calls if c[1].startswith('s_swappc')])] += 1
        for c in calls:
            if c[1].startswith('s_swappc'):
                tgt_src[(c[2], c[3])] += 1
    rows.append((it['hash'], it['op'], hex(it['pc']), it['words'], calls))
print('swappc calls per shader:', dict(ncalls))
print('target sources (s14 writer, s15 writer):')
for k, v in tgt_src.most_common():
    print('  ', v, k)
for r in rows:
    if r[1] != '0x21':
        print(r[:4], r[4][:4])
json.dump(rows, open('C:/kyty/f287/f1a/calls.json', 'w'), indent=0)
# callee return form in eboot
EB = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
with open(EB, 'rb') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    for name, w in (('s_setpc_b64 s[14:15]', 0xbe80200e), ('s_setpc_b64 s[30:31]', 0xbe80201e), ('s_swappc_b64 s[14:15],s[14:15]', 0xbe8e210e)):
        p = struct.pack('<I', w)
        c = 0
        i = mm.find(p)
        first = []
        while i != -1:
            if i % 4 == 0:
                c += 1
                if len(first) < 5: first.append(hex(i))
            i = mm.find(p, i + 1)
        print(name, 'aligned in eboot:', c, first)
