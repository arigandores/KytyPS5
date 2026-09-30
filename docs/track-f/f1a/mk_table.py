import json, struct, collections, sys, hashlib
sys.path.insert(0, 'C:/kyty/f287/f1a')
from rdis import dis
idx = json.load(open('C:/kyty/f287/f1a/code/index.json'))
rows = ['hash\tfamily\topcode\tfirst_pc\tcode_words\teboot_offset\tcode_sha256_16\tswappc_sites\ttarget_pairs']
for it in sorted(idx, key=lambda r: (r['op'], r['hash'])):
    data = open('C:/kyty/f287/f1a/code/%s.bin' % it['hash'], 'rb').read()
    words = list(struct.unpack('<%dI' % it['words'], data))
    ins = dis(words)
    tg = collections.Counter()
    n = 0
    for k, (pc, ws, text) in enumerate(ins):
        if text.startswith('s_swappc_b64'):
            n += 1
            src = '?'
            for j in range(k - 1, max(-1, k - 40), -1):
                t = ins[j][2]
                if t.startswith('s_mov_b32 s14, '):
                    src = t.split(', ')[1]
                    break
            tg[src] += 1
    rows.append('%s\t%s\t%s\t0x%x\t%d\t0x%x\t%s\t%d\t%s' % (it['hash'], it['fam'], it['op'], it['pc'], it['words'], it['start'],
                hashlib.sha256(data).hexdigest()[:16], n, ','.join('%s:%d' % kv for kv in sorted(tg.items()))))
open('C:/kyty/f287/f1a/b26_shaders.tsv', 'w', newline='\n').write('\n'.join(rows) + '\n')
print(len(rows) - 1, 'rows')
def rev32(x):
    return int('{:032b}'.format(x)[::-1], 2)
print('rev32(0x20468000)=0x%08x' % rev32(0x20468000))
tot = sum(int(r.split('\t')[7]) for r in rows[1:])
print('total swappc sites in 96 shaders', tot)
q = collections.Counter()
for r in rows[1:]:
    for kv in r.split('\t')[8].split(','):
        if kv:
            k, v = kv.split(':'); q[k] += int(v)
print(q)
